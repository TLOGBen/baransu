---
name: book
description: "Use When the user wants to convert any content source into a beautifully rendered, browser-ready HTML document. Do Run a three-stage pipeline: Acquire (URL / slug / local path / text) → Synthesize (classify content type, extract structure) → Render (Kami-themed HTML + SVG, quality-gated). Trigger On '/book', '轉成 book', '做成 HTML book', '存成 book'."
argument-hint: "<url | slug | path | text>"
user-invocable: true
---

Converts any content into a Kami-themed, browser-ready HTML book saved to `.claude/book/{slug}.html`.

**User-facing language**: 繁體中文. All output shown to the user must be in Traditional Chinese.

---

## Stage 0 — Environment Self-Check

### 1. Python check

```bash
python3 --version 2>/dev/null
```

If this fails: output 「Python 3.8+ 未安裝，無法繼續。請先安裝 Python: https://python.org」 and stop.

### 2. Platform detection

- **WSL2**: `grep -qi microsoft /proc/version 2>/dev/null && echo wsl2` → set `$PLATFORM=WSL2`
- **macOS**: `uname -s 2>/dev/null | grep -qi darwin && echo macos` → set `$PLATFORM=macOS`
- **Otherwise**: set `$PLATFORM=Linux`

### 3. markitdown check

```bash
python3 -m markitdown --version 2>/dev/null
```

If not installed (or `browser-use` is also missing): run `npx tsx "$CLAUDE_SKILL_DIR/scripts/install-deps.ts"`.
The script installs both `markitdown` and `browser-use` in one pass.
If installation fails: output 「依賴安裝失敗，請手動執行：pip install markitdown browser-use」 and stop.

### 4. Output directory

Ensure `.claude/book/` exists relative to the project root:

```bash
mkdir -p ".claude/book"
```

---

## Stage 1 — Acquire

Route the input argument to the correct acquisition path. The goal is to produce a
**plain-text or Markdown body** stored in a temp variable `$RAW_CONTENT`.

### 1. URL (`http://` or `https://` prefix)

Follow the same proxy cascade as `/read` Stage 1 §9:

```
Layer 1: curl -sL "https://defuddle.md/{url}" → check word count > 100 and lines > 5
Layer 2: curl -sL "https://r.jina.ai/{url}"   → same quality checks
Layer 3: curl -sL "{url}" -H "User-Agent: Mozilla/5.0"
```

Store the best result in a temp file `/tmp/book-raw-{slug}.{ext}`.
Convert to Markdown via `markitdown "/tmp/book-raw-{slug}.{ext}" -o "/tmp/book-body-{slug}.md" 2>/dev/null`.
Set `$RAW_CONTENT` to the content of `/tmp/book-body-{slug}.md`.

If all three layers fail or produce < 100 words:
- output 「Acquire 失敗：{url} 無法取得內容。請改用 --text「貼入文字」或確認 URL 是否可公開存取。」 and stop.

### 2. `/read` slug or `/learn` digest slug

If the input matches the slug pattern (no `http://`, `./`, `/`, `*` prefix and no `--` prefix):

Check the following paths in order:
1. `.claude/learn/digests/{slug}.md`
2. `.claude/read/material/{slug}/index.md`

If found: read the file; set `$RAW_CONTENT` to its body (strip YAML frontmatter).
If not found: treat as a bare topic → go to §4 (plain text).

### 3. Local file path (`./`, `/`, or existing file)

```bash
test -e "{input}" && echo "exists" || echo "missing"
```

If exists: run `markitdown "{input}" -o "/tmp/book-body-local.md" 2>/dev/null`; set `$RAW_CONTENT`.
If missing: output 「找不到檔案：{input}」 and stop.

### 4. Plain text / bare topic

If the input is a bare topic (no URL, no file, no known slug): set `$RAW_CONTENT = input` directly.
This enables `/book "agent 協作方式"` where the user types the content inline.

### 5. `--text "…"` flag

User can pass `--text "…"` to explicitly force plain-text mode regardless of input shape.
Set `$RAW_CONTENT` to the quoted string.

### Acquire completion

Output one progress line:
「已取得內容（{word_count} 詞），開始分析…」

---

## Stage 2 — Synthesize

Receives `$RAW_CONTENT`. Produces `$STRUCTURE` (a JSON-like outline) and `$CONTENT_TYPE`.

### 1. Read the perception guide

Read `references/perception-guide.md` before classifying. That file is authoritative for:
- Content type taxonomy (Technical / Narrative / Research)
- Visual treatment per type
- SVG strategy per type
- Synthesis length limits (4–8 sections, ≤ 1800 words in final HTML)

### 2. Classify content type

Based on the perception guide signals, assign `$CONTENT_TYPE` to one of:
- `technical` — code, how-to, architecture, tool guides
- `narrative` — essays, opinions, threads, stories
- `research` — analyses, reports, multi-source synthesis

Output one line: 「內容類型偵測：{$CONTENT_TYPE}」

### 3. Extract structure

From `$RAW_CONTENT`, extract:
- **Title** (first `# ` heading, or infer from opening sentence)
- **Kicker** (2–4 word category label)
- **Subtitle** (one-sentence summary of the whole piece)
- **4–8 sections**, each with:
  - Section heading
  - 1–3 key claims (concrete, specific — no vague summaries)
  - Whether this section benefits from an SVG diagram

Store as `$STRUCTURE`.

Apply synthesis length limits from the perception guide. Remaining content → reference as 延伸閱讀 at the bottom.

### 4. Determine slug

Derive `$SLUG` from the title:
- Lowercase all characters
- Replace spaces and non-ASCII with hyphens
- Collapse consecutive hyphens
- Strip leading/trailing hyphens
- Truncate to 60 chars

Check `.claude/book/` for existing files with the same slug.
If a collision exists: append `_v2`, `_v3`, etc.

---

## Stage 3 — Render

Produces a complete HTML file at `.claude/book/{$SLUG}.html`.

### 1. Read the design system

Before generating any HTML:

1. Read `references/golden-template.html` for the exact CSS tokens, component patterns, and SVG conventions.
2. Read `$CLAUDE_SKILL_DIR/../.././../design/references/paper-preset.md` (or locate `design/references/paper-preset.md` via `find`) for the full Kami design token definitions.

The golden template is a show-by-example contract — every element in the output HTML should have a visual counterpart in the template. Do not invent new CSS patterns; extend only within Kami constraints.

### 2. Generate HTML structure

Produce the full HTML document using the golden-template.html structure:

```
<head> with Kami CSS (copy from golden-template, fill {{TITLE}})
<nav class="toc-wrap"> with <a href="#sN"> for each section
<article class="paper">
  <header> with kicker, h1, subtitle, meta
  <section id="sN"> for each section (4–8 sections)
  <footer>
</article>
<script> for TOC active-link logic (copy from golden-template)
```

### 3. Section content rules

For each section from `$STRUCTURE`:

- Open with `<h2><span class="sec-num">0N</span>{Section Title}</h2>`
- Write 1–3 paragraphs expanding the key claims using language from `$RAW_CONTENT`
- Immediately follow with a `<figure class="diagram">` block containing an SVG if the section was flagged for it
- Use `.callout`, `.card-grid`, `table.cmp`, or `.tradeoff-row` components from the template where they improve readability

**No improvisation**: every component class must exist in the golden-template CSS. If a component isn't in the template, use plain `<p>` — do not add new CSS.

### 4. SVG generation rules

Follow the SVG conventions in `references/golden-template.html` comment block and `references/perception-guide.md §SVG Strategy by Type`:

- Minimum 1 SVG per document; place the first SVG in section 1 or 2
- Use Kami stroke colours only: `#1B365D` (brand), `#504e49` (olive), `#6b6a64` (stone)
- stroke-width: 1.5 for primary paths, 1 for secondary
- Fill: `none` for paths; `rgba(27,54,93,0.07)` for node backgrounds
- Text labels: `font-family="sans-serif"` `font-size="11"` `fill="#504e49"`
- Every SVG must have explicit `width`, `height`, and `viewBox`
- Include `<defs>` with arrow markers if the diagram uses directed lines

Reuse the exact `<defs>` marker snippet from golden-template.html's comment block.

### 5. Write the output file

Write the complete HTML to `.claude/book/{$SLUG}.html`.

Do not write partial content — write the full file in one operation.

---

## Stage 4 — Validate & Report

### 1. Run quality gate

```bash
npx tsx "$CLAUDE_SKILL_DIR/scripts/validate-output.ts" ".claude/book/{$SLUG}.html"
```

Exit codes:
- `0` (GATE PASS): proceed to completion report
- `1` (GATE FAIL): read the failure lines printed to stdout; fix the specific failing element and re-write the file; re-run the gate once more
  - If the gate fails a second time: output 「品質閘第二次失敗，請手動開啟 .claude/book/{$SLUG}.html 確認問題。」 and stop.
- `2` (usage error): script invocation was wrong — fix and re-run

### 2. Visual render verification (browser-use)

After GATE PASS, verify layout with `browser-use` (guaranteed installed by Stage 0):

```bash
# Get absolute path
ABS_PATH=$(realpath ".claude/book/{$SLUG}.html")

# Open in headless browser
browser-use open "file://$ABS_PATH"

# Full-page screenshot → saved as preview
browser-use screenshot ".claude/book/{$SLUG}-preview.png" --full

# Check horizontal overflow (跑版)
OVERFLOW=$(browser-use eval "document.documentElement.scrollWidth > window.innerWidth")

# Verify key structural elements exist
HAS_PAPER=$(browser-use eval "!!document.querySelector('.paper')")
HAS_H1=$(browser-use eval "!!document.querySelector('h1')")
HAS_H2=$(browser-use eval "!!document.querySelector('h2')")

# Close session
browser-use close
```

Interpret results:
- If `OVERFLOW` is `true`: output 「⚠ 跑版偵測：有橫向溢出，請開啟 .claude/book/{$SLUG}-preview.png 手動確認。」
- If `HAS_PAPER`, `HAS_H1`, or `HAS_H2` is `false`: output 「⚠ 結構元素缺失：{element} 未出現在頁面中。」
- If `browser-use open` fails (e.g. daemon error): output 「⚠ 視覺驗證無法執行，請手動開啟 .claude/book/{$SLUG}.html。」 and continue to completion report.
- If all checks pass: output 「✅ 視覺驗證通過」

### 3. Completion report

Output (繁中):

```
✅ 已儲存：.claude/book/{$SLUG}.html
內容類型：{$CONTENT_TYPE}
SVG 圖解：{N} 張
字數：約 {word_count} 詞
預覽截圖：.claude/book/{$SLUG}-preview.png
```

---

## Constraints

- **Kami only**: all visual elements follow `design/references/paper-preset.md` and `references/golden-template.html`. No inline hex colours; use named CSS variables.
- **No new CSS patterns**: every class in the output HTML must exist in the golden-template CSS block. Extend within Kami; don't invent outside it.
- **SVG required**: a document with 0 SVG diagrams fails the quality gate and must be fixed before completion.
- **Length cap**: final HTML body ≤ 1800 words. Excess goes into a 延伸閱讀 link block.
- **No LLM-generated commentary**: the rendered HTML contains the source content, structured and styled — not Claude's own analysis. The Synthesize stage extracts; the Render stage presents.
- **Partial failure**: if Acquire fails for one of multiple inputs, report the failure per-input and continue with the rest.

## Gotchas

- **SPA / login walls**: X.com, LinkedIn, paywalled pages often fail the proxy cascade. Report the failure clearly; don't silently produce an empty or skeleton page.
- **markitdown escaped underscores in URLs**: when markitdown converts HTML, it sometimes escapes `_` to `\_` inside image URLs. Run a cleanup pass on all `![...](\url)` patterns before processing.
- **SVG path closure**: always close `<path>` elements with `/>`; validate-output.ts checks SVG tag balance but not path syntax. Keep SVG shapes simple (lines, rects, circles, ellipses, simple paths).
- **Kami token lookup**: if `design/references/paper-preset.md` cannot be found via relative path, use `find . -path "*/design/references/paper-preset.md" -not -path "*/cache/*" | head -1` to locate it.
