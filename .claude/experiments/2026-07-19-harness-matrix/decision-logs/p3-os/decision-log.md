
## [1784442888] p3-os/spec
- Situation: Task grouping for the analyze spec — dispatch names task-a/b/c by item, but analyze Stage 5 convention groups by module layer.
- Options: (1) group by layer (shared/data/service/presentation) per analyze default; (2) group by item a/b/c per the explicit dispatch.
- Decision: Group by item a/b/c. Item B legitimately spans presentation + library(dao/facade) + both handlers, breaking "one module layer per task."
- Why: The dispatch explicitly names task-a/b/c and the three items are functionally independent (A=rule.rs, B=switch-source stack, C=tui/search.rs); explicit instruction wins over the layer convention, and independence lets execute parallelize (前置群組: 無 each).
- Spec-gap: analyze's layer-grouping vs an item-oriented dispatch — resolved in favor of the dispatch.

## [1784442888] p3-os/spec
- Situation: Item B must migrate progress without breaking single-transaction atomicity; progress is written inside update_book_source_tx's one transaction (dao step 4).
- Options: (1) write progress a second time after the tx with the migrated idx; (2) resolve the target idx pre-tx via a pure helper and pass it INTO the tx as a new parameter.
- Decision: Option 2 — resolve pre-tx, pass resolved_idx into update_book_source_tx; forbid any post-tx progress write. Reset case passes new-first-idx.
- Why: A post-tx write violates B5 single-transaction atomicity; a parameter keeps the whole state change in one transaction. Old-name resolution reads (progress + old TOC) happen before the tx, preserving abort-before-tx.
- Spec-gap: brief fixes the matching algorithm but not the tx wiring; chose the atomicity-preserving signature change.

## [1784442888] p3-os/spec
- Situation: Existing dao tests int1/int4 assert reset semantics (progress == new first idx); adding resolved_idx changes the call signature.
- Options: (1) leave them and add only new tests; (2) adapt int1/int4/int2a-d/empty to pass resolved_idx explicitly, keeping asserted values.
- Decision: Adapt them to pass resolved_idx (int1->3, int4->5, same asserted values), plus a NEW test where resolved_idx(7) != new-first-idx(3) to pin migrated idx landing. Same for req005_s2/s3 gaining the new Deps methods.
- Why: The signature change is a mechanical superset; the asserted behavior for reset is unchanged, only the call site gains a parameter. This is the B5/C12 explicit supersede path.
- Spec-gap: brief allows adapting a pre-existing test only when its asserted behavior is superseded — recorded here as required.

## [1784442888] p3-os/spec
- Situation: Item A appeared as a "fresh add" but the self-check already exists at rule.rs:148, sitting after Selector::parse at :145.
- Options: (1) add another self-check; (2) reorder so Selector::parse runs only in the non-`&` branch.
- Decision: Reorder only (guard the parse inside the non-`&` branch); do not re-add the existing check. select_within has NO check -> add one there. A7 (doc-level) is BONUS.
- Why: Selector::parse("&") fails first and bails before line 148 is reached; the missing piece is ordering, not a new check. Called out precisely in a-ctx so the implementer doesn't duplicate/miss.
- Spec-gap: brief describes A as a bug but the half-applied state is only visible in source — captured in the ctx.

## [1784442888] p3-os/spec
- Situation: Item C folding — extend assemble_rows vs a post-pass helper; how to carry multi-source without breaking Enter-on-first-source.
- Options: (1) edit assemble_rows to fold inline; (2) post-pass fold_hits(rows)->rows; (3) stuff merged source names into the existing source_name String.
- Decision: Post-pass fold_hits helper; add source_names: Vec<String> to HitOrStatus::Hit and keep `hit` = first occurrence. Do not reshape Catalog PL SearchHit.
- Why: A post-pass keeps assemble_rows' 6 pure tests green (minimizes C6/C21 supersede); keeping the first hit satisfies C4/C19 (Enter acts on first source); reshaping SearchHit would break wild-JSON serde contracts.
- Spec-gap: brief says "extend assemble_rows or add a post-pass" — chose post-pass and recorded the enum field addition.

## [1784442888] p3-os/spec
- Situation: Bonus criteria (A7 doc-level `&`; B3 Arabic-vs-Chinese cross-numeral matching) risk hard-failing acceptance or forcing test.md to anchor optional work.
- Options: (1) treat all criteria as MUST; (2) mark A7 and cross-numeral as BONUS, excluded from required test anchors.
- Decision: Mark A7 (goal C7) and cross-numeral (goal C15) as BONUS; test.md anchors only MUST criteria.
- Why: The brief labels A7 "(bonus)" and states Arabic-vs-Chinese cross-matching is "NOT required; doing it is bonus." Marking them BONUS keeps the experiment DoD ("every numbered criterion met") mechanically checkable against MUST only.
- Spec-gap: none — brief is explicit; recorded the MUST/BONUS split.

## [1784442888] p3-os/spec
- Situation: Stage-6 three-subagent review replaced (per dispatch) by one self-review pass answering the three cross-layer questions.
- Options: n/a (dispatch-mandated single self-review).
- Decision: Ran Agent-1 (task↔test↔goal-criteria) as a literal C{n} checklist, Agent-2 (test↔design), Agent-3 (design↔req↔goal). Found one gap: C13 (CLI/TUI messaging) lacked an explicit E2E-table anchor with a Criteria column — added a C13 row to test.md.
- Why: The experiment DoD is "every numbered criterion met"; the goal-criteria clause is highest-value. Every other MUST C{n} had a test anchor; every REQ traced to a criterion; design error-handling covered every edge case.
- Spec-gap: none remaining after the C13 fix.

## [1784542888] p3-os/impl-a
- Situation: extract_within already had a self-check (`if alt.selector == "&"`) at the old line 148, but `Selector::parse(&alt.selector)` ran unconditionally BEFORE it, so `Selector::parse("&")` fails first (EmptySelector) and the self-check is unreachable dead code.
- Options: (1) reorder so the `&` check happens before `Selector::parse` is called, computing the selector object lazily inside the else-branch; (2) wrap `Selector::parse` in a helper that special-cases `&`.
- Decision: chose (1) — moved the `alt.selector == "&"` check to guard the `Selector::parse` call itself, so parse only runs in the non-`&` branch. Applied the same pattern to select_within (had no self-check at all), select_nodes/extract_doc/extract_all_doc (bonus doc-level `&` -> root_element()).
- Why: matches ctx.md's explicit instruction not to re-add a self-check that already exists, only reorder; minimal diff, no new warnings, no behavior change for non-`&` selectors.
- Spec-gap: none — ctx.md fully specified the reorder pattern and doc-level root_element() approach.
- Test strategy: added 8 new named-value assertions to rule.rs's existing `#[cfg(test)] mod tests` (Html::parse_fragment + ElementRef), covering self-text, self-attr, self-html/outerHtml, self+regex, both fallback orderings, missing-attr-falls-through-to-self, and select_within self len==1. Did not modify the 4 pre-existing tests. Confirmed Red (8 failures, EmptySelector panics) before implementing, then Green (12/12 rule tests, 56/56 whole-repo tests).

## review p3-os/review-a — Task a (2026-07-19T06:52:58Z)
tier: advisory; green_ok: true; 12/12 rule tests + 56/56 repo green (exit 0); red_proof credible; C1-C6 met, C7 bonus impl untested.

### green_proof (p3-os/review-a, Task a)
test_command: `LIBCLANG_PATH=/usr/lib/llvm-18/lib cargo test catalog::service::rule::tests`
exit_code: 0 (CARGO_EXIT captured separately, not via pipe)
tests_correspondence:
  C1 <- extract_within_self_text
  C2 <- extract_within_self_attr + extract_within_self_html_and_outer_html
  C3 <- extract_within_self_attr_with_regex
  C4 <- extract_within_fallback_missing_then_self + extract_within_self_first_in_fallback
  C5 <- select_within_self_returns_single_element
  C6 <- parse_basic + parse_attr_and_replace + parse_alternatives + extract_text_with_fallback (4 pre-existing) + whole-repo 56/56
  C7 (BONUS) <- implemented (root_element branch in select_nodes/extract_doc/extract_all_doc), no dedicated test
output_tail (verbatim last 16 lines):
```
running 12 tests
test catalog::service::rule::tests::extract_text_with_fallback ... ok
test catalog::service::rule::tests::extract_within_self_attr ... ok
test catalog::service::rule::tests::extract_within_self_attr_missing_falls_through_to_self_text ... ok
test catalog::service::rule::tests::extract_within_fallback_missing_then_self ... ok
test catalog::service::rule::tests::extract_within_self_first_in_fallback ... ok
test catalog::service::rule::tests::extract_within_self_html_and_outer_html ... ok
test catalog::service::rule::tests::parse_alternatives ... ok
test catalog::service::rule::tests::extract_within_self_text ... ok
test catalog::service::rule::tests::parse_attr_and_replace ... ok
test catalog::service::rule::tests::parse_basic ... ok
test catalog::service::rule::tests::select_within_self_returns_single_element ... ok
test catalog::service::rule::tests::extract_within_self_attr_with_regex ... ok

test result: ok. 12 passed; 0 failed; 0 ignored; 0 measured; 44 filtered out; finished in 0.00s

```

## [1784444121] p3-os/impl-b
- Situation: TASK-b-01 chapter-number regex CHAR-SET copy-verbatim from ctx.md includes a raw Chinese-numeral char class; needed a `regex::Regex` const built once per call (no lazy_static/once_cell in deps) for `extract_chapter_number`.
- Options: (1) `regex::Regex::new` inline per call (simple, tiny perf cost, no new dep); (2) add `once_cell`/`lazy_static` for a cached static.
- Decision: (1) — inline `Regex::new` per call.
- Why: this is a cold path (invoked once per switch-source attempt, not per-chapter-render); avoids a new Cargo dependency for a negligible perf win; `regex` crate is already a dependency.
- Spec-gap: none — ctx.md gave the exact pattern; only the "how to instantiate the regex" mechanics were unspecified.

## [1784444121] p3-os/impl-b
- Situation: TASK-b-02 requires `update_book_source_tx` to take a new trailing `resolved_idx: i64` param and write it at tx step 4, per ctx.md CRUX. This breaks the signature used by 6 existing tests (int1, int2a-d via `assert_rollback_for_step`, int3, int4, empty) plus the fault-injection variant.
- Options: (1) add a second `_with_resolved_idx` method, leave old one for back-compat; (2) change `update_book_source_tx`'s signature directly and adapt every existing call site.
- Decision: (2) — direct signature change; adapted int1 (pass 3, same assertion), int2a-d (pass 3, unaffected by fault-injection semantics), int3 (pass 0), int4 (pass 5, same assertion), empty (pass 0). Added new `c8_migrated_idx_lands_non_dense` test passing resolved_idx=7 while new-first-idx=3, asserting progress lands at 7 (not 3) — the exact non-dense-migration regression the ctx flags.
- Why: ctx.md line 95-97 explicitly authorizes this as the C12-supersede adaptation (asserted values unchanged, only the call signature gains a parameter); a parallel method would let a stale first-idx-only path linger and violate "single write path, no post-tx write" spirit.
- Spec-gap: none — ctx.md Test section literally prescribes int1->idx=3, int4->idx=5, new-test resolved_idx=7-vs-first_idx=3.

## [1784444121] p3-os/impl-b
- Situation: TASK-b-03 orchestration in `run_with_deps` needs old-state reads (`read_progress` + `read_old_toc`) added to the `SwitchSourceDeps` trait boundary, which the two pre-existing REQ-005 abort tests (req005_s2/s3) construct via a struct literal with a now-larger field set.
- Options: (1) extend the `FakeDeps` struct literal at both call sites directly (repeats old_progress:None, old_toc:vec![], tx_resolved_idx:Mutex::new(None) at every site); (2) add a `FakeDeps::minimal(...)` ctor defaulting the new REQ-002/003 fields to the reset-path defaults (no progress) and use it everywhere.
- Decision: (2) — `FakeDeps::minimal` ctor; existing req005_s2/s3 tests switched to it (asserted behavior/messages unchanged, only construction syntax changed) per the C12-supersede rule; new migrate/reset/no-progress tests set `old_progress`/`old_toc` directly on the returned struct.
- Why: keeps the two pre-existing abort tests' logic and assertions byte-identical while accommodating the larger struct; a ctor is less repetitive than a 3-field literal expansion at 4+ call sites.
- Spec-gap: ctx.md didn't specify HOW to keep old FakeDeps-based tests compiling under a larger trait — chose a minimal-ctor helper, logged here as the adaptation mechanism (not a behavior change, so not a strict C12 supersede of assertions, but the construction syntax did change).

## [1784444121] p3-os/impl-b
- Situation: TASK-b-04 ctx.md says "format_outcome pure fn (if extracted)" — optional extraction, but B6/C13 require CLI print + TUI toast to be textually consistent.
- Options: (1) duplicate the migrate/reset message string logic independently in switch_source.rs (CLI) and tui/switch_source.rs (TUI); (2) extract `format_switch_message(&SwitchOutcome) -> String` in switch_source_core.rs and call it from both handlers.
- Decision: (2) — extracted `format_switch_message`, unit-tested for both migrated/reset substrings ("進度已遷移"/"進度重置到首章"), and both handlers now call it instead of hand-rolling `format!`.
- Why: guarantees the two surfaces can't drift out of sync (the risk C13/B6 is guarding against); also gives a pure, directly-testable surface instead of only being exercisable through the full CLI/TUI stack.
- Spec-gap: none — the ctx.md phrasing "(if extracted)" already anticipated this choice as the preferred path when B6/C13 need cross-surface consistency.

## [1784444121] p3-os/impl-b — Red gate evidence
- Situation: Recording the Red-gate compile-error proofs for each of the three signature-changing sub-steps (b-01 pure helpers, b-02 dao resolved_idx, b-03 trait+FakeDeps extension, b-04 format_switch_message), since each Red state manifested as a compile error (missing fn / wrong arity) rather than a runtime assertion failure — the natural TDD red state when adding a new pure fn / new trait method that tests already reference.
- Options: n/a — recording, not a decision.
- Decision: n/a.
- Why: n/a.
- Spec-gap: none.

## [review-b] p3-os/review-b — Item B review
- Situation: Reviewing impl-b (switch-source progress migration, M task) against b-ctx.md 驗收標準 C8-C14 + REQ-002/003/004.
- Verdict: advisory. All MUST criteria met; 72/72 tests green (`LIBCLANG_PATH=/usr/lib/llvm-18/lib cargo test`, exit 0). Layer grep clean (0 hits). red_proof credible (3 compile-error red states, specific E-codes).
- AC map: C8 exact→.index=Some(7) c8_resolve_migrated_idx_exact_match_non_dense + c8_migrated_idx_lands_non_dense (dao progress==7, non-dense) + c8_migrate_path_fake_deps_records_resolved_idx; C9 whitespace c9; C10 fullwidth c10; C11 no-match None c11 + c11_reset_path; precedence c11b_precedence_exact_beats_number; C12 int1/int2a-d/int3/int4/empty + req005_s2/s3 abort-before-tx (old-state reads never run before abort); C13 c13_format migrate/reset + CLI println + TUI toast both via format_switch_message; C14 fake-deps migrate/reset/no-progress.
- Atomicity: resolved_idx computed pre-tx (core.rs:305-323), passed into single tx, written at dao step 4 (dao.rs:355), no post-tx progress write. Old-state reads precede tx. Confirmed.
- Advisory (non-blocking): (1) SwitchOutcome.chapter_count is dead code (dead_code warning at core.rs:73) — pre-existing (identical on parent 3386023), NOT introduced by this task, so "no new warnings" holds; could be surfaced or removed later. (2) migrated message shows "（第 {idx+1} 章）" where idx is the non-dense enumerate index, so the displayed 1-based position (e.g. 第8章) differs from the chapter's own name (第12章); the authoritative name is also shown so not misleading, but the parenthetical is a TOC position not a chapter number.
- No direct fix made (nothing mechanical to correct; both advisories are non-blocking design notes out of M-task correctness scope).

## [1784445050] p3-os/impl-c
- Situation: Task c (REQ-005) needs to fold cross-source search hits into one row per book, keyed by (name, author). The existing `HitOrStatus::Hit` had a singular `source_name: String` field consumed by both `assemble_rows` (producer) and `draw()` (renderer) and by one existing test (`req003_scenario1_three_sources_all_hit`) that destructures it directly.
- Options: (a) add a separate `fold_hits` post-pass over a NEW `source_names: Vec<String>` field, replacing `source_name` entirely; (b) keep `source_name` singular and add a second `folded_sources: Vec<String>` field only used when folding happens, to avoid touching the existing field/test; (c) edit `assemble_rows` itself to do the folding inline.
- Decision: Went with (a), exactly as ctx.md's Design section recommended — rename `source_name: String` to `source_names: Vec<String>` (len 1 unfolded), add pure `fold_hits(Vec<HitOrStatus>) -> Vec<HitOrStatus>` post-pass, wire `do_search` as `fold_hits(assemble_rows(per_source))`, update `draw()` to render the folded format when `source_names.len() > 1`.
- Why: (b) would leave two parallel display-name fields long-term (drift risk); (c) would entangle assemble_rows's per-source dispatch semantics with fold semantics, risking C21 (assemble_rows tests supersede) and violating the "assemble_rows stays the funnel/dispatch layer only" boundary already documented in its doc comment. (a) is the ctx.md-recommended path and keeps assemble_rows tests changed only additively (field rename in one match arm's assertion), which the brief explicitly permits under the supersede rule.
- Spec-gap: ctx.md doesn't fully specify what happens if `fold_hits` receives Hit rows whose own `source_names` already has len > 1 (e.g., composing folds); I implemented `fold_hits` to `extend()` the existing vec on repeat-key match rather than assume len==1 input, so it composes safely — decided since ctx.md text mentions this is meant to run once as a single linear scan post-assemble_rows pass, but a defensive/composable implementation costs nothing extra.
- Test strategy: pure unit tests only (no tokio, no scraper, no db) directly on `fold_hits`, covering C16 (3-source fold + count), C17 (different author stays separate), C18 (first-occurrence position ordering across two book names), C20 (StatusLine rows preserved in relative order), two edge cases (empty input; two None-author same-name rows fold), and C19 (Enter extracts first-occurrence book_url) by mirroring the exact extraction pattern used in `handle_event`'s Enter branch on `fold_hits` output. Renamed the one existing `assemble_rows` test assertion that touched the field rename (`req003_scenario1_three_sources_all_hit`), leaving all other pre-existing tests byte-for-byte unchanged, per the C21/supersede rule.

## p3-os/review-c (review) — Item C multi-source search folding

- Verdict: advisory (all MUST met, mark complete). green_ok: true.
- Ran `LIBCLANG_PATH=/usr/lib/llvm-18/lib cargo test --bin novel-looker` → 79/79 pass (exit 0); search module 15/15. Layer grep `use crate::(catalog|library)::facade` in src/{catalog,library} → 0 hits. Only the 2 pre-existing dead_code warnings; no new.
- AC→test map verified: C16←c16_..._with_all_source_names; C17←c17_same_name_different_author_stays_separate; C18←c18_folded_row_keeps_first_occurrence_position; C19←c19_enter_on_folded_row_uses_first_occurrence_book_url; C20←c20_status_lines_kept_with_relative_order_preserved; C21←existing assemble_rows(6)+Esc(2) tests intact, scenario1 additive-only supersede logged.
- red_proof credible: E0026/E0559 (source_names field) + E0425 (fold_hits fn) — genuine Rust-TDD pre-impl red.
- Design honored: pure fold_hits post-pass (linear scan, key trimmed name+author-or-empty, StatusLine never keyed/positionally stable), assemble_rows dispatch untouched, SearchHit not reshaped, first-occurrence hit kept → C19 free.
- 1 non-blocking advisory: draw() fold/single-source rendering not directly unit-asserted (TUI render); pure-helper data tests cover fold semantics per design recommendation. No direct fix needed.

## p3-os/final-review @ 2026-07-19T15:20:06+08:00
- Tree: HEAD=bb1ac2f (dirty only in .exp/ + untracked .claude/, EXPERIMENT-BRIEF.md) → ran suite myself.
- `LIBCLANG_PATH=/usr/lib/llvm-18/lib cargo test` → exit 0, 79 passed / 0 failed @ 2026-07-19T15:20:06+08:00.
- REQ-001..005 all covered by green tests; goal C1-C6,C8-C14,C16-C21 (MUST) all satisfied. C7/C15 BONUS (implemented/partial, non-blocking).
- Advisory: 2 dead_code warnings (`filename`, `chapter_count` never read) — goal narrative asks "無新警告"; not a C{n} criterion → advisory only.
- needs_fixer: false
