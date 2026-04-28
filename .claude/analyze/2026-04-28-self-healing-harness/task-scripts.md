# Tasks: scripts
**前置群組**：shared

3 個執行腳本，是 skill SKILL.md 邏輯的實作載體。

---

## TASK-scripts-01: grade-collector — telemetry → grade.jsonl

**需求追溯**：REQ-002 Scenarios 1-3、INT-3、INT-10、INT-11、INV-4
**目標**：讀 telemetry.jsonl，篩 `terminal_state == completed`，5 維 equal-weight 計算 verdict，寫 grade.jsonl，並在累積閾值處輸出 tune trigger 訊號。
**驗收標準**：
- [ ] script 路徑（建議 `plugins/baransu/scripts/grade-collector.{sh|py}`）存在且可執行
- [ ] 對 mock telemetry（10 條 mix completed/aborted）只對 completed 寫 verdict
- [ ] 5 維分數計算公式可在程式中直接 grep 到 `1/5` 或 `0.2` 或 `equal weight` 標記
- [ ] aggregate = sum(5 dims) / 5，精度 ≤ 1e-6
- [ ] 累積 ≥ 50 completed row 時輸出含 `tune_review_due: true` 的 stdout / log line

### 步驟

#### 程式骨架
- [ ] 解析 `.claude/harness/telemetry.jsonl` 全檔（pyjson 或 jq）
- [ ] filter `terminal_state == completed`
- [ ] 對每條 row 算 5 維分數（rubric 計算邏輯依 task-skills-grade-01 的 5 維 baransu-native rubric 表執行：`outcome_quality` / `iteration_velocity` / `scope_blast` / `human_override_rate` / `failure_recurrence`）

#### 計算與輸出
- [ ] 依 rubric 計算 5 維（spec rubric 細節在 SKILL.md，本 task 只實作載體）
- [ ] aggregate / quality enum mapping
- [ ] 寫 grade.jsonl row（schema 見 task-shared-02）

#### tune trigger
- [ ] 統計目前累積 completed row 數
- [ ] ≥ 50 時 stdout 印 `tune_review_due: true` 一行 + cluster summary

#### 單元測試
- [ ] INT-10：固定 5 維分數 → aggregate 數值精確
- [ ] INT-11：模擬 49 vs 50 條 → 訊號正確 toggle
- [ ] INT-3：non-completed 完全不出現在 grade.jsonl

---

## TASK-scripts-02: triage-cluster — grade.jsonl → triage.jsonl

**需求追溯**：REQ-003 Scenarios 1, 3、INT-4
**目標**：聚類 poor verdict（同 skill / 同根因簽名），5 維 severity 排序，輸出 cluster row + 標 escalate flag。不負責 investigator subagent 派發（那在 /triage SKILL.md 層做）。
**驗收標準**：
- [ ] script 存在且可執行
- [ ] 對 mock grade.jsonl 含 5 poor verdict（3 同 skill 同 issue + 2 異） → 產出 ≥ 1 cluster row 且其 member_session_ids 含正確 3 條
- [ ] 5 維 severity 計算可重現（給同樣輸入產同樣輸出）
- [ ] 過閾值 cluster 標 `escalate: false`（待 /triage SKILL.md 後續派 investigator）；不過閾值 cluster 進 trend log 段（仍寫 jsonl 但 escalate 欄位透過適當值表達）

### 步驟

#### 聚類規則設計
- [ ] 決定 cluster key（建議：`skill_outcome.skill_name` + 主要錯誤訊號 hash）
- [ ] 寫 pseudo-code 到 SKILL.md 對應段落

#### 實作聚類
- [ ] 載入 grade.jsonl
- [ ] 群組 by cluster key
- [ ] 對每群算 5 維 severity（公式可從 9 dims 或 cohort properties 推；spec 階段允許用最直觀的 max / mean）

#### 輸出 + escalate 標記
- [ ] 寫 triage.jsonl row（schema 見 task-shared-02）
- [ ] severity_aggregate 過閾值 → escalate flag 預備（具體 escalate enum 由 /triage SKILL.md 後續判定）

#### 單元測試
- [ ] INT-4：mock 輸入產出預期 cluster
- [ ] 同樣輸入跑兩次結果相同（deterministic）

---

## TASK-scripts-03: bridge-replay — worktree + replay + statistical gate + trap

**需求追溯**：REQ-005 Scenarios 1-4、INT-8、INT-9
**目標**：給定 target branch 與要比較的 skill 名，從 telemetry 抽 ≥ N 條 completed prompt，在 isolated worktree 跑兩版 head-to-head 並回統計閘門結果。SIGINT/EXIT 時清理乾淨。
**驗收標準**：
- [ ] script 路徑（建議 `plugins/baransu/scripts/bridge-replay.{sh|py}`）存在且可執行
- [ ] 用 `mktemp -d /tmp/baransu-bridge-XXX` 建 tmp dir
- [ ] `git worktree add` 把目標 branch checkout 到 tmp dir
- [ ] `trap SIGINT EXIT` 正確掛上清理（`git worktree remove --force` + `rm -rf`）
- [ ] 對 N 個 prompt 跑兩遍打分（rubric 重用 grade-collector 的 5 維計算）
- [ ] aggregate Δ ≥ 0.15 → exit code = fail（建議非零 exit 並印 top-N 退化 prompt）
- [ ] Δ < 0.15 → exit code = pass

### 步驟

#### Worktree 隔離
- [ ] 寫 `mktemp -d` + `git worktree add`
- [ ] 寫 trap handler

#### Replay 迴圈
- [ ] 從 telemetry 撈 prompt（filter `terminal_state == completed`，數量上限可參數化）
- [ ] 對每個 prompt 在 v1（目前 main HEAD）+ v2（worktree branch）各自跑該 skill（如何在 script 中呼叫 skill：可走 baransu CLI / Claude Code subprocess；spec 階段允許暫定）
- [ ] 抓兩次 score 並儲存

#### 統計閘門
- [ ] aggregate Δ 計算
- [ ] 樣本數不足 → 印 inconclusive 並 exit non-zero（不誤報 pass/fail）
- [ ] Δ ≥ 0.15 → fail 路徑：印 top-5 退化 prompt
- [ ] Δ < 0.15 → pass 路徑

#### Cleanup 驗證
- [ ] 跑完後 `git worktree list` 不應出現 `/tmp/baransu-bridge-*`
- [ ] INT-9 測試：送 SIGINT 模擬中斷，cleanup 正確

#### 單元測試
- [ ] mock 兩版 score → 確認 gate 結果正確
- [ ] mock SIGINT → trap 觸發 + worktree 清乾淨
