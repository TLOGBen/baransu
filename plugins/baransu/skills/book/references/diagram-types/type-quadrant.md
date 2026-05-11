---
name: quadrant
status: ref-only
example: null
---

# Quadrant

**Best for**: 優先級排序（Impact × Effort）、定位圖（Reach × Frequency）、portfolio map、2×2 decision frame、scenario planning。

## Layout conventions

- 2×2 grid，axis line 為 1px `--ink` cross 穿過中心；axis arrow tip 收在 viewBox 邊內側 ~60–80px，留呼吸空間給 label。
- **Axis label Jobs-minimal**：每個 arrow tip 一個 **單字**，不帶 `↑` / `→` 等 glyph、不帶 `(HIGH/LOW)` 括號修飾；`--font-mono` 9px regular weight、tracked `0.18em`、uppercase；側 flanking arrow tip，不可坐在 axis line 上。
- Item 為 small labeled dot（`r=4`），分布在四象限內；label 距 dot 8–10px，**不可跨 axis line**；item 數量上限 ~12，超過則 cluster 或拆圖。
- `--brand` 只用在「do first」的單一 item（通常落在右上象限），不可上在多個 item，也不可填色整個象限格。

## Anti-patterns

- 四個象限分別填四種不同色塊。
  - *Why fails*：quadrant 的資訊承載靠「位置 + label」，色塊只是噪音；多色填底會與單一 `--brand` focal 競爭，且色盲讀者無法分辨象限差異，違反 Kami 三語意色限制。
- Item 落在 axis line 上（象限歸屬模糊）。
  - *Why fails*：axis 把平面切成四區的前提是 item 確切在某一區內；落在線上等於宣告「兩個象限都成立」，破壞 2×2 frame 的決策力，讀者無法回答「這個 item 屬於哪一類」。
- 缺 axis name 或 label 上標 `↑ HIGH IMPACT` 之類的多餘修飾。
  - *Why fails*：缺 name 時讀者不知 x/y 各代表什麼維度，圖等同沒有座標系；額外的 `↑` glyph 與 `HIGH / LOW` 括號則重複了 arrow 本身已表達的方向資訊，視覺上累贅且違反 Jobs-minimal 原則。

## Examples

**Status: ref-only**. example HTML 待 v2-N 補。/book 遇此型時 fallback 通用 SVG primitives，final-report 標 `degraded-type: quadrant`。
