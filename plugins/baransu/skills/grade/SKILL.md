---
name: grade
description: 'Score baransu skill telemetry on a deterministic 5-dim rubric — reads .claude/harness/telemetry.jsonl, writes per-row verdicts to grade.jsonl. Daily cron 00:00 or on demand. Trigger on 「打分」「跑 grade」「評分 skill」, "score skills". 繁體中文輸出。'
---

# grade — score completed telemetry rows on a deterministic rubric

`/grade` is one of three skills (`/grade`, `/triage`, `/bridge`) that close
the self-healing harness loop. It is the **scoring** stage: it never mutates
`telemetry.jsonl` itself (the only allowed adjacent mutation is performed by
the standalone `harness-reaper` script invoked in Stage 0), it does not
cluster (that is `/triage`'s job), and it does not call any LLM judge — the
rubric is fully deterministic and reproducible byte-for-byte.

The body below is English (agent-facing). All user-visible output is in
**Traditional Chinese (繁體中文)** per the baransu plugin convention.

---

## When to trigger

- **Cron** — daily 00:00 (self-healing harness schedule).
- **Manual** — user invokes `/baransu:grade` (e.g. `「幫我跑 grade」`,
  `「對昨天的 skill 打分」`).
- **Tune-acknowledged reset** — `/baransu:grade --tune-acknowledged`
  resets `state.json.tune_review_due_since` to null. **DEFERRED**: not
  yet implemented in `grade-collector.py`; the flag currently returns
  unrecognized-flag. See `## --tune-acknowledged flag (manual reset)` below
  for the spec'd behaviour and current workaround.

---

## Inputs / outputs

| Direction | Path | Note |
|---|---|---|
| Read | `.claude/harness/telemetry.jsonl` | append-only JSONL; only `terminal_state == "completed"` rows are scored |
| Read | `.claude/harness/state.json` | for `cumulative_completed_count`, `tune_review_due_since` |
| Write | `.claude/harness/grade.jsonl` | per-row verdict (5 dim scores + aggregate + quality enum + weights snapshot) |
| Write | `.claude/harness/state.json` | update `last_grade_run_at`, `cumulative_completed_count`, and (when threshold crossed) `tune_review_due_since` |
| Adjacent mutation (via reaper) | `.claude/harness/telemetry.jsonl` | `harness-reaper` flips stale `in_progress` rows to `interrupted`; `/grade` itself never writes telemetry |

Schema for `grade.jsonl` is locked in
`plugins/baransu/skills/_shared/grade-triage-schema.md` §5.

---

## Stage 0 — Pre-flight: health probe + telemetry check + harness-reaper

0. Cron silent-failure health check (inline). **First action of `/grade`.**
   ```sh
   python3 plugins/baransu/scripts/health_check.py \
     --state .claude/harness/state.json \
     --threshold-hours 36
   ```
   - Inspects `last_grade_run_at`; emits a 4–6 line 繁中 warning to stdout
     when missing / null / older than 36h. Healthy state is silent.
   - **Always exits 0** — the warning is observational; it never blocks
     the grading pipeline.
   - The warning points to `plugins/baransu/skills/grade/CRON.md` rather
     than printing CronCreate / crontab literals (CRON.md is the single
     SoT for registration commands).
1. Confirm `.claude/harness/telemetry.jsonl` exists and is non-empty.
   - If missing: print 繁中 `「telemetry.jsonl 不存在或為空，沒有可打分的資料；結束。」` and exit 0 (no error — the harness simply has nothing to grade yet).
2. Invoke the staleness sweep:
   ```sh
   python3 plugins/baransu/scripts/harness-reaper.py \
     --telemetry .claude/harness/telemetry.jsonl
   ```
   - The reaper is the **only** writer permitted to mutate
     `telemetry.jsonl` adjacent to `/grade`. It enforces the single
     allowed terminal-state transition: `in_progress → interrupted`
     when a row's start time is older than 24 hours. No other field
     of any row may be touched.
   - Reaper failures (non-zero exit) are non-fatal — log a 繁中 warning
     and continue. The grading itself does not depend on reaper success.

> Mutation contract: `/grade` is a **read** consumer of telemetry.jsonl.
> The reaper exists precisely so that the staleness sweep is a separate,
> auditable script — `/grade` never writes telemetry itself.

---

## Stage 1 — Read + filter `terminal_state == completed`

1. Stream `telemetry.jsonl` line by line. For each line:
   - Parse JSON; on parse error, skip the row and log a 繁中 warning
     (`「telemetry 第 N 行解析失敗，已跳過」`); do not abort.
   - Keep the row only if `terminal_state == "completed"`.
   - All other states (`aborted`, `interrupted`, `in_progress`) are
     dropped silently — they do **not** contribute a verdict.
2. Pass the filtered rows to Stage 2.

> Hard rule (KD#3, INT-3): `/grade` only scores `terminal_state == "completed"`
> rows. Any other status is excluded from `grade.jsonl` entirely.

---

## Stage 2 — Run grade-collector

Invoke the rubric collector script. It is the single owner of the scoring
math; this SKILL.md describes only the contract.

```sh
python3 plugins/baransu/scripts/grade-collector.py \
  --telemetry .claude/harness/telemetry.jsonl \
  --output    .claude/harness/grade.jsonl \
  --state     .claude/harness/state.json
```

Arguments:

| Flag | Meaning |
|---|---|
| `--telemetry` | input JSONL path (read-only) |
| `--output` | output JSONL path; collector appends one verdict per `terminal_state == "completed"` row |
| `--state` | state.json path; collector updates `last_grade_run_at`, `cumulative_completed_count`, and (when threshold crossed) `tune_review_due_since` |

The collector implements the 5-dimension equal-weight rubric defined
below. Weights are **not** hard-coded inside the script body — they live
in the rubric configuration (currently `1/5` each per Bootstrap), and the
script reads them so they can be tuned without code edits (INV-4
deterministic invariants apply).

Error handling:

| Situation | Behaviour |
|---|---|
| `telemetry.jsonl` line parse error | skip row, log 繁中 warning, continue |
| Per-dim NaN / arithmetic failure | mark that row's verdict as `dims_calc_failed` with `aggregate=null`; do not abort the whole run |

---

## Stage 3 — Tune-trigger evaluation

After the collector finishes:

1. Read updated `cumulative_completed_count` from `state.json`.
2. If `cumulative_completed_count >= 50` AND
   `state.json.tune_review_due_since == null`, then:
   - Set `state.json.tune_review_due_since = <ISO-8601 datetime>`.
   - Print to stdout: `tune_review_due: true` (machine-readable signal,
     in addition to the 繁中 user-facing line in Stage 4).
3. If `cumulative_completed_count < 50`, do nothing — the harness has
   not yet accumulated enough completed rows to warrant a weight review.
4. The `--tune-acknowledged` flag (handled in Stage 0 short-circuit before
   reaching Stage 1, wired by TASK-skills-grade-02) resets
   `tune_review_due_since` to null and prints
   `「tune_review_due 已 acknowledge，等待下次累積跨閾值。」`.

> The `>= 50` threshold is a **quantitative lock** (KD#4): it cannot be
> softened to "feels like enough" or any heuristic. Until the cumulative
> count crosses ≥ 50 completed rows, weights remain at `1/5` each
> (equal_weight bootstrap).

---

## Stage 4 — Completion report (Traditional Chinese)

Print a 繁中 summary block to stdout. The block has two lines:

```
對 N 條 completed row 打分完成；poor M 條；trigger {tune_review_due / not_yet}
目前 completed row 累積：C；tune trigger {due / not yet}
```

Where:
- `N` = number of `terminal_state == "completed"` rows scored this run.
- `M` = number of those rows whose `quality == "poor"` (i.e.
  `aggregate < 0.50`; band edges per `_shared/grade-triage-schema.md` §3).
- `trigger = tune_review_due` on the first line when Stage 3 emitted
  the signal this run; otherwise `not_yet`.
- `C` = `state.json.cumulative_completed_count` after Stage 2 finished
  (i.e. the running total across all `/grade` runs to date, the
  authoritative source for the threshold check in Stage 3).
- `tune trigger` on the second line is `due` whenever
  `state.json.tune_review_due_since != null` at the end of Stage 3
  (regardless of whether this run is the one that crossed the
  threshold), and `not yet` when it is still `null`. This makes the
  line a current-state read, so a user re-running `/grade` after a
  threshold cross still sees `due` until they acknowledge.

Then exit 0. The 繁中 block is the canonical user-facing artefact;
downstream `/triage` reads `grade.jsonl` directly, not stdout.

### `--tune-acknowledged` flag (manual reset) — **DEFERRED, not yet implemented**

> **Status**: this section describes a future-spec'd command. It is **not**
> wired in the current `grade-collector.py` — running `/baransu:grade
> --tune-acknowledged` today returns an unrecognized-flag error. Until
> implemented, manually edit `state.json.tune_review_due_since` to `null`
> if a reset is genuinely needed. Tracked as follow-up; the partition
> contract in `_shared/state-json-schema.md` §4 already accommodates this
> writer landing under the `/grade` partition.

When the user has reviewed the accumulated `grade.jsonl` and decided
on the next rubric weight policy, they would invoke:

```
/baransu:grade --tune-acknowledged
```

The intended behaviour: short-circuit the normal pipeline (no Stage 1
read, no Stage 2 collector run, no Stage 3 threshold check). The skill
performs a single mutation: load `state.json`, set
`state.json.tune_review_due_since = null`, and atomically write the
file back. It then prints a 繁中 confirmation line:

```
tune_review_due 已 acknowledge，等待下次累積跨閾值。
```

Semantics:
- **Manual only**: the flag is the single user-facing reset path. The
  collector itself never clears `tune_review_due_since` — only this
  flag does (KD#4 prohibits auto-reset).
- **Idempotent**: running `--tune-acknowledged` against a state where
  `tune_review_due_since` is already `null` is a no-op and does not
  error. The confirmation line is still printed.
- **Atomic**: the same temp-file + rename atomic write contract from
  `_shared/state-json-schema.md` §4 applies; `--tune-acknowledged`
  must not partial-write `state.json`.

---

## 5-dim baransu-native rubric (locked)

The dimension names, telemetry source fields, and deterministic derivation
rules are reproduced verbatim from
`plugins/baransu/skills/_shared/grade-triage-schema.md` §1 — that file is
the single source of truth. **Do not re-derive here.** This table exists
in SKILL.md so user-facing reads (`「跑 grade 是怎麼算的？」`) can answer
without round-tripping through the schema doc.

| dim | 意義 | telemetry 來源 | 推導規則 (deterministic) |
|---|---|---|---|
| `outcome_quality` | 結果品質：完成且綠燈高分 | `skill_outcome.exit_code` + `skill_outcome.final_state` | `terminal_state == "completed"` 且 `exit_code == 0` 且 `final_state` 不含 `failed`/`aborted`/`error` 子字串 → 1.0；否則按 `exit_code` 與 `final_state` 標記分檔降階（rubric script 內表查） |
| `iteration_velocity` | 迭代速度：少回合即高速 | `attempt_history`（同 cluster_id）+ `commit_hash` | 該 session 對應 cluster 的 attempt 次數 N → score = `1 / N`（N≥1，無 cluster 則視為 N=1） |
| `scope_blast` | 變動爆量：動到的檔案數 + 路徑風險 | `diff_summary_redacted` | `score = 1 - min(1, files_touched / 10) * 0.7 - risk_path_hit * 0.3`（敏感樣式如 `*.lock` / `migrations/*` 命中即 `risk_path_hit=1`，否則 0） |
| `human_override_rate` | 人工 override 率：低為高分 | `skill_outcome.final_state`（含 override 標記） | `final_state` 含 `override`/`manual`/`bypass` 子字串 → 0.0；否則 1.0 |
| `failure_recurrence` | 失敗重現：同 cluster 越多次累計失敗越低分 | `attempt_history` 中與此 row `cluster_id` 同 key 的近 7 日累計 `result == "fail"` 次數 K | `score = max(0, 1 - K * 0.2)`（K=0 → 1.0；K≥5 → 0.0） |

> 0–1 浮點精度 ≤ 1e-6 (INT-10 對應)。所有公式 deterministic：相同
> telemetry 輸入兩次計算 score 必同；禁含 `now()`/`uuid`/`random`/dict
> 順序依賴等隨機/時間敏感欄位。

### Quality enum (band edges, locked)

| `quality` | `aggregate` 區間 |
|---|---|
| `excellent` | `aggregate ≥ 0.85` |
| `good` | `0.70 ≤ aggregate < 0.85` |
| `acceptable` | `0.50 ≤ aggregate < 0.70` |
| `poor` | `aggregate < 0.50` |

`poor` is the entry point that `/triage` filters on.

---

## Bootstrap + tune trigger clause (locked)

- **Equal-weight bootstrap**: each of the 5 dimensions weighs exactly
  `1/5` (i.e. `0.2`). The aggregate is plain mean: `aggregate = sum(dims) / 5`.
  Weights are loaded from rubric configuration, **not** hard-coded inside
  `grade-collector.py`'s body — INV-4 grep checks rely on this file (and
  the `_shared` schema) to surface the `1/5` / `0.2` / `equal_weight`
  literals.
- **Tune trigger**: once cumulative `terminal_state == "completed"` rows
  reach `>= 50`, `/grade` prints `tune_review_due: true` on stdout and
  records `tune_review_due_since` (ISO-8601) into `state.json`. This is
  a **review** flag, not an auto-tune — weights are not changed
  automatically. A human reviews the accumulated grade.jsonl and either
  decides to keep equal weights or proposes new weights via a separate
  spec change.
- **Acknowledgement reset**: `/baransu:grade --tune-acknowledged` resets
  `tune_review_due_since` to null; subsequent runs stop printing the
  signal until the cumulative count again crosses the threshold (which
  for a freshly-reset state means another 50 fresh completed rows).

---

## Constraints

- **Only `terminal_state == "completed"` rows are scored.** All other
  states are excluded from `grade.jsonl` (KD#3 / INT-3).
- **No clustering.** Pattern detection across rows belongs to `/triage`.
- **No LLM judge.** The rubric is fully deterministic; same inputs →
  identical verdict bytes.
- **No telemetry mutation by `/grade` itself.** The only adjacent
  mutation is performed by the standalone `harness-reaper` script
  invoked in Stage 0, and even that is restricted to the single
  transition `in_progress → interrupted` past 24 hours.
- **Weights never hard-coded.** `1/5` lives in rubric config / this
  SKILL.md / `_shared/grade-triage-schema.md`, not inside the
  collector's source body — INV-4 grep gates depend on this layout.
- **All user-visible output in Traditional Chinese (繁體中文).** English
  appears only in this SKILL.md body, code paths, and JSON field names.

---

## References

- Implementation: `plugins/baransu/scripts/grade-collector.py`
  (5-dim equal-weight rubric, `1/5` each; reads telemetry.jsonl,
  writes grade.jsonl, updates state.json).
- Staleness sweep: `plugins/baransu/scripts/harness-reaper.py`
  (24h `in_progress → interrupted`; only writer of telemetry.jsonl
  adjacent to `/grade`).
- Authoritative schema: `plugins/baransu/skills/_shared/grade-triage-schema.md`
  (5 dim names, equal-weight bootstrap, tune trigger ≥ 50, quality enum
  4 values, escalate enum 3 values).
- Downstream consumer: `/triage` reads `grade.jsonl` rows where
  `quality == "poor"` and clusters them into `triage.jsonl`.
