# loop-pauses — /evolve PAUSE classification

Per-skill PAUSE classification for non-interactive drivers. The cross-cutting
vocabulary and semantics live in `../../_shared/loop-contract.md` (§1 vocabulary,
§2 PAUSE semantics, §3 hard stops); this file enumerates only /evolve's own
interaction points. Re-verify when this skill's SKILL.md changes its interaction
points.

| Interaction point | Class | Non-interactive default |
|---|---|---|
| Stage 0.4 — benchmark ask when the target has no `test-prompts` set | Input | Run structure-axis-only: hard-label dims 7–9 `no-benchmark` (unscored, never assumed), skip Stage 7 held-out validation.「此處採預設：結構軸單軸演化」 |
| Stage 6 — adoption write-back of a kept mutation into the target SKILL.md | **Authorization** | Hard stop (`safety-gates.md` Gate 1). Report `needs input` with the diff + score delta; never auto-write the mutation, regardless of drive context. Diagnosis / mutation-into-scratch / scoring / restore are not PAUSEs and continue automatically |

/evolve is `loop=drivable`: every interaction point above is classified, and an
Authorization PAUSE (adoption) coexists with drivability exactly as in /review.
Its Stage-5 judge panel rides the ultracode=overlap dual adapter
(`orchestration-interface.md`); the depth invariant (judges and the diagnostician
never invoke skills or dispatch further subagents) holds in both adapters.
