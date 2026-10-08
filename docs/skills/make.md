# 創作家族：draw · ui · write

<img src="../images/family-make.png" width="320" alt="創作家族概念圖">

> 每個選擇都有理由：先出計畫，再動手，做完自己看過、評過再交。

`/draw` 畫說明用的圖與動畫、`/ui` 改你 app 自己的介面、`/write` 處理文字。

[← 回文件索引](../README.md)

---

## `/draw`

Claude Code：`/baransu:draw`　Codex：`$baransu:draw`

**用途**　把任何東西畫出來：編輯級靜態圖（44 型）、可點可探索的互動圖、程式渲染的動態影片、或一頁可拖時間軸的動畫說明頁；全部自包含，先出計畫、再做、再自己看圖打分修到 8 分。

**什麼時候用**
- 想把點子、系統、流程、資料或故事視覺化、畫成圖、做成動畫、分鏡、reel、發表影片、架構圖、流程圖、時序圖、時間軸、圖表或說明頁。
- 觸發語：`/draw`、畫一下、畫成圖、圖解、做成動畫、做支影片、架構圖、流程圖、時序圖、說明頁、draw this、visualize、make a diagram、animate it、motion graphics；或貼上 Mermaid／draw.io／Excalidraw 要重畫。
- 參數：`<要畫什麼 | 檔案 | repo 目錄 | 貼上的文字> [--lane diagram|map|motion|page] [--format 9:16|1:1|16:9] [--dark]`

**四條 lane**

| Lane | 產出 | 機械檢查 |
|---|---|---|
| diagram | 編輯級靜態圖，44 型，HTML ＋ inline SVG；可加 seek overlay 讓圖隨時間動 | `self_check.py` |
| map | 可探索互動圖：architecture／workflow／sequence／data flow／lifecycle 五型 | `archify finalize` 收據 |
| motion | 程式渲染影片：`seek(t)` → MP4／WebM，彈簧、節拍網格、合成音效；一條 timeline 可輸出 9:16／1:1／16:9 | `render.mjs hash` ＋ 每個格式的 contact sheet |
| page | 一頁說明頁，內含可拖時間軸的動畫圖 | `verify-page.mjs` |

**共同骨幹**　一則訊息講清計畫（lane、類型、尺寸、預算砍掉什麼）→ 建 → 自己看（contact sheet／截圖／收據）→ 計分卡每列 ≥ 8 或跑滿三輪 → 交付。

**產出**　`.claude/draw/<slug>/`：`index.html`（diagram、map、page）或 `out/final.mp4` 與原始碼（motion）、`docs/review_log.md`、擷圖；影片另有 `docs/brief.md`。完成報告列出檔案、lane、跑過的檢查與分數。

**自包含**　不連網找內容、不依賴其他 skill 安裝；但使用者指定的品牌來源（網址、token、資料夾、`/ui` 的 `reference-<slug>.md`）可以讀一次存成 profile。

**不適用**
- 改你 app 的 UI → `/ui`（要嵌進站內的圖，先 `export_svg.py` 再交 `/ui`）
- 抓網頁成 Markdown → `/read`
- 整理成筆記 → `/learn`
- 接即時資料的數字儀表板

**第三方來源**　diagram、map、手繪動畫等子模組 vendored 自 MIT 授權專案，清單見 `plugins/baransu/skills/draw/NOTICE.md`。

**非互動驅動**　`loop=assisted`（全片渲染是 Authorization PAUSE）。

---

## `/ui`

Claude Code：`/baransu:ui`　Codex：`$baransu:ui`

**用途**　你 repo 裡的 UI 設計主導：定調色／字／版／動效後直接寫改 UI 檔；能從參考網站、截圖、藝術流派抽出設計語言，也能拿既有 UI 對照參考修整。

**什麼時候用**
- 想讓頁面或元件更好看、不那麼制式、更有設計感，或照某個東西的風格做。
- 觸發語：`/ui`、設計 UI、美化、調 UI、加樣式、介面設計、照這個網站的風格、看起來太 AI／太模板／太陽春、make it look designed、add some styling、styling、frontend design。
- 參數：`<brief | 既有 UI 的路徑 | 要學的網址或圖片>`

**運作方式**　改任何檔案前，先在對話中提出設計計畫（色彩、字體角色、版面概念、原則）→ 對照 brief 檢查 → 建 → 自我批評。給了參考時，先把設計語言整理到 `.claude/design/reference-<slug>.md` 再套用。

**產出**　使用者專案裡的 UI 原始碼；選用的 `.claude/design/reference-<slug>.md`；收尾訊息逐檔列出改了什麼（環境能截圖時附截圖）。

**不適用**
- Claude Design 畫布 mockup → 內建 `design` skill
- 說明性圖表與動畫 → `/draw`
- 小寫 `design.md` 技術架構文件不歸這裡管

**非互動驅動**　`loop=not-drivable`。

---

## `/write`

Claude Code：`/baransu:write`　Codex：`$baransu:write`

**用途**　雙語寫作／潤色：套排版與風格規則，輸出 Before/After 與每處改動理由。

**什麼時候用**
- 中英文寫作協助：潤稿、生成、校對。
- 觸發語：`/write`、潤稿、寫一篇、改寫這段、校對、找錯字、抓錯字、proofread。
- 參數：`[zh|en] [voice="…"] <文字=潤稿 | prompt=生成 | 檔案路徑=校對>`

**三種模式**（自動分類；語言跟前綴，沒給就自動偵測）

| 模式 | 產出 |
|---|---|
| Refine 潤稿 | Before／After ＋逐條規則標記的修正說明 |
| Generate 生成 | 新文章＋格式／語氣說明 |
| Proofread 校對 | 自帶樣式的 `錯字修改.html`，六欄錯誤表；錯誤類型固定三種：錯別字／用語不妥／語句不通順 |

**底線規則**　中文禁對仗句、禁排比、禁名詞化；英文另禁 em dash。

**不適用**
- 寫完要 commit／push 的收尾 → `/ship`
- 把來源消化成筆記 → `/learn`、`/read`

**非互動驅動**　`loop=drivable`。
