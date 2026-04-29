# state.json Schema (authoritative)

> **Scope**: every consumer of `.claude/harness/state.json` (the `/triage`
> 自動修補子流程 running inside an isolated worktree, plus `/grade` for
> observation writes) MUST treat this document as the single source of
> truth for the state record shape. Field names, types, writer attribution,
> partition ownership, daily reset semantics and the daily push quota = 5
> hard cap are locked here.
>
> **Format**: a single JSON object (NOT JSON Lines).
> Path: `.claude/harness/state.json` (gitignored under `.claude/harness/`).
>
> Traces: REQ-004 (auto-fix five safety boundaries — daily quota=5),
> REQ-004 Scenario 4 (daily push hard cap), Hard Constraint KD#5,
> INT-7 (daily counter reset across days), INV-6.

---

## 1. Top-level fields (authoritative)

The following 6 fields are authoritative. Fields 1–4 are required by
TASK-shared-04 acceptance criteria; fields 5–6 are owned by
TASK-skills-grade-02 and live alongside the original four (no separate
section). The schema is **open to additive extension** — see §5 for
further forward-compat slots.

| 欄位 | 型別 | 寫入者 | 寫入時機 | 範例值 |
|------|------|--------|----------|--------|
| `daily_push_count` | int (≥ 0) | `/triage` 自動修補子流程 (in isolated worktree) | 每次 push 成功後 +1；reset 時設為 0 | `0` |
| `daily_push_date` | string (ISO date `YYYY-MM-DD`, 本機時區) | `/triage` 自動修補子流程 (in isolated worktree) | 初始化時 / reset 時寫入今日 | `"2026-04-29"` |
| `last_grade_run_at` | string (ISO 8601 datetime) **or** null | `/grade` skill | `/grade` 跑完後寫入；尚未跑過時為 `null` | `"2026-04-29T03:00:00Z"` |
| `last_triage_run_at` | string (ISO 8601 datetime) **or** null | `/triage` 自動修補子流程 (in isolated worktree) | `/triage` 跑完後寫入；尚未跑過時為 `null` | `"2026-04-29T03:05:00Z"` |
| `tune_review_due_since` | string (ISO 8601 datetime) **or** null | `/grade` skill | `/grade` 累積 ≥ 50 條 `terminal_state == "completed"` row 後寫入；user 跑 `/grade --tune-acknowledged` 後清回 `null`。未觸發前為 `null`。 | `"2026-04-29T03:00:00Z"` |
| `cumulative_completed_count` | int (≥ 0) **or** null | `/grade` skill | `/grade` 跑完更新；用來判斷是否觸發 `tune_review_due` 旗標。`/grade` 從未跑過時為 `null`。 | `0` |

> 「最後一次跑時間」兩欄為觀測用（design.md 流程 1 SeqDiag 的觀察點），
> 不影響 daily quota 判斷邏輯。
>
> `tune_review_due_since` 與 `cumulative_completed_count` 由 TASK-skills-grade-02
> 升級為 authoritative：CAS 寫入規則為「僅當原值為 `null` 才寫入新時間」，
> 避免覆寫先前 due since（見 task ctx Constraints）。`--tune-acknowledged`
> 是唯一允許將 `tune_review_due_since` 清回 `null` 的路徑（KD#4 禁止 auto-reset）。

---

## 2. Daily quota = 5 (KD#5 hard cap)

`daily_push_count` 的硬上限為 **daily quota = 5**。此數值由 Hard Constraint
KD#5（auto-fix 五條安全邊界其中一條）鎖定，不可修改。

判斷規則：

```
if daily_push_count >= 5:
    abort push
    mark cluster row as "daily_quota_exceeded"
```

對應場景：REQ-004 Scenario 4「當日已 push 5 次 auto-fix → 第 6 個 cluster
push abort」。

---

## 3. Daily reset semantics (INT-7)

當 auto-fix 讀 state.json 時，**先 reset 再判斷 quota**：

```
今日 = current_date (本機 ISO date, YYYY-MM-DD)
       —— 測試環境可由 BARANSU_HARNESS_FAKE_NOW 環境變數覆寫 (per INT-7)

read state.json
if state.daily_push_date ≠ today:
    state.daily_push_count = 0
    state.daily_push_date = today
    atomic_write(state)
# 此時再判斷 quota
if state.daily_push_count >= 5:
    abort push, mark daily_quota_exceeded
```

文字版說明：當 state.json 內 `daily_push_date` 欄位的值不等於今日（系統本機
ISO date，或測試環境下的 `BARANSU_HARNESS_FAKE_NOW` 覆寫值）時，counter
重設為 0，`daily_push_date` 更新為今日，再寫回（atomic）。reset 完才進入
daily quota = 5 的硬閘判斷。

對應 INT-7：「daily counter 隔日 reset」整合測試的設計層落腳。

---

## 4. Partition contract + read-merge-write atomic

state.json 是 **3-writer 共享單檔**（不是單 writer）。為避免 writer 互相
覆寫對方的欄位，schema 採 **explicit partition 隔離 + read-merge-write
atomic** 契約 —— 沒有 flock，partition 規則本身就保證寫入不衝突。

### 4.1 Partition table

每個欄位精確屬於一個 partition；partition 定義了哪一個 writer 可以寫
該欄位。Writer 跨 partition 寫禁止。

| Partition | Writer | Owns (3 fields) |
|-----------|--------|-----------------|
| `grade` | `/grade` skill (`grade-collector.py` + `--tune-acknowledged`) | `last_grade_run_at`, `cumulative_completed_count`, `tune_review_due_since` |
| `triage` | `/triage` 自動修補子流程 (in isolated worktree, via `push-gate.sh`) | `daily_push_count`, `daily_push_date`, `last_triage_run_at` |

- **grade owns**: `last_grade_run_at`, `cumulative_completed_count`,
  `tune_review_due_since`
- **triage owns**: `daily_push_count`, `daily_push_date`, `last_triage_run_at`

> Writer attribution canonical name (grep anchor): /triage 自動修補子流程
> (in isolated worktree). 此字面在 cron / runbook / KD#1 read-only invariant
> 文件中作為唯一指涉名 —— investigator-agent (read-only) 不再被誤標為
> 寫入者，與 KD#1 對齊。

### 4.2 Cross-partition write prohibition

**跨 partition 寫禁止**：

- `/grade` 的 writer (`grade-collector.py` 與 `--tune-acknowledged` code path)
  **僅可** mutate grade-partition 三欄；嚴禁碰 triage-partition 任一欄。
- `/triage` 自動修補子流程 (in isolated worktree) 的 writer (`push-gate.sh`)
  **僅可** mutate triage-partition 三欄；嚴禁碰 grade-partition 任一欄。
- 任何違反 cross-partition 規則的程式碼路徑由 `INV-7` grep lint
  （`plugins/baransu/scripts/check-invariants.sh`）抓出，cron / CI
  exit non-zero 拒絕。

### 4.3 Read-merge-write atomic contract

每個 writer **必須** 走以下四步流程，使對方 partition 的欄位 byte-for-byte
不動（含未列名於 §1 的下游擴充欄位 / 未來 schema 欄位）：

```
read-merge-write(my_partition_updates):
    1. read full state.json into memory (含對方 partition + unknown keys)
    2. modify ONLY own-partition keys (依 my_partition_updates)
    3. serialize merged state to .claude/harness/state.json.tmp
    4. atomic rename(2): .claude/harness/state.json.tmp -> .claude/harness/state.json
```

說明：

- **read full → modify own → temp + rename**：步驟 1 必須讀「整個」
  state.json 而非只讀自己 partition 的欄位；步驟 2 嚴禁碰 own-partition
  以外任何 key（含對方 partition 欄位、未知欄位、forward-compat 槽）。
- 同一目錄下的 `rename(2)` 在 POSIX 為 atomic，可保證讀者要嘛看到舊檔、
  要嘛看到新檔，不會看到半寫狀態。
- 沒有 `flock` —— partition 隔離本身保證 grade writer 與 triage writer
  之間不會互相覆寫；交錯任意順序跑亦保留所有欄位（REQ-005 Scenario 4
  100 次交錯 invocation 驗證）。
- state.json 屬 harness-owned scratch space（`.gitignore` 覆蓋的
  `.claude/harness/` 內），`/triage` 自動修補子流程在 isolated worktree
  內對其 mutation 不違反 KD#6「auto-fix 永不 touch 主 repo working tree」。

### 4.4 Forward-compat under read-merge-write

read-merge-write 步驟 1 讀整檔保留對方 partition 之外，亦保留 **未知欄位**
byte-identical（B11 / B17 邊界）：未列名於 §1 的下游擴充欄位（例如未來
TASK 加入的 `last_bridge_run_at`）由 partition guard **僅限 own-partition
寫入面**；讀取與 merge 不限制 unknown keys。Writer 不得 reject 或 drop
未知欄位。

---

## 5. Forward-compat（下游欄位擴充預告）

design.md 在資料模型節列出的 state.json 權威 schema 共 6 欄位，§1 已將
全部 6 欄位列為 authoritative：

- **TASK-shared-04** 鎖定前 4 欄位（`daily_push_count`、`daily_push_date`、
  `last_grade_run_at`、`last_triage_run_at`）。
- **TASK-skills-grade-02** 將 `tune_review_due_since`、
  `cumulative_completed_count` 從原本的 forward-compat 註記升級為 §1 中的
  authoritative 欄位（owner 為 `/grade` skill）。

> schema 採 open-to-extension 設計：未列名於 §1 的欄位仍視為下游擴充槽，
> 不違反本 schema；本節保留供更下游任務（若有）登記其欄位 owner。

---

## 6. Example state.json

初始檔內容（auto-fix 從未跑過時的 baseline；`tune_review_due_since` 與
`cumulative_completed_count` 在尚未觸發前為 `null`）：

```json
{"daily_push_count": 0, "daily_push_date": "2026-04-29", "last_grade_run_at": null, "last_triage_run_at": null, "tune_review_due_since": null, "cumulative_completed_count": null}
```

`/grade` 跑過一次但累積尚未跨閾值（`cumulative_completed_count` 已寫入，
`tune_review_due_since` 仍為 `null`）：

```json
{"daily_push_count": 0, "daily_push_date": "2026-04-29", "last_grade_run_at": "2026-04-29T03:00:00Z", "last_triage_run_at": null, "tune_review_due_since": null, "cumulative_completed_count": 12}
```

`/grade` 累積跨 ≥ 50 條 completed row 後（`tune_review_due_since` 已寫入
ISO 時間，等待 user 手動 `/grade --tune-acknowledged`）：

```json
{"daily_push_count": 0, "daily_push_date": "2026-04-29", "last_grade_run_at": "2026-04-29T03:00:00Z", "last_triage_run_at": null, "tune_review_due_since": "2026-04-29T03:00:00Z", "cumulative_completed_count": 50}
```

當日已用滿 daily quota = 5（後續 push 全 abort）：

```json
{"daily_push_count": 5, "daily_push_date": "2026-04-29", "last_grade_run_at": "2026-04-29T03:00:00Z", "last_triage_run_at": "2026-04-29T03:05:00Z", "tune_review_due_since": null, "cumulative_completed_count": 12}
```

---

## 7. jq query 範例

讀 daily push counter：

```
jq '.daily_push_count' .claude/harness/state.json
```

判斷是否需要 reset（shell 整合範例）：

```
TODAY="$(date +%Y-%m-%d)"
STATE_DATE="$(jq -r '.daily_push_date' .claude/harness/state.json)"
if [ "$STATE_DATE" != "$TODAY" ]; then
  # trigger reset path
  ...
fi
```

驗證初始檔合法性（CI / invariants 檢查）：

```
jq -e '.daily_push_count == 0 and .daily_push_date != null' \
   .claude/harness/state.json
```
