---
topic: "Kami 的 3D 圖與 PDF 機制：Evidence layout、Architecture redraw、Concept tradeoff"
sources:
  - slug: "kami"
    url: "https://github.com/tw93/Kami"
created_at: "2026-05-11T04:00:00Z"
language: "zh"
phases_completed:
  - collect
  - digest
  - outline
  - fill_in
  - refine
---

### 一、核心定位：設計系統 ≠ 渲染引擎

Kami 的本質是一套「印刷物件的約束語言」，而非任何形式的 3D 渲染引擎或圖形框架。它的口號 *Good content deserves good paper* 精確描述了它的角色分工：Kami 只負責制定規格（字體、色彩、間距、圖表語彙），實際的渲染工作——無論是 WeasyPrint 生成 PDF，還是 ChatGPT Images 生成插圖——都由外部工具承接。

README 的 Travel 章節明確說明：三張旅行插圖（Evidence layout、Architecture redraw、Concept tradeoff）「Rendered by ChatGPT Images 2.0 in a single pass with no manual touch-up」。這句話直接給出了答案：圖是 AI 圖像生成工具畫的，代碼沒有參與；Kami 在其中的角色是設計 brief 的提供者。

### 二、PDF 生成技術棧

PDF 輸出的主路徑是：HTML 模板 → WeasyPrint → PDF。Kami 為 8 種文件類型各提供獨立的 EN/CN HTML 模板（One-Pager、Long Doc、Letter、Portfolio、Resume、Slides、Equity Report、Changelog）。其中幻燈片的預設路徑是 slides-weasy.html（中文）或 slides-weasy-en.html（英文）；只有在用戶明確要求可編輯 PPTX 時，才走 Python 腳本（slides.py / slides-en.py）生成 PPTX。

WeasyPrint 本身有兩個已知 bug 需要繞開，Kami 的設計規範都圍繞著這兩點做了對應約束：

1. `rgba()` 觸發 double-rectangle bug：WeasyPrint 在渲染帶有半透明填色的標籤時會出現多餘矩形。Kami 的解法是所有填色一律使用 solid hex——原本的 `rgba(20,20,19,0.08)` 就被預先混算成 `#EAE9E2` 寫死在 token 裡。
2. `<marker orient="auto">` 不支援：WeasyPrint 的 SVG 渲染層對 `marker` 元素的方向支援有限，所有箭頭如果用 `marker` 標記都會固定朝右。Kami 的解法是完全放棄 `marker`，改用手工繪製的 chevron `<path>`，每個箭頭的方向都直接硬編碼在路徑座標裡。

語言切換邏輯也整合在技術棧內：中文走 `*.html` 模板配 TsangerJinKai02 字體；英文走 `*-en.html` 配 Charter；日文走最佳努力 CJK 路徑，出貨前進行視覺 QA。

### 三、行內 SVG 圖表系統（14 種）

Kami 的圖表不依賴任何 JavaScript 圖表庫或 Mermaid 這類 DSL，每一種圖表都是自包含的 HTML 檔 + inline SVG，可以直接在瀏覽器開啟預覽，也可以把 `<svg>` 塊複製到 `<figure>` 標籤裡嵌入長文或作品集，無需額外 build step。

14 種圖表類型覆蓋了結構性（Architecture、Flowchart、Swimlane、Tree、Layer Stack）、資料性（Bar、Line、Donut、Candlestick、Waterfall）、關係性（Quadrant、Venn）與時序性（State Machine、Timeline）四大場景。

設計規範刻意設置了幾個「防 AI slop」的硬約束，讓圖表維持手工製圖的精度：所有座標、寬度、間距必須是 4 的倍數；節點寬度只允許 128 / 144 / 160 三個層級；焦點節點（ink-blue `#1B365D` 描邊）最多 1-2 個；箭頭一律使用開口 chevron 而非填色三角形。嵌入長文時，字體尺寸還需要從 standalone 的 `7/9/12` 放大到 `14-24` 範圍，因為嵌入後渲染寬度只剩約 470pt，若不調整文字會過小。

### 四、三張旅行插圖的實際機制

**Evidence layout**（Tesla Optimus 手部和前臂專利圖，中文）：這張圖的任務是把多張專利原圖用 Kami 設計語言重新排版成 Evidence 版式——暖羊皮紙底、ink-blue 標注、細 serif 說明文字。它展示的是「如何把外部圖像資料整理成可讀的證據頁面」，立體感來自 ChatGPT Images 2.0 對設計 brief 的解讀，不是 SVG 或代碼渲染。

**Architecture redraw**（SpatialVLA Figure 1，英文）：這張是把 SpatialVLA 論文的原始架構圖重繪成 Kami 的 schematic 風格。從技術上看，這個任務理論上可以用 Kami 的 `architecture.html` SVG 模板手工填入，但 Travel 章節展示的版本選擇了交給 ChatGPT Images 2.0 一次性生成——輸入是 Kami 的 references 資料夾作為設計 brief，加上原圖或圖的描述。

**Concept tradeoff**（3D 表示的算力-推理性取捨，中文）：這裡的「3D」是研究主題（3D representation methods，如 NeRF、3DGS 等），不是指圖形渲染技術本身是三維的。這張圖展示的是不同 3D 表示法在算力消耗與推理性能之間的取捨關係——是一張概念性 tradeoff 圖，同樣由 ChatGPT Images 2.0 依據 Kami 設計 brief 生成。

### 五、「設計系統作為 prompt brief」的工作流

三張插圖共享同一套工作流。核心 prompt 模式是把 `references` 資料夾（含 design.md、diagrams.md、tokens.json 等設計規格文件）作為上下文傳給繪圖 AI，後者就能「繼承」Kami 的暖羊皮紙色調、ink-blue 克制、單線幾何圖標、editorial typography。Kami 負責規格，AI 負責渲染，整個流程無需手工後製。

README 明確點名的工具是 ChatGPT Images 2.0。其他圖像生成工具（Midjourney 等）理論上也可接受文字 brief，但兼容性屬於推論，未有原始資料支撐。
