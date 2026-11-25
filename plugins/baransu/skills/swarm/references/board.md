# board — the program that keeps the board

`scripts/board.mjs` is the swarm protocol as a program: every command is one legal move, an illegal one is refused with the reason and exit 1, and the board is left as it was. It prints one line per change (`T12: running → verified`) and then the status line. Plain Node, no dependencies; atomic writes, UTF-8, LF.

```
node <this skill>/scripts/board.mjs <command> <board> ...
  init <board> [seats]                       seats <board> <n>
  add <board> <task-json>                    split <board> <id> <parts-json-array>
  dispatch <board> <id> <bee> <model> <effort>
  ask <board> <id> queen|user|env <question> answer <board> <id> <answer>
  resume <board> <id>                        accept <board> <id> <report-name> <evidence>
  fail <board> <id> <reason>                 show <board>
```

`<board>` is the board folder, `.claude/swarm/<slug>/`. A task given to `add` is `{"id"?, "title", "kind", "paths"?, "depends"?}`; without an id it gets the next `T<n>`. `kind` is scout, worker, guard, measurer or lint. A dependency must already be on the board, so dependencies cannot form a cycle; `split` checks for one. A path is a file or a folder, and a folder owns everything under it; `add` and `split` store each in one spelling — forward slashes, no `./`, `.` or `..` segments, no trailing slash, relative to the project root when it lies inside it — and refuse a glob (`*`, `?`, `[`) and a path that climbs out of the project. Two paths are compared in that spelling and in one case, so `./src/a.ts`, `src\a.ts` and `Src/A.ts` are one path.

## Files

| File | Holds |
|---|---|
| `tasks.jsonl` | one line per task: `id`, `title`, `kind`, `owner`, `model`, `effort`, `paths`, `depends`, `state`, `attempt`, and for the current attempt `resumed`, `questions`; `env_fixed`; `awaits` (`from` queen, user or env, `question`, `answer`); `evidence` |
| `board.json` | `seats`; `reported_rows` — the decision-log rows already shown to the user; and `read` — each report a command has acted on, by name with a hash of what it held: `accept`, `ask`, `fail` and `split` record every unread report of their task |
| `reports/` | bees' reports, named `<id>-a<attempt>.md`; they stay where their bee wrote them, and one not recorded as read — or written again since — is unread |

## States

| State | Means | Moves to |
|---|---|---|
| `waiting` | a task it depends on is not `verified` | `ready` when all are; `gap` when one is a gap — rechecked after every command that changes a state; `split` by `split` |
| `ready` | can start; while a held task owns one of its paths, `show` says it waits for that task | `running` by `dispatch`; `split` by `split` |
| `running` | a bee has it and a seat | `blocked` by `ask`; `verified` by `accept`; `ready` or `gap` by `fail`, a second question, or a second broken environment; `split` by `split` once its bee has reported |
| `blocked` | waits on the queen or the user; keeps its paths, frees its seat | `running` by `resume`, once answered and a seat is free; `split` by `split` |
| `verified` | done, with the report and evidence | — |
| `gap` | could not be done or shown; two failed attempts, or depends on a gap | — |
| `split` | replaced by its parts; what depended on it depends on all of them | — |

## Commands and the model

The protocol is model-checked in this repo's `.claude/hypothesis/swarm-protocol/` (`model/Swarm.tla`, rules in `model/SwarmRules.tla`). Each command implements these actions; `/hypothesis --maintain` compares the two.

| Command | Model action | Notes |
|---|---|---|
| `init` | `Init` | `seats` is the number of `Workers` |
| `seats` | — | changes the constant `Workers` between steps; not a transition |
| `add` | `AddTask`, then `Promote` / `Cascade` | a shared path is allowed and printed, as the model's t1 and t2 share one; it is refused at `dispatch` |
| `dispatch` | `Start` | `Free(w)` is fewer `running` tasks than seats; refuses a task not `ready`, and one whose path a held task owns (`PathsFree`), naming the task it waits for |
| `ask queen`, `ask user` | `Take` on `blockedLead` / `blockedUser`, and `Ask` for the user — the program prints the question for the queen to put to the user; a second question in one attempt: `Take` → `FailAttempt` | `questions` is the model's `blocks` |
| `ask env` | `Take` on `envFail`; with `env_fixed`, `FailAttempt` | `env_fixed` lasts across attempts, as `envFixed` does |
| `answer` | `Answer` (user); the deciding half of `AnswerLead` (queen, env) | one answer per question |
| `resume` | `ResumeAfterUser`; `AnswerLead`, which sets `env_fixed` for env | prints only the answer — the one thing the bee is sent |
| `accept` | `Take` on `ev`, `Verify`, then `Promote` / `Cascade` | `reported` lives only inside the command; refused without an unread report file (R1) |
| `fail` | with a report of the task: `Take` on `noev`, `Retry`; without one: `Take` on `none` — `ResumeWorker` the first time (`resumed`), `FailAttempt` the second | |
| `show` | reads only; what `Compact` recovers from; `MarkPathWait` | `can start` lists `Startable` tasks, longest chain behind first (R12); a `ready` task's `waits for` is `Holder(t)`, worked out each time rather than stored, so it is never stale |
| `split` | not in the model | the model treats the parts as `AddTask`; the original's retirement and the rewired dependencies are not modelled. It takes a task not yet ended — `ready`, `waiting`, `blocked`, or `running` once its bee has left an unread report — so a task too big for one bee is split from that report, never retried whole; its reports are recorded as read and its attempt ends there |
| — | `QueenWait` | the queen waits only when seats are full or `can start` is empty |
| — | `StartJob`, `JobDone`, `Report`, `Vanish` | the bee's own steps; the program never acts for a bee |
