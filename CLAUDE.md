# CLAUDE.md

`baransu` is a Claude Code plugin distributing sixteen governance skills (thirteen user-facing + three cron-driven self-healing harness skills). Theme: バランス — deliberate before executing, verify after.

## Working Principles

### 1. Think Before Coding

Don't assume. Don't hide confusion. Surface tradeoffs.

- State assumptions explicitly — if uncertain, ask rather than guess
- Present multiple interpretations — don't pick silently when ambiguity exists
- Push back when warranted — if a simpler approach exists, say so
- Stop when confused — name what's unclear and ask for clarification

### 2. Simplicity First

Minimum code that solves the problem. Nothing speculative.

- No features beyond what was asked
- No abstractions for single-use code
- No "flexibility" or "configurability" that wasn't requested
- No error handling for impossible scenarios
- If 200 lines could be 50, rewrite it

The test: would a senior engineer say this is overcomplicated? If yes, simplify.

### 3. Surgical Changes

Touch only what you must. Clean up only your own mess.

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting
- Don't refactor things that aren't broken
- Match existing style, even if you'd do it differently
- If you notice unrelated dead code, mention it — don't delete it

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused
- Don't remove pre-existing dead code unless asked

The test: every changed line should trace directly to the request.

### 4. Goal-Driven Execution

Define success criteria. Loop until verified.

| Instead of… | Transform to… |
|-------------|--------------|
| "Fix the bug" | Write a test that reproduces it, then make it pass |
| "Add validation" | Write tests for invalid inputs, then make them pass |
| "Refactor X" | Ensure tests pass before and after |

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
```

Strong success criteria let the loop run independently. Weak criteria ("make it work") require constant clarification.

### Read-before-write

Re-read any file before Edit/Write in the same turn. Never rely on memory of a previous turn's read.

## Layout

```
.claude-plugin/
  marketplace.json             # marketplace catalog
plugins/
  baransu/
    .claude-plugin/
      plugin.json              # plugin manifest (v1.0.0)
    skills/
      think/ review/ analyze/ dev/ write/ execute/ ship/ hunt/ read/ learn/ book/ design/ codex-skill-transfer/
    agents/
      # Perspective: architecture-reviewer.md  quality-reviewer.md  security-reviewer.md
      # Execute:     summarize-agent.md  impl-agent.md  review-agent.md  smart-friend-agent.md
      #              e2e-fix-agent.md  final-review-agent.md  final-fixer-agent.md  merge-agent.md
```

**Critical**: `.claude-plugin/marketplace.json` at repo root is the catalog; `plugins/baransu/.claude-plugin/plugin.json` is the plugin manifest. Never merge them. Components (`skills/`, `agents/`) go at the plugin root (`plugins/baransu/`), not inside `.claude-plugin/`.

## Skills

Invoke with `/baransu:<name>`. To edit a skill, read its `SKILL.md` — design constraints live there, not here.

| Skill | When to invoke |
|-------|---------------|
| `/think` | Before any new feature, architecture decision, or non-trivial design choice |
| `/review` | After any model output — code, plan, claim — for independent re-verification |
| `/analyze` | Medium-to-large tasks: builds goal→requirement→design→test→task spec |
| `/dev` | Small tasks with clear scope: TDD Red→Green with hard gates |
| `/execute` | Run an `/analyze` spec: drives TDAID loop, produces `final-report.md` |
| `/write` | Bilingual copywriting: `zh`/`en` prefix; Refine (existing text) or Generate (new) |
| `/ship` | Session cleanup: archive `.claude/` dirs, commit, push, optional worktree removal |
| `/hunt` | Bug diagnosis: symptom → root cause via observability-first investigation |
| `/read` | Capture any content to offline Markdown: URL, path, glob, Chrome, `--topic`, `--web`, `--gh`, `--x` |
| `/design` | UI/UX spec: `gen` (guided), `lint` (Stitch+Kami), `preset <name>` |
| `/learn` | Research pipeline: Collect→Digest→Outline→Fill In→Refine; `--brief` stops at Digest |
| `/book` | Convert any content source (URL, `/read` slug, `/learn` digest, local file, `--text`) into a Kami-themed browser-ready HTML with SVG diagrams. Three stages: Acquire → Synthesize (technical/narrative/research) → Render (golden-template + validate-output.ts gate) |
| `/codex-skill-transfer` | One-way port Claude Code skill / plugin / marketplace material to Codex format. Auto-detects single-skill / batch / plugin mode. Refuses `context: fork` skills (cross-boundary; surfaces three Codex paths). |
| `/grade` | 對 baransu skill telemetry 評分：cron 觸發 5 維 equal-weight rubric，輸出 grade.jsonl |
| `/triage` | 從 grade.jsonl 聚類 poor verdict、派 investigator-agent、走 5-black 閘門 auto-fix |
| `/bridge` | 手動 head-to-head replay：在隔離 worktree 比對 main vs target branch，Δ-gate 統計閘門 |

All skills: English body, 繁體中文 user output. Do not change this convention in any skill.

## Non-obvious Invariants

These have each caused regressions — do not "optimize" them away:

- **No `skills` array in `plugin.json`**: Claude Code discovers skills from the filesystem. Adding one was done in v0.3.0 and immediately reverted.
- **`review-agent` must NOT call `/baransu:review`**: subagent depth = 1. Calling it triggers AskUserQuestion + parallel Tasks, violating the depth limit. Implement four-tier semantics directly in `review-agent.md`.
- **`/ship` branch deletion uses `-D` not `-d`**: after push the branch is unmerged locally, so `-d` always fails. Both steps need `git -C "$MAIN_REPO" branch -D`.
- **`failure_count` excludes compile errors**: compile errors do NOT count toward the 3-strike TDAID block limit. Merging these two counters breaks retry behavior.
- **`DESIGN.md` ≠ `design.md`**: uppercase at project root = UI visual spec (from `/design`); lowercase in `.claude/analyze/` = technical architecture layer (from `/analyze`). Never confuse them.

## Install

```
# Local:  /plugin marketplace add /home/vakarve/projects/baransu
# Remote: /plugin marketplace add https://git.hy-tech.com.tw/ben.tsai/baransu.git
/plugin install baransu@baransu
/plugin validate
```

## Versioning

`plugins/baransu/.claude-plugin/plugin.json` holds the authoritative version. **Bump on every distributed change** — plugin caching means users won't see updates without a bump. `plugin.json` wins over `marketplace.json`.

## No Build / Test Commands

The plugin itself ships no build toolchain. The self-healing harness includes its own structural and pytest tests under `tests/`; run them via the per-suite shell scripts and `python3 -m pytest tests/scripts/` for the Python unit tests.

## Commit Style

Conventional commits (`feat`, `fix`, `refactor`, `docs`, `chore`). Attribution lines disabled globally. For new skills, dogfood `/baransu:think`.
