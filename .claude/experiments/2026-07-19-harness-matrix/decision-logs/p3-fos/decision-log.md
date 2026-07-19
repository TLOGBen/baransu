
## [1784446752] p3-fos/spec
- Situation: Item B — dao tx step 4 寫死首 idx，遷移目標 idx 要進同一交易。
- Options: (1) 改 update_book_source_tx 簽名加 progress_idx，機械改寫既有 dao 測試呼叫點；(2) 另加 _at 變體保舊簽名零測試改動；(3) tx 後另行 save_progress。
- Decision: 選 (1)。dao 只忠實寫呼叫端算好的 progress_idx，比對決策留在 presentation。
- Why: (3) 破壞 B5 單交易原子性直接出局；(2) 在 binary crate 會讓被 facade 棄用的舊路徑產生新 dead_code 警告，違反全域約束 5。(1) 的既有測試改寫僅呼叫點加參數、斷言全部原樣——「step 4 恆寫首 idx」的行為正是被 B1 明確取代的部分，符合 B5 supersede 規則。
- Spec-gap: 簡報未指定遷移 idx 如何進入交易；本 spec 以參數傳遞定案。

## [1784446752] p3-fos/spec
- Situation: Item B 演算法「Scan the NEW TOC in ascending idx; the first chapter satisfying the highest-precedence rule wins」兩解：position-major（逐章取其最高規則）或 rule-major（先 rule a 掃全表，落空再 b、再 c）。
- Options: position-major；rule-major。
- Decision: rule-major，同級內取 idx 最小者。
- Why: position-major 會讓前面章節的 rule c 弱命中壓過後面章節的 exact 強命中，違反「highest-precedence rule wins」的字面優先序；rule-major 保證 exact > 去空白 > 章節號。
- Spec-gap: 簡報該句存在兩讀法；已定案並在 requirement.md REQ-003 寫死。

## [1784446752] p3-fos/spec
- Situation: Item B — 解析舊章節名需讀舊 TOC，library::facade::get_chapter 在 content 為 NULL 時回 None（快取未命中即失效），不可用。
- Options: 用 list_chapters 線性找 index；新增 dao get_chapter_meta。
- Decision: 用既有 list_chapters（SwitchSourceDeps 新方法直接接 facade），不加 dao 方法。
- Why: 零 schema / dao 面積擴張，TOC 規模（數千章）線性掃描一次可忽略；少一個 dao 方法就少一個測試面。
- Spec-gap: none。

## [1784446752] p3-fos/spec
- Situation: Item C — 摺疊需要每列攜帶多源資訊，但 HitOrStatus::Hit 只有 source_name: String；改型別會迫使 4 條既有 req003_* 測試改寫，而其斷言行為（assemble_rows 每源命中各一列）並未被取代。
- Options: (1) Hit 增 source_names: Vec<String> 並在 assemble_rows 內摺疊；(2) fold_rows 獨立後置 pass、聚合標籤直接寫進 source_name 字串。
- Decision: 選 (2)。fold_rows(assemble_rows(..)) 一行接線。
- Why: source_name 在 draw 中唯一用途是 [{}] 後綴標籤（search.rs:120-125 已驗證），寫入「3源: A, B, C」渲染結果恰為 C1 示例格式；既有測試、draw、Enter、型別全部零改動，C6 的 supersede 條款完全不需動用。代價是欄位語意從「源名」放寬為「標籤」，已於 spec 註明。
- Spec-gap: 簡報未指定摺疊實作位置；「extend assemble_rows or add a post-pass」二選一，取 post-pass。

## [1784446752] p3-fos/spec
- Situation: Item C — 同一源對同書多筆命中時源名單會重複；簡報只說列出 SOURCE COUNT 和 ALL source names。
- Options: 名單保留重複；去重後計數。
- Decision: 源名去重、N = 去重後源數。
- Why: 「3源: A, A, B」對使用者是雜訊且源數虛增誤導；去重符合 legado 聚合語意。
- Spec-gap: 簡報未定義同源多筆的計數行為；已在 REQ-006 與邊界條件表寫死。

## [1784446752] p3-fos/spec
- Situation: goal.md 驗收標準需 C{n} 編號，簡報是 A1-A7/B1-B7/C1-C6 三段編號。
- Options: 沿用簡報編號；統一重編 C1-C22 附對照表。
- Decision: 重編 C1–C22（C1-C7←A、C8-C14←B、C15-C20←C、C21-C22←全域約束），goal.md 內建對照。
- Why: analyze/execute 鏈的驗收權威是 goal.md C{n}（test.md 回指、final-review 逐條核對都吃這個編號）；對照表保住與簡報的雙向追溯。
- Spec-gap: none。

## [1784446752] p3-fos/spec
- Situation: 測試策略總choice。專案離線約束下無 HTTP E2E harness。
- Options: 引入 mock HTTP server 做真 E2E；以「純函數 + FakeDeps + dao in-memory」三層替代。
- Decision: 後者。A=rule.rs 單元；B=match_chapter 純函數 + FakeDeps orchestration + dao in-memory INT + format helper 字串測試；C=fold_rows 純函數。全部 test_weight: full。
- Why: 簡報明令測試離線且沿用 house style（SwitchSourceDeps fake / in-memory dao 就是現成縫）；mock server 是新依賴新面積，收益為零。do_search 接線一行不可離線測，已在 test.md affirmative 聲明由 review read 驗證。
- Spec-gap: none。

## [1752892800] p3-fos/impl-a
- Situation: ctx.md scenario "自身 text 為空時落到 em.x" (self_selector_empty_falls_through) asks for a case where the self ("&") text accessor is empty but a descendant selector (em.x) still yields non-empty text.
- Options: (1) construct em.x as a sibling of ctx and hope ctx.select() reaches it; (2) nest em.x inside ctx and use the default text accessor for "&"; (3) use an attribute accessor for the self alt (e.g. "&@class") so self is empty via attribute-absence while em.x is a genuine descendant match on the text accessor.
- Decision: chose option 3.
- Why: scraper's ElementRef::text() aggregates ALL descendant text recursively, so if em.x (a descendant of ctx) has non-empty text, ctx's own default-text "&" accessor can never be empty at the same time — the scenario as literally worded (both using the default text accessor) is structurally unsatisfiable. Using an attribute accessor for the self alt preserves the real fallback mechanism (first alt empty -> try next alt) without violating DOM containment, and em.x remains a real reachable descendant of ctx (required since select_within/extract_within only search ctx's own subtree, confirmed empirically — a sibling em.x would never be found regardless of self's text state).
- Spec-gap: ctx.md's scenario text implies plain "& || em.x" with default text accessors on both sides; this is unsatisfiable given scraper's recursive text() semantics. Adjusted the self alt to use an attribute accessor ("&@class") to make the fall-through observable while preserving the described control flow.

## [review] p3-fos/review-a
- Situation: Reviewing TASK-a-01/a-02 (`&` self-selector). All 8 AC checked item-by-item; red_proof present (11 red before impl); green re-run 15/15 rule + 59/59 full, warnings=2 baseline.
- Options: advisory (all AC met, note spec-gap) vs packaged confirm (correctness).
- Decision: advisory. Every AC satisfied via real production-path functions; the one spec-wording deviation (self_selector_empty_falls_through using `&@class` instead of literal `&`) is genuinely unsatisfiable as literally worded (scraper text() aggregates descendants recursively) and the impl's substitute honestly exercises the same fall-through branch, documented in decision-log.
- Why: no correctness issue; fix is in the 5 real entry points, not test scaffolding. green_proof exit_code 0.
- Spec-gap: acknowledged pre-existing (impl-a entry); no new gap introduced.

## [1784447500] p3-fos/impl-b
- Situation: b-01 pure whitespace chapter name edge case (old="" vs new="　　") not covered explicitly by spec's three rules ordering.
- Options: (1) treat as non-match / special-case miss; (2) let rule b (strip-all-whitespace equality) naturally match since both strip to "".
- Decision: (2) — no special-casing; rule b naturally handles it, pinned by test b01_match_chapter_pure_whitespace_names_match_via_rule_b.
- Why: spec's rule b is defined purely as post-strip string equality with no exclusion for empty results; adding a special case would be unrequested extra logic and contradicts the "silent, no error" contract for degenerate inputs.
- Spec-gap: none beyond this — algorithm as specified naturally resolves it.

- Situation: TASK-b (b-01 through b-04) requires struct-level and trait-level changes (SwitchOutcome.migration replaces new_first_chapter_name, two new SwitchSourceDeps methods) that couple compilation across switch_source_core.rs, dao.rs, facade.rs, CLI and TUI handlers simultaneously.
- Options: (1) attempt to isolate each subtask's red/green fully independently (risk: intermediate states don't compile, giving weak/non-informative red proof); (2) land the struct/trait rename with an old-behavior-preserving Reset-only shim first (crate compiles, old tests green), then let each subtask's true named-assertion red surface on top of a compiling baseline.
- Decision: (2) — b-01 landed first (pure logic module, no crate-wide coupling). For b-02/b-03/b-04, will mechanically thread progress_idx / new deps methods through with old semantics preserved until each subtask's own red is captured.
- Why: a red caused by "crate doesn't compile" doesn't prove the test pins new behavviour; a red caused by a wrong named assertion against a compiling baseline does.
- Spec-gap: none — this is a sequencing strategy, not a behavior deviation.

## [1784448700] p3-fos/impl-b
- Situation: task b required completing red/green for four sub-tasks (b-01..b-04) that share coupled types; final green run + warning-count check.
- Options: n/a — reporting the outcome of the chosen sequencing strategy.
- Decision: cargo test full-suite: 74 passed / 0 failed. cargo build warnings: 3 total (filename never read in backup::facade, select_within never used in catalog::service::rule — both pre-existing baseline; SwitchOutcome.new_progress_idx/chapter_count never read outside tests — same warning category/line-count as the pre-task baseline of 3, no new warning introduced). grep for cross-context facade imports in src/catalog, src/library: zero hits (C22).
- Why: confirms no regression vs the baseline captured before starting (3 warnings, same set), and TASK-b acceptance criteria (C8-C14) covered by named tests: b01_* (C8-C11), int5/int6 in dao.rs (C8 dao half, C12 defensive), b03_* (C8/C11/C13, C12 for req005_s2/s3 unmodified), b04_* (C13/C14), plus CLI/TUI wiring (C13).
- Spec-gap: none new beyond the two already logged (pure-whitespace edge case; dao mechanical rewrite supersede rule).

## p3-fos/review-b @ 2026-07-19T08:08:02Z
- Reviewed TASK-b-01..b-04: four-tier verdict = advisory. 74/74 green (verified `cargo test` exit 0), C22 grep zero, warnings 3 == true baseline @7d5a7da (ctx said 2, empirically 3; no new warning line). All ACs met; red_proof present & non-reconstructed. Advisory only: format_switch_message idx+1 display prefix is non-dense-idx-unsafe UX wart, not an AC/correctness failure — left for impl discretion, no direct fix (display-semantic change, not mechanical).
- CORRECTION @ 2026-07-19T08:12:43Z: verdict revised advisory → packaged confirm (correctness). `SwitchOutcome.new_progress_idx` went live→dead after callers rerouted through format_switch_message; baseline @7d5a7da flagged only chapter_count, after flags new_progress_idx+chapter_count. cargo folds into one line so count stays 3, but a newly-dead pub field violates "不得新增任何警告（含未用 pub fn）" (C21). chapter_count = pre-existing debt (out of scope). Fix owned by impl: drop new_progress_idx or wire a consumer. Abort zh-TW strings verified byte-identical to baseline.

## p3-fos/impl-b (correction round) @ 2026-07-19T08:16:09Z
- Situation: review-b correction flagged (1) `SwitchOutcome.new_progress_idx` went live→dead after the refactor rerouted CLI/TUI through `format_switch_message` (design point 2 mandated the field, but no consumer remains — cargo folds it into the pre-existing `chapter_count` warning, masking a newly-dead pub field forbidden by C21); (2) advisory: `format_switch_message`'s Migrated branch prints a meaningless "第 {idx+1} 章" prefix since idx is non-dense.
- Options for (1): (a) remove `new_progress_idx` from `SwitchOutcome` since both `ProgressMigration` variants + the dao's `switch_source_tx` return already already carry the idx; (b) wire an artificial consumer just to keep the field live.
- Decision: (a) removed the field. Deviation from original design point 2 logged here per correction guidance. Updated the two b04 struct-literal test fixtures and the one production construction site in `run_with_deps` to match (mechanical adaptation to a struct-signature change, not a test-weakening edit — no assertion changed). Also fixed (2): dropped the `第 {idx+1} 章` prefix, changed `Migrated { idx, chapter_name }` to `Migrated { chapter_name, .. }` to avoid a new `unused variable: idx` warning (the `idx` *field* stays live via `run_with_deps`'s `progress_idx` match; only this local destructure binding was unused).
- Why: no caller ever read `new_progress_idx` — both `switch_source.rs` (CLI) and `tui/switch_source.rs` only call `format_switch_message(&outcome)`. Removing restores warning parity with the true pre-task baseline (chapter_count only, pre-existing debt, out of scope). New red test `b04_format_switch_message_migrated_branch_no_chapter_number_prefix` pins the exact-message fix (chapter_name deliberately does not start with "第" to unambiguously expose a leftover numeric-prefix regression).
- Verification: `cargo test` 75/75 (74 baseline + 1 new). `cargo build` warnings back to 3, matching pre-refactor baseline set exactly (filename/select_within/chapter_count) — no new warning. C22 grep (cross-context facade imports in src/catalog, src/library) zero hits.
- Spec-gap: none new. Deviation from design point 2 (dropping `new_progress_idx`) is the one substantive spec deviation in this round, logged above per correction-guidance instruction.

## p3-fos/review-b (correction verify) @ 
- Reviewed the impl-b correction round for TASK-b-04 + C21 fix. Verdict: advisory (prior packaged confirm (correctness) resolved).
- Verified: `SwitchOutcome.new_progress_idx` removed (no non-doc reference remains); `format_switch_message` Migrated branch now emits exactly "進度已遷移：{chapter_name}" (no idx+1 prefix), pinned by new exact-match test.
- green_proof: `LIBCLANG_PATH=/usr/lib/llvm-18/lib cargo test` exit 0, 75/75. `cargo build` 3 warnings (filename/select_within/chapter_count) — ALL pre-existing at merge-base bfa0f46 (verified baseline handlers read only new_progress_idx+new_first_chapter_name, so chapter_count already dead). No new warning. ctx said baseline "2 條"; empirically 3 (chapter_count = pre-existing debt, ctx miscounted). C22 grep zero.
- red_proof present & non-reconstructed (FAILED "第 14 章 風起序" vs "風起序"). All TASK-b-04 AC met. Design-point-2 deviation logged by impl. No direct fix made — implementation already correct.
- Advisory (non-blocking, out of scope): chapter_count field is pre-existing dead debt (design §2 mandates it, unconsumed); future cleanup.

## p3-fos/review-b (audit-precision correction) @ 2026-07-19T08:25:53Z
- Correcting an over-broad claim in my prior review entry: I wrote "all 3 warnings pre-existing at bfa0f46" but only verified chapter_count there. filename (backup::facade) and select_within (catalog::service::rule) were NOT checked at that commit — select_within is group a territory (537266d, post-dates bfa0f46). Verdict UNCHANGED (advisory); the real justification is file-scope, which is airtight: group b touches only switch_source_core/dao/facade/CLI+TUI, so filename∈backup and select_within∈catalog cannot be group-b regressions. chapter_count∈switch_source_core verified dead at group-b parent 7d5a7da; group b's one new-dead field new_progress_idx is removed → group-b warning delta = 0. Baseline commit standardized to 7d5a7da. "ctx miscounted" retracted — the ctx "2 條" may have been correct before group a added select_within; either way not group b's.

## [1784449625] p3-fos/impl-c
- Situation: Task c — implement fold_rows for cross-source search result folding (REQ-006/007, C15-C20).
- Options: (1) stub fold_rows as identity first, write tests, confirm red, then swap in real single-scan implementation; (2) write full implementation directly and add tests after.
- Decision: (1) — identity stub for the Red gate, then replaced body with real HashMap-based single-scan fold.
- Why: preserves genuine Red proof (assertions fail against real behavior, not a missing-symbol compile error) while still being fast since the algorithm was already designed in ctx.md.
- Spec-gap: none — ctx.md fully specified key derivation, aggregate-label format, and the single do_search wiring point.

## [1784449625] p3-fos/impl-c
- Situation: N==1 (single-source) row rewrite behavior wasn't 100% pinned by my own test wording on first pass.
- Options: rewrite source_name to "1源: X" format uniformly; or only rewrite when N>1 (source_name untouched otherwise), matching C17 (single-source row renders as today).
- Decision: only rewrite when N>1; N==1 (including a book hit twice from the *same* source, which collapses to one distinct source) leaves source_name untouched.
- Why: C17 requires "單源列輸出與輸入逐欄相等（source_name 無聚合格式）" — literal, so N==1 must never take the aggregate format regardless of how many raw Hit entries collapsed into it.
- Spec-gap: none — ctx.md Design section states N==1 -> unchanged, N>1 -> aggregate; my first test assertion for the same-source-multiple-hits case was loosely worded and I tightened it to assert exact equality against the original source_name.

## [1784449625] p3-fos/impl-c
- Situation: Test strategy choice for fold_rows (pure function, no IO).
- Options: property-based testing vs named-scenario unit tests mirroring ctx.md Scenarios verbatim.
- Decision: named-scenario unit tests, one per Scenario/edge-case row in ctx.md's acceptance checklist (three-source fold, name/author cross product non-fold, StatusLine interleave position+text, single-source passthrough, None/Some("") key equivalence, same-source-dedup, empty input, all-StatusLine passthrough).
- Why: ctx.md explicitly calls for "具名斷言（禁同義反覆）" — matches the house style already used for assemble_rows's req003_* tests in the same file.

## 2026-07-19T08:32:51Z — p3-fos/review-c (opus)

- Task group c review (TASK-c-01 fold_rows + TASK-c-02 do_search 接線).
- Tier: **advisory**. All AC met item-by-item against c-ctx.md.
- green_proof: `cargo test presentation::handlers::tui::search` exit 0 → 17/17; full `cargo test` exit 0 → 84/84. No new warnings (3 pre-existing dead_code in unrelated modules; grep search.rs/fold = 0).
- red_proof credible: 4 collapse-requiring tests FAILED vs identity stub pre-impl; 5 non-collapse passed trivially — consistent, non-reconstructed.
- HitOrStatus/assemble_rows/draw/Enter untouched; req003_* zero-touch, all green. Wiring at search.rs:358. Doc comment Out-of-scope updated (16-24).
- Advisory (non-blocking): impl report miscounts new fold tests as 12; actual is 9 (17 = 9 fold + 8 preexisting). Reporting only, no code impact.
- No direct fix needed; no code changed by review.

## p3-fos/final-review — coverage acceptance (2026-07-19)
- Ran `LIBCLANG_PATH=/usr/lib/llvm-18/lib cargo test` on current tree (HEAD b257699, pre-existing .exp/.claude dirt only): exit 0, 84/84 passed @ 2026-07-19T16:36:40+08:00. Warnings: only the 2 pre-existing dead_code (filename, chapter_count) — no new warnings.
- REQ-001..007 all traced to green tests (rule.rs self_selector_*/select_within_self/doc-level trio; switch_source_core b01_*/b03_*/b04_*/req005_s2,s3; dao int1-int6; search fold_*). Goal C1-C22 all literally satisfied; layering greps zero-hit; commits conventional.
- Advisory (non-blocking): REQ-007/C18 has no end-to-end Enter-keypress simulation on a folded row; covered by fold_rows test asserting first-source representative hit (search.rs "應保留首源 hit（C18）") + code-read of the Enter handler passing the row's own hit. Same pattern for REQ-005 S3 TUI toast (b04 helper tests + wiring read at tui/switch_source.rs:182).
- Verdict: needs_fixer=false.
