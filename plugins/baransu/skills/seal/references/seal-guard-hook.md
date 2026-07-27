# seal-guard hook — shipped Stop hook, blocking by default

> Distribution note: both Claude Code and Codex plugin packages ship the Stop hook. Codex users must review and trust the installed definition through `/hooks`; until then Codex skips it.

The plugin ships a real Stop hook (`plugins/baransu/hooks/seal-guard.sh`, registered in
`plugins/baransu/hooks/hooks.json`) — installation loads the definition; Claude activates
it directly, while Codex waits for `/hooks` trust. It is the
mechanism anchor for the selection-telemetry blind spot: when `/seal` *should* have fired
but nothing invoked it, no skill is running to log the miss. The hook detects that state
mechanically at session stop.

**Default mode is BLOCKING** (user decision 2026-07-19 — the bold variant of the KD5
anchor). Falsifiable clause: if the monthly telemetry review shows a material
false-block rate, the shipped default degrades to `log`.

## Behavior

At `Stop`, the hook:

1. **Loop protection first**: reads stdin JSON; if `stop_hook_active` is `true`
   (official semantics: Claude Code is already continuing as a result of a stop hook),
   exits 0 immediately. Claude Code additionally force-releases after 8 consecutive
   blocks — the hook never needs its own counter.
2. **Early exits** (all exit 0): not a git repo; no uncommitted diff; no added line in
   the source-dir prefixes (`src|app|lib|bin|cli|ui` by default, tunable via
   `SEAL_GUARD_PATHS`; test paths excluded) matching the user-facing surface
   patterns (`println!` / `console.log` / `printf(` / `print(` …, tunable via
   `SEAL_GUARD_PATTERNS`). The heuristic is deliberately conservative: misses are
   acceptable, false blocks are the expensive failure mode. The default path set
   assumes an application-code layout — a repo without those top-level dirs
   (plugin trees, monorepos) MUST set `SEAL_GUARD_PATHS`, or the filter never
   matches and the hook silently never fires; a zero-event telemetry month is
   therefore ambiguous (no misses vs. filter never matched) until PATHS is
   confirmed to fit the repo layout.
3. **Seal evidence** (exit 0): a same-day line in `~/.claude/baransu/telemetry/{project}/seal-log-{YYYY-MM}.jsonl`
   (written by `/seal` on completion), or a `SEAL:` trailer in the latest commit.
4. **On miss — telemetry in every mode**: appends one JSON line to
   `~/.claude/baransu/telemetry/{project}/seal-guard-{YYYY-MM}.jsonl`（central user scope, split by project and month; `BARANSU_TELEMETRY_DIR` overrides the root）
   (`{"ts":…,"event":"seal-miss","mode":…,"repo":…,"surfaces":N}`), so the monthly
   review keeps its data even when blocking is degraded.
5. **Verdict**: default → the same Traditional Chinese instruction on both runtimes
   (「偵測到 user-facing 變更尚未 /baransu:seal——請執行 seal 收尾，或設 SEAL_GUARD=log
   降級」). Claude receives exit 2 + stderr; Codex receives exit 0 + structured
   `{"decision":"block","reason":"...","systemMessage":"..."}` so Stop creates a
   continuation prompt from `reason`. `SEAL_GUARD=log`
   or `off` → exit 0 with no block.

## Degrade / disable

Set in the environment Claude Code runs under (e.g. shell profile or project `.env`
loading mechanism):

- `SEAL_GUARD=log` — detect + record, never block.
- `SEAL_GUARD=off` — same as `log` but reserved for "I have read the miss data and
  opted out"; telemetry still appends so the review stays honest.
- Claude per-user hard disable: override the `Stop` hook in `settings.json`.
- Codex per-user hard disable: disable the installed hook in `/hooks`, or set
  `[features] hooks = false` to disable all non-managed hooks.

## Monthly review

- **Miss rate input**: lines in `seal-guard.jsonl` a human confirms were genuine
  misses, per `../../_shared/selection-telemetry.md` arithmetic.
- **False-block check**: lines where the session was blocked but no seal was actually
  warranted (surface heuristic false positive). Material false-block rate → flip the
  shipped default to `log` (edit the `case` fallthrough in `seal-guard.sh`), and note
  the flip in CHANGELOG.
- Escalation beyond blocking (e.g. PreToolUse gating) is out of scope — one Stop-time
  gate is the ceiling this line accepts.
