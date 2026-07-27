---
name: evolve
description: Improves, scores, or evolves a SKILL.md via a forward-only ratchet — fixed 9-dimension rubric, one single-variable change per round, three fresh blind judges; kept only on strict improvement, else the snapshot is restored. Dual-axis evaluation (structure + effectiveness), held-out validation, Kami result card; adoption is an Authorization PAUSE. Not for authoring a brand-new SKILL.md, or deciding whether a skill should exist (/think Evaluation Mode). Trigger on '/evolve', '優化 skill', 'skill 評分', '演化 skill', 'optimize skill', 'improve skill quality', 'evolve a skill', '幫我改 skill'. 繁體中文輸出。
---

# evolve — optimize a SKILL.md like you train a model

The deliverable is an **evolution package**: a target SKILL.md made measurably better through a ratchet that can only turn forward. The rubric is the fixed selection environment, the target SKILL.md is the gene, and an external benchmark is the yardstick. The single most important property is **evaluation independence** — the model that mutates the skill never also judges whether the mutation was an improvement.

All user-visible output is in **Traditional Chinese (繁體中文)**.

## Outcome Contract

- **Outcome**: 對目標 SKILL.md 跑只能向前轉的棘輪，產出每步可追溯、經獨立盲評與 held-out 驗證的演化包。
- **Done when**: `.claude/evolve/<slug>/` 內有 `report.md`、`results.tsv`、`log.md`、`held-out.md`、收斂曲線與成果卡（零採納時成果卡依 Stage 7 較輕出口省略並於 `report.md` 註記），且演化版已過結構閘並經使用者於 Authorization PAUSE 採納或全部回滾。
- **Evidence**: `report.md` 的起訖分數、effectiveness mode（real-exec / offline-同源 / no-benchmark）與 Gate 3 理由、每軸證據來源與 held-out 證據力標籤；`log.md` 的逐輪 keep/restore 記錄。
- **Output**: `.claude/evolve/<slug>/` 演化包；對話內呈現繁中收斂摘要與成果卡。
- **Automation**: ultracode=overlap, loop=drivable（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）
  In the same non-interactive pass, read `references/loop-pauses.md` for this skill's own PAUSE classification.

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
4. Locate or build the benchmark `test-prompts`, split into **train** (drives the loop) and **held-out** (final validation only) by this rule: the held-out set keeps at least 1 prompt and about 1/3 of all benchmark prompts (round up), and held-out prompts stay invisible to the evolution loop (Stages 1–6) until Stage 7 — feeding every prompt into the loop hollows out held-out validation. If the target has no benchmark, pause and ask the user for 2–3 prompts; the system fills a skeleton for confirmation — never fabricate the pass criteria. **If the user declines or no benchmark is confirmed → then run the loop structure-axis-only: hard-label dims 7–9 as `no-benchmark` (unscored, never assumed) in `report.md`, and skip Stage 7's held-out validation (there is no held-out set). Do not silently proceed as if effectiveness were measured.**

### Orchestration interface (dual-mode)

When — and only when — the run is Workflow-driven or a system-reminder confirms
ultracode, read `references/orchestration-interface.md` before Stage 1 and apply
its adapter contract; on the default interactive path, skip the read and write no
mode record — the absence of a mode record means the current (parallel-Task)
adapter. On the Workflow path, pin the mode at Stage 0 (record to disk, no mid-run
switch); the read happens once — never re-read before a Stage-5 judge panel. Both
adapters return identical votes; the Stage 5 tally never senses the mode.

## Stage 1 — Snapshot + diagnose

1. Snapshot the target file's bytes to `snapshot/<round>.md` (file-level; see `references/safety-gates.md` Gate 2).
2. Dispatch the **evolve-diagnostician** agent with the target path and the rubric. It scores all 9 dimensions and returns the single weakest dimension (by weighted headroom) plus one concrete, single-variable improvement direction. It diagnoses only — it never edits.

## Stage 2 — Mutate (single variable)

Apply exactly one change, targeting only the weakest dimension, into a scratch copy. Hold the red lines: do not touch other dimensions; if the dimension is in a related cluster ({3,4,5} or {7,8} per the rubric), make the minimal change and let the judges check the siblings for regression.

## Stage 3 — Structure gate (before any judging matters)

Repo-mode verify-skills scans only the live skills tree — a scratch copy is invisible to it — so the gate runs as a bounded **write-verify-restore** window on the target path: (1) confirm `snapshot/<round>.md` exists (no snapshot → abort the round, no write); (2) write the scratch bytes to the target path; (3) run `python3 scripts/verify-skills.py` (no argument — repo mode) and read the mutated skill's line in the output; (4) restore the snapshot bytes to the target path immediately, pass or fail, before any Stage 4/5 dispatch. **Interruption recovery**: at the start of every Stage 1 round (including a resumed run after an interruption), if the live target's bytes ≠ the latest `snapshot/<round>.md` and `log.md` carries no matching adoption entry → then restore the snapshot bytes to the target and log `decision: window-breach-restored` in `log.md` before any diagnosis — an interruption between step (2) and step (4) otherwise leaves mutation bytes live and silently bypasses the ratchet's restore guarantee. The window is sanctioned by the mutation-isolation invariant (Constraints below) and never by itself constitutes adoption. Do **not** pass the skill dir as an argument: verify-skills treats its arg as a skills-root to iterate, so the single-dir form mis-scans the skill's own `references/` / `scripts/` subdirs as skills and emits a false `references: 缺 SKILL.md` failure (this breaks every skill-with-`references/`, including evolve itself). **Keep is only possible** if exit code is 0 **and** stdout carries no `⚠️ ADVISORY` line (a body-bloat advisory returns exit 0 but must be read and treated as a failure). On failure: the snapshot is already restored by step (4) — skip to Stage 6's restore accounting; this round produced nothing. Score never overrides structure (`references/safety-gates.md` Gate 4). **Degraded gate**: if the target is not governed by a repo `scripts/verify-skills.py` (any non-baransu skill — the script's constants pin it to its own checkout), do not run it against the wrong repo; degrade to a declared minimal mechanical check on the scratch copy — frontmatter parses, name/description limits hold, body-line advisory — and label the gate `degraded-gate` in `report.md`.

## Stage 4 — Effectiveness axis (real-exec or offline)

Score the effectiveness dimensions (7–9). Decide real-exec vs offline via the **trust + capability dual gate** (`references/safety-gates.md` Gate 3):
- **Capability gate** — interactive/approval-gated skills (think, review, analyze, …) cannot run unattended → offline.
- **Trust gate** — only user-owned-path skills with no destructive-pattern hit run for real; unknown/third-party/pattern-hit → offline.
- **Destructive-pattern red line (`real-exec-destructive-forbid`)** — if the real-exec trust gate hits ANY destructive pattern (`rm` / writing files outside the target directory / network writes / secret access) → then force-downgrade to offline and NEVER execute that skill. This is a hard if-then prohibition with the same rigidity as the git-tree red line, not advice: actually executing an untrusted skill is the genuinely irreversible destructive surface, so it is forbidden, not merely flagged. When real-exec does run (no destructive pattern, trust + capability both clear), mark it untrusted in the report and rotate memory after the run. When offline, the effectiveness output is same-source as the structure axis → label it `offline-同源` and treat its evidence as single-axis.

## Stage 5 — Blind judge panel

Blind the panel mechanically, not by instruction alone: copy the pre- and post-mutation versions to `.claude/evolve/<slug>/panel/round-<N>/alpha.md` and `beta.md` (byte-identical copies — no added headers or annotations that could mark which is which). Round parity decides the assignment (odd rounds: mutation = alpha; even rounds: mutation = beta), cancelling position bias; the mapping is never disclosed to judges. Then dispatch **three fresh evolve-judge agents in parallel**, passing ONLY the two neutral panel paths — never the live skill path or the scratch path, whose names leak which version is the mutation. Each judge returns `{better, strict_improvement, per_dimension_deltas}`. Judges are single-use — never reuse a judge across rounds.

**Keep iff ≥ 2 of 3 judge strict_improvement = true.** When the effectiveness axis ran via real-exec (Stage 4 evidence label `real-exec`, not `offline-同源`), the keep-bar is 3 of 3; otherwise 2 of 3. If any of the three judges fails to return a well-formed `{better, strict_improvement, per_dimension_deltas}` vote (crash, timeout, or malformed payload) → then record that vote as `strict_improvement=false` (a non-vote never counts toward keep); it still counts as a cast vote, the tally always runs over exactly 3 votes, and re-dispatch is never attempted.

## Stage 6 — Adoption (Authorization PAUSE) or restore

- If kept: adoption is an **Authorization PAUSE** (`references/safety-gates.md` Gate 1), satisfied one of two ways. **(a) Interactive or non-interactive without standing authorization** → present the diff + score delta and halt; write back only on explicit user adoption. **(b) Non-interactive WITH a standing authorization** recorded in the driving context (the loop/cron prompt or approved plan explicitly authorizes adoption / the evolve→ship sweep) → auto-adopt, but only for a change that clears every Gate-1 precondition (structure gate pass, blind-judge bar tightened to **3/3**, snapshot retained, `log.md` audit with `decision: standing-auth auto-adopt`); a change failing any precondition is restored, never written. The end-state check (`make test`) is the final arbiter for downstream steps. After any write-back, re-read the target (the baseline changed) and reset the no-progress counter. **If the user declines adoption** → discard the scratch (the next diagnostician round starts from the unchanged target), leave the target untouched, increment the no-progress counter, log `decision: user-declined`, and continue to Stage 7's convergence check.
- If not kept (judges, or structure gate, or restore path): restore the snapshot to the target file, then increment the no-progress counter (the only site it advances — Stage 7 converges at N=3 consecutive). File-level only — never `git reset --hard` / `stash` / `clean` / `checkout`.
- Append a `log.md` entry either way: round #, dimension, mutation summary, gate result, votes, decision.

## Stage 7 — Convergence + held-out + package

- **Converge** when the no-progress counter reaches **N=3** consecutive rounds, or the round cap **R=6** total rounds is hit. Otherwise loop back to Stage 1.
- **Held-out**: validate the converged version on the held-out set by rerunning Stage 5's blinding mechanism verbatim on the held-out prompts — byte-identical panel copies to `.claude/evolve/<slug>/panel/held-out/alpha.md` and `beta.md` (no added headers or annotations), the same odd/even round-parity assignment rule (treat the held-out pass as the next round number), and three fresh held-out judges dispatched in parallel, passed ONLY the two neutral panel paths. Fresh held-out judges are the baseline (judges are single-use anyway), NOT an independence layer; an independence layer changes the ruler — a different rubric dimension weighting, or human ground-truth. Write `held-out.md` with the evidence-strength label (`硬證據` only if a ruler-changing independence layer was applied; otherwise `題目泛化證據`). **Regression branch**: if ≥ 2 of 3 held-out judges vote the pre-evolution version `better`, mark the run 未通過 held-out prominently in `report.md`, the result card, and the convergence summary, and offer a rollback to `snapshot/1.md` — a second Authorization PAUSE (never auto-rollback in either direction; non-interactive runs flag the regression and stop there). See `references/output-contract.md`.
- **Package**: write `results.tsv`, `convergence.svg` (the score-over-rounds curve; the effective baseline steps up on keeps only), and `report.md` (start/end score, effectiveness mode + Gate 3 reason, per-axis evidence source) — every artifact lands in `.claude/evolve/<slug>/`. **Make the user-facing surfaces human-readable — draft the convergence summary and the card copy through `/write` (zh), then render the result card through the `/book` entry (never hand-assemble HTML) and copy the `/book` output HTML to `.claude/evolve/<slug>/card.html` (the durable card artifact named in `references/output-contract.md`); see that file's §Human-readable delivery.** Surface the `/write`-refined 繁中 convergence summary, not the raw round-by-round trace. **Lighter exit**: if zero mutations were adopted, skip `/write` + `/book` — report a one-paragraph 繁中 convergence summary in-conversation, omit the result card, and note the omission in `report.md`.

## Provenance + optional engine

The mechanism is concept-aligned with public prior art but re-derived in original wording; run the clean-room checklist in `references/provenance.md` at `../review/SKILL.md` time. The base engine is self-written and the default; `skillopt` is optional, version-pinned, and degrades gracefully when absent — never a silent dependency (`references/provenance.md`).

## Constraints

- Never edit the rubric mid-run; it is the fixed selection environment.
- One dimension per round; keep only strict improvements; restore otherwise.
- Adoption write-back is an Authorization PAUSE on every platform — satisfied interactively, or by a standing authorization in the driving context under the Gate-1 preconditions (structure gate + 3/3 judges + snapshot + audit). Never by a bare default substitution.
- `real-exec-destructive-forbid` — if the Stage 4 real-exec trust gate hits any destructive pattern (`rm` / writing outside the target dir / network writes / secret access) → then force-downgrade to offline and never execute that skill. Actually executing an untrusted skill is irreversible; this prohibition carries the same gated/forbidden rigidity as the `git reset --hard` / `stash` / `clean` / `checkout` red line below.
- Restore is file-level; never touch the git working tree beyond the single target file.
- Mutation-isolation invariant — Stage 2 writes ONLY to the scratch copy. The live target SKILL.md is touched in exactly two sanctioned ways: (a) Stage 3's bounded write-verify-restore window — scratch bytes in, verifier runs, snapshot bytes restored before any Stage 4/5 dispatch; the window is always closed by a restore and never by itself constitutes adoption — and (b) the Stage 6 adoption write-back. Both require the Stage 1 snapshot: if no snapshot/<round>.md exists for the current round → then abort the round before any write to the target.
- The diagnostician and judges are stateless leaf nodes (subagent depth = 1): they never dispatch further subagents or invoke any `/baransu:*` skill. Being dispatched as a subagent does NOT disable this skill's own worker fan-out — the `Agent` tool is always available (probe run a928109). The depth=1 rule here governs the leaf diagnostician/judges this skill dispatches (they never dispatch further), NOT evolve's own ability to fan out its judge panel when evolve is itself hosted as a subagent. evolve is a pure fan-out dispatcher: its adoption gate is the loop-contract Authorization PAUSE plus standing-auth (Gate-1 preconditions), NOT an interactive prompt — the fan-out uses 0 AskUserQuestion calls. Fan-out is released unconditionally and is orthogonal to interactive-capability detection — it is never gated behind an AskUserQuestion proxy.
- All user-visible output is Traditional Chinese (繁體中文).
