---
name: <area>-formal-verification
description: Reruns and reads this project's verifications of <what the checks guard>. Use before closing work that touches <covered paths>, when lint reports a stale, failing or never-run check, or when asked whether <area> still holds.
---

# <area> verification

The checks live in `<.codex/hypothesis/<area>/check.toml | .codex/prove-it/replays/*/check.toml>`. Each `[[check]]` there names its promise, where the promise comes from and the files it covers, and `record.json` beside it holds when the runner last synced and admitted it; read them there, they are not repeated here.

What these checks do not prove: <for a model, the code itself — its only link to the code is the fingerprint over the covered files, so a change shows as `stale` | for a replay, whatever a model or a person decides on the path — what an agent chooses next, whether a screen reads right — which stays a live prove-it run>.

## Run

From the project root, no AI needed:

- `python .claude/verify/run.py status <ids>` — seconds; runs nothing, compares each check with what was synced and with its last stamp.
- `python .claude/verify/run.py quick <ids>` — runs the quick tier; at most 10 minutes.
- `python .claude/verify/run.py full <ids>` — runs every tier.

An id is `<folder>/<id>` (`<kind>:` in front — `hypothesis`, `codex-hypothesis`, `replays`, `codex-replays` — when two kinds have that folder) or a folder name; none means every check. Each run leaves `.claude/verify/results/<kind>__<folder>__<id>.json` and a `.log` beside it. The runner needs Python 3.11 or newer and runs a `python` judge with its own interpreter. <Tools that must be on PATH, and how to install them.>

## Read

One line per check: `<state> <id> <seconds>s <promise>`.

- `ok` — passed on the files as they are now.
- `failing` — the judge said no; the log path and its tail follow.
- `broken-judge` — the check could not run: a missing tool, a timeout, covers that match no file.
- `never-run` — no stamp yet.
- `draft` — not admitted yet; listed, never counted.
- `stale` — covered files changed since `synced`, the code the judge was last brought in step with, or since the last run; each is listed with which, and `judge` marks a file of the check itself.

Exit 0: all ok. Exit 1: some check is failing. Exit 2: something is stale, never run or broken, and nothing is failing. `status` counts admitted quick checks, and a full check only when it failed.

A judge exits 1 only when the promise is broken, and catches its own crashes and exits 2: an uncaught Python exception also exits 1, and the runner would report it as broken code.

## When it is not 0

- Exit 1: the code breaks the promise. Fix the code, or show from its source that the promise changed and bring the check in step. Never edit the judge to make it pass.
- `stale` since the last run, or `never-run`: run `quick` (or `full` for that check) and read again.
- `stale` since `synced`: the judge describes older code, and no run clears it. Bring it in step with <`$baransu:hypothesis --maintain <area>` | prove-it `--maintain`>, then `python .claude/verify/run.py sync <id>` records that it now describes these files.
- A missing tool: install it; the runner never does.

The contract behind these rules is baransu's `_shared/regression.md`.
