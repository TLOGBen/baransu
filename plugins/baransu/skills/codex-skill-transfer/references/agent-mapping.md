## Contents

- 1. The three Codex paths
- 2. SKILL.md frontmatter mapping (Path 1 specifics)
- 3. Body rewrite for Path 1
- 4. Agent stub generation (`agents/*.md` → `.codex-agents-templates/*.toml`)
- 5. Naming-collision pitfall

# Agent Mapping (Claude `context: fork` → Codex Subagents)

This file owns the `Claude agent → Codex subagent` translation in full. It covers two layers that earlier versions of this skill split awkwardly:

- **SKILL.md frontmatter level** — when a skill declares `context: fork` + `agent: <type>`, that's the per-skill request to spawn a forked subagent. See §1–§3.
- **Plugin level** — when a Claude plugin ships `agents/*.md` files, those are subagent definitions. See §4 for the stub-generation rules used by `codex-skill-transfer`.

[`skill-mapping.md`](skill-mapping.md) and [`plugin-mapping.md`](plugin-mapping.md) cross-ref into this file rather than duplicating the rules.

## 1. The three Codex paths

Codex **does** have an equivalent for `context: fork` — native Subagents at `.codex/agents/{name}.toml` — but the mapping crosses the skill-package boundary into the user's Codex configuration. The transfer cannot decide which path you want, so for any source skill with `context: fork`, it refuses to auto-port and surfaces these three options:

### Path 1: Codex native Subagents (closest equivalent)

Codex defines subagents as standalone TOML files at:

- `~/.codex/agents/{name}.toml` (personal)
- `.codex/agents/{name}.toml` (project-scoped, trusted repo)

Required fields: `name`, `description`, `developer_instructions`. Optional fields inherit from the parent session when omitted: `nickname_candidates`, `model`, `model_reasoning_effort`, `sandbox_mode`, `mcp_servers`, and `skills.config`. Three built-in agents ship by default: `default`, `worker`, `explorer`.

Officially confirmed by the Codex Subagents docs (2026-06):

- Required custom-agent fields: `name`, `description`, `developer_instructions`.
- Optional custom-agent/config fields: `nickname_candidates`, `model`, `model_reasoning_effort`, `sandbox_mode`, `mcp_servers`, `skills.config`.
- Built-ins: `default`, `worker`, `explorer`.
- Global settings: `agents.max_threads` default `6`, `agents.max_depth` default `1`, optional `agents.job_max_runtime_seconds`.
- Model guidance: omit `model` and `model_reasoning_effort` unless you need deterministic routing; Codex can choose or inherit a balanced setup. When pinning, start with `gpt-5.5` for demanding agents, use `gpt-5.4` only for workflows pinned to GPT-5.4, and use `gpt-5.4-mini` for fast read-heavy scans.

**Spawn semantics:**
- Explicit only — Codex never spawns a subagent without the parent telling it to.
- Spawning is via natural-language instruction in the SKILL.md body (e.g. "Spawn a `worker` subagent to handle X"), not via frontmatter.
- Multiple subagents run in parallel; Codex waits for all and consolidates.
- Subagents inherit the parent sandbox and approval policy; live parent runtime overrides take precedence over custom-agent TOML defaults.
- In non-interactive flows, a subagent action that needs fresh approval fails and surfaces the error back to the parent workflow.
- Depth is capped by `agents.max_depth`; the default `1` allows direct child agents but prevents deeper recursion.

**Best for**: heavy-IO forks where context isolation is the *reason* the original used `context: fork` — e.g. baransu `/execute`'s impl-agent, `/triage`'s investigator-agent.

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
| `model: opus` | Usually omit `model` and inherit. If pinning is required, choose the current Codex model intentionally (`gpt-5.5` for demanding agents as of 2026-06). |
| `effort: high` | `model_reasoning_effort = "high"` |
| `allowed-tools: ...` / `tools: ...` | emitted as a **commented** `# mcp_servers = [...]` line in the stub. Codex `mcp_servers` takes MCP server ids (not Claude tool names) so the user must rename each entry to the matching Codex MCP server before uncommenting. |

## 3. Body rewrite for Path 1

Replace the Claude-side prose that describes the forked task with an explicit Codex spawn instruction:

```markdown
Spawn a `{agent_name}` subagent and pass it this task:
{original SKILL.md body content describing the forked work}
Wait for the subagent's result and use it as input for the next step.
```

The intent is preserved (the model gets the same factual context); only the *who runs it* changes from "an implicit forked subagent" to "an explicit Codex subagent invocation."

## 4. Agent stub generation (`agents/*.md` → `.codex-agents-templates/*.toml`)

Claude plugins ship subagent definitions as Markdown files in `agents/`. Codex's equivalent is `~/.codex/agents/<name>.toml` — TOML, **user-side**, outside the plugin package. Two reasons not to auto-write directly to `~/.codex/agents/`:

1. The plugin cannot safely reach into the user's config directory.
2. Each agent needs choices (model, reasoning effort, sandbox, MCP servers) the transfer can't make.

Therefore the transfer emits **stubs** at `<output>/.codex-agents-templates/<name>.toml`. The user reviews each stub and copies into their config dir.

### 4.1 Stub shape

The stub uses TOML literal multi-line strings (`'''...'''`) for the body — they accept any character except three consecutive single-quotes, so no escaping is needed for the most common content. `name` and `description` use JSON-quoted strings (`json.dumps`) for ironclad escaping of quotes / newlines / unicode.

```toml
# Stub generated from <agent-name>.md.
# Review before copying to ~/.codex/agents/<name>.toml (personal)
# or .codex/agents/<name>.toml (project-scoped trusted repo).
# See codex-skill-transfer references/agent-mapping.md for the mapping rules.

name = "<name>"
description = "<first-line of frontmatter description if found>"

developer_instructions = '''
<the original .md body, with frontmatter stripped>
'''

# Choose what to fill in below; omit optional fields to inherit from the parent session.
#
# model = "gpt-5.5"                   # demanding agents; use gpt-5.4-mini for light read-heavy scans
# model_reasoning_effort = "high"      # minimal | low | medium | high | xhigh
# sandbox_mode = "workspace-write"     # read-only | workspace-write | danger-full-access; parent runtime overrides win
# mcp_servers = []                     # list of MCP server ids the agent may invoke
# Sandbox note: source tools look read-only; consider a read-only sandbox unless the prompt requires writes.
# nickname_candidates = []             # cosmetic names for spawned instances
#
# [[skills.config]]                    # optional per-agent skill enable/disable override
# path = "/path/to/skill/SKILL.md"
# enabled = false
```

If the body contains literal `'''`, the script falls back to TOML basic multi-line (`"""..."""`) with full backslash + quote escape. This is rare for natural-language agent instructions.

All commented optional fields in the stub are official Codex custom-agent/config fields as of 2026-06. They are commented because inheritance is the safer default and because pinning model, sandbox, MCP, or per-agent skill visibility is an operator choice.

The script adds a sandbox note derived from Claude `tools:`:

- Read/Grep/Glob-style agents get a read-only suggestion.
- Write/Edit/Bash-style agents get a workspace-write + approval-policy warning.
- Missing `tools:` gets an inheritance note.

This is intentionally advisory. Codex custom agents still inherit the parent runtime policy, and live `/permissions` / CLI overrides take precedence over TOML defaults.

### 4.2 What the user fills in after copying

- `model` — Codex model id. Omit to inherit or let Codex choose; use `"gpt-5.5"` for demanding agents, `"gpt-5.4-mini"` for light read-heavy scans, or `"gpt-5.4"` only when the workflow is intentionally pinned.
- `model_reasoning_effort` — map from Claude's `effort` if it was present (`minimal` / `low` / `medium` / `high` / `xhigh`).
- `sandbox_mode` — usually safer to omit; parent session policy and live runtime overrides apply.
- `mcp_servers` — list of MCP server ids this agent should access. If the Claude source had `tools: ...`, the stub already includes a commented suggestion with the original Claude tool names; rename each entry to the corresponding Codex MCP server id, then uncomment.
- `nickname_candidates` — optional cosmetic names.
- `skills.config` — optional per-agent skill enable/disable overrides when a custom agent should see a narrower or broader skill set than the parent.

### 4.3 What the stub deliberately doesn't translate

The Markdown body lands in `developer_instructions` verbatim because the agent's *prompt* is the meaningful content. References to Claude-specific tools (`Task`, `AskUserQuestion`, etc.) survive unchanged — the user adapts these by hand using the body-rewrite table in [`skill-mapping.md`](skill-mapping.md) §6 when they migrate the stub into their Codex config.

## 5. Naming-collision pitfall

Codex uses `agents/` in two **different** places, and this skill writes to neither at runtime:

- `agents/openai.yaml` *inside a skill package* — UI metadata + `policy` + MCP `dependencies`. The skill DOES emit this when a SKILL.md has `disable-model-invocation: true`; it lives inside the per-skill output and is harmless.
- `.codex/agents/{name}.toml` *in the Codex config dir* — subagent definitions. The skill **never** writes here. Stubs go to `<output>/.codex-agents-templates/` and the user copies manually.

Keep the two straight; they're unrelated despite the directory-name collision.
