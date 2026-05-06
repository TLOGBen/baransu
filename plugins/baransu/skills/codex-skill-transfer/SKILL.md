---
name: codex-skill-transfer
description: "Port Claude Code skills, plugins, or marketplace catalogs to OpenAI Codex format. Claude is the source of truth; Codex is a one-way derived target. Handles single SKILL.md, batches, and whole plugins (.claude-plugin/plugin.json → .codex-plugin/plugin.json + agent-stub TOMLs). Use whenever the user wants to convert, port, migrate, mirror, or generate a Codex-compatible version of Claude Code material — phrasings like 「轉成 codex 版」「給 codex 用」「port to codex」「整個 plugin 轉過去」「make this work in codex」「Codex 對應」. Also trigger when the user asks how a specific Claude field (disable-model-invocation, context fork, allowed-tools, $ARGUMENTS, !`cmd` injection, plugin.json, marketplace.json, etc.) maps to Codex."
license: Apache-2.0
compatibility: Designed for Claude Code; output targets Codex CLI. Optional `skills-ref` CLI for validation.
metadata:
  author: baransu
  version: "0.4.0"
---

# Codex Skill Transfer

One-way port from Claude Code → Codex. Claude is canonical; this skill produces the Codex shadow.

## Direction is one-way (Claude → Codex)

The user keeps editing on the Claude side. Each rerun regenerates the Codex output from the current Claude source. The Codex output is **derived**, not authoritative — never edit it by hand expecting changes to flow back.

## Step 1 — Identify the source shape

Look at the source path the user gave you. Pick the matching mode:

| Source path looks like | Mode | What it produces |
|---|---|---|
| `<dir>/.claude-plugin/plugin.json` exists | **Plugin** | Full Codex plugin tree with manifest, skills, agent stubs |
| `<dir>/SKILL.md` exists at the top level | **Single skill** | One `<output>/<skill-name>/` |
| `<dir>` has children that each contain `SKILL.md` | **Skills batch** | One subdir per child |
| `<dir>/.claude-plugin/marketplace.json` exists | **Marketplace** (manual) | See [`references/marketplace-mapping.md`](references/marketplace-mapping.md); not script-automated |

`scripts/transfer.py` auto-detects Plugin / Single skill / Skills batch and dispatches. Marketplace is the only mode that always needs human work.

## Step 2 — Run the transfer

Default invocation for any of the three automated modes:

```bash
python3 scripts/transfer.py <claude-source> <codex-output>
```

The script refuses if `<codex-output>` overlaps the source — there is a real data-loss path otherwise (rerun would `rmtree` the source). Always pick a separate output directory.

For inline (in-conversation) execution without the script — when the user wants to inspect every change — read the source file(s), apply the rules in the relevant reference (see Step 3), and write the output yourself. The rules are deterministic enough that inline and scripted runs converge.

## Step 3 — Follow the rules in the right reference

The transformation is layered; each reference owns one layer. Read the matching one for the work in front of you, not all three:

- [`references/skill-mapping.md`](references/skill-mapping.md) — SKILL.md frontmatter + body rewrites. Covers the `disable-model-invocation` → `agents/openai.yaml` move, `$ARGUMENTS` → natural language, `` !`cmd` `` → imperative TODO, the `context: fork` three-paths decision, and tool-API rewrites. **This is the file to read for any per-skill question.**
- [`references/plugin-mapping.md`](references/plugin-mapping.md) — `.claude-plugin/plugin.json` → `.codex-plugin/plugin.json`, plus agent-stub generation. Read when porting a whole plugin.
- [`references/marketplace-mapping.md`](references/marketplace-mapping.md) — `.claude-plugin/marketplace.json` → `.agents/plugins/marketplace.json`. Read when the user wants to publish a marketplace catalog. Manual conversion only.

## Step 4 — Produce output by copying golden templates

All output shapes live in `assets/`. The script reads them; if you're working inline, copy them and fill the placeholders by hand. Each is a single file with `$placeholder` markers (Python `string.Template` syntax — `$name`, `$version`, etc.):

- [`assets/codex-plugin.template.json`](assets/codex-plugin.template.json) — fills the `.codex-plugin/plugin.json` for a plugin that bundles skills (the common case)
- [`assets/openai.template.yaml`](assets/openai.template.yaml) — fills `<skill>/agents/openai.yaml` when a skill needs `disable-model-invocation` ported (locks `policy.allow_implicit_invocation: false`)
- [`assets/agent-stub.template.toml`](assets/agent-stub.template.toml) — fills `<output>/.codex-agents-templates/<name>.toml` for each Claude agent definition; the user reviews and copies into their own `~/.codex/agents/`
- [`assets/codex-marketplace.template.json`](assets/codex-marketplace.template.json) — starting point for `.agents/plugins/marketplace.json` (manual, not used by the script)

Editing the templates updates the output without touching the script. If the user wants the Codex output to look different (different `interface.category`, an extra field, a logo path), the template is the right place to make the change.

## Step 5 — Print a transfer report

For automated runs the script prints the report. For inline runs you write it. Use this skeleton (繁中):

```
## Codex Transfer Report — <name>

- 來源: `<source-path>`
- 輸出: `<output-path>`

### 完整保留 (lossless)
- ...

### 翻譯處理 (mapped)
- ...

### 動態注入改寫 (rewrites)
- ...

### 已捨棄 (dropped)
- ...

### ⚠️ 需人工檢視 (manual review)
- ...
```

The report is the point of friction-resolution: **每一條 dropped/manual review 都是一個未來想優化的線索**。Encourage the user to track these.

## Boundaries

- **Never mutate the source.** Always write to a separate directory. The script refuses overlapping paths; inline work follows the same rule.
- **Never auto-write to user config dirs.** Agent stubs land in `<output>/.codex-agents-templates/` — the user copies them into `~/.codex/agents/` themselves. The plugin package has no business reaching into the user's home directory.
- **Never invent fields the user didn't author.** When a Claude field has no Codex target and no rewrite preserves intent, document it in the report. Silent fabrication is worse than an obvious gap.
- **Never translate domain-specific instructions or examples** in skill bodies — only the structural elements (frontmatter, dynamic injection, argument substitution, Claude-specific tool references). The author's voice stays.
- **Flag aggressively when in doubt.** A noisy report is cheaper than a silently wrong port.

## Repository layout this skill expects

```
codex-skill-transfer/
├── SKILL.md                              # this file
├── references/
│   ├── skill-mapping.md                  # per-skill rules (most consultation lands here)
│   ├── plugin-mapping.md                 # plugin manifest + agent stubs
│   └── marketplace-mapping.md            # marketplace catalog (manual only)
├── assets/
│   ├── codex-plugin.template.json        # → output/.codex-plugin/plugin.json
│   ├── openai.template.yaml              # → output/<skill>/agents/openai.yaml
│   ├── agent-stub.template.toml          # → output/.codex-agents-templates/*.toml
│   └── codex-marketplace.template.json   # starter for manual marketplace conversion
└── scripts/
    └── transfer.py                       # CLI entry; auto-detects mode
```

Single Python file by design — the script's three responsibilities (skill-level, plugin-level, dispatch) share enough state that splitting would add `sys.path` ceremony with little reading benefit. baransu's other tooling scripts (`grade-collector.py`, `health_check.py`) follow the same single-file convention.
