---
name: execute
description: "TDAID orchestration engine for medium-to-large tasks built from /analyze spec. Reads a spec directory, builds a dependency DAG, drives each task group through Summarize→Impl→Review TDAID loops via subagents, runs E2E and Final-Review, and writes final-report.md. Triggers: '/baransu:execute', 'execute the plan', 'run the spec', 'implement the analyze result', '開始執行', '跑 execute', '依照 analyze 執行'."
argument-hint: "<spec-dir-path>"
user-invocable: true
---

Long-running orchestration engine for medium-to-large tasks. This body is English (agent-facing). All user-visible output is **Traditional Chinese (繁體中文)**.

## 目標

Read an `/analyze` spec directory. Execute every task through a Summarize → Impl → Review TDAID loop with subagent context isolation. Run E2E tests and Final-Review. Write `final-report.md`. Never stop early — if a task is blocked, escalate and continue unblocked work.

---

## 核心限制 (Hard Constraints)

These apply across all steps. The review-agent rule and the spec-read-only rule are the two most commonly violated — they are the first things to re-read at Steps 4, 5, and 6 entry after any auto-compact.

- **review-agent is never optional.** Every task — documentation, scripts, config, code — goes through review-agent after each impl-agent attempt. `TaskUpdate status=completed` is only reachable as the result of a review-agent outcome for the current impl attempt. Marking a task ✅ without dispatching review-agent first is a constraint violation.
- **Analyze spec directory is read-only.** Never Edit or Write any file under `.claude/analyze/`. Any execution path that attempts this must stop immediately and escalate as a structural blocker.
- **Subagent depth = 1.** Agents in `agents/*.md` are stateless leaf nodes. They do not dispatch further subagents.
- **All Task Tools created before execution begins.** Register every group × task via TaskCreate in Step 2. No mid-execution task creation.
- **Working files live under `.claude/execute/`.** Edit and Write are only permitted in the execute working directory.

---

## Step 0 — Spec Validation

Validate the provided spec directory. Check: (1) directory exists, (2) `goal.md`, `requirement.md`, `design.md`, `test.md` are present, (3) at least one `task-{group}.md` is present.

Derive `{date}-{slug}` from the spec directory name (same date + slug segment). Write confirm.md at `.claude/execute/{date}-{slug}/execute/confirm.md`. Template: `references/output-formats.md §confirm.md`.

**Done when:** All required files confirmed present; confirm.md written with file list and timestamps.

**Fallback:** Directory missing → output 「找不到 Analyze spec 目錄，請先執行 /baransu:analyze」and stop. Files missing → list them, write confirm.md with gaps noted, escalate 「spec 文件不完整，缺少：{list}，無法繼續執行」and stop.

---

## Step 1 — Dependency Analysis + Classification

**1a. Build DAG.** Read every `task-{group}.md`. Extract the `前置群組` field. Build a directed graph: node = group, edge A→B = group B depends on A.

**1b. BFS topological sort.** Level 0 = groups with `前置群組：無`. Level N = groups whose every predecessor is at Level ≤ N−1. Maximum parallel frontier width = max groups at any single level.

**1c. Classify.**

| Max width | Class | Parallel workflows | Worktrees |
|-----------|-------|--------------------|-----------|
| ≥ 4 | XL | 4 (serialize excess per wave) | 4 gitworktrees |
| 2–3 | L | width count | gitworktree per group |
| 1 | M | 1 | none (main branch) |

When the DAG allows ≥ 2 groups at the same level, run them in parallel — do not serialize L-class groups sequentially. For XL waves with > 4 groups, pick the first 4 by document order; remainder wait for the next wave.

**1d. Pre-scan for file conflicts.** For group pairs in the same frontier level, scan their `步驟` sections for identical file paths. If confident overlap exists: serialize those two groups (move the later one to the next level), record reason in task-map.md.

**1e. Update confirm.md.** Fill `classification` and `DAG 分析` sections.

**Done when:** DAG built, all groups assigned frontier levels, classification decided, confirm.md updated.

**Fallback:** Malformed or missing `前置群組` → assume no predecessors; note in task-map.md.

---

## Step 2 — Task Tool Creation

Register every group × task before any implementation begins:

```
For each group (topological order):
  For each TASK-{group}-NN in task-{group}.md:
    TaskCreate: title="{group} / TASK-{group}-NN: {task title}", status=pending
    Record: Task Tool ID → (group, task-id) mapping
```

**Done when:** Every task registered. Do not begin Step 3 until all TaskCreate calls complete.

---

## Step 3 — Work Document Initialization

Write:
- `.claude/execute/{date}-{slug}/execute/task-map.md` — maps Task Tool IDs to groups and checklist files. Template: `references/output-formats.md §task-map.md`.
- `.claude/execute/{date}-{slug}/execute/impl-checklist-{group}.md` (one per group) — copies `驗收標準` items from each task in `task-{group}.md`, adds blank `Review 結果:` and `備註:` fields. Template: `references/output-formats.md §impl-checklist`.

**Done when:** task-map.md and all impl-checklist files written.

---

## Step 4 — TDAID Loop

> **Re-read checkpoint:** Before entering Step 4, re-read §核心限制 and this entire step. Confirm review-agent dispatch is mandatory, `failure_count`/`compile_error_count` semantics (§4b Phase 2–3), cascade-blocked propagation (§4c), and merge retry cap (§4d). These are the rules most vulnerable to drift during long sessions.

### 4a. Execution order + worktrees

Process groups by frontier level (topological order). Groups at the same level run in parallel.

For **M**: single workflow, main branch. No worktrees.

For **L/XL**: create one gitworktree per group in the current wave before dispatching any impl-agent for that wave:
```bash
git worktree add .git/worktrees/{group} -b execute/{date}-{slug}/{group}
```

### 4b. Per-task TDAID loop

For each group, for each task in document order:

**Phase 1 — Summarize**

Dispatch **summarize-agent** with `spec_dir`, `task_id`, and `output_path`. The agent produces `context/{group}-{task-id}-ctx.md` containing all eight fields:

| Field | Source |
|-------|--------|
| Goal | Full objective from goal.md |
| Requirements | REQ-XXX entries this task traces to |
| Scenarios | Relevant Given/When/Then from requirement.md |
| Task | Task title, goal sentence, and acceptance criteria |
| Design | Relevant sections from design.md |
| Test | Relevant test strategy from test.md |
| Constraints | Naming rules, architecture constraints, scope boundaries |
| Files | Files to create / delete / modify (from task 步驟) |

**Phase 2 — Impl** (Write Tests → Prove Red → Impl Green)

```
failure_count = 0
compile_error_count = 0  # only counted after smart-friend has been dispatched

LOOP:
  Dispatch impl-agent with:
    - ctx_path:            context/{group}-{task-id}-ctx.md
    - worktree_path:       group worktree path (or null for M)
    - refactor_mode:       false  (set true only when review signals it)
    - correction_strategy: smart-friend output if failure_count == 2

  CASE impl-agent status == ⚠️  (Red gate not passed — test already passing):
    Report: "Red gate not passed: test was already passing before impl"
    Mark task BLOCKED (reason: Red gate failed — wrong test)
    TaskUpdate: status=blocked
    escalate to user
    break LOOP

  CASE impl-agent status == ❌  AND failure detail mentions compile error:
    # Compile errors do NOT count toward failure_count
    if failure_count >= 2:
      compile_error_count += 1
      if compile_error_count >= 3:
        Mark task BLOCKED (reason: 持續 compile error after smart-friend)
        TaskUpdate: status=blocked
        escalate to user: 「TASK-{group}-NN blocked：smart-friend 後持續 compile error」
        break LOOP
    continue LOOP  # retry without incrementing failure_count

  → proceed to Phase 3 (impl-agent returned Green, no compile error)
```

**Phase 3 — Review** (Verify Green → optional Refactor → Review quality)

> This phase is mandatory. Do not mark a task ✅ before dispatching review-agent for the current impl attempt.

Dispatch **review-agent** with:
- `impl_result`: impl-agent output
- `ctx_path`: context/{group}-{task-id}-ctx.md
- `checklist_path`: impl-checklist-{group}.md
- `worktree_path`: group worktree path (null for M)
- `task_classification`: M | L | XL

**Interpreting review-agent output and routing:**

review-agent returns one of five tiers. Map them to actions as follows:

```
SWITCH review_tier:

  CASE "direct fix":
    # review-agent applied a cosmetic fix inline
    mark task ✅
    TaskUpdate: status=completed
    break LOOP

  CASE "advisory":
    # findings are informational; no action required
    mark task ✅
    TaskUpdate: status=completed
    break LOOP

  CASE "packaged confirm (quality)"  # code quality / standards / arch / security
    if task_classification is L or XL  AND  review.refactor_signal == true:
      # Refactor phase: at most once per task for L/XL
      Dispatch impl-agent with refactor_mode=true  ← does NOT count as failure_count
      Dispatch review-agent again (same inputs)
      SWITCH second_review_tier:
        CASE "direct fix" | "advisory" | "packaged confirm (quality)":
          mark task ✅
          TaskUpdate: status=completed
          break LOOP
        CASE "packaged confirm (correctness)" | "needs judgment":
          failure_count += 1
          → go to failure escalation logic below
    else:
      # M task, or no refactor signal: treat as advisory
      mark task ✅
      TaskUpdate: status=completed
      break LOOP

  CASE "packaged confirm (correctness)"  OR  "needs judgment":
    # Primary failure: tests incomplete, Green not verified, or impl incorrect
    failure_count += 1
    → go to failure escalation logic below
```

**Failure escalation logic** (reached from correctness/judgment cases):

```
  if review.spec_contradiction != false:
    Mark task BLOCKED (reason: spec contradiction — {details})
    TaskUpdate: status=blocked
    escalate to user: 「TASK-{group}-NN blocked：{spec_contradiction 說明}」
    break LOOP

  if failure_count >= 3:
    reason = "3 consecutive impl failures"
    if smart_friend_output defined AND smart_friend_output.spec_issue != false:
      reason += "；smart-friend 診斷：" + smart_friend_output.spec_issue
    Mark task BLOCKED (reason)
    TaskUpdate: status=blocked
    escalate to user with reason
    break LOOP

  if failure_count == 2:
    Dispatch smart-friend-agent with:
      - task_goal:         Task.目標 from ctx.md
      - spec_excerpts:     Requirements + Design + Test from ctx.md
      - failure_summary_1: review findings from attempt 1
      - failure_summary_2: review findings from attempt 2
    # smart-friend output becomes correction_strategy for next impl dispatch
    continue LOOP

  continue LOOP  # failure_count == 1: retry with review findings
```

### 4c. Cascade-blocked propagation

After each task is marked BLOCKED, evaluate group-level status:
- A group is **group-blocked** if ANY of its tasks is BLOCKED.

For each downstream group G where `前置群組` contains at least one group-blocked group: mark G **cascade-blocked**. TaskUpdate all G's tasks to cascade-blocked.

Record direct-blocked vs cascade-blocked separately in final-report.

### 4d. Merge Point (L/XL only)

After all tasks in a frontier level complete (✅, blocked, or cascade-blocked):

```
merge_retry_count = 0
last_failed_tests = null

LOOP:
  Dispatch merge-agent with:
    - worktree_paths:  list of worktree paths for this level
    - target_branch:   main
    - test_command:    from test.md
    - failed_tests:    last_failed_tests (null on first dispatch)

  CASE merge-agent status == ✅:
    proceed to next frontier level
    break

  CASE merge-agent status == ❌  (semantic conflict):
    escalate to user immediately with conflict_details
    mark all pending downstream groups BLOCKED (reason: merge conflict)
    record in final-report blocked list
    break

  CASE merge-agent status == ⚠️  (Green broken):
    last_failed_tests = merge-agent failed_tests
    merge_retry_count += 1
    if merge_retry_count >= 3:
      escalate to user: 「Merge 後 Green 仍未通過，已重試 2 次」
      mark all pending downstream groups BLOCKED
      break
    continue LOOP
```

**Done when (Step 4):** All frontier levels processed. All tasks are ✅, blocked, or cascade-blocked.

---

## Step 5 — E2E Test

> **Re-read checkpoint:** Before entering, re-read this step. Confirm single-retry limit for E2E.

Read `test.md` for the E2E startup command (typically in the E2E 測試策略 section). Use Monitor tool to observe long-running test output.

If no command found → record 「E2E 跳過：test.md 未提供啟動命令」in final-report; proceed to Step 6.

If E2E passes → record ✅ in final-report.

If E2E fails:
1. Group independent failure clusters (one per failing feature area; if boundaries unclear, one cluster per failing test)
2. Dispatch one **e2e-fix-agent** per cluster in parallel
3. Re-run E2E (Monitor)
4. Passes → ✅. Still fails → record ❌ with details in final-report blocked section; proceed to Step 6.

**Done when:** E2E result recorded (✅ / ❌ / skipped).

**Fallback:** If Monitor is unavailable, run via Bash and parse output. If E2E command produces no output after 5 minutes, record as ❌ timeout.

---

## Step 6 — Final-Review + Final-Fixer

> **Re-read checkpoint:** Before entering, confirm: final-fixer runs exactly once, never twice.

Dispatch **final-review-agent** with:
- `requirement_path`: path to requirement.md
- `test_dir`: parse from test.md integration/E2E sections; default to `tests/`

If `needs_fixer: false` → record conclusion in final-report; proceed to Step 7.

If `needs_fixer: true`:
1. Dispatch **final-fixer-agent** with: `coverage_report`, `requirement_excerpts` (full text of ❌ REQ-XXX entries), `design_excerpts` (design.md sections relevant to ❌ REQs)
2. After fixer completes, dispatch final-review-agent again (same inputs)
3. If `needs_fixer: false` → proceed to Step 7
4. If still `needs_fixer: true` → record remaining gaps in final-report blocked section; proceed to Step 7. **Do not invoke fixer again.**

Advisory notes from Coverage Report → record in final-report; do not trigger fixer.

**Done when:** Final-review result recorded (✅ / gaps listed).

---

## Step 7 — final-report.md + Cleanup

Write `.claude/execute/{date}-{slug}/execute/final-report.md`. Template: `references/output-formats.md §final-report.md`.

Remove all gitworktrees created this session:
```bash
git worktree remove .git/worktrees/{group} --force
git branch -D execute/{date}-{slug}/{group}
```

Output to user (繁體中文):
```
/baransu:execute 完成。
spec_dir: {path}
completed_at: {ISO 8601}
整體結果：{N}/{M} REQ 達成率
final-report.md: .claude/execute/{date}-{slug}/execute/final-report.md
{若有 blocked 項目，條列清單}
```

**Done when:** final-report.md written; all worktrees removed; user notified.

---

## Gotchas

- **[review-agent bypass trap]**: Documentation, script, and config tasks feel like they "have nothing to test". The orchestrator rationalizes skipping review-agent because impl-agent reported success. This is the failure mode: review-agent verifies impl-checklist-{group}.md acceptance criteria, not just unit tests. `TaskUpdate status=completed` is only reachable after a review-agent outcome.
  Solution: Re-read §核心限制 before marking any task ✅.

- **[compile error vs failure_count]**: After impl-agent returns ❌ with a compile error, `failure_count` must NOT increment. Counting compile errors as failures triggers smart-friend early and wastes the retry budget on syntax issues.
  Solution: Only `failure_count++` on review-agent "packaged confirm (correctness)" or "needs judgment" returns.

- **[final-fixer one-pass cap]**: If Final-Review is still `needs_fixer: true` after the fixer pass, record remaining gaps as BLOCKED and proceed to Step 7. Looping back to dispatch the fixer again is a constraint violation.
  Solution: The re-read checkpoint at Step 6 entry is the enforcement reminder.

- **[refactor only for L/XL]**: Refactor is dispatched at most once per task, and only for L/XL tasks when review-agent signals `refactor_signal`. M tasks treat "packaged confirm (quality)" as advisory — no refactor dispatch, task marks ✅.
  Solution: Check `task_classification` before dispatching refactor-mode impl-agent.

- **[Red gate ⚠️ vs impl failure ❌]**: ⚠️ means the test was already passing before impl started — wrong test design. This is not a failure_count increment; it is an immediate BLOCKED with escalation. Do not retry impl.
  Solution: The ⚠️ / ❌ branch in §4b Phase 2 is explicit; re-read before handling impl-agent status.

- **[merge branch deletion]**: Use `git branch -D` (force delete), never `git branch -d`. The execute branch was pushed but not PR-merged, so `-d` fails.
  Solution: Always `-D` for `execute/{date}-{slug}/{group}` branches.

- **[task-map.md missing during merge]**: merge-agent needs to know which impl-checklist files exist. If task-map.md was not written in Step 3 before starting Step 4, merge-agent cannot verify coverage. Step 3 must complete fully before Step 4 begins.
  Solution: The Step 2 / Step 3 "Done when" gates enforce ordering.

---

## Constraints

- Analyze spec directory is read-only across all steps; hooks intercept any write attempts.
- All Task Tools are created in Step 2 before any implementation starts.
- Each task passes through review-agent for every impl attempt.
- Gitworktrees are created for any parallel execution (L/XL); removed in Step 7 after final-report.md is written.
- final-fixer-agent is dispatched at most once per session.
- smart-friend-agent is dispatched at most once per task (when failure_count reaches 2).
- compile errors do not increment failure_count.
- All user-visible output is Traditional Chinese (繁體中文).
- Working files go under `.claude/execute/{date}-{slug}/execute/`.

---

## Error Reference

| Condition | Detection point | Action |
|-----------|-----------------|--------|
| Spec dir missing | Step 0 | Stop; tell user to run /analyze |
| Spec file missing | Step 0 | List gaps; escalate; stop |
| Red gate not passed ⚠️ | §4b Phase 2 | BLOCKED (wrong test); escalate |
| Compile error ❌ | §4b Phase 2 | Retry; does NOT count toward failure_count |
| Impl failure (correctness/judgment) | §4b Phase 3 | failure_count++; retry |
| failure_count == 2 | §4b escalation | Dispatch smart-friend; retry |
| failure_count == 3 | §4b escalation | BLOCKED |
| Spec contradiction | review-agent output | BLOCKED; escalate |
| Merge semantic conflict ❌ | §4d | BLOCKED downstream; escalate |
| Merge Green broken × 3 | §4d | BLOCKED downstream; escalate |
| E2E fails | Step 5 | e2e-fix-agents (one cluster per agent); one re-run |
| E2E still fails after fix | Step 5 | Record ❌; continue to Step 6 |
| Final-Review needs_fixer: true | Step 6 | final-fixer once; one re-review |
| Final-Review still needs_fixer: true | Step 6 | Record remaining gaps as BLOCKED; proceed |
| Write attempt to analyze dir | All steps | Immediate structural blocker; escalate |
