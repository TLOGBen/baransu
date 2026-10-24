# traps — 這個形狀會怎麼壞

## 介面太小帶來的

1. **腳本是唯一的窗口，腳本壞了所有讀者一起瞎。** Python 找不到、front matter 解析器有 bug、`git` 不在 PATH，讀者拿到的是 exit 3。讀者必須把 exit 3 當成「不知道」，不能當成「沒有假說涵蓋」——後者會讓 review 少問必答題、讓綠燈直接過。五個讀者的那一兩行都要寫明這件事；這是讀者唯一要記的例外。

2. **自動判斷輸入種類猜錯，使用者沒看第一行。** 例如 `docs/adr/0003.md` 被當成需求文件，抽出一堆「規則」。擋法只有第一行說出判斷、§2 確認規則時再露一次輸入種類。使用者不在場（被 hunt 叫起）時更容易漏看。

3. **只讀靠的是腳本沒有寫檔程式碼，但讀者手上還有編輯工具。** 一個讀者「順手」改了 README 的規則文字，腳本完全看不出來。要靠各讀者的只讀規則，以及 `/hypothesis` 下次執行時發現 front matter 與 evidence 對不上（規則文字改了、evidence 沒重跑）。

4. **介面藏太深，讀者反而繞路。** 讀者覺得腳本輸出不夠，自己去開 `area.md` 或解析 README 正文——介面就漏了，而且漏的那一份會在 README 格式改的時候壞掉。area.md 開頭寫明「讀者需要開這個檔就是腳本輸出要補」，修腳本，不修讀者。

## 過期判斷的盲點

5. **`covers` 漏了檔案。** 新檔案寫入受保護的狀態（例如新的背景工作直接改 `status` 欄位），blob 比對看不到，假說會繼續顯示成立。緩解：`covers` 可以寫目錄（目錄裡多一個檔就過期），`--maintain` 的 Drift 要搜尋每個模型變數的寫入者而不只看 diff。剩下的盲點是跨目錄的新寫入者，這是接受的邊界。

6. **文件是 URL。** `/read --save` 的 `raw/` 不可變，假說引用 raw 副本，上游網頁改了也永遠不會過期。需要在 sources.md §Document 規定：URL 來源在 README 標明「上游可能已變」，`--maintain` 時重抓一次比對。

7. **換行與 git filter。** blob hash 用 git 的預設 filter，所以 `core.autocrlf` 不同的兩台機器不會誤判；但 repo 外的文件沒有 `.gitattributes`，filter 行為取決於呼叫時的工作目錄。腳本要固定在 repo 根目錄呼叫 `git hash-object`。

8. **`sync` commit 消失。** rebase、squash 之後 commit 不在了；過期判斷不受影響（看 blob），但 `--maintain` 沒有 diff 起點，只能整份重讀，成本變高，而且容易在整份重讀時漏看「刻意改的承諾」的證據。

## 跟其他 skill 的接面

9. **hunt 還是得知道 H1–H3。** 觸發清單是唯一一段讀者要讀的規則文字。hunt 引用 `formal.md` §Triggers 錨點，錨點名稱一改 hunt 就斷——`scripts/verify-skills.py` 若有檢查交叉引用錨點的 gate，要把它納進去；沒有的話這是 review 的 single-source 題。

10. **`/prove-it` 的 description 還有 'model-check this'、'證明所有順序都不會壞'。** 兩個 skill 會搶同一句觸發。同一次變更要把這兩個觸發詞搬到 `/hypothesis`，prove-it 留「真的修好了嗎」這類跑一次的觸發。

11. **hunt 在非互動模式（/loop）下叫 `/hypothesis`。** 這個 skill 是 `loop=not-drivable`，規則要人確認。hunt 在 loop 裡碰到 H1–H3 不能叫它，只能在交接（Handoff）裡寫「需要 /hypothesis，需要人在場」，否則會卡在一個沒有人回答的 Input PAUSE。

12. **Codex 鏡像找不到腳本。** 讀者的路徑寫成 `$CLAUDE_SKILL_DIR/../hypothesis/scripts/hypothesis.py`，`$CLAUDE_SKILL_DIR` 是 Claude Code 才有的變數。hunt 已經有同樣的問題，鏡像要用 hunt 現成的解法；這個形狀不能比 hunt 多依賴任何東西。

13. **舊位置與新位置同時存在、內容不同。** 搬遷中途停下，或使用者手動複製了一份。腳本兩份都列（一份 `舊位置`、一份正常），prove-it 可能兩份都跑。規則：同名時新位置優先，舊的一律只顯示 `舊位置`、不跑。

## 執行環境

14. **TLC 找不到。** 檢查行不能寫死 `D:\Workspace\00_Env\tla\tla2tools.jar` 這種本機路徑（README 會被 commit 到別人的機器）。轉接頭讀 `TLA2TOOLS_JAR`，沒設就 exit 3 並印「找不到 TLC：請設定 TLA2TOOLS_JAR」；讀者照第 1 條當「不知道」處理。

15. **evidence 被 commit 進 git。** area 是保留產物，跟分支一起 commit。TLC 的完整狀態傾印、`states/` 目錄可能很大。evidence 只存摘錄（違反的那條路徑、狀態數、版本），暫存目錄放系統暫存區。

16. **CDN 被竄改或離線。** 圖頁從 jsDelivr 載 Mermaid，版本與 SRI hash 都釘死在 page.md；離線時靠每張圖下面的文字版。SRI hash 寫錯會讓整頁圖都不顯示，要在 page.md 釘一次、試行時看過一次。

## 嚴格度被悄悄放鬆

17. **「無法寫成」變成逃生門。** 因為 `cannot` 不擋綠燈（tradeoffs 第 10 條），模型可能把難寫的模組都標成無法建模。擋法是原因紀錄的四欄必須具體（缺哪個工具、哪個外部依賴、試過什麼範圍跑了多久），以及「何時可形式化」那一欄讓下次觸發時重新評估。試行時要量 `cannot` 的比例——這同時是計畫前提一的量測。

18. **`check` 只比對規則狀態，不重做「看過它失敗」。** 讀者重跑得到的成立，是「模型在同一份來源上仍然成立」，不是「模型仍然抓得到錯」。這只在來源沒變時成立；來源一變就過期，回到 `/hypothesis` 重做 §4。所以 `check` 絕不能在過期的 area 上跑出結果——腳本在過期時不重跑，就是為了這條。
