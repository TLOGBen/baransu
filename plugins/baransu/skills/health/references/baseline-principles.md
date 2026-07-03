# Baseline Working Principles — recommended agent-instruction floor

Advisory baseline for a project's or a user's agent-instruction surface (`CLAUDE.md` / `AGENTS.md` / rules). These are broadly-applicable engineering-discipline principles, not baransu-specific. The health audit checks whether the instruction surface *covers* these themes and, when one is missing, offers to append the canonical text below.

Two hard framing rules:

- **Advisory, not mandatory.** Missing coverage is a `WARN` (Standard/Complex tier) or informational (Simple tier) — never a hard `FAIL`, never auto-applied.
- **Mutation is gated (INV-4).** Appending happens only after explicit user confirmation. General, plugin-agnostic principles go to **user scope** (`~/.claude/CLAUDE.md`); only project-specific rules go to project scope. Never recommend duplicating a principle already covered at user scope into a project file.

## Coverage checklist (what the audit tests)

Judge by substance — a theme counts as covered whether it appears verbatim or paraphrased.

| Principle | Present if the instruction surface says, in substance… |
|---|---|
| Think Before Coding | state assumptions, surface tradeoffs, ask when ambiguous rather than guess silently |
| Simplicity First | minimum solution that solves the problem; no speculative abstraction/config; prefer 50 lines over 200 |
| Surgical Changes | touch only what the request needs; don't refactor untouched code; clean up only self-made orphans |
| Goal-Driven Execution | define success criteria / verification; loop until a concrete check passes |
| First Principles | return to the root problem; decompose into smallest verifiable units; justify "why," not just "how" |
| Adversarial Review | before delivery, self-review from logic / fact / simpler-approach angles; list likely-break points; require evidence over "looks fine" |

Read-before-write (re-read a file before editing it in the same turn) is a related floor; treat it as covered if either the instruction surface or a loaded rule states it.

## Canonical template (append the missing sections only)

```markdown
## Working Principles

### 1. Think Before Coding

Don't assume. Don't hide confusion. Surface tradeoffs.

- State assumptions explicitly — if uncertain, ask rather than guess
- Present multiple interpretations — don't pick silently when ambiguity exists
- Push back when warranted — if a simpler approach exists, say so
- Stop when confused — name what's unclear and ask for clarification

### 2. Simplicity First

Minimum code that solves the problem. Nothing speculative.

- No features beyond what was asked
- No abstractions for single-use code
- No "flexibility" or "configurability" that wasn't requested
- No error handling for impossible scenarios
- If 200 lines could be 50, rewrite it

The test: would a senior engineer say this is overcomplicated? If yes, simplify.

### 3. Surgical Changes

Touch only what you must. Clean up only your own mess.

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting
- Don't refactor things that aren't broken
- Match existing style, even if you'd do it differently
- If you notice unrelated dead code, mention it — don't delete it

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused
- Don't remove pre-existing dead code unless asked

The test: every changed line should trace directly to the request.

### 4. Goal-Driven Execution

Define success criteria. Loop until verified.

| Instead of… | Transform to… |
|-------------|--------------|
| "Fix the bug" | Write a test that reproduces it, then make it pass |
| "Add validation" | Write tests for invalid inputs, then make them pass |
| "Refactor X" | Ensure tests pass before and after |

For multi-step tasks, state a brief plan, each step with its verification check.
Strong success criteria let the loop run independently. Weak criteria ("make it work") require constant clarification.

### 5. First Principles

Return to the root before acting. Don't copy convention.

- Ask what problem the task actually solves — don't inherit "how everyone does it."
- Decompose the problem into the smallest verifiable units and solve them one at a time.
- Every decision must justify its "why," not just its "how."

### 6. Adversarial Review (mandatory before delivery)

When the work is done, switch into the most critical reviewer and attack your own output.

- Attack from three angles: logical holes, factual correctness, whether a simpler approach exists.
- Proactively list the 3–5 points most likely to break, fix them, then deliver.
- Don't accept "looks fine" — produce verified evidence.
```
