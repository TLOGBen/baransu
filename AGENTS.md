# AGENTS.md

**Single source of truth: [CLAUDE.md](CLAUDE.md).** Repo layout, the skills table, non-obvious invariants, versioning, and commit style all live there — read it first and follow it. This file only adds what a non-Claude agent (e.g. Codex CLI) needs to know. (General, plugin-agnostic working principles are user-scoped, not repeated here.)

`baransu` is a Claude Code plugin distributing twelve governance skills. Theme: バランス — deliberate before executing, verify after. The Philosophy (origin and core principle of バランス) lives in CLAUDE.md's Philosophy section — it is not duplicated here.

## Notes for non-Claude agents

- The Codex copy of the skills lives under `codex/plugins/baransu/skills/` and is maintained by hand alongside the Claude side: mirror every Claude-side change into it in the same change, using `/baransu:codex-skill-transfer` as the porting reference and checklist. Its `scripts/transfer.py` is an optional drafting helper — run it only into a scratch directory, never over `codex/`.
- Skill bodies are English; all user-facing output is 繁體中文. Do not change this convention.
- Plugin manifests: `.claude-plugin/marketplace.json` (repo root, catalog) and `plugins/baransu/.claude-plugin/plugin.json` (manifest, authoritative version). Never merge them.

## Verification

此 plugin 不做任何單元測試。A skill working well has nothing to do with unit tests, a skill failing has nothing to do with them, and when skills change it is the tests that break, not the skills — so since v8.0.0 the repo keeps none. `make test` now runs only the structural verifier.

```bash
make test          # scripts/verify-skills.py only (structural verifier)
make parity-check  # scripts/verify-codex-parity.py
make ship-check    # both, before a release
```
