#!/usr/bin/env python3
"""Tests for the /book Stage 4 "Validator division of labor" verification split.

TASK-book-skill-02 — the Validator section must articulate the two-tier split:

  1. HARD FLOOR — a blocking mechanical gate (validate-output.ts) covering
     token-only / no-rgba / accent ≤5% / PDF-safe; a violation = GATE FAIL.
  2. SOFT RANGE — style-reviewer + a few mechanical heuristics (bare hex,
     second accent, column width past the §9 ceiling) — NON-blocking opinion,
     recorded in the review, never blocking output.

The split must be explicit (hard floor blocks; soft range advises) and must
reference validate-output.ts as the hard-floor mechanism.
"""

from __future__ import annotations

import unittest
from pathlib import Path

THIS_FILE = Path(__file__).resolve()
WORKTREE_ROOT = THIS_FILE.parents[2]
SKILL = WORKTREE_ROOT / "plugins" / "baransu" / "skills" / "book" / "SKILL.md"


def validator_section(text: str) -> str:
    """Isolate the '## Validator division of labor' section (up to next '## ' or EOF)."""
    marker = "## Validator division of labor"
    start = text.find(marker)
    assert start != -1, "'## Validator division of labor' header not found"
    body = text[start:]
    nxt = body.find("\n## ", len(marker))
    return body if nxt == -1 else body[:nxt]


class TestValidatorDivision(unittest.TestCase):
    def setUp(self) -> None:
        self.full = SKILL.read_text(encoding="utf-8")
        self.section = validator_section(self.full)
        self.lower = self.section.lower()

    def test_names_hard_floor_as_blocking_mechanical_gate(self):
        """(1) Hard floor named as a blocking mechanical gate covering all four items."""
        self.assertIn("hard floor", self.lower, "section must name the 'hard floor'")
        self.assertTrue(
            "blocking" in self.lower or "gate fail" in self.lower or "blocks" in self.lower,
            "hard floor must be described as blocking (gate fail / blocks)",
        )
        # All four hard-floor items must be named.
        self.assertIn("token-only", self.lower)
        self.assertIn("rgba", self.lower)
        self.assertTrue(
            "accent" in self.lower and "5%" in self.section,
            "accent ≤5% must be named",
        )
        self.assertTrue(
            "pdf-safe" in self.lower or "pdf safe" in self.lower,
            "PDF-safe must be named",
        )

    def test_names_soft_range_as_nonblocking_opinion(self):
        """(2) Soft range named as style-reviewer + heuristics, non-blocking opinion."""
        self.assertIn("soft range", self.lower, "section must name the 'soft range'")
        self.assertIn("style-reviewer", self.lower)
        self.assertTrue(
            "non-blocking" in self.lower or "advises" in self.lower or "opinion" in self.lower,
            "soft range must be described as non-blocking / opinion / advises",
        )
        # The soft mechanical heuristics must be named.
        self.assertIn("bare hex", self.lower)
        self.assertTrue(
            "second accent" in self.lower or "second-accent" in self.lower,
            "soft range must name the second-accent heuristic",
        )
        self.assertIn("column width", self.lower)

    def test_references_validate_output_as_hard_floor_mechanism(self):
        """(3) validate-output.ts referenced as the hard-floor mechanism."""
        self.assertIn("validate-output.ts", self.section)

    def test_makes_division_explicit(self):
        """The hard-blocks / soft-advises division is stated explicitly."""
        self.assertTrue(
            "hard floor blocks" in self.lower or ("hard floor" in self.lower and "blocks" in self.lower),
            "must state the hard floor blocks",
        )
        self.assertTrue(
            "soft range advises" in self.lower or ("soft range" in self.lower and "advises" in self.lower),
            "must state the soft range advises",
        )


if __name__ == "__main__":
    unittest.main()
