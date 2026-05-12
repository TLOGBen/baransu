# slide-checklist.md

> P0 lint rules for `/design` slide output. Each rule uses a three-column structure: **現象 → 根因 → 做法**. Audience: `check.py` lint source and slide-core authors.

---

## P0-1：標題不可 `text-align:center`

- **Scope**: PPT only（long-form 標題由 typography 自行處理，不受此限）。
- **現象**: slide-core HTML 的 `<h1>` / `<h2>` 套上 `text-align: center`，導致左對齊網格被破壞、行長度與 Swiss 主軸不一致。
- **根因**: 作者沿用簡報習慣將「標題」視同「居中元素」，忽略 Swiss preset 以 baseline grid + 左對齊為主軸；cover/closing/kpi-grid 三種版式的標題對齊由 preset `tokens.css` 控制（如 `--swiss-cover-title-align`），不該由 slide-core inline 寫死。
- **做法**: 移除 `<h1>` / `<h2>` 上所有 `text-align: center` 宣告；對齊一律走 token。例外：`section` 與 `quote` 兩版式可置中（已在 preset tokens 中設定）；`cover` / `closing` / `kpi-grid` 標題對齊由 preset tokens.css 決定，slide-core 不可寫死。

---

## P0-2：圖片不可 `object-position: top center`

- **Scope**: PPT only。
- **現象**: 人物或場景照在 `content-2col` / `compare` / `cover` 版式中設成 `object-position: top center`，導致人物下巴、肩膀、視線焦點被裁切。
- **根因**: 作者依「頭頂貼齊頂部」直覺設定，未考慮人臉視覺重心在「上 1/3」處（約 35%）；`top center` 把整張臉壓到框頂，反而失衡。
- **做法**: 人物 / 場景照一律改用 `object-position: center 35%`（見 `slide-image-prompts.md` 第 2 節對照表）；圖表類用 `object-fit: contain` 並 `center center`。建議在 `check.py` 加入 regex `object-position:\s*top\s+center` 偵測。

---

## P0-3：每張投影片至多 1 個 `<h1>`

- **Scope**: PPT only（long-form 為單篇文件，`<h1>` per file 而非 per slide）。
- **現象**: 同一張 slide-core HTML 內出現多個 `<h1>`，破壞 outline 與 a11y heading hierarchy；輔助科技讀屏會誤判為多個獨立 section。
- **根因**: 作者把「視覺上的大字」一律標 `<h1>`，未區分 H1（slide 主標題）與 H2（slide 內副標 / 區塊標）；9 版式中只有 `cover` 應使用 H1 作為主標，其餘 8 版式 H1 槽位最多 1 個（且常為空，由 H2 承擔）。
- **做法**: per-slide scope：每張 slide-core HTML 最多 1 個 `<h1>`。`content-bullets` / `content-2col` / `data` / `kpi-grid` / `compare` 等版式的區塊標題改用 `<h2>` / `<h3>`。`check.py` 加入 per-slide `<h1>` count > 1 偵測。

---

## P0-4：bullets `<ul>` / `<ol>` direct child `<li>` ≤ 5

- **Scope**: both（PPT 強制；long-form 為建議上限，超過時 lint 出 warning）。
- **現象**: 單一 `<ul>` 或 `<ol>` 內直接子 `<li>` 超過 5 條，導致 slide 文字密度爆表、字級被迫縮小至不可讀，違反 Swiss preset 的閱讀距離設計（≥ 2m）。
- **根因**: 作者把「待辦清單」整段貼進 slide，未做資訊取捨；忽略 slide 不是文件，超過 5 條視覺即雜訊。多份清單（例如 `content-2col` 左右各一）各自獨立計算上限。
- **做法**: 單一 `<ul>` / `<ol>` direct child `<li>` 上限 = 5。多份清單各算（左欄 5 + 右欄 5 合法）。超過時拆 slide 或合併語義相近項。`check.py` 對每個 `<ul>` / `<ol>` 計算 direct `<li>`（不含巢狀），> 5 時報 P0-4。

---

## P0-5：`--format ppt` 下 SVG 內無 `<text>` 作可見標籤

- **Scope**: PPT only（long-form 不受此限；long-form SVG 可內嵌 `<text>` 作圖說）。
- **現象**: slide-core HTML 內嵌 SVG 使用 `<text>` 元素繪製可見的圖例 / 軸標 / 註記，與外層 HTML typography 不一致，且字級不受 `tokens.css` 控制，無法跟著 preset 切換。
- **根因**: 作者沿用 Figma / Illustrator 匯出習慣，把標籤打包進 SVG；slide-core 的 `--format ppt` 模式要求 SVG 為「純圖形向量」，所有文字標籤由外層 HTML（`<figcaption>` / `<aside>`）負責，以便 token 控制與 a11y 讀取。
- **做法**: PPT 模式下 SVG 內**不可**有 `<text>` 元素作可見標籤；改用 HTML 標籤覆蓋在 SVG 上方，或放進 `<figcaption>`。`validate-output.ts` GATE-A 至 GATE-E 已涵蓋此規則（PPT mode SVG 限制）；`check.py` 在 `--format ppt` 上下文加入 `<svg>.*<text>` 偵測。

---

## v1 dogfood 後可能補的長尾規則（future-trigger）

以下規則暫不列為 P0，待 v1 dogfood（至少 10 份實際 deck 經 `/design preset swiss` + `check.py` 走過一輪）後，視觀察到的高頻問題決定是否升格：

- **P1 候選**: `<figure>` 缺 `<figcaption>` 時 lint warning（目前僅在 image_slot 版式強制）。
- **P1 候選**: `font-size` inline 寫死（應一律走 token），目前由 `validate-output.ts` 處理，`check.py` 是否需補同步檢查待觀察。
- **P1 候選**: `color` inline 寫死非 token 值（同上）。
- **P1 候選**: `kpi-grid` 內 KPI tile 數量上限 / 下限（目前無硬性規定，可能 dogfood 後發現 < 3 或 > 6 都會破版）。
- **P1 候選**: `compare` 版式左右兩側 image_slot 焦點不一致（兩側 `object-position` 必須相同）。
- **P1 候選**: SVG `viewBox` 缺失或比例與 slot 不符（會被瀏覽器拉伸變形）。
- **P1 候選**: `<aside>` 註腳字級下限（避免縮到不可讀）。
- **觀察項**: long-form 模式下 bullets 上限是否需從 warning 升格為 P0。

future-trigger 機制：每次 `/design preset` dogfood 跑完，將 `check.py` 跳出的 warning top-5 寫進本節「觀察項」，連續 3 個 release 出現的 warning 自動評估升格 P0。
