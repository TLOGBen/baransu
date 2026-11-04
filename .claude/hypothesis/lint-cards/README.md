# 假說：lint 的卡片，在畫面的任何畫法與任何事件順序下，都畫在它那一列

## 2026-11-04 擴充二：卡片說的話在當下為真，而且只說一次

- **現況（8.46.0，未重跑）**：使用者定下「用途 > 顯示」：能畫就畫，不為了保證看得到加機制。8.46.0 照此改：拿掉輸入框上方那條與收合組的強制展開（E4–E7、Q1 退役；E1 縮成「`/lint` 一定有一張」），P10–P13 照修法修掉，P14、R3 決定為「沒有發現就不畫」。這份紀錄描述的是 8.45.0；`model/card-content.test.ts` 已改成新規則（多了 B0：輸入框上方不留卡片），還沒在 8.46.0 上重跑，`view-judge`、`view-more`、`CardRules.tla` 仍是舊規則。使用者選擇先在真的 session 裡玩過再重跑。

- **使用者要拿它做什麼**：在真的 session 看到刪除預覽放行後又出現一次（純文字、寫著「再下一次」），要先知道還有哪些情境的卡片不符預期，再一次修好。
- **理想**：每張卡片上的每一句話，在你讀到時都還成立；同一個動作的同一件事只對你說一次，也只對模型說一次。
- **主張與量詞**：對每個時機 × 每個等級（含沒有發現）× 第一次送出與下一個回應再送一次，lint 畫的每張卡片都只說當下為真的話，而且只說一次。
- **已證明**（往上推）：82 個情境在真程式上跑過（`model/card-content.test.ts`，測試複本，範圍內），72 個守住，10 個被打破（P10–P14，其中 P13、P14 和文件或既有設計衝突）；另有 1 個（`/ship` 沒有發現時的卡片）和 E1 衝突，列為讀法 R3。
- **最好可能**（往下壓）：理想本身。P10–P12 修法已知（放行時拿掉已交代過的發現；放行的卡片也轉路徑清單；preset 的 message 不寫「再下一次」），修完應達到；P13、P14、R3 要使用者先決定規則。
- **差距**：還能改進，修法已知，還沒修。範圍外：`around:*`、`after:*` 沒掃；E8 的「被擋下卻寫成跑完」這一半沒有情境打破過，檢查器能不能判出來沒有證明。
- **規則確認**：E8–E11 與讀法 R1（放行時模型也不再收到）、R2（放行時畫面上不留卡片）使用者 2026-11-04 確認（回覆「先按建議」）。
- **涵蓋的對象**：`engine/engine.ts`（`callAfterTake` 的 hold-once、`withPreview`、放行後的 `keepCard(summarize(...))`；回答處理的 `answerCard`；`skillPrompt`；Stop 的處理）、`engine/text.ts`（`summarize`、`skillCard`）、`engine/timing.ts`（`PRE`、`settle`）、`skills/lint/preset/sets/runtime.toml`（`destructive-preview` 的 message）、`view/card.ts`（`drawCard`）。
- **描述的版本**：8.45.0（commit `8be4e929`，工作樹只多了 `card.ts` 的圖示對齊）。
- **定稿雜湊**：card-content.test.ts `857b56431eec…`、engine.ts `4a6586c2cf41…`、text.ts `10d741721123…`、card.ts `06b5a948bf35…`。
- **重跑**：把 `model/card-content.test.ts` 複製到測試複本的 `hooks/`（只放這一個測試檔的複本最快），`claude plugin test .`（82 個情境，約 20 秒）。每個情境印一行 `SIT …`，寫出兩次送出各畫了什麼。
- **第二推導**：獨立 agent 只讀原始碼與 preset，找到 P11（E8、E9、E11、R1）、P12 的 E11，根因與這邊相同；它把 `/ship` 沒有發現時的卡片判成 E10 違反，這邊依 E1 判成該有，兩條規則衝突，列為 R3。它沒找到 P10 的一般 `check`、P13、P14。
- **檢查器的校準**：使用者截圖的刪除情境是已知事實。第一版只判出 E8、E11，漏了 E9、R1（擋下的卡片把預覽放在 `paths`，比對只看發現的行），改成連路徑也比之後才定稿。兩個 E10 誤判（`/ship` 違反 E1 的例外、`post:retry` 把前置指令的卡片算進來）修正後才定稿。

| # | 類型 | 規則 | 結果 |
|---|---|---|---|
| E8 | 不能發生 | 卡片說的和結果相反（已執行卻寫「再下一次」「沒有執行」「改寫再跑」；被擋下卻寫成跑完） | 打破：P11、P12 |
| E9 | 不能發生 | 同一個動作的同一條發現出現在兩張卡片上 | 打破：P10、P11、P13（P13 是 `format.md:88` 寫明的行為） |
| E10 | 不能發生 | 沒有發現的動作也畫卡片（`/lint` 除外） | 打破：P14（`answer.test.ts` R16 刻意的設計）；`/ship`、`/review` 見 R3 |
| E11 | 不能發生 | 刪除預覽列得出路徑，卻畫成純文字 | 打破：P11、P12 |
| R1 | 讀法（已定） | 放行時模型不再收到已交代過的發現 | 打破：P10、P11；P13 守住 |
| R2 | 讀法（已定） | 放行時畫面上不留卡片 | 同 E9 |
| R3 | 讀法（開著） | skill 開始前沒有發現：E1 說一定有一張，E10 說不該有 | 要使用者決定 |

| 情境 | 守住 | 被打破 |
|---|---|---|
| `pre:edit`、`pre:bash`、`pre:commit`、`pre:push` × error／retry／warn／info／沒有發現 | 全部 | — |
| 同上 × `check` | — | P10 |
| 刪除預覽 × `check` | 第一次 | 第二次 P11 |
| 刪除預覽 × `warn`／`info`／`retry` | — | P12 |
| `pre:stop` × error／warn／info／沒有發現 | 全部 | — |
| `pre:stop` × `check`／`retry` | 第一次 | 第二次 P13 |
| `post:edit`、`post:bash`、`post:commit`、`post:push`、`post:agent`、`pre:compact`、`post:compact`、`post:file`、`/lint` × 每個等級 | 全部 | — |
| `pre:skill:ship` × 每個等級 | 全部（沒有發現時那張依 E1 算該有，見 R3） | — |
| `post:retry` × error／warn／info | 全部 | — |
| `post:retry` × 沒有發現 | — | P14 |

## 2026-11-04 擴充：每個時機都有一張看得到的卡片

- **使用者要拿它做什麼**：確認卡片改成「每個時機都畫」之後，有沒有該出現卻沒出現、或哪個時機沒有卡片，修完再 commit。
- **理想**：lint 有結果要給你看時，一定有一張卡片，出現在對的位置，留到你該看的時候，而且只出現一次。
- **主張與量詞**：在所有事件順序下（同一次回應裡的多個呼叫、Agent 呼叫比 subagent 先結束、skill 由模型載入或由你打、兩則訊息之間的多個無呼叫事件、mod 重新載入），每個時機給人看的結果都是一張看得到的卡片：有呼叫的掛在那次呼叫底下，沒呼叫的畫在輸入框上方、留到你送出下一則訊息，沒有畫面能畫那條時改送一行文字。
- **已證明**（往上推）：修正後，E1–E7 在 18 個情境上全部守住（`model/view-judge.test.ts`，真程式、測試複本，範圍內）；review 的 F1（卡片寫出還有幾條、工具輸出末 3 行）、F2（同一個 Workflow 的 subagent 各一張）由 `model/view-more.test.ts` 守住。每個修正都由故意改壞的版本確認抓得到（`model/view_mutants.py`，12/12）。修正前同一個檢查器打破 7 個情境（P4–P9），每條路徑先紅後綠。
- **最好可能**（往下壓）：理想本身，修正版在範圍內達到。W2 靠「同時送一行文字」達到（問卷佔著那條時 hook 必須讓），代價是終端機與桌面版看得到卡片和文字兩份，使用者 2026-11-04 選了這個代價。
- **差距**：範圍內相遇。範圍外：輸入框上方超過 20 張時最舊的仍會被丟（W1 的讀法下仍算消失，要兩則訊息之間 21 個無呼叫事件）；第二推導的 E3-b、E5-b 沒在真程式重現。
- **規則確認**：E1–E7 與讀法 W1–W3（都算違反）使用者 2026-11-04 確認；W4（自己收起那條）當作正常，只回報。
- **涵蓋的對象**：`engine/engine.ts`（`post`、`keepCard`、`promptSubmit` 清 band、`skillPrompt`、`skillCalling`、`bandCards`、`agentStarted`／`agentStopped` 的 `agentCalls`、各時機改用 `post`）、`engine/text.ts`（`cardOf`、`skillCard`、`cardText`）、`adapters/claude-code/hooks.ts`（Skill 的 `tool.call`、`agent.spawn`）、`instance.ts`、`view/hooks.ts`、`view/port.ts`、`view/card.ts`。
- **描述的版本**：8.45.0（未 commit 的工作樹，2026-11-04）。
- **定稿雜湊（修正後）**：engine.ts `4a6586c2cf41…`、text.ts `10d741721123…`、engine/ports.ts `e4b22e015c35…`、adapters hooks.ts `b0784a8e5f63…`、adapters ports.ts `c00ddf1c07c2…`、instance.ts `7cce2e5c7b73…`、view/hooks.ts `3a6d544bbeab…`、view/port.ts `8834e3237f37…`、view/card.ts `31828d1835ef…`、view-judge.test.ts `19acbcb49b14…`、view-more.test.ts `af864842ad71…`、view_mutants.py `986588c96782…`。12 組改壞測試跑在加入「讀 Claude Code 語言設定」之前的 engine.ts 上；那次改動不碰卡片與 band，加入後全部測試（316 個，含兩個檢查器）重跑全過。修正前凍結的版本：engine.ts `e681b0e7a1fa…`，檢查器 `b538a495c560…`。
- **重跑**：`model/view-judge.test.ts`、`model/view-more.test.ts` 複製到測試複本的 `hooks/`，`claude plugin test .`（20 個情境，約 5 秒）；說得出不：`python model/view_mutants.py <測試複本>`（12 組，約 15 分鐘）。
- **第二推導**：獨立 agent 只讀原始碼，找到 E3、E4（W1）、W2、W3 與我們相同，另外找到 E4-b（P8）、E5-a（P9），補進檢查器後確認；E1-a（`/lint help`、`show` 沒卡片）是讀法：那兩個不跑任何檢查，沒有結果，不算違反；E3-b（重新載入時 `skillCall` 留舊值）、E5-b（Stop 檢查還在跑時你送出訊息，卡片晚到）需要平台允許那種順序，沒有在真程式重現，列為開著的問題。

| # | 類型 | 規則 | 結果 |
|---|---|---|---|
| E1 | 不能發生 | 某個時機有結果要給人看，卻沒有卡片；skill 開始前與 `/lint` 一定有一張 | 修正前：兩個 skill 同時載入時打破（P4）；修正後守住 |
| E2 | 不能發生 | 卡片掛在 Agent／Skill 呼叫底下，那一列在畫面上卻看不到 | 守住（背景 subagent 比 Agent 呼叫晚結束也守住） |
| E3 | 不能發生 | 卡片掛錯呼叫 | 修正前打破（P4）；修正後守住（用 skill 名稱對回呼叫） |
| E4 | 不能發生 | 沒呼叫的卡片在你送出下一則訊息前就消失（W1：存了沒畫也算） | 修正前打破（P5、P8）；修正後守住（上限 20、全畫、訊息真的送出才清） |
| E5 | 不能發生 | 你送出下一則訊息後，上一則的卡片還在 | 修正前只貼圖片打破（P9）；修正後守住 |
| E6 | 不能發生 | 同一張卡片同時在呼叫底下和輸入框上方 | 守住 |
| E7 | 不能發生 | 沒有畫面能畫那條時沒改送文字（W2 問卷、W3 手機都算） | 修正前 W2（P6）、W3（P7）打破；修正後守住（沒呼叫的卡片一律同時送文字） |

## 2026-11-03 原始主張
- **已證明**（往上推）：修正版（模型 `Variant = "new"`）在範圍內（2 次呼叫、MaxSteps 8、卡片上限 1 與 2）守住 A、B、D、Q1；24 種「顯示方式 × 呼叫結果 × 桌面／終端機」在真的 lint 程式碼上全過。現在的程式（`"old"`）打破 A、B、Q1，24 種錯 12 種。
- **最好可能**（往下壓）：理想本身——修正版在範圍內達到。
- **差距**：範圍內相遇；但修正版靠兩個還沒在真的 App 驗證的前提（見前提表的「假設」），以及一條開著的讀法（UserClose）。
- **主張與量詞**：在所有事件順序下（呼叫開始、結束、存卡片、收進組、展開或收合、捲動重畫、重新載入、卡片超過上限被刪、`/clear`），以及每種顯示方式（獨立列、組裡展開的列、收成一行的組），每張還在的卡片都畫在它那一列。
- **規則確認**：A、B、D、Q1 已確認（使用者 2026-11-03：Q1 選 b「我還是想看到」、Q2 上限 500 刪掉的不算、Q3 只在 session 內）。UserClose **未確認**，是開著的讀法。
- **涵蓋的對象**：`plugins/baransu/hooks/adapters/claude-code/view/hooks.ts`（`ui.render` 的 ToolUse、ToolResult、ToolGroup hook；8.45.0 從 `hooks.ts` 搬來，判斷不變，ToolUse 多畫同一次呼叫底下各 subagent 的卡片）、`view/card.ts`（`drawCard`）、`engine/engine.ts`（`keepCard` 與上限、`cardFor`、`cleared`、`callAfterTake` 存卡片的時機）。
- **描述的版本**：8.45.0（未 commit 的工作樹，2026-11-04；被擋下的獨立列，ToolResult 直接回空區塊，不靠改寫 output）。
- **定稿雜湊（8.45.0）**：view/hooks.ts `3a6d544bbeab…`、view/card.ts `31828d1835ef…`、engine.ts `4a6586c2cf41…`、CardRules.tla `b84dc49e0d00…`、CardRender.tla `2df7aa4b996c…`（只改了來源路徑的註解）、check.py `d28538e2a686…`
- **維護紀錄**：2026-11-04 `--maintain`（8.45.0，卡片改照 11/03 的設計稿「Lint 卡片設計」）：`card.ts` 換了顏色與圖示，多了「已改」「只給你看」兩種卡片，刪除預覽改畫成分組的路徑清單；`engine.ts` 存的卡片多了 `paths`，種類多了 `edited`、`note`。模型描述的是卡片畫在哪一列、會不會漏畫或畫兩次，這些都沒變（`keepCard`、`cardFor`、ToolUse／ToolResult／ToolGroup 三個 hook 沒動），分類為「沒有影響」。重跑 `--quick` 0 unexpected（47 秒），`cards.test.ts` 24 個全過。結果：in step。同日稍晚，三個 hook 搬進 `view/hooks.ts`（判斷不變；ToolUse 多畫同一次呼叫底下各 subagent 的卡片，ToolGroup 展開時也算它們），再重跑 `--quick` 0 unexpected（47 秒），`cards.test.ts` 24 個全過。結果：in step。
- **重跑**：`cd model && python check.py --quick`（MaxSteps 6，約 45 秒）；`python check.py`（MaxSteps 8，約 50 秒）。情境判斷：測試複本 `claude plugin test .` 的 `cards.test.ts`（24 個，約 3 秒）。

## 問題帳

| # | 問題 | 推動哪一邊 | 最便宜的證據 | 結清方式 | 結果 |
|---|---|---|---|---|---|
| Q1 | 現在的程式在哪些畫法下看不到卡片 | 已證明 | 24 種情境在真的程式碼上跑 | 推翻 | 收進組（展開或收成一行）且帶卡片的 12 種全錯；獨立列全對 |
| Q2 | 有沒有某種事件順序讓卡片漏畫 | 已證明 | TLC 列舉所有順序 | 推翻（舊）／範圍內（新） | 舊版打破 A、B、Q1；修正版全部守住 |
| Q3 | 修正版的三處改動是否都必要 | 檢查會說不 | 拿掉一處再跑 | 證明 | 拿掉 ToolUse → 12 種錯（TLC：A）；拿掉 ToolResult 清空 → 被擋的獨立列錯（B）；拿掉 ToolGroup → 收成一行的 6 種錯（Q1）；卡片在兩處都畫 → D |
| Q4 | 卡片要是晚一步才存，修正版還守得住嗎 | 前提 | TLC `KeepFirst = FALSE` | 推翻 | 守不住（A、B、Q1）。原始碼是先存再交回（`engine.ts` 371、513-518），所以修正版靠這個順序；改程式時不能把存卡片挪到 hook 回傳之後 |
| Q5 | 修正版會不會蓋過使用者手動收合 | 讀法 | TLC `UserClose` | 推翻 | 會：組裡有卡片時，你收合也會被打開。要不要讓收合優先，要使用者決定 |

## 裁判：規則（`model/CardRules.tla`）

| # | 類型 | 規則 | 出處 |
|---|---|---|---|
| A | 不能發生 | 有卡片、已結束的呼叫出現在畫面上，卻看不到卡片 | `hooks.ts` 註解「Lint's card under the call it is about」；使用者回報 |
| B | 不能發生 | 被擋下的呼叫，卡片和紅字同時出現，或只剩紅字 | 同處「in place of the error text for a held or refused call」 |
| C | 不能發生 | 跑完的呼叫，卡片蓋掉工具本身的結果 | 同處「below the tool's own result otherwise」（情境判斷檢查；TLC 模型不畫結果內容） |
| D | 不能發生 | 同一張卡片在同一列畫兩次 | 理想 |
| Q1 | 不能發生 | 收成一行的組裡有帶卡片的呼叫，卻維持一行 | 使用者 Q1-b |
| UserClose | 讀法 | 使用者收合的組維持收合 | 開著的讀法，只回報 |

## 前提

| 前提 | 怎麼確定 | 結果 |
|---|---|---|
| 獨立列畫 ToolUse，結果由 ToolResult 畫在下面 | 實測（HUNT-2026-002：`Lhvr4VrP` use 與 render 都有） | 是 |
| 收進組後，每一列由 ToolUse 直接畫結果，不呼叫 ToolResult | 實測（`Gciu2RD1`、`4fCYvDC1` 只有 use）＋讀出（`ToolUse.output`：「An expanded group's rows draw it inline」） | 是 |
| 收成一行的組只畫 ToolGroup | 讀出（`ToolGroup`：「the group draws one line」） | 是 |
| ToolGroup hook 設 `isExpanded` 就會展開 | 讀出（「A hook that sets `isExpanded` unfolds the group where it is」） | 是 |
| 組裡每個呼叫帶 `tool_use_id` | 讀出（「Absent on a desktop host that predates it」） | 假設：目前的桌面版有 |
| 把 ToolUse 的 `output` 改成空字串，組裡那一列的紅字就不見 | — | **假設**，要在真的 App 驗證（`/prove-it`） |
| 收進組、展開或收合時，平台重畫組裡每一列 | 部分實測（重新載入後每列都有 use） | 假設 |
| 呼叫跑完時，該列從「執行中」重畫成「結束」 | 實測（use `running=true` 之後 `running=false`） | 是 |
| 卡片在 tool.call hook 回傳之前存好 | 讀出（`engine.ts` 371、513-518） | 是 |

## 界與證據

| 界 | 值 | 依據 | 證明／範圍內 | 模型外 |
|---|---|---|---|---|
| 已證明 | 修正版守住 A、B、D、Q1 | TLC，2 次呼叫、MaxSteps 8、3,834 個狀態；24 種情境在真的程式碼上全過 | 範圍內 | 卡片的外觀；subagent 的列（同一套 id 機制，未另外建模）；終端機的進度列；`$.state` 寫入失敗 |
| 最好可能 | 理想 | 修正版達到 | 範圍內 | — |

## 檢查會說「不」

- 現在的程式：TLC 打破 A、B、Q1；情境判斷錯 12 種。
- 修正版各拿掉一處：nogroup → Q1、noempty → B、double → D；情境判斷各自重新變紅。
- 情境判斷的校準：第一次把被擋的獨立列判成沒卡片，對照已知事實（`lint.test.ts` 的 `a held rm is drawn as a card`）找到判斷的比對條件漏了「先確認」，修正後才採用。

## 出錯路徑（現在的程式）

- **P1 — A、B：被擋下的呼叫收進組後只剩紅字**。1. 呼叫 1 被刪除預覽擋下，lint 存卡片；2. 那一列是獨立列，ToolResult 畫出卡片（畫面「閃一下」）；3. 呼叫 2 開始，兩列收成一組；4. 組裡的列由 ToolUse 畫，lint 沒有 ToolUse hook，畫出存下的紅字。害處：該看的預覽提醒不見了。
- **P2 — A：跑完但有 warn 的呼叫收進組後卡片消失**。同 P1，第 1 步換成跑完、帶 warn 的呼叫。
- **P3 — Q1：收成一行的組裡有被擋下的呼叫，畫面只有一行摘要**。終端機預設收合讀取類的組；組裡的列根本不畫。
