"""Migrate check files from the `files` field to the scope fields (baransu 8.43.0). Used by `/lint sync`.

  python migrate-scope.py <checks-folder> [--dry-run]

For every `*.toml` holding a `files = ...` line:
  - `files` becomes `file` (the same list: one kind, so the OR inside it is kept; never split into `ext`);
  - a `run` check whose command has no `{file}` and whose `on` names `commit` or `done` also gets
    `scope = "diff"`: before 8.43.0 such a check ran only when the change touched its files, and without
    the scope it would now run at every commit.
Comments, order and every other line stay as written. A file already holding `scope =` keeps its own.
Prints one line per file changed; exit 0. Nothing is deleted.
"""
import re
import sys
from pathlib import Path


def migrate(text: str) -> tuple[str, list[str]]:
    lines = text.splitlines(keepends=True)
    notes: list[str] = []
    if not any(re.match(r"\s*files\s*=", l) for l in lines):
        return text, notes
    out = []
    for l in lines:
        m = re.match(r"(\s*)files(\s*=.*)", l, re.S)
        if m:
            out.append(f"{m.group(1)}file{m.group(2)}")
            notes.append("files → file")
        else:
            out.append(l)
    body = "".join(out)
    run = re.search(r"^\s*run\s*=\s*(\[.*?\])", body, re.M | re.S)
    on = re.search(r"^\s*on\s*=\s*(.*)$", body, re.M)
    has_scope = re.search(r"^\s*scope\s*=", body, re.M)
    # `on` naming commit or done, or a skill whose run joins done (/ship, /review): those ran only when touched.
    joins_done = on and re.search(r"[\"'](commit|done|skill:(baransu:)?(ship|review))[\"']", on.group(1))
    if run and "{file}" not in run.group(1) and joins_done and not has_scope:
        # Appended at the end, never inside a field: a `file = [` list may span lines.
        nl = "\r\n" if "\r\n" in body else "\n"
        body = body + ("" if body.endswith(("\n", "\r\n")) else nl) + 'scope = "diff"' + nl
        notes.append('scope = "diff"（以前只在改到這些檔時才跑）')
    return body, notes


def main() -> int:
    # The notes are Chinese; a Windows console's cp950 would garble or refuse them.
    sys.stdout.reconfigure(encoding="utf-8")
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv
    if not args:
        print(__doc__)
        return 2
    folder = Path(args[0])
    for f in sorted(folder.glob("*.toml")):
        # newline='': read and write the file's own line endings, so a migration changes only the fields.
        with open(f, encoding="utf-8", newline="") as fh:
            text = fh.read()
        new, notes = migrate(text)
        if new != text:
            if not dry:
                with open(f, "w", encoding="utf-8", newline="") as fh:
                    fh.write(new)
            print(f"{f.name}: {'、'.join(notes)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
