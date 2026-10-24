# artifact — what one hypothesis is on disk

The writer's contract for `.claude/hypothesis/<area>/`. Readers do not read this file; they read `reading.md`.

## Layout

(unimplemented) — Fixed tree; nothing else is written in an area:

```
.claude/hypothesis/<area>/
  hypothesis.json        # the publish record: coverage, sync point, rules, verdicts, evidence. Written last.
  README.md              # the human page in prose, from templates/README.md
  diagrams.html          # the progressive diagram set, from templates/diagrams.html
  model/                 # <Name>.tla + <Name>.cfg, or the code-level harness
  variants/              # one patch per safety rule: the broken variant that made the check fail
  paths/                 # P<n>.md — one counterexample script per numbered bug path
  check.log              # raw tool output of the last published run
```

No index file exists. The set of `hypothesis.json` files is the index; `scripts/hypothesis-status.py` derives it on every read.

## Area name

(unimplemented) — A lowercase slug in the source's own word for the part (`approval`, `refund-retry`); a comparison is `<behaviour>-vs-<rules>`. Stable across maintenance: renaming an area is a new area plus removal of the old, never an edit.

## hypothesis.json

(unimplemented) — Schema `baransu.hypothesis/1`, field by field, in `templates/hypothesis.json.md`. What each field is for: `sync` decides freshness, `check` decides whether a verdict may be shown, `rules`/`goals`/`paths` are what readers quote, `unformalized` and `questions` are what readers list.

## Sync point

(unimplemented) — Two parts with two jobs:
- `sync.commit` — where `--maintain` diffs from. For the maintainer only.
- `sync.files` — the content hash (`sha256-lf`: SHA-256 after CRLF→LF) of every covered source at the moment the model was last confirmed to describe it. For readers: freshness is a hash comparison against the working tree, so uncommitted edits, branch switches and rebases are all seen, and returning to the synced content is fresh again.
- For a document, `sync.files` hashes the original file (the one a person edits), and `sync.versions` records the version string the document states, for display only.
- `sync.watch` — each guarded-state write pattern with the exact set of tracked files it matched at sync. A new match is a `new-writer`; a lost match is `writer-gone`.
- `sync.artifact` — the hash of every other file in the area at publish time; a later mismatch is `draft`.

## Coverage map

(unimplemented) — `rules[].cites` and `model_map[]` tie each model part (action, variable, constant) to `file:line` or quote + location; `sync.files` is exactly the set of files those citations name, no more, no less. The README renders the same map as a table.

## Verdict values

(unimplemented) — Stored, writer side only: per rule `held` | `violated`; per area `verdict_at_sync` = `proved` | `disproved` | `unformalized`. Reader-facing states are computed (`reading.md` § States) and never stored.

## Reason record

(unimplemented) — Four fields, seven classes, one row per unformalized part; schema in `templates/reason-record.md`. The same record shape is used when a caller (hunt, review) declines to write a hypothesis for an H1–H8 match, written into that caller's output.

## Writing (publish)

(unimplemented) — Order: model, variants, paths, check.log, diagrams.html, README.md; then compute every hash; then write `hypothesis.json.tmp`; re-read `hypothesis.json` and compare its `generation` with the one read at the start of this run — different means another writer published meanwhile: stop, discard the tmp, report, and restart from §1; equal means `os.replace` the tmp over `hypothesis.json` with `generation + 1`. A run that stops before the replace leaves the old record whose artifact hashes no longer match: readers see `draft`.

## Who may write

(unimplemented) — Only `/hypothesis`. No product code, no file outside `.claude/hypothesis/<area>/`, except a scratch copy of the source for broken variants, created under the system temp dir and removed in the same step.
