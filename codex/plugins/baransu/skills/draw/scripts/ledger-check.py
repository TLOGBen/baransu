#!/usr/bin/env python3
"""ledger-check.py — prove each applicable step ran its step command.

Usage:
    python3 "<skill>/scripts/ledger-check.py" "<project>/.codex/draw/<slug>"

The ledger is <output-folder>/docs/lookups.log, written by lookup.py. A step command
(`lookup.py --step <id> --log <out> [--value key=value ...]`) prints every chapter the
step needs and writes one step record followed by one line per topic, all with the same
time:

    <UTC ISO time>\\tstep\\t<step id>\\t<topic ids, space-separated>
    <UTC ISO time>\\t<topic id>\\t<file>\\t<heading>\\t<anchor>

A single-topic lookup (`lookup.py <topic> --log <out>`) writes only the topic line. The
steps are references/steps.json. Python 3, standard library only, no network.

This check proves the step commands ran, nothing more. Whether the builder read and used
what was printed is judged from the run itself, not from file names or file times.

Which steps apply
-----------------
Form, approach and conditions come from `Form:`, `Approach:` and `When:` lines in
docs/brief.md (also accepted, and merged: the same lines in docs/lookups.log, optionally
after `#`, and in README.md). A few conditions are also read off the artifact's code files
(*.html, *.htm, *.js, *.mjs, *.cjs, *.ts, *.tsx, *.jsx, *.svg; never under <out>/scratch/
or node_modules/):
    * the Anatomy kit (kitScript, iso-kit, ISO_CSS, plateHtml)  → approach:mechanism
    * WebGL (glLayer, glScript, a quoted "webgl"/"webgl2"/"experimental-webgl",
      WebGL2RenderingContext, WebGLRenderer)                     → when:webgl
    * turning groups (turnScript, TURN.<name>, TURN_CSS)        → when:3d
    * window.seek / globalThis.seek / self.seek in a diagram whose HTML has an <svg>
                                                                 → when:seek-overlay
A step applies when one of its applies_to entries holds (`all`, or every `&`-joined
`form:` / `approach:` / `when:` condition is declared or detected). Steps listed at or
after `ledger-check` in steps.json run after this check and are not checked.

PASS when
---------
1. docs/lookups.log exists.
2. Every applicable step has a step record. (A step that has a record but does not apply
   is listed as "ran" and checked the same way.)
3. Every topic a record lists has its topic line with the record's time (it was printed).
4. A step whose lookup_before has a template ({move}, {fn}, {chosen} …) lists at least one
   topic filled from it in some record (a template whose plan may say "none" is exempt).

The script prints the conditions, then one row per checked step. It also notes, without
failing, when docs/first_version.md was created more than 60 minutes after the run's first
log line. Exit 0 on PASS, 1 on FAIL, 2 on a usage error.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
STEPS_JSON = SKILL_ROOT / "references" / "steps.json"
INDEX_JSON = SKILL_ROOT / "references" / "index.json"
LOG_REL = Path("docs") / "lookups.log"
FIRST_VERSION_REL = Path("docs") / "first_version.md"
FIRST_VERSION_MINUTES = 60
CONDITION_SOURCES = (Path("docs") / "brief.md", LOG_REL, Path("README.md"))

FORMS = ("diagram", "map", "film", "component")
APPROACHES = ("diagram-system", "mechanism", "free-creative")
CODE_SUFFIXES = (".html", ".htm", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".svg")

# (kind, value, pattern, what the hit means)
DETECTORS = (
    ("approach", "mechanism", re.compile(r"\bkitScript\b|iso-kit|\bISO_CSS\b|\bplateHtml\b"),
     "uses the Anatomy kit"),
    ("when", "webgl", re.compile(r"\bglLayer\b|\bglScript\b|[\"'`](?:experimental-)?webgl2?[\"'`]"
                                 r"|\bWebGL2?RenderingContext\b|\bWebGLRenderer\b"),
     "uses WebGL"),
    ("when", "3d", re.compile(r"\bturnScript\b|\bTURN\s*\.\s*[A-Za-z_]|\bTURN_CSS\b"),
     "uses turning groups (the 3D mode)"),
    ("when", "seek-overlay",
     re.compile(r"\b(?:window|globalThis|self)\s*(?:\.\s*seek\b|\[\s*[\"'`]seek[\"'`]\s*\])"),
     "is an SVG diagram driven by window.seek"),
)

LINE_RE = {key: re.compile(rf"^[\s#>*\-|]*\**{key}\**\s*[:：]\s*(.+)$", re.I | re.M)
           for key in ("Form", "Approach", "When")}


def setup_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def load_lookup():
    spec = importlib.util.spec_from_file_location("draw_lookup", SKILL_ROOT / "scripts" / "lookup.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def excluded(folder: Path, p: Path) -> bool:
    """Files under <out>/scratch/ and any node_modules/ are never part of the artifact."""
    parts = p.relative_to(folder).parts
    return bool(parts) and (parts[0] == "scratch" or "node_modules" in parts)


# ---------------------------------------------------------------- conditions

def norm_token(tok: str) -> str:
    return re.sub(r"[\s_]+", "-", tok.strip().strip("`*.").lower())


def declared_conditions(folder: Path) -> tuple[set, set, set, list[str]]:
    forms, approaches, whens, sources = set(), set(), set(), []
    for rel in CONDITION_SOURCES:
        p = folder / rel
        if not p.is_file():
            continue
        text = read_text(p)
        hit = False
        for key, rx in LINE_RE.items():
            for m in rx.finditer(text):
                hit = True
                value = m.group(1)
                if key == "When":
                    for tok in re.split(r"[,;、，/]+|\s+\+\s+", value):
                        tok = norm_token(re.sub(r"\(.*?\)", "", tok))
                        if tok and tok not in ("none", "-", "n/a"):
                            whens.add(tok)
                    continue
                low = norm_token(value)
                for known in (FORMS if key == "Form" else APPROACHES):
                    if re.search(rf"(?<![a-z]){re.escape(known)}(?![a-z])", low):
                        (forms if key == "Form" else approaches).add(known)
                if key == "Approach" and re.search(r"(?<![a-z-])diagram(?![a-z-])", low):
                    approaches.add("diagram-system")
        if hit:
            sources.append(rel.as_posix())
    return forms, approaches, whens, sources


def detect(folder: Path, forms: set) -> list[tuple[str, str, str, Path]]:
    """[(kind, value, why, first file that shows it)]"""
    files = sorted(p for p in folder.rglob("*")
                   if p.is_file() and p.suffix.lower() in CODE_SUFFIXES and not excluded(folder, p))
    texts = {p: read_text(p) for p in files}
    has_svg_page = any("<svg" in t.lower() for p, t in texts.items() if p.suffix.lower() in (".html", ".htm"))
    found = []
    for kind, value, rx, why in DETECTORS:
        if value == "seek-overlay" and not (has_svg_page and "diagram" in forms):
            continue
        hits = [p for p in files if rx.search(texts[p])]
        if hits:
            found.append((kind, value, why, hits[0]))
    return found


def clause_holds(clause: str, facts: set) -> bool:
    return all(c.strip() == "all" or c.strip() in facts for c in clause.split("&"))


# ---------------------------------------------------------------- the log

def parse_time(s: str) -> datetime | None:
    s = s.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        t = datetime.fromisoformat(s)
    except ValueError:
        return None
    return t if t.tzinfo else t.replace(tzinfo=timezone.utc)


class Record:
    def __init__(self, time: datetime, step: str, listed: list[str], line: int):
        self.time, self.step, self.listed, self.line = time, step, listed, line
        self.canons: list[str] = []      # canonical ids of the listed topics that were printed
        self.unprinted: list[str] = []   # listed topics with no topic line of the same time


def read_log(folder: Path, names: dict) -> tuple[list[Record], list[str], datetime | None]:
    """(step records, notes, time of the first line)."""
    at_time: dict[datetime, set] = {}
    records, notes, first = [], [], None
    for n, line in enumerate(read_text(folder / LOG_REL).splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#") or "\t" not in line:
            continue
        fields = line.split("\t")
        t = parse_time(fields[0])
        if t is None or len(fields) < 2:
            notes.append(f"lookups.log:{n}: not a lookup line")
            continue
        first = t if first is None or t < first else first
        if fields[1].strip() == "step":
            sid = fields[2].strip() if len(fields) > 2 else ""
            listed = fields[3].split() if len(fields) > 3 else []
            records.append(Record(t, sid, listed, n))
            continue
        req = fields[1].strip().lower()
        if req not in names:
            notes.append(f"lookups.log:{n}: unknown topic {fields[1].strip()!r}")
            continue
        at_time.setdefault(t, set()).add(names[req][1]["id"].lower())
    for r in records:
        printed = at_time.get(r.time, set())
        for raw in r.listed:
            canon = names[raw.lower()][1]["id"].lower() if raw.lower() in names else None
            if canon is None or canon not in printed:
                r.unprinted.append(raw)
            else:
                r.canons.append(canon)
    records.sort(key=lambda r: r.time)
    return records, notes, first


def stem_of(tid: str) -> str:
    return tid.split("{", 1)[0].lower()


def fills(topic: str, stem: str) -> bool:
    """A canonical topic id is filled from a template stem ('type-ramp' counts for 'type-ramp-')."""
    return topic.startswith(stem) or topic == stem.rstrip("-")


def unfilled_templates(step: dict, templates: dict, recs: list[Record]) -> list[str]:
    tids = [t for t in step["lookup_before"] if "{" in t]
    stems = [stem_of(t) for t in tids]
    printed = {c for r in recs for c in r.canons}
    missing = []
    for tid, stem in zip(tids, stems):
        if templates.get(tid, {}).get("none"):
            continue
        longer = [s for s in stems if s != stem and s.startswith(stem)]
        if not any(fills(c, stem) and not any(fills(c, s) for s in longer) for c in printed):
            missing.append(tid)
    return missing


def utc_birth(p: Path) -> datetime:
    st = os.stat(p)
    ts = getattr(st, "st_birthtime", None) or (st.st_ctime if os.name == "nt" else st.st_mtime)
    return datetime.fromtimestamp(ts, tz=timezone.utc)


# ---------------------------------------------------------------- main

def main(argv=None) -> int:
    setup_stdio()
    ap = argparse.ArgumentParser(description="Check docs/lookups.log against references/steps.json.")
    ap.add_argument("folder", help="the output folder (<project>/.codex/draw/<slug>)")
    ap.add_argument("--upto", default="ledger-check",
                    help="check only the steps before this step id (the critique loop passes --upto critique-loop)")
    args = ap.parse_args(argv)
    folder = Path(args.folder)
    if not folder.is_dir():
        print(f"ledger-check: no such folder: {folder}", file=sys.stderr)
        return 2

    lookup = load_lookup()
    names = lookup.by_name(json.loads(read_text(INDEX_JSON)))
    data = json.loads(read_text(STEPS_JSON))
    steps, templates = data["steps"], data.get("templates", {})
    step_ids = [s["id"] for s in steps]
    if args.upto not in step_ids:
        print(f"ledger-check: --upto {args.upto}: no such step in steps.json", file=sys.stderr)
        return 2
    after_check = set(step_ids[step_ids.index(args.upto):])

    forms, approaches, whens, sources = declared_conditions(folder)
    detections = detect(folder, forms)
    print(f"Folder: {folder}")
    print(f"Declared in: {', '.join(sources) or '(nothing)'}")
    for kind, value, why, first_file in detections:
        bucket = approaches if kind == "approach" else whens
        note = "" if value in bucket else " — not declared; its steps apply"
        print(f"detected {kind}:{value} ({why}, {first_file.relative_to(folder).as_posix()}){note}")
        bucket.add(value)
    print(f"Form: {', '.join(sorted(forms)) or '-'}  Approach: {', '.join(sorted(approaches)) or '-'}  "
          f"When: {', '.join(sorted(whens)) or '-'}")
    facts = {f"form:{f}" for f in forms} | {f"approach:{a}" for a in approaches} | {f"when:{w}" for w in whens}

    failures = []
    if not forms and not detections:
        failures.append("no Form: line in docs/brief.md, docs/lookups.log or README.md, and nothing detected: "
                        "cannot tell which steps apply")
    if not (folder / LOG_REL).is_file():
        failures.append(f"{LOG_REL.as_posix()} is missing: run each step's command, "
                        f"lookup.py --step <id> --log {folder}")
        records, first_line = [], None
    else:
        records, log_notes, first_line = read_log(folder, names)
        for prob in log_notes:
            print(f"note: {prob}")

    by_step: dict[str, list[Record]] = {}
    for r in records:
        if r.step not in step_ids:
            print(f"note: lookups.log:{r.line}: step record of a step steps.json does not have ({r.step!r})")
            continue
        by_step.setdefault(r.step, []).append(r)

    rows = []
    for s in steps:
        sid = s["id"]
        if sid in after_check:
            continue
        required = any(clause_holds(c, facts) for c in s["applies_to"])
        recs = by_step.get(sid, [])
        if not required and not recs:
            continue
        detail = []
        if not recs:
            detail.append(f"no step record: run lookup.py --step {sid} --log <out> before the step")
        for r in recs:
            if r.unprinted:
                detail.append(f"the step record at line {r.line} lists topics that were not printed: "
                              + ", ".join(r.unprinted))
        if recs:
            missing = unfilled_templates(s, templates, recs)
            if missing:
                detail.append("no topic filled from " + ", ".join(missing)
                              + ": pass --value with the plan's values")
        if detail:
            rows.append((sid, "FAIL", " | ".join(detail)))
            failures.append(f"{sid}: " + " | ".join(detail))
        else:
            printed = sorted({c for r in recs for c in r.canons})
            what = f"{len(recs)} record(s), {len(printed)} topic(s) printed"
            if not required:
                what += " (ran; not required by the brief)"
            rows.append((sid, "pass", what))

    fv = folder / FIRST_VERSION_REL
    if fv.is_file() and first_line is not None:
        minutes = (utc_birth(fv) - first_line).total_seconds() / 60
        if minutes > FIRST_VERSION_MINUTES:
            print(f"note: the first version came {minutes:.0f} minutes after the run's first log line "
                  f"(> {FIRST_VERSION_MINUTES}); say so in the completion report")

    w = max([len(r[0]) for r in rows] + [4])
    print()
    print(f"| {'step'.ljust(w)} | status | detail")
    print(f"|{'-' * (w + 2)}|--------|-------")
    for sid, status, detail in rows:
        print(f"| {sid.ljust(w)} | {status.ljust(6)} | {detail}")
    print()
    if failures:
        for f in failures:
            print(f"FAIL {f}")
        print(f"ledger-check: FAIL ({len(failures)} problem(s), {len(rows)} step(s) checked)")
        return 1
    print(f"ledger-check: PASS ({len(rows)} step(s) checked: every applicable step has its record "
          "and printed its topics)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
