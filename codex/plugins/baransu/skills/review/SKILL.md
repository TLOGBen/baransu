---
name: review
description: 'Reviews a diff, PR, plan, artifact, or quoted claim against what the user asked for, by reading only: finds every place that no longer holds with the change and reports each with two citations and a verdict. Trigger On 「看一下」「幫我看」「check 一下」「review 一下」「是不是做過頭了」, "take a look at X". Not for a reported error ($baransu:hunt) or the project''s agent config ($baransu:health).'
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

# review — find the places that no longer hold

Arguments the user may give after `$baransu:review`: `<diff | PR | file | plan | quoted claim> [--full] [--model <m>] [--effort <e>]`.

## Codex Port Adapter - Bundled Agent Resolution

This plugin does not assume package-local TOMLs are auto-registered as custom
agents. The required definitions for this skill are bundled at
`../../.codex-agents/<agent-name>.toml`: `reviewer`, `verifier`.

Before every named-agent dispatch:

1. Resolve the exact bundled TOML from this `SKILL.md` directory (strip a
   leading `baransu:` namespace from the requested name).
2. Verify the file exists, then pass its absolute path and the task input to a
   generic Codex subagent. The first instruction to that subagent is to read
   the TOML's `developer_instructions` completely before doing any task work
   and to treat relative paths as relative to the TOML file.
3. If the TOML is missing or unreadable, stop with
   `AGENT_DEFINITION_MISSING: <path>`. Never invent, summarize, or substitute a
   role from the agent name.

Paths this skill hands to an agent are absolute, resolved from this `SKILL.md`
directory — for example the principles directory is the absolute path of
`references/principles/`.

`--model` and `--effort` map to `spawn_agent`'s `model` and `reasoning_effort`
parameters. When the runtime's `spawn_agent` does not expose them, or rejects
the value, report that in the limits; never substitute another model or effort.


## Codex Port Adapter - Review Isolation

This skill is countering the model's inertia to rubber-stamp its own prior work, so "fresh" means a context that never saw the authoring conversation. Spawn every reviewer and verifier without parent history: `fork_turns="none"` on `spawn_agent` (`fork_context=false` on the older tool; `spawn_agent` otherwise inherits the whole conversation by default). The task message carries only what the steps below hand over. If `spawn_agent` is unavailable or cannot start without parent history, run the agent in an independent Codex invocation or session that writes its result to a file, and read the result from that file; if neither is possible, the pass is a same-context pass and the report says so.

Do not simulate independent review by asking the same conversation context several times in sequence. Authorization PAUSE remains a hard stop; only input-selection PAUSE may degrade to direct text questions.


A change is right when every place that owns, restates, or relies on what it changed still holds with it. The first of those places is the user's goal. A place holds in three ways, and a problem is a place that fails one:

- **It says the same.** Any place that states the fact — in passing or by its job — states the new one.
- **It says it where it is owed.** A place whose job is to state the fact — a table, a list, a description, a spec, an example, an expected result — states it rather than leaving it out.
- **It gets what it needs.** Each consumer — a caller, a later step, a listener, a platform, the user — receives what it relies on: a value, a state, a moment, an environment.

Each problem is shown by two citations: the target's side, and the place that no longer holds — quoted where it is written, or derived from what the code does with the fact（「第 N 行拿這個值去做 Y，所以它需要 Z」）. A principle's article is the second citation where `references/principles/index.md` says. A problem counts whichever change introduced it, whatever note admits it, however small; size orders problems and never removes one. A clean review is a valid result（「乾淨的 review 也是有效的 review」）.

A review only reads. The evidence already exists: the code, its tests, its history, and the author's record of running them on this version. Running them is the author's part. What the evidence settles neither way is uncertain, listed with what would settle it; where only a run could, the line reads 「coverage lost: needs X」, for the author to close.

All user-facing output is in Traditional Chinese.

## Outcome Contract

- **Outcome**: One review of the pinned target against the user's goal, reporting each place that no longer holds as two citations with its chain, every walked place with its verdict, the uncertain and excluded places, independence, and limits.
- **Done when**: Target, goal, and scope are pinned; the change map and the walk exist; the reviewer has returned a verdict for every place on the walk, with the principles it loaded; under `--full`, the verifier has checked every citation and confirmed or adjusted every problem's severity and confidence; each retained problem carries both citations and its chain, each exclusion its proof, each uncertain place what would settle it; each standing question is answered or marked 不確定; the verdict is computed by its printed rule; zero problems with stated scope is a complete result.
- **Evidence**: The two citations of every retained problem (as the verifier read them, under `--full`), the records the review relied on, the walk, and the independence statement.
- **Output**: A Traditional Chinese review report in the conversation; `.codex/review/<slug>.md` when persistence is useful or requested (`$baransu:ship` archives that directory).
- **Automation**: ultracode=neutral, loop=drivable（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）

PAUSE classification for non-interactive drivers: `references/loop-pauses.md`.

## 1. Pin the target, the goal, and the scope

Pin the supplied artifact, diff, plan, or directly quoted claim. Do not invent a diff base, a target, or a claim from an author's completion statement; if none can be pinned, ask for it and stop.

The goal comes from acceptance when present (criteria the user names, a `.codex/think/<slug>.md` plan's Building and Not building sections, a spec), otherwise from the request in its own words, not the author's summary of it.

Scope is each fact the change alters and every place that fact reaches. With `--full`, each fact is followed to the end of its lifecycle across the whole system. Depth follows consequence: stop where another look could no longer move the verdict or the user's next decision.

Review-only: no edits to the target, its tests, configuration, or working tree, including typos and formatting, and no running the target, its tests, or experiments. A proposed bedrock is part of a finding, not a change.

## 2. Map the change, then lay out the walk

This step is done once, before any place is judged — by the reviewer itself in the default pass, by the session running the review under `--full` — from command output alone — `git diff --stat`, `git log`, `git blame`, `grep -n`, the CI's run listing — without opening the places it finds. Before laying out the walk, load the principles `references/principles/index.md` sets for the walk stage, and lay out the walk with them. Each place is read once, by whoever judges it.

**The change map.** Read the change as `git diff -W` prints it — each touched function whole, since its unchanged lines now run with the change — and go through it from its first edit to its last and list each fact it alters: a name, a value, a rule, a signature, an output, a behaviour, a promise in prose. A changed line that only reads a state — a condition, a guard, a branch — changes when that state matters: list the state as a fact. Beside it, list what the goal requires. Every edit serves a goal item or serves none; every goal item has its edit or lacks it.

**The walk.** For each fact, list where else it lives, and for each place the question it must answer — what it states, or what it needs. Use the method of `$baransu:why` and `$baransu:how` on this change rather than running those skills:
- **History** (the `$baransu:why` anchor): `git log` and `git blame` of the changed lines' previous versions, the commit and PR messages, plans and decisions they cite, earlier fixes or reverts in the same area. A decision already made is a place the change must hold with; a mistake this repo has made twice is where to look first.
- **Lifecycle** (the `$baransu:how` flow): each fact from where it is born to where its result is finally taken, as `blast-radius.md` lays out.
- **Copies and contracts**: every other statement of the fact under each form it takes — its name, its old value, the words a description would use — in code, prose, tables, examples, expected results, and mirrors; and for each file the change touches, the rules that govern that file — the schema, loader, adapter, or tool that reads it.
- **Records and environments**: the author's run records of this version (CI, attached output) and the environments they ran in.

Hand the walk over as locations and questions, not as quotes to compare: a short quote shows what a place says, never what it fails to say or fails to get.

## 3. Choose the depth

`--model` and `--effort` set the model and reasoning effort of every agent the review dispatches; without them each agent inherits the session's. A value the host does not support is reported, never silently replaced.

- **Default**: one fresh reviewer does the whole review — maps the change, lays out the walk, walks it, and reports — in its own context, so the session stays clean and the pass is independent of the author. No second reader checks its citations; the report says so.
- **`--full`**, or the user asks for a full or thorough review（「完整審」「仔細審」）: the session maps the change and lays out the walk — unless it authored the target, in which case the reviewer builds them as in the default — a fresh reviewer walks it, a fresh verifier checks every citation, and each fact is followed to the end of its lifecycle.

If a fresh agent is unavailable, or the current session authored the target, disclose it: a same-context pass can find problems but cannot earn an independent verdict.

## 4. Stage one — the reviewer

Dispatch the bundled `reviewer` agent (`../../.codex-agents/reviewer.toml`, per the adapter above) with the pinned target, the goal, the scope, and the absolute path of this skill's `references/principles/`; in the default pass it also takes step 2 of this skill and builds the change map and the walk itself, and under `--full` it takes the session's change map and walk instead. The author's defense or desired verdict is not evidence and is not handed over.

The reviewer reads `principles/index.md` and loads each principle whose trigger a place meets, then walks every place: it reads the behaviour there, answers the place's question, and gives the place one verdict. **Holds**: proved as `evidence.md` #8 requires. **Fails**: a finding with two citations and its chain, under the header `principles/index.md` defines — a place whose behaviour departs from the goal or a contract, or that a contract permits to carry a loaded principle's risk, fails at the confidence its evidence reaches. **Uncertain**: neither can be shown yet; one line naming what would settle it. Every place on the walk ends in one of the three. A place the reviewer suspected of failing and then found holding is an exclusion, kept with its proof. It also returns each principle it loaded and the place that needed it, and the places it added.

## 5. Stage two — the verifier (`--full`)

Dispatch a fresh bundled `verifier` agent (`../../.codex-agents/verifier.toml`, per the adapter above) with the change map, the reviewer's findings, and its exclusions with their proofs, never with its reasoning beyond them. Other holds and uncertain verdicts go to the report as they are. For each finding it opens both citations, confirms each says what the finding quotes, re-derives any derived need from the consumer's code, confirms both concern the same fact in the same scope, version, and environment, and confirms the place fails in the way the finding names. A finding is dropped only as unfounded — its target side is not in the pinned version — or with the line showing the place holding; an exclusion stands only on its proof; the rest becomes uncertain, with the failed check named. It confirms or adjusts every retained finding's severity and confidence, with the evidence.

## 6. Judge the chain

Every retained problem is one chain:

1. **Phenomenon** — the target's side: its citation, the trigger, what it does.
2. **Impact** — the place that no longer holds: its citation or derived need, which of the three ways it fails, and which part of the goal fails with it.
3. **Root** — why it could be written: a copy no source keeps in step, a contract owned elsewhere, an environment the author's run never covered, a consumer the change never read, two definitions in one place, a principle the design skipped. A symptom is not a root.
4. **Bedrock** — the restated statement that makes it impossible, preferring deletion and simplification to a guard beside the symptom, with the level the fix belongs at: one owner by architecture, then a type, then a check whose error names the fix, then a test, and documentation last, only for a judgment call. Name why a higher level does not work.
5. **Verification** — under `--full`, the verifier's check of both citations; in the default pass, the reviewer's own reading of both, marked as not checked by a second reader.

Where no place states what should hold and the code alone cannot show what a consumer needs, a principle's article is the second citation, reported as 「沒有地方寫明，但違反原則 X 第 n 條」 with the risk it carries; where no principle covers it either, it is a question for the user, not a problem.

A count or an "it ran" claim is evidenced only by the output of the author's run, never by a sentence someone typed, and is checked against the exact noun and scope claimed, per `../_shared/fact-check.md`. Removing what the goal carries — validation at a trust boundary, handling that prevents data loss, security, accessibility, anything the user asked for — fails the goal, so no bedrock proposes it. A review whose bedrocks are all guards has stopped at symptoms and says so. Do not suppress a contradiction to your own earlier authoring decision by declaring it off-goal.

If reviewing a workflow or a skill, the root is usually a clause: distinguish human-owned purpose from compensation for a model failure; shorter instructions or a stronger model are not evidence that a long-run protection is obsolete.

## 7. Report

Write plain Traditional Chinese: what was reviewed, against which goal, how independently; each problem under its header and as its chain（現象／影響／根源／基石／驗證）with both citations and the user's next step; each English term explained at first use; no fact the evidence has not established. Report the principles loaded and why, the places walked with their verdicts, problems, independence, and limits, with one line per standing question — 做到了／多做了／做小了 — stating its verdict or 不確定. End with two lists, one line per item: 不確定 — each uncertain place or question and what would settle it, 「coverage lost: needs X」 where that is a run; 排除 — each exclusion and each dropped finding, with its reason. No problems is not universal correctness; no tests is not an exempt layer; an absent required record is unverified, not passed. When the host offers a tool for reporting findings, report through it; its specification governs its own fields, and what those fields cannot hold goes in the report text.

The verdict is computed by this rule, printed beside it, never by opinion: **PROVEN** when each goal item and standing question is answered with evidence, each runnable behaviour the target claims is covered by the author's record of this version, and nothing failed; **NOT PROVEN** when a problem of severity 3 or more stands, or a record shows a failure inside what the target claims or pins; **PARTLY PROVEN** when neither holds but a problem of severity 0–2 stands or required evidence is missing — each such problem by its header, a behaviour or platform with no record of this version, a recorded failure outside what the target pins, no independent pass, anything left 不確定 — each listed as the reason. A verdict is recomputed from this run's evidence, never carried over.

Close with one line the user can act on:
「review 完成：判定 {PROVEN／PARTLY PROVEN／NOT PROVEN}（{觸發的規則一句}）；{N} 項問題（嚴重程度 ≥3 的 {M} 項）、{K} 項不確定；獨立性：{獨立／同 context 自檢}；若只能改一處：{那一處的基石，或「無」}。」

## Not-for boundaries

- Auditing the user's project agent configuration and AI-maintainability → `$baransu:health`.
- Diagnosing a reported error or failing behaviour from its symptom → `$baransu:hunt`; a review judges a finished target, it does not chase a bug.
- Verifying baransu's own skill structure → `scripts/verify-skills.py`.
