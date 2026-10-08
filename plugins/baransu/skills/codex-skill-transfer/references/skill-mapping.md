## Contents

- Quick lookup
- Rules in detail
- See also
- Cross-tool implications

# Frontmatter Mapping Reference

Authoritative translation table from Claude Code SKILL.md frontmatter to Codex skill format, used as a checklist when the two copies are maintained by hand. Each row carries the rationale so future ambiguous cases can be judged rather than guessed.

Baseline: Claude Code 2.1.293 (skills docs), Codex CLI 0.161.0 (`codex-rs/skills/src/parser.rs`, `interface.rs`, `catalog_prompt.rs` at `rust-v0.161.0`). Labels: *(inferred)* = derived, not stated officially; *(unpublished)* = not documented by the vendor.

## Quick lookup

The Codex skill parser reads exactly three frontmatter keys: `name`, `description`, and `metadata.short-description`. Every other key is ignored without an error. "Codex reads?" states that fact per row; "Action" is what the Codex copy should do about it.

| Claude field | Codex reads? | Codex target | Action |
|--------------|---|--------------|--------|
| `name` | yes | `name` | Keep, identical on both sides. Codex caps it at 64 chars and falls back to a default name when it is absent, so always write it. |
| `description` | yes (required, non-empty) | `description` | Keep; trigger phrases first. |
| `metadata` | only `short-description` | `metadata` | Keep (harmless). `metadata.short-description` is the only nested key Codex reads. The script adds `version: "0.1.0-codex"` when `version` is missing. |
| `license` | no | `license` | Keeping it is harmless; Codex ignores it. |
| `compatibility` | no | `compatibility` | Keeping it is harmless; Codex ignores it. Claude caps it at 500 chars. |
| `allowed-tools` | no | — | Keeping it is harmless; Codex ignores it and has no per-skill tool allow-list. If the restriction mattered, restate it as a body instruction. |
| `disallowed-tools` | no | — | Drop; restate as a body instruction when it mattered. |
| `disable-model-invocation: true` | no | `agents/openai.yaml` → `policy.allow_implicit_invocation: false` | Move out of frontmatter (§2) |
| `user-invocable: false` | no | — | Drop. No Codex equivalent. Add a body note such as "this skill is intended for model-side use only". |
| `argument-hint` | no | — | Drop. Informs the body rewrite of `$ARGUMENTS` (§3). |
| `arguments` | no | — | Drop. Use the names to rewrite `$name` placeholders in the body (§3). |
| `model` | no | — | Drop. Codex model is set via CLI flag, `config.toml`, or profile overlay files (`$CODEX_HOME/<profile>.config.toml` with `--profile`; legacy `[profiles.x]` deprecated 0.134.0). Codex 0.149.0 removed skill model delegation. |
| `effort` | no | — | Drop. No per-skill equivalent; a spawned subagent can take `reasoning_effort` (see [`agent-mapping.md`](agent-mapping.md)). |
| `context: fork` | no | spawn instruction in the body | **Manual review required.** Two Codex paths exist (see §5); choice depends on isolation needs. |
| `agent` | no | `agent_type` of the spawn | **Manual review required.** Coupled with `context: fork`. |
| `background` | no | — | Drop. If the fork was backgrounded, say in the body whether to wait for the subagent. |
| `hooks` | no | plugin `hooks/hooks.json` | Drop from skill frontmatter (Codex skills have no frontmatter hooks). Codex lifecycle hooks belong in `~/.codex/hooks.json`, project `.codex/hooks.json`, config TOML, or a plugin's `hooks/hooks.json`. Non-managed hooks are trust-gated through `/hooks`; `command` and `mcp_tool` handlers execute; `prompt` and `agent` handlers are parsed but skipped. Relocate to the plugin layer or record the loss. |
| `paths` | no | — | Drop. No Codex equivalent for glob-scoped activation. Record it. |
| `shell` | no | — | Drop. Codex runs shell through its own tool, not a pre-declared shell. |
| `when_to_use` | no | `description` | Merge: append as `{description} Also use when: {when_to_use}`. Codex reads only `description` for implicit invocation, so dropping it loses the trigger phrases. Length: the Codex parser puts no cap on `description`; the real limit is the skill catalog budget (2% of context, 8,000 chars when unknown; `skills.max_context_tokens` ≤ 10,000 tokens), which shortens descriptions when exceeded. 1024 is the agentskills.io limit and the `agents/openai.yaml` `short_description` cap; the script trims to 1024 to stay inside the open standard. Claude truncates `description` + `when_to_use` at 1,536 chars in its listing. |
| any other key | no | — | Drop and name it in the report — an unlisted key is never lost silently. Add a row here when a new key earns a real mapping. |

## Rules in detail

### 1. Open-standard fields

`name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools` are defined by [agentskills.io/specification](https://agentskills.io/specification); the official Codex skills docs ([learn.chatgpt.com/docs/build-skills](https://learn.chatgpt.com/docs/build-skills)) require `name` and `description` and describe the optional `agents/openai.yaml` metadata. Claude reads all of these; Codex reads only `name`, `description`, and `metadata.short-description`, so the rest survive in the Codex copy as harmless documentation. Note the `compatibility` field caps at 500 chars on the Claude side — keep values within that limit.

Keep these unchanged. When the script fills gaps, it sets `compatibility` (if absent) to:

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

The script emits `agents/openai.yaml` only when `disable-model-invocation: true` is set; it does not create empty config files. When maintaining by hand, add the file whenever one of its fields earns its place. Full field set (Codex docs + `codex-rs/skills/src/interface.rs`):

| Key | Purpose |
|---|---|
| `interface.display_name` | UI name |
| `interface.short_description` | UI blurb, ≤ 1024 chars |
| `interface.icon_small`, `interface.icon_large` | Icon paths, relative to the skill |
| `interface.brand_color` | Accent color |
| `interface.default_prompt` | Suggested prompt, ≤ 1024 chars — a good place to hint how to invoke a skill that a Claude mod button used to trigger |
| `policy.allow_implicit_invocation` | `false` = explicit `$name` / `/skills` only |
| `policy.products` | Parsed but not enforced at 0.161 |
| `dependencies.tools[]` | MCP tool dependencies |

`agents/openai.yaml` belongs only in the Codex copy. Do not create an `agents/` folder inside a Claude skill — it is easily confused with the plugin-level `agents/` directory.

### 3. The `$ARGUMENTS` family — body rewrites

These placeholders are evaluated by Claude Code before the model sees the SKILL.md content. Codex has no such preprocessor *(inferred: neither the skill parser nor the catalog prompt substitutes anything, and no argument mechanism is documented)*, so `$ARGUMENTS` would reach the model literally.

The rewrite replaces the placeholder with a natural-language reference to the user's input. The model is smart enough to map "the user-provided arguments" to whatever is in the conversation. Concrete examples:

| Before (Claude) | After (Codex) |
|----|----|
| `Fix GitHub issue $ARGUMENTS following our coding standards.` | `Fix the GitHub issue the user named, following our coding standards.` |
| `Migrate the $ARGUMENTS[0] component from $ARGUMENTS[1] to $ARGUMENTS[2].` | `Migrate the named component from the source framework to the target framework, using the three values the user provided in order.` |
| `Migrate the $0 from $1 to $2.` | same as above |
| `Log to logs/${CLAUDE_SESSION_ID}.log:\n$ARGUMENTS` | `Log the user-provided message to a log file under \`logs/\` named after the current session.` |

When `arguments: [issue, branch]` is declared, prefer rewriting `$issue` → "the issue number" and `$branch` → "the target branch" rather than the generic "first argument."

### 4. The dynamic shell injection rewrite

The bang-backtick inline form (an exclamation mark immediately followed by a backtick-wrapped command) and triple-backtick blocks beginning with an exclamation mark tell Claude Code to execute the command before the SKILL.md is sent to the model, then splice the output into the prompt. Codex has no equivalent *(inferred; none is documented)*.

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

Codex **does** have an equivalent for forked subagents — native Subagents at `.codex/agents/{name}.toml` — but the mapping crosses the skill-package boundary into the user's Codex configuration. The transfer refuses to auto-port skills with `context: fork` and surfaces two viable Codex paths (native Subagents / skill chain).

For the full decision matrix, frontmatter mapping table, and body-rewrite pattern, see [`agent-mapping.md`](agent-mapping.md). That file owns this layer end-to-end so per-skill rules and per-plugin bundled-agent generation stay co-located.

### 6. Tool / API references in the body

Skill bodies often mention Claude Code surface APIs:

The transfer is governed by [`CODEX_PORT_PLAN.md`](CODEX_PORT_PLAN.md): each rewrite preserves the counterweight against model inertia, not merely a feature name. `transfer.py` therefore keeps a capability registry for lossy tokens. Each entry records:

- `codex_level`: hard stop / artifact gate / machine gate / runtime probe / soft prompt.
- `strategy`: the Codex-side replacement.
- `habit_strength`: how hard the original mechanism pushed against the shortcut.
- `countered_inertia`: the concrete shortcut or self-serving model behavior the original mechanism countered.
- `tier` and weighted risk: used to sort the transfer report's `Capability 降級風險` section.

Strong-inertia mechanisms must not silently degrade to soft prompts. If the original mechanism fought a shortcut the model naturally wants to take, move the tooth to a durable surface: artifact gate, phase split, sandbox/approval gate, or independent session artifacts.

| Claude API | Codex equivalent or rewrite |
|-----------|----------------------------|
| `Agent` tool (formerly the Task tool; subagent dispatch) | "spawn a Codex subagent" via `spawn_agent` — see [`agent-mapping.md`](agent-mapping.md) Path 1; or, if user opted for skill chaining (Path 2), rewrite as `$skill-name` mention. `spawn_agent` v1 takes `message`/`items`, `agent_type`, `fork_context`, `model`, `reasoning_effort`; v2 takes `task_name` (required), `message` (required), `agent_type`, `fork_turns` (`none` / `all` / N, default `all`), `model`, `reasoning_effort`. Claude's `effort` parameter (2.1.292) maps to `reasoning_effort`. |
| `Dispatch **seal-agent** with:` / `Dispatch <agent> with:` | `Spawn a `seal-agent` subagent with:` / `Spawn a `<agent>` subagent with:` |
| `Dispatch 3 subagents in parallel Tasks` | `Spawn 3 Codex subagents in parallel` |
| `parallel Task(s)` | `parallel Codex subagent(s)` |
| `clean Task contexts` | `clean Codex subagent contexts` |
| `via Task` | `by spawning Codex subagents` |
| `Stage 4 Tasks have returned` | `Stage 4 Codex subagents have returned` |
| `AskUserQuestion` tool | Prefer Codex's structured `request_user_input` runtime tool when it is exposed. It is available only in the modes that allow it; in Default mode it is still under development and gated by `[features] default_mode_request_user_input = true` (check `codex features list`); a skill cannot enable user config, so every mapping keeps a no-tool fallback (list numbered options, stop, wait for the reply). The tool accepts 1-3 questions per call; each option needs a `label` and a `description`, with 2-3 authored options per question; the UI appends free-text Other. Oversized question batches split sequentially (`/book`'s four-question interview becomes 3+1). `/think` uses one sequential call per Stage A round, while its four-option Stage G gate becomes a conditional two-question flow so no stable choice is smuggled into Other. If the tool is absent, `/think` retains its phase split + `alignment.md` artifact gate; authorization PAUSE sites ask directly and stop; `/read`, `/book`, and `/design` fall back to numbered options and stop. `/evolve` and `/health` mention the Claude tool only descriptively and still rewrite to a plain noun with no stop instruction — as do noun-phrase/negated mentions in any skill ("an AskUserQuestion proxy", "0 AskUserQuestion calls", "ONE AskUserQuestion round"). Unknown future skills remain unclassified until their PAUSE semantics are known. |
| `EnterPlanMode` / `ExitPlanMode` tools | **No skill-callable equivalent in Codex.** In Claude Code these are model-callable, harness-managed; the skill can instruct the model to enter Plan Mode (subject to user approval). In Codex, `active mode` only changes when the developer/system/client message changes it — a skill cannot self-switch. Rewrite as a prompt-driven plan gate ("produce a plan and pause for confirmation before any edits"); if the skill genuinely needs Plan Mode, add a note that the runtime/client must enter Plan Mode externally before invocation. |
| `TodoWrite` tool | Disabled by default in current Claude Code (the `TaskCreate` family replaced it). Codex: `update_plan` for display, plus a file for anything that must survive a restart |
| `TaskCreate` / `TaskUpdate` / `TaskGet` / `TaskList` / `TaskOutput` / `TaskStop` | Rewrite to `task-map.md` durable state. `update_plan` or any runtime plan display is presentation only; after session restart, state must be recoverable from `task-map.md` and adjacent artifacts. Where a source skill treats the task map, blocked statuses, failure counters, or green-proof gates as a contract, they stay a contract — not cosmetic wording. |
| `SendUserFile` | Write the artifact to disk and list its absolute path. This is weak-inertia delivery convenience, not a hard gate. |
| `Skill tool` (calling another skill) | "invoke the related skill" — Codex mentions skills with `$skill-name` (`$plugin:skill` inside a plugin) |
| `WebSearch` | Codex hosted `web_search` (cached by default; live only with `--search`); rephrase as "search the web" |
| `WebFetch` | Codex has no fetch tool *(inferred: none documented)*; rephrase as "fetch the URL with a shell command" |
| `Bash` / `PowerShell` tool | Codex `exec_command` / `write_stdin` (matched as `Bash` in hooks); write "run the command" |
| `Read` / `Edit` / `Write` / `Glob` / `Grep` | Codex edits through `apply_patch` and reads/searches through the shell; write "read / modify the file", not a tool name |
| `Monitor` | No Codex counterpart; rewrite as polling or split into steps. (Codex has a feature-gated `sleep` tool and async hooks, neither a watch.) |
| `CronCreate` / `ScheduleWakeup` | No Codex counterpart; document how the user reschedules, or drop |
| `PushNotification` | No skill-callable counterpart; Codex `notify` (external command) and `tui.notifications` are user config. Degrade to a final message |
| `Artifact` | No counterpart (OpenAI's porting guide says Claude live artifacts are unsupported); write the file and list its absolute path |
| `Workflow` | No counterpart; restate the steps in the body, spawning subagents explicitly where the workflow fanned out |
| `SendMessage` / `ListAgents` | Codex `send_message` / `send_input` / `followup_task` / `list_agents` / `wait_agent` / `close_agent`; name the behavior, not the tool |
| `CLAUDE.md` (instruction-file reference) | `AGENTS.md`. Since Claude Code 2.1.277, Claude reads `AGENTS.md` when no `CLAUDE.md` exists, so one shared `AGENTS.md` can serve both platforms. (A previously cited 32 KiB combined Codex cap was not found in the 2026-10-08 docs — treat it as unverified.) Body-level rewrite; the script scans references/ files and flags them instead (see §8). |

If a reference cannot be rewritten cleanly, prefer "ask the model to perform X" over inventing a Codex-specific name.

The subagent rewrite is intentionally explicit because Codex does not infer subagent fan-out from a skill body. A Codex-facing skill should say who to spawn, how many agents to run in parallel, what inputs each one gets, whether to wait for all results, and what consolidated result shape to return. When the subagent needs a clean context, say so: `fork_turns="none"` (v2 tool) or `fork_context=false` (v1); otherwise v2 forks the whole conversation by default. Codex spawns only when the user, `AGENTS.md`, or a skill asks for it, and subagents inherit the parent's sandbox and approval policy. For review-style skills whose value is an independent verdict, isolation is itself the tooth countering self-rubber-stamp inertia: first run or consult a `codex-isolation-probe.md` conclusion. If native Codex subagents are not clean enough, run each perspective in an independent invocation/session and merge from file artifacts. When the source uses ad-hoc reviewers rather than plugin-level `agents/*.md` definitions, rewrite to built-in `worker`/`explorer` subagents only when the task prompt is fully inline; otherwise flag for manual review.

Any skill carrying a red/green gate also receives an adapter note: red/green decisions must come from real test runner exit codes, not model self-report.

### 6.1 Repo-internal path references (`rewrite_repo_paths`)

Skill bodies often cite sibling material by repo-root path (`plugins/<plugin>/agents/<name>.md`, `plugins/<plugin>/skills/_shared/<doc>.md`). Those prefixes do not exist in the Codex tree, so left alone they dangle — a dispatched reviewer told to read `plugins/<plugin>/agents/foo.md` finds nothing. The same rule applies to plugin-variable paths (CLAUDE_PLUGIN_ROOT + `/skills/<self>/x` → `x`): Codex resolves relative paths from the `SKILL.md` directory and substitutes no variables in skill text, so every live path becomes relative. Hand ports apply the table below; `rewrite_repo_paths` in the script applies it automatically for the prefix of the plugin it ships in (and only flags CLAUDE_PLUGIN_ROOT, see §8):

| Claude repo path | Codex-layout rewrite |
|---|---|
| `plugins/<plugin>/agents/<name>.md` (glob `<name>` allowed, e.g. `*-reviewer`) | Package-relative `.codex-agents/<name>.toml` (`SKILL.md` → `../../.codex-agents/…`, `references/*.md` → `../../../.codex-agents/…`); see [`agent-mapping.md`](agent-mapping.md) §4 |
| `plugins/<plugin>/skills/<other>/…` | `<updots><other>/…` — sibling skill under `skills/` (`_shared` is just `<other>=_shared`); `<updots>` reaches the `skills/` dir from the file being rewritten (SKILL.md → `../`, `references/*.md` → `../../`) |
| `[$VAR/]plugins/<plugin>/skills/<self>/…` | skill-root-relative — a self-reference drops the prefix (and any `$VAR/` bash anchor), e.g. `$REPO_ROOT/plugins/<plugin>/skills/<self>/scripts` → `scripts` |
| `plugins/<plugin>/.claude-plugin/plugin.json` | plugin-root `plugin.json`, relative (`<updots>../plugin.json`) |
| `.claude/<dir>` (output/config dirs; never `.claude-plugin`) | `.codex/<dir>` |

When a command must receive an absolute path (a script that cannot run from a relative one), instruct the model to resolve the absolute location of the `SKILL.md` it is reading first and build the path from there.

Applied to: SKILL.md bodies, the `description` frontmatter field, copied `references/*.md`, and verbatim-copied shared aux dirs (`_shared/*.md`).

**Bundled-agent base.** A runtime definition at `.codex-agents/<name>.toml` resolves its own live references from that directory: skills become `../skills/...`, rules become `../rules/...`, and sibling agents become `../.codex-agents/<name>.toml`. `emit_agent_stub(..., skills_relative=False)` remains only as an optional flat-export helper for users who explicitly want a global/project custom-agent install; plugin operation does not depend on it.

**Exemptions (script).** Files whose repo paths are documentation *about* the repo or the mapping itself — not live cross-references — are skipped (rewriting corrupts meaning) and stay Claude-token-scanned only: the whole `codex-skill-transfer` skill (`REPO_PATH_REWRITE_EXEMPT_SKILLS`, its own mapping tables) and design's `references/slide-checklist.md` version-bump example (`REPO_PATH_REWRITE_EXEMPT_RELPATHS`). Scripts/assets (`.sh`/`.css`/`.py` fallback-probing and self-describing comments) are not path-rewritten — they carry their own multi-fallback discovery logic; only the `$CLAUDE_SKILL_DIR` rewrite touches `scripts/`.

### 6.2 Slash-invocation mentions (`rewrite_skill_mentions`)

Claude prose mentions sibling skills as slash commands (`/review`, `/<plugin>:review`). Codex mentions skills with a `$` prefix — the official skills docs: "run `/skills` or type `$` to mention a skill" — so a slash mention left in ported text points at a command Codex does not have.

| Claude mention | Codex rewrite | Condition |
|---|---|---|
| `/<plugin>:<name>` | plugin mode: `$<plugin>:<name>`; single-skill / batch: `$<name>` | Always — the namespaced shape is unambiguous |
| `/<name>` | plugin mode: `$<plugin>:<name>`; single-skill / batch: `$<name>` | Only when `<name>` is a *known sibling skill* (the source skill plus every sibling dir carrying a SKILL.md), and the `/` is not part of a path/URL (`.claude/read/`, `skills/read`, `example.com/review` stay) and not a longer identifier (`/design-cores`, `/reads` stay) |

Codex names a plugin skill `<plugin>:<skill>` and resolves an explicit mention only on that exact name (`codex-rs` `skills/src/selection.rs`; `:` is a legal mention character), so a bare `$review` never reaches `<plugin>:review` inside a plugin. Single-skill and batch output installs unnamespaced under `.agents/skills/`, where `$<name>` is the full name.

Applied AFTER the §6.1 path rewrite (a `/name` inside a repo path has already been resolved to a relative path there, so what survives is invocation prose), to the same carriers: SKILL.md bodies, the `description` frontmatter field (trigger phrases like `'/design'`), copied `references/*.md`, shared aux dirs (`_shared/*.md`), plugin `rules/*.md`, and bundled agent TOML instructions. Code spans and fenced examples ARE rewritten — a quoted `` `/review` `` is an invocation mention, and the ported invocation surface is `` `$review` ``. The §6.1 exemptions apply unchanged; `scripts/` bodies are never mention-rewritten (their user-facing strings stay flagged territory, not rewrite territory). A lone single-skill source knows no sibling set, so only the namespaced form is rewritten there; the glob prose form `/<plugin>:*` is also left as-is.

### 7. Output format invariants

The output `SKILL.md` must:

- Have valid YAML frontmatter delimited by `---` lines
- Have `name` exactly equal to the output directory name (open spec rule)
- Have a `name` of lowercase letters / digits / hyphens, ≤ 64 chars (agentskills.io)
- Be ≤ 500 lines (open spec recommendation; if the source exceeds this, suggest splitting into `references/`)
- Pass `skills-ref validate` if available

`transfer.py` enforces these after writing each SKILL.md (`check_output_invariants`): line count and name charset/length are checked directly; `skills-ref validate` runs only when found on PATH (skipped silently otherwise) and its result lands in the report. If any check fails after translation, the result is emitted anyway but the failure is flagged in the report.

### 8. Auxiliary content handling

**Hand-port rule.** Keep every folder the skill uses: `scripts/`, `references/`, `assets/`, `evals/`, and any other folder (`templates/`, `examples/`, …) that the body or a script points to. The Codex skills docs list `scripts/`, `references/`, `assets/`, and `agents/openai.yaml` as the optional parts of a skill; that is an enumeration, not an allow-list, and nothing documents other folders being rejected *(inferred)*. Exclude only files that are Claude-only by nature (a frontmatter-hook script with no Codex hook to call it, say). Then apply the same leftover checks as the body: live CLAUDE_PLUGIN_ROOT / CLAUDE_SKILL_DIR paths in references become relative paths (§6.1); hook commands are the only place that keeps a plugin variable, as `PLUGIN_ROOT`.

**Script behavior (`copy_aux`, optional helper).** The script is stricter than the hand-port rule — know its gaps before trusting a draft:

- `scripts/`, `references/`, `assets/`, and `evals/` are copied. `scripts/` gets the `$CLAUDE_SKILL_DIR` → `.` rewrite; `references/` gets the §6.1 repo-internal path rewrite (below) but no tool/API-token rewrite. Evaluation corpora are data artifacts, so `evals/` is preserved byte-for-byte rather than interpreted as runtime instructions.
- **`references/*.md` bodies are rewritten only for repo-internal path references** (§6.1: `plugins/<plugin>/…`, `.claude/…`), which would otherwise dangle in the Codex tree. They are NOT rewritten for Claude-only tool/API tokens. Instead, each copied reference is scanned for those tokens (`AskUserQuestion`, `Task tool`, `TodoWrite`, `EnterPlanMode`, `$ARGUMENTS`, `` !`cmd` `` injection, `CLAUDE_SKILL_DIR`, `CLAUDE_PLUGIN_ROOT`, `CLAUDE.md`, `parallel Tasks`, `clean Task contexts`, `via Task`, `TaskCreate`, `TaskUpdate`, `Dispatch **...**`) and one 需人工檢視 report line per affected file lists what was found. Rationale: tokens may be quoted *as documentation* (this skill's own mapping tables are the canonical example) — a blind token rewrite would corrupt them — whereas a repo path is unambiguously a broken pointer once the tree is relaid out. The `codex-skill-transfer` skill and design's `slide-checklist.md` are exempt from the path rewrite too (§6.1).
- A generated `SKILL.md` that still contains `CLAUDE_PLUGIN_ROOT` is likewise reported for manual review and left byte-for-byte intact at that token. Codex sets `PLUGIN_ROOT` / `PLUGIN_DATA` (and the `CLAUDE_PLUGIN_ROOT` / `CLAUDE_PLUGIN_DATA` aliases) only in the environment of plugin hook commands, never in skill text, so the fix is the §6.1 relative-path rewrite done by hand — not a `PLUGIN_ROOT` substitution.
- `SendUserFile` is also scanned in references so delivery-only gaps are visible without rewriting quoted documentation.
- Skill-root orphan **files** are copied and reported (翻譯處理).
- Skill-root orphan **directories** (any subdir other than `scripts` / `references` / `assets` / `evals` / `agents`) are NOT copied; each is listed under 已捨棄 so the omission is visible. This is stricter than Codex itself requires — after a script draft, copy such folders (`templates/` and the like) into the Codex copy by hand.

## See also

- [`plugin-mapping.md`](plugin-mapping.md) — `.claude-plugin/plugin.json` → portable root `plugin.json` plus bundled agents/rules.
- [`marketplace-mapping.md`](marketplace-mapping.md) — `.claude-plugin/marketplace.json` → `.agents/plugins/marketplace.json` (manual).
- [`CODEX_PORT_PLAN.md`](CODEX_PORT_PLAN.md) — behavior-weight plan for preserving counterweights against model inertia.

## Cross-tool implications

Because both Claude Code and Codex are supersets of the agentskills.io standard, a SKILL.md that uses **only** open-standard fields and **no** dynamic injection or argument substitution is portable to **all** agentskills.io adopters (Cursor, Gemini CLI, Goose, Junie, etc.) without modification. When porting skills, prefer this lowest-common-denominator form when the loss of Claude-specific features is acceptable — it broadens the skill's reach beyond just Codex.

The flip side: any vendor extension this skill cannot translate is a portability tax. The transfer report's "已捨棄" section is, in effect, a tax bill — review it for opportunities to refactor the source skill toward the open standard.
