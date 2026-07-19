---
name: contract
description: "Writes a one-page work contract (~35 lines) before a medium-sized change: goal, assertable criteria, can't-miss surfaces, verbatim constants. Use before implementing a feature that deserves pinned acceptance but not a full /analyze spec. Trigger On '/contract', '寫合約', '一頁合約', '開工合約', 'pin the criteria'. Not for multi-module specs (use /analyze) or post-hoc verification (use /seal). 繁體中文輸出。"
argument-hint: "<one-sentence task description>"
user-invocable: true
---

# contract — pin acceptance before you build

Validated form: the 2026-07-19 experiment's p-min arm — a 35-line contract plus
one independent seal — matched a full-pipeline champion on behavior (20/20
criteria, 0 introduced med/high) at 22% of the cost. The contract is the
quality lever: criteria written to rejection strength kill whole defect
classes before implementation starts.

This body is English (agent-facing). All user-visible output is
**Traditional Chinese (繁體中文)**.

## Outcome Contract

- **Outcome**: A one-page CONTRACT.md exists for the stated task — goal, assertable criteria, can't-miss surface inventory, verbatim constants — written to rejection strength per the shared gate rules.
- **Done when**: `CONTRACT.md` (project root, or the path the user names) contains the four sections, every user-facing-text criterion passes the G1 assertability check (exact format or prohibition list — no substring-contains), and the user has confirmed the contract in one round.
- **Evidence**: The written CONTRACT.md plus the per-criterion G1 disposition list shown at confirmation (each criterion marked 可斷言 / 已改寫).
- **Output**: `CONTRACT.md` (~35 lines) in the conversation and on disk; operational messages in Traditional Chinese.
- **Automation**: ultracode=neutral, loop=drivable（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）
- **Telemetry**: on invocation, append one selection record per `../_shared/selection-telemetry.md`.

PAUSE classification for non-interactive drivers: `references/loop-pauses.md`.

## Constraints

- One page. Target ~35 lines, hard cap 60. A contract that needs more is a signal the task belongs to `/analyze` — say so and stop instead of writing a long contract.
- The gate rules live in `../_shared/contract-gate.md` (G1 assertability, G2 trap promotion, G3 verbatim constants, G4 surface inventory). Read it before writing any criterion; do not restate its rules here or in the contract.
- The contract pins WHAT must hold, never HOW to implement. No file-by-file plans, no pseudo-code.
- Read the relevant code before writing criteria — G2 requires promoting discovered traps into criteria, which is impossible without looking.
- This skill writes the contract only. Implementation follows in the same or next session under `_shared/tdd.md` §7 discipline; verification is `/seal`'s job.

## Flow

### Step 1 — Ground

Read `../_shared/contract-gate.md`. Then read the code surfaces the task
touches (entry points, the data shapes involved, existing output formats).
Note every trap found (non-dense indexes, encoding quirks, abort semantics) —
each MUST surface as a criterion per G2.

### Step 2 — Write CONTRACT.md (four sections)

```markdown
# CONTRACT — {task title}

## 目標
{1-3 lines: the observable difference when this is done}

## 可斷言條文
{numbered criteria, each assertable per G1; user-facing text criteria give the
EXACT format or a prohibition list; every G2 trap appears here as a
prohibition-style criterion}
- [ ] A1: ...
- [ ] A2: ...

## 錯不起表面（Surface Inventory）
{G4 table: surface → exact format → pinning test name (to be written)}
| 表面 | 格式 | 釘死測試 |
|------|------|----------|

## Verbatim Constants
{G3 fenced block — every regex / format string / magic literal, copy-paste
source of truth}
```

### Step 3 — Confirm (one round)

Show the contract with a per-criterion G1 disposition (可斷言 ✓ / 已改寫自模糊
表述). Ask the user to confirm or amend — one round, in Traditional Chinese.
On confirmation, write the file and output:
「合約已釘死：{path}（{N} 條可斷言條文、{M} 個錯不起表面）。實作時照抄
Verbatim Constants；完工後跑 /baransu:seal 驗收。」

## Not-for boundaries

- Task spans ≥2 interdependent modules or needs a task DAG → `/baransu:analyze`（大頻段全管線）.
- Work is already done and needs verification → `/baransu:seal`.
- The ask is a value judgment (worth doing?) → `/baransu:think` Evaluation Mode.
