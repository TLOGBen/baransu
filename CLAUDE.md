# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Intent

`baransu` is a Claude Code **plugin marketplace** distributing one governance-focused plugin, also named `baransu`. The plugin's theme is バランス ("balance") — forcing alignment and approval before execution, and surgical multi-perspective verification after. Currently ships two skills: `/think` (deliberate before building) and `/review` (independent multi-perspective re-verification of any model output).

## Actual Layout

```
.claude-plugin/
  marketplace.json             # marketplace catalog — lists distributed plugins
plugins/
  baransu/
    .claude-plugin/
      plugin.json              # plugin manifest (v0.2.0)
    skills/
      think/
        SKILL.md               # governance skill — align/research/approve before code
      review/
        SKILL.md               # governance skill — isolated multi-perspective re-verification
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
- **Iron law**: no code, scaffolding, pseudo-code, or directory trees until Stage 8 approval.
- **Rigid output schema**: the five section titles are contract — downstream tools will parse them verbatim. Do not rename or add sections.
- **Stage ordering encodes dependencies** (e.g. Stage 2's official-solution check feeds Stage 4's Option 1 slot). Do not reorder.
- **Type 10 governance inverts some Skills BPs**: rigid contract steps are a feature, not railroading. See `ch2-擴充Agent/02-Skills.md` Type 10 section for the rationale.

When iterating on this skill, keep it under 500 lines (currently ~278) and avoid putting dynamic strings (timestamps, IDs, paths) in SKILL.md itself — they break prompt cache prefix stability.

### `/baransu:review` — independent multi-perspective verification

Task-analyst + dispatcher. Re-verifies any model output — code diff, file set, directory, /think's approved plan, a bare claim — by dispatching **isolated** perspective agents in clean Task contexts, then triaging findings into four response levels (direct fix / packaged confirm / ask user / FYI).

Key design properties to preserve when editing `review/SKILL.md` or the three agent files:

- **Principle-led, not rule-enumerated.** SKILL.md is ~155 lines of flow + principles, not a legalistic contract. When tempted to add an iron rule, a "What /review is NOT" disclaimer, a verdict enum, or a numeric cap (e.g. "≤4 questions"), first check whether it's defending against a real failure or the author's own anxiety. Most additions lose against the spec's core line: **"複雜度需要證明自己的價值"**.
- **Main skill is pure orchestrator.** No per-perspective review rubric lives in `skills/review/SKILL.md`; those live in `agents/*-reviewer.md`. Main skill owns only: flow, dispatch, triage.
- **Agents are perspectives, not personas.** Every `agents/*-reviewer.md` uses `視角 / 目標 / 通用原則 / 禁忌`. Role-play descriptions ("you are a senior …") are banned; they induce hallucination. The spec asked for the first three — the 禁忌 fourth section earns its place only as a lane-keeper between agents.
- **Activation looks at target behavior, not invocation keywords.** Dispatch decisions depend on what the target actually does (opens a socket, persists data, writes to disk, has cross-layer change, is a plan document) — never on strings in the user's invocation text.
- **Auto-fix is cosmetic-only.** Formatter / imports / typo / dead-import. Anything semantic — control flow, boundaries, API, state — goes to packaged confirm or needs-judgement.
- **Balance check is mandatory.** Every new-work finding must pass the 不做 / 做 / 中間方案 trio. Failing findings downgrade to advisory. This is the load-bearing principle — surgical precision over ceremony.
- **E2E hard gate** for code targets: no in-session green-run evidence → results say "not finished, e2e pending".
- **繁體中文 user-facing output; English agent-facing body.** Same convention as `/think`.

When iterating: keep `review/SKILL.md` lean (currently 155 lines). If a new iron rule or disclaimer section feels like an obvious addition, that's usually the moment to resist — the pre-v0.3.0 version of this skill ballooned to 271 lines through exactly that pattern before being cut back.

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

A /think-downstream **implementer** skill is still planned (separate from `/review`) — positioning goal is "trust /think's approval, strip redundant ceremony, finish simple tasks in minutes not hours". `/review` is the audit-side counterpart, not the implementer itself. Final design for the implementer will be produced via `/baransu:think` (dogfooding). Do not pre-scaffold it.

## What's Intentionally Absent

- **No build / test / lint commands** — no package manifest or toolchain yet. Do not fabricate `npm test` / `pytest` / similar. Update this section when one is introduced.
- **License**: MIT (see `LICENSE`). Declared in `plugin.json` and `README.md`.
