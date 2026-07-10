---
name: execute
description: "Implements a medium-to-large /analyze spec end-to-end — TDAID orchestrator: reads the spec, drives Summarize→Impl→Review loops via subagents, runs E2E + Final-Review, writes final-report.md. Use when a completed /analyze spec exists. Trigger On '/execute', '開始執行', '跑 execute', '依照 analyze 執行'. Not for: tasks with no /analyze spec (implement directly) or worth/value judgments (use /think)."
argument-hint: "<spec-dir-path>"
user-invocable: true
---

Long-running orchestration engine for medium-to-large tasks. This body is English (agent-facing). All user-visible output is **Traditional Chinese (繁體中文)**.

## Outcome Contract

- **Outcome**: Every task in the /analyze spec is executed through the Summarize → Impl → Review TDAID loop and the run is fully reported.
- **Done when**: `.claude/execute/{date}-{slug}/execute/final-report.md` exists, every registered task ended ✅ / blocked / cascade-blocked, and the Step 6 Final-Review coverage result is recorded in it.
- **Evidence**: final-report.md carries the {N}/{M} REQ achievement rate and the blocked list; all session worktrees removed.
- **Output**: Working documents plus `final-report.md` under `.claude/execute/{date}-{slug}/execute/`.
- **Automation**: ultracode=overlap, loop=drivable（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）
  In the same non-interactive pass, read `references/loop-pauses.md` for this skill's own PAUSE classification.

## Goal

Read an `/analyze` spec directory. Execute every task through a Summarize → Impl → Review TDAID loop with subagent context isolation. Run E2E tests and Final-Review. Write `final-report.md`. Never stop early — if a task is blocked, escalate and continue unblocked work.

---

## Hard Constraints

These apply across all steps. The review-agent rule and the spec-read-only rule are the two most commonly violated — they are the first things to re-read at Steps 4, 5, and 6 entry after any auto-compact.

- **The review ROLE is never optional; its host varies by mode.** Every task — documentation, scripts, config, code — goes through review-agent after each impl-agent attempt (in serial-absorbed mode the orchestrator hosts the role — Step 0 — still mandatory, mechanical gates still enforced). `TaskUpdate status=completed` is only reachable as the result of a review outcome for the current impl attempt. Marking a task ✅ without the review role having run first is a constraint violation.
- **Analyze spec directory is read-only.** Never Edit or Write any file under `.claude/analyze/`; hooks intercept any write attempts. Any execution path that attempts this must stop immediately and escalate as a structural blocker.
- **Subagent depth = 1.** Agents in `agents/*.md` are stateless leaf nodes. They do not dispatch further subagents. Being dispatched as a subagent does NOT disable this skill's own worker fan-out whenever a subagent-dispatch tool (Agent / Task-dispatch) is present — presence is decided by the Step 0 tool-list probe (inspection, never attempt-and-catch). When NO dispatch tool exists, the run enters **serial-absorbed** mode (defined in Step 0) instead of blocking. The depth=1 rule governs the leaf agents this skill dispatches (they never dispatch further), NOT this dispatcher's own ability to fan out its summarize/impl/review Tasks. Fan-out is never gated behind an AskUserQuestion proxy.
- **All Task Tools created before execution begins.** Register every group × task via TaskCreate in Step 2. No mid-execution task creation.
- **Working files live under `.claude/execute/`.** Edit and Write are only permitted in the execute working directory.
- **goal.md criteria are the top acceptance authority.** requirement.md / test.md operationalizations are means, not the finish line: when they under-specify a goal.md 驗收標準 (C{n}), the criterion's literal wording wins. A criterion satisfied only inside test scaffolding while its production path stays inert is NOT met (see the [latent-defect disclosure trap] gotcha). Step 6 cross-checks every C{n} against its literal wording.
- **Process artifacts are a closed list.** The only working documents this skill writes are: confirm.md, task-map.md, impl-checklist-{group}.md, context/*-ctx.md, and final-report.md (plus task-registry.md only when Task tools are unavailable). Do not invent additional per-task self-review / telemetry / coverage documents — review evidence lives in the checklist fields and final-report.md. Runs that absorb agent roles (serial-absorbed mode — Step 0) get no extra artifacts beyond this list; in such a single-context run, context/*-ctx.md may be terse — the eight field headers with file/line pointers instead of copied prose — since it exists for post-compaction re-read resilience, not for a subagent reader.
- **Goal-Alignment Filter is hard governance.** `failure_count` accounting is affected by the filter (off-goal findings are downgraded to advisory and do not increment the counter), but findings tied to an acceptance-criterion direct failure (驗收標準直接失敗) are protected by the hard invariant — they keep their original tier and still increment `failure_count`.
- **Worktree lifecycle.** Worktrees are created for any parallel execution (L/XL) **only when git is available**; removed in Step 7 after final-report.md is written. When the project has no git repo, or any `git worktree add` fails, the run degrades one-way to in-place serialized execution (see §4a) — a missing git repo never blocks tasks and never wedges the session.
- **final-fixer-agent is dispatched at most once per session.**
- **smart-friend-agent is dispatched at most once per task** (when failure_count reaches 2).
- **Error Reference.** When any step hits an error condition not covered by an inline Fallback, read `references/error-reference.md` and apply the matching condition → action row (condition / detection point / action lookup table, all steps). If no row matches, do not improvise: mark the affected task blocked with the verbatim error, escalate 「未涵蓋的錯誤：{condition}，該任務已標記 blocked」, and continue unblocked work per the Goal line.

### Orchestration interface (dual-mode)

When — and only when — the run is Workflow-driven or a system-reminder confirms
ultracode, read `references/orchestration-interface.md` before Step 0 and apply
its adapter contract; on the default interactive path, skip the read and write
no mode record — the absence of a mode record means the current (subagent-loop)
adapter. Detection is explicit system-reminder confirmation only, never inferred.
On the Workflow path, pin the mode into confirm.md at Step 0, never switch
adapters mid-run, and re-apply the dispatch contract at Step 4 entry.

---

## Step 0 — Design.md soft-read + Spec Validation

### Design.md soft-read

Before spec validation, check for a DESIGN.md at the project root:
1. Run `git rev-parse --show-toplevel 2>/dev/null`. If the command fails or returns empty,
   skip silently — no error output.
2. If `{root}/DESIGN.md` exists, read it into context and output one line in Traditional Chinese:
   「已載入 DESIGN.md，視覺規格已參考」
3. If absent, skip silently. Non-blocking.

### Git availability probe

Run `git rev-parse --show-toplevel 2>/dev/null` in the project root. Record `git_available: true|false` into confirm.md. When false, also record `execution_mode: degraded-in-place` and output one line: 「偵測不到 git repo：L/XL 將降級為就地序列執行（無 worktree、無 merge point）」. A missing git repo is NEVER a stop condition — the run proceeds; only the worktree/merge machinery is skipped.

### Dispatch-tool probe

Inspect the tool list once, here at Step 0: is a subagent-dispatch tool (Agent / Task-dispatch) present? Inspection only — never attempt-and-catch. Record `dispatch_available: true|false` in confirm.md; when false, also record `execution_mode: serial-absorbed` and output one line: 「無 subagent 派遣工具：進入 serial-absorbed 模式（保留 worktree/merge 機制，角色由 orchestrator 吸收）」.

**serial-absorbed semantics**: classification, worktrees, §4d merge points, and Step 7 cleanup are ALL retained. Groups at the same frontier level process serially in document order (logged in task-map.md). Agent roles are absorbed by the orchestrator — absorption is sanctioned ONLY in this mode — with their artifacts still produced and their MECHANICAL gates still enforced: green_proof Bash verification, red_proof capture, checklist fill. The loss of reviewer independence is disclosed in final-report.md. Never a stop condition.

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
| ≥ 4 | XL | 4 (serialize excess per wave) | 4 worktrees |
| 2–3 | L | width count | worktree per group |
| 1 | M | 1 | none (main branch) |

When the DAG allows ≥ 2 groups at the same level, run them in parallel — do not serialize L-class groups sequentially, except under §1d file-overlap or serial-absorbed mode (dispatch absent, Step 0) — both logged. For XL waves with > 4 groups, pick the first 4 by document order; remainder wait for the next wave.

**1d. Pre-scan for file conflicts.** For group pairs in the same frontier level, scan their `步驟` sections for identical file paths. Overlap is defined as: the two groups' `步驟` sections name at least one identical normalized file path (exact string match after trimming whitespace and resolving relative-path prefixes against the repo root). When that condition holds: serialize those two groups (move the later one to the next level), record reason in task-map.md.

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
- `.claude/execute/{date}-{slug}/execute/task-map.md` — maps Task Tool IDs to groups and checklist files, and records each task's `test_weight` (full | riding, per the §4b tier rule) decided NOW — before any dispatch. Gate-time only: a weight may change later solely via an explicit re-decision logged at that task's dispatch time; classifying weights retroactively after implementation is a constraint violation (post-hoc rationalization, not a decision). Template: `references/output-formats.md §task-map.md`.
- `.claude/execute/{date}-{slug}/execute/impl-checklist-{group}.md` (one per group) — copies `驗收標準` items from each task in `task-{group}.md`, adds blank `Review 結果:` and `備註:` fields. Template: `references/output-formats.md §impl-checklist`.

**Done when:** task-map.md and all impl-checklist files written.

---

## Step 4 — TDAID Loop

> **Re-read checkpoint:** Before entering Step 4, re-read §Hard Constraints and this entire step. Confirm review-agent dispatch is mandatory, `failure_count`/`compile_error_count` semantics (§4b Phase 2–3), cascade-blocked propagation (§4c), and merge retry cap (§4d). These are the rules most vulnerable to drift during long sessions.

> **Status-mapping rule:** The Task tool status enum has no blocked state. Every `TaskUpdate: status=blocked|cascade-blocked` below means: keep `status=in_progress` and set metadata `{state: blocked|cascade-blocked, reason}`; task-map.md and final-report.md remain the authoritative blocked record. Do not create new tasks for blockers (Hard Constraint: no mid-execution TaskCreate).

### 4a. Execution order + worktrees

Process groups by frontier level (topological order). Groups at the same level run in parallel (serially in document order under serial-absorbed mode — Step 0; worktrees and §4d merge points unchanged).

For **M**: single workflow, main branch. No worktrees.

For **L/XL**: worktrees require `git_available: true` (Step 0 probe). If git is unavailable, or any `git worktree add` below exits non-zero: do NOT retry and do NOT block the wave — degrade the whole run, one-way, to **in-place serialized execution**: process every group sequentially in topological document order in the main working directory with M-mode semantics (no worktrees, no §4d merge points), record `execution_mode: degraded-in-place` plus the failing command's verbatim output in confirm.md, and continue the TDAID loop unchanged. Announce once: 「worktree 不可用，已降級為就地序列執行」.

Otherwise (git available): BEFORE running the first `git worktree add`, record `target_branch = $(git branch --show-current)` (fallback `main` if empty/detached) and the wave's worktree-registry rows into confirm.md — every later merge targets this recorded value, never a hardcoded name, and a crash between adds must never leave a worktree invisible to Step 7's registry-iterating cleanup. Then create the wave's worktrees before dispatching any impl-agent for that wave, strictly in this per-group order: registry row written in confirm.md → run the add → verify exit 0 → next group:
```bash
git worktree add .claude/worktrees/execute-{date}-{slug}-{group} -b execute/{date}-{slug}/{group}
```

Never place worktree checkouts under `.git/worktrees/` — that directory is git's own per-worktree metadata store; a checkout there shares its directory with git's HEAD/index/commondir files, so the tree is permanently dirty and a Step 7 WIP `git add -A` would commit git internals.

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

**Test-weight tier (orchestrator decides per task, before the first dispatch)**: a task whose 步驟 only wire existing behavior — thin pass-through forwarders, module registration, re-exports, config plumbing — takes the **coverage-riding path** (`test_weight: riding`): impl-agent writes no new per-task tests when every 驗收標準 item is already semantically pinned by a named test elsewhere in the suite (same session or pre-existing); the pinning tests must be named per criterion in the impl report and in `green_proof.tests_correspondence`, and review-agent verifies that correspondence. Any task that gives birth to new observable behavior — new logic, new state, new user-visible output — takes the full Red gate → Green path (`test_weight: full`). When in doubt, full. This is the 輕重 rule: the prove-red ritual is spent where behavior is born; wiring rides on the named pinning tests plus the Step 5 E2E net.

```
failure_count = 0
compile_error_count = 0  # consecutive compile-error ❌ returns; reset by any other return

LOOP:
  Dispatch impl-agent with:
    - ctx_path:            context/{group}-{task-id}-ctx.md
    - worktree_path:       group worktree path (or null for M)
    - test_weight:         full | riding  (per the tier rule above; default full)
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
    # Compile errors do NOT count toward failure_count — but they are capped on
    # their own channel at EVERY failure_count level, so a deterministic compile
    # error can never retry unbounded.
    compile_error_count += 1
    if compile_error_count >= 3:
      Mark task BLOCKED (reason: 3 consecutive compile errors)
      TaskUpdate: status=blocked
      escalate to user: 「TASK-{group}-NN blocked：連續 3 次 compile error」
      break LOOP
    continue LOOP  # retry without incrementing failure_count

  compile_error_count = 0   # any non-compile-error return breaks the consecutive chain
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

**Pre-SWITCH guard — verify green_proof**: mandatory before entering the SWITCH below or marking any task ✅. Full verify procedure and FAIL handling (failure_count accounting, finding injection, re-dispatch): `references/green-proof-verify.md`. PASS → enter the SWITCH; FAIL → follow that file's failure path and skip the SWITCH this round.

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

**Per-task commit**: immediately after a task marks ✅ (any SWITCH path above), commit that task's changes in its working tree with a conventional message — `feat|fix|refactor({group}): TASK-{group}-NN {title}`. One task = one commit: red/green checkpoints stay bisectable and mid-run work is never lost to a crash. Never batch multiple ✅ tasks into one commit.

**Goal-Alignment Filter** (applies to: `packaged confirm (correctness)`, `needs judgment`)

Full procedure — applicability gate, finding-level loop, hard invariant (an 驗收標準直接失敗 finding must not be downgraded), semantic-coverage decision criterion, and re-tier post-step — lives in `references/goal-alignment-filter.md` and is authoritative for `failure_count` accounting in this sub-step. Follow it; its outcome routes to either task ✅ (all findings downgraded to advisory) or the failure escalation logic below (`failure_count += 1`).

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

**Composite `correction_strategy`**: schema and assembly rules (paired broader-guidance markers, `investigate_files` pass-through, `agents/impl-agent.md` 通用原則 5 field coupling) in `references/correction-strategy.md` — build it from smart-friend output exactly as specified there before the next impl dispatch.

### 4c. Cascade-blocked propagation

After each task is marked BLOCKED, evaluate group-level status:
- A group is **group-blocked** if ANY of its tasks is BLOCKED.

For each downstream group G where `前置群組` contains at least one group that is group-blocked OR already cascade-blocked: mark G **cascade-blocked**. TaskUpdate all G's tasks to cascade-blocked. Re-evaluate until no group changes state (fixpoint) — propagation is transitive: a group depending only on a cascade-blocked group is itself cascade-blocked.

Record direct-blocked vs cascade-blocked separately in final-report.

### 4d. Merge Point (L/XL only)

Skipped entirely on a degraded in-place run (`execution_mode: degraded-in-place`): work already lives in the main working directory — record `integration_status[{group}] = in-place` for each all-✅ group in task-map.md and proceed to the next frontier level.

After all tasks in a frontier level complete (✅, blocked, or cascade-blocked):

```
merge_retry_count = 0
last_failed_tests = null

LOOP:
  Dispatch merge-agent with:
    - worktree_paths:  list of worktree paths for this level — ONLY groups whose tasks are all ✅; direct-blocked and cascade-blocked groups' worktrees are excluded from the dispatch and recorded integration_status[{group}] = not-integrated (branches kept per Step 7's guard), so expected-red partial work cannot poison the level merge
    - target_branch:   the recorded target_branch from confirm.md (see §4a)
    - test_command:    from test.md
    - failed_tests:    last_failed_tests (null on first dispatch)

  CASE merge-agent status == ✅:
    record integration_status[{group}] = integrated to task-map.md for each group in this level
    proceed to next frontier level
    break

  CASE merge-agent status == ❌  (semantic conflict):
    record integration_status[{group}] = not-integrated to task-map.md for each group in this level
    escalate to user immediately with conflict_details
    mark all pending downstream groups BLOCKED (reason: merge conflict)
    record in final-report blocked list
    break

  CASE merge-agent status == ⚠️  (Green broken):
    last_failed_tests = merge-agent failed_tests
    merge_retry_count += 1
    if merge_retry_count >= 3:
      record integration_status[{group}] = not-integrated to task-map.md for each group in this level
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

If E2E passes → record ✅ in final-report together with an `e2e_evidence` block: the exact command run, its exit_code, the collected/passed test counts parsed from the output, and a verbatim output tail. A ✅ without this block is a claim, not a confirmation. Exit 0 with 0 tests collected, or counts that cannot be parsed from the output, is NOT a pass — record ❌ and enter the failure path below.

If E2E fails:
1. Group independent failure clusters (one per failing feature area; if boundaries unclear, one cluster per failing test)
2. Dispatch one **e2e-fix-agent** per cluster in parallel, with: `e2e_failure_report` (that cluster's error messages, failing case names, stack traces), `e2e_strategy` (the E2E 測試策略 section excerpted from test.md), `relevant_files` (paths of the code files implicated by the failing stack/case)
3. Re-run E2E (Monitor)
4. Passes → ✅. Still fails → record ❌ with details in final-report blocked section; proceed to Step 6.

**Done when:** E2E result recorded (✅ / ❌ / skipped).

**Fallback:** If Monitor is unavailable, run via Bash and parse output. If E2E command produces no output after 5 minutes, record as ❌ timeout.

---

## Step 6 — Final-Review + Final-Fixer

> **Re-read checkpoint:** Before entering, confirm: final-fixer runs exactly once, never twice.

Dispatch **final-review-agent** with:
- `requirement_path`: path to requirement.md
- `goal_path`: path to goal.md
- `test_dir`: parse from test.md integration/E2E sections; default to `tests/`
- `e2e_evidence`: the Step 5 e2e_evidence block plus the current tree state (`git rev-parse HEAD` and whether `git status --porcelain` is empty), so the agent can decide whether that suite run is current and reusable

The Coverage Report has two mandatory parts: (1) per-REQ coverage as before, and (2) a **goal-criteria cross-check** — every C{n} in goal.md judged against its LITERAL wording (displayed fields, persistence semantics, production effectiveness), each with evidence. A criterion that passes only inside test scaffolding while its production path is inert (a PRAGMA / feature flag / wiring the real entry point never sets) is ❌. `needs_fixer: true` when any REQ **or any C{n}** is ❌.

If `needs_fixer: false` → record conclusion in final-report; proceed to Step 7.

If `needs_fixer: true`:
1. Dispatch **final-fixer-agent** with: `coverage_report`, `requirement_excerpts` (full text of ❌ REQ-XXX entries), `design_excerpts` (design.md sections relevant to ❌ REQs), `goal_excerpts` (verbatim goal.md 驗收標準 text of each ❌ C{n} row plus the cross-check's inert-mechanism evidence)
2. After fixer completes, dispatch final-review-agent again (same inputs)
3. If `needs_fixer: false` → proceed to Step 7
4. If still `needs_fixer: true` → record remaining gaps in final-report blocked section; proceed to Step 7. **Do not invoke fixer again.**

Advisory notes from Coverage Report → record in final-report; do not trigger fixer.

**Done when:** Final-review result recorded (✅ / gaps listed).

---

## Step 7 — final-report.md + Cleanup

Write `.claude/execute/{date}-{slug}/execute/final-report.md`. Template: `references/output-formats.md §final-report.md`.

When emitting the report:
- If an upstream work journal exists (`.claude/think/*.html` for the approved plan; `.claude/review/*.html` when the spec was handed off via a review deliverable), read `../_shared/output-journal.md` and append this run's off-spec decisions / forced changes / tradeoffs to its 執行日誌 section per that contract, then SendUserFile the updated journal. Journal selection when several exist: pick the one whose slug matches the plan/spec this run traces to; if no slug matches unambiguously, pick the most recently modified journal and open the appended entry with 「（自動選定最近修改的 journal）」 — never fan out the append to multiple journals.

Remove all worktrees created this session, iterating the confirm.md worktree registry (a degraded in-place run has an empty registry — skip this whole block silently). The worktree-remove is safe only because dirty not-integrated worktrees are WIP-committed first (below) — after that it discards a checkout, not committed work. The branch force-delete is **integration-state-gated**: `git branch -D` is irreversible and would silently discard any commits that never reached main, so it runs **only** for a group whose work is confirmed integrated (`in-place` groups have no session branch — nothing to delete).

If a `git worktree remove --force` exits non-zero: run `git worktree prune`; if the directory still exists, fall back to `rm -rf {path}` **only** when the path is recorded in this session's registry AND lies under `.claude/worktrees/` — then `git worktree prune` again. If it still fails, append 「worktree 清理失敗：{path}，請手動處理」 to final-report.md and continue — cleanup failure never wedges the session.

For each session group's worktree — if the group's `integration_status` is not `integrated`, first run `git -C .claude/worktrees/execute-{date}-{slug}-{group} status --porcelain`; if dirty, commit the WIP onto the group's kept branch (`git -C .claude/worktrees/execute-{date}-{slug}-{group} add -A && git -C .claude/worktrees/execute-{date}-{slug}-{group} commit -m "WIP: blocked partial work"`) so the retained branch actually preserves it — then:
```bash
git worktree remove .claude/worktrees/execute-{date}-{slug}-{group} --force
```
Then decide per group whether to force-delete its branch by reading the `integration_status[{group}]` field recorded in task-map.md by §4d:
- **Integrated (force-delete allowed)**: task-map.md records `integration_status[{group}] = integrated` (work landed on the recorded target_branch). Only then run:
  ```bash
  git branch -D execute/{date}-{slug}/{group}
  ```
- **Not integrated (do NOT delete)**: the group ended direct-blocked (§4b), cascade-blocked (§4c), or task-map.md records `integration_status[{group}] = not-integrated` (work never integrated into main). Skip the `git branch -D` for that group, keep the branch, and record one line in final-report:
  「保留未合併分支 execute/{date}-{slug}/{group}（{原因}），未強制刪除」

`-D` (force) is still required — never `-d` — when deletion is allowed: an integrated execute branch was pushed but not PR-merged, so `-d` fails. The integration-state guard above only decides *whether* to delete; it never relaxes `-D` to `-d`.

After all session worktrees are removed, remove the now-empty parent: `rmdir .claude/worktrees 2>/dev/null` — ignore failure (non-empty means other worktrees live there).

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
  Solution: Re-read §Hard Constraints before marking any task ✅.

- **[loaded-orchestrator self-review trap]**: When execute runs in a context already holding the spec (e.g. inline after a think→analyze chain), the orchestrator rationalizes absorbing subagent roles — writing and reviewing in its own polluted context because the ceremony "feels redundant when I already understand the task". Honest boundary (see /think Stage E "Mechanism necessity"): this gotcha is prose inside the same path that fails, so it can be skipped like any other — it raises the cost and names the move, it does not mechanically prevent it; real prevention removes the trigger (do not invoke execute inline; hand off to a fresh session) or gates verifier dispatch outside the orchestrator's cognition.
  Solution: When dispatch IS available (Step 0 probe), any subagent bearing a verification function must run in a fresh-context subagent; the orchestrator may never substitute itself. In serial-absorbed mode (dispatch absent) the substitution is sanctioned but evidence-gated — the mechanical green_proof/red_proof gates are precisely what compensates for the lost independence. The review ROLE is never optional; its host varies by mode. Context-loading roles (summarize) may be absorbed only by still producing their artifact for downstream agents to read.

- **[compile error vs failure_count]**: After impl-agent returns ❌ with a compile error, `failure_count` must NOT increment. Counting compile errors as failures triggers smart-friend early and wastes the retry budget on syntax issues. The exclusion is not a license for unbounded retries: `compile_error_count` increments on every consecutive compile-error ❌ (any other return resets it) and blocks the task at 3.
  Solution: Only `failure_count++` on review-agent "packaged confirm (correctness)" or "needs judgment" returns; cap compile errors on their own counter.

- **[latent-defect disclosure trap]**: Implementation reveals a pre-existing defect that makes an acceptance criterion production-inert — tests pass only because test scaffolding enables what production never does (a PRAGMA, a feature flag, a missing wire in the real entry point). The orchestrator rationalizes "out of scope" and settles for disclosing it in final-report while the criterion marks ✅. Disclosure alone never converts to ✅.
  Solution: If the minimal fix sits inside the task's already-touched modules and is small (single-digit lines), it IS part of the task — inject a finding and fix it with a test in the current TDAID loop. Otherwise mark the affected task blocked (reason: latent defect blocks C{n}) and escalate. The Step 6 goal-criteria cross-check is the backstop.

- **[final-fixer one-pass cap]**: If Final-Review is still `needs_fixer: true` after the fixer pass, record remaining gaps as BLOCKED and proceed to Step 7. Looping back to dispatch the fixer again is a constraint violation.
  Solution: The re-read checkpoint at Step 6 entry is the enforcement reminder.

- **[refactor only for L/XL]**: Refactor is dispatched at most once per task, and only for L/XL tasks when review-agent signals `refactor_signal`. M tasks treat "packaged confirm (quality)" as advisory — no refactor dispatch, task marks ✅.
  Solution: Check `task_classification` before dispatching refactor-mode impl-agent.

- **[Red gate ⚠️ vs impl failure ❌]**: ⚠️ means the test was already passing before impl started — wrong test design. This is not a failure_count increment; it is an immediate BLOCKED with escalation. Do not retry impl.
  Solution: The ⚠️ / ❌ branch in §4b Phase 2 is explicit; re-read before handling impl-agent status.

- **[merge branch deletion]**: Use `git branch -D` (force delete), never `git branch -d`. The execute branch was pushed but not PR-merged, so `-d` fails. This applies only when the branch is eligible for deletion — see the integration-state guard in Step 7: a branch whose work never reached main (direct-blocked, cascade-blocked, or merge ❌/⚠️) is kept, not deleted.
  Solution: Always `-D` for `execute/{date}-{slug}/{group}` branches that are integrated; do not delete branches that are not integrated.

- **[task-map.md missing during merge]**: the orchestrator's §4d `integration_status` bookkeeping and the Step 7 branch-deletion guard both read task-map.md. If task-map.md was not written in Step 3 before starting Step 4, those records have nowhere to live and Step 7 cannot tell integrated branches from blocked ones. Step 3 must complete fully before Step 4 begins.
  Solution: The Step 2 / Step 3 "Done when" gates enforce ordering.

- **[goal-alignment over-filter trap]**: When the Goal-Alignment Filter downgrades all reviewer-initiated off-goal findings to advisory, an acceptance-criteria failure finding can be misclassified as off-goal and silently downgraded too. That collapses back to the [review-agent bypass trap] failure mode — the task marks ✅ while a 驗收標準直接失敗 finding was suppressed.
  Solution: The hard invariant is the floor — a finding that traces to an 驗收標準直接失敗 keeps its original tier and still increments `failure_count`. review-agent's 「逐條核對驗收標準」 is the supporting check that keeps the invariant honest; never let the filter run without it.
