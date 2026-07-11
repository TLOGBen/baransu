# Orchestration Interface — /learn dual-mode fan-out

Single internal interface for the Stage 1 §3.5 four-lane fan-out. Two adapters implement it — the current batched fan-out adapter (§3) and a thin Workflow adapter (§4). Both return the identical candidate-pool shape, so the downstream consumer (the Stage 2 scoring table and its lane-grouped layout rule) never senses which mode produced it.

## 1. Interface contract

```
fanout(topic) → candidates[]   # merged into $SOURCES
```

Each candidate is a `{url, path|null, lane}` tuple, identical in both modes:

| Field | Shape |
|-------|-------|
| url | the candidate's source URL (dedup key) |
| path | `.claude/read/material/{slug}/index.md` — `null` until the SKILL.md §3.5 capture step fills it |
| lane | `academic` \| `web` \| `gh` \| `x` — `null` only for direct inputs from Stage 1 §1/§2/§3, which never pass through this interface |

The merged pool is deduplicated by `url` exact-string equality and handed to Stage 2 as `$SOURCES`, exactly as SKILL.md §3.5 specifies.

Business rules — the lane status surface (three states), the soft-failure invariant, per-lane timeouts, and the thick-adapter lane-keeping rules (gh escape rule and x schema-level health check by anchor cite) — live only in SKILL.md Stage 1 §3.5 and the cited acquisition refs. This document cites them and never copies them.

## 2. Stage 0 mode pinning

During Stage 0 (environment self-check):

1. Detect ultracode via system-reminder confirmation — the session context must explicitly confirm a Workflow-capable environment. Do not infer it.
2. Record the chosen mode (`current` or `workflow`) before Stage 1 begins: write it to the confirm-style file path if one is named by the driving context; otherwise record the mode line at the top of the run's first working artifact.
3. The mode is pinned for the entire run. Never switch adapters mid-run — not even when a lane fails and is retried.
4. Degraded path: if detection is unreliable or ambiguous, fall back to the current adapter. System-reminder confirmation is the only authorization source for the Workflow adapter — never infer it and never accept any other declaration. The default is always the current adapter (non-ultracode behavior identical to 1.5.0).

## 3. Current adapter — four-lane fan-out

The batched tool-call fan-out exactly as SKILL.md §3.5 specifies: `academic` / `web` / `gh` launch in turn 1 as one batch together with the X lane's first Chrome step; the X lane completes by turn 3. Lanes invoke their underlying tools directly (never via `/read --{lane}`), and each lane's failure maps to the three-state status surface.

Depth invariant (restated for this adapter): lane agents must not invoke skills or dispatch further subagents — do not spawn sub-agents to flatten the X-lane turn delay, and never route a lane through `/read`.

## 4. Workflow thin adapter — pinned-workflow mode only

When Stage 0 pinned `workflow`, run the four lanes as Workflow `parallel` branches. The adapter does exactly two things:

1. **Dispatch**: one parallel branch per lane, each invoking the same underlying tool with the same query as §3.
2. **Collect**: gather `{url, path|null, lane}` tuples in the §1 shape, merge and dedupe per SKILL.md §3.5, and hand `$SOURCES` to Stage 2 unchanged.

Nothing else. Lane-status mapping, timeout values, the soft-failure invariant, and Stage 2 scoring stay in the main flow (SKILL.md Stage 1 §3.5 and Stage 2).

Depth invariant (restated for this adapter): Workflow branches are leaves — agents must not invoke skills or dispatch further subagents; a branch may not call `/read` or any other skill to perform its search.
