#!/usr/bin/env python3
"""seek_split.py — gate a seek-overlay diagram with the static self-check.

    python3 scripts/diagram/seek_split.py my-diagram.seek.html [--out my-diagram.html]

A seek-overlay diagram (see references/diagram/seek-overlay.md) is a complete
static diagram plus one `<script data-seek-overlay>` block and one
`[data-seek-controls]` element. self_check.py rightly refuses any script other
than the canonical motion controller, so this tool strips exactly those two
blocks, writes the static twin, and runs self_check.py on it. The twin is what
a no-JS reader, print, reduced motion, and the SVG/PNG export see; if it fails,
the overlay was leaning on JavaScript for meaning.

Exit codes: 0 twin written and self_check passed · 1 self_check failed ·
2 usage or the file carries no overlay / more than one overlay.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT_RE = re.compile(r"\s*<script\b[^>]*\bdata-seek-overlay\b[^>]*>.*?</script>", re.S)
CONTROLS_RE = re.compile(r"\s*<div\b[^>]*\bdata-seek-controls\b[^>]*>.*?</div>", re.S)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("seek_html")
    ap.add_argument("--out", help="static twin path (default: strip .seek from the name, or add .static)")
    a = ap.parse_args()
    src = Path(a.seek_html)
    if not src.is_file():
        print(f"not found: {src}", file=sys.stderr)
        return 2
    html = src.read_text(encoding="utf-8")
    scripts = SCRIPT_RE.findall(html)
    if len(scripts) != 1:
        print(f"expected exactly one <script data-seek-overlay> block, found {len(scripts)}", file=sys.stderr)
        return 2
    static = CONTROLS_RE.sub("", SCRIPT_RE.sub("", html, count=1), count=1)
    if a.out:
        out = Path(a.out)
    elif ".seek" in src.name:
        out = src.with_name(src.name.replace(".seek", "", 1))
    else:
        out = src.with_name(src.stem + ".static" + src.suffix)
    out.write_text(static, encoding="utf-8")
    print(f"static twin → {out}")
    r = subprocess.run([sys.executable, str(HERE / "self_check.py"), str(out)])
    return 0 if r.returncode == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
