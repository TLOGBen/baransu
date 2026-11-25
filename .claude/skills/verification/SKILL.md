---
name: verification
description: Reruns and reads this repo's end-to-end replays, today the Codex lint hook journeys, with no AI. Use before closing work that touches plugins/baransu/hooks/ (engine, util, the Codex adapter or its bundle), when lint reports a stale, failing or never-run replay, or when asked whether lint on Codex still decides the same way.
---

# Replays

The checks live in `.claude/prove-it/replays/*/check.toml`. Each `[[check]]` there names its promise, where the promise comes from and the files it covers, and `record.json` beside it holds when the runner last synced and admitted it; read them there, they are not repeated here.

| Replay | Folder | What it drives |
|---|---|---|
| `codex-lint/journeys` | `.claude/prove-it/replays/codex-lint/` | eight Codex lint journeys, fed as the hook JSON Codex sends, to the bundled hook Codex would start |

What these checks do not prove: whatever a model or a person decides on the path — whether the model rewrites the refused edit, what it says after a held turn — which stays a live `/baransu:prove-it` run.

## Run

From the repo root, no AI needed:

- `python .claude/verify/run.py status codex-lint` — seconds; runs nothing.
- `python .claude/verify/run.py quick codex-lint` — about 15 s warm, 25 s cold.

Needs `node` and `git` on PATH, and the Codex bundle built (`make codex-lint`). Each run leaves `.claude/verify/results/replays__codex-lint__journeys.json` and a `.log` beside it.

## Read

One line per check: `<state> <id> <seconds>s <promise>`; a failing line lists `red <journey> step <n> <event>: expected …, got …`. Exit 0 all ok, 1 a journey decided differently, 2 something is stale, never run or broken (node or the bundle missing, a payload the hook no longer accepts).

## When it is not 0

- Exit 1: the hook decides a journey differently. Fix the code, or drive the journey live with `/baransu:prove-it` and show the new decision is the intended one; never edit the expected values to pass.
- `stale` since the last run, or `never-run`: run `quick` and read again.
- `stale` since `synced`: the hook code changed. Drive the journeys live (`/baransu:prove-it --maintain`), refresh expected values only from a live run that passed, then `python .claude/verify/run.py sync codex-lint/journeys`.
- A missing tool: install it; the runner never does.

The contract behind these rules is baransu's `plugins/baransu/skills/_shared/regression.md`.
