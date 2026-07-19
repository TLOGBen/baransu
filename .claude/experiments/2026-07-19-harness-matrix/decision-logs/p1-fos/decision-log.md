# Decision Log — exp/p1-fos

## [1784432619] p1-fos/lead
- Situation: Worker split for the three brief items (1–3 sequential sonnet workers).
- Options: (1) one worker for everything; (2) three workers, one per item; (3) two workers — A+C together, B alone.
- Decision: Two workers. sub-1 = Item A (rule DSL `&` self-selector) + Item C (search result folding); sub-2 = Item B (progress migration).
- Why: A and C are both localized, pure-logic changes with unit-only test surfaces (rule.rs / tui/search.rs) and zero overlap with B's files. B spans dao → facade → core → CLI → TUI and deserves an undiluted context. One-worker risks context exhaustion mid-B; three workers pays a full warm-up cost for tiny Item A alone.
- Spec-gap: none.

## [1784432619] p1-fos/lead
- Situation: Item B — how the migrated progress idx reaches the DB transaction without breaking the 6 existing dao tests (INT-1/2a-d/3/4 assert "progress = first idx").
- Options: (1) change `update_book_source_tx` to take an explicit `progress_idx: i64` and adapt all dao test call sites; (2) add a parallel `_with_progress` public fn and keep the old one (risk: old fn becomes test-only → NEW dead_code warning in non-test builds, violating global constraint 5); (3) add `progress_idx: Option<i64>` param, `None` → first idx (existing behavior).
- Decision: Option 3 — `Option<i64>` threaded dao → facade → `SwitchSourceDeps::switch_source_tx`. Existing dao tests add `, None` at call sites; every assertion stays byte-identical.
- Why: Keeps the reset path as the dao-level default (B4 = today's behavior verbatim), avoids a dead public fn, and the test adaptation is purely mechanical — asserted behavior is untouched, so this stays within the B5 supersede rule's spirit (logged here as required).
- Spec-gap: brief doesn't say where the matched idx is decided; decided: matching is a pure fn in presentation (`switch_source_core.rs`), dao only receives the final idx.

## [1784432619] p1-fos/lead
- Situation: Item B precedence semantics — "the first chapter satisfying the highest-precedence rule wins" is ambiguous (per-chapter first-rule-hit vs per-rule full scan).
- Options: (1) single pass, first chapter matching ANY rule wins; (2) three sequential full passes (exact → whitespace-stripped → chapter-number token), first match of the highest pass that has any match wins.
- Decision: Option 2 — three ordered full passes over the new TOC.
- Why: "highest-precedence rule wins" only has meaning if a lower-precedence early match cannot shadow a higher-precedence later match; a single pass would let a rule-c early hit beat a rule-a late hit, contradicting the precedence list.
- Spec-gap: this exact ambiguity; resolved as above and encoded in sub-2's instructions.

## [1784432619] p1-fos/lead
- Situation: Item B — errors while reading OLD progress/TOC from the DB (SELECTs before the tx).
- Options: (1) propagate Err and abort the whole switch; (2) treat any read error as "unresolvable old name" → fallback reset.
- Decision: Option 2 (best-effort semantics).
- Why: the feature is explicitly "best-effort migration"; a failed migration lookup must never block a switch that today succeeds. The five abort classes stay the ONLY abort causes.
- Spec-gap: brief defines fallback for "no progress row / unresolvable name" but not for read errors; folded read errors into "unresolvable".

## [1784432619] p1-fos/lead
- Situation: Item C — representation of folded rows vs the existing `HitOrStatus` consumed by draw(), Enter handling, and 5 existing pattern-matching tests.
- Options: (1) new parallel row enum + convert at draw time; (2) extend `HitOrStatus::Hit` with a `co_sources: Vec<(SearchHit, String)>` field (empty = single-source) and add a pure `fold_rows` post-pass after `assemble_rows`.
- Decision: Option 2.
- Why: every existing test matches `Hit { source_name, .. }` / `Hit { .. }` with rest-patterns, so adding a field compiles without touching a single existing assertion; `assemble_rows` semantics stay pinned by the old tests, folding gets its own pure fn + tests (C6). Primary hit stays in the `hit` field so Enter-on-collapsed-row = first source's hit (C4) with zero changes to `handle_enter_on_hit`.
- Spec-gap: none.

## [1784432619] p1-fos/lead
- Situation: Test strategy across the delivery.
- Options: unit-only vs unit + in-memory dao integration.
- Decision: A/C = unit tests in-module (house style). B = pure-fn unit tests for matching + `FakeDeps` orchestration tests for migrated/reset outcome (B1–B4, B6) + one new dao in-memory test pinning `progress_idx: Some(n)` actually lands in the progress row; existing INT-1..4 keep pinning the `None` path.
- Why: matches the existing seam design (`SwitchSourceDeps`, `open_in_memory`); every criterion gets a test that fails if the feature is reverted (global constraint 2).
- Spec-gap: none.

## [1784433200] p1-fos/sub-1
- Situation: Item A implementation — confirmed the guard-before-parse design from lead's brief; also extended `select_within` and the doc-level entry points (`extract_doc`, `select_nodes`, `extract_all_doc`) to short-circuit on `alt.selector == "&"` BEFORE calling `Selector::parse`, matching the same pattern already used in `extract_within`.
- Options: (1) only fix `extract_within` (A1-A5 minimum); (2) also do A7 bonus (doc-level `&` = root element) since it is cheap and explicitly requested.
- Decision: did both — A1-A7 all implemented in one commit.
- Why: A7 was flagged "cheap, do it" in dispatch instructions; the per-alternative-in-loop guard pattern is identical across all four entry points, so no new logic was invented, just replicated the established idiom.
- Spec-gap: none. Updated the module-level doc-comment (top of rule.rs) to describe `&` as working (previously silent on this — the detailed "currently broken" narrative lived in CLAUDE.md, not rule.rs itself, so nothing there needed correction).
- Test strategy: added 6 new tests to the existing `#[cfg(test)] mod tests`, each asserting an exact value (Some("Hi"), Some("/x"), Some("Ji"), vec len==1 with matching text, root_element() equality) per house style — no `is_ok`/`is_some`-only assertions. Full `cargo test` = 54 passed (48 baseline + 6 new), 0 failed. Build warnings: 3 total (`select_within` dead_code, `BackupReceipt.filename` dead_code — both expected/pre-existing per CLAUDE.md — plus `SwitchOutcome.chapter_count` dead_code, which was ALREADY on the branch before I touched anything, per `git log` showing it in a prior baseline commit `bfa0f46`/`9ef29de`; not introduced by my Item A change, and rule.rs/search.rs are the only files I'm authorized to touch, so I did not attempt to silence it.

## [1784433600] p1-fos/sub-1
- Situation: Item C implementation — followed lead's design (extend `HitOrStatus::Hit` with `co_sources: Vec<(SearchHit, String)>`, pure `fold_rows` post-pass, `hit_row_label` render helper).
- Options: considered whether `fold_rows` should sort/dedupe further (e.g. also re-sort co_sources) — decided against; brief only requires iteration-order preservation, not resorting.
- Decision: implemented exactly as specified: `fold_rows` iterates in order, first Hit occurrence per `(name.trim(), author-or-"".trim())` key survives at its original index, later duplicates removed and appended to `co_sources`; StatusLine rows pass through untouched (gives C5 for free). `hit_row_label` reproduces today's exact string when `co_sources` is empty, and adds `[{count}源: {names...}]` otherwise. `do_search` tail changed to `fold_rows(assemble_rows(per_source))`. Enter-on-hit needs zero changes since `handle_event` already clones the top-level `hit` field only (C4: acts on first source's hit).
- Why: matches house style (pure helper + existing seam), keeps `assemble_rows`'s 5 pinned tests untouched (only added `co_sources: Vec::new()` at its single construction site, which all 5 tests already match via rest-patterns).
- Spec-gap: brief did not specify whether `author: None` vs `author: Some("")` should fold. Per lead's decision-log entry (recorded before I started) the default is: they fold, both normalize to `""` via `.as_deref().unwrap_or("").trim()`. I implemented and tested this explicitly (test `c2_different_author_stays_separate_none_and_empty_fold_together`).
- Test strategy: 4 new pure unit tests (C1, C2, C3, C5) in the existing `#[cfg(test)] mod tests`, each asserting exact lengths/positions/substrings (no `is_ok`/`is_some`-only checks) — reused `make_hit` and added `make_hit_author(name, src_url, author: Option<&str>)` per dispatch instructions. Full `cargo test` after Item C = 58 passed (48 baseline + 6 Item-A + 4 Item-C), 0 failed. All 5 pre-existing `search::tests` pass unchanged. `cargo build` warning count unchanged at 3 (select_within, BackupReceipt.filename — both expected per CLAUDE.md — plus the pre-existing `chapter_count` warning noted in my Item A log entry, confirmed present in the repo before I touched any file via `git log`/`bfa0f46`).

## [1784433430] p1-fos/sub-2
- Situation: Item B implementation start — confirmed `cargo test` green (58 passed, 0 failed) before touching anything, per lead instructions.
- Options: n/a (verification step).
- Decision: proceed with lead's design exactly as specified (DAO `progress_idx: Option<i64>` param, facade pass-through, pure matching fns in `switch_source_core.rs`, `SwitchSourceDeps` extended with `get_progress`/`list_old_chapters`, orchestration resolves migration BEFORE the tx, `SwitchOutcome.progress: ProgressOutcome` + `format_progress_note`).
- Why: lead's design already resolved the ambiguous points (3-pass precedence, best-effort abort semantics, outcome shape) — no reason to deviate.
- Spec-gap: none at this step.

## [1784433440] p1-fos/sub-2
- Situation: `chapter_num_token` regex character class — lead's spec character class mixes an actual digit range (`0-9`, `０-９`) with individual Chinese numeral literals (`一二三...兩`) with no separating hyphens between the CJK chars.
- Options: (1) write the class using `\u{XXXX}` escapes for every CJK char to be maximally explicit about codepoints; (2) write the literal CJK characters directly in the regex string.
- Decision: used literal characters directly (`"第\\s*([0-9０-９一二三四五六七八九十百千零〇两兩]+)\\s*[章回節节卷]"`), matching the brief's spec string byte-for-byte.
- Why: escape-per-char (attempted first) is harder to visually verify against the spec and risks an off-by-one range mistake (e.g. `\u{4e00}-\u{4e8c}` would silently become a *range* covering unintended codepoints instead of two literal alternatives); the literal-character form is trivially diffable against the brief text and the source file is UTF-8, so no encoding risk.
- Spec-gap: none — chose the safer of two implementations of the same spec.

## [1784433450] p1-fos/sub-2
- Situation: DAO `update_book_source_tx`/`_with_fault`/`_inner` gained `progress_idx: Option<i64>`. Five existing call sites (1 dao test, 1 fault-injection helper, 3 more dao tests) needed the new arg.
- Options: (1) mechanical `, None` addition at every existing call site, all assertions untouched (sanctioned B5 adaptation per lead's design point 1); (2) overload with a second method name to avoid touching existing call sites.
- Decision: (1) — mechanical `, None` addition. `int1_update_book_source_tx_happy_path`, `assert_rollback_for_step` (covers int2a-d), `int3_no_cascade_progress_row_survives`, `int4_progress_chapter_index_matches_new_first_idx`, `empty_new_chapters_returns_err_without_touching_db` all got `, None` (or `, None,` before `fault_step` for the fault helper) with zero assertion changes.
- Why: lead's design explicitly sanctions this as the one allowed B5 adaptation; adding a second method name would create two production entry points, an unjustified new API surface.
- Test strategy: added one new dao test `migrated_progress_idx_overrides_new_first_idx` — `progress_idx: Some(7)`, new_toc first idx 3, asserts `returned == 7`, `progress.chapter_index == 7`, `progress.scroll_offset == 0` (pins B: effective_idx overrides first_idx, scroll always resets to 0 on both paths).

## [1784433470] p1-fos/sub-2
- Situation: CLI/TUI success-message formatting when `ProgressOutcome::Migrated` — `SwitchOutcome.new_first_chapter_name` is (and remains, unchanged) always the NEW TOC's first chapter name, NOT the migrated chapter's name. Naively reusing the old one-line message template (`"第 {idx}: {new_first_chapter_name}"`) with the migrated idx would print a mismatched idx/name pair (migrated idx paired with the *first* chapter's name, not the matched chapter's name).
- Options: (1) keep one uniform message template for both paths, accepting the idx/name mismatch on the Migrated path; (2) branch the message per `ProgressOutcome` variant — Migrated path uses `format_progress_note` (which already embeds the correctly-matched chapter name) + just the idx, Reset path keeps the original idx + `new_first_chapter_name` pairing.
- Decision: (2) — branched formatting in both `switch_source.rs` (CLI) and `tui/switch_source.rs` (TUI toast).
- Why: printing a self-contradictory idx/name pair to the user would be a correctness regression hiding inside a UX feature; the spec's example strings ("進度已遷移：第12章 風起" / "進度重置到首章") already imply the two paths carry different information, so branching is the more faithful reading, not scope creep.
- Spec-gap: brief's exact CLI/TUI message format was "format free" (B6) — I chose to keep the existing `✓ 已換源...` prefix/structure and append `format_progress_note`'s output, only branching the trailing detail clause to avoid the mismatch above.

## [1784433480] p1-fos/sub-2
- Situation: Best-effort read failures for `get_progress`/`list_old_chapters` inside orchestration — lead's design says "if either read returns Err, treat as unresolvable (fallback), do NOT abort."
- Options: (1) `.ok().flatten()` / `.unwrap_or_default()` to silently coerce Err → None/empty, no logging; (2) log a warning via eprintln before falling back.
- Decision: (1) — silent coercion, no logging.
- Why: brief's five abort classes are the only sanctioned failure surface for this use case; adding stderr side effects for a best-effort path not covered by any criterion would be unrequested scope, and the existing codebase has no logging framework to hook into consistently.
- Spec-gap: none — this was already decided by the lead's design point (5); recorded here for completeness since it's the actual code path exercised.

## [1784433490] p1-fos/sub-2
- Test strategy: pure-level unit tests for `strip_ws`, `chapter_num_token`, `match_chapter` (B1-B4 non-dense-idx cases, whitespace variant, same-number-different-tail, full-width digit, Chinese numeral, no-match), `resolve_old_chapter_name` (index-field lookup not position, None progress, no matching entry), and `format_progress_note` (both variants) — all assert exact values, never `is_ok`/`is_some` alone. Orchestration-level: extended `FakeDeps` with `old_progress`/`old_chapters`/`progress_idx_passed: Mutex<Option<Option<i64>>>` (mirrors existing `switch_tx_called` pattern) and added 3 new `#[tokio::test]`s asserting the exact `ProgressOutcome` variant + idx + the captured `progress_idx` handed to `switch_source_tx`, covering: migrated match, no old-progress row (fallback), and old-progress row present but no name match in new TOC (fallback). Existing `req005_s2`/`req005_s3` tests got the two new `FakeDeps` fields added (`old_progress: None, old_chapters: vec![]`, `progress_idx_passed: Mutex::new(None)`) with all original assertions unchanged (mechanical B5-style adaptation, same rationale as the dao changes above).
- Full `cargo test` after Item B: 74 passed, 0 failed (58 baseline-after-A/C + 16 new: 1 dao + 11 pure/orchestration in switch_source_core + no changes elsewhere). `cargo build` warning count unchanged at 3 (`BackupReceipt.filename`, `select_within`, `SwitchOutcome.chapter_count` — all three pre-existing on the branch before I touched anything, confirmed via `git stash`/rebuild comparison). File size: `switch_source_core.rs` grew to 697 lines — under the 800-line ceiling, so no split into a sibling `switch_source_migrate.rs` module was needed (lead's design point 7 conditional not triggered).

## [1784434200] p1-fos/review
- Situation: Independent opus audit of sub-1 (Items A, C) + sub-2 (Item B) against every brief criterion A1-A7, B1-B7, C1-C6, architecture + test-effectiveness constraints.
- Options: (a) trust worker reports; (b) full re-audit — read all 3 diffs, run cargo test, run layering greps, mutation-test the load-bearing tests, trace the 3rd warning's origin.
- Decision: Full re-audit (b). No production defects found; committed zero fixes.
- Why: Every criterion is met and pinned by a test that fails under mutation. Diffs are spec-faithful; layering greps zero-hit; the 3rd (chapter_count) dead_code warning is pre-existing (introduced in 2e427f9, present at parent bfa0f46), not introduced by any experiment commit — so "do not introduce NEW warnings" holds.
- Spec-gap: Brief lists only 2 expected dead_code warnings but the branch carried a 3rd (SwitchOutcome.chapter_count) before the experiment began; left as-is (fixing it = out-of-item-scope taste change on working code). Flagged to lead.

### Verification evidence
- cargo test: 74 passed / 0 failed (48 baseline + 6 A + 4 C + 16 B).
- Layering: `grep dao|rusqlite` over service dirs = 0 hits; `grep 'use crate::(catalog|library)::facade'` over src/catalog src/library = 0 hits.
- Mutation A (disable & short-circuit in extract_within) → 4 A-tests FAIL. 
- Mutation B (match_chapter → always None) → b1/b2/b3*/orchestration_migrates FAIL.
- Mutation C (fold_rows → identity) → c1/c2/c3/c5 FAIL.
- B match-precedence: 3-full-pass (exact→ws-stripped→num-token, each global) is spec-faithful reading of "first chapter satisfying the highest-precedence rule wins" — rule precedence dominates idx order, `.find()` returns lowest-idx within a pass. Correct.
- C4 (Enter on folded row): search.rs:198 clones primary `hit` only, ignores co_sources — meets "act on FIRST source's hit". Not in C6's required-test set; no gap.

## [1784434203] p1-fos/lead (integration)
- Situation: Final integration pass over sub-1 (A, C), sub-2 (B), and the opus review. Task: spot-verify reviewer verdicts, confirm all brief criteria, run final full test, fix anything broken.
- Options: (a) accept reviewer's clean bill after spot-checks; (b) re-audit everything; (c) additionally clean up the pre-existing `chapter_count` dead_code warning.
- Decision: (a). Zero fix commits needed; tree ships as the three worker commits (5fcd56d, 21289e1, a6b2f77) on top of bfa0f46.
- Spot-checks performed: final `cargo test` = 74 passed / 0 failed; `cargo build` = exactly 3 warnings (`select_within`, `BackupReceipt.filename`, `SwitchOutcome.chapter_count`); `git grep '\.chapter_count'` at both bfa0f46 and HEAD = 0 reads → 3rd warning definitively pre-existing at parent, "no NEW warnings" constraint holds with the 2-expected + 1-inherited reading; `&` short-circuit confirmed before `Selector::parse` in all 5 rule.rs entry points; dao.rs diff vs bfa0f46 shows only mechanical `, None` call-site additions + new-test assertions, zero pre-existing assertion changes (B5); `match_chapter` = 3 sequential global passes exact → strip_ws → num-token (spec precedence order, `.find()` gives lowest-idx within pass); `fold_rows` StatusLine arm is pure pass-through preserving relative position, fold key = (name.trim, author-or-"".trim), first occurrence keeps slot (C1/C5).
- Reviewer agreement: agreed on all verdicts, including both "left for the lead" items — the 3rd warning stays (out-of-scope taste change on pre-existing working code; removing the field would itself be an uninstructed API change to `SwitchOutcome`), and no C4 test is required (C6's mandated set is C1/C2/C3/C5; C4 is behavior-preserved-by-construction since Enter handling was never modified).
- Protocol: `.exp/` and `EXPERIMENT-BRIEF.md` intentionally uncommitted; all production+test work committed in the three commits above; no fix: commit exists because nothing needed fixing.
