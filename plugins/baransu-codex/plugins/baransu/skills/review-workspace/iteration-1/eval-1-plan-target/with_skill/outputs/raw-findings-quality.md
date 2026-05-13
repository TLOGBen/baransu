# quality-reviewer — raw findings

Target: fixtures/review_plan.md (a /think 5-section plan)
Target type: plan / design document (apply plan-specific rules from 目標 item 6)
Reviewer context: simulated isolated Task context. Does not know what architecture-reviewer or adversarial produced.

Rubric applied: 視角 + 目標 (plan-variant) + 通用原則 + 禁忌 from quality-reviewer.md.
Primary axis: hallucination-check — for each claim on the checklist, is it verifiable from the plan itself?

---

## Findings

- id: qual-01-unknowns-missing-required-triad
  severity: major
  citation: "Unknowns" section all three items
  claim_violated: plan-rubric item 6 "Unknowns 具備具體問題 + 延後理由 + 誰何時決定"
  observation: |
    All three Unknowns are missing two of the three required elements.

    U1 (agent rubric bullets): has the problem, but no "延後理由" (why defer? because the SKILL shape must land first? to keep this plan small?) and no "誰何時決定" (author during implementation turn? which turn?).

    U2 (6 adversarial angles → plan target): problem + partial "延後理由" ("首個 plan-target 試跑時") but no "誰何時決定". Ironically, the very review being done right now IS the first plan-target run, which should have resolved U2 — the Unknown is pointing at itself.

    U3 (v0.2.0 vs v0.1.1): has the problem, no reasoning about the axes (is it a breaking change? new public surface?), no decider.

    Plan fails its own stated standard for Unknowns.
  suggested_fix: |
    For each Unknown, add one line: "延後理由: <why> | 決定者/時機: <who/when>". Four ~15-character annotations total. U2 specifically should be resolved now, not merely annotated.
  balance_note: |
    不做: Unknowns remain vague; when revisited they're expensive to reconstruct ("wait, why did we defer this?").
    做了: ~4 lines of text; no behavior change.
    中間: do it for U1 and U3 minimally; resolve U2 in-flight since this very review surfaces the answer (0.2.0 for the new skill introduction).
    Recommend surgical fix.

- id: qual-02-claimed-section-7-"輸出繁中報告"-underspecified
  severity: minor
  citation: "Building" step 7
  claim_violated: plan-rubric "Building 的描述讓讀者能立刻想像成品"
  observation: |
    Building 1–6 each describe a concrete operation (checklist, dispatch, adversarial, triage, auto-fix, e2e-gate). Step 7 is just "輸出繁中報告". Compared to the others this is a thin stub. Can the reader "想像成品"? Not quite — what are the report's sections? Verdict format? Where is it rendered? This is a claim-to-implementation fidelity gap: Building says step 7 exists but under-specifies it relative to its siblings.
  suggested_fix: |
    Expand step 7 to ~one sentence: "輸出結構化繁中報告，含 Verdict (PASS/CONCERN/FAIL/INCOMPLETE)、Target、Claim Checklist、派遣紀錄、四級 findings、E2E gate、結論." Parity with steps 1–6.
  balance_note: |
    不做: reader has to infer report shape from context.
    做了: one-sentence expansion.
    中間: one sentence — cheap, recommend accept.

- id: qual-03-key-decision-3-claim-vs-building-gap
  severity: minor
  citation: "Key decisions" item 3 vs "Building" step 2
  claim_violated: C3 (dispatch 1-3 agents) and D3 (activation = property table)
  observation: |
    KD #3 says activation is a property table handling non-code targets. Building step 2 describes "依 target 規模與激活規則決定派遣 1~3 個獨立 perspective agent". These are compatible, but Building step 2 does not cite the property-table mechanism — it could be read as manual/heuristic judgement. A reader checking "did the plan say how activation happens?" sees two loosely-coupled restatements with no cross-reference.
  suggested_fix: |
    Weak fix: in Building step 2 add "(依 Key decisions #3 的屬性表)" as explicit cross-reference. Cost: 12 characters.
  balance_note: |
    不做: cross-reference missing but recoverable.
    做了: one parenthetical.
    中間: advisory-level; experienced readers resolve naturally.
    Recommend FYI / advisory.

- id: qual-04-not-building-NB5-scope-check
  severity: advisory
  citation: "Not building" NB5
  claim_violated: none
  observation: |
    NB5 says "不做審核者互審或 review-of-review". Clear negative boundary. But checking against Approach's rejected options: Approach says it rejected "極繁方案(審核者互審 / 每人一次對抗)". Consistent. However, the exact phrase "review-of-review" (recursion self-call) vs "審核者互審" (reviewers checking each other) could be read as two separate things. Is the plan saying both are out, or just one? Good hygiene would spell out that these are two distinct prohibitions: (a) reviewers don't review other reviewers' findings; (b) /review never invokes /review.
  suggested_fix: |
    Advisory: split NB5 into two bullets, "不做審核者互審" and "不 recursive /review".
  balance_note: |
    不做: lexical ambiguity only.
    做了: trivial edit.
    中間: tolerable as-is. Downgrade to FYI.

- id: qual-05-building-step-5-scope-of-"自動修復"-check
  severity: minor
  citation: "Building" step 5
  claim_violated: C5 (auto-fix locked to format/import/typo/dead-import)
  observation: |
    Building step 5 says "執行第一級自動修復(僅限 formatter / imports / typo / dead import)". This repeats the radius, which is good. But the plan does not declare what happens if the target has NO such trivial issues (no-op silently?), or what happens if the detected change accidentally exceeds the radius (abort? demote to T2?). The claim is complete about the allowed range but silent on off-range handling — which is a typical off-by-X edge case in my rubric.
  suggested_fix: |
    Add one sentence to Building step 5: "若修改超出範圍 → 降級為 T2 待確認；若無可修 → 跳過此步驟。"
  balance_note: |
    不做: edge-case left to implementor discretion; likely fine.
    做了: one sentence.
    中間: could also be moved into SKILL.md itself during implementation, not the plan. Plan-level decision: advisory.
    Recommend advisory.

- id: qual-06-version-bump-unknown-is-actually-decidable
  severity: minor
  citation: "Unknowns" U3
  claim_violated: self — plan says U3 is unknown but it is decidable from stated facts
  observation: |
    U3 asks v0.2.0 vs v0.1.1. Plan already says this is a new skill introduction adding agents + new CLAUDE.md section — a user-visible feature addition. SemVer minor bump (0.2.0) is the mechanical answer. This is an Unknown that isn't — it's "un-decided" rather than "un-knowable". My rubric item 6 flags this exact pattern.
  suggested_fix: |
    Promote to Key decisions: "v0.2.0 (minor bump — new feature, no breaking change)." Remove from Unknowns.
  balance_note: |
    不做: trivially decidable later; low cost of leaving.
    做了: 2-line promotion.
    中間: resolve in-flight during this review (suggest v0.2.0); annotate.
    Recommend resolve now.

## Summary
6 findings. 1 major (Unknowns missing triad), 3 minor, 2 advisory. No logic errors, no reachability issues, no boundary bugs (it's a plan, not code). All findings are about self-consistency and plan-to-claim fidelity. Plan is largely self-consistent but has a couple of claims that don't meet the standard the plan itself sets for Unknowns.
