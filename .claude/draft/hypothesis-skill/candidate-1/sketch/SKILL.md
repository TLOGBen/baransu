---
name: hypothesis
description: "Writes down how part of a system must behave as a machine-checked formal model a person can read — plain rules, a model citing its sources, the checker's verdict with its scope, and a page of state diagrams built up one part at a time — from code, a symptom, a document, or two documents compared, and keeps it in step when the source changes. Trigger On '/hypothesis', '假說', '寫成假說', '這個模組不能出錯', '畫狀態圖給我看', '文件有沒有矛盾', 'SD 有沒有滿足 SA', 'model-check this'. Not for running the app to prove a claim (/prove-it) or a guess about a cause (/hunt 推測)."
argument-hint: "[code path | symptom | HUNT-id | document [document]] [--maintain]"
---

# hypothesis — write it down so a machine can check it and a person can read it

(unimplemented) One paragraph: a hypothesis is a claim about how part of a system behaves, always a formal model, owned here and only here; every other skill reads it through `scripts/hypothesis.py` and never writes `.claude/hypothesis/`.

(unimplemented) User-facing language line: Traditional Chinese; commands, paths, identifiers and quoted source text stay as they are.

## Outcome Contract

- **Outcome**: (unimplemented) one area under `.claude/hypothesis/<area>/` whose verdict a reader can trust: holds, open, broken, or cannot — never a pass on a stale source.
- **Done when**: (unimplemented) rules agreed; every model part cites its source; seen failing; seen succeeding; scope stated; every unformalized part has a reason record; page opened; area swapped in whole.
- **Evidence**: (unimplemented) `evidence/` beside the model, named in README §Proof.
- **Output**: (unimplemented) the area directory (README.md, model files, page.html, evidence/); one closing line.
- **Automation**: ultracode=neutral, loop=not-drivable（the rules are agreed with the person and the page is read by them）

## 1. Read what you were given

(unimplemented) Decide the input once, from the arguments alone, before anything else is read; say the decision in the first status line so the user can correct it. Order:

| Given | Input | Adapter in `references/sources.md` |
|---|---|---|
| nothing | the conversation's current subject; if none, every area `status` lists as 過期 or 舊位置 | — |
| `HUNT-YYYY-NNN`, or a sentence describing a failure | symptom | §Symptom |
| one path or symbol in code | code | §Code |
| one document (path or URL to .md .pdf .docx .pptx .xlsx .html, or prose under a docs dir) | document | §Document |
| two documents | comparison; upstream is rules, downstream is behaviour | §Comparison |

(unimplemented) Then run `scripts/hypothesis.py status <the files the input resolves to>`: an area that covers them and is in sync → rerun it with `check` and stop (not-trigger row "already in sync"); an area that is 過期 → `--maintain` turns on by itself per `../_shared/auto-flags.md` and §7 runs instead of §2–§6; any 舊位置 area → offer the move first (§7 Migration).

(unimplemented) Gate against `references/formal.md` §Triggers and §Not triggers. No row matches → no area; say which not-trigger row held, one line, in the reason-record form.

## 2. Agree the rules

(unimplemented) One plain sentence per rule, in the source's own words, no variable or action names. Every safety rule is paired with a goal rule. For a document, each rule quotes its passage and location. Ambiguities become questions with who to ask, never filled in. Parts that will not be formalized are listed now with their reason class. Ask once; this is the one Input PAUSE before the end.

## 3. Write the model true to its source

(unimplemented) Tool chosen by the question (`references/formal.md` §Tool). Every action, variable and constant cites its source; one indivisible step in the source is one step in the model; names are the source's. The coverage map in the README is written as the model is, not after.

## 4. See it fail, see it succeed

(unimplemented) Per safety rule: a broken variant in a throwaway copy, caught, dropped. Per goal rule: reachable, and unreachable once one named transition is removed. A rule that passes both gates only vacuously is rejected, not weakened. Outputs go to `evidence/`.

## 5. Check and sort what it found

(unimplemented) Run every check in README `checks`. A counterexample is replayed against the source step by step: a step the source cannot take → the model is wrong, fix it and say what was wrong; every step possible → a finding. Finding kinds come from the input's adapter (code: bug path; document: contradiction, gap, ambiguity; comparison: refinement counterexample). Never weaken a rule or the model to pass.

## 6. Draw the page and write the area

(unimplemented) Build `page.html` per `references/page.md` and open it the way the environment allows. Write the whole area in a draft directory and swap it in only when §2–§5 are complete (`references/area.md` §Writing). Close with:
「hypothesis 完成：{area} {狀態}（{N} 條路徑／{Q} 個待釐清）；範圍：{bounds}；{tool} {version}；圖：{page path}；同步於 {sync}；{U} 筆未形式化。」

## 7. Keep it in step (`--maintain`)

(unimplemented) Trigger written beside the flag: an area covering the input is 過期. Per area: read every change to its covers since the sync point, sort each into the four outcomes (`references/formal.md` §Drift), rerun before and after, see it fail again on the new source, then swap in with the new sync point; a blocked area keeps its old sync point. Edits only the area; product code is the user's.

### Migration from `.claude/prove-it/formal/`

(unimplemented) Move one legacy area at a time on the user's yes: copy into a draft, fill the README contract, run §4 on the current source, swap in, then remove the legacy directory. Until then `status` lists it as 舊位置 and `/prove-it` keeps reading it as it does today.

## Not-for boundaries

(unimplemented) Running the real app to settle a claim → `/prove-it` (it reads this skill's areas through `check`). An informal causal guess → `/hunt`'s 推測. A presentation-grade figure → `/draw`, by hand. Deciding whether to build → `/think`. Reviewing a change → `/review` (reads through `status`).
