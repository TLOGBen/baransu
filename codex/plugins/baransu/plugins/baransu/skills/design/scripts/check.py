#!/usr/bin/env python3
"""check.py — Lint HTML/CSS files against a design system's invariants.

Usage:
  python3 check.py <file.html>
  python3 check.py <file.css>
  python3 check.py path/to/dir/              (scans *.html + *.css recursively)
  python3 check.py path/to/dir/ --rules rules.json   (custom invariant config)

Exit codes:
  0 — no violations
  1 — violations found
  2 — structural error (file not found, bad JSON)
"""

import json
import re
import sys
from pathlib import Path


# ── Default rule set (warm-serif design system: parchment / ink-blue) ──────

DEFAULT_RULES = {
    "cool_gray_blocklist": [
        # Tailwind gray / slate / zinc / neutral
        "#f9fafb","#f3f4f6","#e5e7eb","#d1d5db","#9ca3af","#6b7280","#4b5563",
        "#374151","#1f2937","#111827","#030712",
        "#f8fafc","#f1f5f9","#e2e8f0","#cbd5e1","#94a3b8","#64748b","#475569",
        "#334155","#1e293b","#0f172a",
        "#fafafa","#f4f4f5","#e4e4e7","#d4d4d8","#a1a1aa","#71717a","#52525b",
        "#3f3f46","#27272a","#18181b",
        # Bootstrap gray
        "#f8f9fa","#e9ecef","#dee2e6","#ced4da","#adb5bd","#6c757d","#495057",
        "#343a40","#212529",
        # Pure cool grays / absolute extremes
        "#ffffff","#f5f5f5","#eeeeee","#e0e0e0","#bdbdbd","#9e9e9e","#757575",
        "#616161","#424242","#212121","#000000",
    ],
    "max_heading_weight": 500,      # invariant: headings locked at 500
    "max_body_line_height": 1.55,   # invariant: body line-height ≤ 1.55
    "min_shadow_blur_px": 4,        # invariant: no hard shadows (blur < 4)
    "allow_rgba_in_box_shadow": True,
    "allow_rgba_elsewhere": False,  # WeasyPrint compat + token discipline
    "allow_italic": False,          # many warm-serif systems ban italics
}


# ── Regex patterns ──────────────────────────────────────────────────────────

_RGBA       = re.compile(r'rgba\s*\(',                          re.I)
_ITALIC     = re.compile(r'font-style\s*:\s*italic',            re.I)
_BOLD_HDG   = re.compile(r'font-weight\s*:\s*(700|800|900|bold|bolder)', re.I)
_HEADING    = re.compile(r'\bh[1-6]\b',                         re.I)
_LINE_H     = re.compile(r'line-height\s*:\s*([\d.]+)',         re.I)
_SHADOW     = re.compile(
    r'box-shadow\s*:\s*(?!.*var\()(-?\d+px\s+){1,2}(\d+)px',   re.I
)
_HEX        = re.compile(r'#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b')


def _norm_hex(h: str) -> str:
    h = h.lower().lstrip('#')
    return '#' + (h if len(h) == 6 else ''.join(c * 2 for c in h))


def load_rules(path: Path) -> dict:
    try:
        data = json.loads(path.read_text())
        return {**DEFAULT_RULES, **data}
    except Exception as e:
        print(f'Error reading rules file {path}: {e}', file=sys.stderr)
        sys.exit(2)


def check_file(path: Path, rules: dict) -> list[dict]:
    text = path.read_text(encoding='utf-8', errors='replace')
    cool_set = {_norm_hex(h) for h in rules['cool_gray_blocklist']}
    findings = []

    def add(inv: int, name: str, msg: str, lineno: int, snippet: str):
        findings.append({
            'file': str(path), 'line': lineno,
            'inv': inv, 'name': name,
            'msg': msg, 'snippet': snippet.strip()[:80],
        })

    for i, line in enumerate(text.splitlines(), 1):

        # rgba usage
        if _RGBA.search(line):
            in_shadow = 'box-shadow' in line.lower()
            if in_shadow and not rules['allow_rgba_in_box_shadow']:
                add(8, 'no-rgba', 'rgba() in box-shadow — use solid hex token', i, line)
            elif not in_shadow and not rules['allow_rgba_elsewhere']:
                add(8, 'no-rgba',
                    'rgba() outside box-shadow — use solid hex token (avoids rendering bugs)',
                    i, line)

        # italics
        if not rules['allow_italic'] and _ITALIC.search(line):
            add(10, 'no-italic', 'font-style: italic — banned by this design system', i, line)

        # heading weight
        if _HEADING.search(line):
            m = _BOLD_HDG.search(line)
            if m:
                add(5, 'heading-weight',
                    f'heading font-weight {m.group(1)} exceeds max {rules["max_heading_weight"]}',
                    i, line)

        # body line-height
        m = _LINE_H.search(line)
        if m:
            lh = float(m.group(1))
            cap = rules['max_body_line_height']
            if lh > cap and not any(k in line.lower() for k in ('headline', 'title', 'display')):
                add(6, 'line-height',
                    f'line-height {lh} > {cap} for body text', i, line)

        # hard shadow
        m = _SHADOW.search(line)
        if m:
            blur = int(m.group(2))
            min_blur = rules['min_shadow_blur_px']
            if blur < min_blur:
                add(9, 'soft-shadow',
                    f'box-shadow blur {blur}px < {min_blur}px — use ring or whisper shadow',
                    i, line)

        # cool-gray hex codes
        for hm in _HEX.finditer(line):
            hx = _norm_hex(hm.group(0))
            if hx in cool_set:
                add(3, 'warm-tones', f'{hx} is a cool-gray — use a warm-toned palette token', i, line)

    return findings


def main():
    args = sys.argv[1:]
    if not args:
        print('Usage: check.py <file|dir> [--rules rules.json]', file=sys.stderr)
        sys.exit(2)

    rules_path = None
    if '--rules' in args:
        idx = args.index('--rules')
        if idx + 1 >= len(args):
            print('--rules requires a path argument', file=sys.stderr)
            sys.exit(2)
        rules_path = Path(args[idx + 1])
        args = args[:idx] + args[idx + 2:]

    target = Path(args[0])
    if not target.exists():
        print(f'Error: {target} not found', file=sys.stderr)
        sys.exit(2)

    rules = load_rules(rules_path) if rules_path else DEFAULT_RULES

    files = (
        list(target.rglob('*.html')) + list(target.rglob('*.css'))
        if target.is_dir() else [target]
    )
    if not files:
        print('No .html or .css files found.')
        sys.exit(0)

    all_findings: list[dict] = []
    for f in sorted(files):
        all_findings.extend(check_file(f, rules))

    if not all_findings:
        print(f'✅  {len(files)} file(s) checked — no violations found.')
        sys.exit(0)

    by_file: dict[str, list] = {}
    for f in all_findings:
        by_file.setdefault(f['file'], []).append(f)

    print(f'❌  {len(all_findings)} violation(s) in {len(by_file)} file(s):\n')
    for filepath, ff in by_file.items():
        print(f'  {filepath}')
        for f in ff:
            print(f"    L{f['line']}  [#{f['inv']} {f['name']}] {f['msg']}")
            print(f"           {f['snippet']}")
        print()

    sys.exit(1)


if __name__ == '__main__':
    main()
