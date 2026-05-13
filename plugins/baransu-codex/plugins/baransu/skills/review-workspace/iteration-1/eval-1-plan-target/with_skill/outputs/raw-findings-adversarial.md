# Adversarial test — raw output

Target: fixtures/review_plan.md
Target type: plan. Six angles translated per SKILL.md Stage 5 plan-variant mapping:
1 → ambiguous premise
2 → sections internally inconsistent
3 → decision-to-decision contradiction
4 → scope creep / reader misreading
5 → cause/effect confusion
6 → apparent plan completeness being a hallucinated signal

Reviewer context: simulated isolated general-purpose Task. Does not see reviewer outputs.

---

## 1. Ambiguous premise

The whole plan rests on the premise that "isolated Task contexts" prevent context pollution, that this is the core value of /review, and that it works. But Task isolation in Claude Code means the subagent does not see the parent's message history — it DOES see the prompt text the parent supplies. If the parent skill (SKILL.md) writes a highly shaped prompt (claim checklist, framing, "look for X/Y/Z"), the reviewer's "clean context" is re-polluted by the parent's framing. The plan treats isolation as sufficient; it actually requires both isolation AND minimal parent-framing. The plan does not name this constraint anywhere. If the premise fails, activation rules and the agents' "通用原則" sections are the only remaining barriers to drift.

Impact: the core value proposition ("clean context re-verification") could be weaker than the plan implies. Finding: surface this premise dependency.

## 2. Sections internally inconsistent

**Building step 3** says adversarial runs "達門檻時". **Key decision #4** says adversarial runs on ">100 行 code, or >3 decision points in plan, or 跨層級變更". These are structurally consistent (Building is the descriptive mention, KD is the decision that locks the thresholds), but the reader reading top-down sees "達門檻時" in Building step 3 with no forward-reference to KD #4. Minor, and already covered by quality-reviewer qual-03 pattern.

More substantive: **Not building NB7** says "不支援 --auto 模式跳過 AskUserQuestion". But **Building step 4** describes "彙總後分成四級...需判斷詢問". If there is no --auto, what happens in headless / Copilot environments where AskUserQuestion is costly or impossible? The plan implicitly assumes an interactive user is always present. The real SKILL.md (already written) addresses this in "Gotchas", but the plan itself does not declare this assumption. If this skill is ever used from Copilot Coding Agent (no human present), the plan's design collapses silently into an unusable interactive-only tool.

Finding: the plan asserts "no --auto" without declaring "interactive-only is the supported mode; other platforms out-of-scope". This is a premise masquerading as a prohibition.

## 3. Decision-to-decision contradiction

**KD #1** (pure orchestrator; no rubric in SKILL.md) vs **KD #5** ("四級 triage 的 打包確認 批次彈 AskUserQuestion").

KD #5 defines triage mechanics — assigning severity classes, the auto-fix radius, the packaged-confirm shape. These ARE reviewer rubric logic. If the main SKILL.md codifies the triage shape (which it must, since nothing else can), KD#1 is partially violated: SKILL.md is not purely an orchestrator — it owns the triage rubric. 

This is not a fatal contradiction; it is a scope-of-term issue. "Rubric" in KD#1 seemingly means "what counts as an architectural problem / a quality problem / a security problem" (the finding-detection rubrics), which live in agent files. Triage mechanics (tier assignment, packaging) are a different kind of logic and legitimately live in SKILL.md. But the plan doesn't distinguish these two senses of "rubric", so a naive reader could accuse the implementation of violating KD#1 when reading the final SKILL.md.

Finding: KD#1 should be split into "SKILL.md owns dispatch + triage; agent files own detection rubrics" to pre-empt this confusion.

## 4. Scope creep / reader misreading

Plausible misreads:

(a) A reader sees "四級 triage" and "auto-fix 直接套用" and concludes /review is an auto-fixer that can be run in CI. Actually the plan only permits T1 auto-fixes (format/import/typo/dead-import), not "review-driven auto-correction". The word "auto" in different contexts invites creep.

(b) A reader sees "checklist" as Stage 2 output and could treat it as a formal spec artifact to be version-controlled. Actually it is an in-session scratchpad. Plan does not say where the checklist lives or whether it persists.

(c) A reader wanting a general-purpose reviewer sees the title "/baransu:review" and might expect /review to eventually absorb native /review and /security-review. The plan's Approach section rejects this but does not declare it in Not building. Low-risk misreading.

Finding (a) is most concerning: "auto-fix" framing could mislead integrators into CI usage.

## 5. Cause-effect confusion

The plan claims "isolated Task context → anti-pollution → better review". This presents isolation AS the cause of better review. But the true causal chain is more like: isolation → absence of the originator's context → if and only if the agent's prompting stays minimal AND the agent's rubric is well-scoped, then better review. Isolation alone is necessary, not sufficient. The plan elides the sufficiency conditions (specifically: prompt minimality in Stage 4 dispatch, and rubric discipline in agent files).

Also in Approach: "官方方案(原生 /review 與 /security-review)不適用：兩者都是單 pass、無 perspective 切分、無分級、無對抗、無 triage、無 auto-fix、不支援非 PR target." This lists differences, then uses "因此不適用". But "official tools lack feature X" does not entail "official tools are unsuitable" — it entails "if I need feature X, official tools don't cover it". The plan implicitly argues its features are necessary without justifying their necessity. Several of the claimed differentiators (triage tiers, auto-fix, adversarial) are themselves plan decisions not orthogonal requirements.

Finding: the Approach section conflates "we have more features" with "the alternatives are wrong". A cleaner form: "native /review does not support non-PR targets; perspective separation + triage are design preferences, not hard requirements".

## 6. Apparent plan completeness = hallucinated signal?

The plan hits all five /think sections, cites concrete files, names decisions, surfaces Unknowns. It reads complete. But three signals suggest the completeness is partly performative:

(a) Unknowns U1 essentially defers the real content of three agent files ("具體 rubric 細節尚未逐條寫出") — i.e. the majority of the behavioral spec is deferred. The plan is a scaffold; most of the substance is in the still-unwritten agent files. This is not bad (plans should defer detail), but it means a reader should not infer "plan approved = design locked" — they should infer "plan approved = shape agreed, substance TBD".

(b) Unknown U2 punts the adversarial plan-mapping to "first run" — which is the run happening now. A reviewer now must invent the mapping. If this mapping is wrong, the adversarial test is degraded. The plan does not anticipate who adjudicates the mapping.

(c) The plan does not mention evaluation / acceptance criteria. How will anyone know the skill works? Presumably, by running it. But that's another deferred operation, not a plan artifact. For a governance skill like this, an absent "how do we know it's doing its job" section is a real gap, though perhaps legitimately out of scope for a /think output.

Finding: the sense of closure from five filled sections is partly an artefact of the fixed schema — several items are scaffolding rather than substance. The plan is not hallucinating completeness, but a naive reader could over-weight "approved" as "ready to ship".

## Root-cause vs symptom check

Looking across the reviewer-found issues that I can guess at (without seeing them):
- "Unknowns missing triad" / "Decisions as activities" / "Plan closure is performative" — all symptoms of one deeper cause: the plan describes a SHAPE, not a specification. It says what categories will exist; it mostly defers what's in them. If the root cause were attacked, the fix would be "either commit to shipping the agent-rubric content now, or explicitly downgrade this plan to scaffold-only and schedule a rubric-decision turn". Individual line-item fixes are symptom-level.

## epistemic-consensus check

If all reviewers converged on "Unknowns are under-specified" — is that because it's true or because they're all reading plan-rubric item 6 out of their 目標 section, which is identical text? Yes, they share training-rubric bias on this exact axis. One way the unanimous view could be wrong: maybe "Unknowns 具備具體問題 + 延後理由 + 誰何時決定" is itself over-prescriptive for a small in-flight skill-authoring plan, and the correct resolution is to relax the rubric, not punish the plan. Counter-point: the plan claims to follow this rubric; self-declared standards are fair to enforce.
