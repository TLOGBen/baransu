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

### 2.5 兩階層決策樹（Layer 1 內容類型 → Layer 2 diagram 結構）

Stage 2A 的選擇分為兩層，**順序不可顛倒**：

- **Layer 1（content type → HTML 版面密度）**：由 §2 已產出的 `$CONTENT_TYPE`（A=`technical` / B=`narrative` / C=`research`）決定整篇 HTML 的版面樣式——TOC 是否展開、cards 數量、密度、callout 風格等，皆由 `references/perception-guide.md` 對應 A/B/C 三類分別給定。
- **Layer 2（13 型 selection → 每段 diagram 結構）**：每個含 diagram 的 section 獨立 lookup Stage 3 §4「13 型 selection 表」，依該段資料形狀挑一個 diagram type（architecture / flowchart / sequence / ...）。

兩軸正交：Layer 1 控版面，Layer 2 控每段 SVG 結構；先 Layer 1、再 Layer 2，每段獨立決定不沿用上一段選擇。

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
  <marker id="arrow" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="#504e49"/>
  </marker>
  <marker id="arrow-accent" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="#1B365D"/>
  </marker>
  <marker id="arrow-link" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="#1B365D"/>
  </marker>
</defs>
```

#### Marker defs（箭頭走 `<marker>`，三個 id 固定）

**規則**：每張含箭頭的 SVG 必須在 `<defs>` 內定義以下三個 marker，並以 `marker-end="url(#…)"` 引用；不再使用手寫的箭頭 path。

| Marker id | 對應用途 | fill |
|-----------|----------|------|
| `arrow` | default（一般 / 內部流向，muted） | `#504e49`（`--olive`） |
| `arrow-accent` | focal / 主流（brand 色） | `#1B365D`（`--brand`） |
| `arrow-link` | external / API call / 跨界（可用 brand-light） | `#1B365D` 或 brand-light |

**marker 屬性固定**：`markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"`。

**Why**：marker 由 SVG 引擎管理方向與端點對齊，避免手寫箭頭 path 在 viewBox 縮放下產生對位偏差；同時三個語意分層（一般 / focal / external）才能與「焦點節點 ≤ 2」「跨系統呼叫」這兩條規格在 SVG 層對齊。

**SVG 引用範例**：

```svg
<line x1="120" y1="80" x2="240" y2="80"
      stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
<line x1="120" y1="120" x2="240" y2="120"
      stroke="#1B365D" stroke-width="1.4" marker-end="url(#arrow-accent)"/>
```

#### 兩層 paper-mask（節點背景與 canvas 底）

**規則**：每張 SVG 在 `<defs>` 後**先後**疊兩層 mask，再開始畫節點與箭頭：

```svg
<!-- Layer 1（必選）：全幅 paper fill -->
<rect width="100%" height="100%" fill="#f5f4ed"/>
<!-- Layer 2（可選）：dotted pattern overlay -->
<rect width="100%" height="100%" fill="url(#dots)" opacity="0.55"/>
```

- Layer 1（**強制**）：全幅 `<rect width="100%" height="100%" fill="{paper-token}"/>`，paper-token 走 `--parchment`（`#f5f4ed`）
- Layer 2（**可選**）：全幅 `<rect width="100%" height="100%" fill="url(#dots)" opacity="0.55"/>`，僅在長文 / 單頁 hero diagram 採用；產品頁或卡片內嵌時省略以避免紋路堆疊成噪訊
- **不做三層**：v1 規格明文禁止第三層 mask 堆疊（如 vignette、tint wash）；Unknown #3 留待 v1 dogfood 後再決定是否升級

**Why**：兩層結構讓 SVG 在「畫線之前」就已經有不透明底色，避免箭頭線穿過節點 fill 時 z-order 失控；三層以上會在嵌入 PDF 後與外部背景複合，產生灰階偏移。

#### Type tag（節點左上 7px Geist Mono uppercase）

**規則**：每個節點左上角配置一個 7px uppercase 的小標籤，標示節點類別（如 `API`、`DB`、`EXT`、`CACHE`、`UI`），含 0.8 stroke 細框，使用 Geist Mono 字體與 0.08em letter-spacing。

```svg
<!-- 矩形 tag 細框（rx=2，非 pill；0.8 stroke） -->
<rect x="X+8" y="Y+6" width="28" height="12" rx="2"
      fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
<text x="X+22" y="Y+15" fill="#141413" font-size="7"
      font-family="'Geist Mono', monospace" text-anchor="middle"
      letter-spacing="0.08em">API</text>
```

**Why**：節點主文字（Geist sans）負責人類可讀名稱，type tag（Geist Mono）負責「這是哪一類元件」的視覺索引；分兩層字體在低資訊密度的 diagram 中仍能保留掃讀路徑。

#### Legend strip（viewBox 底部 ~60px）

**規則**：所有 SVG 在主要節點與箭頭繪製完成後，於 viewBox 底部預留約 60px 高度，放置一條 hairline `<line>` + 水平 legend 條目（每項一個 mini swatch + label），涵蓋該圖實際出現的所有節點類型與箭頭類型：

```svg
<!-- Hairline 分隔線 -->
<line x1="30" y1="LEGEND_Y-8" x2="VIEWBOX_W-30" y2="LEGEND_Y-8"
      stroke="#141413" stroke-opacity="0.10" stroke-width="0.8"/>
<!-- LEGEND 標題 -->
<text x="30" y="LEGEND_Y+8" fill="#504e49" font-size="8"
      font-family="'Geist Mono', monospace" letter-spacing="0.14em">LEGEND</text>
<!-- Items — 水平排列，~160px 間距，每項一個 swatch + label -->
```

- **例外**：當 SVG `viewBox` 寬度 < 400px（卡片內嵌、小型 diagram）可省略 legend strip，由內文補充說明替代

**Why**：把圖例放在 diagram 外部（而非節點之間）保留中央區域給結構資訊；hairline 分隔讓 legend 在視覺上歸屬「腳註區」而不是圖的一部分，避免讀者把 swatch 誤認為節點。

#### 抗 slop 精度約束

- 所有座標、寬度、間距必須是 **4 的倍數**
- 節點寬白名單 **12 檔**：{80, 96, 112, 120, 128, 140, 144, 160, 180, 200, 240, 320}
- 節點高：**32**（pill）/ **64**（standard）
- 焦點節點透過 `data-role="focal"` 屬性標記（**不**用 class），每張 SVG 最多 **2** 個 `data-role="focal"` 節點；焦點節點視覺走 `--brand` 描邊 + `--brand-tint` 填色 + `marker-end="url(#arrow-accent)"`
- `<text y>` ≥ font-size × 1.2（防文字切頂）
- 箭頭 endpoint 精確落在節點邊緣（透過 marker `refX="7"` 自動對齊）

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

#### 13 型 selection 表（v1 ref skeleton + status 揭露）

每段含 diagram 的 section 依 Layer 2 從本表 lookup 對應 ref。Status 欄一律對齊各 ref frontmatter：`complete` 表示有可直接重用的 example HTML；`ref-only` 表示僅有 ref 規格、example HTML 待 v2-N 補（renderer fallback 通用 SVG primitives）。

| Type | Best for | Reference | Status |
|------|----------|-----------|--------|
| architecture | 系統概覽 / data-flow / 整合 map / infra topology / 元件 + 連線 | `references/diagram-types/type-architecture.md` | `status: complete` |
| flowchart | 決策邏輯 / 演算法步驟 / "Should I…?" 分支 / onboarding routing / support-triage | `references/diagram-types/type-flowchart.md` | `status: ref-only` |
| sequence | request/response 流程 / protocol 交握 / 多 actor 互動 / API call trace / 事故重建 | `references/diagram-types/type-sequence.md` | `status: ref-only` |
| state | 有限狀態邏輯 / order status / auth state / connection lifecycle / form wizard | `references/diagram-types/type-state.md` | `status: ref-only` |
| er | database schema / API resource 關係 / domain model / aggregate boundary / 跨服務 ownership | `references/diagram-types/type-er.md` | `status: ref-only` |
| timeline | release 歷史 / project milestone / 事故時間線 / roadmap / changelog | `references/diagram-types/type-timeline.md` | `status: ref-only` |
| swimlane | 跨職能流程 / RACI flow / vendor handoff / multi-team workflow / 跨團隊責任歸屬 | `references/diagram-types/type-swimlane.md` | `status: ref-only` |
| quadrant | 優先級排序（Impact × Effort）/ 定位圖 / portfolio map / 2×2 decision / scenario planning | `references/diagram-types/type-quadrant.md` | `status: ref-only` |
| nested | 透過 containment 表達 hierarchy / scope boundary / CLAUDE.md cascade / trust zone / blast radius | `references/diagram-types/type-nested.md` | `status: ref-only` |
| tree | org chart / dependency tree / taxonomy / file tree / decision breakdown / skill tree | `references/diagram-types/type-tree.md` | `status: ref-only` |
| layers | OSI model / CSS cascade / context hierarchy / tech stack / abstraction layer / memory hierarchy | `references/diagram-types/type-layers.md` | `status: ref-only` |
| venn | 概念交集 / 跨類別共同屬性 / ikigai-style frame / 定位 sweet spot | `references/diagram-types/type-venn.md` | `status: ref-only` |
| pyramid | hierarchy of needs / prioritization rank / value pyramid / conversion funnel / content importance | `references/diagram-types/type-pyramid.md` | `status: ref-only` |

> `ref-only` 型 fallback 通用 SVG primitives（marker / paper-mask / type tag / legend strip 規格仍生效）；final-report 標 `degraded-type: <type-name>` 告知 v2-N 補 example HTML。

> **Forward note**：v2-N 補 dark/full variant 或新 SVG primitive 時，必須沿用 `design-token-resolver.md` 的 hex shape contract（`^#[0-9a-fA-F]{3,8}$`），不得另開 sink。

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

### 2. Visual render verification (Playwright)

After GATE PASS, render the HTML in headless Chromium via the bundled helper (Playwright is guaranteed installed by Stage 0). One invocation produces both the preview screenshot and a JSON probe of structural elements:

```bash
PROBE=$(python3 "$CLAUDE_SKILL_DIR/scripts/verify-render.py" \
  ".claude/book/{$SLUG}.html" \
  ".claude/book/{$SLUG}-preview.png")
echo "$PROBE"
```

`$PROBE` is a single-line JSON like:
```json
{"overflow": false, "has_paper": true, "has_h1": true, "has_h2": true, "svg_count": 3, "title": "…"}
```

Interpret results:
- If `overflow` is `true`: output 「⚠ 跑版偵測：有橫向溢出，請開啟 .claude/book/{$SLUG}-preview.png 手動確認。」
- If `has_paper`, `has_h1`, or `has_h2` is `false`: output 「⚠ 結構元素缺失：{element} 未出現在頁面中。」
- If the script exits non-zero (Playwright launch / navigation failure): output 「⚠ 視覺驗證無法執行，請手動開啟 .claude/book/{$SLUG}.html。」 and continue to completion report.
- If all checks pass: output 「✅ 視覺驗證通過」

> Why Playwright (not browser-use): browser-use's headless Chromium silently fails to load `file://` URLs (readyState reports complete but the DOM stays empty). Playwright handles `file://` correctly and is the project-standard E2E driver.

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
> - 預覽截圖（PNG）：永遠出現（Playwright 截圖在 Stage 4 §2 執行）
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
