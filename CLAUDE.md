# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Intent

`baransu` is a Claude Code **plugin marketplace** that currently distributes one plugin, also named `baransu`. The marketplace layout is scaffolded but component directories (skills/agents/commands/hooks) are not yet populated.

## Actual Layout

```
.claude-plugin/
  marketplace.json             # marketplace catalog — lists distributed plugins
plugins/
  baransu/
    .claude-plugin/
      plugin.json              # plugin manifest (name, version, author, component paths)
    skills/                    # <name>/SKILL.md — not yet created
    agents/                    # <name>.md — not yet created
    commands/                  # flat .md files — not yet created
    hooks/                     # hooks.json + scripts — not yet created
```

**Critical distinction**: `.claude-plugin/marketplace.json` at the repo root is the *catalog*; `plugins/baransu/.claude-plugin/plugin.json` is the *plugin manifest*. Never merge them. Component dirs (`skills/`, `agents/`, etc.) go at the **plugin root** (`plugins/baransu/`), not inside `.claude-plugin/` and not at the repo root.

## Install Flow (for testing locally)

```
/plugin marketplace add /home/vakarve/projects/baransu
/plugin install baransu@baransu
/plugin validate                    # or: claude plugin validate
```

## Versioning

`plugins/baransu/.claude-plugin/plugin.json` holds the authoritative `version`. Bump it on every distributed change — users won't pick up updates without a version bump due to plugin caching. If a version is also set in `marketplace.json`'s plugin entry, `plugin.json` wins.

## Working Conventions (inherited from the owner's global rules)

These come from `~/.claude/CLAUDE.md` and apply here unless this file overrides them:

- **everything-cli pipeline** (`/panel-review → /eidos → /execute`) is the default for non-trivial changes. For a skill/agent addition that has obvious scope, `/dev-lite` or direct execution is acceptable.
- **Read-before-write**: re-Read any file in the same turn before Edit/Write, even if read earlier in the session.
- **Handoff artifacts** land in `.agent-workspace/handoff/`. The existing `.agent-workspace/` dir is for transient pipeline state — do not commit its contents (add to `.gitignore` when the first commit lands).
- **Commit style**: conventional commits (`feat:`, `fix:`, `docs:`, …). Attribution lines are disabled globally.

## What's Intentionally Absent

- **No build / test / lint commands** — there is no package manifest, test suite, or toolchain yet. Do not fabricate `npm test` / `pytest` / similar. When a toolchain is introduced, update this section.
- **No skills / agents / commands / hooks** — scaffolding these is the next natural step. The name "baransu" (バランス, "balance") hints at a theme the user will describe; ask before inventing one.
- **No license declared** — do not invent one in `plugin.json` or elsewhere without the user's say-so.
