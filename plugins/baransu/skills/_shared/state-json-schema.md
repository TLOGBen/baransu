# state.json Schema (authoritative)

> **Scope**: every consumer of `.claude/harness/state.json` (the auto-fix
> investigator subagent invoked by `/triage`, plus `/grade` for observation
> writes) MUST treat this document as the single source of truth for the
> state record shape. Field names, types, writer attribution, daily reset
> semantics and the daily push quota = 5 hard cap are locked here.
>
> **Format**: a single JSON object (NOT JSON Lines).
> Path: `.claude/harness/state.json` (gitignored under `.claude/harness/`).
>
> Traces: REQ-004 (auto-fix five safety boundaries — daily quota=5),
> REQ-004 Scenario 4 (daily push hard cap), Hard Constraint KD#5,
> INT-7 (daily counter reset across days), INV-6.

---

## 1. Top-level fields (4, locked for this task)

The following 4 fields are required by TASK-shared-04 acceptance criteria.
The schema is **open to additive extension** — see §5 for forward-compat.

| 欄位 | 型別 | 寫入者 | 寫入時機 | 範例值 |
|------|------|--------|----------|--------|
| `daily_push_count` | int (≥ 0) | auto-fix investigator subagent | 每次 push 成功後 +1；reset 時設為 0 | `0` |
| `daily_push_date` | string (ISO date `YYYY-MM-DD`, 本機時區) | auto-fix investigator subagent | 初始化時 / reset 時寫入今日 | `"2026-04-29"` |
| `last_grade_run_at` | string (ISO 8601 datetime) **or** null | `/grade` skill | `/grade` 跑完後寫入；尚未跑過時為 `null` | `"2026-04-29T03:00:00Z"` |
| `last_triage_run_at` | string (ISO 8601 datetime) **or** null | `/triage` skill | `/triage` 跑完後寫入；尚未跑過時為 `null` | `"2026-04-29T03:05:00Z"` |

> 「最後一次跑時間」兩欄為觀測用（design.md 流程 1 SeqDiag 的觀察點），
> 不影響 daily quota 判斷邏輯。

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

## 4. Atomic write expectation

state.json 屬「單一 JSON object 全量覆寫」型檔案。寫入須為 atomic 以避免
cron 自癒迴圈與 manual 觸發並發毀檔：

```
atomic_write(state):
    write state to .claude/harness/state.json.tmp
    rename .claude/harness/state.json.tmp -> .claude/harness/state.json
```

說明：

- **temp-file + rename** 即可，不需要 flock —— state.json 屬單一 writer
  （auto-fix investigator subagent 在 isolated worktree 內 mutate；`/grade`、
  `/triage` 觀測欄位寫入時機與 auto-fix 不重疊）。
- 同一目錄下的 `rename(2)` 在 POSIX 為 atomic，可保證讀者要嘛看到舊檔、
  要嘛看到新檔，不會看到半寫狀態。
- state.json 屬 harness-owned scratch space（`.gitignore` 覆蓋的
  `.claude/harness/` 內），auto-fix 對其 mutation 不違反 KD#6
  「auto-fix 永不 touch 主 repo working tree」。

---

## 5. Forward-compat（下游欄位擴充預告）

design.md 在資料模型節列出的 state.json 權威 schema 共 6 欄位，本文件鎖
前 4 欄位（task-shared-04 範圍）。後續任務將以**附加欄位**方式擴充：

- **TASK-skills-grade-02** 將加入：
  - `tune_review_due_since`：ISO 8601 datetime / null。`/grade` 累積 ≥ 50 條
    `terminal_state == "completed"` row 後寫入；user 跑
    `/grade --tune-acknowledged` 後清回 null。
  - `cumulative_completed_count`：int。`/grade` 跑完更新；用來判斷是否觸發
    `tune_review_due` 旗標。

> 本 task 範圍**不** redefine 或設定該兩欄位的初值。schema 採 open-to-extension
> 設計：未列名於 §1 的欄位視為下游擴充槽，不違反本 schema。

---

## 6. Example state.json

初始檔內容（auto-fix 從未跑過時的 baseline）：

```json
{"daily_push_count": 0, "daily_push_date": "2026-04-29", "last_grade_run_at": null, "last_triage_run_at": null}
```

`/grade` 跑過一次後（`last_grade_run_at` 已寫入）：

```json
{"daily_push_count": 0, "daily_push_date": "2026-04-29", "last_grade_run_at": "2026-04-29T03:00:00Z", "last_triage_run_at": null}
```

當日已用滿 daily quota = 5（後續 push 全 abort）：

```json
{"daily_push_count": 5, "daily_push_date": "2026-04-29", "last_grade_run_at": "2026-04-29T03:00:00Z", "last_triage_run_at": "2026-04-29T03:05:00Z"}
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
