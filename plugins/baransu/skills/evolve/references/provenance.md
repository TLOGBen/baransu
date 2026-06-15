# provenance — clean-room record + optional skillopt boundary

evolve's mechanism is concept-aligned with public prior art (autoresearch-style ratchets, the darwin-skill project, Microsoft's SkillOpt framework). The **ideas** are not copyrightable; the **text** is. The darwin-skill repository ships no LICENSE file, so its prose defaults to all-rights-reserved. evolve therefore re-derives the mechanism in independent wording and copies no source text.

## Clean-room checklist (run at /review time)

For each artifact evolve ships, record one of `獨立得出` (independently derived) or `概念對齊 darwin 但措辭自寫` (concept-aligned, wording original):

| Item | Status |
|------|--------|
| 9-dimension rubric — dimension **names** | 獨立得出 |
| rubric dims 3/4/6 — **concepts** | 概念對齊 darwin 但措辭自寫 |
| rubric dims 1/2/5/7/8/9 | 獨立得出（from baransu skill conventions） |
| rubric scoring language + weights | 獨立得出 |
| result-card fields/layout | 獨立得出（Kami design system, via /book） |
| ratchet / snapshot / keep-restore mechanism | 概念對齊（autoresearch/darwin ratchet）但措辭自寫 |
| blind-judge / diagnostician prompts | 獨立得出 |
| stage structure of SKILL.md | 獨立得出（baransu skill house style） |

No line of darwin-skill prose is reproduced verbatim. If a future review finds substantial textual similarity in any row, rewrite that row's artifact before keeping it.

## Optional skillopt boundary

`skillopt` (Microsoft's validation-gated-edits PyPI package) MAY be used as an underlying engine, but the base engine is **self-written and the default**:

- **Default**: no third-party dependency. evolve runs entirely on its own instruction-based engine.
- **If skillopt is adopted** (only after a spike shows it clearly wins): **pin** the version; on missing package, **gracefully degrade** to the self-written engine (never hard-fail); and disclose it as a third-party supply-chain artifact per `skills/health/SKILL.md` §supply-chain — it runs with the user's privileges.
- baransu "ships no build toolchain" (CLAUDE.md): introducing a runtime PyPI dependency must be a conscious, disclosed, version-pinned choice — not a silent default.
