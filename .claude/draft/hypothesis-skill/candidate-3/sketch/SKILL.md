---
name: hypothesis
description: "Writes down a hypothesis: a claim about how part of a system behaves, always as a formal model a machine checks (TLA+ by default), every part citing its source, with plain rules and a step-by-step state-diagram page; reads code, requirement documents, or two documents against each other, and keeps the hypothesis in step when its source changes. Trigger On '/hypothesis', '假說', '寫成假說', '這個模組不能出錯', '畫狀態圖給我看', '這兩份文件對得上嗎', 'SD 有沒有滿足 SA', 'model-check this'. Not for running the app to prove a claim (/prove-it) or tracing a bug's cause (/hunt)."
argument-hint: "<code path | document | symbol> [claim] [--against <rules source>] [--seed <hunt case>] [--tool <name>] [--unbounded] | --maintain [area]"
---

# hypothesis — write it down so a machine can check it and a person can read it

(unimplemented) One paragraph: a hypothesis is one claim, written as a formal model, checked by a machine, readable without the tool. This skill writes it and keeps it; every other skill only reads it.

(unimplemented) One paragraph on the shape: two things vary — the source and the tool — and each sits behind a port with one adapter file per kind. The steps below never name a tool or a citation form; they speak the forms in `references/ports.md` and call the bound adapters.

All user-facing output is in Traditional Chinese; commands, paths, identifiers, quoted source passages and model text stay in their original form.

## Outcome Contract

- **Outcome**: (unimplemented) one hypothesis under `.claude/hypothesis/<area>/` that passed the strictness gates or names the gate it is stuck at.
- **Done when**: (unimplemented) the five gates in `references/formal.md` § Strictness, the page opened, every unformalized part has a reason record.
- **Evidence**: (unimplemented) the README frontmatter fields `scripts/hypothesis-status.py` reads, and the gate log.
- **Output**: (unimplemented) `.claude/hypothesis/<area>/` (README.md, model/, sources/, page.html) — a kept product, never archived by `/ship`.
- **Automation**: ultracode=neutral, loop=not-drivable（the rule confirmation and the page are read by the person; `--maintain` is decided in a later slice）

## 0. Bind the adapters

(unimplemented) Classify each argument by asking every source adapter's § Recognize, in the order code → document; two sources or `--against` bind `pair` around them. `--seed` is a claim origin, never a source. Choose the tool in step 3, not here. Load exactly the bound adapter files — at most three — and no others.

## 1. Extract the claim sheet

(unimplemented) The source adapter's § Read and § Extract fill the claim sheet (`references/ports.md` § Claim sheet): actors, states, steps with citations and atomicity, candidate rules (safety, goal, refinement), and the parts it will not model. A seed adds its symptoms as candidate rules. Nothing the source does not say is filled in; it becomes an ambiguity question.

## 2. Confirm the rules with the person

(unimplemented) Show each rule as one plain sentence with its citations, each safety rule paired with a goal rule, and the parts left out with their reason class. The person confirms, corrects, or drops each; a dropped rule becomes a reason record quoting them. Nothing is modelled before this.

## 3. Choose the tool, or record why none fits

(unimplemented) Match the claim sheet's shape (transition system or every-input code property), the trigger row's default (`references/formal.md` § Triggers), the source language and `--unbounded` against each tool adapter's § Capability and its installed check. No admitted adapter fits → status `unformalizable` with a reason record of class 沒有工具 naming the missing tool; stop after step 8.

## 4. Write the model and its coverage map

(unimplemented) The tool adapter's § Encode turns the confirmed claim sheet into model files under `model/`; every model element gets one coverage-map row pointing at a claim-sheet citation. Names are the source's own words.

## 5. Run the strictness gates

(unimplemented) In this order, each realized by the bound adapters, each logged: true to source (coverage map complete, every citation resolves via the source adapter § Cite) → seen failing (one mutation per safety rule, from the source adapter § Mutate, realized by the tool adapter § Realize a mutation) → seen succeeding (each goal reachable; reachable no longer once one transition is removed — tool adapter § Reachability) → scope stated → the real check. A gate that does not pass leaves status `draft`; never weaken a rule or the model to pass.

## 6. Sort what the check found

(unimplemented) Each violation arrives as a normalized trace (`references/ports.md` § Trace). The source adapter's § Replay decides it: every step takeable in the source → a finding in the source adapter's vocabulary (bug; contradiction, gap, ambiguity; refinement failure); a step the source cannot take → the model was wrong: fix it, say what was wrong, rerun from gate 1.

## 7. Draw the page

(unimplemented) Build `page.html` from the claim sheet and the traces per `references/diagrams.md`; open it in the person's browser with what the environment provides.

## 8. Record and report

(unimplemented) All writes happened in a staging directory; write the README from `templates/README.md`, set the sync point from each source adapter's § Sync point, then swap staging into `.claude/hypothesis/<area>/` per `references/ports.md` § Writing the artifact. Close with one line:
「hypothesis 完成：{area}；{N} 條規則，{H} 條成立、{V} 條被推翻；工具 {tool} {version}，範圍：{bounds}；同步點 {sync}；圖：{page path}」

## 9. Keep it in step (`--maintain`)

(unimplemented) Per `references/maintain.md`: for each hypothesis (or the named one), each source adapter's § Diff since sync lists the changes; sort into the four kinds; rerun before and after; move the sync point only after gate 2 passes again on the new source. First run also offers the move from `.claude/prove-it/formal/`.

## Reader contract

(unimplemented) Readers — `/prove-it`, `/hunt`, `/review`, the red/green green step, `/draft`, `/health` — call `scripts/hypothesis-status.py` and run `tool.command` with `$HYP_TMP` set to their own scratch; they never write under `.claude/hypothesis/`. `stale` is computed by the script, never stored.

## Not-for boundaries

- Running the real app to show a claim holds or a counterexample happens → `/prove-it`; it reads this skill's artifact.
- A symptom whose cause is unknown → `/hunt`; it calls this skill for H1–H3 symptoms.
- A claim a single run settles, or anything on the non-trigger list → TDD red/green under `../_shared/tdd.md`.
- A presentation-grade figure → `/draw`, called by the person.
