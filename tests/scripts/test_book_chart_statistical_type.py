#!/usr/bin/env python3
"""Structural + regression assertions for TASK-book-01 — /book's new 14th chart
type ("統計圖表" / `statistical`), wired into the two linked tables inside
`references/svg-rendering-rules.md` (§4.9 first-match decision tree, §4.10
reference-lookup table), plus the L1/L2 undeclared-capability degrade branch
documented in SKILL.md's Stage 3 §4 render flow.

/book is a prose-driven skill (SKILL.md + reference *.md, executed by an LLM
agent, not a running app) — see tests/scripts/test_design_chart_capability_skill.py
for the established precedent of asserting prose/reference-file content via
structural/regex checks. This suite follows that same pattern.

Covers (per ctx.md's Test block, REQ-001 Scenarios 1/3 + acceptance criteria):
  (a) statistical-feature content (axis/legend/multi-datapoint) routes to the
      new type — §4.10's 14th row + the new type-statistical.md reference file
  (b) existing-13-type priority tie-break holds — §4.9's 7 structural rows are
      still positioned to win first-match ties against the 7 statistical rows
  (c) the L1/L2 degrade branch selection logic is documented in SKILL.md and
      testable via structural assertion
  (d) regression — none of the existing 13 types' rows/content changed meaning
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
SVG_RULES = BOOK_SKILL_DIR / "references" / "svg-rendering-rules.md"
DIAGRAM_TYPES_DIR = BOOK_SKILL_DIR / "references" / "diagram-types"
NEW_TYPE_FILE = DIAGRAM_TYPES_DIR / "type-statistical.md"

EXISTING_13_TYPES = [
    "architecture", "flowchart", "sequence", "state", "er", "timeline",
    "swimlane", "quadrant", "nested", "tree", "layers", "venn", "pyramid",
]

# The 7 pre-existing structural §4.9 rows (data shape, chosen chart) — must
# survive verbatim (content unchanged; order may move as a block).
STRUCTURAL_ROWS = [
    ("2×2 strategic positioning", "Quadrant"),
    ("Hierarchical data depth ≥ 2", "Tree"),
    ("Process with decision branches", "Flowchart"),
    ("Cross-role process ≥ 3 actors", "Swimlane"),
    ("2-3 cluster sets overlapping", "Venn"),
    ("System components + connections", "Architecture"),
    ("Timeline + milestones", "Timeline"),
]

# The 7 previously-orphaned §4.9 statistical rows — Data shape column must
# survive verbatim; Chosen chart column is expected to now resolve to the
# unified `statistical` type instead of a dangling name.
ORPHANED_DATA_SHAPES = [
    "OHLC / per-day price",
    "+/- contributions summing",
    "One series, sums to ~100%, items ≤ 6",
    "One series, sums to ~100%, items ≥ 7",
    "Two or more time series",
    "One time series, dominated by large changes",
    "Multi-category snapshot at one time, 2+ series",
]

ORPHANED_ORIGINAL_NAMES = [
    "Candlestick", "Waterfall", "Donut", "Horizontal Bar", "Line", "Bar",
    "Grouped Bar",
]

# Original 13 §4.10 rows — full verbatim lines (content must not change).
ORIGINAL_410_ROWS = [
    "| architecture | system overview / data-flow / integration map / infra topology / components + connections | `references/diagram-types/type-architecture.md` | `status: complete` |",
    '| flowchart | decision logic / algorithm steps / "Should I…?" branches / onboarding routing / support-triage | `references/diagram-types/type-flowchart.md` | `status: complete` |',
    "| sequence | request/response flow / protocol handshake / multi-actor interaction / API call trace / incident reconstruction | `references/diagram-types/type-sequence.md` | `status: complete` |",
    "| state | finite-state logic / order status / auth state / connection lifecycle / form wizard | `references/diagram-types/type-state.md` | `status: complete` |",
    "| er | database schema / API resource relationships / domain model / aggregate boundary / cross-service ownership | `references/diagram-types/type-er.md` | `status: complete` |",
    "| timeline | release history / project milestone / incident timeline / roadmap / changelog | `references/diagram-types/type-timeline.md` | `status: complete` |",
    "| swimlane | cross-functional process / RACI flow / vendor handoff / multi-team workflow / cross-team responsibility | `references/diagram-types/type-swimlane.md` | `status: complete` |",
    "| quadrant | prioritization (Impact × Effort) / positioning map / portfolio map / 2×2 decision / scenario planning | `references/diagram-types/type-quadrant.md` | `status: complete` |",
    "| nested | expressing hierarchy via containment / scope boundary / CLAUDE.md cascade / trust zone / blast radius | `references/diagram-types/type-nested.md` | `status: complete` |",
    "| tree | org chart / dependency tree / taxonomy / file tree / decision breakdown / skill tree | `references/diagram-types/type-tree.md` | `status: complete` |",
    "| layers | OSI model / CSS cascade / context hierarchy / tech stack / abstraction layer / memory hierarchy | `references/diagram-types/type-layers.md` | `status: complete` |",
    "| venn | concept intersection / shared attributes across categories / ikigai-style frame / positioning sweet spot | `references/diagram-types/type-venn.md` | `status: complete` |",
    "| pyramid | hierarchy of needs / prioritization rank / value pyramid / conversion funnel / content importance | `references/diagram-types/type-pyramid.md` | `status: complete` |",
]

# Structural geometry only (<rect>/<line>/<circle> position attrs) — text x/y
# baselines are deliberately excluded: centering text inside an odd-width
# label box (e.g. width=28 → center offset +14) routinely produces non-4
# values even in all 13 existing type-*.md files (verified empirically), so
# the §4.7 "multiples of 4" rule is enforced on shape geometry, not text.
TAG_RE = re.compile(r"<(rect|line|circle)\b([^>]*)>")
ATTR_RE = re.compile(r'(?<=\s)(x1?|y1?|x2|y2|cx|cy|width|height)="(-?\d+(?:\.\d+)?)"')


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


def section_49(text: str) -> str:
    return _extract_region(
        text, "## §4.9 14-type chart routing decision tree", ["\n## §4.10"])


def section_410(text: str) -> str:
    return _extract_region(text, "## §4.10", [])


def stage3_render_stage(text: str) -> str:
    marker = "## Stage 3 — Render"
    start = text.find(marker)
    assert start != -1, "'## Stage 3 — Render' header not found"
    body = text[start:]
    nxt = body.find("\n## ", len(marker))
    return body if nxt == -1 else body[:nxt]


def git_diff_touched(path: Path) -> bool:
    """True if `path` differs from HEAD (tracked-file regression guard)."""
    rel = path.relative_to(WORKTREE_ROOT)
    result = subprocess.run(
        ["git", "-C", str(WORKTREE_ROOT), "diff", "--name-only", "HEAD", "--", str(rel)],
        capture_output=True, text=True, check=True,
    )
    return bool(result.stdout.strip())


class TestNewStatisticalReferenceFileExists(unittest.TestCase):
    """(a) — the new unified reference file itself."""

    def setUp(self) -> None:
        self.assertTrue(NEW_TYPE_FILE.exists(), f"{NEW_TYPE_FILE} must exist")
        self.text = NEW_TYPE_FILE.read_text(encoding="utf-8")

    def test_frontmatter_fields(self):
        self.assertIn("name: statistical", self.text)
        self.assertIn("status: complete", self.text)
        self.assertIn("example: inline", self.text)

    def test_template_sections_present(self):
        for heading in ("## Contents", "## Layout conventions", "## Anti-patterns", "## Examples"):
            self.assertIn(heading, self.text, f"missing template section {heading!r}")
        self.assertIn("**Best for**:", self.text)

    def test_axis_legend_multi_datapoint_conventions_documented(self):
        layout = _extract_region(self.text, "## Layout conventions", ["\n## Anti-patterns"])
        self.assertIn("axis", layout.lower(), "Layout conventions must define axis convention")
        self.assertIn("legend", layout.lower(), "Layout conventions must define legend convention")
        self.assertTrue(
            "data point" in layout.lower() or "data-point" in layout.lower(),
            "Layout conventions must define data-point convention",
        )

    def test_inline_example_has_axis_legend_and_multiple_datapoints(self):
        examples = _extract_region(self.text, "## Examples", [])
        self.assertIn("```html", examples, "Examples must include a fenced html SVG block")
        self.assertIn("<figure class=\"diagram\">", examples)
        self.assertIn("<svg", examples)
        self.assertIn("LEGEND", examples, "must reuse §4.6 legend strip")
        circle_count = examples.count("<circle")
        self.assertGreaterEqual(
            circle_count, 8,
            "must render multiple data points across 2+ series (>=8 circles expected)",
        )

    def test_reuses_defs_and_marker_primitives(self):
        examples = _extract_region(self.text, "## Examples", [])
        self.assertIn('id="dots"', examples)
        for marker_id in ("arrow", "arrow-accent", "arrow-link"):
            self.assertIn(f'id="{marker_id}"', examples, f"marker def {marker_id} must exist")
            self.assertIn(
                f'marker-end="url(#{marker_id})"', examples,
                f"marker {marker_id} must actually be referenced (GATE-D bijective integrity)",
            )

    def test_reuses_two_layer_paper_mask(self):
        examples = _extract_region(self.text, "## Examples", [])
        self.assertEqual(
            examples.count('<rect width="100%" height="100%"'), 2,
            "must stack exactly the two paper-mask layers",
        )

    def test_reuses_type_tag_primitive(self):
        examples = _extract_region(self.text, "## Examples", [])
        self.assertIn('width="28" height="12" rx="2"', examples, "must reuse §4.5 type-tag shape")

    def test_reuses_node_width_whitelist_at_most_two_tiers(self):
        examples = _extract_region(self.text, "## Examples", [])
        widths = set(re.findall(r'<rect[^>]*\bwidth="(\d+)"', examples))
        # Exclude sub-primitives (<40) and full-bleed masks — only look at real tiers used.
        top_level = {w for w in widths if int(w) >= 40}
        self.assertTrue(top_level, "expected at least one top-level whitelisted-width rect")
        self.assertTrue(
            top_level.issubset({"128", "144", "160"}),
            f"top-level rect widths must be within the {{128,144,160}} whitelist, got {top_level}",
        )
        self.assertLessEqual(len(top_level), 2, "at most 2 distinct node-width tiers per SVG")

    def test_focal_cap_respected(self):
        examples = _extract_region(self.text, "## Examples", [])
        focal_count = examples.count('data-role="focal"')
        self.assertGreaterEqual(focal_count, 1, "should demonstrate at least 1 focal element")
        self.assertLessEqual(focal_count, 2, "GATE-A caps data-role=focal at 2 per SVG")

    def test_shape_geometry_coordinates_are_multiples_of_four(self):
        examples = _extract_region(self.text, "## Examples", [])
        defs_end = examples.find("</defs>")
        body = examples[defs_end + len("</defs>"):] if defs_end != -1 else examples
        offenders = []
        for tag, attrs in TAG_RE.findall(body):
            for name, val in ATTR_RE.findall(" " + attrs):
                if val == "100%":
                    continue
                if float(val) % 4 != 0:
                    offenders.append((tag, name, val))
        self.assertEqual(
            offenders, [],
            f"§4.7 anti-slop requires rect/line/circle geometry be multiples of 4, offenders: {offenders}",
        )

    def test_best_for_traces_back_to_all_seven_orphaned_data_shapes(self):
        # Traceability: the reference file should name the statistical chart
        # sub-shapes that route here from §4.9, so a reader can tell which
        # data shapes this file governs.
        best_for_region = _extract_region(self.text, "**Best for**:", ["\n## Layout conventions"])
        lower = best_for_region.lower()
        for name in ORPHANED_ORIGINAL_NAMES:
            self.assertIn(
                name.lower(), lower,
                f"Best-for line should trace back to the original §4.9 shape name {name!r}",
            )


class TestFourteenthRowInSelectionTable(unittest.TestCase):
    """(a) — §4.10 gains a real 14th row for `statistical`."""

    def setUp(self) -> None:
        self.full = SVG_RULES.read_text(encoding="utf-8")
        self.section = section_410(self.full)

    def test_statistical_row_present(self):
        self.assertIn("| statistical |", self.section)
        self.assertIn("references/diagram-types/type-statistical.md", self.section)
        # The statistical row must itself be status: complete (per Constraints).
        row_line = next(l for l in self.section.splitlines() if l.startswith("| statistical |"))
        self.assertIn("`status: complete`", row_line)

    def test_table_now_has_fourteen_rows(self):
        rows = [l for l in self.section.splitlines() if l.startswith("| ") and " | " in l[2:]]
        # First matching line is the header row, second is the separator; data rows follow.
        data_rows = [l for l in rows if not l.startswith("| Type |") and not set(l.replace("|", "").strip()) <= {"-"}]
        self.assertEqual(len(data_rows), 14, f"expected 14 data rows, got {len(data_rows)}:\n{data_rows}")

    def test_heading_and_toc_updated_to_fourteen(self):
        self.assertIn("14-type selection table", self.full)
        self.assertNotIn("13-type selection table", self.full)

    def test_all_thirteen_original_rows_unchanged(self):
        for row in ORIGINAL_410_ROWS:
            self.assertIn(row, self.section, f"original §4.10 row changed or missing:\n{row}")


class TestFirstMatchOrderingPriority(unittest.TestCase):
    """(b) — §4.9's 7 structural rows keep first-match priority over the 7
    statistical rows, per design.md's 既有型態優先 tie-break rule."""

    def setUp(self) -> None:
        self.full = SVG_RULES.read_text(encoding="utf-8")
        self.section = section_49(self.full)

    def test_all_structural_rows_survive_unchanged(self):
        for data_shape, chosen in STRUCTURAL_ROWS:
            self.assertIn(
                f"| {data_shape} | {chosen} |", self.section,
                f"structural row for {chosen!r} must survive verbatim",
            )

    def test_all_orphaned_data_shapes_survive_unchanged(self):
        for data_shape in ORPHANED_DATA_SHAPES:
            self.assertIn(
                data_shape, self.section,
                f"orphaned row's Data shape column must survive verbatim: {data_shape!r}",
            )

    def test_orphaned_rows_now_resolve_to_statistical(self):
        for data_shape in ORPHANED_DATA_SHAPES:
            line = next(
                (l for l in self.section.splitlines() if l.startswith(f"| {data_shape} |")), None
            )
            self.assertIsNotNone(line, f"row for {data_shape!r} not found")
            assert line is not None
            self.assertTrue(
                line.rstrip().endswith("| Statistical |"),
                f"orphaned row must now route to Statistical, got: {line!r}",
            )

    def test_structural_rows_positioned_before_statistical_rows(self):
        lines = [l for l in self.section.splitlines() if l.startswith("| ")]
        data_lines = [l for l in lines if l != "|---------|---------|" and "Data shape" not in l]
        structural_indices = [
            i for i, l in enumerate(data_lines)
            if any(l.endswith(f"| {chosen} |") for _, chosen in STRUCTURAL_ROWS)
        ]
        statistical_indices = [i for i, l in enumerate(data_lines) if l.endswith("| Statistical |")]
        self.assertEqual(len(structural_indices), 7)
        self.assertEqual(len(statistical_indices), 7)
        self.assertLess(
            max(structural_indices), min(statistical_indices),
            "all 7 structural rows must precede all 7 statistical rows for "
            "first-match tie-break priority (既有型態優先)",
        )

    def test_wiring_note_names_all_seven_original_shapes(self):
        for name in ORPHANED_ORIGINAL_NAMES:
            self.assertIn(
                name, self.section,
                f"§4.9 must retain a visible trace of the original chart-shape name {name!r}",
            )


class TestDegradeLogicDocumented(unittest.TestCase):
    """(c) — the L1/L2 undeclared-capability degrade branch, per design.md's
    錯誤處理策略 bullet 3 and TASK-book-01 acceptance criterion 5."""

    def setUp(self) -> None:
        self.full = SKILL.read_text(encoding="utf-8")
        self.section = stage3_render_stage(self.full)
        self.lower = self.section.lower()

    def test_declaration_state_check_documented(self):
        self.assertIn("chart-capability", self.lower)
        self.assertIn("tokens.css", self.lower)
        self.assertIn("declared", self.lower)
        self.assertIn("undeclared", self.lower)

    def test_l1_single_trend_fallback_documented(self):
        self.assertIn("l1", self.lower)
        self.assertTrue(
            "single-hue" in self.lower or "single hue" in self.lower,
            "L1 branch must fall back to the existing single-hue accent ramp",
        )

    def test_l2_small_multiples_or_table_documented(self):
        self.assertIn("l2", self.lower)
        self.assertTrue(
            "small-multiples" in self.lower or "small multiples" in self.lower,
            "L2 branch must degrade to small-multiples",
        )
        self.assertIn("table", self.lower)

    def test_branches_are_mutually_exclusive(self):
        self.assertTrue(
            "mutually exclusive" in self.lower or "exactly one" in self.lower,
            "degrade branches must be documented as mutually exclusive (no mixing/misjudging)",
        )

    def test_l1_l2_boundary_covers_exactly_two_series_no_gap(self):
        """Round-2 regression guard (review-agent finding): AC5's own text is
        a strict binary — 單一數列 → L1 ／ 多條互不相關數列 → L2, where 多條
        (plural) means 2+, not 3+. The L2 branch bullet must anchor its
        threshold at 2, not 3, so the exactly-2-mutually-unrelated-series
        case is never silently left unrouted between L1's "single series"
        bucket and L2's bucket (不開豁免 — no exemptions precedent from
        design.md's cited prior /think discussion)."""
        l1_line = next((l for l in self.section.splitlines() if "**L1**" in l), None)
        l2_line = next((l for l in self.section.splitlines() if "**L2**" in l), None)
        self.assertIsNotNone(l1_line, "L1 branch bullet not found")
        self.assertIsNotNone(l2_line, "L2 branch bullet not found")
        assert l1_line is not None and l2_line is not None
        self.assertNotIn(
            "3+", l2_line.lower(),
            "L2 branch must not gate its threshold at 3+, which would silently "
            "leave the exactly-2-mutually-unrelated-series case unrouted",
        )
        self.assertTrue(
            re.search(r"\b2\+|\b2 or more\b|\btwo or more\b", l2_line.lower()),
            f"L2 branch must explicitly state its threshold starts at 2 (includes "
            f"exactly-2-series), got: {l2_line!r}",
        )


class TestSeriesColorDisciplineDoesNotBypassDegrade(unittest.TestCase):
    """Round-2 regression guard (review-agent finding): type-statistical.md's
    'Series color discipline' note must not assert that 2-series content may
    *always* use the 2 pre-existing --accent/--brand-light marker hues — that
    would be an undocumented third path bypassing the SKILL.md undeclared-
    capability degrade decision entirely (exactly the silent exemption the
    不開豁免 precedent forbids). The note may describe the declared-capability
    outcome, but must tie the 2-hue usage to the declared/undeclared check,
    not exempt 2-series content from it."""

    def setUp(self) -> None:
        self.text = NEW_TYPE_FILE.read_text(encoding="utf-8")
        layout = _extract_region(self.text, "## Layout conventions", ["\n## Anti-patterns"])
        start = layout.find("Series color discipline")
        self.assertNotEqual(start, -1, "Series color discipline note not found")
        end = layout.find("\n- **", start + 1)
        self.note = layout[start: end if end != -1 else len(layout)]
        self.note_lower = self.note.lower()

    def test_note_ties_two_hue_usage_to_declared_state(self):
        self.assertIn("declared", self.note_lower)
        self.assertIn("undeclared", self.note_lower)

    def test_note_does_not_exempt_two_series_from_degrade_check(self):
        self.assertTrue(
            "degrade" in self.note_lower or "l1" in self.note_lower or "l2" in self.note_lower,
            "note must reference the SKILL.md degrade decision by name, not just "
            "the declared/undeclared state, so a reader cannot mistake this for "
            "an independent third path",
        )
        self.assertNotIn(
            "only ever needs", self.note_lower,
            "note must not unconditionally assert 2-series content only ever "
            "needs the 2 pre-existing hues — that phrasing bypasses the "
            "undeclared-capability degrade check for the exactly-2-series case",
        )


class TestRegressionExistingThirteenTypesUntouched(unittest.TestCase):
    """(d) — none of the existing 13 types' files/content changed meaning."""

    def test_thirteen_type_files_not_touched_by_this_task(self):
        for name in EXISTING_13_TYPES:
            path = DIAGRAM_TYPES_DIR / f"type-{name}.md"
            with self.subTest(type=name):
                self.assertTrue(path.exists())
                self.assertFalse(
                    git_diff_touched(path),
                    f"type-{name}.md must not be modified by TASK-book-01",
                )

    def test_directory_now_has_fourteen_type_files(self):
        files = sorted(p.name for p in DIAGRAM_TYPES_DIR.glob("type-*.md"))
        self.assertEqual(len(files), 14, f"expected 14 type-*.md files, got {files}")

    def test_sections_41_through_48_untouched(self):
        full = SVG_RULES.read_text(encoding="utf-8")
        # Spot-check one verbatim string per §4.1-§4.8 section to guard against
        # accidental edits outside the §4.9/§4.10 scope of this task.
        untouched_anchors = [
            "| Canvas background | `--paper` | `#f5f4ed` |",
            '<marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto">',
            "Layer 1 (**mandatory**): full-width",
            "place a 7px uppercase small label at the top-left corner of each node",
            "after the main nodes and arrows are drawn, every SVG reserves about 60px",
            "Node-width whitelist is **3 sizes**",
            "| H2 / focal node | 24 |",
        ]
        for anchor in untouched_anchors:
            self.assertIn(anchor, full, f"§4.1-§4.8 content must be untouched, missing: {anchor!r}")


if __name__ == "__main__":
    unittest.main()
