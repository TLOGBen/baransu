#!/usr/bin/env python3
"""Structural + regression assertions for TASK-book-03 — the narrowly-scoped
declared-statistical-chart-container exception added to `/book`'s existing
single-chromatic-accent rule (perception-guide.md Anti-Slop #8 + SKILL.md's
pre-render checklist item #4), per REQ-004 Scenarios 1-3.

/book is a prose-driven skill (SKILL.md + reference *.md, executed by an LLM
agent, not a running app) — see tests/scripts/test_book_chart_statistical_type.py
for the established precedent of asserting prose/reference-file content via
structural/regex checks. This suite follows that same pattern.

TASK-book-03's real scope is narrow: the declaration-state read mechanism
(`{project_root}/tokens.css` line 1's `; chart-capability: <N>` header, read
via `design/scripts/check.py`'s `_parse_chart_capability_header` contract) was
already implemented by TASK-book-01/02 at SKILL.md:356-361. This task only
updates RULE TEXT in two files so the existing rule knows about the exception,
without duplicating or re-implementing the read mechanism. Covers (per ctx.md's
Test block):
  (a) perception-guide.md Anti-Slop #8 documents the container-scoped exception
  (b) the exception text explicitly excludes prose/captions outside the
      `<figure>` boundary and every other section/diagram type
  (c) fail-closed language is present (missing/malformed tokens.css ->
      undeclared, no silent multi-color pass-through)
  (d) SKILL.md checklist item #4 references the same exception, not a
      divergent one
  (e) regression — SKILL.md:356-361 (the existing declared/undeclared read +
      degrade logic) and check.py are untouched; Anti-Slop items 1-7 and the
      warm-gray-neutral sub-rule inside #8 are unchanged
"""

from __future__ import annotations

import hashlib
import unittest
from pathlib import Path

THIS_FILE = Path(__file__).resolve()
WORKTREE_ROOT = THIS_FILE.parents[2]
BOOK_SKILL_DIR = WORKTREE_ROOT / "plugins" / "baransu" / "skills" / "book"
SKILL = BOOK_SKILL_DIR / "SKILL.md"
PERCEPTION_GUIDE = BOOK_SKILL_DIR / "references" / "perception-guide.md"
CHECK_PY = (
    WORKTREE_ROOT / "plugins" / "baransu" / "skills" / "design" / "scripts" / "check.py"
)

# Snapshot taken BEFORE TASK-book-03 touched any file (out-of-scope guard —
# check.py is explicitly not part of this task's file scope). A content hash
# is used instead of `git diff` because check.py already carries uncommitted
# changes from earlier tasks (TASK-design-01/02) in this working tree, so
# `git diff --name-only HEAD` would report it as touched regardless of this
# task's own edits.
# Re-pinned after the /design audit fix (Check C slug→prefix-family mapping +
# Check E HTML-comment stripping — the shipped google-design preset previously
# failed its own lint with 43 violations). That fix is intentional and outside
# TASK-book-03's scope question; the pin below reflects check.py post-fix.
# Re-pinned again after the field-smoke audit fix (legacy per-file mode:
# Markdown inline-code exemption — the 紙 preset's own DESIGN.md documents the
# bans in backtick-quoted prose and previously failed its own 紙-sanity.sh
# gate with 7 false violations). Likewise intentional and outside
# TASK-book-03's scope question; the pin below reflects check.py post-fix.
CHECK_PY_SHA256_BEFORE_TASK = (
    "4c5d8326b13f94722cb4d53b2989ed5d2e586bbec8c3a95811a5e779334d317f"
)

# Verbatim text of SKILL.md's existing "Statistical-type color-capability
# degrade" section (lines ~356-361 at task start) — TASK-book-01/02's already-
# working declaration-read + Declared/Undeclared/L1/L2 branch logic. This task
# must not modify a single character of it.
DEGRADE_HEADER_PARAGRAPH = (
    "**Statistical-type color-capability degrade (undeclared-style fallback)**: "
    "when Layer 2 resolves a section to the `statistical` type (§4.9/§4.10), "
    "before writing that section's SVG, Render checks "
    "`{project_root}/tokens.css` line 1's header for the `; chart-capability: "
    "<N>` field written by `/baransu:design` (declared vs undeclared per "
    "`design/scripts/check.py`'s `_parse_chart_capability_header` contract):"
)

DECLARED_BULLET = (
    "- **Declared** (field present) → before writing the section's SVG, Render "
    "reads `references/color-reasoning.md` (the categorical / ordinal / "
    "sequential / diverging / status color-job distinction, plus the dual-axis "
    "/ rainbow-gradient / identity-color-without-legend anti-patterns) and "
    "applies its guidance when choosing the section's palette, then validates "
    "the chosen colors via `color_distance.py`'s CVD-separation check "
    "(TASK-shared-01, already wired)."
)

UNDECLARED_BULLET_OPEN = (
    "- **Undeclared** (the default; no field present — matching every "
    "invocation that never ran `--chart-capability`) → apply this degrade so "
    "the section never emits an undeclared multi-color palette. Pick "
    "**exactly one** of the two branches below per section — they are "
    "mutually exclusive, never mixed, never guessed past the content shape, "
    "and together cover every case with no silent gap between them (不開豁免):"
)

L1_BULLET = (
    "  - Content expressible as a single trend / single data series (exactly "
    "one line, one bar family, depth conveyed by shade alone) → **L1**: fall "
    "back to the existing single-hue `--accent` ramp already used by every "
    "other diagram type — no new token, no new color."
)

L2_BULLET = (
    "  - Content that must distinguish 2 or more mutually-unrelated identities "
    "(independent series — including exactly 2 — that do not share a common "
    "trend/comparison axis and cannot be told apart by shade depth alone) → "
    "**L2**: degrade to small-multiples (render N separate single-accent "
    "diagrams, one per series, laid out side by side) or a `table.cmp` "
    "comparison table, whichever the section's existing §3 component-selection "
    "rule already picks for that content shape. This threshold starts at 2, "
    "not 3 — an exactly-2-series undeclared section is never left unrouted "
    "between L1 and L2."
)

# Regression anchors — one verbatim spot-check per pre-existing Anti-Slop item
# 1-7 (must survive unchanged; TASK-book-03 only edits item #8).
ANTI_SLOP_1_7_ANCHORS = [
    "1. **Fake `::before` en-dash / hyphen bullets** → default LLM rendering, zero brand",
    "2. **Round-dot `•` bullets next to CJK** → reads childish, breaks print register → none",
    "3. **ASCII arrows / straight quotes / printed italic** → keyboard defaults, not editorial",
    "4. **Filler opener** (\"In today's rapidly evolving…\" / 「擁抱／打造／賦能／重構」) → delays",
    "5. **Caption restating the figure/title** → echo adds no information → none. Pass test",
    "6. **Emoji / icon as section marker** → fakes hierarchy type should carry → sparing inline",
    "7. **`rgba()` tag/chip background** → WeasyPrint composites alpha into a double-rectangle",
]

# Verbatim text of the existing "One chromatic accent only" clause and the
# "Warm-gray neutrals only" sub-rule inside item #8 — must survive unchanged.
ONE_CHROMATIC_ACCENT_CLAUSE = (
    "**One chromatic accent only.** Every coloured element (links, `sec-num`, "
    "emphasis words,\n     `1px` left rule) uses `var(--accent)`; total "
    "accent-painted area ≤ 5% of body. Emphasis\n     is **colour OR weight, "
    "never both** (combining the two breaks Kami's single-weight voice)."
)

WARM_GRAY_NEUTRAL_CLAUSE = (
    "**Warm-gray neutrals only.** Every neutral gray must be warm (`R≥G>B`); "
    "cold gray\n     (`R≤G≤B`) and pure neutral (`R=G=B`) are banned."
)

WARM_WARNING_TOKEN_EXCEPTION_CLAUSE = (
    "Only legitimate exception: pre-existing warm warning tokens (e.g. "
    "changelog breaking\n     badge `--breaking-bg`/`--breaking-fg`, both warm "
    "`R>G>B`). No exception for body accents."
)


def _extract_region(text: str, start_marker: str, end_markers: list[str]) -> str:
    start = text.find(start_marker)
    assert start != -1, f"marker not found: {start_marker!r}"
    body = text[start:]
    end = len(body)
    for marker in end_markers:
        idx = body.find(marker, len(start_marker))
        if idx != -1:
            end = min(end, idx)
    return body[:end]


def anti_slop_8_region(text: str) -> str:
    return _extract_region(
        text,
        "8. **Accent over-paint / cold-gray neutrals**",
        ["\n## SVG Strategy by Type"],
    )


class TestAntiSlop8DocumentsDeclaredStatisticalChartException(unittest.TestCase):
    """(a) — Anti-Slop #8 now documents the container-scoped exception."""

    def setUp(self) -> None:
        self.assertTrue(PERCEPTION_GUIDE.exists())
        self.full = PERCEPTION_GUIDE.read_text(encoding="utf-8")
        self.region = anti_slop_8_region(self.full)
        self.lower = self.region.lower()

    def test_exception_named_and_scoped_to_statistical_chart_type(self):
        self.assertIn("declared-statistical-chart container exception", self.lower)
        self.assertIn("statistical", self.lower)
        self.assertIn('<figure class="diagram">', self.region)

    def test_exception_marked_additional_not_replacing_warm_warning_exception(self):
        self.assertTrue(
            "does not replace or loosen" in self.lower
            or "additional" in self.lower,
            "new exception must be documented as additive, not a replacement "
            "of the pre-existing warm-warning-token exception",
        )

    def test_exception_gated_on_same_skill_md_check_not_a_new_one(self):
        # REQ-004 Scenario 3 / ORCHESTRATOR-CONFIRMED CONSTRAINT: must cite
        # the exact existing mechanism (SKILL.md Stage 3 §4's statistical-type
        # color-capability degrade check, via check.py's
        # _parse_chart_capability_header), and explicitly disclaim inventing
        # a second, parallel declaration-reading mechanism.
        # (The citation used to be line-number-based — "skill.md:356" — which
        # is brittle and had already drifted; the audit replaced it with the
        # stable section anchor asserted below.)
        self.assertIn("skill.md stage 3 §4", self.lower)
        self.assertIn("statistical-type color-capability degrade", self.lower)
        self.assertIn("tokens.css", self.lower)
        self.assertIn("chart-capability", self.lower)
        self.assertIn("_parse_chart_capability_header", self.region)
        self.assertTrue(
            "not a second" in self.lower or "not a separate" in self.lower,
            "must explicitly disclaim being a new/separate declaration check",
        )

    def test_fail_closed_language_present(self):
        # REQ-004 Scenario 3 / task-book.md AC4 / design.md 錯誤處理策略 bullet 4.
        self.assertIn("undeclared", self.lower)
        self.assertIn("malformed", self.lower)
        self.assertTrue(
            "never silently" in self.lower or "no silent" in self.lower,
            "must explicitly state missing/malformed tokens.css never silently "
            "permits multi-color",
        )


class TestExceptionScopedInsideContainerOnly(unittest.TestCase):
    """(b) — the exception explicitly excludes prose/captions outside the
    figure boundary, and every other section/diagram type."""

    def setUp(self) -> None:
        self.full = PERCEPTION_GUIDE.read_text(encoding="utf-8")
        self.region = anti_slop_8_region(self.full)
        self.lower = self.region.lower()

    def test_excludes_prose_and_caption_outside_figure_boundary(self):
        self.assertIn("<figcaption>", self.region)
        self.assertTrue(
            "prose" in self.lower and "outside" in self.lower,
            "must explicitly state the section's own surrounding prose/caption "
            "outside the <figure> boundary is NOT exempt",
        )

    def test_excludes_every_other_section(self):
        self.assertIn("every other section", self.lower)

    def test_excludes_every_other_diagram_type(self):
        self.assertTrue(
            "every other diagram type" in self.lower
            or "non-statistical types" in self.lower,
            "must explicitly state every other (non-statistical) diagram type "
            "is NOT exempt",
        )

    def test_excludes_undeclared_capability_statistical_chart(self):
        # A statistical-type section under an undeclared style must stay on
        # the existing L1/L2 degrade — the new exception must not be misread
        # as loosening that branch too.
        self.assertTrue(
            "l1" in self.lower and "l2" in self.lower,
            "must reference the existing L1/L2 degrade to clarify undeclared "
            "statistical charts stay excluded from the new exception",
        )

    def test_no_exception_heading_present(self):
        self.assertIn("no exception outside the container", self.lower)


class TestAntiSlop1Through7AndWarmGraySubruleUnchanged(unittest.TestCase):
    """(e, partial) — regression: items 1-7 and the warm-gray-neutral
    sub-rule inside #8 are unchanged; the pre-existing warm-warning-token
    exception and the one-chromatic-accent clause also survive verbatim."""

    def setUp(self) -> None:
        self.full = PERCEPTION_GUIDE.read_text(encoding="utf-8")

    def test_anti_slop_items_1_through_7_unchanged(self):
        for anchor in ANTI_SLOP_1_7_ANCHORS:
            with self.subTest(anchor=anchor):
                self.assertIn(anchor, self.full)

    def test_warm_gray_neutral_subrule_unchanged(self):
        self.assertIn(WARM_GRAY_NEUTRAL_CLAUSE, self.full)

    def test_one_chromatic_accent_clause_unchanged(self):
        self.assertIn(ONE_CHROMATIC_ACCENT_CLAUSE, self.full)

    def test_warm_warning_token_exception_clause_unchanged(self):
        self.assertIn(WARM_WARNING_TOKEN_EXCEPTION_CLAUSE, self.full)


class TestSkillChecklistItem4ReferencesSameException(unittest.TestCase):
    """(d) — SKILL.md's pre-render checklist item #4 references the SAME
    exception documented in perception-guide.md, not a divergent one."""

    def setUp(self) -> None:
        self.assertTrue(SKILL.exists())
        self.full = SKILL.read_text(encoding="utf-8")
        marker = "4. **Single accent**"
        start = self.full.find(marker)
        self.assertNotEqual(start, -1, "checklist item #4 not found")
        end = self.full.find("\n5.", start)
        self.assertNotEqual(end, -1, "checklist item #5 not found (end marker)")
        self.item4 = self.full[start:end]
        self.lower = self.item4.lower()

    def test_item4_references_declared_statistical_chart_container_exception(self):
        self.assertIn("declared-statistical-chart container exception", self.lower)

    def test_item4_still_cites_anti_slop_8(self):
        self.assertIn("perception-guide anti-slop #8", self.lower)

    def test_item4_mentions_figure_container_boundary(self):
        self.assertTrue(
            "<figure>" in self.item4 or "figure" in self.lower,
            "checklist item #4 must reference the <figure>/SVG container boundary",
        )

    def test_item4_exception_name_matches_perception_guide_verbatim(self):
        # Cross-file consistency: both documents must use the exact same
        # exception name so a reader/self-check gate cannot mistake this for
        # two divergently-defined exceptions.
        guide_text = PERCEPTION_GUIDE.read_text(encoding="utf-8").lower()
        self.assertIn("declared-statistical-chart container exception", guide_text)
        self.assertIn("declared-statistical-chart container exception", self.lower)


class TestRegressionSkillDegradeLogicAndCheckPyUntouched(unittest.TestCase):
    """(e) — SKILL.md:356-361 (the existing declaration-read/degrade logic)
    and check.py are untouched by this task."""

    def setUp(self) -> None:
        self.full = SKILL.read_text(encoding="utf-8")

    def test_degrade_header_paragraph_unchanged(self):
        self.assertIn(DEGRADE_HEADER_PARAGRAPH, self.full)

    def test_declared_bullet_unchanged(self):
        self.assertIn(DECLARED_BULLET, self.full)

    def test_undeclared_bullet_open_unchanged(self):
        self.assertIn(UNDECLARED_BULLET_OPEN, self.full)

    def test_l1_bullet_unchanged(self):
        self.assertIn(L1_BULLET, self.full)

    def test_l2_bullet_unchanged(self):
        self.assertIn(L2_BULLET, self.full)

    def test_check_py_content_hash_unchanged(self):
        actual = hashlib.sha256(CHECK_PY.read_bytes()).hexdigest()
        self.assertEqual(
            actual, CHECK_PY_SHA256_BEFORE_TASK,
            "check.py is explicitly OUT of TASK-book-03's file scope — it "
            "must not be modified by this task",
        )


if __name__ == "__main__":
    unittest.main()
