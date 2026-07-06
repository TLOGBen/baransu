# loop-pauses — /review PAUSE classification

PAUSE classification for non-interactive drivers; semantics in ../../_shared/loop-contract.md §2.

| Interaction point | Class | Non-interactive default |
|---|---|---|
| Stage 1 target pinning — AskUserQuestion when no target can be materialized from disk | Input | Report `no progress: no materializable target` and end the run |
| Stage 7 「Packaged confirm」 — batch diff presented once for confirmation | Input | Do NOT apply the batch; list it in the report as pending-confirm.「此處採預設：不套用，留待人工確認」 |
| Stage 1.5 domain grounding — AskUserQuestion when sources for the transition table are insufficient | Input | Do not ask; treat as sources-insufficient: skip domain-reviewer dispatch, the Domain grounding missing hard stop hits, and the report must not claim domain coverage. A driving context may pre-supply source paths to avoid this outcome |
| Stage 7 「Needs judgment」 — batched AskUserQuestion for logic / boundary / API / behavior / security findings, including hard-stops-sweep pinned findings | **Authorization** | Hard stop. Return verdict 「需判斷」 to the driver with the findings; never auto-apply behavior changes |
