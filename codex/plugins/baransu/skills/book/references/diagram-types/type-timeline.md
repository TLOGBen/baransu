---
name: timeline
status: ref-only
example: null
---

# Timeline

**Best for**: release 歷史、project milestone、事故時間線（incident timeline）、roadmap、changelog 視覺化。

## Layout conventions

- 中央一條 horizontal hairline baseline（`stroke-width=1`，`--color-muted`）；tick marks 落在 time boundary（quarters / months / sprints），下方 date label 用 `--font-mono`。
- Event 為 baseline 上 small filled circle（`r=4`，`--ink`）；label 上下交替排列以避免碰撞，靠 1px hairline drop 連回 circle。
- Major milestone 為 `--brand` 顏色的 circle（`r=6`）+ `--font-sans` bold label；一張圖只 highlight 真正的「里程碑」，不可每個 event 都標 brand。
- 時間刻度必須誠實：間隔不等時 circle 間距也必須不等；密度過高的區段顯式做 axis break，不為美觀偽造 linear spacing。

## Anti-patterns

- 把時間上不等距的 event 等距排列。
  - *Why fails*：timeline 唯一的語意承諾就是「x 軸代表時間」；等距排列把不等變相等，讀者會誤判 release cadence 或事故頻率，圖直接說謊。
- 缺少 axis 單位 label（「這是 day / week / quarter？」）。
  - *Why fails*：timeline 的 tick 數字（如 `2024-Q1`）必須有單位 context，否則 `Q1` 跟 `Sprint 1` 在視覺上長一樣；缺單位 = reader 必須回 prose 推測，違背 diagram 自我承載的原則。
- 多個 label 沒做垂直 offset，全擠在 baseline 一側。
  - *Why fails*：相鄰 event 的 label 會互相 overlap 到看不清字；timeline 規範 label 必須上下交替排列正是為了在 1D 空間用 2D 來解決碰撞，省略此 offset 等於放棄可讀性。

## Examples

**Status: ref-only**. example HTML 待 v2-N 補。/book 遇此型時 fallback 通用 SVG primitives，final-report 標 `degraded-type: timeline`。
