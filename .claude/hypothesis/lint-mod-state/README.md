# 假說：lint mod 的跨事件狀態，在任何事件順序下都照它的承諾提醒

- **使用者要拿它做什麼**：決定 lint mod 能不能直接 ship、信任它的「重新」「刪除前預覽」「收尾紀錄」，不必在每個 session 裡盯著它有沒有漏報或亂報。
- **理想**：主迴圈該被提醒的事，每一件都恰好提醒一次；不該提醒的（subagent 的動作、已經交代過的一輪、`/clear` 之前的對話）一次都不提醒；刪除只在模型看過預覽之後才執行；任何事件順序下都一樣。
- **已證明**（往上推）：現在的程式（模型的 `Fix=TRUE, Now=TRUE`，8.43 的時機版）在範圍內守住全部 19 條規則（R1–R17、R19、R21；R18、R20 見〈還開著的列〉）。範圍是 MaxSteps 7、2 段寫錯語言的文字、2 個刪除指令、2 個同時進行的主迴圈呼叫、2 個目錄，每條 1,188,960 個狀態。0917b911（`Now=FALSE`）在同一範圍打破 R1、R4–R8、R11；第一版（`Fix=FALSE`）打破 R3 以外全部。8.43 時機版的初版打破 R4、R5（P18、P19），兩處都已修好。依據：TLC `check.py --quick` 55/55，見界與證據。
- **最好可能**（往下壓）：理想本身——現在的模型達到了。
- **差距**：在範圍內「相遇」；範圍外（更多步、更多同時呼叫）只靠論證，見界與證據。
- **主張與量詞**：在所有事件順序下（prompt.submit 的各種訊息、turn.start、turn.step、session.append、主迴圈與 subagent 的 tool.call、turn.complete、skill.prompt、mod 重新載入、`/clear` 任意交錯）
- **規則確認**：R1–R10 已確認（使用者 2026-11-02；讀法 D1 選 B、D2 選 A）。R11 **未經確認**：它把 R6 收緊成「看過預覽才放行」，來自 0917b911 的 review（使用者要求全部修好），沒有另外請使用者確認這條文字。 R4、R5 的 8.43 改寫，以及 R19、R21，已確認（使用者 2026-11-04）。
- **涵蓋的對象**：`plugins/baransu/hooks/engine/engine.ts` 的狀態（`Memory`：`ready` 載入、`take`／`giveBack`、`save`）與讀寫它的方法：`promptSubmit`、`turnStarted`、`stepBegan`／`textStreamed`、`replyAppended`、`cleared`、`toolCall`、`turnCompleted`、`skillPrompt`、`cardFor`，8.43 起加上 `stopping`（`classic.Stop`）與 `enqueue`／`queued`；平台事件到這些方法的翻譯 `hooks/adapters/claude-code/hooks.ts`、`translate.ts`；存取 `$.state` 的 `ports.ts`（`hostState`）；`hooks/main.ts` 註冊的 `turn.step`；型別 `plugins/baransu/types/index.d.ts`。模型的每個動作原本對應 lint.ts 的一個 hook，現在對應一個引擎方法（一對一，見 Q6）。8.43 新增、但模型沒有描述的入口：`agentStarted`／`agentStopped`（spans）、`compacting`、`fileChanged`、`bump`／`rearm`／`wake`（timers），R18、R20 只靠論證
- **描述的版本**：8.44.0 合集版面（engine.ts sha256 `124de9ee6cc5…`）
- **定稿雜湊（8.44.0）**：LintRules.tla `0efaf38df2b2…`、LintMod.tla `74501647702a…`、check.py `a66c593a3261…`（三個都沒變）、engine.ts `124de9ee6cc5…`、timing.ts `ea961ab7e008…`、hooks.ts `1747353b9c73…`、translate.ts `cc2ca5999cfe…`、ports.ts `c07639f6d396…`、types/index.d.ts `26c1ac14ec06…`
- **維護紀錄（8.44.0 合集版面，2026-11-04，`--maintain`）**：
  - 分類：`LintState` 多了兩個欄位，都分類為「沒有影響」。它們不是要交付給模型的東西，模型描述的狀態和規則都沒變。
    - `objects`：暫存 git 的路徑，只是讓重新載入找得到它。`/clear` 時保留。
    - `lintTurn`：`/lint` 這一輪的旗標。它只決定規則要不要重讀，在這一輪結束時清掉。
  - 其他改動也都是「沒有影響」，因為不寫跨事件狀態：
    - 規則讀一次後放在記憶體，`/lint` 時重讀。
    - around 改存在暫存 git，`Runner.write` 拿掉了。
  - 重跑：`--quick` 55/55 符合預期（1404 秒），每條 1,188,960 個狀態。模型沒改，所以這次是確認舊結果還成立；程式的改動用 282 個測試把關。
  - 結果：updated（版本、雜湊），in step。
- **維護紀錄（8.43.0 時機版，2026-11-03，`--maintain`）**：
  - 分類：`report-before-stop` 從 `turn.complete` 移到 `pre:stop`，`pendingReport` 被拿掉 →「不再描述」，模型新增 `Stop(err, line)`；放行時把這一輪結束合併進同一步，被打斷的一輪仍然走 `TurnComplete(FALSE)`。新的狀態 `queued` 在 `MainBegin`／`UserPrompt` 被拿走，出錯時還回去；`held` 只是 `previewed` 改名，意思沒變。`spans`、`timers`、`touched` 沒有建模，靠論證（同步拿走並存檔，這種做法 R1、R2 已經驗證過）。
  - 規則：R4、R5 改寫（見規則表）；新增 R19（一輪最多被擋 4 次）、R21（排隊的話只送一次，最晚在使用者下一則訊息前送到）。
  - TLC 找到兩個程式錯誤，都修好了，各有紅綠測試：
    - P18（R4）：這一輪先被別的 error 擋過，host 的 `stop_hook_active` 就用掉了，之後做了事沒交代也不會再被要求。改成每條檢查各自記一次（`held` 的 `stop|<id>`）。
    - P19（R5）：已經要求過交代，之後每次被 error 擋又要求一次。改成擋過的檢查只畫在卡片上。
  - 重跑：`--quick` 55/55 符合預期（1379 秒）。新規則、舊版本、所有植入的 bug 都照預期。
  - 之後第二次 review 的修正（post 時機的結果在指令失敗時也送給模型、計時器的鍵加上時機、commit／push 只看真正的 git 段落、壓縮帶走的「重新」記成已送達、`explain-before-edit` 的 error 每次都擋）：模型描述的狀態都沒變（壓縮、計時器不在模型裡；error 等級的「先說明」不是預設），分類為「沒有影響」，只更新雜湊。
  - 結果：updated，in step。
- **維護紀錄（8.43.0，2026-11-03，`--maintain`）**：
  - 先照原樣跑：模型改動前的整份清單 51/51 符合預期。
  - 逐條分類 8.40.0 之後的改動：8.41.0（skill 前檢查、push refspec、「說過話」）、8.42.0（`/lint help`／`show`）都是「沒有影響」，不寫跨事件狀態；8.43.0 的 `answering`、`answerSeq`、`answerCard` 中，`answerCard` 是顯示用、不受規則判斷（「沒有影響」），`answering` 是「不再描述」，模型改了兩處：
    1. 「先說明」的「重新」只有在工具沒出錯時才算送達（程式在出錯時不把說明交給模型）；模型原本無條件送達。
    2. 程式用清單記每一次送達；模型原本只記一個步數，新送達會蓋掉舊的（review 驗證者排除 (a) 找到的落差）。模型改成步數的集合，R15 由「計數不超過 1」改成「同一次送達不被檢查兩次」（`dupG`）。
  - 重跑：51/51 符合預期（856 秒），R1–R17 在現在的版本守住，每條 786,402 個狀態；天真取法、R14／R15／R17 的植入 bug、`vis`、`queued` 都被抓到。
  - 結果：updated，in step。
- **舊的定稿雜湊（8.40.0）**：LintRules.tla `72f43553d653…`、LintMod.tla `922ce7d1532a…`（8.40 只改了開頭與變數的註解，指向新的 engine.ts；動作不變）、check.py `5c9b84c65f46…`、engine.ts `adea58e89a1e…`、hooks.ts `0d3adf75de9d…`、translate.ts `b290e67c935e…`、ports.ts `6822c45ff5cf…`、main.ts `d083274f294d…`、types/index.d.ts `52df08ef23e5…`
- **維護紀錄**：2026-11-03 `--maintain`：8.37.1 之後的改動（`turn.step` 本體抽成 `lintTurnStep` 由 `main.ts` 呼叫、狀態列加上又拿掉、「動手前要說明」的提示文字）都分類為「沒有影響」；重跑 `--quick` 39/39 符合預期（716 秒）。結果：in step。
  2026-11-03 第二次 `--maintain`（分層實作完成）：lint.ts 刪除，狀態與 hook 的邏輯搬進 `engine/engine.ts` 的方法、平台事件的翻譯搬進 `adapters/claude-code/`。分類：
  - 「不再描述」：只有名稱，每個 hook 對應到一個方法，粒度不變，模型的動作改對到方法名稱，模型本身不用改。
  - 「沒有影響」：新增的兩件事不寫跨事件狀態——非 git 資料夾的根目錄（`Config.git`），和手動時機（`/lint` 走 `skillPrompt`，不動 `reviewPending`）。
  - 證據：
    - 新舊兩版在 56 個情境上逐字一致，包括 P11–P17 的路徑和最後存下的狀態（紀錄 `lint-engine-impl-equivalence.txt`，/ship 後在本機的 `.claude/archived/`）。
    - 41 個原有測試在新引擎上全過。
    - 重跑 `--quick`，39/39 符合預期（638 秒）。
  
  結果：updated（涵蓋與雜湊），in step。
  之後兩次 review 的修正（commit 的檢查改在所在的子 repo、`edited` 回傳是否清掉快取、`/lint` 逐檔跑）分類為「沒有影響」：都發生在拿走欠的東西之後，不寫 `$.state`，跨事件狀態沒變；沒有重跑 TLC，只更新雜湊（engine.ts `adea58e89a1e…`、ports.ts `6822c45ff5cf…`）。
- **重跑**：`cd model && python check.py --quick`（51 個 run，MaxSteps 7，約 23 分鐘；預算 1500 秒）；不加 `--quick` 是 MaxSteps 8，會在預算用完時停下，結論不靠它。關鍵節點：`python check.py --mutants --quick`（約 26 分鐘，會超過預算停在最後一個，`clear-keeps` 另外跑）
- **設計期擴充（範圍類型，2026-11-03）**：替 `.claude/draft/lint-scope.md` 的新狀態 `LintState.answering`（「重新」的回應檢查）加上 R14–R17。模型新增：常數 `Ans`、變數 `answering`／`ansStep`／`rowLate`／`rowStep`、動作 `RowAppend`／`EmptyRow`，ghost `ansOwedG`／`ansStepG`／`answerRowG`／`checkNow`／`checksG`。結果：`--quick` 51 題中 50 題符合預期；第一版的 R3 因為狀態變多而逾時，放寬上限後守住（2,325,929 個狀態，123 秒），所以 `TIME_LIMIT` 改成 180 秒。現在的版本守住 R1–R17，每條 788,904 個狀態。這部分描述的是骨架，不是程式：實作後要跑 `--maintain`，從真正的程式重畫模型。雜湊：LintRules.tla `cfff4d96c89e…`、LintMod.tla `59458642a541…`、check.py `4c83ecd2187c…`。
- **維護紀錄（8.40.2，2026-11-03）**：一輪結束分成「答完」與「被打斷」，被打斷的不欠交代（使用者 2026-11-03），模型的 `TurnComplete(answered)` 照改；新增 R12（8.40.1 的規則 A）、R13（答完的 /review 要記下）。重跑 `--quick` 41/41 符合預期（舊版本仍照之前打破，新版本守住 R1–R13，植入 bug 各被抓到）；`review-ignored` 突變現在打破 R13。

## 問題帳

| # | 問題 | 推動哪一邊 | 最便宜的證據 | 結清方式 | 結果 |
|---|---|---|---|---|---|
| Q1 | 第一版的程式在所有順序下守住哪些規則 | 已證明 | TLC 跑 `Fix=FALSE` | 推翻 | R3 以外全部被打破（P1–P9）；R3 依字面守住 |
| Q2 | 修正能不能讓全部規則守住 | 最好可能 | TLC 跑現在的版本 | 範圍內 | 11 條全部守住（範圍內） |
| Q3 | 模型有沒有漏掉原始碼會走的路徑（翻譯對不對） | 翻譯 | 獨立推導、複查、review | 推翻後修正（兩次） | 第一次漏了 6 類（見「獨立推導」）；0917b911 的 review 再找到：模型的 cd 追蹤在指令失敗時跟程式不一樣、模型假設追蹤的目錄永遠是真的、沒有「同一次回覆」「唯讀指令」「工具前的文字」「被擋下的訊息」「沒有命名空間的 skill」「中途停掉的 review」「/clear」。都已補進模型，0917b911 成為第二個版本 |
| Q4 | 範圍 7 夠不夠 | 範圍 | 每條規則的植入 bug、0917b911 的每個錯都在範圍 7 被抓到 | 範圍內 | 平行重複重述（R2）在 7 首次出現；0917b911 的錯最長 7 步（R7） |
| Q5 | 0917b911 打破哪些規則 | 已證明 | TLC 跑 `Fix=TRUE, Now=FALSE` | 推翻 | R1、R4、R5、R6、R7、R8、R11（P11–P17）；R6 與 R5 的路徑是 review 沒列到的 |
| Q6 | `/draft` 的分層骨架（`.claude/draft/lint-engine.md`，本體未填）會不會讓哪條規則不成立 | 翻譯 | 對照骨架與模型的動作粒度 | 實作後結清：逐字比對 56/56 加 TLC 39/39 | 不需改模型：引擎的每個方法對應現在的一個 hook，方法裡同步的那段就是模型的一個動作；拿走在 await 之前（`toolCall`／`promptSubmit` 不是 async、`StateStore.save` 回傳 void）、放回、在拿走時讀步數、預覽 key 與「下一次回覆才放行」、review 答完才算、`/clear` 保留語言與 git 事實，都原樣保留。存檔照今天的做法每次當下寫出，前提「寫入依序存進 `$.state`」維持假設。`proceed` 之後丟例外時要放回拿走的東西（骨架後置條件 1）；平台保證已呼叫過的 `next` 不會重跑工具 |

還開著的列與理由：R18（agent 的快照只取一次）、R20（每個期限最多觸發一次）沒有建模，因為它們用的是 R1、R2 已經驗證過的同一種「同步取走並存檔」，靠論證成立。要把它們變成證明，得在模型裡加上 spans 和 timers。

## 這部分在做什麼

（statechart 圖這次沒有產生；`--maintain` 時用 `_shared/statechart.md` 的程式從模型畫出，不手畫。）

## 裁判：規則

| # | 種類 | 規則（白話） | 出處 | 結果 |
|---|---|---|---|---|
| R1 | 終究會發生 | 主迴圈寫錯語言的那段，最晚在使用者下一則模型會讀的訊息時，一定被要求用使用者的語言重新說一次 | 使用者 2026-11-02；`restateNote` | 第一版被打破（P1、P2、P4）；0917b911 被打破（P11）；現在守住 |
| R2 | 不能發生 | 同一段被要求重新說超過一次 | 同上 | 第一版被打破（P3）；之後守住 |
| R3 | 不能發生 | subagent 的文字或動作觸發主迴圈的「重新」 | `!e.agentId` | 字面守住；寬讀法即 P1，已修 |
| R4 | 終究會發生 | 做了事沒交代的一輪，一定會被要求交代：到 8.42 是在使用者下一則訊息附上「照 what-now 重新交代」；8.43 起改在這一輪結束前擋下，讓它在同一輪交代。不論哪一版，到使用者下一則訊息時，都不會有一輪做了事、沒交代又從沒被要求的。8.43 的改寫已確認（使用者 2026-11-04） | 使用者；`report-before-stop`；8.43 的時機設計（`.claude/draft/lint-timing.md`） | 第一版被打破（P4、重新載入）；0917b911 被打破（P12）；8.43 初版被打破（P18：這一輪先被別的 error 擋過，host 的 stop_hook_active 就被用掉了）；現在守住 |
| R5 | 不能發生 | 沒有欠交代時被要求重新交代（8.43：同一輪已經要求過一次，就不再要求） | 理想 | 修改中途的版本被打破（P10）；0917b911 被打破（P13）；8.43 初版被打破（P19：每次被 error 擋下就再要求一次）；現在守住 |
| R6 | 不能發生 | 刪除或搬移第一次下就直接執行（讀法 D1-B：放行只到這一輪結束） | `destructive-preview.toml` | 第一版被打破（P5）；0917b911 被打破（P14）；現在守住 |
| R7 | 不能發生 | 沒預覽過的刪除目標，因為別的被放行而跟著放行 | 使用者 | 第一版被打破（P6）；0917b911 被打破（P15）；現在守住 |
| R8 | 不能發生 | 收尾紀錄宣稱改檔後有 review 或指令，實際沒有 | `session-record.toml` | 第一版被打破（P7）；0917b911 被打破（P16）；現在守住 |
| R9 | 不能發生 | 收尾紀錄在改過檔的 session 說「沒有改檔」 | `sessionRecord` | 第一版被打破（P8）；之後守住 |
| R10 | 不能發生 | 一輪第一個動作前沒文字，卻沒被標出「先說明」 | `explain-before-edit.toml` | 第一版被打破（P9）；之後守住 |
| R11 | 不能發生 | 主迴圈的刪除，在模型拿到預覽之前就執行（同一次回覆裡的另一份相同指令被放行）——**未經確認** | 0917b911 的 review；`destructive-preview` 的頁尾「確認沒錯，再下一次」 | 第一版、0917b911 被打破（P17）；現在守住 |
| R12 | 不能發生 | 這一輪動作前已經說過話（畫面上看到的），卻被標「先說明」 | 使用者 2026-11-03（規則 A） | 8.40.1 起守住（說話以 thinking 送出也算） |
| R13 | 不能發生 | 改檔後答完過 /review，收尾紀錄卻說沒 review | 使用者 2026-11-03 | 現在守住；突變 `review-ignored` 會打破它 |
| R14 | 不能發生 | 模型回答「重新」的那一列（交付之後才開始的回覆裡，第一列看得到內容的主迴圈列）沒有被檢查 | 範圍設計（`.claude/draft/lint-scope.md`），使用者 2026-11-03 | 8.43.0 程式守住；Break `R14`、`vis`、`queued` 各打破它 |
| R15 | 不能發生 | 同一次交付被檢查超過一次 | 同上 | 8.43.0 程式守住（同一次送達不被檢查兩次）；Break `R15` 打破它 |
| R16 | 不能發生 | 不是回答的列被當成回答檢查（交付前就寫好、晚寫入的那一列，或沒有內容的列） | 同上 | 8.43.0 程式守住；天真的取法（`Ans = "naive"`）打破它 |
| R17 | 不能發生 | subagent 的列觸發「重新」的檢查 | 同上 | 8.43.0 程式守住；Break `R17` 打破它 |
| R19 | 不能發生 | 一輪在結束前被擋超過 4 次（error 最多 3 次，交代或 check 另外各 1 次），導致一條過不了的檢查把這一輪卡死——已確認（使用者 2026-11-04） | 8.43 的時機設計（`STOP_HOLDS`） | 8.43 程式守住；Break `R19`（不設上限）打破它 |
| R21 | 不能發生 | 排隊要給模型的那一行（一輪結束時放行的檢查、subagent 結束後、外部改檔、時間到）送了兩次，或到使用者下一則訊息時還沒送到——已確認（使用者 2026-11-04） | 8.43 的時機設計（`queued`） | 8.43 程式守住；Break `R21`（送出後沒拿掉）打破它 |

上層規範：無

## 讀法

| # | 文字 | 讀法 A | 讀法 B | 結果 |
|---|---|---|---|---|
| D1 | 刪除預覽的放行多久有效 | 永久 | 只到這一輪結束 | 使用者選 B |
| D2 | mod 重新載入算不算範圍內 | 算 | 不算 | 使用者選 A |
| D3 | 「重新」的回答是哪一列 | 交付後的第一列 | 模型拿到「重新」之後才開始的回覆裡，第一列看得到內容的主迴圈列 | 使用者照建議（2026-11-03）選 B |
| D4 | 一輪在回答前就結束 | 丟掉 | 模型讀到了才丟，跟著排隊訊息、還沒讀到的留給下一輪 | 使用者選「丟掉」；第二推導（A-3）指出排隊訊息模型根本還沒讀到，所以細化成 B |
| D5 | 一列同時回答兩種「重新」 | 檢查兩次 | 合併成一次 | 使用者照建議選 B |

## 數學本質

順序（H1、H3）：同一個模組的多個 hook 交錯，host 決定順序。TLA+／TLC 列舉範圍內的所有順序；已證明＝範圍內每個狀態都守住，最好可能＝理想本身。

## 前提

| 前提 | 以為 | 出處 | 怎麼確定 | 結果 |
|---|---|---|---|---|
| subagent 的事件帶 `agentId`，主迴圈的不帶 | 是 | `claude-code.d.ts` `TurnStartInput.agentId`、`tool.call` 的 agentId | 讀出 | 是 |
| mod 重新載入時模組變數歸零、`$.state` 留著 | 是 | `reference.md`：「`$.state` and `$.store` stay; the module's own variables start over」 | 讀出 | 是 |
| 同一則訊息裡的工具呼叫，hook 可能交錯執行 | 可能 | host 並行跑工具 | 假設 | 模型兩個呼叫同時進行 |
| `$.session.cwd()` 是 shell 真正所在的目錄：前景 `cd` 會移動它，背景指令和子殼層不會；在 hook 裡讀到的是該執行者自己的 | 是 | `claude-code.d.ts` `cwd`「keep the value read inside the hook…(a subagent's own)」、`backgroundCwdHint`「the session cwd was not changed by a backgrounded command」 | 讀出；實際 session 未另外量 | 模型的 `cwdG` 就是它 |
| 每次模型回覆是一個 `turn.step`；同一次回覆的工具呼叫都在下一個 step 之前 | 是 | `TurnStepInput`「a model request of the turn」 | 讀出 | 模型的 `MainStep` |
| 工具呼叫之前的文字先串流（turn.step），它那一列的 session.append 在工具呼叫之後 | 是 | lint.ts 註解；0917b911 的 review | 讀出（程式註解）；引擎測試 F8 模擬這個順序 | 模型的 `MainPre`／`LateAppend`。**已推翻**（2026-11-03，HUNT-2026-001）：在 Claude Opus 5.5 上，模型在工具之間對使用者說的話以 `thinking` 區塊送出（官方 Opus 5.5 migration guide「Text between tool calls is returned in thinking blocks」，每個工具前最多一段；看不到的思考是空字串），App 照樣顯示給使用者；mod 只把 `text` chunk 當成說話。實測：log 4673–4765 text 0、thinking 38，transcript 的那段 thinking 就是使用者畫面上的話。這是事件內容的前提，不是事件順序，R1–R11 的結論不受影響；修正在 `translate.ts`（見案件檔） |
| `result.isReadOnly` 標出唯讀的指令 | 是 | `claude-code.d.ts`「Bash `ls`: set」 | 讀出 | 模型的 `ro` |
| `/clear` 觸發 `session.end`（reason `clear`），之後沒有 `session.start` | 是 | `SessionEndInput` 的說明 | 讀出 | 模型的 `Clear` |
| 「交代」＝最後一次做事之後串流出 60 個字母以上（漢字算兩個） | 是 | 設計 | 讀出（程式） | 範圍外的判讀不在模型內 |
| 用 Bash 寫檔的判斷（`writesFiles`） | 啟發式 | 程式 | 假設 | 模型假設判斷正確 |
| 第 k 次回覆的每一列，都在第 k+1 次的 `turn.step` 之前寫入；`stepBegan` 早於那一步的任何一列 | 是 | 下一次請求要帶著這些列；兩個 hook 等同一個 `engine.ready` | 假設（R14–R17 依賴它） | 模型的 `MainStep` 要求晚寫入的列先寫完（`~rowLate`）；不成立時要改用列的 message id 對到步數 |
| subagent 的 `session.append` 帶 `agentId` | 是 | `translate.ts` `actorOf` | 假設（只對 `turn.start`、`tool.call` 讀出過） | R3、R17 依賴它；實作時用 hook log 量一次 |
| 一則回覆的每個內容區塊各寫成一列；只有 tool_use 或空 thinking 的列沒有看得到的內容 | 是 | 第二推導 A-2 | 讀出（transcript 結構） | 模型的 `EmptyRow` |
| 狀態的每次寫入都依序存進 `$.state` | 假設 | — | 假設 | 模型把每個動作當成一次存好；`turn.step` 中途重新載入不在模型內。分層後的 `hostState.save` 照今天的做法每次當下寫出，這個前提維持假設（依序存檔在 review 後撤回：它延後寫入，reload 時會掉資料） |

裁判的校對：這個 session 的實際運作——寫英文後下一個工具呼叫被標出（user-language）、`rm` 先被暫停再放行、指令字串不同就再擋一次（destructive-preview）、沒先說明就跑指令被標出（explain-before-edit）——與模型的對應步驟一致。

## 界與證據

| 界 | 值 | 依據 | 是緊的嗎 | 證明／範圍內 | 對哪一類成立、模型外有什麼 |
|---|---|---|---|---|---|
| 已證明 | 17/17 規則守住（R14–R17 是設計期，描述骨架） | TLC，現在的版本，MaxSteps 7，每條 788,904 個狀態（加入「重新」的動作前是 597,637） | 是：0917b911 在同範圍打破 7 條、第一版打破 10 條，植入 bug 各被抓到 | 範圍內 | 模型外：檢查內容本身、5 秒設定快取、畫面、啟發式判斷的準確度、subagent 的「下一次回覆」（模型讓它在任何下一個呼叫放行，比程式寬） |
| 最好可能 | 理想 | 已證明達到 | 相遇 | 範圍內 | — |
| 範圍外 | 更多步、更多同時呼叫也守住 | 論證：所有「取走待辦」都是 await 之前的同步 `splice`，每個待辦只會被一個呼叫取走；所有狀態都在 `$.state`，重新載入只讀回；刪除的放行比的是 hook 裡讀到的真實目錄與回覆序號，不依賴之前的指令 | — | 論證，未經第二人檢查 | — |

## 檢查會說「不」

- 第一版（`Fix=FALSE`）：R3 以外全部被打破。
- 0917b911（`Fix=TRUE, Now=FALSE`）：R1、R4、R5、R6、R7、R8、R11 被打破（P11–P17）。
- 現在的版本植入一個 bug（Break）：R2 重述兩次、R3 subagent 觸發標記、R5 無條件欠交代、R7 一放行全部放行、R8 review 判斷忽略改檔、R11 放行不看回覆序號——六個都被抓到。
- 「重新」的檢查（設計期）：天真的取法——主迴圈的任何一列都取走——打破 R16，最短路徑是「開始一輪 → 呼叫 → 交付 → 一列只有 tool_use」；植入 bug R14（不取）、R15（取了不清）、R17（subagent 的列也取）各被抓到；修正的兩處各自必要：取走時不看有沒有內容（`vis`）、一輪結束全部清掉（`queued`），都打破 R14。
- 引擎測試 41 個：P1–P9 在 8.37.0 第一版紅；新加的 12 個（F1–F8、F14、語言誤報）在 0917b911 紅；全部在 8.37.1 綠。原本 P10 的回合結束事件格式不完整，mod 的 hook 被跳過，之前是假綠，已改正。

## 關鍵節點（突變分析，2026-11-03）

問題：哪些 hook 步驟是任何狀態變化下都不准出錯的——單元測試該守在哪裡。做法：模型加常數 `Mut`，每個值拿掉一個步驟的核心效果，`python check.py --mutants --quick`（MaxSteps 7，R1–R12 全查；`-continue` 一次列出所有被打破的不變式）。`Mut = "none"` 時模型與之前相同。新增 R12（規則 A，使用者 2026-11-03）：動作前已經說過話，就不能被標「先說明」。

| 節點（拿掉的效果） | 打破的規則 | 守著它的單元測試 |
|---|---|---|
| 重新載入後狀態還在（`reload-forgets`） | R1、R4、R9、R10 | P8（R9）、P9（R10）；R1、R4 在重新載入後**沒有測試** |
| `/clear` 重設狀態（`clear-keeps`） | R5、R6、R8 | F14（只測 R1）；R5、R6、R8 在 `/clear` 後**沒有測試** |
| 使用者訊息帶走欠的東西（`prompt-take`） | R1、R4 | P4、Q1、F7、F2 |
| turn.start 重設這一輪的旗標（`start-reset`） | R6、R10 | P5（R6）；R10 在新一輪開始時**沒有測試** |
| 工具前的串流文字被聽到（`stream-deaf`） | R12、R5 | 8.40.1 的 thinking 測試、spoke 三個測試 |
| 最後一個工具後的文字被聽到（`text-deaf`） | R12、R5 | P10、F5 |
| 改檔被計數（`no-edit-count`） | R8、R9 | P7、P8 |
| 主迴圈的呼叫帶走待重述（`call-take`） | R2 | P3 |
| 第一個沒說話的動作被標出（`no-explain`） | R10 | P9、8.40.1 的 hidden-thinking 測試 |
| 刪除先暫停預覽（`no-hold`） | R6 | rm 被暫停、F3、F4 |
| 做了事就忘掉之前的交代（`work-keeps-report`） | R4 | F8 |
| turn.complete 記下欠交代（`no-owe`） | R4 | Q2 |
| 答完的 /review 被記下（`review-ignored`） | R13（8.40.2 補上；之前**無**） | — |

讀法：打破越多規則的節點越關鍵；「沒有測試」的格子是單元測試該補的地方。`review-ignored` 原本沒打破任何規則，表示規則有洞：R8 只禁止「宣稱 review 過卻沒有」，沒有規則要求「review 過就要記下」。使用者 2026-11-03 確認補上 R13，`review-ignored` 現在打破 R13。8.40.2 補上表裡三個「沒有測試」的格子（reload 後的 R1、R4，`/clear` 後的 R5、R6、R8，新一輪的 R10），每個測試都在弄壞對應程式時變紅。

## 獨立推導

第一次（封存到驗證才打開）：十條全部打破，其中 6 類是模型漏掉的路徑（呼叫被擋或失敗、await 之間的交錯、非改檔工具、後面一輪的交代、跨目錄與 subagent 的刪除、用 Bash 寫檔、slash command 的語言），已補進模型並修正程式。

第一次修正後的複查（第二位讀者只讀程式）：八條各找到模型外的破法，0917b911 修掉（hook 失敗放回、取走後立刻存檔、`/cost` 不取走、欠的交代跟著指令、背景指令不算、`git rm`／`bash -c`／`rd`／`rimraf` 也預覽、子殼層與兩種 shell、建 lint 前的改檔）。

0917b911 的完整 review（審查者加驗證者，15 項成立）：其中「目錄」「同一次回覆」「唯讀指令」「工具前的文字」「被擋下的訊息」「沒有命名空間的 skill」「中途停掉的 review」「/clear」是模型沒涵蓋的路徑，已補進模型成為第二個版本，TLC 在它身上抓到 P11–P17；8.37.1 全部修掉。原本記為邊界的 9 項，review 判定「同一則訊息兩個相同刪除」「交代後跑唯讀指令」「中途停掉的 review」站不住，已修；`find -delete` 改成實際列出清單。

「重新」回應檢查的設計期推導（2026-11-03，封存到模型寫完才打開，只讀程式）：照最初的契約寫法，A、B、C 都會被打破，共七條路徑。其中這幾條模型原本沒涵蓋，已補進模型：
- 只有 tool_use 或空 thinking 的列（A-2、C-4）：模型的 `EmptyRow`。
- 跟著排隊訊息交付、模型還沒讀到，這一輪就結束了（A-3）：讀法 D4。
- 交付前就寫好、晚寫入的那一列（C-1）：模型原本就有，`rowLate`。

其餘路徑要靠實作的順序來守，寫進 draft 的後置條件 12，不在模型的粒度內：
- thinking 裡的字沒有傳進檢查（A-1），所以 `ReplyEvent` 要多帶 `visible`。
- offer 模式要在 `turnStarted` 才設定（A-4）。
- 交付時才設定、放回時撤掉（B-2、C-3）。
- 取走和存檔都要在第一個 await 之前（B-1，否則也會打破 R12）。

D 只有在「subagent 的 `session.append` 帶 `agentId`」這個前提下才守住，這個前提已記進前提表。

仍記為邊界（不修，review 判定站得住）：`~`、`$` 無法展開，只標明；`xargs rm` 要刪什麼由前一個指令決定，暫停一次後放行；MCP 寫檔工具不算改檔；hook 逾時被跳過；`warn` 不擋；交代後又跑會改東西的指令要再交代一次；subagent 跑到回答完的 `/review` 算 review。
