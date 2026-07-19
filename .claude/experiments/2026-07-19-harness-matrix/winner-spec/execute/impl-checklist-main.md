# Impl Checklist — 2026-07-19-legado-parity

Spec: `.claude/analyze/2026-07-19-legado-parity/`
Context files: `.claude/execute/context/{a,b,c}-ctx.md`
三群組互相獨立（前置群組皆「無」），可任意順序或並行。

| Group | Tasks | Criteria | test_weight | Files | Impl-status | Review-result |
|-------|-------|----------|-------------|-------|-------------|---------------|
| a | TASK-a-01, TASK-a-02 | C1–C7 | full | src/catalog/service/rule.rs | ✅ Green (commit 1296196) | advisory |
| b | TASK-b-01 … TASK-b-04 | C8–C14 | full | src/library/{dao,facade}.rs, src/presentation/handlers/switch_source_core.rs, switch_source.rs, tui/switch_source.rs | ✅ Green (commit dd89755) | advisory |
| c | TASK-c-01, TASK-c-02 | C15–C20 | full | src/presentation/handlers/tui/search.rs | ✅ Green (commit 285af40) | advisory |

## Review notes — group a (p3-f/review-a)

tier: advisory. All C1–C7 met; red_proof present (2 rounds, EmptySelector Err matches root cause); C6 diff-verified (no test lines touched by commit 1296196); constraints hold (no rusqlite/dao imports; warning set identical, 3 pre-existing dead_code).

Findings (advisory, no correctness issue):
- rule.rs:302 (self_selector_in_fallback_chain): C4's lazy-parse deferral is implemented (parse inside per-alt branch) but not observably pinned — `"& || em.x"` still passes if parse were hoisted, since em.x is valid. Suggest adding a case like `extract_within(el, "& || ](bad")` asserting Ok(Some(..)) to pin deferral.
- Checklist line「既有兩條 dead_code 屬預期」is stale: baseline has 3 (filename, select_within, chapter_count) — verified via git-stash build by impl, re-verified at review (3 warnings before/after). Orchestrator should update the 收尾 line to 3.

green_proof:
- test_command: `LIBCLANG_PATH=/usr/lib/llvm-18/lib cargo test` (full suite) + `cargo test catalog::service::rule` (module)
- exit_code: 0
- tests_correspondence: 以下 test 對應 TASK-a-01/a-02 的驗收標準 —
  C1 ← catalog::service::rule::tests::self_selector_returns_own_text;
  C2 ← self_selector_with_accessors;
  C3 ← self_selector_with_regex_replace;
  C4 ← self_selector_in_fallback_chain;
  C5 ← select_within_self_selector;
  C6 ← parse_basic / parse_attr_and_replace / parse_alternatives / extract_text_with_fallback (unmodified, passing);
  C7 ← doc_self_selector_targets_root_element (extract_doc + select_nodes + extract_all_doc);
  邊界 ← self_selector_trims_surrounding_spaces, self_selector_empty_value_falls_through
- output_tail:
  ```
  test catalog::service::rule::tests::parse_alternatives ... ok
  test catalog::service::rule::tests::parse_basic ... ok
  test catalog::service::rule::tests::parse_attr_and_replace ... ok
  test catalog::service::rule::tests::extract_text_with_fallback ... ok
  test catalog::service::rule::tests::doc_self_selector_targets_root_element ... ok
  test catalog::service::rule::tests::self_selector_returns_own_text ... ok
  test catalog::service::rule::tests::self_selector_in_fallback_chain ... ok
  test catalog::service::rule::tests::self_selector_trims_surrounding_spaces ... ok
  test catalog::service::rule::tests::select_within_self_selector ... ok
  test catalog::service::rule::tests::self_selector_with_accessors ... ok
  test catalog::service::rule::tests::self_selector_empty_value_falls_through ... ok
  test catalog::service::rule::tests::self_selector_with_regex_replace ... ok
  test result: ok. 12 passed; 0 failed; 0 ignored; 0 measured; 44 filtered out; finished in 0.00s
  (full suite: test result: ok. 56 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.02s)
  ```

## Review notes — group b (p3-f/review-b)

tier: advisory. All TASK-b-01…b-04 驗收標準 met item by item (C8–C14, C22); red_proof present (4 rounds, behavior-absent scaffolds, assertion failures with named values — not compile errors); existing tests received mechanical-only adaptation (diff shows no removed assertion lines; call sites +None, FakeDeps +fields); no mod.rs touched; warning set byte-identical to baseline (filename / select_within / chapter_count — re-verified at review via cargo build); facade imports no catalog::* (grep: comments only); one reconciliation (`#[allow(dead_code)]` on SwitchOutcome.new_progress_idx) properly decision-logged.

Findings (advisory, no correctness issue):
- switch_source_core.rs:209 (RealDeps::current_chapter_name): the get_progress→list_chapters composition has no direct test — pinned only at the fake-deps layer, composition verified by code review (decision-logged by impl-b). Suggest a future in-memory integration pin when an AppContext test harness exists.
- Checklist 收尾 line「基線 48 passed」is stale twice over: group-a baseline was 56, group-b lands at 73. Orchestrator should track the running total.

green_proof:
- test_command: `LIBCLANG_PATH=/usr/lib/llvm-18/lib cargo test` (full suite)
- exit_code: 0
- tests_correspondence: 以下 test 對應 TASK-b-01…b-04 的驗收標準 —
  C8 ← library::dao::tests::int5_progress_idx_some_migrates_chapter_index (dao half) + switch_source_core::tests::mig1_rule_a_exact_match_non_dense_idx + mig_run_exact_name_migrates_progress;
  C9 ← mig2_rule_b_fullwidth_whitespace_matches + mig2b_whitespace_only_old_name_skips_rule_b (邊界);
  C10 ← mig3_rule_c_number_token_fullwidth_normalized + mig3b_chinese_vs_arabic_numerals_do_not_cross_match + mig3c_tokenless_side_never_matches_rule_c;
  C11 ← int1_update_book_source_tx_happy_path (斷言值不變) + mig4_no_rule_matches_returns_none + mig_run_no_old_progress_resets_to_first_idx (非稠密首 idx 2) + mig_run_unrelated_name_resets;
  C12 ← int2a–d rollback + int3 + req005_s2_fetch_info_fail_aborts_before_tx + req005_s3_fetch_toc_timeout_aborts_before_tx (原樣通過);
  C13/C14 ← msg1_migrated_names_chapter_and_idx_verbatim + msg2_reset_names_first_chapter_verbatim (describe_progress 共用，CLI/TUI 呼叫點 diff 核對);
  邊界 ← mig5_duplicate_names_first_ascending_idx_wins + mig6_higher_rule_beats_lower_rule_at_smaller_idx + mig_run_resolver_err_degrades_to_reset_not_abort + mig_run_resolution_after_toc_check_before_tx (時序);
  C22 ← grep facade/dao 無 catalog import
- output_tail:
  ```
  test presentation::handlers::switch_source_core::tests::mig_run_unrelated_name_resets ... ok
  test presentation::handlers::switch_source_core::tests::mig3b_chinese_vs_arabic_numerals_do_not_cross_match ... ok
  test presentation::handlers::switch_source_core::tests::mig3_rule_c_number_token_fullwidth_normalized ... ok
  test presentation::handlers::switch_source_core::tests::mig3c_tokenless_side_never_matches_rule_c ... ok
  test library::dao::tests::get_novel_by_book_url_returns_some_when_present ... ok
  test library::dao::tests::get_novel_by_book_url_returns_none_when_absent ... ok
  test library::dao::tests::empty_new_chapters_returns_err_without_touching_db ... ok
  test library::dao::tests::int2b_rollback_at_delete_chapters ... ok
  test library::dao::tests::int2d_rollback_at_update_progress ... ok
  test library::dao::tests::int4_progress_chapter_index_matches_new_first_idx ... ok
  test library::dao::tests::int2a_rollback_at_update_novels ... ok
  test library::dao::tests::int3_no_cascade_progress_row_survives ... ok
  test library::dao::tests::int5_progress_idx_some_migrates_chapter_index ... ok
  test library::dao::tests::int2c_rollback_at_insert_chapters ... ok
  test library::dao::tests::int1_update_book_source_tx_happy_path ... ok
  test presentation::handlers::tui::search::tests::req003_scenario5_esc_in_results_mode_transitions_to_menu ... ok
  test presentation::handlers::tui::menu::tests::moving_clears_stub_msg ... ok
  test presentation::handlers::tui::menu::tests::enter_on_shelf_transitions_to_shelf_screen ... ok
  test presentation::handlers::tui::menu::tests::k_from_zero_wraps_to_last ... ok
  test presentation::handlers::tui::menu::tests::j_moves_down_and_wraps ... ok
  test presentation::handlers::tui::menu::tests::enter_on_settings_sets_stub_msg_and_stays ... ok
  test presentation::handlers::tui::reader::tests::unit4b_direct_mode_m_quits ... ok
  test presentation::handlers::tui::menu::tests::m_key_is_stay_no_panic ... ok
  test presentation::handlers::tui::menu::tests::enter_on_quit_item_returns_quit ... ok
  test presentation::handlers::tui::menu::tests::q_returns_quit ... ok
  test presentation::handlers::tui::search::tests::req003_scenario4_esc_in_input_mode_transitions_to_menu ... ok
  test presentation::handlers::tui::reader::tests::unit4a_menu_mode_m_to_menu ... ok

  test result: ok. 73 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.03s
  ```

## Review notes — group c (p3-f/review-c)

tier: advisory. All TASK-c-01/c-02 驗收標準 met item by item (C15–C20 + C21 + edges); red_proof present (2 slices, named assertion failures with left/right values — C15 pinned at 3 rows pre-fold → 1 post-fold, exactly the deliverable pin ctx's Test section demanded); assemble_rows body untouched (diff-verified: only removed lines are the inline first_hit_idx extraction and the do_search tail); zero test assertion lines removed; only production file touched is tui/search.rs (constraint); warning set byte-identical to baseline (bin: filename / select_within / chapter_count — re-verified via touch+rebuild at review; test bin shows 2 because select_within is used by group-a tests); same-source-duplicate edge decided 照併/count-includes-dup per ctx and pinned + decision-logged.

Findings (advisory, no correctness issue):
- search.rs:530 (req003_scenario1 match): the mechanical Folded panic arm technically breaks the literal 「一字不改」constraint, but the constraint is unsatisfiable once the enum gains a variant (exhaustive match, no wildcard). Semantics preserved (any non-Hit row still panics); properly decision-logged as spec-gap. Orchestrator should note the spec-gap for final review — no action needed.
- search.rs folded_label: defensive empty-slice branch (returns "") is unreachable under the len>=2 invariant and unpinned — acceptable as defense; a debug_assert would make the invariant louder.
- Folded label for same-source dup shows "2源: A, A" (display-level dedup unspecified; faithful-count chosen and logged). If UX later wants dedup'd display, that is a new criterion, not a defect.
- 收尾 line「基線 48 passed」remains stale (group-c lands at 84 = 73 + 11).

green_proof:
- test_command: `LIBCLANG_PATH=/usr/lib/llvm-18/lib cargo test` (full suite)
- exit_code: 0
- tests_correspondence: 以下 test 對應 TASK-c-01/c-02 的驗收標準 —
  C15 ← presentation::handlers::tui::search::tests::req005_c15_three_sources_same_book_fold_to_one_row (fold half) + req006_folded_label_shows_name_author_count_and_all_sources (顯示半邊，exact string 「超維術士 / 牧狐 [3源: A, B, C]」);
  C16 ← req005_c16_different_author_or_name_stays_separate + req005_c16_author_none_empty_blank_share_key (邊界);
  C17 ← req005_c17_fold_lands_at_first_occurrence_single_source_stays_hit;
  C18 ← req006_c18_enter_on_folded_acts_on_first_source_hit (空 db 可觀察路徑：狀態列含 http://a、不含 http://c);
  C19 ← req005_c19_statusline_relative_position_preserved + req005_fold_rows_empty_input (邊界);
  C20 ← req003_scenario1_three_sources_all_hit + req003_scenario2/3 + req003_assemble_rows_empty_input + req003_assemble_rows_zero_hits (原樣通過，僅機械性 exhaustiveness arm);
  C21 ← 84/84 綠 + 警告集 A/B 核對 (bin 3 條 pre-existing dead_code，無新增);
  REQ-006 first_hit_idx ← req006_first_hit_idx_treats_folded_as_hit_row (含首列 Folded 情境);
  邊界 ← req005_same_source_duplicate_hits_fold_and_count_includes_dup + req006_folded_label_no_author_shows_dash
- output_tail:
  ```
  test presentation::handlers::tui::search::tests::req005_c15_three_sources_same_book_fold_to_one_row ... ok
  test presentation::handlers::tui::search::tests::req005_c16_author_none_empty_blank_share_key ... ok
  test presentation::handlers::tui::search::tests::req005_c16_different_author_or_name_stays_separate ... ok
  test presentation::handlers::tui::search::tests::req005_c17_fold_lands_at_first_occurrence_single_source_stays_hit ... ok
  test presentation::handlers::tui::search::tests::req005_c19_statusline_relative_position_preserved ... ok
  test presentation::handlers::tui::search::tests::req005_fold_rows_empty_input ... ok
  test presentation::handlers::tui::search::tests::req005_same_source_duplicate_hits_fold_and_count_includes_dup ... ok
  test presentation::handlers::tui::search::tests::req006_first_hit_idx_treats_folded_as_hit_row ... ok
  test presentation::handlers::tui::search::tests::req006_folded_label_no_author_shows_dash ... ok
  test presentation::handlers::tui::search::tests::req006_folded_label_shows_name_author_count_and_all_sources ... ok
  test presentation::handlers::tui::search::tests::req003_scenario1_three_sources_all_hit ... ok
  test presentation::handlers::tui::search::tests::req003_scenario4_esc_in_input_mode_transitions_to_menu ... ok
  test presentation::handlers::tui::search::tests::req006_c18_enter_on_folded_acts_on_first_source_hit ... ok

  test result: ok. 84 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.04s
  ```

## 收尾全域檢查（final review 用）

- [ ] `cargo test` 全綠（基線 48 passed；預期 48 + 新增 N）
- [ ] 無新編譯警告（既有兩條 dead_code 屬預期）
- [ ] `grep -rn "rusqlite\|::dao" src/catalog/service src/library/service` 零命中（C22）
- [ ] `grep -rnE "use crate::(catalog|library)::facade" src/catalog src/library` 零命中（C22）
- [ ] goal.md C1–C22 逐條字面核對（C{n} 僅在測試鷹架成立、產線路徑死路 = 未達成）
- [ ] conventional commits 提交
