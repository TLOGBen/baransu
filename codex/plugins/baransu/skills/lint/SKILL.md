---
name: lint
description: "Keeps a project's lint gate in `.claude/lint/`: copies baransu's preset into the project, adds, disables or changes the severity of a check, explains why a rule exists, and syncs the preset after an update; the baransu mod then runs each check at its moment — after an edit, before a git commit or push, before $baransu:ship or $baransu:review, and first thing when this skill is called (every check, manual-only ones included) — and shows the result in the chat. Trigger On '$baransu:lint', 'lint 規則', '加一條 lint', '初始化 lint', '這條規則為什麼', 'lint preset', '別再犯這個錯'. Not for diagnosing a failure ($baransu:hunt) or auditing agent config ($baransu:health)."
---

# lint — keep the checks that make a known mistake impossible

A mistake an agent has found once should not be possible again. This skill owns the project's `.claude/lint/` folder: what each check catches, when it runs, how severe it is. It never runs the checks itself; the baransu mod does that at each moment "What the mod does" lists — calling this skill is one of them — and shows the result in the chat (see "What the mod does"). `$baransu:hunt`, `$baransu:health` and `$baransu:draft` decide that a check should exist; they hand the writing to this skill, so the format has one owner.

All user-facing output is in Traditional Chinese.

## Outcome Contract

- **Outcome**: The project's `.claude/lint/` holds the checks the user wants, each in its own file, with the preset copied from this skill's `preset/` on first use and kept in step on request.
- **Done when**: The asked change is written in the format `references/format.md` gives; a new or changed check was run once on the current tree and, when a past commit carried the mistake, on that commit, and both results were shown; an explanation names what the rule blocks, why it exists, and what to use instead.
- **Evidence**: The files written or changed, and the output of the check run on the tree (and on the past commit when one exists).
- **Output**: Files under `.claude/lint/`; a Traditional Chinese summary in the conversation.
- **Automation**: ultracode=neutral, loop=not-drivable（each change is a choice the user makes about their own project）

## The folder

```
.claude/lint/
  lint.json             # optional: converter, checks folder, sgconfig path (format.md)
  sgconfig.yml          # ast-grep config: ruleDirs: [rules]
  checks/<id>.toml      # one check per file; the file name is its id
  rules/<id>.yml        # ast-grep rules, ast-grep's own format
```

`references/format.md` is the format: the fields of a check, the built-in checks, and how the mod matches a file. Read it before writing a check. `$baransu:ship` never archives this folder: it is a kept product, like `.claude/hypothesis/`.

## Uses

**Init** (`$baransu:lint init`, or the first use in a project with no `.claude/lint/`). Ask for a level first:

- **關閉** — no preset; only the project's own checks.
- **預設** — `preset/general/`, and from `preset/personal/` the 3–7 checks that fit this project. Read the project first — its languages, scripts, shells, tools, and the owner's rules that apply to it — then recommend those checks, one line each with why it fits here, and let the user confirm. Never hand over the whole personal list to tick.
- **嚴格** — 預設, with `built-before-commit`, `up-to-date` and `private-key-material` raised to `error`, plus one TLA+ check per `.claude/hypothesis/<area>/` in the project, written from that hypothesis's README as `references/format.md` (last section) shows. The TLA+ checks stay off below this level: most projects keep no model, and TLC is the slowest check there is.

Then copy into the project: show the list with one line per check and let the user drop any before copying. Write `sgconfig.yml` when any rule is copied. Each copied file keeps a `from = "baransu-preset@<version>"` line, the version from `../../.claude-plugin/plugin.json`. If `.claude/lint/` would be ignored by git (`git check-ignore`), say so, because the checks would then not reach the repo or its CI.

**Add a check.** From the user, or handed over by `$baransu:hunt`, `$baransu:health` or `$baransu:draft` with the mistake and where it happened. Pick the cheapest form that catches it: an ast-grep rule when the mistake has a syntax shape, a `forbid` regex when it is plain text, a `run` command when the project already has a tool that catches it (ESLint, a type check, a test), a built-in when the mistake is about the agent's behaviour rather than a file. Write the message as what to use instead. Run the check once on the current tree; when a past commit carried the mistake, run it there too (`git worktree add` a temporary tree), and show both: it should fail on the past and pass now. A check that cannot fail on the mistake it names is not done. A `$baransu:hypothesis` model is a check too: its TLC command as a `run` check on `done`, scoped to the code it covers (`references/format.md`, last section), so a change that breaks one of its rules stops `$baransu:ship`.

**Disable or change severity.** Change `severity` to `error`, `warn` or `off` in that check's file. Never delete a preset check the user only wants quiet: `off` keeps it visible to the next sync.

**Introduce** (`$baransu:lint` with no other ask, or 「現在有哪些 lint」). Show what the project's lint does, grouped by the moments "What the mod does" lists (manual included: the checks that run only when this skill is called) — each check in one line: what it blocks and how severe. Pick the smallest view that makes the shape clear from the forms `../show-me/SKILL.md` lays out (a flow of those moments is usually it) and draw it inline; that skill is invoked only by the user, so read it rather than calling it.

**Explain.** For a check id or a message the user saw: what it blocks, the evidence it came from (its `from`, its `origin` commit, or the rule it restates), and what to write instead. Read the file and the commit; do not answer from memory.

**Sync** (`$baransu:lint sync`). Compare each project file carrying `from` with this skill's current preset: list checks that changed, were added, or were removed upstream, and apply only what the user picks. A project's own edits to a copied check win unless the user says otherwise.

**The project's own "run X before Y".** When the project's `CLAUDE.md` or `AGENTS.md` tells the agent to run something before a step (「commit 前跑 ESLint」), offer to turn it into a check with the matching `on`, so the mod runs it instead of the agent remembering it.

## What the mod does

The baransu mod reads `.claude/lint/` and runs, at each moment, the checks whose `on` names it:

- **edit** — after Edit / Write / MultiEdit / NotebookEdit succeeds: the checks in scope for that file, and ast-grep on it.
- **bash** — before every Bash or PowerShell command: checks whose `forbid` reads the command line, and the preview of what a deleting or discarding command would touch.
- **commit** — before a Bash call that runs `git commit` or `git push`: those checks, and the git built-ins.
- **done** — before `$baransu:ship` or `$baransu:review` starts: every `done` check, ast-grep on the whole tree, and the session record. The result is written at the top of the skill's text as this version's lint record; for `$baransu:ship` an error means stop.
- **manual** — when this skill is called: every check on files over the whole tree — each `forbid` and `run` whose `on` names `manual`, `edit`, `commit` or `done` — and ast-grep, written at the top of this skill's text. When the text opens with that 「Lint 紀錄」, tell the person what it found in a sentence or two (saying so when it found nothing) before the work they asked for. A check `on = ["manual"]` runs only here.
- **session start** — the worktree built-in.
- **each user message** — when it reads as a correction, the model is asked, after fixing, whether the mistake can become a check here.

Errors and warnings are shown to the person as a notice row in the chat and handed to the model with the tool result. An error before a commit refuses that Bash call with the reason. A project without `.claude/lint/` gets nothing from the mod.
