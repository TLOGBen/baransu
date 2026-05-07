# Frontmatter Mapping Reference

Authoritative translation table from Claude Code SKILL.md frontmatter to Codex skill format. Each row carries the rationale so future ambiguous cases can be judged rather than guessed.

## Quick lookup

| Claude field | Codex target | Action |
|--------------|--------------|--------|
| `name` | `name` | Pass through (open standard, both require) |
| `description` | `description` | Pass through (open standard, both require) |
| `license` | `license` | Pass through (open standard) |
| `compatibility` | `compatibility` | Pass through; if missing, add a default |
| `metadata` | `metadata` | Pass through; if missing `version`, add `"0.1.0-codex"` |
| `allowed-tools` | `allowed-tools` | Pass through (open-standard experimental field; Codex may currently ignore) |
| `disable-model-invocation: true` | `agents/openai.yaml` → `policy.allow_implicit_invocation: false` | Move out of frontmatter |
| `user-invocable: false` | — | Drop. No Codex equivalent. Note in report; the skill may need a body-side note saying "this skill is intended for model-side use only" |
| `argument-hint` | — | Drop. Inform body rewrite of `$ARGUMENTS`. |
| `arguments` | — | Drop. Use the names to rewrite `$name` placeholders in the body. |
| `model` | — | Drop. Codex model is set via CLI flag. Optionally surface as a comment in the body. |
| `effort` | — | Drop. No Codex equivalent. |
| `context: fork` | `.codex/agents/{name}.toml` (user-side) | **Manual review required.** Three Codex paths exist (see §5); choice depends on isolation needs. |
| `agent` | `.codex/agents/{name}.toml` `name` field | **Manual review required.** Coupled with `context: fork`. |
| `hooks` | — | Drop. No Codex equivalent. Note in report. |
| `paths` | — | Drop. No Codex equivalent for glob-scoped activation. Note in report. |
| `shell` | — | Drop. Codex skills run shell via tool calls, not a pre-declared shell. |

## Rules in detail

### 1. Open-standard fields

`name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools` are defined by [agentskills.io/specification](https://agentskills.io/specification). Both Claude and Codex are supersets of this standard.

Pass these through unchanged. If `compatibility` is absent, set:

```yaml
compatibility: Designed for Claude Code; ported to Codex.
```

If `metadata.version` is absent, set:

```yaml
metadata:
  version: "0.1.0-codex"
```

These are conservative defaults that document the porting context without overstating compatibility.

### 2. The `disable-model-invocation` rewrite

`disable-model-invocation: true` in Claude means "Claude must not auto-trigger; only the user can invoke this." The Codex equivalent lives in `agents/openai.yaml`:

```yaml
policy:
  allow_implicit_invocation: false
```

When emitting `agents/openai.yaml`, also include a minimal `interface` block so the Codex UI has something to display:

```yaml
interface:
  display_name: "{Title-cased skill name}"
  short_description: "{first sentence of description}"
policy:
  allow_implicit_invocation: false
```

Only emit `agents/openai.yaml` if `disable-model-invocation: true` is set. Don't create empty config files.

### 3. The `$ARGUMENTS` family — body rewrites

These placeholders are evaluated by Claude Code before the model sees the SKILL.md content. Codex doesn't have this preprocessor, so `$ARGUMENTS` would reach the model literally.

The rewrite replaces the placeholder with a natural-language reference to the user's input. The model is smart enough to map "the user-provided arguments" to whatever is in the conversation. Concrete examples:

| Before (Claude) | After (Codex) |
|----|----|
| `Fix GitHub issue $ARGUMENTS following our coding standards.` | `Fix the GitHub issue the user named, following our coding standards.` |
| `Migrate the $ARGUMENTS[0] component from $ARGUMENTS[1] to $ARGUMENTS[2].` | `Migrate the named component from the source framework to the target framework, using the three values the user provided in order.` |
| `Migrate the $0 from $1 to $2.` | same as above |
| `Log to logs/${CLAUDE_SESSION_ID}.log:\n$ARGUMENTS` | `Log the user-provided message to a log file under \`logs/\` named after the current session.` |

When `arguments: [issue, branch]` is declared, prefer rewriting `$issue` → "the issue number" and `$branch` → "the target branch" rather than the generic "first argument."

### 4. The dynamic shell injection rewrite

The bang-backtick inline form (an exclamation mark immediately followed by a backtick-wrapped command) and triple-backtick blocks beginning with an exclamation mark tell Claude Code to execute the command before the SKILL.md is sent to the model, then splice the output into the prompt. Codex has no equivalent.

The rewrite shifts execution from "preprocessor" to "tool call inside the session." Two patterns:

**Inline form** (literal source — bang directly followed by backtick-wrapped command):
```
Current branch: <BANG><BACKTICK>git branch --show-current<BACKTICK>
```
(replace `<BANG>` with an exclamation mark and `<BACKTICK>` with a backtick character)
→
```markdown
Run `git branch --show-current` and treat the result as the current branch context.
```

**Block form:**
```markdown
## Environment
```!
node --version
npm --version
git status --short
```
```
→
```markdown
## Environment

Before proceeding, run these three commands and read their output:

- `node --version`
- `npm --version`
- `git status --short`
```

The intent is preserved (the model gets the same factual context); only the *who runs it* changes from Claude Code to Codex.

### 5. The `context: fork` / `agent` problem

Codex **does** have an equivalent for forked subagents — native Subagents at `.codex/agents/{name}.toml` — but the mapping crosses the skill-package boundary into the user's Codex configuration. The transfer refuses to auto-port skills with `context: fork` and surfaces three viable Codex paths (native Subagents / skill chain / Codex-as-MCP).

For the full decision matrix, frontmatter mapping table, and body-rewrite pattern, see [`agent-mapping.md`](agent-mapping.md). That file owns this layer end-to-end so per-skill rules and per-plugin agent-stub generation stay co-located.

### 6. Tool / API references in the body

Skill bodies often mention Claude Code surface APIs:

| Claude API | Codex equivalent or rewrite |
|-----------|----------------------------|
| `Task tool` (subagent dispatch) | "spawn a Codex subagent" — see [`agent-mapping.md`](agent-mapping.md) Path 1; or, if user opted for skill chaining (Path 2), rewrite as `$skill-name` mention |
| `AskUserQuestion` tool | "ask the user directly" |
| `TodoWrite` tool | "track steps internally" or use Codex's own task system if mentioned |
| `Skill tool` (calling another skill) | "invoke the related skill" — Codex supports skill-to-skill dispatch via `$skill-name` mention |
| `WebFetch` / `WebSearch` | Codex has its own browse tool; rephrase as "fetch the URL" / "search the web" |
| `Bash` tool | identical (both have shell tool) |
| `Read` / `Edit` / `Write` | identical (both have file tools) |

If a reference cannot be rewritten cleanly, prefer "ask the model to perform X" over inventing a Codex-specific name.

### 7. Output format invariants

The output `SKILL.md` must:

- Have valid YAML frontmatter delimited by `---` lines
- Have `name` exactly equal to the output directory name (open spec rule)
- Be ≤ 500 lines (open spec recommendation; if the source exceeds this, suggest splitting into `references/`)
- Pass `skills-ref validate` if available

If any of these fail after translation, emit the result anyway but flag the failure in the report.

## See also

- [`plugin-mapping.md`](plugin-mapping.md) — `.claude-plugin/plugin.json` → `.codex-plugin/plugin.json` and agent stubs.
- [`marketplace-mapping.md`](marketplace-mapping.md) — `.claude-plugin/marketplace.json` → `.agents/plugins/marketplace.json` (manual).

## Cross-tool implications

Because both Claude Code and Codex are supersets of the agentskills.io standard, a SKILL.md that uses **only** open-standard fields and **no** dynamic injection or argument substitution is portable to **all** agentskills.io adopters (Cursor, Gemini CLI, Goose, Junie, etc.) without modification. When porting baransu's skills, prefer this lowest-common-denominator form when the loss of Claude-specific features is acceptable — it broadens the skill's reach beyond just Codex.

The flip side: any vendor extension this skill cannot translate is a portability tax. The transfer report's "已捨棄" section is, in effect, a tax bill — review it for opportunities to refactor the source skill toward the open standard.
