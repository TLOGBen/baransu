---
name: review
description: Independent multi-perspective re-verification of any model output — code, a plan (e.g. /think's approved proposal), a claim, a diff, a file set, a directory. Dispatches isolated perspective agents (architecture / quality / security) in clean Task contexts to surface hallucinations, drift, over-engineering, unnecessary complexity, missing e2e verification, and balance violations. Triages findings into four tiers (safe auto-fix / packaged for confirm / ask user / FYI). Hard-gates code targets with an e2e requirement. Use when the user wants a rigorous independent audit of a prior actor's work, especially after a long-running or multi-turn session where context pollution is likely. User-facing output is in Traditional Chinese (繁體中文).
---

# review — independent multi-perspective re-verification

Models drift. After a long turn, after a pipeline, after a self-declared "done", the same model that produced the work is exactly the wrong one to audit it: context pollution and inertia make it repeat its own assumptions. `/review` is the counter-move — an orchestrator that dispatches **isolated** perspective agents in clean Task contexts and lets them re-read the target without the originating session's baggage.

This skill is not a big monolithic reviewer. It's a **task-analyst + dispatcher**: it parses target shape, produces the claim checklist, grades scope, applies activation rules, dispatches 1–3 perspective agents in parallel Tasks, optionally runs one adversarial pass, then consolidates everything into a four-tier triage. Main skill has no review rubric of its own — rubrics live in the perspective agent files (`architecture-reviewer`, `quality-reviewer`, `security-reviewer`).

---

## The iron rules

1. **No role-play.** Perspective ≠ persona. Agents are dispatched with "視角 + 目標 + 通用原則 + 禁忌", never with a character ("you are a senior security engineer"). Role-play induces hallucination.
2. **No keyword activation.** Activation is by target *property* (has auth surface, has cross-layer change, has executable code, etc.), not by matching words in the user's invocation string.
3. **Auto-fix blast radius is locked.** Only formatter / imports / typos / dead imports. Any change that touches control flow, boundaries, API shape, logic, or state **must** go to Tier 2 (packaged for confirm). Never expand.
4. **Balance check is mandatory.** Every finding that proposes new work must pass the 天平 check: *不做的代價 / 做的代價 / 有沒有中間方案*. Findings that fail downgrade to FYI or drop.
5. **E2E hard gate for code targets.** If the target contains executable code and no test-run evidence exists in-session, the verdict is forced to **INCOMPLETE** regardless of all other findings being clean.
6. **Never recurse.** `/review` never invokes `/review`; adversarial test runs exactly once per invocation; reviewers do not review each other.
7. **Output in Traditional Chinese.** Body is English (agent-facing); everything the user sees is 繁體中文.

---

## What /review is NOT

- Not a pipeline gate. Does not read `.agent-workspace/flow-state.json`. Does not emit handoff envelopes. Does not auto-fire after `/think` or any other skill.
- Not a cross-session tracker. Stateless by design; every invocation is independent.
- Not an implementer. Even Tier 1 auto-fix is cosmetic. Any semantic change is the *next* turn's problem, not this skill's problem.
- Not a replacement for native `/review` or `/security-review`. Those remain useful for simple PR single-pass audits. `/baransu:review` is for multi-perspective, triaged, balance-aware, hallucination-focused audits.

---

## Target types

`/baransu:review <target-spec>` accepts, in rough order of frequency:

| shape | example invocation | how to probe |
|---|---|---|
| Current uncommitted changes | `/baransu:review` (no arg) | `git diff` + `git status` |
| Commit range / branch | `/baransu:review HEAD~3..HEAD` or `/baransu:review feature/x` | `git diff <range>` |
| Explicit file list | `/baransu:review src/foo.ts src/bar.ts` | Read each |
| Directory | `/baransu:review src/auth/` | Glob + Read |
| Plan document | `/baransu:review .agent-workspace/plans/foo.md` | Read the plan |
| Inline plan text | `/baransu:review` with the /think output pasted / referenced | treat the prior assistant turn as target |
| Claim | `/baransu:review "this function is thread-safe"` + context | check the claim against code cited |

If the target is unbounded ("review the whole repo") or exceeds soft limits (>2000 LOC, >20 files, >10 plan sections), **PAUSE with AskUserQuestion** to narrow — do not attempt a boil-the-ocean run.

---

## Stage 0 — Mode decision (quick / standard / deep)

Before any work, pick a tier based on target surface area. Tier determines which perspective agents activate and whether adversarial testing runs.

| tier | trigger | reviewers | adversarial |
|---|---|---|---|
| **T1 quick** | ≤ 100 LOC code, or ≤ 3 plan decisions, single file | 1 reviewer (see activation) | skip |
| **T2 standard** | 100–500 LOC, or 3–8 decisions, single-module/layer | 1–2 reviewers | skip unless cross-layer |
| **T3 deep** | > 500 LOC, or cross-layer, or > 8 decisions, or multi-service | all applicable (up to 3) | mandatory |

Measure honestly. If you're uncertain between T1 and T2, round up; if uncertain between T2 and T3, look at whether boundaries are crossed (new file in another package, schema change, cross-component call) — if yes, round up.

---

## Stage 1 — Receive & probe

1. Parse the invocation argument. Determine target shape from the table above.
2. Read the minimum needed to size the target (Bash `git diff --stat`, Glob, or head-of-file Reads). Do **not** pre-judge correctness yet.
3. Compute LOC / decision-count / file-count / layer-span.
4. If unbounded or over soft limits: stop and PAUSE via AskUserQuestion asking the user to narrow.
5. Record target metadata for the report's "Target" section.

---

## Stage 2 — Produce the claim checklist

Before dispatching any reviewer, write down — in 繁中 — what the target is **claiming**. This is the spec against which reviewers verify. It is the skill's most important hallucination-prevention step: without an explicit claim checklist, reviewers drift into free-form critique.

The checklist must enumerate:
- What the target says it **did** (operations, changes, new behaviour).
- What the target says it **decided** (design choices, trade-offs taken).
- What the target says it **achieved** (observable outcomes, metrics, guarantees).
- What the target says it is **NOT doing** / explicit out-of-scope.
- What the target says are **unknowns / deferred**.

If the target is a /think output (or similar structured plan), lift claims directly from Building / Approach / Key decisions / Not building / Unknowns sections. If the target is code, derive claims from commit messages, PR description, function docstrings, or the user's invocation argument — where no source exists, write "no explicit claim for <area>" rather than inventing one.

The checklist is included verbatim in the final report and is passed to every dispatched reviewer.

---

## Stage 3 — Activation rules

Apply the tier from Stage 0 and the property rules below. **No keyword matching on the user's text** — only properties observed in the target itself.

**Perspective activation** (union — each row that matches adds):

| target has… | activate |
|---|---|
| any executable code (source file in any language) | quality-reviewer |
| > 3 files touched OR new module/package/service OR cross-layer change OR changed public API/interface | architecture-reviewer |
| auth / authz / session / input-handling / secrets / crypto / network / serialization / persistence / file-path handling / shell-execution / user-supplied template rendering | security-reviewer |
| plan / design / claim type (no executable code) | architecture-reviewer + quality-reviewer; security-reviewer only if plan references any of the security surfaces above |

**Adversarial activation**:

- T3 tier → mandatory.
- T2 with cross-layer or cross-service change → mandatory.
- Anything else → skip.

Log the activation decision and its triggering rule in the report (Stage 7). If a reviewer is activated, any finding it produces is admissible; if it was not activated, findings in its domain default to FYI unless clearly critical.

---

## Stage 4 — Parallel dispatch

Dispatch all activated perspective reviewers **in a single message** (parallel Task calls). Each Task:

- Uses the corresponding subagent type (`architecture-reviewer`, `quality-reviewer`, `security-reviewer` — these are the plugin-bundled agents at `plugins/baransu/agents/`).
- Runs in a clean Task context (isolated from the current main-skill conversation; this is the core anti-pollution mechanism).
- Receives: the target spec, the claim checklist (from Stage 2), the target metadata (tier, LOC, span), and explicit instructions to return findings in the shape below.

Required finding shape (each reviewer returns a list of):

```
- id: <short slug>
  severity: <critical | major | minor | advisory>
  citation: <file:line or plan-section-name>
  claim_violated: <which checklist item, or "none">
  observation: <what the reviewer saw>
  suggested_fix: <1–3 sentences, surgical; or "none — advisory only">
  balance_note: <answers 不做的代價 / 做的代價 / 中間方案; or "N/A — not a new-work proposal">
```

Reviewers are **not** told about each other and do not coordinate. Duplicates are the main skill's problem at consolidation.

---

## Stage 5 — Adversarial test (conditional)

Run exactly once, only if activation conditions met (Stage 3). Dispatch as a single Task with `subagent_type: general-purpose`, embedding all six angles in the prompt:

1. **違反假設** — name each assumption the target makes; construct one scenario where each is false; ask whether the target still holds.
2. **組合失敗** — find the smallest combination of events / inputs / states that jointly break the target, even if each individual component is fine.
3. **上下級串聯錯** — trace one message/data path through all layers; look for contract mismatches where each layer is locally correct but the chain corrupts meaning.
4. **濫用場景** — name three plausible misuse patterns a non-adversarial user might fall into; for each, what does the target do.
5. **根因辨識** — for each reviewer-found issue, ask: is this the root cause or a symptom? List any that are symptoms of a deeper unfixed cause.
6. **epistemic 共識檢查** — if all reviewers agreed on some point, is that because it's objectively true, or because they share a training-data-level bias? Name one way the unanimous view could be wrong.

For plan / claim targets, translate:
1 → ambiguous premise;
2 → sections internally inconsistent;
3 → decision-to-decision contradiction;
4 → scope creep / reader misreading;
5 → cause/effect confusion;
6 → apparent plan completeness being a hallucinated signal.

Adversarial output is added to the finding pool for Stage 6 consolidation. It does **not** override reviewer findings — it augments.

---

## Stage 6 — Consolidate & triage (with balance check)

1. **De-duplicate**: collapse findings pointing to the same citation + same observation; assign the collapsed finding to the perspective whose scope most narrowly covers it.
2. **Balance check (mandatory)**: for every finding whose `suggested_fix` introduces new work (new file, new layer, new check, new dependency, new refactor), evaluate:
   - 不做 (keep current state) 會得到什麼 / 失去什麼
   - 做了 (apply the fix) 會得到什麼 / 失去什麼
   - 有沒有更小 / 更平衡的中間方案
   - Is the fix a surgical minimum, or is it over-processing?
   - Is a legitimate original design choice being downgraded to "problem" just because a reviewer prefers a different style?
   - If balance fails → downgrade to FYI or drop with a one-line note.
3. **Assign tier**:

| class of finding | tier | action |
|---|---|---|
| formatter, import order, unused import, obvious typo in identifier/comment, trailing whitespace, quote-style inconsistency | **T1 — auto-fix** | apply directly via Edit |
| non-semantic but beyond T1: variable renamed, duplicate constant collapsed, dead code removal, doc typo that is a semantic noun | **T2 — packaged confirm** | batch into one AskUserQuestion with full diff preview |
| logic / boundary / API / behaviour / security findings with concrete fix | **T3 — ask user** | batch into ≤ 4 AskUserQuestions total (not per finding) |
| findings without concrete fix, or balance-downgraded, or considered-but-not-recommended | **T4 — FYI only** | report, no action |

Cap Tier 3 at 4 AskUserQuestions per invocation. If more than 4 genuine T3 findings exist, bundle by theme and surface the rest in the report body for the user to act on later.

---

## Stage 7 — Emit (auto-fix, confirm, ask, report)

1. **Tier 1 auto-fix**: apply Edits directly. For each change, record: file, line range, before/after. Never touch anything outside format/import/typo/dead-import scope — if in doubt, demote to Tier 2.
2. **Tier 2 packaged confirm**: single AskUserQuestion with options [全部套用] / [逐項選擇] / [全部跳過]. On [逐項選擇], follow up with a multiSelect question listing the items. Apply accepted, report skipped.
3. **Tier 3 ask**: batched AskUserQuestions, at most 4 total. Each question carries 2–4 options (one recommended). Record answers alongside findings in the report.
4. **Tier 4 FYI**: report only, no interaction.

**E2E hard gate (code target only)**:
- Detect project test infra: presence of `package.json` + test script, `pyproject.toml`/`pytest.ini`, `go.mod`, `Cargo.toml`, `Gemfile`, `pom.xml`, `build.gradle`, `Makefile` with test targets, `.github/workflows/` with test jobs — any one triggers "test infra present".
- Detect evidence of green test run in-session: Bash tool results showing test-command output with exit 0 and visible PASS summary. Tool output from prior turns counts; no run = no evidence.
- If test infra present and no evidence of green run: **verdict = INCOMPLETE** regardless of other findings.
- If test infra absent (e.g. baransu itself): verdict logic ignores e2e; note "e2e gate: n/a (no test infra)".
- For plan / claim targets: e2e gate is n/a.

**Final report (繁體中文)**:

```
# /baransu:review — 審核結果

**Verdict：{PASS | CONCERN | FAIL | INCOMPLETE}**

## Target
<target 描述 + tier + size 指標>

## 目標宣稱 (Claim Checklist)
<Stage 2 的逐條列表>

## 派遣的審核者
- 架構審核：[啟用 / 略過] — <理由>
- 品質審核：[啟用 / 略過] — <理由>
- 安全審核：[啟用 / 略過] — <理由>
- 對抗測試：[啟用 / 略過] — <理由>

## 發現（四級 triage）

### Tier 1 — 已自動修復（format / import / typo / dead import）
<list of applied changes with file:line>

### Tier 2 — 待確認（非語意但超出 T1）
<list, or "無">

### Tier 3 — 需判斷（已透過 AskUserQuestion 批次詢問）
<list with user's answers recorded>

### Tier 4 — 僅供參考
<list, or "無">

## E2E Gate
{pass / fail: <reason> / n/a: <reason>}

## 結論
<one-paragraph verdict rationale in 繁中>
```

Verdict rubric:
- **PASS** — no T2/T3 findings open, e2e gate pass or n/a, balance-clean.
- **CONCERN** — T3 findings exist and user chose non-fix options; or balance-passing advisories user should see.
- **FAIL** — critical-severity T3 finding with no accepted fix path; or hallucinated claim confirmed.
- **INCOMPLETE** — code target, test infra present, no green run evidence. Overrides all other categories.

---

## Gotchas

- **Over-dispatching reviewers on tiny targets.** A 30-line bug fix doesn't need architecture review. Trust the tier table.
- **Balance-check skipped under time pressure.** The point of `/review` is to catch exactly the overreach that a hurried reviewer misses. Never skip.
- **Reviewer agents echoing the main-skill's framing.** If a reviewer returns findings phrased like the claim checklist verbatim, it's cargo-culting rather than thinking. Push back: re-dispatch with "re-read the target directly, not via the checklist".
- **E2E gate becoming bureaucratic.** If test infra is present but genuinely inappropriate for the change (e.g. doc-only change), note it as n/a with reason — don't FAIL a README typo for lack of test run.
- **AskUserQuestion fatigue.** The 4-batch cap is a hard limit, not a suggestion. If you're drafting a 5th question, consolidate.
- **Recursion attempts.** If a reviewer suggests "you should run /baransu:review on this", strip that suggestion at consolidation. This skill never recommends itself.
- **User rejects verdict in free text.** Do not re-run Stages 3–6. Ask which specific finding is contested, re-verify that one (re-Read the citation, re-ask one reviewer with narrower scope), and amend the report section — don't restart.
- **Plan target pointing back at /think.** If a reviewer finds the plan under-specified, the remediation is **not** "go back to /think" — `/review` only reports, doesn't route. Note the under-specification as a T3 finding.
- **Non-code "claim" targets.** When the user pastes a bare claim like "this function is thread-safe", require at least a code citation. If none, PAUSE to ask "審核哪個檔案/函式來驗證這個宣稱？".

---

## Constraints (hard)

- Never produce role-play prompts for reviewer Tasks.
- Never expand auto-fix beyond format / import / typo / dead-import.
- Never recurse; adversarial runs once; reviewers never review each other.
- Never skip the balance check in Stage 6.
- Never emit verdict PASS on a code target without e2e evidence; default to INCOMPLETE.
- Never read `.agent-workspace/flow-state.json` or emit handoff artifacts — this skill is stateless and user-triggered only.
- All user-facing output in 繁體中文.
