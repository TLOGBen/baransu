# Tasks: skills-grade
**前置群組**：shared, hooks, scripts

/grade skill — 對 telemetry 打分。User-facing skill 入口；實作邏輯由 grade-collector script 載體。

---

## TASK-skills-grade-01: /grade SKILL.md + references 撰寫

**需求追溯**：REQ-002 Scenarios 1-3、INT-3、INT-11、INV-4
**目標**：寫 /grade 的 SKILL.md，描述 cron + manual 觸發、5 維 rubric 規格（含 dim 定義）、equal-weight bootstrap、tune trigger，並串接 grade-collector script。
**驗收標準**：
- [ ] `plugins/baransu/skills/grade/SKILL.md` 存在，frontmatter 含 name + description（description 含足以觸發 skill 的 trigger phrases）
- [ ] SKILL body 描述：何時觸發、輸入（telemetry.jsonl）、輸出（grade.jsonl）、5 維 rubric 各維意義
- [ ] 明寫 equal-weight bootstrap：「Week-1 用 1/5 each」+ tune trigger「累積 ≥ 50 條 completed row 後 review」
- [ ] 明寫只看 `terminal_state == completed`
- [ ] 引用 grade-collector script 路徑

### 步驟

#### Frontmatter 與 description
- [ ] 寫 description 含 user-facing trigger phrases（「打分」「grade」「評分這幾天的 skill 表現」）

#### Stage 描述
- [ ] Stage 0：環境檢查（telemetry.jsonl 存在 / non-empty）
- [ ] Stage 1：讀取 + filter completed
- [ ] Stage 2：跑 grade-collector script
- [ ] Stage 3：tune trigger 判斷 + 印訊號
- [ ] Stage 4：完成報告（繁中：「對 N 條 completed row 打分完成；poor M 條；trigger {tune_review_due / not_yet}」）

#### 5 維 baransu-native rubric 文件
- [ ] 維度名稱固定為：`outcome_quality` / `iteration_velocity` / `scope_blast` / `human_override_rate` / `failure_recurrence`
- [ ] 為每維寫一句意義說明 + 對應 telemetry 來源欄位（必填 table）：

| dim | 意義 | telemetry 來源 | 推導規則（deterministic） |
|-----|------|---------------|------------------------|
| `outcome_quality` | 該次 skill 最終是否乾淨完成 | `skill_outcome.exit_code` + `skill_outcome.final_state` | exit_code==0 且 final_state in {approved/done/passed} → 1.0；其他組合按表查值（建議：exit≠0 → 0.0；exit==0 但 final_state 含 fail/error → 0.3） |
| `iteration_velocity` | 完成所需回合的快慢 | `attempt_history`（length）+ session 起訖時間 | 直接完成（attempt_history==[] 且 1 commit） → 1.0；retry≥1 → 0.6；retry≥3 → 0.2 |
| `scope_blast` | 該次動到的檔案範圍與風險 | `diff_summary_redacted` | 0 檔 → 1.0（read-only）；1-3 檔且全在 `plugins/baransu/skills/**` → 0.8；4+ 檔或命中 risky path（`.github/`、`plugin.json`、`marketplace.json`、`scripts/`）→ 0.3 |
| `human_override_rate` | 是否被 user 中途 override / pivot | `skill_outcome.final_state` 含 `override` / `aborted` 標 | 無 override → 1.0；有 override 但任務完成 → 0.6；override 後放棄 → 0.2 |
| `failure_recurrence` | 同 cluster_id 在過去 N 日的累計失敗次數 | `attempt_history` 全 array 過濾 cluster_id | 0 fail in last 7d → 1.0；1-2 → 0.5；≥3 → 0.0 |

- [ ] 明寫 bootstrap 1/5 與 tune trigger 鎖量化條件 ≥ 50

#### 串接 script
- [ ] SKILL body 引用 `plugins/baransu/scripts/grade-collector.{sh|py}` 路徑
- [ ] 描述如何傳入 telemetry path 與 grade output path 參數

---

## TASK-skills-grade-02: tune_review_due 訊號完整鏈路

**需求追溯**：REQ-002 Scenario 3、INT-11
**目標**：把 tune trigger 從 grade-collector script 傳到 user 看得見的位置（/grade 完成報告 + 視需要寫入 state.json 標記）。
**驗收標準**：
- [ ] /grade 完成報告含「目前 completed row 累積：N；tune trigger {due / not yet}」一行
- [ ] 若 due，state.json 加一個 flag `tune_review_due_since: <ISO date>`，再次 review tune 後人工 reset
- [ ] INT-11 case 可重現

### 步驟

- [ ] 修改 grade-collector 把 trigger flag 寫進 stdout 結構化區段
- [ ] /grade SKILL body 解析該訊號並 echo 給使用者
- [ ] 設計 state.json `tune_review_due_since` 欄位（補進 task-shared-04 schema 文件）
- [ ] 寫一個小步驟讓 user 在 tune 完後手動清 flag（例如手動跑 `/grade --tune-acknowledged`）
