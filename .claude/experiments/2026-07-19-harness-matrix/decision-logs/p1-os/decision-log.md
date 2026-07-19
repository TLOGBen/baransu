# Decision Log — p1-os

## [1752900000] p1-os/lead — delegation mechanism
- Situation: Brief says delegate implementation coding to sonnet subagents via the Agent tool (opus lead + sonnet workers). No Agent/Task spawn tool is actually present in this environment — only agent-team SendMessage (needs pre-existing teammates) and worktree tools are available.
- Options: (a) attempt to fabricate a spawn path; (b) implement all three items directly as lead, keeping the opus-plans/reviews discipline internally.
- Decision: Implement directly. Items A/B/C are well-scoped and file-disjoint; I hold the full design in context and self-review each item + run the authoritative cargo test at integration.
- Why: The deliverable is the three items green + committed; delegation is a means, not an end. Absent the spawn tool, direct execution is the only path that ships.
- Spec-gap: The dispatch prompt assumes a spawn tool the harness did not expose.

## [1752900600] p1-os/lead — Item A design
- Situation: `&` self-selector errored because `Selector::parse("&")` ran before the self-check in extract_within; select_within/doc-level fns had no self-path at all.
- Options: (a) special-case only extract_within; (b) guard the parse in every extraction entry point uniformly.
- Decision: Guard `Selector::parse` behind `alt.selector == "&"` in all five entry points; extract_within/select_within → current element, extract_doc/select_nodes/extract_all_doc → document root_element (A7 bonus).
- Why: Uniform semantics; A1-A5 need within/element, A7 needs doc-root; skipping parse is the minimal correct fix. accessor/regex/fallback fall out for free since parse_alt already handled `&`, `&@x`, `&##..##..`.
- Spec-gap: Brief didn't specify what `&@attr` on the doc root returns (root <html> has no such attr) — treated as empty→fallthrough, tests assert root text instead.

## [1752900700] p1-os/lead — Item B design
- Situation: switch_source_tx always reset progress to new first idx; needed best-effort migration by name, atomic, both UI paths.
- Options for match order: (a) single ascending scan checking a→b→c per chapter; (b) rule-major — whole-TOC pass per rule, (a) before (b) before (c).
- Decision: rule-major (b). Pure `migrate_progress(old_toc, old_idx, new_toc) -> SwitchOutcome{Migrated|Reset}` in switch_source_core; target idx flows into the DAO tx via a new `target_idx` param (single transaction preserved). Old-side reads (progress + old toc) are best-effort: a read Err degrades to Reset, never a sixth abort class.
- Why: Only rule-major makes precedence observable (an earlier weak (c) match must not preempt a later exact (a) match — pinned by b1 decoy test). Idx is sparse so both resolve and target use `.index`, never vec position.
- Spec-gap: Brief left the SwitchOutcome shape and the DAO plumbing open. Chose a Migrated|Reset enum (dropped the unused `chapter_count` field, which also cleared a live dead-code warning). Existing dao int1/int2/int3/int4 + empty-chapters tests adapted to pass `target_idx = new first idx` — mechanical signature update that PRESERVES their reset-behavior assertions (allowed: their old behavior is the Reset path, not superseded).

## [1752900800] p1-os/lead — Item C design
- Situation: cross-source search showed one row per source per book; needed folding with first-occurrence position, status lines untouched.
- Options: (a) change SearchState::Results to a new DisplayRow type; (b) add a `HitOrStatus::Folded` variant + pure `fold_rows` post-pass over the existing enum.
- Decision: (b). `fold_rows(assemble_rows(..))`; every book becomes a `Folded` (len-1 renders identically to the old Hit line), keyed on trimmed (name, author-or-empty); StatusLine passes through in place.
- Why: Additive variant keeps assemble_rows + all existing search tests valid (no supersede needed); a single global HashMap pass gives first-occurrence position (C3), encounter-order sources (C4), preserved status positions (C5).
- Spec-gap: Display format is "format free" per C1 — chose `name / author [src]` for singletons (matches old look) and `name - author [N源: A, B, C]` for folds. One pre-existing scenario1 test's match got an added Folded arm (unreachable — assemble_rows never yields Folded); assertion unchanged.
