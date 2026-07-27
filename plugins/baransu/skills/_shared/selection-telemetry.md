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

Append one JSON line to the central user-scope ledger — NOT a per-project file:

```
~/.claude/baransu/telemetry/{project}/selection-log-{YYYY-MM}.jsonl
```

`{project}` = the git-root basename; when there is no git repo, simply the cwd
folder name. `{YYYY-MM}` = current month (monthly files are the time rotation —
no other rotation mechanism exists or is needed). The seal-guard hook writes its
`seal-guard-{YYYY-MM}.jsonl` and reads `/seal`'s `seal-log-{YYYY-MM}.jsonl` in the
same directory, so the monthly review is one directory read per project under a
single root. Example record:

```json
{"ts":"2026-07-19T21:40:00+08:00","skill":"contract","task":"換源進度遷移 CLI 訊息","band":"medium","why":"one feature, few files, user-facing surfaces","miss":false}
```

Fields: `ts` (ISO 8601), `skill` (or `"none"` for a deliberate bare run), `task`
(one phrase), `band` (`small|medium|large`), `why` (one clause), `miss` (bool).
Keep it to one line; this is telemetry, not a journal.

## Monthly review arithmetic

- **False-trigger rate** = records where the band/skill chosen was wrong for the task
  (judged in hindsight) ÷ total records.
- **Miss rate** = (`"miss": true` records + seal-guard-\{month\}.jsonl confirmed lines) ÷
  (those + total records).
- Review outcomes feed three standing decisions: seal-guard default de-escalation
  (blocking → log, if the false-block rate is material), the `/codex-skill-transfer` retirement clause
  (three consecutive zero-use months → retire, ceiling back to 14), and routing-table
  wording fixes for whichever confusion pair actually fired.
- **Zero-event caveat (seal-guard)**: a month with zero `seal-guard-{month}.jsonl`
  lines is ambiguous — it means either "no misses" or "the path filter never
  matched" (the hook writes telemetry only after the filter matches). Before
  reading zero as success, confirm `SEAL_GUARD_PATHS` covers the repo's actual
  source layout (default `src|app|lib|bin|cli|ui` assumes application-code
  top-level dirs; plugin trees and monorepos need the override). A de-escalation
  decision driven only by false-block rate cannot see this failure.

## Reform gate signals (Phase 3 — 2026-07)

The Phase 3 gates (現實接觸強制閘 / Critical 硬停 / R10 證據異議) each carry a
falsifiable exit clause; those need firing records to evaluate, so a gate firing
appends one supplementary line with an `event` field (other fields as above,
`miss:false`):

- `"event":"reality_contact_flip"` — the 現實接觸強制閘 flipped a `未驗` premise to
  `已驗`, or escalated it to the user (analyze Stage 1 / contract Ground).
- `"event":"critical_hard_stop"` — final-review's Critical hard-stop blocked a green
  delivery on an open Critical (carrying its 死因四件套).
- `"event":"r10_premise_patch"` — an R10 evidence-backed dissent triggered a
  sanctioned goal.md 前提/C{n} patch.

Three monthly reform signals (reform-proposal §5), from the month's records:
- **錯誤前提穿透率** — tasks whose delivered data source / premise was wrong ÷ tasks
  with a premise-bearing spec.
- **Critical 發現後解決率** — `critical_hard_stop` events resolved before delivery ÷
  total Criticals found.
- **seal 字面誤判率** — evidence-backed correct deviations wrongly rejected on literal
  wording (should trend to 0 as R10 + `r10_premise_patch` land).

Falsifiable-exit evaluation: a Phase 3 gate with zero firing events (or only
overridden false-positive firings) across three months is a retirement candidate —
the same forward-only discipline as the `/codex-skill-transfer` sunset.
