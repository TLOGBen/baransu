---
name: analyze
description: Builds a goal→requirement→design→test→task spec under .codex/analyze/,
  then hands off to /execute. Use when task scope spans ≥2 interdependent modules
  and context rot is real. Trigger On '/analyze', '分析需求', '展開規格'. Not for single-file
  or single-layer changes with no cross-module dependency (use /think or implement
  directly); not for deciding whether a task is worth doing (/think Evaluation Mode).
  繁體中文輸出。
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

# analyze — define done before execution

- Define completion first: write goal, requirements, design, tests, and tasks in that order, each layer anchored to the one above, then hand the spec to a fresh execution session.
- This skill produces the five spec documents only — it never executes code.
- Definition and execution should never share the same context.
- The body below is English (agent-facing); all user-visible output is in **Traditional Chinese (繁體中文)**.

---

## Outcome Contract

- **Outcome**: A five-layer spec (goal → requirement → design → test → task) exists for the stated goal, ready for /execute handoff.
- **Done when**: `.codex/analyze/{date}-{slug}/` contains `goal.md`, `requirement.md`, `design.md`, `test.md`, and at least one `task-{group}.md`, and the Stage 6 cross-layer review round (3 subagents + one auto-correct round) has completed.
- **Evidence**: The `ls` output of the spec dir captured in the Stage 7 declaring turn, plus a clean template-placeholder scan; Stage 6 findings and the auto-corrections applied to the design / test / task layers.
- **Output**: Spec directory `.codex/analyze/{YYYY-MM-DD}-{slug}/` holding the five spec documents.
- **Automation**: ultracode=assist, loop=assisted（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）

PAUSE classification for non-interactive drivers: `references/loop-pauses.md` — read it alongside `../_shared/loop-contract.md` when driven by /loop, cron, or Workflow, or hosted as a subagent.

## Constraints

- Do not write production code, scaffolding, or config files during Stages 1-6. The only output is the five spec documents.
- Do not call `/review` from within Stages 1-6. Cross-layer subagents answer alignment questions ("are these two layers consistent?"), not per-layer quality questions ("what's wrong with this layer?"). These are different questions. The sole exception is the test-quality checks explicitly embedded in Agent 1's Stage 6 review question (reachability / assertion validity / redundancy) - those are part of Agent 1's mandate, not an invitation to general per-layer critique. Stage 7 may offer /review as a handoff option — that is a post-spec quality check, not an in-spec alignment check.
- Auto-correction is one round. No silent looping.
- On a same-day same-slug directory collision (Stage 0.C), never silently overwrite: branch via the direct user question (record the authorization decision; stop until the user answers) among resume / overwrite-rebuild / new -N-suffixed directory before writing any spec file. The overwrite-rebuild branch may delete only the computed spec dir `{repo_root}/.codex/analyze/{date}-{slug}/`; if the resolved delete target does not string-equal that path (or contains `..`, or falls outside `{repo_root}` from `git rev-parse --show-toplevel`), abort the deletion and fall back to the `-N`-suffixed branch instead.
- `goal.md` and `requirement.md` are user-intent layers. Do not modify their semantics during auto-correct. Only design / test / task layers are auto-correctable.
- Never invent requirement numbers. Every `REQ-XXX` reference in task files must have a matching entry in `requirement.md`.
- Never invent Criteria numbers. Every `C{n}` reference in `test.md` must have a matching entry in `goal.md`.
- All user-visible output is Traditional Chinese (繁體中文). English appears only in this SKILL.md body, in code identifiers, file paths, and diagram labels the task itself uses.

## Stage 0 — Lightweight alignment + scope gate

Two steps before any file is written.

### Design.md soft-read

Before Step A, check for a DESIGN.md at the project root:
1. Run `git rev-parse --show-toplevel`. If it fails, skip silently.
2. If `{root}/DESIGN.md` exists, read it into context and output one line in 繁中:
   「已載入 DESIGN.md，視覺規格已參考」
3. If absent, skip silently. This check is non-blocking and does not affect any gate.

### A. Get a one-sentence goal

Ask the user (繁中): 「請用一句話描述本次目標，以及預計會動到的主要模組或範圍。」

This sentence becomes the seed for `goal.md`. If the user passes a /think-approved plan or a longer description, extract the core sentence and confirm it in one line before proceeding.

### B. Scope gate

Reject if the task is clearly small:
- Single-file change with no cross-module impact
- Changes that affect only one layer and one area, with no other layer depending on the result

Rejection (繁中): 「這個任務的規模適合直接執行或走 /think；/analyze 是為中大型、跨模組任務設計的。建議：[具體替代方案]。」

On borderline cases, proceed — err toward running /analyze rather than rejecting a task that turns out larger than expected.

### C. Derive slug and directory

Slug: lowercase, hyphens for spaces, ASCII only, max 30 characters, from the goal sentence.

All spec files share one directory:
```
.codex/analyze/{YYYY-MM-DD}-{slug}/
```

Use today's date from the `currentDate` context. Confirm the path to the user in one line before writing.

Then resolve the directory-existence failure path explicitly — never silently overwrite. If `.codex/analyze/{date}-{slug}/` already exists (the same-day, same-goal-slug rerun case), then call `authorization PAUSE` once to pick among three branches before any file is written; otherwise (directory absent) create it and continue:

```
question: "目錄 .codex/analyze/{date}-{slug}/ 已存在，怎麼處理？"
header:   "目錄衝突"
options:
  1. label: "resume 既有 spec 【推薦】"
     description: "沿用現有目錄與已寫檔案，只補齊或更新缺漏的層，不刪除既有內容。"
  2. label: "覆寫重建"
     description: "僅刪除計算出的 spec 目錄 .codex/analyze/{date}-{slug}/ 內容後從 Stage 1 重新生成五層 spec；刪除範圍嚴格限定在這唯一一個路徑。"
  3. label: "改用 -2 後綴另建目錄"
     description: "改寫到 .codex/analyze/{date}-{slug}-2/，保留原目錄不動（已存在 -2 則續加 -3、-4…）。"
```

If the user picks option 2 (覆寫重建), apply a scoped path-guard before deleting anything: resolve the intended delete target and compute the canonical spec dir as `{repo_root}/.codex/analyze/{date}-{slug}/`, where `{repo_root}` comes from `git rev-parse --show-toplevel`. If that command fails (the project is not a git repo), the overwrite-rebuild branch is unavailable — do not delete anything; take the option-3 `-N`-suffixed branch automatically and tell the user 「非 git repo，無法安全定界刪除範圍，改用 -N 後綴目錄」. **If** the resolved delete target is not exactly that computed spec dir — i.e. the resolved path does not string-equal the computed spec dir, OR it contains any `..` segment, OR it does not lie under `{repo_root}` — **then** abort the overwrite entirely and fall back to the option-3 `-N`-suffixed branch (write to `.codex/analyze/{date}-{slug}-2/`, then `-3`, `-4`… ) instead of deleting. Only when the resolved target string-equals the computed spec dir may the directory contents be deleted. This pins the only irreversible deletion to one verifiable path so a single dropdown click can never remove anything outside the computed spec subdirectory.

---

## Stage 1 — Goal layer → `goal.md`

Write `goal.md`. Fill every section — do not leave template placeholders.

```markdown
# Goal

## 目標（Goal）
{一句話：完成後的世界和現在有什麼不同}

## 驗收標準（Criteria）
{可觀察的條件清單；Agent 可用這個清單判斷任務是否完成。每條冠 `C{n}` 編號，供 test.md 逐列回指}
- [ ] C1: {criterion 1}
- [ ] C2: {criterion 2}
- [ ] C3: {criterion 3}

## 範圍（Scope）

### 包含（In scope）
- {item}

### 不包含（Out of scope）
- {item — and why it's excluded}
```

After writing, show the `goal.md` content to the user. Then call `authorization PAUSE`:

```
question: "goal.md 確認"
header:   "Stage 1 確認"
options:
  1. label: "確認，繼續 【推薦】"
     description: "goal 和驗收標準沒問題，繼續到 Stage 2。"
  2. label: "需要調整"
     description: "說明哪個部分要修改，我會更新 goal.md 後重新確認。"
```

Wait for confirmation before proceeding to Stage 2.

---

## Stage 2 — Requirements layer → `requirement.md`

Derive requirements from `goal.md`. Each requirement is a discrete condition the system must satisfy. One goal typically yields 2–5 requirements.

```markdown
# Requirements

## REQ-001: {requirement title}

**描述**：{one sentence — what the system must do}

### Scenarios

**Scenario 1: {scenario name}**
- **Given** {precondition}
- **When** {action}
- **Then** {expected outcome}
- **And** {additional outcome, if needed}

**Scenario 2: {scenario name}**
- **Given** ...
- **When** ...
- **Then** ...

---

## REQ-002: {requirement title}

**描述**：...

### Scenarios
...
```

Number sequentially: `REQ-001`, `REQ-002`, … These numbers are referenced by task files; do not change them after writing.

---

## Stage 3 — Design layer → `design.md`

Produce technical design. Apply this include/skip decision rule per diagram — each maps to a concrete trigger condition:

| Diagram | Include when |
|---------|--------------|
| 系統架構 | Always include. |
| 整體操作流程 | Always include. |
| 畫面關聯 | Only if the task touches ≥2 frontend pages. |
| API Sequence | Only for tasks with ≥1 new/changed backend endpoint — one diagram per endpoint. |
| 整體資料流 | Only if the task spans ≥2 layers (e.g., frontend + backend, or service + DB). |
| 資料模型 | Only if a new entity or schema migration is introduced. |
| 錯誤處理策略 | Always include. |

```markdown
# Design

## 系統架構
{說明主要元件與其職責；文字說明或 Mermaid 圖均可}

## 整體操作流程
{使用者操作 → 系統回應 → 狀態轉換}
\`\`\`mermaid
flowchart TD
  A[使用者動作] --> B[系統處理] --> C[狀態更新]
\`\`\`

## 畫面關聯（前端任務適用）
\`\`\`mermaid
flowchart LR
  PageA --> PageB --> PageC
\`\`\`

## API Sequence（每支 API 一張，後端任務適用）
\`\`\`mermaid
sequenceDiagram
  participant Client
  participant Server
  participant DB
  Client->>Server: POST /endpoint
  Server->>DB: query
  DB-->>Server: result
  Server-->>Client: response
\`\`\`

## 整體資料流
\`\`\`mermaid
flowchart TD
  Frontend --> API --> Service --> DB
\`\`\`

## 資料模型
{主要實體及其欄位；用表格或 Mermaid ER 圖}

## 錯誤處理策略
{各層如何處理、傳遞、最終向使用者呈現錯誤}
```

---

## Stage 4 — Test layer → `test.md`

Define the testing strategy that verifies the implementation satisfies requirements. This layer participates in the subagent review chain: Agent 1 (Stage 6) checks that task boundaries produce testable seams and that test.md's edge cases cover the conditions task-*.md creates.

```markdown
# Test Strategy

## E2E 測試策略
{每條 = 主路徑分支盤點中的一個分支；每條標明真實入口（已驗證存在）與所斷言的具體可觀察值，並回指一個 goal Criteria 編號 C{n}}

| 場景（主路徑分支） | 真實入口（端點或方法名＋file:line，已 grep/read 驗證存在） | 具體斷言（具名 ReturnCode／狀態轉換／回調觸發或不觸發） | 對應 Criteria |
|------|------|------|--------------|
| {branch} | {verified entry point + file:line} | {named assertion} | C{n} |

## 整合測試策略
{跨層邊界的驗證；哪些服務或元件需要實際啟動。關鍵驗證點必須是具名可斷言的觀察值，「有回應／全綠」這類同義反覆一律不收}

| 測試目標 | 涉及層 | 關鍵驗證點（具名斷言，禁同義反覆） |
|---------|--------|-----------|
| {target} | {layers} | {named assertion — 具名值，非「有回應」} |

## 關鍵邊界條件
{每條邊界條件雙向追溯：連到它驗證的 REQ-XXX，並連到產生此風險的 task（TASK-{group}-NN）；孤懸於任何 task 風險之外的邊界條件應刪除。task 編號於 Stage 5 回填——撰寫本節時 task 尚未編號，該欄先留佔位}

- {edge case — REQ-XXX — 由 TASK-{group}-NN 製造的風險}
- {edge case — REQ-XXX — 由 TASK-{group}-NN 製造的風險}

## 冗餘與首要交付掃描
{逐條掃上面三張表，列出並刪除重複或不對應任何 task 風險的多餘測試；並確認本次首要交付物本身有一條測試把「達成」釘死（收斂類重構需一條殘留複本掃描列，例如 grep 存量呼叫點＝模板一檔）。逐 task 對應檢查所需的 task 編號於 Stage 5 回填}
- {kept/removed — reason}
```

---

## Stage 5 — Task layer → `task-{group}.md`

> **Re-read checkpoint**: Before beginning task decomposition, re-read this SKILL.md §Stage 5 (task sizing rule, group naming, wave.md cap). The sizing and dependency rules are the most judgment-heavy part of /analyze and are vulnerable to attention decay after Stages 1–4.

Decompose the work into tasks. Start from the innermost reusable layer and work outward. Each group becomes a separate file.

### Task sizing rule

One task = one session can complete it independently. A task passes if:
- It does not require coordination with another task-group to proceed
- Its implementation does not depend on output from another task not yet complete
- Its changes concentrate in one module layer (not simultaneously spanning service + dao + controller + frontend)

If a natural task fails the above, split it.

### Group naming examples

**Backend**: `shared` (utils, enums, consts) → `data` (models, migrations, DAOs) → `service` (business logic) → `api` (endpoints, middleware) → `integration` (wiring, config)

**Frontend**: `shared` (components, utils) → `api` (clients, mappers) → `feature` (page logic, state)

**Full-stack**: use both, innermost backend first.

Cap at 8 group files. If work exceeds 8 groups, add `wave.md` that divides groups into Wave 1 / Wave 2 with explicit dependency notes between waves. `wave.md` is presentational only — /execute never reads it; the `前置群組` field is the sole authoritative dependency channel, so every inter-wave dependency noted in `wave.md` MUST also appear as `前置群組` entries in the affected group files.

Before writing task files, note which groups must complete before another can start. Capture this as the `前置群組` field at the top of each file.

### Task file template

```markdown
# Tasks: {group name}
**前置群組**：{names of groups that must finish first, or 無}

## TASK-{group}-01: {task title}

**需求追溯**：REQ-XXX
**測試重量建議**：full | riding（純接線/轉發時；選填）
**目標**：{one sentence — what will exist or work when this task is done}
**驗收標準**：
- [ ] {observable criterion}
- [ ] {observable criterion}

### 步驟

#### {Step group 1 — e.g., 建立資料結構}
- [ ] {concrete action}
- [ ] {concrete action}

#### {Step group 2 — e.g., 實作邏輯}
- [ ] {concrete action}
- [ ] {concrete action}

---

## TASK-{group}-02: {task title}
...
```

Every task must have at least one requirement reference (`REQ-XXX`). Do not invent requirement numbers not defined in `requirement.md`.

The optional 「測試重量建議」 line lets the spec author mark wiring-only tasks (thin pass-through forwarders, module registration, re-exports, config plumbing) as `riding` at decomposition time, when that knowledge is freshest. It is advisory input only — /execute's §4b test-weight tier rule keeps final decision authority (when in doubt, full). Omit the line when unsure.

### Backfill test.md task references

After all task files are written — and before dispatching the Stage 6 review — reopen `test.md` and replace the placeholder task back-references left in Stage 4's 「關鍵邊界條件」 and 「冗餘與首要交付掃描」 sections with the actual `TASK-{group}-NN` numbers now defined in the task files. Any edge case that cannot be traced to a risk produced by a real task is deleted, per Stage 4's existing rule. This backfill is the sanctioned in-process write point for task references in `test.md`, so Agent 1's Stage 6 back-reference audit checks a chain the flow itself completed rather than relying on auto-correct to repair it.

---

## Stage 6 — Cross-layer subagent review

Spawn 3 Codex subagents in parallel, each in a clean context. Pass each agent: the spec_dir path, its required file list (below), and its specific review question. Each agent reads its required files independently via Read tool — do not pass all spec content inline. Each agent must return a verdict per review question from 「對齊 / 未對齊 / 未檢查」, and each finding as {file, section anchor, one-line claim, quoted evidence}. An empty finding list under explicit 「對齊」 verdicts is a legal, completed return — do not invent findings to fill the list.

> In an ultracode session, this stage's 3-way review may be dispatched to Workflow parallel-research primitives instead; the returned data shape is unchanged.
> When loop-driven, the loop-mode default is assisted: if unresolved findings remain after auto-correct, report back to the driver rather than adjudicating on your own.

**Agent 1 — task ↔ test alignment**

Required files: `task-*.md`, `test.md`, `requirement.md`, `goal.md`

Review question: 「task-*.md 的每個 task 是否都有 test.md 裡對應的測試覆蓋錨點？task 產生的邊界條件（例如空值、並發、超時）是否在 test.md 的邊界條件清單中被覆蓋，且每條邊界條件都回指到產生該風險的 task？有沒有 task 產出了一個功能，但 test.md 裡找不到驗證它的策略？requirement.md 的每個 Given-When-Then 情境，是否都能在 test.md 找到對應的覆蓋錨點（E2E 列、整合測試列、或邊界條件項）？沒有錨點的情境即為 finding。再檢查測試品質三點，任一不過即為 finding：(1) 可達性與語意正確性——每條 E2E 列的真實入口（端點或方法）是否經 grep/read 驗證存在，且斷言指向該操作自身的真實結果、未張冠李戴到另一個互斥操作上；主路徑分支盤點是否完整——每個互斥的主路徑情境各佔一列、未被折疊，凡同一條件在兩側產生不同結果者兩側各算一列——缺任一分支或誤標即為 finding；(2) 斷言有效性——關鍵驗證點是否為具名可斷言值（具名 ReturnCode／狀態轉換／回調觸發或不觸發），凡「有回應／回傳成功／全綠」這類同義反覆即為 finding；(3) 冗餘與首要交付——是否有重複或不對應任何 task 風險的多餘測試，且本次首要交付物是否有一條測試把『達成』釘死。最後檢查 goal 準則錨定，任一不過即為 finding：goal.md 的每條 C{n} 是否至少有一列 test.md 錨點回指？test.md 每個 C{n} 回指是否都存在於 goal.md（不得杜撰編號）？字面含持久化語意的準則（例如「重啟後仍在」）是否有一列 reopen 形狀的測試（關閉後重開／process 重入），而非僅結構性推論？」

The goal-criteria clause mirrors /execute's final-review goal-criteria cross-check (final-review-agent §1b) so C{n} gaps die at spec time, not at execute time.

**Agent 2 — test ↔ design alignment**

Required files: `test.md`, `design.md`

Review question: 「test.md 的整合測試策略是否對應到 design.md 架構圖中的跨層邊界？test.md 列出的關鍵邊界條件，design.md 有沒有對應的錯誤處理策略？E2E 測試流程能不能在 design.md 的操作流程圖上走通？」

**Agent 3 — design ↔ requirement ↔ goal alignment**

Required files: `design.md`, `requirement.md`, `goal.md`

Review question: 「design.md 的架構和資料流是否能支撐 requirement.md 的所有情境（Given-When-Then）？requirement.md 的每條需求是否都能追溯到 goal.md 的 Criteria？有沒有 Criteria 在 requirement.md 裡沒有任何需求對應？」

### Subagent-failure path

If any of the 3 review subagents returns without per-question verdicts, errors out, or does not complete, then re-dispatch that single agent once. If it fails again, skip that agent's lane and record in the Stage 7 handoff output the line 「Stage 6 第N位審查員未完成，該層交叉審查略過」 (substituting the agent's number for N) — so the Done-when review round is never silently reported as complete.

A 「未檢查」 verdict is the same incompleteness in a softer coat: a lane that returns 「未檢查」 for any of its review questions is treated as incomplete — apply the same single re-dispatch to that agent. If any question is still 「未檢查」 after the re-dispatch, record the same Stage 7 skip line extended to name the unchecked question(s): 「Stage 6 第N位審查員未完成，該層交叉審查略過（未檢查：[問題摘要]）」. A lane that answered 未檢查 is never silently treated as reviewed.

### After receiving findings

A finding is a claim, not a mandate: before editing for a finding, Read the file at its cited anchor and confirm the claim matches the current spec state; if it does not, skip that finding and log it — never force-apply. Auto-correct the spec files to address the confirmed findings. One round only. Changes allowed: fix broken requirement references, add missing test cases, add missing data flow entries, correct mermaid diagrams that contradict the text.
Report skipped findings in the Stage 7 handoff output with the line 「已略過 N 項與 spec 現況不符的發現：[清單]」 (omit when N = 0).

Changes not allowed during auto-correct: modify `goal.md` or `requirement.md` semantics (those represent user intent; changing them requires user confirmation).

After the single auto-correct round, the author session does not certify its own corrections as resolved. For each lane whose findings were corrected, re-dispatch that lane's agent once in a clean context (same dispatch protocol as above), passing the corrected files, the original finding, and one question: 「此發現是否已解決？」. Only a verifier-returned resolved counts; a failed re-dispatch or an ambiguous answer leaves the finding open — an unverifiable resolution counts as unresolved.

Classify each still-open finding as either wording-only or structural, where structural means any of: a broken REQ reference, a task-produced feature with no test-coverage anchor in test.md, or a cross-layer contradiction. Pause for user confirmation if-and-only-if at least one structural finding remains:

「spec 驗收後仍有未解問題，需要你確認：
[摘要問題，條列]
請說明如何處理，或直接修改對應的 spec 檔案。」

If no structural finding remains but one or more wording-only findings are still open, do not pause; record them in the Stage 7 handoff output with the line 「spec 驗收後仍有 N 項純措辭層級未解發現（不阻擋交接）：[清單]」, so no still-open finding is silently dropped.

---

## Stage 7 — Handoff

Run `ls` on the spec dir in this turn and list the generated files exactly as that output returns them — never from memory. Confirm the five layers are present and grep the spec files for leftover template braces (e.g. `{criterion`, `{item}`). Each check has an explicit failure path. **If** the `ls` output lacks any of the five required spec files (`goal.md`, `requirement.md`, `design.md`, `test.md`, at least one `task-{group}.md`), **then** do not call the handoff `authorization PAUSE` — return to the stage that produces the missing layer, regenerate it, and re-run this Stage 7 check once. **If** the grep finds leftover template braces, **then** repair is allowed in `design.md` / `test.md` / `task-*.md` only (one pass, then re-grep); **if** a placeholder sits in `goal.md` or `requirement.md`, do not auto-repair — those are user-intent layers per Constraints — pause and show the user the offending line for confirmation before declaring. Only after both checks pass (or the user has confirmed the goal/requirement placeholder), call `authorization PAUSE`:

```
question: "spec 完成。接下來怎麼做？"
header:   "下一步"
options:
  1. label: "送 /review 再決定 【推薦】"
     description: "用 /baransu:review 對完成的 spec 文件做整體品質複審，review 完成後再決定執行方式。"
  2. label: "直接交接 execute（完全授權）"
     description: "找出 execute skill 並傳入 spec 目錄路徑，自主執行，不再過問使用者。"
  3. label: "手動決定"
     description: "列出 spec 路徑，讓使用者自行決定下一步（新 session 逐一執行，或呼叫 execute）。"
```

**Option 1 — 送 /review 再決定.** Invoke `/baransu:review` on the generated spec files. Review goal: 「確認五層 spec 的品質與一致性，找出任何可能影響執行的遺漏或矛盾」. After review, the user naturally loops back to this gate.

**Option 2 — 直接交接 execute（完全授權）.** Inline same-session execution contradicts this skill's never-share-context premise, so gate it on spec size: **if** the spec dir contains ≥2 `task-*.md` group files or a `wave.md`, **then** stop at the handoff and tell the user to run /execute in a fresh session instead of continuing in the loaded context (see /think Stage E, Mechanism necessity), outputting: 「spec 規模跨多個 task 群組，請在新 session 執行：/baransu:execute .codex/analyze/{date}-{slug}/」. Only a single-group spec — exactly one `task-*.md` and no `wave.md` — may continue inline: find the execute skill and pass the spec directory path, executing autonomously without asking the user for further confirmation.

**Option 3 — 手動決定.**

「spec 已完成，路徑：`.codex/analyze/{date}-{slug}/`

下一步選擇：
1. 在新 session 中開始依 task-*.md 逐一執行（建議：每個 task 獨立 session）
2. 呼叫你的 execute skill 並以上述路徑作為輸入」
