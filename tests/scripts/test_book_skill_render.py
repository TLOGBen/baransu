#!/usr/bin/env python3
"""Tests for the /book Stage 3 (Render) soft-generation reframe.

TASK-book-skill-01 — the Render stage moves from a fixed class whitelist
("No improvisation / no new CSS" / "class must exist in the SSOT template")
to soft generation within bounds: book reads tokens.css + DESIGN.md §9
expression-range + the current article context and GENERATES layout inside
a hard safety floor (canonical tokens, no bare hex). When §9 lacks the
expression-range fields (older preset), book falls back to a conservative
symmetric layout instead of improvising.
"""

from __future__ import annotations

import unittest
from pathlib import Path

THIS_FILE = Path(__file__).resolve()
WORKTREE_ROOT = THIS_FILE.parents[2]
SKILL = WORKTREE_ROOT / "plugins" / "baransu" / "skills" / "book" / "SKILL.md"


def render_stage(text: str) -> str:
    """Isolate the Stage 3 — Render section (up to the next '## Stage' or EOF)."""
    marker = "## Stage 3 — Render"
    start = text.find(marker)
    assert start != -1, "'## Stage 3 — Render' header not found"
    body = text[start:]
    nxt = body.find("\n## ", len(marker))
    return body if nxt == -1 else body[:nxt]


class TestRenderSoftGeneration(unittest.TestCase):
    def setUp(self) -> None:
        self.full = SKILL.read_text(encoding="utf-8")
        self.section = render_stage(self.full)
        self.lower = self.section.lower()

    def test_references_section9_expression_range_and_context(self):
        mentions_s9 = ("§9" in self.section) or ("expression range" in self.lower)
        self.assertTrue(
            mentions_s9,
            "Render stage must reference §9 / expression range as a soft-generation input",
        )
        self.assertIn(
            "context",
            self.lower,
            "Render stage must reference the current article context as a generation input",
        )

    def test_states_generation_within_hard_floor(self):
        mentions_floor = ("hard floor" in self.lower) or ("safety floor" in self.lower)
        self.assertTrue(
            mentions_floor,
            "Render stage must restate the hard floor / safety floor that bounds generation",
        )
        self.assertIn(
            "generate",
            self.lower,
            "Render stage must describe GENERATING layout within bounds",
        )

    def test_no_fixed_class_whitelist_reframe(self):
        # The reframe must explicitly state it is NOT limited to a fixed class whitelist
        # that must pre-exist in an SSOT template.
        self.assertIn(
            "whitelist",
            self.lower,
            "Render stage must explicitly reframe away from a fixed class whitelist",
        )
        self.assertTrue(
            ("not limited" in self.lower)
            or ("no fixed class whitelist" in self.lower)
            or ("not a fixed class whitelist" in self.lower)
            or ("not restricted to a fixed class whitelist" in self.lower),
            "Render stage must state it is NOT limited to a fixed pre-existing class whitelist",
        )

    def test_conservative_fallback_when_section9_missing(self):
        self.assertTrue(
            ("conservative" in self.lower) and ("symmetric" in self.lower),
            "Render stage must define a conservative symmetric fallback when §9 lacks "
            "the expression-range fields",
        )

    def test_hard_floor_canonical_token_no_bare_hex_restated(self):
        self.assertIn(
            "canonical token",
            self.lower,
            "Render stage must restate that all colors go through canonical tokens",
        )
        self.assertIn(
            "bare hex",
            self.lower,
            "Render stage must restate the no-bare-hex hard floor",
        )


if __name__ == "__main__":
    unittest.main()
