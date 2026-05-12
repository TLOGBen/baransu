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

# Boundary-aware: matches the standalone CSS keyword "serif" but NOT "sans-serif".
# A negative lookbehind on "sans-" handles the canonical fallback. The trailing
# boundary accepts comma, semicolon, whitespace, or end of value.
_SERIF_KW   = re.compile(r'(?<!sans-)\bserif\b', re.I)

_DATA_LAYOUT = re.compile(r'\bdata-layout\s*=\s*["\']', re.I)
_CLASS_ATTR  = re.compile(r'\bclass\s*=\s*"([^"]*)"|\bclass\s*=\s*\'([^\']*)\'', re.I)
_FIGCAPTION  = re.compile(r'<\s*figcaption\b', re.I)


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


def _make_finding(path: Path, inv: int, name: str, msg: str,
                  lineno: int, snippet: str) -> dict:
    return {
        'file': str(path), 'line': lineno,
        'inv': inv, 'name': name,
        'msg': msg, 'snippet': snippet.strip()[:80],
    }


def _check_swiss_tokens_css(path: Path, text: str) -> list[dict]:
    """Lint a swiss-preset/tokens.css file against three structural invariants.

    Rules (single-file scope — no cross-file consistency, see GATE-G):
      (a) First non-empty line MUST contain `/* preset: swiss */`.
      (b) `--accent` custom property MUST be defined.
      (c) Font-stack values MUST NOT contain the bare `serif` keyword.
          The `sans-serif` fallback is allowed (boundary-aware regex).
    """
    findings: list[dict] = []
    lines = text.splitlines()

    # (a) preset comment must appear in the first non-empty line.
    first_nonempty_idx = next((i for i, ln in enumerate(lines) if ln.strip()), None)
    if first_nonempty_idx is None:
        findings.append(_make_finding(
            path, 20, 'swiss-preset-comment',
            'swiss preset 缺 `/* preset: swiss */` 首行註解（檔案為空）',
            1, ''))
    else:
        first = lines[first_nonempty_idx]
        if '/* preset: swiss */' not in first:
            findings.append(_make_finding(
                path, 20, 'swiss-preset-comment',
                'swiss preset 缺首行 `/* preset: swiss */` 識別註解',
                first_nonempty_idx + 1, first))

    # (b) --accent definition must exist.
    accent_re = re.compile(r'--accent\s*:')
    if not any(accent_re.search(ln) for ln in lines):
        # Report at line 1 since the token is globally missing.
        findings.append(_make_finding(
            path, 21, 'swiss-accent-token',
            'swiss preset 缺 --accent token 定義（IKB blue 必備）',
            1, lines[0] if lines else ''))

    # (c) No bare `serif` keyword in font stacks. Scan font-family / --font-*
    # declarations and the right-hand side of any property whose value mentions
    # a font stack. Apply boundary-aware regex (excludes sans-serif).
    font_decl_re = re.compile(r'(font-family\s*:|--font-[a-z-]*\s*:)', re.I)
    for i, line in enumerate(lines, 1):
        if font_decl_re.search(line) and _SERIF_KW.search(line):
            findings.append(_make_finding(
                path, 22, 'swiss-no-serif',
                'swiss preset font stack 不可含 serif 關鍵字（sans-serif 例外）',
                i, line))

    return findings


def _parse_slide_core_front_matter(text: str) -> tuple[dict, str]:
    """Extract YAML front-matter from an HTML comment at the top of the file.

    Slide-core HTML files wrap their YAML in `<!-- --- ... --- -->`. Returns
    (parsed_dict, error_message). parsed_dict is empty if extraction fails.
    """
    # Locate the YAML block. The opening `---` and closing `---` must appear
    # inside an HTML comment near the top.
    m = re.search(
        r'<!--\s*\n?\s*---\s*\n(.*?)\n\s*---\s*',
        text, re.DOTALL,
    )
    if not m:
        return {}, 'YAML front-matter not found (expect `<!-- --- ... --- -->`)'
    body = m.group(1)
    # Minimal YAML parser — only the keys we care about (top-level k:v and
    # block-mapping `applies_to:` with nested keys). We avoid a hard PyYAML
    # dependency to keep the script portable.
    parsed: dict = {}
    current_block: str | None = None
    for raw in body.splitlines():
        if not raw.strip() or raw.lstrip().startswith('#'):
            continue
        indent = len(raw) - len(raw.lstrip(' '))
        stripped = raw.strip()
        if indent == 0:
            if ':' not in stripped:
                continue
            key, _, val = stripped.partition(':')
            key = key.strip()
            val = val.strip()
            if val == '':
                parsed[key] = {}
                current_block = key
            else:
                parsed[key] = val.strip('"\'')
                current_block = None
        else:
            if current_block is None:
                continue
            if ':' not in stripped:
                continue
            sub_key, _, sub_val = stripped.partition(':')
            block = parsed.setdefault(current_block, {})
            if isinstance(block, dict):
                block[sub_key.strip()] = sub_val.strip().strip('"\'')
    return parsed, ''


def _check_slide_core_html(path: Path, text: str) -> list[dict]:
    """Lint a slide-cores/*.html file against four structural invariants.

    Rules (single-file scope):
      (a) `data-layout="..."` attribute MUST appear somewhere in the file.
      (b) YAML front-matter MUST be parseable and contain `layout_id` and
          `applies_to` keys.
      (c) `<figcaption>` (or `<figure>` containing caption) MUST be present.
      (d) Class attributes use a single prefix family: either every class
          token starts with `kami-*` / `swiss-*` (or stays unprefixed for
          generic anchors), and the file does NOT mix kami-* with swiss-*.
    """
    findings: list[dict] = []

    # (a) data-layout attribute
    data_layout_line = None
    for i, line in enumerate(text.splitlines(), 1):
        if _DATA_LAYOUT.search(line):
            data_layout_line = i
            break
    if data_layout_line is None:
        findings.append(_make_finding(
            path, 30, 'slide-data-layout',
            'slide-core 缺 data-layout="..." 屬性（layout 識別必備）',
            1, ''))

    # (b) YAML front-matter
    parsed, err = _parse_slide_core_front_matter(text)
    if err:
        findings.append(_make_finding(
            path, 31, 'slide-yaml-front-matter',
            f'slide-core YAML front-matter 解析失敗：{err}',
            1, ''))
    else:
        if 'layout_id' not in parsed:
            findings.append(_make_finding(
                path, 31, 'slide-yaml-front-matter',
                'slide-core YAML front-matter 缺 layout_id key',
                1, ''))
        if 'applies_to' not in parsed:
            findings.append(_make_finding(
                path, 31, 'slide-yaml-front-matter',
                'slide-core YAML front-matter 缺 applies_to key',
                1, ''))

    # (c) figcaption presence
    if not _FIGCAPTION.search(text):
        findings.append(_make_finding(
            path, 32, 'slide-figcaption',
            'slide-core 缺 <figcaption> 槽位（標題 / 圖說必備）',
            1, ''))

    # (d) class prefix discipline — kami-* OR swiss-* per file, never mixed.
    has_kami = False
    has_swiss = False
    first_swiss_line = first_kami_line = None
    for i, line in enumerate(text.splitlines(), 1):
        for m in _CLASS_ATTR.finditer(line):
            classes = (m.group(1) or m.group(2) or '').split()
            for cls in classes:
                if cls.startswith('kami-'):
                    has_kami = True
                    if first_kami_line is None:
                        first_kami_line = i
                elif cls.startswith('swiss-'):
                    has_swiss = True
                    if first_swiss_line is None:
                        first_swiss_line = i
    if has_kami and has_swiss:
        findings.append(_make_finding(
            path, 33, 'slide-class-prefix',
            f'slide-core 同檔混用 kami-* (L{first_kami_line}) 與 '
            f'swiss-* (L{first_swiss_line}) 兩前綴；單檔需一致',
            first_swiss_line or first_kami_line or 1, ''))

    return findings


def check_file(path: Path, rules: dict) -> list[dict]:
    text = path.read_text(encoding='utf-8', errors='replace')

    # Path-triggered lint families. Each artifact tree owns its own invariants:
    # swiss-preset/ and slide-cores/ are Swiss-typed artifacts (different
    # aesthetic from the warm-serif Kami default), so the generic cool-gray /
    # italic / heading-weight rules do NOT apply. Existing presets (紙-preset/,
    # google-design-preset/) keep their original lint behavior unchanged.
    path_str = str(path).replace('\\', '/')
    if 'swiss-preset/' in path_str and path.suffix.lower() == '.css':
        return _check_swiss_tokens_css(path, text)
    if 'slide-cores/' in path_str and path.suffix.lower() == '.html':
        return _check_slide_core_html(path, text)

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
