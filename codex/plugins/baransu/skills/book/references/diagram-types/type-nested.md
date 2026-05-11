---
name: nested
status: ref-only
example: null
---

# Nested Containment

**Best for**: 透過 containment 表達 hierarchy——scope boundary、CLAUDE.md cascade、trust zone、folder nesting、blast radius。外 = 寬泛，內 = 具體。

## Layout conventions

- 3–5 個 rounded rectangle（`rx=8`）巢狀，inset padding 一致（建議 horizontal 24–32px、vertical 32–36px）；padding 不規則 = 看起來像意外。
- 每層 label 落在左上以 `--font-mono` eyebrow 風格（7–8px、letter-spacing 0.14em）；label 坐在 `--parchment` 色 mask rect 上，遮住與 ring 頂邊的交會處避免線壓字。
- Stroke 階梯：最外圈 faint（`--color-muted` 淡）→ 中層 `--color-muted` → 內層 `--ink` → 最內層 focal 走 `--brand`；fill 同樣從外到內 opacity 漸升，最內層用 `--brand-tint`。
- 可選 file-icon glyph（折角 rect）放在每層內側暗示 scope content；italic `--font-serif` 旁注（參見 `references/primitive-annotation.md`）最多 1–2 條，多了會搶 hierarchy 主軸。

## Anti-patterns

- 超過 6 層 nesting。
  - *Why fails*：每多一層內側面積便砍半，最內層字會小到看不見、stroke 也與背景混；超過 6 層代表 hierarchy 本身結構過深，應拆 sub-diagram 而非硬塞在一張圖。
- 各層 padding 不對稱（左右不等、上下不等）。
  - *Why fails*：規則 padding 是讀者辨識「這是 hierarchy 而非任意圖形」的視覺信號；padding 不均勻會讓圖看起來像草稿或 bug，破壞 nested containment 的 grammar，讀者無法立即判斷層級關係。
- 內容物放在 ring 裡但其實不屬於該層級（如 metadata、legend、unrelated note）。
  - *Why fails*：nested 的承諾是「ring 邊界 = scope 邊界」，放入無關物件會讓 scope 語意鬆動，讀者無法區分「這是該層級的成員」還是「這只是恰好畫在這」，hierarchy 表達失效。

## Examples

**Status: ref-only**. example HTML 待 v2-N 補。/book 遇此型時 fallback 通用 SVG primitives，final-report 標 `degraded-type: nested`。
