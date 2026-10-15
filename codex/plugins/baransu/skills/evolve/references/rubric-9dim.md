# rubric-9dim — the fixed selection environment

This rubric is the **selection environment**: it stays constant across every round of an evolution run. The target SKILL.md is the gene; the rubric is what selects for fitness. Never edit this file mid-run — a moving rubric makes scores incomparable across rounds and the ratchet stops being a ratchet.

Total = 100 points across 9 dimensions, on two axes. **Structure axis** (dims 1–6) is scored by static reading of the SKILL.md text. **Effectiveness axis** (dims 7–9) requires *output* — produced by real-exec (running the skill on benchmark prompts) or, when real-exec is gated off, by offline replay against the yardstick (see `safety-gates.md` for the real-exec/offline decision and `output-contract.md` for how offline evidence is labelled).

Effectiveness is weighted higher than structure on purpose: a beautifully-written skill that performs badly is still a bad skill.

The structure axis scores **decisions a reader gets right**, never the number of rules on the page. Length is a cost on this axis (dim 6 aside, which scores gates): two versions that encode the same decisions tie on every dimension except Economy, where the shorter one wins.

## Structure axis (static — 48 pts)

| # | Dimension | Weight | Scores high when… |
|---|-----------|--------|-------------------|
| 1 | **Trigger Clarity** | 8 | frontmatter `description` carries unambiguous trigger phrases AND explicit "not-for" boundaries; the skill fires on the right intents and stays silent on the wrong ones |
| 2 | **Stage Coherence** | 8 | body stages are ordered, each anchored to the previous; no orphan step, no forward reference to an undefined stage |
| 3 | **Failure-Mode Encoding** | 8 | the failure paths that matter are handled by the principle that covers their class — one `if <condition> then <recovery>` at the boundary where the condition is decided — not by a case list that grows one entry per incident, and not by a vague "be careful" |
| 4 | **Actionable Specificity** | 8 | directives are concrete and state the rule, not its history; hedge words ("consider", "as appropriate", "use judgment", "be flexible", "if needed") are absent or pinned to a decision rule; a directive that needs a paragraph to justify itself scores mid — the paragraph is a symptom |
| 5 | **Economy** | 8 | every clause changes a decision the reader would otherwise get wrong; no clause restates another clause's decision or rationale, defends against a failure another clause already covers, or contradicts another clause (a contradiction caps this dimension at half); between two versions that encode the same decisions, the shorter scores higher |
| 6 | **High-Risk Action Discipline** | 8 | destructive operations (`rm`, `git reset --hard`, force push, secret handling, irreversible writes) are explicitly gated or forbidden, not left implicit |

## Effectiveness axis (requires output — 52 pts)

| # | Dimension | Weight | Scores high when… |
|---|-----------|--------|-------------------|
| 7 | **Goal Attainment** | 20 | following the skill on benchmark prompts actually produces the stated outcome |
| 8 | **Output Fidelity** | 18 | produced output matches the declared contract — format, language, required sections, structure |
| 9 | **Robustness** | 14 | off-road / edge / adversarial benchmark prompts are handled gracefully, not silently mishandled |

## Related clusters (do not optimize one in isolation)

- **{3, 4, 5}** — Failure-Mode Encoding and Actionable Specificity pull toward explicitness; Economy pulls toward fewer words. The tension is deliberate: an added `if-then` (dim 3) pays for its words on dim 5 unless it displaces a clause, and a deletion that drops a decision pays on dim 3 or 4. When a mutation lands in this cluster, the judge MUST score all three — a gain in one that quietly degrades a sibling is not a strict improvement.
- **{7, 8}** — Goal Attainment and Output Fidelity correlate: output that does not match the contract usually also misses the goal.

## Scoring protocol

- Each dimension is scored on its own 0→weight scale; the round score is the weighted sum (0–100).
- **Vacuous-compliance case (dim 6)**: a skill with no destructive-action surface at all scores **full marks** on High-Risk Action Discipline — there is nothing ungated, so absence of risk is compliance, not a gap. Do not score it mid. (Dims 1–5 have no vacuous case: a skill always has a description, stages, failure paths, directives, and words to assess.)
- A mutation is a **strict improvement** only if total score rises AND no individual dimension regresses below its pre-mutation value (a net-positive trade that tanks one dimension is not strict — it is a different design, not an improvement). Because Economy scores length, a version that keeps every decision and drops words is a strict improvement; a version that adds a rule without displacing one is not, unless the rule changes a decision worth more than its words.
- Effectiveness dims (7–9) carry an evidence label inherited from the run mode: `real-exec` or `offline-同源` (single-axis; see `output-contract.md`). Offline-derived effectiveness scores are advisory, not hard evidence.

## Provenance

Dimensions 3, 4, 6 are concept-aligned with the public state of the art (failure-mechanism encoding, actionable specificity, high-risk-action discipline) but the dimension names, definitions, scoring language, and weights here are independently authored. Dimension 5 (Economy) is concept-aligned with the subtraction principles in cursor/plugins `pstack` (MIT) — laziness protocol, subtract-before-you-add, "keep only prose that changes a decision" — in original wording. Dimensions 1, 2, 7, 8, 9 are independently derived from baransu's own skill conventions. See `provenance.md` for the per-item clean-room record.
