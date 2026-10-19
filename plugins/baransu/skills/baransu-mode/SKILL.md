---
name: baransu-mode
description: "Works in the user's baransu style: matches the task to one of its playbooks and runs each step by invoking that step's baransu skill, never by imitating it, then reconciles every step against what its skill left behind. Trigger On '/baransu-mode', '照我的方式做', '照流程跑', '串起來跑'. Not for one skill you already know to call (call it), or deciding whether to build at all (/think)."
argument-hint: "[task | 繼續 | ledger slug]"
disable-model-invocation: true
---

# baransu-mode — run the playbook through the skills

Each baransu skill exists to counter one inertia of the model: `/think` the rush to answer before agreeing on the question, `/review` the author grading their own work, `/draft` the first shape that came to mind, `/hunt` the guess that skips the evidence, `/prove-it` the claim nobody ran. Those counters exist only while the skill's own SKILL.md is loaded. This mode keeps them loaded by running every step through its skill, in the order a playbook fixes.

All user-facing output is in Traditional Chinese; keep skill names, paths, and technical terms in English, and explain a term where it first appears.

## Outcome Contract

- **Outcome**: The task carried through its playbook, every step run by invoking its skill or marked skipped by the playbook's own rule, and every stop being one this file or the step's own skill names.
- **Done when**: The playbook was matched and its steps copied into the task list; every step that ran shows its Skill invocation and the artifact its skill defines; every skipped step quotes the grounding fact that makes its bracket false; any version-control step ran through `/ship`; the reconciliation table was shown.
- **Evidence**: The ledger (`references/ledger.md`) — per step the skill invoked, its artifact path, HEAD, and working-tree hash — and `scripts/audit-run.py` run over this session's transcript.
- **Output**: Traditional Chinese conversation; the ledger at `.claude/baransu-mode/<slug>.md` (`/ship` archives that directory).
- **Automation**: ultracode=neutral, loop=not-drivable（it holds the authorization and the stops itself; a second driver wrapped around it would hold them twice）
- **Telemetry**: on invocation, append one selection record per `../_shared/selection-telemetry.md`; a playbook found wrong mid-run is a `"miss": true` record.

## Running a step

- **A step runs only by invoking its skill.** Call the Skill tool with `baransu:<skill>`, passing the task, the grounding, and the previous step's artifact path. The SKILL.md that call loads governs the step until its own end. Reading a SKILL.md and doing what it says in this session is not running the step: record that step 未執行, never 完成.
- **Build is the one step that is not a skill.** It is implemented in this session under `../_shared/tdd.md`, and its evidence is the red → green run output, quoted.
- **Version control runs only through `/ship`.** Commit, push, merge, branch removal, and archiving `.claude/` working directories happen only by invoking `baransu:ship`, whatever the authorization sentence says. This mode never runs a git command that writes.
- **A skill only the user can invoke** (`/show-me`, `/what-now`) is suggested to the user, never imitated.
- **Own every step's result.** A step's "done" is a claim. Read its artifact before the next step starts, and start the next step from what the artifact shows.

## Playbooks

Match the task to one playbook and open it:

- **Bug** — something fails: `references/playbooks/bug.md`.
- **Feature** — new or changed behaviour, direction settled: `references/playbooks/feature.md`.
- **Skill change** — a SKILL.md, an agent prompt, an instruction or rules file: `references/playbooks/skill-change.md`.

Copy the playbook's steps into the task list verbatim, before any task-specific item.

- **Only a bracketed step may be skipped,** and only when the grounding shows its condition false; the skip quotes that fact（「改動只動 `src/a.ts` 一個檔案」）. An unbracketed step is never skipped, and no principle — laziness, size, speed — overrides that. A skipped step stays in the list as `skip: <the quoted fact>`.
- **No playbook fits.** Invoke `/think` with the task; its plan names the steps. If the user is not there to deliberate, stop and show the closest playbook with each difference marked, for the user's yes. Never change a playbook's steps on your own judgment.
- **A step cannot run as written** — its tool is missing, its skill is user-only, one of its rules blocks the chain. Stop, name the step and the clause, and say what is needed. Never emulate it, never skip it silently; a fix goes to that skill in its own change.

## Stops and authorization

- **A step's stops are its own.** Each step stops where its SKILL.md and its `references/loop-pauses.md` say; this mode passes only what those tables mark defaultable and never declares a step's stop void.
- **`/think` runs with the user, and the run waits after it.** Its restatement cannot be defaulted, and its turn ends at the plan; the run continues only on the user's go.
- **The authorization sentence** is recorded verbatim in the ledger and names the endpoint（「跑到 review」「跑到 ship main」）. Inside the endpoint it covers moving from step to step. It never covers a push to a branch it does not name, an effect outside this machine it does not name, or a choice that is the user's.
- **Review rounds.** A review finding is fixed in this session under `../_shared/tdd.md`, then reviewed again by invoking `/review`; the same finding twice, or two fix rounds without a clean verdict, stops the run as blocked.
- **Stop only for:** (a) a choice that is the user's; (b) a blocked review; (c) a result that overturns the playbook — changing it needs the user's yes; (d) an authorization point the sentence does not name; (e) a step that reports no progress; (f) a step that cannot run as written. Record the stop in the ledger and say in one sentence what is needed.

## Subagents

The session that receives `/baransu-mode` runs the playbook and never hands it to a subagent. A subagent spawned inside a step is briefed with this file's path and that step's SKILL.md path and reads both before any work; agents a step's skill dispatches itself — review's reviewer, draft's designers — keep that skill's own brief.

## Principles

The bedrock is the set of statements `/review` judges by, in `../review/references/principles/`: the work aims at what it will be judged on. In the reply, name each principle that shaped a decision and the choice it changed; cite only principles whose file was read this run. Beside them, `../../rules/anti-patterns.md` applies to every step.

## Resume

`/baransu-mode` with no task, 「繼續」, or a ledger slug: open the named ledger, or the newest open one. Compare HEAD and the hash of `git status --porcelain` with the last finished step's; if either differs, say 「工作樹自 {step} 後已變」 and rerun the most recent verification before going on.

## Report

Close with the reconciliation table — one row per playbook step: the skill invoked (or 未執行／skip with its fact), the artifact path, and the verdict — then run `python3 "${CLAUDE_PLUGIN_ROOT}/skills/baransu-mode/scripts/audit-run.py" --ledger <ledger path>` and paste its output. A step the audit cannot find an invocation for is reported as 未執行, whatever the ledger says. End with:
「baransu-mode：{完成|停在 {step}|卡住}，{n}/{m} 步經 skill 執行；帳本：{ledger path}」

## Not-for boundaries

- One skill you already know to call → call it; this mode adds nothing to one known step.
- Whether to build at all, or which direction → `/think`.
- Changing how a step works → that skill's own SKILL.md; this mode never restates a step's rules.
