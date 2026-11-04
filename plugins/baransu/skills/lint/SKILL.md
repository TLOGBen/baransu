---
name: lint
description: "Keeps a project's lint gate in `.claude/lint/`: copies baransu's preset into the project, adds, disables or changes the severity of a check, explains why a rule exists, and syncs the preset after an update; the baransu mod then runs each check at its timing — before, after or around an act, before a skill or the turn's end, and first thing when this skill is called — and shows the result in the chat. Trigger On '/lint', 'lint 規則', '加一條 lint', '初始化 lint', '這條規則為什麼', 'lint preset', '別再犯這個錯'. Not for diagnosing a failure (/hunt) or auditing agent config (/health)."
argument-hint: "[help | show | init | add <mistake> | <check> off|info|warn|retry|check|error | why <check> | sync] — runs every check first (not for help or show)"
---

# lint — keep the checks that make a known mistake impossible

A mistake an agent has found once should not be possible again. This skill owns the project's `.claude/lint/` folder: what each check catches, when it runs, how severe it is. It never runs the checks itself; the baransu mod does that at each moment "What the mod does" lists — calling this skill is one of them — and shows the result in the chat (see "What the mod does"). `/hunt`, `/health` and `/draft` decide that a check should exist; they hand the writing to this skill, so the format has one owner.

All user-facing output is in Traditional Chinese.

## Outcome Contract

- **Outcome**: The project's `.claude/lint/` holds the checks the user wants, in sets that `config.toml` extends — the preset's under `sets/baransu/`, the project's own under `sets/local/` — with the preset copied from this skill's `preset/` on first use and kept in step on request.
- **Done when**: The asked change is written in the format `references/format.md` gives; a new or changed check was run once on the current tree and, when a past commit carried the mistake, on that commit, and both results were shown; an explanation names what the rule blocks, why it exists, and what to use instead.
- **Evidence**: The files written or changed, and the output of the check run on the tree (and on the past commit when one exists).
- **Output**: Files under `.claude/lint/`; a Traditional Chinese summary in the conversation.
- **Automation**: ultracode=neutral, loop=not-drivable（each change is a choice the user makes about their own project）

## The folder

```
.claude/lint/
  config.toml           # [settings] · [[extends]] the sets in force · [check.<id>] changes to a preset check
  sets/baransu/*.toml   # baransu's preset sets, copied by init, replaced whole by sync — never edited by hand
  sets/local/*.toml     # the project's own sets: every check this project writes ([check.<id>] tables)
  rules/<id>.yml        # ast-grep rules, ast-grep's own format
  scripts/              # the scripts a `run` check names
  sgconfig.yml          # ast-grep config: ruleDirs: [rules]
```

`references/format.md` is the format: the layout, the fields of a check, the built-in checks, and how the mod matches a file. Read it before writing a check. The mod reads the folder once and keeps it in memory; it reads it again when this skill is called and when a file under it is edited, so a change made here is in force at once. `/ship` never archives this folder: it is a kept product, like `.claude/hypothesis/`.

## Uses

**Init** (`/lint init`, or the first use in a project with no `.claude/lint/`). Ask for a level first:

- **關閉** — no preset; only the project's own checks.
- **預設** — the preset sets that fit this project, each at level `normal`. Read the project first — its languages, scripts, shells, tools, and the owner's rules that apply to it — then recommend the sets, one line each with why it fits here (`git`, `files`, `docs`, `env`, `runtime`, `tla`), and let the user drop any. A set with one or two checks that do not fit stays, with `except = [...]` on its extends entry.
- **嚴格** — 預設 at level `strict`: the sets' own `strict` values (`built-before-commit`, `up-to-date`, `private-key-material` to `error`, `tla-parses` on), plus one TLA+ check per `.claude/hypothesis/<area>/` in the project, written into `sets/local/` from that hypothesis's README as `references/format.md` (last section) shows. The TLA+ checks stay off below this level: most projects keep no model, and TLC is the slowest check there is.

Then write the folder: copy each chosen set from this skill's `preset/sets/<name>.toml` to `.claude/lint/sets/baransu/<name>.toml`, write `config.toml` with one `[[extends]]` entry per set (`set = "sets/baransu/<name>.toml"`, `level` when strict), create `sets/local/` for the project's own checks, copy the scripts a copied check's `run` names from `preset/scripts/` to `.claude/lint/scripts/`, and the ast-grep rules that fit from `preset/rules/` with `sgconfig.yml`. Write `# baransu-preset@<version>` at the top of `config.toml`, the version from `../../.claude-plugin/plugin.json`. If `.claude/lint/` would be ignored by git (`git check-ignore`), say so, because the checks would then not reach the repo or its CI.

**Add a check.** From the user, or handed over by `/hunt`, `/health` or `/draft` with the mistake and where it happened. Pick the timing where it can still be stopped (`references/format.md`, 時機): `pre:` when the act can be refused before it happens — a write's text, a command line, a commit — `post:` or `around:` when only the result shows it, `pre:stop` for what the turn must not end without, `remind = true` when the model should know the rule before acting. Pick the cheapest form that catches it: an ast-grep rule when the mistake has a syntax shape, a `forbid` regex when it is plain text, a `run` command when the project already has a tool that catches it (ESLint, a type check, a test), a built-in when the mistake is about the agent's behaviour rather than a file. Write the message as what to use instead. Run the check once on the current tree; when a past commit carried the mistake, run it there too (`git worktree add` a temporary tree), and show both: it should fail on the past and pass now. A check that cannot fail on the mistake it names is not done. Give each check the narrowest scope that still catches the mistake (`references/format.md`, 範圍): `scope = "diff"` when an old problem elsewhere must not stop this change, `related` when the files it imports or that import it can break with it, `folder` / `file` / `ext` for where, `actions` for an act rather than a file, `when` for the environment it applies in — and copy the template of that kind from format.md. Write the check as a `[check.<id>]` table in a set under `sets/local/` (a new set when it belongs to no existing one, then an `[[extends]]` entry for it in `config.toml`), never in `sets/baransu/`. A `/hypothesis` model is a check too: its TLC command as a `run` check on `pre:skill:ship` and `pre:skill:review`, `file` the code it covers with `scope = "diff"` (`references/format.md`, last section), so a change that breaks one of its rules stops `/ship`.

**Disable or change severity.** For a preset check, write the change in `config.toml` as a table with only that field — `[check.<id>]` and `severity = "..."` — never in `sets/baransu/`, so the next sync keeps it; for the project's own check, change it in its set under `sets/local/`. The levels are `error`, `check`, `retry`, `warn`, `info` and `off`; a level the check's timing refuses (`references/format.md`, 時機) keeps it off, so say which levels its timings take. Never delete a preset check the user only wants quiet: `off` keeps it visible to the next sync.

**Help** (`/lint help`, or 「lint 怎麼用」). Explain how lint is used, for someone who has not used it: what it is for, the three levels, the timings a check can run at (the 時機 of `references/format.md`: pre / post / around an act, `after:<act>:<wait>`, `manual`, and the acts — edit, bash, commit, push, a skill, the stop, a subagent, a compaction, a file changed outside Claude, a 重新 answer), what a check can cover (its 範圍: the whole project, this change, the change and its imports, a folder, a file pattern, an extension, a delete or a worktree removal, and an environment), what a check can do (`forbid`, `run`, an ast-grep rule, a built-in, a message alone, `remind`), the six levels — error, check, retry, warn, info, off — and what each does before and after an act, with the exceptions (the stop held at most three times; a subagent, an outside change and a wait only warn or info; a compaction never refused; before `/review` a record only), the uses of this skill, and one example: a `config.toml` extending a preset set, and one check of the project's own in `sets/local/`. Take every fact from `references/format.md` and this file, not from memory. Nothing is run.

**Show** (`/lint show`, or 「現在有哪些 lint」). List every check in this project's `.claude/lint/`, read from the files — the ones turned off too, and for each where it comes from (`sets/baransu/git.toml`, `sets/local/repo.toml`, or changed in `config.toml`) — grouped by its timing as written (`pre:bash`, `after:edit:10m`), one row each: its id; its scope in plain words (「整個專案」, 「這次改到的檔」, 「改到的檔和 import 它們的檔，三層」, 「只看 `*.tla`」, 「`src/` 底下，排除測試」, 「刪除前，刪到 hypothesis 時」, 「只在 Windows」); what it looks for in plain words — a `forbid` regex or a `run` command translated into what it catches, a built-in by what it does — never the raw pattern alone; its level (error / check / retry / warn / info / off) with what that level does at that timing, and 「提醒」 when `remind` is on. End with the ast-grep rules, one line each. Nothing is run. `/lint` with no other ask runs every check first (the mod does), says what that found, then shows this list.

**Explain.** For a check id or a message the user saw: what it blocks, the evidence it came from (its `from`, its `origin` commit, or the rule it restates), and what to write instead. Read the file and the commit; do not answer from memory.

**Sync** (`/lint sync`). From this skill's directory, bring the project to this version's format first, each step only when the mod reports what it fixes, and show each script's lines:

1. 「files 改名了」 — `python scripts/migrate-scope.py <the project's checks folder>`: `files` becomes `file`, a slow `run` check gets the `scope = "diff"` it used to imply.
2. 「舊寫法 …」 timings — `python scripts/migrate-timing.py <the project's .claude/lint folder>`: `on`, `actions = ["push"|"redo"]`, and the built-ins' levels whose meaning moved.
3. 「還是舊的版面」 — `python scripts/migrate-layout.py <the project's .claude/lint folder>`: `lint.json` into `config.toml [settings]`, `lint.toml` into `config.toml`, `sets/baransu-*.toml` to `sets/baransu/`, other sets to `sets/local/`, and each `checks/<id>.toml`, after steps 1 and 2's rewrites, to a `config.toml` patch of only the fields that differ when an extended preset set defines that id with the same action, otherwise to `sets/local/checks.toml`. It writes only new files and never overwrites one that already holds something else (it names it instead). Then call this skill again (the mod reads the folder again) and confirm no 「設定讀不懂」 is left and the checks in force are the same; only then run it once more with `--remove`, on its own, to delete the old files.

Then update the presets: compare each `sets/baransu/<name>.toml` with this skill's `preset/sets/<name>.toml`, list the checks that changed, were added or were removed upstream in plain words, and copy the new sets over whole — the project's changes live in `config.toml` and `sets/local/`, so nothing of theirs is lost. A changed check that a `config.toml` patch touches is named, so the user can decide whether the patch still fits. Bring the scripts a set's `run` checks name into `.claude/lint/scripts/`, and update the version line at the top of `config.toml`.

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

Findings are handed to the model as their level says at that timing, and shown to the person where the surface can: as a card under the call they belong to (a tool call, the Agent or Workflow call that started a subagent, the Skill call that loaded a skill), or, for a moment with no call, as a plain row in the chat. A clean run draws nothing, except `/lint`, which was asked for its result; what a hold-once already showed is not said again when the act passes. A project without `.claude/lint/` gets nothing from the mod.
