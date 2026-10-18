---
name: review
description: 'Independent review of a concrete artifact, diff, plan, or directly quoted claim against the user''s goal, by reading only: a problem is two places that disagree about the same thing — the goal, a copy, a contract, a record, a consumer, or a principle against the target — shown as two citations and traced phenomenon → impact → root → restated bedrock → verification; one fresh reviewer applies the principles its places need, one fresh verifier checks every citation; never edits or runs the target; verdict by a printed rule (PROVEN / PARTLY PROVEN / NOT PROVEN); a clean review is a valid result. Trigger On 「看一下」「看看」「幫我看」「check 一下」「review 一下」「是不是做過頭了」, or casual "take a look at X". Not for auditing the user''s own project agent-config (route to /health) or diagnosing a reported error (/hunt). 繁體中文輸出。'
argument-hint: "<diff | PR | file | plan | quoted claim> [--quick | --full] [--model <m>] [--effort <e>]"
---

# review — find where two places disagree

A change is right when every place that owns, copies, consumes, or judges what it changed still agrees with it. The first of those places is the user's goal. A problem is a disagreement between two places about the same thing, shown by citing both: the goal says X and the target does Y; one copy says A and another says B; a caller relies on one thing and the callee does another; a run record contradicts what the code assumes; a principle's article says one thing and the code does another. A disagreement is a problem whichever change introduced it, whatever note admits it, however small. Size orders problems and never removes one. A clean review is a valid result（「乾淨的 review 也是有效的 review」）.

A review only reads. The evidence already exists: the code, its tests, its history, and the author's record of running them on this version. Running them is the author's part. Where only a run could settle a question, that missing run is the result: 「coverage lost: needs X」, for the author to close.

All user-facing output is in Traditional Chinese.

## Outcome Contract

- **Outcome**: One review of the pinned target against the user's goal, reporting each disagreement found as two citations with its chain, the places checked and found in agreement, independence, and limits.
- **Done when**: Target, goal, and scope are pinned; the change map and place list exist; the reviewer has returned with the principles it loaded; the verifier has checked every citation (or `--quick` disclosed the same-context pass); each retained problem carries both citations and its chain; each standing question is answered or marked 未驗證; the verdict is computed by its printed rule; zero problems with stated scope is a complete result.
- **Evidence**: The two citations of every retained problem as the verifier read them, the records the review relied on, the place list, and the independence statement.
- **Output**: A Traditional Chinese review report in the conversation; `.claude/review/<slug>.md` when persistence is useful or requested (`/ship` archives that directory).
- **Automation**: ultracode=neutral, loop=drivable（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）

PAUSE classification for non-interactive drivers: `references/loop-pauses.md`.

## 1. Pin the target, the goal, and the scope

Pin the supplied artifact, diff, plan, or directly quoted claim. Do not invent a diff base, a target, or a claim from an author's completion statement; if none can be pinned, ask for it and stop.

The goal comes from acceptance when present (criteria the user names, a `.claude/think/<slug>.md` plan's Building and Not building sections, a spec), otherwise from the request in its own words, not the author's summary of it.

Scope is each fact the change alters and every place that fact reaches. With `--full`, each fact is followed to the end of its lifecycle across the whole system. Depth follows consequence: stop where another look could no longer move the verdict or the user's next decision.

Review-only: no edits to the target, its tests, configuration, or working tree, including typos and formatting, and no running the target, its tests, or experiments. A proposed bedrock is part of a finding, not a change.

## 2. Map the change, then find its places

This step is done once, by the session running the review, and handed to the agents as locations with short quotes, not file dumps.

**The change map.** Go through the change from its first edit to its last and list each fact it alters: a name, a value, a rule, a signature, an output, a behaviour, a promise in prose. Beside it, list what the goal requires. Every edit serves a goal item or serves none; every goal item has its edit or lacks it.

**The places.** For each fact, find where else it lives — the method of `/why` and `/how`, applied to this change rather than run as those skills:
- **History** (the `/why` anchor): `git log` and `git blame` of the changed lines' previous versions, the commit and PR messages, plans and decisions they cite, and earlier fixes or reverts in the same area. A decision already made is a place the change must agree with; a mistake this repo has made twice is where to look first.
- **Lifecycle** (the `/how` flow): where the fact is born, what reads it, when each step runs, what takes the result once the change hands it off — through timing, teardown, indirect dispatch, serialized formats, and other readers of the same data, not only the calls a search finds.
- **Copies and contracts**: every other statement of the fact under each form it takes — its name, its old value, the words a description would use — in code, prose, tables, examples, expected results, mirrors, and the specifications of tools and adapters the target uses.
- **Records and environments**: the author's run records of this version (CI, attached output) and the environments they ran in.

## 3. Choose the depth

`--model` and `--effort` set the model and reasoning effort of every agent the review dispatches; without them each agent inherits the session's. A value the host does not support is reported, never silently replaced.

- **Default**: one fresh reviewer, then one fresh verifier.
- **`--quick`**, or the user asks for a quick look（「快速」「看一眼」「簡單看一下」）: the session reviews the places itself, with no agents, and discloses that the result is a same-context pass, not an independent one.
- **`--full`**: the same two stages with the lifecycle followed to its end.

If a fresh agent is unavailable, or the current session authored the target, disclose it: a same-context pass can find problems but cannot earn an independent verdict.

## 4. Stage one — the reviewer

Dispatch `${CLAUDE_PLUGIN_ROOT}/agents/reviewer.md` with the goal, the change map, the place list, the scope, and the path `${CLAUDE_PLUGIN_ROOT}/skills/review/references/principles/`. The author's defense or desired verdict is not evidence and is not handed over.

The reviewer reads `principles/index.md`, loads each principle whose trigger a place meets, reads the places, and returns each disagreement as two citations with its chain, each place it checked and found in agreement, each principle it loaded and the place that needed it, and each question only a run could settle.

## 5. Stage two — the verifier

Dispatch a fresh `${CLAUDE_PLUGIN_ROOT}/agents/verifier.md` with the reviewer's findings and the agreement list, never with the reviewer's reasoning beyond them. For each finding it opens both citations and confirms that each says what the finding quotes, that both speak of the same thing in the same scope, version, and environment, and that they disagree. It confirms each agreement entry the same way. A finding whose citations fail is dropped with the failed check named; nothing is dropped for any other reason.

## 6. Judge the chain

Every retained problem is one chain:

1. **Phenomenon** — the target's side of the disagreement: its citation, the trigger, what it does.
2. **Impact** — the other side: its citation, and which part of the goal fails.
3. **Root** — why the disagreement could be written: a copy no source keeps in step, a contract owned elsewhere, an environment the author's run never covered, a consumer the change never read, two definitions in one place, a principle the design skipped. A symptom is not a root.
4. **Bedrock** — the restated statement that makes the disagreement impossible, preferring deletion and simplification to a guard beside the symptom, with the level the fix belongs at: one owner by architecture, then a type, then a check whose error names the fix, then a test, and documentation last, only for a judgment call. Name why a higher level does not work.
5. **Verification** — the verifier's check of both citations.

Where nothing states the expectation, a principle's article is the other citation; report it as 「沒有地方寫明，但違反原則 X 第 n 條」 with the risk it carries. Where nothing states it and no principle covers it, it is a question for the user, not a problem.

A count or an "it ran" claim is evidenced only by the output of the author's run, never by a sentence someone typed, and is checked against the exact noun and scope claimed, per `../_shared/fact-check.md`. Removing what the goal carries — validation at a trust boundary, handling that prevents data loss, security, accessibility, anything the user asked for — fails the goal, so no bedrock proposes it. A review whose bedrocks are all guards has stopped at symptoms and says so. Do not suppress a contradiction to your own earlier authoring decision by declaring it off-goal.

If reviewing a workflow or a skill, the root is usually a clause: distinguish human-owned purpose from compensation for a model failure; shorter instructions or a stronger model are not evidence that a long-run protection is obsolete.

## 7. Report

Write plain Traditional Chinese: what was reviewed, against which goal, how independently; each problem as its chain（現象／影響／根源／基石／驗證）with both citations and the user's next step; each English term explained at first use; no fact the evidence has not established. Report the principles loaded and why, the places checked and found in agreement, problems, coverage lost, independence, and limits, with one line per standing question — 做到了／多做了／做小了 — stating its verdict or 未驗證. No problems is not universal correctness; no tests is not an exempt layer; an absent required record is unverified, not passed. When the host offers a tool for reporting findings, report through it; its specification governs its own fields, and what those fields cannot hold goes in the report text.

The verdict is computed by this rule, printed beside it, never by opinion: **PROVEN** when each goal item and standing question is answered with evidence, each runnable behaviour the target claims is covered by the author's record of this version, and nothing failed; **NOT PROVEN** when a problem stands or a record shows a failure inside what the target claims or pins; **PARTLY PROVEN** when nothing failed but required evidence is missing — a behaviour or platform with no record of this version, a recorded failure outside what the target pins, no independent pass, a question 未驗證 — each listed as the reason. A verdict is recomputed from this run's evidence, never carried over.

Close with one line the user can act on:
「review 完成：判定 {PROVEN／PARTLY PROVEN／NOT PROVEN}（{觸發的規則一句}）；{N} 項問題、{U} 項未驗證；獨立性：{獨立／同 context 自檢}；若只能改一處：{那一處的基石，或「無」}。」

## Not-for boundaries

- Auditing the user's project agent configuration and AI-maintainability → `/health`.
- Diagnosing a reported error or failing behaviour from its symptom → `/hunt`; a review judges a finished target, it does not chase a bug.
- Verifying baransu's own skill structure → `scripts/verify-skills.py`.
