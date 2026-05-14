# Changelog

All notable changes to the **baransu** Claude Code plugin.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
within the patch line that Claude Code's plugin cache observes.

## [Unreleased]

_Nothing yet._

## [1.4.4] — 2026-05-14

### Added (`/baransu:review`)
- **Hard stops sweep** — Stage 6.5 aggregate gate after balance check.
  Four required items (Unverified claims / Destructive auto-execution /
  Unknown identifier in target / Dependency changes) plus one optional
  item (Injection / hardcoded secret, listed only when
  `security-reviewer` was not dispatched). Any hit pins the relevant
  finding to `需判斷` and forbids balance-downgrade to advisory.
- **Sign-off receipt** — structured tail after the prose body. Eight
  aligned fields: `files`, `scope`, `depth`, `perspectives`,
  `hard_stops`, `new_tests`, `doc_debt`, `e2e_status`. Field semantics
  pinned in SKILL.md so they don't drift over time.
- **Hard-stops-sweep checklist** rendered alongside the prose body.
  Required items always listed; Optional item omitted when
  `security-reviewer` ran in Stage 4 (no duplicate enforcement).

### Changed
- Sourced from Waza `/check` skill (read material captured under
  `.claude/read/material/check-review-before-you-ship/`, digest under
  `.claude/learn/digests/waza-check-skill-code-review.md`).

## [1.4.3] — 2026-05-14

### Added (`/baransu:hunt`)
- **Side-effect rule** in Instrumentation: log changing observed
  behavior is direct evidence of a timing / lifecycle / concurrency
  problem, not a logging side-effect to dismiss.
- **Scope Blast Mode** — new section after Confirm or Discard. After
  root cause is confirmed, grep the repo for the pattern signature;
  for each match record `fix` / `leave: <reason>` / `unsure:
  <question>` in the case file's Scope Blast section. Success report's
  `迴歸守護` line cites that section by id (e.g.
  `HUNT-YYYY-NNN §3`).
- **Repeated Regression Mode** — new section after Bisect Mode. When
  user provides a "good" screenshot / version / fixture as reference
  oracle, 5-step flow: list symptoms with original wording → identify
  oracle → define pass/fail check → name precise delta → cross-
  reference Hard Rule "Same symptom recurs after fix" if symptom
  remains.
- **Hard Rules +2**:
  - "Fix plan or current diff touches 6 or more files (without a
    Scope Blast pattern justification) → Stop before adding the 6th
    file; narrow back or route to `/baransu:analyze`."
  - "Someone (user or agent) deflects suspicion from a specific area
    (semantic trigger, not literal string match) → Treat as a signal;
    re-examine the deflected area with one targeted instrument."

### Added (`/baransu:think`)
- **Two-tier mode selection in Step 0**:
  - Tier 1: Plan vs Evaluation (kind)
  - Tier 2 (Plan only): Lightweight vs Full (depth)
- **Evaluation Mode** main section: Kill / Keep / Pivot verdicts,
  triggered by Waza's seven canonical phrases plus disambiguation
  vs `/baransu:hunt`. Each verdict requires three reasons grounded
  in the user's real constraints.
- **Memory-type mapping** rule in Stage D Premise validation:
  `fact` → D, `pattern`/`learning` → E,
  `decision`/`preference`/`principle` → F. Includes "current state
  overrides memory" and CLAUDE.md global authority notes.
- **Gotchas table refactor**: 6 existing + 4 Waza counter-examples
  consolidated into a What-happened / Rule two-column table (11 rows
  total); User-fatigue prose retained above the table; fixed prior
  Option 2/3 numbering typo.

### Internal
- SKILL.md size for `/think`: 357 → 435 lines (budget ≤ 465);
  for `/hunt`: 227 → 266 lines.
- Waza materials archived under `.claude/read/material/waza-hunt/`,
  `.claude/read/raw/waza-hunt/`, `.claude/read/raw/waza-think/`,
  `.claude/learn/digests/waza-hunt-skill-diagnose-before-fix-
  debugging-methodology.md`.

## [1.4.2] — 2026-05-13

### Changed (`/baransu:codex-skill-transfer`)
- `transfer.py`: +145 lines distributing improvements to the one-way
  port pipeline from Claude Code skills / plugins / marketplaces to
  Codex format (SKILL.md / batch / plugin → agent-stub TOMLs).

## [1.4.1] — 2026-05-13

### Added (`/baransu:book`)
- **GATE-L viewBox containment** in `validate-output.ts`: iterates
  `<rect>` / `<line>` / `<circle>` / `<ellipse>` / `<text>` in every
  SVG and asserts each renderable geometric edge falls inside the
  viewBox (0.5 px tolerance). Skips `defs` / `marker` / `pattern` /
  `clipPath` / `mask` / `symbol` and descendants of transformed
  groups. Catches arithmetic errors where `x + width` or `y + height`
  spills past viewBox bounds — browsers render fine
  (`overflow: visible`) but pipeline screenshots / PDFs crop.
- **`install-deps.ts` cheerio path**: added, so the first GATE run
  after a fresh checkout no longer fails with `MODULE_NOT_FOUND` from
  `validate-output.ts`'s cheerio import.

### Changed (`/baransu:book`)
- `verify-render.py`: `has_paper` probe now uses
  `[class*="paper"]` selector instead of literal `.paper`; matches
  `kami-paper-body` / `kami-paper` / any preset's `*-paper-*`
  variants (was preset-naive, only handled Kami's bare-class case).

### Added (`/baransu:design`)
- **紙 preset applied to project root**: `tokens.css` +
  `DESIGN.md` + `DESIGN.html` + `design-cores/` 21 files +
  `slide-cores/` 21 files + `紙-sanity.sh`.
- CLAUDE.md design block upgraded v1.2 → v1.3 canonical
  (adds `slide-cores/` reference and canonical 36-name vocabulary
  markers per `/design` Stage 0 spec).

## [1.4.0] — earlier (baseline-parity milestone)

### Added
- v1.4.0 baseline-parity milestone reaches 100.0% across
  REQ-001 ~ REQ-012.
- `baseline-parity-score.py` (REQ-012).
- `/baransu:review` v1.4.0 audit findings folded back as score
  hardening + security advisory.

### Internal
- Numerous incremental tasks (`TASK-finalize-01` through
  `TASK-finalize-03`, `TASK-ct-*`, `TASK-cg-*`, `TASK-layouts-*`)
  shaped the design + book pipeline up to baseline-parity.
