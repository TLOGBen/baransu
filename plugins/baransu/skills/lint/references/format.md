# `.claude/lint/` format

## Where it lives: the root, `config.toml` and the sets

The project's root is the nearest folder, from the session's directory upward, that holds `.claude/lint/` — a git repo or a plain folder (a workspace over several repos). With none found, the git top level. In a plain folder every check still runs, and settings, globs and `sgconfig` are always read from the lint root. `forbid` searches the folder's files with each repo's own `.gitignore` applied (`git grep --no-index --exclude-standard`). A commit or push there is checked once per git write, in the repo it commits in — the directory the command reaches through `cd`, `Set-Location` or `git -C`: the git built-ins (`git-facts`, `secret-files`, `up-to-date`) and "what the change touches" read that repo, and `forbid` and ast-grep report only that repo's files; a `run` with `scope = "diff"` runs when that repo's change touches its scope, any other `run` runs at the lint root as at any moment. When `.claude/lint` sits in a repo's subfolder, a commit's git built-ins read that repo. A commit whose directory the text does not show (`~`, a variable, `cd -`, `popd`, git inside another command) or that has no repo to check gets a warning that its checks did not run; the commit itself goes ahead. `worktree-cleanup` and the git facts given to the model belong to a repo and are skipped at a plain-folder root. In an ordinary project (the root is a repo) a commit is checked at the root, as before.

The folder:

```
.claude/lint/
  config.toml           # [settings] · [[extends]] the sets in force · [check.<id>] changes to a preset check
  sets/baransu/*.toml   # baransu's preset sets: copied by /lint init, replaced whole by /lint sync
  sets/local/*.toml     # the project's own sets
  rules/<id>.yml        # ast-grep rules
  scripts/              # scripts a `run` check names
  sgconfig.yml          # ast-grep's config
```

The mod reads the folder once and keeps what it read in memory: it reads it again when `/lint` is called and when a file under the folder is edited (dot folders are not rules). Nothing is written into the folder.

`config.toml` is the one fixed path. Its parts:

| Part | Meaning |
|---|---|
| `[settings]` | `converter` (default `"toml"`): the reader of the sets, `toml` the only one today. `sgconfig` (default `"sgconfig.yml"`): ast-grep's config, relative to `.claude/lint/` and inside it; where the rules live is its own `ruleDirs`. A value that is not a string, or a path outside the folder, keeps the default and is reported. |
| `[[extends]]` | One set in force: `set = "sets/baransu/git.toml"`; `level = "strict"` takes the set's `strict` values; `severity` sets every check of the set; `only = [...]` / `except = [...]` choose its checks. In written order. |
| `[check.<id>]` | A change to a check a set brought in: only the fields it writes replace that check's (`severity = "off"` turns it off). A table with `forbid`, `run` or `builtin` defines a whole check instead. |

A set is a file of `[check.<id>]` tables, each one whole check. Which wins, from first to last: each extends entry in order (a later definition of the same id replaces an earlier one), then `config.toml`'s own tables. For a check's level the strongest is `config.toml`'s, then an extends entry's `severity`, then the set's `strict` (at `level = "strict"`) or `severity`.

A project still in the layout before 8.44 — `checks/<id>.toml`, `lint.json`, `lint.toml` — gets one 「設定讀不懂」 naming `/lint sync`, and those files' checks are not in force until sync moves them.

## A check: a `[check.<id>]` table

One table per check in a set; the table's name after `check.` is its id. The mod reads a small subset of TOML: `[table]` headers, `[[extends]]`, `key = "string"`, `key = 'literal string'`, `key = ["a", 'b']` (on one line or several), and `#` comments. Use single-quoted literal strings for regexes, so backslashes stay as written.

| Field | Meaning |
|---|---|
| `on` | When it runs: a list of timings, `"<side>:<act>[:<arg>]"` or `manual` — see 時機 below. Absent with `actions` set: `pre:bash`, where the actions are read. |
| `severity` | `error`, `check`, `retry`, `warn`, `info`, or `off`. What each does depends on the timing (時機 below): before an act `error` refuses it, after one it asks for a fix. `off` keeps the check out of force everywhere. A level a timing refuses (`check` after an act) keeps the check off with 「設定讀不懂」. |
| `remind` | `true`: the check's `message` is in the system prompt from the start, so the model knows the rule before it acts, not only after a slip. Only on a check with no file scope (`folder`, `file`, `ext`, `scope`): a reminder for some files would be said for every file. |
| `scope`, `via`, `depth`, `folder`, `file`, `ext`, `ignores`, `actions`, `when` | Which files, acts and environments the check covers — see 範圍 below. All absent: every file, every occurrence of its moments. |
| `forbid` | A regex that must not match any line in scope. On files it is PCRE, as `git grep -P` reads it; on a command line, a deleted path or a reply it is a JavaScript regex, a leading `(?i)` meaning ignore case. |
| `run` | A command as an argument list. A non-zero exit is a failure, and the output's last lines are shown. `{file}` becomes a path: at `post:edit` the edited file (or, with `scope = "related"`, each file one hop away), at `post:file` each file changed outside Claude, at `manual` each file in scope, before a commit, a push, `/ship` or `/review` each file of a `diff` or `related` scope; a whole-tree `{file}` check does not run there. At a timing whose subject is text (時機 below) the command runs once with the text in `LINT_TEXT`; at an `around:` timing it also gets `LINT_CHANGED` (the changed paths, one per line) and `LINT_BEFORE` (one line per changed path, `<path>` a tab and the blob of its content before the act; empty for a new file; left out when a before could not be kept, so a script never reads "new" for "unknown"), read with `git --git-dir="$LINT_GIT_DIR" cat-file blob <blob>`. `LINT_GIT_DIR` is the mod's own bare git in the system's temp folder (for `around:commit`, the project's own git, which holds the commit before), and `GIT_ALTERNATE_OBJECT_DIRECTORIES` lets the same command reach a blob the project's git holds; nothing is written into the project. A command without `{file}` runs once; with `scope = "diff"` or `"related"` only when the change touches its scope, so a slow check (a test suite, TLC) runs only when its code moved. The command must be one the project can run on its own, so CI can run the same command. At most 500 files are checked; the rest are counted on the card. |
| `builtin` | One of the built-ins below, in place of `forbid` / `run`. |
| `message` | What to write instead. Shown with every finding. |
| `changed` | A note before a commit, a push, `/ship` or `/review` whenever the change touches a file in the check's scope, pass or fail; it reaches the model, not only the card. For a check whose truth lives outside the code, like a model of it. |
| `origin` | The commit the mistake was found in, when there is one. |
| `action` | A label for the reader: `重新` on a built-in whose answer is a redo (the words already reached the user, so the model says it again the right way). The mod does not read it; the built-in decides. |
| `redo` | On a 重新 built-in, the instruction the model gets in place of the default (`user-language`: restate the way `/huh` does; `explain-before-edit`: say how the change will be made in a sentence or two, then go on; `report-before-stop`: report the way `/what-now` does). |

At most one of `forbid`, `run`, `builtin` per check. A check with none of them says its `message` whenever it is due and its scope selects something (never at `manual`): a reminder after a wait (`after:edit:10m`), after a compaction (`post:compact`), or before a skill.

## 時機 — when a check runs, and what its level does there

`on` lists timings. Each is a side and an act, `<side>:<act>`, with an argument for two of them:

- `pre` — before the act: it can still be stopped.
- `post` — after it: it can only be fixed or redone.
- `around` — after it, reading the difference between a snapshot before and one after: `forbid` matches only what is new (the lines an edit added, the paths a command changed, the subjects of new commits).
- `after:<act>:<wait>` — when that long has passed since the last such act with no other in between (`after:edit:10m`; `s`, `m`, `h`; at least one minute). The line for the model waits for its next step; the model is never woken.
- `manual` — when `/lint` is called: every check on files runs first over the whole tree (a check on text only — a command line, a stop's words — has nothing to read there). A check `on = ["manual"]` runs there and nowhere else.

| Act | pre | post | around | after | What a check reads |
|---|---|---|---|---|---|
| `edit` | ✓ | ✓ | ✓ | ✓ | pre: the text the call will write (forbid matches it before the file changes); post: the written file; around: the lines it added |
| `bash` | ✓ | ✓ | ✓ | ✓ | pre: the command line, what it deletes (`actions`); post: the command and its output; around: the files it changed |
| `commit`, `push` | ✓ | ✓ | commit only | ✓ | pre: the files of the change (a push: the files it sends); post: the newest commit (author, message) and the command's output; around: the new commits. A command that commits and pushes is both. |
| `skill:<name>` | ✓ | | | | before that skill starts (`pre:skill:baransu:hypothesis`; `pre:skill:hypothesis` names it too); `pre:skill:ship` and `pre:skill:review` are the gate before closing |
| `stop` | ✓ | | | | the turn's last words the person saw, when the model wants to end its turn |
| `agent` | | ✓ | ✓ | | post: the subagent's last words; around: the files it changed between its start and its end |
| `compact` | ✓ | ✓ | | | pre: the compaction's instructions; post: the summary it wrote |
| `file` | | ✓ | | | a file changed outside Claude (in the editor, by a build); files Claude wrote this turn with Edit or Write are left out, while a file one of its shell commands wrote still counts |
| `retry` | | ✓ | | | the model's answer to a 重新 (the first row with words the person sees, in a later response) |

What a level does:

| Level | pre | post / around |
|---|---|---|
| `error` | refuse the act | ask the model to fix what it did |
| `check` | refuse it once: the same act sent again in a later response of the same actor goes through (it has read the list) | not a level here: the act is done, nothing is left to stop |
| `retry` | let it run and ask the model to redo it — a 重新, whose answer is checked at `post:retry` | ask to redo it |
| `warn` | let it run; one line to the model | the same |
| `info` | the person's card only | the same |

Exceptions, each a fact of the host:

- `pre:stop`: holding means the turn may not end yet — the model goes on in the same turn with the reason. `error` holds at most three times a turn, then lets the turn end and tells the person; `check` and `retry` hold once a turn each, and once held are shown on the card only. A stop that ends the turn queues what it still has for the model's next step.
- `post:agent`, `around:agent`, `post:file`, `after:*`: only `warn` and `info` (`error` reads as `warn` at `post:file`). A subagent does not go on when held, and a file changed outside Claude or a wait has no act to stop. Their lines wait for the model's next step. The host's own compaction agent is not a subagent here.
- `pre:compact`: only `warn` and `info` — refusing a compaction would leave the conversation full. The mod writes what is still owed (a 重新, a queued line) into the compaction's instructions, so the summary keeps it.
- `post:compact`: no `retry`. `post:retry`: no `retry` (it would ask again for every answer), and its `warn` stays on the card.
- `pre:skill`: no `check` — a skill is invoked once, so there is no later same act to let through. `error` there is an instruction in the skill's text to stop first.
- `post:file` needs the watch, which the host sets up at a session start: a check added mid-session counts from the next start or compaction.

The names before 8.43 are problems that keep the check off and point to `/lint sync`, which rewrites them with `scripts/migrate-timing.py`: `edit` → `post:edit`; `bash` → `pre:bash`; `commit` → `pre:commit`, `pre:push`; `done` → `pre:skill:ship`, `pre:skill:review`; `skill:<x>` → `pre:skill:<x>`; `actions = ["push"]` → `on = ["pre:push"]`; `actions = ["redo"]` → `on = ["post:retry"]`. Built-ins whose level changed meaning move with it: `destructive-preview` and `explain-before-edit` `error` → `check`; `explain-before-edit`, `user-language` and `report-before-stop` `warn` → `retry`.

## 範圍 — which files, acts and environments a check covers

One rule combines them: **different fields AND, values inside one field OR**. `base` picks a starting set, the path fields narrow it, `ignores` subtracts, `actions` narrows which occurrences count, `when` gates on the environment. A scope the mod cannot read keeps the whole check off and names every problem as 「設定讀不懂」 — a dropped narrowing never widens a check.

| Field | Values | Meaning |
|---|---|---|
| `scope` | `all` (default) · `diff` · `related` | `all`: the whole project. `diff`: this change — the working tree and staged files against HEAD; at an act that names its own files (an edit, `post:file`, what an `around:` act changed) those files; at a push, the files its commits send. `related`: this change plus the files it imports and the files importing it, walked up and down separately. A plain folder outside a commit has no change, so `diff` and `related` checks wait for a commit there. |
| `via` | `imports` (default) · `mentions` | With `related`: `imports` reads TypeScript / JavaScript, Python, C#, Java and Rust imports; `mentions` adds files that name a changed file or what it exports (one hop). |
| `depth` | `"1"`–`"6"`, default `"3"` | With `related`, before a commit, a push, a skill and at `manual`. After an edit it is always one hop. |
| `folder` | `"src/billing"` · `"re:^packages/[^/]+/src$"` | A folder and everything under it; `re:` tests the regex on a file's folder. Every `re:` in a scope (`folder`, `file`, `ignores`, `branch:re:`) is a JavaScript regex, a leading `(?i)` meaning ignore case; a `forbid` on files is PCRE. |
| `file` | `"*.sh"` · `"src/**/*.ts"` · `"re:(?i)readme"` · `"@docs"` | A glob (no `/`: the name anywhere; with `/`: the path from the root), a regex on the whole path, or an alias: `@docs` (Markdown, rst, adoc, `docs/`, README, CHANGELOG), `@env` (`.env*`, Dockerfile, compose, CI workflows, dependency manifests), `@run` (Makefile, justfile, Procfile, the prove-it recipe, deploy scripts), `@tla` (every `.tla`, and a `.cfg` beside a `.tla` of the same name). |
| `ext` | `["ts", "tsx"]` · `"TLA+"` | Extensions without the dot, any case. `TLA+` is `tla`. |
| `ignores` | like `file` (not `@tla`) | Left out. |
| `actions` | `delete` · `worktree-remove` | What a `pre:bash` command is, read instead of its command line. `delete`: before a command that deletes or moves, the `forbid` reads each path it removes (`rm`, `rmdir`, `del`, `Remove-Item`, `rimraf`, `mv`'s sources, `git rm`), and a path counts when it is in scope or is a folder above the scope (`rm -rf .claude` deletes `.claude/hypothesis/`). What only a run can tell — `find -delete`, `git clean`, `git reset --hard`, `xargs rm` — is not read; `destructive-preview` lists those. `worktree-remove`: the worktrees a `git worktree remove` takes away. (A push is the timing `pre:push`, the answer to a 重新 the timing `post:retry`.) |
| `when` | `os:windows` · `tool:tlc` · `env:CI` · `env:NODE_ENV=production` · `branch:main` · `branch:re:^release/` · `git` · `exists:Dockerfile`, each may start with `!` | Every guard must hold. A guard that does not hold keeps the check quiet; a missing tool says 「沒有 tlc，這條沒檢查」 on the card only. Write the cheap guard first. |

`or` across fields does not exist: "a shell script, or a Makefile" is one field, `file = ["*.sh", "*.bash", "*.zsh", "Makefile"]`, never `ext` plus `file` (that would mean "and").

Templates — copy one, change the values:

```toml
# This change only: a problem already in the tree does not stop this commit.
on = ["pre:commit"]
severity = "error"
scope = "diff"
forbid = '^(<<<<<<<|>>>>>>>) '
message = "還有合併衝突標記"
```

```toml
# The change and what imports it, three hops: type-check each related file at commit.
on = ["pre:commit"]
severity = "warn"
scope = "related"
ext = ["ts", "tsx"]
run = ["npx", "tsc", "--noEmit", "{file}"]
message = "相關的檔型別不過"
```

```toml
# A folder, minus its tests.
on = ["post:edit", "pre:commit"]
severity = "warn"
folder = ["src/billing"]
ignores = ["**/*.test.ts"]
forbid = '\bconsole\.log\('
message = "用 logger"
```

```toml
# An act: never delete the hypothesis records.
actions = ["delete"]
severity = "error"
folder = [".claude/hypothesis"]
forbid = '.'
message = "hypothesis 是保留的產品，不要刪"
```

```toml
# An environment: on Windows a Makefile that runs Python sets UTF-8.
on = ["post:edit", "pre:commit"]
severity = "warn"
when = ["os:windows"]
file = ["Makefile"]
run = ["git", "grep", "-q", "--untracked", "export PYTHONUTF8", "--", "{file}"]
message = "Makefile 要 export PYTHONUTF8=1"
```

```toml
# Documents: a doc that names a changed file, checked for a stale path.
on = ["pre:skill:ship"]
severity = "warn"
scope = "related"
via = ["mentions"]
file = ["@docs"]
forbid = 'hooks/lint\.ts'
message = "lint.ts 已拆成 engine／adapters；改寫文件裡的路徑"
```

```toml
# A 重新 answer: the restate must not still be English prose.
on = ["post:retry"]
severity = "warn"
forbid = '[A-Za-z]{4,}( [A-Za-z]{2,}){4,}'
message = "回答還是英文"
```

```toml
# Before the write: a TLA+ string with a non-ASCII letter is refused before the file changes.
on = ["pre:edit"]
severity = "error"
file = ["*.tla"]
forbid = '"[^"]*[^\x00-\x7F][^"]*"'
message = "TLC 不收非 ASCII 字串"
```

```toml
# After a command: read its output.
on = ["post:bash"]
severity = "warn"
forbid = 'DeprecationWarning'
message = "有相依套件過時了"
```

```toml
# A wait: ten minutes after the last edit with nothing run.
on = ["after:edit:10m"]
severity = "warn"
builtin = "session-record"
message = "改完十分鐘還沒跑過建置或測試"
```

```toml
# A rule known before the act: in the system prompt from the start, and checked before the command.
on = ["pre:bash"]
severity = "error"
remind = true
forbid = 'git\s+push\b.*--force(?!-with-lease)'
message = "不要 force push；要覆寫遠端用 --force-with-lease"
```

```toml
# Before the turn ends: the last words must not leave a TODO for the person.
on = ["pre:stop"]
severity = "retry"
forbid = '(?i)\bTODO\b'
message = "收尾的話裡留了 TODO：說清楚誰要做、什麼時候做"
```

Before 8.43.0 a check narrowed by `files`; that field is now a problem that keeps the check off. `/lint sync` migrates it with `scripts/migrate-scope.py`: `files` becomes `file`, and a `run` without `{file}` whose `on` names `commit`, `done`, or a skill that joins done (`skill:ship`, `skill:review`) also gets `scope = "diff"` at the end of the file, since it used to run only when the change touched its files.


## ast-grep rules: `rules/<id>.yml`

ast-grep's own rule format (`id`, `language`, `severity: error | warning | off`, `message`, `files`, `ignores`, `rule`). The mod scans with `.claude/lint/sgconfig.yml` (`ruleDirs: [rules]`): the edited file after an edit, the whole tree before a commit or push, before `/ship` and `/review`, and at `manual`. Start `files` globs with `**/`, since ast-grep resolves them from the config's folder. `language: typescript` covers `.ts` only; a rule meant for `.tsx` or `.js` needs its own copy with `language: tsx` or `javascript`. ast-grep reads UTF-8 only: a Big5 file yields no match and no error.

## Built-ins

Checks the mod computes itself, because they are about the session or the repo rather than a file's text.

| `builtin` | Timing | What it does |
|---|---|---|
| `git-facts` | session start, `pre:commit`, `pre:push` | Collects the repo's facts: remote and whether it is public or private (GitHub through `gh`; other hosts read 「未知」), the configured author against recent authors, the format and language of recent subjects, whether past commits carry `Co-Authored-By`, the default branch and whether work reaches it by direct push or by PR / MR merges. The facts go to the model at session start. At commit it flags an author that matches no recent author, a `Co-Authored-By` trailer in a repo that never used one, and a push to the default branch in a repo that merges through PRs. A push that names a refspec is read by it: `git push origin tmp:main` lands on main and sends the commits tmp has that `origin/main` lacks; without one, the current branch and its upstream decide. |
| `secret-files` | `pre:commit` | Flags staged files whose names look like secrets (`.env`, `*.pem`, `*.key`, `id_rsa*`, `*.p12`, `credentials*.json`); a name ending `.example`, `.sample` or `.template` (`.env.example`) is a committed example, not a secret. |
| `built-before-commit` | `pre:commit`, `pre:push` | Flags a commit or push when no command ran since the last edit — nothing was built or tested. |
| `up-to-date` | `pre:commit`, `pre:push` | Fetches, then flags a commit or push while the upstream has commits this branch lacks. |
| `session-record` | `pre:skill:ship`, `pre:skill:review`; and `after:<act>:<wait>` when its `on` names one | Lists the commands run since the last edit with how each ended (a background command does not count as run; an edit is counted even before `.claude/lint/` existed), and whether a `/review` that ran to its answer started since then (one the user stopped does not count), so `/ship` can see whether the change was built, tested and reviewed. |
| `worktree-cleanup` | session start | Lists worktrees whose branch is already merged and could be removed. |
| `destructive-preview` | `pre:bash` (default `check`) | Before a command that deletes, moves or discards (`rm`, `mv`, `Remove-Item`, `rd`, `rimraf`, `git rm`, `find … -delete` / `-exec rm`, `git clean`, `git reset --hard`, `git checkout --`, `git restore`, `git branch -D`, `git worktree remove`, `git stash drop` / `clear`), lists what it would touch — each path as a file, a folder with its entry count, or missing; the files `find … -print` and `git clean -n` name; the changes a reset or restore drops; the branch's last commits and whether it is merged; a worktree's uncommitted files and whether its branch's commits are on a remote. Paths are read from the directory the session's shell is really in (`$.session.cwd()`, the actor's own), never guessed from earlier commands. At `check` the first run is held back with that list, and the same command goes through only in a later response of the same actor (main loop or a subagent), in the same directory and shell, and only until the turn ends — two copies in one response are both held. A `sudo`, `env` or `npx` prefix, a `( … )` subshell and `bash -c` / `pwsh -c` / `cmd /c` are seen through; a path with `~` or `$` is shown as one the mod cannot expand; `xargs rm` is held with a note, since what it deletes depends on the command before it. |
| `explain-before-edit` | `pre:edit`, `pre:bash` (default `retry`) | 重新. The first file change of a main-loop turn — an edit, or a shell command that writes a file — came before any words to the user: the model says in a sentence or two how it will make the change, then goes on without waiting, stopping to ask only when it is unsure. A read-only command is no change. Words are what the person sees: streamed text, or a thinking block that carries text (on Claude Opus 5.5 the words between tool calls stream that way); hidden reasoning is not. At `check` the call is held once, with that request; at `error` every such call is. |
| `report-before-stop` | `pre:stop` (default `retry`) | 重新. When the main loop wants to end a turn in which it edited or ran something, without a report after the last such step (60 letters or more the person saw, as `explain-before-edit` counts words, code included, a Chinese character counting as two; a read-only command such as `git status` is not a step), the turn is held once and the model reports in the same turn, the way `/what-now` does. A turn the person interrupts reaches no stop and owes nothing. |
| `correction-to-lint` | every user message | When the user's message reads as a correction（「又犯」「不是這樣」「說過了」, "again", "wrong"）, a notice says so and the model is told to fix first, then decide whether the mistake can become a check — hand it to `/lint` if it can, say why in one line if it cannot. So a mistake the user had to correct once becomes a candidate check every time, not only when someone remembers. At `info` only the notice is shown. |
| `user-language` | every reply (default `retry`) | 重新. Checks what the model actually wrote: when the user writes Chinese (`language = "..."` when set, else read from the user's latest message, a slash command's arguments included) and a block the model sends is English prose — code and backticks left out — identifiers such as `session.start` or `camelCase` left out too — the person sees it flagged and the model restates each such block once, the way `/huh` does, by the user's next message at the latest. A reminder in the system prompt alone did not stop the slip, so this reads the output. At `info` the block is flagged on the card only, and nothing is asked of the model. |
| `built-before-commit`, `up-to-date`, … | | Every built-in's state, the cards drawn and the git facts included, is kept in the session (`$.state`), so a reload of the mod forgets nothing; a `/clear` starts it over. The rules this state keeps in every order of events are checked by a TLA+ model in baransu's repo, `.claude/hypothesis/lint-mod-state/`. |

## A TLA+ model as a check

`/lint init` writes these only at the 嚴格 level. This is how a state the code must keep — a state machine's rules, an order that must never happen — stays true while the code keeps changing. A `/hypothesis` judge registers as a `run` check: `on = ["pre:skill:ship", "pre:skill:review"]`, `file` the code the hypothesis covers with `scope = "diff"`, `run` the TLC command its README gives, `severity = "error"`. The check runs only when the covered code changed. TLC exits 0 when every rule holds and non-zero on a violation or a deadlock, so a broken rule stops `/ship`.

TLC checks the spec, not the code: when the code changed and the spec did not, TLC still passes. So the check carries a `changed` note that sends the model to `/hypothesis --maintain` whenever the covered code moved, pass or fail; maintenance redraws the model from the changed code and reruns the judge. The check's own TLC run catches a spec edit that breaks a rule.

```toml
on = ["pre:skill:ship", "pre:skill:review"]
severity = "error"
file = ["src/billing/**"]
scope = "diff"
run = ["tlc", "-workers", "1", "-config", ".claude/hypothesis/billing/Billing.cfg", ".claude/hypothesis/billing/Billing.tla"]
changed = "billing 的程式改了：先跑 /baransu:hypothesis --maintain，讓模型跟上程式再驗證"
message = "billing 的假說有規則被打破；照 .claude/hypothesis/billing/README.md 的出錯路徑修"
```
