---
name: evolve
description: Use when the user wants to improve, score, or evolve a SKILL.md. Point
  it at any skill and it runs a forward-only ratchet — a fixed 9-dimension rubric
  is the selection environment; each round an independent judge picks the weakest
  dimension, one single-variable change is made, and three fresh blind judges vote,
  keeping the change only on a strict improvement (else the file-level snapshot is
  restored). Dual-axis evaluation (structure + effectiveness — effectiveness via real-exec
  gated by a trust+capability check, else offline replay), held-out validation with
  an independence layer, and a Kami result card. Adoption of any change is an Authorization
  PAUSE; rollback never touches the git working tree. Trigger on '/evolve', '優化 skill',
  'skill 評分', '演化 skill', 'optimize skill', 'improve skill quality', 'evolve a skill',
  '幫我改 skill'. 繁體中文輸出。
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

# evolve — optimize a SKILL.md like you train a model

The deliverable is an **evolution package**: a target SKILL.md made measurably better through a ratchet that can only turn forward. The rubric is the fixed selection environment, the target SKILL.md is the gene, and an external benchmark is the yardstick. The single most important property is **evaluation independence** — the model that mutates the skill never also judges whether the mutation was an improvement.

The body below is English (agent-facing). All user-visible output is in **Traditional Chinese (繁體中文)**.

## Outcome Contract

- **Outcome**: 對目標 SKILL.md 跑只能向前轉的棘輪，產出每步可追溯、經獨立盲評與 held-out 驗證的演化包。
- **Done when**: `.claude/evolve/<slug>/` 內有 `report.md`、`results.tsv`、`log.md`、`held-out.md`、收斂曲線與成果卡，且演化版已過結構閘並經使用者於 Authorization PAUSE 採納或全部回滾。
- **Evidence**: `report.md` 的起訖分數、dry_run 比例、每軸證據來源與 held-out 證據力標籤；`log.md` 的逐輪 keep/restore 記錄。
- **Output**: `.claude/evolve/<slug>/` 演化包；對話內呈現繁中收斂摘要與成果卡。
- **Automation**: ultracode=assist, loop=assisted（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）

## When to use / not

Use when a SKILL.md (or any skill-shaped instruction file) should be measurably improved against a stable rubric. Not for: writing a new skill from scratch (that is authoring, not evolution); one-off prose edits (just edit it); judging whether a skill should exist (a value call — that is `../think/SKILL.md` Evaluation Mode).

## The four pillars (do not weaken)

1. **Single editable asset, single variable** — one target SKILL.md, one rubric dimension changed per round. This is what makes every improvement attributable.
2. **Dual evaluation** — structure axis (static rubric reading) and effectiveness axis (output from real-exec or offline replay). See `references/rubric-9dim.md`.
3. **Evaluation independence is the lifeline** — the mutator never judges; judges are fresh each round, blind, neutrally named. LLM self-evaluation is unreliable; independent blind panels are the correction.
4. **Fixed rubric = selection environment; SKILL.md = gene; external benchmark = yardstick.** Never edit the rubric mid-run.

## Stage 0 — Target, slug, work dir

1. Resolve the target SKILL.md path. Derive `<slug>` from the skill name.
2. Create `.claude/evolve/<slug>/` with a `snapshot/` subdir.
3. Read `references/rubric-9dim.md` (the selection environment) and `references/safety-gates.md` (the red lines). Both are loaded once and held constant for the whole run.
4. Locate or build the benchmark `test-prompts`, split into **train** (drives the loop) and **held-out** (final validation only). If the target has no benchmark, pause and ask the user for 2–3 prompts; the system fills a skeleton for confirmation — never fabricate the pass criteria. **If the user declines or no benchmark is confirmed → then run the loop structure-axis-only: hard-label dims 7–9 as `no-benchmark` (unscored, never assumed) in `report.md`, and skip Stage 7's held-out validation (there is no held-out set). Do not silently proceed as if effectiveness were measured.**

## Stage 1 — Snapshot + diagnose

1. Snapshot the target file's bytes to `snapshot/<round>.md` (file-level; see `references/safety-gates.md` Gate 2).
2. Dispatch the **evolve-diagnostician** agent with the target path and the rubric. It scores all 9 dimensions and returns the single weakest dimension (by weighted headroom) plus one concrete, single-variable improvement direction. It diagnoses only — it never edits.

## Stage 2 — Mutate (single variable)

Apply exactly one change, targeting only the weakest dimension, into a scratch copy. Hold the red lines: do not touch other dimensions; if the dimension is in a related cluster ({3,4,5} or {7,8} per the rubric), make the minimal change and let the judges check the siblings for regression.

## Stage 3 — Structure gate (before any judging matters)

Run `python3 scripts/verify-skills.py` (no argument — repo mode) over the repo containing the mutated copy, then read the mutated skill's line in the output. Do **not** pass the skill dir as an argument: verify-skills treats its arg as a skills-root to iterate, so the single-dir form mis-scans the skill's own `references/` / `scripts/` subdirs as skills and emits a false `references: 缺 SKILL.md` failure (this breaks every skill-with-`references/`, including evolve itself). **Keep is only possible** if exit code is 0 **and** stdout carries no `⚠️ ADVISORY` line (a body-bloat advisory returns exit 0 but must be read and treated as a failure). On failure: restore the snapshot and skip to Stage 6 — this round produced nothing. Score never overrides structure (`references/safety-gates.md` Gate 4).

## Stage 4 — Effectiveness axis (real-exec or offline)

Score the effectiveness dimensions (7–9). Decide real-exec vs offline via the **trust + capability dual gate** (`references/safety-gates.md` Gate 3):
- **Capability gate** — interactive/approval-gated skills (think, review, analyze, …) cannot run unattended → offline.
- **Trust gate** — only user-owned-path skills with no destructive-pattern hit run for real; unknown/third-party/pattern-hit → offline.
- When real-exec runs, mark it untrusted in the report and advise memory rotation. When offline, the effectiveness output is same-source as the structure axis → label it `offline-同源` and treat its evidence as single-axis.

## Stage 5 — Blind judge panel

Dispatch **three fresh evolve-judge agents in parallel**. Present the pre- and post-mutation versions under neutral labels (alpha / beta); swap which label is "new" on odd vs even rounds to cancel position bias. Each judge returns `{better, strict_improvement, per_dimension_deltas}`. Judges are single-use — never reuse a judge across rounds.

**Keep iff ≥ 2 of 3 judge strict_improvement = true.** Under high real-exec noise, tighten to 3 of 3.

## Stage 6 — Adoption (Authorization PAUSE) or restore

- If kept: present the diff + score delta and **halt at an Authorization PAUSE** (`references/safety-gates.md` Gate 1). Adoption write-back is never skippable — not under `/loop`, cron, ultracode, or Workflow. Only on explicit user adoption is the change written to the target file; then re-read the target (the baseline changed) and reset the no-progress counter.
- If not kept (judges, or structure gate, or restore path): restore the snapshot to the target file. File-level only — never `git reset --hard` / `stash` / `clean` / `checkout`.
- Append a `log.md` entry either way: round #, dimension, mutation summary, gate result, votes, decision.

## Stage 7 — Convergence + held-out + package

- **Converge** when the no-progress counter reaches **N=3** consecutive rounds, or the round cap **R=6** total rounds is hit. Otherwise loop back to Stage 1.
- **Held-out**: validate the converged version on the held-out set with an **independence layer** (default: a separate judge pool; options: different rubric weighting, or human ground-truth). Write `held-out.md` with the evidence-strength label (`硬證據` only if an independence layer was applied; otherwise `題目泛化證據`). See `references/output-contract.md`.
- **Package**: write `results.tsv`, `convergence.svg` (the score-over-rounds curve; the effective baseline steps up on keeps only), and `report.md` (start/end score, dry_run ratio, per-axis evidence source) — every artifact lands in `.claude/evolve/<slug>/`. **Make the user-facing surfaces human-readable — draft the convergence summary and the card copy through `/write` (zh), then render the result card through the `/book` entry (never hand-assemble HTML) and write it to `.claude/evolve/<slug>/card.png` (the durable card artifact named in `references/output-contract.md`); see that file's §Human-readable delivery.** Surface the `/write`-refined 繁中 convergence summary, not the raw round-by-round trace.

## Provenance + optional engine

The mechanism is concept-aligned with public prior art but re-derived in original wording; run the clean-room checklist in `references/provenance.md` at `../review/SKILL.md` time. The base engine is self-written and the default; `skillopt` is optional, version-pinned, and degrades gracefully when absent — never a silent dependency (`references/provenance.md`).

## Constraints

- Never edit the rubric mid-run; it is the fixed selection environment.
- One dimension per round; keep only strict improvements; restore otherwise.
- Adoption write-back is an Authorization PAUSE on every platform.
- Rollback is file-level; never touch the git working tree beyond the single target file.
- The diagnostician and judges are stateless leaf nodes (subagent depth = 1): they never dispatch further subagents or invoke any `/baransu:*` skill.
- All user-visible output is Traditional Chinese (繁體中文).
