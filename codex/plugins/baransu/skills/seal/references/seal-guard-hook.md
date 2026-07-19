# seal-guard hook — shipped Stop hook, blocking by default

> Distribution note: the Stop hook ships with the Claude Code plugin only. Distributions without a Stop-hook system (e.g. the Codex mirror) get this document as description, not mechanism — there, run /seal manually before ending a session.

The plugin ships a real Stop hook (`plugins/baransu/hooks/seal-guard.sh`, registered in
`plugins/baransu/hooks/hooks.json`) — installing the plugin activates it. It is the
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
   `src|app|lib|bin|cli|ui` (test paths excluded) matching the user-facing surface
   patterns (`println!` / `console.log` / `printf(` / `print(` …, tunable via
   `SEAL_GUARD_PATTERNS`). The heuristic is deliberately conservative: misses are
   acceptable, false blocks are the expensive failure mode.
3. **Seal evidence** (exit 0): a same-day line in `.codex/harness/seal-log.jsonl`
   (written by `/seal` on completion), or a `SEAL:` trailer in the latest commit.
4. **On miss — telemetry in every mode**: appends one JSON line to
   `.codex/harness/seal-guard.jsonl`
   (`{"ts":…,"event":"seal-miss","mode":…,"repo":…,"surfaces":N}`), so the monthly
   review keeps its data even when blocking is degraded.
5. **Verdict**: default → exit 2 with the Traditional Chinese instruction on stderr
   (「偵測到 user-facing 變更尚未 /baransu:seal——請執行 seal 收尾，或設 SEAL_GUARD=log
   降級」), which per the Stop-hook contract prevents the stop and feeds the instruction
   back to Claude. `SEAL_GUARD=log` or `off` → exit 0 (never block).

## Degrade / disable

Set in the environment Claude Code runs under (e.g. shell profile or project `.env`
loading mechanism):

- `SEAL_GUARD=log` — detect + record, never block.
- `SEAL_GUARD=off` — same as `log` but reserved for "I have read the miss data and
  opted out"; telemetry still appends so the review stays honest.
- Per-user hard disable: override the `Stop` hook in your own `settings.json`
  (user hooks merge with plugin hooks; see Claude Code hooks docs).

## Monthly review

- **Miss rate input**: lines in `seal-guard.jsonl` a human confirms were genuine
  misses, per `../../_shared/selection-telemetry.md` arithmetic.
- **False-block check**: lines where the session was blocked but no seal was actually
  warranted (surface heuristic false positive). Material false-block rate → flip the
  shipped default to `log` (edit the `case` fallthrough in `seal-guard.sh`), and note
  the flip in CHANGELOG.
- Escalation beyond blocking (e.g. PreToolUse gating) is out of scope — one Stop-time
  gate is the ceiling this line accepts.
