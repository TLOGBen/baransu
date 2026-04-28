# Tasks: shared
**前置群組**：無

最內層共用層：schema 規範文件、gitignore、state.json 初始檔。後續所有 group 都依賴這層的契約。

---

## TASK-shared-01: 撰寫 telemetry.jsonl schema 規範文件

**需求追溯**：REQ-001、REQ-006 Scenario 3
**目標**：產一份權威 schema 文件，定義 telemetry.jsonl 每個 row 的 7 個欄位格式、enum 值、寫入時序、誰寫哪個欄位。後續所有元件都引用這份文件。
**驗收標準**：
- [ ] `plugins/baransu/skills/_shared/telemetry-schema.md`（或類似路徑）存在
- [ ] 文件含 7 欄位：`session_id` / `terminal_state` / `prompt_text` / `skill_outcome` / `commit_hash` / `diff_summary_redacted` / `attempt_history` 各自的型別、寫入者、寫入時機
- [ ] 含 1 條完整範例 row（可被 jq 解析的合法 JSON）
- [ ] 明寫 `terminal_state` 三個 enum：completed / aborted / interrupted

### 步驟

#### 撰寫 schema 文件
- [ ] 開新檔，先列 7 欄位表（型別 / 寫入者 / 寫入時機 / 範例值）
- [ ] 加一段「寫入時序」說明（UserPromptSubmit 先寫 session_id + prompt_text；PostToolUse 補 skill_outcome + commit_hash + diff_summary_redacted；終態由 PostToolUse 在 final tool 後寫；ctrl-c 時由補刀機制標 aborted）
- [ ] 加 `attempt_history` 子 schema（含 cluster_id / run_at / result）
- [ ] 加合法範例 row + jq 範例查詢

---

## TASK-shared-02: 撰寫 grade.jsonl + triage.jsonl schema 規範

**需求追溯**：REQ-002、REQ-003、REQ-006 Scenario 4
**目標**：定義 /grade 與 /triage 寫出的兩份 jsonl row 格式，鎖定 5 維欄位名與 equal-weight bootstrap 規格。
**驗收標準**：
- [ ] schema 文件含 grade.jsonl row：`session_id` / `dims`（9 子欄）/ `aggregate` / `quality`（4 enum）/ `weights`
- [ ] schema 文件含 triage.jsonl row：`cluster_id` / `member_session_ids` / `severity_dims`（9 子欄）/ `severity_aggregate` / `escalate`（3 enum: false / requires_human / daily_quota_exceeded）/ `evidence_bundle` / `attempt_count`
- [ ] 5 維 baransu-native 欄位命名固定：`outcome_quality` / `iteration_velocity` / `scope_blast` / `human_override_rate` / `failure_recurrence`
- [ ] equal-weight bootstrap 條款明寫：每維權重 = 1/5，tune trigger = 累積 ≥ 50 條 completed row
- [ ] 每維說明：`outcome_quality`（從 skill_outcome.exit_code + final_state 推：完成且綠燈為 high）、`iteration_velocity`（從 attempt_history 與 commit_hash 推：少回合即高速）、`scope_blast`（從 diff_summary_redacted 推：動到的檔案數 + path 風險度）、`human_override_rate`（從 skill_outcome.final_state 含 override 標記推）、`failure_recurrence`（同 cluster_id 在 attempt_history 內近 N 日累計失敗次數）

### 步驟

#### 撰寫 grade schema
- [ ] 列欄位表
- [ ] 列 quality enum 對應分數區間（excellent / good / acceptable / poor）
- [ ] 範例 row

#### 撰寫 triage schema
- [ ] 列欄位表
- [ ] 列 escalate enum 三種觸發條件
- [ ] evidence_bundle 子 schema（root_cause_guess + citations[]）
- [ ] 範例 row

#### Bootstrap 與 tune trigger 條款
- [ ] 明寫權重表（dim → 1/5）
- [ ] 明寫 tune trigger：「累積 ≥ 50 條 `terminal_state == completed` row 後 review 並 tune 一次」

---

## TASK-shared-03: `.claude/harness/` 加進 .gitignore + 建立目錄

**需求追溯**：REQ-001 Scenario 4、REQ-006 Scenario 6（EDGE-1）、INV-6
**目標**：保證 telemetry / grade / triage / state 檔不被 git 追蹤；提供結構基底讓後續 hook 直接寫入。
**驗收標準**：
- [ ] `.gitignore` 含 `.claude/harness/` 規則（與既有 `.claude/dev/`、`.claude/think/` 同層風格）
- [ ] `.claude/harness/` 目錄存在
- [ ] `git status` 在新建 `.claude/harness/test.jsonl` 後不出現該檔
- [ ] `.gitkeep` 或 README 一併處理（避免空目錄不入 commit）的決定有顯式處理

### 步驟

#### .gitignore 修改
- [ ] 讀現有 `.gitignore` 找到「Transient baransu workspace dirs」段落
- [ ] 在該段落附近加 `.claude/harness/` 條目（含一行註解說明「self-healing harness telemetry — local only」）

#### 建目錄與驗證
- [ ] `mkdir -p .claude/harness/`
- [ ] 跑 `touch .claude/harness/probe.jsonl && git status` 確認 untracked 不含 probe
- [ ] 清掉 probe.jsonl

---

## TASK-shared-04: state.json schema + 初始檔

**需求追溯**：REQ-004、INT-7
**目標**：定義 auto-fix 跨 run 狀態檔（daily push counter、reset 機制）。
**驗收標準**：
- [ ] schema 文件含 state.json 4 欄位：`daily_push_count` / `daily_push_date` / `last_grade_run_at` / `last_triage_run_at`
- [ ] 初始 state.json 已落到 `.claude/harness/state.json`（counter=0、date=今日）
- [ ] daily reset 條款明寫（`daily_push_date` ≠ today → reset counter 為 0）

### 步驟

- [ ] 撰寫 schema 文件章節（可併入 task-shared-01 的 schema 文件，分節即可）
- [ ] 寫 reset 演算法說明（pseudo-code 或敘述）
- [ ] 建立初始 `.claude/harness/state.json` 檔案內容
