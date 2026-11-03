"""Flag a CSV file that is not UTF-8 with a BOM.

  python .claude/lint/scripts/csv-utf8-bom.py <file.csv>...

Excel reads a CSV without a BOM in the machine's legacy code page, so 中文 comes out garbled; the BOM
(EF BB BF) tells it the file is UTF-8. A file that is not UTF-8 at all (Big5, cp1252) is flagged too.
An empty file passes. Exit 1 when any file is flagged.
"""
import sys
from pathlib import Path

BOM = b"\xef\xbb\xbf"


def problem(path: str) -> str | None:
    b = Path(path).read_bytes()
    if not b:
        return None
    try:
        b.decode("utf-8")
    except UnicodeDecodeError:
        return f"{path}：不是 UTF-8"
    return None if b.startswith(BOM) else f"{path}：UTF-8 但沒有 BOM"


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    found = [m for p in sys.argv[1:] if p.lower().endswith(".csv") and Path(p).is_file() and (m := problem(p))]
    for m in found:
        print(m)
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
