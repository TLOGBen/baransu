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

- **Outcome**: 把任一內容來源（URL / slug / 本地檔 / 文字）經 Acquire → Synthesize → Render 三階段轉成 Kami 主題、瀏覽器可直接開啟的 HTML book。
- **Done when**: 輸出 HTML 通過 scripts/validate-output.ts 全部 GATE（exit 0），且檔案落於 `.claude/book/{slug}.html`。
- **Evidence**: validate-output.ts 的執行結果（GATE A-E / F / G / J / K / L 全綠或合法 SKIP）。
- **Output**: `.claude/book/{slug}.html`；依 `--format` 另含 `.pdf` / `.pptx`。
- **Automation**: ultracode=neutral, loop=drivable

## Stage 0 — Environment Self-Check

> 本 SKILL.md 採 Fact-Verification Principle #0（見下文 Stage 2A §0「Fact-Verification Principle #0」段）：在合成長文前，凡偵測到具體產品 / 版本 / 人名 + 職位 pattern，強制 search the web 驗證；0 結果即 ask the user directly 阻擋。

### 1. Design context soft-read

執行於所有其他 Stage 0 步驟之前。沿用 /design / /analyze 的同款 soft-read 模式，把當下 preset 的設計哲學帶進 context 作 advisory framing。

1. 解析 project root：`git rev-parse --show-toplevel 2>/dev/null`，失敗則用 cwd。
2. 嘗試讀取以下檔（皆 best-effort，**全部失敗也不中止 Stage 0**，只 stderr warning）：
   - `{project_root}/DESIGN.md`：當下 preset 的九段設計規格。讀入 context 供後續 Stage 2A typography 選用 / Stage 3 SVG token decisions 參考。
   - `{project_root}/tokens.css` 第一行：解析 preset slug（例：`/* preset: kami */` → `kami`），存為 `$STYLE` 預備值（之後若 user 顯式給 `--style` 則覆寫，否則沿用本值）。
3. 若 `DESIGN.md` 存在 → stderr `已載入 DESIGN.md，視覺規格已參考（preset=$STYLE）`。
4. 若 `DESIGN.md` 不存在 → stderr `未找到 DESIGN.md；建議先跑 /baransu:design preset <name>。本次 /book 將使用 fallback 模板，視覺風格可能與 preset 不一致`，繼續執行。

此步驟讀入的 DESIGN.md 內容在 Stage 4 視 user 是否觸發 `/baransu:review --include=style` 而被傳遞給 style-reviewer 作為 spec anchor；正常 /book 流程中只作為 generation-time advisory，不影響任何 gate。

### 2. --format 旗標解析

解析使用者呼叫中的 `--format` 旗標：

- 支援值：`html` | `pdf` | `ppt` | `all`
- 若未提供 `--format`：預設為 `html`
- 若值不合法（非 html/pdf/ppt/all）：輸出「`--format` 值不合法。支援：html | pdf | ppt | all」並停止（不呼叫 install-deps.ts）
- 設定 `$FORMAT` 供後續所有 Stage 使用

### 3. --style 旗標解析

解析使用者呼叫中的 `--style` 旗標（v1.3 PPT + HTML 雙模式）：

- 支援值：`kami` | `google-design` | `swiss` | user-supplied gen slug（pattern `/^[a-z][a-z0-9-]{1,15}$/`，須先跑過 `/baransu:design gen --slug <slug>`）
- 未提供 `--style`：從 `{project_root}/tokens.css` 第一行 `/* preset: <slug> */` 解析；都無則預設 `kami`
- 不合法值：輸出「--style 不合法。支援 v1.3 三 preset 或已註冊 gen slug」並停止
- HTML 模式從 `{project_root}/design-cores/long-form.html` 動態讀模板；PPT 模式從 `{project_root}/slide-cores/` 動態讀 layout
- 設定 `$STYLE` 供後續 Stage 使用（Stage 3 tokens.css tie-break / GATE-F prefix 比對讀 `$STYLE`）

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
npx tsx "the skill's root directory/scripts/install-deps.ts" --format $FORMAT
```

若腳本回傳非零 exit code：
- 輸出錯誤訊息（腳本已列出詳情）並停止，不進入 Stage 1
- 若 `$FORMAT` 含 `pdf`：確認 WeasyPrint 可用
- 若 `$FORMAT` 含 `ppt`：確認 playwright + pptxgenjs 可用

### 7. Output directory

Ensure `.claude/book/` exists relative to the project root:

```bash
mkdir -p ".claude/book"
```

---

## Stage 0b — Pre-interview Gate（受眾 / 硬約束前置）

在 Stage 1 取得 `$RAW_CONTENT` **之前**，先壓住 50% 不確定性。模式對齊 /design Gen Mode Step 1：用 **單一 ask the user directly 批次**（4 題並陳，不逐題阻塞）對齊受眾、用途、風格傾向、硬約束。

### 跳過條件（任一成立即整段跳過）

- `--auto` 或 `--no-interview` 旗標出現
- input 是 `/read` slug / `/learn` digest slug（受眾 + 用途已隱含於原 capture metadata）
- input 是 `--text "…"` 且字數 < 200（極短 inline 不值得問）

跳過時 stderr 印一行：「Stage 0b skipped: {reason}」，繼續 Stage 1。

### 訪談題目（batch 一次提，4 題並陳）

1. **受眾** — 「主要讀者是誰？（例如：技術同儕 / 產品 PM / 非技術主管 / 公開讀者 / 自己備忘）」
2. **用途與時長** — 「這份 book 的使用情境？（例如：5 分鐘速讀 / 30 分鐘深讀 / 簡報前置 / 長期參考文件）」
3. **風格傾向** — 「視覺密度偏哪邊？（例如：高密度技術文件 / 留白敘事散文 / 多圖表 research 報告 / 隨 preset 預設）」
4. **硬約束** — 「有沒有必須 / 不要的元素？（例如：必含某段內文、不要 SVG diagram、限定字數、特定 callout 數）」

未答 / 「隨預設」一律走 preset 既有 default，不另存。已答內容寫入 `$INTERVIEW_BRIEF`（純文字 4-8 行），於 Stage 2A §1 分類前 prepend 為 advisory framing，**不覆寫** `references/perception-guide.md` 既有 A/B/C 分類邏輯（衝突時以 perception-guide 為準，brief 僅作 nudge）。

### 完成輸出

一行：「訪談完成：受眾={...} / 用途={...} / 風格={...} / 約束={...}，進入 Stage 1。」

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

### 0. Fact-Verification Principle #0

**Purpose**：在合成長文進入 §1 分類前先做事實閘，防止把幻想的具體規格（虛構版本號、虛構人物職位）寫進最終 HTML。對應 REQ-006 Scenario 1 / Criteria C6。歷史案例：「Linear MCP v3.4.7 released 2025-09-15」屬虛構，但若不驗證，會被當作既有事實渲染到 book 內。

**Trigger regex**（對 `$RAW_CONTENT` 全文 soft-match，不強制全部命中視為錯誤，只作為觸發 search the web 的訊號）：

```
/([A-Z][a-zA-Z]+\s+(MCP|SDK|CLI|API)?\s*v?\d+(\.\d+)*)|([A-Z][a-z]+\s+[A-Z][a-z]+(\s|,)+(CEO|CTO|founder|engineer))/
```

說明：
- 前半 alternation：產品名（capitalized word）+ 選擇性 MCP/SDK/CLI/API + 選擇性 `v` + 一段以上點分數字 → 命中如「Linear MCP v3.4.7」「Anthropic SDK 0.39」。
- 後半 alternation：人名（兩個 capitalized words）+ 空白或逗號 + 職位（CEO/CTO/founder/engineer）→ 命中如「Jane Doe, CTO」。

**Flow on hit**（每命中一筆 `{hit}`）：

1. **Sanitize `{hit}` before query**：將 `{hit}` 內所有 `"` (`U+0022`) 字元先剝除（regex 抓的是合法 identifier/version 字串，正常情況不含 quote；含則為 noise 或 adversarial input）。Sanitized `{hit_clean}` 再丟下一步。
2. 跑 `search the web`，query template：`"{hit_clean}" release notes` 或 `"{hit_clean}" announcement`（人名命中改用 `"{hit_clean}" announcement` / `"{hit_clean}" interview`）。
3. 若 search the web 回傳 **0 結果** → 透過 `ask the user directly` 顯示：「Fact-verify pending: '{hit_clean}' 在 search the web 0 結果。選擇：強制繼續 / 改用 `--text` 餵已驗證版本 / 中止本次 /book」。等使用者選擇後再決定是否進入 §1。
4. 若 search the web 回傳 **≥ 1 結果** → 視為事實可驗，繼續，但仍把該 hit 列入 `$STRUCTURE` 末尾的「Sources」清單（在 Stage 2A §4 extract 階段一併處理）。

**Flow on no hit**：直接進入 §1 分類。

**Boundary**：regex 為 soft trigger，不是 hard match——不命中不代表內容必為真，未來會視 telemetry 結果擴充 pattern。**測試 fixture**：字串 `Linear MCP v3.4.7 released 2025-09-15` 為虛構，預期觸發 regex、search the web 回傳 0 結果、走 ask 流程（不可靜默繼續）。

### 1. Classify content type

對 `$RAW_CONTENT` 做粗略 keyword + 結構 scan，先猜 `$CONTENT_TYPE` 落在哪一類；若邊界不明（如混合敘事+技術 / 全新類型 / 多源綜述 vs 單篇分析難分），**才讀** `references/perception-guide.md` 做最終分類。

`perception-guide.md` 含完整 taxonomy（Technical / Narrative / Research）、各類視覺處理策略、SVG 策略、合成長度上限（4–8 sections、≤1800 words）。

### 2. Decide $CONTENT_TYPE

Based on the perception guide signals, assign `$CONTENT_TYPE` to one of:
- `technical` — code, how-to, architecture, tool guides
- `narrative` — essays, opinions, threads, stories
- `research` — analyses, reports, multi-source synthesis

Output one line: 「內容類型偵測：{$CONTENT_TYPE}」

### 3. 兩階層決策樹（Layer 1 內容類型 → Layer 2 diagram 結構）

Stage 2A 的選擇分為兩層，**順序不可顛倒**：

- **Layer 1（content type → HTML 版面密度）**：由 §2 已產出的 `$CONTENT_TYPE`（A=`technical` / B=`narrative` / C=`research`）決定整篇 HTML 的版面樣式——TOC 是否展開、cards 數量、密度、callout 風格等，皆由 `references/perception-guide.md` 對應 A/B/C 三類分別給定。
- **Layer 2（13 型 selection → 每段 diagram 結構）**：每個含 diagram 的 section 獨立 lookup Stage 3 §4「13 型 selection 表」，依該段資料形狀挑一個 diagram type（architecture / flowchart / sequence / ...）。

兩軸正交：Layer 1 控版面，Layer 2 控每段 SVG 結構；先 Layer 1、再 Layer 2，每段獨立決定不沿用上一段選擇。

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
If a collision exists: append `_v2`, `_v3`, etc.

**$SLUG 只在 Stage 2A 推導一次，Stage 2B 和所有 Render 步驟繼承相同 $SLUG，不另行推導。**

---

## Stage 2B — Synthesize（投影片，僅 --format ppt 或 all）

僅在 `$FORMAT` ∈ {`ppt`, `all`} 時執行；產出 `$STRUCTURE_SLIDES`（6–12 slides，首頁固定 `cover`、末頁條件式 `closing`）。**layout 不寫死**：動態讀 `{project_root}/slide-cores/*.html` 的 YAML front-matter 註冊決策表，以 first-match + positional override 派 layout_type。

**規則細節（10-row 決策表 / closing 條件辨識 / graceful degradation / `$STRUCTURE_SLIDES` schema）→ 讀 `references/slide-synthesis.md`。**
## Stage 3 — Render

Produces a complete HTML file at `.claude/book/{$SLUG}.html`.

### 1. Read the design system

Before generating any HTML:

1. **唯一 token 來源**：讀 `{project_root}/tokens.css`（由 `/baransu:design preset <style>` 寫入；本 skill 只讀，不改）。此規則**同時適用** `--format ppt` 與 `--format html`。
   - 若 `{project_root}/tokens.css` **不存在** → 報錯「請先跑 `/baransu:design preset <style>`（kami / google-design / swiss）」並**中止 Stage 3**。
   - tokens.css 開頭含 preset 識別註解（`/* preset: kami */` / `/* preset: google-design */` / `/* preset: swiss */` 或 user-supplied gen slug），供 Stage 0 解析得到的 `$STYLE` 變數於 GATE-F 做 tie-break 比對。
2. **v1.3 long-form template SSOT 動態讀**：優先讀 `{project_root}/design-cores/long-form.html`，將 `<section data-slot="long-form-body">` 視為 body insertion point。
   - 檔案**存在但讀失敗**（malformed / chmod 000 / 0 bytes）→ **hard fail**，不靜默 fallback；stderr「long-form.html 讀取失敗：{原因}」、中止 Stage 3。
   - 檔案**不存在** → fallback 至 `references/golden-template.html`（v1.2 Kami 風內建範本）；stderr warning「current preset 為 {style} 但 fallback 到 Kami template，class prefix 可能不一致；建議先跑 /baransu:design preset {style}」；繼續產出（GATE-F 將檢出 class prefix 不一致，是預期行為）。

The long-form.html slot 是 show-by-example contract — slot 內示範 6+ section type（heading / paragraph / quote / code / SVG / list）。Token 值由 `{project_root}/tokens.css` 提供；模板只引用 canonical 名（var(--paper) / var(--accent) 等）。不發明新 CSS 模式。

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

`<slug>` is the preset prefix read from `tokens.css` line 1 (kami / google / swiss / gen slug). All class names in output 必須使用該 prefix；GATE-F 守護一致性。

### 3. Section content rules

For each section from `$STRUCTURE`:

- Open with `<h2><span class="sec-num">0N</span>{Section Title}</h2>`
- Write 1–3 paragraphs expanding the key claims using language from `$RAW_CONTENT`
- Immediately follow with a `<figure class="diagram">` block containing an SVG if the section was flagged for it
- Use `.callout`, `.card-grid`, `table.cmp`, or `.tradeoff-row` components from the template where they improve readability

**No improvisation**: every component class must exist in the SSOT template (`{project_root}/design-cores/long-form.html`) or fallback `references/golden-template.html`. If a component isn't in either source, use plain `<p>` — do not add new CSS.

### 4. SVG 生成規格

只在 long-form HTML 含 `<figure class="diagram">` 時生效。spec 含：色彩 token（canonical names + Kami hex 預設）、必備 `<defs>` / marker / 兩層 paper-mask、type tag、legend strip、4 px 對齊與 3 檔節點寬白名單（128/144/160）、嵌入字體校正、14 型圖表 first-match 決策樹、13 型 selection 表（含 `status: complete | ref-only`）。

**完整規則 → 讀 `references/svg-rendering-rules.md`。**SVG fill / stroke **禁用 `rgba()`**；節點寬限 3 檔（128/144/160）；焦點節點透過 `data-role="focal"` 標記，每張 SVG 上限 2 個。

### 5. Core Asset Protocol（圖片取得）

任一階段需 fetch 點陣 / 攝影 / logo / UI mockup 圖時，**嚴格依序**走以下 4 步。**Steps must run in order; skipping = fail and abort.**（跳步即視為 fail 並中止；例：未 verify 就 freeze。）

1. **Ask** — 與 user 確認圖片用途、構圖、必含元素、禁用元素（避免 AI slop：六指、扭曲文字、浮水印、page chrome）。未拿到確認前不得進入步驟 2。
2. **Generate OR Search** — 二擇一：
   - **Generate**：跑 **Codex CLI image-gen**，brief 由 `/baransu:design export-brief` 產出後 stdin 餵入。範例：
     ```bash
     codex prompt --stdin < .claude/design/brief-{preset}-{date}.md \
       --suffix "請生成符合上述 design brief 的封面圖，no title, no footer, no page chrome, no logo, no border"
     ```
   - **Search**：呼叫 `search the web` 找現成資源；**只接受 CC license**（CC0 / CC-BY / CC-BY-SA），其餘一律退回 Generate 分支。
3. **Verify** — renderer 將圖嵌入 long-form HTML preview，user 肉眼確認構圖、版面對齊、無 AI slop、無 watermark；未通過則退回步驟 2 重跑。
4. **Freeze** — commit 圖檔到 `.claude/book/{slug}/assets/`，並寫 `meta.json` 含 `source`（generate / search）、`prompt`（Generate 路徑必填）、`license`（Search 路徑必填）、`verified_at` 時戳。Freeze 後該圖視為不可變；要換 → 從步驟 1 重來。

### 6. 多 format pipeline (PDF / PPTX)

只在 `$FORMAT` ∈ {`pdf`, `ppt`, `all`} 時生效。

- **PDF**：HTML 注入 `@page` + 隱藏 `.toc-wrap` + serif `body { font-family: var(--font-serif) }`，存 patched HTML，呼叫 `python3 -m weasyprint`。失敗 → warning，不中止。
- **PPTX**：依 `$STRUCTURE_SLIDES` 從 `{project_root}/slide-cores/<layout-id>.html` 取骨架；輸出 `<body width=960>` + 每 slide `<div class="slide" data-layout=...>`；呼叫前驗三項 (`width=960` / `.slide` 存在 / 無 `background-image`)；通過後呼叫 `node html2pptx.js`。

**詳細步驟（HTML 預處理 / 驗證項 / 失敗處理）→ 讀 `references/render-pipelines.md`。**
### 7. Write the output file

Write the complete HTML to `.claude/book/{$SLUG}.html`.

Do not write partial content — write the full file in one operation.

---

## Stage 4 — Validate & Report

### 1. Run quality gate

```bash
npx tsx "the skill's root directory/scripts/validate-output.ts" ".claude/book/{$SLUG}.html"
```

Exit codes:
- `0` (GATE PASS): proceed to completion report
- `1` (GATE FAIL): read the failure lines printed to stdout; fix the specific failing element and re-write the file; re-run the gate once more
  - If the gate fails a second time: output 「品質閘第二次失敗，請手動開啟 .claude/book/{$SLUG}.html 確認問題。」 and stop.
- `2` (usage error): script invocation was wrong — fix and re-run

### 2. Visual render verification + completion report

GATE PASS 後跑 Playwright headless render（產 preview screenshot + JSON probe）並輸出最終 completion report。

**詳細規格 → 讀 `references/validation.md`**（含 `verify-render.py` 呼叫方式、probe JSON schema、判讀規則、完整 report template）。

最終 user-visible 輸出固定格式（核心 lines）：

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

## Gotchas

- **SPA / login walls**: X.com, LinkedIn, paywalled pages often fail the proxy cascade. Report the failure clearly; don't silently produce an empty or skeleton page.
- **markitdown escaped underscores in URLs**: when markitdown converts HTML, it sometimes escapes `_` to `\_` inside image URLs. Run a cleanup pass on all `![...](\url)` patterns before processing.
- **SVG path closure**: always close `<path>` elements with `/>`; validate-output.ts checks SVG tag balance but not path syntax. Keep SVG shapes simple (lines, rects, circles, ellipses, simple paths).
- **Missing project-root tokens**: if `{project_root}/tokens.css` is absent, Stage 3 aborts with 「請先跑 `/baransu:design preset <style>`（kami / google-design / swiss）或 `/baransu:design gen --slug <slug>`」 — **do not** fall back to `find` or sibling-skill paths. Fallback to `references/golden-template.html` is allowed only when long-form.html is absent (see §3.1).

## Validator 分工

- `scripts/validate-output.ts`：負責輸出層（output HTML）的 set membership 與 prefix 一致性，含 GATE A-E (SVG 既有規則) / GATE-F (class prefix `kami-*` / `swiss-*` 不混 + tokens.css preset tie-break) / GATE-G (`data-layout` 必對應 `{project_root}/slide-cores/` 實存檔) / GATE-J node-width whitelist / GATE-K chevron-strict / GATE-L viewBox containment (rect/line/circle/ellipse/text 全落在 viewBox 內，0.5px 容差；skips defs/marker/pattern/clipPath/mask/symbol 與 transformed group)。**信任** `/design` 端 `check.py` 已 lint 過 slide-core artifact 內部結構，本驗證不重做 per-file lint。
- 對應 `/design` 端見 `plugins/baransu/skills/design/scripts/check.py` 的 artifact-internal lint 規則。

## REQ-003 Scenario 2 automated evidence

- Fixture: `scripts/validate-fixtures/swiss-positive.html` — a hand-written swiss-style slide HTML that mirrors the shape `/book` Stage 3 emits under `--format ppt --style swiss`（body 960pt×540pt、`data-layout="content-bullets"` / `quote`、所有 class `swiss-*`、無 hard-fail 違反）。
- Smoke runner: `scripts/swiss-smoke-test.sh` — Stage 1 跑 `validate-output.ts` 對 fixture（預期全綠，GATE-C/GATE-G 因 viewBox 高度與 project root 無 `slide-cores/` 而 SKIP）；Stage 2 在 `pptxgenjs` + `playwright` 已安裝時跑 `html2pptx.js`，並用 `python3 zipfile` 確認 `.pptx` 是合法 zip 且含 `ppt/presentation.xml` + `[Content_Types].xml`。依賴未裝時 Stage 2 SKIP（`--strict` 改為 FAIL）。
- 用途：作為 REQ-003 S2「文件可在 PowerPoint 打開」的最小自動化證據起點。要做完整 PowerPoint round-trip 須先 `npx tsx scripts/install-deps.ts --format ppt`。
