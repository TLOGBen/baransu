"""Rewrite a project's lint timings to the 8.43 form. Used by `/lint sync`.

  python migrate-timing.py <lint-folder>        rewrite lint.toml, sets/*.toml and checks/*.toml in place
  python migrate-timing.py --text < file         print one file's text rewritten (for tests and fixtures)

Per check table (a `[check.<id>]` table, or a whole one-check file):
  on:       edit → post:edit; bash → pre:bash; commit → pre:commit, pre:push; done → pre:skill:ship,
            pre:skill:review; skill:<x> → pre:skill:<x>; reply → post:retry; manual stays
  actions:  push → on pre:push; redo → on post:retry; the rest (delete) stays; an empty list goes
  built-ins: `on` goes (their timing is fixed); levels whose meaning moved are renamed —
            destructive-preview and explain-before-edit error → check (both refused once before),
            explain-before-edit, user-language and report-before-stop warn → retry (they always asked again)
            — in `severity` and in `strict` alike, and only while the folder still holds an old timing: once
            migrated, warn on explain-before-edit or error on destructive-preview is the person's own choice
An array written over several lines (`on = [` … `]`) is read whole and written back on one line.
Lines are rewritten in place: comments, the order of fields and the line endings stay. A folder already in the
new form is left as it is (running twice changes nothing). Prints one line per changed check. Exit 0.
"""
import re
import sys
from pathlib import Path

OLD = {
    "edit": ["post:edit"],
    "bash": ["pre:bash"],
    "commit": ["pre:commit", "pre:push"],
    "done": ["pre:skill:ship", "pre:skill:review"],
    "reply": ["post:retry"],
    "manual": ["manual"],
}
LEVELS = {
    "destructive-preview": {"error": "check"},
    "explain-before-edit": {"error": "check", "warn": "retry"},
    "user-language": {"warn": "retry"},
    "report-before-stop": {"warn": "retry"},
}
HEADER = re.compile(r"^\s*\[(?!\[)([^\]]+)\]\s*(#.*)?$")
FIELD = re.compile(r"^(\s*)(on|actions|builtin|severity|strict)(\s*=\s*)(.*?)(\s*(#.*)?)$")
ITEM = re.compile(r"""["']([^"']*)["']""")


def items(value: str) -> list[str]:
    return ITEM.findall(value)


def arr(xs: list[str]) -> str:
    return "[" + ", ".join(f'"{x}"' for x in xs) + "]"


def new_on(old: list[str]) -> list[str]:
    out: list[str] = []
    for x in old:
        for y in OLD.get(x, [f"pre:{x}"] if x.startswith("skill:") else [x]):
            if y not in out:
                out.append(y)
    return out


def join_arrays(lines: list[str]) -> list[str]:
    """`key = [` … `]` over several lines → one line, so a field is always one line below."""
    out: list[str] = []
    i = 0
    while i < len(lines):
        ln = lines[i]
        m = re.match(r"^\s*(on|actions)\s*=\s*\[", ln)
        if m and "]" not in ln.split("#", 1)[0]:
            eol = "\r" if ln.endswith("\r") else ""
            parts = [ln.rstrip("\r")]
            i += 1
            while i < len(lines):
                parts.append(lines[i].strip().rstrip("\r"))
                if "]" in lines[i].split("#", 1)[0]:
                    break
                i += 1
            out.append(" ".join(p for p in parts if p) + eol)
        else:
            out.append(ln)
        i += 1
    return out


OLD_NAME = re.compile(r"""["'](edit|bash|commit|done|reply|skill:[^"']*)["']""")


def has_old(text: str) -> bool:
    """Whether a file still names a timing or an action from before 8.43."""
    for ln in join_arrays(text.split("\n")):
        m = FIELD.match(ln)
        if m and m.group(2) == "on" and OLD_NAME.search(m.group(4)):
            return True
        if m and m.group(2) == "actions" and re.search(r"""["'](push|redo)["']""", m.group(4)):
            return True
    return False


def rewrite_block(lines: list[str], levels: bool) -> tuple[list[str], bool]:
    """One check's lines → its rewritten lines, and whether anything changed. `levels`: rename the built-ins'
    levels whose meaning moved (only while the folder is being migrated)."""
    lines = join_arrays(lines)
    fields: dict[str, tuple[int, re.Match]] = {}
    for i, ln in enumerate(lines):
        m = FIELD.match(ln)
        if m and m.group(2) not in fields:
            fields[m.group(2)] = (i, m)
    if not fields:
        return lines, False
    out = list(lines)
    drop: set[int] = set()
    builtin = items(fields["builtin"][1].group(4))[0] if "builtin" in fields and items(fields["builtin"][1].group(4)) else None
    if builtin:
        if "on" in fields and not all(x.startswith("after:") for x in items(fields["on"][1].group(4))):
            drop.add(fields["on"][0])
        for f in ("severity", "strict") if levels else ():
            if f in fields:
                i, m = fields[f]
                lv = items(m.group(4))
                if lv and lv[0] in LEVELS.get(builtin, {}):
                    out[i] = f'{m.group(1)}{f}{m.group(3)}"{LEVELS[builtin][lv[0]]}"{m.group(5)}'
    else:
        on = items(fields["on"][1].group(4)) if "on" in fields else []
        acts = items(fields["actions"][1].group(4)) if "actions" in fields else []
        on2 = new_on(on)
        if "push" in acts and "pre:push" not in on2:
            on2.append("pre:push")
        if "redo" in acts and "post:retry" not in on2:
            on2.append("post:retry")
        acts2 = [a for a in acts if a not in ("push", "redo")]
        if "on" in fields:
            i, m = fields["on"]
            out[i] = f"{m.group(1)}on{m.group(3)}{arr(on2)}{m.group(5)}"
        elif on2:
            i, m = fields["actions"]
            out.insert(i, f"{m.group(1)}on = {arr(on2)}")
            fields = {k: ((j + 1 if j >= i else j), mm) for k, (j, mm) in fields.items()}
        if "actions" in fields:
            i, m = fields["actions"]
            if acts2:
                out[i] = f"{m.group(1)}actions{m.group(3)}{arr(acts2)}{m.group(5)}"
            else:
                drop.add(i)
    out = [ln for j, ln in enumerate(out) if j not in drop]
    return out, out != lines


def rewrite(text: str, levels: bool = True) -> tuple[str, list[str]]:
    """A whole file: each [check.<id>] table, or the file itself when it has none (a checks/ file)."""
    lines = text.split("\n")
    blocks: list[tuple[str, list[str]]] = [("", [])]
    for ln in lines:
        h = HEADER.match(ln)
        if h:
            blocks.append((h.group(1).strip(), [ln]))
        else:
            blocks[-1][1].append(ln)
    has_tables = any(name.startswith("check.") for name, _ in blocks)
    out: list[str] = []
    changed: list[str] = []
    for name, blk in blocks:
        if (has_tables and name.startswith("check.") and name.count(".") == 1) or (not has_tables and name == ""):
            new, did = rewrite_block(blk, levels)
            if did:
                changed.append(name[len("check."):] if name else "(this file)")
            out.extend(new)
        else:
            out.extend(blk)
    return "\n".join(out), changed


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) == 2 and sys.argv[1] == "--text":
        sys.stdin.reconfigure(encoding="utf-8")
        text = sys.stdin.read()
        print(rewrite(text, has_old(text))[0], end="")
        return 0
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    root = Path(sys.argv[1])
    files = [root / "lint.toml", *sorted((root / "sets").glob("*.toml")), *sorted((root / "checks").glob("*.toml"))]
    files = [f for f in files if f.is_file()]
    # newline="": CRLF stays CRLF.
    texts = {f: f.open(encoding="utf-8", newline="").read() for f in files}
    levels = any(has_old(x) for x in texts.values())
    for f in files:
        text = texts[f]
        new, changed = rewrite(text, levels)
        if new != text:
            f.write_text(new, encoding="utf-8", newline="")
            where = f.stem if f.parent.name == "checks" else f.name
            print(f"{f.relative_to(root)}：{'、'.join(c if c != '(this file)' else where for c in changed)} 換成新的時機寫法")
    return 0


if __name__ == "__main__":
    sys.exit(main())
