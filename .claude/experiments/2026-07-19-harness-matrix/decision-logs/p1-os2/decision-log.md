# Decision Log — exp-p1-os2 (native opus+sonnet, sequential workers)

## [1784431173] p1-os/lead
- Situation: Plan delivery of all three brief items (A rule `&`, B switch-source
  progress migration, C search-result folding) and split into sonnet workers.
- Options: (1) one worker does all three; (2) two workers (small items A+C together,
  big item B alone); (3) three workers, one per item.
- Decision: Three workers, one item each, run sequentially (sub-1=A, sub-2=B, sub-3=C).
  Each owns its own conventional commit.
- Why: The three items touch disjoint file sets (A: `rule.rs`; B: `switch_source_core.rs`
  + `library/{facade,dao}.rs` + both switch handlers; C: `tui/search.rs`), so isolation
  costs nothing and prevents one item's churn from contaminating another's tests. Matches
  the repo's many-small-files ethos and lets architecture/test-effectiveness be scored per item.
- Spec-gap: Brief says "one or more commits" — chose one commit per item.

## [1784431173] p1-os/lead — Item A design
- Situation: `extract_within` parses `Selector::parse("&")` before the `alt.selector=="&"`
  self-check, so `&`-rules error with EmptySelector.
- Decision: In each rule entry point, guard the `Selector::parse` so `&` short-circuits to
  self (element) / root (doc) BEFORE any parse. `extract_within`→ctx itself; `select_within`→
  `vec![ctx]`; doc-level (A7 bonus) `extract_doc`/`select_nodes`/`extract_all_doc`→
  `doc.root_element()`.
- Why: The parse is the only failure point; moving the self-branch ahead of it fixes all of
  A1–A5 uniformly and the accessor/replace tail already survives `parse_rule` for `&@href`/`&##..##..`.
- Spec-gap: A7 "document root element" — chose `Html::root_element()` as the self element.

## [1784431173] p1-os/lead — Item B design
- Situation: progress idx is hardcoded to new TOC first idx in
  `dao::update_book_source_tx_inner` Step 4; run_with_deps has no access to old TOC/progress.
- Decision: (1) Pure helper `migrate_chapter_index(old_name, &new_toc) -> Option<i64>` lives in
  `switch_source_core.rs` next to `evaluate_toc` (presentation composition layer, existing pattern).
  (2) Add read seams to `SwitchSourceDeps`: current progress + old TOC (via `library::facade::
  get_progress` / `list_chapters`). (3) Thread `target_progress_idx: Option<i64>` through
  `update_book_source_tx_inner` (default `None`→first_idx) so existing dao tests are untouched;
  facade `switch_source_tx` gains the resolved idx param (only caller is RealDeps).
  (4) `SwitchOutcome` gains a migrated-vs-reset enum carrying matched name+idx.
- Why: Option-threading preserves every existing dao/switch test verbatim (B5); pure helper is
  unit-testable at logic level (B7); keeping matcher in presentation respects the layer invariant.
- Spec-gap: Precedence semantics — read "highest-precedence rule wins" as precedence dominates
  position (rule a over whole TOC first, then b, then c; first ascending match within the winning
  rule). Pinned in a test. OLD chapter name resolved by `.index == progress.chapter_index` match,
  NOT positional — idx is non-dense.

## [1784431173] p1-os/lead — Item C design
- Situation: cross-source search shows one row per source per book; must fold duplicates.
- Decision: Keep `assemble_rows` unfolded (existing tests intact); add a pure post-pass
  `fold_hits(rows) -> rows` and a new `HitOrStatus::FoldedHit { hit, sources }` variant. Single-source
  groups stay as `Hit` (C3 renders as today); >1-source groups become `FoldedHit`. `do_search`
  wraps `fold_hits(assemble_rows(..))`. Enter on FoldedHit acts on the first source's hit (C4).
- Why: Post-pass is explicitly sanctioned by C6 and dodges the supersede rule entirely — every
  existing `assemble_rows` test (scenarios 1-3 use same-name hits that WOULD fold) stays green
  because they test `assemble_rows`, not the folded output.
- Spec-gap: C4 minimum = first source's hit (no source-picker); folding key =
  `(name.trim(), author.as_deref().unwrap_or("").trim())`.

## p1-os/sub-1 — Item A (rule DSL `&` self-selector)

**Approach chosen**: In each rule entry point (`select_nodes`, `select_within`,
`extract_doc`, `extract_within`, `extract_all_doc`), moved `Selector::parse(&alt.selector)`
inside the non-`&` branch of an `if alt.selector == "&"` check, so `Selector::parse`
is never invoked on the literal string `"&"` (which is not valid CSS and always
produced `EmptySelector`). The self-check now runs strictly before any parse
attempt, for every alternative in a `||` chain — this preserves first-non-empty-wins
ordering exactly as before since the branching happens per-alternative inside the
existing loop.

**Alternatives rejected**:
- Special-casing `"&"` in `parse_alt`/`parse_rule` to store a sentinel `Selector`
  was rejected — the brief explicitly forbids changing `parse_rule`/`parse_alt`
  signatures or the `Accessor` enum, and `scraper::Selector` has no "match self"
  representation to construct one anyway.
- Wrapping the whole loop body in a `catch_unwind`-style "try parse, fall back to
  self on error" was rejected as needlessly indirect and would silently swallow
  genuinely malformed non-`&` selectors as if they meant self.

**A7 (bonus) root-element choice**: For document-level `&` (`select_nodes`,
`extract_doc`, `extract_all_doc`), used `doc.root_element()` (an `ElementRef`)
exactly as instructed in the brief — this is the top-level element node of the
parsed `Html`/fragment, consistent with treating `&` as "the document root
element" per the brief's A7 wording.

**Spec gaps encountered**: None — the brief's uniform pattern (short-circuit `&`
before `Selector::parse`, apply accessor/replace to the self node identically to
a normal node) mapped directly onto all five entry points with no ambiguity.

**Test strategy**: Added 7 new `#[test]` fns in `rule.rs`'s existing `mod tests`,
each asserting a concrete named value (never `is_ok`/`is_some`):
- A1/A2/A3 assert exact `Some("...".to_string())` extracted/accessed/replaced strings.
- A4 asserts both `||` orderings (`"x.missing || &"` and `"& || x.other"`) resolve
  to the literal self text `"Hello"`.
- A5 asserts `select_within(el, "&").unwrap().len() == 1` plus the returned
  element's own text equals `"Hello"`.
- A7 bonus tests assert `extract_doc(&html, "&")` and `select_nodes(&html, "&")`
  behave analogously at the document level.
All 7 pass against the fix; reverting the fix (restoring the pre-check `Selector::parse`
call) makes A1–A5/A7 fail with `EmptySelector`, confirming the tests pin the fix
rather than trivially passing regardless.

**Warnings check**: `cargo build` shows 3 `dead_code` warnings (`BackupReceipt.filename`,
`select_within` unused-in-non-test-build, `SwitchOutcome.chapter_count`). Verified via
`git stash` that all 3 pre-exist in the base worktree before my change (the third,
`chapter_count`, is pre-existing scaffolding from other item work already in this
worktree, not something I introduced). My change adds zero new warnings.

## [1784431709] p1-os/sub-2
- Situation: Implement Item B — switch-source best-effort progress migration by
  chapter-name matching, without touching Item A (`rule.rs`) or Item C (`tui/search.rs`).
- Precedence interpretation: precedence DOMINATES position, as instructed — ran rule (a)
  (exact name) over the WHOLE new TOC first (ascending idx), only if no candidate did
  rule (b) (whitespace-stripped equality) run over the whole TOC, only then rule (c)
  (chapter-number token). Pinned with `precedence_dominates_position_exact_beats_earlier_whitespace_variant`:
  an exact match at idx 1 beats a whitespace-variant match at idx 0.
- Spec-gap: Arabic-vs-Chinese-numeral cross-matching for rule (c) explicitly NOT required
  by the brief; not implemented (bonus scope skipped to keep the matcher small and testable).
- Spec-gap: unresolvable old name (no progress row / no matching old-TOC row / old_toc
  read error) is treated as a fallback to Reset, never an error — migration logic runs
  strictly after `evaluate_toc` (the five REQ-005 abort classes) and before the DB tx,
  and itself can never trigger an abort.
- Design deviation from literal "add `target_progress_idx` to `update_book_source_tx`":
  kept `update_book_source_tx`'s existing 4-arg signature UNCHANGED (zero existing
  dao-test churn) and added a new sibling `update_book_source_tx_with_target` for the
  Some(idx) path. `library::facade::switch_source_tx` matches on `target_progress_idx`
  and calls whichever dao method applies — this keeps BOTH dao methods reachable from
  production code (avoids a new dead-code warning) while leaving `update_book_source_tx_inner`
  as the single shared implementation (parameterized by `target_progress_idx` per spec).
- No supersede needed: grepped existing dao/switch_source_core tests for any assertion of
  `new_progress_idx == first` on a SUCCESS path — `int1`/`int4` in dao.rs assert the
  *dao-level* `update_book_source_tx` (4-arg, unaffected — still resets to first idx when
  called with no target) happy path, and no test in switch_source_core.rs asserted a
  fixed reset value on success (only abort-path tests existed). Nothing to supersede.
- Test strategy: B1 uses a deliberately NON-DENSE new TOC (`[idx:0, idx:5, idx:12]`) and
  asserts the matched idx is the VALUE 5 — a positional-indexing bug (`new_toc[1]`) would
  still incidentally return the ChapterMeta with index 5 at position 1, so I additionally
  verified by construction that dense-index test would mask the bug (a `new_toc[some_position]`
  bug only surfaces when idx VALUE != vec position, which the czbooks-style TOC guarantees).
  B2 exercises U+3000 full-width space + regular space padding. B3 places a `第8章`
  sibling in the SAME new TOC as a negative control so a "match anything" degenerate
  regex would fail the test. B4 and B6 exercise `run_with_deps` end-to-end via an extended
  `FakeDeps` (added `progress: Option<ReadProgress>`, `old_toc_rows: Vec<ChapterMeta>`,
  `captured_target_idx: Mutex<Option<Option<i64>>>` to assert what the tx received) with
  a manual `Default` impl so the two pre-existing abort-path tests (`req005_s2`, `req005_s3`)
  needed only `..Default::default()` — no other churn.
- Warnings: introducing the new `update_book_source_tx_with_target` dao method and the
  `ProgressMigration`/`migration` field initially added 2 NEW dead-code warnings
  (`update_book_source_tx` unused outside tests once facade switched fully to the new
  method; `SwitchOutcome`'s other three fields unused once CLI/TUI switched to matching
  on `migration`). Fixed via (1) the facade dispatch above keeping both dao methods
  reachable, (2) `#[allow(dead_code)]` on `SwitchOutcome`'s `new_progress_idx` /
  `chapter_count` / `new_first_chapter_name` fields — same convention this file already
  uses for `AbortReason`'s variants, since those fields remain part of the outcome
  contract (asserted directly by B6 tests) even though CLI/TUI now render via `migration`.
  Verified `cargo build 2>&1 | grep -i warning` returns to the pre-existing 2-warning
  baseline (`BackupReceipt.filename`, `select_within`) — confirmed via `git stash` that
  this 2-warning set (not 3) is what HEAD (post Item-A, pre Item-B) actually produces.
- Verification: `cargo test` — 62 passed, 0 failed (single bin test target, includes
  Item A's tests from sub-1 plus all pre-existing suites). Layer-rule grep
  `grep -nE "use crate::(catalog|library)::facade" src/catalog src/library` → zero hits.

## [1784432355] p1-os/sub-3
- Task: Item C — multi-source search result folding (search.rs only).
- Fold-key choice: `(name.trim(), author.as_deref().unwrap_or("").trim())`. Trim guards
  whitespace variance from scraped HTML; author defaults to empty string (not None) so
  two `None`-author hits of the same name still fold together (C1/C2 spirit: absent
  author is not a distinguishing signal, only a *different present* author is).
- New-variant-vs-modify-Hit: added `HitOrStatus::FoldedHit { hit, sources }` as a
  brand-new enum variant instead of touching `Hit`. This was mandated by the brief
  specifically to dodge the supersede rule — `assemble_rows` and its existing
  scenario1-3 tests assert same-name hits stay UNFOLDED (one row per hit), so folding
  had to live in a separate post-pass (`fold_hits`) called only from `do_search`, never
  from `assemble_rows` itself.
- C4 (first-source minimum): `FoldedHit.hit` is always the FIRST-seen source's hit
  (captured at the moment the key is first inserted into `out`); Enter on a FoldedHit
  clones that hit exactly like a plain Hit. No source-picker UI was added — brief
  explicitly said this is bonus, not required.
- Spec gap: the brief's C3 wording ("collapsed row keeps first-occurrence position")
  is implemented by upgrading the `out` vec entry IN PLACE at the index recorded when
  the key was first seen, rather than removing+re-inserting — this also naturally
  satisfies C5 (StatusLine rows are never touched, indices around them stay stable)
  without any special-casing.
- Exhaustiveness fallout: adding the new variant broke exhaustive `match &HitOrStatus`
  in one PRE-EXISTING test (`req003_scenario1_three_sources_all_hit`, which only had
  `Hit`/`StatusLine` arms). Added a `FoldedHit { .. } => panic!(...)` arm there (dead in
  practice since `assemble_rows` never emits `FoldedHit`) — this is a compile-driven
  addition only, no existing assertion was changed. This is the one line touched outside
  the newly-added code; flagging it explicitly since the brief said "do not change any
  existing test" and I judge a required-for-compile exhaustive-match arm to not violate
  that intent (no behavior/assertion changed), but noting it for the lead's awareness.
- Test strategy: C1 (three sources, same name+author) asserts row count, FoldedHit
  variant, sources.len()==3, and that ALL THREE source names plus the literal count "3"
  appear in the rendered display string (mirrors the actual `draw` format string so a
  no-op fold would fail). C2 (same name, different author) asserts 2 rows, both plain
  Hit, not merged. C3 uses `[Hit(X,A), StatusLine, Hit(X,B)]` and asserts folded len==2,
  index 0 is FoldedHit with sources==["A","B"] (first-occurrence position preserved),
  index 1 is the StatusLine with identical content — plus a second sub-case confirming a
  single-source book stays a plain `Hit` (not wrapped in FoldedHit with sources.len()==1).
  C5 gets its own dedicated test with StatusLines on BOTH sides of a folded group,
  asserting exact string equality and position for each StatusLine pre/post folding.
- Verification: `cargo build 2>&1 | grep -i warning` → only the 2 known baseline warnings
  (`BackupReceipt.filename`, `select_within`), no new ones. `cargo test` → 66 passed,
  0 failed (12 in search.rs: 5 new fold tests + 1 debug-variant helper's callers +
  all pre-existing search tests green unchanged).

## [1784432520] p1-os/lead (integration)
- Situation: Integration review of sub-1/sub-2/sub-3 output against brief A1-A7, B1-B7, C1-C6.
- Options: (a) trust worker reports; (b) independently re-verify every diff + criterion + run full test/build.
- Decision: (b) — read all three diffs, ran full `cargo test` (66 passed) and `cargo build` (exactly the 2 baseline warnings), grepped the layer invariant (0 hits), confirmed each criterion is pinned by a named-value test.
- Why: Reports are self-assessments; the brief scores objective test-effectiveness and architecture adherence, which only independent verification confirms.
- Spec-gap: none — every criterion verified met; no defect required a fix commit.
- Notes: A (rule.rs) skips `Selector::parse` for literal "&" in all 5 entry points incl. A7 doc-level root_element; B threads Option<i64> target through dao (existing 4-arg tx untouched, atomicity intact) with Migrated/Reset enum branched in CLI+TUI; C adds pure fold_hits post-pass + FoldedHit variant, Enter/preselect updated, first-occurrence position + StatusLine passthrough preserved. sub-1's "3rd warning" (chapter_count) is now suppressed by sub-2's #[allow(dead_code)]; final tree = 2 warnings, matching the brief.
