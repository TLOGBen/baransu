---
name: codex-skill-transfer
description: "Porting reference and parity checklist for hand-maintained Claude Code and OpenAI Codex copies of a skill, plugin, or marketplace: field mapping, what Codex ignores, paths, invocation, bundled agents, hooks, Claude-only parts (mods, userConfig, monitors), versioning. By default audits a Claude/Codex pair and reports gaps; a script can optionally draft a copy. Trigger on 「轉成 codex 版」「給 codex 用」「port to codex」「檢查 codex 版」, or Claude→Codex mapping questions (disable-model-invocation, context fork, ARGUMENTS, plugin.json). Not for reverse porting (Codex→Claude) or a brand-new Codex skill with no Claude counterpart."
license: Apache-2.0
compatibility: Mapping checked against Claude Code 2.1.293 and Codex CLI 0.161.0 (2026-10-08). Optional transfer.py helper needs Python 3 and PyYAML; optional `skills-ref` CLI for validation.
metadata:
  author: baransu
  version: "0.19.0"
---

# Codex Skill Transfer

Claude Code and Codex copies of the same material are maintained **by hand, side by side**. This skill is the porting reference and the parity checklist for that work. `scripts/transfer.py` is an optional drafting helper, not the default path.

Baseline: Claude Code `2.1.293`, Codex CLI `0.161.0` (source tag `rust-v0.161.0`), checked 2026-10-08. Rules below come from official docs or the Codex source unless marked *(inferred)* — derived from evidence, not stated officially — or *(unpublished)* — the vendor has not documented it. Keep those labels whenever you repeat a rule; never upgrade an inferred or unpublished item to a fact.

## Outcome Contract

- **Outcome**: A Claude-source / Codex-copy pair (skill, plugin, or marketplace) is checked against the current platform mapping, every gap is named with its fix, and — only when the user asks — the Codex copy is edited by hand to close those gaps.
- **Done when**: every Step 3 checklist section that applies to the detected shape has been walked against both trees, each finding names file + rule + fix, and (edit mode) the Codex copy re-checks clean with its version bumped alongside the Claude copy.
- **Evidence**: The 繁中 parity report from Step 5 with a status for every applicable checklist item; both trees untouched in checklist mode; in generate mode, the script's own transfer report plus the draft-vs-copy review.
- **Output**: The parity report, plus the edited Codex copy (port-by-hand mode) or a draft directory in a scratch location (generate mode).
- **Automation**: ultracode=assist, loop=assisted（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）

## Who owns what

Each copy is authoritative for its own platform. A change to one is mirrored into the other by hand, in the same change set, using the Step 3 checklist. Never regenerate a hand-maintained Codex copy wholesale with the script: it would overwrite hand fixes, and the script refuses a non-generated output directory anyway.

## Step 1 — Pick the mode and identify the shape

| Mode | When | What you do |
|---|---|---|
| **Checklist** (default) | The user names a Claude source and its Codex copy, or asks whether the Codex copy is right | Read both trees, walk Step 3, write the Step 5 report. Read-only. |
| **Port by hand** | The Codex copy is missing or stale and the user asks to create or update it | Create or edit the Codex copy item by item from Step 3, then run Checklist mode on the result |
| **Generate** (optional) | The user explicitly asks for the script or a throwaway first draft | Run `scripts/transfer.py` into a scratch directory (Step 4), review the draft with Step 3, port the useful parts by hand |
| **Reference question** | A field-mapping or "does Codex support X" question | Answer from the references below, keeping the *(inferred)* / *(unpublished)* labels |

| Source looks like | Shape | Checklist sections |
|---|---|---|
| `<dir>/.claude-plugin/plugin.json` | Plugin | 3.1 for every skill, 3.2, 3.3, 3.5 |
| `<dir>/SKILL.md` | Single skill | 3.1, plus 3.5 if the skill is versioned |
| children that each hold `SKILL.md` | Skills batch | 3.1 per child |
| `<dir>/.claude-plugin/marketplace.json` | Marketplace | 3.4, then each listed plugin |

Codex falls back to Claude's files when its own are missing: plugin manifest lookup ends at `.claude-plugin/plugin.json`, catalog lookup at `.claude-plugin/marketplace.json`. So a Codex tree with no Codex manifest or catalog still "loads" — with Claude-only tokens in every body and Claude-only plugins (including mods) in the catalog. Treat a missing Codex manifest or catalog as a gap, never as "works already".

## Step 2 — Refresh when the platforms moved

Run `claude --version` and `codex --version`. If either is newer than the baseline, or you are about to change a mapping rule, re-read the authoritative pages first; they drift faster than this skill:

- OpenAI's Claude-plugin porting guide (read first): `https://developers.openai.com/plugins/guides/submit-claude-plugin.md`
- Codex packaging (manifest, marketplace, hooks in plugins): `https://developers.openai.com/plugins/build/plugins.md`
- Codex docs under `https://learn.chatgpt.com/docs/`: `build-skills.md`, `hooks.md`, `agent-configuration/subagents.md`, `config-file/config-reference.md`, `import.md`, `changelog`. (`developers.openai.com/codex/*` now redirects there.)
- Codex source at the matching tag: `codex-rs/skills/src/parser.rs`, `codex-rs/core-plugins/src/{manifest,marketplace,store}.rs`, `codex-rs/agent-roles/src/loader.rs`, `codex-rs/core/src/tools/handlers/{multi_agents_spec,request_user_input_spec}.rs`, `codex-rs/hooks/src/engine/discovery.rs`.
- Claude docs under `https://code.claude.com/docs/en/`: `skills.md`, `plugins/manifest-reference.md`, `plugins/marketplace-reference.md`, `plugins/loading.md`, `sub-agents.md`, `hooks.md`, `tools-reference.md`, `plugins/mods/overview.md`, `changelog.md`.

Codex's `/import` can pull Claude instructions, skills, plugins, hooks, and subagents into Codex. Its result is a useful comparison point, but it still needs this checklist.

## Step 3 — Walk the checklist

Each item names the rule's home. Mark every applicable item 一致 / 需修正 / 刻意省略 / 待查 in the report.

### 3.1 Skills — [`references/skill-mapping.md`](references/skill-mapping.md)

- [ ] **Frontmatter.** Codex reads only `name`, `description`, and `metadata.short-description`; every other key is silently ignored. Merge `when_to_use` into `description`; turn Claude-only keys that carried behavior into body instructions; harmless keys (`license`, `compatibility`, `metadata`) may stay.
- [ ] **Name.** Same `name` on both sides, equal to the directory name, lowercase-hyphen, ≤ 64 chars (Codex's limit is the tighter one).
- [ ] **Description.** Trigger words first — both platforms shorten descriptions when the skill catalog runs over budget.
- [ ] **Invocation policy.** `disable-model-invocation: true` → `agents/openai.yaml` `policy.allow_implicit_invocation: false`. `user-invocable: false` has no counterpart; say so in the body. `agents/openai.yaml` exists only in the Codex copy.
- [ ] **Paths.** Codex substitutes no variables in skill text: relative paths resolve from the `SKILL.md` directory. Rewrite every CLAUDE_PLUGIN_ROOT, CLAUDE_SKILL_DIR, and CLAUDE_PLUGIN_DATA placeholder in bodies and references to a relative path (`scripts/x.py`, `../other-skill/...`). When a command needs an absolute path, tell the model to resolve the absolute location of `SKILL.md` first. Plugin variables (`PLUGIN_ROOT`, `PLUGIN_DATA`) exist only in hook commands.
- [ ] **Invocation syntax.** Claude `/plugin:skill` and bare sibling `/skill` mentions → `$plugin:skill` in a plugin; `$skill` for a standalone skill install.
- [ ] **Arguments and injection.** `$ARGUMENTS` → natural language ("the value the user gave"); positional and named argument placeholders likewise. Bang-backtick inline commands and bang-fenced blocks → "run these commands and read their output first". Codex has no counterpart for either *(inferred: neither the parser nor the catalog handles them)*.
- [ ] **Tools.** AskUserQuestion → `request_user_input` plus a no-tool fallback; Agent → `spawn_agent` with explicit count, inputs, wait, and return shape; Task/Todo tools → `update_plan` plus a durable file; Monitor, cron, Artifact, SendUserFile, WebFetch → degrade per the table in skill-mapping §6. Keep the anti-inertia tooth, not just the name — see [`references/CODEX_PORT_PLAN.md`](references/CODEX_PORT_PLAN.md).
- [ ] **Forked context.** `context: fork` / `agent:` → an explicit spawn instruction in the body; ask for a clean context with `fork_turns="none"` (v2 tool) or `fork_context=false` (v1). See [`references/agent-mapping.md`](references/agent-mapping.md).
- [ ] **Skill hooks.** Frontmatter `hooks` → plugin-level `hooks/hooks.json`, or drop and record.
- [ ] **Extra folders.** Keep every folder the skill uses — `scripts/`, `references/`, `assets/`, `evals/`, and also `templates/` or any other folder the body points to. Codex docs list four folders as examples, not as an allow-list *(inferred: no documented rejection)*.
- [ ] **Instruction files.** `CLAUDE.md` → `AGENTS.md` in Codex bodies. Claude ≥ 2.1.277 reads `AGENTS.md` when no `CLAUDE.md` exists, so one shared `AGENTS.md` can serve both.

### 3.2 Plugin — [`references/plugin-mapping.md`](references/plugin-mapping.md)

- [ ] **Manifest format.** Pick one per plugin: portable root `plugin.json` (`$schema` from agent-plugins.org, OpenAI settings under `extensions."com.openai"`; recommended for new packages) or `.codex-plugin/plugin.json` (still supported compatibility path). `extensions."com.openai"` replaces the `.codex-plugin` overlay wholesale — never keep both with different content.
- [ ] **Fields.** `displayName` → `extensions."com.openai".interface.displayName`; `defaultEnabled` → the marketplace entry's `policy.installation`; `userConfig`, `dependencies`, `settings`, `types`, `channels`, `lspServers`, `outputStyles`, `experimental.*`, icon and URL fields → remove (3.3).
- [ ] **Bundled agents.** Codex 0.161 plugins still do not register agents. Pick option A (fold the agent procedure into the skill — OpenAI's advice), B (package-local TOML plus a resolver that inlines it into the spawn message), or C (the user adds `[agents.<name>] config_file` to their own `config.toml`; the cache path changes with every version *(inferred)*).
- [ ] **Hooks.** Codex runs 12 events and only `command` / `mcp_tool` handlers; drop Claude-only events instead of mapping them to a neighbour; CLAUDE_PLUGIN_ROOT → `PLUGIN_ROOT` in hook commands; `SessionEnd` timeout ≤ 3 s; add `commandWindows` for Windows; users must trust plugin hooks in `/hooks`; a plugin with lifecycle hooks cannot be listed in OpenAI's public directory.
- [ ] **MCP.** Portable Codex packages read root `mcp.json` (no leading dot), and every server declares a transport `type`.
- [ ] **Data directory.** Skills get no `PLUGIN_DATA`; pick an explicit Codex-side path for persistent data.

### 3.3 Claude-only components

| Component | How to spot it | Codex handling |
|---|---|---|
| Mods | `hooks/hooks.json` holding `{"modules": [...]}`; manifest `types` | Omit the whole mod plugin from the Codex catalog. Never copy its `hooks/`: Codex reads `hooks/hooks.json` as lifecycle hooks *(inferred breakage)*. Skills a mod button triggers stay reachable through `$plugin:skill`; a `default_prompt` in `agents/openai.yaml` can hint at them. |
| Monitors | `monitors/monitors.json`, `experimental.monitors` | Remove; rewrite any dependent flow as polling |
| `userConfig` | manifest `userConfig`, `user_config.KEY` references, `CLAUDE_PLUGIN_OPTION_*` env vars | Per-task values become skill inputs; machine settings become env vars or a config file, with an actionable error when missing |
| Plugin dependencies | manifest `dependencies` | Remove; name the required plugins in the Codex README or skill body |
| LSP | `lspServers`, `.lsp.json` | Remove and record |
| Other | `output-styles/`, `themes`, `workflows/`, `bin/`, `channels`, `settings.json`, `statusLine` / `subagentStatusLine`, `claude plugin eval` suites | Remove and record |

A plugin that is entirely Claude-only is left out of the Codex catalog. A plugin with some Claude-only parts ships without them, and its Codex README says what is missing.

### 3.4 Marketplace — [`references/marketplace-mapping.md`](references/marketplace-mapping.md)

- [ ] **Lookup order.** Codex reads the first that exists: `.agents/plugins/marketplace.json` → `.agents/plugins/api_marketplace.json` → `.claude-plugin/marketplace.json` → `.cursor-plugin/marketplace.json`. A repo that ships a Claude catalog needs a repo-root `.agents/plugins/marketplace.json`, or Codex loads the Claude catalog *(inferred consequence)*.
- [ ] **Entries.** Each carries `policy.installation`, `policy.authentication`, and `category`. Source `github` → `url`; `archive` and `command` have no Codex counterpart. Claude-only plugins are not listed.
- [ ] **Enablement.** The Codex CLI has no enable/disable command; it is `[plugins."<plugin>@<marketplace>"] enabled` in `config.toml`. Install docs are written separately per platform.

### 3.5 Versions and caching — [`references/plugin-mapping.md`](references/plugin-mapping.md) §8

- [ ] Bump `version` in both copies on every distributed change. Claude: manifest `version` → marketplace entry `version` → commit SHA; an unchanged string means no update. Codex: cache dir `~/.codex/plugins/cache/<marketplace>/<plugin>/<version>/`, named from the manifest version; users refresh with `codex plugin marketplace upgrade <marketplace>`.
- [ ] Keep version strings plain semver. Whether a `+build` suffix is a valid Codex cache segment is *(unpublished)*; avoid it or verify after install.
- [ ] Whether Codex recopies a plugin whose version is unchanged but whose content changed is *(unpublished)* — always bump.
- [ ] Re-check any model name pinned in a custom-agent TOML against the current Codex changelog; models retire often.

## Step 4 — Edit the Codex copy (port by hand), or draft with the script

**By hand.** Change only structural elements — frontmatter, paths, invocation syntax, argument and injection markers, tool names, components. Never translate domain instructions or examples; the author's voice stays. Use file-edit tools rather than scripted string replacement when the content holds backslashes or quotes. Then search the Codex copy for leftovers and justify every hit (a quoted example is fine; a live instruction is a gap):

```bash
grep -rnE 'CLAUDE_(PLUGIN_ROOT|PLUGIN_DATA|SKILL_DIR)|\$ARGUMENTS|AskUserQuestion|TodoWrite|disable-model-invocation|context: fork|user_config\.' <codex-copy>
```

Parse every JSON manifest and catalog, run `skills-ref validate` when available, and bump both versions.

**Golden templates.** `assets/` holds two starting shapes with `$placeholder` markers (Python `string.Template` syntax): [`assets/codex-plugin.template.json`](assets/codex-plugin.template.json) (portable root `plugin.json`) and [`assets/codex-marketplace.template.json`](assets/codex-marketplace.template.json) (repo-root catalog). Copy and fill by hand, or let the script render them.

**Generate mode (optional).** `python3 scripts/transfer.py <claude-source> <scratch-output>` drafts a full Codex tree. It refuses (exit 2) when the output overlaps the source, and when the output exists, is non-empty, and lacks the generated marker; after a refusal you MUST NOT delete the refused directory yourself — pick another scratch directory. Never point it at the hand-maintained Codex copy. Diff the draft against the copy and port what is useful by hand. Known gaps in the draft: it drops skill folders other than `scripts/` / `references/` / `assets/` / `evals/` / `agents/` (copy `templates/` and the like yourself), it does not recognize mod plugins or the Codex-only `Interrupt` event, and it leaves CLAUDE_PLUGIN_ROOT in skill bodies for manual review instead of rewriting it to relative paths.

## Step 5 — Write the parity report

Use this skeleton (繁中):

```
## Codex 對照報告 — <name>

- Claude 版：`<path>`（version <x>）
- Codex 版：`<path>`（version <y>）
- 對照基準：Claude Code <ver> ／ Codex CLI <ver>

### 一致
- ...

### 需修正（檔案 — 規則 — 修法）
- ...

### 刻意省略（Claude 專用，Codex 版不放）
- ...

### 降級風險（依模型慣性加權）
- ...

### 待查（推論或官方未公布）
- ...
```

Then append `### Next-port follow-ups`, one line per item under 需修正, 刻意省略, and 待查, each tagged with exactly one disposition: `fix-now` (a hand edit closes it), `refresh-mapping` (a reference in this skill is out of date), `file-issue` (an upstream limitation to track), or `accept-as-lossy` (no Codex target exists; the gap is permanent and intentional). With nothing to list, write the single line `- none`.

## Boundaries

- **Checklist mode never edits.** Edit either copy only when the user asked for it.
- **Never regenerate over a hand-maintained Codex copy.** The script writes only to a scratch directory.
- **Never write to user config.** No writes to `~/.codex/agents/`, `.codex/agents/`, or `config.toml`; option C in 3.2 is documented for the user to apply.
- **Never claim parity while an item is unchecked**, and never silently drop a component — every omission is named in the report.
- **Never invent fields.** A Claude field with no Codex target is recorded, not fabricated into something plausible.
- **Never translate domain content.** Only structural elements change.
- **Keep the evidence labels.** *(inferred)* and *(unpublished)* stay attached; flag aggressively when in doubt — a noisy report is cheaper than a silently wrong copy.

`scripts/transfer.py` stays a single Python file by design, matching the single-file convention of the plugin's other tooling scripts.
