# formal — when a claim is a hypothesis, and what makes its check trustworthy

Moved from `prove-it/references/formal.md` (8.15.0) and extended. The single source of the trigger list: every other skill cites this file's H1–H8 and non-trigger list, never restates them.

## Triggers H1–H8

(unimplemented) — The table from the plan, verbatim in English: # / category (HAZOP guide word) / visible signal / default tool / one non-trigger example per row. H7 with no verifier for the language ends `unformalized` / `no-tool`; it never falls back to property-based testing.

## Not triggers

(unimplemented) — The six rows: a claim one run settles; a static permission check on one endpoint; look, copy, docs, config values, parameter choices; a read-only query with one reader; an area already covering the target whose state is `proved` or `disproved` (rerun it instead — decided by `hypothesis-status.py`, not by memory); a prototype the user says will be thrown away.

## Let the question choose the tool

(unimplemented) — Order in steps → TLA+/TLC (default, any language); every input of the code itself → code-level verifier (Kani, Verus, Dafny); authorization from composed policies → SMT; every size → a proof (tool decided at first request; this machine has none). Each tool is an adapter with one required output shape (§ Tool adapter output). A tool adapter is listed only after it has passed a known-answer exam on a real machine (a model with a planted bug it must catch and a fixed one it must pass); until then the row's result is `no-tool`, never a guess.

## Tool adapter output

(unimplemented) — What every adapter must yield for publish: tool + version, one pinned command, per-rule `held`/`violated`, a counterexample trace per violation mapped to model parts, states or cases explored, seconds. An adapter that cannot yield one of these is not usable for a hypothesis.

## Strict, every time

(unimplemented) — The six rules from the plan, each mapped to the field that records it, so the status script can enforce what is enforceable:
- true to source → `model_map` cites every part; names are the source's.
- seen failing → `check.seen_failing` per safety rule.
- seen succeeding → `check.seen_succeeding` per goal, with the removed transition.
- scope stated → `check.bounds`, `assumptions`, `left_out`; unbounded request → a proof.
- findings stay findings → a counterexample every step of which the source can take is a `path`; a step it cannot take is a model error fixed before publish.
- unformalized parts recorded → `unformalized[]`, `templates/reason-record.md`.

## Never weaken to pass

(unimplemented) — No rule edited, no bound narrowed, no transition removed to reach `proved`. A rule changes only under `--maintain`'s "promise changed on purpose", with the evidence cited and old and new wording kept in `history`.
