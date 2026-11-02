# `.claude/lint/` format

## A check: `checks/<id>.toml`

One check per file; the file name without `.toml` is its id. The mod reads a small subset of TOML: `key = "string"`, `key = 'literal string'`, `key = ["a", 'b']`, and `#` comments. Use single-quoted literal strings for regexes, so backslashes stay as written.

| Field | Meaning |
|---|---|
| `on` | When it runs: any of `edit`, `commit`, `done`, `bash`. `bash` is before every Bash or PowerShell command, and its `forbid` is matched against the command line itself, not a file — for rules about how commands are written. Built-ins fix their own moment and ignore this. |
| `severity` | `error`, `warn`, or `off`. An error stops: it refuses a commit and tells `/ship` to stop. A warning is shown and lets the step go on. |
| `files` | Globs the check applies to. A glob with no `/` matches the file name anywhere (`*.sh`, `Makefile`); one with `/` matches the path from the repo root (`**/*.test.ts`, `src/**`). Empty or absent: every file. |
| `ignores` | Globs to leave out, same rules. |
| `forbid` | A regex (PCRE, as `git grep -P` reads it) that must not match any line in scope. |
| `run` | A command as an argument list. At `edit`, `{file}` becomes the edited file's path; a command holding `{file}` runs only at `edit`. A non-zero exit is a failure, and the output's last lines are shown. At `commit` and `done`, a `run` check with `files` runs only when the change since the last commit touches a file in scope, so a slow check (a test suite, TLC) runs only when its code moved. The command must be one the project can run on its own, so CI can run the same command. |
| `builtin` | One of the built-ins below, in place of `forbid` / `run`. |
| `message` | What to write instead. Shown with every finding. |
| `changed` | A note shown at `commit` / `done` whenever the change touches a file in `files`, pass or fail. For a check whose truth lives outside the code, like a model of it. |
| `from` | Set by `/lint init` on a copied preset check: `baransu-preset@<version>`. |
| `origin` | The commit the mistake was found in, when there is one. |

Exactly one of `forbid`, `run`, `builtin` per check.

## ast-grep rules: `rules/<id>.yml`

ast-grep's own rule format (`id`, `language`, `severity: error | warning | off`, `message`, `files`, `ignores`, `rule`). The mod scans with `.claude/lint/sgconfig.yml` (`ruleDirs: [rules]`): the edited file at `edit`, the whole tree at `commit` and `done`. Start `files` globs with `**/`, since ast-grep resolves them from the config's folder. `language: typescript` covers `.ts` only; a rule meant for `.tsx` or `.js` needs its own copy with `language: tsx` or `javascript`. ast-grep reads UTF-8 only: a Big5 file yields no match and no error.

## Built-ins

Checks the mod computes itself, because they are about the session or the repo rather than a file's text.

| `builtin` | Moment | What it does |
|---|---|---|
| `git-facts` | session start, commit | Collects the repo's facts: remote and whether it is public or private (GitHub through `gh`; other hosts read 「未知」), the configured author against recent authors, the format and language of recent subjects, whether past commits carry `Co-Authored-By`, the default branch and whether work reaches it by direct push or by PR / MR merges. The facts go to the model at session start. At commit it flags an author that matches no recent author, a `Co-Authored-By` trailer in a repo that never used one, and a push to the default branch in a repo that merges through PRs. |
| `secret-files` | commit | Flags staged files whose names look like secrets (`.env`, `*.pem`, `*.key`, `id_rsa*`, `*.p12`, `credentials*.json`). |
| `session-record` | done | Lists the commands run since the last edit with how each ended, and whether `/review` ran since then, so `/ship` can see whether the change was built, tested and reviewed. |
| `worktree-cleanup` | session start | Lists worktrees whose branch is already merged and could be removed. |
| `destructive-preview` | bash | Before a command that deletes, moves or discards (`rm`, `mv`, `Remove-Item`, `git clean`, `git reset --hard`, `git checkout --`, `git restore`, `git branch -D`, `git worktree remove`, `git stash drop` / `clear`), lists what it would touch — each path as a file, a folder with its entry count, or missing; the files `git clean -n` names; the changes a reset or restore drops; the branch's last commits and whether it is merged; a worktree's uncommitted files. At `error` the first run is held back with that list and the same command again goes through. |
| `explain-before-edit` | edit | Flags a turn whose first edit or Bash call came before any text to the user. |
| `user-language` | every turn | Tells the model the user's language: `language = "..."` when set, else the language of the user's latest message. |

## A TLA+ model as a check

`/lint init` writes these only at the 嚴格 level. This is how a state the code must keep — a state machine's rules, an order that must never happen — stays true while the code keeps changing. A `/hypothesis` judge registers as a `run` check: `on = ["done"]`, `files` the code the hypothesis covers, `run` the TLC command its README gives, `severity = "error"`. The check runs only when the covered code changed. TLC exits 0 when every rule holds and non-zero on a violation or a deadlock, so a broken rule stops `/ship`.

TLC checks the spec, not the code: when the code changed and the spec did not, TLC still passes. So the check carries a `changed` note that sends the model to `/hypothesis --maintain` whenever the covered code moved, pass or fail; maintenance redraws the model from the changed code and reruns the judge. The check's own TLC run catches a spec edit that breaks a rule.

```toml
on = ["done"]
severity = "error"
files = ["src/billing/**"]
run = ["tlc", "-workers", "1", "-config", ".claude/hypothesis/billing/Billing.cfg", ".claude/hypothesis/billing/Billing.tla"]
changed = "billing 的程式改了：先跑 /baransu:hypothesis --maintain，讓模型跟上程式再驗證"
message = "billing 的假說有規則被打破；照 .claude/hypothesis/billing/README.md 的出錯路徑修"
```
