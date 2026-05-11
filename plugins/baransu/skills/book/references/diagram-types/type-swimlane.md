---
name: swimlane
status: ref-only
example: null
---

# Swimlane

**Best for**: 跨職能流程、RACI-style flow、vendor handoff、multi-team shipping workflow、跨團隊責任歸屬視覺化。

## Layout conventions

- Layer 3 derived token：`lane-A` = `--ink @ 0.08`、`lane-B` = `--ink @ 0.04`、`lane-C` = `--ink @ 0.02`（v1 ground truth 分別為 `#ebeae5` / `#f3f1ec` / `#f6f5f0`），預計算為 solid hex，不出現 `rgba(`；參見 `references/design-token-resolver.md`。
- Horizontal lane（或 vertical column）一個 actor / team 一條；lane 底色循環 `lane-A` / `lane-B` / `lane-C` 區分；lane label 在左 margin（或頂部）以 `--font-mono` eyebrow 標示。
- Lane divider 為 1px hairline；process step 為 rect，**只能放在執行該 step 的 actor 所屬 lane 內**；step 間以 arrow 連接表流向。
- Handoff（跨 lane 邊界的 arrow）是 swimlane 圖最重要的邊；`--brand` 留給導致最大耦合或延遲的那一個 handoff，一張圖一個；不要強迫每個 lane 步數相等，一 lane 一個 step 也可以。

## Anti-patterns

- Lane 沒有 label。
  - *Why fails*：swimlane 的整個價值就是「告訴讀者哪個步驟由誰負責」；缺 lane label 等於丟掉這個唯一資訊，整張圖退化成普通 flowchart 而且多了視覺雜訊。
- 一個 step 跨在兩條 lane 之間（責任不明）。
  - *Why fails*：lane 的語意承諾是 single owner；step 跨 lane 等於宣告「兩個 owner 共同負責」，但實際運作必有一方先動手，視覺上的 ambiguity 直接對應流程上的 ambiguity，圖反過來助長協作 bug。
- Arrow 在 lane 間 snake back-and-forth 來回鑽。
  - *Why fails*：來回鑽的 arrow 視覺上像迷宮，讀者無法 trace 主流向；應重排 step 順序讓 flow 大致直線，若無法 straighten 代表流程本身設計過於混亂，圖反映了該事實但無解決它。

## Examples

**Status: ref-only**. example HTML 待 v2-N 補。/book 遇此型時 fallback 通用 SVG primitives，final-report 標 `degraded-type: swimlane`。
