#!/usr/bin/env python3
"""lookup.py — open one chapter of the /draw references, the way a book index does.

The draw skill is a step guide plus a book index. Each step names the topics to look
up before it is done; this script prints only that chapter (or that one table row,
list item or command line) instead of a whole reference file.

Usage (the script finds the references next to itself, so run it from any folder):

    python3 "<skill>/scripts/lookup.py" <topic-id>            print the chapter
    python3 "<skill>/scripts/lookup.py" <topic-id> --log "<project>/.claude/draw/<slug>"
                                    print it and append a line to <slug>/docs/lookups.log
                                    (absolute or cwd-relative; a folder inside the skill
                                    is refused with exit 2)
    python3 "<skill>/scripts/lookup.py" --step <step-id> --log "<project>/.claude/draw/<slug>"
                                    [--value key=value ...]
                                    the step command: print every chapter the step's
                                    lookup_before (references/steps.json) names, a {key}
                                    template filled from --value key=... (repeat it, or
                                    comma-separate, for several values; aliases resolve;
                                    {form} / {approach} default to the brief's Form: /
                                    Approach: lines), then log one `step` line and one line
                                    per topic. An unknown step or value exits 1, logs nothing
    python3 "<skill>/scripts/lookup.py" --sync-aliases [--dry-run]
                                    give every template alias in steps.json (camera-push-in,
                                    transition-push, type-ramp-doc-inline, type-erd, ...) an
                                    index alias, then regenerate INDEX.md
    python3 "<skill>/scripts/lookup.py" <search words ...>    ranked candidate topic ids
    python3 "<skill>/scripts/lookup.py" --list [area]         every topic (of one area)
    python3 "<skill>/scripts/lookup.py" --render-index        regenerate references/INDEX.md
    python3 "<skill>/scripts/lookup.py" --check               every index entry resolves
    python3 "<skill>/scripts/lookup.py" --rebuild-index [--rename OLD=NEW ...]
                                    [--add FILE[=AREA] ...] [--dry-run]
                                    re-index from the current headings: entries that still
                                    resolve keep their id, aliases and keywords; a renamed
                                    file keeps its entries (--rename, paths relative to the
                                    skill); a heading renamed one-for-one keeps its id; new
                                    headings get new ids; then INDEX.md is regenerated

The data is references/index.json. Each topic is
    {id, title, area, keywords[], file, heading, parent?, row?, item?, match?, from?, to?,
     aliases?, overview?, whole?, whole_reason?}
- heading: the exact heading text (without the #'s); null means the whole file.
- parent:  the exact text of the directly enclosing heading, when the heading text repeats
           in the file.
- row:     the first cell of one Markdown table row inside the section (exact, or a unique
           prefix); the output is the section's intro, the table header and that row.
- item:    the start of one list item inside the section (after its bullet or number);
           the output is the section's intro and that item with its continuation lines.
- match:   substrings; the output is the section's intro and the lines containing them.
- from/to: a run of lines inside the section, for a long chapter with no sub-headings:
           from = the start of the first line (unique in the section; absent = the heading
           line itself), to = the start of the first line after it that is no longer part
           of the run (absent = the section's end).
- overview: the topic prints only the section's opening text and its sub-topic ids.
- whole:   the topic deliberately prints its sub-headings as one unit (whole_reason says why);
           it is also the only way past the 120-line limit.

lookups.log is tab-separated, one line per lookup:
    <UTC ISO time>\t<topic id as requested>\t<file>\t<heading>\t<row, item, match or range>
and, for a step command, first one step record with the same time as its topic lines:
    <UTC ISO time>\tstep\t<step id>\t<filled topic ids, space-separated>

Exit codes: 0 found (or search with candidates), 1 unknown topic / no candidates /
unresolvable entry, 2 usage error. Standard library only; UTF-8 in and out; no network.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
INDEX_JSON = SKILL_ROOT / "references" / "index.json"
INDEX_MD = SKILL_ROOT / "references" / "INDEX.md"
STEPS_JSON = SKILL_ROOT / "references" / "steps.json"

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
ITEM_RE = re.compile(r"^(\s*)(?:[-*+]|\d+[.)])\s+(.*)$")
SEP_RE = re.compile(r"^\s*\|?\s*:?-{2,}")
CELL_SPLIT = re.compile(r"(?<!\\)\|")


# ---------------------------------------------------------------- parsing

_cache: dict[Path, list[str]] = {}


def read_lines(path: Path) -> list[str]:
    if path not in _cache:
        _cache[path] = path.read_text(encoding="utf-8-sig").splitlines()
    return _cache[path]


def exists(path: Path) -> bool:
    return path in _cache or path.is_file()


def headings(lines: list[str]) -> list[tuple[int, int, str]]:
    """(line index, level, text) for every heading outside fenced code."""
    out, fence = [], False
    for i, line in enumerate(lines):
        if FENCE_RE.match(line):
            fence = not fence
            continue
        if fence:
            continue
        m = HEADING_RE.match(line)
        if m:
            out.append((i, len(m.group(1)), m.group(2)))
    return out


def in_fence_flags(lines: list[str]) -> list[bool]:
    flags, fence = [], False
    for line in lines:
        if FENCE_RE.match(line):
            flags.append(True)
            fence = not fence
            continue
        flags.append(fence)
    return flags


def ancestors(heads, k):
    """Texts of the enclosing headings of heads[k], outermost first."""
    chain, level = [], heads[k][1]
    for j in range(k - 1, -1, -1):
        if heads[j][1] < level:
            chain.append(heads[j][2])
            level = heads[j][1]
    return list(reversed(chain))


class Unresolved(Exception):
    pass


def locate(entry: dict) -> tuple[list[str], int, int, list[str]]:
    """(lines, start, end, heading path) of the entry's section; raises Unresolved."""
    path = SKILL_ROOT / entry["file"]
    if not exists(path):
        raise Unresolved(f"{entry['id']}: file not found: {entry['file']}")
    lines = read_lines(path)
    heading = entry.get("heading")
    if heading is None:
        return lines, 0, len(lines), []
    heads = headings(lines)
    hits = [k for k, h in enumerate(heads) if h[2] == heading]
    parent = entry.get("parent")
    if parent is not None:
        hits = [k for k in hits if ancestors(heads, k)[-1:] == [parent]]
    if len(hits) != 1:
        raise Unresolved(
            f"{entry['id']}: heading {heading!r} found {len(hits)} times in {entry['file']}"
            + (f" under {parent!r}" if parent else ""))
    k = hits[0]
    start, level = heads[k][0], heads[k][1]
    end = len(lines)
    for j in range(k + 1, len(heads)):
        if heads[j][1] <= level:
            end = heads[j][0]
            break
    return lines, start, end, ancestors(heads, k) + [heading]


def blocks(lines, start, end):
    """Split lines[start+1:end] into blank-separated blocks of (first, last) indices,
    keeping fenced code inside one block."""
    out, cur, fence = [], None, False
    for i in range(start + 1, end):
        line = lines[i]
        if FENCE_RE.match(line):
            fence = not fence
            if cur is None:
                cur = [i, i]
            cur[1] = i
            continue
        if not fence and not line.strip():
            if cur:
                out.append(tuple(cur))
                cur = None
            continue
        if cur is None:
            cur = [i, i]
        cur[1] = i
    if cur:
        out.append(tuple(cur))
    return out


def is_prose(line: str) -> bool:
    s = line.lstrip()
    return bool(s) and not (s.startswith("|") or FENCE_RE.match(line) or ITEM_RE.match(line)
                            or HEADING_RE.match(line))


def intro(lines, start, end, code: bool = True) -> list[str]:
    """The section's opening: its first prose paragraph, or an opening code block (an import
    line) followed by the prose paragraph after it."""
    bl = blocks(lines, start, end)
    if not bl:
        return []
    a, b = bl[0]
    if is_prose(lines[a]):
        return lines[a:b + 1]
    if code and FENCE_RE.match(lines[a]):
        # the first block may run on into prose when no blank line follows the fence
        out = []
        i, fence = a, False
        while i <= b:
            out.append(lines[i])
            if FENCE_RE.match(lines[i]):
                fence = not fence
                if not fence:
                    i += 1
                    break
            i += 1
        while i <= b and is_prose(lines[i]):
            out.append(lines[i])
            i += 1
        if len(out) == (b - a + 1) and len(bl) > 1 and is_prose(lines[bl[1][0]]):
            out += [""] + lines[bl[1][0]:bl[1][1] + 1]
        return out
    return []


def cells(line: str) -> list[str]:
    parts = CELL_SPLIT.split(line.strip())
    if parts and parts[0].strip() == "":
        parts = parts[1:]
    if parts and parts[-1].strip() == "":
        parts = parts[:-1]
    return [p.strip() for p in parts]


def tables(lines, start, end):
    """Tables in the section as (header index, separator index, [row indices])."""
    out, i, flags = [], start + 1, in_fence_flags(lines)
    while i < end:
        if not flags[i] and lines[i].lstrip().startswith("|") and i + 1 < end and SEP_RE.match(lines[i + 1]):
            hdr, sep, rows = i, i + 1, []
            j = i + 2
            while j < end and lines[j].lstrip().startswith("|"):
                rows.append(j)
                j += 1
            out.append((hdr, sep, rows))
            i = j
        else:
            i += 1
    return out


def find_row(entry, lines, start, end):
    want = entry["row"]
    found = []
    for hdr, sep, rows in tables(lines, start, end):
        for r in rows:
            first = cells(lines[r])[0] if cells(lines[r]) else ""
            found.append((first, hdr, sep, r))
    exact = [f for f in found if f[0] == want]
    hits = exact or [f for f in found if f[0].startswith(want)]
    if len(hits) != 1:
        raise Unresolved(f"{entry['id']}: row {want!r} found {len(hits)} times in {entry['file']} § {entry.get('heading')}")
    return hits[0][1:]


def find_item(entry, lines, start, end):
    want = entry["item"]
    flags = in_fence_flags(lines)
    hits = []
    for i in range(start + 1, end):
        if flags[i]:
            continue
        m = ITEM_RE.match(lines[i])
        if m and m.group(2).startswith(want):
            hits.append(i)
    if len(hits) != 1:
        raise Unresolved(f"{entry['id']}: item {want!r} found {len(hits)} times in {entry['file']} § {entry.get('heading')}")
    i = hits[0]
    indent = len(ITEM_RE.match(lines[i]).group(1))
    j, fence = i + 1, False
    while j < end:
        line = lines[j]
        if FENCE_RE.match(line):
            fence = not fence
            j += 1
            continue
        if fence:
            j += 1
            continue
        if not line.strip():
            # a blank line ends the item unless the next non-blank line is indented under it
            k = j + 1
            while k < end and not lines[k].strip():
                k += 1
            if k < end and (len(lines[k]) - len(lines[k].lstrip())) > indent and not HEADING_RE.match(lines[k]):
                j = k
                continue
            break
        m = ITEM_RE.match(line)
        if m and len(m.group(1)) <= indent:
            break
        if HEADING_RE.match(line):
            break
        j += 1  # a deeper sub-item, an indented line or a lazy continuation of the item
    while j > i + 1 and not lines[j - 1].strip():
        j -= 1
    return i, j


def find_matches(entry, lines, start, end):
    want = entry["match"]
    if isinstance(want, str):
        want = [want]
    flags = in_fence_flags(lines)
    hits = [i for i in range(start + 1, end) if any(w in lines[i] for w in want)]
    if not hits:
        raise Unresolved(f"{entry['id']}: no line matching {want!r} in {entry['file']} § {entry.get('heading')}")
    return hits, flags


def is_range(entry) -> bool:
    return entry.get("from") is not None or entry.get("to") is not None


def find_range(entry, lines, start, end):
    """(first line, end line) of a from/to run inside the section."""
    flags = in_fence_flags(lines)
    a = start
    if entry.get("from") is not None:
        want = entry["from"]
        hits = [i for i in range(start + 1, end) if not flags[i] and lines[i].lstrip().startswith(want)]
        if len(hits) != 1:
            raise Unresolved(f"{entry['id']}: from {want!r} found {len(hits)} times in {entry['file']} § {entry.get('heading')}")
        a = hits[0]
    b = end
    if entry.get("to") is not None:
        want = entry["to"]
        hits = [i for i in range(a + 1, end) if not flags[i] and lines[i].lstrip().startswith(want)]
        if not hits:
            raise Unresolved(f"{entry['id']}: to {want!r} not found after its start in {entry['file']} § {entry.get('heading')}")
        b = hits[0]
    while b > a + 1 and not lines[b - 1].strip():
        b -= 1
    return a, b


def range_text(entry) -> str:
    parts = []
    if entry.get("from") is not None:
        parts.append(f"from {entry['from']}")
    if entry.get("to") is not None:
        parts.append(f"to {entry['to']}")
    return " ".join(parts)


def is_part(entry) -> bool:
    return any(entry.get(k) is not None for k in ("row", "item", "match", "from", "to"))


def span(entry) -> tuple[str, int, int]:
    """(file, first line, end line) of the part of a file an entry covers."""
    lines, start, end, _ = locate(entry)
    if is_range(entry):
        a, b = find_range(entry, lines, start, end)
        return entry["file"], a, b
    if entry.get("row") is not None:
        _, _, r = find_row(entry, lines, start, end)
        return entry["file"], r, r + 1
    if entry.get("item") is not None:
        a, b = find_item(entry, lines, start, end)
        return entry["file"], a, b
    if entry.get("match") is not None:
        hits, _ = find_matches(entry, lines, start, end)
        return entry["file"], hits[0], hits[-1] + 1
    return entry["file"], start, end


def subtopics(entry, topics: list[dict]) -> list[dict]:
    """The topics directly inside an overview entry's section, in file order.

    A topic is inside when it sits in the same file within the section's lines; it is
    direct when no other heading topic inside the section also encloses it."""
    f, s, e = span(entry)
    inner = []
    for t in topics:
        if t is entry or t["file"] != f:
            continue
        try:
            tf, ts, te = span(t)
        except Unresolved:
            continue
        if s <= ts and te <= e and (is_part(t) or (ts, te) != (s, e)):
            inner.append((ts, te, t))
    direct = []
    for ts, te, t in inner:
        enclosed = any(
            c is not t and not is_part(c) and cs <= ts and te <= ce
            and ((cs, ce) != (ts, te) or is_part(t))
            for cs, ce, c in inner)
        if not enclosed:
            direct.append((ts, t))
    direct.sort(key=lambda p: p[0])
    return [t for _, t in direct]


PREAMBLE_MAX = 40


def overview_body(entry, lines, start, end, topics: list[dict]) -> list[str]:
    """Heading, the section's opening text, then the ids of its sub-topics."""
    body = [lines[start], ""] if entry.get("heading") is not None else []
    first = start + 1 if entry.get("heading") is not None else 0
    flags = in_fence_flags(lines)
    stop = end
    for i in range(first, end):
        if not flags[i] and HEADING_RE.match(lines[i]) and not (entry.get("heading") is None and i == 0):
            stop = i
            break
    pre = lines[first:stop]
    if entry.get("heading") is None and pre and HEADING_RE.match(pre[0]):
        body += [pre[0], ""]
        pre = pre[1:]
    while pre and not pre[0].strip():
        pre = pre[1:]
    while pre and not pre[-1].strip():
        pre = pre[:-1]
    if len(pre) > PREAMBLE_MAX:
        pre = intro(lines, start if entry.get("heading") is not None else 0, end)
    if pre:
        body += pre + [""]
    subs = subtopics(entry, topics)
    body.append("This topic is an overview. Look up the sub-topic you need:")
    body.append("")
    for t in subs:
        body.append(f"- `{t['id']}` — {t.get('title', '')}")
    return body


_topics_cache: list[dict] | None = None


def all_topics() -> list[dict]:
    global _topics_cache
    if _topics_cache is None:
        _topics_cache = load_index()["topics"]
    return _topics_cache


def render(entry, topics: list[dict] | None = None) -> str:
    """The text printed for one topic (also used by the tests)."""
    lines, start, end, hpath = locate(entry)
    head = [f"topic: {entry['id']} — {entry.get('title', '')}",
            f"source: {entry['file']}",
            "heading: " + (" › ".join(hpath) if hpath else "(whole file)")]
    body: list[str]
    if entry.get("overview"):
        head.append("overview: yes")
        body = overview_body(entry, lines, start, end, topics if topics is not None else all_topics())
    elif is_range(entry):
        a, b = find_range(entry, lines, start, end)
        head.append("range: " + range_text(entry))
        if a == start:
            body = lines[a:b]
        else:
            body = [lines[start], ""]
            bl = blocks(lines, start, end)
            if bl and bl[0][0] < a:
                ip = intro(lines, start, end)
                if ip:
                    body += ip + [""]
            body += lines[a:b]
    elif entry.get("row") is not None:
        hdr, sep, r = find_row(entry, lines, start, end)
        head.append(f"row: {entry['row']}")
        body = [lines[start], ""]
        ip = intro(lines, start, end)
        if ip:
            body += ip + [""]
        # the paragraph right above the table, when it is not the intro
        k = hdr - 1
        while k > start and not lines[k].strip():
            k -= 1
        above = []
        while k > start and lines[k].strip() and is_prose(lines[k]):
            above.insert(0, lines[k])
            k -= 1
        if above and above != ip:
            body += above + [""]
        body += [lines[hdr], lines[sep], lines[r]]
    elif entry.get("item") is not None:
        a, b = find_item(entry, lines, start, end)
        head.append(f"item: {entry['item']}")
        body = [lines[start], ""]
        ip = intro(lines, start, end)
        if ip:
            body += ip + [""]
        body += lines[a:b]
    elif entry.get("match") is not None:
        hits, flags = find_matches(entry, lines, start, end)
        m = entry["match"]
        head.append("match: " + (" | ".join(m) if isinstance(m, list) else m))
        body = [lines[start], ""]
        ip = intro(lines, start, end, code=False)
        if ip:
            body += ip + [""]
        fenced = [i for i in hits if flags[i]]
        plain = [i for i in hits if not flags[i]]
        body += [lines[i] for i in plain]
        if fenced:
            body += ["```"] + [lines[i] for i in fenced] + ["```"]
    else:
        seg = lines[start:end] if entry.get("heading") is not None else lines[:]
        while seg and not seg[-1].strip():
            seg = seg[:-1]
        body = seg
    return "\n".join(head) + "\n---\n" + "\n".join(body).rstrip() + "\n"


# ---------------------------------------------------------------- index

def load_index() -> dict:
    return json.loads(INDEX_JSON.read_text(encoding="utf-8"))


def by_name(index: dict) -> dict[str, tuple[str, dict]]:
    """lowercased id or alias → (spelling as defined, entry)."""
    out = {}
    for e in index["topics"]:
        out[e["id"].lower()] = (e["id"], e)
        for a in e.get("aliases", []):
            out[a.lower()] = (a, e)
    return out


WORD_RE = re.compile(r"[a-z0-9㐀-鿿]+")


def words(text: str) -> list[str]:
    return WORD_RE.findall(text.lower().replace("_", " "))


def search(index: dict, query: str, limit: int = 15) -> list[tuple[float, dict]]:
    q = [w for w in words(query.replace("-", " ")) if w]
    if not q:
        return []
    scored = []
    for e in index["topics"]:
        idw = set(words(" ".join([e["id"]] + e.get("aliases", [])).replace("-", " ")))
        tw = set(words(e.get("title", "")))
        hw = set(words(e.get("heading") or ""))
        kw = set(words(" ".join(e.get("keywords", []))))
        fw = set(words(Path(e["file"]).stem.replace("-", " ")))
        s = 0.0
        for w in q:
            if w in idw:
                s += 3
            elif any(x.startswith(w) or w.startswith(x) for x in idw if len(x) > 2 and len(w) > 2):
                s += 1.5
            if w in tw or w in hw:
                s += 2
            if w in kw:
                s += 1
            if w in fw:
                s += 0.5
        if s > 0:
            # every query word present somewhere beats a partial match
            hit_all = all(w in idw | tw | hw | kw | fw for w in q)
            scored.append((s + (2 if hit_all else 0), e))
    scored.sort(key=lambda t: (-t[0], t[1]["id"]))
    return scored[:limit]


def line_for(e: dict) -> str:
    where = e["file"] + (f" § {e['heading']}" if e.get("heading") is not None else "")
    if e.get("row") is not None:
        where += f" → row {e['row']}"
    elif e.get("item") is not None:
        where += f" → item {e['item']}"
    elif e.get("match") is not None:
        m = e["match"]
        where += " → lines " + (", ".join(m) if isinstance(m, list) else m)
    elif is_range(e):
        where += " → " + range_text(e)
    return f"{e['id']} — {e.get('title', '')} — {where}"


def code(text: str) -> str:
    return f"`{text}`" if "`" not in text else text


def render_index_md(index: dict) -> str:
    out = ["# /draw reference index",
           "",
           "<!-- Generated by `python3 scripts/lookup.py --render-index` from `references/index.json`. "
           "Do not edit by hand: edit index.json and regenerate. -->",
           "",
           "The book index of the draw skill: topic id — title — file § chapter (→ row, item or line range). "
           "Look a topic up with `python3 \"<skill>/scripts/lookup.py\" <topic-id> --log \"<project>/.claude/draw/<slug>\"`, "
           "which prints only that chapter and appends the lookup to `<slug>/docs/lookups.log`; "
           "`python3 \"<skill>/scripts/lookup.py\" <words>` lists candidate ids. Aliases follow a topic in brackets.",
           ""]
    areas = index.get("areas", {})
    order = list(areas) + sorted({e["area"] for e in index["topics"]} - set(areas))
    for area in order:
        topics = [e for e in index["topics"] if e["area"] == area]
        if not topics:
            continue
        out += [f"## {area}", ""]
        if areas.get(area):
            out += [areas[area], ""]
        files: list[str] = []
        for e in topics:
            if e["file"] not in files:
                files.append(e["file"])
        for f in files:
            out += [f"### `{f}`", ""]
            for e in topics:
                if e["file"] != f:
                    continue
                line = f"- `{e['id']}` — {e.get('title', '')} — § " + (e["heading"] if e.get("heading") is not None else "(whole file)")
                if e.get("row") is not None:
                    line += f" → row `{e['row']}`" if "`" not in e["row"] else f" → row {e['row']}"
                elif e.get("item") is not None:
                    line += f" → item {e['item']}"
                elif e.get("match") is not None:
                    m = e["match"]
                    line += " → lines " + ", ".join(f"`{x}`" for x in (m if isinstance(m, list) else [m]))
                elif is_range(e):
                    if e.get("from") is not None:
                        line += " → from " + code(e["from"])
                    if e.get("to") is not None:
                        line += (" to " if e.get("from") is not None else " → to ") + code(e["to"])
                if e.get("aliases"):
                    line += " [" + ", ".join(f"`{a}`" for a in e["aliases"]) + "]"
                out.append(line)
            out.append("")
    return "\n".join(out).rstrip() + "\n"


def check(index: dict) -> list[str]:
    problems, seen = [], {}
    for e in index["topics"]:
        for name in [e["id"]] + e.get("aliases", []):
            key = name.lower()
            if key in seen:
                problems.append(f"duplicate id or alias {name!r} ({seen[key]} and {e['id']})")
            seen[key] = e["id"]
        try:
            text = render(e, index["topics"])
        except Unresolved as exc:
            problems.append(str(exc))
            continue
        if e.get("overview"):
            if is_part(e):
                problems.append(f"{e['id']}: an overview must be a heading or a whole file, not a row, item or match")
            elif not subtopics(e, index["topics"]):
                problems.append(f"{e['id']}: overview with no sub-topics inside its section")
            else:
                problems += uncovered(e, index["topics"])
        n = len(text.splitlines())
        if n > MAX_LINES and not e.get("whole"):
            problems.append(f"{e['id']}: prints {n} lines (> {MAX_LINES}); split it into sub-topics "
                            "and make it an overview, or flag it \"whole\" with a reason")
        if e.get("whole") and not str(e.get("whole_reason", "")).strip():
            problems.append(f"{e['id']}: flagged whole without a whole_reason")
    for f, i, text in unreached_headings(index["topics"]):
        problems.append(f"{f}:{i + 1}: heading {text!r} is reached by no topic")
    return problems


def reached_lines(topics: list[dict]) -> dict[str, set[int]]:
    """Per file, the heading lines some topic reaches: the start of a heading topic, and every
    line inside a line range, a whole-file topic or a topic flagged whole (an overview reaches
    only its own heading; its sub-headings need topics of their own)."""
    out: dict[str, set[int]] = {}
    for e in topics:
        try:
            f, s, t = span(e)
        except Unresolved:
            continue
        got = out.setdefault(f, set())
        if is_range(e) or (not e.get("overview") and (e.get("heading") is None or e.get("whole"))):
            got.update(range(s, t))
        elif not is_part(e):
            got.add(s)
    return out


def unreached_headings(topics: list[dict]) -> list[tuple[str, int, str]]:
    reached = reached_lines(topics)
    out = []
    for f in sorted({e["file"] for e in topics}):
        path = SKILL_ROOT / f
        if not exists(path):
            continue
        for i, _, text in headings(read_lines(path)):
            if i not in reached.get(f, set()):
                out.append((f, i, text))
    return out


# ---------------------------------------------------------------- rebuild

STOP_WORDS = {"the", "a", "an", "and", "of", "to", "for", "in", "on", "with", "your", "its", "is", "how"}


def slug(text: str) -> str:
    plain = text.replace("`", "")
    w = re.findall(r"[a-z0-9]+", plain.lower())
    kept = [x for x in w if x not in STOP_WORDS] or w
    return "-".join(kept[:6])


def file_prefix(f: str, topics: list[dict]) -> str:
    ids = [e["id"] for e in topics if e["file"] == f]
    if ids:
        tops = [e["id"] for e in topics if e["file"] == f and not is_part(e)]
        base = min(tops or ids, key=len)
        if all(i == base or i.startswith(base + "-") for i in ids):
            return base
        common = ids[0].split("-")
        for i in ids[1:]:
            parts = i.split("-")
            n = 0
            while n < min(len(common), len(parts)) and common[n] == parts[n]:
                n += 1
            common = common[:n]
        if common:
            return "-".join(common)
    return slug(Path(f).stem) or "topic"


def area_for(f: str, topics: list[dict], areas: dict) -> str:
    same = [e["area"] for e in topics if e["file"] == f]
    if same:
        return max(set(same), key=same.count)
    near = [e["area"] for e in topics if Path(e["file"]).parent == Path(f).parent]
    if near:
        return max(set(near), key=near.count)
    parts = Path(f).parts
    for p in parts:
        if p in areas:
            return p
    return "shared"


def rebuild(index: dict, renames: dict[str, str] | None = None,
            adds: list[tuple[str, str | None]] | None = None) -> tuple[dict, list[str]]:
    """Re-index from the current headings. Returns (new index, report lines)."""
    renames, adds = renames or {}, adds or []
    report: list[str] = []
    topics = [dict(e) for e in index["topics"]]
    for e in topics:
        if e["file"] in renames:
            e["file"] = renames[e["file"]]
    for old, new in renames.items():
        report.append(f"renamed {old} -> {new}")

    kept, dropped = [], []
    for e in topics:
        try:
            span(e)
            kept.append(e)
        except Unresolved as exc:
            dropped.append((e, str(exc)))

    files: list[str] = []
    for e in topics:
        if e["file"] not in files and exists(SKILL_ROOT / e["file"]):
            files.append(e["file"])
    add_area = {}
    for f, area in adds:
        if not exists(SKILL_ROOT / f):
            report.append(f"skipped --add {f}: no such file")
            continue
        if f not in files:
            files.append(f)
        add_area[f] = area

    names = {n.lower() for e in kept for n in [e["id"]] + e.get("aliases", [])}
    reached = reached_lines(kept)
    new_by_file: dict[str, list[dict]] = {}
    for f in files:
        lines = read_lines(SKILL_ROOT / f)
        heads = headings(lines)
        counts: dict[str, int] = {}
        for _, _, text in heads:
            counts[text] = counts.get(text, 0) + 1
        prefix = file_prefix(f, kept) if any(e["file"] == f for e in kept) else slug(Path(f).stem) or "topic"
        area = add_area.get(f) or area_for(f, kept, index.get("areas", {}))
        for k, (i, _, text) in enumerate(heads):
            if i in reached.get(f, set()):
                continue
            chain = ancestors(heads, k)
            entry = {"id": "", "title": text.replace("`", ""), "area": area,
                     "keywords": sorted(set(words(text.replace("-", " ")) + [Path(f).stem]) - STOP_WORDS),
                     "file": f, "heading": text}
            if counts[text] > 1 and chain:
                entry["parent"] = chain[-1]
            base = prefix if k == 0 and heads[0][1] == 1 and i == heads[0][0] and not any(
                e["file"] == f for e in kept) else f"{prefix}-{slug(text) or 'section'}"
            cand, n = base, 2
            if cand.lower() in names and entry.get("parent"):
                cand = f"{prefix}-{slug(entry['parent'])}-{slug(text)}"
            while cand.lower() in names:
                cand, n = f"{base}-{n}", n + 1
            entry["id"] = cand
            names.add(cand.lower())
            new_by_file.setdefault(f, []).append(entry)

    # a heading renamed one-for-one keeps its id
    for f, new in new_by_file.items():
        gone = [e for e, _ in dropped if e["file"] == f and not is_part(e) and e.get("heading") is not None]
        if len(gone) == 1 and len(new) == 1:
            old, entry = gone[0], new[0]
            names.discard(entry["id"].lower())
            entry["id"] = old["id"]
            if old.get("aliases"):
                entry["aliases"] = old["aliases"]
            entry["keywords"] = sorted(set(old.get("keywords", [])) | set(entry["keywords"]))
            dropped = [(e, m) for e, m in dropped if e is not old]
            report.append(f"kept id {old['id']}: heading {old['heading']!r} -> {entry['heading']!r}")
    for e, msg in dropped:
        report.append(f"dropped {e['id']}: {msg}")

    out: list[dict] = []
    placed = set()
    for i, e in enumerate(kept):
        out.append(e)
        last_of_file = all(x["file"] != e["file"] for x in kept[i + 1:])
        if last_of_file and e["file"] in new_by_file:
            out += new_by_file[e["file"]]
            placed.add(e["file"])
    for f, new in new_by_file.items():
        if f not in placed:
            out += new
    for f, new in new_by_file.items():
        for entry in new:
            report.append(f"added {entry['id']}: {f} § {entry['heading']}")

    # overview flags follow the size of the section and its sub-topics
    for e in out:
        if is_part(e) or e.get("whole"):
            continue
        try:
            lines, start, end, _ = locate(e)
        except Unresolved:
            continue
        first = start + 1 if e.get("heading") is not None else 0
        fenced = in_fence_flags(lines)
        has_sub = any(not fenced[i] and HEADING_RE.match(lines[i])
                      for i in range(first, end) if not (e.get("heading") is None and i == 0))
        if e.get("overview"):
            if not has_sub and not subtopics(e, out):
                del e["overview"]
                report.append(f"{e['id']}: no sub-topics left, no longer an overview")
            continue
        if has_sub and len(render(e, out).splitlines()) > MAX_LINES:
            e["overview"] = True
            report.append(f"{e['id']}: over {MAX_LINES} lines with sub-headings, now an overview")

    new_index = {k: v for k, v in index.items() if k != "topics"}
    new_index["topics"] = out
    return new_index, report


def dump_index(index: dict) -> str:
    return json.dumps(index, ensure_ascii=False, indent=1) + "\n"


MAX_LINES = 120


def uncovered(entry, topics: list[dict]) -> list[str]:
    """Sub-headings of an overview section that no sub-topic reaches."""
    lines, start, end, _ = locate(entry)
    first = start + 1 if entry.get("heading") is not None else 0
    flags = in_fence_flags(lines)
    spans = []
    for t in topics:
        if t is entry or t["file"] != entry["file"]:
            continue
        try:
            spans.append(span(t))
        except Unresolved:
            continue
    out = []
    for i in range(first, end):
        if flags[i] or not HEADING_RE.match(lines[i]):
            continue
        if entry.get("heading") is None and i == 0:
            continue
        if not any(ts <= i < te for _, ts, te in spans):
            out.append(f"{entry['id']}: overview leaves heading {lines[i].strip()!r} "
                       f"(line {i + 1}) without a topic")
    return out


def now_stamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def append_log(folder: Path, requested: str, e: dict, stamp: str | None = None) -> Path:
    docs = folder / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    log = docs / "lookups.log"
    stamp = stamp or now_stamp()
    anchor = e.get("row") or e.get("item") or ""
    if not anchor and e.get("match") is not None:
        m = e["match"]
        anchor = " | ".join(m) if isinstance(m, list) else m
    if not anchor and is_range(e):
        anchor = range_text(e)
    fields = [stamp, requested, e["file"], e.get("heading") or "", anchor]
    fields = [f.replace("\t", " ").replace("\n", " ") for f in fields]
    with log.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write("\t".join(fields) + "\n")
    return log


# ---------------------------------------------------------------- steps and templates

FORM_NAMES = ("diagram", "map", "film", "component")
APPROACH_NAMES = ("diagram-system", "mechanism", "free-creative")


def load_steps() -> dict:
    return json.loads(STEPS_JSON.read_text(encoding="utf-8"))


def template_key(tid: str) -> str:
    """'camera-{move}' → 'move'."""
    m = re.search(r"\{([^}]+)\}", tid)
    return m.group(1) if m else ""


def norm_value(raw: str) -> str:
    """'Push-in, 0–2 s' → 'push-in'; 'doc-inline (960×600)' → 'doc-inline'; 'whip pan' → 'whip-pan'."""
    low = raw.strip().strip("`*").lower()
    low = re.split(r"[^a-z0-9\s_\-]", low, maxsplit=1)[0]
    return re.sub(r"[\s_\-]+", "-", low).strip("-")


def template_vocabulary(tid: str, spec: dict) -> tuple[str, dict]:
    """(stem, {spelling: canonical value, or None for a value that names no topic})."""
    stem = tid.split("{", 1)[0]
    if spec.get("from") in ("@form", "@approach"):
        chosen = FORM_NAMES if spec["from"] == "@form" else APPROACH_NAMES
        mapping = spec.get("map")
        vocab = {}
        for v in chosen:
            if mapping is None:
                vocab[v] = v
            elif v in mapping:
                vocab[v] = mapping[v]
        if spec["from"] == "@approach":
            vocab.setdefault("diagram", "diagram-system")
        return stem, vocab
    values = list(spec.get("values", []))
    if spec.get("values_from_files"):
        for p in sorted(SKILL_ROOT.glob(spec["values_from_files"])):
            if p.stem.startswith(stem):
                values.append(p.stem[len(stem):])
    vocab = {v: v for v in values}
    for alias, target in spec.get("aliases", {}).items():
        vocab.setdefault(norm_value(alias), target)
    for word in spec.get("none", []):
        vocab.setdefault(norm_value(word), None)
    return stem, vocab


def match_head(value: str, vocab: dict) -> str | None:
    """The longest known spelling the value is, or starts with (whole words only)."""
    for k in sorted(vocab, key=len, reverse=True):
        if value == k or value.startswith(k + "-"):
            return k
    return None


def fill_template(tid: str, spec: dict, raws: list[str], names: dict) -> tuple[list[str], list[str]]:
    """(canonical topic ids, values that are not known) for a template filled with raw values.
    A value is known when the template's vocabulary has it (or starts with it), or when
    <stem><value> is a topic id or alias in the index (e.g. kit-slab)."""
    stem, vocab = template_vocabulary(tid, spec)
    found, unknown = [], []
    for raw in raws:
        raw = raw.strip()
        if not raw:
            continue
        v = norm_value(raw)
        k = match_head(v, vocab) if v else None
        if k is None:
            direct = (stem + raw).lower()
            if direct in names:
                found.append(names[direct][1]["id"])
            elif v and (stem + v) in names:
                found.append(names[stem + v][1]["id"])
            else:
                unknown.append(raw)
            continue
        target = vocab[k]
        if target is None:
            continue
        key = (stem + target).lower()
        if key not in names:
            unknown.append(raw)
            continue
        found.append(names[key][1]["id"])
    out = []
    for t in found:
        if t not in out:
            out.append(t)
    return out, unknown


BRIEF_LINE = {key: re.compile(rf"^[\s#>*\-|]*\**{key}\**\s*[:：]\s*(.+)$", re.I | re.M)
              for key in ("Form", "Approach")}


def declared_values(folder: Path | None, key: str) -> list[str]:
    """Form or approach values named in <folder>/docs/brief.md (for {form} / {approach})."""
    if folder is None:
        return []
    brief = folder / "docs" / "brief.md"
    if not brief.is_file():
        return []
    text = brief.read_text(encoding="utf-8-sig", errors="replace")
    known = FORM_NAMES if key == "form" else APPROACH_NAMES
    out = []
    for m in BRIEF_LINE["Form" if key == "form" else "Approach"].finditer(text):
        low = re.sub(r"[\s_]+", "-", m.group(1).lower())
        for v in known:
            if re.search(rf"(?<![a-z]){re.escape(v)}(?![a-z])", low) and v not in out:
                out.append(v)
        if key == "approach" and re.search(r"(?<![a-z-])diagram(?![a-z-])", low) and "diagram-system" not in out:
            out.append("diagram-system")
    return out


def step_topics(step: dict, templates: dict, values: dict[str, list[str]], names: dict,
                folder: Path | None) -> tuple[list[str], list[str]]:
    """(canonical topic ids in lookup_before order, problems) for one step."""
    topics, problems, used = [], [], set()
    for tid in step["lookup_before"]:
        if "{" not in tid:
            if tid.lower() not in names:
                problems.append(f"{tid} is not in the index")
                continue
            topics.append(names[tid.lower()][1]["id"])
            continue
        spec = templates.get(tid)
        if spec is None:
            problems.append(f"{tid} has no template in steps.json")
            continue
        key = template_key(tid)
        used.add(key)
        raws = values.get(key, [])
        if not raws and spec.get("from") in ("@form", "@approach"):
            raws = declared_values(folder, key)
        if not raws:
            _, vocab = template_vocabulary(tid, spec)
            known = sorted(k for k, t in vocab.items() if t) if vocab else []
            hint = (": " + ", ".join(known[:40]) + (" …" if len(known) > 40 else "")) if known else \
                f" (a {tid.split('{')[0]}… topic id: lookup.py --list or search words)"
            problems.append(f"{tid} needs --value {key}=<value>{hint}")
            continue
        filled, unknown = fill_template(tid, spec, raws, names)
        for u in unknown:
            problems.append(f"--value {key}={u!r} is not a known value for {tid}")
        topics.extend(filled)
    for key in values:
        if key not in used:
            problems.append(f"step {step['id']} has no {{{key}}} template; --value {key}=… does not apply")
    out = []
    for t in topics:
        if t not in out:
            out.append(t)
    return out, problems


def append_step_record(folder: Path, step_id: str, entries: list[tuple[str, dict]]) -> Path:
    """One `step` line, then one line per topic, all with the same time."""
    stamp = now_stamp()
    docs = folder / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    log = docs / "lookups.log"
    with log.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write("\t".join([stamp, "step", step_id, " ".join(t for t, _ in entries)]) + "\n")
    for t, e in entries:
        append_log(folder, t, e, stamp)
    return log


def step_command(step_id: str, raw_values: list[str], log_dir: Path | None, index: dict) -> int:
    data = load_steps()
    steps = {s["id"]: s for s in data["steps"]}
    if step_id not in steps:
        near = [s for s in steps if step_id.split("-")[0] in s] or list(steps)
        print(f"unknown step {step_id!r}. Steps: " + ", ".join(near), file=sys.stderr)
        return 1
    values: dict[str, list[str]] = {}
    for rv in raw_values:
        if "=" not in rv:
            print(f"--value needs key=value, got {rv!r}", file=sys.stderr)
            return 2
        k, v = rv.split("=", 1)
        for piece in v.split(","):
            if piece.strip():
                values.setdefault(k.strip().lower(), []).append(piece.strip())
    names = by_name(index)
    step = steps[step_id]
    topics, problems = step_topics(step, data.get("templates", {}), values, names, log_dir)
    if problems:
        print(f"step {step_id}: nothing printed, nothing logged:", file=sys.stderr)
        for p in problems:
            print("  " + p, file=sys.stderr)
        return 1
    entries = [(t, names[t.lower()][1]) for t in topics]
    out = [f"step: {step_id} — {step['title']}",
           f"do: {step['do']}",
           f"done when: {step['done_when']}",
           "topics: " + (", ".join(topics) or "(none)")]
    try:
        for t, e in entries:
            out.append("")
            out.append("=" * 72)
            out.append(render(e).rstrip("\n"))
    except Unresolved as exc:
        print(f"index entry does not resolve: {exc}", file=sys.stderr)
        return 1
    sys.stdout.write("\n".join(out) + "\n")
    if log_dir is not None:
        log = append_step_record(log_dir, step_id, entries)
        print(f"(step record logged to {log.as_posix()})", file=sys.stderr)
    else:
        print("(not logged: pass --log \"<project>/.claude/draw/<slug>\" so ledger-check sees this step)",
              file=sys.stderr)
    return 0


def alias_plan(index: dict, data: dict) -> tuple[list[tuple[str, str]], list[str]]:
    """[(topic id, alias to add)] so every template alias of steps.json is an index alias; problems."""
    names = by_name(index)
    adds, problems = [], []
    for tid, spec in data.get("templates", {}).items():
        if spec.get("from", "").startswith("@") or spec.get("calls_of_index_prefix"):
            continue
        stem, vocab = template_vocabulary(tid, spec)
        for spelling, target in sorted(vocab.items()):
            alias = stem + spelling
            goal = stem + target if target is not None else spec.get("none_topic")
            if goal is None:
                continue
            if goal.lower() not in names:
                problems.append(f"{tid}: {spelling!r} points at {goal}, which is not in the index")
                continue
            entry = names[goal.lower()][1]
            have = names.get(alias.lower())
            if have is not None:
                if have[1] is not entry:
                    problems.append(f"{tid}: {alias} already names {have[1]['id']}, not {entry['id']}")
                continue
            adds.append((entry["id"], alias))
            names[alias.lower()] = (alias, entry)
    return adds, problems


def sync_aliases(index: dict, dry: bool) -> int:
    adds, problems = alias_plan(index, load_steps())
    before = set(check(index)) if adds else set()
    by_id = {e["id"]: e for e in index["topics"]}
    for tid, alias in adds:
        print(f"alias {alias} → {tid}")
        by_id[tid].setdefault("aliases", []).append(alias)
    for p in problems:
        print("FAIL", p)
    check_problems = []
    for p in (check(index) if adds else []):
        if p in before:
            print("note (already in the index, not from an alias):", p)
        else:
            check_problems.append(p)
            print("FAIL", p)
    if dry:
        print(f"dry run: {len(adds)} alias(es) to add, {len(problems) + len(check_problems)} problems; nothing written")
    elif adds and not check_problems:
        INDEX_JSON.write_text(dump_index(index), encoding="utf-8", newline="\n")
        INDEX_MD.write_text(render_index_md(index), encoding="utf-8", newline="\n")
        print(f"wrote references/index.json and references/INDEX.md ({len(adds)} alias(es) added)")
    else:
        print(f"{len(adds)} alias(es) added; nothing written" if not adds else "not written: the index has problems")
    return 0 if not problems and not check_problems else 1


# ---------------------------------------------------------------- CLI

USAGE = __doc__.split("Usage (the script finds the references next to itself, so run it from any folder):")[1].split("The data is")[0]


def inside_skill(path: Path) -> bool:
    try:
        path.resolve().relative_to(SKILL_ROOT)
        return True
    except ValueError:
        return False


def main(argv: list[str]) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    args, log_dir, i = [], None, 0
    mode, renames, adds, dry = None, {}, [], False
    step_id, raw_values = None, []
    while i < len(argv):
        a = argv[i]
        if a in ("--step", "--value"):
            if i + 1 >= len(argv):
                print(f"{a} needs a value", file=sys.stderr)
                return 2
            if a == "--step":
                step_id = argv[i + 1]
            else:
                raw_values.append(argv[i + 1])
            i += 2
            continue
        if a in ("--log", "--rename", "--add"):
            if i + 1 >= len(argv):
                print(f"{a} needs a value", file=sys.stderr)
                return 2
            v = argv[i + 1]
            if a == "--log":
                log_dir = Path(v).resolve()
                if inside_skill(log_dir):
                    print(f"--log {v!r} is inside the draw skill ({SKILL_ROOT.as_posix()}); the log belongs "
                          "to the output folder: --log \"<project>/.claude/draw/<slug>\"", file=sys.stderr)
                    return 2
            elif a == "--rename":
                if "=" not in v:
                    print("--rename needs OLD=NEW (paths relative to the skill)", file=sys.stderr)
                    return 2
                old, new = v.split("=", 1)
                renames[old.strip().replace("\\", "/")] = new.strip().replace("\\", "/")
            else:
                f, _, area = v.partition("=")
                adds.append((f.strip().replace("\\", "/"), area.strip() or None))
            i += 2
            continue
        if a in ("--list", "--render-index", "--check", "--rebuild-index", "--sync-aliases"):
            mode = a
        elif a == "--dry-run":
            dry = True
        elif a in ("-h", "--help"):
            print("Usage:" + USAGE.rstrip())
            return 0
        else:
            args.append(a)
        i += 1
    if (renames or adds) and mode != "--rebuild-index":
        print("--rename and --add go with --rebuild-index", file=sys.stderr)
        return 2
    if dry and mode not in ("--rebuild-index", "--sync-aliases"):
        print("--dry-run goes with --rebuild-index or --sync-aliases", file=sys.stderr)
        return 2
    if raw_values and step_id is None:
        print("--value goes with --step", file=sys.stderr)
        return 2
    if step_id is not None and (mode or args):
        print("--step takes no topic, search words or other mode", file=sys.stderr)
        return 2
    index = load_index()

    if step_id is not None:
        return step_command(step_id, raw_values, log_dir, index)
    if mode == "--sync-aliases":
        return sync_aliases(index, dry)

    if mode == "--rebuild-index":
        new_index, report = rebuild(index, renames, adds)
        for line in report:
            print(line)
        problems = check(new_index)
        for p in problems:
            print("FAIL", p)
        if dry:
            print(f"dry run: {len(new_index['topics'])} topics, {len(problems)} problems; nothing written")
        else:
            INDEX_JSON.write_text(dump_index(new_index), encoding="utf-8", newline="\n")
            INDEX_MD.write_text(render_index_md(new_index), encoding="utf-8", newline="\n")
            print(f"wrote references/index.json and references/INDEX.md "
                  f"({len(new_index['topics'])} topics, {len(problems)} problems)")
        return 0 if not problems else 1

    if mode == "--render-index":
        INDEX_MD.write_text(render_index_md(index), encoding="utf-8", newline="\n")
        print(f"wrote {INDEX_MD.relative_to(SKILL_ROOT).as_posix()} ({len(index['topics'])} topics)")
        return 0
    if mode == "--check":
        problems = check(index)
        md_ok = INDEX_MD.is_file() and INDEX_MD.read_text(encoding="utf-8") == render_index_md(index)
        for p in problems:
            print("FAIL", p)
        if not md_ok:
            print("FAIL references/INDEX.md is out of date: run python3 scripts/lookup.py --render-index")
        print(f"{len(index['topics'])} topics, {len(problems)} unresolved, INDEX.md {'current' if md_ok else 'stale'}")
        return 0 if not problems and md_ok else 1
    if mode == "--list":
        area = args[0] if args else None
        if area and area not in {e["area"] for e in index["topics"]}:
            print(f"unknown area {area!r}; areas: " + ", ".join(index.get("areas", {})), file=sys.stderr)
            return 1
        for e in index["topics"]:
            if area is None or e["area"] == area:
                print(line_for(e))
        return 0

    if not args:
        print("Usage:" + USAGE.rstrip(), file=sys.stderr)
        return 2
    names = by_name(index)
    if len(args) == 1 and args[0].lower() in names:
        requested, e = names[args[0].lower()]
        try:
            text = render(e)
        except Unresolved as exc:
            print(f"index entry does not resolve: {exc}", file=sys.stderr)
            return 1
        sys.stdout.write(text)
        if log_dir is not None:
            log = append_log(log_dir, requested, e)
            print(f"(logged to {log.as_posix()})", file=sys.stderr)
        return 0

    query = " ".join(args)
    single_id = len(args) == 1 and re.fullmatch(r"[\w{}.-]+", args[0]) is not None and "-" in args[0]
    found = search(index, query)
    if single_id:
        # a template such as camera-{move}, or a near miss: offer ids sharing the prefix first
        stem = args[0].lower().split("{")[0].rstrip("-")
        pref = [e for e in index["topics"] if e["id"].lower().startswith(stem + "-") or e["id"].lower() == stem]
        if pref:
            ids = {e["id"] for e in pref}
            found = [(99.0, e) for e in pref] + [t for t in found if t[1]["id"] not in ids]
        print(f"unknown topic {args[0]!r}. Candidates:", file=sys.stderr)
        for _, e in found[:25]:
            print("  " + line_for(e))
        if not found:
            print("  (none) — try search words, or --list", file=sys.stderr)
        return 1
    if not found:
        print(f"no topic matches {query!r}; try other words or --list", file=sys.stderr)
        return 1
    print(f"candidates for {query!r} (look one up by its id):")
    for _, e in found:
        print("  " + line_for(e))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
