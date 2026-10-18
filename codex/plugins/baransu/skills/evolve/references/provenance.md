# provenance — clause provenance, clean-room record, optional skillopt boundary

evolve's mechanism is concept-aligned with public prior art (autoresearch-style ratchets, the darwin-skill project, Microsoft's SkillOpt framework). The **ideas** are not copyrightable; the **text** is. The darwin-skill repository ships no LICENSE file, so its prose defaults to all-rights-reserved. evolve therefore re-derives the mechanism in independent wording and copies no source text.

## Clause provenance — recovering why a clause exists

The diagnostician's finding names the problem the implicated clause was originally added to solve. Recover it in this order and record the source; stop at the first hit:

1. **The clause's own text** — a rationale, a cited incident, a "because" — `source: rationale-in-text`.
2. **This run's or a previous run's `log.md`** under `.codex/evolve/<slug>/` — the round that introduced or last replaced the clause carries its finding — `source: log.md round N`.
3. **Repository history** — `git log -S '<distinctive phrase>' -- <target path>` and the CHANGELOG entry the commit points to — `source: git/CHANGELOG <ref>`.
4. **Unknown** — `source: unknown`. The replacement must still solve whatever failure the clause visibly handles; an unknown origin is not a licence to delete.

A clause whose origin problem no longer exists (the mechanism moved into a verifier gate, the stage it guarded was removed) is replaced by `delete` with the carrier named.

## Clean-room checklist (run at $baransu:review time)

For each artifact evolve ships, record one of `獨立得出` (independently derived) or `概念對齊 darwin 但措辭自寫` (concept-aligned, wording original):

| Item | Status |
|------|--------|
| 9-dimension rubric — dimension **names** | 獨立得出 |
| rubric dims 3/4/6 — **concepts** | 概念對齊 darwin 但措辭自寫 |
| rubric dims 1/2/7/8/9 | 獨立得出（from baransu skill conventions） |
| rubric dim 5 Economy + the finding shape (implicated clause / origin / replacement) | 概念對齊 cursor/plugins pstack（MIT：laziness protocol、subtract-before-you-add、reflect 的 already-covered／decision-changing 準則）但措辭自寫 |
| rubric scoring language + weights | 獨立得出 |
| result-card fields/layout | 獨立得出（via $baransu:draw page lane） |
| ratchet / snapshot / keep-restore mechanism | 概念對齊（autoresearch/darwin ratchet）但措辭自寫 |
| blind-judge / diagnostician prompts | 獨立得出 |
| seed hunt (three seeds from one brief, blind pick, refine the winner only) | 獨立得出（baransu `$baransu:draw` 7.6.0 seed-hunt 的做法，措辭自寫） |
| phenomenon → impact → root → bedrock → verification chain; four operations with evidence; blind known-answer exam taken twice, noise band, cost in the keep bar, case-term gate, decision ledger, falsification by cost without result, checkpoint return | 獨立得出（baransu review 基石迭代，2026-10-17～18） |
| stage structure of SKILL.md | 獨立得出（baransu skill house style） |

No line of darwin-skill or pstack prose is reproduced verbatim. If a future review finds substantial textual similarity in any row, rewrite that row's artifact before keeping it.

## Optional skillopt boundary

`skillopt` (Microsoft's validation-gated-edits PyPI package) MAY be used as an underlying engine, but the base engine is **self-written and the default**:

- **Default**: no third-party dependency. evolve runs entirely on its own instruction-based engine.
- **If skillopt is adopted** (only after a spike shows it clearly wins): **pin** the version; on missing package, **gracefully degrade** to the self-written engine (never hard-fail); and disclose it as a third-party supply-chain artifact per `skills/health/SKILL.md` §supply-chain — it runs with the user's privileges.
- baransu "ships no build toolchain" (CLAUDE.md): introducing a runtime PyPI dependency must be a conscious, disclosed, version-pinned choice — not a silent default.
