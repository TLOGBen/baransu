# Feature map example

The shape of one feature file under `.codex/prove-it/features/`, for an invented terminal app `jot` that keeps short notes. The map's `README.md` holds what every file shares — baseline preconditions (a disposable data directory per run, the doctor command), driving conventions (stable handles, literal commands), proof rules (action plus resulting state; a read-back of anything stored; an unreachable path reported with its unmet precondition) — and an index linking each feature file.

---

# Add a note

Add a note lets a user save a one-line note from the terminal and see it in the list afterwards.

## Sub-features

- `add-basic` saves the text given on the command line.
- `add-empty` refuses an empty note with a message and exit code 2.
- `add-list` shows the new note at the top of `jot list`.

## How to get to it (user POV)

- Run `jot add "<text>"` in a terminal.
- Run `jot` with no arguments and type the note at the `>` prompt.

## Driving it with a terminal session

Preconditions: `jot doctor` reports the disposable data directory `JOT_HOME=/tmp/jot-$RUN_ID`, and the list is empty.

- **Add.** Run `jot add "buy milk"`. Exit code 0; stdout reads `saved 1`.
- **Read it back.** Run `jot list`. The first line is `1  buy milk`.
- **Prompt entry.** Run `jot`, type `call bank` at `>`, press Enter, then Ctrl-D. `jot list` now shows `call bank` first.
- **Empty.** Run `jot add ""`. Exit code 2; stderr reads `note is empty`; `jot list` is unchanged.
- **Proof.** Save each command with its stdout, stderr, and exit code to `evidence/add-note/`.

## Gotchas

- `saved 1` alone is not proof the note was stored; read it back with `jot list`.
- The prompt entry needs a real terminal session; piping text into `jot` takes a different path and does not prove the prompt.
