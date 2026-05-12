---
topic: "HTML-native 簡報/設計 skill 結構參考"
sources:
  - slug: "guizang-ppt-skill"
    url: "https://github.com/op7418/guizang-ppt-skill"
  - slug: "huashu-design"
    url: "https://github.com/alchaincyf/huashu-design"
  - slug: "book-skill"
    url: "local:/home/vakarve/.claude/plugins/cache/baransu/baransu/1.1.21/skills/book/SKILL.md"
created_at: "2026-05-12T14:27:32+08:00"
language: "zh"
phases_completed:
  - collect
  - digest
  - outline
  - fill_in
  - refine
notes: "Stage 5 Refine skipped intentionally — technical density (class names, file paths, hex tokens, layout ids) preserved verbatim; run /write zh separately if prose polish needed."
---

# HTML-native 簡報/設計 skill 結構參考

對照三份 skill（op7418/guizang-ppt-skill、alchaincyf/huashu-design、baransu/book）拆解視覺品質背後的結構約束，回頭看 `/book` 的 PPT 產出可以從哪裡借力。

## 1. Skill 檔案組織策略

三份 skill 都收斂在同一個拆分模式：`SKILL.md` 只放決策路由與工作流，深度規則拆檔到 `references/`，工具腳本另外擺到 `scripts/`。

`guizang-ppt-skill` 的 SKILL.md 像玄關，七問澄清 + 風格 A/B 路由 + 圖片約定，本體不到 500 行；它把版式骨架（layouts.md/layouts-swiss.md，總計 ≈ 1500 行）、主題色預設（themes.md/themes-swiss.md）、配圖提示詞（image-prompts.md）、生成後質檢（checklist.md）、版式鎖定（swiss-layout-lock.md）、組件目錄（components.md）拆成八個 references 檔案，再加一支 `scripts/validate-swiss-deck.mjs` 機器校驗。`huashu-design` 採同樣骨架：`SKILL.md` + `assets/{animations.jsx, ios_frame.jsx, deck_stage.js, design_canvas.jsx, ...}`（starter components）+ `references/{animation-pitfalls, design-styles, slide-decks, editable-pptx, critique-guide, video-export}` + `scripts/{render-video.js, html2pptx.js, export_deck_pdf.mjs, export_deck_pptx.mjs, verify.py}`。

`/book` 自己也是這種拆法：`SKILL.md` + `references/{perception-guide.md, design-token-resolver.md, golden-template.html, slide-template.html, diagram-types/}` + `scripts/{install-deps.ts, html2pptx.js, validate-output.ts, verify-render.py}`。但對比 guizang 把 PPT 版式拆成獨立的 layouts-swiss.md + swiss-layout-lock.md + themes-swiss.md，`/book` 對於 PPT 場景只有單一個 `slide-template.html` + SKILL.md §6 寫了五個版型（cover/section/content/data/closing），份量明顯偏輕。

## 2. 視覺風格的「鎖定」策略

guizang 提供兩種完全切分的視覺世界：「電子雜誌風 A」（Noto Serif SC + Playfair Display + WebGL 流體背景 + 暖色）與「瑞士國際主義 B」（Inter + Helvetica + 網格點陣 + 單一高飽和 accent IKB/檸檬黃/檸檬綠/安全橙）。兩種風格不混用，七問澄清的第一題就是「A 還是 B」，決定後續所有檔案怎麼挑。

Swiss 風格的硬規則是「高級灰白底 + 單一高飽和高亮色」— 不允許混搭多個 accent。實作層面把 `--paper / --paper-rgb / --ink / --ink-rgb / --grey-1 / --grey-2 / --grey-3 / --accent / --accent-rgb / --accent-on` 全部走 CSS variables，換主題時整套替換 `:root{}` 區塊；其他 CSS 都 `var(--...)`，零額外改動。

huashu-design 的 Anti AI-slop 規則從反向定義「不要做什麼」：禁用 purple gradients、emoji icons、rounded-corner + 左邊框 accent、SVG humans、Inter-as-display、CSS silhouettes 代替真實產品圖。建議改用 `oklch` 色彩空間 + serif display 字體 + `text-wrap: pretty` + CSS Grid。

`/book` 走 Kami 設計系統，token 統一在 `design/references/paper-preset.md`，CSS class 都必須來自 `golden-template.html` — 規定不發明新 class，違反就拿 `<p>` 兜底。風格鎖定的方向跟 guizang Swiss 一致，但只提供一種視覺基調，沒有為 PPT 場景做差異化。

## 3. 版式登記制 + 機器驗證（最該借鑒的部分）

guizang Swiss 模式登記了 22 個版式 S01–S22，每個 `<section class="slide">` 強制標 `data-layout="Sxx"`。版式表細到「必須保留的骨架 / 圖片規則 / 圖片比例」— 例如 S22 Image Hero 規定主圖按 21:9 生成、關鍵主體放中央 70% 安全區、photo 的 `object-position` 不可 `top center`（人像/會議場景會被裁掉臉），而是 `center 35%`；S15/S16 多圖網格規定同組必同高同寬同容器背景，`.fit-contain` 只用於必須保留原始比例的截圖。

`scripts/validate-swiss-deck.mjs` 把上述規則寫成機器可執行的校驗：攔截未登記版式、缺少 `data-layout`、P23/P24 實驗結構、SVG 內可見文字、S22 hero 未綁 class、object-position 違規。生成完後一定要跑這支 script，校驗失敗就回去改 HTML。

「Golden Source」概念也值得注意：swiss-layout-lock.md 直接指向作者本機的原始 PPT 路徑 `/Users/guohao/Documents/op7418的仓库/项目/Thin-Harness-Fat-Skills/ppt/index.html`，22 個版式都是從這份原始檔反推出來，新增版式必須回到原始檔對骨架，不允許在 LLM 端發明。

huashu-design README 提到生成後跑 Playwright click test，但 README 沒揭露 validator 的內部規則，無法直接學。

`/book` 的 PPT pipeline 對應檢查只有三條：`<body>` width 含 `960`、文件包含至少一個 `.slide`、不含 `background-image`（SKILL.md §6 步驟二）。沒有版式登記、沒有 `data-layout="Sxx"` 強制標、沒有比例驗證、沒有 SVG 文字禁用、沒有圖片 `object-position` 檢查。同一支 `scripts/validate-output.ts` 主要為長文 HTML 設計（檢查 `.paper` / `h1` / `h2` / SVG 計數），PPT 場景幾乎無實質規則拘束。

## 4. 配圖規格化（PPT 醜的最大來源）

guizang 把配圖視為比版式更敏感的議題，定下「先選槽位再生成圖片」的原則：頁面布局決定圖片落位，落位決定比例（16:9 / 16:10 / 4:3 / 21:9 / 3:2 / 3:4 等），比例再寫進生成提示詞作為硬約束。例如 S22 Hero Strip 的提示詞必須包含 `21:9 ultra-wide strip`, `subject centered in the safe middle area`，加上一段固定的負面指令 `no title, no footer, no page chrome, no logo, no border` 防止生成圖自帶 slide chrome。

每張配圖最後都會補一段規格約束尾巴：「輸出必須是 [16:9/16:10/4:3/3:2] 橫向構圖，主體居中但保留邊距，畫面密度中等，與同組圖片保持相同視覺縮放和邊距。只保留核心圖形/畫面本身，不要生成頁眉、頁腳、標題、頁碼、角標、署名、裝飾邊框、超長條、豎圖或不規則比例。」一組多圖再加一句「這是一組圖片中的一張，請保持與同組相同的畫面比例、元素大小、邊距、線條粗細和標注密度」。

對原始截圖的處理也有規定：原圖比例接近目標槽位就用 `cover`/`fit-contain`；過高過窄就重生成「截圖再設計」到目標比例；UI 圖被拉成巨長條就拆 2-3 個同高面板。

huashu-design 的 Core Asset Protocol 處理「品牌資產」場景：五步驟強制 ask → search → download → verify → freeze 到 `brand-spec.md`，原則是「never guess from memory」。logo 三段 fallback（SVG → inline-SVG → social avatar）、產品圖三段 fallback（hero → press kit → launch video frames → AI generated from reference）、UI 兩段 fallback（App Store 截圖 → 官方影片定格）。作者揭露 A/B 測試結果：v2 的這套協議讓六個 agent 的穩定性方差降 5×。

`/book` PPT pipeline 對配圖完全沒著墨。SKILL.md §6 步驟一只說「若 `has_svg` 為 true，插入對應的 inline SVG」，沒有像素規格、沒有 viewBox 約束、沒有對外部圖片的處理流程。長文 SVG 那一側倒是非常細（14 型決策樹、`<defs>` 必備片段、座標 4 倍數、節點寬 12 檔白名單、字體大小依嵌入 scale ≈ 0.47 校正），但這些規格是為 A4 嵌入 PDF 設計，不是為 16:9 投影片設計，PPT 場景目前沒有對等規範。

## 5. 工作流節制（防止暴衝）

guizang 的 Step 1「7 問澄清」是動手前的硬閘門：風格 A/B、受眾與場景、分享時長、原始素材、圖片、主題色、硬約束，必須對齊才能進 Step 2。並且做了環境感知 — Codex 環境改用普通對話，Claude Code 環境用 AskUserQuestion。如果用戶沒有大綱，給一份「敘事弧模板」搭骨架：Hook（1 頁拋反差/問題）→ Context（1-2 頁背景）→ Core（3-5 頁主體）→ Shift（1 頁轉折）→ Takeaway（1-2 頁收束），並提供頁數規劃公式（15 分鐘 ≈ 10 頁，30 分鐘 ≈ 20 頁）。

huashu-design 的 Junior Designer Workflow 是同一精神的不同表達：禁止一次到位的英雄式嘗試；先 assumption + placeholder + reasoning 寫進 HTML → 早期讓用戶看（即使是灰塊）→ 填真內容 → 變體 → tweaks，每個階段都給用戶看。原則是「Fixing a misunderstanding early is 100× cheaper than fixing it late」。另外 Principle #0 Fact Verification First：提到具體產品/技術名稱時必先 `WebSearch` 驗證版本與規格，不靠訓練語料記憶，「一次搜尋 10 秒，假設錯誤要重做 1–2 小時」。

`/book` 在 Stage 1 §4 允許「plain text / bare topic」直接進 Synthesize，沒有七問澄清；Stage 2A 直接從 `$RAW_CONTENT` 抽 4–8 sections，沒有對齊用戶意圖的中斷點。從觸發到 Render 之間沒有 user-in-the-loop 的 checkpoint。

## 6. P0 質檢清單（生成後自檢）

guizang 的 `checklist.md` 是從真實迭代踩過的坑總結出來的，按重要性排序：P0 是「一定不能犯的錯」，內容像 0-S（Swiss locked mode：正文頁必須來自原始 22P）、0-S-2（Swiss 頂部標題默認左上，不是居中）、0-A（瑞士風畫布對齊法則 — `.canvas-card` 已自帶 `padding:5.6vh 5vw 4.4vh`，主體區別再寫 `padding:5vh 5vw 4vh` 就會內縮重複 5vw）。這種具體 CSS 陷阱比抽象規則有用得多 — 一條條都是某次真實 bug 的標本。

huashu-design 的 5 維評審覆蓋創作後評估：philosophical coherence（哲學一致性）/ visual hierarchy（視覺層次）/ execution craft（執行精度）/ functionality（功能性）/ innovation（創新），每維 0–10，輸出 radar chart 與 Keep/Fix/Quick Wins 清單。

`/book` 的 Stage 4 §1 用 `scripts/validate-output.ts` 做機器閘門，§2 用 Playwright 做視覺驗證（檢查 `overflow / has_paper / has_h1 / has_h2 / svg_count`）。檢查項偏向「結構元素是否存在」，沒有 P0 級別的「禁止清單」（例如禁止 `text-align:center` 在大標題、禁止 SVG `<text>` 作為可見標籤、禁止圖片容器灰底包白底信息圖），也沒有將過去踩過的坑沉澱成 checklist。

## 7. 對 /book PPT 的改善切入點

對照三方差異，`/book` 的 PPT 不好看的成因可以拆成四個結構性缺口，每個都對應一個可以從 guizang 抄過來的補丁。

**第一個缺口是版式不足且未鎖定**。`/book` SKILL.md §6 只定義五個版型（cover/section/content/data/closing），缺乏「多圖網格」、「KPI 塔/矩陣」、「Hero Strip + 三 KPI」、「Duo Compare」、「敘述 + 條形圖」這類資訊密度版式 — 而這些正是 guizang Swiss 的 S04/S06/S15/S16/S18–S22。建議把 `references/slide-template.html` 擴成有十幾個 layout 的 catalog，每個都給命名（如 `book-S01..book-S12`），並在生成時強制每個 slide 寫 `data-layout="<id>"`；對應在 `scripts/validate-output.ts` 加 PPT 模式校驗，攔截未登記 layout。

**第二個缺口是視覺風格只有一種**。Kami 的紙感長文設計適合長文 HTML，但搬到 16:9 投影片就顯得保守。借 guizang 雙風格的做法，PPT 場景可以額外提供「Swiss / Magazine / Kami」三選一，整套 token 走 `var(--paper) / var(--ink) / var(--accent)`，在 Stage 1 多問一題「PPT 視覺基調」做開機選擇。

**第三個缺口是配圖規格化幾乎為零**。SKILL.md §6 步驟一只說「若 `has_svg` 為 true，插入對應的 inline SVG」，沒有對應 guizang 的「先選槽位再生成圖片」原則。建議新增 `references/slide-image-prompts.md`，定義 PPT 場景每個版型對應的圖片比例（21:9 / 16:9 / 16:10 / 3:2）、提示詞模板（含 `no title, no footer, no page chrome` 負面指令）、`object-position` 規則（人物場景 `center 35%`、抽象構圖 `center center`、絕不 `top center`）。

**第四個缺口是缺少 P0 checklist**。`validate-output.ts` 目前只查「元素是否存在」，沒有像 guizang `checklist.md` 那樣的禁止清單。建議在 `references/` 下開一份 `slide-checklist.md`，沉澱每次 PPT 醜的具體 root cause（標題置中、SVG 內含文字、多圖混高、配圖自帶 chrome 等）；每次手動發現問題就回灌成一條 P0，逐步把抽象的「醜」轉成可機器校驗的具體規則。

優先順序建議：版式登記制（含 validator）→ 配圖規格化 → P0 checklist → 雙風格切換。前兩項是結構性硬約束，做完馬上能看到輸出品質提升；後兩項是抓長尾與差異化，可以分批迭代。
