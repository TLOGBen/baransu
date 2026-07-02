#!/usr/bin/env python3
"""Tests for plugins/baransu/skills/_shared/scripts/color_distance.py.

REQ-002 (TASK-shared-01) — color-distance validation tool: advisory-only,
non-blocking colorblind-simulation distinguishability check, callable by
both `/design` (bakes candidate color sets into tokens.css) and `/book`
(re-validates a chart's actually-selected color subset).

Coverage:
  - Scenario 1: adjacent-pair distinguishability computed via real
    colorblind-simulation math (not naive RGB distance), reported with
    non-blocking vocabulary ("adequate"/"marginal"/"low", never "pass"/"fail").
  - Boundary: fewer than 2 colors -> "unverifiable", never throws.
  - Boundary: invalid hex color format -> "unverifiable", never throws.
"""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

# Resolve repo paths relative to this file so the suite passes from any
# checkout (main repo or git worktree).
THIS_FILE = Path(__file__).resolve()
WORKTREE_ROOT = THIS_FILE.parents[2]

SCRIPT = (
    WORKTREE_ROOT
    / "plugins" / "baransu" / "skills" / "_shared" / "scripts" / "color_distance.py"
)


def run_tool(colors: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), ",".join(colors)],
        capture_output=True,
        text=True,
    )


class TestColorDistanceComputation(unittest.TestCase):
    """REQ-002 Scenario 1 — per-adjacent-pair distinguishability under CVD simulation."""

    def test_computes_advisory_label_per_adjacent_pair(self):
        # High-contrast pair (black/white) must be clearly "adequate" under
        # every colorblind simulation.
        proc = run_tool(["#000000", "#ffffff"])
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        result = json.loads(proc.stdout)
        self.assertEqual(result["status"], "computed")
        self.assertEqual(len(result["pairs"]), 1)
        pair = result["pairs"][0]
        self.assertEqual(pair["color_a"], "#000000")
        self.assertEqual(pair["color_b"], "#ffffff")
        self.assertIsInstance(pair["distance"], (int, float))
        self.assertEqual(pair["advisory_label"], "adequate")

        # Red vs olive/brown is a documented protanopia confusion pair — it
        # must be flagged as poorly distinguishable ("low"). A naive
        # plain-RGB Euclidean distance would call this pair highly distinct
        # (large raw RGB delta), so a "low" result here proves the tool
        # actually runs colorblind-simulation math, not raw RGB distance.
        confusion_proc = run_tool(["#ff0000", "#996600"])
        self.assertEqual(confusion_proc.returncode, 0, msg=confusion_proc.stderr)
        confusion_result = json.loads(confusion_proc.stdout)
        confusion_pair = confusion_result["pairs"][0]
        self.assertEqual(confusion_pair["advisory_label"], "low")

    def test_returns_a_pair_for_every_adjacent_color_in_a_longer_list(self):
        # N colors -> N-1 adjacent pairs, in list order (not full combinatorics).
        proc = run_tool(["#000000", "#ffffff", "#000000"])
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        result = json.loads(proc.stdout)
        self.assertEqual(result["status"], "computed")
        self.assertEqual(len(result["pairs"]), 2)
        self.assertEqual(
            [(p["color_a"], p["color_b"]) for p in result["pairs"]],
            [("#000000", "#ffffff"), ("#ffffff", "#000000")],
        )

    def test_result_payload_contains_no_block_or_fail_vocabulary(self):
        proc = run_tool(["#000000", "#ffffff"])
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        result = json.loads(proc.stdout)
        payload_text = json.dumps(result).lower()
        self.assertNotIn('"pass"', payload_text)
        self.assertNotIn('"fail"', payload_text)
        self.assertNotIn('"block"', payload_text)


class TestColorDistanceBoundaries(unittest.TestCase):
    """REQ-002 boundary handling — advisory tool never throws."""

    def test_fewer_than_two_colors_returns_unverifiable_without_throwing(self):
        proc = run_tool(["#ff0000"])
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        self.assertEqual(proc.stderr, "")
        result = json.loads(proc.stdout)
        self.assertEqual(result["status"], "unverifiable")
        self.assertEqual(result["pairs"], [])
        self.assertIn("reason", result)

        empty_proc = run_tool([])
        self.assertEqual(empty_proc.returncode, 0, msg=empty_proc.stderr)
        empty_result = json.loads(empty_proc.stdout)
        self.assertEqual(empty_result["status"], "unverifiable")
        self.assertEqual(empty_result["pairs"], [])

    def test_invalid_hex_format_returns_unverifiable_without_throwing(self):
        proc = run_tool(["#ff0000", "not-a-color"])
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        self.assertEqual(proc.stderr, "")
        result = json.loads(proc.stdout)
        self.assertEqual(result["status"], "unverifiable")
        self.assertEqual(result["pairs"], [])
        self.assertIn("reason", result)
        self.assertIn("not-a-color", result["reason"])


if __name__ == "__main__":
    unittest.main()
