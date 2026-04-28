# Tasks: integration
**前置群組**：shared, hooks, scripts, agents, skills-grade, skills-bridge, skills-triage（全部）

跨層收尾：CLAUDE.md 更新、Cron 註冊、invariants 檢查腳本、R3 demo、E2E 真機跑通。

---

## TASK-integration-01: CLAUDE.md skill 表更新 11→14

**需求追溯**：REQ-006 Scenario 2、INV-2
**目標**：更新 CLAUDE.md 把新增的 /grade /triage /bridge 三 skill 加進「Skills」表，總數 11→14。
**驗收標準**：
- [ ] CLAUDE.md Skills 表含 14 列（11 既有 + 3 新增）
- [ ] 每新 skill 一行描述「When to invoke」（與既有風格一致：簡潔 use-case 句）
- [ ] 既有 11 skill 的描述保持不動（不順手改 wording）
- [ ] CLAUDE.md 最後一節「No Build / Test Commands」更新為反映現在引入了 bats / pytest（若 task-shared 起就決定引入）

### 步驟

- [ ] 讀現有 CLAUDE.md 的 Skills 表
- [ ] 加 3 列：/grade（「對 baransu skill transcript 評分」）、/triage（「聚類 poor verdict + 自動修補」）、/bridge（「skill 兩版本 head-to-head replay」）
- [ ] 視需要調整「No Build / Test Commands」段（若實際引入 bats / pytest）

---

## TASK-integration-02: CronCreate 註冊 daily 00:00

**需求追溯**：REQ-002、REQ-003
**目標**：用 CronCreate 註冊每日午夜觸發 /grade（chain 到 /triage 與 auto-fix）。
**驗收標準**：
- [ ] 排程已註冊（透過 Claude Code CronCreate primitive 或等效機制）
- [ ] 可手動 list（CronList 或對應 tool）看到該 schedule
- [ ] schedule 文件記錄在 task report 或 CLAUDE.md 對應段落

### 步驟

- [ ] 確認 CronCreate primitive 可以呼叫 baransu skill；若不行，採其他註冊方式（user-level systemd timer / cron 等）
- [ ] 寫註冊指令 + delete 指令備忘
- [ ] 跑一次手動觸發驗證 chain（/grade → /triage → auto-fix）邏輯能跑

---

## TASK-integration-03: invariants 檢查腳本

**需求追溯**：REQ-006 全部、INV-1～6
**目標**：寫一支 shell script 一次跑完 6 條 KD invariant + 5 黑安全邊界 settings 檢查，回 exit 0/non-zero。
**驗收標準**：
- [ ] `plugins/baransu/scripts/check-invariants.sh` 存在且可執行
- [ ] 輸出對 6 條 invariant + 5 條安全邊界各自一行 PASS / FAIL 摘要
- [ ] 全部 PASS exit 0；任一 FAIL exit non-zero
- [ ] script 可被 `/baransu:execute` 或 cron 引用

### 步驟

#### INV-1 檢查
- [ ] `jq '.hooks // {} | keys' ~/.claude/settings.json` 含 UserPromptSubmit + PostToolUse
- [ ] `grep -F '"hooks"' plugins/baransu/.claude-plugin/plugin.json` 必須 exit 1（無命中）

#### INV-2 檢查
- [ ] `find plugins/baransu/skills -mindepth 1 -maxdepth 1 -type d | wc -l` == 14
- [ ] CLAUDE.md skill table row count == 14

#### INV-3 檢查
- [ ] `tail -1 .claude/harness/telemetry.jsonl | jq -r 'keys[]'` 含 7 個 expected keys

#### INV-4 檢查
- [ ] grep `1/5` 或 `0.2` 或 `equal weight` 在 `plugins/baransu/scripts/grade-collector.*` 或 `plugins/baransu/skills/grade/SKILL.md`
- [ ] 5 維欄位名 `outcome_quality` / `iteration_velocity` / `scope_blast` / `human_override_rate` / `failure_recurrence` 各自在 grade.jsonl schema 文件 / SKILL.md 命中
- [ ] grep `>= 50` 或 `≥ 50` 在 SKILL.md tune trigger 段

#### INV-5 檢查
- [ ] 觸發 dry-run 模式 auto-fix（mock cluster），跑前後主 repo `git status --porcelain` 結果相同
- [ ] 或：grep auto-fix 章節描述「mktemp -d」+「不在主 repo」

#### INV-6 檢查（5 黑）
- [ ] EDGE-1：grep `.claude/harness/` 在 .gitignore
- [ ] EDGE-2：grep redaction 路徑清單**全 5 條**（`.env*` / `*secret*` / `*credential*` / `*.pem` / `*.key`）各自命中 PostToolUse hook script 或對應規範文件
- [ ] EDGE-3：grep denylist **全 5 條**路徑（`.github/`、`plugin.json`、`marketplace.json`、`.gitignore`、`scripts/`）各自在 /triage SKILL.md 命中
- [ ] EDGE-4：grep `K=3` 或 `attempt cap.*3` + `attempt_history` 邊界在 /triage SKILL.md（同時驗 cluster 跨 run 累計邏輯被描述）
- [ ] EDGE-5：grep `daily_push.*5` 或 `daily quota.*5` 在 /triage SKILL.md / state.json schema 兩處皆命中

---

## TASK-integration-04: R3 demo — 注入 regression 並用 /bridge 抓出

**需求追溯**：REQ-005 Scenario 5、E2E-4、C6
**目標**：實際走一次 R3 success — 在 telemetry corpus ≥ 50 條時，建一個含人工 regression 的 target branch，跑 /bridge 看到 fail。
**驗收標準**：
- [ ] 製造一個 demo target branch（建議命名 `demo/regression-{date}`）含一條清楚 regression（例如 /think 的 Stage A 縮成 1 輪而非 3 輪）
- [ ] 跑 /bridge 比對 main HEAD vs demo branch
- [ ] /bridge 回 fail 並印含 regression 影響的 top-N 退化 prompt
- [ ] demo 結果寫進 `.claude/analyze/2026-04-28-self-healing-harness/r3-demo.md` 留紀錄

### 步驟

- [ ] 等到 telemetry 累積 ≥ 50 完成 row（這是時序前置條件，spec 階段可標 BLOCKED until corpus）
- [ ] checkout 一個 demo branch 修一支 skill（首選 /think）
- [ ] 跑 /bridge
- [ ] 把結果與分析寫進 r3-demo.md（含 invocation command、輸出摘要、解讀）
- [ ] 把 demo branch 標 archive（不 merge 進 main）

---

## TASK-integration-05: E2E 真機跑一輪自癒迴圈

**需求追溯**：E2E-1, E2E-2, E2E-5, E2E-6
**目標**：手動觸發或快轉一次完整 cron chain（/grade → /triage → auto-fix），看到所有產出檔（telemetry / grade / triage / harness/fix branch / state.json）齊全；同時驗證 redaction、denylist 在真機上生效。
**驗收標準**：
- [ ] E2E-1：跑某 baransu skill 後 telemetry.jsonl 多一筆 7 欄齊全 row
- [ ] E2E-2：手動跑 /grade + /triage chain 後 grade.jsonl 與 triage.jsonl 各自更新；若有過閾值 cluster，harness/fix/{id} branch 在 GitLab 出現
- [ ] E2E-5：手動製造一次涉及 .env / config/secret.yaml 的 diff，看到 redaction 生效（telemetry 不含這幾條）
- [ ] E2E-6：手動製造一次涉及 marketplace.json 的 diff，看到 denylist abort 生效（cluster 標 requires_human、無 push）
- [ ] 把跑通結果寫進 `.claude/analyze/2026-04-28-self-healing-harness/e2e-report.md`

### 步驟

- [ ] 跑 baransu skill 製造一筆 telemetry（E2E-1）
- [ ] 製造 ≥1 個 poor verdict（可以人工注入或讓 skill 真的失敗一次）
- [ ] 手動觸發 /grade /triage chain
- [ ] 觀察 grade.jsonl / triage.jsonl / state.json 與 isolated worktree 軌跡
- [ ] 製造 redaction 與 denylist 觸發場景，個別驗證
- [ ] 寫 e2e-report.md
