# 獨立審核報告 — `/baransu:review` 5-section 計畫

**審核對象**：`fixtures/review_plan.md`（已經 /baransu:think 走完並由使用者 Option 1 批准）
**審核角度**：乾淨視角、獨立驗證。聚焦三件事 — 內部矛盾、過度工程、偽裝成已解決的 unknown。
**審核者立場**：預設 Claude，不套用任何 skill。以文本為唯一證據來源。
**裁決語氣**：嚴格。已批准不代表無懈可擊；既然使用者明確要求再驗一次，就從最不友善的視角讀。

---

## 總體裁決

**CONDITIONAL GO — 需修正後再進設計**。

計畫方向合理、Not-building 段切得乾淨，但存在 **3 處實質內部矛盾**、**4 處偽裝成已解決的 unknown**、以及 **至少 2 處未自證的複雜度**。其中有 2 個屬於「動設計前必須先釐清、否則會在 SKILL.md 撰寫階段爆出來」的等級，應該打回去補，而不是帶著進 Eidos。

以下分三大類逐項列出，附嚴重度（🔴 Critical / 🟠 High / 🟡 Medium / ⚪ FYI）與修正建議。

---

## 一、內部矛盾（計畫裡兩段話彼此打架）

### 🔴 矛盾 1：「純 orchestrator，不擔任 reviewer」與「自動修復 level 1」

Key decisions #1 說：「Skill 本體是純 orchestrator / 任務分析師，不擔任 reviewer：主 SKILL.md 不寫任何『該找什麼問題』的 rubric，只寫派遣邏輯。」

但 Building #5 + Key decisions #6 說：Skill 會「執行第一級自動修復（僅限 formatter / imports / typo / dead import）」、「落檔直接改」。

**衝突點**：
- 要判斷某個 diff「是 formatter 修正 vs. 邏輯變更」、「是 typo vs. API 名稱更改」、「是 dead import vs. 被反射用到的 import」，本身就是 reviewer 級的判斷。這個判斷要寫在哪？
  - 如果寫在 SKILL.md → 直接破壞「主 SKILL.md 不寫 rubric」。
  - 如果寫在三個 perspective agent 檔 → 但 agent 在 Task context 中只輸出建議，不執行 Edit；執行自動修復的是 orchestrator，orchestrator 需要自己帶判斷邏輯。
  - 如果委派第四個「fixer agent」→ 計畫裡沒有這個角色，且會再增加複雜度。

**這不是小矛盾**：它直接決定 SKILL.md 的結構。進 Eidos 設計時，Daedalus 遇到這題會卡住。

**建議修正**：三選一 ——
1. 拿掉自動修復（最乾淨，讓 review 就是 review，修復是後續動作）。
2. 把自動修復外包給 perspective agent 之一（例：quality-reviewer 的禁忌裡改成「只提出建議，但對 format/import/typo/dead-import 類 agent 可直接回傳 patch 並由 orchestrator 套用」）。
3. 承認 SKILL.md 會有「fix-safety rubric」這小段，且明確將它從「review rubric」中切開。

**在本計畫裡，這題被當作已經解決。它沒有。**

---

### 🟠 矛盾 2：Unknown 段列出「v0.2.0 vs v0.1.1」，但 Building 段已經寫死 v0.2.0

Building 段明列：「`plugins/baransu/.claude-plugin/plugin.json` 版本 bump 到 `0.2.0`」。

Unknown 段第 3 條：「v0.2.0 vs v0.1.1 的語意版本決策。」

**衝突點**：要嘛是 Unknown，要嘛是 Decision。不能同時。這透露一個訊號 —— Stage F 產出時，「還沒想清楚」被當作「已經決定」塞進 Building 段，又在 Unknown 段暗藏了回馬槍。這是「偽裝成已解決的 unknown」的標準樣態。

**建議修正**：
- 如果真的還沒決定，從 Building 段移除版本號，改寫「版本 bump（具體號碼依 Unknown #3 決定）」。
- 如果 0.2.0 是決策，從 Unknown 段刪掉那一條，並補理由（新增 skill + 新增 agents 檔 → minor bump）。

小事，但影響整個計畫的可信度基線 —— 既然這題是「已解決」和「未解決」可以同時存在的，審核者就有理由懷疑其他項目。

---

### 🟡 矛盾 3：「不做 pipeline gate」vs. 「執行第一級自動修復」

Not-building 宣稱「不做 pipeline gate：不自動在任何 skill 宣告 done 前插入」。但 Building #6 說「未偵測到 e2e 跑過 → verdict 強制降為 INCOMPLETE」。

**衝突點**：INCOMPLETE verdict 對使用者而言，在行為上近似「阻擋你宣告 done」。語意上它是「建議」，但實質效果是 soft gate。這不違反 Not-building 字面，但違反其精神。

**嚴重度較低**，因為設計意圖（只施壓、不強制）是可接受的邊界，但文件應明確寫出「INCOMPLETE 不代表回拒使用者已批准的動作，使用者仍可覆寫」。

**建議修正**：Not-building 補一句「INCOMPLETE 僅為 advisory verdict，使用者可忽略繼續」，或改寫 Building #6 為「標記並提醒，不改動 verdict 等級」。

---

## 二、偽裝成已解決的 Unknown（Unknown 段之外的隱藏未知）

這類最危險 —— Unknown 段只列 3 項，但計畫裡還有至少 4 個實質未定義的決策點。

### 🔴 隱藏 unknown A：「激活規則 = 目標屬性表，非關鍵詞匹配」的實際機制

Key decisions #3 把這個寫成已決策。但計畫沒回答：
- 屬性表有哪些欄位？（檔數？總行數？副檔名？是否含 markdown？是否為 plan 格式？）
- 「對 /think 輸出這種非 code target 也能正確派遣」—— 怎麼派？派給誰？三個 agent 都是針對 code 設計的（architecture / quality / security），plan 型 target 該套哪一個？還是新增一個？
- 「決定派遣 1~3 個」—— 1 個的門檻？2 個的門檻？3 個的門檻？

**這整段被寫得像已解決，但其實是設計的核心**。送進 Eidos 時會立刻要求補全。

**建議修正**：
- 拆出一張最小屬性表（至少 3 欄：target 型別、行數/容量、是否含 code）。
- 定義每個 agent 的觸發條件（例：architecture 觸發於 `type ∈ {plan, design-doc, diff >200L}`）。
- 或承認「激活規則細則」是第 4 個 Unknown。

---

### 🔴 隱藏 unknown B：對抗性測試的觸發門檻本身就需要 rubric

Key decisions #4：「對抗性測試只在觸發門檻時跑（>100 行 code，或 >3 decision points in plan，或跨層級變更）。」

- 「>3 decision points in plan」—— 怎麼算 decision point？誰來數？如果 orchestrator 數，它需要一個 rubric（又回到矛盾 1）；如果交給第一輪 perspective agent 數，則觸發順序變成「先跑 agent → 再判斷要不要跑對抗」，這改變了計畫裡暗示的 stage 順序。
- 「跨層級變更」—— 層級指什麼？plugin/skill/agent？還是 module/function？定義不存在。

**建議修正**：把這個當作第 2 個明列 Unknown，或把 decision-point 計算器規則寫進 plan（即便粗略）。

---

### 🟠 隱藏 unknown C：「偵測 e2e 跑過」的偵測機制

Building #6 說「若 target 為程式變更，未偵測到 e2e 跑過」。怎麼偵測？
- 讀 CI log？—— skill 跑在本地，不一定有 CI 存取權。
- 讀 git commit message？—— 不可靠。
- 讀 test coverage file？—— target repo 不一定有。
- 問使用者？—— 違反 Not-building 的「不跑 e2e」精神的反面：變成每次都要 AskUserQuestion「你跑過 e2e 嗎」。

**這是偽裝成已解決的 unknown 的經典樣態**：給了一個動詞（「偵測」）卻沒給機制。

**建議修正**：明確寫「偵測 = 詢問使用者 + 檢查 .agent-workspace/ 最近的 test log 檔案」之類的 concrete 規則，或把這項推遲到 v0.3。

---

### 🟡 隱藏 unknown D：AskUserQuestion 批次打包確認的 UI 契約

Key decisions #5：「四級 triage 的『打包確認』批次彈 AskUserQuestion，一次一批，避免逐題騷擾。」

AskUserQuestion 工具本身對單次 options 數量有實作上限（依 harness 而定，一般不超過 10 選項）。若一批有 15 項「大概對的」修正，機制怎麼處理？
- 分批？（那就不是「一次一批」）
- 合併？（怎麼合併語意不同的建議？）
- 用 multi-select 還是逐項 yes/no？

**建議修正**：補一段 UI contract — 每批上限、超出時的分頁策略、合併 vs 逐項的選擇。

---

## 三、過度工程 / 複雜度未自證

### 🟠 複雜度 E：7 階段 + 3 agents + 對抗輪 + triage + auto-fix + report 真的比 3x 單 subagent 更有價值嗎？

計畫在 Approach 段用「隔離思考、perspective 切分」打掉極簡方案。但：
- 「隔離思考」只需要獨立 Task context。一個 reviewer subagent 跑 3 次（3 個不同 prompt）也能達成。
- 「perspective 切分」—— 三個獨立 agent 檔 vs. 同一個 agent 檔 + 3 份 prompt 模板，在隔離性上差異微弱，檔案管理成本卻顯著不同（3 檔 vs 1 檔）。
- 三個 agent 檔共用的「通用原則」段 10~15 bullets（Unknown #1）—— 若三檔各 10 條且多數重複，這就是複製貼上的重量級結構。

**計畫用「違反核心理念」一句帶過極簡方案，但沒有用證據反駁**。「複雜度需自證」的原則在這裡沒有實踐。

**建議修正**：在 Approach 段補一段具體理由，說明為何三個獨立 agent 檔比「一個 agent + 三份 perspective prompt」值得付出 3x 維護成本。若補不出，退回單 agent 方案。

---

### 🟡 複雜度 F：agent 檔案名本身就是人設

Key decisions #2：「三個 perspective agent 檔...明禁人設」。

但檔名是 `architecture-reviewer.md` / `quality-reviewer.md` / `security-reviewer.md`。這些字串本身就是角色標籤，模型在讀取時會把「你是這個檔案的主角」當作 implicit persona，即便內文寫「禁人設」。

這不是致命問題，但「明禁人設」的自信有點過頭。更誠實的寫法是「弱人設、強 rubric」。

**建議修正**：Key decisions #2 改寫為「以視角/目標/原則/禁忌取代傳統『你是 XX 工程師』敘述，接受檔名本身仍構成弱人設」。

---

### ⚪ 複雜度 G：審 /think 輸出的遞迴問題

Approach 段「已接受的邊界」承認：「審 /think 輸出時陷入遞迴靠 SKILL.md 明文規則禁止 —— 無法 100% 防止某個 agent 在自由文字中暗示。」

這個誠實承認很好。但既然 `/baransu:review` 的一個明確 use case 就是審 /think 的計畫（本次 eval 就是這個情境），這個邊界應該被提升為 First-class 設計考量，而不是擱在 Approach 末段。

**建議修正**：把「審 plan-target 時如何防遞迴」從 Unknown #2 拉出來，寫成 Key decisions 的新一條，哪怕只是「在 agent 檔的禁忌段明寫『不得呼叫 /think、不得要求使用者重跑 /think』」。

---

## 四、正面評價（為求平衡）

- **Not-building 段品質很高**：7 條明確的負面清單，邊界乾淨，減少後續爭議面積。
- **不支援 `--auto` 模式**的決定與 skill 的審查性質一致，方向正確。
- **不做 review-of-review**避免了無限遞迴的顯性陷阱。
- **對抗性六角度**的設計是有想法的（雖然觸發門檻不清楚）。
- **版本 bump 意識**（記得 plugin.json 版本推進）顯示對 plugin 機制的理解。

---

## 五、建議進度

| 項目 | 行動 |
|---|---|
| 🔴 矛盾 1（純 orchestrator vs. auto-fix） | **必修**。三選一，寫回計畫。 |
| 🔴 隱藏 unknown A（激活規則細節） | **必修**。補最小屬性表或列為明列 Unknown。 |
| 🔴 隱藏 unknown B（對抗觸發門檻） | **必修**。補 decision-point 計算規則。 |
| 🟠 矛盾 2（版本號） | 應修。改 Building 或刪 Unknown #3。 |
| 🟠 隱藏 unknown C（e2e 偵測機制） | 應修。給具體方法或推遲。 |
| 🟠 複雜度 E（三 agent 檔 vs. 單 agent） | 應修。在 Approach 段補反駁極簡方案的實證。 |
| 🟡 矛盾 3（INCOMPLETE 是否為 soft gate） | 可修。補一句 advisory 聲明。 |
| 🟡 隱藏 unknown D（AskUserQuestion 批次） | 可修。補 UI contract。 |
| 🟡 複雜度 F（檔名即人設） | 可修。改寫自信表述。 |
| ⚪ 複雜度 G（審 /think 遞迴） | FYI。升格為 Key decisions 更好。 |

**最小可進設計門檻**：修掉 3 個 🔴。其餘可在 Eidos 階段補齊，但建議帶著已修過的計畫進去，而不是讓 Daedalus 邊設計邊發現矛盾。

---

## 六、給使用者的一句話

> 計畫方向對、Not-building 段寫得好，但「純 orchestrator」與「自動修復」的矛盾、以及激活規則/對抗門檻/e2e 偵測這三個被當作已解決的 unknown，合起來足以讓 Eidos 階段反覆回打。送回補強比帶瑕疵進設計便宜。

— 獨立審核者（預設 Claude，無 skill 介入）
