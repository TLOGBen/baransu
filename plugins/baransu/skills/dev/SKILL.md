---
name: dev
description: Gate-enforced TDD executor for small tasks. Receives a concrete task (described directly or handed off from /think), builds a TaskCreate checklist upfront, then executes Red→Green with hard gates before invoking /baransu:review. Cosmetic-only changes (comments, dead imports, renames, formatting) skip Red/Green and go straight to review. Use when direction is known and scope fits one session. User-facing output in Traditional Chinese (繁體中文).
---

# dev — gate-enforced TDD for small tasks

The failure mode this skill prevents: a developer knows what to build, starts coding, skips the test because "this one is small", and ships something that breaks an edge case they didn't anticipate. The gate is what makes TDD enforceable rather than advisory.

This skill does not deliberate. It executes. Direction comes from the user's description or from a /think-approved handoff summary. If the direction is unclear, use /think first.

The body below is English (agent-facing). All user-visible output is in **Traditional Chinese (繁體中文)**.

---

## Stage 0 — Receive task and classify

Accept the task from one of two sources:
- **Standalone**: user describes the task directly in the invocation
- **/think handoff**: /think's Stage G handoff summary is the input

Extract one sentence describing what will be true when the task is done. This becomes the task goal.

**Classify: TDD or cosmetic**

Cosmetic = the change has no semantic impact on runtime behavior: comment edits, dead import removal, identifier renames with no behavior change, pure formatting. When uncertain, treat as TDD.

Do not ask the user — classify based on the task description alone.

---

## Stage 1 — Build task list upfront

Create all tasks before executing any. This makes the completion criteria visible from the start.

**TDD path** — call TaskCreate for each:
- TASK-01: 撰寫紅燈測試
- TASK-02: 確認紅燈（預期失敗）
- TASK-03: 撰寫綠燈實作
- TASK-04: 確認綠燈通過

**Cosmetic path** — call TaskCreate for each:
- TASK-01: 實作變更
- TASK-02: 送 /review

Confirm the task list to the user in one line (繁中) before proceeding.

---

## Stage 2 — Execute: TDD path

### TASK-01 — 撰寫紅燈測試

Write a test that specifies the new behavior described in the task goal. The test must target new behavior only — do not write a test for something that already works.

Mark TASK-01 complete.

### TASK-02 — 確認紅燈 gate

Run the project's existing test command.

**Gate logic:**

| Result | Action |
|---|---|
| Test fails | Red confirmed. Mark TASK-02 complete. Proceed to TASK-03. |
| Test passes | Stop. Report: 「紅燈測試通過了，代表這個測試驗的是既有行為，不是新行為。請修改測試後重試。」Do not proceed to TASK-03. |
| Compile error | Stop. The test itself may be malformed. Report: 「紅燈階段出現編譯錯誤，請先修正測試語法再繼續。」Fix the test and restart from TASK-01. Does not count as a Green retry. |

### TASK-03 — 撰寫綠燈實作

Write the minimum implementation to make the failing test pass. Do not add more than the test requires.

Mark TASK-03 complete.

### TASK-04 — 確認綠燈 gate

Run the project's existing test command.

**Gate logic:**

| Result | Action |
|---|---|
| Tests pass, no regression | Green confirmed. Mark TASK-04 complete. Proceed to Stage 4. |
| Test fails (1st attempt) | Auto-retry: revise the implementation without stopping or asking the user. Run again. |
| Test fails (2nd attempt) | Two consecutive failures. Invoke `/baransu:think` automatically. Pass context: original task goal + the two test failure summaries (not full stack traces) + the red test code. After /think completes: mark TASK-03 in-progress, rewrite implementation (TASK-03), then run TASK-04 once (two-attempt counter resets for this resumed round). If this gate run fails, stop completely. Report: 「/think 對焦後仍無法通過測試，建議重新評估任務範圍或設計。」Do not invoke /think again. |
| Compile error | Fix the compile error and re-run. Does **not** count as a retry attempt — only test runner failures count toward the two-attempt limit. |

---

## Stage 3 — Execute: cosmetic path

### TASK-01 — 實作變更

Apply the cosmetic change directly. No test writing, no gate verification.

Mark TASK-01 complete.

---

## Stage 4 — Invoke /baransu:review

Call `/baransu:review` with:
- **Review goal**: the task goal sentence from Stage 0
- **Claim checklist**: each task in the task list and its completion status (all tasks are complete on a success path)

If the cosmetic path was taken, mark TASK-02 complete after `/review` returns.

**Only invoke /review if work completed successfully** (TDD Green gate passed, or cosmetic change applied). If the session ended on the failure path (Green failed after /think re-alignment), do not invoke /review — there is nothing to review.

---

## Constraints

- Never skip the Red gate. Even when the test "obviously" fails, run it and confirm.
- Never modify the test during the Green phase. The test is the spec; implementation must satisfy it as written.
- Cosmetic classification is final once made. Do not re-classify mid-execution.
- The /think invocation on double Green failure is automatic — do not ask the user first.
- The /think-assisted resume rewrites the implementation (TASK-03) and gets one more gate run (TASK-04); the two-attempt counter resets for this round. If the gate run fails, stop completely; no further auto-/think invocations.
- All user-visible output is Traditional Chinese (繁體中文). English appears only in this SKILL.md body, code identifiers, and file paths.
