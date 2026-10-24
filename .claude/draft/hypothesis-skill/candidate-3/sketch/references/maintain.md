# maintain — keeping a hypothesis in step with its source

(unimplemented) Intent: the drift pass, source-neutral; each source adapter's § Diff since sync supplies the changes. Moves here from `prove-it/references/formal.md` § Keeping it in step.

## Which hypotheses

(unimplemented) The named area, or every area `scripts/hypothesis-status.py --all` lists as `stale` or `legacy`.

## Run as it is first

(unimplemented) Rerun every cfg or harness before touching anything; record the result as the baseline.

## Sort each change

(unimplemented) The four kinds — no effect (judged against the model, not the message); the model no longer describes the source (update from the source); the promise changed on purpose (cite the evidence, old and new wording); the promise may be broken (bug candidate).

## Rerun and move the sync point

(unimplemented) After updating: gate 1 again, gate 2 on the new source, then the check. Each hypothesis ends `in sync`, `updated`, `bug`, or `blocked` (updated and bug can both hold). Move the sync point — and, for documents, replace the snapshot — except for `blocked`.

## Moving a legacy check

(unimplemented) A directory under `.claude/prove-it/formal/<area>/`: offer the move, `git mv` on yes, convert its README to `../templates/README.md` (fields that existed carry over; missing gates leave status `draft`), and record the move in the maintenance log. Never copy: one location per area.

## Never

(unimplemented) Edit product code or the person's documents; a fix to either is theirs, in a change of its own.
