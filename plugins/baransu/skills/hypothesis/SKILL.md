---
name: hypothesis
description: "Writes down how part of a system must behave as a machine-checked formal model — TLA+ by default — with plain rules and step-by-step state diagrams, from code, a symptom, or documents; owns and maintains it so other skills can read one status line. Trigger On '/hypothesis', '假說', '這個模組不能出錯', '畫狀態圖給我看', '文件有沒有矛盾', '是否滿足', 'SD 有沒有滿足 SA', '先建立假說', '證明所有順序都不會壞', 'model-check this'. Not for proving it on the running app (/prove-it) or tracing a root cause (/hunt)."
argument-hint: "<path|module|HUNT-id|symptom|doc> [--satisfies <rules-doc>] [--maintain [area]]"
---

# hypothesis — write it down so a machine can check it and a person can read it

A hypothesis is a claim about how part of a system — or a process a document describes — must behave, always written as a formal model, citing its source, checked by a tool within a stated scope, and explained in plain rules and a progressive series of state diagrams. This skill is its only writer and keeps it in step when the source changes. Every other skill reads it through one script and acts on one computed state; none of them writes it.

The default this skill corrects: asked to make something "not go wrong", the model writes more tests of the cases it already thought of, or a model that passes because nothing in it can happen. A hypothesis is the opposite of both: every order the model allows is explored, it is seen failing on a broken variant and seen succeeding on its goals, and what was not formalized says why.

All user-facing output is in Traditional Chinese; identifiers, paths, model code and quoted source stay as they are. Words follow the repo glossary (`CONTEXT.md`): a hypothesis is 成立 (`established`), 未成立 (`draft`) or 無法成立 (`unformalized`); a rule is 守住 or 被打破 — never 證實／推翻, which are `/prove-it`'s, the step that proves a hypothesis.

## Outcome Contract

- **Outcome**: every claim in scope ends as a hypothesis whose computed state is `established` (成立假說) or `unformalized` (無法成立假說), with nothing unexplained.
- **Done when**: the rules were confirmed by the user; every model part cites its source; each safety and liveness rule was seen failing on a broken variant; each goal was seen reachable and seen unreachable with one transition removed; the scope is stated; every unformalized part has a reason record; `scripts/hypothesis-status.py --area <area>` prints the intended state; the diagram page (its figures drawn by `/draw`) is open; an `established` code area with a rule 被打破 was handed to `/prove-it` and each path carries its verdict.
- **Evidence**: the `check` block of `hypothesis.json` (tool, version, command, bounds, states, seen_failing, seen_succeeding), `check.txt`, and the status line quoted.
- **Output**: `.claude/hypothesis/<area>/` per `references/artifact.md`, never archived by `/ship`; no product code edited.
- **Automation**: ultracode=neutral, loop=assisted（`--maintain` is called by readers without a person and pauses only when a change may have changed a promise with no evidence; a first write needs the person to confirm the rules — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）
- **Telemetry**: on invocation, append one selection record per `../_shared/selection-telemetry.md`.

PAUSE classification for non-interactive drivers: `references/loop-pauses.md`.

## 1. Decide whether this is a hypothesis

Run `scripts/hypothesis-status.py --files <target>` first (`python` where `python3` is absent):

- an existing `established` hypothesis covering the target is not-trigger 5: rerun it with the `--check` command and write nothing new;
- a `stale`, `draft` or `broken` one goes to §6;
- a `legacy` one of the same area is moved first (§6, Migration) — one area never lives in two places.

Otherwise match the target against H1–H8 and the not-trigger list in `references/formal.md`. Before creating anything, confirm the matched row's default tool runs here (for TLA+: Java and `tla2tools.jar`); a missing tool goes to `/health`'s environment doctor, and if it stays missing the result is `unformalized`, class `no-tool`, never a half-built area. A miss ends with one reason record (`templates/reason-record.md`) in the caller's output, not under `.claude/hypothesis/`.

## 2. Read the source and name the area

Decide the input kind from the argument alone and say it in the first status line so the user can correct it:

- a path or symbol in code → code;
- a `HUNT-YYYY-NNN` id, or a sentence describing a failure → symptom;
- one document → document;
- `--satisfies`, or wording such as 「A 是否滿足 B」 → two sources, each a document or code, with the roles stated in the first line (the one flag kept, because without the wording the direction cannot be guessed).

Then read the source as its adapter in `references/sources.md` says. Choose the area name (`references/artifact.md` § Area name). Record the coverage — every cited file, and every writer of the guarded state as watch patterns — while you read, not after.

## 3. Confirm the rules in plain words

Show the user, and wait for them:

- one sentence per rule, of kind safety (不能發生), liveness (終究會發生) or goal (做得到), with no variable or action names, each with its citation;
- for a document, every extracted rule with its quote and location, ticked by the user one by one;
- every ambiguity as a question with whom to ask, never filled in;
- every part that will not be formalized, with its reason class, before modelling starts.

This is the one Input PAUSE of a first write (`references/loop-pauses.md`).

## 4. Model and check

Choose the tool and hold to the strictness rules in `references/formal.md`: true to the source — what the model takes as one step is indivisible in the source — and the source's names. Run the check with one pinned command, sending the tool's scratch output to the system temp dir. Then both evidence gates, both mandatory:

- **seen failing** — for each safety and liveness rule, make a broken variant in a scratch copy of the source, see the check catch it, keep the variant under `variants/`, drop the copy; a rule the source as written already breaks names the source as its evidence instead (`references/formal.md` § Strict, 2);
- **seen succeeding** — reach each goal, then remove one named transition and see the goal become unreachable.

A counterexample every step of which the source can take is a finding: write it as a script in the source's words under `paths/` (`templates/path.md`). A step the source cannot take is a model error: fix the model and say what was wrong. Never weaken a rule, a bound or the model to pass.

## 5. Draw and publish

Have `/baransu:draw` draw the diagram series per `references/diagrams.md` — static State Machine figures into `diagrams/`, `--quick`, one seed with no polish: diagram 1 is the happy path with at most 7 states, each next one adds one part, the last numbers every path with the same `P<n>` ids as `paths/` — then write the index page `diagrams.html`. Write `README.md` from `templates/README.md`. Publish per `references/artifact.md` § Writing — `hypothesis.draft.json`, then `scripts/hypothesis-publish.py <area dir>` — and run `scripts/hypothesis-status.py --area <area>`. Quote its line. If it does not print the state you intended, a gate is missing: fix it and publish again. Open the page for the user.

When the state is `established`, a rule is 被打破, and the behaviour side is code that runs (a `/draft` sketch is not), invoke `/prove-it` at once on the area's paths, the way a reader that sees `stale` invokes `--maintain`: it replays each `paths/P<n>.md` on the real app with the forced order the path states. A path it 推翻 — the app does not take one of its steps — is a suspected model error (`references/formal.md` § Strict, 5): find the step the model allows and the source does not, fix the model, and publish again. A path 無法到達 stays a finding read from the source, and the report says so. A document has no app to replay on; say that instead.

## 6. Keep it in step (`--maintain`)

Follow `references/maintain.md`. It turns on by itself when the target is covered by a `stale`, `draft` or `legacy` hypothesis, and readers invoke it when they see `stale`. Start from `hypothesis-status.py --all`; for each listed area, read every change since `sync.commit` and every `new-writer` the script names twice — what the source does now, the way `/how` reads it, and why it changed, the way `/why` looks for reasons — sort each into the four outcomes, rerun before and after, re-derive the variants when the model changed, then publish as §5. The first run offers to move any `.claude/prove-it/formal/<area>/` (§ Migration).

## 7. Report

Plain first, then detail. Each finding, path and question opens with one sentence in everyday words — none of 活性、安全性、精化、不變式、同步點、TLC、模型、狀態空間 — then its technical layer (`file:line`, tool, states, rule name). This rule is this skill's own; it does not call `/huh`. Then the one closing line, fixed:

「hypothesis 完成：{area}｜{成立假說／無法成立假說}｜{N} 條規則，{F} 條被打破（{path ids}）、{H} 條守住｜{tool} {version}，{states} 個狀態｜範圍：{bounds}｜同步：{sync}｜圖：{page path}」

For documents add 「矛盾 {c}｜缺漏 {g}｜模糊 {a}」. Add the unformalized count and the README section it lives in. After a replay, `/prove-it`'s own closing line follows, and each path in the report carries its 證實／推翻／無法到達.

## For readers

Readers — `/prove-it`, `/review`, `/hunt`, `/health`, the green step of `../_shared/tdd.md`, `/draft` — follow `references/reading.md` and nothing else here (the state picture they share is `../_shared/hypothesis-states.md`): they run the status script, read `state`, and act per its state × reader table. They never open `hypothesis.json`, never compare commits or hashes, never write under `.claude/hypothesis/`.

## Not-for boundaries

- Proving it on the running app, replaying a counterexample with forced order → `/prove-it`.
- Finding the cause of a failure → `/hunt`, which hands an H1–H3 symptom here and turns paths into conjectures.
- A claim one run can settle, a static permission check, look and copy → not a hypothesis; red/green under `../_shared/tdd.md`.
- A figure polished for a presentation → `/draw`, by hand.
