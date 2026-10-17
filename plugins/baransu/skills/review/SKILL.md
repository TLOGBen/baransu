---
name: review
description: 'Independent re-verification of a concrete artifact, diff, plan, or directly quoted claim against the user''s goal: a problem is where the target fails that goal, traced phenomenon → impact → root → restated bedrock → verification; dispatches a fresh verifier — plus at most two perspective lenses chosen by what the target is — never edits the target, and reports under a verdict computed by a printed rule (PROVEN / PARTLY PROVEN / NOT PROVEN); a clean review is a valid result. Trigger On 「看一下」「看看」「幫我看」「check 一下」「review 一下」「是不是做過頭了」, or casual "take a look at X". Not for auditing the user''s own project agent-config (route to /health) or diagnosing a reported error (/hunt). 繁體中文輸出。'
---

# review — find where the target fails the user's goal

A problem is a place where the target fails the user's goal. Performance, consistency, and security belong to every goal the user has not waived; a cost or a risk that does not make the goal fail only stands in the user's way, so by definition it is not a problem. A clean review is a valid result（「乾淨的 review 也是有效的 review」）.

Every retained problem is one chain, and the chain is the whole method:

1. **Phenomenon** — what the target actually does, at a location, under a trigger, shown by a run or a read.
2. **Impact** — which part of the user's goal it fails.
3. **Root** — the statement, premise, or model default that produced it; a symptom is not a root.
4. **Bedrock** — the restated statement that makes the phenomenon impossible: replacement text, preferring deletion and simplification to a guard beside the symptom.
5. **Verification** — evidence that each link above holds and the bedrock breaks nothing else.

All user-facing output is in Traditional Chinese.

## Outcome Contract

- **Outcome**: One independent review of the pinned target against the user's goal, converging into a report of the lenses used, the problems whose whole chain survived verification, independence, and remaining limits.
- **Done when**: The target and goal are pinned, the lenses named, the verifier has returned, each retained problem carries its full chain, each standing question is answered or marked unverified, the verdict is computed by its printed rule, and independence and limits are stated; zero problems with stated scope is a complete result.
- **Evidence**: The verifier's returned observations and, for every retained problem, the evidence behind each link of its chain; the independence statement.
- **Output**: A Traditional Chinese review report in the conversation; `.claude/review/<slug>.md` when persistence is useful or requested (`/ship` archives that directory).
- **Automation**: ultracode=neutral, loop=drivable（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）

PAUSE classification for non-interactive drivers: `references/loop-pauses.md`.

## Pin the target and the goal

Pin the supplied artifact, diff, plan, or directly quoted claim, and the goal it serves. Inspect the real target and its relevant upstream and downstream context. Do not invent a diff base, a target, or a claim from an author's completion statement; if none can be pinned, ask for it and stop.

Review-only means no target, test, configuration, or working-tree edits, including obvious typos and automatic formatting. A proposed bedrock remains part of a finding. Creating a requested separate review report does not authorize changing the reviewed material.

The goal comes from acceptance when present (criteria the user names, a `.claude/think/<slug>.md` plan's Building and Not building sections, a spec); none is a prerequisite. Otherwise read the goal off the request as stated, not the author's summary of it, through the three standing questions — the goal lens every review carries:

1. **Did it do what was asked?** Correctness of the asked-for behaviour on real executed paths.
2. **Did it add what was not asked?** Guards for states no caller produces, error handling that hides instead of fails, an interface with one implementation, an option nobody requested, validation repeated behind a boundary that already validates. The cost it adds is the impact.
3. **Did it solve a smaller problem than asked?** The happy path only, a requirement silently narrowed, the hard part left as a TODO or an "out of scope" the request never granted, tests that pass while the asked behaviour is absent. Cite the dropped part.

## Choose the lenses

Ask where this target most likely fails the goal, and choose lenses by that answer, never by size or a default fan-out. One lens is the default: the verifier itself, carrying the standing questions and the existing tests. Add at most two perspective agents from `${CLAUDE_PLUGIN_ROOT}/agents/` — quality (logic, error paths, edge cases), security, architecture, domain — each for a distinct way this target could fail the goal. Performance and consistency go to the verifier as a named place to look. The report opens with one line naming the lenses that ran and why. A directly quoted claim, or a diff that fits on one screen, is the fast path: the default lens alone, no canary, the short report; say that this is the path taken.

When the target's field has an instrument a practitioner would use — a dry run on a copy for a migration, an interleaving for a concurrency change, a known-answer test for numerics, a replay of real data for a parser, the squint test for a page — name it in the dispatch and have it run, not described.

Two instruments carry fixed triggers. The **canary** — one line that matters broken in a disposable copy, which the tests must catch — is mandatory off the fast path whenever the pass rests on tests the same change wrote or modified; skipped when the tests predate the change — their red → green run already showed they can fail. **Fresh inputs**: at least ten inputs development did not use — boundaries, empty and huge values, unusual order — none sharing a development case's output, run on the reference and the target alike. Mandatory whenever the claim is "behaves as before" (a migration, port, refactor, version move). The report states the n the claim rests on (rule of three, `../_shared/modeling.md`).

## Dispatch

Dispatch each added lens fresh, in its own context, with the target, the goal, and the read scope, asking for proposed problems as chains. Then load `${CLAUDE_PLUGIN_ROOT}/agents/verifier.md` completely and dispatch a fresh, narrow-context verifier with the target, the goal (acceptance, or the standing questions), every lens proposal, the permitted read and probe scope, the named instrument, and the raw evidence. The verifier checks each proposal's whole chain and drops those whose chain breaks. Do not supply the author's defense or desired verdict.

If independent execution is unavailable, or the current session authored the target, disclose the limitation. A same-context self-check can still find problems, but cannot earn an independent pass. Only a tool or instrument that actually ran yields findings; one that could not run leaves 「coverage lost: needs X」 in the limits, never a clean line. Never assume a tool or model exists because it worked in another session.

## Verify the chain

Verify consequential counts against the exact noun and scope claimed, per `../_shared/fact-check.md`; coverage is measured against real executed paths, and mocking the claimed layer does not test that layer. Evidence is a run's own output, never a count or a sentence someone typed. Output comparisons follow the verifier's bytes-tolerance-mask rule; each tolerance and mask is listed in the report with its why, and a difference outside them is a finding, never a value to adjust. For business behavior, distinguish upstream-reachable states and authoritative requirements from what the target happens to accept.

Retain a problem only when every link of its chain holds. Test a plausible disconfirming explanation for a severe claim; repeated agreement from the same model is one source, not independent ground truth.

The impact link is where an objection to the goal falls out: a fix whose only reason is "safer", or an argument that the asked-for work is costly or risky, fails no part of the goal and is not a problem. Removing what the goal carries — validation at a trust boundary, handling that prevents data loss, security, accessibility, anything the user asked for — does fail it, so no bedrock proposes that. Do not suppress a contradiction to your own earlier authoring decision by declaring it off-goal.

The bedrock link is where a guard falls out: try deleting, reusing what the codebase already has, a platform feature, a one-line change, and only then a mechanism, which names the failure it makes impossible. A review whose bedrocks are all guards has stopped at symptoms and says so. Separate problems, unknowns, and optional improvements; say which problems are worth acting on, with a one-line reason each.

If reviewing a workflow or a skill, the root is usually a clause: distinguish human-owned purpose from compensation for a model failure, and evaluate the actual failure conditions and enforcement surface; shorter instructions or a stronger model are not evidence that a long-run protection is obsolete. Do not promote a short scenario probe into a reliability claim for an hours-long coupled task.

Before extending a review into repeated probes, read `references/verification-effort.md`. A finding's validity does not itself authorize extra rounds, fixes, or a broader target.

## Report

Write plain Traditional Chinese: what was reviewed, against which goal, how independently; each problem as its chain（現象／影響／根源／基石／驗證）with the user's next step; each English term explained at first use; no fact the evidence has not established. Report the lenses line, examined scope, problems, evidence, independence, and limits, with one line per standing question（做到了／多做了／做小了）stating its verdict or 未驗證. No problems is not universal correctness; no tests is not an exempt layer; an absent required observation is unverified, not passed. When the host offers a tool for reporting findings, report through it; its own specification governs its fields and the text around it.

The verdict is computed by this rule, printed beside it, never by opinion, and on every path, the fast path included: **PROVEN** when every required check ran — each standing question or criterion answered with evidence, the existing tests executed with their output pasted, each triggered instrument run — and none failed; **NOT PROVEN** when a problem stands, a check failed, or nothing executed; **PARTLY PROVEN** when nothing failed but a required check could not run — a tool absent, no independent pass, a question 未驗證 — each listed as the reason. A verdict is recomputed from this run's evidence, never carried over from an earlier review.

Close with one line the user can act on:
「review 完成：判定 {PROVEN／PARTLY PROVEN／NOT PROVEN}（{觸發的規則一句}）；{N} 項問題（{M} 項值得處理）、{U} 項未驗證；獨立性：{獨立／同 context 自檢}；若只能改一處：{那一處的基石，或「無」}。」

## Not-for boundaries

- Auditing the user's project agent configuration and AI-maintainability → `/health`.
- Diagnosing a reported error or failing behaviour from its symptom → `/hunt`; a review judges a finished target, it does not chase a bug.
- Verifying baransu's own skill structure → `scripts/verify-skills.py`.
