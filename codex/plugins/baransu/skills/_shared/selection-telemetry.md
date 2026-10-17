# Selection telemetry — decision-log convention

Phase 1 of the harness reform (2026-07-19) made "trigger accuracy is observable" the
success criterion for the three-band routing. This file is the shared convention every
routing-relevant skill points at. It is a *convention*, not an automated analytics
pipeline — analysis is a human monthly review.

## When to write a record

1. **On every baransu skill invocation** that begins real work (not an immediate
   off-ramp): one line at start.
2. **On a detected miss**: the model realizes mid-task (or a reviewer surfaces)
   that a skill *should* have been used and was not — one line with `"miss": true`.
   No hook covers the no-skill-was-running blind spot; this record is the only channel,
   so write it the moment the miss is noticed rather than at session end.

## What to write

Append one JSON line to the central user-scope ledger — NOT a per-project file:

```
~/.claude/baransu/telemetry/{project}/selection-log-{YYYY-MM}.jsonl
```

`{project}` = the git-root basename; when there is no git repo, simply the cwd
folder name. `{YYYY-MM}` = current month (monthly files are the time rotation —
no other rotation mechanism exists or is needed). Example record:

```json
{"ts":"2026-07-19T21:40:00+08:00","skill":"review","task":"換源進度遷移 CLI 訊息","band":"medium","why":"one feature, few files, user-facing surfaces","miss":false}
```

Fields: `ts` (ISO 8601), `skill` (or `"none"` for a deliberate bare run), `task`
(one phrase), `band` (`small|medium|large`), `why` (one clause), `miss` (bool).
Keep it to one line; this is telemetry, not a journal.

## Monthly review arithmetic

- **False-trigger rate** = records where the band/skill chosen was wrong for the task
  (judged in hindsight) ÷ total records.
- **Miss rate** = `"miss": true` records ÷ (those + total records).
- Review outcomes feed two standing decisions: the `/codex-skill-transfer` retirement
  clause (three consecutive zero-use months → retire), and
  routing-table wording fixes for whichever confusion pair actually fired.
- **Zero-miss caveat**: a month with zero `"miss": true` records is ambiguous — it means
  either "no misses" or "nobody noticed". There is no mechanical cross-check; read it
  as weak evidence, not as success.
