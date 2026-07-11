# Orchestration Interface — /review dual-mode dispatch

Single internal interface for the Stage 4 perspective dispatch. Two adapters implement it — the current parallel-Task adapter (§3) and a thin Workflow adapter (§4). Both return findings in the identical shape, so downstream consumers (Stage 6 consolidate + balance check, Stage 7 response tiers) never sense which mode produced them.

## 1. Interface contract

```
dispatch(activated_perspectives, target, claim_checklist, review_goal) → findings[]
```

Inputs per dispatched perspective — identical in both modes; SKILL.md Stage 4 is the single source:

- target content
- the claim checklist (Stage 1) — the Stage 1.6 fact table travels with it to every perspective
- the review goal (Stage 1)
- for domain-reviewer only: the Stage 1.5 domain transition table (a fourth input for that one perspective)

Each returned finding is natural language (not YAML) and carries exactly the fields SKILL.md Stage 4 mandates — that list is the single source; this document cites it and never copies it.

Tier vocabulary is fixed by Stage 7 and applied downstream only: `direct fix` / `packaged confirm` / `needs judgment` / `advisory`. Adapters never assign tiers.

Business rules — perspective lane-keeping (agent files), the balance check, the hard-stops sweep, and four-tier routing — live only in SKILL.md Stages 5–7 and `plugins/baransu/agents/*-reviewer.md`. This document cites them and never copies them.

## 2. Pre-Stage-1 mode pinning (ultracode-confirmed runs only)

This file is read only when the run is Workflow-driven or a system-reminder confirms ultracode (see the SKILL.md pointer). On the default interactive path this file is never read and no mode record exists — the absence of a mode record means the current (parallel-Task) adapter.

When the read does happen, before Stage 1 begins:

1. Detect ultracode via system-reminder confirmation — the session context must explicitly confirm a Workflow-capable environment. Do not infer it from tool names or vibes.
2. Record the pinned mode (`workflow`) to disk in the session's working notes before any dispatch.
3. The mode is pinned for the entire run. Never switch adapters mid-run, even after a partial dispatch failure.
4. Degraded path: if detection is unreliable or ambiguous, use the Workflow adapter only when the user explicitly declares it; otherwise fall back to the current adapter and write no mode record (non-ultracode behavior identical to 1.5.0).

## 3. Current adapter — parallel Tasks

One **parallel Task** per activated perspective, each in a clean context, exactly as SKILL.md Stage 4 specifies. Reviewers do not know about each other and do not coordinate. The adversarial round (Stage 5) runs after all Tasks return — exactly one round.

Depth invariant (restated for this adapter): dispatched perspective agents must not invoke skills or dispatch further subagents — review-agent-style leaves never call `/review`, reviewers do not review each other, and /review never invokes /review.

## 4. Workflow thin adapter — pinned-workflow mode only

When mode pinning (§2) pinned `workflow`, dispatch the same activated perspectives via Workflow `parallel` primitives instead of hand-rolled parallel Tasks. The adapter does exactly two things:

1. **Dispatch**: one parallel branch per activated perspective, passing the same inputs as §1 (including the Stage 1.6 fact table alongside the checklist, and the Stage 1.5 domain transition table for domain-reviewer).
2. **Collect**: gather findings in the §1 shape and hand them to Stage 5/6 unchanged.

Nothing else. No tiering, no balance check, no dedup, no adversarial logic — those stay in the main flow (SKILL.md Stages 5–7).

Depth invariant (restated for this adapter): Workflow-dispatched perspective agents must not invoke skills or dispatch further subagents — no branch may add reviewers, extra rounds, or cross-review.
