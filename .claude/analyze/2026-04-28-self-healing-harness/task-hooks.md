# Tasks: hooks
**前置群組**：shared

兩個 user-level hook + 註冊機制。資料擷取的源頭。

---

## TASK-hooks-01: 實作 UserPromptSubmit hook（含 secret redaction）

**需求追溯**：REQ-001 Scenario 1、Scenario 5（prompt redaction）
**目標**：在 user 送出 prompt 那一刻 append 一條 telemetry row（含 `session_id` + 已 redact 的 `prompt_text` + 預設 `terminal_state: in_progress`）。寫入前對 prompt 跑 secret-pattern redaction，避免 user 貼進的 token / key 永久落地。
**驗收標準**：
- [ ] 有可執行的 hook script（路徑與 ~/.claude/settings.json 一致；語言可選 shell / python）
- [ ] script 收到 stdin（hook payload）後正確抽 prompt 文本與 session id
- [ ] **secret-pattern redaction filter 已實作**，至少 5 條 pattern 命中後改寫為 `<REDACTED:type>`（例如 `<REDACTED:gitlab_token>`）
- [ ] 寫入 `.claude/harness/telemetry.jsonl` 為合法 JSON（jq 可解）
- [ ] 不阻擋 user 主流程（hook exit 0 / 失敗也不影響 prompt 送達）
- [ ] 走 `flock(2)` 持有 `.claude/harness/.telemetry.lock`（遵守 design.md「Telemetry mutation contract」並發保護）

### 步驟

#### 設計 script 介面
- [ ] 確認 Claude Code UserPromptSubmit hook payload schema（透過 docs / 既有 plugin 範例 / 實測）
- [ ] 決定 script 路徑（建議放 `plugins/baransu/hooks/user-prompt-submit.{sh|py}`）

#### 實作 redaction filter
- [ ] 預編譯 5 條 regex pattern：
  - GitLab/GitHub/Slack/OpenAI/Stripe 類 token：`(sk|glpat|ghp|gho|ghu|ghs|ghr|xox[baprs])-[A-Za-z0-9_-]{20,}`
  - PEM private key block：`-----BEGIN [A-Z ]+ PRIVATE KEY-----[\s\S]*?-----END [A-Z ]+ PRIVATE KEY-----`
  - AWS access key：`AKIA[0-9A-Z]{16}`
  - 通用 secret 名值：`(?i)(token|key|secret|password|api[_-]?key)\s*[=:]\s*\S+`
  - PEM 內容（fallback，避免上 pattern 漏）：`-----BEGIN .*-----`
- [ ] 命中改寫：`<REDACTED:{pattern_class}>`（例 `<REDACTED:gitlab_token>` / `<REDACTED:private_key>` / `<REDACTED:aws_key>` / `<REDACTED:secret_kv>`）
- [ ] 不影響其他文本

#### 實作 hook 主體
- [ ] 讀 stdin / 環境變數抓 prompt 與 session id
- [ ] 對 prompt 跑 redaction filter
- [ ] 組 row JSON（含 redacted `prompt_text`、預設 `terminal_state: in_progress`、`attempt_history: []`、`commit_hash` 留空待 PostToolUse 補）
- [ ] 持 flock + atomic write（讀全檔 → modify in-memory → temp file → atomic rename）
- [ ] 失敗 path：log stderr + exit 0（不阻擋）

#### 單元測試
- [ ] 測試 happy path：餵 mock payload → 檔案多一行合法 JSON
- [ ] 測試 disk-full / permission denied：script 不 crash，exit 0
- [ ] **redaction 5 條 pattern 各自正例 + 一條負例**（不命中 pattern 的純文字保持原樣）
- [ ] 並發測試：同時 fork 100 個 hook → 最終仍 100 條合法 jsonl 行、無 partial write

---

## TASK-hooks-02: 實作 PostToolUse hook（含 redaction）

**需求追溯**：REQ-001 Scenario 1、Scenario 3、REQ-006 Scenario 6（EDGE-2）
**目標**：skill 跑完後 append `skill_outcome` + `commit_hash` + `diff_summary_redacted` 到對應 telemetry row（或產一條完整 row 若 UserPromptSubmit 未先寫）。Redaction 過濾敏感路徑。
**驗收標準**：
- [ ] hook script 存在（與 settings.json 設定一致）
- [ ] 可正確算 `commit_hash`（git rev-parse HEAD）與 `diff_summary` (git diff name-status with +N -N)
- [ ] redaction filter 跳過：`.env*` / `*secret*` / `*credential*` / `*.pem` / `*.key`
- [ ] 其他路徑只記 `{path, plus, minus}`，**不記 diff 字面**
- [ ] 對應到 UserPromptSubmit 已寫的 row 時，更新而非新增（或採 append + merge 策略，需明確）

### 步驟

#### 設計
- [ ] 決定「更新 vs append + 後續 merge」策略；若採 append，記錄 row 對齊規則（用 session_id 做 join key）
- [ ] redaction filter 採 glob 還是 regex；列 5 條規則的具體 pattern

#### 實作
- [ ] 計算 commit_hash + diff
- [ ] 跑 redaction filter
- [ ] 序列化 `diff_summary_redacted` 並 append / merge
- [ ] **terminal_state CAS guard**（design.md「Telemetry mutation contract」單調規則）：寫 `terminal_state=completed` 前先 read 對應 row 當前值；只在 `in_progress` 才升 `completed`；若已是 `aborted` / `interrupted`，僅 merge 非 state 欄位（commit_hash / diff_summary_redacted / skill_outcome），不可改 terminal_state
- [ ] 走 flock + atomic rename（同 task-hooks-01 規格）

#### 單元測試
- [ ] EDGE-2 測試：餵 5 條敏感路徑 + 1 條正常路徑 → output 只剩正常路徑
- [ ] commit_hash 在不同 git state（dirty / clean / detached HEAD）都能算
- [ ] redaction 不影響 +N/-N 數字準確度
- [ ] INT-1 配對測試：模擬 UserPromptSubmit 先寫 → PostToolUse 再寫 → 最終 telemetry.jsonl 對該 session_id 唯一一條 row、7 欄齊全（jq 驗證）
- [ ] **CAS guard 測試（Q-F1 ordering B）**：模擬 row 已是 `aborted`（Stop hook 先觸發）→ PostToolUse 寫入 → terminal_state 仍是 `aborted`、其他欄位（commit_hash / diff / outcome）正常 merge

---

## TASK-hooks-03: terminal_state 標記機制（採方案 c：Stop hook + grade-collector staleness check 並用）

**需求追溯**：REQ-001 Scenario 2、INT-2
**目標**：保證 ctrl-c / 異常終止的 session 也能被標記為 `aborted`/`interrupted`，不留 in_progress 殘餘干擾 /grade。spec 階段已收斂到方案 (c) — 兩條保險並用。
**驗收標準**：
- [ ] Stop hook 已實作並註冊（在 task-hooks-04 一起寫進 settings.json）
- [ ] Stop hook 在 session end 觸發，找對應 session_id 仍 `in_progress` 的 row 標 `aborted`
- [ ] grade-collector script 加 staleness check：超過 24h 仍 `in_progress` 的 row 標 `interrupted`（防 Stop hook 漏掛或進程 SIGKILL 沒走 hook）
- [ ] INT-2 模擬步驟可重現：用 `kill -SIGINT` 中斷、讀 telemetry → row 在數秒內被 Stop hook 標 `aborted`；用 `kill -SIGKILL` + 等 24h（測試時調短 threshold）→ 隔日 /grade 標 `interrupted`

### 步驟

#### 設計
- [ ] 採方案 (c)：Stop hook 是首要、staleness check 是備援
- [ ] Stop hook 與 PostToolUse 區分：PostToolUse 在 tool 跑完寫 completed；Stop 在 session 結束時若 row 仍 in_progress 則寫 aborted

#### 實作 Stop hook
- [ ] 寫 hook script（路徑建議 `plugins/baransu/hooks/stop.{sh|py}`）
- [ ] 讀 `.claude/harness/telemetry.jsonl`，找 `session_id == 當前 session` 且 `terminal_state == in_progress` 的 row
- [ ] **CAS guard**（design.md「Telemetry mutation contract」單調規則）：只在當前 `terminal_state == in_progress` 才轉 `aborted`；若已是 `completed`（PostToolUse 先到）則不動；若已是 `aborted` / `interrupted` 也不重寫
- [ ] 標 `aborted` 並回寫（持 flock + atomic rename）
- [ ] task-hooks-04 註冊到 settings.json

#### 實作 staleness reaper（拆出獨立 script，遵 A-F3）
- [ ] 寫獨立 script `plugins/baransu/scripts/harness-reaper.{sh|py}`（不在 grade-collector 內）— 避免污染 /grade 職責
- [ ] reaper 對 `terminal_state == in_progress` 且 `created_at` 超過 24h 的 row 改標 `interrupted`
- [ ] CAS guard：只在 `in_progress` 才轉 `interrupted`，其他狀態不動
- [ ] /grade Stage 0 呼叫該 reaper（保證 stale row 在打分前被收割）
- [ ] 在 task-shared-01 的 schema 文件記載 staleness 行為

#### INT-2 測試重現
- [ ] 寫測試輔助：模擬 ctrl-c → 驗 Stop hook 路徑（aborted）
- [ ] 寫測試輔助：mock `created_at` 為 25h 前 → 驗 staleness 路徑（interrupted）

---

## TASK-hooks-04: 註冊兩 hook 到 ~/.claude/settings.json + 驗證 plugin.json 不污染

**需求追溯**：REQ-006 Scenario 1、INV-1
**目標**：把兩個 hook 寫進 user-level settings.json，並驗證 plugin.json 沒被誤改加 hooks 欄位。
**驗收標準**：
- [ ] `~/.claude/settings.json` 含 UserPromptSubmit + PostToolUse 兩個 hook 條目，路徑與 task-hooks-01 / 02 產出檔案一致
- [ ] `grep -F '"hooks"' plugins/baransu/.claude-plugin/plugin.json` 0 命中
- [ ] settings.json 修改在 commit 中可被 review（這是 user-level 檔，不在 git 裡，但要在 task report 顯示 diff）
- [ ] 若採用 Stop hook（task-hooks-03），一併在這裡註冊

### 步驟

#### 註冊 hook
- [ ] 讀現有 settings.json 結構（先備份）
- [ ] 加 UserPromptSubmit + PostToolUse 條目（路徑用絕對路徑或 `${CLAUDE_PLUGIN_ROOT}` 變數）
- [ ] 若有 Stop hook 一併加

#### 驗證
- [ ] grep plugin.json 確認無 hooks 欄位
- [ ] 跑一支 baransu skill 看 telemetry.jsonl 確實累積條目
- [ ] settings.json diff 印在 task report
