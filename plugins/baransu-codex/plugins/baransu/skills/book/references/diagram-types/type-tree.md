---
name: tree
status: ref-only
example: null
---

# Tree / Hierarchy

**Best for**: org chart、dependency tree、taxonomy、file tree、decision breakdown、skill tree。

## Layout conventions

- Root 置頂、children 向下扇開（或 root 在左、children 向右）；root 不能有兩個。
- Node 為 small labeled rectangle（`rx=6`），name 用 `--font-sans` 12px 600，可選 sublabel 用 `--font-mono` 9px；node 寬度 120–180px，高度 40–52px，整張圖只用 2 種寬度。
- **Connector 一律 orthogonal（elbow）不畫對角線**：parent 下一條 short vertical → horizontal bus 連接 sibling → 每個 child 上方 short vertical 入頂邊；stroke 走 `--color-muted` 1px；connector 必須先畫，node 後畫（z-order）。
- 最大深度 4（root + 3 tier）、每層最大寬度 5；`--brand` 只能上在**單一 node**（root 或關鍵 leaf，二擇一，不可兩者皆有）。

## Anti-patterns

- 在單張圖畫 5 層以上深度。
  - *Why fails*：tree 越深 leaf 字越小、垂直空間越擠，5 層後讀者無法掃讀整體結構；應水平拆分為 sub-tree 或改用 nested containment 重新表達。
- Node 寬度自由發揮、每個都不一樣。
  - *Why fails*：tree 結構本應靠拓撲傳遞 hierarchy，寬度變化會被讀者誤讀為「這個 node 比較重要」；統一 2 種寬度可讓視覺節律穩定，讓讀者聚焦在連線結構而非 box 尺寸。
- 跳級連線（parent 直接連到 grandchild，中間 node 不畫）。
  - *Why fails*：tree 的語意是「parent → child」單階關係，跳級線等於宣告中介層級不存在，但實際 tree 結構仍有；視覺上讀者會誤判 depth，導致對整體 hierarchy 的錯估。

## Examples

**Status: ref-only**. example HTML 待 v2-N 補。/book 遇此型時 fallback 通用 SVG primitives，final-report 標 `degraded-type: tree`。
