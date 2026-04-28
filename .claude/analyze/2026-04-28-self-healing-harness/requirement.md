# Requirements

## REQ-001: Telemetry capture（兩 hook + 7 欄位 schema）

**描述**：當任何 baransu skill 執行時，UserPromptSubmit hook 與 PostToolUse hook 必須協同把該次 invocation 寫成完整 telemetry 條目，落到 `.claude/harness/telemetry.jsonl`。

### Scenarios

**Scenario 1: 完整 session 寫入 7 欄位**
- **Given** `~/.claude/settings.json` 已註冊 UserPromptSubmit + PostToolUse 兩個 hook，且 `.claude/harness/` 已存在
- **When** 使用者跑 `/baransu:think 「重構某模組」` 並等到 skill 結束
- **Then** `.claude/harness/telemetry.jsonl` 多出一條 row
- **And** 該 row 含 `session_id`（非空字串）、`terminal_state`（`completed`）、`prompt_text`（含 user 原句）、`skill_outcome`（含 skill 名 + final state）、`commit_hash`（git rev-parse HEAD）、`diff_summary_redacted`（list of `{path, +N, -N}`）、`attempt_history`（empty list 或現有 list）

**Scenario 2: ctrl-c 中斷的 session 標記為 aborted**
- **Given** 已註冊兩 hook，使用者在 skill 跑到一半按 ctrl-c
- **When** session 結束時 PostToolUse 來不及收到 final tool 結果
- **Then** 該 session 的 telemetry row（若 UserPromptSubmit 已寫過）`terminal_state` 標記為 `aborted` 或 `interrupted`
- **And** `skill_outcome` 欄位反映「中斷」狀態，不留空

**Scenario 3: 敏感路徑 redaction**
- **Given** 使用者跑 /dev 動了 `.env`、`config/secret.yaml`、`certs/server.pem` 三個檔案
- **When** PostToolUse hook 寫 telemetry 時計算 diff 摘要
- **Then** `diff_summary_redacted` 內這三條路徑整條跳過（不出現在 list）
- **And** 其他正常路徑的條目只有 `path` + `+N` + `-N`，沒有 diff 字面內容

**Scenario 4: hook 寫入路徑不被 git 追蹤**
- **Given** `.gitignore` 已加進 `.claude/harness/` 規則
- **When** 寫了若干筆 telemetry 後跑 `git status`
- **Then** `.claude/harness/telemetry.jsonl` 不出現在 untracked 或 modified 清單

**Scenario 5: prompt_text secret redaction**
- **Given** UserPromptSubmit hook 已掛上 secret-pattern redaction filter
- **When** user 送出 prompt 含字面密鑰，例如「我的 token 是 `glpat-abc123def456ghi789jkl012`，請幫我 debug」
- **Then** telemetry.jsonl 對應 row 的 `prompt_text` 把該字面值改寫為 `<REDACTED:gitlab_token>`（或對應分類標）
- **And** 5 條 redaction pattern（`(sk|glpat|ghp|gho|ghu|ghs|ghr|xox[baprs])-[A-Za-z0-9_-]{20,}`、`-----BEGIN .* PRIVATE KEY-----`、`AKIA[0-9A-Z]{16}`、PEM block 內容、`(token|key|secret|password)\s*[=:]\s*\S+`）任一命中皆觸發 mask
- **And** 一般文字（不命中 pattern）保持原樣

---

## REQ-002: Grade（5 維 baransu-native deterministic rubric + bootstrap）

**描述**：/grade 由 cron 排程觸發，對前一日 `terminal_state == completed` 的 telemetry 條目按 5 維 equal-weight rubric 打分，poor verdict 寫到 `.claude/harness/grade.jsonl`。

### Scenarios

**Scenario 1: bootstrap equal weight 打分**
- **Given** telemetry.jsonl 有 12 條 completed row + 5 條非 completed row
- **When** 執行 /grade
- **Then** grade.jsonl 只新增 12 個 row（每個 completed row 對應一個 verdict）
- **And** 每個 verdict 含 5 維分數（每維權重 1/5；維度名 `outcome_quality` / `iteration_velocity` / `scope_blast` / `human_override_rate` / `failure_recurrence`）+ 一個 aggregate score
- **And** 非 completed row 完全不出現在 grade.jsonl

**Scenario 2: poor 篩選正確**
- **Given** 12 個 verdict 中有 4 個 aggregate score < 預定 threshold（例如 0.5）
- **When** /grade 跑完
- **Then** 4 個 poor verdict 在 grade.jsonl 中標記 `quality: poor`
- **And** 其他 8 個標記 `quality: acceptable` 以上

**Scenario 3: tune trigger 觀察**
- **Given** telemetry.jsonl 已累積 50+ completed row
- **When** /grade 跑完當下
- **Then** /grade 額外輸出一條 `tune_review_due: true` 的訊號（log line 或 stdout 標記）
- **And** 該訊號讓人類知道可以 review 並調 rubric 權重了

---

## REQ-003: Triage（聚類 + 5 維 severity + investigator evidence bundle）

**描述**：/triage 讀 grade.jsonl 與 telemetry.jsonl，對 poor verdict 聚類後依 5 維 severity 排序產出 top cluster；對 top cluster 派 investigator subagent 收集證據並寫 `.claude/harness/triage.jsonl`。

### Scenarios

**Scenario 1: 聚類產出 top cluster**
- **Given** grade.jsonl 內 4 條 poor verdict，其中 3 條來自同一 skill (/dev)、1 條來自 /think
- **When** /triage 執行
- **Then** triage.jsonl 至少出現 1 個 cluster row，`cluster_id` 唯一
- **And** 該 cluster 含 5 維 severity 分數（`outcome_quality` / `iteration_velocity` / `scope_blast` / `human_override_rate` / `failure_recurrence`，與 grade dims 同名）
- **And** cluster 含其源頭 messageIds 清單

**Scenario 2: investigator subagent 產 evidence bundle**
- **Given** triage 產出 1 個 top cluster（severity 過閾值）
- **When** /triage 派 investigator-agent 處理該 cluster
- **Then** investigator agent 讀 git log / 對應 telemetry row / 相關 source file，回傳結構化 evidence bundle（含根因推論 + cited file paths）
- **And** evidence bundle 寫進 triage.jsonl 的對應 cluster row
- **And** investigator 過程中沒有任何 git ops（write / push / branch ops 為 0）

**Scenario 3: 不過 severity 閾值的 cluster 留在 trend log**
- **Given** 某 cluster 的 5 維 severity aggregate < 閾值
- **When** /triage 執行
- **Then** 該 cluster 寫進 trend section（仍在 triage.jsonl 但標 `escalate: false`）
- **And** 不派 investigator-agent

---

## REQ-004: Auto-fix（deterministic 模板 + 五條安全邊界）

**描述**：對 top cluster 的 evidence bundle，auto-fix 走 deterministic 模板填入 cluster_id + top-N evidence 條目後呼叫 /dev，產出修補；push 前過 5 條安全閘門（gitignore 已防、hook 已 redact、push denylist、attempt cap、daily quota）。

### Scenarios

**Scenario 1: fix prompt deterministic 模板**
- **Given** cluster_id = `cl-001`、evidence bundle 含 top-3 條目（root cause guess + 3 個 file:line citations）
- **When** auto-fix 呼叫 /dev
- **Then** /dev 收到的 prompt 文本嚴格符合預定模板格式（`{cluster_id}` 變數、`{top_N_evidence}` 變數固定位置、其餘文字字面相同）
- **And** prompt 完全不含 LLM-generated 自由 sentence（可由 diff 對 baseline 模板驗證）

**Scenario 2: push denylist abort**
- **Given** /dev 修了 `plugins/baransu/skills/dev/SKILL.md` 與 `marketplace.json`
- **When** auto-fix 準備 git push
- **Then** push 之前 `git diff --name-only HEAD~1` 命中 `marketplace.json`
- **And** push 動作 abort，cluster row 標 `requires_human`，不發到 GitLab

**Scenario 3: cross-run attempt cap**
- **Given** 同 cluster `cl-002` 在 telemetry 的 `attempt_history` 有 3 個 fail 記錄
- **When** /triage 該日再次抓出 `cl-002`
- **Then** auto-fix 跳過該 cluster（不呼叫 /dev、不 push）
- **And** cluster row 標 `escalate_human`

**Scenario 4: daily push hard cap**
- **Given** 當日已 push 5 次 auto-fix
- **When** 第 6 個 cluster 通過所有其他閘門到 push 步驟
- **Then** push abort
- **And** cluster row 標 `daily_quota_exceeded`、後續同日不再 push（隔日 reset）

**Scenario 5: gitignore + redaction 已生效（複合）**
- **Given** `.gitignore` 含 `.claude/harness/` 規則、hook 已掛 redaction filter
- **When** 跑 baransu skill 動了 `.env` 與 `src/main.py` 後 `git status`
- **Then** `.claude/harness/telemetry.jsonl` 不在 git status 輸出
- **And** telemetry row 的 `diff_summary_redacted` 不含 `.env` 條目，僅含 `src/main.py` 條目（path + +N/-N）

---

## REQ-005: Bridge（隔離 worktree + 歷史 prompt replay + statistical gate）

**描述**：手動呼叫 /bridge 時，從 telemetry.jsonl `terminal_state == completed` 條目撈 `prompt_text` 當歷史 corpus，在 `mktemp -d /tmp/baransu-bridge-XXX` 隔離 worktree 上跑兩個 skill 版本（v1 = main HEAD、v2 = 指定 branch）head-to-head，比較 score 差距判定 pass/fail。

### Scenarios

**Scenario 1: 正常 head-to-head 跑通**
- **Given** telemetry.jsonl 有 50+ completed row、目前 branch `feature/skill-v2-experiment` 修了 /think SKILL.md
- **When** 手動跑 `/bridge feature/skill-v2-experiment` 比較 /think v1 vs v2
- **Then** 在 `/tmp/baransu-bridge-XXX` 建出 isolated worktree
- **And** 主 repo working tree 在 /bridge 跑期間 + 結束後 `git status` 都沒有額外 untracked / modified 檔案
- **And** /bridge 對 50 個 prompt 跑兩遍打分，回傳 aggregate Δ

**Scenario 2: Δ ≥ 0.15 觸發 fail**
- **Given** v2 比 v1 平均 score 低 0.20
- **When** statistical gate 計算
- **Then** /bridge 回 `fail`、印 cohort 細節
- **And** 不自動 promote、不切流量

**Scenario 3: Δ < 0.15 觸發 pass**
- **Given** v2 比 v1 平均 score 持平或高
- **When** statistical gate 計算
- **Then** /bridge 回 `pass`、印 promote 建議

**Scenario 4: SIGINT 中斷時 worktree 清理**
- **Given** /bridge 跑到一半使用者按 ctrl-c
- **When** trap 觸發
- **Then** isolated worktree 被 `git worktree remove --force` + `rm -rf` 清掉
- **And** `git worktree list` 不見 `/tmp/baransu-bridge-*` 殘餘

**Scenario 5: R3 regression 偵測 demo**
- **Given** telemetry corpus ≥ 50 條、注入一個人工 regression（例如 v2 的 /think 故意讓 Stage A 第三輪不對焦就出 plan）
- **When** /bridge 跑該 v2 vs v1
- **Then** /bridge 對該 regression 觸發 `fail`（Δ ≥ 0.15）
- **And** 印出哪些 prompt 上表現掉最多（top-N 退化 prompt）

> 註：corpus 前置（≥ 50 條 completed row 或注入等量 fixture corpus）詳見 test.md E2E-4。

---

## REQ-006: Invariants（Cross-cutting，最後驗收用）

**描述**：實作完成後可由獨立檢查腳本驗證 6 條 KD invariants 仍然成立，不被任何 task 隱藏地破壞。

### Scenarios

**Scenario 1: hook 註冊位置正確**
- **Given** 全部 task 已完成
- **When** 檢查 `~/.claude/settings.json` 與 `plugins/baransu/.claude-plugin/plugin.json`
- **Then** settings.json 含 `UserPromptSubmit` 與 `PostToolUse` 兩個 hook 條目
- **And** plugin.json 不含 `hooks` 欄位（grep `\"hooks\"` 為 0 命中）

**Scenario 2: 總 skill 數正確**
- **Given** 全部 task 已完成
- **When** 列舉 `plugins/baransu/skills/*/SKILL.md`
- **Then** skill 目錄共 14 個（11 既有 + 3 新增 /grade /triage /bridge）
- **And** CLAUDE.md skill 表也是 14 列

**Scenario 3: telemetry schema 7 欄位齊全**
- **Given** 跑過至少 1 個 baransu skill
- **When** 檢查 `.claude/harness/telemetry.jsonl` 的最新一條 row
- **Then** 該 JSON 含 7 個 top-level key：`session_id`、`terminal_state`、`prompt_text`、`skill_outcome`、`commit_hash`、`diff_summary_redacted`、`attempt_history`

**Scenario 4: rubric weight bootstrap**
- **Given** /grade 已跑過至少 1 次
- **When** 檢查 /grade SKILL.md 或實作的 rubric 設定
- **Then** 5 維每維權重 = 1/5（或標記為 equal weight bootstrap 階段）
- **And** tune review trigger 鎖在「累積 ≥ 50 條 completed row」這個量化條件

**Scenario 5: auto-fix 不 touch 主 repo working tree**
- **Given** 一輪完整 cron auto-fix 跑完
- **When** 對比 cron 開始前 vs 結束後主 repo 的 `git status`
- **Then** 主 repo working tree 變化 = 空（所有 git ops 都發生在 isolated worktree）

**Scenario 6: 5 黑安全邊界齊全**
- **Given** 全部 task 已完成
- **When** 跑 invariants 檢查腳本
- **Then** 以下 5 條規則各自有對應 test 並 pass：gitignore 含 `.claude/harness/`、redaction filter 路徑清單正確、push denylist 路徑清單正確、attempt cap K=3 設定值、daily push quota = 5 設定值
