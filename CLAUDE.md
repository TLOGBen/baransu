# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Intent

`baransu` is a Claude Code **plugin marketplace** distributing one governance-focused plugin, also named `baransu`. The plugin's theme is バランス ("balance") — forcing alignment and approval before execution. Currently ships a single skill: `/think`.

## Actual Layout

```
.claude-plugin/
  marketplace.json             # marketplace catalog — lists distributed plugins
plugins/
  baransu/
    .claude-plugin/
      plugin.json              # plugin manifest (v0.1.0)
    skills/
      think/
        SKILL.md               # governance skill — align/research/approve before code
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

Next skill is planned as a /think downstream consumer — positioning goal is "trust /think's approval, strip redundant ceremony, finish simple tasks in minutes not hours". Final design will be produced via `/baransu:think` itself (dogfooding). Do not pre-scaffold it.

## What's Intentionally Absent

- **No build / test / lint commands** — no package manifest or toolchain yet. Do not fabricate `npm test` / `pytest` / similar. Update this section when one is introduced.
- **License**: MIT (see `LICENSE`). Declared in `plugin.json` and `README.md`.
