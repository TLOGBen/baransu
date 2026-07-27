# Plugin-level Mapping (`.claude-plugin/plugin.json` → `.codex-plugin/plugin.json`)

Translation rules for the plugin manifest itself, plus the agent/rule content closure that accompanies a full plugin port. For SKILL.md frontmatter and body rules (one level down), see [`skill-mapping.md`](skill-mapping.md). For marketplace catalogs (one level up), see [`marketplace-mapping.md`](marketplace-mapping.md).

## 1. Why two manifest formats look so similar but aren't interchangeable

Both Claude Code and Codex follow a `<plugin-root>/<config-dir>/plugin.json` shape. The two diverge on **discovery philosophy**:

- **Claude is filesystem-driven** — Claude Code scans `<plugin>/skills/`, `<plugin>/agents/`, `<plugin>/hooks/` automatically. The manifest's job is just to identify the plugin (name + version + description).
- **Codex is manifest-driven** — every component category must be pointed at explicitly inside `plugin.json`. If `skills/` exists but no `"skills": "./skills/"` line is in the manifest, Codex will not find them.

This is why baransu's `plugin.json` deliberately has **no** `skills` array on the Claude side (it was added in v0.3.0 and reverted; see project CLAUDE.md), but the Codex output **must** include `"skills": "./skills/"` when skills are present. Same data, opposite convention.

## 2. Required-field gap

Claude makes only `name` strictly required; Codex requires `name` (kebab-case) + `version` (semver) — `description` is **optional** per the official build docs ([developers.openai.com/plugins/build/plugins](https://developers.openai.com/plugins/build/plugins)) but recommended. Fill the gaps with conservative defaults rather than aborting:

| Field | Claude | Codex | Default to use when absent on Claude side |
|------|---|---|------|
| `name` | required | required (kebab-case) | (error if absent — names cannot be invented) |
| `version` | optional | required (semver) | `"0.1.0-codex"` |
| `description` | optional | optional (recommended) | use `name` as a recommended fill |

The defaults flag the gap: `"0.1.0-codex"` is obviously a placeholder, and a `description` equal to `name` immediately reads as "needs a real description." This is intentional — silent fabrication is worse than an obvious gap.

## 3. Component pointer addition

For each component directory present on the Claude side, add the matching pointer to the Codex manifest. All component-pointer path fields must be relative, start with `./`, and stay within **125 chars** (Codex spec rules, per the official build docs).

| If source has | Add to Codex `plugin.json` |
|----|----|
| `skills/<name>/SKILL.md` | `"skills": "./skills/"` |
| `agents/*.md` | No manifest pointer exists; emit `.codex-agents/*.toml` and inject package-local fail-closed resolvers into consuming skills |
| `mcp.json` (or any MCP server config) | `"mcpServers": "./.mcp.json"` (verify path) — **manual review**; see below |
| `hooks/hooks.json` | `"hooks": "./hooks/hooks.json"` — supported command handlers are copied; unsupported events/types are reported |
| `rules/*.md` | No manifest pointer exists; copy to `rules/` and normalize live references (`CLAUDE.md` → `AGENTS.md`, skill paths to package-relative paths) |
| App connector config (none in baransu today) | `"apps": "./.app.json"` |

baransu now uses both the `skills/` and `hooks/` pointers. The transfer script handles those two package-local surfaces; MCP and apps remain manual-review surfaces.

**Hooks are outcome-ported; MCP remains manual.** Current Codex loads plugin-bundled hooks from the default `hooks/hooks.json` path (or a manifest pointer), enables hooks by default, and provides `PLUGIN_ROOT` / `PLUGIN_DATA` plus compatibility aliases `CLAUDE_PLUGIN_ROOT` / `CLAUDE_PLUGIN_DATA`. The transfer therefore copies the hook directory, adds the manifest pointer, retains supported events with `type="command"`, rewrites those handlers' command strings to the canonical Codex variables (`CLAUDE_PLUGIN_ROOT` → `PLUGIN_ROOT`, `CLAUDE_PLUGIN_DATA` → `PLUGIN_DATA`), and names every rejected event or handler in the report. It never invents lifecycle equivalence: Claude `SessionEnd` is dropped and reported, not rewritten to Codex `Stop`. Installation does not imply trust; the user must review changed plugin hooks in `/hooks` before they execute.

Hook scripts still own runtime result translation. In particular, a Claude Stop script that blocks with a non-zero exit must emit Codex's structured `{"continue":false,"stopReason":"..."}` result when running under Codex. A dual-runtime script can detect Codex through `PLUGIN_ROOT`; transfer preserves script bytes because generic shell-semantic rewriting would be unsafe. Only the structured `hooks.json` command fields receive the canonical variable-name rewrite.

MCP config is still report-only. Server startup, authentication, and trust are external runtime concerns, so `mcp.json` / `.mcp.json` is not copied automatically yet.

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

Dropped (no plugin-level Codex equivalent): `lspServers` (Codex plugins don't host LSP). A manifest-level `agents` pointer has no Codex equivalent, but file-based `agents/*.md` content is not dropped: it is converted into the bundled runtime path described below.

`commands` gets a 需人工檢視 line instead of a plain drop: Codex custom prompts are officially **deprecated** — convert each `commands/*.md` into a Codex skill (directory + SKILL.md). Never port to `~/.codex/prompts/`; a known 0.117.0 regression broke prompt loading there.

## 6. Bundled agent and rule closure

When the source plugin ships `agents/*.md`, the transfer emits runtime TOMLs at `<plugin-output>/.codex-agents/*.toml`, rewrites consuming skill references to those files, and injects a resolver that fails with `AGENT_DEFINITION_MISSING` if a definition cannot be read. It does not rely on a manual copy into `~/.codex/agents/`. See [`agent-mapping.md`](agent-mapping.md) §4.

When the source ships `rules/`, the transfer copies it to `<plugin-output>/rules/` and normalizes live Claude-only paths. Plugin mode inventories every source top-level component; an unknown component is reported as unhandled so the run cannot silently imply a complete content closure.

## 7. Template assets

The transfer uses one template from `assets/` for the plugin manifest:

- [`codex-plugin.template.json`](../assets/codex-plugin.template.json) — the canonical `.codex-plugin/plugin.json` shape

The script renders this template with JSON-safe substitution, parses the result, prunes empty pass-through scalars, and merges complex fields (`author`, `keywords`) directly from the translated manifest. Editing the template changes the canonical shape; absent source fields are pruned automatically.

The bundled-agent TOML and skill-level `agents/openai.yaml` are NOT templated — they're built directly via `yaml.safe_dump` and `json.dumps`, because honor-system templating proved unsafe for content that may contain quotes, newlines, or escape sequences. See `scripts/transfer.py` `emit_bundled_agent_definition` and `write_skill` for the actual code.
