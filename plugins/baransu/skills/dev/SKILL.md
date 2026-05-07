---
name: dev
description: >-
  Use When a small task with clear scope arrives directly or via /think handoff and is ready to implement in one session. Do Build a TaskCreate checklist, run hard Red→Green TDD gates, then hand off to /review. Trigger On 「一起處理吧」「直接改」「幫我修」「可以了」, option picks (「選 1」「A - 2」「第一個」), or /think approved-plan handoff. 繁體中文輸出。
---

# dev — gate-enforced TDD for small tasks

The failure mode this skill prevents: a developer knows what to build, starts coding, skips the test because "this one is small", and ships something that breaks an edge case they didn't anticipate. The gate is what makes TDD enforceable rather than advisory.

This skill does not deliberate. It executes. Direction comes from the user's description or from a /think-approved handoff summary. If the direction is unclear, use /think first.

The body below is English (agent-facing). All user-visible output is in **Traditional Chinese (繁體中文)**.

---

## Stage 0 — Receive task and classify

### Design.md soft-read

Before task classification, check for a DESIGN.md at the project root:
1. Run `git rev-parse --show-toplevel`. If it fails, skip silently.
2. If `{root}/DESIGN.md` exists, read it into context and output one line in 繁中:
   「已載入 DESIGN.md，視覺規格已參考」
3. If absent, skip silently. This check is non-blocking and does not affect any gate.

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

進入 RED 之前請閱讀 `plugins/baransu/skills/_shared/tdd.md`，特別注意 vertical slicing 與 test-verifies-behavior 兩條原則。

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
| Test fails (2nd attempt) | Stop. Report: 「綠燈連續失敗兩次。若方向有疑問，可呼叫 /baransu:think 重新對焦後再試；若確認方向無誤，請直接重試。」Do not continue automatically. |
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

If the cosmetic path was taken, mark TASK-02 complete before calling `/review`.

**Only invoke /review if work completed successfully** (TDD Green gate passed, or cosmetic change applied). If the session ended on a failure path, do not invoke /review — there is nothing to review.

---

## Constraints

- Never skip the Red gate. Even when the test "obviously" fails, run it and confirm.
- Never modify the test during the Green phase. The test is the spec; implementation must satisfy it as written.
- Cosmetic classification is final once made. Do not re-classify mid-execution.
- All user-visible output is Traditional Chinese (繁體中文). English appears only in this SKILL.md body, code identifiers, and file paths.
