---
name: pyramid
status: complete
example: inline
---

# Pyramid / Funnel

**Best for**: hierarchy of needs、prioritization rank、value pyramid、conversion funnel、content importance stack。

## Layout conventions

- **二擇一方向，不可混用**：pyramid（尖端朝上）= 頂端為最重要 / 最稀有 / 最有價值，底層為最基礎；funnel（尖端朝下）= 底端為 conversion（最小群），頂為 widest audience。
- 4–6 層為限；視覺由 `<path>` 梯形外輪廓 + 每層 `<rect>` callout 構成（**Kami spec 禁用 `<polygon>`**，見下 Examples 段），**層高一致**（56–72px）；寬度從 base 到 apex 線性遞減（pyramid）或 top 到 bottom 遞減（funnel），呈現真實 funnel 資料時寬度必須誠實（與 count / percentage 成比例）。
- 每層三段資訊：name label 置中`--font-sans` 12–14px 600；sublabel 在 name 下方或側邊`--font-mono` 9–10px；可選 side annotation 放右或左（funnel 的 drop-off 百分比，如 `−40%`）。
- 層間 1px hairline divider，外輪廓 1px `--color-muted` 或 `--ink`；fill 二擇一：subtle 漸層 tint **或**全 paper-2 + hairline divider；`--brand` 只上在**單一層**（pyramid 的 apex、funnel 的 conversion 層、或關鍵 bottleneck）。

## Anti-patterns

- 7 層以上。
  - *Why fails*：梯形層數一多每層垂直空間就被擠到無法容納 label，且讀者難以一眼數出層級；應壓縮（合併語意接近的層）或拆兩張圖。
- 用 pyramid 表達非 hierarchical 資料（純分類、平行比較）。
  - *Why fails*：pyramid 的視覺承諾是「上下有 rank 關係」（稀有度 / 重要性 / 規模）；用在無 rank 的資料上會誤導讀者建立根本不存在的階層，應改用 tree 或 bar chart。
- 寬度造假（drop-off 不等時偽裝成等寬遞減）。
  - *Why fails*：funnel 唯一的量化承諾是「寬度反映實際漏斗比例」；等寬遞減在視覺上抹平真實 conversion drop，讀者無法看出哪個階段流失嚴重，圖直接違背 honest data viz 原則。

## Examples

Inline example below — 5-level value pyramid（Vision[focal] / Strategy / Tactics / Execution / Foundation）。**Kami spec 禁用 `<polygon>`**，故梯形視覺由 `<path>` 描繪外輪廓 + 5 個 `<rect>` 階層 callout（寬度交替 {128, 160} 兩檔白名單）構成；節點寬白名單仍合規。完整 `<defs>` 三 chevron marker、兩層 paper-mask、1 個 `data-role="focal"` 節點（apex Vision）、所有 `x/y/width/height` 為 4 的倍數、legend strip。

```html
<figure class="diagram">
  <svg viewBox="0 0 1000 600" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="5-level value pyramid with focal Vision apex">
    <defs>
      <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">
        <circle cx="1" cy="1" r="0.9" fill="#E3E2DC"/>
      </pattern>
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

    <!-- Paper-mask layer 1（強制） -->
    <rect width="100%" height="100%" fill="#f5f4ed"/>
    <!-- Paper-mask layer 2（可選 dotted overlay） -->
    <rect width="100%" height="100%" fill="url(#dots)" opacity="0.55"/>

    <!-- ===== PYRAMID SILHOUETTE（path，非 polygon）===== -->
    <!-- 外輪廓三角形：apex (500, 96) → base-left (200, 460) → base-right (800, 460) → close -->
    <path d="M 500 96 L 200 460 L 800 460 Z"
          fill="#f1f0eb" stroke="#504e49" stroke-width="1"/>

    <!-- ===== LEVEL DIVIDERS（4 條 hairline 內部分層） ===== -->
    <line x1="440" y1="168" x2="560" y2="168"
          stroke="#141413" stroke-opacity="0.12" stroke-width="0.8"/>
    <line x1="380" y1="240" x2="620" y2="240"
          stroke="#141413" stroke-opacity="0.12" stroke-width="0.8"/>
    <line x1="320" y1="312" x2="680" y2="312"
          stroke="#141413" stroke-opacity="0.12" stroke-width="0.8"/>
    <line x1="260" y1="384" x2="740" y2="384"
          stroke="#141413" stroke-opacity="0.12" stroke-width="0.8"/>

    <!-- ===== LEVEL CALLOUTS（5 rect 節點，alternating {128, 160}，max 2 tiers） ===== -->
    <!-- L5 Apex: Vision — FOCAL（128，最窄符合 apex 視覺） -->
    <rect x="436" y="108" width="128" height="32" rx="6" fill="#f5f4ed"/>
    <rect data-role="focal"
          x="436" y="108" width="128" height="32" rx="6"
          fill="#EEF2F7" stroke="#1B365D" stroke-width="1.4"/>
    <rect x="444" y="112" width="28" height="12" rx="2"
          fill="transparent" stroke="#1B365D" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="458" y="121" fill="#1B365D" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">L5</text>
    <text x="500" y="130" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Vision</text>

    <!-- L4: Strategy（160） -->
    <rect x="420" y="184" width="160" height="32" rx="6" fill="#f5f4ed"/>
    <rect x="420" y="184" width="160" height="32" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="428" y="188" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="442" y="197" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">L4</text>
    <text x="500" y="206" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Strategy</text>

    <!-- L3: Tactics（128） -->
    <rect x="436" y="256" width="128" height="32" rx="6" fill="#f5f4ed"/>
    <rect x="436" y="256" width="128" height="32" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="444" y="260" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="458" y="269" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">L3</text>
    <text x="500" y="278" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Tactics</text>

    <!-- L2: Execution（160） -->
    <rect x="420" y="328" width="160" height="32" rx="6" fill="#f5f4ed"/>
    <rect x="420" y="328" width="160" height="32" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="428" y="332" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="442" y="341" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">L2</text>
    <text x="500" y="350" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Execution</text>

    <!-- L1: Foundation（128） -->
    <rect x="436" y="400" width="128" height="32" rx="6" fill="#f5f4ed"/>
    <rect x="436" y="400" width="128" height="32" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="444" y="404" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="458" y="413" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">L1</text>
    <text x="500" y="422" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Foundation</text>

    <!-- ===== UPWARD-VALUE ARROW（左外緣，accent，指向 focal apex） ===== -->
    <line x1="160" y1="440" x2="160" y2="120"
          stroke="#1B365D" stroke-width="1.4" marker-end="url(#arrow-accent)"/>
    <text x="148" y="284" fill="#1B365D" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="end" letter-spacing="0.08em">value ↑</text>

    <!-- ===== BREADTH ANNOTATION（右外緣，普通箭頭，向下） ===== -->
    <line x1="840" y1="120" x2="840" y2="440"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <text x="852" y="284" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.08em">breadth ↓</text>

    <!-- ===== LEGEND STRIP ===== -->
    <line x1="60" y1="540" x2="940" y2="540"
          stroke="#141413" stroke-opacity="0.10" stroke-width="0.8"/>
    <text x="60" y="560" fill="#504e49" font-size="8"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.14em">LEGEND</text>

    <rect x="140" y="552" width="16" height="12" rx="2"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <text x="160" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Level callout</text>

    <rect x="280" y="552" width="16" height="12" rx="2"
          fill="#EEF2F7" stroke="#1B365D" stroke-width="1.2"/>
    <text x="300" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Focal apex</text>

    <line x1="420" y1="556" x2="440" y2="556"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <text x="448" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Breadth axis</text>

    <line x1="560" y1="556" x2="580" y2="556"
          stroke="#1B365D" stroke-width="1.4" marker-end="url(#arrow-accent)"/>
    <text x="588" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Value axis</text>

    <line x1="700" y1="556" x2="720" y2="556"
          stroke="#2D5A8A" stroke-width="1.2" marker-end="url(#arrow-link)"/>
    <text x="728" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Cross-pyramid ref</text>
  </svg>
  <figcaption>圖：5-level value pyramid（Vision[focal] / Strategy / Tactics / Execution / Foundation）。梯形外輪廓走 `<path>`（無 polygon），階層 callout 寬交替 {128, 160}。</figcaption>
</figure>
```
