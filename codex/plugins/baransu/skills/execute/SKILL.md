---
name: execute
description: 'TDAID orchestration engine for medium-to-large tasks built from /analyze
  spec. Reads a spec directory, builds a dependency DAG, drives each task group through
  Summarize→Impl→Review TDAID loops via subagents, runs E2E and Final-Review, and
  writes final-report.md. Triggers: ''/baransu:execute'', ''execute the plan'', ''run
  the spec'', ''implement the analyze result'', ''開始執行'', ''跑 execute'', ''依照 analyze
  執行''.'
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
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
- **Goal-Alignment Filter is hard governance.** `failure_count` accounting is affected by the filter (off-goal findings are downgraded to advisory and do not increment the counter), but findings tied to 驗收標準直接失敗 are protected by the hard invariant — they keep their original tier and still increment `failure_count`.

---

## Step 0 — Design.md soft-read + Spec Validation

### Design.md soft-read

Before spec validation, check for a DESIGN.md at the project root:
1. Run `git rev-parse --show-toplevel 2>/dev/null`. If the command fails or returns empty,
   skip silently — no error output.
2. If `{root}/DESIGN.md` exists, read it into context and output one line in 繁中:
   「已載入 DESIGN.md，視覺規格已參考」
3. If absent, skip silently. Non-blocking.

### Spec Validation

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
    - correction_strategy: composite object {text, investigate_files} when
                           failure_count == 2 (built from smart-friend output;
                           see "Composite correction_strategy" note below).
                           Omit on rounds 1–2.

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

**Pre-SWITCH guard — verify green_proof**: 在進入下方 SWITCH、`mark task ✅` 之前，主 skill
必須先 verify review-agent 回報的 `green_proof` 欄位符合 `agents/review-agent.md` §3 的 5-tier
必填矩陣。verify 規則：

```
verify_green_proof(review_result):
  # Step 1 — existence check applies to ALL tiers (including direct fix).
  # 4 keys 必須在 schema 中存在（值的語義由 tier 決定，但 key 本身不可省）。
  REQUIRE green_proof.test_command          key present
  REQUIRE green_proof.exit_code             key present (value 為整數)
  REQUIRE green_proof.output_tail           key present
  REQUIRE green_proof.tests_correspondence  key present
  IF any REQUIRE fails:
    return FAIL, reason="green_proof key missing"

  # Step 2 — tier-specific value check.
  IF review_result.tier == "direct fix":
    # direct-fix tier 允許 4 個 value 為 "n/a"/0/""/"n/a"；不再驗 value 內容
    return PASS
  ELSE:
    # advisory / packaged confirm (quality|correctness) / needs judgment 必填實 test
    REQUIRE green_proof.test_command          non-empty AND != "n/a"
    REQUIRE green_proof.tests_correspondence  non-empty AND != "n/a"
    REQUIRE green_proof.exit_code == 0        # else Green failed, not a passed review
    REQUIRE green_proof.output_tail           non-empty
    IF any REQUIRE fails:
      return FAIL, reason="green_proof incomplete or exit_code != 0"
    return PASS
```

verify 結果處理：
- `PASS` → 進入下方 SWITCH，照原邏輯 routing。
- `FAIL` → review 視為失敗：**直接跳過 Goal-Alignment Filter**（因 verify-fail 注入的
  finding 是 process-level、既不對應 task 驗收標準也不對應 task 目標，若送入 filter 會被
  誤判為 off-goal observation 而 downgrade 至 advisory，導致 task 在無實 test 證據下被
  mark ✅；此漏洞由本段顯式處理）。直接走以下路徑：
    1. `failure_count += 1`（verify-fail 計入 task-level failure_count，與 §4b Phase 2
       的 compile-error 排除規則不同——compile error 走 `compile_error_count`、不計入；
       verify-fail 是 review-stage 的 process 失敗、計入 failure_count）。
    2. 附加 finding `{citation: "green_proof", observation: "<verify reason>", fix:
       "重派 review-agent 並要求附完整 green_proof"}` 到 review_result.findings。
    3. 重派 impl-agent + review-agent（接 §4b Phase 2 retry 邏輯：第 1 次重試直接
       重派；第 2 次失敗觸發 smart-friend 補上 correction_strategy）。
    4. 不進下方 SWITCH，本輪 Phase 3 結束。

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
    # → first run the Goal-Alignment Filter sub-step below; failure_count
    #   accounting happens AFTER the filter has had a chance to downgrade
    #   off-goal findings.
    → go to Goal-Alignment Filter sub-step below
```

**Goal-Alignment Filter** (applies to: `packaged confirm (correctness)`, `needs judgment`)

Applicability gate. This sub-step runs ONLY when the SWITCH above landed on
`packaged confirm (correctness)` or `needs judgment`. For `advisory`,
`direct fix`, and `packaged confirm (quality)` the filter is **skipped**
and the original SWITCH outcome stands unchanged.

Purpose. review-agent is a finding-producing perspective; governance lives
here. Some findings reviewer raises are **off-goal observations** (style,
unrelated polish) that should not block the task. The filter walks each
finding and decides whether it serves `ctx.md → Task.目標` / corresponds
to a `Task.驗收標準` failure. Off-goal findings are downgraded to advisory
and do not contribute to `failure_count`.

Finding-level loop:

```
# Initial counter accumulation: every finding observed feeds the metric.
total_findings_count += len(findings)

FOR each finding F in review.findings:
  # Step 1 — does F correspond to a 驗收標準 failure (semantic coverage)?
  is_acceptance_failure = semantic_match(F.observation, ctx.Task.驗收標準)
  # Step 2 — does F serve Task.目標?
  serves_goal           = semantic_match(F.observation, ctx.Task.目標)

  IF is_acceptance_failure:
    # Hard invariant — see below. F keeps its original tier; never downgraded.
    F.downgraded_to_advisory = false
  ELIF serves_goal:
    # On-goal but not acceptance-bound: keep original tier.
    F.downgraded_to_advisory = false
  ELSE:
    # Off-goal observation. Downgrade to advisory.
    F.downgraded_to_advisory = true
    downgraded_to_advisory_count += 1
END FOR
```

**Hard invariant — 驗收標準直接失敗 finding 不可 downgrade 為 advisory.**
Any finding whose observation corresponds to a 驗收標準直接失敗
(`is_acceptance_failure == true`) **不可**被 goal-alignment 邏輯
downgrade 為 advisory；該 finding 維持原 tier，並依原邏輯計入
`failure_count`。invariant 是 R2 的下界，不是建議。

Filter 判斷準則：以驗收標準語意覆蓋範圍判斷，而非字面引用編號。若
finding 的 observation 描述了某個失敗條件，而 `Task.驗收標準` 任一
條目的語意涵蓋此條件，即視為「對應驗收標準直接失敗」並受 invariant
保護 — 即使 finding 文字不只字面引用驗收標準編號（例如 finding 寫
「authentication middleware 未掛載」、驗收標準寫「endpoint 必須要求
授權」即構成語意覆蓋）。

Post-step — review-level tier 重新計算 (re-tier):

```
# After all findings have been classified, recompute the review-level tier.
remaining = [F for F in review.findings if not F.downgraded_to_advisory]

IF every F in review.findings was downgraded to advisory  (remaining is empty):
  # All findings off-goal → review-level tier 改 advisory；task 走 ✅ 路徑。
  review_tier = "advisory"
  failure_count is NOT incremented   # filter absorbed the failure
  mark task ✅
  TaskUpdate: status=completed
  break LOOP

ELSE:
  # At least one finding survives (acceptance failure or on-goal). Keep
  # original tier (correctness / judgment) for routing.
  failure_count += 1
  → go to failure escalation logic below
```

`total_findings_count` and `downgraded_to_advisory_count` are the source
of truth for the matching `goal_alignment_filter_metric` block in Step 7's
`final-report.md`; both counters live across the task's full TDAID loop
and are emitted at report time.

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
      - ctx_path:          context/{group}-{task-id}-ctx.md
      - worktree_path:     group worktree path (or null for M)
      - failure_summary_1: review findings from attempt 1
      - failure_summary_2: review findings from attempt 2
    # smart-friend returns {root_cause, correction_strategy, spec_issue,
    # investigate_files, broader_guidance}. Orchestrator builds the composite
    # correction_strategy for the next impl dispatch as described in
    # "Composite correction_strategy" below.
    continue LOOP

  continue LOOP  # failure_count == 1: retry with review findings
```

**Composite `correction_strategy`** (built by orchestrator from smart-friend output for the next impl dispatch):

```
correction_strategy:
  text: |
    [broader guidance from smart-friend]
    {smart-friend.broader_guidance}
    [/broader guidance]

    {smart-friend.correction_strategy}
  investigate_files: {smart-friend.investigate_files}   # passed through as-is; absent → []
```

Rules:
- `broader_guidance` is **prepended** to `text` wrapped in the paired markers
  `[broader guidance from smart-friend]` ... `[/broader guidance]` so newlines
  or special characters in the over-scope note cannot bleed into the body.
  Both markers MUST appear (paired); never emit one without the other.
- If `smart-friend.broader_guidance` is empty (`""` or absent), still wrap the
  empty string with the paired markers — downstream parsing relies on the pair.
- `investigate_files` is forwarded verbatim; orchestrator does not filter it.
- This composite schema is consumed by **`agents/impl-agent.md` 通用原則 5
  (`correction_strategy`)**, which mandates Read-before-Red-gate on every
  path in `investigate_files`. Field names here MUST match that schema
  exactly; any drift is a cross-file invariant violation.

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

When emitting the report:
- 將 §4b Phase 3 累加的 `total_findings_count` 與 `downgraded_to_advisory_count` 寫入 `## Goal-Alignment Filter Metric` 段（即 `goal_alignment_filter_metric` block）。若整個 session 內無任何 review-agent 回傳（counters 從未遞增），兩值皆寫 `0`，metric 段仍須輸出（不得省略）。filter 行為與降級判斷準則維持 §4b Phase 3 定義，本步驟僅做序列化，不重新計算。

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

- **[goal-alignment over-filter trap]**: When the Goal-Alignment Filter downgrades all reviewer-initiated off-goal findings to advisory, an acceptance-criteria failure finding can be misclassified as off-goal and silently downgraded too. That collapses back to the [review-agent bypass trap] failure mode — the task marks ✅ while a 驗收標準直接失敗 finding was suppressed.
  Solution: The hard invariant is the floor — a finding that traces to 驗收標準直接失敗 keeps its original tier and still increments `failure_count`. review-agent 「逐條核對驗收標準」 is the supporting check that keeps the invariant honest; never let the filter run without it.

---

## Constraints

- Analyze spec directory is read-only across all steps; hooks intercept any write attempts.
- All Task Tools are created in Step 2 before any implementation starts.
- Each task passes through review-agent for every impl attempt.
- Gitworktrees are created for any parallel execution (L/XL); removed in Step 7 after final-report.md is written.
- final-fixer-agent is dispatched at most once per session.
- smart-friend-agent is dispatched at most once per task (when failure_count reaches 2).
- compile errors do not increment failure_count.
- failure_count 計算受 Goal-Alignment Filter 影響（off-goal findings 降為 advisory 不計入）；驗收標準失敗 finding 不受 filter 影響（hard invariant）。
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
| Filter downgraded finding to advisory | §4b Phase 3 | 正常路徑；計入 metric，不增 failure_count |
| Invariant violation: 驗收標準失敗 finding 被誤降級 | §4b Phase 3 filter sub-step | Structural blocker; escalate (hard invariant breach) |
