# Orchestration Interface — /execute dual-mode dispatch

Single internal interface for the Step 4 TDAID per-task agent dispatch. Two adapters implement it — the current subagent-loop adapter (§3) and a thin Workflow adapter (§4). Both return the identical review-agent shape, so downstream consumers (the §4b Phase 3 SWITCH, the Goal-Alignment Filter, and `failure_count` accounting) never sense which mode produced it. This is an annotation layer only: the TDAID subagent loop logic in SKILL.md §4b is not modified.

## 1. Interface contract

```
dispatch(task) → review_result   # fixed sequence: summarize → impl → review
```

The unit of dispatch is one task's agent sequence (summarize-agent → impl-agent → review-agent), with the per-agent inputs SKILL.md §4b already defines. The return value is the review-agent result, unchanged and mode-invariant:

| Field | Shape |
|-------|-------|
| tier | one of the five tiers: `direct fix` / `advisory` / `packaged confirm (quality)` / `packaged confirm (correctness)` / `needs judgment` |
| findings[] | citation + observation + fix (the shape the Goal-Alignment Filter walks) |
| green_proof | the 4 mandatory keys per `agents/review-agent.md` §3: `test_command`, `exit_code`, `output_tail`, `tests_correspondence` |
| refactor_signal | boolean, consumed by the §4b quality-tier branch |
| spec_contradiction | false or details, consumed by failure escalation |

**Goal-Alignment Filter consumption contract**: the filter walks `review.findings` exactly as returned. Field names, tier vocabulary, and `green_proof` keys are mode-invariant, so the pre-SWITCH `verify_green_proof` gate, the hard invariant (驗收標準 findings never downgraded), and `failure_count` accounting in SKILL.md §4b Phase 3 apply unchanged in both modes.

Business rules — `failure_count` / `compile_error_count` accounting, smart-friend trigger at 2, 3-strike BLOCKED, cascade-blocked propagation, merge retry caps — live only in SKILL.md §4b–§4d. This document cites them and never copies them.

## 2. Stage 0 mode pinning

At Step 0 (alongside spec validation):

1. Detect ultracode via system-reminder confirmation — the session context must explicitly confirm a Workflow-capable environment. Do not infer it.
2. Record the chosen mode (`current` or `workflow`) into `confirm.md` before Step 1 begins.
3. The mode is pinned for the entire run. Never switch adapters mid-run — not between frontier levels, not after a blocked task.
4. Degraded path: if detection is unreliable or ambiguous, use the Workflow adapter only when the user explicitly declares it. The default is always the current adapter (non-ultracode behavior identical to 1.5.0).

## 3. Current adapter — subagent loop

The orchestrator-driven loop exactly as SKILL.md §4b specifies: dispatch summarize-agent, impl-agent, and review-agent as stateless leaf Tasks per task, groups at the same frontier level in parallel (L/XL via gitworktrees), merge points per §4d. All routing (SWITCH, filter, escalation) happens in the orchestrator after collection.

Depth invariant (restated for this adapter): subagent depth = 1 — dispatched agents must not invoke skills or dispatch further subagents; review-agent never calls `/baransu:review`, and impl-agent never spawns its own helpers.

## 4. Workflow thin adapter — pinned-workflow mode only

When Step 0 pinned `workflow`, express the same dispatch as Workflow primitives: a `pipeline` of summarize → impl → review per task, and `parallel` across same-frontier-level groups. The adapter does exactly two things:

1. **Dispatch**: run the pipeline with the same per-agent inputs as §1.
2. **Collect**: return the review-agent result in the §1 shape to the orchestrator unchanged.

Nothing else. The Phase 3 SWITCH, `verify_green_proof`, the Goal-Alignment Filter, `failure_count` accounting, smart-friend dispatch, and merge logic stay in SKILL.md §4b–§4d untouched — the pipeline never short-circuits them.

Depth invariant (restated for this adapter): pipeline steps are leaf agents — agents must not invoke skills or dispatch further subagents; no step may add review rounds, self-dispatch, or mark tasks ✅ on its own.
