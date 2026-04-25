---
name: hunt
description: >
  Diagnose before you fix. Tracks a bug from symptom to root cause — selects
  the right observability tool (playwright, MCP db query, LSP, bash logging,
  or static analysis) for the relevant layer, bisects log output, and
  confirms or discards each hypothesis before touching code.
when_to_use: "排查, 查查, 報錯, 崩潰, debug, why broken, not working, fix error, 找 bug, 追問題, 查問題, 狩獵, 定位根因, bisect, 為什麼失敗, what's wrong, hunt the bug"
allowed-tools: Read Write Edit Grep Glob Bash AskUserQuestion Skill
metadata:
  version: "1.0.0"
  scope: investigation-and-fix
---

# Hunt — Diagnose Before You Fix

開始狩獵時，第一行輸出 🥷

A patch applied to a symptom creates a new bug somewhere else.

**Do not touch code until you can state the root cause in one sentence:**
> 「根因是 [X]，因為 [證據]。」
Name a specific file, function, line, or condition. "A state management issue" is not a hypothesis. "Stale cache in `useUser` at `src/hooks/user.ts:42` because the dependency array is missing `userId`" is.

---

## Rationalization Watch

When these surface, stop and re-examine:

| 思維 | 實際意義 | 規則 |
|------|---------|------|
| 「試試這個」 | 沒有假說，隨機亂走 | 停。先寫出假說再行動。 |
| 「我確定是 X」 | 信心不是證據 | 找一個能證偽它的工具再說。 |
| 「應該跟上次一樣」 | 用已知模式套新症狀 | 從頭重讀執行路徑。 |
| 「我這邊跑得起來」 | 環境差異就是 bug | 逐一列出每個環境差異再說。 |
| 「再重啟應該就好了」 | 迴避錯誤訊息 | 原文讀最後一條錯誤。重啟不超過兩次而沒有新證據。 |

---

## Progress Signals

When these appear, the diagnosis is moving in the right direction:

| 思維 | 意義 | 下一步 |
|------|------|------|
| 「這筆 log 符合假說」 | 找到正向證據 | 再找一個獨立證據交叉確認。 |
| 「我能預測下一個錯誤會是什麼」 | Mental model 成形 | 執行預測；若吻合，模型正確。 |
| 「根因在 A，症狀出現在 B」 | 傳播路徑已理解 | 從 A 到 B 的呼叫鏈逐個確認。 |
| 「我能寫一個在舊 code 上失敗的測試」 | 假說夠具體可測 | 先寫測試再動 code。 |

進展的聲稱必須對應上述至少一個信號。

---

## Tool Scan

調查開始前，選擇**能觀測到問題發生層的工具**，不是第一個可用的工具：

| 工具 | 可觀測的層 | 選它的時機 |
|------|---------|---------|
| playwright / browser automation | UI 行為、渲染結果 | 視覺錯誤、表單流程、前端邏輯 |
| MCP db query tool | 資料狀態、schema | 資料不一致、FK 錯誤、狀態值異常 |
| LSP findReferences | 呼叫鏈結構 | 誰呼叫這個 method、哪裡會被影響 |
| bash logging / runtime instrument | Runtime 中間值 | 非預期分支路徑、條件判斷值 |
| 靜態讀 code | 靜態結構 | 以上都無法觀測到問題層時 |

如果問題發生層不確定，先用 bash logging 確認症狀出現的模組，再選精確工具。

---

## Instrumentation — 🎯 HUNT-id Tagging

所有診斷用工具（log 行、failing assertion、test probe）**必須帶 HUNT-id tag**。

- Tag 格式見 `references/hunt-case-template.md`
- `grep "🎯HUNT-[id]"` 一次找到所有診斷工具
- 找到根因後，**一次清除**所有帶 tag 的診斷工具，確認 build 仍通過

Log 二分法：每輪只加 2-3 個觀測點，不是 20 個。
```
第 1 輪：suspect 入口 / 中間 / 出口各一個觀測點 → 確認問題在哪個區段
第 2 輪：出問題的區段內再加 2-3 個觀測點 → 再收斂
第 3 輪：通常可定位到 5-10 行以內
```

---

## Before You Fix

修復前兩件事都要完成，缺一不可：

### 1. 呼叫鏈分析

- 直接呼叫者（LSP findReferences / graphify / code search）
- 這段 code 影響的業務場景
- 高風險點（最可能「改 A 壞 B」的地方）

### 2. 測試矩陣

針對要修改的邏輯，列出維度 × 邊界值的組合：
- 每個維度的邊界值都要覆蓋
- **unchanged 場景最容易漏**（版本號、時間戳、FK 可能需要同步）
- **multi-X 場景最容易出問題**（multi-org、multi-tenant、multi-item）

Build the matrix before entering any fix. A fix without a test matrix is a symptom patch.

---

## Confirm or Discard

每次只加**一個**最小化工具（一行 log、一個 failing assertion、或最小測試案例）。

執行後：
- 證據**支持假說** → 再找一個獨立證據交叉確認，再進入修復。
- 證據**反駁假說** → **完全丟棄假說**。不是修補，不是解釋。用剛學到的資訊重新定向。

A preserved-but-contradicted hypothesis produces a new bug. Discard completely.

---

## Bisect Mode

Activate when: 「以前能跑，現在壞了」或「更新後壞了」。

1. 找 `last-known-good`：用最近的 tag，不用日期或 raw SHA。(`git tag --sort=-version:refname | head -5`)
2. 在 bisect 開始前，定義 **pass/fail 測試指令**。指令必須可自動執行、產出明確 exit code。寫下來，每步重用同一個。
3. 執行：`git bisect start` → `git bisect bad`（當前）→ `git bisect good <tag>`。讓 bisect 引導，不跳步。
4. bisect 指出 commit 後：只讀那個 commit 的 diff，不讀周邊歷史。

---

## Hard Rules

| 條件 | 動作 |
|------|------|
| 修復後同症狀再現 | 停。假說未完成。重讀執行路徑，不再碰 code。 |
| 「先試試這個」出現 | 停。寫出假說再行動。 |
| 三次假說失敗 | 切換 Handoff 格式（見 Output）。 |
| Before You Fix 未完成就要修復 | 停。完成呼叫鏈分析和測試矩陣後再繼續。 |
| 外部工具失敗 | 先診斷原因（server 跑嗎？config 正確？），再換工具。 |
| Visual / 渲染 bug | 靜態分析優先（DevTools layers、stacking context），加 log 是第二步。 |

---

## Gotchas

| 情境 | 規則 |
|------|------|
| 多實體比對（multi-org / multi-tenant） | 用業務鍵（SEQ / CODE / NAME）比對，不用 ID。 |
| unchanged 項目的同步 | 版本號 / 時間戳 / FK 可能需要同步，即使「沒有變化」的項目。 |
| Clone 後繼承 ID | Clone 後覆蓋 PK 和 FK，不繼承來源的 ID。 |
| Stack trace 指向函式庫深處 | 往回走 3 個 frame 到自己的 code；bug 幾乎都在那裡。 |
| 平行 pipeline 某段顯示 RUNNING | 逐段隔離測試；每段正確不代表組合正確。 |

---

## Output

### 成功格式

```
根因：      [問題是什麼，file:line 或 component/query/condition]
修復：      [改了什麼，在哪裡]
確認方式：  [哪個證據或測試確認了修復]
測試矩陣：  [通過數 / 總數，迴歸測試位置]
迴歸守護：  [test file:line] 或 [無，理由]
```

狀態：**已解決** / **已解決（附帶條件說明）** / **受阻**

對於曾修過又再現的 bug，「已解決」的條件是：(1) 迴歸測試在舊 code 失敗、新 code 通過；(2) 測試在 project test suite 裡；(3) commit message 說明再現原因與防止方式。

### Handoff 格式（三次假說失敗後使用）

```
症狀：[原始錯誤，一句話]

已測試的假說：
1. [假說 1] → [測試方式] → [結果：因為...排除]
2. [假說 2] → ...
3. [假說 3] → ...

已蒐集的證據：[Log / stack trace / 觀測到的中間值 / 重現步驟 / 環境]
已排除的根因：[已消除的可能性]
尚不知道的事：[還不清楚的地方]
建議下一步：[下一個調查方向 / 需要的工具或權限]
```

狀態：**受阻**

---

狩獵完成後，建議在 `reference/` 下建立 hunt case 文件（格式見 `references/hunt-case-template.md`），記錄根因和修復過程供日後查閱。

---

## Core constraints

- Do not touch code before stating the root cause in one sentence.
- Before You Fix (impact analysis + test matrix) is mandatory before any fix.
- All diagnostic instrumentation must carry a HUNT-id tag; remove all after root cause is confirmed.
- Confirm or Discard: one instrument at a time; contradicted hypotheses are discarded completely, not patched.
- Three failed hypotheses triggers Handoff format, not another guess.
