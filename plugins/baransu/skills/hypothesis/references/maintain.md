# maintain — keeping each hypothesis in step (`--maintain [area]`)

Moved from the drift pass in `prove-it/references/formal.md` and owned here. The work list comes from the status script, not from memory.

`--maintain` turns on by itself, per `../../_shared/auto-flags.md`, when the target a user or a reader names is covered by a hypothesis whose state is `stale`, `draft`, `broken` or `legacy`. Readers call it: a reader that sees `stale`, or a `draft` whose every reason is `no-evidence`, invokes `/hypothesis --maintain <area>` at once (`reading.md` § State × reader), so a hypothesis never stays stale waiting for someone to remember.

## Work list

Run `scripts/hypothesis-status.py --all --json`, or `--area <area>` when one is named. Every area whose state is `stale`, `draft`, `broken` or `legacy` is on the list (a `broken` one is rebuilt from its own files — model, variants, paths, README — and published again with `base_generation` 0, since its old record cannot be read); `established` and `unformalized` areas are left as they are. A `changed: <original>` — the original of a `sources/` copy (`sync.originals`) — is read by copying the original into `sources/` again, then sorting it like any other changed source; publishing without the fresh copy leaves the area stale. The `why` field is the starting set of changes: `changed`, `missing`, `new-writer`, `writer-gone`, `artifact-edited`, `no-evidence`.

## Read every change — what it does, and why it changed

Two readings per change, done the way two other skills do them:

- **What the source does now** — read it the way `/how` does (`../../how/SKILL.md`): the entry points, the data flow, who owns and writes the guarded state, trusting control flow over names. For code: `git diff <sync.commit> -- <covered files>` plus the working tree, every `new-writer` file whole, and renames or moves of covered functions (a `missing` file is searched for by the symbols it was cited for). Then search for every writer of each model variable again — the watch patterns are a floor, not a guarantee. For documents: diff the `/read` Markdown of the synced and the current original. This reading decides whether the model still describes the source.
- **Why it changed** — look for the reason the way `/why` does (`../../why/SKILL.md`), nearest record first: the commit messages since `sync.commit`, doc comments and tests touched by the change, the changelog, decision records, plans under `.claude/think/`, a document's revision note. This reading decides whether a promise was changed on purpose. No reason found means no evidence, never "probably intended".

## Four outcomes

Each change is sorted into exactly one, judged against the model, never against the commit message alone:

- `no-effect` — nothing the model describes changed. Rerun the check and the existing variants unchanged, have the never-happens list refuted again against the changed source (`no-effect` is the maintainer's judgement, and the refuter is the one who checks it), and publish with the new hashes.
- `model-update` — the model no longer describes the source: a step split in two, a branch added or removed, a check moved, a new path to the guarded state, a value range changed. Update the model from the source (never from what makes it pass), re-derive the variants and the never-happens list, have the list refuted again by a fresh agent, take the new `--model-hash`, and rerun all three evidence gates. A changed model file leaves the old `seen_faithful` record describing a model that no longer exists; the status script shows the area `draft` until it is redone.
- `promise-changed` — the "why" reading found evidence that the promise changed on purpose. Rewrite the rule citing that evidence; keep old and new wording in `history`.
- `bug-candidate` — no such evidence, and the check now fails. The counterexample becomes a new path, `finding: bug`.

`model-update` and `bug-candidate` can both hold for one change.

## Run twice

Run the check once on the area as it is, before changing anything, and once after; keep both outputs in `check.txt`. A pass before the update says only that the old description still holds.

## Publish or block

Publish per `artifact.md` § Writing; that is the only step that moves the sync point. A change that cannot be sorted — the source unreadable, the tool missing, or a possible promise change with no evidence — ends the area `blocked` in the report: nothing is published, so readers keep seeing `stale`. Under a non-interactive driver the missing evidence is the one Input PAUSE in `loop-pauses.md`. When a caller (`/hunt`, the green step) was waiting on this maintenance, it may close its own work and leave the questions here; the hypothesis stays `stale` until a person answers them.

## Migration

One area lives in exactly one place at any moment. While `.claude/prove-it/formal/<area>/` exists, `/hypothesis` refuses to write `.claude/hypothesis/<area>/` and offers the move first, once:

1. `git mv` the whole directory to `.claude/hypothesis/<area>/`, model files into `model/`.
2. Build `hypothesis.json` from its README (sync commit, coverage, property, bounds), with `seen_succeeding` and `unformalized` left empty, and `migrated_from` set to the old path.
3. Publish.

The status script then shows the area as `draft`, why `no-evidence` — 「嚴格檢查未完成」 — until a `--maintain` run completes the evidence gates and the reason records.

A `draft` whose every reason is `路徑 P<n> 還沒重播` needs no sorting either: hand its paths to the replay (`../SKILL.md` §5), record each verdict, and publish with history `correction` (or `model-update` when a replay 推翻 a path and the model changed).

An area published before 8.27.0 has no `check.seen_faithful` and no `model_map[].kind`: it shows as `draft`, why `no-evidence: 沒看過它像程式`, and readers hand it here at once (`reading.md` § State × reader). Sort nothing — the source did not change; add the kinds, derive the list, have it refuted, and fix every refuted item from the source. Publish with history outcome `correction` when every item stood, and `model-update` when any did not — a refuted item always changes the model, and the changed model's list is refuted again before publish. An 8.15.0 check that was never moved is `legacy` and is never usable to declare anything done either. A move stopped before publish leaves a directory without `hypothesis.json`: `draft`, never `legacy`, never passing.

## Never

Edit product code; edit a rule to make a failure pass; move a sync point without a published check.
