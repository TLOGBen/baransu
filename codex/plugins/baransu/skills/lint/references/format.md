# `.claude/lint/` format

## Where it lives: the root and `lint.json`

The project's root is the nearest folder, from the session's directory upward, that holds `.claude/lint/` — a git repo or a plain folder (a workspace over several repos). With none found, the git top level. In a plain folder every check still runs, and settings, globs and `sgconfig` are always read from the lint root. `forbid` searches the folder's files with each repo's own `.gitignore` applied (`git grep --no-index --exclude-standard`). A commit or push there is checked once per git write, in the repo it commits in — the directory the command reaches through `cd`, `Set-Location` or `git -C`: the git built-ins (`git-facts`, `secret-files`, `up-to-date`) and "what the change touches" read that repo, and `forbid` and ast-grep report only that repo's files; a `run` with `files` runs when that repo's change touches them, a `run` without `files` runs at the lint root as at any moment. When `.claude/lint` sits in a repo's subfolder, a commit's git built-ins read that repo. A commit whose directory the text does not show (`~`, a variable, `cd -`, `popd`, git inside another command) or that has no repo to check gets a warning that its checks did not run; the commit itself goes ahead. `worktree-cleanup` and the git facts given to the model belong to a repo and are skipped at a plain-folder root. In an ordinary project (the root is a repo) a commit is checked at the root, as before.

`.claude/lint/lint.json` is optional, plain JSON, and the one fixed path; every other path is named inside it, relative to its folder, and may not leave the project (a path that does falls back to its default and is reported). Its fields and defaults:

| Field | Default | Meaning |
|---|---|---|
| `converter` | `"toml"` | Which reader turns a check file into a check. `toml` is the only one today. |
| `checks` | `"checks"` | The folder of check files. |
| `sgconfig` | `"sgconfig.yml"` | ast-grep's config; where the rules live is its own `ruleDirs`. |

## A check: `checks/<id>.toml`

One check per file; the file name without `.toml` is its id. The mod reads a small subset of TOML: `key = "string"`, `key = 'literal string'`, `key = ["a", 'b']`, and `#` comments. Use single-quoted literal strings for regexes, so backslashes stay as written.

| Field | Meaning |
|---|---|
| `on` | When it runs: any of `edit`, `commit`, `done`, `bash`, `manual`. `bash` is before every Bash or PowerShell command, and its `forbid` is matched against the command line itself, not a file — for rules about how commands are written. `manual` runs only when the lint skill is called: calling it first runs every check on files over the whole tree — each `forbid` and `run` whose `on` names `manual`, `edit`, `commit` or `done`, a `run` whether or not the change touched its files (one holding `{file}` once per file in its scope, at most 200), and ast-grep — and puts the result at the top of the skill's text; a check `on = ["manual"]` (a code-style pass, a slow suite) runs there and nowhere else. `skill:<name>` runs it before that skill starts, over the whole tree as `manual` does, with the result at the top of the skill's text (`skill:baransu:hypothesis`; `skill:hypothesis` names it too); one naming `$baransu:ship` or `$baransu:review` joins their `done` run, and `$baransu:lint` runs it with every other check on files. Built-ins fix their own moment and ignore this. |
| `severity` | `error`, `warn`, or `off`. An error stops: it refuses a commit and tells `$baransu:ship` to stop. A warning is shown and lets the step go on. |
| `files` | Globs the check applies to. A glob with no `/` matches the file name anywhere (`*.sh`, `Makefile`); one with `/` matches the path from the repo root (`**/*.test.ts`, `src/**`). Empty or absent: every file. |
| `ignores` | Globs to leave out, same rules. |
| `forbid` | A regex (PCRE, as `git grep -P` reads it) that must not match any line in scope. |
| `run` | A command as an argument list. At `edit`, `{file}` becomes the edited file's path; a command holding `{file}` runs only at `edit`. A non-zero exit is a failure, and the output's last lines are shown. At `commit` and `done`, a `run` check with `files` runs only when the change since the last commit touches a file in scope, so a slow check (a test suite, TLC) runs only when its code moved. The command must be one the project can run on its own, so CI can run the same command. |
| `builtin` | One of the built-ins below, in place of `forbid` / `run`. |
| `message` | What to write instead. Shown with every finding. |
| `changed` | A note shown at `commit` / `done` whenever the change touches a file in `files`, pass or fail. For a check whose truth lives outside the code, like a model of it. |
| `from` | Set by `$baransu:lint init` on a copied preset check: `baransu-preset@<version>`. |
| `origin` | The commit the mistake was found in, when there is one. |
| `action` | A label for the reader: `重新` on a built-in whose answer is a redo (the words already reached the user, so the model says it again the right way). The mod does not read it; the built-in decides. |
| `redo` | On a 重新 built-in, the instruction the model gets in place of the default (`user-language`: restate the way `$baransu:huh` does; `explain-before-edit`: say how the change will be made in a sentence or two, then go on; `report-before-stop`: report the way `$baransu:what-now` does). |

Exactly one of `forbid`, `run`, `builtin` per check.

Four answers, from before the act to after it: **error** stops it; **hold** (`destructive-preview`) stops it once to show what it touches; **warn** lets it run and says so; **重新** comes after the words already reached the user and asks for them again, the right way.

## ast-grep rules: `rules/<id>.yml`

ast-grep's own rule format (`id`, `language`, `severity: error | warning | off`, `message`, `files`, `ignores`, `rule`). The mod scans with `.claude/lint/sgconfig.yml` (`ruleDirs: [rules]`): the edited file at `edit`, the whole tree at `commit`, `done` and `manual`. Start `files` globs with `**/`, since ast-grep resolves them from the config's folder. `language: typescript` covers `.ts` only; a rule meant for `.tsx` or `.js` needs its own copy with `language: tsx` or `javascript`. ast-grep reads UTF-8 only: a Big5 file yields no match and no error.

## Built-ins

Checks the mod computes itself, because they are about the session or the repo rather than a file's text.

| `builtin` | Moment | What it does |
|---|---|---|
| `git-facts` | session start, commit | Collects the repo's facts: remote and whether it is public or private (GitHub through `gh`; other hosts read 「未知」), the configured author against recent authors, the format and language of recent subjects, whether past commits carry `Co-Authored-By`, the default branch and whether work reaches it by direct push or by PR / MR merges. The facts go to the model at session start. At commit it flags an author that matches no recent author, a `Co-Authored-By` trailer in a repo that never used one, and a push to the default branch in a repo that merges through PRs. A push that names a refspec is read by it: `git push origin tmp:main` lands on main and sends the commits tmp has that `origin/main` lacks; without one, the current branch and its upstream decide. |
| `secret-files` | commit | Flags staged files whose names look like secrets (`.env`, `*.pem`, `*.key`, `id_rsa*`, `*.p12`, `credentials*.json`). |
| `built-before-commit` | commit | Flags a commit or push when no command ran since the last edit — nothing was built or tested. |
| `up-to-date` | commit | Fetches, then flags a commit or push while the upstream has commits this branch lacks. |
| `session-record` | done | Lists the commands run since the last edit with how each ended (a background command does not count as run; an edit is counted even before `.claude/lint/` existed), and whether a `$baransu:review` that ran to its answer started since then (one the user stopped does not count), so `$baransu:ship` can see whether the change was built, tested and reviewed. |
| `worktree-cleanup` | session start | Lists worktrees whose branch is already merged and could be removed. |
| `destructive-preview` | bash | Before a command that deletes, moves or discards (`rm`, `mv`, `Remove-Item`, `rd`, `rimraf`, `git rm`, `find … -delete` / `-exec rm`, `git clean`, `git reset --hard`, `git checkout --`, `git restore`, `git branch -D`, `git worktree remove`, `git stash drop` / `clear`), lists what it would touch — each path as a file, a folder with its entry count, or missing; the files `find … -print` and `git clean -n` name; the changes a reset or restore drops; the branch's last commits and whether it is merged; a worktree's uncommitted files. Paths are read from the directory the session's shell is really in (`$.session.cwd()`, the actor's own), never guessed from earlier commands. At `error` the first run is held back with that list, and the same command goes through only in a later response of the same actor (main loop or a subagent), in the same directory and shell, and only until the turn ends — two copies in one response are both held. A `sudo`, `env` or `npx` prefix, a `( … )` subshell and `bash -c` / `pwsh -c` / `cmd /c` are seen through; a path with `~` or `$` is shown as one the mod cannot expand; `xargs rm` is held with a note, since what it deletes depends on the command before it. |
| `explain-before-edit` | edit | 重新. The first file change of a main-loop turn — an edit, or a shell command that writes a file — came before any words to the user: the model says in a sentence or two how it will make the change, then goes on without waiting, stopping to ask only when it is unsure. A read-only command is no change. Words are what the person sees: streamed text, or a thinking block that carries text (on Claude Opus 5.5 the words between tool calls stream that way); hidden reasoning is not. At `error` the call is held once, with that request. |
| `report-before-stop` | turn end | 重新. A main-loop turn that edited or ran something ended with an answer but without a report (a turn the person interrupted owes none, and leaves a report owed from before as it was) (60 letters or more the person saw after the last such step, as `explain-before-edit` counts words, code included, a Chinese character counting as two; words written before that step do not count, and a read-only command such as `git status` is not a step): the user's next message carries the request — a slash command carries a copy, delivered once the command opens a turn, so `/cost` leaves it owed — or else the next main-loop command does, to report the way `$baransu:what-now` does. A later turn that reports clears it. |
| `correction-to-lint` | every user message | When the user's message reads as a correction（「又犯」「不是這樣」「說過了」, "again", "wrong"）, a notice says so and the model is told to fix first, then decide whether the mistake can become a check — hand it to `$baransu:lint` if it can, say why in one line if it cannot. So a mistake the user had to correct once becomes a candidate check every time, not only when someone remembers. |
| `user-language` | every reply | 重新. Checks what the model actually wrote: when the user writes Chinese (`language = "..."` when set, else read from the user's latest message, a slash command's arguments included) and a block the model sends is English prose — code and backticks left out — identifiers such as `session.start` or `camelCase` left out too — the person sees it flagged and the model restates each such block once, the way `$baransu:huh` does, by the user's next message at the latest. A reminder in the system prompt alone did not stop the slip, so this reads the output. |
| `built-before-commit`, `up-to-date`, … | | Every built-in's state, the cards drawn and the git facts included, is kept in the session (`$.state`), so a reload of the mod forgets nothing; a `/clear` starts it over. The rules this state keeps in every order of events are checked by a TLA+ model in baransu's repo, `.claude/hypothesis/lint-mod-state/`. |

## A TLA+ model as a check

`$baransu:lint init` writes these only at the 嚴格 level. This is how a state the code must keep — a state machine's rules, an order that must never happen — stays true while the code keeps changing. A `$baransu:hypothesis` judge registers as a `run` check: `on = ["done"]`, `files` the code the hypothesis covers, `run` the TLC command its README gives, `severity = "error"`. The check runs only when the covered code changed. TLC exits 0 when every rule holds and non-zero on a violation or a deadlock, so a broken rule stops `$baransu:ship`.

TLC checks the spec, not the code: when the code changed and the spec did not, TLC still passes. So the check carries a `changed` note that sends the model to `$baransu:hypothesis --maintain` whenever the covered code moved, pass or fail; maintenance redraws the model from the changed code and reruns the judge. The check's own TLC run catches a spec edit that breaks a rule.

```toml
on = ["done"]
severity = "error"
files = ["src/billing/**"]
run = ["tlc", "-workers", "1", "-config", ".claude/hypothesis/billing/Billing.cfg", ".claude/hypothesis/billing/Billing.tla"]
changed = "billing 的程式改了：先跑 $baransu:hypothesis --maintain，讓模型跟上程式再驗證"
message = "billing 的假說有規則被打破；照 .claude/hypothesis/billing/README.md 的出錯路徑修"
```
