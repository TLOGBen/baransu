
## [1784440447] p3-f/spec
- Situation: Item B — where the chapter-name matching pure function should live (layer placement).
- Options: (1) new library/service/progress.rs module; (2) pure helper in presentation/handlers/switch_source_core.rs.
- Decision: switch_source_core.rs pure helper (find_migration_target), with ProgressResolution enum defined there too.
- Why: follows the in-repo precedent (evaluate_toc is already a pure judgment fn in that file); inputs/outputs are PL types only; keeps fake-deps tests colocated. Avoids putting a presentation-consumed type into Library PL (mod.rs must stay logic-free).
- Spec-gap: brief does not say which layer hosts the matcher; "pure, unit-testable" satisfied either way.

## [1784440447] p3-f/spec
- Situation: Item B — dao tx must write a migrated idx but existing tests call the 4-arg update_book_source_tx and assert first-idx reset.
- Options: (1) parallel method _with_progress; (2) add trailing param progress_idx: Option<i64> with None = current behavior.
- Decision: Option<i64> trailing param on update_book_source_tx(_inner/_with_fault) and facade switch_source_tx; existing call sites/tests mechanically append None.
- Why: keeps a single tx entry point (no duplicated tx logic to drift); appending None does not change any asserted behavior, so B5's "existing tests pass" holds without invoking the supersede rule.
- Spec-gap: brief B5 allows adapting tests only when behavior is superseded; signature-only adaptation is judged mechanical, logged here for transparency.

## [1784440447] p3-f/spec
- Situation: Item B step 1 — what to do when resolving the old chapter name itself errors (DB read Err), beyond the specified "no progress row / unresolvable name" cases.
- Options: (1) propagate Err (new abort class); (2) degrade to no-match → reset path.
- Decision: any Err/None in resolution degrades to Reset; switch itself proceeds. Deps method current_chapter_name added to SwitchSourceDeps so fakes can inject Err.
- Why: "best-effort migration" semantics + B5 forbids touching the five abort classes — adding a sixth failure exit would violate abort-class parity.
- Spec-gap: brief only lists "no progress row / unresolvable name → fallback"; Err case unspecified.

## [1784440447] p3-f/spec
- Situation: Item B B6 — migrated-message format: existing CLI prints "第 {idx+1} 章" derived from idx.
- Options: (1) keep idx+1 derivation; (2) show matched chapter name + raw idx.
- Decision: spec mandates matched name + raw idx, forbids idx+1 → 第N章 derivation in the migrated message.
- Why: idx is non-dense (CLAUDE.md czbooks example), so idx+1 as a chapter ordinal is factually wrong; B1 explicitly warns about the non-dense assumption.
- Spec-gap: brief leaves message format free.

## [1784440447] p3-f/spec
- Situation: Item C — where folding runs: extend assemble_rows or post-pass.
- Options: (1) fold inside assemble_rows; (2) fold_rows post-pass + new Folded variant, do_search composes fold_rows(assemble_rows(..)).
- Decision: post-pass with new HitOrStatus::Folded { hits: Vec<(SearchHit, String)> }; single-source rows stay Hit.
- Why: existing req003_scenario1 asserts 3 rows for the same book from 3 sources against assemble_rows — folding inside it would force invoking the supersede rule; post-pass keeps all 5 existing tests untouched (C6-brief) and C3 (single-source renders as today) is guaranteed by the type.
- Spec-gap: brief allows either ("extend assemble_rows or add a post-pass").

## [1784440447] p3-f/spec
- Situation: Item C — same source returning the same book twice: fold key only considers (name, author).
- Options: (1) dedup source names in the folded row; (2) fold as-is, count includes repeated source entries.
- Decision: fold as-is; count = hits.len(), source names in appearance order (may repeat).
- Why: simplest consistent rule; brief only defines the fold key, not intra-source dedup.
- Spec-gap: brief silent on duplicate hits from one source.

## [1784440447] p3-f/spec
- Situation: REQ numbering collides with legacy REQ-003/005/007 comments already in the code (previous spec round).
- Options: (1) renumber this spec REQ-101..; (2) keep skill-mandated sequential REQ-001.. + explicit anti-collision notice.
- Decision: keep REQ-001..REQ-006, add a prominent 編號防撞聲明 at the top of requirement.md/design.md and in every task file and ctx file.
- Why: analyze SKILL.md mandates sequential numbering from 001; the notice removes the impl-agent confusion risk without deviating from the skill.
- Spec-gap: skill does not cover pre-existing REQ comments in target code.

## [1784440447] p3-f/spec
- Situation: Test strategy — B6 says "the CLI handler prints it"; capturing stdout of a handler that calls process::exit is costly.
- Options: (1) stdout-capture integration test; (2) assert message content at a shared pure fn (describe_progress) + thin forwarding in CLI/TUI.
- Decision: message assembly extracted to describe_progress, unit-tested for both states; CLI/TUI are thin forwarders (documented in test.md 冗餘掃描 as an explicit removal).
- Why: pins the user-visible text with a cheap named-value assertion; matches the brief's "pure-logic level" test guidance (B7) and house style.
- Spec-gap: none — B6 requires the outcome be surfaced; verification level was unspecified.

## [1784440447] p3-f/spec
- Situation: Stage 6 three-subagent review replaced (per dispatch) by one self-review pass over the three cross-layer questions.
- Options: n/a (mandated by dispatch).
- Decision: findings fixed: added E2E row for C18/folded_label (was only a boundary entry), added layer-grep verification row (C22 had no test anchor), added C14 to the global test-count row's criteria citation.
- Why: C{n} anchoring rule — every goal criterion needs at least one test.md anchor.
- Spec-gap: none.

## [1784440724] p3-f/impl-a
- Situation: TASK-a-01/a-02 — `&` self-selector across 5 rule-DSL entrypoints; chose implementation shape for deferred parsing.
- Options: (1) pre-scan rule for `&` and special-case before the loop; (2) move `Selector::parse` into the non-`&` branch inside the per-alternative loop (lazy parse); (3) teach parse_alt to emit an enum variant for `&`.
- Decision: Option 2, exactly as the ctx Design section prescribes; select_within/select_nodes early-return `Ok(vec![candidate])` on `&`; extract_all_doc branches if/else inside the loop keeping the `if !out.is_empty() break` fallback intact.
- Why: Smallest diff satisfying C4's "parse deferred until the alternative's turn"; option 3 would touch parse_rule which the spec forbids; option 1 breaks `||` ordering semantics.
- Spec-gap: none (Design section fully specified the fix shape).

## [1784440724] p3-f/impl-a
- Situation: Brief says "two pre-existing dead_code warnings"; baseline build actually emits 3 (filename, select_within, chapter_count).
- Options: (1) treat count literally and try to silence one; (2) verify baseline via git stash and require identical before/after warning sets.
- Decision: Option 2 — stashed my change, built baseline: same 3 warnings; after change: same 3. No new warnings introduced; no warning-silencing edits made (constraint forbids touching dead_code annotations).
- Why: The real invariant is "no NEW warnings"; the brief's count is stale. select_within stays dead in the bin target because tests are cfg(test)-gated.
- Spec-gap: brief undercounts pre-existing warnings (3, not 2).

## [1784440724] p3-f/impl-a
- Situation: Test strategy for task a.
- Options: single mega-test vs per-criterion named tests; exact-string vs contains assertions for doc root text.
- Decision: 8 named tests (C1,C2,C3,C4,C5,C7 + two boundary tests: trim `" & "`, empty-`&`-falls-through/all-empty-None), two RED/GREEN rounds (element layer then doc layer). Exact assertions: `"alphabeta"` for root text, node id equality for element identity, full outerHtml string.
- Why: Test-effectiveness constraint demands named-value pins; two rounds keep vertical slicing per design task split (a-01/a-02).
- Spec-gap: spec didn't state expected root text join format; scraper joins text nodes without separator → "alphabeta", verified green.

## [1784440886] p3-f/review-a
- Situation: Four-tier review of group a (TASK-a-01/a-02, commit 1296196). All C1–C7 AC met item by item; C6 diff-verified (no test lines in the removed hunks); red_proof present and root-cause-consistent; green re-run 12/12 module + 56/56 full, exit 0; warning set 3 pre-existing dead_code, none new.
- Options: (1) advisory with findings; (2) packaged confirm (correctness) over the unpinned C4 lazy-parse deferral.
- Decision: tier = advisory. Deferral is implemented and code-verified; the AC's testable clause (both || orders parse correctly) is pinned. Missing invalid-trailing-selector pin is an improvement, not an unmet criterion. Second advisory: checklist 收尾 line says 2 pre-existing warnings, actual 3 (impl already logged the spec-gap; re-verified).
- Why: M-classified task — quality observations route to advisory per contract; no correctness gap, no spec contradiction.
- Spec-gap: none new beyond the warning-count undercount already logged by impl-a.

## [1784441545] p3-f/impl-b
- Situation: Rust cannot express a behavioral RED for a not-yet-existing symbol/signature — the test won't compile.
- Options: (1) accept compile error as red; (2) add a behavior-absent scaffold (stub fn returning None / param added but ignored / trait method added but not called) so tests compile and fail on ASSERTIONS.
- Decision: Option 2 for all four rounds (b-02 stub None, b-01 param ignored, b-03 field=Reset + tx gets None, b-04 stub ""); every red_proof is an assertion failure with named values, not a compile error.
- Why: Contract treats red-phase compile errors as test-syntax problems to fix; a scaffold that changes no behavior gives an honest "feature absent" red (e.g. int5 red: left 3, right 5).
- Spec-gap: none.

## [1784441545] p3-f/impl-b
- Situation: Negative tests (mig2b/mig3b/mig3c/mig4 expecting None) already pass against the None-returning stub — they cannot red.
- Options: (1) drop them; (2) keep them as boundary pins that only become meaningful once positive logic exists.
- Decision: Keep; the round's red is carried by the 5 positive-match tests (all failed pre-impl), the None tests pin the rule boundaries (empty-after-strip skip, no cross-numeral match, tokenless side) against the green implementation.
- Why: A None-expected test genuinely cannot fail before the matcher exists; its value is regression pinning of the b/c rule edges.
- Spec-gap: none.

## [1784441545] p3-f/impl-b
- Situation: After rewiring CLI/TUI onto describe_progress, SwitchOutcome.new_progress_idx became dead in the bin target, expanding a dead_code warning (baseline: chapter_count only; after: new_progress_idx and chapter_count) = a new warning name.
- Options: (1) remove the field — forbidden, ctx Design says 既有三欄不動; (2) leave the grown warning — violates 不引入新警告; (3) #[allow(dead_code)] on new_progress_idx (house style: SwitchSourceScreen, AbortReason variants).
- Decision: Option 3; verified post-change bin warning set is byte-identical to baseline (filename, select_within, chapter_count) via git stash A/B build.
- Why: Field stays part of the outcome API and is pinned by tests (mig_run_* assert it); only its bin-side reader moved into describe_progress.
- Spec-gap: ctx demands both "keep the three fields" and "no new warnings" without saying how to reconcile them when the CLI stops reading idx.

## [1784441545] p3-f/impl-b
- Situation: TASK-b-03 criterion for RealDeps::current_chapter_name (get_progress → list_chapters same-idx name, any None → Ok(None)) — no test layer prescribed for the Real impl itself.
- Options: (1) integration-test via a constructed AppContext (needs Scraper wiring); (2) implement per spec, pin the behavior contract at the run_with_deps/FakeDeps layer, verify Real composition by code review.
- Decision: Option 2 — RealDeps is a thin facade composition (match get_progress { None → Ok(None) } + find on chapter idx); the migrate/reset/Err-degrade/ordering semantics are pinned by 5 fake-layer tests.
- Why: House style (existing REQ-005 tests) treats RealDeps as un-mocked production wiring; building an AppContext with a live Scraper in unit tests would exceed the seam the codebase established.
- Spec-gap: none.

## [1784441545] p3-f/impl-b
- Situation: Test strategy + supersede record for TASK-b (B5 supersede rule).
- Options: —
- Decision: 17 new named tests in 4 RED/GREEN rounds (9 pure-fn, 1 dao in-memory, 5 fake-deps, 2 message-string). Existing tests received ONLY mechanical adaptation: dao/facade call sites +None, FakeDeps +new fields via ..Default::default() and +current_chapter_name; zero assertion changes. CLI/TUI 「進度重置到第 N 章」 wording replaced by describe_progress output per TASK-b-04 explicit supersede (no test asserted the old string; also removes the idx+1 derivation which is wrong for non-dense idx).
- Why: Each round is one vertical slice per tdd.md §1.2; message strings asserted verbatim (進度已遷移：第2章 破曉（idx 5） / 進度重置：序章 起風之日) per test-effectiveness constraint.
- Spec-gap: exact message punctuation was free ("例：" in ctx); chose the ctx example format verbatim.

## [1784441583] p3-f/review-b
- Situation: Four-tier review of group b (TASK-b-01…b-04, commit dd89755). All C8–C14 + C22 AC met item by item; red_proof present (4 rounds, behavior-absent scaffold assertion failures); green re-run 73/73 full suite, exit 0; warning set re-verified at 3 pre-existing dead_code (byte-identical names to baseline); diff shows zero removed assertion lines in existing tests (mechanical-only adaptation confirmed); no mod.rs touched; timing + rule-precedence + Err-degrade criteria all pinned by named tests.
- Options: (1) advisory with findings; (2) packaged confirm over the untested RealDeps::current_chapter_name composition.
- Decision: tier = advisory. The RealDeps composition is spec-conformant by code review and its behavioral contract (migrate/reset/Err-degrade/ordering) is pinned at the fake-deps seam; ctx's Test section prescribes pure-fn/fake-deps/dao layers only, so no criterion is unmet. Second advisory: 收尾 line's「基線 48 passed」stale (56 pre-b, 73 post-b).
- Why: M-classified task — quality observations route to advisory per contract; no correctness gap, no spec contradiction; #[allow(dead_code)] reconciliation was decision-logged with an A/B warning-set proof.
- Spec-gap: none new beyond the keep-three-fields vs no-new-warnings tension already logged by impl-b.

## [1784442147] p3-f/impl-c
- Situation: (a) Design approach for TASK-c-01/c-02 — cross-source fold.
- Options: (1) dedup inside assemble_rows; (2) pure post-pass fold_rows over assemble_rows output; (3) fold at do_search loop level.
- Decision: (2) per Design section — new variant `HitOrStatus::Folded { hits: Vec<(SearchHit, String)> }`, one-pass fold with HashMap<(name,author),usize> recording first output position; mem::replace upgrade Hit→Folded in the owned output vec; do_search tail becomes fold_rows(assemble_rows(..)).
- Why: assemble_rows body and its 5 tests stay byte-identical (constraint); single-source rows keep Hit variant so C17 is guaranteed by type; index stability holds because out is push-only.
- Spec-gap: none (design was prescribed).

## [1784442147] p3-f/impl-c
- Situation: (b) Adding the Folded variant broke compilation of the existing test req003_scenario1_three_sources_all_hit — its match on &rows[i] had only Hit/StatusLine arms (no wildcard), and the constraint says the 5 assemble_rows tests are 一字不改.
- Options: (1) add a panic arm for Folded; (2) rewrite the match with a wildcard; (3) avoid the new variant (violates Design).
- Decision: (1) mechanical exhaustiveness arm `HitOrStatus::Folded { .. } => panic!(...)` with a comment marking it as such.
- Why: preserves the test's exact semantics (any non-Hit row panics); the literal 一字不改 constraint is impossible to satisfy once the enum gains a variant — minimal mechanical adaptation, no weakening.
- Spec-gap: the spec did not anticipate that extending HitOrStatus forces an edit in one existing test's exhaustive match.

## [1784442147] p3-f/impl-c
- Situation: (c) Same-source duplicate hits of the same book (edge case flagged for logging).
- Options: (1) dedup by source_name inside a fold group; (2) merge as-is, count includes duplicates.
- Decision: (2) — [Hit X(A), Hit X(A)] → Folded hits.len==2, label "2源: A, A"; pinned by test req005_same_source_duplicate_hits_fold_and_count_includes_dup.
- Why: ctx explicitly mandates 照併、計數含重複; also keeps fold_rows a trivial one-pass with no per-group set.
- Spec-gap: label shows the repeated source name twice ("A, A") — display-level dedup unspecified, chose faithful count over cosmetic dedup.

## [1784442147] p3-f/impl-c
- Situation: (d) Test strategy; also how to test Enter-on-Folded and first_hit_idx without a live scraper.
- Options: for Enter: (1) assert via observable append_status path on empty in-memory db; (2) refactor selected_hit extraction into a pure fn. For first_hit_idx: (1) extract pure helper; (2) leave inline (untestable without do_search).
- Decision: Two RED→GREEN slices (c-01 pure fold_rows: 7 tests; c-02 render/interaction: 4 tests). Enter test uses empty db → get_source(hits[0].0.source_url) → None → StatusLine "找不到書源：http://a" pins hits[0] (and asserts http://c absent). Extracted first_hit_idx(&[HitOrStatus]) as a named pure fn (behavior-preserving seam, done in RED with old Hit-only body so the new test genuinely failed, left:2 right:1).
- Why: behavior-through-public-interface (tdd.md §1.1/§1.3 — no mocks of own modules, db is in-memory boundary); RED for fold pinned C15 at 3 rows vs expected 1 (fold absent), exactly the deliverable pin the ctx demanded.
- Spec-gap: none.

## [1784442317] p3-f/review-c
- Situation: Four-tier review of group c (TASK-c-01/c-02, commit 285af40). All C15-C20 + C21 AC met item by item; red_proof present (2 slices, assertion failures with named left/right values; C15 pinned 3-rows-pre-fold vs 1-post-fold per ctx Test section); green re-run 84/84 full suite exit 0; warning set re-verified byte-identical to baseline via touch+rebuild (bin: filename/select_within/chapter_count; test bin 2 since select_within is used by group-a tests); diff shows zero removed test assertion lines; assemble_rows body untouched; only tui/search.rs among production files.
- Options: (1) advisory; (2) packaged confirm (correctness) over the mechanical Folded arm added inside existing test req003_scenario1 (literal 一字不改 constraint).
- Decision: tier = advisory. The constraint is unsatisfiable once HitOrStatus gains a variant (exhaustive match, no wildcard); the arm is mechanical, semantics-preserving (any non-Hit row still panics), and decision-logged as spec-gap by impl-c — a reconciliation, not an unmet criterion.
- Why: M-classified task — quality observations route to advisory per contract; no correctness gap, no spec contradiction. Advisories: folded_label defensive empty branch unpinned (suggest debug_assert), dup-source label "A, A" faithful-count noted, 收尾 baseline line stale (84 now).
- Spec-gap: none new beyond impl-c's logged 一字不改-vs-exhaustiveness gap.

## [1784442722] p3-f/final-review
- Situation: Coverage review of merged tree a687ca0. Tree carried one stray untracked 0-byte file `src/lib.rs` (mtime Jul 14, predates experiment); moving it aside was blocked by the permission classifier.
- Options: (1) refuse to run until clean; (2) run the suite with the stray file present and reason about its effect.
- Decision: (2) — ran `LIBCLANG_PATH=/usr/lib/llvm-18/lib cargo test` twice (14:26:21 and 14:28:25 +08:00), both exit 0, 84/84 bin tests green. The empty lib.rs only adds an empty lib target (0 tests, 0 doc-tests) and cannot mask bin-test failures or add warnings; warning set = exactly the 2 expected dead_code warnings (backup filename, SwitchOutcome chapter_count).
- Why: a 0-byte lib.rs is compile-inert for the bin target where all 84 tests live; refusing would block on a file outside the merged tree.
- Spec-gap: none. Verdict: all REQ-001..006 covered green; C1-C22 all ✅; needs_fixer=false. Advisory: stray src/lib.rs should be deleted before ship; TUI toast composition line itself is pinned only indirectly (describe_progress msg1/msg2 + shelf unit7).
