---
name: review
description: 'Independent re-verification of a concrete artifact, diff, plan, or directly quoted claim against the user''s goal, by reading it and the author''s run records of this version: a problem is where the target fails that goal, traced phenomenon → impact → root → restated bedrock → verification; a fresh reviewer loads only the lenses its claims need, a fresh verifier rules on its proposals; never edits the target; verdict by a printed rule (PROVEN / PARTLY PROVEN / NOT PROVEN); a clean review is a valid result. Trigger On 「看一下」「看看」「幫我看」「check 一下」「review 一下」「是不是做過頭了」, or casual "take a look at X". Not for auditing the user''s own project agent-config (route to /health) or diagnosing a reported error (/hunt). 繁體中文輸出。'
argument-hint: "<diff | PR | file | plan | quoted claim> [--full] [--model <m> | --model <stage>=<m>] [--effort <e>]"
---

# review — find where the target fails the user's goal

A problem is a place where the target fails the user's goal, whichever change introduced it, whatever note already admits it, and however small: size orders problems and never removes one, so nothing sits between problems and limits. The goal is the only baseline — consistency means every place agrees with the goal, not merely with each other, so a part is not excused because a sibling, a copy, or an earlier version fails the same way. Performance, consistency, and security belong to every goal; only the user waives a part of one. A clean review is a valid result（「乾淨的 review 也是有效的 review」）.

Every retained problem is one chain:

1. **Phenomenon** — what the target does, at a location, under a trigger, read from the code, its tests' assertions, and this version's recorded runs. A failed record suspects the observation first: a recorded run outside what the target claims or pins shows the run, not the target.
2. **Impact** — which part of the user's goal it fails.
3. **Root** — the statement, premise, or model default that produced it; a symptom is not a root.
4. **Bedrock** — the restated statement that makes the phenomenon impossible: replacement text, preferring deletion and simplification to a guard beside the symptom.
5. **Verification** — a read showing each link above holds and the bedrock breaks nothing else.

A review judges evidence that already exists: the code, its tests, and the author's record of running them on this version. Running them is the author's part; reading that record is the review's. What the review would have to run to settle a claim is exactly what the record lacks, and that gap is the result: 「coverage lost: needs X」 in the limits, for the author to close — an observation the review made itself would answer a question the author's record leaves open, and hide that it is open. A claim of passing with no record of this version is a problem.

All user-facing output is in Traditional Chinese.

## Outcome Contract

- **Outcome**: One independent review of the pinned target against the user's goal, converging into a report of the lenses loaded, the problems verified, each with its chain, independence, and remaining limits.
- **Done when**: The target, goal, claim map, and scope are pinned, the reviewer has returned with its lenses named, both verifier passes have returned, each retained problem carries its chain, any unverified link marked, each claim and standing question is answered or marked unverified, the verdict is computed by its printed rule, and independence and limits are stated; zero problems with stated scope is a complete result.
- **Evidence**: The verifier's returned observations, the run records they rest on, and, for every retained problem, the evidence behind each link of its chain; the independence statement.
- **Output**: A Traditional Chinese review report in the conversation; `.claude/review/<slug>.md` when persistence is useful or requested (`/ship` archives that directory).
- **Automation**: ultracode=neutral, loop=drivable（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）

PAUSE classification for non-interactive drivers: `references/loop-pauses.md`.

## Pin the target, the goal, and the scope

Pin the supplied artifact, diff, plan, or directly quoted claim, and the goal it serves. Do not invent a diff base, a target, or a claim from an author's completion statement; if none can be pinned, ask for it and stop.

Scope is the change and what it directly touches — the rest of each changed unit, its callers and callees, other readers of the data it changes. With `--full`, scope is the whole system the change leaves behind, and each fact is traced to its end. Depth within the scope follows consequence: look as far as the conclusion could move the user's next decision, and stop where another look could no longer change the verdict or that decision.

Review-only means no target, test, configuration, or working-tree edits, including obvious typos and automatic formatting. A proposed bedrock remains part of a finding. Creating a requested separate review report does not authorize changing the reviewed material.

The goal comes from acceptance when present (criteria the user names, a `.claude/think/<slug>.md` plan's Building and Not building sections, a spec), otherwise from the request as stated, not the author's summary of it; neither acceptance nor a plan is a prerequisite. Before reading the change through, write the claim map: each behaviour the goal requires and each the target says it delivers, worded so that a record, an assertion, or a line could settle it, beside the evidence that would. A claim is read from that evidence — this version's record first, since a record can settle it before any other reading — and is done when its answer is settled; every edit then serves a claim or serves none, and every claim has its edit and evidence or lacks them. Every review asks three standing questions of that map — the goal lens it always carries:

1. **Did it do what was asked?** Correctness of the asked-for behaviour across the scope; under `--full`, from the user's trigger to where the user sees the result complete. The change works only if facts outside its lines hold — the untouched lines of a changed unit, when each step starts, what takes the result once the change hands it off — and these are reached through timing, lifecycle, indirect dispatch, and other readers of the same data more often than through a call a search finds. Name each such fact and prove it, stating the level reached: cited line, reasoned through every branch, shown by the author's record of this version. The changed unit's own tests prove the unit, not the path; a fact left below the strongest level the existing evidence reaches leaves this question 未驗證.
2. **Did it add what was not asked?** Guards for states no caller produces, error handling that hides instead of fails, an interface with one implementation, an option nobody requested, validation repeated behind a boundary that already validates. The cost it adds is the impact.
3. **Did it solve a smaller problem than asked?** The happy path only, a requirement silently narrowed, the hard part left as a TODO or an "out of scope" the request never granted, tests whose assertions would pass with the asked behaviour broken. Cite the dropped part.

## Dispatch

Two stages, one fresh agent each, so the agent that rules on a problem is never the one that proposed it. Fetch the shared evidence once — the pinned target, the author's run records of this version — and hand both agents the same copy with the goal, the claim map, the scope, and the definition of evidence above; each reads from what it was handed and fetches only what a claim needs beyond it. The author's defense or desired verdict is not evidence and is not handed over. `--model` and `--effort` set the model and reasoning effort of every agent the review dispatches (`--model <stage>=<m>` sets one stage); without them each agent inherits the session's. A value the host does not support is reported, never silently replaced.

- **Reviewer** — a fresh agent that works from the claim map and proposes problems as chains, each with the evidence it cites. The perspective lenses in `${CLAUDE_PLUGIN_ROOT}/agents/` are references it loads for a claim whose answer turns on the lens's question, and not otherwise: **quality** — does what the target states hold together and match what it does, in code or prose; **architecture** — does a definition, interface, or boundary other parts rely on still hold for them; **security** — is input, a credential, or a command checked where it crosses a trust boundary; **domain** — are business states, transitions, or rules legal, judged against a transition table from the spec or upstream paths. It reports each lens it loaded and the claim that needed it.
- **Verifier** — load `${CLAUDE_PLUGIN_ROOT}/agents/verifier.md` completely and dispatch a fresh verifier at the same time as the reviewer, naming performance as a place to look. Its first pass — the standing questions, the author's run evidence, the consistency sweep — never sees the reviewer's output. When the proposals return, hand them with their evidence to the verifier for a second, light pass that rules on each chain from that evidence.

With `--full`, each lens the claims need instead runs as its own fresh subagent in parallel, one lens each, with the reviewer's brief; all their proposals go to the verifier's second pass.

If a fresh agent is unavailable, or the current session authored the target, disclose the limitation. A same-context self-check can still find problems, but cannot earn an independent pass.

## Judge the chain

A count or an "it ran" claim is evidenced only by the output of the author's run, never by a sentence someone typed, and is checked against the exact noun and scope claimed, per `../_shared/fact-check.md`.

A phenomenon that holds and fails the goal is a problem; a wrong root or bedrock is traced again, and if it cannot be, that link is marked unverified — never a reason to drop the problem. Weigh a plausible disconfirming explanation against a severe finding's evidence; repeated agreement from the same model is one source, not independent ground truth.

Removing what the goal carries — validation at a trust boundary, handling that prevents data loss, security, accessibility, anything the user asked for — fails the goal, so no bedrock proposes it. Do not suppress a contradiction to your own earlier authoring decision by declaring it off-goal.

The bedrock link is where a guard falls out: try deleting, reusing what the codebase already has, a platform feature, a one-line change, and only then a mechanism, which names the failure it makes impossible. A review whose bedrocks are all guards has stopped at symptoms and says so. Separate problems from what remains unverified.

If reviewing a workflow or a skill, the root is usually a clause: distinguish human-owned purpose from compensation for a model failure, and evaluate the actual failure conditions and enforcement surface; shorter instructions or a stronger model are not evidence that a long-run protection is obsolete. Do not promote a short scenario's record into a reliability claim for an hours-long coupled task.

A finding's validity does not itself authorize extra rounds, fixes, or a broader target.

## Report

Write plain Traditional Chinese: what was reviewed, against which goal, how independently; each problem as its chain（現象／影響／根源／基石／驗證）with the user's next step; each English term explained at first use; no fact the evidence has not established. Report the lenses loaded and why, examined scope, problems, evidence, independence, and limits, with one line per standing question（做到了／多做了／做小了）stating its verdict or 未驗證, the 做到了 line naming each fact the path rests on and the level it reached. No problems is not universal correctness; no tests is not an exempt layer; an absent required record is unverified, not passed. When the host offers a tool for reporting findings, report through it; its specification governs its own fields, and a root or bedrock those fields cannot hold goes in the report text.

The verdict is computed by this rule, printed beside it, never by opinion: **PROVEN** when each claim and standing question is answered with evidence, each runnable behaviour the target claims is covered by the author's record of this version, and nothing failed; **NOT PROVEN** when a problem stands or a record shows a failure inside what the target claims or pins; **PARTLY PROVEN** when nothing failed but required evidence is missing — a behaviour or platform with no record of this version and no claim that it passed, a recorded failure outside what the target pins, no independent pass, a question 未驗證 — each listed as the reason. A verdict is recomputed from this run's evidence, never carried over from an earlier review.

Close with one line the user can act on:
「review 完成：判定 {PROVEN／PARTLY PROVEN／NOT PROVEN}（{觸發的規則一句}）；{N} 項問題、{U} 項未驗證；獨立性：{獨立／同 context 自檢}；若只能改一處：{那一處的基石，或「無」}。」

## Not-for boundaries

- Auditing the user's project agent configuration and AI-maintainability → `/health`.
- Diagnosing a reported error or failing behaviour from its symptom → `/hunt`; a review judges a finished target, it does not chase a bug.
- Verifying baransu's own skill structure → `scripts/verify-skills.py`.
