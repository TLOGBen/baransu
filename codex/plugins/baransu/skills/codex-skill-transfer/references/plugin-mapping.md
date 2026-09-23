# Plugin-level Mapping (`.claude-plugin/plugin.json` → portable root `plugin.json`)

Translation rules for the plugin manifest itself, plus the agent/rule content closure that accompanies a full plugin port. For SKILL.md frontmatter and body rules (one level down), see [`skill-mapping.md`](skill-mapping.md). For marketplace catalogs (one level up), see [`marketplace-mapping.md`](marketplace-mapping.md).

Source of truth: the official "Package your plugin" page ([developers.openai.com/plugins/build/plugins](https://developers.openai.com/plugins/build/plugins)) and the Codex loader at `rust-v0.156.1` (`codex-rs/core-plugins/src/manifest.rs`, `loader.rs`). Refresh both before changing a rule here.

## 1. Output format: the portable Agent Plugins manifest

Codex accepts two manifest families, chosen by `find_plugin_manifest_path`:

1. **Portable (preferred for new packages)** — `plugin.json` at the plugin root whose `$schema` starts with `https://agent-plugins.org/schemas/`.
2. **Legacy / compatibility** — `.codex-plugin/plugin.json`, then `.claude-plugin/plugin.json`, then `.cursor-plugin/plugin.json`.

The transfer emits **only** the portable manifest. It writes no `.codex-plugin/plugin.json` overlay: an inline `extensions."com.openai"` object replaces that overlay wholesale (the two are never merged), and baransu targets the current Codex release only.

Codex could read the Claude manifest directly through the legacy path, but that route leaves every Claude-only construct in skill bodies untouched (`$ARGUMENTS`, `AskUserQuestion`, `context: fork`, Task wording). The transfer's value is the body rewrite and the hook/agent closure, not the manifest shape.

## 2. Field mapping

| Portable field | Required | Source |
|------|---|---|
| `$schema` | yes | constant `https://agent-plugins.org/schemas/1.0.0/plugin.schema.json` |
| `name` | yes | Claude `name` (error if absent — names cannot be invented) |
| `version` | no | Claude `version`; **omitted** when absent |
| `description` | no | Claude `description`; **omitted** when absent |
| `author`, `homepage`, `repository`, `license`, `keywords` | no | pass through unchanged when present |
| `extensions."com.openai".hooks` | no | `"./hooks/hooks.json"` when at least one hook survives the port (§3) |
| `extensions."com.openai".interface` | no | §4 |

Absent optional fields are omitted, never filled with placeholders — a fabricated `version` or a `description` copied from `name` is worse than an obvious gap. The portable schema sets `additionalProperties: false`, so nothing outside this table is emitted at the root.

## 3. Components

Portable packages discover components from fixed paths, so the manifest carries no component pointers:

| If source has | Codex output |
|----|----|
| `skills/<name>/SKILL.md` | `skills/<name>/` — discovered from the fixed `skills/` path; a `skills` pointer would be ignored and is not emitted |
| `agents/*.md` | No manifest surface exists (plugins cannot register custom agents); emit `.codex-agents/*.toml` and inject package-local fail-closed resolvers into consuming skills |
| `mcp.json` / `.mcp.json` | **Manual review.** Portable packages read root `mcp.json` (no leading dot; every server declares a transport `type`); not copied automatically |
| `hooks/hooks.json` | `hooks/` copied; `extensions."com.openai".hooks = "./hooks/hooks.json"`; unsupported events/types are reported |
| `rules/*.md` | No manifest surface; copy to `rules/` and normalize live references (`CLAUDE.md` → `AGENTS.md`, skill paths to package-relative paths) |
| App connector config | `extensions."com.openai".apps = "./.app.json"` (none in baransu today) |

**Hooks are outcome-ported; MCP remains manual.** Codex loads plugin hooks from the manifest's hook pointer, enables hooks by default, and provides `PLUGIN_ROOT` / `PLUGIN_DATA` plus compatibility aliases `CLAUDE_PLUGIN_ROOT` / `CLAUDE_PLUGIN_DATA`. The transfer copies the hook directory, retains supported events, and names every rejected event or handler in the report:

- **Events** kept: those in `CODEX_HOOK_EVENTS` (`transfer.py`), including `SessionEnd` (Codex ≥0.145.0). A Claude event Codex lacks is dropped and reported — never rewritten to a neighbouring lifecycle event.
- **`SessionEnd` timeout**: Codex defaults SessionEnd handlers to 1 second with a 3-second cap. A source `timeout` above 3 is clamped to 3 and reported; a handler without `timeout` gets a report note that Codex will stop it after 1 second.
- **Handler types** kept: `command` and `mcp_tool` (same `server` / `tool` / `input` fields on both sides). `prompt` and `agent` handlers are parsed but skipped by Codex, so the transfer drops and reports them. Exception: Codex does not run `mcp_tool` handlers on `SessionEnd`, so an `mcp_tool` handler under `SessionEnd` is dropped and reported too.
- **Variables**: command strings are rewritten to the canonical Codex names (`CLAUDE_PLUGIN_ROOT` → `PLUGIN_ROOT`, `CLAUDE_PLUGIN_DATA` → `PLUGIN_DATA`).

Installation does not imply trust; the user must review changed plugin hooks in `/hooks` before they execute.

**Windows behavior is pinned at transfer time.** Codex documents `commandWindows` as the optional Windows-only command override for hook handlers, and gives no cross-platform guarantee for the `PLUGIN_ROOT` path format — on Windows it is a `C:\` path, and a `bash "${PLUGIN_ROOT}/…"` command line frequently lands on WSL bash, which cannot read Windows paths, so the hook errors on every firing. Every kept `command` handler without a source-supplied override therefore gets a `commandWindows`, chosen by the same-name-`.ps1` convention: when the command runs a bundled `.sh` and a sibling `.ps1` with the same basename ships next to it, `commandWindows` runs that native port via `powershell -NoProfile -ExecutionPolicy Bypass -File "${PLUGIN_ROOT}/<path>.ps1"`; otherwise the handler gets `"cmd /c exit 0"`, Windows degrades to a silent no-op instead of wedging the session, and the report names the degrade. `mcp_tool` handlers run no shell and get no override. A source-supplied `commandWindows` is preserved byte-for-byte and always wins. `.ps1` ports targeting Windows PowerShell 5.1 MUST carry a UTF-8 BOM — 5.1 parses BOM-less non-ASCII scripts as ANSI and fails.

Hook scripts still own runtime result translation. A Codex Stop or SubagentStop hook requests continuation either with structured `{"decision":"block","reason":"..."}` output or by exiting 2 with the reason on stderr; `continue:false` takes precedence over continuation decisions. A dual-runtime script can detect Codex through `PLUGIN_ROOT`; transfer preserves script bytes because generic shell-semantic rewriting would be unsafe. Only the structured `hooks.json` command fields receive the canonical variable-name rewrite.

## 4. UI metadata (`extensions."com.openai".interface`)

The transfer fills the fields it can derive:

- `displayName` — from `name`, hyphens → spaces, Title Case.
- `shortDescription` — first 120 chars of `description`; omitted when the source has no description.

Left for the user (they need design judgment or source assets): `longDescription`, `developerName`, `category`, `capabilities`, `websiteURL`, `privacyPolicyURL`, `termsOfServiceURL`, `defaultPrompt` (≤3 prompts, ≤128 chars each), `brandColor`, `composerIcon`, `logo`, `logoDark`, `screenshots`. Keep asset paths relative, starting with `./`, preferably under `./assets/`.

## 5. Dropped fields and manual components

Dropped (no plugin-level Codex equivalent): `lspServers` (Codex plugins don't host LSP). A manifest-level `agents` pointer has no Codex equivalent, but file-based `agents/*.md` content is not dropped: it is converted into the bundled runtime path described below.

`commands` gets a 需人工檢視 line instead of a plain drop: Codex custom prompts are officially **deprecated** — convert each `commands/*.md` into a Codex skill (directory + SKILL.md). Never port to `~/.codex/prompts/`. (Codex auto-migrates `commands/*.md` only for legacy manifests, and skips any command using `$ARGUMENTS`, `!` injection, `@file`, or `{{…}}`; the portable output does not rely on it.)

## 6. Bundled agent and rule closure

When the source plugin ships `agents/*.md`, the transfer emits runtime TOMLs at `<plugin-output>/.codex-agents/*.toml`, rewrites consuming skill references to those files, and injects a resolver that fails with `AGENT_DEFINITION_MISSING` if a definition cannot be read. It does not rely on a manual copy into `~/.codex/agents/`. See [`agent-mapping.md`](agent-mapping.md) §4. (OpenAI's Claude-plugin porting guide instead suggests folding agent procedures into skills; `.codex-agents/` is this transfer's own convention because it keeps each persona intact and isolated.)

When the source ships `rules/`, the transfer copies it to `<plugin-output>/rules/` and normalizes live Claude-only paths. Plugin mode inventories every source top-level component; an unknown component is reported as unhandled so the run cannot silently imply a complete content closure.

## 7. Template assets

The transfer uses one template from `assets/` for the plugin manifest:

- [`codex-plugin.template.json`](../assets/codex-plugin.template.json) — the canonical portable root `plugin.json` shape (`$$schema` is the `string.Template` escape for a literal `$schema` key)

The script renders this template with JSON-safe substitution, parses the result, prunes empty scalars (absent `version` / `description` / `homepage` / `repository` / `license` / `hooks` / `shortDescription`), and merges complex fields (`author`, `keywords`) directly from the translated manifest. Editing the template changes the canonical shape.

The bundled-agent TOML and skill-level `agents/openai.yaml` are NOT templated — they're built directly via `yaml.safe_dump` and `json.dumps`, because honor-system templating proved unsafe for content that may contain quotes, newlines, or escape sequences. See `scripts/transfer.py` `emit_bundled_agent_definition` and `write_skill` for the actual code.
