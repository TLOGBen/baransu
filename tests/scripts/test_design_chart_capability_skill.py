#!/usr/bin/env python3
"""Structural + cross-check assertions for /design's chart-capability declaration
mechanism (TASK-design-02, REQ-003 / REQ-002 Scenario 3).

/design is a prose-driven skill (SKILL.md, executed by an LLM agent via
Bash/Write, not a running app) — see tests/scripts/test_design_skill_gen.py for
the established precedent of asserting SKILL.md prose via structural/regex
checks. This suite extends that pattern to the new "圖表分類色能力" declaration
entry point:

  1. Preset Mode Step 3 documents a declaration entry point (CLI flag) and the
     bake+emit contract (call color_distance.py, write the 6
     CHART_CAPABILITY_TOKENS names, emit a `; chart-capability: <N>` header
     field distinct from `schema: 43`), plus the undeclared no-op guarantee and
     the atomic-rewrite-clears-stale-declaration invariant.
  2. Gen Mode Step 1 documents its own declaration entry point (AskUserQuestion,
     positioned alongside the existing extreme-commitment axis).
  3. The documented header-field syntax actually satisfies check.py's
     already-built CHART_CAPABILITY_FIELD_RE / _parse_chart_capability_header /
     _check_chart_capability_completeness contract (TASK-design-01, read-only) —
     verified by constructing a fixture and running check.py's parser against
     it, not just by visual inspection of the prose.
  4. The three shipped presets remain untouched (regression guard).
"""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

THIS_FILE = Path(__file__).resolve()
WORKTREE_ROOT = THIS_FILE.parents[2]
SKILL = WORKTREE_ROOT / "plugins" / "baransu" / "skills" / "design" / "SKILL.md"
CHECK_PY = WORKTREE_ROOT / "plugins" / "baransu" / "skills" / "design" / "scripts" / "check.py"
REFS = WORKTREE_ROOT / "plugins" / "baransu" / "skills" / "design" / "references"


def _extract_region(text: str, start_marker: str, end_markers: list[str]) -> str:
    """Isolate a SKILL.md region from start_marker up to whichever end_marker
    (searched after the start) occurs first, or EOF if none found."""
    start = text.find(start_marker)
    assert start != -1, f"marker not found: {start_marker!r}"
    body = text[start:]
    end = len(body)
    for marker in end_markers:
        idx = body.find(marker, len(start_marker))
        if idx != -1:
            end = min(end, idx)
    return body[:end]


def preset_step3_region(text: str) -> str:
    return _extract_region(
        text,
        "### Step 3 — Apply preset",
        ["\n### Step 4 — Render DESIGN.html"],
    )


def gen_step1_region(text: str) -> str:
    return _extract_region(
        text,
        "### Step 1 — Ask direction questions",
        ["\n#### Gen Mode Step 1.5", "\n### Step 2 — Generate DESIGN.md"],
    )


def _load_check_module():
    """Import check.py as a module to access its constants/functions directly."""
    spec = importlib.util.spec_from_file_location(
        "check_design_chart_cap_under_test", CHECK_PY)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestPresetModeDeclarationEntryPoint(unittest.TestCase):
    """REQ-003 Scenario 1 / task-design.md 「宣告入口」 step — Preset Mode side."""

    def setUp(self) -> None:
        self.region = preset_step3_region(SKILL.read_text(encoding="utf-8"))

    def test_declaration_flag_documented(self):
        self.assertIn(
            "--chart-capability", self.region,
            "Preset Mode Step 3 must document a --chart-capability declaration entry point",
        )

    def test_capability_name_documented(self):
        self.assertIn(
            "圖表分類色", self.region,
            "Preset Mode Step 3 must name the 圖表分類色 (chart-category color) capability",
        )

    def test_color_distance_tool_invocation_documented(self):
        self.assertIn(
            "color_distance.py", self.region,
            "Preset Mode Step 3 must document invoking color_distance.py to validate the "
            "candidate palette before baking",
        )

    def test_all_six_chart_cat_token_names_documented(self):
        for i in range(1, 7):
            token = f"--chart-cat-{i}"
            self.assertIn(
                token, self.region,
                f"Preset Mode Step 3 must document the exact canonical name {token}",
            )

    def test_header_field_syntax_documented_distinct_from_schema(self):
        self.assertIn(
            "chart-capability:", self.region,
            "Preset Mode Step 3 must document the `; chart-capability: <N>` header field",
        )
        self.assertIn(
            "schema: 43", self.region,
            "Preset Mode Step 3 must reference schema: 43 to contrast the new version tier",
        )

    def test_undeclared_path_is_documented_noop(self):
        self.assertIn(
            "不呼叫 color_distance.py", self.region,
            "Preset Mode Step 3 must state that the undeclared path never calls "
            "color_distance.py (zero behavior change)",
        )

    def test_atomic_rewrite_clears_stale_declaration_documented(self):
        self.assertTrue(
            ("自然清除" in self.region) or ("不會殘留" in self.region),
            "Preset Mode Step 3 must state that atomic full-rewrite naturally clears a "
            "declared→undeclared transition's stale chart-capability header field",
        )


class TestGenModeDeclarationEntryPoint(unittest.TestCase):
    """REQ-003 Scenario 1 / task-design.md 「宣告入口」 step — Gen Mode side."""

    def setUp(self) -> None:
        self.region = gen_step1_region(SKILL.read_text(encoding="utf-8"))

    def test_ask_user_question_entry_point_documented(self):
        self.assertIn(
            "AskUserQuestion", self.region,
            "Gen Mode Step 1 must add an AskUserQuestion-based chart-capability entry "
            "point, consistent with the existing gen interview pattern",
        )

    def test_capability_name_documented(self):
        self.assertIn(
            "圖表分類色", self.region,
            "Gen Mode Step 1 must name the 圖表分類色 (chart-category color) capability",
        )

    def test_positioned_after_extreme_commitment_axis_subsection(self):
        axis_idx = self.region.find("#### The extreme-commitment axis")
        chart_idx = self.region.find("圖表分類色")
        self.assertNotEqual(axis_idx, -1, "extreme-commitment axis subsection must exist")
        self.assertNotEqual(chart_idx, -1, "chart-capability subsection must exist")
        self.assertGreater(
            chart_idx, axis_idx,
            "chart-capability declaration must sit alongside (after) the "
            "extreme-commitment-axis subsection in Step 1",
        )

    def test_consistency_with_preset_mode_noted(self):
        self.assertIn(
            "--chart-capability", self.region,
            "Gen Mode Step 1 must cross-reference Preset Mode's --chart-capability flag "
            "to document that both entry points funnel into the same downstream contract",
        )


class TestChartCapabilityHeaderFormatSatisfiesCheckPy(unittest.TestCase):
    """Requirement 6 — cross-check the documented header format against check.py's
    actual parser, not just visual inspection of the prose."""

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_check_module()

    def test_documented_header_field_parses_as_declared(self):
        # Exact syntax documented in Preset/Gen Mode Step 3: `; chart-capability: 1`.
        header = "/* preset: testslug; schema: 43; chart-capability: 1 */\n"
        status, version = self.mod._parse_chart_capability_header(header)
        self.assertEqual((status, version), ("declared", 1))

    def test_documented_six_token_names_satisfy_completeness_check(self):
        tokens = self.mod.BASE_TOKENS + self.mod.CAPABILITY_TOKENS + [
            f"--chart-cat-{i}" for i in range(1, 7)
        ]
        body = "\n".join(f"  {t}: #000000;" for t in tokens)
        css = f"/* preset: testslug; schema: 43; chart-capability: 1 */\n:root {{\n{body}\n}}\n"
        status, _ = self.mod._parse_chart_capability_header(css)
        findings = self.mod._check_chart_capability_completeness(
            Path("tokens.css"), css, status)
        self.assertEqual(findings, [])

    def test_undeclared_header_has_no_field(self):
        # Simulates a declared→undeclared atomic regeneration: the header simply
        # omits the field entirely (no leftover fragment) once the source
        # tokens.css this run has no chart-capability declaration.
        header = "/* preset: testslug; schema: 43 */\n"
        status, version = self.mod._parse_chart_capability_header(header)
        self.assertEqual((status, version), ("undeclared", None))


class TestThreeExistingPresetsUntouched(unittest.TestCase):
    """Regression constraint — this task must not modify or activate the
    capability for any of the three shipped presets."""

    PRESETS = [
        REFS / "紙-preset" / "tokens.css",
        REFS / "swiss-preset" / "tokens.css",
        REFS / "google-design-preset" / "tokens.css",
    ]

    def test_no_preset_declares_chart_capability(self):
        for path in self.PRESETS:
            with self.subTest(preset=path.parent.name):
                text = path.read_text(encoding="utf-8")
                self.assertNotIn("chart-capability", text)


if __name__ == "__main__":
    unittest.main()
