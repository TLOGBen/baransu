# maintain — keeping each area in step (`--maintain [area]`)

Moved from the drift pass in `prove-it/references/formal.md` and owned here. The work list comes from the status script, not from memory.

## Work list

(unimplemented) — `hypothesis-status.py --all --json` (or `--area <area>`); every area whose state is `stale`, `draft`, or `legacy` is on the list; `proved` / `disproved` / `unformalized` areas are untouched. The `why` field is the starting set of changes: `changed`, `missing`, `new-writer`, `writer-gone`, `artifact-edited`.

## Read every change

(unimplemented) — For code: `git diff <sync.commit> -- <covered files>` plus the working tree, plus every `new-writer` file whole, plus renames and moves of covered functions (a `missing` file is searched for by its cited symbols). For documents: diff the `/read` Markdown of the old and new versions.

## Four outcomes

(unimplemented) — Per change, judged against the model, not the commit message:
- `no-effect` — nothing the model describes changed; rerun the check and the existing variants unchanged; publish with new hashes.
- `model-update` — the model no longer describes the source; update the model from the source, re-derive the variants, rerun both evidence gates.
- `promise-changed` — evidence (doc comment, test, changelog, commit message, document revision) says the promise changed on purpose; rewrite the rule citing it; old and new wording in `history`.
- `bug-candidate` — no such evidence and the check now fails: a new path, `finding: bug`.

## Run twice

(unimplemented) — Run the check once as it is before changing anything, once after; record both in `check.log`. `model-update` and `bug-candidate` can both hold.

## Publish or block

(unimplemented) — Publish per `artifact.md` § Writing, which moves the sync point. A change that cannot be sorted (source unreadable, tool missing) ends the area as `blocked` in the report: nothing is published, so readers keep seeing `stale` — never a moved sync point without a check.

## Migration

(unimplemented) — One area lives in exactly one place at any moment. While `.claude/prove-it/formal/<area>/` exists, `/hypothesis` refuses to write `.claude/hypothesis/<area>/` and asks for the move first. The move, proposed to the user once: `git mv` the whole dir to `.claude/hypothesis/<area>/` (model files into `model/`), build `hypothesis.json` from its README (sync commit, coverage, property, bounds) with `seen_succeeding` and `unformalized` left empty, record `migrated_from`, and publish. The script then shows it as `draft`, why `no-evidence` — 「嚴格檢查未完成」 — until the next `--maintain` run on it completes both evidence gates and the reason records. A move stopped before publish leaves a dir without `hypothesis.json`: `draft`, never `legacy` and never passing.

## Never

(unimplemented) — Edit product code; edit a rule to make a failure pass; move a sync point without a published check.
