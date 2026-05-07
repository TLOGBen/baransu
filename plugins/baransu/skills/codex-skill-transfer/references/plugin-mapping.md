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

Dropped (no plugin-level Codex equivalent): `commands` (Codex merges these into skills); `lspServers` (Codex plugins don't host LSP); `agents` (must move to user-side `.codex/agents/*.toml`; see [`agent-mapping.md`](agent-mapping.md)).

## 6. Agent stub generation

When the source plugin ships `agents/*.md` files, the transfer emits TOML stubs at `<output>/.codex-agents-templates/*.toml`. The full stub shape, escaping rules, and per-field guidance live in [`agent-mapping.md`](agent-mapping.md) §4. The user reviews each stub and copies it into their own `~/.codex/agents/` — this skill never writes to user config dirs.

## 7. Template assets

The transfer uses one template from `assets/` for the plugin manifest:

- [`codex-plugin.template.json`](../assets/codex-plugin.template.json) — the canonical `.codex-plugin/plugin.json` shape

The script renders this template with JSON-safe substitution, parses the result, prunes empty pass-through scalars, and merges complex fields (`author`, `keywords`) directly from the translated manifest. Editing the template changes the canonical shape; absent source fields are pruned automatically.

The agent-stub TOML and skill-level `agents/openai.yaml` are NOT templated — they're built directly via `yaml.safe_dump` and `json.dumps`, because honor-system templating proved unsafe for content that may contain quotes, newlines, or escape sequences. See `scripts/transfer.py` `emit_agent_stub` and `write_skill` for the actual code.
