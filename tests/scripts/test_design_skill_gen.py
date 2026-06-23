#!/usr/bin/env python3
"""Structural assertions for /design Gen Mode Step 1 — extreme-commitment framing.

TASK-design-skill-01 (REQ-004) — the gen interview's intensity/boldness axis is
reframed into "commit to one clear extreme". The chosen extreme is an EQUAL peer
(極簡 minimal is a chosen extreme, NOT a default safe value) and drives BOTH
derivation lines: (a) capability-token VALUE derivation and (b) §9 expression-range
authoring. This test reads the design SKILL.md and asserts the Step 1 region carries
that framing.
"""

from __future__ import annotations

import unittest
from pathlib import Path

THIS_FILE = Path(__file__).resolve()
WORKTREE_ROOT = THIS_FILE.parents[2]
SKILL = WORKTREE_ROOT / "plugins" / "baransu" / "skills" / "design" / "SKILL.md"


def gen_step1_region(text: str) -> str:
    """Isolate the Gen Mode 'Step 1' region (from its header to the next '### Step ' or '## ')."""
    marker = "### Step 1 — Ask direction questions"
    start = text.find(marker)
    assert start != -1, "Gen Mode 'Step 1 — Ask direction questions' header not found"
    body = text[start + len(marker):]
    # The region ends at the next top-level '## ' Mode header (Step 1.5 / Step 2 stay inside).
    nxt = body.find("\n## ")
    return body if nxt == -1 else body[:nxt]


class TestGenStep1ExtremeCommitment(unittest.TestCase):
    def setUp(self) -> None:
        self.region = gen_step1_region(SKILL.read_text(encoding="utf-8"))
        self.lower = self.region.lower()

    def test_extreme_commitment_framing_present(self):
        """Step 1 mentions an extreme-commitment framing with a list of extremes."""
        self.assertIn(
            "extreme",
            self.lower,
            "Gen Step 1 must frame the axis as committing to an 'extreme'",
        )
        for extreme in ("minimal", "maximal", "brutalist"):
            self.assertIn(
                extreme,
                self.lower,
                f"Gen Step 1 extreme list must include '{extreme}'",
            )

    def test_memorable_hook_prompt_present(self):
        """Step 1 adds a 記憶點 (memorable hook) interaction point."""
        self.assertTrue(
            ("記憶點" in self.region) or ("memorable hook" in self.lower),
            "Gen Step 1 must add a memorable-hook (記憶點) prompt",
        )

    def test_minimal_marked_as_chosen_equal_extreme_not_default(self):
        """Minimal is a CHOSEN/EQUAL extreme, explicitly not a default safe value."""
        chosen = ("chosen extreme" in self.lower) or ("equal" in self.lower) or (
            "平等極端" in self.region
        )
        self.assertTrue(
            chosen,
            "Gen Step 1 must mark minimal as a chosen/equal extreme",
        )
        self.assertTrue(
            ("not a default" in self.lower)
            or ("not a default safe value" in self.lower)
            or ("non-default" in self.lower)
            or ("not the default" in self.lower),
            "Gen Step 1 must state minimal is NOT a default safe value",
        )

    def test_both_derivation_lines_referenced(self):
        """The chosen extreme drives BOTH token-value derivation AND §9 expression range."""
        # Line (a): capability-token value derivation.
        token_line = (
            ("--shadow-drama" in self.region)
            or ("--stagger-step" in self.region)
            or ("--duration" in self.region)
            or ("capability-token" in self.lower)
            or ("capability token" in self.lower)
        )
        self.assertTrue(
            token_line,
            "Gen Step 1 must reference the capability-token VALUE derivation line",
        )
        # Line (b): §9 expression-range authoring.
        s9_line = ("§9" in self.region) or ("expression range" in self.lower) or (
            "表現範圍" in self.region
        )
        self.assertTrue(
            s9_line,
            "Gen Step 1 must reference the §9 expression-range authoring line",
        )


if __name__ == "__main__":
    unittest.main()
