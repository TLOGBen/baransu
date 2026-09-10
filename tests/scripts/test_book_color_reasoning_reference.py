#!/usr/bin/env python3
"""Structural + regression assertions for TASK-book-02 — the new dataviz
color-reasoning reference document (`references/color-reasoning.md`) and its
read-step wiring into `/book`'s statistical-type Render path.

/book is a prose-driven skill (SKILL.md + reference *.md, executed by an LLM
agent, not a running app) — see tests/scripts/test_book_chart_statistical_type.py
for the established precedent of asserting prose/reference-file content via
structural/regex checks. This suite follows that same pattern.

Covers (per ctx.md's Test block + task-book.md's 3 acceptance criteria):
  (a) the new file exists and follows the writing-principles.md-mirrored
      structural shape: numbered entries, each with a "Claude defaults to..."
      framing sentence, a "*Why it fails*:" causal explanation, and a
      Before/After table; all 3 named anti-patterns present; the
      categorical/ordinal/sequential/diverging/status color-job distinction
      present; a pointer to color_distance.py present.
  (b) the read-step wiring is scoped to the statistical type only — the
      reference to `color-reasoning.md` appears inside SKILL.md's
      "Statistical-type color-capability degrade" section and nowhere else
      in the file (so it never triggers for the existing 13 types).
  (c) regression — none of the 13 existing type-*.md files changed, and
      unrelated SKILL.md sections are still present unchanged.
"""

from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path

THIS_FILE = Path(__file__).resolve()
WORKTREE_ROOT = THIS_FILE.parents[2]
BOOK_SKILL_DIR = WORKTREE_ROOT / "plugins" / "baransu" / "skills" / "book"
SKILL = BOOK_SKILL_DIR / "SKILL.md"
DIAGRAM_TYPES_DIR = BOOK_SKILL_DIR / "references" / "diagram-types"
TYPE_STATISTICAL = DIAGRAM_TYPES_DIR / "type-statistical.md"
COLOR_REASONING = BOOK_SKILL_DIR / "references" / "color-reasoning.md"
COLOR_DISTANCE_SCRIPT = "plugins/baransu/skills/_shared/scripts/color_distance.py"

EXISTING_13_TYPES = [
    "architecture", "flowchart", "sequence", "state", "er", "timeline",
    "swimlane", "quadrant", "nested", "tree", "layers", "venn", "pyramid",
]

# task-book.md acceptance criterion 2 (verbatim-required anti-patterns).
REQUIRED_ANTI_PATTERNS_ZH = ["雙軸圖表", "彩虹漸層", "身份色僅靠顏色不給圖例"]

# ctx.md Files field / Content grounding (a): the five color-job distinction.
COLOR_JOBS = ["categorical", "ordinal", "sequential", "diverging", "status"]


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


def git_diff_touched(path: Path) -> bool:
    """True if `path` differs from HEAD (tracked-file regression guard)."""
    rel = path.relative_to(WORKTREE_ROOT)
    result = subprocess.run(
        ["git", "-C", str(WORKTREE_ROOT), "diff", "--name-only", "HEAD", "--", str(rel)],
        capture_output=True, text=True, check=True,
    )
    return bool(result.stdout.strip())


class TestColorReasoningFileExistsAndMirrorsTemplateShape(unittest.TestCase):
    """(a) — structural shape mirrors writing-principles.md."""

    def setUp(self) -> None:
        self.assertTrue(COLOR_REASONING.exists(), f"{COLOR_REASONING} must exist")
        self.text = COLOR_REASONING.read_text(encoding="utf-8")
        self.lower = self.text.lower()

    def test_toc_and_framing_present(self):
        self.assertIn("## Contents", self.text)
        self.assertIn("Claude", self.text)

    def test_read_scope_note_present(self):
        # task-book.md AC3: the doc's own framing should be honest about when
        # it is read (statistical type only), not just SKILL.md's wiring.
        self.assertIn("statistical", self.lower)

    def test_at_least_eight_numbered_entries(self):
        entries = re.findall(r"\*\*\d+\.\s", self.text)
        self.assertGreaterEqual(
            len(entries), 8,
            "expected >= 8 numbered entries (5 color jobs + 3 anti-patterns)",
        )

    def test_before_after_table_shape_mirrors_writing_principles(self):
        count = self.text.count("| Before (default) | After (correction) |")
        self.assertGreaterEqual(
            count, 8,
            "each numbered entry should carry a Before/After table, per "
            "writing-principles.md's confirmed shape",
        )

    def test_claude_default_framing_sentence_per_entry(self):
        occurrences = len(re.findall(r"Claude defaults to", self.text))
        self.assertGreaterEqual(occurrences, 8)

    def test_why_it_fails_causal_explanation_present(self):
        why_blocks = re.findall(r"\*Why it fails\*:(.+)", self.text)
        self.assertGreaterEqual(len(why_blocks), 8)
        for block in why_blocks:
            self.assertIn(
                "because", block.lower(),
                "why-it-fails must name a causal mechanism, not just assert wrongness",
            )

    def test_three_named_anti_patterns_present(self):
        for phrase in REQUIRED_ANTI_PATTERNS_ZH:
            self.assertIn(phrase, self.text, f"missing required anti-pattern: {phrase!r}")

    def test_color_job_distinction_present(self):
        for job in COLOR_JOBS:
            self.assertIn(job, self.lower, f"missing color-job distinction: {job!r}")

    def test_ordinal_vs_categorical_mistake_named_as_its_own_entry(self):
        # ctx.md: "using categorical hues where an ordinal ramp is needed is
        # a common default mistake worth its own entry".
        self.assertIn("not categorical hues", self.lower)

    def test_pointer_to_color_distance_script_present(self):
        self.assertIn("color_distance.py", self.text)
        self.assertIn(COLOR_DISTANCE_SCRIPT, self.text)


class TestReadStepWiredIntoSkillOnlyForStatisticalType(unittest.TestCase):
    """(b) — read-step wiring scoped to the statistical-type degrade section."""

    def setUp(self) -> None:
        self.full = SKILL.read_text(encoding="utf-8")

    def test_declared_branch_reads_color_reasoning_file(self):
        region = _extract_region(
            self.full,
            "Statistical-type color-capability degrade",
            ["\n### 5. Core Asset Protocol"],
        )
        self.assertIn("color-reasoning.md", region)

    def test_read_step_scoped_only_to_statistical_degrade_section(self):
        region_start = self.full.find("Statistical-type color-capability degrade")
        region_end = self.full.find("### 5. Core Asset Protocol")
        self.assertNotEqual(region_start, -1)
        self.assertNotEqual(region_end, -1)
        matches = list(re.finditer(re.escape("color-reasoning.md"), self.full))
        self.assertTrue(matches, "no reference to color-reasoning.md found in SKILL.md")
        for match in matches:
            self.assertTrue(
                region_start <= match.start() < region_end,
                "read-step reference to color-reasoning.md must stay scoped inside "
                "the statistical-type degrade section — a reference outside it "
                "would trigger for the existing 13 types too",
            )

    def test_forward_reference_punt_removed(self):
        # TASK-book-01 planted a forward-reference punt clause pointing at
        # this task; the "串接" step replaces it with the concrete read step.
        self.assertNotIn("statistical-chart color-reasoning task territory", self.full)


class TestRegressionExistingTypesAndUnrelatedSkillSectionsUnchanged(unittest.TestCase):
    """(c) — none of the 13 existing type-*.md files or unrelated SKILL.md
    sections changed meaning."""

    def test_thirteen_type_files_not_touched_by_this_task(self):
        # `architecture` is exempted: the book-diagrams change legitimately
        # extends type-architecture.md's Layout conventions with the
        # scale-levels cluster (Level 1 figure → board → sister boards).
        # `tree` is exempted: once Org Chart became a dedicated type routed
        # above Tree in §4.9, type-tree.md's Best-for dropped its "org chart"
        # first-match bait (re-scoped to "module hierarchy").
        for name in [t for t in EXISTING_13_TYPES if t not in ("architecture", "tree")]:
            path = DIAGRAM_TYPES_DIR / f"type-{name}.md"
            with self.subTest(type=name):
                self.assertTrue(path.exists())
                self.assertFalse(
                    git_diff_touched(path),
                    f"type-{name}.md must not be modified by TASK-book-02",
                )

    def test_unrelated_skill_sections_still_present(self):
        full = SKILL.read_text(encoding="utf-8")
        anchors = [
            "### 2. Generate HTML structure",
            "### 6. Multi-format pipeline (PDF / PPTX)",
            "pre-render visual self-check",
            "### 7. Write the output file",
        ]
        for anchor in anchors:
            self.assertIn(anchor, full, f"unrelated SKILL.md section anchor missing: {anchor!r}")

    def test_l1_l2_degrade_lines_unaffected(self):
        # Guard that only the Declared bullet changed — the Undeclared/L1/L2
        # branch lines (owned by TASK-book-01) must survive verbatim.
        full = SKILL.read_text(encoding="utf-8")
        self.assertIn(
            "fall back to the existing single-hue `--accent` ramp already used "
            "by every other diagram type — no new token, no new color.",
            full,
        )
        self.assertIn(
            "This threshold starts at 2, not 3", full,
        )

    def test_type_statistical_cross_reference_pointer_in_layout_conventions(self):
        text = TYPE_STATISTICAL.read_text(encoding="utf-8")
        layout = _extract_region(text, "## Layout conventions", ["\n## Anti-patterns"])
        self.assertIn("color-reasoning.md", layout)

    def test_type_statistical_series_color_discipline_note_still_intact(self):
        # Regression guard against test_book_chart_statistical_type.py's
        # TestSeriesColorDisciplineDoesNotBypassDegrade contract: appending a
        # cross-reference pointer must not remove the declared/undeclared/
        # degrade wording or introduce the forbidden "only ever needs" phrase.
        text = TYPE_STATISTICAL.read_text(encoding="utf-8")
        layout = _extract_region(text, "## Layout conventions", ["\n## Anti-patterns"])
        start = layout.find("Series color discipline")
        self.assertNotEqual(start, -1)
        end = layout.find("\n- **", start + 1)
        note = layout[start: end if end != -1 else len(layout)]
        note_lower = note.lower()
        self.assertIn("declared", note_lower)
        self.assertIn("undeclared", note_lower)
        self.assertNotIn("only ever needs", note_lower)


if __name__ == "__main__":
    unittest.main()
