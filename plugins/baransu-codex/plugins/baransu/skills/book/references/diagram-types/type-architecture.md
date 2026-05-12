---
name: architecture
status: complete
example: assets/example-architecture-kami.html
---

# Architecture

**Best for**: 系統概覽（system overview）、資料流圖（data-flow）、整合 map（integration map）、基礎設施拓樸（infra topology）、元件 + 連線（components & connections）。

## Layout conventions

- 依 tier 或 trust boundary 分群（frontend → backend → data；public → private）；同群節點水平或垂直對齊，群間以間距區隔，不靠連線去暗示分層。
- 主流方向選 LTR 或 TTB 一個守一個；不要在同一張圖內混用兩個主流方向。次要回饋線（callback、retry）可逆向，但箭頭一定要顯式標出。
- 線先畫、boxes 後畫：SVG 內箭頭 `<line>` 先進 DOM，節點 `<rect>` / `<g>` 後進，z-order 才會把連線壓在節點底下，避免箭頭尾巴穿過節點外框。
- 1–2 個焦點節點用 `data-role="focal"` 屬性標記（**非** class）；焦點節點視覺走 `--brand-tint` 填色 + `--brand` 描邊，並以 `marker-end="url(#arrow-accent)"` 收尾。每張 SVG 最多 2 個 focal，超過則「重點」就消失。
- Dashed boundary rectangle 標 region（VPC、security group、trust zone）；boundary 標籤坐在 `--parchment` 色 mask 上，覆蓋 dashed 線條與標籤交會處，避免線壓字。
- 節點寬度走 grid 的 12 檔之一（如 96 / 144 / 192 / 240px），不要每個節點寬度自由發揮；視覺節律一致時讀者掃讀速度才會穩定。
- 節點內嵌字 14–24px：超過 24 看起來像 hero、低於 14 在 1× SVG 下會糊。標題用 `--font-sans`、metric / id 用 `--font-mono`、單位用 `--color-muted`。
- 三個 marker（`arrow` / `arrow-accent` / `arrow-link`）在 `<defs>` 內統一定義，屬性固定 `markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"`；不再手寫箭頭 path，避免 viewBox 縮放下對位偏差。

## Anti-patterns

- **每個 box 都 focal**（全部 `--brand-tint` 填、`--brand` 描邊）。
  - *Why fails*：focal 的本質是相對比較——當所有節點都「重點」，視覺階層就崩，讀者無法在 3 秒內鎖定主流路徑或主整合點，圖等同沒有重點。
- **雙向箭頭當單向意義已經明確**（例如 `Browser ↔ CDN`，但實際只關心讀取路徑）。
  - *Why fails*：雙向箭頭增加一個方向的雜訊，讀者得多花一拍判斷「這條線到底要看哪一邊」；同時讓真正需要雙向語意的節點（如 cache write-back）失去辨識度。
- **Legend 飄在 diagram canvas 內**，與節點或連線重疊。
  - *Why fails*：legend 是 meta-information，與 diagram body 屬不同閱讀層級；放在 canvas 內會與節點碰撞、被連線穿過，讀者得在「讀圖」與「對照 legend」之間反覆切換視焦。應放在 SVG 底部約 60px 的 legend strip（hairline 隔開、horizontal items）或 canvas 外。
- **用顏色標 node type 而非用 shape**（例如所有 service 用紅色、所有 datastore 用藍色）。
  - *Why fails*：Kami 規格僅給三個語意色（`--brand` / `--brand-tint` / `--color-muted`），多餘的色彩會 over-load 配色系統，與 focal 的語意衝突，色盲讀者也無法分辨；type 區分應走 shape（rect / cylinder / hexagon）或 dashed border，把色彩留給 focal 與 boundary。

## Examples

- `assets/example-architecture-kami.html` — minimal Kami（v1 唯一完整 example；對應本 ref 的 `example` 欄位）
- `assets/example-architecture-dark.html` — minimal dark variant（v3+ 規劃，v1 不出貨）
- `assets/example-architecture-full.html` — full editorial（v3+ 規劃，v1 不出貨）
