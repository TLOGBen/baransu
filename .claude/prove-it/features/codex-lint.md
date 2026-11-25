# Lint on Codex

## Sub-features

| Journey | Code | Codex event |
|---|---|---|
| An edit writing a forbidden pattern is refused, the model rewrites | DTO-7 | PreToolUse `apply_patch` |
| An edit that leaves an error is asked to be fixed in the same turn | PE-5 | PostToolUse `apply_patch` |
| A `check` command is held once, sent again in a later response it runs | RM-6 | PreToolUse `Bash` |
| A patch deleting a protected file is refused | KP-8 | PreToolUse `apply_patch` (`*** Delete File`) |
| The turn is held at its end until the answer is fixed | ST-9 | Stop |
| `remind` rules are in the session's context from the start | DTO-7 | SessionStart |
| Typing `$baransu:review` runs the checks before review | RV-3 | UserPromptSubmit |
| The model reading a skill's SKILL.md runs them too | RV-3 | PostToolUse `Bash` |
| A file changed outside Codex is reported at the next event | PF-1 | any hook (resume) |
| After a compaction, post:compact reaches the model | PC-2 | PreCompact / PostCompact / SessionStart(compact) |
| After a subagent ends, post:agent reaches the main model | AG-4 | SubagentStop |
| A `run` check runs in a trusted project | RN-1 | PreToolUse `Bash` (`git commit`) |
| Without Node, the session says so | — | SessionStart (second handler) |

## How to get to it (user POV)

A colleague installs baransu's Codex plugin, trusts its hook when Codex asks, and works in a project holding
`.claude/lint/`. They never call anything: the hook runs at each Codex event.

## Driving it with codex exec

- DTO-7 / PE-5 / KP-8: ask for the edit in plain words (「用 BeanUtils.copyProperties …」「加一行 System.out.println …」「用 apply_patch 刪掉 keep/x.txt」); read the file back afterwards.
- RM-6: 「用 Remove-Item 刪掉 tmp.txt；被擋下就照理由做」; check `tmp.txt` is gone only after a second send.
- ST-9: 「最後一句話照抄：Plan noted. TODO: write tests later.」; the hook line `hook: Stop Blocked`, then the final answer has no TODO.
- RV-3 (typed): put `$baransu:review` in the prompt; ask for the code in the 「Lint 紀錄」.
- RV-3 (read): 「用 Get-Content 讀 <R>/codex/plugins/baransu/skills/review/SKILL.md 的前 3 行」.
- PF-1: write `FIXME` into `notes.txt` between two sessions, then `resume` and run any command.
- PC-2: `resume` with `-c model_auto_compact_token_limit=12000`; the code arrives at the next event after the compaction.
- AG-4: 「我明確要求你用 sub-agent …」 (Codex spawns one only when asked).
- RN-1: 「git add -A 然後 git commit -m test」 in the scratch project; the commit itself may be refused by other built-ins — only the RN-1 line matters.
- No Node: run `codex.exe` with a PATH without node (recipe, Drive).

## Gotchas

- The model answers in Chinese on this machine (the person's Codex settings), so an English slip — the user-language 重新 — cannot be provoked here; it is driven only by feeding the hook JSON.
- A second automatic compaction can wipe the PC-2 line it just delivered; read the rollout for the line, not only the final answer.
- Hooks run in the model's shell (PowerShell on Windows): a hook command must read the same in PowerShell, cmd and sh.
- The hook's state lives under `~/.codex/plugins/data/lintpilot-lintpilotmkt/`; cleanup deletes it, copy it first.

Sources: `plugins/baransu/hooks/adapters/codex/{main,ports,store,patch}.ts`, `plugins/baransu/hooks/engine/`,
`codex/plugins/baransu/hooks/hooks.json`. Last driven live: a741eba5 + working tree (8.49.0), 2026-11-18.
