# 假說：lint 的卡片，在畫面的任何畫法與任何事件順序下，都畫在它那一列

- **使用者要拿它做什麼**：決定卡片的修正要涵蓋哪些情況，修完後不必再一個一個撞到才發現（HUNT-2026-002 的後續）。
- **理想**：lint 為一次呼叫存了卡片，只要那次呼叫出現在畫面上，就看得到那張卡片，只出現一張，出現在那一列。
- **已證明**（往上推）：修正版（模型 `Variant = "new"`）在範圍內（2 次呼叫、MaxSteps 8、卡片上限 1 與 2）守住 A、B、D、Q1；24 種「顯示方式 × 呼叫結果 × 桌面／終端機」在真的 lint 程式碼上全過。現在的程式（`"old"`）打破 A、B、Q1，24 種錯 12 種。
- **最好可能**（往下壓）：理想本身——修正版在範圍內達到。
- **差距**：範圍內相遇；但修正版靠兩個還沒在真的 App 驗證的前提（見前提表的「假設」），以及一條開著的讀法（UserClose）。
- **主張與量詞**：在所有事件順序下（呼叫開始、結束、存卡片、收進組、展開或收合、捲動重畫、重新載入、卡片超過上限被刪、`/clear`），以及每種顯示方式（獨立列、組裡展開的列、收成一行的組），每張還在的卡片都畫在它那一列。
- **規則確認**：A、B、D、Q1 已確認（使用者 2026-11-03：Q1 選 b「我還是想看到」、Q2 上限 500 刪掉的不算、Q3 只在 session 內）。UserClose **未確認**，是開著的讀法。
- **涵蓋的對象**：`plugins/baransu/hooks/adapters/claude-code/hooks.ts`（`ui.render` 的 ToolResult hook；修正版在測試複本加 ToolUse、ToolGroup hook）、`card.ts`（`drawCard`）、`engine/engine.ts`（`keepCard` 與上限、`cardFor`、`cleared`、`callAfterTake` 存卡片的時機）。
- **描述的版本**：8.40.1（修正已套進 repo 的 `hooks.ts`；被擋下的獨立列，ToolResult 直接回空區塊，不靠改寫 output）。
- **定稿雜湊**：hooks.ts `909559c47184…`、card.ts `535c5751c881…`、engine.ts `71b10179253b…`、CardRules.tla `b84dc49e0d00…`、CardRender.tla `f08f96f07e53…`、check.py `d28538e2a686…`
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
