# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Intent

`baransu` is a Claude Code **plugin marketplace** distributing one governance-focused plugin, also named `baransu`. The plugin's theme is バランス ("balance") — forcing alignment and approval before execution, and surgical multi-perspective verification after. Currently ships seven skills: `/think` (deliberate before building), `/review` (independent multi-perspective re-verification of any model output), `/analyze` (goal-anchored spec builder for medium-to-large tasks), `/dev` (gate-enforced TDD executor for small tasks), `/write` (bilingual zh/en copywriting assistant), `/execute` (TDAID orchestration engine for medium-to-large tasks; reads `/analyze` spec, drives parallel worktrees via agent-only skills, produces `final-report.md`), and `/ship` (session cleanup — archive work files, commit, push, optional worktree removal).

## Actual Layout

```
.claude-plugin/
  marketplace.json             # marketplace catalog — lists distributed plugins
plugins/
  baransu/
    .claude-plugin/
      plugin.json              # plugin manifest (v0.3.1)
    skills/
      think/
        SKILL.md               # governance skill — align/research/approve before code
      review/
        SKILL.md               # governance skill — isolated multi-perspective re-verification
      analyze/
        SKILL.md               # governance skill — goal-anchored spec builder for medium-to-large tasks
      dev/
        SKILL.md               # governance skill — gate-enforced TDD executor for small tasks
      write/
        SKILL.md               # copywriting skill — bilingual zh/en Refine + Generate assistant
      execute/
        SKILL.md               # orchestration skill — TDAID engine for medium-to-large tasks
      ship/
        SKILL.md               # cleanup skill — archive, commit, push, optional worktree removal
    agents/
      architecture-reviewer.md # perspective agent — structural coherence, boundaries, overreach
      quality-reviewer.md      # perspective agent — claim-vs-implementation, logic, edges
      security-reviewer.md     # perspective agent — attack surface, input trust, secrets
      summarize-agent.md       # execute agent — extracts 8-field task context from spec
      impl-agent.md            # execute agent — Red/Green TDD implementation cycle
      review-agent.md          # execute agent — four-tier semantic review (direct impl, no /review call)
      smart-friend-agent.md    # execute agent — root-cause diagnosis after 2 consecutive failures
      e2e-fix-agent.md         # execute agent — fixes E2E failure clusters
      final-review-agent.md    # execute agent — REQ-XXX coverage verification
      final-fixer-agent.md     # execute agent — supplements missing tests/impl for uncovered REQs
      merge-agent.md           # execute agent — git merge + Green confirmation for parallel worktrees
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

### `/baransu:review` — independent multi-perspective verification

Task-analyst + dispatcher. Re-verifies any model output — code diff, file set, directory, /think's approved plan, a bare claim — by dispatching **isolated** perspective agents in clean Task contexts, then triaging findings into four response levels (direct fix / packaged confirm / ask user / FYI).

Key design properties to preserve when editing `review/SKILL.md` or the three agent files:

- **English body, 繁體中文 output.** SKILL.md body is agent-facing English; every user-visible string (headings, questions, report sections) is 繁體中文. Same convention as `/think`. Writing the body in 繁中 is a regression — catch and revert.
- **Goal input is load-bearing.** The main skill derives a one-sentence 繁中 **review goal** in Stage 1 alongside the claim checklist, and passes both to every dispatched reviewer. Without the goal, well-meaning perspectives each find their own zone's issues regardless of relevance and the review bloats. With the goal, the fourth balance-check question — 「是否服務於 goal」 — downgrades off-topic findings to advisory, even when the finding itself is correct. Deleting it is a regression.
- **Principle-led, not rule-enumerated.** SKILL.md is ~177 lines of flow + principles, not a legalistic contract. The skill has a dedicated Gotchas section capturing two symmetric traps (add-too-much / cut-too-much) — read it before editing.
- **Main skill is pure orchestrator.** No per-perspective review rubric lives in `skills/review/SKILL.md`; those live in `agents/*-reviewer.md`. Main skill owns: flow, dispatch, goal derivation, triage.
- **Agents are perspectives, not personas.** Every `agents/*-reviewer.md` uses `視角 / 目標 / 通用原則 / 禁忌`. Role-play descriptions ("you are a senior …") are banned — they induce hallucination.
- **Activation looks at target behavior, not invocation keywords.**
- **Auto-fix is cosmetic-only.** Anything semantic goes to packaged confirm or needs-judgment.
- **Balance check is mandatory, with four questions.** Every new-work finding must answer: 不做 / 做 / 中間方案 / **是否服務於 goal**. Failing any one downgrades to advisory.
- **E2E hard gate** for code targets: no in-session green-run evidence → results say 「未完成，等 e2e」.
- **Re-read before Stage 6 (Core constraints).** Stage 6 consolidation is the single moment most vulnerable to attention decay in a /review session — the four balance-check questions and tier definitions must be recalled precisely there. Single-layer protection (Core constraints only) is intentional: /review sessions are short and rarely trigger more than one auto-compact, so dual-layer would be overhead without benefit.

### `/baransu:analyze` — spec builder for medium-to-large tasks

Goal-anchored spec generator. Takes a task description, expands it into five spec layers written to `.claude/analyze/{date}-{slug}/`, validates cross-layer alignment with subagents, then hands off to execute.

Key design properties to preserve when editing `analyze/SKILL.md`:

- **English body, 繁體中文 output.** Same convention as `/think` and `/review`.
- **Five layer order is a constraint.** goal → requirement → design → test → task. Each layer depends on the one above for its precision. Do not reorder.
- **test layer is in the review chain.** Three subagents in parallel: Agent 1 (task ↔ test alignment), Agent 2 (test ↔ design alignment), Agent 3 (design ↔ requirement ↔ goal alignment).
- **Stage 6 dispatch passes path + required-file-list per agent; agents self-read.** Agent 1 reads `task-*.md` + `test.md`; Agent 2 reads `test.md` + `design.md`; Agent 3 reads `design.md` + `requirement.md` + `goal.md`. Main skill does not pre-read or inline spec content — each agent loads only what its review question needs.
- **Stage 7 offers /review as handoff option.** The Constraints "Do not call /review" applies to Stages 1-6 only; Stage 7 may invoke /review as a post-spec quality check.
- **Auto-correct is one round, goal/requirement layers are immutable.** Only design / test / task layers are auto-correctable.
- **Cross-layer subagents ≠ /review.** /review asks "what's wrong with this layer?"; /analyze's subagents ask "are these two layers consistent?" Different question, do not conflate.
- **Golden templates embedded in SKILL.md.** Preserve template structure — downstream tasks copy these templates.
- **Task sizing rule is explicit.** One task = one session: no cross-group coordination needed, no waiting on other tasks' output, changes in one module layer only.

### `/baransu:dev` — gate-enforced TDD executor for small tasks

Receives a concrete task (directly described or handed off from `/think`), builds a TaskCreate checklist upfront, then executes Red→Green with hard gates before invoking `/baransu:review`. Cosmetic-only changes skip Red/Green and go straight to review.

Key design properties to preserve when editing `dev/SKILL.md`:

- **English body, 繁體中文 output.** Same convention as all other skills.
- **All tasks created upfront in Stage 1.** TDD path: 4 tasks (Red test, Red gate, Green impl, Green gate → review). Cosmetic path: 2 tasks (implement, review). Never create tasks mid-execution.
- **Gate logic is hard, not advisory.** Red gate: test must fail — if it passes, stop and report (wrong test, not new behavior). Green gate: fail×1 = auto-retry impl; fail×2 = auto-invoke `/baransu:think` with task goal + two failure summaries + red test code; if /think-assisted resume also fails, stop completely.
- **Compile errors are distinct from test failures.** At Red: compile error = malformed test, stop. At Green: fix and re-run, does NOT count toward the two-attempt limit.
- **Cosmetic classification is final.** Model decides at Stage 0; no re-classification mid-execution. Cosmetic = zero semantic runtime impact.
- **/review only on success.** If the session ends on a failure path, do not invoke /review.
- **Downstream of /think.** /think → /dev is the small-task pipeline. /think → /analyze is the medium-large pipeline. /dev does not read `/analyze`'s task-*.md files — that is `/execute`'s job.

### `/baransu:write` — bilingual copywriting assistant (zh/en)

Accepts a language prefix (`zh`/`en`) or auto-detects from content. Classifies input as Refine (existing text → Before/After with rule annotations) or Generate (request prompt → finished piece with format/tone note). Applies embedded rule sets: zh uses sparanoid compact rules (spacing, punctuation, numbers, proper nouns); en uses four core English copywriting rules (Oxford comma, active voice, sentence length ≤25 words, parallel structure).

Key design properties to preserve when editing `write/SKILL.md`:

- **English body, exception output.** Content output is in the language specified by prefix or auto-detection. Operational notifications remain Traditional Chinese. This exception must be declared in an explicit `User-facing language` section in SKILL.md.
- **Prefix determines both rule set and output language simultaneously.** `zh` = zh rules + zh output; `en` = en rules + en output. These cannot be set independently.
- **Prefix-content mismatch: Refine stops, Generate continues.**
- **Mode detection: refine keyword + existing body beats imperative tone.** Uncertainty defaults to Generate.
- **Vague topic fallback in Generate: topic ambiguous, not format absent.**
- **Writing style principles in `references/writing-principles.md`** (BP4 progressive disclosure): both Refine and Generate read this file on demand. Do not embed these principles in SKILL.md.
- **Single-pass only.** No iterative loop; user re-invokes for adjustments.

### `/baransu:execute` — TDAID orchestration engine for medium-to-large tasks

Reads an `/analyze` spec directory, builds a dependency DAG, classifies XL/L/M, drives each task group through a Summarize→Impl→Review while-loop via 8 agent-only skill files, handles blocking and smart-friend escalation, runs E2E and Final-Review, then writes `final-report.md`.

Key design properties to preserve when editing `execute/SKILL.md` or the agent files:

- **English body, 繁體中文 output.** Same convention as all other skills.
- **Analyze spec directory is strictly read-only.** No Edit/Write under `.claude/analyze/`. This is enforced as a structural blocker (Stage 0), not just advisory. Do not weaken it.
- **Subagent depth = 1.** The 8 `agents/*.md` files are designed for depth-1 dispatch only — they cannot themselves dispatch parallel Tasks + AskUserQuestion. `review-agent.md` in particular MUST implement four-tier semantics directly; it must NOT call `/baransu:review`. That would violate the depth limit.
- **All Task Tool entries created before execution begins.** Stage 2 registers every group × task via TaskCreate before Stage 3 starts. No mid-execution task creation.
- **failure_count semantics are precise.** Compile errors do NOT count. Packaged confirm (quality) does NOT count (triggers refactor pass for L/XL only). Only packaged confirm (correctness) and needs-judgment count. smart-friend dispatched at count==2; BLOCKED at count==3.
- **Merge retry cap = 2.** After 2 ⚠️ Green-broken merge retries, block downstream and escalate.
- **cascade-blocked propagation is explicit.** After any task is BLOCKED, Stage 4d checks downstream groups and marks them cascade-blocked. Report separates direct-blocked from cascade-blocked.
- **pre-scan is advisory only.** File overlap between parallel groups generates a warning in task-map.md; prefer the no-overlap assumption when descriptions are ambiguous.
- **final-fixer runs once.** If Final-Review still `needs_fixer: true` after one fixer pass, record remaining gaps as blocked and proceed to Stage 7.
- **agent files follow established pattern.** YAML frontmatter (name, description, tools) + `視角 / 目標 / 通用原則 / 禁忌`. No role-play persona descriptions. Fixed static content at file HEAD for prompt cache stability.
- **Re-read at Stage 4/5/6 entry (Core constraints + stage-adjacent checkpoints).** /execute sessions are long and survive multiple auto-compacts. Dual-layer protection: Core constraints (global, survives compacts) + stage-adjacent re-read checkpoint at Stage 4 (before 4a), Stage 5, and Stage 6 entry. At each checkpoint, confirm: `failure_count`/`compile_error_count` semantics, cascade-blocked propagation, merge_retry_count cap, E2E single-retry limit, Final-Review single-fixer limit.

### `/baransu:ship` — session cleanup

Archives work directories, commits all changes, pushes to origin, and optionally removes the current git worktree. Fully automatic — no user confirmation.

Key design properties to preserve when editing `ship/SKILL.md`:

- **English body, 繁體中文 output.** Same convention as all other skills.
- **Archive scope is fixed.** `.claude/tmp/`, `.claude/analyze/`, `.claude/execute/` only. Do not make this configurable — selective archiving belongs to the user's own workflow.
- **Step 1 is the empty-state gate.** If all three source directories are empty or absent, output a message and stop. Do not commit or push an empty session.
- **Collision suffix is deterministic.** Timestamp suffix (`-{unix_timestamp}`) resolves name collisions in `.claude/archived/` without interactive prompts.
- **Worktree cleanup is conditional on detection.** Only executes when `git rev-parse --git-dir` output contains `.git/worktrees/`. Branch deletion after worktree removal is part of the same step.

## 禁止事項

- **絕對不許** 在 `plugin.json` 加 `skills` array：Claude Code 用 filesystem 自動發現 skills，`v0.3.0` 曾誤加隨即移除。
- **絕對不許** `review-agent` 呼叫 `/baransu:review`：subagent 深度 = 1 硬性限制，必須直接實作四層語義；呼叫會觸發 AskUserQuestion + parallel Tasks，違反深度限制。
- **不許** 在 `/ship` Step 5 用 `git branch -d`：push 後未 merge，`-d` 必然失敗；兩個子命令都要 `git -C "$MAIN_REPO"` + `-D`。
- **不許** 簡化 `failure_count` / `compile_error_count` 的區分：compile error 不計入 failure_count，這個語義不能被「優化」掉，否則 TDAID loop 重試行為會錯誤。

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

- **Search First**: before creating any new skill, agent, or pattern, search `plugins/baransu/skills/` and `plugins/baransu/agents/` for existing implementations. Re-use and adapt before creating from scratch.
- **everything-cli pipeline** (`/panel-review → /eidos → /execute`) is the default for non-trivial changes elsewhere, but **inside this repo** skill-authoring work is small enough that direct edits are usually appropriate. For designing *new skills within baransu*, dogfood `/baransu:think` itself.
- **Read-before-write**: re-Read any file in the same turn before Edit/Write, even if read earlier in the session.
- **Handoff artifacts** land in `.agent-workspace/handoff/` and are gitignored.
- **Commit style**: conventional commits (`feat:`, `fix:`, `docs:`, …). Attribution lines disabled globally.
- **CLAUDE.md size target**: keep under 200 lines. If it grows beyond that, trim advisory prose before adding new content.

## Roadmap (informal)

- `/analyze` shipped in v0.1.6 — goal-anchored spec builder for medium-to-large tasks.
- `/dev` shipped in v0.1.7 — gate-enforced TDD executor for small tasks; downstream of `/think`.
- `/write` shipped in v0.1.9 — bilingual zh/en copywriting assistant; Refine + Generate dual-mode; language prefix controls both rule set and output language.
- `/execute` shipped in v0.3.0 — TDAID orchestration engine for the `/analyze` downstream. Reads `task-*.md` spec files, classifies XL/L/M via DAG BFS, drives parallel worktrees via 8 agent-only skill files, runs E2E and Final-Review, produces `final-report.md`. Spec designed via `/baransu:think` + `/baransu:analyze` dogfood.
- `/ship` shipped in v0.3.1 — session cleanup skill. Archives `.claude/tmp/` + `.claude/analyze/` + `.claude/execute/` to `.claude/archived/`, commits all pending changes, pushes to origin, removes the current git worktree if detected. Designed via `/baransu:think` dogfood.

## What's Intentionally Absent

- **No build / test / lint commands** — no package manifest or toolchain yet. Do not fabricate `npm test` / `pytest` / similar. Update this section when one is introduced.
- **License**: MIT (see `LICENSE`). Declared in `plugin.json` and `README.md`.
