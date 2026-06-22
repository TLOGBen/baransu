---
name: analyze
description: Use When task scope spans ≥2 interdependent modules and context rot is
  real. Do Build a goal→requirement→design→test→task spec under .claude/analyze/,
  then hand off to /execute. Trigger On '/analyze', '分析需求', '展開規格'. Not for single-file
  or single-layer changes with no cross-module dependency (use /think or implement
  directly); not for deciding whether a task is worth doing (/think Evaluation Mode).
  繁體中文輸出。
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

# analyze — define done before execution

The canonical failure mode of large-task execution is context rot: the model generates while it plans, loses the original intent across auto-compacts and session resets, and produces a system that matches neither the goal nor the requirements. The fix is to define completion first — write goal, requirements, design, tests, and tasks in that order, each layer anchored to the one above — then hand the spec to a fresh execution session.

This skill does not execute code. It produces five spec documents that an execute skill (or a fresh session) consumes. The separation matters: definition and execution carry different failure modes and should never share the same context.

The body below is English (agent-facing). All user-visible output is in **Traditional Chinese (繁體中文)**.

---

## Outcome Contract

- **Outcome**: A five-layer spec (goal → requirement → design → test → task) exists for the stated goal, ready for /execute handoff.
- **Done when**: `.claude/analyze/{date}-{slug}/` contains `goal.md`, `requirement.md`, `design.md`, `test.md`, and at least one `task-{group}.md`, and the Stage 6 cross-layer review round (3 subagents + one auto-correct round) has completed.
- **Evidence**: The generated file list shown at Stage 7 handoff with full paths; Stage 6 findings and the auto-corrections applied to the design / test / task layers.
- **Output**: Spec directory `.claude/analyze/{YYYY-MM-DD}-{slug}/` holding the five spec documents.
- **Automation**: ultracode=assist, loop=assisted（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）

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
.claude/analyze/{YYYY-MM-DD}-{slug}/
```

Use today's date from the `currentDate` context. Confirm the path to the user in one line before writing.

Then resolve the directory-existence failure path explicitly — never silently overwrite. If `.claude/analyze/{date}-{slug}/` already exists (the same-day, same-goal-slug rerun case), then call `authorization PAUSE` once to pick among three branches before any file is written; otherwise (directory absent) create it and continue:

```
question: "目錄 .claude/analyze/{date}-{slug}/ 已存在，怎麼處理？"
header:   "目錄衝突"
options:
  1. label: "resume 既有 spec"
     description: "沿用現有目錄與已寫檔案，只補齊或更新缺漏的層，不刪除既有內容。"
  2. label: "覆寫重建"
     description: "僅刪除計算出的 spec 目錄 .claude/analyze/{date}-{slug}/ 內容後從 Stage 1 重新生成五層 spec；刪除範圍嚴格限定在這唯一一個路徑。"
  3. label: "改用 -2 後綴另建目錄"
     description: "改寫到 .claude/analyze/{date}-{slug}-2/，保留原目錄不動（已存在 -2 則續加 -3、-4…）。"
```

If the user picks option 2 (覆寫重建), apply a scoped path-guard before deleting anything: resolve the intended delete target and compute the canonical spec dir as `{repo_root}/.claude/analyze/{date}-{slug}/`, where `{repo_root}` comes from `git rev-parse --show-toplevel`. **If** the resolved delete target is not exactly that computed spec dir — i.e. the resolved path does not string-equal the computed spec dir, OR it contains any `..` segment, OR it does not lie under `{repo_root}` — **then** abort the overwrite entirely and fall back to the option-3 `-N`-suffixed branch (write to `.claude/analyze/{date}-{slug}-2/`, then `-3`, `-4`… ) instead of deleting. Only when the resolved target string-equals the computed spec dir may the directory contents be deleted. This pins the only irreversible deletion to one verifiable path so a single dropdown click can never remove anything outside the computed spec subdirectory.

---

## Stage 1 — Goal layer → `goal.md`

Write `goal.md`. Fill every section — do not leave template placeholders.

```markdown
# Goal

## 目標（Goal）
{一句話：完成後的世界和現在有什麼不同}

## 驗收標準（Criteria）
{可觀察的條件清單；Agent 可用這個清單判斷任務是否完成}
- [ ] {criterion 1}
- [ ] {criterion 2}
- [ ] {criterion 3}

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
{關鍵使用者流程；每條對應哪個 Criteria}

| 場景 | 起點 | 終點 | 對應 Criteria |
|------|------|------|--------------|
| {scenario} | {start} | {end} | {criterion ref} |

## 整合測試策略
{跨層邊界的驗證；哪些服務或元件需要實際啟動}

| 測試目標 | 涉及層 | 關鍵驗證點 |
|---------|--------|-----------|
| {target} | {layers} | {assertion} |

## 關鍵邊界條件
{哪些邊界條件必須有測試覆蓋；連結到對應需求}

- {edge case — REQ-XXX}
- {edge case — REQ-XXX}
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

Cap at 8 group files. If work exceeds 8 groups, add `wave.md` that divides groups into Wave 1 / Wave 2 with explicit dependency notes between waves.

Before writing task files, note which groups must complete before another can start. Capture this as the `前置群組` field at the top of each file.

### Task file template

```markdown
# Tasks: {group name}
**前置群組**：{names of groups that must finish first, or 無}

## TASK-{group}-01: {task title}

**需求追溯**：REQ-XXX
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

---

## Stage 6 — Cross-layer subagent review

Spawn 3 Codex subagents in parallel, each in a clean context. Pass each agent: the spec_dir path, its required file list (below), and its specific review question. Each agent reads its required files independently via Read tool — do not pass all spec content inline.

> In an ultracode session, this stage's 3-way review may be dispatched to Workflow parallel-research primitives instead; the returned data shape is unchanged.
> When loop-driven, the loop-mode default is assisted: if unresolved findings remain after auto-correct, report back to the driver rather than adjudicating on your own.

**Agent 1 — task ↔ test alignment**

Required files: `task-*.md`, `test.md`

Review question: 「task-*.md 的每個 task 是否都有 test.md 裡對應的測試覆蓋錨點？task 產生的邊界條件（例如空值、並發、超時）是否在 test.md 的邊界條件清單中被覆蓋？有沒有 task 產出了一個功能，但 test.md 裡找不到驗證它的策略？」

**Agent 2 — test ↔ design alignment**

Required files: `test.md`, `design.md`

Review question: 「test.md 的整合測試策略是否對應到 design.md 架構圖中的跨層邊界？test.md 列出的關鍵邊界條件，design.md 有沒有對應的錯誤處理策略？E2E 測試流程能不能在 design.md 的操作流程圖上走通？」

**Agent 3 — design ↔ requirement ↔ goal alignment**

Required files: `design.md`, `requirement.md`, `goal.md`

Review question: 「design.md 的架構和資料流是否能支撐 requirement.md 的所有情境（Given-When-Then）？requirement.md 的每條需求是否都能追溯到 goal.md 的 Criteria？有沒有 Criteria 在 requirement.md 裡沒有任何需求對應？」

### Subagent-failure path

If any of the 3 review subagents returns empty findings, errors out, or does not complete, then re-dispatch that single agent once. If it fails again, skip that agent's lane and record in the Stage 7 handoff output the line 「Stage 6 第N位審查員未完成，該層交叉審查略過」 (substituting the agent's number for N) — so the Done-when review round is never silently reported as complete.

### After receiving findings

Auto-correct the spec files to address findings. One round only. Changes allowed: fix broken requirement references, add missing test cases, add missing data flow entries, correct mermaid diagrams that contradict the text.

Changes not allowed during auto-correct: modify `goal.md` or `requirement.md` semantics (those represent user intent; changing them requires user confirmation).

After the single auto-correct round, classify each still-open finding as either wording-only or structural, where structural means any of: a broken REQ reference, a task-produced feature with no test-coverage anchor in test.md, or a cross-layer contradiction. Pause for user confirmation if-and-only-if at least one structural finding remains:

「spec 驗收後仍有未解問題，需要你確認：
[摘要問題，條列]
請說明如何處理，或直接修改對應的 spec 檔案。」

---

## Stage 7 — Handoff

List all generated files with their paths. Then call `authorization PAUSE`:

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

**Option 2 — 直接交接 execute（完全授權）.** Find the execute skill and pass the spec directory path. Execute autonomously without asking the user for further confirmation.

**Option 3 — 手動決定.**

「spec 已完成，路徑：`.claude/analyze/{date}-{slug}/`

下一步選擇：
1. 在新 session 中開始依 task-*.md 逐一執行（建議：每個 task 獨立 session）
2. 呼叫你的 execute skill 並以上述路徑作為輸入」

---

## Constraints

- Do not write production code, scaffolding, or config files during Stages 1-6. The only output is the five spec documents.
- Do not call `/review` from within Stages 1-6. Cross-layer subagents answer alignment questions ("are these two layers consistent?"), not per-layer quality questions ("what's wrong with this layer?"). These are different questions. Stage 7 may offer /review as a handoff option — that is a post-spec quality check, not an in-spec alignment check.
- Auto-correction is one round. No silent looping.
- On a same-day same-slug directory collision (Stage 0.C), never silently overwrite: branch via the ask the user directly, record the authorization decision, and stop until the user answers among resume / overwrite-rebuild / new -N-suffixed directory before writing any spec file. The overwrite-rebuild branch may delete only the computed spec dir `{repo_root}/.claude/analyze/{date}-{slug}/`; if the resolved delete target does not string-equal that path (or contains `..`, or falls outside `{repo_root}` from `git rev-parse --show-toplevel`), abort the deletion and fall back to the `-N`-suffixed branch instead.
- `goal.md` and `requirement.md` are user-intent layers. Do not modify their semantics during auto-correct. Only design / test / task layers are auto-correctable.
- Never invent requirement numbers. Every `REQ-XXX` reference in task files must have a matching entry in `requirement.md`.
- All user-visible output is Traditional Chinese (繁體中文). English appears only in this SKILL.md body, in code identifiers, file paths, and diagram labels the task itself uses.
