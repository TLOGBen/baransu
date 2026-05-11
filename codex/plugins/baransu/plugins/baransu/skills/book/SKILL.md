---
name: book
description: 'Use When the user wants to convert any content source into a beautifully
  rendered, browser-ready HTML document. Do Run a three-stage pipeline: Acquire (URL
  / slug / local path / text) → Synthesize (classify content type, extract structure)
  → Render (Kami-themed HTML + SVG, quality-gated). Trigger On ''/book'', ''轉成 book'',
  ''做成 HTML book'', ''存成 book''.'
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

Converts any content into a Kami-themed, browser-ready HTML book saved to `.claude/book/{slug}.html`.

**User-facing language**: 繁體中文. All output shown to the user must be in Traditional Chinese.

---

## Stage 0 — Environment Self-Check

### 0. --format 旗標解析

解析使用者呼叫中的 `--format` 旗標：

- 支援值：`html` | `pdf` | `ppt` | `all`
- 若未提供 `--format`：預設為 `html`
- 若值不合法（非 html/pdf/ppt/all）：輸出「`--format` 值不合法。支援：html | pdf | ppt | all」並停止（不呼叫 install-deps.ts）
- 設定 `$FORMAT` 供後續所有 Stage 使用

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

Run the format-aware dependency installer:

```bash
npx tsx "$CLAUDE_SKILL_DIR/scripts/install-deps.ts" --format $FORMAT
```

若腳本回傳非零 exit code：
- 輸出錯誤訊息（腳本已列出詳情）並停止，不進入 Stage 1
- 若 `$FORMAT` 含 `pdf`：確認 WeasyPrint 可用
- 若 `$FORMAT` 含 `ppt`：確認 playwright + pptxgenjs 可用

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

## Stage 2A — Synthesize（長文，所有 format）

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

**$SLUG 只在 Stage 2A 推導一次，Stage 2B 和所有 Render 步驟繼承相同 $SLUG，不另行推導。**

---

## Stage 2B — Synthesize（投影片，僅 --format ppt 或 all）

> 僅在 `$FORMAT` 為 `ppt` 或 `all` 時執行。使用與 Stage 2A 相同的 `$RAW_CONTENT` 作為輸入，`$SLUG` 繼承自 Stage 2A。

從 `$RAW_CONTENT` 提取投影片結構 `$STRUCTURE_SLIDES`。

### $STRUCTURE_SLIDES schema

```typescript
interface SlideStructure {
  slides: Slide[];
}

interface Slide {
  layout_type: 'cover' | 'section' | 'content' | 'data' | 'closing';
  heading: string;
  body_bullets?: string[];  // 用於 content 版型，通常 3-5 條
  has_svg?: boolean;        // 若 true，在此 slide 生成 inline SVG
}
```

### 版型說明

| 版型 | 用途 |
|------|------|
| `cover` | 封面。大標題 + 副標題 + 可選說明行，無 bullets |
| `section` | 章節分隔頁。單一大標題居中，背景使用 `--brand-tint` |
| `content` | 標準內容頁。heading + 3-5 條 body_bullets + 可選 SVG |
| `data` | 全幅資料 / 圖表頁。heading + 全幅 SVG 或資料表，無 bullets |
| `closing` | 結語。摘要句 + 可選 CTA，無 bullets |

### 數量與結構約束

- 總 slide 數量：**6-12 張**
- 第一張必為 `cover`，最後一張必為 `closing`
- `heading` 為必填；`body_bullets` 和 `has_svg` 為可選

儲存結果為 `$STRUCTURE_SLIDES`。

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

### 4. SVG 生成規格

#### 色彩 token（SVG 角色）

所有 SVG fill / stroke **禁用 `rgba()`**，一律使用 solid hex token：

| SVG 角色 | CSS 變數 | Hex 值 |
|----------|----------|--------|
| Canvas 底色 | `--parchment` | `#f5f4ed` |
| 標準節點填色 | `--ivory` | `#faf9f5` |
| 標準節點描邊 / 主要文字 | `--near-black` | `#141413` |
| 焦點節點填色 | `--brand-tint` | `#EEF2F7` |
| 焦點節點描邊 | `--brand` | `#1B365D` |
| 標準箭頭 / 次要文字 | `--olive` | `#504e49` |

> CSS `box-shadow` 中的 `rgba()` 不受限（非 SVG 屬性）。

#### 必備 `<defs>` 片段（每張 SVG 開頭必加）

```svg
<defs>
  <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">
    <circle cx="1" cy="1" r="0.9" fill="#E3E2DC"/>
  </pattern>
</defs>
<rect width="100%" height="100%" fill="#f5f4ed"/>
<rect width="100%" height="100%" fill="url(#dots)" opacity="0.55"/>
```

#### 箭頭：chevron path（禁 `<marker orient="auto">`）

```svg
<path d="M2 1 L8 5 L2 9" fill="none" stroke="#504e49" stroke-width="1.5" stroke-linecap="round"/>
```

#### 抗 slop 精度約束

- 所有座標、寬度、間距必須是 **4 的倍數**
- 節點寬只有三層：**128 / 144 / 160**
- 節點高：**32**（pill）/ **64**（standard）
- 焦點節點（`--brand` 描邊 + `--brand-tint` 填色）最多 **1-2 個**
- `<text y>` ≥ font-size × 1.2（防文字切頂）
- 箭頭 endpoint 精確落在節點邊緣

#### 嵌入字體校正（嵌入 A4 後 scale ≈ 0.47）

| 角色 | 字體大小 |
|------|--------|
| H2 / 焦點節點 | 24 |
| Body / 標準文字 | 22-24 |
| H3 / 子標籤 | 18-20 |
| Caption | 15-16 |
| Mono tag | 14 |

#### 14 型圖表路由決策樹（first-match）

依資料形狀由上至下找第一個匹配項：

| 資料形狀 | 選用圖表 |
|---------|---------|
| OHLC / per-day price | Candlestick |
| +/- 貢獻加總 | Waterfall |
| 一系列，加總 ~100%，項目 ≤ 6 | Donut |
| 一系列，加總 ~100%，項目 ≥ 7 | Horizontal Bar |
| 兩條以上時間序列 | Line |
| 一條時間序列，大量變化主導 | Bar |
| 多類別同時間快照，2+ 系列 | Grouped Bar |
| 2×2 策略定位 | Quadrant |
| 層次資料 depth ≥ 2 | Tree |
| 有決策分支的流程 | Flowchart |
| 跨角色流程 ≥ 3 actors | Swimlane |
| 2-3 群集合重疊 | Venn |
| 系統元件 + 連線 | Architecture |
| 時間軸 + 里程碑 | Timeline |

> 無法匹配時 → fallback 到 **Architecture**（通用型）。

---

### §5 PDF pipeline（if `--format` 包含 `pdf` 或 `all`）

> 僅當 `$FORMAT` 為 `pdf` 或 `all` 時執行。

**步驟一：HTML 預處理**

取 Stage 3 §2-§4 生成的 long-form HTML 內容，注入下列 `<style>` 於 `<head>` 末尾：

```html
<style>
  .toc-wrap { display: none; }
  @page { margin: 2cm; }
  body { font-family: 'TsangerJinKai02', Georgia, serif; }
</style>
```

將修改後的 HTML 存至臨時路徑 `{patched_html}`（例如 `.claude/book/{$SLUG}-pdf-patch.html`）。

**步驟二：呼叫 WeasyPrint**

```bash
python3 -m weasyprint "{patched_html}" ".claude/book/{$SLUG}.pdf"
```

若命令失敗（exit code ≠ 0）：輸出警告 `⚠️ PDF 生成失敗：WeasyPrint 錯誤`，繼續執行其他格式，不停止整個流程。

---

### §6 PPTX pipeline（if `--format` 包含 `ppt` 或 `all`）

> 僅當 `$FORMAT` 為 `ppt` 或 `all` 時執行。依賴 Stage 2B 生成的 `$STRUCTURE_SLIDES`。

**步驟一：生成 slide HTML**

依 `$STRUCTURE_SLIDES` 的每個 slide 物件，對應 `references/slide-template.html` 的 5 種版型（cover / section / content / data / closing），生成 slide HTML 檔案：

- `<body style="width:960px; height:540px; margin:0; padding:0;">`
- 每個 slide 包在 `<div class="slide" data-layout="{layout_type}">` 中
- 文字內容使用 `<h1>`/`<h2>` 和 `<ul><li>` 呈現
- 若 `has_svg` 為 true，插入對應的 inline SVG

**步驟二：驗證 slide HTML**

在呼叫 html2pptx.js 之前，驗證三項：

1. `<body>` 的 `width` 樣式包含 `960`
2. 文件包含至少一個 `.slide` 元素（`class="slide"`）
3. 不含 `background-image`

若任何一項驗證失敗：輸出 `⚠️ Slide HTML 驗證失敗：{失敗原因}`，不呼叫 html2pptx.js，其他格式繼續。

**步驟三：呼叫 html2pptx.js**

```bash
node "$CLAUDE_SKILL_DIR/scripts/html2pptx.js" "{slide_html_path}" ".claude/book/{$SLUG}.pptx"
```

若命令失敗（exit code ≠ 0）：標記 `PPT：失敗（詳見上方錯誤）`，繼續其他格式，不停止整個流程。

---

### 7. Write the output file

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
✅ 已儲存：
  HTML：.claude/book/{$SLUG}.html
  PDF： .claude/book/{$SLUG}.pdf        （若 $FORMAT 包含 pdf，且生成成功）
  PPT： .claude/book/{$SLUG}.pptx       （若 $FORMAT 包含 ppt，且生成成功）
        PPT：失敗（詳見上方錯誤）          （若 html2pptx.js 回傳非零 exit code）
  預覽：.claude/book/{$SLUG}-preview.png
內容類型：{$CONTENT_TYPE}
SVG 圖解：{N} 張
字數：約 {word_count} 詞
```

> - HTML 行**必有**（所有 format 皆輸出 HTML）
> - PDF 行：僅 `--format pdf` 或 `--format all` 時出現
> - PPT 行：僅 `--format ppt` 或 `--format all` 時出現；PPTX 生成失敗時改為「PPT：失敗（詳見上方錯誤）」
> - 預覽截圖（PNG）：永遠出現（browser-use 截圖在 Stage 4 §2 執行）
> - 不在 Stage 4 重新推導 `$SLUG`；繼承 Stage 2A §4 推導的值

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
