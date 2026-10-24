#!/usr/bin/env python3
"""hypothesis-status — the one read-only view every reader skill uses.

Answers, for a selector, in one call: which hypotheses cover these files, are they in
sync, what do they say, did they pass. Freshness is computed here at read time from
content hashes; nothing it prints is cached. It never writes a file.

Usage:
  hypothesis-status.py (--diff BASE | --files PATH... | --area AREA | --all) [--json]
  hypothesis-status.py (--rules | --paths | --scope | --check) AREA [--json]

Exit: 0 every listed area is `established` with every rule held (`unformalized` areas are
      listed, not judged); 10 none covers the selector; 1 anything else listed, or an
      established area with a broken rule; 2 the script failed (readers treat as `broken`).

Stdlib only, Python 3.9+. Run from anywhere inside the repo; paths are repo-relative.
Without git, --diff fails (exit 2) and every area with watch patterns is `stale` (no-git).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

SCHEMA = "baransu.hypothesis/1"
REASON_CLASSES = frozenset({"no-tool", "cannot-model", "out-of-scope", "non-trigger",
                            "no-truth", "user-declined", "handed-off"})
REASON_FIELDS = ("where", "class", "detail", "until", "instead")
SHOWS_VERDICT = frozenset({"established"})
# Stored `check.verdict_at_sync`: the model's prediction. `proved`/`disproved` are the names
# records published before 8.22.0's rename carry; they read as `held`/`violated`.
OLD_VERDICT = {"proved": "held", "disproved": "violated"}
VERDICTS = frozenset({"held", "violated", "unformalized"})


def stored_verdict(rec: dict) -> str | None:
    v = rec.get("check", {}).get("verdict_at_sync")
    return OLD_VERDICT.get(v, v)
AGENT_DIRS = (".claude", ".codex")  # Claude Code and Codex keep their work under different dirs


@dataclass(frozen=True)
class Why:
    kind: str     # changed | missing | new-writer | writer-gone | artifact-edited
    subject: str  # | no-evidence | schema | no-git | unpublished | unparseable


@dataclass
class Row:
    area: str
    state: str
    rules: int
    sync: str
    why: tuple[Why, ...]
    dir: Path
    record: dict | None = None
    covers: frozenset[str] = field(default_factory=frozenset)


def _git(root: Path, *args: str) -> str | None:
    try:
        out = subprocess.run(["git", "-c", "core.quotepath=false", *args], cwd=root, capture_output=True, text=True,
                             encoding="utf-8", errors="replace", check=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    return out.stdout


def repo_root() -> Path:
    top = _git(Path.cwd(), "rev-parse", "--show-toplevel")
    return Path(top.strip()) if top else Path.cwd()


def hash_lf(path: Path) -> str | None:
    """sha256 of the file's bytes with CRLF→LF; None when the file is missing."""
    try:
        data = path.read_bytes()
    except OSError:
        return None
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def load_record(area_dir: Path) -> tuple[dict | None, Why | None]:
    p = area_dir / "hypothesis.json"
    if not p.exists():
        return None, Why("unpublished", "hypothesis.json")
    try:
        rec = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None, Why("unparseable", "hypothesis.json")
    if not isinstance(rec, dict) or rec.get("schema") != SCHEMA:
        found = rec.get("schema") if isinstance(rec, dict) else type(rec).__name__
        return None, Why("schema", str(found))
    return rec, None


def watch_matches(root: Path, pattern: str, paths: list[str] | None = None) -> list[str] | None:
    """Sorted repo-relative paths matching `pattern` within `paths` (default: the repo), never inside a
    hypothesis area; None without git."""
    if _git(root, "rev-parse", "--git-dir") is None:
        return None
    try:
        spec = list(paths or ["."]) + [f":(exclude){d}/hypothesis" for d in AGENT_DIRS]
        out = subprocess.run(["git", "-c", "core.quotepath=false", "grep", "-l", "--untracked", "-E", pattern, "--", *spec], cwd=root,
                             capture_output=True, text=True, encoding="utf-8", errors="replace")
    except OSError:
        return None
    if out.returncode not in (0, 1):
        return None
    return sorted(line.strip().replace("\\", "/") for line in out.stdout.splitlines() if line.strip())


def cited_files(rec: dict) -> set[str]:
    cites: list[str] = []
    for part in rec.get("model_map", []):
        cites += part.get("cites", [])
    for rule in rec.get("rules", []):
        cites += rule.get("cites", [])
    return {c.rsplit(":", 1)[0] if re.search(r":\d", c) else c for c in cites}


def evidence_gaps(rec: dict) -> list[Why]:
    gaps: list[Why] = []
    check = rec.get("check", {})
    verdict = stored_verdict(rec)
    if verdict not in VERDICTS:
        gaps.append(Why("no-evidence", f"verdict={verdict}"))
        return gaps
    if verdict in ("held", "violated"):
        caught = {e.get("rule") for e in check.get("seen_failing", []) if e.get("caught") is True}
        succeeded = {e.get("goal") for e in check.get("seen_succeeding", [])
                     if e.get("reached") is True and e.get("unreachable_after") is True}
        guarded = {r for g in rec.get("goals", []) for r in g.get("guards", [])}
        for rule in rec.get("rules", []):
            if rule.get("kind") in ("safety", "liveness"):
                if rule.get("id") not in caught:
                    gaps.append(Why("no-evidence", f"{rule.get('id')} 沒看過它失敗"))
                if rule.get("id") not in guarded:
                    gaps.append(Why("no-evidence", f"{rule.get('id')} 沒有對應的目標"))
        for goal in rec.get("goals", []):
            if goal.get("id") not in succeeded:
                gaps.append(Why("no-evidence", f"{goal.get('id')} 沒看過它成功"))
        if not rec.get("goals"):
            gaps.append(Why("no-evidence", "沒有任何目標規則"))
    if verdict == "unformalized" and not rec.get("unformalized"):
        gaps.append(Why("no-evidence", "無法成立假說卻沒有任何原因紀錄"))
    for u in rec.get("unformalized", []):
        if any(not str(u.get(f, "")).strip() for f in REASON_FIELDS) or u.get("class") not in REASON_CLASSES:
            gaps.append(Why("no-evidence", f"原因紀錄 {u.get('id', '?')} 不完整"))
    missing = cited_files(rec) - set(rec.get("sync", {}).get("files", {}))
    for m in sorted(missing):
        gaps.append(Why("no-evidence", f"引用了 {m} 卻沒列在同步檔案裡"))
    return gaps


def compute_state(root: Path, area_dir: Path) -> Row:
    """First match wins, in this order — the order is the contract (reading.md § States)."""
    area = area_dir.name
    rec, problem = load_record(area_dir)
    if rec is None:
        state = "draft" if problem and problem.kind == "unpublished" else "broken"
        return Row(area, state, 0, "-", (problem,) if problem else (), area_dir)
    sync = rec.get("sync", {})
    covers = frozenset(sync.get("files", {}))
    for w in sync.get("watch", []):
        covers |= frozenset(w.get("matched", []))
    commit = str(sync.get("commit") or "-")[:7]
    row = lambda state, why: Row(area, state, len(rec.get("rules", [])), commit,
                                 tuple(why), area_dir, rec, covers)

    edited = [Why("artifact-edited", name) for name, h in sorted(sync.get("artifact", {}).items())
              if hash_lf(area_dir / name) != h]
    if edited:
        return row("draft", edited)

    stale: list[Why] = []
    for name, h in sorted(sync.get("files", {}).items()):
        now = hash_lf(root / name)
        if now is None:
            stale.append(Why("missing", name))
        elif now != h:
            stale.append(Why("changed", name))
    for copy, original in sorted(sync.get("originals", {}).items()):
        now = hash_lf(root / original)  # a moved-away original is fine; an edited one makes the copy stale
        if now is not None and now != hash_lf(root / copy):
            stale.append(Why("changed", original))
    for w in sync.get("watch", []):
        now = watch_matches(root, w.get("pattern", ""), w.get("paths"))
        if now is None:
            stale.append(Why("no-git", w.get("state", "?")))
            continue
        before = set(w.get("matched", []))
        stale += [Why("new-writer", p) for p in sorted(set(now) - before)]
        stale += [Why("writer-gone", p) for p in sorted(before - set(now))]
    if stale:
        return row("stale", stale)

    gaps = evidence_gaps(rec)
    if gaps:
        return row("draft", gaps)
    if stored_verdict(rec) == "unformalized":
        return row("unformalized", [])
    return row("established", [Why("violated", str(r.get("id"))) for r in rec.get("rules", [])
                               if r.get("verdict") == "violated"])


def legacy_rows(root: Path, migrated: set[str]) -> list[Row]:
    rows = []
    for base in (root / dot / "prove-it" / "formal" for dot in AGENT_DIRS):
        if not base.is_dir():
            continue
        for d in sorted(p for p in base.iterdir() if p.is_dir()):
            rel = d.relative_to(root).as_posix()
            if rel in migrated or rel + "/" in migrated:
                continue
            readme = d / "README.md"
            text = readme.read_text(encoding="utf-8", errors="replace") if readme.exists() else ""
            named = frozenset(m.group(1) for m in re.finditer(r"`([\w./-]+\.\w+)(?::\d[\d-]*)?`", text))
            rows.append(Row(d.name, "legacy", 0, "-", (Why("no-evidence", "嚴格檢查未完成"),), d,
                            None, named))
    return rows


def all_rows(root: Path) -> list[Row]:
    rows = [compute_state(root, d) for base in (root / dot / "hypothesis" for dot in AGENT_DIRS)
            if base.is_dir() for d in sorted(base.iterdir()) if d.is_dir()]
    migrated = {str(r.record.get("migrated_from")).rstrip("/") for r in rows
                if r.record and r.record.get("migrated_from")}
    return rows + legacy_rows(root, migrated)


def changed_since(root: Path, base: str) -> list[str]:
    parts = [_git(root, "diff", "--name-only", base), _git(root, "diff", "--name-only"),
             _git(root, "ls-files", "--others", "--exclude-standard")]
    if parts[0] is None:
        raise RuntimeError(f"git diff {base} 失敗")
    return sorted({l.strip() for p in parts if p for l in p.splitlines() if l.strip()})


def covering(rows: Sequence[Row], files: Sequence[str]) -> list[Row]:
    def norm(f: str) -> str:
        f = f.replace("\\", "/")
        while f.startswith("./"):
            f = f[2:]
        return f.rstrip("/")
    wanted = {norm(f) for f in files}
    def hits(row: Row) -> bool:  # an exact file, or a directory that contains a covered file
        return any(c == w or c.startswith(w + "/") for c in row.covers for w in wanted)
    return [r for r in rows if hits(r)]


def content_changed(rows: Sequence[Row]) -> list[Row]:
    """Rows that are stale for any reason: covered content changed or went missing, whether
    or not git tracks the file, or the set of files writing a guarded state changed — a new
    writer lives in a file the hypothesis never covered, so no file match can find it."""
    return [r for r in rows if r.state == "stale"]


def fmt_why(why: Sequence[Why]) -> str:
    return "; ".join(f"{w.kind}: {w.subject}" for w in why) or "-"


def print_table(rows: Sequence[Row], as_json: bool) -> None:
    if as_json:
        print(json.dumps([{"area": r.area, "state": r.state, "rules": r.rules, "sync": r.sync,
                           "why": [{"kind": w.kind, "subject": w.subject} for w in r.why]}
                          for r in rows], ensure_ascii=False, indent=1))
        return
    for r in rows:
        print(f"{r.area}\t{r.state}\t{r.rules}\t{r.sync}\t{fmt_why(r.why)}")


def print_detail(row: Row, view: str, as_json: bool) -> None:
    rec = row.record or {}
    show = row.state in SHOWS_VERDICT
    check = rec.get("check", {})
    if view == "rules":
        items = [{"id": r.get("id"), "kind": r.get("kind"), "verdict": r.get("verdict") if show else "?",
                  "text": r.get("text")} for r in rec.get("rules", [])]
        items += [{"id": g.get("id"), "kind": "goal", "verdict": "reached" if show else "?",
                   "text": g.get("text")} for g in rec.get("goals", [])]
    elif view == "paths":
        rule_verdict = {r.get("id"): r.get("verdict") for r in rec.get("rules", [])}
        items = [{"id": p.get("id"), "rule": p.get("rule") or "-",
                  "verdict": (rule_verdict.get(p.get("rule")) or p.get("finding", "-")) if show else "?",
                  "summary": p.get("summary"), "script": p.get("script")} for p in rec.get("paths", [])]
    elif view == "scope":
        items = [{"bounds": check.get("bounds"), "assumptions": check.get("assumptions", []),
                  "left_out": check.get("left_out", []), "unformalized": rec.get("unformalized", [])}]
    else:
        items = [{"tool": check.get("tool"), "version": check.get("version"), "command": check.get("command"),
                  "dir": row.dir.as_posix(), "note": "在暫存目錄裡重跑；結果寫進你自己的紀錄，不寫進這份假說"}]
    if as_json:
        print(json.dumps({"area": row.area, "state": row.state, "items": items}, ensure_ascii=False, indent=1))
        return
    print(f"# {row.area}  state={row.state}")
    for it in items:
        if view == "rules":
            print(f"{it['id']}\t{it['kind']}\t{it['verdict']}\t{it['text']}")
        elif view == "paths":
            print(f"{it['id']}\t{it['rule']}\t{it['verdict']}\t{it['summary']}\t{it['script']}")
        else:
            for k, v in it.items():
                print(f"{k}: {json.dumps(v, ensure_ascii=False) if not isinstance(v, str) else v}")


def exit_code(rows: Sequence[Row]) -> int:
    if not rows:
        return 10
    judged = [r for r in rows if r.state != "unformalized"]
    return 0 if all(r.state == "established" and not r.why for r in judged) else 1


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="hypothesis-status.py", add_help=True)
    sel = ap.add_mutually_exclusive_group(required=True)
    sel.add_argument("--diff", metavar="BASE")
    sel.add_argument("--files", nargs="+", metavar="PATH")
    sel.add_argument("--area")
    sel.add_argument("--all", action="store_true")
    for view in ("rules", "paths", "scope", "check"):
        sel.add_argument(f"--{view}", metavar="AREA")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    root = repo_root()
    rows = all_rows(root)
    for view in ("rules", "paths", "scope", "check"):
        area = getattr(a, view)
        if area:
            match = [r for r in rows if r.area == area]
            if not match:
                return 10
            print_detail(match[0], view, a.json)
            return exit_code(match)
    if a.area:
        rows = [r for r in rows if r.area == a.area]
    elif a.files:
        rows = covering(rows, a.files)
    elif a.diff:
        hit = covering(rows, changed_since(root, a.diff))
        rows = hit + [r for r in content_changed(rows) if r not in hit]
    print_table(rows, a.json)
    return exit_code(rows)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as exc:  # readers treat exit 2 as `broken`, never as "no hypothesis"
        print(f"hypothesis-status 失敗：{exc}", file=sys.stderr)
        raise SystemExit(2)
