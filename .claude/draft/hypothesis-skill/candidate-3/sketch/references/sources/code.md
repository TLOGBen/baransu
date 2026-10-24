# source adapter — code

(unimplemented) Intent: code in any language in the current repo. Language matters only to tool choice (step 3), never to this adapter.

## Recognize

(unimplemented) A path, glob or symbol that resolves inside the repo's tracked files. A hunt case file is a seed, not a source.

## Read

(unimplemented) Open the entry point and follow control flow before searching names; map the stored state first, then who writes it (hunt's reading discipline). No snapshot: the commit is the snapshot.

## Cite

(unimplemented) `path:line` or `path:start-end` at the sync commit. Resolves when `git show <commit>:<path>` has that line range and the cited text is the step named.

## Extract

(unimplemented) A step is the code between two points where another actor can interleave: an await, a lock release, a request boundary, a queue hop, a transaction end. Two writers of one state are two actors. Atomic only where the code shows a lock, a compare-and-swap, or a transaction.

## Sync point

(unimplemented) `{ role, kind: code, covers: [paths], commit }`. `covers` lists the files the coverage map cites.

## Stale

(unimplemented) `git diff --name-only <commit>..HEAD -- <covers>` non-empty, or a dirty working tree in `covers`. Known blind spot: a new file that writes the guarded state; `--maintain` searches for it, the status script cannot.

## Mutate

(unimplemented) Per safety rule, one break at a cited place that the rule exists to catch — remove the guard, split the atomic step, reorder two writes. Recorded as a mutation record; applied only in a throwaway copy outside the working tree, or as a model variant when the tool works on a model.

## Replay

(unimplemented) For each trace step, read the cited code at the sync commit: can it take this step from that state? All yes → bug. One no → model-wrong, with the step and the reason. A replay in the running app is `/prove-it`'s, not this skill's.

## Findings vocabulary

(unimplemented) `Bug N`: the steps in the code's words with `path:line` each, and the harm in one sentence (the 劇本).

## Diff since sync

(unimplemented) The diff of `covers` since the commit, plus renamed or moved covered functions, plus a search for new writers of every state in the claim sheet.
