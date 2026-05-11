---
name: layers
status: ref-only
example: null
---

# Layer Stack

**Best for**: OSI model、CSS cascade、context hierarchy、tech stack、abstraction layer、memory hierarchy。

## Layout conventions

- 水平 band 垂直堆疊；每層為 full-width rectangle（同 x、同 width），4–6 層為限；layer 高度 56–72px，寬度通常 800–880px 落在 1000px viewBox 內。
- 每列由左至右含三段：(1) **index tag**（`L3` / `07` / `APPLICATION`）`--font-mono` 8–9px eyebrow；(2) **layer name** 略偏左中`--font-sans` 14–16px 600；(3) **sublabel / note** 靠最右`--font-mono` 9–10px `--color-muted`。
- 層間 border 為 1px hairline `--ink @ 0.12`；外輪廓 1px `--ink` 或 `--color-muted`；fill 二擇一：交替淡色（`--parchment` / paper-2）**或**全 `--parchment` 配 hairline divider，**選定後守一個**不可混用。
- 左 margin 外側放方向指示（small up/down arrow + `--font-mono` label，如 `abstraction ↑` / `packets ↓`）；`--brand` 只上在**單一 focal layer**（stroke + 微 tint fill），代表 bottleneck / pay-rent layer / 討論主軸。

## Anti-patterns

- 把實際非 hierarchical 的概念硬塞成 layer。
  - *Why fails*：layer stack 的承諾是「上層依賴下層、下層為上層提供 abstraction」；用它表達 cross-cutting concern（如 monitoring）或 peer relationship 會讓讀者誤建依賴關係，應改用 swimlane 或 architecture。
- 層編號跳號（L3 → L5 中間沒 L4 也沒解釋）。
  - *Why fails*：layer 編號是 hierarchy 唯一可用的序列承諾；跳號代表「中間有東西但我沒畫」，讀者無法判斷是設計漏掉還是刻意省略，hierarchy 的完整性破功。
- 每層上不同色塊（rainbow stack）。
  - *Why fails*：layer 的 hierarchy 是靠垂直位置 + 編號傳遞，色塊只是噪音；多色讓讀者誤以為「每層代表一種類別」而非「上下層級」，且與 single-brand focal 規則衝突。

## Examples

**Status: ref-only**. example HTML 待 v2-N 補。/book 遇此型時 fallback 通用 SVG primitives，final-report 標 `degraded-type: layers`。
