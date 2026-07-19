# NovelReader — Legado-Parity Work Brief (Experiment Edition)

You are working on `novel-looker`, a Rust terminal novel reader (legado 3.0 CLI port).
Your worktree is your entire world: **never read or write outside it**. Read `CLAUDE.md`
and `README.md` in the worktree root before touching code.

Deliver ALL THREE items below. Definition of done for the whole brief:
every numbered criterion met, `cargo test` fully green, work committed
(conventional commits, one or more commits).

Build note: `target/` is pre-warmed. If a build ever needs bindgen:
`LIBCLANG_PATH=/usr/lib/llvm-18/lib cargo test`. Tests are offline — never add
tests that hit the network.

---

## Item A (bug) — rule DSL `&` self-selector

`src/catalog/service/rule.rs`: the `&` selector ("the current element itself")
errors with `EmptySelector` because `Selector::parse(&alt.selector)` runs before
the `alt.selector == "&"` self-check (see `extract_within`). Legado sources rely
on current-element rules; this must work.

Criteria:
- **A1** `extract_within(el, "&")` returns the element's own text.
- **A2** `extract_within(el, "&@href")` (any attribute / `html` / `outerHtml` accessor) reads from the element itself.
- **A3** `extract_within(el, "&##<regex>##<repl>")` applies the regex replace to the self-extracted value.
- **A4** `||` fallback works with `&` in any position, e.g. `"em.missing || &"` resolves to self; `"& || em.x"` uses self first.
- **A5** `select_within(el, "&")` returns `vec![el]` (no error).
- **A6** All pre-existing tests still pass unchanged (`catalog::service::rule::tests` and everything else).
- **A7** (bonus) document-level rules (`extract_doc` / `select_nodes` / `extract_all_doc`) treat `&` as the document root element instead of erroring.

## Item B (feature) — switch-source best-effort progress migration

Today `switch-source` always resets `progress.chapter_index` to the new TOC's
first idx. Legado preserves reading position across source switches. Implement
best-effort migration by chapter-name matching.

Algorithm (fixed — deviations must be logged as decisions):
1. Before the DB transaction, resolve the OLD current chapter's name (from the
   old TOC + current progress). No progress row / unresolvable name → fallback (step 4).
2. Scan the NEW TOC in ascending idx; the first chapter satisfying the highest-
   precedence rule wins. Precedence:
   a. exact name equality;
   b. equality after stripping ALL Unicode whitespace from both names;
   c. chapter-number token equality: extract via regex
      `第\s*([0-9０-９一二三四五六七八九十百千零〇两兩]+)\s*[章回節节卷]` (first capture group)
      from both names, normalize full-width digits to half-width, compare as strings.
      (Arabic-vs-Chinese-numeral cross-matching is NOT required; doing it is bonus.)
3. On match: `chapter_index` = matched NEW idx, `scroll_offset` = 0.
4. On no match: current behavior (first chapter idx of new TOC, `scroll_offset` = 0).

Criteria:
- **B1** Exact-name match migrates `chapter_index` to the matched new idx (remember: idx values are NOT dense 0..N-1 — never assume 第N章 → idx N-1).
- **B2** Whitespace-variant names match (rule b).
- **B3** Same 第N章 number with different tail text matches (rule c).
- **B4** No match → resets to new first idx exactly as today.
- **B5** All five pre-tx abort classes and single-transaction atomicity are untouched; every existing dao/switch-source test still passes (a pre-existing test may be adapted ONLY if its asserted behavior is explicitly superseded by these criteria — record it in the decision log).
- **B6** Outcome is surfaced to the user on BOTH paths: `SwitchOutcome` conveys migrated-vs-reset (and the matched chapter name/idx when migrated); the CLI handler prints it and the TUI toast shows it (e.g. 「進度已遷移：第12章 風起」 / 「進度重置到首章」).
- **B7** New unit/integration tests cover B1–B4 and B6 at the pure-logic level (the existing `SwitchSourceDeps` fake / dao in-memory tests show the house style).

## Item C (UX) — multi-source search result folding

Today the TUI cross-source search shows the same book once per source. Fold
duplicates (legado aggregates search results per book).

Criteria:
- **C1** Hit rows whose `(name.trim(), author-or-empty.trim())` are equal collapse into ONE row; its display text includes the book name, author, the SOURCE COUNT and ALL source names (format free, e.g. `超維術士 - 牧狐 [3源: A, B, C]`).
- **C2** Same name but different author (or vice versa) stays separate.
- **C3** A collapsed row keeps the list position of its first occurrence; a single-source row renders as today.
- **C4** Enter on a collapsed row: minimum required behavior = act on the FIRST source's hit (source iteration order). A source-picker UI is bonus, not required.
- **C5** StatusLine rows (errors / timeouts) are unaffected and keep their positions relative to surviving rows.
- **C6** The folding logic lives in a pure, unit-testable helper (extend `assemble_rows` or add a post-pass); new unit tests cover C1/C2/C3/C5; all existing search tests still pass (same supersede rule as B5).

---

## Global constraints (scored)

1. **Architecture adherence**: the DDD 4-context × 5-layer invariants in
   CLAUDE.md are hard rules — `service/*.rs` never imports rusqlite or any dao;
   facades never call another context's facade (sole exception backup→library);
   cross-context composition only in `presentation/handlers/`; keep PL types in
   `mod.rs` logic-free; follow existing local patterns (pure helpers for testable
   logic, `SwitchSourceDeps`-style seams).
2. **Test effectiveness**: tests must pin behavior — a test that still passes
   when the feature is broken scores zero. Assert named values, not "is ok".
3. Do not modify existing passing tests except under the explicit supersede rule (B5/C6).
4. Do not touch `book-sources/`, `.claude/skills/`, or files unrelated to the three items.
5. The two pre-existing `dead_code` warnings are expected; do not introduce NEW warnings.

## Mandatory experiment protocol (not scored, but required)

**Timestamps** — first action when you start, last action when you finish:
```bash
echo "<AGENT_ID> start $(date +%s)" >> .exp/timestamps   # / end
```

**Decision log** — append to `.exp/decision-log.md` (create if missing). Every
agent MUST log, at minimum: (a) per item, the design approach chosen and the
alternatives rejected; (b) every situation this brief or the spec does not
cover, and what you decided; (c) any deviation from the algorithm/criteria and
why; (d) your test strategy choice. Entry format:

```markdown
## [<unix-ts>] <AGENT_ID>
- Situation: <what came up>
- Options: <realistic alternatives considered>
- Decision: <what you chose>
- Why: <reasoning in 1-3 sentences>
- Spec-gap: <what the brief/spec left unspecified here, or "none">
```

`<AGENT_ID>` is given to you in your dispatch prompt. Log honestly — the log is
research data, never graded for polish.
