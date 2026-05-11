---
name: sequence
status: ref-only
example: null
---

# Sequence

**Best for**: request / response 流程、protocol 交握、多 actor 隨時間的互動、API call trace、事故重建（incident reconstruction）。

## Layout conventions

- Layer 3 derived token：`lifeline-color` 由 `--ink @ 0.30` 預計算為 solid hex（v1 ground truth `#b6b5af`），不得出現 alpha-channel CSS 函式形式；計算方式參見 `references/design-token-resolver.md`。
- Actor 為頂端水平排列的 box；每個 actor 下垂一條 dashed vertical line 作 lifeline，stroke 走上述 `lifeline-color`，stroke-width=1、stroke-dasharray="3,3" 固定。
- Message 為 lifeline 之間的 horizontal arrow，**時間 top→down**；activation bar 為 lifeline 上窄 rect（`w=8`，`--ink @ 0.06` fill，0.8 hairline stroke），跨越該 actor 持有控制權的區間，巢狀呼叫往內堆疊。
- Self-message 用 U 型短 loop 回到同一條 lifeline，label 放 loop 右側；return message 用 dashed line，**顏色同發起該 call 的線**。
- `--brand` 只能用在主要 success response 或 headline message，一條最多兩條，不可每條都上色。

## Anti-patterns

- Message arrow 向上指（時間倒流）。
  - *Why fails*：sequence diagram 唯一的 invariant 就是 y 軸代表單向時間；arrow 向上等於否定 y 軸語意，讀者無法判斷因果順序，整張圖的 grammar 崩壞。
- Activation bar 沒有 close（懸而未收）。
  - *Why fails*：activation bar 的語意是「這個 actor 在這個區間持有 control」，未 close 等於宣告 control 從未交還，與實際系統行為不符；同時破壞 nested call 的視覺對稱性。
- Label 坐在另一條 lifeline 之上。
  - *Why fails*：lifeline 是視覺骨架，label 壓在上面會讓 lifeline 與文字互相吃光，讀者掃讀時 y 位置就會錯位；應縮短 label 或將 y 移到 lifeline 間隔處。

## Examples

**Status: ref-only**. example HTML 待 v2-N 補。/book 遇此型時 fallback 通用 SVG primitives，final-report 標 `degraded-type: sequence`。
