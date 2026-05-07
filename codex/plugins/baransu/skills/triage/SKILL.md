---
name: triage
description: Cluster `quality == "poor"` verdicts produced by `/grade`, score each
  cluster on the same 5-dim baransu-native rubric, dispatch the read-only `investigator-agent`
  for evidence collection, and write cluster rows into `.claude/harness/triage.jsonl`.
  Trigger immediately when the user asks to「跑 triage」/「triage 一下昨天的 poor 」/「分流 poor
  verdict」/「處理 poor verdict」/「對 grade.jsonl 聚類」or in English "run triage" / "cluster
  poor verdicts" / "dispatch investigator". Also fires on the daily cron schedule
  (00:00) inside the self-healing harness, immediately after `/grade`. `/triage` does
  NOT score (that is `/grade`'s job) and does NOT directly edit code (the auto-fix
  sub-flow at Stage 4 delegates code edits to `/dev`). User-facing output is in Traditional
  Chinese (繁體中文).
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

# triage — cluster poor verdicts and prepare evidence-backed rows

`/triage` is one of three skills (`/grade`, `/triage`, `/bridge`) that close
the self-healing harness loop. It is the **clustering + evidence** stage:

- **Reads** `.claude/harness/grade.jsonl` (`quality == "poor"` rows) and
  `.claude/harness/telemetry.jsonl` (the corresponding telemetry rows
  joined by `session_id`).
- **Clusters** poor verdicts via `plugins/baransu/scripts/triage-cluster.py`,
  computing 5-dim severity scores per cluster (same dim names as `/grade`).
- **Dispatches** the `investigator-agent` (read-only perspective subagent)
  on each over-threshold cluster to collect an `evidence_bundle`.
- **Writes** one row per cluster to `.claude/harness/triage.jsonl`.
- **Triggers** the auto-fix sub-flow at Stage 4 (deferred to extender
  tasks `TASK-skills-triage-02 / 03 / 04`).

The body below is English (agent-facing). All user-visible output is in
**Traditional Chinese (繁體中文)** per the baransu plugin convention.

---

## 目標

- Take `quality == "poor"` rows out of `grade.jsonl` and group them into
  stable cluster ids so that downstream auto-fix attacks the
  **pattern**, not one-off symptoms.
- Score each cluster's severity along the 5 baransu-native rubric
  dimensions so that `/triage`'s priority order is reproducible
  (deterministic — no LLM judge, no `now()` / `random` dependency).
- Hand off to the `investigator-agent` (perspective-class, read-only)
  to attach an evidence bundle (`root_cause_guess` + cited file paths +
  confidence) to each over-threshold cluster row.
- Make the triage.jsonl row the **single artefact** that the auto-fix
  sub-flow consumes — `/triage` itself never modifies repo source.

---

## 邊界（boundaries / scope）

What `/triage` is **not** allowed to do:

- **不打分（grading 由 /grade 負責）.** Per-row scoring lives in
  `/grade`; `/triage` only aggregates already-scored `poor` rows into
  cluster severity.
- **不直接修 code.** The auto-fix sub-flow at Stage 4 (defined by
  TASK-skills-triage-02 / 03 / 04) is the **only** path that delegates
  code edits, and even then it dispatches to `/dev` inside an isolated
  worktree — `/triage` core never touches the main repo working tree.
- **不調 rubric.** The 5-dim names and the equal-weight bootstrap are
  locked in `plugins/baransu/skills/_shared/grade-triage-schema.md`.
  `/triage` reuses those dimension names for cluster severity (not for
  per-row grading).
- **不寫 telemetry.jsonl.** Only the auto-fix sub-flow's worktree-side
  write may extend `attempt_history` per the merge-into-existing-row
  contract; `/triage` core is read-only against `telemetry.jsonl`.
- **不接 LLM judge.** Cluster severity is deterministic; same
  `grade.jsonl` + `telemetry.jsonl` inputs → byte-identical
  `triage.jsonl` rows.

---

## Inputs / outputs

| Direction | Path | Note |
|---|---|---|
| Read | `.claude/harness/grade.jsonl` | append-only JSONL; `/triage` filters to rows with `quality == "poor"` |
| Read | `.claude/harness/telemetry.jsonl` | join key = `session_id`; used for `attempt_history` aggregation, `diff_summary_redacted`, etc. |
| Write | `.claude/harness/triage.jsonl` | one row per cluster (8 fields, see schema §6 of `_shared/grade-triage-schema.md`) |

Schema for `triage.jsonl` is locked in
`plugins/baransu/skills/_shared/grade-triage-schema.md` §6 + §7.

---

## Stage 0 — Environment check

0. Cron silent-failure health check (inline). **First action of `/triage`.**
   ```sh
   python3 plugins/baransu/scripts/health_check.py \
     --state .claude/harness/state.json \
     --threshold-hours 36
   ```
   - Inspects `last_grade_run_at`; emits a 4–6 line 繁中 warning to stdout
     when missing / null / older than 36h. Healthy state is silent.
   - **Always exits 0** — observational only; never blocks triage.
   - `/triage` carries this same probe (despite typically firing after
     `/grade` on cron) because `/triage` SKILL.md own description allows
     manual trigger as a legitimate path; the health check must catch
     the manual-only path too.
1. Confirm `.claude/harness/grade.jsonl` exists and is non-empty.
   - If missing or empty → print 繁中
     `「grade.jsonl 不存在或為空，沒有可分流的 verdict；結束。」`
     and exit 0 (no error — the harness has nothing to triage yet).
2. Confirm `.claude/harness/telemetry.jsonl` exists. (`/triage` joins
   on `session_id`; without telemetry, the join is a no-op and the
   resulting cluster rows would be missing fields.)
   - If missing → print 繁中
     `「telemetry.jsonl 不存在；triage 無法 join，結束。」`
     and exit 0.
3. Quickly count `quality == "poor"` rows via `jq`:
   ```sh
   jq -c 'select(.quality == "poor")' .claude/harness/grade.jsonl | wc -l
   ```
   - If count == 0 → print 繁中
     `「目前 grade.jsonl 沒有 poor verdict；無需分流。」`
     and exit 0.
4. Snapshot `git status --porcelain` for later comparison against the
   investigator's read-only invariant (see Stage 2 + §INT-5).

> Hard rule (KD#3): `/triage` consumes `grade.jsonl` which has
> already been filtered by `/grade` to `terminal_state == "completed"`
> rows. `/triage` does NOT re-filter telemetry by terminal state —
> that is `/grade`'s job.

---

## Stage 1 — Run triage-cluster

Invoke the cluster-and-severity script. It is the single owner of the
clustering math; this SKILL.md describes only the contract.

```sh
python3 plugins/baransu/scripts/triage-cluster.py \
  --grade     .claude/harness/grade.jsonl \
  --telemetry .claude/harness/telemetry.jsonl \
  --output    .claude/harness/triage.jsonl
```

Arguments:

| Flag | Meaning |
|---|---|
| `--grade` | input JSONL path (read-only) — `quality == "poor"` rows are clustered |
| `--telemetry` | input JSONL path (read-only) — joined by `session_id` for severity inputs |
| `--output` | output JSONL path; the script appends one row per cluster with `escalate` initially `false` |

The script produces, per cluster:

- `cluster_id` (stable id — e.g. `cl-001`, derived from
  `attempt_history.cluster_id` on the underlying telemetry rows).
- `member_session_ids` (the session_id list covered by this cluster).
- `severity_dims` (5 sub-fields, **same dim names** as
  `grade.jsonl.dims`: `outcome_quality`, `iteration_velocity`,
  `scope_blast`, `human_override_rate`, `failure_recurrence`; each
  in `[0, 1]`, where higher = more severe — typically `1 - avg(grade
  dim)` across cluster members).
- `severity_aggregate` (`sum(severity_dims) / 5`).
- `escalate` initially `false` — Stage 2 / Stage 3 promotes the enum
  based on severity threshold + investigator confidence + (in the
  triage-03 extender) the 5-black push gates.

> Cluster keys come from `attempt_history.cluster_id`; rows without a
> cluster_id collapse into a synthetic singleton `cl-singleton-<hash>`.

---

## Stage 2 — Dispatch investigator-agent

For each cluster whose `severity_aggregate ≥ 0.5` (the over-threshold
gate), dispatch the read-only `investigator-agent` perspective
subagent. Below-threshold clusters are recorded as trend rows
(`escalate: false`) and **no investigator is dispatched** for them
(REQ-003 Scenario 3).

### Dispatch contract (Agent tool)

Use the Claude Code `Agent` tool with `subagent_type="investigator"`
(maps to `plugins/baransu/agents/investigator-agent.md`). The dispatch
prompt **must** include:

- `cluster_id` — stable identifier the investigator echoes back.
- `member_session_ids` — the list to inspect.
- Context paths — which telemetry rows / git refs / source paths to
  read. The investigator is **only** allowed to read; it must not
  open editor / write tools / git mutations.

The investigator returns a structured `evidence_bundle`:

```json
{
  "root_cause_guess": "<one-sentence string>",
  "citations": [
    {"file_path": "src/<path>", "line_range": "42-58", "excerpt": "<≤200 chars>"}
  ],
  "confidence": 0.55
}
```

`/triage` merges this bundle into the corresponding `triage.jsonl`
row at Stage 3.

### Investigator read-only invariant (KD#1 / INT-5)

The `investigator-agent` is a **perspective-class, read-only** subagent.
The contract is enforced by **defense in depth**, NOT by a single tool
whitelist — the whitelist alone cannot prevent every mutation, since
`Bash` is in the list and a sufficiently coercive prompt could ask it to
shell-out (`> file`, `git add`, `chmod`). Three layers cooperate:

- **Tool whitelist**: the agent's `tools` list (in
  `plugins/baransu/agents/investigator-agent.md`) is `Read, Grep, Glob,
  Bash`. This narrows the *initial* attack surface — Edit / Write /
  NotebookEdit / Task are excluded — but is **not** the final enforcer.
- **Agent-body lane-keeping (instruction-level)**: the agent body
  declares an explicit Forbidden list (no `git add`/`commit`/`push`/
  `branch`/`worktree`, no `>` redirects, no `chmod`, no Edit/Write tool
  calls). The agent is instructed to refuse any prompt asking for them.
- **Pre/post `git status` postcheck (INT-5a — the structural enforcer)**:
  the snapshot taken at Stage 0 step 4 is compared against
  `git status --porcelain` after the investigator returns. If they
  differ, the investigator violated the read-only contract; the run
  aborts and the cluster's `evidence_bundle` is rejected (it is **not**
  treated as legitimate evidence — the caller surfaces an error signal
  and the row is not written). This postcheck is the load-bearing
  enforcement: it would catch a mutation even if the whitelist + lane
  instructions both failed.
- **Negative case (INT-5b)**: if a mock prompt tries to coerce the
  investigator into a write/git op, the dispatcher intercepts (or the
  agent self-rejects per lane-keeping). `git status` stays clean; the
  rejection surfaces as an error to `/triage`'s caller; no fabricated
  evidence is merged.

> Hard constraint (KD#1): `investigator-agent` performs ZERO git ops
> (no `git add` / `commit` / `push` / `branch` / `worktree`), writes
> ZERO files. Any deviation invalidates the evidence bundle.

---

## Stage 3 — Write triage.jsonl

Merge cluster + evidence_bundle into one append-only row per cluster
in `.claude/harness/triage.jsonl`. The 8-field row schema is locked in
`_shared/grade-triage-schema.md` §6:

| Field | Source |
|---|---|
| `cluster_id` | `triage-cluster.py` Stage 1 output |
| `member_session_ids` | Stage 1 output (telemetry session_ids covered) |
| `severity_dims` | Stage 1 output (5 sub-fields, same names as grade dims) |
| `severity_aggregate` | Stage 1 output (`sum(severity_dims) / 5`) |
| `escalate` | promoted from `false` (Stage 1 default) to one of `false` / `requires_human` / `daily_quota_exceeded` per §4 of the schema |
| `evidence_bundle` | written by Stage 2 `investigator-agent`; `null` when `escalate == false` (no investigator dispatched) |
| `attempt_count` | derived view from telemetry — `count(attempt_history[*] where cluster_id == self.cluster_id and result == "fail")` (read-only aggregate; authority lives in `telemetry.jsonl`) |

`escalate` enum promotion rules (from `_shared/grade-triage-schema.md`
§4) — applied after Stage 2 returns:

| `escalate` value | trigger |
|---|---|
| `false` | `severity_aggregate < 0.5` (below threshold; no investigator dispatched) |
| `requires_human` | `severity_aggregate ≥ 0.5` AND `evidence_bundle.confidence < 0.6` (or root cause ambiguous) |
| `daily_quota_exceeded` | day's auto-fix attempt cap already hit (controlled by harness state — concrete logic added in TASK-skills-triage-03's 5-gate push pipeline) |

> The three values are mutually exclusive; one cluster row can only
> hold one of them.

Atomic write: append one JSON line per cluster to
`.claude/harness/triage.jsonl`. The file is append-only, gitignored,
and lives next to `telemetry.jsonl` / `grade.jsonl`.

---

## Stage 4 — Trigger auto-fix sub-flow（自動修補子流程）

> **Wired contracts (harness-followup TASK-enforcement-01/02/03 +
> TASK-skills-triage-04).** Stage 4.1 (renderer call), Stage 4.2
> (push-gate call) and Stage 4.3 (worktree isolation) are wired
> contracts — SKILL.md指示如何呼叫腳本並依 exit code / stdout 行動，
> deterministic enforcement 已 rebase 到 `render-auto-fix-prompt.py`
> 與 `push-gate.sh`。 Cron-driven loop dispatcher（逐 row 跑
> auto-fix）尚未在本任務範圍內接入；在那之前，`/triage` 仍寫完
> `triage.jsonl` 即 exit。

Stage 4 iterates over `triage.jsonl` rows where `escalate == false`
AND `severity_aggregate ≥ 0.5` (i.e. confident, over-threshold,
auto-fixable clusters), and run the auto-fix sub-flow per row.

### 4.1 auto-fix prompt — renderer call (TASK-enforcement-03)

For each over-threshold cluster (`severity_aggregate ≥ 0.5` AND
`escalate == false`), Stage 4.1 hands the prompt-construction job to
the deterministic Python renderer. SKILL.md does **not** describe
escape rules, marker-forgery defences, or truncate logic in prose —
those defences live inside the renderer (single source of truth) and
are documented in its docstring + unit tests.

#### Renderer call contract

```sh
python3 plugins/baransu/scripts/render-auto-fix-prompt.py \
    <cluster_id> <evidence_bundle.json>
```

| Field | Value |
|---|---|
| `<cluster_id>` | `triage.jsonl.cluster_id` (e.g. `cl-001`) |
| `<evidence_bundle.json>` | path to a JSON file holding the cluster's `evidence_bundle` (the same object the investigator-agent returned at Stage 2) |
| stdout | the fully-rendered prompt to feed to `/dev` |
| exit 0 | prompt rendered (incl. empty-citations case) |
| exit 1 | structural error (missing `citations` key, malformed JSON, I/O); SKILL.md Stage 4.1 aborts and does NOT dispatch `/dev` |

The renderer is the single source of truth for the S-F5
prompt-injection defences; this SKILL.md only invokes it. See
`render-auto-fix-prompt.py` docstring for the locked-order sanitiser
and the per-line / total truncate rules — they are intentionally not
duplicated here.

#### sha256 reproducibility (INT-12)

Same `(cluster_id, evidence_bundle.json)` → byte-stable stdout.
Two consecutive invocations MUST produce a stdout whose `sha256` is
byte-identical. The renderer is deterministic — no timestamps, no
uuid, no randomness, no dict-insertion-order dependency.

To reproduce the check by hand:

```sh
sha256sum \
  <(python3 plugins/baransu/scripts/render-auto-fix-prompt.py cl-001 bundle.json) \
  <(python3 plugins/baransu/scripts/render-auto-fix-prompt.py cl-001 bundle.json)
# Both sha256 hashes MUST match. A `cmp` between the two rendered
# prompts MUST return 0 (byte-identical / reproducible).
```

Mismatch = invariant violation → block the auto-fix attempt and log
the diff (KD#5 第 1 條 audit).

#### /dev invocation contract

Auto-fix calls `/dev` through the Skill tool (i.e. `Skill tool`
dispatch with `skill: "dev"`), passing the renderer's stdout
unchanged:

| Field | Value |
|---|---|
| `skill` | `"dev"` (resolves to `plugins/baransu/skills/dev/SKILL.md` via Skill tool) |
| `prompt` | the renderer's stdout (no LLM rewriting; byte-stable) |
| `working_dir` | the isolated worktree from Stage 4.3 — never the main repo working tree |

Expected return shape from `/dev`:

```
{
  "status": "Green" | "Red" | "Blocked",
  "patch":  "<unified diff>",
  "commit_hash": "<sha1>" | null,
  "tests_summary": { "passed": <int>, "total": <int> }
}
```

`/dev` itself is unchanged by this task — `/triage` is just a caller
that pipes the renderer's stdout into it.

### 4.2 auto-fix push gates — push-gate.sh call (TASK-enforcement-03)

每次 auto-fix `/dev` 在 worktree 內完成 patch 後，呼叫 `push-gate.sh`
觀察 exit code 來決定下一步。SKILL.md 不描述 gate 內部順序、denylist
glob、attempt cap 邏輯、daily quota 計算 —— 那些細節是 `push-gate.sh`
的內部規格（單一 source of truth），文件在腳本 header docstring。

#### Gate-script call contract

```sh
bash plugins/baransu/scripts/push-gate.sh \
    <cluster_id> <worktree_path> <state_json_path> <telemetry_jsonl_path>
```

| Token | Meaning |
|---|---|
| `<cluster_id>` | 目前要嘗試 push 的 cluster id (e.g. `cl-001`) |
| `<worktree_path>` | Stage 4.3 mktemp 出來的 isolated worktree 絕對路徑 |
| `<state_json_path>` | `.claude/harness/state.json` 路徑 |
| `<telemetry_jsonl_path>` | `.claude/harness/telemetry.jsonl` 路徑 |

#### Exit code → escalate enum 對應表

| Exit code | 意義 | SKILL.md Stage 4.2 行為 |
|---|---|---|
| `exit 0` | happy path（4 gates 全過） | 允許後續 `git push origin harness/fix/<cluster_id>`、`state.json daily_push_count++`、`telemetry.jsonl attempt_history` append 一個 `result: "success"` element |
| `exit 1` | gate 命中 | 解析 stdout `escalate=<enum>`，把該值原樣寫進 `triage.jsonl` 該 cluster 的 `escalate` 欄位；`telemetry.jsonl` 對應 row 的 `attempt_history` append 一個 `result: "fail"` element；**不** push |
| `exit 2` | structural error（缺 input / state 不可讀 / git diff 失敗） | abort + 把 stderr 訊息報給 caller；**不** push、**不**更新 `state.json`、**不**寫 `triage.jsonl` |

`exit 1` 時 stdout 第一行恆為 `escalate=<enum>`，其中 `<enum>` 為下列三者之一
（單一 source of truth：`push-gate.sh` 自行決定哪個 enum，SKILL.md 不可自選）：

- `escalate=requires_human` — denylist 命中 / preflight 命中
- `escalate=escalate_human` — attempt cap K=3 命中
- `escalate=daily_quota_exceeded` — daily quota 命中

#### BARANSU_HARNESS_FAKE_NOW

`push-gate.sh` 內部走 daily-quota reset 路徑時，若環境變數
`BARANSU_HARNESS_FAKE_NOW`（ISO date 字串，例如 `2026-04-30`）有設，
則以該值為「today」；未設則使用 `date +%Y-%m-%d`。INT-7 重現支援：

```sh
BARANSU_HARNESS_FAKE_NOW=2026-04-30 \
  bash plugins/baransu/scripts/push-gate.sh cl-001 "$worktree" \
       .claude/harness/state.json .claude/harness/telemetry.jsonl
```

#### Caller 責任（push-gate.sh 後續處理）

- `exit 0` 後：在 worktree 內跑 `git push origin harness/fix/<cluster_id>`，
  push 成功印出 GitLab MR 連結
  `https://git.hy-tech.com.tw/{owner}/baransu/-/merge_requests/new?merge_request[source_branch]=harness/fix/<cluster_id>`；
  push 失敗（git error / 網路 / 503）→ `attempt_history` append `result: "fail"`、
  **不刷** `daily_push_count`（避免單次失敗吃配額）、寫
  `triage.jsonl.escalate = requires_human`。
- `exit 1` 後：caller 解析 stdout `escalate=` 行，照原值寫進
  `triage.jsonl`；不再對該 cluster 呼叫 `/dev`、不 push。
- `exit 2` 後：caller 直接 abort，不更新 `state.json`、不寫 `triage.jsonl`，
  把 stderr 訊息冒泡到 cron run log。

#### attempt_history 寫入契約（沿用 design.md telemetry mutation 子契約）

- auto-fix 是除 hook 以外**唯一**對 `telemetry.jsonl` 既有 row 做 mutation 的 writer。
- mutation 形式 = 對 row 的 `attempt_history` array append 一個 element
  （**不**新增 jsonl 行；以 `session_id + cluster_id` 作 join key locate 既有 row）。
- `triage.jsonl` 的 `attempt_count` 欄位是這份 attempt_history 的衍生 aggregate
  （read-only view）；權威來源永遠在 `telemetry.jsonl`。
- **並發保護**：必須持 `flock(2)` 鎖 `.claude/harness/.telemetry.lock`；
  mutation 走 read 全檔 → modify in-memory → 寫臨時檔 → atomic `rename(2)` 取代原檔。
- 失敗（lock timeout / write error）→ log stderr，不 crash auto-fix 主流程。

#### 不變量驗證 (Test cases — 呼叫 push-gate.sh + 觀察 exit code)

對應 `Test:` 章節的 5 條測試。每條 EDGE 案例都化為「設定 fixture →
跑 `push-gate.sh` → 觀察 exit code 與 stdout」：

- **EDGE-3**：mock `/dev` 產生的 diff 含 `plugins/baransu/.claude-plugin/marketplace.json`
  → 跑 `push-gate.sh` → `exit 1`、stdout `escalate=requires_human`；無 git push 副作用。
- **EDGE-4**：seed `telemetry.jsonl` 同 cluster_id 的 attempt_history 含 3 個
  `result: "fail"` element → 第 4 次跑 `push-gate.sh` → `exit 1`、stdout
  `escalate=escalate_human`；不 push。
- **EDGE-5**：seed `state.json` `daily_push_count = 5`、`daily_push_date = today`
  → 第 6 個 cluster 跑 `push-gate.sh` → `exit 1`、stdout `escalate=daily_quota_exceeded`；
  不 push。
- **INT-7**：以 `BARANSU_HARNESS_FAKE_NOW=2026-04-30` 模擬隔日跑 `push-gate.sh`
  → state.json reset count = 0、date = 2026-04-30 → `exit 0` 可繼續 push。
- **INT-6**：`exit 0` 路徑後，`telemetry.jsonl` 對應 (session_id + cluster_id) row
  的 `attempt_history` array 多一個 `result: "success"` element（不是新增 jsonl 行）。

### 4.3 auto-fix worktree 隔離（trap-protected mktemp）(TASK-skills-triage-04)

auto-fix 全程在 isolated worktree 內進行，主 repo working tree 永不被 touch
（INV-5、KD#6）。

#### Worktree 設定

Namespace 與 `/bridge` 區分：auto-fix 用 `baransu-harness-*`、`/bridge` 用
`baransu-bridge-*`，避免 `git worktree list` 混用。

```sh
# Namespace distinct from /bridge (baransu-harness-* vs baransu-bridge-*)
tmpdir=$(mktemp -d /tmp/baransu-harness-XXXXXX)
git worktree add "$tmpdir" "$target_branch"
cd "$tmpdir"
```

模板與 task-scripts-03（`plugins/baransu/scripts/bridge-replay.sh`）的
mktemp + `git worktree add` + `trap` 結構一致；需要時可抽 helper 共用。

#### Trap cleanup（SIGINT 與 EXIT 共用同一程式碼路徑）

```sh
cleanup() {
  local exit_code=$?
  cd /  # leave the worktree before removing
  git worktree remove --force "$tmpdir" 2>/dev/null || true
  rm -rf "$tmpdir"
  exit $exit_code
}
trap cleanup EXIT INT TERM
```

cleanup 順序固定：先 `git worktree remove --force`（清 git 內部 metadata），
再 `rm -rf`（清 dir 本體）。順序顛倒會在 `git worktree list` 留 stale entry。
INT-9a（SIGINT 路徑）與 INT-9b（inconclusive exit 路徑）走同一 cleanup 函式。

#### 適用範圍（all termination paths）

- 5 gates abort（denylist / attempt cap / daily quota）→ trap 自然觸發 cleanup
- `/dev` 失敗（Red / Blocked）→ trap 觸發 cleanup
- push 失敗 → trap 觸發 cleanup
- push 成功 → trap 觸發 cleanup（worktree 用完即清）
- SIGINT（ctrl-c）→ trap 觸發 cleanup
- inconclusive exit（樣本不足、corpus < N）→ trap 觸發 cleanup（INT-9b）

cleanup 失敗時不靜默忽略：trap handler 應 log stderr 並回非零 exit code
（與 INT-9 對齊）。

#### INV-5 驗證（auto-fix 不 touch 主 repo working tree）

cron run 前後對主 repo `git status --porcelain` 結果必相同。下列 one-liner
作為 invariant gate：

```sh
pre=$(git -C /home/vakarve/project/clis/baransu status --porcelain | sort)
# ... cron 觸發 /triage auto-fix ...
post=$(git -C /home/vakarve/project/clis/baransu status --porcelain | sort)
diff <(echo "$pre") <(echo "$post") && echo PASS-INV-5 || echo FAIL-INV-5
```

注意：`.claude/harness/*` 是 gitignored，runtime 寫入 telemetry / grade /
triage / state 不影響 INV-5；KD#6 invariant 的「working tree」明確排除
gitignored 子樹。

#### Helper 抽出（YAGNI — 暫不拆）

worktree + trap 設定模板與 `plugins/baransu/scripts/bridge-replay.sh` 結構
相同。若日後共用次數變多，可抽 `plugins/baransu/scripts/harness-worktree.sh`
helper；本 task 不抽（YAGNI），保持兩處 inline；任何修改要保持兩處一致
（mktemp 路徑 pattern、trap handler、cleanup 順序）。

> **本範圍：** Stage 4.1（renderer call）、Stage 4.2（push-gate call）、
> Stage 4.3（worktree isolation）契約已透過 harness-followup
> TASK-enforcement-01/02/03 + TASK-skills-triage-04 接好；SKILL.md 不再
> 自寫 enforcement 邏輯。**尚未接入：** cron-driven auto-fix loop dispatcher
> （逐 `triage.jsonl` row 套用上面的 4.1 → 4.2 sub-flow）；在它落地前，
> `/triage` 寫完 `triage.jsonl` 即 exit。

---

## Stage 4 完成回報（Traditional Chinese）

After triage.jsonl is written (and Stage 4 is, for now, a no-op
stub), print a 繁中 summary block to stdout:

```
分流完成：產生 N 個 cluster；above-threshold M 個（已派 investigator）；trend K 個（未派 investigator）。
auto-fix sub-flow 待 TASK-skills-triage-02/03/04 接上後啟動。
```

Where:
- `N` = total cluster rows appended to `triage.jsonl` this run.
- `M` = clusters with `severity_aggregate ≥ 0.5` (investigator was
  dispatched; evidence_bundle attached).
- `K` = clusters with `severity_aggregate < 0.5` (`escalate: false`,
  trend section only).

Then exit 0. The 繁中 block is the canonical user-facing artefact;
downstream auto-fix (when extenders land) reads `triage.jsonl`
directly, not stdout.

---

## Investigator 派發契約（summary）

| 項目 | 內容 |
|---|---|
| Subagent type | `investigator` (`plugins/baransu/agents/investigator-agent.md`) |
| Dispatch tool | Claude Code `Agent` tool, `subagent_type="investigator"` |
| Prompt structure | `cluster_id` + `member_session_ids` list + relevant spec / code paths |
| Return shape | `evidence_bundle` = `{root_cause_guess, citations[], confidence}` (§7 of `_shared/grade-triage-schema.md`) |
| Read-only invariant | INT-5: pre-run vs post-run `git status --porcelain` byte-identical (see Stage 2) |
| Violation handling | INT-5b: dispatcher intercepts OR agent self-rejects → cluster's `evidence_bundle` is **not** trusted; caller surfaces error |

---

## Constraints (recap)

- **No scoring** — `/grade` owns per-row scoring; `/triage` only
  aggregates `quality == "poor"` rows into cluster severity.
- **No direct code edits** — `/triage` core never modifies repo
  source. Auto-fix sub-flow (Stage 4 extenders) delegates to `/dev`
  inside an isolated worktree.
- **No telemetry mutation** — `/triage` only reads `telemetry.jsonl`.
  The auto-fix sub-flow (in extenders) is the only writer, and it
  writes from inside the worktree against the merge-into-existing-row
  contract.
- **No LLM judge** — cluster severity is deterministic; same inputs
  → byte-identical `triage.jsonl` rows.
- **Investigator is read-only** — zero git ops, zero file writes
  (KD#1 / INT-5).
- **All user-visible output in Traditional Chinese (繁體中文).**
  English appears only in this SKILL.md body, code paths, and JSON
  field names.

---

## References

- Implementation: `plugins/baransu/scripts/triage-cluster.py`
  (clustering + 5-dim severity computation; reads `grade.jsonl` +
  `telemetry.jsonl`, writes `triage.jsonl` cluster rows with initial
  `escalate: false`).
- Investigator subagent: `plugins/baransu/agents/investigator-agent.md`
  (perspective class, read-only — zero git ops, zero file writes;
  returns `evidence_bundle` with `root_cause_guess` + `citations[]` +
  `confidence`).
- Authoritative schema: `plugins/baransu/skills/_shared/grade-triage-schema.md`
  (5 dim names, equal-weight bootstrap, `triage.jsonl` 8-field row
  schema §6, `evidence_bundle` sub-schema §7, `escalate` enum 3 values
  §4).
- Upstream: `/grade` writes `.claude/harness/grade.jsonl`;
  `/triage` consumes `quality == "poor"` rows from there.
- Stage 4 wired contracts (harness-followup analyze):
  - TASK-enforcement-01 — `plugins/baransu/scripts/push-gate.sh`
    (denylist + preflight + attempt cap + daily quota; single source of
    truth for the 5-black push gates and `escalate=<enum>` stdout).
  - TASK-enforcement-02 — `plugins/baransu/scripts/render-auto-fix-prompt.py`
    (deterministic prompt renderer; locked-order escape / truncate /
    marker-forgery defences for S-F5).
  - TASK-enforcement-03 — Stage 4.1 / Stage 4.2 SKILL.md call-contracts
    pointing at the two scripts above (this section).
  - TASK-skills-triage-04 — Stage 4.3 `mktemp` + `git worktree add` +
    `trap` worktree isolation (KD#6).
