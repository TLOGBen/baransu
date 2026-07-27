# Book 逐頁導演資訊支援計畫

狀態：規劃草案，尚未批准實作  
撰寫時間：2026-07-21 10:40:29 CST（UTC+08:00）  
撰寫者／模型：Codex（GPT-5）

## 起因判斷

現行 `/book` 無法可靠支援「重新描述場景目標、每頁內容大綱、每頁要呈現的感覺」，根因不是 `/design` 缺少視覺規格，而是 Book 的內容結構在使用者互動後才自動產生，且沒有逐頁的權威輸入契約。

1. Stage 0b 在取得來源以前執行，只問受眾、用途、風格傾向與硬限制；回答會寫入 `$INTERVIEW_BRIEF`，但只是 advisory framing，不能覆蓋內容分類。因此它既不知道實際頁面，也不能保證每頁意圖被保留。
2. Stage 2A 直接由 `$RAW_CONTENT` 擷取 4–8 個 section；Stage 2B 直接由同一來源擷取 6–12 張投影片。兩種結構都沒有場景目標、頁面大綱或呈現感覺欄位。
3. Stage 3 雖會讀取 `DESIGN.md` 與 tokens，但它的規則是依資料形狀選元件，而非依頁面感覺選擇。`/design` 提供的是全書共用視覺範圍，不是特定 book 的敘事分鏡。
4. 現有測試驗證 Stage 0 的 format、Stage 3 軟生成與 validator 分工；沒有覆蓋 Stage 0b、`$INTERVIEW_BRIEF` 或 `$STRUCTURE_SLIDES` 的互動／一對一映射。

結論：問題是缺少「結構生成後、渲染前」的逐頁確認層。把內容責任移到 `/design` 會混淆全書視覺系統與單一本書的敘事責任，不能解決根因。

## 推薦方案

在 `/book` 新增 Stage 2C「Storyboard confirmation」，位置固定在：

1. Stage 2A 已產出長文結構後；
2. Stage 2B 已產出投影片結構後（若 format 包含 PPT）；
3. Stage 3 Render 開始前。

此位置讓使用者看到的是實際將被渲染的單元，而非尚未解析的原始來源。`/design` 保留現狀，僅持續提供全書一致的 tokens、版面範圍與表現上限。

## 目標行為

- 以 `--storyboard` 作為可選互動模式；未指定時，既有直接輸入流程不變。
- `--auto` 與 `--no-interview` 保持優先；若與 `--storyboard` 同時出現，明確輸出跳過原因，不進入互動。
- Stage 2C 以一個批次確認呈現：重新描述後的場景目標，以及每個實際輸出單元的內容大綱與呈現感覺。
- HTML／PDF 以 section 為確認單元；PPT 以實際 slide 為確認單元；`--format all` 必須分別確認兩種結構。
- 確認後的逐頁資訊成為渲染依據；原始來源僅能補足段落與佐證，不能自行遺漏、改寫或推翻已確認的目標、大綱與感覺。
- 若使用者調整導致現有 section／slide 數量限制不成立，流程必須先重新整理結構並再次確認，不可靜默截斷或補寫。
- 「呈現感覺」只能在 DESIGN.md、tokens、硬性品質閘與既有格式限制內影響版面表現，不得覆蓋全書設計系統。

## 明確不做

- 不把每頁內容或分鏡規則放入 `/design`。
- 不新增跨 skill 的持久化 storyboard 工件。
- 不變更未指定 `--storyboard` 的 `/book` 行為。
- 不放寬 `--auto`、`--no-interview` 或現有品質閘。
- 不新增 runtime dependency、外部服務或新執行程序。

## 預計驗證

1. 新增 Book skill 的靜態契約測試，確認 Stage 2C 位於結構生成與 Render 之間，並覆蓋 opt-in、skip 優先序、三個逐頁欄位、格式映射及權威性規則。
2. 確認既有 Stage 0、Render 與 validator 測試仍通過。
3. 以 `make mirror` 重生 Codex 鏡像，再以 `make mirror-check` 確認無漂移。
4. 執行 `make test`。

## 參考依據

- `plugins/baransu/skills/book/SKILL.md`：Stage 0b（134–158）、結構擷取（277–288）、Stage 2B（309–313）、Render（357–376）、completion report（463–477）。
- `plugins/baransu/skills/book/references/slide-synthesis.md`：投影片來源與 schema（10–15、67–91）。
- `plugins/baransu/skills/design/SKILL.md`：設計產物與全域方向訪談（10–15、235–269）。
- `tests/skills/test-book-skill-stage0.sh`、`tests/scripts/test_book_skill_render.py`、`tests/scripts/test_book_skill_validator.py`：現有測試安全網；經搜尋，對 Stage 0b／逐頁藍圖／投影片結構的直接覆蓋為 0。

## 實作前提

此計畫尚未取得實作批准。若未來逐頁藍圖需要供多本 book 或其他 skill 重複使用，應重新評估跨 skill 工件；在目前目標下，仍以 `/book` 內部的 Stage 2C 為準。
