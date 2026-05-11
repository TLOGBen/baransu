---
name: bridge
description: Use When validating a baransu skill upgrade against historical telemetry
  before promotion. Do A/B-replay main HEAD (v1) vs target branch (v2) on the same
  rubric, gated on Δ ≥ 0.15. Trigger On '比較 skill 兩版本', 'shadow run', 'regression
  demo'. 繁體中文輸出。
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

# /bridge — head-to-head skill replay

`/bridge` answers one question:「如果把 skill 從 v1 換成 v2，過去那批使用者的 prompt 跑出來會變好還是變糟？」

Concretely: replay the last N `terminal_state == completed` prompts from `telemetry.jsonl` against two versions of the same skill —
v1 = current `main` HEAD, v2 = the SKILL.md on a user-supplied target branch — score both runs with the same rubric (the rubric used by `grade-collector`), and gate on the signed score delta.

This skill is the manual counterpart to the auto-fix harness loop. Auto-fix never touches the main repo. `/bridge` follows the same isolation rule.

User-facing language is **繁體中文**; the body of this SKILL.md is in English because it is agent-facing.

---

## 目標

- 在「升級 skill 之前」幫使用者拿到一個基於歷史 corpus 的可重複實驗結論。
- 不接 LLM judge：score 由 `grade-collector` 的同一份 rubric 計算，純結構化比對。
- 不切流量、不自動 promote：`/bridge` 只回 `pass / fail / inconclusive` + 證據。是否上線是使用者的決定。

What `/bridge` does not do:
- Does not write to `telemetry.jsonl`, `grade.jsonl`, or `triage.jsonl` (those three are owned by other skills).
- Does not modify the main repo working tree, ever.
- Does not run on a schedule, cron, or hook.

---

## 手動 only（manual only）

`/bridge` is invoked manually with explicit args. It is **not** registered with `CronCreate`, **not** triggered by any PostToolUse / Stop hook, and **not** reachable from any auto-fix loop. Calling `/bridge` always requires a human typing the command.

Usage shape:

```
/baransu:bridge <target_branch> [--skill <name>] [--corpus-size N] [--allow-untrusted]
```

- `<target_branch>` — required; the branch holding the v2 SKILL.md to evaluate.
- `--skill <name>` — optional; the skill being compared (e.g. `think`, `dev`). Default: infer from the diff between main and the target branch.
- `--corpus-size N` — optional; default `50`. Minimum number of completed prompts required to produce a non-inconclusive verdict.
- `--allow-untrusted` — opt-in flag, see Stage 0.

If the user invokes `/bridge` without arguments, ask once for the target branch and exit. Do not guess.

---

## Stage 0 — Environment + trust check (S-F3)

Five things must be true before any worktree is created. If any of them fail, refuse to run and print the reason in 繁體中文.

1. **Telemetry corpus check** — `.claude/harness/telemetry.jsonl` exists and contains at least N entries with `terminal_state == "completed"` and a non-empty `prompt_text`. Default N is 50 (overridable via `--corpus-size`). Insufficient corpus → refuse to run, exit non-zero, do **not** call `bridge-replay.sh` (no worktree is ever created on this path). Required user-facing 繁中 message template:

   > 「目前 telemetry corpus 僅 X 條 completed row（門檻 N=50），暫時無法跑 head-to-head replay。建議：累積至 ≥ 50 條 completed.prompt_text 後再呼叫 `/bridge`。」

   Substitute `X` with the actual matched count and `N` with the effective threshold (the `--corpus-size` value if provided, otherwise 50).

2. **Target branch exists locally** — `git rev-parse --verify <target_branch>` must succeed. If it doesn't, ask the user to fetch first. Do not auto-fetch silently.

3. **Main repo working tree clean** — `git -C <main_repo> status --porcelain` must be empty. If dirty, refuse and ask the user to commit / stash first. The point of `/bridge` is reproducibility; running over a dirty tree pollutes the experiment.

4. **Target branch trust check (S-F3 — local-RCE防線)**.
   - Read the author email of the target branch's most recent commit: `git log -1 --format='%ae' <target_branch>`.
   - Compare against `git config user.email`.
   - If they match → trust check passes.
   - If they do **not** match and `--allow-untrusted` was **not** supplied → refuse with the warning below and exit non-zero.
   - If they do not match and `--allow-untrusted` **was** supplied → log the override into the per-run report and continue.

   Required SKILL warning text (always shown when this check is reached, regardless of outcome):
   > **警告**：v2 SKILL body 會以你的身分在本機執行。只對自己信任的 branch 用 `/bridge`。如果非用不可，請加 `--allow-untrusted` 並承擔本機 RCE 風險。長期解會是 firejail / bwrap sandbox，本期僅以 author email 比對作語意層擋住。

5. **Read-only deps available** — `plugins/baransu/scripts/bridge-replay.sh` and `plugins/baransu/skills/_shared/grade-triage-schema.md` must exist on disk. They are read-only inputs to this stage.

---

## Stage 1 — Corpus extraction

Pull the corpus from telemetry. The contract is fixed by KD#3:

- Source: `.claude/harness/telemetry.jsonl`.
- Filter: `terminal_state == "completed"` AND `prompt_text` non-empty.
- Order: most recent N first (by `ts`).
- Output: in-memory list of `{prompt_id, prompt_text, ts, skill_invoked}` records.

If the user passed `--skill <name>`, additionally filter to entries whose `skill_invoked == <name>`. If the result drops below N, downgrade to inconclusive territory (Stage 3 will handle).

Do not write the corpus to disk. It lives in memory for the duration of the run; the per-run report (Stage 1.5) records corpus size and prompt IDs only.

---

## Stage 1.5 — Open per-run report (A-F2 audit trail)

Open exactly one append-only file per `/bridge` invocation:

```
.claude/harness/bridge-runs/bridge-{ISO_ts}-{branch_or_cluster}.jsonl
```

- `{ISO_ts}` — UTC ISO 8601, e.g. `2026-04-29T13:42:11Z`.
- `{branch_or_cluster}` — sanitised target branch name (or, if the run scope is a cluster of branches, the cluster id).
- Single writer, single reader (this skill); no concurrent writers, no race window.
- The directory `.claude/harness/` is `gitignore`d in baransu (INV-5). The per-run report is harness-owned scratch space, not part of the main repo working tree — invariant 3 below still holds.

First record written is a `meta` line:

```json
{"event":"start","target":"<branch>","skill":"<skill>","corpus_size":N,"start_at":"<ISO_ts>","trust":"matched|allow-untrusted"}
```

If Stage 1.5 cannot create the file, abort the run before any worktree is created. Cleanup is trivial because nothing was created.

---

## Stage 2 — Run bridge-replay

Hand off to the replay script. The script lives at:

```
plugins/baransu/scripts/bridge-replay.sh
```

The script is the single component allowed to:
- call `mktemp -d /tmp/baransu-bridge-XXXXXX` to create the isolated dir,
- call `git worktree add <isolated_dir> <target_branch>` to materialise v2,
- install a `trap` on `SIGINT EXIT` that runs `git worktree remove --force <isolated_dir>` followed by `rm -rf <isolated_dir>`,
- `cd` into the isolated dir for the duration of the loop, so any accidental relative writes hit the worktree, not the main repo.

For every prompt in the corpus, the script:
1. Runs the skill (v1) against `prompt_text`, captures `output_v1`, scores it with `grade-collector` rubric → `score_v1`.
2. Runs the skill (v2, from the worktree) against the same `prompt_text`, captures `output_v2` → `score_v2`.
3. Appends one JSON record per prompt to the per-run report:

```json
{"event":"replay","prompt_id":"<id>","score_v1":0.82,"score_v2":0.74,"delta":-0.08}
```

The skill body in this SKILL.md does not re-implement any of the above. It calls the script and consumes the script's exit code + stdout summary.

---

## Stage 3 — Statistical gate (Δ-gate)

After the replay loop finishes, compute the aggregate signed delta:

```
Δ = mean(score_v2) − mean(score_v1)
```

Decide and emit:

- **inconclusive** — actual sample size after Stage 1's filtering is below the corpus threshold (corpus < N, or `--corpus-size` was set higher than what telemetry supplied). Required user-facing 繁中 message template (this branch is **不是 pass、也不是 fail**；不誤判 pass/fail 是這個分支存在的理由)：

  > 「樣本不足以判定 pass / fail（mean v1 = X、mean v2 = Y、樣本數 K < 統計閾值 T）。結果：inconclusive；建議累積更多 telemetry 後重跑 `/bridge`。」

  Substitute `X` / `Y` with the computed means, `K` with the post-filter sample size, and `T` with the effective threshold (default 50). Exit non-zero so callers cannot mistake inconclusive for pass.
- **fail** — `Δ ≤ -0.15` (i.e. v2 is at least 0.15 worse on average). Print top-N degraded prompts (largest negative per-prompt delta) with prompt_id + Δ, plus a「不要 promote」suggestion, exit non-zero.
- **pass** — neither of the above (`Δ > -0.15` with sufficient corpus). Print Δ + a「可考慮 promote」suggestion, exit 0.

The threshold is fixed at **|Δ| ≥ 0.15** (the design uses Δ ≥ 0.15 in absolute regression direction, signed against v1). Do not parametrise the threshold from the command line — keeping it fixed is what makes the gate a gate.

Append the verdict to the per-run report:

```json
{"event":"verdict","result":"pass|fail|inconclusive","delta":-0.20,"top_degraded":[{"prompt_id":"<id>","delta":-0.41},...]}
```

---

## Stage 4 — Cleanup verification

Even after the trap fires, verify two invariants explicitly before exiting:

1. `git worktree list` no longer shows any `/tmp/baransu-bridge-*` entry.
2. `git status --porcelain` of the main repo is byte-identical to the snapshot taken at Stage 0 step 3.

If either check fails, do not exit silently — print「cleanup 異常，請手動 `git worktree remove --force <path>` + `rm -rf <path>`」and surface the leftover path. The per-run report's last record records cleanup status:

```json
{"event":"cleanup","worktree_clean":true,"main_repo_dirty":false,"end_at":"<ISO_ts>"}
```

Close the per-run report (single-writer; closing here means flushing + releasing the file handle).

---

## Invariants

These four invariants are the contract of `/bridge`. If any is violated, the run is broken regardless of stdout output.

1. **Worktree location** — the isolated worktree lives under `/tmp/baransu-bridge-XXXXXX` (mktemp). It is never created inside the repo, even when convenient.
2. **Cleanup trap mandatory** — `trap cleanup EXIT INT TERM` is installed inside `bridge-replay.sh` (see that script for the canonical `trap … EXIT INT TERM` line) **before** `git worktree add` runs. **All** termination paths — Stage 0 refuse (corpus 不足 / dirty repo / untrusted branch), Stage 3 inconclusive, Stage 3 fail, Stage 3 pass, and SIGINT mid-loop — go through this same cleanup path. The Stage 0 corpus-不足 refuse path exits before any worktree is created, but the trap is a no-op on that path; the contract still holds (cleanup never silently skipped, even when there is nothing to clean).
3. **Main repo working tree never touched** — `git status --porcelain` snapshot taken at Stage 0 step 3 is identical to the snapshot taken at Stage 4. The per-run report under `.claude/harness/bridge-runs/` does not affect this invariant because `.claude/harness/` is gitignored.
4. **Trust default-deny** — target branch with author email ≠ `git config user.email` is refused unless `--allow-untrusted` is supplied. The flag is the only way to override; there is no env var, no config file, no silent path.

---

## Error paths

| 觸發條件 | 行為 |
|---------|------|
| `telemetry.jsonl` 不存在 / corpus < N | Stage 0 拒跑，印「corpus 不足」訊息，無 worktree 創建。|
| target branch 不存在 / 未 fetch | Stage 0 拒跑，請使用者 `git fetch` 或拼字確認。|
| 主 repo working tree 髒 | Stage 0 拒跑，請使用者先 commit / stash。|
| target branch author email 與 user.email 不符且無 `--allow-untrusted` | Stage 0 拒跑，印 RCE 警語。|
| `git worktree add` 失敗 | trap 觸發；per-run report 寫 abort 記錄；錯誤訊息上拋。|
| replay 中 SIGINT | trap → `git worktree remove --force` + `rm -rf`；per-run report 補一筆 `event:"abort"` 後關閉。|
| replay 完成但 corpus 實際 < N | Stage 3 判 inconclusive（**非 pass、非 fail**）；trap cleanup 仍照走，worktree 與 `/tmp/baransu-bridge-*` 不留殘餘。|

---

## 引用 / Reference deps

- `plugins/baransu/scripts/bridge-replay.sh` — implementation carrier for Stage 2; owns `mktemp`, `git worktree`, `trap`, replay loop. The SKILL describes WHAT; the script does HOW.
- `plugins/baransu/skills/_shared/grade-triage-schema.md` — authoritative source of the 5-dim rubric (`outcome_quality / iteration_velocity / scope_blast / human_override_rate / failure_recurrence`); same rubric `grade-collector` uses, so v1/v2 scores are comparable.

---

## Constraints

- All user-facing output (refusal messages, verdict announcement, top-N degraded table) is in **Traditional Chinese (繁體中文)**.
- Never write to `telemetry.jsonl`, `grade.jsonl`, or `triage.jsonl`. The only file `/bridge` is allowed to write is the per-run report under `.claude/harness/bridge-runs/`.
- Never modify the main repo working tree. The per-run report path is harness-owned scratch space (`.claude/harness/` is gitignored).
- Never run on cron, hook, or as part of an auto-loop. Manual invocation only.
- Never silently fall back to `--allow-untrusted`. The flag must be present on the user's command line.
- Never reuse a worktree across invocations. Every `/bridge` run gets a fresh `mktemp -d`.
- Sub-agent depth = 1: do not spawn sub-skills inside this skill's stages.
