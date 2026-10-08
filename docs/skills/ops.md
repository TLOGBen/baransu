# 維運家族：ship · health · evolve · codex-skill-transfer

<img src="../images/family-ops.png" width="320" alt="維運家族概念圖">

> 收好每一輪、照顧工具本身：收工、體檢、磨 skill、兩個平台對齊。

[← 回文件索引](../README.md)

---

## `/ship`

Claude Code：`/baransu:ship`　Codex：`$baransu:ship`

**用途**　session 收尾：歸檔工作檔與 root 的 sealed 合約、commit、push、清理 worktree。

**什麼時候用**
- 一輪工作結束要收工。
- 觸發語：`/ship`、收工、上傳收尾、結束這輪。
- 參數：`[BRANCH]`——給了目標分支，就把目前分支合進去再 push 目標分支。

**步驟**
1. 偵測：沒有 git 的專案在搬任何檔案之前就直接失敗（否則歸檔的檔案沒有 commit 可錨定）。
2. 歸檔：`.claude/` 下的 baransu 工作目錄（`read`／`learn`／`draw`／`design` 的成品除外）與 root 的 sealed 合約，搬到 gitignored、只留本機的 `.claude/archived/`；只有名稱衝突時才加時間戳。
3. commit 前先在本機整合上游。
4. commit。
5. push 目前分支，或合併到目標分支後 push 目標分支。
6. 在 worktree 中執行且工作已確認在 origin 上：移除 worktree，並以 `git branch -D` 刪掉分支（push 後本機分支視為未合併，`-d` 一定失敗）。

**產出**　`.claude/archived/` 下的本機歸檔、有非歸檔變更時的一筆 commit、繁中收工報告（歸檔數、commit 訊息或「跳過」、上游整合結果、push 目標、worktree 清理狀態）。

**不適用**　寫文案 → `/write`；審查產出 → `/review`。`/ship` 只做收尾。

**非互動驅動**　`loop=assisted`。

---

## `/health`

Claude Code：`/baransu:health`　Codex：`$baransu:health`

**用途**　體檢專案的 agent 配置與 AI 可維護性：五層審計，預算姿態先行。

**什麼時候用**
- 懷疑 agent 不聽指令、配置漂移、hooks 沒生效、MCP 壞了、驗證缺失、程式碼在 AI coding 下逐漸腐化。
- 環境急診的預設分派：某個 skill 需要的 CLI／SDK 沒裝、command not found（預設修法＝官方一步全域安裝）。
- 觸發語：`/health`、健康檢查、配置體檢、檢查配置、AI 可維護性、檢查 claude、檢查 codex、配置對不對、健康度、AI coding 腐化、程式碼變爛、上下文混亂、驗證缺失、hooks 沒生效、MCP 壞了、環境問題、依賴缺失、SDK 沒裝、agents ignoring instructions、check config、audit config、health check、config drift、command not found。

**五層審計**　配置 → 指令 → 工具 → 驗證面 → 可維護性。先評估專案等級與預算姿態，只有深度審計才派 inspector 子代理（context／control／maintainability）。

**產出**　對話中的繁中體檢報告：依等級分級、兩條線（agent 配置風險、AI 可維護性風險）、依嚴重度排序（嚴重—立即修／結構性—儘快修／漸進—有空再修）。每個 finding 標出所在層、具體證據（file:line 或腳本輸出段）與可直接複製執行的指令；或給出乾淨證明加剩餘風險。不另存檔，非互動驅動時才另存 `.claude/health/report-{date}.md`。

**不適用**
- baransu 自身的結構驗證 → `scripts/verify-skills.py`
- 審單次模型輸出 → `/review`
- 取代 lint／typecheck

**非互動驅動**　`loop=assisted`。

---

## `/evolve`

Claude Code：`/baransu:evolve`　Codex：`$baransu:evolve`

**用途**　把既有 SKILL.md 對著固定標準一輪輪磨好，只保留確有改進的改動。

**什麼時候用**
- 想改善、評分或演化一份既有的 SKILL.md。
- 觸發語：`/evolve`、優化 skill、skill 評分、演化 skill、幫我改 skill、optimize skill、improve skill quality、evolve a skill。

**運作方式**　只能向前轉的棘輪：
- 固定 9 維評分標準；每輪只改一個變數。
- 先過結構閘，再看效果軸（real-exec 或 offline）。
- 三位全新的盲評 judge，嚴格進步才保留，否則還原快照。
- 雙軸評估（結構＋效果）與 held-out 驗證。
- 採納與否是 Authorization PAUSE，由使用者決定。

**產出**　`.claude/evolve/<slug>/` 演化包：`report.md`、`results.tsv`、`log.md`、`held-out.md`、收斂曲線與成果卡 `card.html`（零採納時可省略成果卡並在 `report.md` 註記）。

**不適用**
- 從零撰寫新的 SKILL.md → 直接撰寫，那是 authoring 不是演化
- 決定一個 skill 該不該存在 → `/think` 存廢判決（Kill / Keep / Pivot）

**非互動驅動**　`loop=drivable`。

---

## `/codex-skill-transfer`

Claude Code：`/baransu:codex-skill-transfer`　Codex：`$baransu:codex-skill-transfer`

**用途**　Claude 版與 Codex 版並列手動維護時的移植對照表＋對齊檢查清單；另附選用的草稿腳本。

**什麼時候用**
- 一份 skill、plugin 或 marketplace 同時有 Claude Code 與 OpenAI Codex 兩份手動維護的版本，要檢查是否對齊或要移植。
- Claude→Codex 欄位對照問題：`disable-model-invocation`、context fork、`ARGUMENTS`、`plugin.json` 等。
- 觸發語：轉成 codex 版、給 codex 用、port to codex、檢查 codex 版。

**四種模式**

| 模式 | 做什麼 |
|---|---|
| Checklist（預設） | 唯讀；輸入一對 Claude／Codex 目錄，輸出落差報告 |
| Port by hand | 依要求手動修改 Codex 版，並與 Claude 版一起升版 |
| Generate（選用） | `transfer.py` 只寫到暫存目錄，不得覆蓋手動維護的 Codex 版 |
| Reference question | 回答對照問題 |

**檢查清單涵蓋**　skill 欄位（Codex 只讀 `name`／`description`／`metadata.short-description`）、內文路徑變數改相對路徑、`$plugin:skill` 呼叫、工具改寫、額外資料夾（如 `templates/`）一律保留；plugin manifest、bundled agent、hooks；Claude 專用元件（mods、monitors、userConfig 等）；marketplace 讀取順序；版本與快取。對照基準：Claude Code 2.1.293、Codex CLI 0.161.0（2026-10-08）；推論或官方未公布的項目會明確標註。

**產出**　繁中對照報告（一致／需修正／刻意省略／降級風險／待查），以及（依模式）手動修改後的 Codex 版或暫存目錄中的草稿。

**不適用**
- 反向移植（Codex→Claude）
- 沒有 Claude 對應版本、全新撰寫的 Codex skill

**存續條款**　這是第 14 個 skill 的附帶條件：若選用遙測連續三個月零使用，就退役並把上限收回 13。

**非互動驅動**　`loop=assisted`。
