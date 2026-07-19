# Decision Log — p1-f/lead

## [1784429314] p1-f/lead
- Situation: Item A design — where to put the `&` self-check across the five rule-engine entry points.
- Options: (1) patch only `extract_within` (minimum for the bug); (2) a shared `matches_within(scope, alt)` helper used by the two `*_within` fns + inline `&`-branches in the three doc-level fns; (3) one fully generic resolver for all five.
- Decision: Option 2.
- Why: A5 requires `select_within` fixed too, and A7 (bonus) is cheap once the pattern exists. A fully generic resolver would force doc-level fns through `root_element().select()`, which unlike `Html::select` excludes the root itself — a silent behavior change for selectors that match the root (e.g. `html`). Inline branches keep the non-`&` path byte-identical.
- Spec-gap: what `&` means at document level — brief A7 says "document root element"; used `Html::root_element()`.

## [1784429314] p1-f/lead
- Situation: Item A test A3 first failed: replacement `"Ch$1: "` lost its trailing space.
- Options: (1) change `parse_rule` to stop trimming pieces; (2) adjust the test to a non-space-terminal replacement.
- Decision: Option 2, with a NOTE comment in the test.
- Why: piece-level trim is pre-existing parse behavior shared by all rules; changing it is out of scope and risks breaking sources in the wild that rely on `a || b` spacing. Not part of A3's criterion.
- Spec-gap: none (A3 only requires the replace to apply to the self-extracted value).

## [1784429314] p1-f/lead
- Situation: Item B — how the migrated progress idx reaches the DB without breaking single-transaction atomicity (B5) and without touching existing dao tests (global constraint 3).
- Options: (1) post-tx second `save_progress` write; (2) change `update_book_source_tx` signature to take `progress_idx: Option<i64>` and update all existing test call sites; (3) keep the old 4-arg dao fn byte-identical, add `update_book_source_tx_with_progress` (validates idx ∈ new TOC), both delegating to the inner fn which gains `progress_idx: Option<i64>`; facade `switch_source_tx` gains `Option<i64>` and dispatches to whichever dao fn applies.
- Decision: Option 3.
- Why: (1) breaks atomicity — a failed second write leaves progress inconsistent, violating B5. (2) textually modifies five existing dao tests without supersession. (3) keeps every existing test untouched, keeps the progress write inside the same tx (step 4), and keeps both dao fns production-used (no new dead_code warning). Facade dispatch is the sole caller-visible change; its only caller is `switch_source_core::RealDeps`.
- Spec-gap: none.

## [1784429314] p1-f/lead
- Situation: Item B step 1 — what to do when `get_progress` / `list_chapters` (old TOC) return `Err` (DB read failure), which the algorithm doesn't cover (it only covers "no progress row / unresolvable name").
- Options: (1) propagate the error and abort the switch; (2) treat read errors as "unresolvable" → reset fallback.
- Decision: Option 2 (`.ok().flatten()`), with an explanatory comment at the call site.
- Why: migration is best-effort by spec; a broken progress read must not abort an otherwise valid switch — aborting would ADD a sixth failure class, which B5 forbids ("five pre-tx abort classes untouched"). Deliberate deviation from the "never silently swallow errors" house style, scoped to these two reads and documented in code.
- Spec-gap: DB read errors during old-name resolution; chose degrade-to-reset.

## [1784429314] p1-f/lead
- Situation: Item B — extending `FakeDeps` with progress/old-TOC fixtures forces the two existing REQ-005 S2/S3 tests' struct literals to be updated (missing-field compile error).
- Options: (1) separate second fake type; (2) add `FakeDeps::new()` baseline ctor and convert existing literals to functional-update syntax (`..FakeDeps::new()`).
- Decision: Option 2.
- Why: purely mechanical adaptation — no assertion in S2/S3 changed; a parallel fake type would duplicate the trait impl for no behavioral gain. Logged under B5's "adapted only if superseded" rule as a compile-necessity adaptation, not an assertion change.
- Spec-gap: none.

## [1784429314] p1-f/lead
- Situation: Baseline `cargo build` shows THREE dead-code warnings (`filename`, `select_within`, `chapter_count`), but the brief says two are expected.
- Options: (1) leave 3 (I add none, criterion literally satisfied); (2) consume `chapter_count` in the CLI switch-source messages (「共 N 章」), dropping the count to exactly the 2 named in CLAUDE.md.
- Decision: Option 2.
- Why: `SwitchOutcome.chapter_count` was constructed but never read at baseline; B6 rework of the CLI messages touches those lines anyway, and surfacing the chapter count is user-useful. Result matches the brief's "2 expected" statement exactly (`filename`, `select_within` — both protected by CLAUDE.md).
- Spec-gap: brief's warning count didn't match the observed baseline; reconciled toward the documented pair.

## [1784429314] p1-f/lead
- Situation: Item B — precedence semantics of rules a/b/c: per-chapter first-rule-wins vs per-rule whole-TOC scan.
- Options: (1) single pass, first chapter matching ANY rule wins; (2) three passes — all of the TOC under rule a, then b, then c.
- Decision: Option 2.
- Why: the brief says "the first chapter satisfying the HIGHEST-precedence rule wins" — a later exact match must beat an earlier number-token match, which only the per-rule scan guarantees. Pinned by test `b_precedence_a_over_b_over_c`.
- Spec-gap: none (wording ambiguity resolved toward precedence-dominant; logged because the one-pass reading exists).

## [1784429314] p1-f/lead
- Situation: Item C — where to fold: inside `assemble_rows` (criterion offers both) or as a post-pass.
- Options: (1) extend `assemble_rows`; (2) pure `fold_rows()` post-pass composed in `do_search`.
- Decision: Option 2.
- Why: folding inside `assemble_rows` would collapse the three same-book rows of existing test `req003_scenario1` (3 sources × 超維術士) and force superseding three passing tests; the post-pass leaves assemble_rows' contract and tests intact and is independently unit-testable. Display text moved to pure `row_label()` so C1's label requirements are directly assertable.
- Spec-gap: duplicate hits from the SAME source — brief only discusses cross-source duplicates. Chose: they fold too (key is name+author only); source count = number of folded hits, names listed in encounter order.

## [1784429314] p1-f/lead
- Situation: Item C — one existing test (`req003_scenario1`) stopped compiling: exhaustive match over `HitOrStatus` gained a `Folded` variant.
- Options: (1) wildcard `_ => panic!` arm; (2) `other => panic!(..., row_label(other))`.
- Decision: Option 2, with a comment marking it as mechanical adaptation.
- Why: compile necessity, zero assertion change (every row must still be `Hit`); `row_label` keeps the panic message informative.
- Spec-gap: none.

## [1784429314] p1-f/lead
- Situation: Test strategy overall (B7/C6 and the brief's "tests must pin behavior" rule).
- Options: pure-logic unit tests only vs adding integration layers.
- Decision: Three tiers, all offline: (a) pure helpers (`find_migration_target`, `fold_rows`, `row_label`, rule-DSL fns) with named-value assertions incl. non-dense idx (第3章 @ idx 7, migrate to idx 9 ≠ N-1); (b) use-case level via extended `FakeDeps`, asserting the exact `progress_idx` argument passed to the tx (pins single-tx atomicity at the seam); (c) dao level INT-5/INT-5b on in-memory SQLite for the new `_with_progress` path (migrated idx written, out-of-TOC idx rejected without touching the DB). C4 pinned via `handle_event(Enter)` on a seeded Results state with in-memory ctx, asserting the first source's URL surfaces in the resulting status line.
- Why: follows house style (`SwitchSourceDeps` fake / dao in-memory / assemble_rows pure tests); every criterion has at least one test that fails if the feature is reverted.
- Spec-gap: none.
