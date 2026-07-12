---
name: codex-skill-transfer
description: Ports Claude Code skills, plugins, or marketplaces one-way to OpenAI
  Codex format (SKILL.md / batches / plugin → agent-stub TOMLs). Trigger on 「轉成 codex
  版」「給 codex 用」「port to codex」, or questions about Claude→Codex field mapping (disable-model-invocation,
  context fork, ARGUMENTS, plugin.json). Not for reverse porting (Codex→Claude) or
  authoring a brand-new Codex skill from scratch that isn't a port of an existing
  Claude source.
license: Apache-2.0
metadata:
  author: baransu
  version: 0.11.0
compatibility: Designed for Claude Code; output targets Codex CLI. Optional `skills-ref`
  CLI for validation.
---

# Codex Skill Transfer

One-way port from Claude Code → Codex. Claude is canonical; this skill produces the Codex shadow.

## Outcome Contract

- **Outcome**: A derived Codex-format copy of the Claude Code skill / batch / plugin source exists in a separate output directory, with every lossy decision surfaced.
- **Done when**: `python3 scripts/transfer.py <claude-source> <codex-output>` completes (or the equivalent inline port is written), the output directory contains the detected mode's expected shape, and the transfer report is printed.
- **Evidence**: The 繁中 transfer report enumerating 完整保留 / 翻譯處理 / 動態注入改寫 / 已捨棄 / Capability 降級風險 / 需人工檢視 items; the source tree is untouched.
- **Output**: The Codex output directory (single skill dir, batch subdirs, or marketplace root) plus the transfer report.
- **Automation**: ultracode=assist, loop=assisted（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）

## Direction is one-way (Claude → Codex)

The user keeps editing on the Claude side. Each rerun regenerates the Codex output from the current Claude source. The Codex output is **derived**, not authoritative — never edit it by hand expecting changes to flow back.

## Step 1 — Identify the source shape

Look at the source path the user gave you. Pick the matching mode:

| Source path looks like | Mode | What it produces |
|---|---|---|
| `<dir>/.claude-plugin/plugin.json` exists | **Plugin** | `<output>/` as marketplace root: `<output>/.agents/plugins/marketplace.json` + `<output>/plugins/<name>/{.codex-plugin, skills, .codex-agents-templates}` |
| `<dir>/SKILL.md` exists at the top level | **Single skill** | One `<output>/<skill-name>/` |
| `<dir>` has children that each contain `SKILL.md` | **Skills batch** | One subdir per child |

`scripts/transfer.py` auto-detects Plugin / Single skill / Skills batch and dispatches. A Skills-batch child without `SKILL.md` is not silently dropped: the script emits a ⚠️ skipped report entry for it (skip_reason: no SKILL.md in source) and the stderr summary counts it — in plugin mode the same child is instead copied verbatim as a shared aux dir and token-scanned. When porting inline, mirror that contract: name every mismatched child in the report rather than dropping it. If the source matches none of the three shapes — e.g. a marketplace root that has `.claude-plugin/marketplace.json` but no top-level `plugin.json` or `SKILL.md` — `transfer.py` exits 2 without writing; marketplace-catalog conversion is manual, so follow [`references/marketplace-mapping.md`](references/marketplace-mapping.md) by hand rather than forcing a mode. Plugin mode emits a Layout B marketplace catalog (codex/ self-contained); for monorepos that publish via git URL, the repo root needs a separate Layout A catalog — see [`references/marketplace-mapping.md`](references/marketplace-mapping.md) §8.

## Step 2 — Run the transfer

Default invocation for any of the three automated modes:

```bash
python3 scripts/transfer.py <claude-source> <codex-output>
```

The script refuses if `<codex-output>` overlaps the source — there is a real data-loss path otherwise (rerun would `rmtree` the source). Always pick a separate output directory. If `transfer.py` exits non-zero because `<codex-output>` overlaps the source, then re-invoke with a sibling output directory outside the source tree (e.g. `codex/` at repo root for baransu) — do NOT delete or move the source to make room.

**Rerun wipes the output.** Each run regenerates the output wholesale: an existing output directory is deleted and rewritten from the current Claude source. To keep that safe, the script refuses (exit 2) when the output exists, is non-empty, and lacks a generated marker — `.agents/plugins/marketplace.json` for plugin mode, a `SKILL.md` inside the per-skill target otherwise. A refusal means the directory was not produced by a prior run: if the marker-check refusal (exit 2) fires, then the agent MUST NOT delete the refused directory itself; instead list the directory contents in the report and either pick a different output directory or wait for the human to delete it by explicitly naming the path; never point the output at a directory holding unrelated content.

For single-skill and batch output, install by copying each skill directory into `<repo>/.agents/skills/` (project) or `~/.agents/skills/` (personal) — note `.agents/`, NOT `.codex/` or `.claude/` — then restart Codex to pick it up.

**For the `baransu` plugin: `<codex-output>` is `codex/` at repo root.** This matches the path committed in `<repo-root>/.agents/plugins/marketplace.json` (Layout A catalog). Do not invent a new output dir — the catalog's `source.path` would dangle and `codex plugin marketplace add <git-url>` (the README install command) would silently break.

For inline (in-conversation) execution without the script — when the user wants to inspect every change — read the source file(s), apply the rules in the relevant reference (see Step 3), and write the output yourself. The script is the default; use inline ONLY when the user explicitly asks to inspect each change. For any plugin/batch source, or any source containing fields that need escape-sensitive serialization (descriptions or agent bodies containing quotes or triple-quotes), use the script — its `yaml.safe_dump`/`json.dumps` path is the only escape-safe one.

## Step 3 — Follow the rules in the right reference

The transformation is layered; each reference owns one layer. Read the matching one for the work in front of you, not all of them:

When changing the mapping rules themselves, refresh the current OpenAI Codex docs first and compare against the relevant official sections: Agent Skills, Build plugins, Subagents, MCP, Hooks, and sandbox/approval behavior. The docs can drift faster than this skill; do not preserve an old mapping just because the transfer script already emits it.

- [`references/CODEX_PORT_PLAN.md`](references/CODEX_PORT_PLAN.md) — behavior-weight survival plan. Read this before changing lossy rewrites: the question is not "which Codex API matches this Claude API", but "which model shortcut/inertia did the original mechanism counter, and is the Codex replacement still hard enough?" Strong-inertia soft-prompt downgrades must move to an artifact/phase/sandbox gate instead.
- [`references/skill-mapping.md`](references/skill-mapping.md) — SKILL.md frontmatter + body rewrites. Covers `disable-model-invocation` → `agents/openai.yaml`, `$ARGUMENTS` → natural language, bang-backtick shell injection → imperative TODO, and tool-API rewrites. **Read this for any per-skill question.**
- [`references/plugin-mapping.md`](references/plugin-mapping.md) — `.claude-plugin/plugin.json` → `.codex-plugin/plugin.json`. Read when porting a whole plugin.
- [`references/agent-mapping.md`](references/agent-mapping.md) — Claude `context: fork` / `agent: ...` → Codex Subagents (`.codex/agents/*.toml`), and `agents/*.md` → `.codex-agents-templates/*.toml` stubs. Read whenever agents are involved at either layer. Co-locates per-skill rules with per-plugin stub generation so you don't bounce between files.
- [`references/marketplace-mapping.md`](references/marketplace-mapping.md) — `.claude-plugin/marketplace.json` → `.agents/plugins/marketplace.json`. Plugin mode auto-emits Layout B (catalog inside `<output>/`); §8 covers Layout A (monorepo repo-root catalog) which stays manual.

## Step 4 — Produce output by copying golden templates

All output shapes live in `assets/`. The script reads them; if you're working inline, copy them and fill the placeholders by hand. Each is a single file with `$placeholder` markers (Python `string.Template` syntax — `$name`, `$version`, etc.):

- [`assets/codex-plugin.template.json`](assets/codex-plugin.template.json) — canonical `.codex-plugin/plugin.json` shape for plugins that bundle skills. The script renders this template, prunes empty pass-through fields, and merges complex fields (`author`, `keywords`) from the translated manifest. Edit this file to change the canonical shape.
- [`assets/codex-marketplace.template.json`](assets/codex-marketplace.template.json) — schema-aligned starter for the repo-root Layout A catalog (the script writes Layout B inline; this template is for the monorepo case where you also need a root-level catalog).

The skill-level `<skill>/agents/openai.yaml` and the agent-stub TOML output are NOT templated — they're built directly via `yaml.safe_dump` and `json.dumps` so escape correctness is ironclad regardless of source content. Earlier versions templated them but had to retire that approach when v0.4.0 review found honor-system escape bugs (description containing `"`, agent body containing `"""`).

## Step 5 — Print a transfer report

For automated runs the script prints the report. For inline runs you write it. Use this skeleton (繁中):

```
## Codex Transfer Report — <name>

- 來源: `<source-path>`
- 輸出: `<output-path>`

### 完整保留 (lossless)
- ...

### 翻譯處理 (mapped)
- ...

### 動態注入改寫 (rewrites)
- ...

### 已捨棄 (dropped)
- ...

### Capability 降級風險 (weighted by model inertia)
- ...

### ⚠️ 需人工檢視 (manual review)
- ...
```

After emitting the report body, you MUST append a final `### Next-port follow-ups` section that lists, one line per item, every entry you put under 已捨棄 (dropped) and 需人工檢視 (manual review) above. For each line, name the item and tag it with exactly one disposition action: `refresh-mapping` (the loss is fixable by updating a Step 3 reference mapping), `file-issue` (track upstream/外部 limitation), or `accept-as-lossy` (no Codex target exists; the gap is permanent and intentional). If there are zero dropped and zero manual-review items, write the single line `- none`.

## Boundaries

- **Never mutate the source.** Always write to a separate directory. The script refuses overlapping paths; inline work follows the same rule.
- **Never auto-write to user config dirs.** Agent stubs land in `<output>/.codex-agents-templates/` — the user copies them into `~/.codex/agents/` (personal) or `.codex/agents/` (project-scoped trusted repo) themselves. The plugin package has no business reaching into the user's home directory.
- **Never invent fields the user didn't author.** When a Claude field has no Codex target and no rewrite preserves intent, document it in the report. Silent fabrication is worse than an obvious gap.
- **Never translate domain-specific instructions or examples** in skill bodies — only the structural elements (frontmatter, dynamic injection, argument substitution, Claude-specific tool references). The author's voice stays.
- **Flag aggressively when in doubt.** A noisy report is cheaper than a silently wrong port.

## Repository layout this skill expects

`scripts/transfer.py` is a single Python file by design — baransu's other tooling scripts (`design/scripts/check.py`, `read/scripts/search-papers.py`) follow the same single-file convention.
