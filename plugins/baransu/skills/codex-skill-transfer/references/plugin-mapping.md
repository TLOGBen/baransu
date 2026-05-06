# Plugin-level Mapping (`.claude-plugin/plugin.json` → `.codex-plugin/plugin.json`)

Translation rules for the plugin manifest itself, plus the agent-stub emission that accompanies a full plugin port. For SKILL.md frontmatter and body rules (one level down), see [`skill-mapping.md`](skill-mapping.md). For marketplace catalogs (one level up), see [`marketplace-mapping.md`](marketplace-mapping.md).

## 1. Why two manifest formats look so similar but aren't interchangeable

Both Claude Code and Codex follow a `<plugin-root>/<config-dir>/plugin.json` shape. The two diverge on **discovery philosophy**:

- **Claude is filesystem-driven** — Claude Code scans `<plugin>/skills/`, `<plugin>/agents/`, `<plugin>/hooks/` automatically. The manifest's job is just to identify the plugin (name + version + description).
- **Codex is manifest-driven** — every component category must be pointed at explicitly inside `plugin.json`. If `skills/` exists but no `"skills": "./skills/"` line is in the manifest, Codex will not find them.

This is why baransu's `plugin.json` deliberately has **no** `skills` array on the Claude side (it was added in v0.3.0 and reverted; see project CLAUDE.md), but the Codex output **must** include `"skills": "./skills/"` when skills are present. Same data, opposite convention.

## 2. Required-field gap

Claude makes only `name` strictly required; Codex requires three. Fill the gap with conservative defaults rather than aborting:

| Field | Claude | Codex | Default to use when absent on Claude side |
|------|---|---|------|
| `name` | required | required (kebab-case) | (error if absent — names cannot be invented) |
| `version` | optional | required (semver) | `"0.1.0-codex"` |
| `description` | optional | required | use `name` |

The defaults flag the gap: `"0.1.0-codex"` is obviously a placeholder, and a `description` equal to `name` immediately reads as "needs a real description." This is intentional — silent fabrication is worse than an obvious gap.

## 3. Component pointer addition

For each component directory present on the Claude side, add the matching pointer to the Codex manifest. All paths must be relative and start with `./` (Codex spec rule).

| If source has | Add to Codex `plugin.json` |
|----|----|
| `skills/<name>/SKILL.md` | `"skills": "./skills/"` |
| `mcp.json` (or any MCP server config) | `"mcpServers": "./.mcp.json"` (verify path) |
| `hooks/hooks.json` | `"hooks": "./hooks/hooks.json"` |
| App connector config (none in baransu today) | `"apps": "./.app.json"` |

baransu skills today only use the `skills/` pointer. The transfer script reflects that focus; other pointers are documented for completeness but require manual review.

## 4. UI metadata (`interface`)

Codex uses an `interface` object for marketplace presentation. The transfer fills the two fields it can derive:

```json
"interface": {
  "displayName": "Title-cased plugin name",
  "shortDescription": "First sentence (~120 chars) of description",
  "category": "productivity",
  "logo": "./assets/icon.png",
  "screenshots": ["./assets/screenshot1.png"]
}
```

Auto-filled: `displayName` (from `name` with hyphens → spaces and Title Case), `shortDescription` (from `description`, truncated). Left for the user: `category`, `logo`, `screenshots` — these need design judgment and source assets the script can't conjure.

## 5. Pass-through and dropped fields

Pass through unchanged when present: `author`, `homepage`, `repository`, `license`, `keywords`.

Dropped (no plugin-level Codex equivalent): `commands` (Codex merges these into skills); `lspServers` (Codex plugins don't host LSP); `agents` (must move to user-side `.codex/agents/*.toml`; see §6 below).

## 6. Agent stub generation (`agents/*.md` → `.codex-agents-templates/*.toml`)

Claude plugins ship subagent definitions as Markdown files in `agents/`. Codex's equivalent is `~/.codex/agents/<name>.toml` — TOML, **user-side**, outside the plugin package. Two reasons not to auto-write directly to `~/.codex/agents/`:

1. The plugin cannot safely reach into the user's config directory.
2. Each agent needs choices (model, reasoning effort, sandbox, MCP servers) the transfer can't make.

Therefore the transfer emits **stubs** at `<output>/.codex-agents-templates/<name>.toml`. The user reviews each stub and copies into their config dir.

### 6.1 Stub shape

The stub is generated from `assets/agent-stub.template.toml` with three placeholders filled: `$name`, `$description`, `$instructions` (and `$source_md` for traceability). Result:

```toml
# Stub generated from <agent-name>.md.
# Review before copying to ~/.codex/agents/<name>.toml.
# See codex-skill-transfer references/plugin-mapping.md for the mapping rules.

name = "<name>"
description = "<first-line of frontmatter description if found>"

developer_instructions = """
<the original .md body, with frontmatter stripped>
"""

# Choose what to fill in below; all are optional and inherit from parent if absent.
#
# model = "gpt-5.4"
# model_reasoning_effort = "high"      # low | medium | high | max
# sandbox_mode = "workspace-write"     # read-only | workspace-write | danger-full-access
# mcp_servers = []                     # list of MCP server ids the agent may invoke
# nickname_candidates = []             # cosmetic names for spawned instances
```

### 6.2 What the user fills in after copying

- `model` — Codex model id (e.g. `"gpt-5.4"`) or omit to inherit from parent session.
- `model_reasoning_effort` — map from Claude's `effort` if it was present (`low` / `medium` / `high` / `max`).
- `sandbox_mode` — usually safer to omit; parent session policy applies.
- `mcp_servers` — list of MCP servers this agent should access.
- `nickname_candidates` — optional cosmetic names.

### 6.3 What the stub deliberately doesn't translate

The Markdown body lands in `developer_instructions` verbatim because the agent's *prompt* is the meaningful content. References to Claude-specific tools (`Task`, `AskUserQuestion`, etc.) survive unchanged — the user adapts these by hand using the body-rewrite table in [`skill-mapping.md`](skill-mapping.md) when they migrate the stub into their Codex config.

## 7. Template assets

The transfer reads two templates from `assets/` to produce its output (Python `string.Template` with JSON-safe substitution):

- [`codex-plugin.template.json`](../assets/codex-plugin.template.json) — the `.codex-plugin/plugin.json` shape
- [`agent-stub.template.toml`](../assets/agent-stub.template.toml) — the agent stub shape

Editing those template files changes the output without touching the script. Treat them as the canonical examples — anything the user wants to ship via this transfer should match these shapes.
