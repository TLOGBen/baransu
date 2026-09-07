#!/usr/bin/env python3
"""Structural assertions for the book-diagrams expansion — the 14→17
diagram-type catalog (org-chart / class / architecture-board), the §4.9/§4.10
registration in `references/svg-rendering-rules.md`, and the new
`maintained-diagrams.md` trio-lifecycle contract.

/book is a prose-driven skill (SKILL.md + reference *.md, executed by an LLM
agent, not a running app) — this suite mirrors the structural-assertion
pattern established by tests/scripts/test_book_chart_statistical_type.py
(machine-checkable surfaces only; no LLM-judgment gates).

Covers:
  (a) catalog completeness — exactly 17 type-*.md files, stem set pinned
  (b) §4.10 fact-sync — every type has a row whose Status backtick value
      equals the file's own frontmatter `status:` line
  (c) §4.9 first-match ordering — Org Chart outranks Tree; Architecture
      Board and Class outrank the general-purpose Architecture sponge; all
      three new rows precede the statistical block
  (d) per-new-file structure contract + gate-shaped example invariants
      (paper-mask ×2, marker bijectivity incl. the zero/zero case, node-width
      whitelist ≤2 tiers, focal cap, LEGEND, type tag, multiples-of-4
      geometry, no rgba, 「圖：」 figcaption)
  (e) maintained-diagrams.md — exists, is NOT a diagram type (no `status:`
      frontmatter), and is wired from both svg-rendering-rules §4.11 and
      book SKILL.md
  (f) legend-hairline GATE-C window — every inline example SVG across all
      17 type files (viewBox height ≥ 400) carries a <line> whose lower end
      sits inside the bottom-60px window GATE-C keys on
  (g) stale-count scan — no 13/14/15/16-count residue ("N-type" / "N 型" /
      "N-set" / "N per-type" / "N diagram(-)types" / "other N") across the
      five catalog-speaking surfaces (book SKILL.md, svg-rendering-rules.md,
      design-token-resolver.md, color-reasoning.md, design slide-checklist.md);
      SKILL.md speaks 「17 型」, color-reasoning speaks "the other 16"
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

THIS_FILE = Path(__file__).resolve()
WORKTREE_ROOT = THIS_FILE.parents[2]
BOOK_SKILL_DIR = WORKTREE_ROOT / "plugins" / "baransu" / "skills" / "book"
SKILL = BOOK_SKILL_DIR / "SKILL.md"
SVG_RULES = BOOK_SKILL_DIR / "references" / "svg-rendering-rules.md"
DIAGRAM_TYPES_DIR = BOOK_SKILL_DIR / "references" / "diagram-types"
MAINTAINED = DIAGRAM_TYPES_DIR / "maintained-diagrams.md"

SEVENTEEN_TYPES = [
    "architecture", "flowchart", "sequence", "state", "er", "timeline",
    "swimlane", "quadrant", "nested", "tree", "layers", "venn", "pyramid",
    "statistical", "org-chart", "class", "architecture-board",
]

NEW_TYPES = ["org-chart", "class", "architecture-board"]

# Same structural-geometry scope as test_book_chart_statistical_type.py:
# <rect>/<line>/<circle> position attrs only; text x/y baselines exempt.
TAG_RE = re.compile(r"<(rect|line|circle)\b([^>]*)>")
ATTR_RE = re.compile(r'(?<=\s)(x1?|y1?|x2|y2|cx|cy|width|height)="(-?\d+(?:\.\d+)?)"')

MARKER_DEF_RE = re.compile(r'<marker id="([^"]+)"')
MARKER_REF_RE = re.compile(r'marker-(?:end|start)="url\(#([^)]+)\)"')


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
        text, "## §4.9 17-type chart routing decision tree", ["\n## §4.10"])


def section_410(text: str) -> str:
    return _extract_region(text, "## §4.10", ["\n## §4.11"])


def data_rows(section: str) -> list[str]:
    rows = [l for l in section.splitlines() if l.startswith("| ")]
    return [
        l for l in rows
        if "Data shape" not in l and not l.startswith("| Type |")
        and set(l.replace("|", "").strip()) != {"-"}
    ]


class TestCatalogSeventeenFiles(unittest.TestCase):
    """(a) — the type-*.md catalog is exactly the pinned 17."""

    def test_glob_count_is_seventeen(self):
        files = sorted(p.name for p in DIAGRAM_TYPES_DIR.glob("type-*.md"))
        self.assertEqual(len(files), 17, f"expected 17 type-*.md files, got {files}")

    def test_stem_set_matches_seventeen_types(self):
        stems = {p.stem for p in DIAGRAM_TYPES_DIR.glob("type-*.md")}
        self.assertEqual(stems, {f"type-{t}" for t in SEVENTEEN_TYPES})


class TestSelectionTableFactSync(unittest.TestCase):
    """(b) — §4.10 rows fact-synced with each file's frontmatter status."""

    def setUp(self) -> None:
        self.section = section_410(SVG_RULES.read_text(encoding="utf-8"))

    def test_every_type_has_a_row_whose_status_matches_frontmatter(self):
        for t in SEVENTEEN_TYPES:
            with self.subTest(type=t):
                ref = f"references/diagram-types/type-{t}.md"
                row = next(
                    (l for l in self.section.splitlines() if ref in l), None)
                self.assertIsNotNone(row, f"§4.10 row missing for {t!r}")
                assert row is not None
                m = re.search(r"`(status: [a-z-]+)`", row)
                self.assertIsNotNone(m, f"no Status backtick value in row: {row!r}")
                assert m is not None
                file_text = (DIAGRAM_TYPES_DIR / f"type-{t}.md").read_text(encoding="utf-8")
                fm_status = next(
                    l.strip() for l in file_text.splitlines() if l.startswith("status:"))
                self.assertEqual(
                    m.group(1), fm_status,
                    f"§4.10 Status column desynced from type-{t}.md frontmatter",
                )

    def test_table_has_seventeen_data_rows(self):
        # The Best-for/Reference table plus nothing else — statistical stays last.
        rows = [l for l in data_rows(self.section) if "references/diagram-types/" in l]
        self.assertEqual(len(rows), 17)
        self.assertTrue(rows[-1].startswith("| statistical |"), "statistical must stay the last row")


class TestRoutingTreeOrdering(unittest.TestCase):
    """(c) — §4.9 first-match priority: position IS priority."""

    def setUp(self) -> None:
        self.rows = data_rows(section_49(SVG_RULES.read_text(encoding="utf-8")))

    def _index(self, predicate) -> int:
        for i, row in enumerate(self.rows):
            if predicate(row):
                return i
        raise AssertionError(f"no row matched in: {self.rows}")

    def test_org_chart_precedes_tree(self):
        org = self._index(lambda r: r.rstrip().endswith("| Org Chart |"))
        tree = self._index(lambda r: r.rstrip().endswith("| Tree |"))
        self.assertLess(
            org, tree,
            "Org Chart must outrank Tree — an org chart is hierarchical too, "
            "so first-match Tree would swallow it",
        )

    def test_board_and_class_precede_architecture(self):
        board = self._index(lambda r: r.rstrip().endswith("| Architecture Board |"))
        cls = self._index(lambda r: r.rstrip().endswith("| Class |"))
        arch = self._index(lambda r: r.rstrip().endswith("| Architecture |"))
        self.assertLess(board, arch, "Architecture Board must outrank the Architecture sponge")
        self.assertLess(cls, arch, "Class must outrank the Architecture sponge")

    def test_all_three_new_rows_precede_statistical_block(self):
        first_stat = self._index(lambda r: r.rstrip().endswith("| Statistical |"))
        for ending in ("| Org Chart |", "| Architecture Board |", "| Class |"):
            with self.subTest(row=ending):
                idx = self._index(lambda r, e=ending: r.rstrip().endswith(e))
                self.assertLess(idx, first_stat)


class TestNewTypeFilesStructureContract(unittest.TestCase):
    """(d) — each new file follows the per-file structure contract and its
    inline example is engineered to the validate-output.ts gate shapes."""

    def _file(self, t: str) -> str:
        return (DIAGRAM_TYPES_DIR / f"type-{t}.md").read_text(encoding="utf-8")

    def _example(self, t: str) -> str:
        return _extract_region(self._file(t), "## Examples", [])

    def test_frontmatter_triple(self):
        for t in NEW_TYPES:
            with self.subTest(type=t):
                text = self._file(t)
                self.assertIn(f"name: {t}", text)
                self.assertIn("status: complete", text)
                self.assertIn("example: inline", text)

    def test_template_headings_and_best_for(self):
        for t in NEW_TYPES:
            with self.subTest(type=t):
                text = self._file(t)
                for heading in ("## Contents", "## Layout conventions",
                                "## Anti-patterns", "## Examples"):
                    self.assertIn(heading, text, f"type-{t}.md missing {heading!r}")
                self.assertIn("**Best for**:", text)

    def test_example_is_single_fenced_html_figure_diagram(self):
        for t in NEW_TYPES:
            with self.subTest(type=t):
                ex = self._example(t)
                self.assertEqual(ex.count("```html"), 1)
                self.assertIn('<figure class="diagram">', ex)
                self.assertIn("<svg", ex)

    def test_exactly_two_paper_mask_layers(self):
        for t in NEW_TYPES:
            with self.subTest(type=t):
                self.assertEqual(
                    self._example(t).count('<rect width="100%" height="100%"'), 2,
                    f"type-{t}.md example must stack exactly the two paper-mask layers",
                )

    def test_type_tag_primitive_present(self):
        for t in NEW_TYPES:
            with self.subTest(type=t):
                self.assertIn(
                    'width="28" height="12" rx="2"', self._example(t),
                    f"type-{t}.md example must reuse the §4.5 type-tag shape",
                )

    def test_node_width_whitelist_at_most_two_tiers(self):
        for t in NEW_TYPES:
            with self.subTest(type=t):
                ex = self._example(t)
                widths = set(re.findall(r'<rect[^>]*\bwidth="(\d+)"', ex))
                top_level = {w for w in widths if int(w) >= 40}
                self.assertTrue(top_level, f"type-{t}.md: no top-level whitelisted-width rect")
                self.assertTrue(
                    top_level.issubset({"128", "144", "160"}),
                    f"type-{t}.md: widths outside the whitelist: {top_level}",
                )
                self.assertLessEqual(
                    len(top_level), 2,
                    f"type-{t}.md: at most 2 distinct node-width tiers per SVG",
                )

    def test_focal_between_one_and_two(self):
        for t in NEW_TYPES:
            with self.subTest(type=t):
                focal = self._example(t).count('data-role="focal"')
                self.assertGreaterEqual(focal, 1, f"type-{t}.md: demonstrate at least 1 focal")
                self.assertLessEqual(focal, 2, f"type-{t}.md: GATE-A caps focal at 2")

    def test_legend_strip_present(self):
        for t in NEW_TYPES:
            with self.subTest(type=t):
                self.assertIn("LEGEND", self._example(t))

    def test_marker_defs_and_refs_bijective_zero_zero_allowed(self):
        for t in NEW_TYPES:
            with self.subTest(type=t):
                ex = self._example(t)
                defined = set(MARKER_DEF_RE.findall(ex))
                referenced = set(MARKER_REF_RE.findall(ex))
                self.assertEqual(
                    defined, referenced,
                    f"type-{t}.md: marker defs ↔ refs must be bijective (GATE-D); "
                    f"defined={sorted(defined)} referenced={sorted(referenced)}",
                )

    def test_org_chart_exercises_the_bijective_zero_case(self):
        ex = self._example("org-chart")
        self.assertEqual(MARKER_DEF_RE.findall(ex), [],
                         "org-chart example must define zero markers (symmetric reporting lines)")
        self.assertEqual(MARKER_REF_RE.findall(ex), [])

    def test_shape_geometry_multiples_of_four(self):
        for t in NEW_TYPES:
            with self.subTest(type=t):
                ex = self._example(t)
                defs_end = ex.find("</defs>")
                body = ex[defs_end + len("</defs>"):] if defs_end != -1 else ex
                offenders = []
                for tag, attrs in TAG_RE.findall(body):
                    for name, val in ATTR_RE.findall(" " + attrs):
                        if val == "100%":
                            continue
                        if float(val) % 4 != 0:
                            offenders.append((tag, name, val))
                self.assertEqual(
                    offenders, [],
                    f"type-{t}.md: §4.7 requires rect/line/circle geometry be "
                    f"multiples of 4, offenders: {offenders}",
                )

    def test_no_rgba_inside_example(self):
        for t in NEW_TYPES:
            with self.subTest(type=t):
                self.assertNotIn("rgba(", self._example(t))

    def test_figcaption_starts_with_tu_prefix(self):
        for t in NEW_TYPES:
            with self.subTest(type=t):
                m = re.search(r"<figcaption>(.*?)</figcaption>", self._example(t), re.S)
                self.assertIsNotNone(m, f"type-{t}.md: figcaption missing")
                assert m is not None
                self.assertTrue(
                    m.group(1).strip().startswith("圖："),
                    f"type-{t}.md: figcaption must start with 「圖：」",
                )


class TestMaintainedDiagramsContract(unittest.TestCase):
    """(e) — maintained-diagrams.md is a lifecycle contract, not a type."""

    def test_file_exists(self):
        self.assertTrue(MAINTAINED.exists())

    def test_no_status_frontmatter_line(self):
        text = MAINTAINED.read_text(encoding="utf-8")
        self.assertIsNone(
            re.search(r"^status:", text, re.M),
            "maintained-diagrams.md must NOT carry diagram-type frontmatter — "
            "the §4.10 fact-sync grep and the 17-count glob must never see it",
        )

    def test_named_by_svg_rules_411(self):
        rules = SVG_RULES.read_text(encoding="utf-8")
        self.assertIn("## §4.11 Maintained-diagram lifecycle (trio contract)", rules)
        region = _extract_region(rules, "## §4.11", [])
        self.assertIn("maintained-diagrams.md", region)

    def test_named_by_book_skill_md(self):
        self.assertIn(
            "references/diagram-types/maintained-diagrams.md",
            SKILL.read_text(encoding="utf-8"),
        )



# GATE-C window scan — mirrors validate-output.ts GATE-C: an SVG with
# viewBox height >= 400 must place a legend hairline <line> whose lower
# end (max of y1/y2) falls within [vbH - 60, vbH].
SVG_VIEWBOX_RE = re.compile(r'<svg\b[^>]*viewBox="0 0 \d+ (\d+)"[^>]*>(.*?)</svg>', re.S)
LINE_TAG_RE = re.compile(r"<line\b[^>]*>")
LINE_Y_RE = re.compile(r'\b(y1|y2)="(-?\d+(?:\.\d+)?)"')


class TestLegendHairlineGateCWindow(unittest.TestCase):
    """(f) — every inline example SVG across ALL 17 type-*.md files places
    its legend hairline inside GATE-C's bottom-60px window, so extracting
    any example verbatim into a document cannot fail GATE-C."""

    # GATE-C exemption, encoded on the same axis the shipped gate uses
    # (§4.6: viewBox height < 400 may omit the legend strip entirely).
    # No current type example is that short — types are exempted by height,
    # never by name, so a future short example self-exempts mechanically.
    GATE_C_MIN_HEIGHT = 400

    def test_legend_hairline_within_bottom_60px_window(self):
        for t in SEVENTEEN_TYPES:
            text = (DIAGRAM_TYPES_DIR / f"type-{t}.md").read_text(encoding="utf-8")
            svgs = SVG_VIEWBOX_RE.findall(text)
            self.assertTrue(svgs, f"type-{t}.md: no viewBox-bearing <svg> in its inline example")
            for i, (vb_h_str, body) in enumerate(svgs):
                vb_h = int(vb_h_str)
                with self.subTest(type=t, svg=i, vb_height=vb_h):
                    if vb_h < self.GATE_C_MIN_HEIGHT:
                        continue  # GATE-C SKIP semantics (legend optional below 400)
                    y_maxes = []
                    for tag in LINE_TAG_RE.findall(body):
                        ys = [float(v) for _, v in LINE_Y_RE.findall(tag)]
                        if len(ys) == 2:
                            y_maxes.append(max(ys))
                    self.assertTrue(
                        any(vb_h - 60 <= y <= vb_h for y in y_maxes),
                        f"type-{t}.md svg#{i}: no <line> with max(y1,y2) in "
                        f"[{vb_h - 60}, {vb_h}] — GATE-C would FAIL this example "
                        f"(line y-maxima seen: {sorted(set(y_maxes))})",
                    )


# Every file that speaks about the diagram-type catalog's size. Consumer
# surfaces (token resolver, chart-color reasoning, the design skill's lint
# checklist) have each gone stale before — scan them all.
STALE_SCAN_FILES = {
    "book SKILL.md": SKILL,
    "svg-rendering-rules.md": SVG_RULES,
    "design-token-resolver.md": BOOK_SKILL_DIR / "references" / "design-token-resolver.md",
    "color-reasoning.md": BOOK_SKILL_DIR / "references" / "color-reasoning.md",
    "design slide-checklist.md": (
        WORKTREE_ROOT / "plugins" / "baransu" / "skills" / "design"
        / "references" / "slide-checklist.md"
    ),
}

# Catalog-count phrasings observed to go stale, expanded across the
# 13/14/15/16 numeric variants so the next catalog bump cannot leave the
# same residue. "other 16" is deliberately absent from the stale list:
# under the 17-type catalog, "the other 16 diagram types" is the one
# correct count-minus-one phrasing (asserted positively below) — which is
# also why "16 diagram types" cannot be a stale literal here.
STALE_COUNT_LITERALS = [
    *(f"{n}-type" for n in (13, 14, 15, 16)),
    *(f"{n} 型" for n in (13, 14, 15, 16)),
    *(f"{n}-set" for n in (13, 14, 15, 16)),
    *(f"{n} per-type" for n in (13, 14, 15, 16)),
    *(f"{n} diagram-types" for n in (13, 14, 15, 16)),
    *(f"{n} diagram types" for n in (13, 14, 15)),
    *(f"other {n} " for n in (13, 14, 15)),
]


class TestStaleCountLiteralsGone(unittest.TestCase):
    """(g) — no 13/14/15/16-count residue on any surface that speaks about
    the diagram-type catalog (mechanical substring grep, no judgment)."""

    def test_scanned_files_free_of_stale_count_literals(self):
        for label, path in STALE_SCAN_FILES.items():
            text = path.read_text(encoding="utf-8")
            for stale in STALE_COUNT_LITERALS:
                with self.subTest(file=label, literal=stale):
                    self.assertNotIn(
                        stale, text,
                        f"stale catalog-count literal {stale!r} in {label}",
                    )

    def test_skill_md_speaks_seventeen(self):
        self.assertIn("17 型", SKILL.read_text(encoding="utf-8"))

    def test_color_reasoning_speaks_the_correct_sixteen_others(self):
        text = STALE_SCAN_FILES["color-reasoning.md"].read_text(encoding="utf-8")
        self.assertIn("the other 16 diagram types", text)


if __name__ == "__main__":
    unittest.main()
