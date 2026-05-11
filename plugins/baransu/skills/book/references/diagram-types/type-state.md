---
name: state
status: ref-only
example: null
---

# State Machine

**Best for**: 有限狀態邏輯——order status、auth state、connection lifecycle、form wizard、job queue status。

## Layout conventions

- Layer 3 derived token：`state-active` = `--brand`（v1 ground truth `#1B365D`），`state-inactive` = `--ink @ 0.05`（v1 ground truth `#f1f0eb`）；皆預計算為 solid hex，不出現 `rgba(`，參見 `references/design-token-resolver.md`。
- State 為 rounded rectangle（`rx=8`），label 用 `--font-sans`；start = filled `--ink` dot（`r=6`），end = ringed dot（外 `r=8` outline、內 filled `r=5`）。
- Transition 為 curved arrow，label 用 `--font-mono`，格式 `event [guard] / action`，不需要的欄位省略；self-loop 從 state 上方繞回。
- 主流方向沿 left→right 或 top→down 對齊；rearrange 直到 transition 不交叉，再考慮繪製。
- `--brand` / `state-active` 只能上在讀者最該注意的單一 state——通常是 error state 或 happy completion，二擇一。

## Anti-patterns

- Transition 數量超過 `states × 2`。
  - *Why fails*：經驗值上這代表你正在把兩個獨立 state machine 硬畫成一張；視覺上會出現 hairball，讀者無法 trace 任何一條路徑，應拆分為兩張圖。
- "From any state" transition 從每個 state 各畫一條到同一目標（如全部 → Error）。
  - *Why fails*：N 條重複線把畫面瓜分，但語意只是「any」一個 quantifier；應改為單一 annotation（`* → Error on timeout`），讓視覺密度與資訊密度對齊。
- 未 label 的 transition。
  - *Why fails*：state machine 的核心問題就是「在什麼條件下從 A 跳到 B」，省掉 label 等於丟掉這張圖唯一回答的問題，剩下的拓樸資訊用 list 就能呈現。

## Examples

**Status: ref-only**. example HTML 待 v2-N 補。/book 遇此型時 fallback 通用 SVG primitives，final-report 標 `degraded-type: state`。
