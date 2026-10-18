---
name: evolve
description: "Improves a SKILL.md round by round, keeping a change only when blind judges and a known-answer exam show it is strictly better at no added cost. Trigger On '$baransu:evolve', '優化 skill', '精簡 skill', 'skill 評分', 'improve skill quality'. Not for writing a new skill, or deciding whether one should exist ($baransu:think)."
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

# evolve — optimize a SKILL.md like you train a model

## Codex Port Adapter - Bundled Agent Resolution

This plugin does not assume package-local TOMLs are auto-registered as custom
agents. The required definitions for this skill are bundled at
`../../.codex-agents/<agent-name>.toml`: `evolve-diagnostician`, `evolve-judge`.

Before every named-agent dispatch:

1. Resolve the exact bundled TOML from this `SKILL.md` directory (strip a
   leading `baransu:` namespace from the requested name).
2. Verify the file exists, then pass its absolute path and the task input to a
   generic Codex subagent. The first instruction to that subagent is to read
   the TOML's `developer_instructions` completely before doing any task work
   and to treat relative paths as relative to the TOML file.
3. If the TOML is missing or unreadable, stop with
   `AGENT_DEFINITION_MISSING: <path>`. Never invent, summarize, or substitute a
   role from the agent name.


The deliverable is an **evolution package**: a target SKILL.md made measurably better through a ratchet that can only turn forward. The rubric is the fixed selection environment, the target SKILL.md is the gene, and an external benchmark is the yardstick. Every change runs one chain — **phenomenon → impact → root → bedrock → verification**: something observed, the user outcome it fails, the clause that causes it, that clause restated as a positive definition where the decision is made, and the evidence that shows the restatement worked. Each link is written or scored by someone who cannot see the answer the next link is judged against.

**Success** is a skill that reads as if it had been this way from the start: it gets at least the results it got before, at no more cost, and it gets there because each step and definition sits in the right place — not because rules were cut or work was skipped. A gain bought with more time or tokens is not an improvement. A positive definition makes the wrong move not arise; a prohibition appended against one failure is a patch. Words are a cost, never a ceiling: a clause the decisions need stays, however long. Every clause proves itself by what it buys: when the work a clause prescribes costs time and produces no result, that falsifies the way it looks at the problem — the clause comes out rather than being strengthened, and the next attempt returns to the last checkpoint known to work, studies how it did the job, and sets out in a different direction.

All user-visible output is in **Traditional Chinese (繁體中文)**.

## Outcome Contract

- **Outcome**: 對目標 SKILL.md 跑只能向前轉的棘輪，每輪沿「現象 → 影響 → 根源 → 基石 → 驗證」找出肇事條文、追回它原本要解的問題，由三份互不相通的種子各自重寫成正面定義、盲選一份，只讓勝者接受盲評與（可實跑時）已知答案的兩次盲考；找回不輸、花費不增才保留，產出每步可追溯、經 held-out 驗證的演化包。
- **Done when**: `.codex/evolve/<slug>/` 內有 `report.md`、`results.tsv`、`log.md`、`decisions.tsv`（已對帳）、`held-out.md`、收斂曲線與成果卡（零採納時成果卡依 Stage 7 較輕出口省略並於 `report.md` 註記），且演化版已過結構閘並經使用者於 Authorization PAUSE 採納或全部回滾。
- **Evidence**: `report.md` 的起訖分數與字數、effectiveness mode（real-exec / offline-同源 / no-benchmark）與 Gate 3 理由、盲考的找回／一致性／雜訊範圍／花費起訖、每軸證據來源與 held-out 證據力標籤；`log.md` 的逐輪 finding（現象／影響／肇事條文／原始問題）、種子盲選分數、勝者基石與 `why_kind`、keep/restore 記錄；`decisions.tsv` 的對帳結果。
- **Output**: `.codex/evolve/<slug>/` 演化包；對話內呈現繁中收斂摘要與成果卡。
- **Automation**: ultracode=overlap, loop=drivable（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）
  In the same non-interactive pass, read `references/loop-pauses.md` for this skill's own PAUSE classification.

## When to use / not

Use when a SKILL.md (or any skill-shaped instruction file) should be measurably improved against a stable rubric. Not for: writing a new skill from scratch (that is authoring, not evolution); one-off prose edits (just edit it); judging whether a skill should exist (a value call — that is `../think/SKILL.md` Route 1 存廢判決 (Kill/Keep/Pivot)).

## The five pillars (do not weaken)

1. **Single editable asset, single decision** — one target SKILL.md, one decision per round: one clause replaced, deleted, or merged with the clause it absorbs, or — when no clause explains the phenomenon — one positive definition added. This is what makes every improvement attributable.
2. **Bedrock, not patches** — every round starts from an observed phenomenon and the clause it implicates; the mutation restates that clause, and the operation it uses (add / delete / merge / replace, or keep as is) is the one the evidence supports over the other three (`references/seed-hunt.md` §Operations).
3. **Dual evaluation** — structure axis (static rubric reading) and effectiveness axis: a blind known-answer exam when the skill can run (`references/exam.md`), offline replay otherwise. See `references/rubric-9dim.md`.
4. **Evaluation independence is the lifeline** — whoever sees the answers writes no mutation; seed authors and examinees never see the answers; exam scorers and judges never know which version is which; the seed picker never decides keep. Every judge is fresh and single-use.
5. **Fixed rubric = selection environment; SKILL.md = gene; external benchmark = yardstick.** Never edit the rubric mid-run.

## Stage 0 — Target, slug, work dir, exam

1. Resolve the target SKILL.md path. Derive `<slug>` from the skill name.
2. Only when the proposed candidate came from a conversation, incident, external repository or release log, or private memory, apply `../_shared/distillation-candidate-matrix.md` after target resolution and before any workdir, snapshot, panel, or report write. Ordinary rubric wording or structure runs skip this gate and retain the existing flow. Only `PROMOTE: shared-skill` with this exact resolved target may enter Stage 1. For `REROUTE`, `DEFER`, or `REJECT`, stop before durable writes and state `候選處置：{PROMOTE|REROUTE|DEFER|REJECT} — {一行理由}`; never mutate another owner layer or add a package artifact or report field.
3. Create `.codex/evolve/<slug>/` with a `snapshot/` subdir, and open `decisions.tsv` — one line per decision for the whole run (`references/output-contract.md`).
4. Read `references/rubric-9dim.md` (the selection environment), `references/safety-gates.md` (the red lines), `references/provenance.md` §Clause provenance (how a clause's original problem is recovered), and `references/seed-hunt.md` (how a round's bedrock is written and picked). All four are loaded once and held constant for the whole run.
5. Locate or build the benchmark `test-prompts`, split into **train** (drives the loop) and **held-out** (final validation only) by this rule: the held-out set keeps at least 1 prompt and about 1/3 of all benchmark prompts (round up), and held-out prompts stay invisible to the evolution loop (Stages 1–6) until Stage 7 — feeding every prompt into the loop hollows out held-out validation. If the target has no benchmark, pause and ask the user for 2–3 prompts; the system fills a skeleton for confirmation — never fabricate the pass criteria. **If the user declines or no benchmark is confirmed → then run the loop structure-axis-only: hard-label dims 7–9 as `no-benchmark` (unscored, never assumed) in `report.md`, and skip Stage 7's held-out validation (there is no held-out set). Do not silently proceed as if effectiveness were measured.** A prompt may carry an **answer key** — what a correct run finds, what counts as partial, what costs points — written or confirmed by the user, never generated by evolve. When Gate 3 will allow real-exec, set up the exam once per `references/exam.md` §Setup: the keys, the case-term list, the fixed exam template and its hash.

### Orchestration interface (dual-mode)

When — and only when — the run is Workflow-driven or a system-reminder confirms
ultracode, read `references/orchestration-interface.md` before Stage 1 and apply
its adapter contract; on the default interactive path, skip the read and write no
mode record — the absence of a mode record means the current (parallel-subagent)
adapter. On the Workflow path, pin the mode at Stage 0 (record to disk, no mid-run
switch); the read happens once — never re-read before a Stage-5 judge panel. Both
adapters return identical votes; the Stage 5 tally never senses the mode.

## Stage 1 — Snapshot + diagnose

1. Snapshot the target file's bytes to `snapshot/<round>.md` (file-level; see `references/safety-gates.md` Gate 2).
2. Assemble the round's evidence: the current version's exam sheet or effectiveness outputs on the **train** prompts (Stage 4 of the previous round; in round 1, run Stage 4 once on the unmodified target as the baseline) — an item found in only one of the two runs counts as a phenomenon, since the text did not lead to it; any incident the user brought; the run's `log.md` so far, including ideas a losing seed left for later.
3. Dispatch the **evolve-diagnostician** agent in diagnose mode with the target path, the rubric, `references/provenance.md`, `log.md`, and the evidence. It scores all 9 dimensions (for `results.tsv`) and returns exactly one **finding** in the shape fixed in `agents/evolve-diagnostician.md`: the phenomenon and its evidence; its impact on the outcome the target's user asked for; the root — the implicated clause (or `none` after a whole-skill read), its flaw (principle / contradiction / side effect / unstated subject / falsified direction), the problem it was added to solve with its source; for a falsified direction, the checkpoint to return to; the verification that would show a fix worked; and the **brief** for the seeds, which states phenomenon, impact and root in general terms — no answer-key item, no case term, no proposed wording. The diagnostician has seen the answers, so it writes no replacement.
4. If the diagnostician returns `finding: none` → then log `decision: no-finding`, count the round as no-progress, and go to Stage 7's convergence check. Never manufacture a weakness from the lowest-scoring dimension — a skill with no observed failure is a valid result, not an empty round.

## Stage 2 — Seed, pick blind, refine the winner

Run `references/seed-hunt.md`: three fresh seed authors receive the same brief, the target path, the rubric and `references/provenance.md`, and nothing else; each returns one bedrock — the operation, the exact text, and one `why_kind` line on why that operation beats the other three. Each seed is applied to its own scratch copy and passes Stage 3's subtraction and case-term gates before the pick; the survivors are shuffled under neutral letters and ranked by one fresh evolve-judge in rank mode. Only the winner continues. It may be refined in wording so it applies cleanly — the implicated clause out, the bedrock in; for `delete`, the clause out; for `merge`, both clauses out and the merged sentence in; for `add`, the new clause in — never by splicing in a losing seed's idea. Do not improve neighbouring prose, because the judges compare whole files and a second change makes the vote unattributable. Record `words_before` → `words_after` for `log.md`.

## Stage 3 — Mechanical gates (before any judging matters)

**Subtraction gate** (each seed; touches nothing): `diff snapshot/<round>.md <scratch>`. If the diff removes or rewrites no existing non-blank line → then refuse the seed unless its operation is `add` and the finding's `implicated` is `none`; log `decision: append-only-refused`. No judge sees an append-only candidate for a phenomenon an existing clause already explains.

**Case-term gate** (each seed; touches nothing): when the run has a case-term list, grep the lines the diff adds for any listed term (whole word, case-insensitive). A hit → refuse the seed, log `decision: case-term-refused`. A bedrock that names the exam has learned the exam, not the skill. The brief takes the same grep before any seed sees it; a brief that hits goes back to a fresh diagnostician once with the hit terms named, and a second hit ends the round as `case-term-refused`. If no seed survives both gates → log `decision: no-surviving-seed` and skip to Stage 6's restore accounting.

**Structure gate** (the winner only): repo-mode verify-skills scans only the live skills tree — a scratch copy is invisible to it — so the gate runs as a bounded **write-verify-restore** window on the target path: (1) confirm `snapshot/<round>.md` exists (no snapshot → abort the round, no write); (2) write the scratch bytes to the target path; (3) run `python3 scripts/verify-skills.py` (no argument — repo mode) and read the mutated skill's line in the output; (4) restore the snapshot bytes to the target path immediately, pass or fail, before any Stage 4/5 dispatch. **Interruption recovery**: at the start of every Stage 1 round (including a resumed run after an interruption), if the live target's bytes ≠ the latest `snapshot/<round>.md` and `log.md` carries no matching adoption entry → then restore the snapshot bytes to the target and log `decision: window-breach-restored` in `log.md` before any diagnosis — an interruption between step (2) and step (4) otherwise leaves mutation bytes live and silently bypasses the ratchet's restore guarantee. The window is sanctioned by the mutation-isolation invariant (Constraints below) and never by itself constitutes adoption. Do **not** pass the skill dir as an argument: verify-skills treats its arg as a skills-root to iterate, so the single-dir form mis-scans the skill's own `references/` / `scripts/` subdirs as skills and emits a false `references: 缺 SKILL.md` failure (this breaks every skill-with-`references/`, including evolve itself). **Keep is only possible** if exit code is 0 **and** stdout carries no `⚠️ ADVISORY` line (a body-bloat advisory returns exit 0 but must be read and treated as a failure). On failure: the snapshot is already restored by step (4) — skip to Stage 6's restore accounting; this round produced nothing. Score never overrides structure (`references/safety-gates.md` Gate 4). **Degraded gate**: if the target is not governed by a repo `scripts/verify-skills.py` (any non-baransu skill — the script's constants pin it to its own checkout), do not run it against the wrong repo; degrade to a declared minimal mechanical check on the scratch copy — frontmatter parses, name/description limits hold, body-line advisory — and label the gate `degraded-gate` in `report.md`.

## Stage 4 — Effectiveness axis (real-exec exam or offline)

Score the effectiveness dimensions (7–9). Decide real-exec vs offline via the **trust + capability dual gate** (`references/safety-gates.md` Gate 3):
- **Capability gate** — the target's declared `Automation: loop=` value decides: only `drivable` runs unattended; `assisted`, `not-drivable`, or no value → offline.
- **Trust gate** — only user-owned-path skills with no destructive-pattern hit run for real; unknown/third-party/pattern-hit → offline.
- **Destructive-pattern red line (`real-exec-destructive-forbid`)** — if the real-exec trust gate hits ANY destructive pattern (`rm` / writing files outside the target directory / network writes / secret access) → then force-downgrade to offline and NEVER execute that skill. This is a hard if-then prohibition with the same rigidity as the git-tree red line, not advice: actually executing an untrusted skill is the genuinely irreversible destructive surface, so it is forbidden, not merely flagged. When real-exec does run (no destructive pattern, trust + capability both clear), mark it untrusted in the report and rotate memory after the run. When offline, the effectiveness output is same-source as the structure axis → label it `offline-同源` and treat its evidence as single-axis.

When real-exec runs, the winner sits the exam in `references/exam.md`: every train prompt runs twice (a, b), each run a fresh examinee given only the fixed template with the prompt and a read-only copy of the version; one fresh evolve-judge in exam mode scores the winner's outputs and the current version's outputs together under neutral labels against the answer keys. The exam sheet gives each version its recall over both runs, the items found in only one run, penalties, mean tokens and wall time, and the noise band — the larger of the two versions' own a–b spreads.

## Stage 5 — Blind judge panel

Blind the panel mechanically, not by instruction alone: copy the pre- and post-mutation versions to `.codex/evolve/<slug>/panel/round-<N>/alpha.md` and `beta.md` (byte-identical copies — no added headers or annotations that could mark which is which), and relabel the exam sheet to the same alpha/beta mapping. Round parity decides the assignment (odd rounds: mutation = alpha; even rounds: mutation = beta), cancelling position bias; the mapping is never disclosed to judges. Then dispatch **three fresh evolve-judge agents in parallel** in pair mode, passing ONLY the two neutral panel paths and the relabelled sheet — never the live skill path or the scratch path, whose names leak which version is the mutation. Each judge returns `{better, strict_improvement, per_dimension_deltas}`. Judges are single-use — never reuse a judge across rounds. Length is scored inside the rubric (dim 5 Economy: equal decisions → the shorter version wins), so a pure simplification can clear the strict bar and a pure addition pays for its words; the orchestrator adds no length rule of its own.

**Keep iff ≥ 2 of 3 judge strict_improvement = true** — 3 of 3 when the effectiveness axis ran via real-exec — **and**, when the exam ran, the mutation's recall is not below the current version's by more than the noise band and its mean tokens and wall time are not above the current version's by more than the noise band: a gain bought with cost is not kept. If any of the three judges fails to return a well-formed `{better, strict_improvement, per_dimension_deltas}` vote (crash, timeout, or malformed payload) → then record that vote as `strict_improvement=false` (a non-vote never counts toward keep); it still counts as a cast vote, the tally always runs over exactly 3 votes, and re-dispatch is never attempted. A kept `delete` or `merge` whose flaw cannot be read from the text alone (a contradiction, a dangling reference, an exact restatement) counts as ablated only when the exam ran; otherwise it is labelled `未經消融` in `log.md`, `report.md` and the adoption view, and Stage 7's held-out is its deferred ablation.

## Stage 6 — Adoption (Authorization PAUSE) or restore

- If kept: adoption is an **Authorization PAUSE** (`references/safety-gates.md` Gate 1), satisfied one of two ways. **(a) Interactive or non-interactive without standing authorization** → present the diff + score delta + word delta (and the exam's recall and cost delta when it ran) and halt; write back only on explicit user adoption. **(b) Non-interactive WITH a standing authorization** recorded in the driving context (the loop/cron prompt or approved plan explicitly authorizes adoption / the evolve→ship sweep) → auto-adopt, but only for a change that clears every Gate-1 precondition (structure gate pass, blind-judge bar tightened to **3/3**, snapshot retained, `log.md` audit with `decision: standing-auth auto-adopt`); a change failing any precondition is restored, never written. The structure gate (`python3 scripts/verify-skills.py`) is the end-state arbiter for downstream steps. After any write-back, re-read the target (the baseline changed) and reset the no-progress counter. **If the user declines adoption** → discard the scratch (the next diagnostician round starts from the unchanged target), leave the target untouched, log `decision: user-declined`, and continue to Stage 7's convergence check.
- If not kept (judges, exam, subtraction or case-term gate, structure gate, or restore path): restore the snapshot to the target file. File-level only — never `git reset --hard` / `stash` / `clean` / `checkout`.
- The no-progress counter advances on every round that adopts nothing (no-finding, refused or surviving no gate, structure-gate failure, judges, exam, user-declined); Stage 7 converges at N=3 consecutive.
- Append a `log.md` entry either way — round #, the finding, the seeds and the pick, the winner's bedrock and `why_kind`, gate results, exam sheet, votes, decision — in the shape in `references/output-contract.md`, and the round's `decisions.tsv` lines, covering what `references/output-contract.md` lists for that file.

## Stage 7 — Convergence + held-out + package

- **Converge** when the no-progress counter reaches **N=3** consecutive rounds, or the round cap **R=6** total rounds is hit. Otherwise loop back to Stage 1.
- **Held-out**: validate the converged version on the held-out set by rerunning Stage 5's blinding mechanism verbatim on the held-out prompts — byte-identical panel copies to `.codex/evolve/<slug>/panel/held-out/alpha.md` and `beta.md` (no added headers or annotations), the same odd/even round-parity assignment rule (treat the held-out pass as the next round number), and three fresh held-out judges dispatched in parallel, passed ONLY the two neutral panel paths and, when the exam ran, the held-out exam sheet (same template, two runs per prompt). Fresh held-out judges are the baseline (judges are single-use anyway), NOT an independence layer; an independence layer changes the ruler — a different rubric dimension weighting, or human ground-truth. Write `held-out.md` with the evidence-strength label (`硬證據` only if a ruler-changing independence layer was applied; otherwise `題目泛化證據`). **Regression branch**: if ≥ 2 of 3 held-out judges vote the pre-evolution version `better`, mark the run 未通過 held-out prominently in `report.md`, the result card, and the convergence summary, and offer a rollback to `snapshot/1.md` — a second Authorization PAUSE (never auto-rollback in either direction; non-interactive runs flag the regression and stop there). See `references/output-contract.md`.
- **Reconcile** `decisions.tsv` before packaging: every evidence pointer resolves, every keep/restore in `log.md` has its line, and every user instruction in the conversation that changed the run has one; list each mismatch in `report.md`.
- **Package**: write `results.tsv`, `convergence.svg` (the score-over-rounds curve; the effective baseline steps up on keeps only), and `report.md` (start/end score and word count, change-kind tally, effectiveness mode + Gate 3 reason, start/end exam recall and cost, per-axis evidence source) — every artifact lands in `.codex/evolve/<slug>/`. **Make the user-facing surfaces human-readable — draft the convergence summary and the card copy through `$baransu:write` (zh), then render the result card through the `$baransu:draw` page lane (never hand-assemble HTML) and copy the `$baransu:draw` output HTML to `.codex/evolve/<slug>/card.html` (the durable card artifact named in `references/output-contract.md`); see that file's §Human-readable delivery.** Surface the `$baransu:write`-refined 繁中 convergence summary, not the raw round-by-round trace. **Lighter exit**: if zero mutations were adopted, skip `$baransu:write` + `$baransu:draw` — report a one-paragraph 繁中 convergence summary in-conversation, omit the result card, and note the omission in `report.md`.

## Provenance + optional engine

The mechanism is concept-aligned with public prior art but re-derived in original wording; run the clean-room checklist in `references/provenance.md` at `../review/SKILL.md` time. The same file's §Clause provenance is what the diagnostician uses to recover a clause's original problem. The base engine is self-written and the default; `skillopt` is optional, version-pinned, and degrades gracefully when absent — never a silent dependency (`references/provenance.md`).

## Constraints

- Never edit the rubric mid-run; it is the fixed selection environment.
- One decision per round; keep only strict improvements that lose no recall and add no cost; restore otherwise. An append-only candidate reaches the panel only as an `add` for a phenomenon no clause explains.
- The answer keys stay with the exam scorer and the panel: no brief, seed author, or examinee sees them, and the exam template is the examinee's whole prompt.
- Adoption write-back is an Authorization PAUSE on every platform — satisfied interactively, or by a standing authorization in the driving context under the Gate-1 preconditions (structure gate + 3/3 judges + snapshot + audit). Never by a bare default substitution.
- `real-exec-destructive-forbid` — if the Stage 4 real-exec trust gate hits any destructive pattern (`rm` / writing outside the target dir / network writes / secret access) → then force-downgrade to offline and never execute that skill. Actually executing an untrusted skill is irreversible; this prohibition carries the same gated/forbidden rigidity as the `git reset --hard` / `stash` / `clean` / `checkout` red line below.
- Restore is file-level; never touch the git working tree beyond the single target file.
- Mutation-isolation invariant — Stage 2 writes ONLY to scratch copies. The live target SKILL.md is touched in exactly two sanctioned ways: (a) Stage 3's bounded write-verify-restore window — scratch bytes in, verifier runs, snapshot bytes restored before any Stage 4/5 dispatch; the window is always closed by a restore and never by itself constitutes adoption — and (b) the Stage 6 adoption write-back. Both require the Stage 1 snapshot: if no snapshot/<round>.md exists for the current round → then abort the round before any write to the target.
- The diagnostician, seed authors, the exam scorer and judges are stateless leaf nodes (subagent depth = 1): they never dispatch further subagents or invoke any `/baransu:*` skill. An examinee is the skill under test, not a leaf: it follows the read-only copy, including the agents that copy dispatches, and never invokes the installed skill. Being dispatched as a subagent does NOT disable this skill's own worker fan-out — the `Agent` tool is always available (probe run a928109). The depth=1 rule here governs the leaf agents this skill dispatches (they never dispatch further), NOT evolve's own ability to fan out its seeds, exam and judge panel when evolve is itself hosted as a subagent. evolve is a pure fan-out dispatcher: its adoption gate is the loop-contract Authorization PAUSE plus standing-auth (Gate-1 preconditions), NOT an interactive prompt — the fan-out uses 0 user-question calls. Fan-out is released unconditionally and is orthogonal to interactive-capability detection — it is never gated behind a user-question proxy.
- All user-visible output is Traditional Chinese (繁體中文).
