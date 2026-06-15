# rubric-9dim — the fixed selection environment

This rubric is the **selection environment**: it stays constant across every round of an evolution run. The target SKILL.md is the gene; the rubric is what selects for fitness. Never edit this file mid-run — a moving rubric makes scores incomparable across rounds and the ratchet stops being a ratchet.

Total = 100 points across 9 dimensions, on two axes. **Structure axis** (dims 1–6) is scored by static reading of the SKILL.md text. **Effectiveness axis** (dims 7–9) requires *output* — produced by real-exec (running the skill on benchmark prompts) or, when real-exec is gated off, by offline replay against the yardstick (see `safety-gates.md` for the real-exec/offline decision and `output-contract.md` for how offline evidence is labelled).

Effectiveness is weighted higher than structure on purpose: a beautifully-written skill that performs badly is still a bad skill.

## Structure axis (static — 48 pts)

| # | Dimension | Weight | Scores high when… |
|---|-----------|--------|-------------------|
| 1 | **Trigger Clarity** | 8 | frontmatter `description` carries unambiguous trigger phrases AND explicit "not-for" boundaries; the skill fires on the right intents and stays silent on the wrong ones |
| 2 | **Stage Coherence** | 8 | body stages are ordered, each anchored to the previous; no orphan step, no forward reference to an undefined stage |
| 3 | **Failure-Mode Encoding** | 8 | known failure paths are encoded explicitly as `if <condition> then <recovery>`, not as a vague "be careful" |
| 4 | **Actionable Specificity** | 8 | directives are concrete; hedge words ("consider", "as appropriate", "use judgment", "be flexible", "if needed") are absent or pinned to a decision rule |
| 5 | **Constraint Explicitness** | 8 | hard rules, invariants, and red-lines are stated as named constraints, not buried in prose |
| 6 | **High-Risk Action Discipline** | 8 | destructive operations (`rm`, `git reset --hard`, force push, secret handling, irreversible writes) are explicitly gated or forbidden, not left implicit |

## Effectiveness axis (requires output — 52 pts)

| # | Dimension | Weight | Scores high when… |
|---|-----------|--------|-------------------|
| 7 | **Goal Attainment** | 20 | following the skill on benchmark prompts actually produces the stated outcome |
| 8 | **Output Fidelity** | 18 | produced output matches the declared contract — format, language, required sections, structure |
| 9 | **Robustness** | 14 | off-road / edge / adversarial benchmark prompts are handled gracefully, not silently mishandled |

## Related clusters (do not optimize one in isolation)

- **{3, 4, 5}** — Failure-Mode Encoding, Actionable Specificity, Constraint Explicitness move together. A mutation that adds an `if-then` (dim 3) usually also lifts dim 4 and may need a dim 5 constraint to land. When a single-variable mutation targets one of these, the judge MUST check the other two for regression (a gain in 3 that quietly degrades 5 is not a strict improvement).
- **{7, 8}** — Goal Attainment and Output Fidelity correlate: output that does not match the contract usually also misses the goal.

## Scoring protocol

- Each dimension is scored on its own 0→weight scale; the round score is the weighted sum (0–100).
- **Vacuous-compliance case (dim 6)**: a skill with no destructive-action surface at all scores **full marks** on High-Risk Action Discipline — there is nothing ungated, so absence of risk is compliance, not a gap. Do not score it mid. (Dims 1–5 have no vacuous case: a skill always has a description, stages, failure paths, directives, and constraints to assess.)
- A mutation is a **strict improvement** only if total score rises AND no individual dimension regresses below its pre-mutation value (a net-positive trade that tanks one dimension is not strict — it is a different design, not an improvement).
- Effectiveness dims (7–9) carry an evidence label inherited from the run mode: `real-exec` or `offline-同源` (single-axis; see `output-contract.md`). Offline-derived effectiveness scores are advisory, not hard evidence.

## Provenance

Dimensions 3, 4, 6 are concept-aligned with the public state of the art (failure-mechanism encoding, actionable specificity, high-risk-action discipline) but the dimension names, definitions, scoring language, and weights here are independently authored. Dimensions 1, 2, 5, 7, 8, 9 are independently derived from baransu's own skill conventions. See `provenance.md` for the per-item clean-room record.
