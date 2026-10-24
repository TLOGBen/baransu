---
name: prove-it
description: "Proves claims by running the real app the way its user does: that a reported problem really fails, and that work said to be done really works. Leaves a record of this version a review can read, and builds the project's run recipe on first use. Trigger On '$baransu:prove-it', '證明它', '跑跑看', '實際跑一次', '真的修好了嗎', '證明所有順序都不會壞', 'prove it works', 'model-check this'. Not for reading-only review ($baransu:review) or tracing a root cause ($baransu:hunt)."
metadata:
  version: 1.0.0
compatibility: Designed for Claude Code; ported to Codex.
---

Arguments the user may give after `$baransu:prove-it`: `[claim | finding | change | feature] [--maintain]`.

# prove-it — what you say does not count; prove it

A claim is not a fact until a run shows it. That holds in both directions: a problem someone reports — a `$baransu:review` finding, a bug report, a suspicion — is real only when a run makes it fail; work someone says is done — a fix, a feature, "tests pass" — is done only when a run shows it working the way its user uses it. Whoever made the claim, the author, a reviewer, or the model itself, the claim is the input and the run is the verdict.

`$baransu:review` only reads and leaves the run to the author; this skill is that run. Its record is what `$baransu:review` weighs a claim against.

All user-facing output is in Traditional Chinese; keep commands, paths, identifiers, and quoted output in their original form, and explain each technical term where it first appears.

## Outcome Contract

- **Outcome**: Each claim in scope ends as proved, disproved, or unreachable on this version, shown by driving the real app along its user's path — and, for a claim about every case, by the hypothesis that covers it (`/hypothesis`) — with evidence that survives cleanup.
- **Done when**: Every claim is written as one sentence a run or a hypothesis can settle; the recipe's doctor passed before the first drive; every claim has a verdict and its evidence; nothing was weakened to reach a verdict; everything the run started is torn down and the evidence is still at its named location.
- **Evidence**: The record — commit and working-tree state, platform, every command run, and per claim the action driven, the resulting state, and the side effects captured; for an every-case claim, the hypothesis status line, the rerun command and its output, and each path replayed on the app.
- **Output**: Traditional Chinese report in the conversation; the record at `.codex/prove-it/records/<short-sha>-<slug>.md` with its evidence beside it (`$baransu:ship` archives `records/` out of Git; the recipe and feature map stay); the run recipe at `.codex/prove-it/recipe.md` and its feature map under `.codex/prove-it/features/`. Hypotheses are `$baransu:hypothesis`'s, under `.codex/hypothesis/`; this skill reads them and never writes them.
- **Automation**: ultracode=neutral, loop=assisted（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics; anything reaching outside this machine still needs the person or a standing authorization that names it）

PAUSE classification for non-interactive drivers: `references/loop-pauses.md`.

## 1. Turn each claim into one sentence a run can settle

Collect the claims in scope and write each as what a user would see:

- **A problem claim** — a finding, a bug report: the trigger and the wrong result（「按下 diff 按鈕後，『已送出』掛滿 30 秒，其間其他按鈕按不動」）. A `$baransu:review` finding already carries its trigger in its chain; use it.
- **A done claim** — a request, a commit message, a changelog line, a plan's Building section, "tests pass": the action and the right result（「按下專案按鈕會在輸入框放入 `/cmd `，不送出」）.
- **A claim about timing or order** — a pending mark that must clear, a lock, a retry, a timeout — keeps its moments（「從送出起最多 30 秒」）, because the run has to make those moments happen.
- **A claim about every case** — every order of steps, every input up to a size（「取消與重跑不論怎麼交錯，會簽清單都不會跟旗標不一致」）— is written with its scope; a run can only sample it, so it is also settled by a hypothesis (`../hypothesis/SKILL.md`), read as `../hypothesis/references/reading.md` says. When no hypothesis covers it, invoke `/hypothesis` on the claim first.
- **A claim about a number** — a speedup, a regression, a latency, which option is faster（「匯出在 6 萬列資料集上 p50 快 30%」）— keeps its unit, its data, and its load, and is driven as `references/benchmark.md` describes.

Pin the version before anything runs: the commit, and whether the working tree differs from it. A record that cannot name its version proves nothing about any version.

## 2. Have a recipe that runs this app

Use `.codex/prove-it/recipe.md`. If the repo has none, build it as `references/recipe.md` describes — launch, doctor, drive, evidence, cleanup, and a feature map, all from this repo's own commands — and prove it once on one feature before relying on it. If the repo does not build or start as it is, say so precisely and stop: a recipe written against a broken base teaches wrong steps.

## 3. Drive each claim

Run the doctor before the first drive and again after anything surprising. Run `hypothesis-status.py --files <the files the claims touch>` (`../hypothesis/references/reading.md` § One command): a claim whose files a hypothesis covers is read against it too, whatever kind of claim it is. Then, per claim:

- **Drive the user's path.** A test-only entry, an internal setter, or a mock past the production boundary proves nothing about the path a user has. A dry-run proves only what you saw it skip — files, network, refs — not what its name promises.
- **Capture the action and what it changed** — the screen, and also files written, rows stored, messages sent, exit codes, logs. A success message alone is not the stored result; read the result back from a second view.
- **A problem claim** is proved when the run reproduces the wrong result from the stated trigger, and disproved when the trigger, driven as stated, gives the right result. Record which; a finding the run disproves goes back to its author with the run, not silently dropped.
- **A timing or order claim**: make the bad order happen in the real app — slow a step, stop it midway, run two at once, wait out the limit — and check the promise after each step.
- **An every-case claim**: act on the hypothesis's state per the `/prove-it` column of `../hypothesis/references/reading.md` § State × reader. `stale` → invoke `/hypothesis --maintain <area>` at once and read again; record 「過期」 meanwhile, never a verdict. `proved` → rerun its `--check` command in a scratch dir and record the output here, never in the area. `disproved` → replay each path on the real app with forced order: map each step of `paths/P<n>.md` to the feature file whose entry point performs it, at replay time and in this record only; a step no feature file reaches gets a feature file written first, then the replay goes on. `legacy` or `draft` → its best result is 「嚴格檢查未完成」, never proved. Drive the user's path too where one exists: the hypothesis holds within its bounds, the drive proves the path it took. A hypothesis's rule 成立 or 不成立; this skill's own verdicts stay 證實／推翻／無法到達.
- **A number claim**: answer every question in `references/benchmark.md` with evidence from runs, and record the verdict, run count, range, and limiter it names.
- **Unreachable**: when the seed data or the environment cannot reach the claim, record the prerequisite (auth, platform, external state) and the route tried. Never weaken a drive until it passes, and never report one entry point as proved through another.

Any step with an effect outside this machine — sending a message, deploying, charging, publishing, writing shared data — needs the user's yes first, a standing authorization that names it (`references/loop-pauses.md`), or a test mode whose skipping you saw.

## 4. Record and report

Write the record with the version, the platform, every command, and per claim its verdict with the evidence and where it lives — under a working name outside `records/`, moved into `records/` only once it is complete, so a reader there never meets a half-written record:

- **proved** — for a done claim, it works as stated; for a problem claim, the problem is real.
- **disproved** — the run shows the opposite of the claim, with what was expected and what happened.
- **unreachable** — with the prerequisite.

A failure of the app is a finding for the user: report it, never edit product code to make it pass, and never rewrite the claim to match what happened. A gap in the recipe — the app works but the drive could not reach it — is fixed in the recipe and driven again before any verdict. Cleanup stops only what this run started, never by process name, and never removes evidence.

Close with one line:
「prove-it 完成：{P} 項證實、{D} 項推翻、{U} 項無法到達；紀錄：{record path}；版本：{short-sha}{，工作目錄有未提交改動}。」

## 5. Keep the recipe honest (`--maintain`)

The recipe and feature map rot as the app changes. Unnamed, `--maintain` turns on per `../_shared/auto-flags.md` for what the run is about to rely on: before the first drive, each feature file the claims reach whose recorded commit predates a change to the files it covers gets its part of this pass first, and the whole pass runs when the doctor fails because of the recipe itself. Under `--maintain`, follow `references/maintain.md` (a stale hypothesis is `/hypothesis --maintain`'s, not this pass's): cover every feature from source and drive every feature live once, then sort each gap as the map being out of date, the recipe unable to reach working behaviour, or the app being broken — only the first two are fixed here; the third is reported.

## Not-for boundaries

- Reading a change against what was asked, without running it → `$baransu:review`; it reads this skill's record as evidence.
- A failure whose cause is unknown → `$baransu:hunt`.
- Writing or fixing tests → implement under `../_shared/tdd.md`; this skill drives the app, it does not author the suite.
