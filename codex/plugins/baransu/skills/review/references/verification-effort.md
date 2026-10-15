# Verification effort follows consequence

The purpose of a review is enough independent evidence to judge the target against its question, not maximum test activity. Before dispatch, record briefly in the review notes: the question (acceptance or the three standing questions), the protected outcomes, the plausible failure paths, the permitted checks, and a finite allowance of rounds. Choose the allowance from risk, current evidence, and the user's budget. For a bounded change, start with one independent pass and one focused recheck after the author's repairs; this is a starting point, not a quality threshold.

## Judge findings and spending separately

- A demonstrated violation of a required outcome blocks that outcome even when the visible change is tiny. A formatting requirement is usually settled by a scoped formatter or an exact comparison; it does not justify probing unrelated behaviour.
- A hidden authorization, financial, consistency, or recovery defect may have serious consequences. Screenshots and green tests of another layer cannot waive the actual failed path.
- A plausible but unsupported consequential failure merits one bounded discriminating check. Until it runs, the claim is unverified, not a confirmed defect and not a pass.
- An optional improvement, or a merely imaginable defect without a causal path, does not expand the review. Keep it separate; never silently widen the user's scope.

For each proposed expansion ask: what required outcome could fail, what observation would decide it, and why is the cheaper existing evidence insufficient? Do not select severity by visibility, line count, number of agreeing reviewers, or how interesting the probe is.

## A probe is a method, not a quota

Run a mutation or fault-injection probe only when it resolves a specific uncertainty about whether the available verification detects a plausible broken result. Name the mutation, the expected detector, the baseline, the isolation, and the stopping point first; prefer a direct behaviour check when it answers the question more simply. Work only in an authorized disposable copy with a recovery plan, never in the user's live target. A test that mocks the mutated layer is not coverage of it. An unavailable probe leaves the exact claim unverified; do not invent a result or relax authorization.

## Rechecks without a treadmill

A recheck targets the actual correction and the contracts it touches, and records what new evidence the round produced. At the allowance, on a repeated failed hypothesis, or when the next step would be a wider refactor, stop and return: the required gap, the evidence gained, the work spent, the bounded alternatives, and a proposed next allowance. New user-owned priorities, risk acceptance, or external authority need the user; a routine focused recheck does not.

If adequate evidence is present and no required gap remains, finish. If the allowance is spent with gaps remaining, report incomplete or unverified. Never write a passing report to end a loop, and never keep probing to avoid handing back a bounded conclusion.
