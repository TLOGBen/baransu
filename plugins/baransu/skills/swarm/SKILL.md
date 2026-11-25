---
name: swarm
description: "Runs a job with many bees and one queen: the queen keeps a board of tasks, keeps every free bee busy, and counts nothing done without evidence. Trigger On '/swarm', 'swarm 下去', '分頭做', '平行處理', '派幾隻', 'fan out'. Not for a single delegated task, two designs of one shape (/draft), or a review (/review)."
argument-hint: "<goal>"
user-invocable: true
---

# swarm — many bees, one queen

This session is the queen. Bees are background agents, each doing one task. The queen keeps the board, decides, and keeps every free bee busy; she never does a bee's work. Three things make a swarm work: no two bees ever touch the same thing, no seat stays empty while there is work, and nothing counts as done until its bee has shown it.

Write to the user in the user's language.

## Outcome Contract

- **Outcome**: The job done by bees, every task ending verified or named as a gap, and one report.
- **Done when**: Every task on the board is `verified` or `gap`; the merged work went through one independent review and one check of its fixes; the report has been given.
- **Evidence**: The board `.claude/swarm/<slug>/tasks.jsonl` and the bees' reports under `.claude/swarm/<slug>/reports/`, each verified task's report holding the commands its bee ran with their output.
- **Output**: The bees' changes in the tree (uncommitted unless the user asked), the board and reports, and the report in the conversation. `/ship` archives `.claude/swarm/`.
- **Automation**: ultracode=neutral, loop=assisted（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）

PAUSE classification for non-interactive drivers: `references/loop-pauses.md`.

## The board

The board is `.claude/swarm/<slug>/tasks.jsonl`, one line per task: id, title, kind, owner, paths, depends on, waits for, state, attempt, and for the current attempt whether its bee was already resumed once and how many questions it has asked, whether the task's environment was already fixed, what it awaits — the queen or the user, with the question, and whether the user has been shown it — the decisions the queen took for it, and evidence. `.claude/swarm/` belongs to the queen alone: she writes the board, bees leave reports, and she moves the board from them.

The board is the swarm's memory. Every report the queen has read moves from `reports/` to `reports/read/`, so a file still in `reports/` is one she has not acted on. After a compaction or in a new session, read the board and `reports/`, never the conversation; treat every `running` task with an unread report, or whose bee is no longer running, as if its bee had just ended; and show the user again every question still awaiting them.

**A task is the size one bee finishes and proves in one attempt**: one thing delivered, one set of paths, one way to check it. Anything bigger is split, and split across rather than along — each part something that can be checked on its own, never one layer of every part, because layers form a chain that only one bee at a time can work on. A split task is replaced by its parts, and whatever depended on it now depends on all of them.

**A task owns its paths** — every file it changes, and also the build output, caches, test servers and credentials it uses, and any code it measures. No path belongs to two tasks at once. Work others depend on goes first and writes down the interface they will read, and dependencies never form a cycle.

| State | Means | Moves to |
|---|---|---|
| `waiting` | a task it depends on is not `verified` | `ready` when all are; `gap` when one is a gap |
| `ready` | can start; when a held task owns one of its paths, `waits for` names that task | `running` when a bee takes it |
| `running` | a bee has it and a seat | `blocked` or `reported`; `ready` or `gap` when the attempt fails outright |
| `blocked` | waits on the queen or the user; keeps its paths, frees its seat | `running` when answered and a seat is free |
| `reported` | the bee's report is in | `verified` with evidence; `ready` again without; `gap` after the second attempt |
| `verified` | done, with evidence | — |
| `gap` | could not be done or shown | — |

After every change, show the user one line counted from the board: verified, running, blocked (and how many wait on the user), gaps.

## The crew

Each round, name the crew in one line — kind, count, model and effort, and why — and pin model and effort on every bee; an unpinned bee runs on the queen's model. Use what this session actually has: the host's own agents, and Codex and Claude workers through the common suite's `delegate` when it is installed.

| Kind | Does | Pick | How many |
|---|---|---|---|
| Scout | read-only sweeps and lookups that come back as a list with locations; understanding them stays with the queen | the cheapest model that reads reliably — a Codex low tier spends the subscription rather than Claude budget | one per separate place to read |
| Worker | builds one task inside its paths | Codex for work given as a goal and its acceptance; Claude for exact procedure or structured output | one per task that can start, three to five at once |
| Guard | the independent review at the end | a model family other than the one that wrote the code | one, through `/review` |
| Measurer | benchmarks and end-to-end runs | any; it runs on a frozen tree | one at a time |
| Lint | turns a mistake seen twice — in any bee's work or the queen's — and the cause of a broken environment into a check through `/lint`; owns `.claude/lint/` | the cheapest model that writes a check reliably | one, on the crew for the whole run whenever the project keeps `.claude/lint/` |

Prepare credentials, and anything else that raises a permission prompt, once before the first bee. For work repeated over many items, send one bee first, turn what it did into the brief, then send rounds that double, and stop a round when fewer than two in three succeed.

## The loop

1. **Lay out the board.** Start from what is already in place: the roles, rules and running work the user set up before this run — a resident guard, a rule about who may touch what, bees still working — each gets its place on the board, or the reason it has none is said. Then say what done looks like, write the tasks with their dependencies, paths and sizes, and show the user the board and the first crew. When several bees try the same task to keep the best, say how the best is picked before they start. Start without waiting; only a step that waits for the user, as Whose call it is draws it, holds its own task.
2. **Fill every free seat.** Start each task that can start — `ready`, an attempt left, none of its paths held — the moment a seat is free, never waiting for the rest of a round. When more can start than there are seats, start first the one with the longest chain of tasks behind it; otherwise the run ends on one long chain with one bee working.
3. **When nothing can start and a seat is free, find work** before waiting: split the largest task not yet started, send a scout to read ahead for a task still waiting on another, or prepare the checks for what is done.
4. **Wait** only when every seat is busy or nothing at all can move without an answer. The next event — a bee ending, the user answering, the user adding a task — brings the queen back.
5. **Read the report, move the board** — the task it is about, and every `waiting` task checked again against its dependencies — then move the report to `reports/read/` and go to step 2.
6. **When every task is `verified` or `gap`**, have a guard review the merged change, and send any claim only a run can settle to `/prove-it`. Each finding is a new task for its owner and goes through the loop; when those are done, a guard checks only those fixes, once, and whatever it still finds goes into the report instead of another round.

## What a bee gets and gives back

The brief stands alone: the task and what done looks like, the files to read first, the paths it owns, the interface it reads or writes, the repo's own rules, no commit unless the user asked, how to check its work by running the real thing — for a measurement, the exact version and the method — and where its report goes. It also says that the bee never writes the board or anything else under `.claude/swarm/`, that a change it needs outside its paths is a question for the queen, and that so is a step it must not take alone — destructive, irreversible, or held by a permission check — never worked around.

The bee's last act is its report, a new file in `reports/` named for its task and attempt, saying one of: done, with the commands it ran and what they printed; done without that; a question for the queen; the environment is broken. It does not finish while a job it started is still running, and its report says so.

## Whose call it is

A swarm ends before anything ships, so nearly every decision in it can still be changed. The queen makes it — a choice of approach, design or taste, and every step inside the run: restarting a process the run started, freeing memory, retrying, reordering, splitting again — and records it in the task's line on the board: what she chose, why, and the alternative. The user reviews those records before shipping. Only a step that cannot be undone or reaches outside the run waits for the user: deleting data the run did not make, an account, a deploy, a message to anyone. A host permission prompt is not a decision: the queen approves the step on her side; if the host still asks, she tells the user where the click is waiting, and when the same prompt keeps coming she shows the exact allow rule, never editing the user's settings herself.

## When something goes wrong

- **No evidence.** The task goes back to `ready` for a second attempt by a fresh bee.
- **No report.** The bee is resumed once to write it; ending without one again is a failed attempt. Before another bee takes the task's paths, stop anything the vanished bee left running there.
- **A question for the queen** is decided and recorded as Whose call it is lays out, and the same bee is resumed in a free seat.
- **A step that waits for the user** — one that cannot be undone or reaches outside the run — is asked once and never taken on the user's behalf, and the board says what is awaited from whom; every other task keeps going, and the bee is resumed on the answer. Steps waiting at the same moment go out together, each with the queen's pick, the evidence for it and its risk.
- **A second question in one attempt** means the bee is stuck: the attempt fails and a fresh bee takes the task.
- **A broken environment** is not the bee's failure: the queen puts the fix on the board and its cause to the lint bee, then resumes the bee once the fix is done; the attempt is not spent. The same task failing on its environment again is a failed attempt.
- **A mistake seen twice**, in any bee's work or the queen's own, goes to the lint bee as a check, so a third bee cannot make it.
- **Too big** — half done, out of time — the task is split, not retried whole; a second bee on the same task falls into the same hole.
- **Two failed attempts** make the task a `gap`, and so does depending on a gap.

## Report

Each task with its state and evidence in one line, the decisions the queen took with their alternatives so the user can change any before shipping, the gaps and why, the review verdict, the cost of one end-to-end run when paid calls were made, and what waits on the user.

## Not-for boundaries

- One bounded task for a cheaper model → delegate it; a swarm is for several bees.
- Two independent designs of one shape → `/draft`.
- Reviewing finished work → `/review`.
