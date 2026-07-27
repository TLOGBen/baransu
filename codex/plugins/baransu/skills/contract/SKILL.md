---
name: contract
description: 'Writes a one-page work contract (~35 lines) before a medium-sized change:
  goal, assertable criteria, can''t-miss surfaces, verbatim constants. Use before
  implementing a feature that deserves pinned acceptance but not a full /analyze spec.
  Trigger On ''/contract'', ''寫合約'', ''一頁合約'', ''開工合約'', ''pin the criteria''. Not
  for multi-module specs (use /analyze) or post-hoc verification (use /seal). 繁體中文輸出。'
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

# contract — pin acceptance before you build

Criteria written to rejection strength kill whole defect classes before
implementation starts — the contract is the quality lever, not the process
around it. All user-visible output is **Traditional Chinese (繁體中文)**.

## Outcome Contract

- **Outcome**: A one-page CONTRACT.md exists for the stated task — goal, assertable criteria, can't-miss surface inventory, verbatim constants — written to rejection strength per the shared gate rules.
- **Done when**: `CONTRACT.md` (project root, or the path the user names) contains the four sections, every user-facing-text criterion passes the G1 assertability check (exact format or prohibition list — no substring-contains), and the user has confirmed the contract in one round.
- **Evidence**: The written CONTRACT.md plus the per-criterion G1 disposition list shown at confirmation (each criterion marked 可斷言 / 已改寫).
- **Output**: `CONTRACT.md` (~35 lines) in the conversation and on disk; operational messages in Traditional Chinese.
- **Automation**: ultracode=neutral, loop=drivable（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）
- **Telemetry**: on invocation, append one selection record per `../_shared/selection-telemetry.md`.

PAUSE classification for non-interactive drivers: `references/loop-pauses.md`.

## Constraints

- **一頁上限**: One page. Target ~35 lines, hard cap 60. A contract that needs more is a signal the task belongs to `/analyze` — say so and stop instead of writing a long contract.
- **閘則外置**: The gate rules live in `../_shared/contract-gate.md` (G1 assertability, G2 trap promotion, G3 verbatim constants, G4 surface inventory). Read it before writing any criterion; do not restate its rules here or in the contract.
- **只釘 WHAT**: The contract pins WHAT must hold, never HOW to implement. No file-by-file plans, no pseudo-code.
- **先讀碼再寫條文**: Read the relevant code before writing criteria — G2 requires promoting discovered traps into criteria, which is impossible without looking.
- **只寫不驗**: This skill writes the contract only. Implementation follows in the same or next session under `_shared/tdd.md` §7 discipline; verification is `/seal`'s job.
- **現實接觸強制閘**: a 未驗 data-source / schema / contract / permission premise may never be written into criteria as fact (procedure: Step 1).
- **無捆綁停權**: an undetermined premise never exempts its adjacent verifiable criteria from becoming independent assertable criteria (procedure: Step 1).
- **禁止靜默覆寫**: never overwrite an existing CONTRACT.md belonging to a different task (procedure: Step 3).

## Flow

### Step 1 — Ground

Read `../_shared/contract-gate.md`. Then read the code surfaces the task
touches (entry points, the data shapes involved, existing output formats).
Note every trap found (non-dense indexes, encoding quirks, abort semantics) —
each MUST surface as a criterion per G2.

Also note every **premise (前提)** the criteria will rest on that affects data
source / schema / contract / permissions; tag each `已驗` (first-hand: DB query /
actual code at file:line / SA doc) or `未驗`. **現實接觸強制閘 (大膽包 A)**: a
`未驗` premise of that kind may NOT be written into criteria as fact — get ONE
first-hand contact to confirm or refute it, or (contact impossible this run)
escalate it to the user as an explicit assumption via `user-question PAUSE (unclassified)`, never
silently. A prior harness experiment's whole failure was one `未驗`
data-source premise entering the contract as 「領域事實」.

**No bundled suspension**: a `未驗-升級` premise never exempts its ADJACENT
verifiable criteria. When one premise is undetermined (e.g. the amount data
source), every behavior unrelated to it (vendor filtering, date-range
passthrough, permission scope dimensions) still becomes its own independent
assertable criterion with its own pinning test — a criterion bundled under an
unverified premise's shadow is how real filters ship silently broken.

If the task touches NO existing code surface (greenfield — no entry point, no
existing output format to read) → do not silently skip G2: the 可斷言條文
section MUST open with one affirmative line — 「G2：本任務無既有程式面可讀，
查無陷阱；條文僅由需求推導」 — and criteria derive from the requirement text
alone under G1/G3/G4; Steps 2–3 proceed unchanged. Silence is non-compliant.

### Step 2 — Write CONTRACT.md (four sections)

```markdown
# CONTRACT — {task title}

## 目標
{1-3 lines: the observable difference when this is done}

## 前提（Premises）
{each premise the criteria rest on, tagged `已驗`(source cited) / `未驗`; any
data-source/schema/contract/permission premise must be `已驗` per the 現實接觸閘,
or explicitly escalated — never silently assumed}

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
If a CONTRACT.md already exists at the target path: if its content belongs to
the same task, overwrite it on confirmation; if it belongs to a different
task, stop and ask the user to name a new path (e.g. `CONTRACT-{slug}.md`) —
silent overwrite is forbidden.
On confirmation, write the file and output:
「合約已釘死：{path}（{N} 條可斷言條文、{M} 個錯不起表面）。實作時照抄
Verbatim Constants；完工後跑 /baransu:seal 驗收。」

## Not-for boundaries

- Task spans ≥2 interdependent modules or needs a task DAG → `/baransu:analyze`（大頻段全管線）.
- Work is already done and needs verification → `/baransu:seal`.
- The ask is a value judgment (worth doing?) → `/baransu:think` Evaluation Mode.
