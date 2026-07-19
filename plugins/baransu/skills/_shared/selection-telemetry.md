# Selection telemetry — decision-log convention

Phase 1 of the harness reform (2026-07-19) made "trigger accuracy is observable" the
success criterion for the three-band routing. This file is the shared convention every
routing-relevant skill points at. It is a *convention plus one mechanical anchor*
(the seal-guard hook), not an automated analytics pipeline — analysis is a human
monthly review.

## When to write a record

1. **On every baransu skill invocation** that begins real work (not an immediate
   off-ramp): one line at start.
2. **On a detected miss**: the model realizes mid-task (or a reviewer/hook surfaces)
   that a skill *should* have been used and was not — one line with `"miss": true`.
   The no-skill-was-running blind spot is covered mechanically by the shipped seal-guard
   Stop hook (`../seal/references/seal-guard-hook.md` — blocking by default,
   `SEAL_GUARD=log|off` degrades), which records seal misses on its own channel in every mode.

## What to write

Append one JSON line to `.claude/harness/selection-log.jsonl` in the user project:

```json
{"ts":"2026-07-19T21:40:00+08:00","skill":"contract","task":"換源進度遷移 CLI 訊息","band":"medium","why":"one feature, few files, user-facing surfaces","miss":false}
```

Fields: `ts` (ISO 8601), `skill` (or `"none"` for a deliberate bare run), `task`
(one phrase), `band` (`small|medium|large`), `why` (one clause), `miss` (bool).
Keep it to one line; this is telemetry, not a journal.

## Monthly review arithmetic

- **False-trigger rate** = records where the band/skill chosen was wrong for the task
  (judged in hindsight) ÷ total records.
- **Miss rate** = (`"miss": true` records + seal-guard.jsonl confirmed lines) ÷
  (those + total records).
- Review outcomes feed three standing decisions: seal-guard default de-escalation
  (blocking → log, if the false-block rate is material), the `/codex-skill-transfer` retirement clause
  (three consecutive zero-use months → retire, ceiling back to 14), and routing-table
  wording fixes for whichever confusion pair actually fired.
