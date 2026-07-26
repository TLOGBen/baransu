---
name: seal
description: 'Single-pass narrow verification with direct-fix rights, run AFTER implementation:
  audits the diff against CONTRACT.md criteria, scans unpinned user-facing surfaces,
  byte-diffs verbatim constants, and mutation-probes 1-2 surfaces. Use to close out
  a /contract-banded task. Trigger On ''/seal'', ''封緘'', ''收尾驗收'', ''驗收剛做完的'', ''seal
  it''. Not for cross-perspective re-verification of any model output (use /review)
  or pre-work criteria pinning (use /contract). 繁體中文輸出。'
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

# seal — one cold-eyed pass before you call it done

Teeth live in the criteria and the mandate, not in the reviewer's model: the
same reviewer that waves a defect through under a loose contract rejects it
under an assertable one. All user-visible output is **Traditional Chinese (繁體中文)**.

## Outcome Contract

- **Outcome**: One single-pass, narrow-scope verification of a finished implementation against its contract (or user-named criteria), with defects fixed directly and pinned by tests.
- **Done when**: All five mandate points below are executed and reported point-by-point with evidence; every mutation probe is reverted (working tree clean of probe residue); every applied fix carries a pinning test that runs green in-session.
- **Evidence**: The five-point report (each point: finding or 「乾淨」), the mutation probe record (what was broken → which test fired / failed to fire → revert confirmation), and the green run output tail for applied fixes.
- **Output**: A Traditional Chinese seal report in the conversation (五點結果＋修正清單＋突變抽查記錄); fixes land as working-tree edits with their pinning tests.
- **Automation**: ultracode=neutral, loop=drivable（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）
- **Telemetry**: on invocation, append one selection record per `../_shared/selection-telemetry.md`.
- **Seal evidence**: on completion, append one JSON line `{"ts":"<ISO8601>","skill":"seal","result":"pass|fixed","target":"<one-phrase>"}` to `~/.codex/baransu/telemetry/{project}/seal-log-{YYYY-MM}.jsonl` ({project} = git-root basename, or the cwd folder name when there is no git) — this is the evidence the shipped seal-guard Stop hook checks; skipping it causes a false block at session end.

PAUSE classification for non-interactive drivers: `references/loop-pauses.md`.

## Target-pin off-ramp (hard rule)

Materialize the target from disk BEFORE anything else, in this order:
1. A `CONTRACT.md` (project root or user-named path) → its criteria are the audit baseline; the diff is `git diff <base>` when the user names a base, else uncommitted + branch-local changes.
2. No contract but user-named criteria / artifact → use those verbatim as the baseline.
3. Neither a materializable diff nor a named artifact → **stop and report** `needs-input`（「無可審工件：請指名 diff 基準或合約」）. Never fabricate a target and never seal from conversation memory.

Seal is designed for cold eyes: re-ground every claim from disk even when this
session wrote the code. What this session remembers is a claim, not evidence.

## Baseline suite pre-flight

After the target is pinned and before mandate point 1, run the project's full
test suite once and record the result as the baseline.

- **No runnable suite** → mandate point 5 degrades to a static pin-audit
  (surface → pinning-test mapping check, no probe injection), and 「無可執行
  測試套件」 is itself a top-level finding; direct-fix rights narrow to
  constant-drift corrections — an in-band finding that cannot be paired with
  a pinning test is reported, not fixed.
- **Baseline already red** → record the pre-existing red tests; mutation-probe
  attribution counts only tests that turn red RELATIVE to the baseline, and
  "green" for applied fixes means green relative to the baseline (the
  pre-existing red set unchanged, listed in the report).

Both branches keep the report template and seal-log JSONL unchanged — the
degraded path records 突變 0/0（靜態核對）in the closing line.

## The five-point mandate

Run all five, in order. The gate rules are the shared single implementation in
`../_shared/contract-gate.md` (G1–G4 + Loose-Criterion Escalation) — read it
first; judge against it, do not restate it.

1. **Criteria audit** — walk the contract criteria one by one against the
   implementation; each gets 符合 / 違反 / 條文太鬆 (G1 judgment).
2. **Unpinned-surface scan** — enumerate every user-facing output the diff
   touches (CLI println, TUI toast, error path); flag each surface no test
   pins at rejection strength (G4 judgment, including the cross-UI shared-helper rule).
   **Zero-test layers are the PRIMARY scan target, never an exempt zone** — a
   layer with no tests (DAO SQL, controller parameter mapping) is where unpinned
   defects live, and the mutation spot-check (point 5) can only fire where tests
   exist, so at least one probe or manual line-by-line check goes into a
   zero-test layer. Two mechanical sub-checks whenever the diff contains
   parameterized queries: (a) **parameter-usage reconciliation** — the set of
   parameters added to the command equals the set referenced in the SQL text
   (an added-but-unreferenced parameter is a correctness finding: the filter
   silently does not filter); (b) **condition-effectiveness** — every query
   condition the contract names (vendor / date-range / permission scopes) is
   confirmed present in the WHERE clause; "the parameter is passed" never
   substitutes for "the condition takes effect", and a criterion resting on an
   unverified premise does not exempt its adjacent verifiable conditions.
3. **Cross-UI consistency** — when two UIs express the same outcome, confirm a
   single shared helper pinned on BOTH real call paths; mirror tests do not count.
4. **Verbatim constants byte-diff** — diff every constant in the implementation
   against the contract's `## Verbatim Constants` block (G3), byte for byte.
5. **Mutation spot-check** — deliberately break 1-2 user-facing surfaces, run
   the test suite, and record which test fired (or that none did). Probe
   revert is a mechanism-level gate, not an intent: BEFORE injecting each
   probe, save the target file's exact pre-probe content byte for byte (a
   temp-path copy, or an exact recorded hunk); the ONLY permitted revert is
   writing that saved content back, and "confirm the revert" is defined as a
   byte-for-byte comparison against the saved copy that matches. When the
   audit target includes uncommitted changes (the argument-hint default
   `none = uncommitted diff`), reverting via `git checkout` / `git restore` /
   `git stash` is forbidden — those commands destroy the under-audit
   uncommitted implementation together with the probe. A probe that no test
   catches is a finding, never a shrug.

## Direct-fix rights and their boundary

Findings within the narrow band — an unpinned surface, a constant drift, a
criteria violation with an obvious minimal fix — are fixed directly, each fix
paired with a pinning test, and the suite re-run to green. Per the shared
Loose-Criterion Escalation rule: a real defect the criteria are too loose to
reject is a SPEC BUG — fix the defect AND record the criteria patch;
"the contract doesn't forbid it" is never grounds to pass.

**Evidence-backed dissent (R10, 大膽包 A)**: if the implementation DEVIATED from
a contract premise or clause AND carries first-hand evidence (a DB query result,
actual code at file:line, an SA-doc citation) that the premise was wrong, judge
the deviation on that EVIDENCE — a correct evidence-backed deviation is 符合,
never 違反 on literal contract wording; record a premise/criteria patch. In a prior
harness experiment, seal rejected an implementer's evidence-backed correct
data-source switch on literal contract wording (seal 字面誤判率 baseline 1) —
R10 forbids that pushback.
A bare assertion WITHOUT first-hand evidence does not qualify (evidence gate).

Out of band — architectural rework, behavior redesign, anything touching files
the diff never touched — is reported, not fixed: route to `/baransu:review`
(independent re-verification) or `/baransu:hunt` (root-cause diagnosis).

Exactly one pass (no seal-of-a-seal, no iterative rounds): findings either get
fixed now with a pinning test, or get reported. A clean seal — five points
executed, zero findings, probes reverted — is a complete, valid deliverable.

## Report shape (Traditional Chinese)

「封緘結果」：五點逐一（符合/發現＋處置）、修正清單（每筆附釘死測試名與綠燈證據）、
突變抽查記錄（弄壞了什麼→哪個測試叫了/沒叫→已還原）、以及（若有）條文補丁建議。
Close with: 「封緘完成：{N} 條條文核對、{M} 個表面掃描、{K} 處修正（各附釘死測試）、
突變 {X}/{Y} 被測試攔截。」

## Not-for boundaries

- Cross-perspective independent re-verification of any model output（跨視角重驗證、四層回應、無預設修正權）→ `/baransu:review`.
- Pre-work criteria pinning（開工前釘條文）→ `/baransu:contract`（contract 開工前、seal 收工後——同一頻段的一對）.
- Large-band spec verification → `/baransu:analyze`'s built-in final review; seal never audits a multi-module spec.
- Symptom/error debugging（報錯排查）→ `/baransu:hunt`.
