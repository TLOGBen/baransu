# Judge: which method can catch a defect

Written 2026-11-04 before any defect was classified. `check.py` reads `corpus.csv` (one row per defect) and computes
every verdict from these columns alone; nothing here is decided per row by taste.

## Readings (confirmed by the user, 2026-11-04)

- W1 = b: a "unit test" is any automated test that does not run the real app — the plugin test kit
  (`claude plugin test`, `claude-code/testing`) included, and the hypothesis judges that run in it.
- W2 = a, plus the user when needed: an end-to-end run is driven by the model through its tools (Bash, Skill,
  Edit, a subagent, computer-use or a screenshot program to see the screen), or by the user doing ordinary
  things in the app.
- W3: "often" means more than half.
- W4: cost is not part of the claim (noted separately).

## A defect

A behaviour of a shipped or about-to-ship version that its owner then fixed: one row per distinct wrong
behaviour, even when one commit fixed several. Code only for claim A (TypeScript mod, scripts); skill text is
counted for claim B where it bears on tests.

## Columns

- `found_by`: what actually surfaced it — `user-real` (the user on the real app), `e2e-model` (the model running
  the real app), `tla` (TLC trace), `kit` (a test-kit test or kit-run judge), `reading` (review, second
  derivation, reading the code), `exam` (a skill exam taker), `unknown`.
- `e2e`: can an end-to-end run catch it?
  - `yes` — the wrong behaviour shows as an observable difference (the screen, a file, the text the model is
    given, an exit status) in a situation the real app can be put into on purpose by W2's means, without
    changing the app.
  - `rare` — only in an order or timing the real app does not let anyone force (two events racing, a mod reload
    inside a turn, a platform event's timing).
  - `no` — never observable from outside, or the situation cannot be produced at all.
- `tla`: can a TLA+ model with TLC catch it, at any modelling effort?
  - `yes` — the fault is in which steps happen, in which order, or which state is kept, so a model at the code's
    step granularity contains the faulty step.
  - `transcribe` — the fault is in a data transformation (a regex, a path join, a string, a label, a number): a
    model only holds it by transcribing that function from the code, and then TLC checks the transcription.
  - `no` — the fault is a premise about the platform (what a surface draws, what an API does) or in text read by
    a model, outside any state machine.
- `kit`: can a test-kit test catch it? `yes` / `no` (the kit emulates the host, so a wrong premise about the
  host is `no`: the kit agrees with the premise).
- `lint`: can a lint check refuse it when the code is written, without running anything of the app (claim C,
  added by the user 2026-11-04 before any row was classified)?
  - `yes` — the fault has a textual or syntactic signature in the change a `forbid` regex, an ast-grep rule or an
    existing static tool (a type check) catches; a `run` check that runs a unit test does not count (W1).
  - `no` — the fault is only in behaviour: which value, which order, which premise.
- `evidence`: where the row's facts come from (commit, README, transcript).

## Verdicts (computed)

- R1 is broken by a row when `kit = yes` and `e2e = no` and `tla = no`.
- R1 under the strict reading also counts `tla = transcribe` as no and `e2e = rare` as no: the row breaks when
  `kit = yes`, `e2e ∈ {no, rare}` and `tla ∈ {no, transcribe}`.
- A row the kit cannot catch but e2e can (`kit = no`, `e2e = yes`) is a case where unit tests gave false
  assurance or were blind; counted, not a rule.

## Claim C (lint in place of a unit test)

Among rows a kit test can catch (`kit = yes`), the share a lint check could refuse at write time (`lint = yes`);
and the R1-strict rows that `lint = yes` would cover anyway. C holds for a row when `lint = yes`.

## Claim B (red-first tests)

`tests.csv`, one row per test change seen in the record: `turned_red_because` = `regression` (a later code change
broke real behaviour and the test caught it), `intent` (the behaviour was meant to change; the test was edited
or removed), `wrong-test` (the test itself was wrong or too strict and was loosened), `original-bug` (red at
writing time because the bug it was written for existed — red-first by construction, not a later catch).
B holds when `regression` is under half of `regression + intent + wrong-test`.
