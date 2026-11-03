---
name: lint
description: "Keeps a project's lint gate in `.claude/lint/`: copies baransu's preset into the project, adds, disables or changes the severity of a check, explains why a rule exists, and syncs the preset after an update; the baransu mod then runs each check at its timing — before, after or around an act, before a skill or the turn's end, and first thing when this skill is called — and shows the result in the chat. Trigger On '/lint', 'lint 規則', '加一條 lint', '初始化 lint', '這條規則為什麼', 'lint preset', '別再犯這個錯'. Not for diagnosing a failure (/hunt) or auditing agent config (/health)."
argument-hint: "[help | show | init | add <mistake> | <check> off|info|warn|retry|check|error | why <check> | sync] — runs every check first (not for help or show)"
---

# lint — keep the checks that make a known mistake impossible

A mistake an agent has found once should not be possible again. This skill owns the project's `.claude/lint/` folder: what each check catches, when it runs, how severe it is. It never runs the checks itself; the baransu mod does that at each moment "What the mod does" lists — calling this skill is one of them — and shows the result in the chat (see "What the mod does"). `/hunt`, `/health` and `/draft` decide that a check should exist; they hand the writing to this skill, so the format has one owner.

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

`references/format.md` is the format: the fields of a check, the built-in checks, and how the mod matches a file. Read it before writing a check. `/ship` never archives this folder: it is a kept product, like `.claude/hypothesis/`.

## Uses

**Init** (`/lint init`, or the first use in a project with no `.claude/lint/`). Ask for a level first:

- **關閉** — no preset; only the project's own checks.
- **預設** — `preset/general/`, and from `preset/personal/` the 3–7 checks that fit this project. Read the project first — its languages, scripts, shells, tools, and the owner's rules that apply to it — then recommend those checks, one line each with why it fits here, and let the user confirm. Never hand over the whole personal list to tick.
- **嚴格** — 預設, with `built-before-commit`, `up-to-date` and `private-key-material` raised to `error`, plus one TLA+ check per `.claude/hypothesis/<area>/` in the project, written from that hypothesis's README as `references/format.md` (last section) shows, and `preset/strict/`: its `tla-parses` check, copied to `checks/`, with its script copied to `.claude/lint/scripts/tla-parse.py` (it parses each edited `.tla` with SANY and catches an action that both changes a variable and lists it in UNCHANGED). The TLA+ checks stay off below this level: most projects keep no model, and TLC is the slowest check there is.

Then copy into the project: show the list with one line per check and let the user drop any before copying. A copied check whose `run` names `.claude/lint/scripts/<name>` brings that script from its preset's `scripts/` folder (`eol-flip.py`, `py-utf8-out.py`, `csv-utf8-bom.py` in `preset/general/`, `tla-parse.py` in `preset/strict/`). Write `sgconfig.yml` when any rule is copied. Each copied file keeps a `from = "baransu-preset@<version>"` line, the version from `../../.claude-plugin/plugin.json`. If `.claude/lint/` would be ignored by git (`git check-ignore`), say so, because the checks would then not reach the repo or its CI.

**Add a check.** From the user, or handed over by `/hunt`, `/health` or `/draft` with the mistake and where it happened. Pick the timing where it can still be stopped (`references/format.md`, 時機): `pre:` when the act can be refused before it happens — a write's text, a command line, a commit — `post:` or `around:` when only the result shows it, `pre:stop` for what the turn must not end without, `remind = true` when the model should know the rule before acting. Pick the cheapest form that catches it: an ast-grep rule when the mistake has a syntax shape, a `forbid` regex when it is plain text, a `run` command when the project already has a tool that catches it (ESLint, a type check, a test), a built-in when the mistake is about the agent's behaviour rather than a file. Write the message as what to use instead. Run the check once on the current tree; when a past commit carried the mistake, run it there too (`git worktree add` a temporary tree), and show both: it should fail on the past and pass now. A check that cannot fail on the mistake it names is not done. Give each check the narrowest scope that still catches the mistake (`references/format.md`, 範圍): `scope = "diff"` when an old problem elsewhere must not stop this change, `related` when the files it imports or that import it can break with it, `folder` / `file` / `ext` for where, `actions` for an act rather than a file, `when` for the environment it applies in — and copy the template of that kind from format.md. A `/hypothesis` model is a check too: its TLC command as a `run` check on `pre:skill:ship` and `pre:skill:review`, `file` the code it covers with `scope = "diff"` (`references/format.md`, last section), so a change that breaks one of its rules stops `/ship`.

**Disable or change severity.** Change `severity` to `error`, `check`, `retry`, `warn`, `info` or `off` in that check's file; a level the check's timing refuses (`references/format.md`, 時機) keeps it off, so say which levels its timings take. Never delete a preset check the user only wants quiet: `off` keeps it visible to the next sync.

**Help** (`/lint help`, or 「lint 怎麼用」). Explain how lint is used, for someone who has not used it: what it is for, the three levels, the timings a check can run at (the 時機 of `references/format.md`: pre / post / around an act, `after:<act>:<wait>`, `manual`, and the acts — edit, bash, commit, push, a skill, the stop, a subagent, a compaction, a file changed outside Claude, a 重新 answer), what a check can cover (its 範圍: the whole project, this change, the change and its imports, a folder, a file pattern, an extension, a delete or a worktree removal, and an environment), what a check can do (`forbid`, `run`, an ast-grep rule, a built-in, a message alone, `remind`), the six levels — error, check, retry, warn, info, off — and what each does before and after an act, with the exceptions (the stop held at most three times; a subagent, an outside change and a wait only warn or info; a compaction never refused; before `/review` a record only), the uses of this skill, and one example check file. Take every fact from `references/format.md` and this file, not from memory. Nothing is run.

**Show** (`/lint show`, or 「現在有哪些 lint」). List every check in this project's `.claude/lint/`, read from the files — the ones turned off too — grouped by its timing as written (`pre:bash`, `after:edit:10m`), one row each: its id; its scope in plain words (「整個專案」, 「這次改到的檔」, 「改到的檔和 import 它們的檔，三層」, 「只看 `*.tla`」, 「`src/` 底下，排除測試」, 「刪除前，刪到 hypothesis 時」, 「只在 Windows」); what it looks for in plain words — a `forbid` regex or a `run` command translated into what it catches, a built-in by what it does — never the raw pattern alone; its level (error / check / retry / warn / info / off) with what that level does at that timing, and 「提醒」 when `remind` is on. End with the ast-grep rules, one line each. Nothing is run. `/lint` with no other ask runs every check first (the mod does), says what that found, then shows this list.

**Explain.** For a check id or a message the user saw: what it blocks, the evidence it came from (its `from`, its `origin` commit, or the rule it restates), and what to write instead. Read the file and the commit; do not answer from memory.

**Sync** (`/lint sync`). First, when any check still carries the pre-8.43.0 `files` field (the mod reports each as 「設定讀不懂：… files 改名了」 and keeps it off), run `python scripts/migrate-scope.py <the project's checks folder>` from this skill's directory and show its lines: it rewrites every such file — the project's own checks too — so none is left off, and gives a slow `run` check the `scope = "diff"` it used to imply. Then, when any check still names a timing from before 8.43 (「舊寫法 … 跑 /lint sync」), run `python scripts/migrate-timing.py <the project's .claude/lint folder>` and show its lines: it rewrites `on`, `actions = ["push"|"redo"]` and the built-ins' levels whose meaning moved, in `lint.toml`, `sets/` and `checks/`; running it twice changes nothing. Then compare each project file carrying `from` with this skill's current preset: list checks that changed, were added, or were removed upstream, and apply only what the user picks; a check that brings a script brings it into `.claude/lint/scripts/`. A project's own edits to a copied check win unless the user says otherwise.

**The project's own "run X before Y".** When the project's `CLAUDE.md` or `AGENTS.md` tells the agent to run something before a step (「commit 前跑 ESLint」), offer to turn it into a check with the matching `on`, so the mod runs it instead of the agent remembering it.

## What the mod does

The baransu mod reads `.claude/lint/` and runs each check at the timings its `on` names (`references/format.md`, 時機), settling what its level does there:

- **before, after and around an act** — an edit (Edit / Write / MultiEdit / NotebookEdit), a Bash or PowerShell command, a `git commit` or `git push`: `pre:` checks can refuse it (a write whose text breaks a rule, a command line, a delete — with the preview of what it would touch — a commit), `post:` checks read the result, `around:` checks the difference; the git built-ins run before a commit or push.
- **before a skill** — `pre:skill:<name>` checks, over the whole tree, the result at the top of the skill's text; before `/ship` and `/review` with ast-grep and the session record — for `/ship` an error means stop. A skill no check names is left as it is.
- **before the turn ends** — `pre:stop` checks and `report-before-stop`; holding keeps the model working in the same turn.
- **after a subagent, around a compaction, after a file changed outside Claude, when a wait runs out** — their lines wait for the model's next step; a compaction's instructions carry what is still owed.
- **a 重新 answered** — `post:retry` checks read the model's answer, drawn on the person's card.
- **manual** — when this skill is called: every check on files over the whole tree, and ast-grep, written at the top of this skill's text. When the text opens with that 「Lint 紀錄」, tell the person what it found in a sentence or two (saying so when it found nothing) before the work they asked for. A check `on = ["manual"]` runs only here.
- **the system prompt** — the repo's git habits, the user's language, and every `remind = true` check's message.
- **session start** — the worktree built-in, and the watch for `post:file`.
- **each user message** — when it reads as a correction, the model is asked, after fixing, whether the mistake can become a check here.

Findings are shown to the person as a card under the call or a notice row in the chat, and handed to the model as their level says at that timing. A project without `.claude/lint/` gets nothing from the mod.
