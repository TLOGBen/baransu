# Iteration-1 Analyst Observations

## Headline

- With skill: **96% ± 7%** pass rate (20/21)
- Without skill: **59% ± 31%** pass rate (12/21)
- Delta: **+37 percentage points**
- Cost: **~3× time**, **~1.6× tokens**

## Per-eval breakdown

| Eval | With skill | Without skill | Delta | Notes |
|---|---|---|---|---|
| eval-0 code-mixed-issues | 88% (7/8) | 25% (2/8) | +63pp | Largest gap — baseline has right content but no structural scaffold |
| eval-1 plan-target | 100% (7/7) | 86% (6/7) | +14pp | Smallest gap — plan review is semantic, less shape-dependent |
| eval-2 claim-vs-code | 100% (6/6) | 67% (4/6) | +33pp | Claim checklist structure is where skill adds value |

## Observations

### 1. One "failed" assertion was actually a test-design bug

eval-0 with_skill's sole failure: assertion demanded `Verdict = INCOMPLETE` citing "no e2e tests". But the skill's own rule (SKILL.md Stage 7) says **"if test infra absent → e2e gate n/a"** — fixtures/ has no test infra, so the skill correctly emitted `Verdict = FAIL` (for critical findings) rather than `INCOMPLETE`. **The skill behaved correctly; the assertion was wrong.**

Action for iteration-2: rewrite this assertion as "Verdict is FAIL *because of* critical security findings, AND e2e gate is explicitly marked n/a with rationale".

### 2. Baseline is surprisingly competent on raw content

Default Claude without `/review` correctly identified:
- All 4 P0s in eval-0 (API key, MD5, null-deref, new_user DB-clobber — **including one my test didn't even have an assertion for**)
- Thread-unsafety in eval-2 with correct minimal fix (`threading.Lock`)
- Most plan critique angles in eval-1 (decision contradictions, pseudo-unknowns, unproven complexity)

The baseline **fails on structure**, not on content. This is the load-bearing finding: `/review`'s value is **structural consistency, anti-drift, and auditability** — not finding more bugs than default Claude.

For users who want "what's wrong": baseline is fine.
For users who want "a triaged, citation-backed, structurally-consistent, auditable report they can hand to another agent or a reviewer": skill wins hard.

### 3. Plan-target delta is small (+14pp) — expected, not a problem

Plans are inherently semantic objects and default Claude has strong reading comprehension. The skill's edge on plan targets is:
- Explicit dispatch log (correctly skipping security-reviewer when plan has no security surface)
- 4-tier triage structure (concrete next actions rather than a long prose review)
- Explicit anti-recursion rule (not recommending /think rerun)

These are small but high-leverage differences for downstream consumers. The **structural verdict call** (CONCERN vs FAIL vs INCOMPLETE) is also more defensible with the skill's explicit rubric.

### 4. Time and token cost is real

- With skill: 268s ± 120s (up to 344s max)
- Without skill: 94s ± 45s

The skill is **~3× slower in wall time** because of parallel subagent dispatch and adversarial pass. This is a feature (isolation prevents context pollution) not a bug, but it means **`/review` should not be invoked casually**. The skill's own description ("use when the user wants a rigorous independent audit of a prior actor's work, especially after a long-running or multi-turn session") correctly gates its invocation.

### 5. Security-reviewer activation is correctly property-based

In eval-1 (plan target), security-reviewer was **correctly skipped** with explicit rationale: "plan has no auth/secret/crypto/network/injection/persistence/serialization surface". This validates the skill's **property-based activation (not keyword matching)** — the plan mentions the word "security" once (as one of three reviewer types) but the activation rule correctly looked at actual content properties, not string matches. Zero false activation.

### 6. Balance check works — over-engineered alternatives got downgraded

eval-2 (claim) is the cleanest demonstration: when adversarial test surfaced alternative fixes (asyncio / queue / multiprocessing / Redis / immutable rewrite), all were **explicitly downgraded to FYI** with "天平不通過" annotation. The `threading.Lock` minimal fix was kept. This is the "手術刀 rather than sledgehammer" principle working in practice.

### 7. Non-discriminating assertions to retire or strengthen

Assertions that passed for **both** with_skill and without_skill (no signal):
- "Traditional Chinese output" — passed everywhere; language is prompt-driven not skill-driven
- "No recursion suggestion" — passed everywhere (baseline doesn't recommend rerunning /think either)

These aren't harmful but they don't discriminate. For iteration-2 consider replacing with more targeted assertions (e.g., "report uses the skill's exact 8-section template" or "every finding carries file:line citation").

### 8. High-variance eval

eval-0 without_skill stddev is implied by the single-run design, but across the three evals, baseline ranges 25%–86% (stddev 31%). This means **baseline reliability depends heavily on target type** — great at code review, weaker at ceremony-dependent structured output. Skill brings all three targets into a tight 88%–100% band (stddev 7%).

## Iteration-2 candidates

Do NOT iterate just to push pass rate from 96% to 100% — that's chasing a bad assertion.

Genuine improvement targets (based on observations, not assertion scores):
1. **Retire or rewrite the buggy eval-0 Verdict assertion** (see Observation 1).
2. **Shave wall time.** 268s average is long. Possible: adversarial-pass gating on strictly cross-layer detection (not just T3 tier); allow adversarial to run as part of a reviewer rather than a separate Task.
3. **Tighten balance-check enforcement.** Currently implicit in reviewer prompts and skill Stage 6; consider adding an explicit rejected-finding count to the final report for auditability.
4. **Add one more test case**: a pure `/think` plan that has **zero real issues** — test for **false positive rate**. /review that finds problems in a clean plan is worse than no /review at all.

## Recommendation

**Ship iteration-1 of the skill as-is for real-world dogfooding.** The failure modes surfaced here are assertion-design issues and known cost tradeoffs, not skill bugs. Use real invocations on diverse targets to surface failure modes that planted-fixture tests can't reach.
