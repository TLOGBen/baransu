---
name: review
description: 'Independent re-verification of a concrete artifact, diff, plan, or directly quoted claim against the user''s goal: a problem is where the target fails that goal, traced phenomenon → impact → root → restated bedrock → verification; dispatches a fresh verifier — plus at most two perspective lenses chosen by what the target is — never edits the target, and reports under a verdict computed by a printed rule (PROVEN / PARTLY PROVEN / NOT PROVEN); a clean review is a valid result. Trigger On 「看一下」「看看」「幫我看」「check 一下」「review 一下」「是不是做過頭了」, or casual "take a look at X". Not for auditing the user''s own project agent-config (route to /health) or diagnosing a reported error (/hunt). 繁體中文輸出。'
---

# review — find where the target fails the user's goal

A problem is a place where the target fails the user's goal, whichever change introduced it and whatever note already admits it. Performance, consistency, and security belong to every goal; only the user waives a part of one. A clean review is a valid result（「乾淨的 review 也是有效的 review」）.

Every retained problem is one chain, and the chain is the whole method:

1. **Phenomenon** — what the target actually does, at a location, under a trigger, observed on the real thing: the target's own checks run here; for a claimed platform not available here, the recorded output of this same version's run on it; a read of the target only where neither exists. A failed observation suspects itself first: a run outside what the target claims or pins shows the run, not the target, until the failure reproduces inside it.
2. **Impact** — which part of the user's goal it fails.
3. **Root** — the statement, premise, or model default that produced it; a symptom is not a root.
4. **Bedrock** — the restated statement that makes the phenomenon impossible: replacement text, preferring deletion and simplification to a guard beside the symptom.
5. **Verification** — a run or a read showing each link above holds and the bedrock breaks nothing else.

All user-facing output is in Traditional Chinese.

## Outcome Contract

- **Outcome**: One independent review of the pinned target against the user's goal, converging into a report of the lenses used, the problems verified, each with its chain, independence, and remaining limits.
- **Done when**: The target and goal are pinned, the lenses named, the verifier has returned, each retained problem carries its chain, any unverified link marked, each standing question is answered or marked unverified, the verdict is computed by its printed rule, and independence and limits are stated; zero problems with stated scope is a complete result.
- **Evidence**: The verifier's returned observations and, for every retained problem, the evidence behind each link of its chain; the independence statement.
- **Output**: A Traditional Chinese review report in the conversation; `.claude/review/<slug>.md` when persistence is useful or requested (`/ship` archives that directory).
- **Automation**: ultracode=neutral, loop=drivable（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）

PAUSE classification for non-interactive drivers: `references/loop-pauses.md`.

## Pin the target and the goal

Pin the supplied artifact, diff, plan, or directly quoted claim, and the goal it serves; for a diff the target is the system the change leaves behind, and the diff only says where to start. Do not invent a diff base, a target, or a claim from an author's completion statement; if none can be pinned, ask for it and stop.

Review-only means no target, test, configuration, or working-tree edits, including obvious typos and automatic formatting. A proposed bedrock remains part of a finding. Creating a requested separate review report does not authorize changing the reviewed material.

The goal comes from acceptance when present (criteria the user names, a `.claude/think/<slug>.md` plan's Building and Not building sections, a spec), otherwise from the request as stated, not the author's summary of it; neither acceptance nor a plan is a prerequisite. Every review asks three standing questions against that goal — the goal lens it always carries:

1. **Did it do what was asked?** Correctness of the asked-for behaviour along its real path, from the user's trigger to where the result is complete, not where the change ends — every unchanged step the result passes through included, each observed as the Phenomenon link says; a step not walked leaves this question 未驗證.
2. **Did it add what was not asked?** Guards for states no caller produces, error handling that hides instead of fails, an interface with one implementation, an option nobody requested, validation repeated behind a boundary that already validates. The cost it adds is the impact.
3. **Did it solve a smaller problem than asked?** The happy path only, a requirement silently narrowed, the hard part left as a TODO or an "out of scope" the request never granted, tests that pass while the asked behaviour is absent. Cite the dropped part.

## Choose the lenses

Ask where this target most likely fails the goal, and choose lenses by that answer, never by size. The verifier always runs, carrying the standing questions and the target's own checks on each platform it claims. When the target's content is code — a diff, a pull request, files, or a paste — quality (logic, error paths, edge cases) runs first by default and proposes chains for the verifier to verify; a document, plan, or claim gets the verifier alone by default. Add others from `${CLAUDE_PLUGIN_ROOT}/agents/` — security, architecture, domain — each for a distinct way this target could fail the goal, up to three lenses in all. Performance goes to the verifier as a named place to look; consistency, as a sweep of every other place that states what the change altered. The report opens with one line naming the lenses that ran and why. A directly quoted claim, or a diff that fits on one screen, is the fast path: no canary and the short report; say that this is the path taken.

When the target's field has an instrument a practitioner would use — a dry run on a copy for a migration, an interleaving for a concurrency change, a known-answer test for numerics, a replay of real data for a parser, the squint test for a page — name it in the dispatch and have it run, not described.

Two instruments carry fixed triggers. The **canary** — one line that matters broken in a disposable copy, which the tests must catch — is mandatory off the fast path whenever the pass rests on tests the same change wrote or modified; skipped when the tests predate the change — their red → green run already showed they can fail. **Fresh inputs**: at least ten inputs development did not use — boundaries, empty and huge values, unusual order — none sharing a development case's output, run on the reference and the target alike. Mandatory whenever the claim is "behaves as before" (a migration, port, refactor, version move). The report states the n the claim rests on (rule of three, `../_shared/modeling.md`).

## Dispatch

Dispatch each added lens fresh, in its own context, with the target, the goal, and the read scope, asking for proposed problems as chains. Then load `${CLAUDE_PLUGIN_ROOT}/agents/verifier.md` completely and dispatch a fresh, narrow-context verifier with the target, the goal (acceptance, or the request), every lens proposal, the permitted read and probe scope, the named instrument, and the raw evidence. The verifier checks each proposal's chain and drops one only when its phenomenon or impact breaks. Do not supply the author's defense or desired verdict.

If independent execution is unavailable, or the current session authored the target, disclose the limitation. A same-context self-check can still find problems, but cannot earn an independent pass. Only a tool or instrument that actually ran yields findings; one that could not run leaves 「coverage lost: needs X」 in the limits, never a clean line. Never assume a tool or model exists because it worked in another session.

## Verify the chain

Verify consequential counts against the exact noun and scope claimed, per `../_shared/fact-check.md`; coverage is measured against real executed paths, and mocking the claimed layer does not test that layer. A count or an "it ran" claim is evidenced only by a run's own output, never by a sentence someone typed. Output comparisons follow the verifier's bytes-tolerance-mask rule; each tolerance and mask is listed in the report with its why, and a difference outside them is a finding, never a value to adjust. For business behavior, distinguish upstream-reachable states and authoritative requirements from what the target happens to accept.

A phenomenon that holds and fails the goal is a problem; a wrong root or bedrock is traced again, and if it cannot be, that link is marked unverified — never a reason to drop the problem. Test a plausible disconfirming explanation for a severe claim; repeated agreement from the same model is one source, not independent ground truth.

Removing what the goal carries — validation at a trust boundary, handling that prevents data loss, security, accessibility, anything the user asked for — fails the goal, so no bedrock proposes it. Do not suppress a contradiction to your own earlier authoring decision by declaring it off-goal.

The bedrock link is where a guard falls out: try deleting, reusing what the codebase already has, a platform feature, a one-line change, and only then a mechanism, which names the failure it makes impossible. A review whose bedrocks are all guards has stopped at symptoms and says so. Separate problems from what remains unverified.

If reviewing a workflow or a skill, the root is usually a clause: distinguish human-owned purpose from compensation for a model failure, and evaluate the actual failure conditions and enforcement surface; shorter instructions or a stronger model are not evidence that a long-run protection is obsolete. Do not promote a short scenario probe into a reliability claim for an hours-long coupled task.

Before extending a review into repeated probes, read `references/verification-effort.md`. A finding's validity does not itself authorize extra rounds, fixes, or a broader target.

## Report

Write plain Traditional Chinese: what was reviewed, against which goal, how independently; each problem as its chain（現象／影響／根源／基石／驗證）with the user's next step; each English term explained at first use; no fact the evidence has not established. Report the lenses line, examined scope, problems, evidence, independence, and limits, with one line per standing question（做到了／多做了／做小了）stating its verdict or 未驗證. No problems is not universal correctness; no tests is not an exempt layer; an absent required observation is unverified, not passed. When the host offers a tool for reporting findings, report through it; its specification governs its own fields, and a root or bedrock those fields cannot hold goes in the report text.

The verdict is computed by this rule, printed beside it, never by opinion, and on every path, the fast path included: **PROVEN** when every required check ran — each standing question or criterion answered with evidence, the target's own checks executed, here or in this version's recorded run, with their output pasted, each triggered instrument run — and none failed; **NOT PROVEN** when a problem stands, a check failed on the target, or nothing executed; **PARTLY PROVEN** when nothing failed on the target but a required check could not run — a tool or claimed platform absent with no recorded run, a failure not yet reproduced inside what the target claims or pins, no independent pass, a question 未驗證 — each listed as the reason. A verdict is recomputed from this run's evidence, never carried over from an earlier review.

Close with one line the user can act on:
「review 完成：判定 {PROVEN／PARTLY PROVEN／NOT PROVEN}（{觸發的規則一句}）；{N} 項問題、{U} 項未驗證；獨立性：{獨立／同 context 自檢}；若只能改一處：{那一處的基石，或「無」}。」

## Not-for boundaries

- Auditing the user's project agent configuration and AI-maintainability → `/health`.
- Diagnosing a reported error or failing behaviour from its symptom → `/hunt`; a review judges a finished target, it does not chase a bug.
- Verifying baransu's own skill structure → `scripts/verify-skills.py`.
