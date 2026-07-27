## Contents

- §confirm.md
- §task-map.md
- §impl-checklist
- §final-report.md

# Execute Output Formats

Templates for all files written by the /analyze execution pipeline. Section anchors (§) are referenced from execution-pipeline.md.

---

## §confirm.md

Path: `.codex/execute/{date}-{slug}/execute/confirm.md`

```markdown
# Confirm — Execute Session

session_start: {ISO 8601}
spec_dir: {provided path}
classification: {M | L | XL}  # filled after Step 1
git_available: {true | false}  # Step 0 probe
dispatch_available: {true | false}  # Step 0 tool-list probe (subagent-dispatch tool present?)
execution_mode: {standard | degraded-in-place | serial-absorbed}  # degraded when git unavailable or worktree add failed (§4a); serial-absorbed when no dispatch tool (Step 0)

## 已讀取文件

| 檔案 | 讀取時間 |
|------|---------|
| goal.md | {ISO 8601} |
| requirement.md | {ISO 8601} |
| design.md | {ISO 8601} |
| test.md | {ISO 8601} |
| task-{group}.md | {ISO 8601} |

## DAG 分析

| Frontier Level | Groups | Notes |
|---------------|--------|-------|
| 0 | {group, group} | 前置群組：無 |
| 1 | {group} | depends on level 0 |

Max frontier width: {N}
Classification: {M | L | XL}
Parallel workflows: {N}
Worktrees: {none | one per group}

## Worktree Registry（standard / serial-absorbed L/XL；degraded-in-place 留空）

| Group | Path | target_branch |
|-------|------|---------------|
| {group} | .codex/worktrees/execute-{date}-{slug}-{group} | {recorded target_branch} |
```

Sections marked "filled after Step N" must not be pre-baked with values at Step 0 — write placeholders and fill at the owning step, so file state can witness step ordering.

---

## §task-map.md

Path: `.codex/execute/{date}-{slug}/execute/task-map.md`

```markdown
# Task Map

| Task Tool ID | Group | Task ID | test_weight | Impl-Checklist | Notes |
|-------------|-------|---------|-------------|----------------|-------|
| {id} | {group} | TASK-{group}-01 | full | impl-checklist-{group}.md | |
| {id} | {group} | TASK-{group}-02 | riding | impl-checklist-{group}.md | ⚠️ file conflict with {other-group} — serialized |

`test_weight` is decided at Step 3 write time (gate-time), one row per task, with a
one-line rationale in Notes when `riding` is chosen.
```

Pre-scan warnings appear in the Notes column when Step 1d detects a shared file path between two groups in the same frontier level.

For L/XL runs, task-map.md also carries the group-level integration record written by §4d and read by the Step 7 branch-deletion guard:

```markdown
## Integration Status

| Group | integration_status | 原因 |
|-------|--------------------|------|
| {group} | integrated \| not-integrated | {merge ✅ / direct-blocked / cascade-blocked / merge ❌ / Green broken ×3} |
```

---

## §impl-checklist

Path: `.codex/execute/{date}-{slug}/execute/impl-checklist-{group}.md`

Populated by copying `驗收標準` items verbatim from each task in `task-{group}.md`. One file per group; all tasks for that group are concatenated in document order.

```markdown
# Impl Checklist: {group}

前置群組：{value from task-{group}.md}

## TASK-{group}-01: {task title}

需求追溯：REQ-XXX
- [ ] {acceptance criterion from task file}
- [ ] {acceptance criterion from task file}

Review 結果：
備註：

---

## TASK-{group}-02: {task title}

需求追溯：REQ-XXX, REQ-YYY
- [ ] {acceptance criterion}

Review 結果：
備註：
```

`Review 結果` and `備註` are filled by review-agent after each impl attempt. On task ✅, both fields contain the review-agent's final verdict and any notes.

---

## §final-report.md

Path: `.codex/execute/{date}-{slug}/execute/final-report.md`

```markdown
# Final Report — /baransu:analyze 執行段

session: {date}-{slug}
spec_dir: {path}
completed_at: {ISO 8601}

## 整體結果

Requirements 達成率：N/M（N 個 REQ-XXX 有對應綠燈測試）

## Task 完成狀態

| Group | Task | 狀態 | 證據 | 備註 |
|-------|------|------|------|------|
| {group} | TASK-{group}-01 | ✅ | green_proof: `{test_command}` exit {exit_code}；{tests_correspondence 摘要} | |
| {group} | TASK-{group}-02 | ❌ blocked | — | 連續失敗 3 次；smart-friend 診斷：{...} |
| {group} | TASK-{group}-03 | ❌ cascade-blocked | — | 前置群組 {group} blocked |
| {group} | TASK-{group}-04 | ❌ blocked | — | spec 矛盾：REQ-001 與 REQ-003 衝突 |

Every ✅ row must fill the 證據 column by citing that task's Pre-SWITCH green_proof
fields (test_command / exit_code / output_tail / tests_correspondence — the exact
schema of `../../../.codex-agents/review-agent.toml` §3) — the report carries the evidence
reference; the gate itself stays at Pre-SWITCH (this step still only serializes,
it does not recompute). A ✅ row with an empty 證據 column is a claim, not a
confirmation.

## E2E 測試結果

{✅ 通過（必附下方 e2e_evidence 塊）| ❌ 失敗：{reason} | ⏭️ 跳過：test.md 未提供啟動命令}

e2e_evidence:（僅 ✅ 時必填；exit 0 但 collected 為 0 或計數不可解析 = ❌）
  command: {實際執行的 E2E 命令}
  exit_code: {0}
  collected: {N}
  passed: {N}
  output_tail: |
    {輸出最後數行，逐字}

## Final-Review 結論

{✅ 通過（needs_fixer: false）| 殘餘問題：{advisory notes}}

goal.md 準則交叉核對（每條 C{n} 依字面判定，缺一即為 needs_fixer）：

| Criteria | 判定 | 證據（字面條件 vs 實際行為） |
|----------|------|------------------------------|
| C1 | ✅/❌ | {evidence} |
| C2 | ✅/❌ | {evidence} |

## Blocked 項目

| Task | 類型 | 詳情 |
|------|------|------|
| TASK-{group}-NN | 連續失敗 3 次 | smart-friend 結論：{...} |
| TASK-{group}-NN | cascade-blocked | 前置群組 {group} blocked |
| TASK-{group}-NN | spec 矛盾 | REQ-XXX 與 REQ-YYY 衝突：{...} |
| TASK-{group}-NN | merge 語意衝突 | 衝突檔案：{...} |
| TASK-{group}-NN | Final-Review 殘餘 | REQ-XXX 未覆蓋（fixer 後仍缺） |

## 產出清單

{list of created/modified files, one per line}
```

The **Blocked 項目** section is omitted entirely when there are no blocked tasks.
