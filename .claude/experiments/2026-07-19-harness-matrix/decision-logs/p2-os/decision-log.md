# Decision Log

## [1752900000] p2-os/spec
- Situation: Item A — the `&` self-check already exists in `extract_within` but is dead code.
- Options: (1) add the self-check (already present — no-op); (2) reorder so `Selector::parse` runs only for non-`&` selectors.
- Decision: The real bug is ordering — `Selector::parse(&alt.selector)` is called *before* the `alt.selector == "&"` branch, so `&` errors out via `?` before the override runs. Fix = guard the parse behind the `!= "&"` check in every entry point that must honour `&`.
- Why: The self-check text in `extract_within` is inert precisely because parse precedes it; the fix is to never parse `"&"` as a CSS selector.
- Spec-gap: none (CLAUDE.md and brief both describe the ordering bug).

## [1752900001] p2-os/spec
- Situation: Item A7 — document-level `&` meaning ("document root element").
- Options: (a) map `&` to `Html::root_element()`; (b) leave doc-level `&` erroring (bonus, skip).
- Decision: Map `&` to `doc.root_element()` in `extract_doc` / `select_nodes` / `extract_all_doc`; same guard pattern as within-element. Treated as in-scope-optional (non-blocking for done).
- Why: `scraper::Html::root_element()` gives an `ElementRef` for the document root, so the same `read_accessor` path works with zero new machinery — the guard generalises cheaply.
- Spec-gap: brief labels A7 "(bonus)"; global DoD says "every numbered criterion met" — resolved by classifying all bonus criteria (A7, C4 picker, rule-c cross-numeral) as in-scope-optional / non-blocking, marked in goal.md.

## [1752900002] p2-os/spec
- Situation: Item B — where does the chapter-name matching helper live?
- Options: (a) `library/service` (domain); (b) `presentation/handlers/switch_source_core.rs` next to `evaluate_toc`.
- Decision: Pure helper `migrate_chapter_index` in `switch_source_core.rs`, alongside the existing pure `evaluate_toc`.
- Why: Switch-source is already a cross-context (catalog+library) use case that lives in presentation/handlers per the layer rules; `evaluate_toc` set the house-style precedent of pure helpers there. Putting it in library/service would need the new TOC pushed down a layer for no benefit.
- Spec-gap: none.

## [1752900003] p2-os/spec
- Situation: Item B — old current-chapter name resolution can fail three ways (no progress row, name not found in old TOC, DB read Err).
- Options: (a) propagate read errors via `?` (would create a NEW pre-tx abort class); (b) map every failure to `None → reset`.
- Decision: Resolve-old-name is `Option<String>`; ALL of {no progress row, chapter_index not present in old TOC, get_progress/list_chapters returned Err} collapse to `None`, which drives the reset fallback (step 4). Never abort.
- Why: B5 fixes the five abort classes as untouched and migration is explicitly "best-effort" — a DB hiccup while reading the OLD state must not block a switch that would otherwise succeed.
- Spec-gap: brief step 1 says "No progress row / unresolvable name → fallback" but does not mention read Err; classified read Err as unresolvable.

## [1752900004] p2-os/spec
- Situation: Item B — old chapter lookup must use `ChapterMeta.index == progress.chapter_index`, not positional indexing.
- Options: (a) `old_toc[progress.chapter_index]`; (b) `old_toc.iter().find(|c| c.index == progress.chapter_index)`.
- Decision: Find by matching `index` field.
- Why: CLAUDE.md invariant — `chapters.idx` is the literal enumerate() index, NOT dense 0..N-1; positional indexing would read the wrong (or out-of-bounds) chapter.
- Spec-gap: none (documented invariant).

## [1752900005] p2-os/spec
- Situation: Item B — a/b/c precedence has two defensible readings.
- Options: (1) evaluate rule-a across the whole new TOC → lowest idx; else rule-b lowest idx; else rule-c lowest idx (per-rule scan, ascending tiebreak within a level). (2) single ascending pass, first chapter satisfying ANY rule wins.
- Decision: Reading (1) — per-rule precedence, ascending-idx tiebreak inside each level.
- Why: (1) makes BOTH brief clauses load-bearing ("highest-precedence rule wins" AND "ascending"); (2) makes "highest-precedence rule wins" nearly vacuous. Since exact-eq ⊆ whitespace-eq, doing rule-a first naturally gives exact matches priority. A discriminating test (token match at low idx vs exact match at higher idx → exact wins) pins the reading so it cannot be silently coded as (2).
- Spec-gap: brief wording "the first chapter satisfying the highest-precedence rule wins" is ambiguous between per-rule and per-chapter scanning; documented divergent case is: low-idx token-only match + higher-idx exact match → reading (1) returns the exact (higher-idx) one.

## [1752900006] p2-os/spec
- Situation: Item B — `update_book_source_tx` hardcodes new progress = first chapter idx; migration needs to write a chosen idx inside the same tx.
- Options: (a) add a `target_chapter_index: i64` param threaded into tx step 4; (b) apply progress after the tx (second write).
- Decision: Add `target_chapter_index` param to `switch_source_tx` / `update_book_source_tx`; step 4 UPSERTs that value; return value becomes the migrated idx. Existing dao tests get a mechanical signature bump passing an explicit target == old first-idx behaviour, preserving their asserted values.
- Why: Option (b) breaks single-transaction atomicity (B5). A pure signature bump that preserves the asserted values does NOT invoke the B5 supersede rule.
- Spec-gap: none; B5 supersede rule NOT invoked because dao assertions are preserved (only the call gains an argument).

## [1752900007] p2-os/spec
- Situation: Item B — `SwitchOutcome` must convey migrated-vs-reset (B6).
- Options: (a) enum `Migrated{..} / Reset{..}`; (b) struct + bool flag.
- Decision: `SwitchOutcome` becomes an enum with `Migrated { new_idx, matched_name, chapter_count }` and `Reset { new_idx, first_name, chapter_count }`, plus a pure `migration_summary(&SwitchOutcome) -> String` helper unit-tested for both variants. Each handler (CLI + TUI) prepends its own 換源-success chrome around the shared summary.
- Why: Keeps handler-specific formatting in handlers (layer rule) while pinning the migrated/reset wording in one tested pure fn — B6 becomes testable at the pure-logic level (B7).
- Spec-gap: brief B6 example strings differ between CLI and TUI today; resolved by shared semantic fragment + per-handler prefix.

## [1752900008] p2-os/spec
- Situation: Item C — extend `assemble_rows` vs add a post-pass?
- Options: (a) fold inside `assemble_rows`; (b) separate pure post-pass `fold_duplicate_hits(rows) -> rows`.
- Decision: Separate post-pass; `do_search` calls `fold_duplicate_hits(assemble_rows(per_source))`.
- Why: The existing `req003_scenario1_three_sources_all_hit` test feeds three SAME name+author hits to `assemble_rows` and asserts `rows.len() == 3`. Folding inside `assemble_rows` would collapse them to 1 and break that passing test (C6 forbids without supersede). A post-pass leaves `assemble_rows` and all its tests byte-identical.
- Spec-gap: brief C6 allows "extend assemble_rows OR add a post-pass"; post-pass chosen to avoid the supersede rule.

## [1752900009] p2-os/spec
- Situation: Item C — enum shape for a folded (multi-source) row.
- Options: (a) new `HitOrStatus::FoldedHit { sources: Vec<(String, SearchHit)> }`, singles stay `Hit`; (b) make every Hit carry a Vec.
- Decision: New `FoldedHit` variant; single-source rows keep the existing `Hit` variant unchanged.
- Why: C3 requires a single-source row to render "as today" (identical). Keeping `Hit` for singletons guarantees byte-identical single rendering and does not disturb existing tests that `matches!(.., HitOrStatus::Hit { .. })`. `FoldedHit.sources[0]` is the primary for Enter (C4).
- Spec-gap: none.

## [1752900010] p2-os/spec
- Situation: Test strategy for all three items.
- Options: heavy E2E (network/DB) vs pure-helper unit tests at the seams.
- Decision: Drive every criterion through pure helpers — rule.rs `extract_*`/`select_*` (Item A), `switch_source_core` pure `migrate_chapter_index` + `migration_summary` + `SwitchSourceDeps` fake + dao in-memory (Item B), `fold_duplicate_hits` (Item C). No network tests (brief: tests are offline).
- Why: The codebase already exposes these seams (assemble_rows, evaluate_toc, SwitchSourceDeps fake, open_in_memory) as the house testing style; pinning named values there satisfies the scored test-effectiveness constraint.
- Spec-gap: none.

## [1784437200] p2-os/impl
- Situation: Item B — `SwitchOutcome::Migrated`'s `matched_name` field could report either the OLD chapter name (the one that was matched against) or the NEW TOC's actual text at the matched idx. Spec's REQ-007 example (`matched_name:"第12章 風起"`) doesn't disambiguate since both would coincide under rule-a (exact match).
- Options: (a) carry the old name forward as `matched_name`; (b) look up the NEW TOC entry at the resolved idx and use its actual name.
- Decision: (b) — `matched_name` is the NEW TOC's chapter text at `new_idx`.
- Why: Under rule-b/rule-c matches the old and new names differ (that's the whole point of fuzzy matching); showing the user the OLD name after they've switched sources would describe a chapter that no longer exists verbatim in the new source. The NEW text is what the reader will actually display.
- Spec-gap: requirement.md REQ-007 Scenario 1 pins the migrated summary substring but not which side's name feeds it; resolved per above.

## [1784437201] p2-os/impl
- Situation: `SwitchOutcome::{Migrated,Reset}` carry a `chapter_count` field (and `Reset` a `first_name`) per design.md's type table, but neither `migration_summary` (as first drafted) nor any other code read them post-construction — `cargo build` flagged two NEW `dead_code` warnings (fields never read), which would violate the "no new warnings" global constraint (C22 / brief global 5).
- Options: (a) `#[allow(dead_code)]` the fields with a comment, mirroring the existing `AbortReason` variant pattern; (b) actually surface the fields in `migration_summary`'s output text.
- Decision: (b) — enriched both summary branches to include the chapter count (and `first_name` for the reset case), e.g. `"進度已遷移：{matched_name}（共 {chapter_count} 章）"` / `"進度重置到首章：{first_name}（共 {chapter_count} 章）"`.
- Why: The fields already exist for a reason (the design explicitly modeled them into the type); silencing the warning with `#[allow]` would keep genuinely dead data, whereas surfacing them is more useful to the user and keeps the fields load-bearing. REQ-007's test scenarios only assert substring containment ("進度已遷移", "第12章 風起", "進度重置到首章"), so the additional text does not break any pinned assertion.
- Spec-gap: none — brief only requires the two substrings above to appear; additional detail is compatible.

## [1784437202] p2-os/impl
- Situation: `req003_scenario1_three_sources_all_hit` (an existing, unmodified-in-behavior test per C6/C20) contains a `match &rows[i] { Hit{..} => .., StatusLine(s) => panic!(..) }` that became non-exhaustive once `HitOrStatus::FoldedHit` was added — `rustc` E0004 (a compile error, not a test-behavior change: this test only ever calls `assemble_rows`, which never produces `FoldedHit`).
- Options: (a) add a wildcard `_ => unreachable!()` arm; (b) add an explicit `other => panic!(...)` arm that also handles `FoldedHit` for a clearer failure message if the invariant is ever violated.
- Decision: (b) — replaced the `StatusLine` arm with an `other => panic!(...)` arm covering both `StatusLine` and `FoldedHit`, preserving the original panic message content for the `StatusLine` case.
- Why: This is a mechanical compile-fix forced by adding a new enum variant elsewhere, not a change to what the test asserts — the asserted values (`rows.len()==3`, per-row `source_name`) are untouched, so the B5/C6 "supersede" rule is not invoked (same category as the dao signature-bump precedent from the spec phase).
- Spec-gap: none.
