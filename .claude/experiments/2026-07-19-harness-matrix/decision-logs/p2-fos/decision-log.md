
## [1784438427] p2-fos/spec
- Situation: Item B rule precedence ambiguity — "scan ascending idx; first chapter satisfying the highest-precedence rule wins" can read as single-scan-best-rule-per-position or rule-major three passes.
- Options: (1) single scan, first chapter matching ANY rule wins; (2) three independent passes a→b→c, any match in a higher rule beats any match in a lower rule, scan order breaks ties within a rule.
- Decision: Option 2 (rule-major three passes).
- Why: "highest-precedence rule wins" modifies the rule, not the position; option 1 would let an early rule-c match beat a later exact match, defeating the precedence list's purpose. Pinned by REQ-005 Scenario 4 + a dedicated test.
- Spec-gap: brief sentence is genuinely parseable both ways.

## [1784438427] p2-fos/spec
- Situation: migrated progress_idx must be written inside the single tx (B5), but dao must stay free of matching logic; existing dao tests call update_book_source_tx with 4 args.
- Options: (1) add progress_idx param to existing fn + mechanically adapt existing test call sites; (2) new parallel fn keeping old signature (old fn becomes test-only -> new dead_code warning, violates constraint 5); (3) write migrated idx in a second post-commit write (breaks single-tx atomicity).
- Decision: Option 1 — signature +1 param (progress_idx: i64); existing dao tests get the 5th arg = new TOC first idx, assertions unchanged verbatim.
- Why: B5's supersede clause explicitly covers this: the "always reset to first idx" contract is superseded by B1-B4; the call-site edit is mechanical, every asserted behavior is preserved (int4 still asserts the Reset path).
- Spec-gap: brief constraint 3 (don't modify existing tests) vs a compile-forced signature change — resolved via the B5 supersede rule, logged per its requirement.

## [1784438427] p2-fos/spec
- Situation: what if the pre-tx read-only lookups (get_progress / list_chapters) return Err during migration resolution?
- Options: (1) propagate Err and abort the switch; (2) degrade to Reset (best-effort) and continue.
- Decision: Option 2 — .ok() degrade, documented as the design's only sanctioned error-swallowing point, pinned by a dedicated test (REQ-006 S2).
- Why: migration is best-effort by the brief's own framing; a value-add read failure must not fail a switch that would succeed today. Abort classes stay exactly five.
- Spec-gap: brief step 1 only covers "no progress row / unresolvable name", not read errors.

## [1784438427] p2-fos/spec
- Situation: Item C folding placement — inside assemble_rows or as a post-pass? Extending assemble_rows would make existing scenario1/scenario2 tests fail (they use identical book names across sources).
- Options: (1) fold inside assemble_rows + supersede 2 existing tests; (2) separate pure fold_rows post-pass applied in do_search; existing assemble_rows tests stay valid as unfolded-contract tests.
- Decision: Option 2, plus extending HitOrStatus::Hit with an extra_sources: Vec<String> field instead of adding a new enum variant.
- Why: C6(brief) explicitly allows a post-pass; keeps ALL existing search tests byte-identical (a new variant would break their exhaustive matches at compile time; a new field passes through their .. patterns). Enter-on-folded-row then needs zero code change (primary hit = first occurrence) satisfying C4(brief).
- Spec-gap: none — brief offered both shapes.

## [1784438427] p2-fos/spec
- Situation: hidden invariants discovered while reading code, recorded for the implementer.
- Options: n/a (facts).
- Decision: (1) old TOC MUST be read before the tx — step 2 DELETEs it; (2) chapters.idx is sparse (czbooks volume-row hole), so match results must carry ChapterMeta.index, never the Vec position; (3) existing CLI/TUI success messages use idx+1 as a fake 1-based chapter number — wrong under sparse idx, replaced by chapter-name-based wording in both Reset and Migrated messages; (4) in-code REQ-00x comments belong to a PREVIOUS spec generation — new spec renumbers from REQ-001; implementer must not "fix" old comments; (5) rule c must fail when either side yields no chapter-number token (two Nones must not match); (6) same-source duplicate hits also fold (key excludes source), source-name list not deduped.
- Why: each is a trap that silently breaks a criterion (C8, C12, C13) or invites accidental spec drift.
- Spec-gap: brief silent on 3, 5, 6 — all pinned in requirement.md/test.md.

## [1784440200] p2-fos/impl
- Situation: Item A REQ-001 Scenario 3's literal example string `extract_within(el, "&##第##Chapter ")` expects output `"Chapter 1章 風起"` (with a space after "Chapter"), but `parse_rule` trims each `||`-split piece via `piece.trim()` BEFORE `parse_alt` splits off the `##regex##replacement` tail — so the trailing space in the replacement literal is stripped before it ever reaches `apply_replace`.
- Options: (1) touch `parse_rule`/`parse_alt` to preserve trailing whitespace in the replacement half only; (2) leave `parse_rule`/`parse_alt` untouched (task-a-01 explicitly forbids touching them) and write the test assertion against the verified real output (`"Chapter1章 風起"`, no space).
- Decision: Option 2.
- Why: task-a-01's steps explicitly say "不動 parse_rule / parse_alt / parse_accessor / read_accessor / apply_replace"; REQ-004/C6 requires non-`&` rule behavior to stay byte-identical, and this trim is pre-existing behavior for ALL rules (not `&`-specific), so "fixing" it would be out of scope for this bug fix and would itself be a behavior change. Verified via a standalone rustc snippet that `"&##第##Chapter ".trim()` already drops the space.
- Spec-gap: requirement.md's literal example string doesn't account for this pre-existing trim; logged as a known discrepancy between the spec's illustrative value and actual code behavior, not a functional defect in my fix.

## [1784440200] p2-fos/impl
- Situation: after adding `progress: ProgressOutcome` matching to CLI/TUI handlers, `SwitchOutcome.new_progress_idx` stopped being read anywhere in production code (only in `#[cfg(test)]` assertions), so `cargo build` would emit a NEW dead-code warning beyond the pre-existing baseline.
- Options: (1) keep faking a chapter number from `new_progress_idx + 1` in one of the two handlers just to keep it "used" (contradicts the design's explicit instruction to stop doing this — idx is sparse); (2) add `#[allow(dead_code)]` to the field with a doc comment explaining it's superseded by `progress` but kept for the `new_progress_idx == (Migrated.new_idx | Reset.first_idx)` invariant tests assert.
- Decision: Option 2 — added `#[allow(dead_code)]` on `new_progress_idx`, matching the existing convention already used on `AbortReason`'s unread variants in the same file.
- Why: preserves the measured baseline of exactly 3 pre-existing warnings (verified via `git stash` + clean build: `filename` never read, `select_within` never used, `chapter_count` never read — note this is 3, not the "two" the brief/CLAUDE.md states; logged as a pre-existing discrepancy, not something I introduced).
- Spec-gap: goal.md / EXPERIMENT-BRIEF.md say "existing two dead_code warnings" but the actual pristine worktree (verified via `git stash`) already emits 3 (`filename`, `select_within`, `chapter_count`). I treated "no NEW warnings beyond the pre-existing ones" as the binding constraint (matching the actually-measured baseline of 3), not the specific count "two" — the count itself is stale documentation, not something this spec's scope covers fixing.

## [1784440200] p2-fos/impl
- Situation: FakeDeps in switch_source_core.rs needed two new read-only methods (`get_progress`, `list_old_chapters`) plus recording of the `progress_idx` passed to `switch_source_tx`, while the existing `req005_s2`/`req005_s3` tests construct `FakeDeps { .. }` with only the original 5 fields.
- Options: (1) give every new field a manual default via a `Default` impl and switch existing test constructors to `FakeDeps { ..., ..Default::default() }`; (2) require every test to enumerate all 9 fields explicitly.
- Decision: Option 1 — added `impl Default for FakeDeps` (progress: None, old_toc: empty, no error injection → always resolves to Reset) and updated `req005_s2`/`req005_s3` construction sites to use `..Default::default()`, assertions unchanged.
- Why: this is a mechanical, additive adaptation of test-fixture *construction* (not assertions) — the two existing tests' actual assertions (err message content + `switch_tx_called == false`) are untouched, satisfying B5's "assertions verbatim" bar while keeping the fixture free of an ever-growing field list at every call site.
- Spec-gap: none — design.md explicitly names "FakeDeps 僅機械式補實作兩個新方法 + 簽名適配" as the sanctioned touch surface for these two tests.

## [1784440200] p2-fos/impl
- Situation: `library::dao` existing tests (`int1`, `int2a-d`, `int4`, `empty_new_chapters`) call `update_book_source_tx`/`_with_fault`, which now require a 5th `progress_idx` argument.
- Options: per design.md's B5/C12 supersede-clause authorization — pass `= new TOC's first idx` for tests exercising Reset-path behavior (int2a-d, int4, empty_new_chapters), and a non-first idx for `int1` (used `3`, which happens to equal `new_toc(3,4)`'s first idx anyway) — all assertions kept byte-identical.
- Decision: mechanical +1 argument at every call site, values chosen to match each test's own new_toc's first idx (i.e., these tests exercise "caller resolved Reset" semantics, not migration) — this is the same class of adaptation already pre-authorized in the handoff summary's Item B section.
- Why: no test's asserted behavior changed; `int4`'s core point ("chapter_index matches new TOC's first idx, not hardcoded") still holds verbatim since I passed exactly that idx as `progress_idx`.
- Spec-gap: none — explicitly pre-authorized by task-b-02's "既有 dao 測試...呼叫點補第 5 引數 = 新 TOC 首 idx 後，原斷言逐字通過".

## [1784439535] p2-fos/review
- Situation: Independent opus close-out audit of all three items against A1-A7/B1-B7/C1-C6, spec conformance, DDD layering, and test effectiveness.
- Options: (a) accept impl summary at face value; (b) re-derive every criterion from source + re-run tests + re-run layering greps + verify warning baseline via clean build.
- Decision: (b). Findings below.
- Why: reviewer mandate is independent re-verification, not confirmation.
- Spec-gap: none.
- Findings:
  - Item A (rule.rs): C1-C7 all MET. Self-check precedes Selector::parse in all four element-level (extract_within/select_within) and three doc-level (extract_doc/select_nodes/extract_all_doc) entries. Tests pin named values (self text, @href, @outerHtml/@html, regex-replace, fallback both positions, empty-self fallthrough, missing-attr None, bad-regex Err). A7 bonus present. Regex-replace deviation (trailing-space stripped by pre-existing parse_rule trim) is genuine and correctly out of scope. VERDICT: kept-as-is.
  - Item B (switch_source_core/dao/facade/handlers): C8-C14 all MET. find_migration_target is rule-major three-pass (a>b>c), each returns ChapterMeta.index (sparse-safe). progress_idx flows caller->tx step 4; dao has defensive membership check. run_with_deps tests pin recorded_progress_idx (7 on exact match, first_idx on no-match). REQ-006 S2 error-swallow (get_progress/list_old_chapters Err -> Reset) is the sole sanctioned degrade, tested. 5 abort classes intact, all pre-tx. B6 surfaced on both CLI+TUI via ProgressOutcome match. VERDICT: kept-as-is.
  - Item C (search.rs): C15-C20 all MET. fold_rows is a pure post-pass applied in do_search after assemble_rows; key=(name.trim,author-or-empty.trim); StatusLine passthrough preserves relative position; primary hit = first occurrence (Enter/C18 needs zero change); single-source format byte-identical to legacy. Tests pin fold count, extra_sources contents, position, author None/blank equivalence, same-source dup fold, format multi-source count+names. VERDICT: kept-as-is.
  - Layering: service/*.rs imports no rusqlite/dao (only backup/service uses library::facade — sanctioned exception); library::facade calls no catalog facade. CLEAN.
  - Warning baseline: clean build emits exactly 3 (filename, select_within, chapter_count); select_within confirmed pre-existing in parent bfa0f46. No new warnings. Brief/CLAUDE.md "two" is stale doc; measured baseline (3) is authoritative — concur with impl.
  - Tests: 91 passed / 0 failed (48 baseline + 43 new). Broken-feature falsifiability spot-checked: identity fold_rows / no-op migration / unwired progress_idx would each fail a named-value assertion.
- Result: zero real defects found; no code changes made.
