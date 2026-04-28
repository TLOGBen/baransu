# Test Strategy

## 測試金字塔

- **單元測試**：每個 script / hook 的純邏輯（rubric 計算、severity aggregate、redaction filter、denylist 比對、equal-weight bootstrap、daily reset）
- **整合測試**：`telemetry → /grade → grade.jsonl → /triage → triage.jsonl → auto-fix → state.json → MR` 的 cron chain；hook 寫 telemetry 與 skill 行為的耦合
- **E2E**：實際跑 baransu skill 看 telemetry 條目產生；手動跑 /bridge 完成一輪 head-to-head；R3 demo 注入 regression 看 /bridge 抓得到
- **不變量驗證**：6 條 KD invariants + 5 黑安全邊界，每條一個獨立 test case

## E2E 測試策略

| 場景 | 起點 | 終點 | 對應 Criteria |
|------|------|------|--------------|
| E2E-1：完整 telemetry 寫入 | user 跑 `/baransu:think 「xxx」` | telemetry.jsonl 多一筆含 7 欄位的 row | C1 |
| E2E-2：cron 全鏈條跑通 | 手動觸發 cron @00:00（或 fast-forward）至少有 1 個 poor verdict 的素材 | grade.jsonl + triage.jsonl + （若通過閘門）GitLab branch / MR 成形 | C2 + C3 + C4 |
| E2E-3：/bridge head-to-head | 手動跑 `/baransu:bridge {target_branch}` 比較同一 skill 的兩版 | /bridge stdout 印 pass/fail + worktree 已清 + 主 repo working tree 無新增 untracked | C5 |
| E2E-4：R3 demo regression catch | 手動在 target branch 注入「故意 regression」（例：把 /think Stage A 第三輪打掉），用 `/bridge` 比 v1 vs v2。**前置條件**：telemetry.jsonl `terminal_state == completed` 累積 ≥ 50 條（spec 階段允許 fixture corpus 注入替代以利非阻塞驗證） | /bridge 回 fail + 印 top-N 退化 prompt（其中應含被注入 regression 影響的 prompt） | C6 |
| E2E-5：hook redaction 真機驗證 | user 跑 /dev 動 `.env`、`config/secret.yaml`、`src/main.py` 三檔 | telemetry row 的 `diff_summary_redacted` 只含 `src/main.py`、不含其他兩條 | C1 + C4-redaction |
| E2E-6：denylist abort 真機驗證 | 在 cluster 觸發 auto-fix 時人工讓 /dev 動 `marketplace.json` | auto-fix abort、不 push、cluster 標 `requires_human` | C4-denylist |

## 整合測試策略

| 測試目標 | 涉及層 | 關鍵驗證點 |
|---------|--------|-----------|
| INT-1：UserPromptSubmit + PostToolUse 兩 hook 配對 | hook + storage | 同一 session 的兩個 hook 各寫一次後合成完整 row（id 配對正確、不重複、不缺漏；同 session_id 雙 hook 序列輸入 → 最終 row 唯一且 7 欄齊全，可由 jq 驗證） |
| INT-2：terminal_state 在 ctrl-c 時為 aborted | hook + storage | 模擬中斷，PostToolUse 來不及寫時，預備機制（例如 SessionEnd hook 補刀或 row 預設 `aborted`）正確標記 |
| INT-3：/grade 只看 completed | skill + storage | telemetry 有 mix of completed / aborted / interrupted，/grade 只對 completed 寫 verdict |
| INT-4：聚類正確 | skill + storage | grade.jsonl 含 5 條 poor verdict 中 3 條同 skill 同 issue → /triage 產 1 個 cluster 涵蓋 3 條 |
| INT-5a：investigator subagent read-only happy path | subagent + git | investigator 跑完後 `git status` 與跑前一致（無 untracked / modified / staged） |
| INT-5b：investigator violation negative case | subagent + dispatcher | 注入一個讓 investigator 嘗試 write / git ops 的 mock prompt → dispatcher 攔截或 agent 自我拒絕；test 驗證 `git status` 仍乾淨且 evidence_bundle 不被視為合法（caller 看見錯誤訊號） |
| INT-6：cluster.attempt_history 跨 run 累計 | skill + state | 同 cluster_id 連 3 次 cron run 都 fail，第 4 次 /triage 直接 escalate（auto-fix 不呼叫 /dev） |
| INT-7：daily counter 隔日 reset | state + 時鐘 | 模擬「第 5 push 已用完 → 第 6 abort → 隔日 cron」流程，第 6 個 cluster 在隔日成功 push（counter 已 reset） |
| INT-8：worktree mktemp 隔離 | bridge / auto-fix + git | /bridge 跑期間，主 repo `git worktree list` 多出 `/tmp/baransu-bridge-*`，跑完不見 |
| INT-9a：trap 清理（SIGINT 路徑）| bridge / auto-fix + signal | 對 /bridge 進程送 SIGINT，worktree 與 tmp 目錄都被清掉，`git worktree list` 乾淨 |
| INT-9b：trap 清理（inconclusive exit 路徑）| bridge + signal | corpus < N 觸發拒跑、或樣本不足觸發 inconclusive，trap EXIT 正常清乾淨（cleanup 與 SIGINT 走同一程式碼路徑） |
| INT-10：rubric equal-weight 計算正確 | script + math | 給 5 維固定分數，aggregate = sum / 5（精度 ≤ 1e-6） |
| INT-11a：tune trigger 啟動 | skill + storage | telemetry 累積到第 50 條 completed row 後，/grade 輸出含 `tune_review_due: true` 訊號，state.json 寫入 `tune_review_due_since` |
| INT-11b：tune-acknowledged reset | skill + state | 跑 `/grade --tune-acknowledged` 後 state.json `tune_review_due_since` 清為 null；之後 /grade 跑完 stdout 不再印 `tune_review_due: true`（直到累積又跨閾值） |
| INT-12：fix prompt 模板 deterministic | script + diff | 對同一 cluster 跑兩次 auto-fix，產出的 fix prompt 文本完全相同（sha256 hash 相同；hash 計算入口在 SKILL.md 對應段） |

## 關鍵邊界條件

對應 5 黑 auto-fix 安全邊界 + 6 條 invariants，每條都獨立 test：

### Auto-fix 五黑

- **EDGE-1：gitignore 含 `.claude/harness/`** — REQ-001 Scenario 4。Test：`grep -F '.claude/harness/' .gitignore` exit 0；新建 `.claude/harness/foo.jsonl` 後 `git status` 不出現該檔。
- **EDGE-2：redaction filter 路徑清單** — REQ-001 Scenario 3、REQ-005 Scenario 5。Test：餵 hook 一個含 `.env` / `secret.yaml` / `id_rsa.pem` / `config.key` / `creds.json` 的 diff，輸出的 `diff_summary_redacted` 不含這 5 條。
- **EDGE-3：push denylist 路徑清單** — REQ-004 Scenario 2。Test：mock /dev 產生 patch 動 `.github/workflows/ci.yml`，auto-fix 在 push 前 abort、cluster 標 `requires_human`、無 git push 副作用。
- **EDGE-4：attempt cap K=3** — REQ-004 Scenario 3。Test：對 cluster_id `cl-test-cap` 預先在 telemetry 寫 3 個 fail attempt，再跑 /triage，auto-fix skip 該 cluster、cluster 標 `escalate_human`。
- **EDGE-5：daily push quota=5** — REQ-004 Scenario 4。Test：state.json 預先寫 `daily_push_count=5` + `daily_push_date=今日`，第 6 個 cluster 過所有其他閘門到 push 步驟，被 abort 並標 `daily_quota_exceeded`。

### Invariants（KD 不變量）

- **INV-1：hook 註冊位置** — REQ-006 Scenario 1。Test：`jq '.hooks' ~/.claude/settings.json` 含 `UserPromptSubmit` + `PostToolUse`；`grep -F '"hooks"' plugins/baransu/.claude-plugin/plugin.json` 0 命中。
- **INV-2：總 skill 數 14** — REQ-006 Scenario 2。Test：`ls -d plugins/baransu/skills/*/` count 14；CLAUDE.md skill 表 row count = 14。
- **INV-3：telemetry 7 欄位齊全** — REQ-006 Scenario 3。Test：`tail -1 .claude/harness/telemetry.jsonl | jq 'keys' | wc -l` ≥ 7，且 7 個 expected key 都在 list 內。
- **INV-4：rubric equal-weight bootstrap** — REQ-006 Scenario 4。Test：對應 /grade 設定檔或 SKILL.md grep `1/5` 或 `0.2` 或 `equal weight` 命中；5 維欄位名 `outcome_quality` / `iteration_velocity` / `scope_blast` / `human_override_rate` / `failure_recurrence` 各自 grep 命中；tune trigger 字串含 `≥ 50` 或 `>= 50`。
- **INV-5：auto-fix 不 touch 主 repo working tree** — REQ-006 Scenario 5。Test：cron run 開始前後對主 repo `git status --porcelain` diff，結果為空；`pwd` 在 cron run 期間應始終非主 repo（in worktree）。
- **INV-6：5 黑安全邊界齊全** — REQ-006 Scenario 6。Test：跑一支 invariants 檢查腳本，依次 grep / 讀設定確認 5 條規則設定值齊全（不檢查行為，只檢查設定存在）。

## 與既有 baransu 測試慣例的一致性

baransu CLAUDE.md 明寫「No Build / Test Commands — 不要捏造 npm test / pytest」。本 spec 的測試策略是**設計層描述**，實作階段才會引入具體測試框架。建議：
- shell 邏輯用 `bats`（bash automated testing system）或純 shell assert
- python 邏輯（若有）用 `pytest`
- E2E 用 shell 腳本 + 期望輸出 diff
- 引入測試框架時更新 CLAUDE.md「No Build / Test Commands」段落

## 對應關係矩陣

每條 Criteria → REQ → 測試類型 → 邊界條件：

| Criteria | REQ | E2E | 整合 | 邊界 |
|----------|-----|-----|------|------|
| C1 telemetry 寫入 | REQ-001 | E2E-1, E2E-5 | INT-1, INT-2 | EDGE-2, INV-3 |
| C2 grade 跑通 | REQ-002 | E2E-2 | INT-3, INT-10, INT-11a, INT-11b | INV-4 |
| C3 triage 跑通 | REQ-003 | E2E-2 | INT-4, INT-5a, INT-5b | — |
| C4 auto-fix 五黑 | REQ-004 | E2E-2, E2E-6 | INT-6, INT-7, INT-12 | EDGE-1～5, INV-6 |
| C5 bridge head-to-head | REQ-005 | E2E-3 | INT-8, INT-9a, INT-9b | — |
| C6 R3 demo | REQ-005 Scenario 5 | E2E-4 | — | — |
| C7 invariants | REQ-006 | — | — | INV-1～6 |
