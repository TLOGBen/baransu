# SVG Rendering Rules — Stage 3 §4

僅在 long-form HTML 含 `<figure class="diagram">` 區塊（Stage 2A flagged section）時讀本檔。

> **Token 命名**：本檔規格使用 v1.3 baransu canonical token names。hex 值欄位列的是 Kami preset 預設值，作為 reference；實作時應從 `{project_root}/tokens.css` 解析該 preset 的實際 hex（swiss `--paper` = `#fafaf8`、google-design `--paper` = `#FEF7FF`、etc.）。

> Upstream anchors re-verified at tw93/Kami@5cd7c8e (2026-06-10): diagrams.md L49 / L79 / L86 unchanged.

## §4.1 色彩 token（SVG 角色）

所有 SVG fill / stroke **禁用 `rgba()`**，一律使用 solid hex token：

| SVG 角色 | Canonical 變數 | Kami hex 預設 |
|----------|---------------|--------------|
| Canvas 底色 | `--paper` | `#f5f4ed` |
| 標準節點填色 | `--surface` | `#faf9f5` |
| 標準節點描邊 / 主要文字 | `--ink` | `#141413` |
| 焦點節點填色 | `--brand-tint` | `#EEF2F7` |
| 焦點節點描邊 | `--accent` | `#1B365D` |
| 標準箭頭 / 次要文字 | `--text-muted` | `#504e49` |

> CSS `box-shadow` 中的 `rgba()` 不受限（非 SVG 屬性）。

## §4.2 必備 `<defs>` 片段（每張 SVG 開頭必加）

```svg
<defs>
  <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">
    <circle cx="1" cy="1" r="0.9" fill="#E3E2DC"/>
  </pattern>
  <!-- Chevron (stroked, non-filled) — WeasyPrint 不支援 marker orient="auto"，
       一律用 path stroke 手繪 chevron 取代 filled polygon。 -->
  <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto">
    <path d="M2 1 L8 5 L2 9" fill="none" stroke="#504e49"
          stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
  </marker>
  <marker id="arrow-accent" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto">
    <path d="M2 1 L8 5 L2 9" fill="none" stroke="#1B365D"
          stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
  </marker>
  <marker id="arrow-link" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto">
    <path d="M2 1 L8 5 L2 9" fill="none" stroke="#2D5A8A"
          stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
  </marker>
</defs>
```

## §4.3 Marker defs（箭頭走 chevron `<path>`，三個 id 固定）

**規則**：每張含箭頭的 SVG 必須在 `<defs>` 內定義以下三個 marker，並以 `marker-end="url(#…)"` 引用；箭頭幾何**一律用 stroked chevron path**（`d="M2 1 L8 5 L2 9"`，`fill="none"`，`stroke-linecap="round"`），不再使用 filled polygon、也不手繪箭頭 path。

| Marker id | 對應用途 | stroke |
|-----------|----------|--------|
| `arrow` | default（一般 / 內部流向，muted） | `#504e49`（`--text-muted`） |
| `arrow-accent` | focal / 主流（accent 色） | `#1B365D`（`--accent`） |
| `arrow-link` | external / API call / 跨界 | `#2D5A8A`（`--brand-light`） |

**marker 屬性固定**：`markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto"`；chevron path 固定 `d="M2 1 L8 5 L2 9"`、`stroke-width="1.5"`、`stroke-linecap="round"`、`stroke-linejoin="round"`、`fill="none"`。

**Why**：WeasyPrint / 多數靜態 PDF renderer 對 `<marker orient="auto">` 旋轉 + `<polygon fill>` 的支援不一致，會出現箭頭翻轉或填色失蹤；改用 stroked chevron path 在所有 print pipeline 都對齊。同時 chevron（線描，非實心）也與 Kami `references/diagrams.md` L86 直接對齊，是 Kami 視覺簽名之一。三個語意分層（一般 / focal / external）才能與「焦點節點 ≤ 2」「跨系統呼叫」兩條規格在 SVG 層對齊。

**SVG 引用範例**：

```svg
<line x1="120" y1="80" x2="240" y2="80"
      stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
<line x1="120" y1="120" x2="240" y2="120"
      stroke="#1B365D" stroke-width="1.4" marker-end="url(#arrow-accent)"/>
```

## §4.4 兩層 paper-mask（節點背景與 canvas 底）

**規則**：每張 SVG 在 `<defs>` 後**先後**疊兩層 mask，再開始畫節點與箭頭：

```svg
<!-- Layer 1（必選）：全幅 paper fill -->
<rect width="100%" height="100%" fill="#f5f4ed"/>
<!-- Layer 2（可選）：dotted pattern overlay -->
<rect width="100%" height="100%" fill="url(#dots)" opacity="0.55"/>
```

- Layer 1（**強制**）：全幅 `<rect width="100%" height="100%" fill="{paper-token}"/>`，paper-token 走 `--paper`
- Layer 2（**可選**）：全幅 `<rect width="100%" height="100%" fill="url(#dots)" opacity="0.55"/>`，僅在長文 / 單頁 hero diagram 採用；產品頁或卡片內嵌時省略以避免紋路堆疊成噪訊
- **不做三層**：v1 規格明文禁止第三層 mask 堆疊（如 vignette、tint wash）；Unknown #3 留待 v1 dogfood 後再決定是否升級

**Why**：兩層結構讓 SVG 在「畫線之前」就已經有不透明底色，避免箭頭線穿過節點 fill 時 z-order 失控；三層以上會在嵌入 PDF 後與外部背景複合，產生灰階偏移。

## §4.5 Type tag（節點左上 7px Geist Mono uppercase）

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

## §4.6 Legend strip（viewBox 底部 ~60px）

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

## §4.7 抗 slop 精度約束

- 所有座標、寬度、間距必須是 **4 的倍數**
- 節點寬白名單 **3 檔**（Kami `references/diagrams.md` L79 對齊）：{`128`, `144`, `160`}；單張 SVG 同時最多用 2 檔，混用 3 檔即 anti-slop fail
  - **例外**：viewBox 寬度 < **360px**（卡片內嵌 / 小型 diagram）可壓 **2 檔**（建議 {128, 144} 或 {128, 160}），仍須保持 2 檔節奏，**不可**個別客製出非白名單寬度
- 節點高：**32**（pill）/ **64**（standard）
- 焦點節點透過 `data-role="focal"` 屬性標記（**不**用 class），每張 SVG 最多 **2** 個 `data-role="focal"` 節點；焦點節點視覺走 `--accent` (`#1B365D`) 描邊 + **`#EEF2F7` fill**（Kami `diagrams.md` L49 對齊，**不**走 `--surface-strong`）+ `marker-end="url(#arrow-accent)"`
- `<text y>` ≥ font-size × 1.2（防文字切頂）
- 箭頭 endpoint 精確落在節點邊緣（透過 marker `refX="8"` 自動對齊 chevron 尖端）
- focal 節點必須對應 caption 中 `<span class="hl">` 強調的元素；focal 與 caption 強調詞錯位即 anti-slop fail（Kami `diagrams.md` anti-slop 表對齊）

## §4.8 嵌入字體校正（嵌入 A4 後 scale ≈ 0.47）

| 角色 | 字體大小 |
|------|--------|
| H2 / 焦點節點 | 24 |
| Body / 標準文字 | 22-24 |
| H3 / 子標籤 | 18-20 |
| Caption | 15-16 |
| Mono tag | 14 |

## §4.9 14 型圖表路由決策樹（first-match）

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

## §4.10 13 型 selection 表（v1 ref skeleton + status 揭露）

每段含 diagram 的 section 依 Layer 2 從本表 lookup 對應 ref。Status 欄一律對齊各 ref frontmatter（事實同步，可 `grep '^status:' references/diagram-types/type-*.md` 二值驗證）：`complete` 表示該 ref 內含 `example: inline` 的可直接重用 SVG example HTML，renderer 應 reuse 該骨架；`ref-only` 表示僅有 ref 規格、example HTML 待補（renderer fallback 通用 SVG primitives）。13 型目前 frontmatter **全部 `status: complete` + `example: inline`**，本表與其對齊；`ref-only` 列僅為未來新增型尚未附 example 時的保留語義。

| Type | Best for | Reference | Status |
|------|----------|-----------|--------|
| architecture | 系統概覽 / data-flow / 整合 map / infra topology / 元件 + 連線 | `references/diagram-types/type-architecture.md` | `status: complete` |
| flowchart | 決策邏輯 / 演算法步驟 / "Should I…?" 分支 / onboarding routing / support-triage | `references/diagram-types/type-flowchart.md` | `status: complete` |
| sequence | request/response 流程 / protocol 交握 / 多 actor 互動 / API call trace / 事故重建 | `references/diagram-types/type-sequence.md` | `status: complete` |
| state | 有限狀態邏輯 / order status / auth state / connection lifecycle / form wizard | `references/diagram-types/type-state.md` | `status: complete` |
| er | database schema / API resource 關係 / domain model / aggregate boundary / 跨服務 ownership | `references/diagram-types/type-er.md` | `status: complete` |
| timeline | release 歷史 / project milestone / 事故時間線 / roadmap / changelog | `references/diagram-types/type-timeline.md` | `status: complete` |
| swimlane | 跨職能流程 / RACI flow / vendor handoff / multi-team workflow / 跨團隊責任歸屬 | `references/diagram-types/type-swimlane.md` | `status: complete` |
| quadrant | 優先級排序（Impact × Effort）/ 定位圖 / portfolio map / 2×2 decision / scenario planning | `references/diagram-types/type-quadrant.md` | `status: complete` |
| nested | 透過 containment 表達 hierarchy / scope boundary / CLAUDE.md cascade / trust zone / blast radius | `references/diagram-types/type-nested.md` | `status: complete` |
| tree | org chart / dependency tree / taxonomy / file tree / decision breakdown / skill tree | `references/diagram-types/type-tree.md` | `status: complete` |
| layers | OSI model / CSS cascade / context hierarchy / tech stack / abstraction layer / memory hierarchy | `references/diagram-types/type-layers.md` | `status: complete` |
| venn | 概念交集 / 跨類別共同屬性 / ikigai-style frame / 定位 sweet spot | `references/diagram-types/type-venn.md` | `status: complete` |
| pyramid | hierarchy of needs / prioritization rank / value pyramid / conversion funnel / content importance | `references/diagram-types/type-pyramid.md` | `status: complete` |

> **Fallback（僅 ref-only 型觸發）**：當且僅當某型 frontmatter 仍為 `status: ref-only`（目前 13 型皆非此狀態，故當前無型別走此路徑）時，renderer fallback 通用 SVG primitives（marker / paper-mask / type tag / legend strip 規格仍生效），並於 final-report 標 `degraded-type: <type-name>` 告知補 example HTML。`status: complete` 型一律 reuse 該 ref 的 `example: inline` SVG 骨架，不得降級為通用 primitives。

> **Forward note**：v2-N 補 dark/full variant 或新 SVG primitive 時，必須沿用 `design-token-resolver.md` 的 hex shape contract（`^#[0-9a-fA-F]{3,8}$`），不得另開 sink。
