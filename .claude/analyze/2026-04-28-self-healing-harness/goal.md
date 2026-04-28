# Goal

## 目標（Goal）

在 baransu plugin 上新增兩個 hook（PostToolUse + UserPromptSubmit）、三個新 skill（/grade /triage /bridge）、1 個 investigator subagent、3 個 script 與一份 telemetry schema，把跑完的 baransu skill transcript 經「grade→triage→auto-fix→re-grade→bridge replay」形成 deterministic 且全本地的自癒迴圈，並讓 Bridge 能在歷史 prompt corpus（≥50 條 completed telemetry row）上擋下一次注入的 regression。

## 驗收標準（Criteria）

- [ ] **C1 — Telemetry 寫入正確**：兩個 hook 註冊到 `~/.claude/settings.json` 後，跑任何 baransu skill 都會在 `.claude/harness/telemetry.jsonl` 產生條目，每條含 7 個欄位（`session_id` / `terminal_state` / `prompt_text` / `skill_outcome` / `commit_hash` / `diff_summary_redacted` / `attempt_history`）。
- [ ] **C2 — Grade 跑通**：/grade 由 CronCreate 排程觸發，對前一日 `terminal_state == completed` 條目按 5 維 baransu-native equal-weight (1/5) rubric 打分，poor verdict 正確寫入 `.claude/harness/grade.jsonl`。
- [ ] **C3 — Triage 跑通**：/triage 讀 grade.jsonl，聚類後依 5 維 severity 排序產出 top cluster；對 top cluster 派 investigator subagent 產 evidence bundle 寫入 `.claude/harness/triage.jsonl`。
- [ ] **C4 — Auto-fix 五黑全 pass**：以下 5 條安全邊界各有獨立 test case 且全部綠燈：
  - `.claude/harness/` 已加進 `.gitignore`
  - hook redaction filter 跳過 `.env*` / `*secret*` / `*credential*` / `*.pem` / `*.key` 路徑且不寫 diff 字面
  - auto-fix push 前 denylist 命中 `.github/` / `plugin.json` / `marketplace.json` / `.gitignore` / `scripts/` 任一即 abort
  - 同 cluster 連 fail K=3 次正確 escalate `requires_human`
  - daily push hard cap = 5，超出 cap 後同日後續 auto-fix 不 push
- [ ] **C5 — Bridge head-to-head 跑通**：手動呼叫 /bridge 時在 `mktemp -d /tmp/baransu-bridge-XXX` 隔離 worktree（trap 清理）跑兩個 skill 版本，比較 score 差距，Δ≥0.15 + 樣本足時觸發 fail，否則 pass；主 repo working tree 未被動到。
- [ ] **C6 — R3 demo**：在累積 ≥50 條 completed row 的歷史 prompt corpus 上注入一次人工 regression（例如改一個 skill body 讓某個 step 故意失敗），Bridge 能正確偵測並回 fail。前置條件：累積 ≥ 50 條 completed row 或注入等量 fixture corpus（參 test.md E2E-4）。
- [ ] **C7 — Invariants 都未破**：6 條 KD invariant 在實作完成後仍可由獨立檢查腳本驗證（兩 hook 在 user-level、telemetry schema 7 欄齊全、auto-fix 永不 touch 主 repo working tree、rubric 用 equal-weight、plugin.json 未加 hooks 欄位、總 skill 數 11→14）。

## 範圍（Scope）

### 包含（In scope）

- 兩個新 hook：PostToolUse + UserPromptSubmit，註冊到 `~/.claude/settings.json`
- 三個新 skill：/grade /triage /bridge（含 SKILL.md + references）
- 1 個新 subagent：investigator-agent（perspective 類，read-only，無 git ops）
- 3 個新 script：grade-collector、triage-cluster、bridge-replay（語言依實作階段選 shell/python，spec 不鎖死語言）
- telemetry schema：`.claude/harness/telemetry.jsonl` 7 欄位 append-only jsonl
- 5 維 baransu-native rubric（`outcome_quality` / `iteration_velocity` / `scope_blast` / `human_override_rate` / `failure_recurrence`）bootstrap：Week-1 equal weight 1/5 each；tune trigger 鎖「累積 ≥50 條 completed row 後 review」
- auto-fix 安全邊界 5 條（gitignore / redaction / denylist / attempt cap / daily quota）
- 隔離保證：/bridge 與 auto-fix 都用 `mktemp -d` 在 repo 外建 worktree + trap 清理
- `.gitignore` 加 `.claude/harness/`
- CLAUDE.md skill 表更新（11→14）

### 不包含（Out of scope）

- **LLM judge** — R2 邊界，本輪不接；含 Bridge replay 不引入 LLM 比對。理由：訊號可信度未知前先用 deterministic 起步，避免 token 成本干擾 loop 驗證。
- **任何外部服務**（Linear / GitHub Actions / CloudWatch / AI Gateway / 第三方 API）— 全部跑在 WSL2 本地。理由：分發成本 vs 驗證可行性的取捨，本輪先驗證可行性。
- **多 user / 多 host 共享 telemetry** — telemetry.jsonl 純本地 append-only，不做 schema versioning / storage abstraction / 雲端同步。理由：與 R2 「不多 host」邊界一致。
- **真實 user traffic 分流** — Bridge 純 git-worktree shadow run on 歷史 prompt corpus。理由：baransu 本來就沒 user traffic 可分流。
- **跨 plugin grade** — harness 只看 baransu 自身 11 支 skill 的 telemetry。理由：跨 plugin 需要更廣的 schema，超出 MVP。
- **歷史 telemetry backfill** — harness 啟用前的 skill 跑紀錄不回填打分。理由：backfill 需要從 transcript 推斷欄位，雜訊大；day 1 開始累積即可。
- **plugin.json 加 hooks 欄位** — hook 註冊只走 user-level settings.json。理由：與「不多 host」邊界一致；plugin-level 散佈留 v2。
- **MR 觸發機制** — gh CLI / glab / 純 git push 之間的選擇延後到實作 auto-fix 那輪（U1）。
- **auto-revert 策略** — pure reset / 反向 cherry-pick / 只標 ticket 之間的選擇延後到實作 Job 5 那輪（U2）。

## Hard Constraints（不可動）

源自 /think + /review 已批准的 6 條 KD，後續所有 stage 與 task 不得淡化：

1. 三件式三 skill (/grade /triage /bridge) + 1 investigator subagent 必 ship；total skill 數 11→14。
2. 兩個 hook（PostToolUse + UserPromptSubmit），註冊在 user-level `~/.claude/settings.json`，**不**進 plugin.json hooks 欄位。
3. telemetry schema 7 欄位齊全；/grade 只看 `terminal_state == completed`；Bridge corpus 來自 completed.prompt_text。
4. 5 維 baransu-native rubric（`outcome_quality` / `iteration_velocity` / `scope_blast` / `human_override_rate` / `failure_recurrence`）Week-1 equal weight 1/5 each；tune trigger = 累積 ≥50 條 completed row。
5. auto-fix 安全邊界 5 條（fix prompt deterministic 模板；hook redaction；.gitignore；push denylist；attempt cap K=3 + daily quota=5）。
6. /bridge 與 auto-fix 都在 `mktemp -d /tmp/baransu-{bridge,harness}-XXX` 隔離 worktree 跑；auto-fix 永不 touch 主 repo working tree。註：「主 repo working tree」= git index 與 git-tracked 工作區；`.claude/harness/` 雖位於 repo 內但已 gitignore，視為 harness-owned scratch space，auto-fix 對其 mutation 不違反此 KD。
