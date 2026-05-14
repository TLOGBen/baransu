# grade.jsonl + triage.jsonl Schema (authoritative)

> **Scope**: `/grade` writes `.claude/harness/grade.jsonl`; `/triage`
> reads `grade.jsonl` + `telemetry.jsonl` and writes
> `.claude/harness/triage.jsonl`. Field names, the 5 baransu-native rubric
> dimensions, the equal-weight bootstrap rule, the tune-trigger threshold,
> and the two enum sets (`quality`, `escalate`) are locked here.
>
> **Format**: append-only JSON Lines. One JSON object per row. Both files
> live under `.claude/harness/` (gitignored, 同 telemetry.jsonl 同層)。
>
> Traces: REQ-002（Grade）/ REQ-003（Triage）/ REQ-006 Scenario 4
> （rubric weight bootstrap）/ Hard Constraint KD#4 / INV-4。

---

## 1. 5 baransu-native rubric dimensions (locked)

下列 5 個維度是 `/grade` 與 `/triage` 共用的 deterministic rubric 維度。
名稱、數量、語意來源欄位（與 telemetry.jsonl 對齊）皆鎖定。新增、改名或
減少任一維度都會破壞 spec 不變量。

| 維度（locked name） | 0–1 浮點分數含義 | telemetry 來源欄位 | deterministic 推導規則 |
|---|---|---|---|
| `outcome_quality` | 結果品質：完成且綠燈高分 | `skill_outcome.exit_code` + `skill_outcome.final_state` | `terminal_state == "completed"` 且 `exit_code == 0` 且 `final_state` 不含 `failed`/`aborted`/`error` 子字串 → 1.0；否則按 `exit_code` 與 `final_state` 標記分檔降階（rubric script 內表查） |
| `iteration_velocity` | 迭代速度：少回合即高速 | `attempt_history`（同 cluster_id）+ `commit_hash` | 該 session 對應 cluster 的 attempt 次數 N → score = `1 / N`（N≥1，無 cluster 則視為 N=1） |
| `scope_blast` | 變動爆量：動到的檔案數 + 路徑風險 | `diff_summary_redacted` | `score = 1 - min(1, files_touched / 10) * 0.7 - risk_path_hit * 0.3`（敏感樣式如 `*.lock` / `migrations/*` 命中即 `risk_path_hit=1`，否則 0） |
| `human_override_rate` | 人工 override 率：低為高分 | `skill_outcome.final_state`（含 override 標記） | `final_state` 含 `override`/`manual`/`bypass` 子字串 → 0.0；否則 1.0 |
| `failure_recurrence` | 失敗重現：同 cluster 越多次累計失敗越低分 | `attempt_history` 中與此 row `cluster_id` 同 key 的近 7 日累計 `result == "fail"` 次數 K | `score = max(0, 1 - K * 0.2)`（K=0 → 1.0；K≥5 → 0.0） |

> 0–1 浮點精度 ≤ 1e-6（INT-10 對應）。所有公式均 deterministic：相同
> telemetry 輸入兩次計算 score hash 必相同，禁含 `now()`/`uuid`/`random`
> /dict 順序依賴等隨機/時間敏感欄位。

### 1.1 5 維欄位名 ↔ telemetry 來源欄位對應表（grep 友善）

```
outcome_quality       ← skill_outcome.exit_code + skill_outcome.final_state
iteration_velocity    ← attempt_history (count) + commit_hash
scope_blast           ← diff_summary_redacted
human_override_rate   ← skill_outcome.final_state (override 標記)
failure_recurrence    ← attempt_history (近 7 日同 cluster_id 失敗累計)
```

---

## 2. Equal-weight bootstrap & tune trigger (locked)

Week-1 bootstrap 規格：5 維每維權重恆為 `1/5`（即 `0.2`），即 **equal weight**。
`/grade` 不寫死權重於 script，而是從 rubric 設定載入；本 schema 鎖定該設定的初值。

```
weights = {
  "outcome_quality":     1/5,   // 0.2
  "iteration_velocity":  1/5,
  "scope_blast":         1/5,
  "human_override_rate": 1/5,
  "failure_recurrence":  1/5
}
aggregate = sum(dims[k] * weights[k] for k in 5)  // = sum(dims) / 5
```

**Tune trigger**：當 `.claude/harness/telemetry.jsonl` 累積 **≥ 50 條**
`terminal_state == "completed"` row 後，`/grade` 跑完當下：

1. stdout 印出 `tune_review_due: true` 訊號（人類可見）。
2. `state.json` 寫入 `tune_review_due_since`（ISO-8601 datetime）；
   `cumulative_completed_count` 同步更新。
3. 直到 user 手動執行 `/grade --tune-acknowledged`，state 才 reset
   `tune_review_due_since` 為 null（INT-11b 對應）。

> 本條 `≥ 50` 是量化條件，不可改成「啟發式」或「人為判斷」。它與 KD#4
> 直接綁定：在累積到 ≥ 50 條前不得 tune 權重；累積後也只 review，不
> 自動 tune。

---

## 3. quality enum (locked: 4 values) + score-band 對應

`grade.jsonl` row 的 `quality` 欄位必為以下 4 值之一，依 `aggregate`
分數區間落點決定（band 邊界鎖定）：

| `quality` enum | `aggregate` 區間 |
|---|---|
| `excellent` | `aggregate ≥ 0.85` |
| `good` | `0.70 ≤ aggregate < 0.85` |
| `acceptable` | `0.50 ≤ aggregate < 0.70` |
| `poor` | `aggregate < 0.50` |

> band 邊界用 `[lo, hi)` 半開區間，避免邊界值兩落。`poor` 是 `/triage`
> 篩選聚類的入口（REQ-002 Scenario 2 + REQ-003 Scenario 1）。

---

## 4. escalate enum (locked: 3 values) + 觸發條件

`triage.jsonl` row 的 `escalate` 欄位必為以下 3 值之一：

| `escalate` enum | 觸發條件 | 後續行為 |
|---|---|---|
| `false` | cluster 的 `severity_aggregate < 0.5`（below threshold；REQ-003 Scenario 3） | 不派 investigator-agent，但仍寫入 triage.jsonl 作 trend section |
| `requires_human` | severity_aggregate ≥ 0.5 且 investigator 給出的 `evidence_bundle.confidence < 0.6`（或 root cause 模糊） | 寫入 triage.jsonl，並由人類接手；不觸發 auto-fix |
| `daily_quota_exceeded` | 當日 auto-fix attempt 已達上限（每日上限由 harness state 控制） | 即使 severity 高也不派 investigator；累積到隔日 quota 重置 |

> 三個值互斥；同一 cluster row 不可同時為兩種狀態。

---

## 5. `grade.jsonl` row schema (5 fields)

每一行對應一條 `terminal_state == "completed"` 的 telemetry row。

| 欄位 | 型別 | 說明 |
|---|---|---|
| `session_id` | string（與 telemetry.jsonl 同 key） | join key；對齊 telemetry 既有 row |
| `dims` | object，5 sub-fields | `{outcome_quality, iteration_velocity, scope_blast, human_override_rate, failure_recurrence}`，每個 0–1 浮點 |
| `aggregate` | float（0–1） | `sum(dims) / 5`（equal weight）；精度 ≤ 1e-6 |
| `quality` | enum: `excellent` / `good` / `acceptable` / `poor` | 由 §3 score-band 決定 |
| `weights` | object，5 sub-fields | 當下計分用的權重快照（bootstrap 階段恆為 1/5）；保留供 tune 後 re-grade 對照 |

> `/grade` 只看 `terminal_state == "completed"` 的 telemetry row；`aborted` /
> `interrupted` / `in_progress` 不進 grade.jsonl（INT-3 對應）。

---

## 6. `triage.jsonl` row schema (8 fields)

每一行對應一個聚類 cluster；每次 `/triage` 跑完可能新增多個 row。

| 欄位 | 型別 | 說明 |
|---|---|---|
| `cluster_id` | string（穩定 ID，例如 `cl-001`） | 與 telemetry.attempt_history.cluster_id 對齊 |
| `member_session_ids` | array of string | 此 cluster 涵蓋的 telemetry session_id 清單 |
| `severity_dims` | object，5 sub-fields | 與 grade dims 同名同結構：`{outcome_quality, iteration_velocity, scope_blast, human_override_rate, failure_recurrence}`，每個 0–1 浮點（severity 維度可由 `/triage` 自行 aggregate，例如 cluster 內 1−avg(dim)） |
| `severity_aggregate` | float（0–1） | `sum(severity_dims) / 5`；高 = 嚴重 |
| `escalate` | enum: `false` / `requires_human` / `daily_quota_exceeded` | 見 §4 |
| `evidence_bundle` | object（見 §7） | investigator 寫入；`escalate == false` 時可為 null |
| `attempt_count` | int（衍生欄位） | 同 cluster_id 跨 run 累計失敗次數；**read-only view，權威來源永遠在 `telemetry.jsonl` 的 `attempt_history`** |

### 6.1 `attempt_count` 權威來源約定（mutation contract）

`triage.jsonl.attempt_count` 是 `telemetry.jsonl.attempt_history` 的衍生
aggregate（read-only view），**不獨立寫入、不獨立更新**。`/triage`
每次跑時即時從 telemetry 重算：

```
attempt_count(cluster_id) =
  count(row.attempt_history[*] in telemetry.jsonl
        where attempt_history[i].cluster_id == cluster_id
          and attempt_history[i].result == "fail")
```

只有 auto-fix（在 isolated worktree、由 `/triage` 觸發）可寫
`telemetry.attempt_history`；`/triage` 本身不寫 telemetry。這條 mutation
contract 與 `telemetry-schema.md` §4 一致。

---

## 7. `evidence_bundle` sub-schema (locked)

由 investigator subagent 寫入 `triage.jsonl` 對應 cluster row。

| 欄位 | 型別 | 說明 |
|---|---|---|
| `root_cause_guess` | string（**一句話**） | investigator 對該 cluster 根因的單句結論 |
| `citations` | array of `{file_path, line_range, excerpt}` | 引用清單；`file_path` 為 repo 內相對路徑，`line_range` 形如 `"42-58"`，`excerpt` 為節錄字串（≤ 200 chars 建議） |
| `confidence` | float（0–1） | investigator 自評信心；< 0.6 觸發 `escalate: requires_human`（見 §4） |

子欄位排序固定（`severity desc, file_path asc, line asc`，與 KD#4 deterministic
invariants 對齊）。investigator 跑完不得做任何 git ops（write / push / branch
ops 為 0；REQ-003 Scenario 2 對應）。

---

## 8. 完整範例 row（皆為 jq-parseable）

### 8.1 `grade.jsonl` 範例 row

```json
{"session_id":"s-2026-04-28-001","dims":{"outcome_quality":0.4,"iteration_velocity":0.5,"scope_blast":0.7,"human_override_rate":1.0,"failure_recurrence":0.6},"aggregate":0.64,"quality":"acceptable","weights":{"outcome_quality":0.2,"iteration_velocity":0.2,"scope_blast":0.2,"human_override_rate":0.2,"failure_recurrence":0.2}}
```

### 8.2 `triage.jsonl` 範例 row

```json
{"cluster_id":"cl-001","member_session_ids":["s-2026-04-28-002","s-2026-04-28-005","s-2026-04-28-009"],"severity_dims":{"outcome_quality":0.8,"iteration_velocity":0.7,"scope_blast":0.6,"human_override_rate":0.5,"failure_recurrence":0.9},"severity_aggregate":0.7,"escalate":"requires_human","evidence_bundle":{"root_cause_guess":"auth session 重新整理時 cluster 在 token refresh 邊界一致地拋 401。","citations":[{"file_path":"src/auth/session.py","line_range":"42-58","excerpt":"if token.expired(): raise Unauthorized()"},{"file_path":"src/auth/login.py","line_range":"110-120","excerpt":"refresh_token() not retried on transient 5xx"}],"confidence":0.55},"attempt_count":4}
```

> 兩條皆為單行 JSONL；上面換行只是版面。`jq .` 可解析。

---

## 9. jq query 範例

抽 grade.jsonl 中所有 `quality == "poor"` 的 row（`/triage` 聚類入口）：
```sh
jq -c 'select(.quality == "poor")' .claude/harness/grade.jsonl
```

驗證 5 維欄位齊全（INV-4 sanity check）：
```sh
tail -1 .claude/harness/grade.jsonl \
  | jq '.dims | has("outcome_quality") and has("iteration_velocity")
        and has("scope_blast") and has("human_override_rate")
        and has("failure_recurrence")'
# expected: true
```

抽 triage.jsonl 中所有需要人工介入的 cluster：
```sh
jq -c 'select(.escalate == "requires_human")' .claude/harness/triage.jsonl
```

從 telemetry 重算 attempt_count（`triage.jsonl.attempt_count` 權威源）：
```sh
jq -c '.attempt_history[] | select(.result == "fail") | .cluster_id' \
   .claude/harness/telemetry.jsonl \
  | sort | uniq -c
```

---

## 10. 變更管理

修改本檔（5 維欄位名、equal-weight 1/5、tune trigger ≥ 50、quality enum
4 值、escalate enum 3 值、evidence_bundle 子 schema、attempt_count
read-only 約定 任一條）= 破壞 spec 不變量，須走完整 `/baransu:analyze` →
`/baransu:execute` 流程，並同步更新 `/grade`、`/triage`、`/bridge`、
`harness-reaper` 與 telemetry-schema.md 的相關段落。
