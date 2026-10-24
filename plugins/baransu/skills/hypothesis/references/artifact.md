# artifact — what one hypothesis is on disk

The writer's contract for `.claude/hypothesis/<area>/`. Readers do not read this file; they read `reading.md`.

## Layout

A fixed tree; nothing else is written in an area:

```
.claude/hypothesis/<area>/
  hypothesis.json        # the publish record: coverage, sync point, rules, verdicts, evidence. Written last.
  README.md              # the human page, from templates/README.md
  diagrams.html          # the index page of the diagram series, from templates/diagrams.html
  diagrams/              # the figures /baransu:draw drew (--out here), with its docs/
  model/                 # <Name>.tla + one .cfg per check, check.sh/check.ps1 running them all; or the code-level harness
  variants/              # the broken variants that made each check fail (kept in git)
  paths/                 # P<n>.md — one counterexample script per numbered path
  sources/               # a frozen copy of a source that would otherwise move or change (sources.md)
  check.txt              # the raw tool output of the last published run (.txt: repos often ignore *.log)
```

No index file exists: the set of `hypothesis.json` files is the index, and `scripts/hypothesis-status.py` derives it on every read. `/ship` never archives `.claude/hypothesis/`.

## Area name

A lowercase slug in the source's own word for the part (`approval`, `refund-retry`); a comparison is `<behaviour>-vs-<rules>`. The name is stable across maintenance: renaming an area is a new area plus the removal of the old one, never an edit. In user-facing text, say 「假說 approval」, not 「區塊」.

## hypothesis.json

Schema `baransu.hypothesis/1`, field by field, in `templates/hypothesis.json.md`. What each part is for: `sync` decides freshness; `check` decides whether a verdict may be shown; `rules`, `goals` and `paths` are what readers quote; `unformalized` and `questions` are what readers list.

## Sync point

- `sync.files` — the content hash (`sha256-lf`: SHA-256 after CRLF→LF) of every covered source at the moment the model was last confirmed to describe it. Freshness is a hash comparison against the working tree, so uncommitted edits, branch switches, rebases and files git ignores are all seen, and returning to the synced content is fresh again.
- `sync.commit` — where `--maintain` diffs from and starts looking for reasons. For the maintainer only; never a freshness test.
- For a document, `sync.files` hashes the original file a person edits; `sync.versions` records the version the document states, for display only.
- `sync.watch` — each guarded-state write pattern with the exact set of files it matched at sync. A new match is `new-writer`; a lost one is `writer-gone`.
- `sync.artifact` — the hash of every other file in the area at publish. A later mismatch is `draft`: someone edited the hypothesis by hand.

## Coverage map

`rules[].cites` and `model_map[]` tie each model part (action, variable, constant) to `path:line` (`path:line-line` for a span); a document's quoted passage goes in `model_map[].quote`, never in `cites`. `sync.files` is exactly the set of files those citations name, plus `sync.extra_files` for a covered file nothing cites directly. The README renders the same map as a table.

## Verdict values

Stored, on the writer's side only: per rule `held` | `violated`; per area `check.verdict_at_sync` = `held` (every rule held) | `violated` (any rule violated) | `unformalized` — the model's prediction. User-facing words: a rule 守住 or 被打破; an area 成立假說 (`established`), 假說未成立 (`draft`), 無法成立假說 (`unformalized`). Never 證實／推翻: proving a hypothesis is `/prove-it`'s. Reader-facing states are computed (`reading.md` § States) and never stored.

## Reason record

Five fields (`where`, `class`, `detail`, `until`, `instead`), seven classes, one row per unformalized part; schema in `templates/reason-record.md`. The same shape is used when `/hunt` declines an H1–H8 match, written into that caller's output.

## Writing (publish)

1. Write the model, the variants, the paths, `check.txt`; have `/draw` draw `diagrams/`; write `diagrams.html` and `README.md`.
2. Write `hypothesis.draft.json`: the whole record without hashes, with `base_generation` set to the generation read at the start of this run (0 for a first publish).
3. Run `python3 scripts/hypothesis-publish.py <area dir>`. It hashes every cited file, every watch match and every artifact file, then swaps the record in only if `hypothesis.json` still has `base_generation`. Exit 3 means another writer published meanwhile, or is publishing this area now: start the run again from the top. The lock is the operating system's, released when its holder exits, so a killed run never leaves one behind. Exit 2 naming files git ignores means this repo's ignore rules hide the area from every other checkout: stop and show the user the rule the script printed (`git check-ignore -v`). Git cannot re-include a file whose parent directory is ignored, so a rule ignoring `.claude/` needs replacing with `.claude/*` plus `!.claude/hypothesis/`, and a filename rule (`*.txt`) needs `!.claude/hypothesis/**`. Never edit their ignore rules yourself. A run that stops before the swap leaves the old record, whose artifact hashes no longer match: readers see `draft`.
4. Run `scripts/hypothesis-status.py --area <area>` and quote its line. It must print the state you intended; anything else (a `draft` with `no-evidence`) means a gate is missing — fix it and publish again, never edit the record by hand.

## Who may write

Only `/hypothesis`, and only inside `.claude/hypothesis/<area>/`, except a scratch copy of the source for broken variants, made under the system temp dir and removed in the same step. No product code.
