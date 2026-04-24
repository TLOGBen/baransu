# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Intent

`baransu` is a Claude Code **plugin marketplace** distributing one governance-focused plugin, also named `baransu`. The plugin's theme is バランス ("balance") — forcing alignment and approval before execution, and surgical multi-perspective verification after. Currently ships four skills: `/think` (deliberate before building), `/review` (independent multi-perspective re-verification of any model output), `/analyze` (goal-anchored spec builder for medium-to-large tasks), and `/dev` (gate-enforced TDD executor for small tasks).

## Actual Layout

```
.claude-plugin/
  marketplace.json             # marketplace catalog — lists distributed plugins
plugins/
  baransu/
    .claude-plugin/
      plugin.json              # plugin manifest (v0.1.7)
    skills/
      think/
        SKILL.md               # governance skill — align/research/approve before code
      review/
        SKILL.md               # governance skill — isolated multi-perspective re-verification
      analyze/
        SKILL.md               # governance skill — goal-anchored spec builder for medium-to-large tasks
      dev/
        SKILL.md               # governance skill — gate-enforced TDD executor for small tasks
    agents/
      architecture-reviewer.md # perspective agent — structural coherence, boundaries, overreach
      quality-reviewer.md      # perspective agent — claim-vs-implementation, logic, edges
      security-reviewer.md     # perspective agent — attack surface, input trust, secrets
```

**Critical distinction**: `.claude-plugin/marketplace.json` at the repo root is the *catalog*; `plugins/baransu/.claude-plugin/plugin.json` is the *plugin manifest*. Never merge them. Component dirs (`skills/`, `agents/`, etc.) go at the **plugin root** (`plugins/baransu/`), not inside `.claude-plugin/` and not at the repo root.

## Skills

### `/baransu:think` — governance (Type 10)

Forces a structured thinking pass before any new-feature / design / architecture code gets written. Produces a 5-section plan (Building / Not building / Approach / Key decisions / Unknowns) gated by explicit user approval via `AskUserQuestion`.

Key design properties to preserve when editing `SKILL.md`:

- **English prose, Chinese output.** Body is agent-readable English; all user-facing output (alignment questions, proposal, plan, AskUserQuestion labels) must be Traditional Chinese.
- **Iron law**: no code, scaffolding, pseudo-code, or directory trees until Stage G approval.
- **Rigid output schema**: the five section titles are contract — downstream tools will parse them verbatim. Do not rename or add sections.
- **Stage ordering encodes dependencies** (e.g. Stage 2's official-solution check feeds Stage 4's Option 1 slot). Do not reorder.
- **Stage G is a four-option gate.** "送 /review 再決定" is 【推薦】 (Option 1); "批准實作（完全授權）" is Option 2. Option 1 handling is a review→think loop: if /review finds substantive gaps, revise the plan via Option 3 mechanism and re-present the gate. Option 2 downstream routing: small task → `/baransu:dev`, medium-large → `/baransu:analyze`.
- **Type 10 governance inverts some Skills BPs**: rigid contract steps are a feature, not railroading. See `ch2-擴充Agent/02-Skills.md` Type 10 section for the rationale.

When iterating on this skill, keep it under 500 lines and avoid putting dynamic strings (timestamps, IDs, paths) in SKILL.md itself — they break prompt cache prefix stability.

### `/baransu:review` — independent multi-perspective verification

Task-analyst + dispatcher. Re-verifies any model output — code diff, file set, directory, /think's approved plan, a bare claim — by dispatching **isolated** perspective agents in clean Task contexts, then triaging findings into four response levels (direct fix / packaged confirm / ask user / FYI).

Key design properties to preserve when editing `review/SKILL.md` or the three agent files:

- **English body, 繁體中文 output.** SKILL.md body is agent-facing English; every user-visible string (headings, questions, report sections) is 繁體中文. Same convention as `/think`. Writing the body in 繁中 is a regression — catch and revert.
- **Goal input is load-bearing.** The main skill derives a one-sentence 繁中 **review goal** in Stage 1 alongside the claim checklist, and passes both to every dispatched reviewer. Without the goal, well-meaning perspectives each find their own zone's issues regardless of relevance and the review bloats. With the goal, the fourth balance-check question — 「是否服務於 goal」 — downgrades off-topic findings to advisory, even when the finding itself is correct. This is the mechanism the skill's own dogfood session exposed as missing; deleting it is a regression.
- **Principle-led, not rule-enumerated.** SKILL.md is ~177 lines of flow + principles, not a legalistic contract. When tempted to add an iron rule, a "What /review is NOT" disclaimer, a verdict enum, or a numeric cap (e.g. "≤4 questions"), first check whether it's defending against a real failure or the author's own anxiety. Most additions lose against the spec's core line: **「複雜度需要證明自己的價值」**. The skill has a dedicated Gotchas section capturing the two symmetric traps (add-too-much / cut-too-much) this drifted into during its own construction — read it before editing.
- **Main skill is pure orchestrator.** No per-perspective review rubric lives in `skills/review/SKILL.md`; those live in `agents/*-reviewer.md`. Main skill owns: flow, dispatch, goal derivation, triage.
- **Agents are perspectives, not personas.** Every `agents/*-reviewer.md` uses `視角 / 目標 / 通用原則 / 禁忌`. Role-play descriptions ("you are a senior …") are banned — they induce hallucination. The original spec asked for the first three; the 禁忌 fourth section earns its place only as a lane-keeper between agents.
- **Activation looks at target behavior, not invocation keywords.** Dispatch decisions depend on what the target actually does (opens a socket, persists data, crosses layers, is a plan document) — never on strings in the user's invocation text.
- **Auto-fix is cosmetic-only.** Formatter / imports / typo / dead-import. Anything semantic — control flow, boundaries, API, state — goes to packaged confirm or needs-judgment.
- **Balance check is mandatory, with four questions.** Every new-work finding must answer: 不做 / 做 / 中間方案 / **是否服務於 goal**. Failing any one downgrades to advisory.
- **E2E hard gate** for code targets: no in-session green-run evidence → results say 「未完成，等 e2e」.

When iterating: keep `review/SKILL.md` lean. If a new iron rule or disclaimer section feels like an obvious addition, that is usually the moment to resist — this skill has already been through one cycle of ballooning to ~270 lines via exactly that pattern before being cut back. The opposite trap is cutting too aggressively and leaving load-bearing mechanisms (like the goal input) implicit; that produced perspective drift the first time around. The safe posture: anything that earns its place on the spec's core principle of **「複雜度需要證明自己的價值」** stays; anything that doesn't, cuts.

### `/baransu:analyze` — spec builder for medium-to-large tasks

Goal-anchored spec generator. Takes a task description, expands it into five spec layers written to `.claude/analyze/{date}-{slug}/`, validates cross-layer alignment with subagents, then hands off to execute.

Key design properties to preserve when editing `analyze/SKILL.md`:

- **English body, 繁體中文 output.** Same convention as `/think` and `/review`.
- **Five layer order is a constraint.** goal → requirement → design → test → task. Each layer depends on the one above for its precision. Do not reorder.
- **test layer is in the review chain.** Three subagents in parallel: Agent 1 (task ↔ test alignment), Agent 2 (test ↔ design alignment), Agent 3 (design ↔ requirement ↔ goal alignment). If test is removed from the chain, task boundary conditions lose their testability anchor.
- **Stage 7 offers /review as handoff option.** The Constraints "Do not call /review" applies to Stages 1-6 only; Stage 7 may invoke /review as a post-spec quality check. These are different questions — alignment vs. quality.
- **Stage 0 lightweight alignment, not /think's three rounds.** /analyze asks for a one-sentence goal and does a scope gate (reject small tasks). It does not replace /think's full alignment ceremony; /think handles direction-uncertain tasks, /analyze handles tasks where the direction is already known.
- **Auto-correct is one round, goal/requirement layers are immutable.** Only design / test / task layers are auto-correctable. goal.md and requirement.md represent user intent and can only change with explicit user confirmation.
- **Cross-layer subagents ≠ /review.** /review asks "what's wrong with this layer?"; /analyze's subagents ask "are these two layers consistent?" Different question, different dispatch, do not conflate.
- **Golden templates embedded in SKILL.md.** Each stage contains a full markdown template for its output file. Preserve template structure — downstream tasks copy these templates.
- **Task sizing rule is explicit.** One task = one session: no cross-group coordination needed, no waiting on other tasks' output, changes in one module layer only.

When iterating: keep `analyze/SKILL.md` under 400 lines. The golden templates take up most of the space — preserve them. The stage instructions should be terse directives, not explanatory prose.

### `/baransu:dev` — gate-enforced TDD executor for small tasks

Receives a concrete task (directly described or handed off from `/think`), builds a TaskCreate checklist upfront, then executes Red→Green with hard gates before invoking `/baransu:review`. Cosmetic-only changes skip Red/Green and go straight to review.

Key design properties to preserve when editing `dev/SKILL.md`:

- **English body, 繁體中文 output.** Same convention as all other skills.
- **All tasks created upfront in Stage 1.** TDD path: 4 tasks (Red test, Red gate, Green impl, Green gate → review). Cosmetic path: 2 tasks (implement, review). Never create tasks mid-execution.
- **Gate logic is hard, not advisory.** Red gate: test must fail — if it passes, stop and report (wrong test, not new behavior). Green gate: fail×1 = auto-retry impl; fail×2 = auto-invoke `/baransu:think` with task goal + two failure summaries + red test code; if /think-assisted resume also fails, stop completely.
- **Compile errors are distinct from test failures.** At Red: compile error = malformed test, stop; does not count toward Green retry limit. At Green: fix and re-run, does NOT count toward the two-attempt limit.
- **Cosmetic classification is final.** Model decides at Stage 0; no re-classification mid-execution. Cosmetic = zero semantic runtime impact.
- **/review only on success.** If the session ends on a failure path, do not invoke /review — there is nothing to review. Review goal = task goal sentence; claim checklist = the task list.
- **Downstream of /think.** /think → /dev is the small-task pipeline. /think → /analyze is the medium-large pipeline. /dev does not read `/analyze`'s task-*.md files — that is the future `/execute` skill's job.

## Install Flow (for testing locally)

```
/plugin marketplace add /home/vakarve/projects/baransu
/plugin install baransu@baransu
/plugin validate                    # or: claude plugin validate
```

Remote install:
```
/plugin marketplace add https://git.hy-tech.com.tw/ben.tsai/baransu.git
/plugin install baransu@baransu
```

## Versioning

`plugins/baransu/.claude-plugin/plugin.json` holds the authoritative `version`. **Bump it on every distributed change** — users won't pick up updates without a version bump due to plugin caching. If a version is also set in `marketplace.json`'s plugin entry, `plugin.json` wins.

## Working Conventions (inherited from the owner's global rules)

These come from `~/.claude/CLAUDE.md` and apply here unless this file overrides them:

- **everything-cli pipeline** (`/panel-review → /eidos → /execute`) is the default for non-trivial changes elsewhere, but **inside this repo** the skill-authoring work is small enough that `/dev-lite` or direct edits are usually appropriate. Note: for designing *new skills within baransu*, dogfood `/baransu:think` itself.
- **Read-before-write**: re-Read any file in the same turn before Edit/Write, even if read earlier in the session.
- **Handoff artifacts** land in `.agent-workspace/handoff/` and are gitignored.
- **Commit style**: conventional commits (`feat:`, `fix:`, `docs:`, …). Attribution lines disabled globally.

## Roadmap (informal)

- `/analyze` shipped in v0.1.6 — goal-anchored spec builder for medium-to-large tasks.
- `/dev` shipped in v0.1.7 — gate-enforced TDD executor for small tasks; downstream of `/think`.
- A `/execute` skill for the `/analyze` downstream is still planned — heavy orchestration, reads task-*.md spec files, injects content into subagents. Different scope from `/dev`. Final design via `/baransu:think` (dogfooding). Do not pre-scaffold it.

## What's Intentionally Absent

- **No build / test / lint commands** — no package manifest or toolchain yet. Do not fabricate `npm test` / `pytest` / similar. Update this section when one is introduced.
- **License**: MIT (see `LICENSE`). Declared in `plugin.json` and `README.md`.
