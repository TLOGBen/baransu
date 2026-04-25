# /baransu:execute — TDAID orchestration skill

Reads an Analyze spec directory, builds a dependency DAG, classifies execution as XL/L/M, drives each task group through a Summarize→Impl→Review while-loop, handles blocking and smart-friend escalation, runs E2E and Final-Review, then writes `final-report.md`.

The body below is English (agent-facing). All user-visible output is in **Traditional Chinese (繁體中文)**.

---

## Core constraints

- **Analyze spec directory is read-only.** Never Edit or Write any file under `.claude/analyze/`. Any execution path that attempts this must stop immediately and escalate as a structural blocker.
- **Subagent depth = 1.** Do not invoke skills that themselves dispatch parallel Tasks + AskUserQuestion. The `agents/*.md` files in this plugin are designed for depth-1 dispatch only.
- **All tasks created before execution begins.** Use Task Tool Create to register every group × task in Stage 2. Do not create tasks mid-execution.
- **Working files are in `.claude/execute/`, not `.claude/analyze/`.** Edit/Write is permitted under the execute working directory.

---

## Stage 0 — Spec validation + confirm.md

### 0a. Validate input path

The user provides a spec directory path (e.g. `.claude/analyze/2026-04-25-my-feature/`).

Check:
1. Directory exists
2. `goal.md`, `requirement.md`, `design.md`, `test.md` are all present
3. At least one `task-{group}.md` is present

If directory does not exist → output 「找不到 Analyze spec 目錄，請先執行 /baransu:analyze」and stop.

If any required file is missing → list missing files in output, write confirm.md with missing files noted, escalate to user with 「spec 文件不完整，缺少：{list}，無法繼續執行」and stop.

### 0b. Write confirm.md

Derive `{date}-{slug}` from the spec directory's directory name (same date + slug segment).

Write `.claude/execute/{date}-{slug}/execute/confirm.md`:

```markdown
# Confirm — Execute Session

session_start: {ISO 8601}
spec_dir: {provided path}
classification: {filled after Stage 1}

## 已讀取文件

| 檔案 | 讀取時間 |
|------|---------|
| goal.md | {timestamp} |
| requirement.md | {timestamp} |
| design.md | {timestamp} |
| test.md | {timestamp} |
| task-{group}.md | {timestamp} |

## DAG 分析
{filled after Stage 1}
```

---

## Stage 1 — DAG analysis + XL/L/M classification

### 1a. Build the dependency DAG

Read every `task-{group}.md`. For each file, extract the `前置群組` field (the line immediately after the heading). Build a directed graph:
- Node: group name
- Edge: A → B means group B's `前置群組` includes A

### 1b. Compute maximum parallel frontier width

Use BFS topological-sort:
1. Level 0: all groups with `前置群組：無`
2. Level 1: groups whose every predecessor is at Level 0
3. Continue until all groups assigned

Maximum parallel frontier width = max count of groups at any single BFS level.

### 1c. Classify

| Width | Classification | Parallel Workflows | Worktrees |
|-------|---------------|-------------------|-----------|
| ≥ 4 | XL | 4 (serialize excess groups) | 4 gitworktrees |
| 2–3 | L | width count | gitworktree per group |
| 1 | M | 1 | none (main branch) |

For XL when a frontier has > 4 groups, pick the first 4 by document order; remaining wait for the next wave.

### 1d. Pre-scan (Advisory)

For each pair of groups in the same frontier level, scan their `步驟` sections for identical file paths. If overlap is detected:
- Add a warning note to that group's row in task-map.md
- Serialize those two groups (move the later one to the next frontier level)
- Record reason in task-map.md notes

If step descriptions are ambiguous, prefer the no-overlap assumption over misdetection. Advisory means: only flag when confident.

### 1e. Update confirm.md

Fill in `classification` and `DAG 分析` sections in confirm.md.

---

## Stage 2 — Task Tool creation

Before any implementation begins, use Task Tool Create to register every group × task combination. Process groups in topological order:

```
For each group at each frontier level (topological order):
  For each TASK-{group}-NN in task-{group}.md:
    TaskCreate: title="{group} / TASK-{group}-NN: {task title}", status=pending
    Record: Task Tool ID → (group, task-id) mapping
```

Do not begin Stage 3 until all tasks are created.

---

## Stage 3 — Work document initialization

### 3a. task-map.md

Write `.claude/execute/{date}-{slug}/execute/task-map.md`:

```markdown
# Task Map

| Task Tool ID | Group | Task ID | Impl-Checklist | Notes |
|-------------|-------|---------|----------------|-------|
| {id} | {group} | TASK-{group}-NN | impl-checklist-{group}.md | {pre-scan warnings} |
```

### 3b. impl-checklist-{group}.md

For each group, write `.claude/execute/{date}-{slug}/execute/impl-checklist-{group}.md`:

Copy the `驗收標準` checklist items from each task in `task-{group}.md`:

```markdown
# Impl Checklist: {group}

前置群組：{value from task file}

## TASK-{group}-01: {title}
需求追溯：REQ-XXX
- [ ] {criterion from task file}
Review 結果：
備註：
```

---

## Stage 4 — TDAID Loop

### 4a. Execution order

Process groups by frontier level (topological order). Within each level, groups with the same level run as parallel Impl Workflows.

For **M**: single workflow, main branch.
For **L/XL**: create one gitworktree per group in the current frontier:
```
git worktree add .git/worktrees/{group} -b execute/{date}-{slug}/{group}
```

### 4b. Per-group Impl Workflow

For each group, for each task in document order:

1. Dispatch **summarize-agent** with:
   - `spec_dir`: the Analyze spec directory path
   - `task_id`: TASK-{group}-NN
   - `output_path`: `.claude/execute/{date}-{slug}/execute/context/{group}-{task-id}-ctx.md`

2. Run TDAID loop for this task (see 4c).

### 4c. TDAID loop (single task)

```
failure_count = 0

LOOP:
  Dispatch impl-agent with:
    - ctx_content: contents of context/{group}-{task-id}-ctx.md
    - worktree_path: path for this group (or main for M)
    - refactor_mode: false (set to true only when review signals it)
    - correction_strategy: from smart-friend output if failure_count == 2

  if impl-agent status == ⚠️ (Red gate not passed):
    # test was already passing — wrong test, not new behavior
    report to user and stop this task (mark blocked: Red gate failed)
    break

  if impl-agent status == ❌ AND failure detail mentions compile error:
    # compile error does NOT count toward failure_count
    continue LOOP

  Dispatch review-agent with:
    - impl_result: impl-agent output
    - ctx_path: context/{group}-{task-id}-ctx.md
    - checklist_path: impl-checklist-{group}.md

  SWITCH review tier:

    CASE "direct fix":
      review-agent applies fix inline (authorized via its Edit tool)
      mark task ✅ (Task Tool status = completed)
      break LOOP

    CASE "advisory":
      mark task ✅ (Task Tool status = completed)
      break LOOP

    CASE "packaged confirm (quality)" AND task is L/XL AND refactor_signal == true:
      dispatch impl-agent again with refactor_mode=true (does NOT count as failure)
      dispatch review-agent again
      mark task ✅
      break LOOP

    CASE "packaged confirm (quality)" AND (task is M OR refactor_signal == false):
      # treat as advisory for M tasks
      mark task ✅
      break LOOP

    CASE "packaged confirm (correctness)" OR "needs judgment":
      failure_count += 1

      if review.spec_contradiction != false:
        mark task BLOCKED (reason: spec contradiction — {details})
        TaskUpdate: status=blocked
        escalate to user: 「TASK-{group}-NN blocked：{spec_contradiction 說明}」
        break LOOP

      if failure_count >= 3:
        mark task BLOCKED (reason: 3 consecutive impl failures)
        TaskUpdate: status=blocked
        escalate to user: 「TASK-{group}-NN blocked after 3 failures」
        break LOOP

      if failure_count == 2:
        dispatch smart-friend-agent with:
          - task_goal: Task.目標 from ctx.md
          - spec_excerpts: Requirements + Design + Test excerpts from ctx.md
          - failure_summary_1: review findings from attempt 1
          - failure_summary_2: review findings from attempt 2
        # smart-friend output is passed to next impl dispatch as correction_strategy
        continue LOOP

      continue LOOP  # failure_count == 1
```

### 4d. Cascade-blocked propagation

After each task is marked BLOCKED, check downstream groups. For each group G where:
- G's `前置群組` list contains at least one blocked group
- AND G has no non-blocked, non-completed predecessors remaining

→ Mark G as cascade-blocked. TaskUpdate all of G's tasks to status=cascade-blocked.

Record in final-report: direct blocked vs cascade-blocked separately.

### 4e. Merge Point (L/XL only)

After all tasks in a frontier level complete (✅, blocked, or cascade-blocked):

```
merge_retry_count = 0

Dispatch merge-agent with:
  - worktree_paths: list of worktree paths for this frontier level
  - target_branch: main
  - test_command: from test.md (look for a "Green" or unit test command)

LOOP:
  if merge-agent status == ✅:
    proceed to next frontier level
    break

  if merge-agent status == ❌ (semantic conflict):
    escalate to user immediately with conflict_details
    mark all pending downstream groups as blocked (reason: merge conflict)
    record in final-report blocked list
    break  # do not proceed

  if merge-agent status == ⚠️ (Green broken):
    merge_retry_count += 1
    if merge_retry_count >= 2:
      escalate to user: 「Merge 後 Green 仍未通過，已重試 2 次」
      mark all pending downstream groups as blocked
      break
    # retry: dispatch merge-agent again with failed_tests as additional context
    continue LOOP
```

---

## Stage 5 — E2E Test

All frontier levels must be processed (merged to main) before Stage 5.

### 5a. Read E2E command

Read `test.md`. Look for an E2E startup command (typically in the E2E 測試策略 section). If none found → record「E2E 跳過：test.md 未提供啟動命令」in final-report and proceed to Stage 6.

### 5b. Run E2E

Execute the E2E startup command via Bash. Monitor output.

If E2E passes → record ✅ in final-report.

If E2E fails:
1. Group independent failure clusters (one cluster per failing feature area)
2. Dispatch one **e2e-fix-agent** per cluster (parallel, independent)
   - Provide each with: `e2e_failure_report`, `e2e_strategy`, `relevant_files`
3. After all fix agents complete, re-run E2E
4. If passes → record ✅
5. If still fails → record ❌ with details in final-report blocked section; proceed to Stage 6

---

## Stage 6 — Final-Review + Fixer

### 6a. Final-Review

Dispatch **final-review-agent** with:
- `requirement_path`: path to requirement.md
- `test_dir`: test directory path

If `needs_fixer: false` → record final-review conclusion in final-report and proceed to Stage 7.

If `needs_fixer: true`:
1. Dispatch **final-fixer-agent** with:
   - `coverage_report`: final-review-agent's Coverage Report
   - `requirement_excerpts`: full text of ❌ REQ-XXX entries from requirement.md
   - `design_excerpts`: design.md sections relevant to ❌ REQs
2. After fixer completes, dispatch final-review-agent again
3. If now `needs_fixer: false` → proceed to Stage 7
4. If still `needs_fixer: true` → record remaining gaps in final-report blocked section; proceed to Stage 7 (do **not** invoke fixer again)

### 6b. Advisory findings

Any `advisory_notes` from the Coverage Report → record in final-report; do not trigger Final-Fixer.

---

## Stage 7 — final-report.md + cleanup

### 7a. Write final-report.md

Write `.claude/execute/{date}-{slug}/execute/final-report.md`:

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
| {group} | TASK-{group}-NN | ✅ | |
| {group} | TASK-{group}-NN | ❌ blocked | {reason} |
| {group} | TASK-{group}-NN | ❌ cascade-blocked | 前置群組 {X} blocked |

## E2E 測試結果
{✅ 通過 / ❌ 失敗原因 + 建議 / ⏭️ 跳過：test.md 未提供啟動命令}

## Final-Review 結論
{✅ 通過 / 殘餘問題（advisory notes）}

## Blocked 項目
| Task | 類型 | 詳情 |
|------|------|------|
| TASK-{group}-NN | 連續失敗 3 次 | smart-friend 結論：{...} |
| TASK-{group}-NN | cascade-blocked | 前置群組 {group} blocked |
| TASK-{group}-NN | spec 矛盾 | REQ-XXX 與 REQ-YYY 衝突：{...} |
| TASK-{group}-NN | merge 語意衝突 | 衝突檔案：{...} |
```

### 7b. Worktree cleanup

After final-report.md is written, remove all gitworktrees created during this session:

```bash
git worktree remove .git/worktrees/{group} --force
git branch -d execute/{date}-{slug}/{group}
```

### 7c. Session end output (繁體中文)

```
/baransu:execute 完成。

spec_dir: {path}
completed_at: {timestamp}

整體結果：{N}/{M} REQ 達成率
final-report.md: .claude/execute/{date}-{slug}/execute/final-report.md

{若有 blocked 項目，列出清單}
```

---

## Error handling reference

| Error | Detection | Action |
|-------|-----------|--------|
| spec 目錄不存在 | Stage 0 | Reject, tell user to run /analyze |
| spec 文件缺失 | Stage 0 | List missing files, escalate |
| Impl 失敗 1 次 | TDAID loop | Retry with review findings |
| Impl 失敗 2 次 | TDAID loop | Dispatch smart-friend, then retry |
| Impl 失敗 3 次 | TDAID loop | BLOCKED |
| spec 矛盾 | review-agent | BLOCKED, escalate |
| Merge 語意衝突 | Merge point | Escalate, BLOCKED downstream |
| Merge Green 破壞 ≤2 次 | Merge point | Retry merge-agent |
| Merge Green 破壞 >2 次 | Merge point | BLOCKED downstream, escalate |
| E2E 失敗 | Stage 5 | e2e-fix-agent(s), one re-run |
| E2E Fix 後仍失敗 | Stage 5 | Record ❌, continue |
| Final-Review 有缺口 | Stage 6 | final-fixer-agent once, one re-run |
| Final-Review 仍有缺口 | Stage 6 | Record as blocked, continue |
| 任何寫入 Analyze 文件的嘗試 | All stages | Immediate structural blocker, escalate |
