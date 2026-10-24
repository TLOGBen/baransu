---
name: hypothesis
description: "Writes down how part of a system must behave as a machine-checked formal model — TLA+ by default — with plain rules and step-by-step state diagrams, from code, a symptom, or documents; owns and maintains it so other skills can read one status line. Trigger On '/hypothesis', '假說', '這個模組不能出錯', '畫狀態圖給我看', '文件有沒有矛盾', 'SD 有沒有滿足 SA', 'model-check this'. Not for proving it on the running app (/prove-it) or tracing a root cause (/hunt)."
argument-hint: "<path|module|question|doc> [--symptom \"…\"] [--satisfies <rules-doc>] [--maintain [area]] [--status …]"
---

# hypothesis — write it down so a machine can check it and a person can read it

(unimplemented) — One paragraph: a hypothesis is a claim about how part of a system behaves, always a formal model, citing its source, checked by a tool within a stated scope, explained in plain rules and a progressive diagram set. This skill is its only writer; every other skill reads it through one script and acts on one computed state.

(unimplemented) — Output language line: user-facing output in Traditional Chinese; identifiers, paths, model code and quoted source stay as they are.

## Outcome Contract

- **Outcome**: (unimplemented) — every claim in scope ends as a hypothesis whose computed state is `proved`, `disproved`, or `unformalized`, with nothing unexplained.
- **Done when**: (unimplemented) — rules confirmed by the user; every model part cites its source; each safety rule seen failing on a broken variant; each goal seen reachable and seen unreachable with one transition removed; scope stated; every unformalized part has a reason record; `hypothesis-status.py --area <area>` prints the intended state; the diagram page is open.
- **Evidence**: (unimplemented) — the `check` block of `hypothesis.json` (tool, version, command, bounds, states, seen_failing, seen_succeeding) and the check log.
- **Output**: (unimplemented) — `.claude/hypothesis/<area>/` per `references/artifact.md`; never archived by `/ship`; no product code edited.
- **Automation**: ultracode=neutral, loop=assisted（`--maintain` is called by readers without a person; it pauses only when a change looks like a promise changed on purpose and needs the person's evidence — read `../_shared/loop-contract.md` first and apply its PAUSE semantics; a first write needs the person to confirm rules and is reported as such, never defaulted）

PAUSE classification for non-interactive drivers: `references/loop-pauses.md`.

## 1. Decide whether this is a hypothesis

(unimplemented) — Run `scripts/hypothesis-status.py --files <target>` first: an existing `proved` or `disproved` area covering the target is the 「已經有一份同步中的假說」 non-trigger — rerun it via `--check`, write nothing new; a `stale` one routes to §6; a `legacy` one of the same area must be moved first (§6 Migration) — one area never lives in two places. Otherwise match the target against H1–H8 and the non-trigger list in `references/formal.md`, and confirm the default tool for the matched row is installed before creating the area dir (a missing tool is `no-tool`, not a half-built area); a miss ends with one reason record (`references/artifact.md` § Reason record), written into the caller's output, not into `.claude/hypothesis/`.

## 2. Read the source and name the area

(unimplemented) — Pick the source adapter (`references/sources.md`): code, symptom, one document, or two documents with roles from `--satisfies`. Choose the area slug (stable, the source's own word for the part). Record the coverage set and the watch patterns (the writes to the guarded state) as you read, not after.

## 3. Confirm the rules in plain words

(unimplemented) — One sentence per rule, kinds `safety` / `goal`, no variable or action names; each with its citation. For documents, every extracted rule carries its quote and location and the user ticks each. Ambiguities become questions with whom to ask, never filled in. Parts not to be formalized are listed with their reason class before modelling starts.

## 4. Model and check

(unimplemented) — Tool choice and the strictness rules from `references/formal.md`: true to source, one indivisible source step = one model step, the source's names. Run the check with one pinned command. Then the two evidence gates, both mandatory: seen failing (a broken variant per safety rule, kept as a patch under `variants/`, the throwaway copy dropped) and seen succeeding (each goal reached; unreachable after removing one named transition). A counterexample every step of which the source can take is a finding, written as a script in the source's words under `paths/`; never weaken a rule or the model to pass.

## 5. Draw and publish

(unimplemented) — Build `diagrams.html` per `references/diagrams.md` (diagram 1 happy path ≤ 7 states; each next adds one part; the last numbers every bug path with the same `P<n>` ids as `paths/`). Write `README.md` from `templates/README.md`. Write `hypothesis.json` LAST, by compare-and-swap on `generation` (`references/artifact.md` § Writing). Run `hypothesis-status.py --area <area>` and quote its line; open the page.

## 6. Keep it in step (`--maintain`)

(unimplemented) — `references/maintain.md`: start from `hypothesis-status.py --all`; for each non-`proved`/`disproved` area, read every change to its coverage since `sync.commit` plus every `new-writer` the script names, sort into the four outcomes, rerun before and after, re-derive variants when the model changed, then publish as §5. First run offers to migrate `.claude/prove-it/formal/<area>/` (legacy) per `references/maintain.md` § Migration.

## 7. Report

(unimplemented) — Plain first, then detail: each finding, path and question opens with one sentence in everyday words (none of 活性、安全性、精化、不變式、同步點、TLC、模型、狀態空間), then its technical layer (`file:line`, tool, states, rule name). This rule is this skill's own; it does not call `/huh`. Then the one closing line, fixed:
「hypothesis 完成：{area}｜{N} 條規則，{D} 條被推翻（{path ids}）、{H} 條成立｜{tool} {version}，{states} 個狀態｜範圍：{bounds}｜同步：{sync}｜圖：{page path}」
plus, for documents, 「矛盾 {c}｜缺漏 {g}｜模糊 {a}」, and the unformalized count with the README section it lives in.

## For readers

(unimplemented) — Three lines pointing at `references/reading.md`: readers run the script, read `state`, and act per the state × reader table; they never open `hypothesis.json`, compare commits, or write under `.claude/hypothesis/`.

## Not-for boundaries

- (unimplemented) Proving it on the running app, replaying a counterexample with forced order → `/prove-it`.
- (unimplemented) Finding the cause of a failure → `/hunt` (which may hand an H1–H3 symptom here).
- (unimplemented) A claim one run can settle, a static permission check, look and copy → not a hypothesis; red/green under `../_shared/tdd.md`.
- (unimplemented) A presentation-grade figure → `/draw`, by hand.
