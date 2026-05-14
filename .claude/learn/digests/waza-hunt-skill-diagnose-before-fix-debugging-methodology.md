---
topic: "Waza hunt skill：診斷優先的除錯方法論"
sources:
  - slug: "waza-hunt"
    url: "https://github.com/tw93/Waza/tree/main/skills/hunt"
created_at: "2026-05-14T03:30:00Z"
language: "zh"
phases_completed:
  - collect
  - digest
  - outline
  - fill_in
  - refine
---

# Waza hunt skill：診斷優先的除錯方法論

## 1. 核心原則：根因要一句話

Waza 的 `/hunt` skill 把整個除錯流程壓縮成一條硬性鐵律：在能用一句話寫出根因之前，不准碰程式碼。這句話的格式固定為「我相信根因是 [X]，因為 [證據]」，而且 X 必須具體到可測試的層級——指出檔案名、函式、行號或具體條件。skill 給的反例非常清晰：「狀態管理問題」這種抽象描述不是假說；但「`src/hooks/user.ts:42` 的 `useUser` 因為依賴陣列漏了 `userId` 導致 stale cache」就是假說，可以立刻寫一個失敗測試。寫不出這種具體句子，就代表還沒有假說，這時去動程式只是在症狀上貼補丁。

## 2. 診斷訊號與假說品質閘

可觀察訊號：log 對得上假說、能在執行前預測下一個錯誤、看得懂從根因到症狀的傳播路徑、能寫出在舊程式碼上失敗的測試。每個訊號出現時，再多找一個獨立證據才推進。

品質閘：在採取行動前列出所有可觀察的症狀（不只是使用者最先回報的那一個）；假說必須能解釋每一個症狀，只解釋一部分的是症狀層級的猜測。flicker、間歇性失敗、race condition 等時序問題必須先穩定重現再診斷。

合理化詞典把開發者常用的閃避語對應到行動：「我先試試這個」代表沒有假說、「我很有信心」代表跑個儀器證明它、「大概是同樣的問題」代表重新從頭讀執行路徑、「在我機器上是好的」代表列出每一個環境差異再下結論、「再重啟一次」代表逐字重讀最後一個錯誤訊息且新證據沒拿到前重啟不超過兩次。

## 3. 七條 Hard Rules

1. **同症狀復發是 hard stop**，「我先試試這個」也是——兩者都代表假說未完成。
2. **三個假說失敗後停下**，改用 Handoff 格式回報。
3. **動手前先驗證**，永遠不要憑記憶報版本號／函式名／檔案位置；先跑 `sw_vers` / `node --version` / `grep`。
4. **外部工具失敗先診斷再切換**：MCP/API 掛掉先確認 server、API key、設定，再考慮換工具。
5. **注意對方的閃避**：當有人說「那部分不重要」時把它當訊號——他迴避的區域常正是 bug 住的地方。
6. **視覺／渲染 bug 先做靜態分析**：DevTools 追 paint layer、stacking context、layer order，失敗後才加 log/overlay。
7. **修因不修症**：修正觸及超過 5 個檔案先停下確認範圍。

## 4. 四種診斷模式

### 4.1 Bisect Mode
觸發：「以前是好的」「used to work」「上一次提交還是對的」「broke after update」。流程：找 last known-good → 在 bisect 開始前定義非互動的 pass/fail 指令 → `git bisect start` → 每一步跑測試標 good/bad → 找到 culprit commit 後只讀那一個 diff → `git bisect reset`。

### 4.2 Repeated Regression / Screenshot Mode
觸發：使用者說同一問題修完還是錯，或提供「好的」截圖／版本。五步：列每一個症狀（保留原話）→ 指認 reference oracle → 動手前定義 pass/fail check → 比對 current vs reference 命名精確 delta → 同症狀仍在則停下從證據重建假說。

### 4.3 Scope Blast Mode
修完根因後、宣告 done 前。提取 pattern signature → `grep -rn` 全 repo → 對 class-of-bug 模式 grep 周圍形狀 → 逐一書面回答「這裡也是同樣的 bug 嗎？」並選 fix／leave（解釋安全理由）／unsure。常見例：視覺 bug、race、validation skip、regex/parser 四類。

### 4.4 Rendering Bug Mode
觸發：「PDF 看起來不對」「page break 問題」「字型沒 render」。靜態 CSS 分析優先：WeasyPrint 的 `rgba()` double-rectangle、`page-break-inside: avoid` 常被忽略、float 在頁面邊界壞掉、外部字型 URL 被擋。字型 `@font-face` 路徑／CORS／格式（偏好 WOFF/TTF）；頁面溢位先算 content height vs page height；瀏覽器列印 CSS 確認 `@media print` 沒被覆寫、`@page` margin 扣印表機不可印區（~6mm）、用 `window.print()` 而非預覽測試。

## 5. Confirm or Discard

加一個目標化儀器（一行 log、會失敗的 assertion、最小失敗測試）；證據反駁假說 → **完全捨棄**並重新定向，不准疊補丁。

## 6. Targeted Logging：把 log 當診斷用的刀

加 log 前先寫下它要回答的 yes/no 問題：「如果這條 log 在 Y 之前印出 X，假說 A 仍可能成立；如果沒印出，假說 A 是錯的。」

第一個 log 放在執行路徑的**中點**而非症狀處（call graph 上的 binary search）。log 只放鑑別性事實：序號／timestamp、輸入 identity key、走了哪個 branch、舊狀態→新狀態的轉換、錯誤碼加上下文字串。永遠不要 log 完整 request/response、credentials、PII、龐大 JSON。優先 log 邊界（handler 入口出口、cache hit/miss 加 key、state setter 新舊值、async callback、外部 API 結果、build step 起訖）。

prefix 紀律：`[hunt:auth]`、`[hunt:cache]`、`[hunt:render]`。debug flag 後面放 verbose；結束前移除暫時 log；留下的有用 log 走 logger level。

**加 log 改變行為這件事本身**就是 timing／lifecycle／concurrency 問題的直接證據，不要當作觀察副作用。

## 7. Durable Context Preflight

只在使用者提到記憶／先前決策／結論時跑。讀取順序：user path → 當前專案 → 全域 preference。Memory type 對應：`decision`/`preference`/`principle` = 診斷約束；`pattern`/`learning` = 假說種子；`fact` 必須對照當前狀態驗證。當前程式碼／log／重現步驟／測試／環境版本／遠端狀態**永遠優先於**記憶。對 `/hunt` 而言，durable context 只是假說燃料，永遠不替代新的根因句／可重現症狀清單／當前狀態證據。

## 8. IME / Unicode 子主題

**IME state desync**：成因為輸入法中途切換／`keydown` handler 在 composition 中消耗事件（沒檢 `event.isComposing`）／webview-native split focus。儀器：log `compositionstart`/`compositionupdate`/`compositionend` 序列。

**游標漂移**：DOM mutation during composition 會 reset selection（要在 `compositionend` flush）；位置數學要用 grapheme 而非 byte/code point（`Array.from(str).length`）。

**Emoji ZWJ 切斷**：用 `Intl.Segmenter` with `granularity: 'grapheme'`，測試 `[...'👩‍🚒'].length === 1`。

**`compositionend` / `keydown` 排序**：macOS 與 Windows 順序不同；用 `compositionstart`/`compositionend` 自設 flag 替代 `event.isComposing` 擋 Enter。

**macOS text system vs webview 衝突**：檢查 Tauri `preventDefaultFor` 是否過寬。

## 9. Gotchas

- 把 client pane 當 local pane → 動檔案前先回溯執行路徑
- MCP 不載入直接換工具 → 先查 server/API key/config
- 多階段 pipeline 中信 orchestrator 顯示 → 每階段隔離測試
- race 被診斷成 stale state → timing 問題先看 event timestamp 與 ordering
- log 滿天飛還說不清 bug → 每條 log 改寫成 yes/no 問題，刪掉不能 rule in/out 的
- 本地能重現 CI 失敗 → 先對齊環境再追程式
- Stack trace 指進 library 深處 → 往回 3 frame 走回自己的程式碼
- App 啟動正常、檔案關聯／拖拉／deep link 壞 → 用 exact entry point 重現

## 10. Outcome 格式

**Success**：
```
Root cause:        [錯在哪，file:line]
Fix:               [改了什麼，file:line]
Confirmed:         [證據／測試]
Tests:             [pass/fail、迴歸測試位置]
Regression guard:  [test file:line] 或 [none, reason]
```

三態：**resolved** / **resolved with caveats**（寫出 caveats）/ **blocked**（寫出未知）。

**迴歸守則硬性條件**：曾復發或先前已「修好」的 bug，必須有在未修版本失敗、已修版本通過的迴歸測試；測試在正式測試套件；commit message 解釋 bug 復發原因與這次修正的阻止機制。

**Handoff Format**（三個假說失敗）：Symptom / Hypotheses Tested（含測試方法與排除理由）/ Evidence Collected / Ruled Out / Unknowns / Suggested Next Steps。Status: blocked。

## 結語

核心三句話：在能寫出一句具體可測的根因之前不准動程式碼；證據反駁假說時整個捨棄不要疊補丁；修完根因之後在 grep 全 repo 確認沒有兄弟 bug 之前不准宣稱結案。其餘的模式、log 紀律、Hard Rules、Outcome 範本，都是為了讓這三句話可以在多人協作與真實時間壓力下穩定執行。
