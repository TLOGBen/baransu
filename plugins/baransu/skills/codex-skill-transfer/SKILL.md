---
name: codex-skill-transfer
description: "Port a Claude Code skill (SKILL.md) to OpenAI Codex format (.agents/skills/{name}/). Use this skill whenever the user wants to convert, port, migrate, mirror, or generate a Codex-compatible version of an existing Claude Code skill — including phrasings like 「轉成 codex 版」「給 codex 用」「port to codex」「make this work in codex」「Codex 對應」. Also trigger when the user asks how a specific Claude frontmatter field (disable-model-invocation, context fork, allowed-tools, $ARGUMENTS, !`cmd` injection, etc.) maps to Codex."
license: Apache-2.0
compatibility: Designed for Claude Code; output targets Codex CLI. Optional `skills-ref` CLI for validation.
metadata:
  author: baransu
  version: "0.1.0"
---

# Codex Skill Transfer

Port a Claude Code skill to a Codex-compatible skill so the same workflow runs under both tools. Output goes to a sibling directory the user nominates (typically `codex-skills/{name}/` or `~/.agents/skills/{name}/`).

## Why this is needed

Claude Code and Codex both follow the [agentskills.io](https://agentskills.io) open standard, so the SKILL.md body and the required `name` / `description` frontmatter fields are portable as-is. The friction is in three places:

1. **Vendor-specific frontmatter** — Claude has 11+ extension fields (`disable-model-invocation`, `context: fork`, `argument-hint`, `hooks`, `paths`, `shell`, etc.) that Codex does not honor.
2. **Dynamic context injection** — `` !`shell command` `` and ` ```! ` blocks are pre-processed by Claude Code before the model sees them; Codex has no equivalent and the model would receive the literal backtick syntax.
3. **Argument substitution** — `$ARGUMENTS`, `$0`, `$N`, `$name` placeholders are Claude-specific; Codex passes user input as a regular message.

This skill knows how to translate each of these, and what to flag for manual review when no clean translation exists (notably `context: fork`).

## When to invoke

Trigger on any of these signals:
- The user names a skill and asks to port / convert / mirror to Codex
- The user provides a `SKILL.md` path and asks for a Codex version
- The user asks how a Claude frontmatter field maps to Codex
- The user asks to batch-convert all skills in a plugin or directory

Do **not** trigger for: writing a new skill from scratch (use `/skill-creator` or `/baransu:think`); editing an existing Claude skill in place.

## Inputs and outputs

**Inputs**
- `<source-skill-dir>` — a directory containing `SKILL.md` (and optionally `scripts/`, `references/`, `assets/`)
- `<output-dir>` — where to write the Codex version (default: sibling `codex-skills/{name}/`)

**Outputs**
- `<output-dir>/SKILL.md` — translated frontmatter + body
- `<output-dir>/agents/openai.yaml` — only when needed (see §3)
- `<output-dir>/scripts/`, `references/`, `assets/` — copied verbatim if present
- A short transfer report listing: lossless mappings, lossy mappings, dropped fields, manual-review flags

## Procedure

### 1. Read and parse

Read the source `SKILL.md`. Split YAML frontmatter from Markdown body. If frontmatter is malformed or `name`/`description` is missing, stop and report — the source is not a valid agentskills.io skill.

Verify the directory name equals the frontmatter `name` (the open spec requires this). If they differ, prefer the directory name and warn the user.

### 2. Translate frontmatter

Apply the mapping rules in `references/mapping.md`. The shape is:

- **Pass through**: `name`, `description`, `license`, `compatibility`, `metadata` — these are open-standard fields. If the source lacks `compatibility` or `metadata.version`, add reasonable defaults (`compatibility: Designed for Claude Code; ported to Codex` and `metadata.version: "0.1.0-codex"`).
- **Pass through with caveat**: `allowed-tools` — kept (it's an experimental open-standard field), but Codex may currently ignore it. Note in the report.
- **Move to `agents/openai.yaml`**: `disable-model-invocation: true` becomes `policy.allow_implicit_invocation: false`. Only emit `agents/openai.yaml` when at least one field needs to move there.
- **Drop with body rewrite**: `argument-hint`, `arguments` — these inform body-side rewrites of `$ARGUMENTS`/`$N`/`$name`, then the field itself is removed.
- **Drop**: `user-invocable`, `model`, `effort`, `hooks`, `paths`, `shell` — no Codex equivalent. Document the loss in the report.
- **Flag for manual review**: `context: fork` and `agent` — Codex has no forked-subagent concept; the skill needs structural redesign. Translate the body as best as possible but mark the output `SKILL.md` with a top comment block warning the user.

### 3. Rewrite the body

The body is mostly portable. Apply these surgical rewrites:

**Dynamic shell injection**: replace `` !`<cmd>` `` (inline) and ` ```! ... ``` ` (block) with imperative instructions. Example:

```markdown
## Current changes

!`git diff HEAD`
```

becomes:

```markdown
## Current changes

Run `git diff HEAD` and read its output before producing the summary below.
```

The principle: keep the *intent* (the model sees the diff), but shift execution from Claude Code's pre-processor to a tool call inside the Codex session.

**Argument substitution**: rewrite each placeholder to a natural-language reference.

| Claude form | Codex rewrite (suggested) |
|-------------|---------------------------|
| `$ARGUMENTS` | "the user-provided arguments" |
| `$0`, `$1`, `$2` | "the first / second / third argument the user provided" |
| `$ARGUMENTS[0]` | same as `$0` |
| `$name` (declared via `arguments:`) | the named role, e.g. "the issue number" |
| `${CLAUDE_SESSION_ID}` | drop or replace with "the current session" |
| `${CLAUDE_SKILL_DIR}` | replace with the absolute path the script will be invoked from, OR keep relative paths from the skill root |
| `${CLAUDE_EFFORT}` | drop |

**`agentskills.io` references**: leave untouched — the standard is shared.

**Claude-specific tooling references**: scan the body for mentions of `subagent_type`, `Task tool`, `AskUserQuestion`, `TodoWrite`, `Skill tool` — these are Claude Code surface APIs. Either rewrite to Codex equivalents (when known) or replace with neutral language ("ask the user", "track the steps internally"). Flag remaining unresolved references in the report.

### 4. Copy auxiliary files

If the source has `scripts/`, `references/`, or `assets/`, copy them verbatim to the output. These are generally portable.

For shell scripts in `scripts/`: scan for hard-coded `${CLAUDE_SKILL_DIR}` and rewrite to relative paths from the skill root, since Codex does not provide that env var.

### 5. Validate

If `skills-ref` is on PATH, run `skills-ref validate <output-dir>` and include the result in the report. Otherwise, perform an internal check against the open spec rules listed in `references/mapping.md` (frontmatter-only).

### 6. Emit transfer report

End with a 繁中 report following this template:

```
## Codex Transfer Report — {name}

- 來源: {source-skill-dir}
- 輸出: {output-dir}

### 完整保留 (lossless)
- {list of fields and content unchanged}

### 翻譯處理 (mapped)
- {Claude field → Codex equivalent}

### 動態注入改寫 (rewrites)
- {N 處 `!cmd` injection 改寫為指令}
- {M 處 $ARGUMENTS 改寫}

### 已捨棄 (dropped, no Codex equivalent)
- {fields with no target}

### ⚠️ 需人工檢視 (manual review)
- {context: fork / agent / unresolved tool references}

### 驗證
- skills-ref: {pass / fail / not-installed}
```

## Two execution modes

### Mode A: inline (default)

Read the source, apply the rules above, write the output, print the report. This is the right default for one-off conversions where the user wants to inspect each change.

### Mode B: scripted batch

If the user asks to convert many skills (e.g. "convert all baransu skills"), invoke `scripts/transfer.py`:

```bash
python3 scripts/transfer.py <source-skills-dir> <output-skills-dir>
```

The script implements the same rules deterministically and emits one combined report. Use this when consistency across many skills matters more than per-skill inspection. The script intentionally refuses to write files for skills containing `context: fork` — those need human attention.

## Boundaries

- **Do not** rewrite the source skill in place. Always write to a separate output directory.
- **Do not** invent fields or behavior the user did not author. If a Claude field has no Codex target and no body rewrite preserves the intent, document it in the report rather than fabricating a workaround.
- **Do not** translate the skill's domain-specific instructions or examples — only the structural elements (frontmatter, dynamic injection, argument substitution, Claude-specific tool references). The author's voice stays.
- **Do** flag aggressively when in doubt. A noisy report is cheaper than a silently wrong port.

## Reference

See [`references/mapping.md`](references/mapping.md) for the complete frontmatter mapping table and the rationale behind each rule.
