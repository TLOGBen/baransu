# architecture-reviewer — raw findings

Target: fixtures/review_plan.md (a /think 5-section plan for building /baransu:review)
Target type: plan / design document (apply plan-specific rules from 目標 section item 6)
Reviewer context: simulated isolated Task context. No knowledge of quality-reviewer or adversarial output.

Rubric applied: 視角 + 目標 (plan-variant) + 通用原則 + 禁忌 from architecture-reviewer.md.

---

## Findings

- id: arch-01-kd-activities-not-decisions
  severity: major
  citation: "Key decisions" section, items 4 and 6
  claim_violated: D1 (Key decisions 都有 why) — implied by 通用原則 plan-rule 6c
  observation: |
    Key decision #4 reads "對抗性測試只在觸發門檻時跑(>100 行 code，或 >3 decision points in plan，或跨層級變更)" — this is an activity/threshold rule, not a decision with rationale. Where is the "why >3 and not >5"? Where is the trade-off considered? Key decision #6 "自動修復落檔直接改，不走 git staging" similarly states what, not why. Plan rubric item 6 from my 目標 requires Key decisions be 「為什麼這樣選」not「做什麼」. Two of six items are activities masquerading as decisions.
  suggested_fix: |
    Rewrite KD #4 and #6 in "chose X over Y because Z" form. For #4 cite what load the ">3 decisions" threshold actually protects against (token budget? noise floor?). For #6 cite why git staging was rejected (complexity? unfamiliar UX? unreliable across projects?).
  balance_note: |
    不做: plan stays less rigorous — readers can't audit whether thresholds were picked intentionally or arbitrarily.
    做了: marginal writing cost (~3 lines each); forces author to surface the actual rationale.
    中間: accept as-is but add a "Unknowns" note "threshold value is heuristic, may need tuning" — this surfaces the gap without demanding full rewrite.
    Recommend 中間方案 — the surgical minimum.

- id: arch-02-not-building-vs-building-overlap-risk
  severity: minor
  citation: "Not building" NB6 vs "Building" step 6
  claim_violated: plan-rule "Building 與 Not building 互斥"
  observation: |
    Building step 6 says "若 target 為程式變更，未偵測到 e2e 跑過 → verdict 強制降為 INCOMPLETE". Not building NB6 says "不跑 e2e：不嘗試執行 target 專案的測試指令，只偵測並用 INCOMPLETE verdict 施壓". These are actually complementary (Building = detect + judge; NotBuilding = don't execute), but the word "e2e" appears in both with adjacent meanings. A reader skimming could misread them as contradictory.
  suggested_fix: |
    Cosmetic: rename NB6 to "不主動執行 target 專案的測試指令" to remove the lexical collision. Or add one clause to Building step 6: "(偵測 only — 不主動執行)".
  balance_note: |
    不做: small reader-confusion risk; experienced readers resolve from context.
    做了: 10-character edit, cost trivial.
    中間: accept as-is — the overlap is lexical, not logical. Downgrade to advisory FYI.

- id: arch-03-activation-rules-sufficiency-unverified
  severity: advisory
  citation: "Approach" paragraph + "Key decisions" item 3
  claim_violated: none — advisory only
  observation: |
    Plan claims activation = target-property table, not keyword matching, and that this handles non-code /think-output targets correctly. But the plan does not enumerate what properties are checked or how the table looks. Architecturally this is the most load-bearing mechanism in the whole design (it is how /review decides who reviews what), yet it is treated as an opaque "table" without a sketch. The plan elevates this to a Key decision but doesn't show its shape.
  suggested_fix: |
    Advisory only: add a 1-liner example row to Approach — e.g. "rule: if target contains any src file → quality-reviewer; if >3 files or cross-layer → architecture-reviewer". This proves the mechanism is concrete, not hand-waved.
  balance_note: |
    不做: the table is left to the author's implementation pass; might drift.
    做了: one example line surfaces the shape.
    中間: one bullet is cheap. But the plan is only a plan — expecting full table definition here is over-reach. This is a legitimate Unknown that should be surfaced in Unknowns, not Building. Propose as advisory.

- id: arch-04-dependency-direction-reviewer-to-skill
  severity: minor
  citation: "Key decisions" item 1
  claim_violated: none
  observation: |
    KD #1 says SKILL.md is pure orchestrator; rubric lives in agent files. Good separation. However, the plan is silent on whether SKILL.md imports/references agent-file content, or whether agent files stand truly independent (only discovered via subagent_type lookup). If the former, SKILL.md effectively depends on agent-file contents, and changes to agents could require SKILL.md changes — breaking the promised independence. If the latter, where does SKILL.md learn what each reviewer *covers*, to decide activation? The plan doesn't say.
  suggested_fix: |
    Add one sentence to KD#1 or to Approach: "SKILL.md references agents by name/subagent_type only; activation decisions are based on target properties, not reviewer rubric content — reviewer agents can evolve independently." This locks the dependency direction.
  balance_note: |
    不做: dependency direction left implicit; future refactor might accidentally couple.
    做了: one sentence.
    中間: one sentence, cheap — recommend accept.

- id: arch-05-cross-layer-qualifier-undefined-in-plan
  severity: advisory
  citation: "Key decisions" item 4
  claim_violated: none
  observation: |
    KD #4 triggers adversarial on "跨層級變更". For a plan-type target (no code), what counts as "跨層級"? The plan doesn't specify. This maps to 通用原則 "Unknowns 有沒有偽裝成 known" — this is a latent Unknown parading as a decided threshold.
  suggested_fix: |
    Either (a) move the cross-layer clause to Unknowns as "threshold for plan-targets TBD first run", or (b) add one sentence defining "cross-layer for plan targets = spanning ≥3 layers/components in the plan's Building section".
  balance_note: |
    不做: genuine ambiguity when audit meets first plan-target.
    做了: one-line definition resolves it.
    中間: surface as Unknown — matches plan's own conceit of honest unknowns.
    Recommend (a): move to Unknowns rather than pretend it's decided.

## Summary
5 findings total. 1 major (KD-as-activities), 2 minor, 2 advisory. No responsibility-displacement, no cross-layer coupling, no over-abstraction, no inconsistency with repo conventions. Plan is architecturally sound; issues are about plan-hygiene, not system design.
