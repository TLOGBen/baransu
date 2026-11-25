---
name: verification-methods-formal-verification
description: Reruns and reads this repo's check that, over its recorded defects, TLA+ or a real run catches every one a unit test would. Use when the defect corpus or its criteria change, when lint reports a stale, failing or never-run check, or when asked whether the case against unit tests still holds here.
---

# verification-methods verification

The checks live in `.claude/hypothesis/verification-methods/check.toml`. Each `[[check]]` there names its promise, where the promise comes from and the files it covers, and `record.json` beside it holds when the runner last synced and admitted it; read them there, they are not repeated here.

What these checks do not prove: anything beyond the recorded corpus — a defect class no past commit shows, or a platform input this machine cannot produce, is outside it (the README's best-possible bound says which).

## Run

From the repo root, no AI needed:

- `python .claude/verify/run.py status verification-methods` — seconds; runs nothing.
- `python .claude/verify/run.py quick verification-methods` — under a second.

Needs only Python 3.11 or newer. Each run leaves `.claude/verify/results/hypothesis__verification-methods__verdicts.json` and a `.log` beside it.

## Read

One line per check: `<state> <id> <seconds>s <promise>`. `ok` passed; `failing` means a rule broke and the log tail names the defect; `stale` lists each corpus file changed since the last run. Exit 0 all ok, 1 a check failed, 2 something is stale, never run or broken.

## When it is not 0

- Exit 1: a recorded defect is now caught only by a unit test (R1), or the red-green tally crossed half (B). Read the defect in `model/corpus.csv`; correct the data only from its commit, never to make the check pass.
- `stale` or `never-run`: run `quick` and read again.

The contract behind these rules is baransu's `plugins/baransu/skills/_shared/regression.md`.
