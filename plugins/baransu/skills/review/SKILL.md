---
name: review
description: 'Independent re-verification of a concrete artifact, diff, plan, or directly quoted claim: dispatches a fresh, narrow-context verifier — with additional perspective agents only for distinct consequential risks — never edits the target, asks whether the work did what was asked, added what was not asked, or solved a smaller problem than asked, and reports examined scope, findings with evidence, independence, and remaining limits under a verdict computed by a printed rule (PROVEN / PARTLY PROVEN / NOT PROVEN); a clean review is a valid result. Trigger On 「看一下」「看看」「幫我看」「check 一下」「review 一下」「是不是做過頭了」, or casual "take a look at X". Not for auditing the user''s own project agent-config (route to /health) or diagnosing a reported error (/hunt). 繁體中文輸出。'
---

# review — find consequential defects in the user's actual target

Find consequential defects in the user's actual target; a clean review is a valid result（「乾淨的 review 也是有效的 review」）. Review-only means no edits.

The default this skill corrects: a reviewer that looks only for what could break, and answers by adding guards. Added defence and added abstraction lower the chance of being wrong without making the work right; so does quietly solving a smaller problem than the one asked. All three are findings here, never safe defaults.

All user-facing output is in Traditional Chinese.

## Outcome Contract

- **Outcome**: One independent re-verification of the pinned target against its review question, converging into a report of examined scope, findings with evidence, independence, and remaining limits.
- **Done when**: The target and question are pinned, the verifier has returned, each retained finding carries a location, trigger, supported consequence, and evidence, the three standing questions have each been answered or marked unverified, the verdict has been computed by the rule printed beside it, and the report states independence and limits; zero findings with stated scope is a complete result.
- **Evidence**: The verifier's returned observations and, for every retained finding, its evidence; the independence statement.
- **Output**: A Traditional Chinese review report in the conversation; `.claude/review/<slug>.md` when persistence is useful or requested (`/ship` archives that directory).
- **Automation**: ultracode=neutral, loop=drivable（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）

PAUSE classification for non-interactive drivers: `references/loop-pauses.md`.

## Pin the target and the question

Pin the supplied artifact, diff, plan, or directly quoted claim and the review question. Inspect the real target and its relevant upstream and downstream context. Do not invent a diff base, a target, or a claim from an author's completion statement; if none can be pinned, ask for it and stop.

Review-only means no target, test, configuration, or working-tree edits, including obvious typos and automatic formatting. A proposed fix remains a finding. Creating a requested separate review report does not authorize changing the reviewed material.

Reuse acceptance criteria when present (criteria the user names, a `.claude/think/<slug>.md` plan's Building and Not building sections, a spec); none is a prerequisite. When no acceptance exists, the review question is the three standing questions, each judged against the request as stated, not against the author's summary of it:

1. **Did it do what was asked?** Correctness of the asked-for behaviour on real executed paths.
2. **Did it add what was not asked?** Guards for states no caller produces, error handling that hides instead of fails, an interface with one implementation, an option or config nobody requested, validation repeated behind a boundary that already validates. Hiding behind defence or abstraction is a finding; the cost it adds is the consequence.
3. **Did it solve a smaller problem than asked?** The happy path only, a requirement silently narrowed, the hard part left as a TODO or an "out of scope" the request never granted, tests that pass while the asked behaviour is absent. Cite the dropped part.

Size the review by causal risk, never by a line-count tier or an automatic multi-perspective fan-out. **Fast path**: a directly quoted claim, or a diff that fits on one screen, gets one verifier with the standing questions and the existing tests, no perspective agents, and the short report; say that this is the path taken. The full path adds, when the target's domain has one, the instrument a practitioner of that field would use — a dry run on a copy for a migration, an interleaving for a concurrency change, a known-answer test for numerics, a replay of real data for a parser, the squint test for a page — named in the dispatch and run, not described.

Two instruments carry fixed triggers. The **canary**: break one line that matters in a disposable copy (a rounding mode, a threshold by one, a comparison) and the tests must go red; a comparator is itself checked by flipping one byte of an output. Mandatory on the full path whenever the pass rests on tests the same change wrote or modified; skipped on the fast path, and when the tests predate the change — their red → green run already showed they can fail. **Fresh inputs**: at least ten inputs development did not use — boundaries (zero, one either side of a threshold, the largest size), empty and huge values, unusual order, malformed records only when the request demands exact behaviour — none with the same output as a development case, run on the reference and on the target alike. Mandatory whenever the claim is "behaves as before" (a migration, port, refactor or version move); skipped otherwise. Ten clean inputs bound the miss rate at 30%, not at zero (`../_shared/modeling.md`, rule of three): the report says which n the claim rests on.

## Dispatch an independent verifier

Load `${CLAUDE_PLUGIN_ROOT}/agents/verifier.md` completely and dispatch a fresh, narrow-context verifier with the target, the question (acceptance when present, otherwise the three standing questions), the permitted read and probe scope, the named instrument when one applies, and the raw evidence. Do not supply the author's defense or desired verdict. Use additional independent perspectives only for distinct consequential risks: the perspective agents under `${CLAUDE_PLUGIN_ROOT}/agents/` (architecture, quality, security, style, domain) are available for that, one per distinct risk, never as a default fan-out.

If independent execution is unavailable, or the current session authored the target, disclose the limitation. A same-context self-check can still find defects, but cannot earn an independent pass. A tool or instrument is in one of three states — present, runnable here, actually ran — and only what actually ran yields findings; one that could not run leaves 「coverage lost: needs X」 in the limits, never a clean line. Never assume a tool or model exists because it worked in another session.

## Judge the evidence

Verify consequential counts against the exact noun and scope claimed, per `../_shared/fact-check.md`; coverage is measured against real executed paths, and mocking the claimed layer does not test that layer. Evidence is a run's own output — a result file, a pasted log fragment — never a count or a sentence someone typed: 「Canary: 已跑」 in the notes is a claim. An output comparison passes on identical bytes, or inside a tolerance the dispatch declared (relative at most 1%, absolute capped at the last printed digit; `../_shared/modeling.md`); masks cover only what legitimately varies, as one regex, never a hand-picked byte range; every tolerance and every mask carries a why and is listed in the report, and a difference outside them is a finding, never a value to adjust. For business behavior, distinguish upstream-reachable states and authoritative requirements from what the target happens to accept.

Retain findings with a concrete location, triggering condition, supported consequence, and relevant evidence. Test a plausible disconfirming explanation for a severe claim; do not inflate confidence or severity from repeated agreement, and treat shared model agreement as one source, not independent ground truth.

Consolidate against the review goal. Separate defects, unknowns, and optional improvements; say which surviving findings are worth acting on and which are not, with a one-line reason each. A finding that proposes a fix first tries, in order, deleting the code, reusing something the codebase already has, a platform feature, a one-line change — and only then a mechanism, which must name the consequential failure it prevents and the cost it adds. A fix whose only reason is "safer" is advisory, never an action item; a review whose action items are all guards has not answered the standing questions and says so. Never advise cutting validation at a trust boundary, handling that prevents data loss, security, accessibility, or anything the user asked for. Do not suppress a contradiction to your own earlier authoring decision by declaring it off-goal.

If reviewing a workflow or a skill, distinguish human-owned purpose from compensation for a model failure. Evaluate the actual failure conditions and enforcement surface; shorter instructions or a stronger model are not evidence that a long-run protection is obsolete. Do not promote a short scenario probe into a reliability claim for an hours-long coupled task.

Before extending a review into repeated probes, read `references/verification-effort.md`. A finding's validity does not itself authorize extra rounds, fixes, or a broader target.

## Report

### Plain-language presentation contract

- Make the immediate context explicit: what was reviewed, against which question, and how independent the check was.
- Explain each retained finding in plain Traditional Chinese: where it is, what triggers it, its practical impact, and the concrete next step the user can take.
- Keep each English technical term, but explain it in plain Traditional Chinese at its first use, in the same sentence or immediately after it.
- Do not add facts that the evidence has not established. This is presentation-only: it adds no PAUSE and does not replace the report's scope / findings / evidence / independence / limits shape.

Report examined scope, findings, evidence, independence, and remaining limits, with one line per standing question（做到了／多做了／做小了）stating its verdict or 未驗證. No findings is not universal correctness; no tests is not an exempt layer; an absent required observation is unverified, not passed. Write `.claude/review/<slug>.md` (slug from the reviewed target) only when persistence is useful or the user asks; otherwise the conversation report is the deliverable.

The verdict is computed by this rule, printed beside it, never by opinion, and on every path, the fast path included: **PROVEN** when every required check ran — each standing question or criterion answered with evidence, the existing tests executed with their output pasted, each triggered instrument run — and none failed; **NOT PROVEN** when a consequential finding stands, a check failed, or nothing executed; **PARTLY PROVEN** when nothing failed but a required check could not run — a tool absent, no independent pass, a question 未驗證 — each listed as the reason. A verdict is recomputed from this run's evidence, never carried over from an earlier review.

Close with one line the user can act on:
「review 完成：判定 {PROVEN／PARTLY PROVEN／NOT PROVEN}（{觸發的規則一句}）；{N} 項有後果的發現（{M} 項值得處理）、{U} 項未驗證；獨立性：{獨立／同 context 自檢}；若只能改一處：{那一處，或「無」}。」

## Not-for boundaries

- Auditing the user's project agent configuration and AI-maintainability → `/health`.
- Diagnosing a reported error or failing behaviour from its symptom → `/hunt`; a review judges a finished target, it does not chase a bug.
- Verifying baransu's own skill structure → `scripts/verify-skills.py`.
