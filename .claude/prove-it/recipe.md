# Run recipe — baransu

baransu is a Claude Code / Codex plugin of skills plus one runtime piece: the lint mod. The surface a proof drives
is the **lint hook on Codex** (CLI, Windows): `codex/plugins/baransu/hooks/{hooks.json,lint.mjs}`, run by Codex at
each hook event. Other surfaces, not driven by this recipe: the lint mod inside Claude Code (needs the working
tree installed as the Claude Code plugin and a new session), Codex desktop (GUI; the person drives it), the skills
themselves (prose; `/review` and `claude plugin eval`).

Paths below: `R` = repo root, `S` = this session's scratchpad, `P` = `$S/prove-codex` (made per run).

## Launch

The hook is a short-lived program; launch = install it once into the real Codex as a throwaway plugin, then run each
drive as its own `codex exec` session. Never copy `auth.json` or make a `CODEX_HOME` with login data: the real
`~/.codex` is used, its `config.toml` backed up first and compared byte for byte at cleanup.

1. `make codex-lint` (the bundle must match the sources: `make parity-check` passes).
2. Back up: `cp ~/.codex/config.toml $P/config.toml.bak`.
3. Marketplace with one plugin holding only the hook:
   - `$P/mkt/.agents/plugins/marketplace.json`:
     `{"name":"lintpilotmkt","interface":{"displayName":"lint pilot"},"plugins":[{"name":"lintpilot","source":{"source":"local","path":"./plugins/lintpilot"},"policy":{"installation":"AVAILABLE","authentication":"ON_INSTALL"},"category":"Productivity"}]}`
   - `$P/mkt/plugins/lintpilot/plugin.json`: `{"name":"lintpilot","version":"0.0.1","description":"baransu lint proof"}`
   - copy `R/codex/plugins/baransu/hooks/hooks.json` and `lint.mjs` to `$P/mkt/plugins/lintpilot/hooks/`.
4. `codex plugin marketplace add "$(cygpath -w $P/mkt)"` then `codex plugin add lintpilot@lintpilotmkt`.
5. Scratch project `$P/proj`: `.claude/lint/config.toml` = `[[extends]]` / `set = "sets/local/checks.toml"`,
   `.claude/lint/sets/local/checks.toml` = `R/.claude/prove-it/fixtures/codex-lint/checks.toml`, files `A.java`
   (`class A {}`), `notes.txt`, `PLAN.md`, `keep/x.txt`, `tmp.txt`; `git init -q` (no commit: lint's git-facts check
   refuses a scratch identity, and nothing needs one). The scratchpad is under a trusted folder
   (`[projects.'<home folder>']` in `~/.codex/config.toml`), so `run` checks run there.

Ready: `codex exec … 'ok'` prints `hook: SessionStart Completed`.

## Doctor

- `node --version` ≥ 18 and `codex --version` (0.169.1 when this was written).
- `make parity-check` passes (the installed `lint.mjs` is this version's).
- `cmp $P/mkt/plugins/lintpilot/hooks/lint.mjs ~/.codex/plugins/cache/lintpilotmkt/lintpilot/local/hooks/lint.mjs`.
- No other test plugin installed: `ls ~/.codex/plugins/cache | grep -i lint` shows only `lintpilotmkt`.

## Drive

One session per scenario, in the scratch project:

`codex exec --dangerously-bypass-hook-trust -s workspace-write -C "$(cygpath -w $P/proj)" '<prompt>'`

- `--dangerously-bypass-hook-trust` skips Codex's hook review for this run only (it writes nothing to config).
- Resume a session: `codex exec … resume <session-id> '<prompt>'`; the id is in the first lines of the output and in
  the newest `~/.codex/sessions/YYYY/MM/DD/*.jsonl`.
- Force a compaction: add `-c model_auto_compact_token_limit=12000` to a resumed session.
- Ask the model to repeat the rule codes it received (`規則代號`): the codes in the fixture checks tell which line
  reached it. The machine's own Codex settings make the model answer in Chinese.
- Without Node: run `codex.exe` with a PATH that has no node (`env PATH=/c/Windows/System32:/c/Windows/System32/WindowsPowerShell/v1.0 "$(which codex)" exec …`); Codex itself is a native program.

## Evidence

- The exec output (hook lines `hook: <Event> Completed|Blocked|Failed`, the model's answer) → `$P/out/<scenario>.txt`.
- The file state afterwards (`cat`, `grep -c`) and `git status` of the scratch project.
- The hook's state: `~/.codex/plugins/data/lintpilot-lintpilotmkt/lint/<session-id>.json` (`jq` it; copy into `$P/out/` before cleanup — cleanup deletes the data folder).
- The session's rollout (`~/.codex/sessions/…/<id>.jsonl`): what reached the model, in order.
- The record quotes what it relies on; the scratch folder is the scratchpad's and goes when it is cleared.

## Cleanup

1. `codex plugin remove lintpilot@lintpilotmkt` and `codex plugin marketplace remove lintpilotmkt`.
2. `cmp ~/.codex/config.toml $P/config.toml.bak` must print nothing.
3. Remove `~/.codex/plugins/cache/lintpilotmkt` and `~/.codex/plugins/data/lintpilot-lintpilotmkt` (full paths, one call of its own).
4. Leave `$P/out/` (evidence).

## Hypotheses

- `.claude/hypothesis/codex-lint-state/` covers `adapters/codex/{main,store}.ts` and the engine's halves: rerun `cd model && python check.py` (TLC; `tlc` on PATH, Java).
- `.claude/hypothesis/lint-mod-state/` covers `engine/engine.ts`: its README names the rerun command.
