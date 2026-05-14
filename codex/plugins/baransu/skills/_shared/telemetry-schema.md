# telemetry.jsonl Schema (authoritative)

> **Scope**: every consumer of `.claude/harness/telemetry.jsonl` (the
> `/grade`, `/triage`, `/bridge` skills, `harness-reaper` and the auto-fix
> investigator subagent) MUST treat this document as the single source of
> truth for the telemetry record shape. Field names, enum values, writer
> attribution and write-time ordering are locked here.
>
> **Format**: append-only JSON Lines. One JSON object per row, one row per
> baransu skill invocation. Path: `.claude/harness/telemetry.jsonl`
> (gitignored under `.claude/harness/`).
>
> Traces: REQ-001 (Telemetry capture: two hooks + 7-field schema),
> REQ-006 Scenario 3 (7 fields present), Hard Constraint #3, INV-3.

---

## 1. Top-level fields (7, locked)

The number, names and ordering authority of these fields are part of the
spec contract. Adding, renaming, or removing any of them invalidates the
schema.

| 欄位 | 型別 | 寫入者 | 寫入時機 | 範例值 |
|------|------|--------|----------|--------|
| `session_id` | string (non-empty; `s-YYYY-MM-DD-NNN` recommended) | `UserPromptSubmit` hook | 在 user 送出 prompt 時，append 新 row 之前產生 | `"s-2026-04-28-001"` |
| `terminal_state` | enum: `in_progress` / `completed` / `aborted` / `interrupted` | initial: `UserPromptSubmit`; transitions: `PostToolUse` (→ `completed`), `Stop` hook (→ `aborted`), `harness-reaper` (→ `interrupted`) | initial 寫於 row 建立時；終態於 final tool 後 / session end / 24h reaper 巡檢時轉移 | `"completed"` |
| `prompt_text` | string (已過 5 條 secret-pattern redaction filter) | `UserPromptSubmit` hook | row 建立時與 `session_id` 同步寫入 | `"重構 auth 模組"` |
| `skill_outcome` | object: `{skill_name: string, final_state: string, exit_code: integer}` | `PostToolUse` hook | skill 的 final tool 執行完成後 merge into existing row | `{"skill_name":"think","final_state":"approved","exit_code":0}` |
| `commit_hash` | string（40 hex；`git rev-parse HEAD` 結果，session 結束時的 HEAD） | `PostToolUse` hook | 與 `skill_outcome` 同一次 merge 寫入 | `"3a525e544f0c8b1e9d2a7f0b1c4d6e8f0a1b2c3d"` |
| `diff_summary_redacted` | array of `{path: string, plus: integer, minus: integer}`（**只含摘要，不得含 diff 字面內容**；敏感路徑整條跳過） | `PostToolUse` hook | 與 `skill_outcome` 同一次 merge 寫入 | `[{"path":"src/main.py","plus":12,"minus":3}]` |
| `attempt_history` | array of `{cluster_id: string, run_at: ISO-8601 string, result: enum "pass"/"fail"}` | initial `[]` 由 `UserPromptSubmit` 寫；之後 append element 由 auto-fix（在 isolated worktree 中，由 `/triage` 觸發）寫入 | row 建立時為空 list；每次 auto-fix attempt 收尾後 append 一筆 | `[{"cluster_id":"cl-001","run_at":"2026-04-28T00:05:00Z","result":"fail"}]` |

> `terminal_state` 的初值 `in_progress` 不在三個 final enum 中，但在實作上是必經
> 的暫態；下游消費者（例如 `/grade`）用 `terminal_state == "completed"` 篩選有效 row。

---

## 2. Terminal state enum (locked: 3 final values)

```
in_progress  ──(PostToolUse)──▶  completed   (final, immutable)
in_progress  ──(Stop hook)─────▶  aborted    (final, immutable)
in_progress  ──(reaper 24h)────▶  interrupted (final, immutable)
```

- `completed` — skill 跑完 final tool，PostToolUse 寫齊 `skill_outcome` /
  `commit_hash` / `diff_summary_redacted` 後升態。`/grade` 只看這個值。
- `aborted` — session 結束（含 ctrl-c）時 row 仍 `in_progress`，由 Stop hook
  以 fallback 形式轉。`skill_outcome` 必含「中斷」標示，不留空。
- `interrupted` — `harness-reaper` script（由 `/grade` Stage 0 呼叫）巡檢
  超過 24h 仍 `in_progress` 的 row，視為 hook 漏寫並轉成 `interrupted`。

### Monotonic CAS rule (locked)

任何 writer 寫 `terminal_state` 之前 MUST 先 read 當前值，**只在當前 ==
`in_progress` 才允許更新**。三個 final 值寫定後不可再轉移、不可往左退。
這條 CAS guard 是 4 個 writer 並發下的不變量。

---

## 3. Write-time ordering (時序)

```
t0  user 送 prompt
     └─▶ UserPromptSubmit hook
          ├─ generate session_id
          ├─ redact prompt_text (5 secret patterns)
          └─ append new row:
             { session_id, prompt_text, terminal_state:"in_progress",
               attempt_history:[],
               skill_outcome:null, commit_hash:null, diff_summary_redacted:null }

t1  ...skill 執行中（一或多個 tool call）...

t2a (happy path)
     PostToolUse hook (final tool 後)
       ├─ locate row by session_id
       ├─ compute diff_summary_redacted（敏感路徑跳過、不含字面）
       ├─ git rev-parse HEAD → commit_hash
       ├─ fill skill_outcome
       └─ CAS: terminal_state in_progress → completed

t2b (ctrl-c / abnormal exit)
     Stop hook
       ├─ locate row by session_id
       ├─ skill_outcome 標「中斷」（不留空）
       └─ CAS: terminal_state in_progress → aborted

t3  (later, ≥24h)
     harness-reaper （由 /grade Stage 0 呼叫）
       └─ CAS: terminal_state in_progress → interrupted

t4  (auto-fix attempt，獨立路徑)
     /triage 觸發 isolated worktree run
       └─ append element 進 attempt_history（用 session_id+cluster_id locate row）
```

---

## 4. `attempt_history` sub-schema

```jsonc
{
  "cluster_id": "cl-001",         // string; triage cluster 識別碼，join key
  "run_at":     "2026-04-28T00:05:00Z", // ISO-8601 UTC timestamp
  "result":     "fail"            // enum: "pass" | "fail"
}
```

合約：
- `attempt_history` 是 auto-fix 對既有 row **唯一允許的 mutation**（其餘
  欄位的 mutation 只能是 hook 在 `in_progress` → 終態的單次轉移）。
- auto-fix 以 cluster_id 作為 join key 反向更新對應 row；不是新增 event row。
- `triage.jsonl` 的 `attempt_count` 是這份 attempt_history 的衍生 aggregate
  （read-only view），權威來源在 telemetry。
- `auto-fix` 以外的元件**不得寫 telemetry**。

---

## 5. Telemetry mutation contract — Writer 名單（4 個 + 1 reaper）

| Writer | 觸發 | 可動欄位 | CAS guard |
|--------|------|----------|-----------|
| `UserPromptSubmit` hook | user 送出 prompt | `session_id` / `prompt_text`(redacted) / `terminal_state="in_progress"`(初值) / `attempt_history=[]`(初值) | n/a（純 append） |
| `PostToolUse` hook | skill 完成 final tool | `skill_outcome` / `commit_hash` / `diff_summary_redacted`(redacted) / `terminal_state` 升 `completed` | 只在 `terminal_state == in_progress` 才升 `completed` |
| `Stop` hook | session end 時 row 仍 `in_progress` | `skill_outcome`（中斷標示）/ `terminal_state` 升 `aborted` | 只在 `terminal_state == in_progress` 才升 `aborted` |
| auto-fix（isolated worktree，由 `/triage` 觸發） | 每次 auto-fix attempt 收尾 | `attempt_history`：append element（不可 modify 已有 element） | n/a（只 append element） |
| `harness-reaper` script（由 `/grade` Stage 0 呼叫） | 巡檢 ≥ 24h 仍 `in_progress` 的 row | `terminal_state` 升 `interrupted` | 只在 `terminal_state == in_progress` 才升 `interrupted` |

任何不在此名單中的元件**不得寫 telemetry**。

---

## 6. Concurrency & atomicity (locked)

- 5 個 writer 對同一檔可能並發。所有寫入路徑 MUST 持 `flock(2)` 鎖
  `.claude/harness/.telemetry.lock`。
- 任何 row 內的欄位變更（hook merge、auto-fix append element）MUST 走 atomic：
  `read 全檔 → modify in-memory → 寫到臨時檔 → atomic rename` 取代原檔。
- 純 append（`UserPromptSubmit` 建新 row）也持 lock 保險。
- 鎖檔位置 `.claude/harness/.telemetry.lock` 與 telemetry 同層；連同 telemetry
  整個 `.claude/harness/` 目錄須在 `.gitignore` 內。

---

## 7. Redaction rules (locked)

- `prompt_text`：經 5 條 secret-pattern redaction filter，命中時改寫為
  `<REDACTED:<category>>`（例如 `<REDACTED:gitlab_token>`）。
- `diff_summary_redacted`：
  - 只允許 `{path, plus, minus}` 三欄；**不得含 diff 字面內容**。
  - 敏感路徑整條跳過（**不出現在 list**），含 `.env*` / `*secret*` /
    `*credential*` / `*.pem` / `*.key` 等樣式。

---

## 8. 完整範例 row（jq-parseable）

```json
{"session_id":"s-2026-04-28-001","terminal_state":"completed","prompt_text":"重構 auth 模組","skill_outcome":{"skill_name":"think","final_state":"approved","exit_code":0},"commit_hash":"3a525e544f0c8b1e9d2a7f0b1c4d6e8f0a1b2c3d","diff_summary_redacted":[{"path":"src/auth/login.py","plus":12,"minus":3},{"path":"src/auth/session.py","plus":4,"minus":1}],"attempt_history":[{"cluster_id":"cl-001","run_at":"2026-04-28T00:05:00Z","result":"fail"},{"cluster_id":"cl-001","run_at":"2026-04-28T00:11:00Z","result":"pass"}]}
```

> 該 row 必為單行 JSONL；上面換行只是版面。`jq .` 可解析。

---

## 9. jq query 範例

最新一條 row 的 keys（INV-3 grep / 7 欄齊全驗證）：
```sh
tail -1 .claude/harness/telemetry.jsonl | jq 'keys'
# expected output（7 個）:
# ["attempt_history","commit_hash","diff_summary_redacted","prompt_text",
#  "session_id","skill_outcome","terminal_state"]
```

`/grade` 取 completed rows：
```sh
jq -c 'select(.terminal_state == "completed")' .claude/harness/telemetry.jsonl
```

按 cluster_id 統計 attempt 次數（`triage.jsonl` 的 `attempt_count` 衍生來源）：
```sh
jq -c '.attempt_history[] | {cluster_id, result}' .claude/harness/telemetry.jsonl \
  | jq -s 'group_by(.cluster_id) | map({cluster_id: .[0].cluster_id, attempt_count: length})'
```

抽 7 個必要欄位是否齊全的快速 sanity check：
```sh
tail -1 .claude/harness/telemetry.jsonl \
  | jq 'has("session_id") and has("terminal_state") and has("prompt_text")
        and has("skill_outcome") and has("commit_hash")
        and has("diff_summary_redacted") and has("attempt_history")'
# expected: true
```

---

## 10. 變更管理

修改本檔（欄位數、欄位名、enum、writer 對應、CAS 規則、append-only / 並發
保護任一條）= 破壞 spec 不變量，須走完整 `/baransu:analyze` →
`/baransu:execute` 流程，並同步更新 `/grade`、`/triage`、`/bridge`、
`harness-reaper` 與兩個 hook 的實作。
