# loop-pauses — /evolve PAUSE classification

Per-skill PAUSE classification for non-interactive drivers. The cross-cutting
vocabulary and semantics live in `../../_shared/loop-contract.md` (§1 vocabulary,
§2 PAUSE semantics, §3 hard stops); this file enumerates only /evolve's own
interaction points. Re-verify when this skill's SKILL.md changes its interaction
points.

| Interaction point | Class | Non-interactive default |
|---|---|---|
| Stage 0.4 — benchmark ask when the target has no `test-prompts` set | Input | Run structure-axis-only: hard-label dims 7–9 `no-benchmark` (unscored, never assumed), skip Stage 7 held-out validation.「此處採預設：結構軸單軸演化」 |
| Stage 6 — adoption write-back of a kept mutation into the target SKILL.md | **Authorization (standing-authorizable)** | WITH a standing authorization in the driving context (loop/cron prompt or approved plan explicitly authorizes adoption / the evolve→ship sweep): auto-adopt, but only for changes clearing all Gate-1 preconditions — structure gate pass, blind-judge bar **3/3** (not 2/3), snapshot retained, `log.md` audit `decision: standing-auth auto-adopt`; failing changes are restored. `make test` is the final go/no-go for downstream steps. WITHOUT standing authorization (e.g. bare `/ultracode`): hard stop, report `needs input`, never auto-write. Diagnosis / mutation-into-scratch / scoring / restore are not PAUSEs and continue automatically |

/evolve is `loop=drivable`: every interaction point above is classified, and an
Authorization PAUSE (adoption) coexists with drivability exactly as in /review.
Its Stage-5 judge panel rides the ultracode=overlap dual adapter
(`orchestration-interface.md`); the depth invariant (judges and the diagnostician
never invoke skills or dispatch further subagents) holds in both adapters.
