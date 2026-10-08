## Contents

- 1. The two Codex paths
- 2. SKILL.md frontmatter mapping (Path 1 specifics)
- 3. Body rewrite for Path 1
- 4. Bundled runtime agent generation (`agents/*.md` → `.codex-agents/*.toml`)
- 5. Naming-collision pitfall

# Agent Mapping (Claude `context: fork` → Codex Subagents)

This file owns the `Claude agent → Codex subagent` translation in full. It covers two layers that earlier versions of this skill split awkwardly:

- **SKILL.md frontmatter level** — when a skill declares `context: fork` + `agent: <type>`, that's the per-skill request to spawn a forked subagent. See §1–§3.
- **Plugin level** — when a Claude plugin ships `agents/*.md` files, those are executable subagent definitions. See §4 for the package-local runtime mapping used by `codex-skill-transfer`.

[`skill-mapping.md`](skill-mapping.md) and [`plugin-mapping.md`](plugin-mapping.md) cross-ref into this file rather than duplicating the rules.

## 1. The two Codex paths

Codex **does** have an equivalent for `context: fork` — native Subagents at `.codex/agents/{name}.toml` — but the mapping crosses the skill-package boundary into the user's Codex configuration. The transfer cannot decide which path you want, so for any source skill with `context: fork`, it refuses to auto-port and surfaces these two options. (A third path — running Codex as an MCP server orchestrated by Agents SDK handoffs — went away when Codex 0.154.0 removed that server mode; embedding Codex now goes through the experimental app-server JSON-RPC, which is out of scope here.)

### Path 1: Codex native Subagents (closest equivalent)

Codex defines subagents as standalone TOML files at:

- `~/.codex/agents/{name}.toml` (personal)
- `.codex/agents/{name}.toml` (project-scoped, trusted repo)

Required fields: `name`, `description`, `developer_instructions`. Optional fields inherit from the parent session when omitted: `nickname_candidates`, `model`, `model_reasoning_effort`, `sandbox_mode`, `mcp_servers`, and `skills.config`. Three built-in agents ship by default: `default`, `worker`, `explorer`.

Officially confirmed by the Codex Subagents docs and the `rust-v0.161.0` role loader (checked 2026-10-08):

- Required custom-agent fields: `name`, `description`, `developer_instructions`.
- Optional custom-agent/config fields: `nickname_candidates`, `model`, `model_reasoning_effort`, `sandbox_mode`, `mcp_servers`, `skills.config`.
- Built-ins: `default`, `worker`, `explorer`.
- Global settings: `agents.enabled` (default true), `agents.max_concurrent_threads_per_session`, `agents.default_subagent_model`, `agents.default_subagent_reasoning_effort`, and `agents.interrupt_message`. `agents.max_threads` remains a legacy alias for the concurrency cap.
- Model guidance: omit `model` and `model_reasoning_effort` unless you need deterministic routing; Codex can choose or inherit a balanced setup. Model names turn over faster than this file — when pinning, take the current recommendation from the Subagents docs at port time rather than from here, and re-check existing pins against the Codex changelog (models are retired on announced dates). Effort values are model-dependent (`low` | `medium` | `high` | `xhigh` | `max` | `ultra`).
- `mcp_servers` is a config **table** (`[mcp_servers.<id>]` with `url` / `command` …), not a list of ids. Role files reject unknown or mistyped keys, so a wrong shape makes the whole agent fail to load. The stub places every commented table (`[[skills.config]]`, `[mcp_servers.<id>]`) after all top-level key comments, so uncommenting any line never pulls a top-level key into a table.
- A custom agent whose `name` matches a built-in (`default`, `worker`, `explorer`) overrides it.

**Spawn tool** (`codex-rs/core/src/tools/handlers/multi_agents_spec.rs`):

| Version | Parameters |
|---|---|
| v1 (`multi_agent`) | `message` or `items`, `agent_type`, `fork_context`, `model`, `reasoning_effort` |
| v2 (`multi_agent_v2`) | `task_name` (required), `message` (required), `agent_type`, `fork_turns` (`"none"` / `"all"` / N; default `"all"`), `model`, `reasoning_effort` |

Companion tools: `send_input`, `send_message`, `followup_task`, `resume_agent`, `wait_agent`, `list_agents`, `close_agent`, `interrupt_agent`. Which version a session exposes depends on feature flags — check `codex features list` (on the 2026-10-08 reference machine `multi_agent` was stable and on, `multi_agent_v2` was not stable). To ask for a clean context, write both forms into the body: `fork_turns="none"` for v2, `fork_context=false` for v1. Whether a clean-context spawn is isolated enough for an independent-verdict skill still needs a runtime probe *(inferred)* — see [`CODEX_PORT_PLAN.md`](CODEX_PORT_PLAN.md) T0-2.

**Spawn semantics:**
- Explicitly requested or instruction-driven — Codex spawns after a direct user request or when applicable `AGENTS.md` / skill instructions request delegation.
- Spawning is via natural-language instruction in the SKILL.md body (e.g. "Spawn a `worker` subagent to handle X"), not via frontmatter.
- Multiple subagents run in parallel; Codex waits for all and consolidates.
- Subagents inherit the parent sandbox and approval policy, and the parent model when none is set; live parent runtime overrides take precedence over custom-agent TOML defaults.
- In non-interactive flows, a subagent action that needs fresh approval fails and surfaces the error back to the parent workflow.

**Best for**: heavy-IO forks where context isolation is the *reason* the original used `context: fork` — e.g. independent review perspectives.

### Path 2: Skill chain (lightweight)

Split the original skill into two skills. The first ends with an instruction telling the model (or the user) to invoke the second via `$skill-name` mention or the `/skills` selector. No forking; both run in the same Codex thread, so context isn't isolated.

**Best for**: short forked work where context pollution isn't a concern — e.g. a few hundred tokens of perspective guidance where running in the same thread is acceptable.

## 2. SKILL.md frontmatter mapping (Path 1 specifics)

When the user picks Path 1, the per-skill frontmatter translates as follows:

| Claude SKILL.md frontmatter | Codex `.codex/agents/{name}.toml` |
|--------|--------|
| `context: fork` | (implicit — opening a TOML file *is* the fork) |
| `agent: Explore` | `name = "explorer"` (built-in) or matching custom |
| `agent: general-purpose` | `name = "default"` |
| `agent: Plan` | custom TOML mirroring Plan agent's behavior |
| `model: opus` | Usually omit `model` and inherit. If pinning is required, choose the current Codex model from the Subagents docs at port time. |
| `effort: high` | Spawn parameter `reasoning_effort: "high"` for a one-off spawn, or `model_reasoning_effort = "high"` in a custom-agent TOML |
| `background: true` | No field. Say in the body whether to wait for the subagent (`wait_agent`) or continue |
| Agent-file `isolation: worktree` | No counterpart; if the agent must not touch the working tree, say so in its instructions and rely on `sandbox_mode` |
| Agent-file `maxTurns`, `memory`, `omitClaudeMd`, `color`, `initialPrompt`, `skills` | No counterpart; drop and record (fold `initialPrompt` into the spawn message when it carried task content) |
| Agent-file `hooks`, `mcpServers`, `permissionMode` | Already ignored by Claude for plugin agents; drop |
| `allowed-tools: ...` / `tools: ...` | No Codex field. The optional native custom-agent export records the Claude tool names as a plain comment and shows the `# [mcp_servers.<id>]` table shape; Claude built-in tools have no MCP equivalent, so narrow capability through `sandbox_mode` instead. Bundled runtime definitions omit this operator-specific pin and inherit the parent runtime. |

## 3. Body rewrite for Path 1

Replace the Claude-side prose that describes the forked task with an explicit Codex spawn instruction:

```markdown
Spawn a `{agent_name}` subagent and pass it this task:
{original SKILL.md body content describing the forked work}
Wait for the subagent's result and use it as input for the next step.
```

The intent is preserved (the model gets the same factual context); only the *who runs it* changes from "an implicit forked subagent" to "an explicit Codex subagent invocation."

## 4. Bundled runtime agent generation (`agents/*.md` → `.codex-agents/*.toml`)

Codex only auto-discovers custom agents from user `~/.codex/agents/` or project
`.codex/agents/` (plus `[agents.<name>] config_file` entries in `config.toml`);
this still holds at 0.161. A plugin-private TOML is not auto-registered, and a
plugin must not write into either user config location. Requiring the user to
copy stubs is also insufficient: the installed plugin can then name an agent
whose definition is absent, inviting the model to improvise the role.

This section describes option B from [`plugin-mapping.md`](plugin-mapping.md)
§6. Option A (fold the procedure into the skill; OpenAI's porting advice) needs
no TOML at all, and option C (the user registers the TOML through
`[agents.<name>] config_file`) is documented for the user, never applied by the
port.

Option B ships a complete, package-local pair:

1. Every `agents/<name>.md` becomes
   `<plugin-output>/.codex-agents/<name>.toml`.
2. Every consuming skill points to that exact TOML and receives the
   `Codex Port Adapter - Bundled Agent Resolution` guard.

Before dispatch, the guard resolves the path from `SKILL.md` and verifies it is
readable. A missing definition stops with `AGENT_DEFINITION_MISSING: <path>`;
the caller must never invent, summarize, or substitute a role from the name.

Two ways to hand the definition to the subagent:

- **Inline (preferred for hand ports).** The lead reads the TOML itself and
  places `developer_instructions` verbatim in the `spawn_agent` message, ahead
  of the task input, with relative paths resolved from the TOML directory. The
  subagent cannot skip or partially read its role, and this does not conflict
  with the Codex skill prompt's rule against delegating the reading of skill
  instructions to a subagent — the lead does the reading *(inferred)*.
- **By path (what the script's generated guard does).** The lead passes the
  absolute TOML path plus task input to a generic subagent whose first
  instruction is to read `developer_instructions` completely and resolve its
  relative paths from the TOML directory.

### 4.1 Runtime definition shape

`name` and `description` use JSON-quoted strings. `developer_instructions`
uses a TOML literal multi-line string, with an escaped basic multi-line
fallback when the body contains `'''`.

```toml
# Bundled Codex runtime definition generated from <agent-name>.md.
# This file is package-local. The invoking skill passes its exact path
# to a generic Codex subagent; plugins do not auto-register custom agents.

name = "<name>"
description = "<first-line of frontmatter description if found>"

developer_instructions = '''
<translated Markdown body, with frontmatter stripped>
'''
```

The runtime definition deliberately omits `model`,
`model_reasoning_effort`, `sandbox_mode`, `mcp_servers`, and `skills.config`.
Those are operator/runtime policy and should inherit from the parent session.

### 4.2 Package-relative instruction rewrite

The agent body is executable content, not archival prose. The transfer
normalizes references so they resolve from `.codex-agents/<name>.toml`:

- `${CLAUDE_PLUGIN_ROOT}/skills/...` → `../skills/...`
- `plugins/<plugin>/skills/...` → `../skills/...`
- `plugins/<plugin>/rules/...` → `../rules/...`
- `agents/<name>.md` → `../.codex-agents/<name>.toml`
- `CLAUDE.md` → `AGENTS.md`
- `.claude/` → `.codex/`
- Claude Task-tool wording → Codex subagent wording

The optional `emit_agent_stub` helper still exists for an explicit native
custom-agent export to `~/.codex/agents/` or project `.codex/agents/`. That
flat export is not used by plugin mode and is never required for the plugin to
find its agents.

## 5. Naming-collision pitfall

Codex uses `agents/` in multiple unrelated places:

- `agents/openai.yaml` *inside a skill package* — UI metadata + `policy` + MCP `dependencies`. The Codex copy carries it when a SKILL.md has `disable-model-invocation: true` or needs UI metadata; it lives inside the per-skill folder and is harmless. Keep it out of the Claude copy.
- `.codex/agents/{name}.toml` *in user/project Codex config* — auto-discovered custom-agent definitions. The skill never writes here.
- `.codex-agents/{name}.toml` *inside generated plugin output* — bundled runtime definitions consumed through the generated fail-closed resolver; this directory is intentionally not presented as auto-discovered config.

Keep the two straight; they're unrelated despite the directory-name collision.
