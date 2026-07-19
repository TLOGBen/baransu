# Execution Pipeline — run the spec to green (large band)

The execution half of `/analyze` (formerly the standalone `/execute` skill,
merged 2026-07 after the harness×model matrix experiment; the R8 reform cuts
the rituals the experiment condemned — summarize-agent dispatch, per-task ctx
files, the blocking Red-gate ritual, retry depth — and keeps the four proven
mechanisms: worktree parallel groups, the compile-error-excluded failure
counter, coverage-riding dispatch, and the merge / e2e-fix / final-fixer
closing agents). This body is English (agent-facing); all user-visible output
is **Traditional Chinese (繁體中文)**.

Entry: `/analyze` Stage 8 (execution handoff) reads this file and drives it,
in the same session (single-group spec) or a fresh session (multi-group spec).

## Goal

Read the `/analyze` spec directory. Execute every task through an
Impl → Review loop with subagent context isolation. Run E2E and Final-Review.
Write `final-report.md`. Never stop early — if a task is blocked, escalate and
continue unblocked work.

## Hard Constraints

- **The review ROLE is never optional; its host varies by mode.** Every task — documentation, scripts, config, code — goes through review-agent after each impl-agent attempt (serial-absorbed mode: the orchestrator hosts the role, mechanical gates still enforced). `TaskUpdate status=completed` is only reachable as the result of a review outcome for the current impl attempt.
- **Analyze spec directory is read-only during execution** — with ONE sanctioned exception: the R7 loose-criterion patch path (§4b Phase 2) may append a criteria patch to goal.md ONLY via the orchestrator, logged in final-report.md. Leaf agents never write the spec dir.
- **Subagent depth = 1.** Agents in `agents/*.md` are stateless leaf nodes; they never dispatch further subagents. Dispatch-tool presence is decided by the Step 0 tool-list probe (inspection, never attempt-and-catch); when absent, enter serial-absorbed mode.
- **All Task Tools created before execution begins** (Step 2). No mid-execution task creation.
- **Working files live under `.claude/execute/`.** (Directory name kept across the merge — it names the execution phase, and /ship's archive rules key on it.)
- **goal.md criteria are the top acceptance authority.** A criterion satisfied only inside test scaffolding while its production path stays inert is NOT met. Step 6 cross-checks every C{n} against its literal wording.
- **Process artifacts are a closed list**: confirm.md, task-map.md, impl-checklist-{group}.md, final-report.md (plus task-registry.md only when Task tools are unavailable). No per-task ctx files — the handoff is the spec itself.
- **Goal-Alignment Filter is hard governance** (`references/goal-alignment-filter.md`): off-goal findings downgrade to advisory and do not increment `failure_count`; findings tied to an 驗收標準直接失敗 keep their tier and count.
- **Worktree lifecycle**: worktrees for parallel execution (L/XL) only when git is available; removed in Step 7. No git, or any `git worktree add` failure → one-way degrade to in-place serialized execution (§4a) — never blocks, never wedges.
- **final-fixer-agent at most once per session; smart-friend-agent at most once per task.**
- **Error Reference**: `references/error-reference.md` is the condition → action lookup for anything not covered inline. No row matches → mark the task blocked with the verbatim error and continue unblocked work.

### Orchestration interface (dual-mode)

When — and only when — the run is Workflow-driven or a system-reminder
confirms ultracode, read `references/orchestration-interface.md` before Step 0
and apply its adapter contract; on the default interactive path, skip the read
and write no mode record — no mode record means the subagent-loop adapter.

## Step 0 — Probes + Spec Validation

1. **Git availability probe**: `git rev-parse --show-toplevel 2>/dev/null`. Record `git_available: true|false` in confirm.md; false → also `execution_mode: degraded-in-place`, announce 「偵測不到 git repo：L/XL 將降級為就地序列執行」. Never a stop condition.
2. **Dispatch-tool probe** (inspection only): record `dispatch_available: true|false`; false → `execution_mode: serial-absorbed`, announce 「無 subagent 派遣工具：進入 serial-absorbed 模式」. Serial-absorbed retains classification, worktrees, merge points, cleanup; roles are absorbed by the orchestrator with their MECHANICAL gates still enforced (green_proof Bash verification, checklist fill); reviewer-independence loss is disclosed in final-report.md. Both probes false → degraded-in-place subsumes.
3. **Spec validation**: spec dir exists; `goal.md`, `requirement.md`, `design.md`, `test.md`, ≥1 `task-{group}.md` present. Derive `{date}-{slug}` from the spec dir name; write confirm.md at `.claude/execute/{date}-{slug}/execute/confirm.md` (template: `references/output-formats.md`). Missing dir → 「找不到 Analyze spec 目錄，請先跑 /baransu:analyze 的規格階段」, stop. Missing files → list, escalate, stop.

Every logged gate result carries its value inline (exit code, counts) as a
contemporaneous, self-contained line.

## Step 1 — Dependency Analysis + Classification

Build the group DAG from each task file's `前置群組` field; BFS topological
sort; classify by max parallel frontier width: ≥4 → XL (4 worktrees, excess
serialized per wave), 2–3 → L (worktree per group), 1 → M (main branch, no
worktrees). Same-level groups run in parallel except under file-overlap
pre-scan (two groups' 步驟 name an identical normalized path → serialize,
record reason in task-map.md) or serial-absorbed mode. Malformed `前置群組` →
assume no predecessors, note in task-map.md. Update confirm.md.

## Step 2 — Task Tool Creation

Register every group × task via TaskCreate before any implementation. The
Task tool status enum has no blocked state: `status=blocked|cascade-blocked`
below means keep `in_progress` + set metadata `{state, reason}`; task-map.md
and final-report.md are the authoritative blocked record.

## Step 3 — Work Document Initialization

- `task-map.md` — Task Tool ID ↔ (group, task) mapping + each task's `test_weight` (full | riding) decided NOW, before any dispatch. Gate-time only: retroactive weight classification is a constraint violation. (Template: `references/output-formats.md`.)
- `impl-checklist-{group}.md` — one per group; copies 驗收標準 items, blank `Review 結果:` / `備註:` fields.

## Step 4 — Impl → Review loop

> Re-read checkpoint: before entering, re-read §Hard Constraints and this
> step — review dispatch is mandatory; `failure_count` / `compile_error_count`
> semantics; cascade-blocked propagation; merge retry cap.

### 4a. Execution order + worktrees

Process groups by frontier level. M: main branch. L/XL: before the wave's
first `git worktree add`, write ALL of the wave's worktree-registry rows plus
`target_branch = $(git branch --show-current)` (fallback `main`) into
confirm.md; then:

```bash
git worktree add .claude/worktrees/execute-{date}-{slug}-{group} -b execute/{date}-{slug}/{group}
```

Never place checkouts under `.git/worktrees/` (git's own metadata store — a
checkout there is permanently dirty and `git add -A` would commit git
internals). Any add failure → one-way degrade to in-place serialized
execution (M semantics, no merge points), record verbatim output in
confirm.md, announce once. Sharing the main tree's build cache
(e.g. `CARGO_TARGET_DIR`) is permitted; log it as a build-env decision.

### 4b. Per-task loop

No summarize phase and no ctx files (R8): dispatch impl-agent directly with
spec references.

**Phase 1 — Impl** (tests + implementation)

Test-weight tier (from task-map.md, decided at Step 3): wiring-only tasks ride
on named pinning tests (`test_weight: riding`); tasks that birth new
observable behavior take the full test-first path. When in doubt, full.

```
failure_count = 0
compile_error_count = 0   # consecutive compile-error ❌; reset by any other return

LOOP:
  Dispatch impl-agent with:
    - spec_dir:            the /analyze spec directory path
    - task_ref:            {task_file_path, task_id}   # agent reads 目標/驗收標準/步驟 directly
    - goal_path:           goal.md path (criteria authority + Verbatim Constants source via design.md)
    - design_path:         design.md path (layer table + Verbatim Constants block)
    - worktree_path:       group worktree path (or null for M)
    - test_weight:         full | riding
    - refactor_mode:       false (true only when review signals it)
    - correction_strategy: composite object when smart-friend has run (see below); else omit

  CASE status == ⚠️ (test already passing before impl):
    # R8: Red gate is advisory, not a blocker. Record the ⚠️ as an advisory
    # finding for the reviewer (test may pin existing, not new, behavior);
    # proceed to Phase 2 review of the delivered implementation.
    note advisory "red-gate ⚠️: {detail}" → attach to the review dispatch
    compile_error_count = 0            # non-compile return resets the consecutive counter
    → proceed to Phase 2

  CASE status == ❌ AND failure detail mentions compile error:
    compile_error_count += 1            # excluded from failure_count (kept invariant)
    if compile_error_count >= 3:
      Mark task BLOCKED (3 consecutive compile errors); TaskUpdate; escalate; break LOOP
    continue LOOP

  compile_error_count = 0
  → proceed to Phase 2
```

**Phase 2 — Review** (mandatory; never mark ✅ without it)

Dispatch **review-agent** with: `impl_result`, `task_ref` (acceptance-criteria
source), `checklist_path`, `worktree_path`, `task_classification`, plus the
spec's design.md path for the R6 verbatim-constant byte-diff. review-agent's
job description (R6 four-point order + R7 loose-criterion escalation) lives in
`agents/review-agent.md`.

**Pre-SWITCH guard — verify green_proof** (mandatory):
`references/green-proof-verify.md`. PASS → SWITCH; FAIL → that file's failure
path, skip the SWITCH this round.

```
SWITCH review_tier:
  CASE "direct fix" | "advisory":
    mark task ✅; TaskUpdate completed; break LOOP
  CASE "packaged confirm (quality)":
    if (L or XL) AND review.refactor_signal:
      Dispatch impl-agent refactor_mode=true (not counted), re-review once;
      second tier quality-or-better → ✅; correctness/judgment → failure path
    else: treat as advisory → ✅
  CASE "packaged confirm (correctness)" | "needs judgment":
    → Goal-Alignment Filter (references/goal-alignment-filter.md);
      all findings downgraded → ✅, else → failure escalation below
```

**Per-task commit**: immediately after ✅, commit in the task's working tree —
`feat|fix|refactor({group}): TASK-{group}-NN {title}`. One task = one commit.

**R7 loose-criterion patch path**: when review returns a correctness finding
citing BOTH a real defect AND a too-loose criterion, the orchestrator appends
the criteria patch to goal.md (sole sanctioned spec write), logs it in
final-report.md, and the re-dispatch judges against the patched criterion.

**Failure escalation** (correctness/judgment, post-filter):

```
  if review.spec_contradiction != false:
    Mark task BLOCKED (spec contradiction); escalate; break LOOP

  failure_count += 1

  if failure_count >= 2:
    # R8 retry cap: one review-rejection re-dispatch per task.
    reason = "impl failed twice (retry cap 1)"
    if smart_friend_output defined AND smart_friend_output.spec_issue != false:
      reason += "；smart-friend 診斷：" + smart_friend_output.spec_issue
    Mark task BLOCKED (reason); TaskUpdate; escalate; break LOOP

  # failure_count == 1: the single retry gets the best possible ammunition —
  # dispatch smart-friend-agent NOW (at most once per task) with the failure
  # summary; build the composite correction_strategy per
  # references/correction-strategy.md; then continue LOOP.
  Dispatch smart-friend-agent (task_ref, worktree_path, failure_summary)
  continue LOOP
```

### 4c. Cascade-blocked propagation

A group is group-blocked if ANY task is BLOCKED. Downstream groups whose
`前置群組` contains a blocked or cascade-blocked group become cascade-blocked;
iterate to fixpoint. Record direct- vs cascade-blocked separately in
final-report.

### 4d. Merge Point (L/XL only; skipped on degraded-in-place)

After a frontier level completes: dispatch **merge-agent** with the all-✅
groups' worktree paths (blocked groups excluded, recorded
`integration_status = not-integrated`), the recorded `target_branch`, the
test command from test.md, and `failed_tests` from the previous attempt
(null first). ✅ → record `integrated`, next level. ❌ semantic conflict →
escalate, downstream BLOCKED. ⚠️ Green broken → retry; at 3 → escalate,
downstream BLOCKED.

## Step 5 — E2E

Read test.md's E2E startup command (Monitor for long-running; Bash for
seconds-fast suites). No command → record 「E2E 跳過」, proceed. Pass →
record ✅ WITH an `e2e_evidence` block (exact command, exit_code, parsed
counts, verbatim output tail) — exit 0 with 0 tests collected is NOT a pass.
Fail → cluster failures, dispatch one **e2e-fix-agent** per cluster in
parallel, re-run once; still failing → record ❌, proceed to Step 6.

## Step 6 — Final-Review + Final-Fixer

Dispatch **final-review-agent** with requirement_path, goal_path, test_dir,
design_path (for the R9 whole-tree verbatim-constant byte-diff and the R4
surface-inventory audit), and the Step 5 e2e_evidence block + current tree
state. The Coverage Report carries: per-REQ coverage; the goal-criteria
cross-check (every C{n} against its LITERAL wording — test-scaffolding-only
satisfaction is ❌); the R9 constant byte-diff result; the surface-inventory
audit (every row's pinning test exists, is green, pins the REAL call path).

`needs_fixer: true` → dispatch **final-fixer-agent** once (coverage_report +
requirement/design/goal excerpts), re-run final-review once. Still true →
record remaining gaps as BLOCKED, proceed. **Never a second fixer pass.**

## Step 7 — final-report.md + Cleanup

Write final-report.md (template: `references/output-formats.md`). If an
upstream work journal exists (`.claude/think/*.html` / `.claude/review/*.html`),
append this run's off-spec decisions per `../../_shared/output-journal.md` and
SendUserFile it (slug match; ambiguous → most recent, annotated).

Remove all session worktrees by iterating the confirm.md registry. Dirty
not-integrated worktrees are WIP-committed first
(`git -C {wt} add -A && git -C {wt} commit -m "WIP: blocked partial work"`).
Then `git worktree remove {wt} --force`; failure → `git worktree prune` →
scoped `rm -rf` (registry-recorded path under `.claude/worktrees/` only) →
prune again; still failing → note in final-report, continue. Branch deletion
is integration-state-gated: `git branch -D execute/{date}-{slug}/{group}`
ONLY when task-map.md records `integration_status = integrated`; blocked /
not-integrated branches are kept and noted. `-D` never relaxes to `-d`
(pushed-but-unmerged branches make `-d` fail). Finally
`rmdir .claude/worktrees 2>/dev/null` (ignore failure).

Output (繁體中文): completion block with spec_dir, {N}/{M} REQ achievement,
final-report path, blocked list. When hosted as a subagent with a mandated
final-text shape, record the block verbatim in final-report.md instead.

## Gotchas

- **[review bypass trap]**: doc/script/config tasks "have nothing to test" — review-agent still runs; it verifies checklist acceptance criteria, not just unit tests.
- **[loaded-orchestrator self-review trap]**: when dispatch IS available, any verification role runs in a fresh-context subagent — the orchestrator never substitutes itself. Serial-absorbed substitution is sanctioned but evidence-gated by the mechanical green_proof gate.
- **[compile error vs failure_count]** (kept invariant): compile errors NEVER increment `failure_count` — they cap on their own `compile_error_count` channel at 3. Only review-rejection returns increment `failure_count` (cap 2 under R8).
- **[latent-defect disclosure trap]**: a criterion green only via test scaffolding while production is inert is NOT met. Small in-scope fix → fold into the task; else BLOCKED. Disclosure alone never converts to ✅. Step 6 is the backstop.
- **[red-gate ⚠️ is advisory, not a block]** (R8): a test passing before impl is evidence the test may pin existing behavior — it travels to the reviewer as an advisory finding and R6's untested-surface scan decides; it no longer blocks the task by itself.
- **[refactor only for L/XL]**: at most once per task, only on `refactor_signal`. M treats quality-tier as advisory.
- **[merge branch deletion]**: `-D` not `-d`, and only for integrated groups.
- **[task-map.md missing during merge]**: Step 3 must complete before Step 4 — §4d bookkeeping and Step 7's deletion guard both read it.
- **[goal-alignment over-filter trap]**: the hard invariant is the floor — an 驗收標準直接失敗 finding keeps its tier and counts, always.
