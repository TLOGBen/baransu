#!/usr/bin/env python3
"""check.py — baransu /design v1.3 lint (structural + cross-artifact consistency).

Modes:
  python3 check.py                         # project root mode: 6 v1.3 checks A-F
  python3 check.py <path/to/project>       # explicit project root
  python3 check.py <file>                  # single-file legacy per-artifact mode
  python3 check.py <dir>                   # recurse legacy per-artifact mode
  python3 check.py --rules rules.json ...  # custom rule overrides

Project-root v1.3 checks (per design.md §跨層 Invariant 補充):
  A. 5 份 artifact 齊全 — tokens.css / DESIGN.md / DESIGN.html / design-cores/ / slide-cores/
     (fail-fast: A 失敗即終止後續 B-F)
  B. tokens.css 含全套 baransu canonical 38 names (參考 CANONICAL_TOKENS)
  C. 同 preset cross-artifact prefix 一致 — design-cores/, slide-cores/ class
     prefix 全部與 tokens.css 第一行 preset header slug 一致
  D. DESIGN.md 九段完整 + 內文不含 v1.2 token 命名（--brand / --parchment 等）
  E. design-cores/long-form.html 含且僅含一個 <section data-slot="long-form-body">
  F. design-cores/dashboard.html 不含 <script> 或外部 src=http(s)://

Per-file legacy mode (preserved for /book validator interop):
  - swiss-preset/tokens.css → preset header + --accent token + no serif keyword
  - slide-cores/*.html → data-layout, YAML front-matter, figcaption, single prefix family

Kami 十不變量已移出本 script。紙 preset sanity 由 紙-preset/紙-sanity.sh 自帶
(透過 --kami-sanity flag 呼叫 check.py 的 sanity 子模式)。

Exit codes:
  0 — no violations
  1 — violations found
  2 — structural error (file not found, bad JSON, project root malformed)
"""

import json
import re
import sys
from pathlib import Path


# ── v1.3 Canonical Token Schema (38 (+5 capability) = 43; mirrors design.md "Canonical Token Schema") ──

# BASE_TOKENS — the 38 always-required canonical names.
BASE_TOKENS = [
    # Surface (5)
    "--paper", "--surface", "--surface-strong", "--dark-surface", "--deep-dark",
    # Accent (2)
    "--accent", "--accent-on",
    # Text (5)
    "--ink", "--text-primary", "--text-secondary", "--text-muted", "--text-faint",
    # Border (2)
    "--border", "--border-soft",
    # Font (3)
    "--font-sans", "--font-serif", "--font-mono",
    # Shadow (2)
    "--shadow-ring", "--shadow-whisper",
    # Spacing (7)
    "--space-xs", "--space-sm", "--space-md", "--space-lg",
    "--space-xl", "--space-2xl", "--space-3xl",
    # Radius (7)
    "--radius-xs", "--radius-sm", "--radius-md", "--radius-lg",
    "--radius-xl", "--radius-2xl", "--radius-hero",
    # Layout (3)
    "--cover-title-align", "--grid-columns", "--grid-gutter",
    # Semantic (2)
    "--delta-up", "--delta-down",
]

# CAPABILITY_TOKENS — the 5 generation-power tokens (grain-opacity intentionally
# excluded: PDF render risk unverified, not in the required set this batch).
CAPABILITY_TOKENS = [
    "--ease", "--duration", "--stagger-step", "--font-display", "--shadow-drama",
]

# Combined canonical set, kept for back-compat: 38 (+5 capability) = 43.
CANONICAL_TOKENS = BASE_TOKENS + CAPABILITY_TOKENS

# v1.2 banned token names (Check D + Check B)
V12_BANNED_TOKENS = [
    "--brand", "--brand-light", "--brand-tint", "--brand-tint-strong",
    "--parchment", "--ivory", "--olive", "--warm-sand", "--stone",
    "--near-black", "--dark-warm", "--charcoal",
    "--sans", "--serif", "--mono",
]

# DESIGN.md required nine-section headings (Appendix B of design.md)
DESIGN_MD_NINE_SECTIONS = [
    "## 1. Visual Theme & Atmosphere",
    "## 2. Color Palette & Roles",
    "## 3. Typography Rules",
    "## 4. Component Stylings",
    "## 5. Layout & Spacing",
    "## 6. Iconography & Imagery",
    "## 7. Motion & Animation",
    "## 8. Do / Don't",
    "## 9. AI Prompt Guide",
]

# Static prefix whitelist (Inv-4 in design.md)
STATIC_PREFIXES = {"kami", "google", "swiss"}

# Slug capture tolerates an optional `; schema: <N>` field (and trailing junk)
# before `*/`. The `[^*]*` technique stops before the closing `*/`.
PRESET_HEADER_RE = re.compile(r"^\s*/\*\s*preset:\s*([a-z][a-z0-9-]{1,15})[^*]*\*/")
# Extracts an integer schema version from a `; schema: <N>` field. Malformed
# fields (e.g. `schema: abc`, `schema: 4x3`) do NOT match → treated as no version.
SCHEMA_FIELD_RE = re.compile(r";\s*schema:\s*(\d+)\s*(?:\*/|;|$)")


# ── Default rule set (used in legacy per-file mode for Kami warm-serif design) ──

DEFAULT_RULES = {
    "cool_gray_blocklist": [
        "#f9fafb","#f3f4f6","#e5e7eb","#d1d5db","#9ca3af","#6b7280","#4b5563",
        "#374151","#1f2937","#111827","#030712",
        "#f8fafc","#f1f5f9","#e2e8f0","#cbd5e1","#94a3b8","#64748b","#475569",
        "#334155","#1e293b","#0f172a",
        "#fafafa","#f4f4f5","#e4e4e7","#d4d4d8","#a1a1aa","#71717a","#52525b",
        "#3f3f46","#27272a","#18181b",
        "#f8f9fa","#e9ecef","#dee2e6","#ced4da","#adb5bd","#6c757d","#495057",
        "#343a40","#212529",
        "#ffffff","#f5f5f5","#eeeeee","#e0e0e0","#bdbdbd","#9e9e9e","#757575",
        "#616161","#424242","#212121","#000000",
    ],
    "max_heading_weight": 500,
    "max_body_line_height": 1.55,
    "min_shadow_blur_px": 4,
    "allow_rgba_in_box_shadow": True,
    "allow_rgba_elsewhere": False,
    "allow_italic": False,
}


# ── Regex patterns (shared) ─────────────────────────────────────────────────

_RGBA       = re.compile(r'rgba\s*\(', re.I)
_ITALIC     = re.compile(r'font-style\s*:\s*italic', re.I)
_BOLD_HDG   = re.compile(r'font-weight\s*:\s*(700|800|900|bold|bolder)', re.I)
_HEADING    = re.compile(r'\bh[1-6]\b', re.I)
_LINE_H     = re.compile(r'line-height\s*:\s*([\d.]+)', re.I)
_SHADOW     = re.compile(r'box-shadow\s*:\s*(?!.*var\()(-?\d+px\s+){1,2}(\d+)px', re.I)
_HEX        = re.compile(r'#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b')
_SERIF_KW   = re.compile(r'(?<!sans-)\bserif\b', re.I)
_DATA_LAYOUT = re.compile(r'\bdata-layout\s*=\s*["\']', re.I)
_CLASS_ATTR  = re.compile(r'\bclass\s*=\s*"([^"]*)"|\bclass\s*=\s*\'([^\']*)\'', re.I)
_FIGCAPTION  = re.compile(r'<\s*figcaption\b', re.I)
_SLOT_RE     = re.compile(r'<\s*section[^>]*data-slot\s*=\s*["\']long-form-body["\']', re.I)
_SCRIPT_TAG  = re.compile(r'<\s*script\b', re.I)
_EXT_SRC     = re.compile(r'\bsrc\s*=\s*["\'](?:https?:)?//', re.I)


def _norm_hex(h: str) -> str:
    h = h.lower().lstrip('#')
    return '#' + (h if len(h) == 6 else ''.join(c * 2 for c in h))


def _make_finding(path: Path | str, inv: int, name: str, msg: str,
                  lineno: int, snippet: str) -> dict:
    return {
        'file': str(path), 'line': lineno,
        'inv': inv, 'name': name,
        'msg': msg, 'snippet': snippet.strip()[:120],
    }


def load_rules(path: Path) -> dict:
    try:
        data = json.loads(path.read_text())
        return {**DEFAULT_RULES, **data}
    except Exception as e:
        print(f'Error reading rules file {path}: {e}', file=sys.stderr)
        sys.exit(2)


# ────────────────────────────────────────────────────────────────────────────
# v1.3 Project-root checks (A-F)
# ────────────────────────────────────────────────────────────────────────────

REQUIRED_DESIGN_CORES = {
    "long-form.html", "gallery.html", "dashboard.html",
    "card.html", "data-table.html", "metric.html",
    "quote-callout.html", "section-title.html", "tag-button.html",
}


def _is_project_root(p: Path) -> bool:
    """Heuristic: project root has both tokens.css and DESIGN.md at top level."""
    if not p.is_dir():
        return False
    return (p / "tokens.css").exists() or (p / "DESIGN.md").exists()


def check_project_root(root: Path) -> list[dict]:
    """v1.3 project-root mode — runs checks A through F.

    Check A fails fast: if 5 artifact not all present, B-F are skipped.
    """
    findings: list[dict] = []

    # Check A: 5 artifact 齊全
    a_missing = []
    for name in ("tokens.css", "DESIGN.md", "DESIGN.html"):
        if not (root / name).is_file():
            a_missing.append(name)
    for name in ("design-cores", "slide-cores"):
        if not (root / name).is_dir():
            a_missing.append(f"{name}/")
    if a_missing:
        findings.append(_make_finding(
            root, 1, 'check-A-artifact-completeness',
            f'缺少 v1.3 artifact: {", ".join(a_missing)}',
            1, ''))
        # Fail-fast: skip B-F
        return findings

    # Resolve preset slug (+ optional schema version) from tokens.css first
    # non-empty line. The schema version drives the version-aware Check B below.
    tokens_path = root / "tokens.css"
    tokens_text = tokens_path.read_text(encoding='utf-8', errors='replace')
    preset_slug, preset_version = _parse_preset_header(tokens_text)

    # Check B: tokens.css 含必備 canonical（依 schema 版本要求 38 或 43）
    findings.extend(_check_tokens_canonical_completeness(
        tokens_path, tokens_text, preset_version))

    if preset_slug is None:
        findings.append(_make_finding(
            tokens_path, 2, 'check-B-preset-header',
            'tokens.css 第一行不符 `/* preset: <slug> */` 格式',
            1, tokens_text.splitlines()[0] if tokens_text.splitlines() else ''))

    # Check C: cross-artifact prefix 一致
    findings.extend(_check_cross_artifact_prefix(root, preset_slug))

    # Check D: DESIGN.md 九段完整 + 內文無 v1.2 命名
    findings.extend(_check_design_md(root / "DESIGN.md"))

    # Check E: long-form.html slot 唯一性
    findings.extend(_check_longform_slot(root / "design-cores" / "long-form.html"))

    # Check F: dashboard.html 純靜態
    findings.extend(_check_dashboard_static(root / "design-cores" / "dashboard.html"))

    return findings


def _parse_preset_header(tokens_text: str) -> tuple[str | None, int | None]:
    """Find first non-empty line; extract (slug, version|None).

    version comes from an optional `; schema: <N>` field. Malformed schema
    fields fall back to None (no error) to protect legacy-file migration.
    """
    for line in tokens_text.splitlines():
        if line.strip():
            m = PRESET_HEADER_RE.match(line)
            if not m:
                return (None, None)
            sm = SCHEMA_FIELD_RE.search(line)
            version = int(sm.group(1)) if sm else None
            return (m.group(1), version)
    return (None, None)


def _required_tokens_for_version(version: int | None) -> list[str]:
    """Map a parsed schema version to the required canonical token set.

    PINNED design.md decision (do not deviate):
      - None or 38 → BASE_TOKENS (legacy default; protects migration)
      - 43         → BASE_TOKENS + CAPABILITY_TOKENS (full canonical)
      - any other known-format integer (e.g. 99) → BASE_TOKENS, plus a stderr
        warning. NEVER fails (conservative: rather under-require than break files).
    """
    if version is None or version == 38:
        return BASE_TOKENS
    if version == 43:
        return BASE_TOKENS + CAPABILITY_TOKENS
    print(f'warning: 未知 schema 版本 {version} — fallback 到 BASE(38)，不 fail',
          file=sys.stderr)
    return BASE_TOKENS


def _check_tokens_canonical_completeness(
        path: Path, text: str, version: int | None = None) -> list[dict]:
    """Check B — required canonical names present; no v1.2 banned name as primary def.

    The required set is version-aware (see _required_tokens_for_version): schema:43
    requires the full 43, absent/legacy versions require only BASE(38).
    """
    findings: list[dict] = []
    required = _required_tokens_for_version(version)
    # Find all `--xxx:` definitions (LHS only, not var() references)
    define_re = re.compile(r'^\s*(--[a-z][a-z0-9-]*)\s*:', re.M)
    defined = set(define_re.findall(text))

    missing = [t for t in required if t not in defined]
    if missing:
        suffix = '（schema:43 需要完整 43）' if version == 43 else ''
        findings.append(_make_finding(
            path, 2, 'check-B-canonical-missing',
            f'tokens.css 缺 canonical names ({len(missing)} 個): {", ".join(missing[:8])}'
            + ('…' if len(missing) > 8 else '') + suffix,
            1, ''))

    banned_found = [t for t in V12_BANNED_TOKENS if t in defined]
    if banned_found:
        findings.append(_make_finding(
            path, 2, 'check-B-v1.2-banned',
            f'tokens.css 含 v1.2 殘留 token 定義: {", ".join(banned_found)}',
            1, ''))

    return findings


def _check_cross_artifact_prefix(root: Path, expected_slug: str | None) -> list[dict]:
    """Check C — design-cores/*.html + slide-cores/*.html 內 class prefix 一致。

    一致性條件：
      - 所有 class first-token prefix 屬於 STATIC_PREFIXES 或等於 expected_slug
      - 同檔內不混 prefix
      - 若 expected_slug 存在，所有檔案 prefix 必須等於 expected_slug
    """
    findings: list[dict] = []
    files = list((root / "design-cores").glob("*.html")) + \
            list((root / "slide-cores").glob("*.html"))
    if not files:
        return findings

    allowed_prefixes = STATIC_PREFIXES | ({expected_slug} if expected_slug else set())

    for fp in files:
        text = fp.read_text(encoding='utf-8', errors='replace')
        prefixes_in_file: dict[str, int] = {}
        for i, line in enumerate(text.splitlines(), 1):
            for m in _CLASS_ATTR.finditer(line):
                classes = (m.group(1) or m.group(2) or '').split()
                for cls in classes:
                    if '-' in cls:
                        pfx = cls.split('-', 1)[0]
                        # only count prefixes that look like preset prefixes
                        # (avoid generic utility classes like "row", "col-12")
                        if pfx in allowed_prefixes or pfx in {'kami', 'google', 'swiss'}:
                            prefixes_in_file.setdefault(pfx, i)
        if not prefixes_in_file:
            continue
        unique_prefixes = set(prefixes_in_file.keys())
        if len(unique_prefixes) > 1:
            findings.append(_make_finding(
                fp, 3, 'check-C-prefix-mix',
                f'單檔混用 prefix: {", ".join(sorted(unique_prefixes))}',
                min(prefixes_in_file.values()), ''))
        elif expected_slug and unique_prefixes != {expected_slug}:
            mismatch = unique_prefixes.pop()
            findings.append(_make_finding(
                fp, 3, 'check-C-prefix-mismatch',
                f'檔內 prefix `{mismatch}-*` 與 tokens.css preset header '
                f'`{expected_slug}` 不一致',
                prefixes_in_file[mismatch], ''))

    return findings


def _check_design_md(path: Path) -> list[dict]:
    """Check D — DESIGN.md 九段完整 + 內文無 v1.2 token 命名。"""
    findings: list[dict] = []
    text = path.read_text(encoding='utf-8', errors='replace')

    # Nine-section completeness
    missing_sections = [s for s in DESIGN_MD_NINE_SECTIONS if s not in text]
    if missing_sections:
        findings.append(_make_finding(
            path, 4, 'check-D-nine-sections',
            f'DESIGN.md 缺段: {", ".join(s.split(".",1)[0] for s in missing_sections)}',
            1, ''))

    # v1.2 token references in body
    for i, line in enumerate(text.splitlines(), 1):
        for banned in V12_BANNED_TOKENS:
            if banned in line:
                findings.append(_make_finding(
                    path, 4, 'check-D-v1.2-token-reference',
                    f'內文含 v1.2 token `{banned}` 引用，應改為 canonical name',
                    i, line))
                break  # one report per line

    return findings


def _check_longform_slot(path: Path) -> list[dict]:
    """Check E — long-form.html 必有且僅有一個 data-slot="long-form-body"。"""
    findings: list[dict] = []
    if not path.is_file():
        findings.append(_make_finding(
            path, 5, 'check-E-longform-missing',
            'design-cores/long-form.html 不存在',
            1, ''))
        return findings
    text = path.read_text(encoding='utf-8', errors='replace')
    count = len(_SLOT_RE.findall(text))
    if count == 0:
        findings.append(_make_finding(
            path, 5, 'check-E-slot-missing',
            'long-form.html 缺 <section data-slot="long-form-body"> 標記',
            1, ''))
    elif count > 1:
        findings.append(_make_finding(
            path, 5, 'check-E-slot-duplicate',
            f'long-form.html 含 {count} 個 data-slot="long-form-body"（須唯一）',
            1, ''))
    return findings


def _check_dashboard_static(path: Path) -> list[dict]:
    """Check F — dashboard.html 不含 <script> 或外部 src。"""
    findings: list[dict] = []
    if not path.is_file():
        findings.append(_make_finding(
            path, 6, 'check-F-dashboard-missing',
            'design-cores/dashboard.html 不存在',
            1, ''))
        return findings
    text = path.read_text(encoding='utf-8', errors='replace')
    for i, line in enumerate(text.splitlines(), 1):
        if _SCRIPT_TAG.search(line):
            findings.append(_make_finding(
                path, 6, 'check-F-script-tag',
                'dashboard.html 含 <script> tag（須純靜態 SVG/HTML）',
                i, line))
        if _EXT_SRC.search(line):
            findings.append(_make_finding(
                path, 6, 'check-F-external-src',
                'dashboard.html 含外部 src=http(s):// 引用（須 offline-first）',
                i, line))
    return findings


# ────────────────────────────────────────────────────────────────────────────
# Legacy per-file mode (preserved for /book validator interop)
# ────────────────────────────────────────────────────────────────────────────

def _check_swiss_tokens_css(path: Path, text: str) -> list[dict]:
    findings: list[dict] = []
    lines = text.splitlines()

    first_nonempty_idx = next((i for i, ln in enumerate(lines) if ln.strip()), None)
    if first_nonempty_idx is None:
        findings.append(_make_finding(
            path, 20, 'swiss-preset-comment',
            'swiss preset 缺 `/* preset: swiss */` 首行註解（檔案為空）',
            1, ''))
    else:
        first = lines[first_nonempty_idx]
        m = PRESET_HEADER_RE.match(first)
        if not m or m.group(1) != 'swiss':
            findings.append(_make_finding(
                path, 20, 'swiss-preset-comment',
                'swiss preset 缺首行 `/* preset: swiss */` 識別註解',
                first_nonempty_idx + 1, first))

    accent_re = re.compile(r'--accent\s*:')
    if not any(accent_re.search(ln) for ln in lines):
        findings.append(_make_finding(
            path, 21, 'swiss-accent-token',
            'swiss preset 缺 --accent token 定義（IKB blue 必備）',
            1, lines[0] if lines else ''))

    font_decl_re = re.compile(r'(font-family\s*:|--font-[a-z-]*\s*:)', re.I)
    for i, line in enumerate(lines, 1):
        if font_decl_re.search(line) and _SERIF_KW.search(line):
            # 例外：--font-serif 在 swiss 為 sans-alias，允許右側引用 sans-serif fallback
            if '--font-serif' in line and ('var(--font-sans)' in line or 'sans-serif' in line):
                continue
            findings.append(_make_finding(
                path, 22, 'swiss-no-serif',
                'swiss preset font stack 不可含 serif 關鍵字（sans-serif 例外）',
                i, line))

    return findings


def _parse_slide_core_front_matter(text: str) -> tuple[dict, str]:
    m = re.search(
        r'<!--\s*\n?\s*---\s*\n(.*?)\n\s*---\s*',
        text, re.DOTALL,
    )
    if not m:
        return {}, 'YAML front-matter not found (expect `<!-- --- ... --- -->`)'
    body = m.group(1)
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
    findings: list[dict] = []

    if not any(_DATA_LAYOUT.search(ln) for ln in text.splitlines()):
        findings.append(_make_finding(
            path, 30, 'slide-data-layout',
            'slide-core 缺 data-layout="..." 屬性', 1, ''))

    parsed, err = _parse_slide_core_front_matter(text)
    if err:
        findings.append(_make_finding(
            path, 31, 'slide-yaml-front-matter',
            f'YAML front-matter 解析失敗：{err}', 1, ''))
    else:
        if 'layout_id' not in parsed:
            findings.append(_make_finding(
                path, 31, 'slide-yaml-front-matter',
                '缺 layout_id key', 1, ''))
        if 'applies_to' not in parsed:
            findings.append(_make_finding(
                path, 31, 'slide-yaml-front-matter',
                '缺 applies_to key', 1, ''))

    if not _FIGCAPTION.search(text):
        findings.append(_make_finding(
            path, 32, 'slide-figcaption',
            'slide-core 缺 <figcaption> 槽位', 1, ''))

    # class prefix mixing (v1.3: kami / google / swiss + dynamic gen slug all allowed,
    # but single file must be one prefix family)
    prefix_lines: dict[str, int] = {}
    for i, line in enumerate(text.splitlines(), 1):
        for m in _CLASS_ATTR.finditer(line):
            classes = (m.group(1) or m.group(2) or '').split()
            for cls in classes:
                if '-' in cls:
                    pfx = cls.split('-', 1)[0]
                    if pfx in STATIC_PREFIXES:
                        prefix_lines.setdefault(pfx, i)
    if len(prefix_lines) > 1:
        findings.append(_make_finding(
            path, 33, 'slide-class-prefix',
            f'slide-core 同檔混用 prefix: {", ".join(sorted(prefix_lines))}',
            min(prefix_lines.values()), ''))

    return findings


def check_file_legacy(path: Path, rules: dict) -> list[dict]:
    """Per-file legacy lint (Kami warm-serif default + swiss/slide-cores special)."""
    text = path.read_text(encoding='utf-8', errors='replace')
    path_str = str(path).replace('\\', '/')
    if 'swiss-preset/' in path_str and path.suffix.lower() == '.css':
        return _check_swiss_tokens_css(path, text)
    if 'slide-cores/' in path_str and path.suffix.lower() == '.html':
        return _check_slide_core_html(path, text)

    cool_set = {_norm_hex(h) for h in rules['cool_gray_blocklist']}
    findings: list[dict] = []

    def add(inv: int, name: str, msg: str, lineno: int, snippet: str):
        findings.append({
            'file': str(path), 'line': lineno,
            'inv': inv, 'name': name,
            'msg': msg, 'snippet': snippet.strip()[:120],
        })

    for i, line in enumerate(text.splitlines(), 1):
        if _RGBA.search(line):
            in_shadow = 'box-shadow' in line.lower()
            if in_shadow and not rules['allow_rgba_in_box_shadow']:
                add(8, 'no-rgba', 'rgba() in box-shadow — use solid hex token', i, line)
            elif not in_shadow and not rules['allow_rgba_elsewhere']:
                add(8, 'no-rgba',
                    'rgba() outside box-shadow — use solid hex token', i, line)
        if not rules['allow_italic'] and _ITALIC.search(line):
            add(10, 'no-italic',
                'font-style: italic — banned by this design system', i, line)
        if _HEADING.search(line):
            m = _BOLD_HDG.search(line)
            if m:
                add(5, 'heading-weight',
                    f'heading font-weight {m.group(1)} exceeds max '
                    f'{rules["max_heading_weight"]}', i, line)
        m = _LINE_H.search(line)
        if m:
            lh = float(m.group(1))
            cap = rules['max_body_line_height']
            if lh > cap and not any(
                    k in line.lower() for k in ('headline', 'title', 'display')):
                add(6, 'line-height',
                    f'line-height {lh} > {cap} for body text', i, line)
        m = _SHADOW.search(line)
        if m:
            blur = int(m.group(2))
            min_blur = rules['min_shadow_blur_px']
            if blur < min_blur:
                add(9, 'soft-shadow',
                    f'box-shadow blur {blur}px < {min_blur}px — use ring or whisper',
                    i, line)
        for hm in _HEX.finditer(line):
            hx = _norm_hex(hm.group(0))
            if hx in cool_set:
                add(3, 'warm-tones',
                    f'{hx} is a cool-gray — use a warm-toned palette token',
                    i, line)

    return findings


# ────────────────────────────────────────────────────────────────────────────
# Main
# ────────────────────────────────────────────────────────────────────────────

def _print_findings(all_findings: list[dict], file_count: int) -> None:
    if not all_findings:
        print(f'✅  /design lint pass — {file_count} file(s) checked, no violations.')
        return
    by_file: dict[str, list] = {}
    for f in all_findings:
        by_file.setdefault(f['file'], []).append(f)
    print(f'❌  {len(all_findings)} violation(s) in {len(by_file)} file(s):\n')
    for filepath, ff in by_file.items():
        print(f'  {filepath}')
        for f in ff:
            print(f"    L{f['line']}  [#{f['inv']} {f['name']}] {f['msg']}")
            if f['snippet']:
                print(f"           {f['snippet']}")
        print()


def main():
    args = sys.argv[1:]
    rules_path = None
    if '--rules' in args:
        idx = args.index('--rules')
        if idx + 1 >= len(args):
            print('--rules requires a path argument', file=sys.stderr)
            sys.exit(2)
        rules_path = Path(args[idx + 1])
        args = args[:idx] + args[idx + 2:]

    rules = load_rules(rules_path) if rules_path else DEFAULT_RULES

    # Resolve target
    if not args:
        # No-arg mode: try project root via cwd
        target = Path.cwd()
    else:
        target = Path(args[0])
        if not target.exists():
            print(f'Error: {target} not found', file=sys.stderr)
            sys.exit(2)

    # Mode dispatch: project root vs legacy per-file
    if _is_project_root(target):
        findings = check_project_root(target)
        _print_findings(findings, 5)  # 5 artifact slots
        sys.exit(1 if findings else 0)
    else:
        files = (
            list(target.rglob('*.html')) + list(target.rglob('*.css'))
            if target.is_dir() else [target]
        )
        if not files:
            print('No .html or .css files found.')
            sys.exit(0)
        all_findings: list[dict] = []
        for f in sorted(files):
            all_findings.extend(check_file_legacy(f, rules))
        _print_findings(all_findings, len(files))
        sys.exit(1 if all_findings else 0)


if __name__ == '__main__':
    main()
