---
name: venn
status: ref-only
example: null
---

# Venn / Set Overlap

**Best for**: 概念 / 領域交集、跨類別的共同屬性、「A 與 B 交會處」、ikigai-style frame（desirable × feasible × viable）、定位 sweet spot。

## Layout conventions

- **優先用 2 或 3 個圓**，避免 4+（不可讀，改用 matrix）；圓 stroke 1px hairline，每個 set 一個色（`--ink` / `--color-muted` / soft）。
- 圓 fill 走極低 opacity tint（`--ink @ 0.04` 或 `--color-muted @ 0.05`），overlap 區會自然疊出較深底；radii 在 set 大小相當時等大，差異有意義時按比例縮放，**不為美觀偽造等大**。
- **Set label 放在圓外**，絕不跨 stroke；`--font-sans` 12–14px 600 為 set name，可選 `--font-mono` 9px sublabel。
- **Intersection label** 放在 overlap 區內，`--font-sans` 12px 600 置中；overlap 過小時用 leader line 引出到 clear space；`--brand` 只上在**單一 focal 交集**（sweet spot），可選 brand stroke 或 clipPath-bounded brand tint fill；圓心與半徑皆可被 4 整除。

## Anti-patterns

- 區域未 label（讀者無法分辨哪個圓是哪個 set）。
  - *Why fails*：venn 的整個價值是「set 名 + 交集 label」帶來的語意；缺 label 只剩拓樸（兩個圓重疊）讀者必須回 prose 推敲哪個圓代表什麼，圖等同失效。
- 該重疊的圓未重疊（畫成相切或分離）。
  - *Why fails*：venn 的視覺承諾就是「重疊區存在 = 元素同時屬於多個 set」；不重疊等於宣告交集為空，與要表達的 sweet spot 語意直接矛盾。
- Set 大小明顯不同卻畫成等大圓。
  - *Why fails*：圓面積在讀者潛意識中對應 set 規模；等大圓會誤導對相對大小的判斷，例如把 1% 邊角案例與 80% 主流情境放在等大圓上，圖在量級上說謊。

## Examples

**Status: ref-only**. example HTML 待 v2-N 補。/book 遇此型時 fallback 通用 SVG primitives，final-report 標 `degraded-type: venn`。
