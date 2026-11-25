---
name: swarm
description: "Runs a job with many bees and one queen: the queen keeps a board of tasks, keeps every free bee busy, and counts nothing done without evidence. Trigger On '$baransu:swarm', 'swarm 下去', '分頭做', '平行處理', '派幾隻', 'fan out'. Not for a single delegated task, two designs of one shape ($baransu:draft), or a review ($baransu:review)."
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

# swarm — many bees, one queen

This session is the queen. Bees are background agents, each doing one task. The queen keeps the board, decides, and keeps every free bee busy; she never does a bee's work. Three things make a swarm work: no two bees ever touch the same thing, no seat stays empty while there is work, and nothing counts as done until its bee has shown it.

Write to the user in the user's language.

## Outcome Contract

- **Outcome**: The job done by bees, every task ending verified or named as a gap, and one report.
- **Done when**: Every task on the board is `verified` or `gap`; the merged work went through one independent review and one check of its fixes; the decision log was audited against the transcript and read by a reviewer on another model; the report has been given.
- **Evidence**: The board `.codex/swarm/<slug>/`, kept by `scripts/board.mjs`; the bees' reports under its `reports/` — each verified task's report holding the commands its bee ran with their output — and the decision log `decisions.tsv` beside them, audited against the transcript and read by a reviewer on another model.
- **Output**: The bees' changes in the tree (uncommitted unless the user asked), the board, reports and decision log, a report to the user each time the crew changes, and the closing report in the conversation. `$baransu:ship` archives `.codex/swarm/`.
- **Automation**: ultracode=neutral, loop=assisted（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）

PAUSE classification for non-interactive drivers: `references/loop-pauses.md`.

## The board

The board is `.codex/swarm/<slug>/`, and only `node <this skill>/scripts/board.mjs <command> <board> ...` writes it: its commands are the protocol's legal moves, it refuses any other with the reason, and it records each report it has acted on as read, leaving it where its bee wrote it. The commands, the states and the model they implement are in `references/board.md`. `.codex/swarm/` belongs to the queen alone; bees leave reports. What the program prints is what the user reads: give them its output — the board after you lay it out, the change lines, the status line, each question it says to ask, and the decision rows it prints.

The board is the swarm's memory. After a compaction or in a new session, run `show`, never read the conversation: treat every `running` task with an unread report, or whose bee is no longer running, as if its bee had just ended, and show the user again every question still waiting on them.

**A task is the size one bee finishes and proves in one attempt**: one thing delivered, one set of paths, one way to check it. Anything bigger is split, and split across rather than along — each part something that can be checked on its own, never one layer of every part, because layers form a chain that only one bee at a time can work on.

**A task owns its paths** — every file it changes, and also the build output, caches, test servers and credentials it uses, and any code it measures; the program never lets two held tasks share one. Work others depend on goes first and writes down the interface they will read.

## The decision log

What the queen decides, and what each step of the run settled, goes into `.codex/swarm/<slug>/decisions.tsv`: one row per decision, six single-line columns — `ts`, `phase` (a task id, or `board`, `crew`, `start`), `decision`, `why`, `evidence`, `result`. Write each row with `node <this skill>/scripts/log.mjs <logfile> <phase> <decision> <why> <evidence> <result>`; it stamps the time, writes the header, keeps every cell on one line, and stops a spreadsheet from reading a cell as a formula. Say each row the way you would tell a teammate what you did. Evidence is a pointer — a report path, `file:line`, a commit, a screenshot — never prose. Log a fork chosen with its alternative, a task verified, a pivot or revert with what triggered it, a step waiting on the user, each crew; not every action. The log is append-only: a wrong call gets a new row that supersedes it. When a new session picks the swarm up, its first row has phase `start` and names the rows it did not write. Each `dispatch` prints the rows added since the last report as a table; put it under the status line in your message to the user.

## The crew

Each round, name the crew in one line — kind, count, model and effort, and why — and pin model and effort on every bee; `dispatch` takes both, since an unpinned bee runs on the queen's model. Use what this session actually has: the host's own agents, and Codex and Claude workers through the common suite's `delegate` when it is installed.

| Kind | Does | Pick | How many |
|---|---|---|---|
| Scout | read-only sweeps and lookups that come back as a list with locations; understanding them stays with the queen | the cheapest model that reads reliably — a Codex low tier spends the subscription rather than Claude budget | one per separate place to read |
| Worker | builds one task inside its paths | Codex for work given as a goal and its acceptance; Claude for exact procedure or structured output | one per task that can start, three to five at once |
| Guard | the independent review at the end | a model family other than the one that wrote the code | one, through `$baransu:review` |
| Measurer | benchmarks and end-to-end runs | any; it runs on a frozen tree | one at a time |
| Lint | turns a mistake seen twice — in any bee's work or the queen's — and the cause of a broken environment into a check through `$baransu:lint`; owns `.claude/lint/` | the cheapest model that writes a check reliably | one, on the crew for the whole run whenever the project keeps `.claude/lint/` |

Prepare credentials, and anything else that raises a permission prompt, once before the first bee. For work repeated over many items, send one bee first, turn what it did into the brief, then send rounds that double, and stop a round when fewer than two in three succeed.

## The loop

1. **Lay out the board.** Start from what is already in place: the roles, rules and running work the user set up before this run — a resident guard, a rule about who may touch what, bees still working — each gets its place on the board, or the reason it has none is said. Then say what done looks like, `init` the board with its seats and `add` the tasks, each after the tasks it depends on, and give the user `show`'s output and the first crew. When several bees try the same task to keep the best, say how the best is picked before they start. Start without waiting; only a step that waits for the user, as Whose call it is draws it, holds its own task.
2. **Fill every free seat.** `dispatch` the tasks the status line lists under `can start`, in its order — the longest chain behind first — the moment a seat is free, never waiting for the rest of a round.
3. **When nothing can start and a seat is free, find work** before waiting: split the largest task not yet started, send a scout to read ahead for a task still waiting on another, or prepare the checks for what is done.
4. **Wait** only when every seat is busy or nothing at all can move without an answer. The next event — a bee ending, the user answering, the user adding a task — brings the queen back.
5. **Read the report and say what it is**: `accept` with the evidence, `fail`, or `ask` — as When something goes wrong lays out — then go to step 2.
6. **When every task is `verified` or `gap`**, have a guard review the merged change, and send any claim only a run can settle to `$baransu:prove-it`. Each finding is a new task for its owner and goes through the loop; when those are done, a guard checks only those fixes, once, and whatever it still finds goes into the report instead of another round.

## What a bee gets and gives back

The brief stands alone: the task and what done looks like, the files to read first, the paths it owns, the interface it reads or writes, the repo's own rules, no commit unless the user asked, how to check its work by running the real thing — for a measurement, the exact version and the method — and where its report goes. It also says that the bee never writes the board or anything else under `.codex/swarm/`, that a change it needs outside its paths is a question for the queen, and that so is a step it must not take alone — destructive, irreversible, or held by a permission check — never worked around.

The bee's last act is its report, a new file `reports/<id>-a<attempt>.md`, saying one of: done, with the commands it ran and what they printed; done without that; a question for the queen; the environment is broken. It does not finish while a job it started is still running, and its report says so.

## Whose call it is

A swarm ends before anything ships, so nearly every decision in it can still be changed. The queen makes it — a choice of approach, design or taste, and every step inside the run: restarting a process the run started, freeing memory, retrying, reordering, splitting again — and logs it as a row in the decision log: what she chose, why, and the alternative. The user reviews those records before shipping. Only a step that cannot be undone or reaches outside the run waits for the user: deleting data the run did not make, an account, a deploy, a message to anyone. What the user meant is never the queen's call: when the user's words can be read two ways that would change different files, she asks which, and every other task keeps going. A host permission prompt is not a decision: the queen approves the step on her side; if the host still asks, she tells the user where the click is waiting, and when the same prompt keeps coming she shows the exact allow rule, never editing the user's settings herself.

## When something goes wrong

- **No evidence** — `fail`: a fresh bee takes the second attempt.
- **No report** — `fail`: the first time it says to resume the bee once to write one; the second fails the attempt. Before another bee takes the task's paths, stop anything the vanished bee left running there.
- **A question** — `ask queen` or `ask user`, then `answer` with the decision or the user's words, and `resume` sends the same bee only that answer in a free seat. A question for the queen is decided and recorded as Whose call it is lays out; one for the user is asked once, never answered on the user's behalf, and every other task keeps going. Steps waiting on the user at the same moment go out together, each with the queen's pick, the evidence for it and its risk. A second question in one attempt fails it. Work a bee was not given is never sent to it: it is a new task, `add`ed.
- **A broken environment** is not the bee's failure: `ask env`, put the fix on the board and its cause to the lint bee, then `answer` and `resume` once the fix is done; the attempt is not spent. The same task's environment breaking again fails the attempt.
- **A mistake seen twice**, in any bee's work or the queen's own, goes to the lint bee as a check, so a third bee cannot make it.
- **Too big** — half done, out of time — `split` it from its bee's report, rather than retrying it whole; a second bee on the same task falls into the same hole.

## Report

First check the decision log told the truth. Walk this session's own transcript — never another conversation — against the rows this session wrote: every row a real decision or action, every evidence pointer showing what its row claims, every fork, pivot or abandoned approach that shaped the work logged. Correct the log with rows that supersede, never by editing. Then have one bee on a model family other than the queen's read the log and the transcript and flag what the user should look at: decisions with weak or no evidence, verification claimed but not shown in the transcript, choices that look risky in hindsight, and gaps a quick read would miss.

The report: `show`'s table — each task with its state and evidence — the decision log as a table so the user can change any decision before shipping, the gaps and why, the review verdict, the cost of one end-to-end run when paid calls were made, and what waits on the user. It ends with an Attention section whose first line names the model that read the log — `reviewed by <model>` — then each flag pointing at its rows; "no flags", in the user's language, is a valid value, a missing model name is not.

## Not-for boundaries

- One bounded task for a cheaper model → delegate it; a swarm is for several bees.
- Two independent designs of one shape → `$baransu:draft`.
- Reviewing finished work → `$baransu:review`.
