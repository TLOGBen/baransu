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

## Outcome Contract

- **Outcome**: Convert any content source (URL / slug / local file / text) through the three stages Acquire → Synthesize → Render into a Kami-themed, browser-openable HTML book.
- **Done when**: The output HTML passes all GATEs of scripts/validate-output.ts (exit 0), and the file lands at `.claude/book/{slug}.html`.
- **Evidence**: The execution result of validate-output.ts (GATE A-E / F / G / J / K / L all green or a legitimate SKIP).
- **Output**: `.claude/book/{slug}.html`; per `--format` additionally includes `.pdf` / `.pptx`.
- **Automation**: ultracode=neutral, loop=drivable（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）

## Stage 0 — Environment Self-Check

> This SKILL.md adopts Fact-Verification Principle #0 (see the Stage 2A §0 "Fact-Verification Principle #0" section below): before synthesizing long-form text, whenever a concrete product / version / person-name + title pattern is detected, search the web verification is forced; 0 results triggers an ask the user directly with numbered options, then stop for the user's reply block.

### 1. Design context soft-read

Runs before all other Stage 0 steps. Follows the same soft-read pattern as /design / /analyze, bringing the current preset's design philosophy into context as advisory framing.

1. Resolve project root: `git rev-parse --show-toplevel 2>/dev/null`; on failure use cwd.
2. Attempt to read the following files (all best-effort, **failing all of them does not abort Stage 0**, only a stderr warning):
   - `{project_root}/DESIGN.md`: the current preset's nine-section design spec. Read into context for later Stage 2A typography selection / Stage 3 SVG token decisions reference.
   - `{project_root}/tokens.css` first line: parse the preset slug (e.g. `/* preset: kami */` → `kami`), store as the `$STYLE` prepared value (later overridden if the user explicitly passes `--style`, otherwise this value is kept).
3. If `DESIGN.md` exists → stderr `已載入 DESIGN.md，視覺規格已參考（preset=$STYLE）`.
4. If `DESIGN.md` does not exist → stderr `未找到 DESIGN.md；建議先跑 /baransu:design preset <name>。本次 /book 將使用 fallback 模板，視覺風格可能與 preset 不一致`, then continue.

The DESIGN.md content read in this step is, in Stage 4, passed to the style-reviewer as a spec anchor depending on whether the user triggers `/baransu:review --include=style`; in the normal /book flow it serves only as a generation-time advisory and affects no gate.

### 2. --format flag parsing

Parse the `--format` flag in the user's invocation:

- Supported values: `html` | `pdf` | `ppt` | `all`
- If `--format` is not provided: default to `html`
- If the value is invalid (not html/pdf/ppt/all): output 「`--format` 值不合法。支援：html | pdf | ppt | all」 and stop (do not call install-deps.ts)
- Set `$FORMAT` for use by all later Stages

### 3. --style flag parsing

Parse the `--style` flag in the user's invocation (v1.3 PPT + HTML dual mode):

- Supported values: `kami` | `google-design` | `swiss` | user-supplied gen slug (pattern `/^[a-z][a-z0-9-]{1,15}$/`, must have run `/baransu:design gen --slug <slug>` first)
- If `--style` is not provided: parse from `{project_root}/tokens.css` first line `/* preset: <slug> */`; if neither is present, default to `kami`
- Invalid value: output 「--style 不合法。支援 v1.3 三 preset 或已註冊 gen slug」 and stop
- HTML mode dynamically reads the template from `{project_root}/design-cores/long-form.html`; PPT mode dynamically reads the layout from `{project_root}/slide-cores/`
- Set `$STYLE` for use by later Stages (Stage 3 tokens.css tie-break / GATE-F prefix matching reads `$STYLE`)

### 4. Python check

```bash
python3 --version 2>/dev/null
```

If this fails: output 「Python 3.8+ 未安裝，無法繼續。請先安裝 Python: https://python.org」 and stop.

### 5. Platform detection

- **WSL2**: `grep -qi microsoft /proc/version 2>/dev/null && echo wsl2` → set `$PLATFORM=WSL2`
- **macOS**: `uname -s 2>/dev/null | grep -qi darwin && echo macos` → set `$PLATFORM=macOS`
- **Otherwise**: set `$PLATFORM=Linux`

### 6. markitdown check

```bash
python3 -m markitdown --version 2>/dev/null
```

Run the format-aware dependency installer:

```bash
npx tsx "./scripts/install-deps.ts" --format $FORMAT
```

If the script returns a non-zero exit code:
- Output the error message (the script has already listed details) and stop; do not enter Stage 1
- If `$FORMAT` contains `pdf`: confirm WeasyPrint is available
- If `$FORMAT` contains `ppt`: confirm playwright + pptxgenjs are available

### 7. Output directory

Ensure `.claude/book/` exists relative to the project root:

```bash
mkdir -p ".claude/book"
```

---

## Stage 0b — 🔴 CHECKPOINT — Pre-interview Gate (audience / hard-constraint front-loading)

**Before** Stage 1 acquires `$RAW_CONTENT`, first suppress 50% of the uncertainty. Pattern aligned with /design Gen Mode Step 1: use a **single ask the user directly with numbered options, then stop for the user's reply batch** (4 questions presented together, not blocking question-by-question) to align audience, purpose, style leaning, and hard constraints.

### Skip conditions (the whole section is skipped if any one holds)

- The `--auto` or `--no-interview` flag is present
- The input is a `/read` slug / `/learn` digest slug (audience + purpose are already implicit in the original capture metadata)
- The input is `--text "…"` with word count < 200 (an extremely short inline is not worth asking about)

When skipping, print one stderr line: 「Stage 0b skipped: {reason}」, then continue to Stage 1.

### Interview questions (batched, 4 questions presented together)

1. **Audience** — 「主要讀者是誰？（例如：技術同儕 / 產品 PM / 非技術主管 / 公開讀者 / 自己備忘）」
2. **Purpose and duration** — 「這份 book 的使用情境？（例如：5 分鐘速讀 / 30 分鐘深讀 / 簡報前置 / 長期參考文件）」
3. **Style leaning** — 「視覺密度偏哪邊？（例如：高密度技術文件 / 留白敘事散文 / 多圖表 research 報告 / 隨 preset 預設）」
4. **Hard constraints** — 「有沒有必須 / 不要的元素？（例如：必含某段內文、不要 SVG diagram、限定字數、特定 callout 數）」

Unanswered / 「隨預設」 always follows the preset's existing default and is not separately stored. Answered content is written into `$INTERVIEW_BRIEF` (plain text 4-8 lines), prepended as advisory framing before Stage 2A §1 classification, and **does not override** the existing A/B/C classification logic in `references/perception-guide.md` (on conflict, perception-guide wins; the brief is only a nudge).

### Completion output

One line: 「訪談完成：受眾={...} / 用途={...} / 風格={...} / 約束={...}，進入 Stage 1。」

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

## Stage 2A — Synthesize (long-form, all formats)

Receives `$RAW_CONTENT`. Produces `$STRUCTURE` (a JSON-like outline) and `$CONTENT_TYPE`.

### 0. Fact-Verification Principle #0

**Purpose**: run a fact gate before long-form synthesis enters §1 classification, preventing hallucinated concrete specs (fabricated version numbers, fabricated person titles) from being written into the final HTML. Corresponds to REQ-006 Scenario 1 / Criteria C6. Historical case: 「Linear MCP v3.4.7 released 2025-09-15」 is fabricated, but if not verified it would be rendered into the book as established fact.

**Trigger regex** (soft-match against the full `$RAW_CONTENT`; not all hits are required and a miss is not an error — it only serves as a signal to trigger search the web):

```
/([A-Z][a-zA-Z]+\s+(MCP|SDK|CLI|API)?\s*v?\d+(\.\d+)*)|([A-Z][a-z]+\s+[A-Z][a-z]+(\s|,)+(CEO|CTO|founder|engineer))/
```

Explanation:
- First-half alternation: product name (capitalized word) + optional MCP/SDK/CLI/API + optional `v` + one or more dot-separated numbers → matches such as 「Linear MCP v3.4.7」「Anthropic SDK 0.39」.
- Second-half alternation: person name (two capitalized words) + space or comma + title (CEO/CTO/founder/engineer) → matches such as 「Jane Doe, CTO」.

**Flow on hit** (for each matched `{hit}`):

1. **Sanitize `{hit}` before query**: first strip all `"` (`U+0022`) characters inside `{hit}` (the regex captures legitimate identifier/version strings, which normally contain no quote; if present it is noise or adversarial input). The sanitized `{hit_clean}` is then passed to the next step.
2. Run `search the web`, query template: `"{hit_clean}" release notes` or `"{hit_clean}" announcement` (for person-name hits use `"{hit_clean}" announcement` / `"{hit_clean}" interview` instead).
3. If search the web returns **0 results** → 🛑 STOP — Fact-verify pending: via `numbered-options question` show: 「Fact-verify pending: '{hit_clean}' 在 search the web 0 結果。選擇：強制繼續 / 改用 `--text` 餵已驗證版本 / 中止本次 /book」. Wait for the user's choice before deciding whether to enter §1.
4. If search the web returns **≥ 1 result** → treat as fact-verifiable, continue, but still add the hit to the 「Sources」 list at the end of `$STRUCTURE` (handled together in the Stage 2A §4 extract phase).

**Flow on no hit**: enter §1 classification directly.

**Boundary**: the regex is a soft trigger, not a hard match — a miss does not mean the content is necessarily true, and the pattern will be expanded in the future based on telemetry results. **Test fixture**: the string `Linear MCP v3.4.7 released 2025-09-15` is fabricated and is expected to trigger the regex, return 0 search the web results, and go through the ask flow (must not silently continue).

### 1. Classify content type

Do a rough keyword + structure scan over `$RAW_CONTENT` and first guess which category `$CONTENT_TYPE` falls into; if the boundary is unclear (e.g. mixed narrative+technical / a brand-new type / hard to tell multi-source synthesis vs single-piece analysis), **only then read** `references/perception-guide.md` to make the final classification.

`perception-guide.md` contains the full taxonomy (Technical / Narrative / Research), each category's visual-treatment strategy, SVG strategy, and synthesis length caps (4–8 sections, ≤1800 words).

### 2. Decide $CONTENT_TYPE

Based on the perception guide signals, assign `$CONTENT_TYPE` to one of:
- `technical` — code, how-to, architecture, tool guides
- `narrative` — essays, opinions, threads, stories
- `research` — analyses, reports, multi-source synthesis

Output one line: 「內容類型偵測：{$CONTENT_TYPE}」

### 3. Two-layer decision tree (Layer 1 content type → Layer 2 diagram structure)

The Stage 2A selection splits into two layers, **the order must not be reversed**:

- **Layer 1 (content type → HTML layout density)**: the `$CONTENT_TYPE` already produced by §2 (A=`technical` / B=`narrative` / C=`research`) determines the whole HTML's layout style — whether the TOC is expanded, number of cards, density, callout style, etc., all given separately for the A/B/C categories by `references/perception-guide.md`. If §1 did not read `references/perception-guide.md`, read it before applying Layer 1, and take the layout density and visual-treatment rules corresponding to that $CONTENT_TYPE.
- **Layer 2 (13-type selection → per-section diagram structure)**: each section containing a diagram independently looks up the Stage 3 §4 「13 型 selection 表」, picking one diagram type based on that section's data shape (architecture / flowchart / sequence / ...).

The two axes are orthogonal: Layer 1 controls layout, Layer 2 controls each section's SVG structure; do Layer 1 first, then Layer 2, deciding each section independently without inheriting the previous section's choice.

### 4. Extract structure

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

### 5. Determine slug

Derive `$SLUG` from the title:
- Lowercase all characters
- Replace spaces and non-ASCII with hyphens
- Collapse consecutive hyphens
- Strip leading/trailing hyphens
- Truncate to 60 chars

Check `.claude/book/` for existing files with the same slug.
If a collision exists: append `_v2`, `_v3`, etc., and **output one Traditional-Chinese notice line so the renamed output is not silent** (notify, not a blocking PAUSE): 「偵測到既有 {slug}.html，本次另存為 {slug}_v2.html（如要覆寫請刪除舊檔後重跑）」, then continue.

**$SLUG is derived only once in Stage 2A; Stage 2B and all Render steps inherit the same $SLUG and do not re-derive it.**

---

## Stage 2B — Synthesize (slides, only --format ppt or all)

Runs only when `$FORMAT` ∈ {`ppt`, `all`}; produces `$STRUCTURE_SLIDES` (6–12 slides, first page fixed as `cover`, last page conditionally `closing`). **The layout is not hard-coded**: dynamically read the YAML front-matter registration decision table of `{project_root}/slide-cores/*.html`, assigning layout_type via first-match + positional override.

**Rule details (10-row decision table / closing condition recognition / graceful degradation / `$STRUCTURE_SLIDES` schema) → read `references/slide-synthesis.md`.**
## Stage 3 — Render

Produces a complete HTML file at `.claude/book/{$SLUG}.html`.

### 1. Read the design system

Before generating any HTML:

1. **Sole token source**: read `{project_root}/tokens.css` (written by `/baransu:design preset <style>`; this skill only reads, never modifies). This rule **applies to both** `--format ppt` and `--format html`.
   - If `{project_root}/tokens.css` **does not exist** → error 「請先跑 `/baransu:design preset <style>`（kami / google-design / swiss）」 and **abort Stage 3**.
   - tokens.css begins with a preset-identifying comment (`/* preset: kami */` / `/* preset: google-design */` / `/* preset: swiss */` or a user-supplied gen slug), for the `$STYLE` variable parsed in Stage 0 to do a tie-break comparison in GATE-F.
2. **v1.3 long-form template SSOT dynamic read**: prefer reading `{project_root}/design-cores/long-form.html`, treating `<section data-slot="long-form-body">` as the body insertion point.
   - File **exists but fails to read** (malformed / chmod 000 / 0 bytes) → **hard fail**, no silent fallback; stderr 「long-form.html 讀取失敗：{原因}」, abort Stage 3.
   - File **does not exist** → fall back to `references/golden-template.html` (the v1.2 Kami-style built-in template); stderr warning 「current preset 為 {style} 但 fallback 到 Kami template，class prefix 可能不一致；建議先跑 /baransu:design preset {style}」; continue producing output (GATE-F will detect the class-prefix inconsistency, which is expected behavior).

The long-form.html slot is a show-by-example contract — the slot demonstrates 6+ section types (heading / paragraph / quote / code / SVG / list). Token values are provided by `{project_root}/tokens.css`; the template only references canonical names (var(--paper) / var(--accent) etc.). Do not invent new CSS patterns.

🔴 GATE — before starting to produce HTML, regardless of whether Stage 2A §1 already read it, you MUST read the 「Output Anti-Slop Blacklist」 and 「Quantified Type Scale」 sections of `references/perception-guide.md` as a render-time standing instruction (to prevent a clean-classification run from regressing to generic-AI-feel output when the typography / anti-slop rules were never loaded).

### 2. Generate HTML structure

Produce the full HTML document using the SSOT template loaded in step 2:

```
<head> with linked tokens.css (use {project_root}/tokens.css; fill {{TITLE}})
<nav class="<slug>-toc"> with <a href="#sN"> for each section
<main>
  <header class="<slug>-cover"> with kicker, h1, subtitle, meta
  <section data-slot="long-form-body">
    <!-- Replace this section's innerHTML with rendered body sections -->
    <section id="sN"> for each section (4–8 sections)
  </section>
  <footer class="<slug>-footer">
</main>
```

`<slug>` is the preset prefix read from `tokens.css` line 1 (kami / google / swiss / gen slug). All class names in output must use that prefix; GATE-F guards consistency.

### 3. Section content rules

For each section from `$STRUCTURE`:

- Open with `<h2><span class="sec-num">0N</span>{Section Title}</h2>`
- Write 1–3 paragraphs expanding the key claims using language from `$RAW_CONTENT`
- Immediately follow with a `<figure class="diagram">` block containing an SVG if the section was flagged for it
- Use `.callout`, `.card-grid`, `table.cmp`, or `.tradeoff-row` components from the template where they improve readability

**Section rhythm standing instruction (render-time hard rule, not vibes)**: when applying the components above, resolve every "generous" / "tight" / "airy" treatment to a number in `references/perception-guide.md` Quantified Type Scale, never to vibes. Three highest-leverage values are binding at render time — each constrains how existing `long-form.html` template classes / tokens are *used* (no new CSS, no new token):

1. **Inter-section vertical gap = 3xl 80–120pt** between long-doc `<section>` blocks — drive it with the existing spacing token at the 3xl step; never inherit the browser-default margin.
2. **Reading-body line-height locked 1.50–1.55** (CJK on screen may relax to 1.55–1.65); **`≥ 1.70` is banned** (reads as floating web-prose, not print).
3. **Reading column capped 680px / max body width 760px** — wider than this is a slop signal, not "generous".

**No improvisation**: every component class must exist in the SSOT template (`{project_root}/design-cores/long-form.html`) or fallback `references/golden-template.html`. If a component isn't in either source, use plain `<p>` — do not add new CSS.

🔴 GATE — pre-render visual self-check (pre-write checklist): **before** writing the HTML to file in Stage 3 §7, go through the following six-line binary checklist item by item (each restates an existing reference rule, not a new rule). Any ✗ → fix it then Write, do not write to disk directly; only enter §7 when all six are ✓.

1. **Inter-section spacing** — is each pair of adjacent `<section>` driven by the 3xl spacing token (80–120pt), not browser-default margin? (§3 render-time hard rule #1)
2. **Reading line-height** — is body line-height ∈ [1.50, 1.55] (CJK screens may relax to 1.65), with no `≥ 1.70` anywhere in the text? (§3 render-time hard rule #2)
3. **Reading column width** — is the reading column ≤ 680px and max body width ≤ 760px? (§3 render-time hard rule #3)
4. **Single accent** — only one chromatic accent (`var(--accent)`) used, accent-painted area ≤ 5% of body, and emphasis is "color OR weight, not both"? (perception-guide Anti-Slop #8)
5. **SVG focal + alignment** — each SVG has ≤ 2 `data-role="focal"`, and all coordinates / widths / spacing are multiples of 4? (svg-rendering-rules §4.7)
6. **figcaption** — does each `<figcaption>` pass the perception-guide Anti-Slop #5 pass test (carrying one of: trade-off / next step / a dimension the figure doesn't directly show), rather than merely restating the title or node name? (perception-guide Anti-Slop #5)

### 4. SVG generation spec

Takes effect only when the long-form HTML contains `<figure class="diagram">`. The spec includes: color tokens (canonical names + Kami hex defaults), the required `<defs>` / marker / two-layer paper-mask, type tag, legend strip, 4px alignment and the 3-step node-width whitelist (128/144/160), embedded-font correction, the 14-type diagram first-match decision tree, and the 13-type selection table (including `status: complete | ref-only`).

**Full rules → read `references/svg-rendering-rules.md`.** SVG fill / stroke **must not use `rgba()`**; node width is limited to 3 steps (128/144/160); focal nodes are marked via `data-role="focal"`, capped at 2 per SVG.

### 5. Core Asset Protocol (image acquisition)

Whenever any stage needs to fetch a raster / photographic / logo / UI mockup image, follow the 4 steps below **strictly in order**. **Steps must run in order; skipping = fail and abort.** (Skipping a step is treated as a fail and aborts; e.g. freezing before verifying.)

1. **Ask** — 🔴 CHECKPOINT — image-purpose confirmation (may not advance to step 2 without confirmation): confirm with the user the image's purpose, composition, required elements, and forbidden elements (avoid AI slop: six fingers, distorted text, watermark, page chrome). May not enter step 2 before confirmation is obtained.
2. **Generate OR Search** — pick one:
   - **Generate**: run **Codex CLI image-gen**, with the brief produced by `/baransu:design export-brief` then fed in via stdin. Example:
     ```bash
     codex prompt --stdin < .claude/design/brief-{preset}-{date}.md \
       --suffix "請生成符合上述 design brief 的封面圖，no title, no footer, no page chrome, no logo, no border"
     ```
   - **Search**: call `search the web` to find ready-made resources; **accept only CC licenses** (CC0 / CC-BY / CC-BY-SA), everything else falls back to the Generate branch.
3. **Verify** — the renderer embeds the image into the long-form HTML preview, and the user visually confirms composition, layout alignment, no AI slop, no watermark; if it fails, fall back to step 2 and rerun.
4. **Freeze** — commit the image file to `.claude/book/{slug}/assets/`, and write a `meta.json` containing `source` (generate / search), `prompt` (required on the Generate path), `license` (required on the Search path), and a `verified_at` timestamp. After freezing the image is treated as immutable; to change it → start over from step 1.

### 6. Multi-format pipeline (PDF / PPTX)

Takes effect only when `$FORMAT` ∈ {`pdf`, `ppt`, `all`}.

- **PDF**: inject `@page` + hidden `.toc-wrap` + serif `body { font-family: var(--font-serif) }` into the HTML, save the patched HTML, call `python3 -m weasyprint`. On failure → warning, do not abort.
- **PPTX**: per `$STRUCTURE_SLIDES`, take the skeleton from `{project_root}/slide-cores/<layout-id>.html`; output `<body width=960>` + per slide `<div class="slide" data-layout=...>`; before calling, verify three items (`width=960` / `.slide` present / no `background-image`); once passed, call `node html2pptx.js`.

**Detailed steps (HTML preprocessing / verification items / failure handling) → read `references/render-pipelines.md`.**
### 7. Write the output file

Write the complete HTML to `.claude/book/{$SLUG}.html`.

Do not write partial content — write the full file in one operation.

---

## Stage 4 — Validate & Report

### 1. Run quality gate

```bash
npx tsx "./scripts/validate-output.ts" ".claude/book/{$SLUG}.html"
```

Exit codes:
- `0` (GATE PASS): proceed to completion report
- `1` (GATE FAIL): three-stage fallback:
  - **Trigger condition**: validate-output.ts returns exit 1.
  - **First-line fix**: read the failure lines printed to stdout, fix only the failing element and rewrite the file, then rerun the quality gate once.
  - **Still-failing fallback**: 🛑 STOP — quality gate failed a second time, human intervention: if exit 1 still on the second run, output 「品質閘第二次失敗，請手動開啟 .claude/book/{$SLUG}.html 確認問題。」 and stop (do not enter the completion report).
- `2` (usage error): script invocation was wrong — fix and re-run

### 2. Visual render verification + completion report

After GATE PASS, run a Playwright headless render (producing a preview screenshot + JSON probe) and output the final completion report.

**Detailed spec → read `references/validation.md`** (including how to call `verify-render.py`, the probe JSON schema, interpretation rules, and the full report template).

The final user-visible output's fixed format (core lines):

```
✅ 已儲存：
  HTML / PDF（若 format 含 pdf）/ PPT（若 format 含 ppt）/ 預覽 PNG
內容類型：{$CONTENT_TYPE}
SVG 圖解：{N} 張
字數：約 {word_count} 詞
```

---

## Constraints

- **Token source = project root**: all visual elements consume tokens from `{project_root}/tokens.css` (written by `/baransu:design preset <style>` or `/baransu:design gen --slug <slug>`) plus the component patterns in `{project_root}/design-cores/long-form.html` (SSOT) or `references/golden-template.html` (fallback). No inline hex colours; use named CSS variables (canonical 36 names).
- **No new CSS patterns**: every class in the output HTML must exist in the active SSOT template or fallback. Extend within the active preset; don't invent outside it.
- **SVG required**: a document with 0 SVG diagrams fails the quality gate and must be fixed before completion.
- **Length cap**: final HTML body ≤ 1800 words. Excess goes into a 延伸閱讀 link block.
- **No LLM-generated commentary**: the rendered HTML contains the source content, structured and styled — not Claude's own analysis. The Synthesize stage extracts; the Render stage presents.
- **Partial failure**: if Acquire fails for one of multiple inputs, report the failure per-input and continue with the rest.

## Red Lines (what not to do)

Scan the forbidden zone via the 🛑 visual marker, not by reading through prose. Each item below restates an existing rule; violating it = that output is compromised; each row carries a "why compromised" rationale anchor and the correct approach.

| 🛑 Anti-pattern | Why it's compromised (rationale anchor) | Correct approach (authoritative reference) |
|----------|---------------------|--------------------------|
| 🛑 Inventing a new CSS class / using inline hex colors | Breaks out of the active SSOT template's set membership, compromising the GATE-F class-prefix and the 36-token list, regressing to generic AI feel | class must exist in the active template; use canonical-name variables for color (§3.3, Constraints; perception-guide Anti-Slop Blacklist #7) |
| 🛑 Using `rgba()` for SVG fill / stroke | WeasyPrint composites the alpha into a double-rectangle ghost-border, distorting the PDF | SVG fill/stroke must always be a solid hex token (§3.4, svg-rendering-rules §4.1) |
| 🛑 Free-styling node widths outside the 3-step whitelist | Mixing more than 3 steps is an anti-slop fail and breaks the diagram rhythm | node width limited to {128/144/160}, at most 2 steps per diagram (svg-rendering-rules §4.7) |
| 🛑 Silently producing an empty page / skeleton when Acquire fails | Disguises failure as a successful output, leaving the user with an empty shell | report each failure clearly, do not produce an empty shell (Gotchas SPA, Constraints Partial failure) |
| 🛑 Falling back to `find` / sibling-skill paths when `tokens.css` is missing | Violates the invariant that the sole token source = project root | tokens.css missing → abort and prompt to run `/baransu:design preset` first (Gotchas Missing project-root tokens, §3.1) |
| 🛑 Skipping a Core Asset step (freezing before verifying) | The 4-step protocol's ordering guarantees "freeze only when there's no AI slop"; skipping bypasses quality confirmation | Ask → Generate/Search → Verify → Freeze strictly in order (§3.5) |
| 🛑 Writing Claude's self-assessment / commentary / analysis into the HTML | The output should be structured source content, not the model's own argumentation | Synthesize extracts, Render presents; do not smuggle in LLM commentary (Constraints No LLM-generated commentary) |

## Gotchas

- **SPA / login walls**: X.com, LinkedIn, paywalled pages often fail the proxy cascade. Report the failure clearly; don't silently produce an empty or skeleton page.
- **markitdown escaped underscores in URLs**: when markitdown converts HTML, it sometimes escapes `_` to `\_` inside image URLs. Run a cleanup pass on all `![...](\url)` patterns before processing.
- **SVG path closure**: always close `<path>` elements with `/>`; validate-output.ts checks SVG tag balance but not path syntax. Keep SVG shapes simple (lines, rects, circles, ellipses, simple paths).
- **Missing project-root tokens**: if `{project_root}/tokens.css` is absent, Stage 3 aborts with 「請先跑 `/baransu:design preset <style>`（kami / google-design / swiss）或 `/baransu:design gen --slug <slug>`」 — **do not** fall back to `find` or sibling-skill paths. Fallback to `references/golden-template.html` is allowed only when long-form.html is absent (see §3.1).

## Validator division of labor

- `scripts/validate-output.ts`: responsible for the output layer's (output HTML) set membership and prefix consistency, including GATE A-E (existing SVG rules) / GATE-F (class prefix `kami-*` / `swiss-*` not mixed + tokens.css preset tie-break) / GATE-G (`data-layout` must correspond to a real file under `{project_root}/slide-cores/`) / GATE-J node-width whitelist / GATE-K chevron-strict / GATE-L viewBox containment (rect/line/circle/ellipse/text all fall within the viewBox, 0.5px tolerance; skips defs/marker/pattern/clipPath/mask/symbol and transformed groups). **Trusts** that the `/design` side's `check.py` has already linted the slide-core artifact's internal structure; this validation does not redo per-file lint.
- The corresponding `/design`-side rules are in `plugins/baransu/skills/design/scripts/check.py`'s artifact-internal lint rules.

## REQ-003 Scenario 2 automated evidence

- Fixture: `scripts/validate-fixtures/swiss-positive.html` — a hand-written swiss-style slide HTML that mirrors the shape `/book` Stage 3 emits under `--format ppt --style swiss` (body 960pt×540pt, `data-layout="content-bullets"` / `quote`, all classes `swiss-*`, no hard-fail violations).
- Smoke runner: `scripts/swiss-smoke-test.sh` — Stage 1 runs `validate-output.ts` against the fixture (expected all green; GATE-C/GATE-G SKIP because of the viewBox height and the project root having no `slide-cores/`); Stage 2, when `pptxgenjs` + `playwright` are installed, runs `html2pptx.js`, and uses `python3 zipfile` to confirm the `.pptx` is a valid zip containing `ppt/presentation.xml` + `[Content_Types].xml`. When dependencies are not installed, Stage 2 SKIPs (`--strict` turns it into FAIL).
- Purpose: serves as the minimal automated-evidence starting point for REQ-003 S2 「文件可在 PowerPoint 打開」. For a full PowerPoint round-trip, run `npx tsx scripts/install-deps.ts --format ppt` first.
