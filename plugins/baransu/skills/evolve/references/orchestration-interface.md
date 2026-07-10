# Orchestration Interface — /evolve dual-mode dispatch

Single internal interface for the Stage 5 blind-judge panel. Two adapters implement it — the current parallel-Task adapter (§3) and a thin Workflow adapter (§4). Both return votes in the identical shape, so the keep/restore decision (Stage 5 tally) and adoption gate (Stage 6) never sense which mode produced them.

## 1. Interface contract

```
dispatch(version_alpha, version_beta, rubric, round_parity) → votes[]   // exactly 3 votes
```

Inputs per dispatched judge — identical in both modes (SKILL.md Stage 5):

- the two neutrally-labelled versions (`alpha` / `beta`) as the **mechanically blinded panel copies** at `.claude/evolve/<slug>/panel/round-<N>/{alpha,beta}.md` (SKILL.md Stage 5) — judges receive only these paths, never the live skill path or the scratch path (path names leak which version is the mutation); `round_parity` fixes which label is the mutated one, swapped on odd vs even rounds to cancel position bias, and is never disclosed to judges
- the fixed rubric (`references/rubric-9dim.md`) — the selection environment, never edited mid-run

Each returned vote carries exactly the fields Stage 5 already mandates:

| Field | Meaning |
|-------|---------|
| better | which label the judge prefers (`alpha` / `beta` / `tie`) |
| strict_improvement | boolean — the mutated version strictly improves (total rises AND no dimension regresses) |
| per_dimension_deltas | signed per-dimension change, used to detect cluster-sibling regression ({3,4,5}, {7,8}) |

The keep rule — **keep iff ≥ 2 of 3 `strict_improvement` = true** (tightened to 3 of 3 whenever the round's effectiveness evidence label is `real-exec`, per SKILL.md Stage 5) — is applied by the main flow only. Adapters never tally votes, never keep, never restore, and never write the target file.

Business rules — single-variable mutation, the structure gate (Gate 4), file-level rollback (Gate 2), and the adoption Authorization PAUSE (Gate 1) — live only in SKILL.md Stages 2–6 and `references/safety-gates.md`. This document cites them and never copies them.

## 2. Stage 0 mode pinning (ultracode-confirmed runs only)

This file is read only when the run is Workflow-driven or a system-reminder confirms ultracode (see the SKILL.md pointer) — once, at Stage 0, never re-read before a judge round. On the default interactive path this file is never read and no mode record exists — the absence of a mode record means the current (parallel-Task) adapter.

When the read does happen, before Stage 1 begins:

1. Detect ultracode via system-reminder confirmation — the session context must explicitly confirm a Workflow-capable environment. Do not infer it from tool names or vibes.
2. Record the pinned mode (`workflow`) to disk under `.claude/evolve/<slug>/` before any dispatch.
3. The mode is pinned for the entire run. Never switch adapters mid-run, even after a partial dispatch failure.
4. Degraded path: if detection is unreliable or ambiguous, use the Workflow adapter only when the user explicitly declares it; otherwise fall back to the current adapter and write no mode record (non-ultracode behavior unchanged).

## 3. Current adapter — parallel Tasks

**Three fresh evolve-judge Tasks in parallel** per round, each in a clean context, exactly as SKILL.md Stage 5 specifies. Judges are single-use — never reuse a judge across rounds — and blind to which label is the mutation. The Stage 1 evolve-diagnostician is a separate single dispatch (no fan-out) and is not part of this panel interface.

Depth invariant (restated for this adapter): dispatched judge and diagnostician agents must not invoke skills or dispatch further subagents — they are stateless leaf nodes (depth = 1) that never call any `/baransu:*` skill and never spawn a sub-panel. This constrains only the leaf agents, not evolve's own fan-out when evolve is itself hosted as a subagent — see the fan-out release in SKILL.md Constraints and loop-contract's detection-primitive paragraph.

## 4. Workflow thin adapter — pinned-workflow mode only

When Stage 0 pinned `workflow`, dispatch the same three judges via Workflow `parallel` primitives instead of hand-rolled parallel Tasks. The adapter does exactly two things:

1. **Dispatch**: one parallel branch per judge, passing the same inputs as §1.
2. **Collect**: gather the three votes in the §1 shape and hand them to the Stage 5 tally unchanged.

Nothing else. No tally, no keep/restore, no adoption, no mutation — those stay in the main flow (SKILL.md Stages 5–6). A batch run that evolves several skills may wrap one such per-skill panel per Workflow item, but the per-run vote schema above is unchanged.

Depth invariant (restated for this adapter): Workflow-dispatched judge agents must not invoke skills or dispatch further subagents — no branch may add judges, extra rounds, or a nested panel. As in §3, the leaf-level invariant does not constrain evolve's own fan-out — stated once in SKILL.md Constraints.
