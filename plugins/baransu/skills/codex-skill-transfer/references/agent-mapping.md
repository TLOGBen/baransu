## Contents

- 1. The three Codex paths
- 2. SKILL.md frontmatter mapping (Path 1 specifics)
- 3. Body rewrite for Path 1
- 4. Bundled runtime agent generation (`agents/*.md` → `.codex-agents/*.toml`)
- 5. Naming-collision pitfall

# Agent Mapping (Claude `context: fork` → Codex Subagents)

This file owns the `Claude agent → Codex subagent` translation in full. It covers two layers that earlier versions of this skill split awkwardly:

- **SKILL.md frontmatter level** — when a skill declares `context: fork` + `agent: <type>`, that's the per-skill request to spawn a forked subagent. See §1–§3.
- **Plugin level** — when a Claude plugin ships `agents/*.md` files, those are executable subagent definitions. See §4 for the package-local runtime mapping used by `codex-skill-transfer`.

[`skill-mapping.md`](skill-mapping.md) and [`plugin-mapping.md`](plugin-mapping.md) cross-ref into this file rather than duplicating the rules.

## 1. The three Codex paths

Codex **does** have an equivalent for `context: fork` — native Subagents at `.codex/agents/{name}.toml` — but the mapping crosses the skill-package boundary into the user's Codex configuration. The transfer cannot decide which path you want, so for any source skill with `context: fork`, it refuses to auto-port and surfaces these three options:

### Path 1: Codex native Subagents (closest equivalent)

Codex defines subagents as standalone TOML files at:

- `~/.codex/agents/{name}.toml` (personal)
- `.codex/agents/{name}.toml` (project-scoped, trusted repo)

Required fields: `name`, `description`, `developer_instructions`. Optional fields inherit from the parent session when omitted: `nickname_candidates`, `model`, `model_reasoning_effort`, `sandbox_mode`, `mcp_servers`, and `skills.config`. Three built-in agents ship by default: `default`, `worker`, `explorer`.

Officially confirmed by the Codex Subagents docs (2026-07):

- Required custom-agent fields: `name`, `description`, `developer_instructions`.
- Optional custom-agent/config fields: `nickname_candidates`, `model`, `model_reasoning_effort`, `sandbox_mode`, `mcp_servers`, `skills.config`.
- Built-ins: `default`, `worker`, `explorer`.
- Global settings: `agents.max_concurrent_threads_per_session`, `agents.default_subagent_model`, `agents.default_subagent_reasoning_effort`, and `agents.interrupt_message`. `agents.max_threads` remains a legacy alias for the concurrency cap.
- Model guidance: omit `model` and `model_reasoning_effort` unless you need deterministic routing; Codex can choose or inherit a balanced setup. When pinning, start with `gpt-5.6` for demanding agents, use `gpt-5.4` only for workflows pinned to GPT-5.4, and use `gpt-5.6-terra` for fast read-heavy scans.

**Spawn semantics:**
- Explicitly requested or instruction-driven — current local Codex releases spawn after a direct user request or when applicable `AGENTS.md` / skill instructions request delegation.
- Spawning is via natural-language instruction in the SKILL.md body (e.g. "Spawn a `worker` subagent to handle X"), not via frontmatter.
- Multiple subagents run in parallel; Codex waits for all and consolidates.
- Subagents inherit the parent sandbox and approval policy; live parent runtime overrides take precedence over custom-agent TOML defaults.
- In non-interactive flows, a subagent action that needs fresh approval fails and surfaces the error back to the parent workflow.

**Best for**: heavy-IO forks where context isolation is the *reason* the original used `context: fork` — e.g. baransu's impl-agent and the `/review` perspective reviewers.

### Path 2: Skill chain (lightweight)

Split the original skill into two skills. The first ends with an instruction telling the model (or the user) to invoke the second via `$skill-name` mention or the `/skills` selector. No forking; both run in the same Codex thread, so context isn't isolated.

**Best for**: short forked work where context pollution isn't a concern. The three perspective agents in baransu `/review` (architecture / quality / security) might fit here — each is a few hundred tokens of guidance, and running in the same thread is acceptable.

### Path 3: Codex MCP server + OpenAI Agents SDK (heavy)

Run `codex mcp-server` and orchestrate from external SDK code that uses `handoffs` between agents. Each agent can have its own git worktree for full isolation.

**Best for**: programmatic, auditable pipelines (CI / cloud agents). Out of scope for typical baransu desktop usage.

## 2. SKILL.md frontmatter mapping (Path 1 specifics)

When the user picks Path 1, the per-skill frontmatter translates as follows:

| Claude SKILL.md frontmatter | Codex `.codex/agents/{name}.toml` |
|--------|--------|
| `context: fork` | (implicit — opening a TOML file *is* the fork) |
| `agent: Explore` | `name = "explorer"` (built-in) or matching custom |
| `agent: general-purpose` | `name = "default"` |
| `agent: Plan` | custom TOML mirroring Plan agent's behavior |
| `model: opus` | Usually omit `model` and inherit. If pinning is required, choose the current Codex model intentionally (`gpt-5.6` for demanding agents as of 2026-07). |
| `effort: high` | `model_reasoning_effort = "high"` |
| `allowed-tools: ...` / `tools: ...` | For an optional native custom-agent export, emit a **commented** `# mcp_servers = [...]` hint. Codex `mcp_servers` takes MCP server ids, not Claude tool names. Bundled runtime definitions omit this operator-specific pin and inherit the parent runtime. |

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
`.codex/agents/`. A plugin-private TOML is not auto-registered, and a plugin
must not write into either user config location. Requiring the user to copy
stubs is also insufficient: the installed plugin can then name an agent whose
definition is absent, inviting the model to improvise the role.

Plugin mode therefore emits a complete, package-local pair:

1. Every `agents/<name>.md` becomes
   `<plugin-output>/.codex-agents/<name>.toml`.
2. Every consuming skill points to that exact TOML and receives the
   `Codex Port Adapter - Bundled Agent Resolution` guard.

Before dispatch, the guard resolves the path from `SKILL.md`, verifies it is
readable, and passes the absolute TOML path plus task input to a generic Codex
subagent. The subagent's first instruction is to read
`developer_instructions` completely and resolve its relative paths from the
TOML directory. A missing definition stops with
`AGENT_DEFINITION_MISSING: <path>`; the caller must never invent, summarize, or
substitute a role from the name.

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
- `plugins/baransu/skills/...` → `../skills/...`
- `plugins/baransu/rules/...` → `../rules/...`
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

- `agents/openai.yaml` *inside a skill package* — UI metadata + `policy` + MCP `dependencies`. The skill DOES emit this when a SKILL.md has `disable-model-invocation: true`; it lives inside the per-skill output and is harmless.
- `.codex/agents/{name}.toml` *in user/project Codex config* — auto-discovered custom-agent definitions. The skill never writes here.
- `.codex-agents/{name}.toml` *inside generated plugin output* — bundled runtime definitions consumed through the generated fail-closed resolver; this directory is intentionally not presented as auto-discovered config.

Keep the two straight; they're unrelated despite the directory-name collision.
