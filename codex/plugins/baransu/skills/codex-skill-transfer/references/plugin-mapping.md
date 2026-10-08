# Plugin-level Mapping (`.claude-plugin/plugin.json` → Codex plugin manifest)

Rules for the plugin manifest itself, plus the agent / rule / hook content that travels with a whole plugin. For SKILL.md frontmatter and body rules (one level down), see [`skill-mapping.md`](skill-mapping.md). For marketplace catalogs (one level up), see [`marketplace-mapping.md`](marketplace-mapping.md).

Source of truth: the official "Package your plugin" page ([developers.openai.com/plugins/build/plugins](https://developers.openai.com/plugins/build/plugins)), OpenAI's Claude-plugin porting guide ([developers.openai.com/plugins/guides/submit-claude-plugin](https://developers.openai.com/plugins/guides/submit-claude-plugin)), the Codex hooks docs, and the Codex source at `rust-v0.161.0` (`codex-rs/core-plugins/src/{manifest,store}.rs`, `codex-rs/agent-roles/src/loader.rs`, `codex-rs/hooks/src/engine/discovery.rs`). Claude side: Claude Code 2.1.293 plugin manifest reference and plugin loading reference. Refresh these before changing a rule here. Labels: *(inferred)* = derived, not stated officially; *(unpublished)* = not documented.

## 1. Manifest location and format choice

Codex looks for a plugin manifest in this order and uses the first it finds:

1. `plugin.json` at the plugin root whose `$schema` starts with `https://agent-plugins.org/schemas/` (portable Agent Plugins manifest).
2. `.codex-plugin/plugin.json`
3. `.claude-plugin/plugin.json`
4. `.cursor-plugin/plugin.json`

**Pick one Codex format per plugin:**

| Format | Status | Notes |
|---|---|---|
| Portable root `plugin.json` + `extensions."com.openai"` | Recommended by OpenAI for new packages | Components are discovered from fixed paths (`skills/`, `mcp.json`, `hooks/hooks.json`); the script emits this shape |
| `.codex-plugin/plugin.json` | Still supported (compatibility path) | Usually carries `"skills": "./skills/"`; fine for an existing hand-maintained copy — say in the repo docs that the choice is deliberate |

`extensions."com.openai"` replaces the `.codex-plugin` overlay wholesale; the two are never merged. Do not ship both with different content.

**Why not just let Codex read `.claude-plugin/plugin.json`?** It would load, but every Claude-only construct in skill bodies stays untouched (path variables, `$ARGUMENTS`, AskUserQuestion, `context: fork`, slash invocations), and Claude-only components (mods, monitors) come along. The Codex copy's value is the body rewrite and the component closure, not the manifest shape.

## 2. Field mapping

Portable manifest fields:

| Portable field | Required | Source |
|------|---|---|
| `$schema` | yes | constant `https://agent-plugins.org/schemas/1.0.0/plugin.schema.json` |
| `name` | yes | Claude `name` (kebab-case; it is also the component namespace on both sides — keep it identical) |
| `version` | no | Claude `version`; omitted when absent (see §8 — in practice always set it) |
| `description` | no | Claude `description`; omitted when absent |
| `author`, `homepage`, `repository`, `license`, `keywords` | no | pass through unchanged when present |
| `extensions."com.openai".hooks` | no | `"./hooks/hooks.json"` when at least one hook survives the port (§3) |
| `extensions."com.openai".interface` | no | §4 |
| `extensions."com.openai".apps` | no | app connector config, e.g. `"./.app.json"` |
| `extensions."com.openai".onboardingSkill` | no | name of a skill Codex surfaces for onboarding (since 0.156.0) |

Absent optional fields are omitted, never filled with placeholders — a fabricated `version` or a `description` copied from `name` is worse than an obvious gap. The portable schema sets `additionalProperties: false`, so nothing outside this table belongs at the root.

Where the other Claude manifest fields go:

| Claude field | Codex handling |
|---|---|
| `displayName` | `extensions."com.openai".interface.displayName` |
| `defaultEnabled` | No manifest field. Use the marketplace entry's `policy.installation: "INSTALLED_BY_DEFAULT"` (otherwise `AVAILABLE`); per-user state lives in `config.toml` `[plugins."<plugin>@<marketplace>"] enabled` |
| `icon`, `documentationUrl`, `supportUrl`, `privacyPolicyUrl`, `termsOfServiceUrl` | Partly expressible in `interface` (`logo`, `websiteURL`, `privacyPolicyURL`, `termsOfServiceURL`); otherwise drop |
| `metadata` | Drop |
| `userConfig` | Drop — Codex neither prompts for nor expands `user_config.*`. See §5 |
| `dependencies` | Drop — no Codex plugin dependencies. See §5 |
| `settings`, `types`, `channels`, `lspServers`, `outputStyles`, `workflows`, `experimental.{themes,monitors,evals}` | Drop and record (§5) |
| `skills`, `commands`, `agents`, `hooks`, `mcpServers` pointers | Not emitted in the portable format — components come from fixed paths (§3) |

## 3. Components

Portable packages discover components from fixed paths, so the manifest carries no component pointers:

| If source has | Codex output |
|----|----|
| `skills/<name>/SKILL.md` | `skills/<name>/` — discovered from the fixed `skills/` path |
| `agents/*.md` | Plugins cannot register custom agents (§6). Choose option A, B, or C |
| `mcp.json` / `.mcp.json` | Root `mcp.json` (no leading dot); every server declares a transport `type`. The script leaves this for manual review |
| `hooks/hooks.json` (lifecycle hooks) | `hooks/` copied; `extensions."com.openai".hooks = "./hooks/hooks.json"`; unsupported events / handler types removed and recorded |
| `hooks/hooks.json` holding `{"modules": [...]}` (a **mod**) | **Never copy.** Codex reads `hooks/hooks.json` as lifecycle hooks by default *(inferred breakage)*. A whole mod plugin is left out of the Codex catalog |
| `rules/*.md` | No manifest surface; copy to `rules/` and normalize live references (`CLAUDE.md` → `AGENTS.md`, skill paths to package-relative paths) |
| `commands/*.md` | Convert each to a skill (§5) |
| `monitors/monitors.json` | Remove and record — Codex has no monitors |
| `output-styles/` | Remove and record |
| `themes/` | Remove and record |
| `workflows/` | Remove and record |
| `bin/` | Remove and record — no Codex counterpart |
| `settings.json` | Remove and record |
| `.lsp.json` | Remove and record — Codex plugins host no LSP |
| App connector config | `extensions."com.openai".apps` |

**Hooks.** Codex loads plugin hooks from `hooks/hooks.json` by default (a manifest `hooks` value replaces the default) and sets `PLUGIN_ROOT` / `PLUGIN_DATA` plus the compatibility aliases `CLAUDE_PLUGIN_ROOT` / `CLAUDE_PLUGIN_DATA` in the hook command environment. The file format matches Claude's three levels (event → matcher → handlers).

- **Events.** Codex has 12: `SessionStart`, `SessionEnd`, `SubagentStart`, `SubagentStop`, `PreToolUse`, `PermissionRequest`, `PostToolUse`, `PreCompact`, `PostCompact`, `UserPromptSubmit`, `Stop`, and the Codex-only `Interrupt`. Claude has 30+ (e.g. `Setup`, `InstructionsLoaded`, `PostToolUseFailure`, `Notification`, `FileChanged`, `PreModelSwitch`, …). A Claude event Codex lacks is removed and recorded — never rewritten to a neighbouring lifecycle event. The script's `CODEX_HOOK_EVENTS` does not list `Interrupt`; that only matters for completeness, since no Claude source uses it.
- **`SessionEnd` / `Interrupt` timeout.** Codex defaults these to 1 second with a 3-second cap. Clamp a larger source `timeout` to 3 and record it.
- **Handler types.** `command` and `mcp_tool` run (same `server` / `tool` / `input` fields on both sides). `prompt` and `agent` are parsed but skipped; `http` does not exist — rewrite as `command` or remove. `SessionEnd` does not run `mcp_tool`.
- **Fields.** Codex supports `statusMessage`, `timeout`, `async` (at most 8 concurrent), `additionalContextLimit`, and `commandWindows` (`command_windows` in TOML). Claude's `if`, `once`, `shell`, and `args` have no Codex counterpart. `additionalContext` defaults to about 2,500 tokens; longer output is spilled to a temp file.
- **Blocking.** `PreToolUse` blocks with `permissionDecision: "deny"`, legacy `decision: "block"`, or exit 2; `allow` + `updatedInput` rewrites input; `ask` is not supported (marked failed, then execution continues) — never rely on it. `Stop` / `SubagentStop` continue the model with `decision: "block"`; `continue: false` takes precedence.
- **Variables.** In hook command strings, CLAUDE_PLUGIN_ROOT → `PLUGIN_ROOT` and CLAUDE_PLUGIN_DATA → `PLUGIN_DATA` (canonical names; the aliases also work). A dual-runtime script can detect Codex by the presence of `PLUGIN_ROOT` *(inferred)*.
- **Trust.** Non-managed hooks, plugin hooks included, run only after the user reviews and trusts them in `/hooks`; trust is bound to the definition's hash, so a changed hook needs re-trust. Say so in the Codex README.
- **Distribution.** A plugin with lifecycle hooks cannot be listed in OpenAI's public plugin directory; it installs manually.

**Windows behavior.** Codex documents `commandWindows` as the optional Windows-only override and gives no cross-platform guarantee for the `PLUGIN_ROOT` path format — on Windows it is a `C:\` path, and a `bash "${PLUGIN_ROOT}/…"` command line frequently lands on WSL bash, which cannot read Windows paths, so the hook errors on every firing. Give every `command` handler a `commandWindows`: when the command runs a bundled `.sh` and a same-name `.ps1` ships next to it, run that via `powershell -NoProfile -ExecutionPolicy Bypass -File "${PLUGIN_ROOT}/<path>.ps1"`; otherwise use `"cmd /c exit 0"` so Windows degrades to a silent no-op instead of wedging the session, and record the degrade. `mcp_tool` handlers run no shell and need no override. A source-supplied `commandWindows` always wins. `.ps1` files targeting Windows PowerShell 5.1 MUST carry a UTF-8 BOM — 5.1 parses BOM-less non-ASCII scripts as ANSI and fails. (The script applies this same-name-`.ps1` convention automatically.)

Hook scripts still own runtime result translation; their bytes are kept as-is because generic shell-semantic rewriting would be unsafe. Only the structured `hooks.json` command fields get the variable-name rewrite.

## 4. UI metadata (`extensions."com.openai".interface`)

Derivable fields:

- `displayName` — Claude `displayName`, or `name` with hyphens → spaces in Title Case.
- `shortDescription` — first 120 chars of `description`; omitted when the source has none.

Left for the author (they need design judgment or source assets): `longDescription`, `developerName`, `category`, `capabilities`, `websiteURL`, `privacyPolicyURL`, `termsOfServiceURL`, `defaultPrompt` (≤ 3 prompts, ≤ 128 chars each), `brandColor`, `composerIcon`, `logo`, `logoDark`, `screenshots`. Keep asset paths relative, starting with `./`, preferably under `./assets/`.

## 5. Claude-only manifest features

OpenAI's porting guide lists these as unsupported; remove them from the Codex copy and record each removal:

| Feature | Codex handling |
|---|---|
| `userConfig` (prompted at enable time; `user_config.KEY` substitution; `CLAUDE_PLUGIN_OPTION_<KEY>` env vars) | Values that vary per task become skill inputs. Machine-level settings move to an env var or a config file the skill reads, with an actionable error message when the value is missing |
| `dependencies` (semver ranges, git tags `{name}--v{version}`) | No plugin dependencies in Codex. Name the required plugins in the Codex README or the skill body |
| `lspServers` / `.lsp.json` | Codex plugins host no LSP |
| `outputStyles` / `output-styles/` | No counterpart |
| `experimental.themes`, `experimental.monitors`, `experimental.evals` | No counterpart (`claude plugin eval` suites stay Claude-side) |
| `channels`, `workflows`, `settings`, `types` | No counterpart |
| Mods (`hooks/hooks.json` with `modules`, manifest `types`) | No in-process UI or behavior extension API in Codex; omit the mod plugin. Codex's `tui.status_line` only picks from fixed IDs, and OpenAI Plugin Extensions (MCP Apps) are a different architecture in the ChatGPT UI |

`commands/*.md` gets a conversion, not a plain drop: Codex custom prompts are deprecated — convert each command into a skill (directory + SKILL.md). Never port to `~/.codex/prompts/`. (Codex auto-migrates `commands` only for legacy manifests and skips any command using `$ARGUMENTS` or `{{…}}`; do not rely on it.)

## 6. Bundled agents and rules

Codex 0.161 plugins still do **not** register agents: the plugin manifest has no agents field, and the role loader only scans config-layer `agents/` directories (`~/.codex/agents/`, `.codex/agents/`) plus `[agents.<name>] config_file` entries. Claude registers `agents/*.md` as `<plugin>:<agent>` (ignoring their `hooks`, `mcpServers`, and `permissionMode`). Three options:

| Option | How | Trade-off |
|---|---|---|
| **A. Fold into the skill** (OpenAI's porting advice) | Move the agent's procedure into the consuming skill (body or `references/`), and spawn a built-in `worker` / `explorer` / `default` with that text | Simplest; loses the standalone persona file |
| **B. Package-local TOML + resolver** | Ship `.codex-agents/<name>.toml` in the package; the consuming skill resolves the file, reads it, and inlines `developer_instructions` into the `spawn_agent` message; a missing file stops with `AGENT_DEFINITION_MISSING` | Keeps each persona intact; needs the resolver text in every consuming skill. The script emits this |
| **C. User config** | The user adds `[agents.<name>] description = …` and `config_file = <path to the TOML>` to their own `config.toml` | Real named agent; the installed cache path changes with every version *(inferred)*, and the plugin must never write user config itself — document it only |

See [`agent-mapping.md`](agent-mapping.md) §4 for option B's resolver and TOML shape.

When the source ships `rules/`, copy it to `<plugin>/rules/` and normalize live Claude-only paths. Inventory every source top-level component; an unknown one is recorded as unhandled so nobody reads the copy as complete.

## 7. Template assets

[`codex-plugin.template.json`](../assets/codex-plugin.template.json) is the canonical portable root `plugin.json` shape (`$$schema` is the `string.Template` escape for a literal `$schema` key). The script renders it with JSON-safe substitution, prunes empty scalars (absent `version` / `description` / `homepage` / `repository` / `license` / `hooks` / `shortDescription`), and merges `author` and `keywords` from the source manifest. For a hand port, copy it, fill it, and add `apps` / `onboardingSkill` / further `interface` keys when needed.

The bundled-agent TOML and skill-level `agents/openai.yaml` are not templated in the script — they're built via `yaml.safe_dump` and `json.dumps`, because template substitution proved unsafe for content containing quotes, newlines, or escape sequences. When writing them by hand, quote with the same care.

## 8. Versions and caching

| | Claude Code | Codex |
|---|---|---|
| Version source | manifest `version` → marketplace entry `version` → source commit SHA | manifest `version`; when absent the docs say a local plugin's cache segment is `local` |
| Cache path | `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/`; old versions removed after 14 days | `~/.codex/plugins/cache/<marketplace>/<plugin>/<version>/`; installing a new version removes the old directory |
| Update trigger | A different version string. A pinned, unchanged version never updates. A marketplace added from a local path loads in place without a bump | `codex plugin marketplace upgrade <marketplace>` refreshes the git snapshot; the plugin cache is keyed by manifest version. Since 0.154.0 running sessions refresh skills and hooks after an external upgrade or rollback |

Rules:

- Bump `version` in **both** copies on every distributed change.
- Keep the strings plain semver. The version is a path segment of the Codex cache directory; whether `+build` metadata is accepted there is *(unpublished)*. Avoid it, or install once and check.
- Whether Codex recopies a plugin whose version is unchanged but whose content changed is *(unpublished)*. Always bump.
- Skills have no `PLUGIN_DATA` in Codex (hooks only). A skill that keeps persistent data needs an explicit Codex-side location (under `~/.codex/` or the project).
