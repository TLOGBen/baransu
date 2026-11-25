---
name: git-account-formal-verification
description: Reruns and reads this repo's verification that lint's git-facts check reminds a commit under the wrong account and never blocks one. Use before closing work that touches plugins/baransu/hooks/engine/moments.ts, when lint reports a stale, failing or never-run check, or when asked whether the git-account rules still hold.
---

# git-account verification

The checks live in `.claude/hypothesis/git-account/check.toml`. Each `[[check]]` there names its promise, where the promise comes from and the files it covers, and `record.json` beside it holds when the runner last synced and admitted it; read them there, they are not repeated here.

What these checks do not prove: the code itself — the TLA+ model and the Lean proof describe the rule, and their only link to `moments.ts` is the fingerprint over it, so a change there shows as `stale`.

## Run

From the repo root, no AI needed:

- `python .claude/verify/run.py status git-account` — seconds; runs nothing.
- `python .claude/verify/run.py quick git-account` — Lean, then TLC; a few seconds warm, about 30 s cold.

Needs `lean` and `tlc` on PATH (`%USERPROFILE%\.local\bin` shims on this machine). Each run leaves `.claude/verify/results/hypothesis__git-account__account.json` and a `.log` beside it.

## Read

One line per check: `<state> <id> <seconds>s <promise>`. `ok` passed on the files as they are now; `failing` means a rule broke and the log tail follows; `broken-judge` means a tool is missing or timed out; `stale` lists each covered file changed since `synced` or since the last run. Exit 0 all ok, 1 a check failed, 2 something is stale, never run or broken.

## When it is not 0

- Exit 1: `moments.ts` breaks R1, R2 or R4. Fix the code, or show from the README's rules that the promise changed and bring the model in step. Never edit the judge to make it pass.
- `stale` since the last run, or `never-run`: run `quick` and read again.
- `stale` since `synced`: the model describes older code. Bring it in step with `/baransu:hypothesis --maintain git-account`, then `python .claude/verify/run.py sync git-account/account`.
- A missing tool: install it; the runner never does.

The contract behind these rules is baransu's `plugins/baransu/skills/_shared/regression.md`.
