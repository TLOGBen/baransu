# loop-pauses — /review PAUSE classification

Per-skill PAUSE classification for non-interactive drivers. The cross-cutting
vocabulary and semantics live in `../../_shared/loop-contract.md` (§1 vocabulary,
§2 PAUSE semantics, §3 hard stops); this file enumerates only /review's own
interaction points. Re-verify when this skill's SKILL.md changes its interaction
points.

| Interaction point | Class | Non-interactive default |
|---|---|---|
| Stage 7 「Packaged confirm」 — batch diff presented once for confirmation | Input | Do NOT apply the batch; list it in the report as pending-confirm.「此處採預設：不套用，留待人工確認」 |
| Stage 7 「Needs judgment」 — batched AskUserQuestion for logic / boundary / API / behavior / security findings, including hard-stops-sweep pinned findings | **Authorization** | Hard stop. Return verdict 「需判斷」 to the driver with the findings; never auto-apply behavior changes |
