# 驗證家族：review · hunt

<img src="../images/family-verify.png" width="320" alt="驗證家族概念圖">

> 換一雙乾淨的眼睛看，拿證據說話；乾淨的結果也是有效的結果。

兩個 skill 分工：`/review` 獨立重驗任何產出、`/hunt` 從症狀追到根因。中頻段的收尾就是 `/review`——8.0.0 起沒有合約、沒有封緘。

[← 回文件索引](../README.md)

---

## `/review`

Claude Code：`/baransu:review`　Codex：`$baransu:review`

**用途**　派一個乾淨 context 的 verifier 獨立重驗任何產出，視角只為不同的實質風險才加；沒有驗收條文時問三題——做到了沒、多做了什麼、做小了沒；不改目標；乾淨的 review 也是有效的 review。

**什麼時候用**
- 任何模型產出之後——程式、計畫、主張——想要獨立重驗。
- 目標必須具體：一個產物、一段 diff，或直接引用的一句主張。
- 觸發語：看一下、看看、幫我看、check 一下、review 一下、take a look at X。

**運作方式**　先釘住目標與要回答的問題 → 一屏以內的 diff 或一句主張走快速路徑（一個 verifier、既有測試、不派視角）→ 派一個窄 context 的 verifier → 只有遇到不同的、會造成後果的風險時才加派視角 agent（architecture／quality／security／style／domain reviewer）→ canary 與 fresh inputs 兩個儀器依固定觸發實跑 → 判讀證據（只有真的跑過的才算發現）→ 報告。從頭到尾不修改目標。

**產出**
- 繁中 review 報告：檢查範圍、每個 finding 的位置／觸發條件／後果／證據、三題各一行（做到了／多做了／做小了）、獨立性聲明、剩餘限制；結尾判定由印在報告裡的規則算出——PROVEN／PARTLY PROVEN／NOT PROVEN——再加「若只能改一處」。
- 零 finding 加上明確範圍，就是完整結果。
- 需要保存時寫到 `.claude/review/<slug>.md`（`/ship` 會歸檔）。

**不適用**
- 審「使用者專案」的 agent 配置與 AI 可維護性 → `/health`
- 找根因 → `/hunt`

**非互動驅動**　`loop=drivable`。

---

## `/hunt`

Claude Code：`/baransu:hunt`　Codex：`$baransu:hunt`

**用途**　從症狀追到根因：選對觀測層、log 二分法定位，指到 file:line 才動手修。

**什麼時候用**
- 有 bug、報錯、崩潰，或「為什麼失敗」。
- 觸發語：排查、查查、查 bug、追問題、查問題、找 bug、報錯、崩潰、狩獵、定位根因、bisect、為什麼失敗、debug、what's wrong、not working、why broken、fix error、hunt the bug。

**運作方式**
- 先挑對觀測工具：playwright、MCP db、LSP、logs、靜態分析。
- 靜態讀碼先開入口追控制流再 grep 名字，先找資料再找誰碰它；每句主張給 file:line 或說「不知道」。
- 以 `🎯HUNT-id` 標記臨時探針，確認或排除每個假設後才碰程式；確認後探針全部移除。
- 修之前先做呼叫鏈分析與測試矩陣；修復跨多檔時切片，每片實作 → `/review`。
- 特殊模式：Fast Path（瑣碎 bug）、Scope Blast、Bisect（版本對時第一批假說從 delta 來）、Repeated Regression；無法在本機重現時改用回報者探針。
- 三個假設都失敗時改出交接報告，不硬修。

**產出**
- 繁中成功報告（根因／修復／確認方式／測試矩陣／迴歸守護）或交接報告，狀態為 已解決／已解決（附帶條件說明）／受阻。
- 案件檔 `.claude/hunt-report/HUNT-YYYY-NNN.md`。

**不適用**
- 主觀的 UI 品味問題 → `/ui`
- 「值不值得修」的價值判斷 → `/think` 存廢判決（Kill / Keep / Pivot）

**非互動驅動**　`loop=assisted`。
