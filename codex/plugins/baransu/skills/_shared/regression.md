# regression — verifications a new session, or a person with no AI, can rerun

> Shared by `$baransu:hypothesis` (a model's judge kept as a check), `$baransu:prove-it` (an E2E path kept as a replay),
> `$baransu:lint` (the stamp checked before a commit and before `$baransu:wrap`) and `$baransu:health` (stale or missing checks listed).
> The runner template is `scripts/verify-run.py`; the project skill template is `regression-skill.md`.

## 1. One idea: three or nothing

A verification is a **promise** in plain words, a **judge** that runs and says yes or no, and a
**fingerprint** of the code the promise is about. A check that lacks one of the three is not
admitted: a judge with no promise is a unit test under another name, a promise with no judge is
a wish, and a judge with no fingerprint cannot say when it stopped describing the code.

The expensive part — model checking, an E2E replay — runs outside the AI, through one runner, by a
person, a schedule or CI. Everything else only reads the stamp the runner left.

## 2. Layout

```
.claude/verify/run.py                               the runner, copied from scripts/verify-run.py
.claude/verify/results/<kind>__<folder>__<id>.json  the check's stamp, a .log beside it; ignored by git
.codex/hypothesis/<area>/check.toml                 checks of a hypothesis area, tracked with the area
.codex/hypothesis/<area>/record.json                what the runner saw: synced and admitted, per check; tracked
.codex/prove-it/replays/<feature>/check.toml        E2E replays, tracked; prove-it records/ stay ignored
.claude/hypothesis/<area>/check.toml                the same, for the Claude copies
.claude/prove-it/replays/<feature>/check.toml       the same, for the Claude copies
.agents/skills/<area>-formal-verification/SKILL.md  optional project skill, one per hypothesis area
.agents/skills/verification/SKILL.md                optional project skill for the replays, one per project
```

The runner reads both trees: the Claude copies keep the same folders under `.claude/`
(`.claude/hypothesis/<area>/check.toml`, `.claude/prove-it/replays/<feature>/check.toml`), and one
runner at `.claude/verify/run.py` serves both, as `.claude/lint/` does. Each folder has a kind:
`hypothesis`, `codex-hypothesis`, `replays` or `codex-replays`. A check's full id is
`<folder name>/<id>`; when two kinds share a folder name it is `<kind>:<folder>/<id>`. A stamp's
name always carries the kind. The project root is the folder above `.claude/verify/` where
the runner sits, so every working directory and CI agree; a copy run from anywhere else takes the
nearest folder from the working directory upward holding `.claude/`, else the git top level. Its `VERSION`
constant tells a skill whether the project's copy is older than the template; an older copy is
replaced whole, never patched.

Nothing a judge produces is tracked. The runner writes a `.gitignore` holding `*` into `results/`
when it creates that folder; a skill that creates a folder for a judge's own outputs — `traces/`,
`states/`, TLC's binaries — writes the same `.gitignore` into it at that moment.

## 3. check.toml and record.json

A person writes what only a person knows in `check.toml`; the runner writes what it saw in
`record.json` beside it, and nothing else writes either half. Each `[[check]]` table is one check.

| Field | Meaning |
|---|---|
| `id` | Unique inside the file. |
| `promise` | What must hold, in words a person can judge without the code. |
| `source` | Where the promise is written: `file:line`, a doc, the user's words. A promise with no source is the model's guess. |
| `covers` | Globs from the project root: the code the promise is about; a trailing `**` means every file below. Their files, plus every file in the check's own folder except `record.json`, `results/`, `traces/`, `states/`, `__pycache__/`, `*.bin`, `*.pyc` and `*_TTrace_*`, make the fingerprint; contents are hashed with line endings made one, so a checkout's CRLF changes nothing. The covered files outside the check's own folder are also compared with the ones recorded at `sync`. Covers that match no file make the check `broken-judge`. |
| `tier` | `quick` (run before work closes; counts in `status`'s exit) or `full` (run on a schedule; listed by `status`, counted in its exit only when it failed). |
| `cwd` | Where the command runs, relative to the check's folder; default `.`. |
| `cmd` | The judge, as an argument list. Exit 0 pass, 1 broken; anything else is a judge problem. A judge exits 1 only for a broken promise and catches its own crashes as 2: the runner cannot tell an uncaught exception, which exits 1 in Python, from a broken promise. A first word `python` or `python3` runs under the runner's own interpreter, so a machine without a `python` on `PATH` still runs it. |
| `needs` | Executables that must be on `PATH`; one missing is a judge problem, not a failure. `python` and `python3` are always present, for the reason above. The runner checks, it never installs. |
| `timeout` | Seconds; past it the whole process tree is killed and the run counts as a judge problem. |
| `[check.admission]` | `fault` (what was broken on purpose), `red` (the output line that showed it red), and `runs`, how many identical runs `admit` asks for. |

`record.json` holds, per check id, `synced` — when, the `HEAD` of that moment, and the content
hash of every covered file outside the check's own folder — and `admitted` — when, the runs, that
they were identical, the slowest run's seconds. `run.py sync` writes the first, `run.py admit` the
second. A check with no `admitted` record is a **draft**: listed, never counted, never run by
`quick` or `full` unless named.

## 4. The runner and its exit codes

`python .claude/verify/run.py <subcommand> [ids…]`; an id is a full id or a folder name. The
runner needs Python 3.11 or newer (it reads `check.toml` with `tomllib`); an older one exits 2
saying so.

- `status` — computes fingerprints only, in seconds, and runs no judge. One line per check,
  `<state> <id> <seconds>s <promise>`: `ok`, `failing` (last run exit 1), `broken-judge` (last run
  exit 2, or the check cannot run), `never-run`, `draft` (not admitted), `stale` (followed by each
  covered file added, removed or changed since `synced`, else since the stamp; a file in the
  check's own folder is marked `judge`).
- `quick` / `full` — runs the admitted checks of the quick tier, or of every tier, and writes a
  stamp per check (`id, exit, seconds, when, head, fingerprint, files`) and its log; a failing
  line shows the log's tail. A run never moves `synced`: a judge that passes on covered files
  changed since `synced` still reports `stale`.
- `sync <id>…` — records the covered files as the ones the judge now describes. Run it only after
  the judge was brought in step with them (or a replay passed on them); it is the one act that
  says so.
- `admit <id>` — see §5.

Every subcommand exits **0** when every check it counts passed on the files as they are now and
those files are the ones recorded at `sync`, **1** when a judge said no, **2** when a judge or tool
is missing or stale, a check never ran, or a stamp no longer matches the code. 1 wins over 2.
`status` counts admitted quick checks, and a `full` check only when it failed: a recorded failure
never ships, and a slow tier's staleness is the schedule's to clear. What a new session does,
without reading the runner:

- **1** — the code breaks a promise. Fix the code, or show that the promise itself changed (the
  user's words, a new `source`) and bring the check in step with it. Never edit the judge to pass.
- **2** — the judge is behind. `stale` since the stamp, or `never-run`: run `quick` (or `full`) and
  read again. `stale` since `synced`: the judge describes older code and no run clears it; bring
  it in step — `$baransu:hypothesis --maintain` for a model, prove-it `--maintain` for a replay —
  and `sync` it, which nothing else does. A missing tool: install it; the runner does not.

## 5. Admission

A check is admitted only with this evidence, gathered by the skill that wrote it:

1. **Red on a planted fault.** Break the covered code on purpose — the smallest edit that breaks
   the promise, in a scratch copy or reverted after — run the judge, see it exit 1, and record
   `fault` and `red`. When the covered code is a shared or built artifact that cannot safely be
   edited, a fault in the judge's input that sends the code down a different decision path also
   counts, and `fault` says it was planted in the input. For a model judge (TLA+, Lean, a
   simulator), the model of the source is what the judge reads, so a variant of that model with the
   guarded step broken — the hypothesis's own variants and planted bugs — counts as the planted
   fault, and `fault` names the variant. A judge that stays green on its own fault guards nothing.
2. **Identical runs.** `run.py admit <id>` runs the check `runs` times (default 5; a replay at
   least 5, since a live app varies more than a model); every run must exit 0 with the same output
   once lines matching the runner's `NOISE` list — timestamps, durations, `states generated`, seed
   and pid lines — are dropped. A flaky judge is refused; make it deterministic rather than
   widening `NOISE`.
3. **Measured time.** `admit` records the slowest run. A quick check takes at most 420 s and the
   whole quick tier at most 10 minutes. Over either, cut a smaller scope — fewer processes, a
   smaller constant, one path — or move the check to `full`; never loosen the limit.

`admit` refuses a check that lacks `promise`, `source`, `covers`, `cmd`, `fault` or `red`, one
never synced, and one whose covered files changed since `synced`. On success it writes the
`admitted` record itself; a check is admitted by the runner, never by an edit.

## 6. What a model check proves

A TLA+ model guards the design, not the code. Its only link to the code is staleness: when the
covered files change and the model does not, `status` says the model may no longer describe them.
Trace validation, property checks and fault injection, which tie a model to the running code,
belong to `$baransu:health` and `$baransu:lint`, not here.

## 7. E2E replays

A replay drives the real app the way its user does and is admitted only when it can be rerun
blind:

- Compare data read back — an API response, a file, a database row, an element's text — never pixels.
- Wait for a ready signal — a health endpoint, a log line, an element present — never a fixed sleep.
- Start each run on a fresh data directory, so no run reads another's leftovers.
- Find elements by stable names — a role, a label, a test id — never by coordinates.
- Leave out every path with side effects outside the run: sending mail, paying, posting, deleting shared data.

## 8. Lint

Lint never runs a judge; a hook waits at most 120 s. Two checks call the runner's `status`, each
`run = ["python", ".claude/verify/run.py", "status"]`: `on = ["pre:commit"]` at `warn`, and
`on = ["pre:skill:wrap"]` at `error`. Any non-zero exit is a finding; the output tells 1 from 2.
The tables are in `../lint/references/format.md`. The first time a skill copies the runner into a
project, it hands these two checks to `$baransu:lint`; a runner nothing calls guards nothing.

## 9. Project skills

A project may keep a skill per hypothesis area, `.agents/skills/<area>-formal-verification/SKILL.md`,
and one for its replays, `.agents/skills/verification/SKILL.md`, both from `regression-skill.md`.
Such a skill holds only how to run the
checks, how to read the states and exit codes, what to do when one is stale, and what the checks do
not prove; for each check's promise, source and covered files it points at the `check.toml` rather
than restating them, so the two cannot drift apart.
