# 假說：lint mod 的跨事件狀態，在任何事件順序下都照它的承諾提醒

- **使用者要拿它做什麼**：決定 lint mod 能不能直接 ship、信任它的「重新」「刪除前預覽」「收尾紀錄」，不必在每個 session 裡盯著它有沒有漏報或亂報。
- **理想**：主迴圈該被提醒的事，每一件都恰好提醒一次；不該提醒的（subagent 的動作、已經交代過的一輪、`/clear` 之前的對話）一次都不提醒；刪除只在模型看過預覽之後才執行；任何事件順序下都一樣。
- **已證明**（往上推）：現在的程式（模型的 `Fix=TRUE, Now=TRUE`）在範圍內（MaxSteps 7、2 段寫錯語言的文字、2 個刪除指令、2 個同時進行的主迴圈呼叫、2 個目錄）守住全部 11 條規則。0917b911（`Now=FALSE`）在同一範圍打破 R1、R4–R8、R11；第一版（`Fix=FALSE`）打破 R3 以外全部。依據：TLC，見界與證據。
- **最好可能**（往下壓）：理想本身——現在的模型達到了。
- **差距**：在範圍內「相遇」；範圍外（更多步、更多同時呼叫）只靠論證，見界與證據。
- **主張與量詞**：在所有事件順序下（prompt.submit 的各種訊息、turn.start、turn.step、session.append、主迴圈與 subagent 的 tool.call、turn.complete、skill.prompt、mod 重新載入、`/clear` 任意交錯）
- **規則確認**：R1–R10 已確認（使用者 2026-11-02；讀法 D1 選 B、D2 選 A）。R11 **未經確認**：它把 R6 收緊成「看過預覽才放行」，來自 0917b911 的 review（使用者要求全部修好），沒有另外請使用者確認這條文字。
- **涵蓋的對象**：`plugins/baransu/hooks/engine/engine.ts` 的狀態（`Memory`：`ready` 載入、`take`／`giveBack`、`save`）與讀寫它的方法：`promptSubmit`、`turnStarted`、`stepBegan`／`textStreamed`、`replyAppended`、`cleared`、`toolCall`、`turnCompleted`、`skillPrompt`、`cardFor`；平台事件到這些方法的翻譯 `hooks/adapters/claude-code/hooks.ts`、`translate.ts`；存取 `$.state` 的 `ports.ts`（`hostState`）；`hooks/main.ts` 註冊的 `turn.step`；型別 `plugins/baransu/types/index.d.ts`。模型的每個動作原本對應 lint.ts 的一個 hook，現在對應一個引擎方法（一對一，見 Q6）
- **描述的版本**：8.40.0（分層後；engine.ts sha256 `adea58e89a1e…`）
- **定稿雜湊**：LintRules.tla `72f43553d653…`、LintMod.tla `922ce7d1532a…`（8.40 只改了開頭與變數的註解，指向新的 engine.ts；動作不變）、check.py `5c9b84c65f46…`、engine.ts `adea58e89a1e…`、hooks.ts `0d3adf75de9d…`、translate.ts `b290e67c935e…`、ports.ts `6822c45ff5cf…`、main.ts `d083274f294d…`、types/index.d.ts `52df08ef23e5…`
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
- **重跑**：`cd model && python check.py --quick`（39 個 run，MaxSteps 7，約 10 分鐘；預算 1500 秒）；不加 `--quick` 是 MaxSteps 8，會在預算用完時停下，結論不靠它

## 問題帳

| # | 問題 | 推動哪一邊 | 最便宜的證據 | 結清方式 | 結果 |
|---|---|---|---|---|---|
| Q1 | 第一版的程式在所有順序下守住哪些規則 | 已證明 | TLC 跑 `Fix=FALSE` | 推翻 | R3 以外全部被打破（P1–P9）；R3 依字面守住 |
| Q2 | 修正能不能讓全部規則守住 | 最好可能 | TLC 跑現在的版本 | 範圍內 | 11 條全部守住（範圍內） |
| Q3 | 模型有沒有漏掉原始碼會走的路徑（翻譯對不對） | 翻譯 | 獨立推導、複查、review | 推翻後修正（兩次） | 第一次漏了 6 類（見「獨立推導」）；0917b911 的 review 再找到：模型的 cd 追蹤在指令失敗時跟程式不一樣、模型假設追蹤的目錄永遠是真的、沒有「同一次回覆」「唯讀指令」「工具前的文字」「被擋下的訊息」「沒有命名空間的 skill」「中途停掉的 review」「/clear」。都已補進模型，0917b911 成為第二個版本 |
| Q4 | 範圍 7 夠不夠 | 範圍 | 每條規則的植入 bug、0917b911 的每個錯都在範圍 7 被抓到 | 範圍內 | 平行重複重述（R2）在 7 首次出現；0917b911 的錯最長 7 步（R7） |
| Q5 | 0917b911 打破哪些規則 | 已證明 | TLC 跑 `Fix=TRUE, Now=FALSE` | 推翻 | R1、R4、R5、R6、R7、R8、R11（P11–P17）；R6 與 R5 的路徑是 review 沒列到的 |
| Q6 | `/draft` 的分層骨架（`.claude/draft/lint-engine.md`，本體未填）會不會讓哪條規則不成立 | 翻譯 | 對照骨架與模型的動作粒度 | 實作後結清：逐字比對 56/56 加 TLC 39/39 | 不需改模型：引擎的每個方法對應現在的一個 hook，方法裡同步的那段就是模型的一個動作；拿走在 await 之前（`toolCall`／`promptSubmit` 不是 async、`StateStore.save` 回傳 void）、放回、在拿走時讀步數、預覽 key 與「下一次回覆才放行」、review 答完才算、`/clear` 保留語言與 git 事實，都原樣保留。存檔照今天的做法每次當下寫出，前提「寫入依序存進 `$.state`」維持假設。`proceed` 之後丟例外時要放回拿走的東西（骨架後置條件 1）；平台保證已呼叫過的 `next` 不會重跑工具 |

還開著的列與理由：無（Q6 已在實作後結清）。

## 這部分在做什麼

（statechart 圖這次沒有產生；`--maintain` 時用 `_shared/statechart.md` 的程式從模型畫出，不手畫。）

## 裁判：規則

| # | 種類 | 規則（白話） | 出處 | 結果 |
|---|---|---|---|---|
| R1 | 終究會發生 | 主迴圈寫錯語言的那段，最晚在使用者下一則模型會讀的訊息時，一定被要求用使用者的語言重新說一次 | 使用者 2026-11-02；`restateNote` | 第一版被打破（P1、P2、P4）；0917b911 被打破（P11）；現在守住 |
| R2 | 不能發生 | 同一段被要求重新說超過一次 | 同上 | 第一版被打破（P3）；之後守住 |
| R3 | 不能發生 | subagent 的文字或動作觸發主迴圈的「重新」 | `!e.agentId` | 字面守住；寬讀法即 P1，已修 |
| R4 | 終究會發生 | 做了事沒交代，使用者下一則訊息一定帶著「照 what-now 重新交代」 | 使用者；`report-before-stop` | 第一版被打破（P4、重新載入）；0917b911 被打破（P12）；現在守住 |
| R5 | 不能發生 | 沒有欠交代時被要求重新交代 | 理想 | 修改中途的版本被打破（P10）；0917b911 被打破（P13）；現在守住 |
| R6 | 不能發生 | 刪除或搬移第一次下就直接執行（讀法 D1-B：放行只到這一輪結束） | `destructive-preview.toml` | 第一版被打破（P5）；0917b911 被打破（P14）；現在守住 |
| R7 | 不能發生 | 沒預覽過的刪除目標，因為別的被放行而跟著放行 | 使用者 | 第一版被打破（P6）；0917b911 被打破（P15）；現在守住 |
| R8 | 不能發生 | 收尾紀錄宣稱改檔後有 review 或指令，實際沒有 | `session-record.toml` | 第一版被打破（P7）；0917b911 被打破（P16）；現在守住 |
| R9 | 不能發生 | 收尾紀錄在改過檔的 session 說「沒有改檔」 | `sessionRecord` | 第一版被打破（P8）；之後守住 |
| R10 | 不能發生 | 一輪第一個動作前沒文字，卻沒被標出「先說明」 | `explain-before-edit.toml` | 第一版被打破（P9）；之後守住 |
| R11 | 不能發生 | 主迴圈的刪除，在模型拿到預覽之前就執行（同一次回覆裡的另一份相同指令被放行）——**未經確認** | 0917b911 的 review；`destructive-preview` 的頁尾「確認沒錯，再下一次」 | 第一版、0917b911 被打破（P17）；現在守住 |

上層規範：無

## 讀法

| # | 文字 | 讀法 A | 讀法 B | 結果 |
|---|---|---|---|---|
| D1 | 刪除預覽的放行多久有效 | 永久 | 只到這一輪結束 | 使用者選 B |
| D2 | mod 重新載入算不算範圍內 | 算 | 不算 | 使用者選 A |

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
| 工具呼叫之前的文字先串流（turn.step），它那一列的 session.append 在工具呼叫之後 | 是 | lint.ts 註解；0917b911 的 review | 讀出（程式註解）；引擎測試 F8 模擬這個順序 | 模型的 `MainPre`／`LateAppend`。**存疑**（2026-11-03）：真實 App 裡模型先寫了文字再動手，「動手前要說明」仍然觸發，表示文字沒被當成「說過話」——這個前提或它在 mock 測試裡的樣子可能不對。要在真實 App 實測（`/prove-it` 或 `/hunt`）；它影響的是「不該提醒卻提醒」，不在 R1–R11 裡（R10 只管該提醒的有沒有提醒） |
| `result.isReadOnly` 標出唯讀的指令 | 是 | `claude-code.d.ts`「Bash `ls`: set」 | 讀出 | 模型的 `ro` |
| `/clear` 觸發 `session.end`（reason `clear`），之後沒有 `session.start` | 是 | `SessionEndInput` 的說明 | 讀出 | 模型的 `Clear` |
| 「交代」＝最後一次做事之後串流出 60 個字母以上（漢字算兩個） | 是 | 設計 | 讀出（程式） | 範圍外的判讀不在模型內 |
| 用 Bash 寫檔的判斷（`writesFiles`） | 啟發式 | 程式 | 假設 | 模型假設判斷正確 |
| 狀態的每次寫入都依序存進 `$.state` | 假設 | — | 假設 | 模型把每個動作當成一次存好；`turn.step` 中途重新載入不在模型內。分層後的 `hostState.save` 照今天的做法每次當下寫出，這個前提維持假設（依序存檔在 review 後撤回：它延後寫入，reload 時會掉資料） |

裁判的校對：這個 session 的實際運作——寫英文後下一個工具呼叫被標出（user-language）、`rm` 先被暫停再放行、指令字串不同就再擋一次（destructive-preview）、沒先說明就跑指令被標出（explain-before-edit）——與模型的對應步驟一致。

## 界與證據

| 界 | 值 | 依據 | 是緊的嗎 | 證明／範圍內 | 對哪一類成立、模型外有什麼 |
|---|---|---|---|---|---|
| 已證明 | 11/11 規則守住 | TLC，現在的版本，MaxSteps 7，每條 597,637 個狀態 | 是：0917b911 在同範圍打破 7 條、第一版打破 10 條，植入 bug 各被抓到 | 範圍內 | 模型外：檢查內容本身、5 秒設定快取、畫面、啟發式判斷的準確度、subagent 的「下一次回覆」（模型讓它在任何下一個呼叫放行，比程式寬） |
| 最好可能 | 理想 | 已證明達到 | 相遇 | 範圍內 | — |
| 範圍外 | 更多步、更多同時呼叫也守住 | 論證：所有「取走待辦」都是 await 之前的同步 `splice`，每個待辦只會被一個呼叫取走；所有狀態都在 `$.state`，重新載入只讀回；刪除的放行比的是 hook 裡讀到的真實目錄與回覆序號，不依賴之前的指令 | — | 論證，未經第二人檢查 | — |

## 檢查會說「不」

- 第一版（`Fix=FALSE`）：R3 以外全部被打破。
- 0917b911（`Fix=TRUE, Now=FALSE`）：R1、R4、R5、R6、R7、R8、R11 被打破（P11–P17）。
- 現在的版本植入一個 bug（Break）：R2 重述兩次、R3 subagent 觸發標記、R5 無條件欠交代、R7 一放行全部放行、R8 review 判斷忽略改檔、R11 放行不看回覆序號——六個都被抓到。
- 引擎測試 41 個：P1–P9 在 8.37.0 第一版紅；新加的 12 個（F1–F8、F14、語言誤報）在 0917b911 紅；全部在 8.37.1 綠。原本 P10 的回合結束事件格式不完整，mod 的 hook 被跳過，之前是假綠，已改正。

## 獨立推導

第一次（封存到驗證才打開）：十條全部打破，其中 6 類是模型漏掉的路徑（呼叫被擋或失敗、await 之間的交錯、非改檔工具、後面一輪的交代、跨目錄與 subagent 的刪除、用 Bash 寫檔、slash command 的語言），已補進模型並修正程式。

第一次修正後的複查（第二位讀者只讀程式）：八條各找到模型外的破法，0917b911 修掉（hook 失敗放回、取走後立刻存檔、`/cost` 不取走、欠的交代跟著指令、背景指令不算、`git rm`／`bash -c`／`rd`／`rimraf` 也預覽、子殼層與兩種 shell、建 lint 前的改檔）。

0917b911 的完整 review（審查者加驗證者，15 項成立）：其中「目錄」「同一次回覆」「唯讀指令」「工具前的文字」「被擋下的訊息」「沒有命名空間的 skill」「中途停掉的 review」「/clear」是模型沒涵蓋的路徑，已補進模型成為第二個版本，TLC 在它身上抓到 P11–P17；8.37.1 全部修掉。原本記為邊界的 9 項，review 判定「同一則訊息兩個相同刪除」「交代後跑唯讀指令」「中途停掉的 review」站不住，已修；`find -delete` 改成實際列出清單。

仍記為邊界（不修，review 判定站得住）：`~`、`$` 無法展開，只標明；`xargs rm` 要刪什麼由前一個指令決定，暫停一次後放行；MCP 寫檔工具不算改檔；hook 逾時被跳過；`warn` 不擋；交代後又跑會改東西的指令要再交代一次；subagent 跑到回答完的 `/review` 算 review。
