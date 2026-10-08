# 驗證家族：seal · review · hunt

<img src="../images/family-verify.png" width="320" alt="驗證家族概念圖">

> 換一雙乾淨的眼睛看，拿證據說話；乾淨的結果也是有效的結果。

三個 skill 分工：`/seal` 對著合約收工、`/review` 獨立重驗任何產出、`/hunt` 從症狀追到根因。

[← 回文件索引](../README.md)

---

## `/seal`

Claude Code：`/baransu:seal`　Codex：`$baransu:seal`

**用途**　中頻段收工封緘：派遣乾淨 context 的 verify-only seal-agent 跑五點驗收（逐條對約、掃未釘表面、跨介面一致、常數逐字比對、突變抽查），findings 回主 session 修＋補釘死測試，複驗上限 2，全清才在合約蓋 sealed 標記。

**什麼時候用**
- `/contract` 立約的任務實作完成後，收尾驗收。
- 觸發語：`/seal`、封緘、收尾驗收、驗收剛做完的、seal it。
- 參數：`[CONTRACT.md 路徑 | base ref | 不給 = 尚未 commit 的 diff]`

**運作方式**（主 session 是調度者）
1. 組裝驗證 payload、先跑一次 baseline 測試。
2. 派遣 seal-agent 在乾淨 context 執行五點：

| # | 檢查 |
|---|---|
| 1 | 逐條對約（criteria audit） |
| 2 | 掃描沒被釘住的表面 |
| 3 | 跨介面一致 |
| 4 | 常數逐字比對 |
| 5 | 突變抽查（mutation spot-check） |

3. seal-agent 只回報、不修；findings 回到主 session 修正，每個修正附一條釘死測試並在 session 內跑綠。
4. 複驗上限 2 次；派遣前後比對指紋，確認探針沒有殘留。
5. 全清才在 `CONTRACT.md` 第 2 行蓋 sealed 標記。

**產出**
- 對話中的繁中封緘報告：五點結果＋修正清單＋突變抽查記錄。
- 修正落在工作目錄，附釘死測試。
- 一行 JSON 證據寫到 `~/.claude/baransu/telemetry/{project}/seal-log-{YYYY-MM}.jsonl`（只由主 session 寫）。seal-guard hook 靠這筆記錄判斷有沒有封緘過，少了會在 session 結束時誤擋。

**不適用**
- 跨視角獨立重驗任何模型產出 → `/review`
- 開工前釘條文 → `/contract`

**非互動驅動**　`loop=drivable`。

### seal-guard hook

隨 plugin 生效，預設阻擋。session 結束（Stop 事件）時若偵測到未 `/seal` 的 user-facing 變更，會擋下並提示補 seal。

- 降級：`SEAL_GUARD=log`（只記錄）或 `SEAL_GUARD=off`。
- 遙測集中在 `~/.claude/baransu/telemetry/{專案}/{類型}-{YYYY-MM}.jsonl`，每月回看誤擋率；過高就降回 log 預設（可證偽條款）。
- 實作：`plugins/baransu/hooks/seal-guard.sh` 與 `seal-guard.ps1`（Windows；必須保留 UTF-8 BOM）。

---

## `/review`

Claude Code：`/baransu:review`　Codex：`$baransu:review`

**用途**　派一個乾淨 context 的 verifier 獨立重驗任何產出，視角只為不同的實質風險才加；不改目標；乾淨的 review 也是有效的 review。

**什麼時候用**
- 任何模型產出之後——程式、計畫、主張——想要獨立重驗。
- 目標必須具體：一個產物、一段 diff，或直接引用的一句主張。
- 觸發語：看一下、看看、幫我看、check 一下、review 一下、take a look at X。

**運作方式**　先釘住目標與要回答的問題 → 派一個窄 context 的 verifier → 只有遇到不同的、會造成後果的風險時才加派視角 agent（architecture／quality／security／style／domain reviewer）→ 判讀證據 → 報告。從頭到尾不修改目標。

**產出**
- 繁中 review 報告：檢查範圍、每個 finding 的位置／觸發條件／後果／證據、獨立性聲明、剩餘限制。
- 零 finding 加上明確範圍，就是完整結果。
- 需要保存時寫到 `.claude/review/<slug>.md`（`/ship` 會歸檔）。

**不適用**
- 審「使用者專案」的 agent 配置與 AI 可維護性 → `/health`
- 封緘合約任務 → `/seal`

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
- 以 `🎯HUNT-id` 標記臨時探針，確認或排除每個假設後才碰程式；確認後探針全部移除。
- 修之前先做呼叫鏈分析與測試矩陣。
- 特殊模式：Fast Path（瑣碎 bug）、Scope Blast、Bisect、Repeated Regression；無法在本機重現時改用回報者探針。
- 三個假設都失敗時改出交接報告，不硬修。

**產出**
- 繁中成功報告（根因／修復／確認方式／測試矩陣／迴歸守護）或交接報告，狀態為 已解決／已解決（附帶條件說明）／受阻。
- 案件檔 `.claude/hunt-report/HUNT-YYYY-NNN.md`。

**不適用**
- 主觀的 UI 品味問題 → `/ui`
- 「值不值得修」的價值判斷 → `/think` 存廢判決（Kill / Keep / Pivot）

**非互動驅動**　`loop=assisted`。
