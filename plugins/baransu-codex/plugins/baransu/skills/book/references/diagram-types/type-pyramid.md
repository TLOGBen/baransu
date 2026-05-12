---
name: pyramid
status: ref-only
example: null
---

# Pyramid / Funnel

**Best for**: hierarchy of needs、prioritization rank、value pyramid、conversion funnel、content importance stack。

## Layout conventions

- **二擇一方向，不可混用**：pyramid（尖端朝上）= 頂端為最重要 / 最稀有 / 最有價值，底層為最基礎；funnel（尖端朝下）= 底端為 conversion（最小群），頂為 widest audience。
- 4–6 層為限；每層為 SVG `<polygon>` 4-point 梯形，**層高一致**（56–72px）；寬度從 base 到 apex 線性遞減（pyramid）或 top 到 bottom 遞減（funnel），呈現真實 funnel 資料時寬度必須誠實（與 count / percentage 成比例）。
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

**Status: ref-only**. example HTML 待 v2-N 補。/book 遇此型時 fallback 通用 SVG primitives，final-report 標 `degraded-type: pyramid`。
