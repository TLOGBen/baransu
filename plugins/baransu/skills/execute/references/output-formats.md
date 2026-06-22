## Contents

- §confirm.md
- §task-map.md
- §impl-checklist
- §final-report.md

# Execute Output Formats

Templates for all files written by /baransu:execute. Section anchors (§) are referenced from SKILL.md.

---

## §confirm.md

Path: `.claude/execute/{date}-{slug}/execute/confirm.md`

```markdown
# Confirm — Execute Session

session_start: {ISO 8601}
spec_dir: {provided path}
classification: {M | L | XL}  # filled after Step 1

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
```

---

## §task-map.md

Path: `.claude/execute/{date}-{slug}/execute/task-map.md`

```markdown
# Task Map

| Task Tool ID | Group | Task ID | Impl-Checklist | Notes |
|-------------|-------|---------|----------------|-------|
| {id} | {group} | TASK-{group}-01 | impl-checklist-{group}.md | |
| {id} | {group} | TASK-{group}-02 | impl-checklist-{group}.md | ⚠️ file conflict with {other-group} — serialized |
```

Pre-scan warnings appear in the Notes column when Step 1d detects a shared file path between two groups in the same frontier level.

---

## §impl-checklist

Path: `.claude/execute/{date}-{slug}/execute/impl-checklist-{group}.md`

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

Path: `.claude/execute/{date}-{slug}/execute/final-report.md`

```markdown
# Final Report — /baransu:execute

session: {date}-{slug}
spec_dir: {path}
completed_at: {ISO 8601}

## 整體結果

Requirements 達成率：N/M（N 個 REQ-XXX 有對應綠燈測試）

## Task 完成狀態

| Group | Task | 狀態 | 備註 |
|-------|------|------|------|
| {group} | TASK-{group}-01 | ✅ | |
| {group} | TASK-{group}-02 | ❌ blocked | 連續失敗 3 次；smart-friend 診斷：{...} |
| {group} | TASK-{group}-03 | ❌ cascade-blocked | 前置群組 {group} blocked |
| {group} | TASK-{group}-04 | ❌ blocked | spec 矛盾：REQ-001 與 REQ-003 衝突 |

## E2E 測試結果

{✅ 通過 | ❌ 失敗：{reason} | ⏭️ 跳過：test.md 未提供啟動命令}

## Final-Review 結論

{✅ 通過（needs_fixer: false）| 殘餘問題：{advisory notes}}

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

## Goal-Alignment Filter Metric

<!-- goal_alignment_filter_metric — observation block; counters accumulated in §4b Phase 3, written here at Step 7. -->

total_findings_count: {N}
downgraded_to_advisory_count: {M}

<!--
Placeholder note: 若 total_findings_count > 0，則 downgrade_rate =
downgraded_to_advisory_count / total_findings_count（即 M/N）。未來三次
spec 後評估，若降級率（M/N）持續 > 50%，須回看 R2 行為（filter 過鬆或
reviewer 大量產 off-goal finding）。
-->
```

The **Blocked 項目** section is omitted entirely when there are no blocked tasks.
The **Goal-Alignment Filter Metric** section is always emitted (counters default to `0` when no review fired).
