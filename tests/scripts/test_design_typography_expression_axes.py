#!/usr/bin/env python3
"""Structural assertions for the design-axes cluster — typography discipline
(size-inverse weight ladder + text-adaptation gotcha trio) and the two optional
expression axes (background texture, motion budget).

/design is a prose-driven skill (SKILL.md executed by an LLM agent) — see
tests/scripts/test_design_chart_capability_skill.py for the established
precedent of asserting SKILL.md prose via structural/regex checks. This suite
covers:

  1. Existence + Gen Mode Step 2 wiring of the two new reference files.
  2. Lossless move of the extreme→value lookup table from SKILL.md into
     canonical-tokens.md (all four data rows pinned verbatim), while the
     Step 1 derivation-line invariants stay independently guarded.
  3. Weight-ladder invariants (per-view monotonicity, small-text floor, the
     two mirrored anti-pattern names) present in typography-discipline.md.
  4. The text-adaptation trio present as IF-THEN rules.
  5. Expression-axes rung shape (texture x4 with flat default, motion x3),
     prefers-reduced-motion floor, I3 restatement, INFORM framing.
  6. No new token DEFINITIONS smuggled into either reference file.
  7. Optionality guard: the three shipped presets and check.py untouched.
  8. The Slide Layout Registry sentence upgraded to 15 slide-embeddable types.
"""

from __future__ import annotations

import hashlib
import re
import subprocess
import unittest
from pathlib import Path

THIS_FILE = Path(__file__).resolve()
WORKTREE_ROOT = THIS_FILE.parents[2]
DESIGN = WORKTREE_ROOT / "plugins" / "baransu" / "skills" / "design"
SKILL = DESIGN / "SKILL.md"
CHECK_PY = DESIGN / "scripts" / "check.py"
REFS = DESIGN / "references"
TYPOGRAPHY = REFS / "typography-discipline.md"
AXES = REFS / "expression-axes.md"
CANONICAL = REFS / "canonical-tokens.md"

# check.py is explicitly OUT of this cluster's file scope (same pin as
# tests/scripts/test_book_accent_chart_exception.py).
CHECK_PY_SHA256 = (
    "4c5d8326b13f94722cb4d53b2989ed5d2e586bbec8c3a95811a5e779334d317f"
)

# The four extreme→value data rows, pinned VERBATIM from design SKILL.md
# L269-272 as they read before the move (lossless-move contract).
EXTREME_ROWS = [
    "| 極簡 minimal | 160–220ms | 30–40ms | calm `cubic-bezier(.4,0,.2,1)` | "
    "soft, alpha ≤0.10 | low / overlap ≤5% | ≤66ch |",
    "| 極繁 maximal | 320–480ms | 60–90ms | emphasized `cubic-bezier(.2,0,0,1)` | "
    "deep, alpha 0.18–0.30 | high / overlap 20–40% | ≤90ch |",
    "| brutalist | 0–140ms | 0–20ms | linear / step | hard offset, 0-blur alpha ≥0.4 | "
    "high, grid-broken / overlap ≤50% | full-bleed |",
    "| editorial | 240–360ms | 50–70ms | decelerate `cubic-bezier(0,0,.2,1)` | "
    "medium, alpha 0.10–0.16 | mid / overlap 10–20% | 60–72ch |",
]

# Exact anti-pattern names chosen in typography-discipline.md §1.
ANTI_PATTERN_BOLD = "bold giant display"
ANTI_PATTERN_LIGHT = "light small caption"


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


def gen_step1_region(text: str) -> str:
    return _extract_region(
        text,
        "### Step 1 — Ask direction questions",
        ["\n### Step 2 — Generate DESIGN.md"],
    )


def gen_step2_region(text: str) -> str:
    return _extract_region(
        text,
        "### Step 2 — Generate DESIGN.md",
        ["\n### Step 3"],
    )


def git_diff_touched(path: Path) -> bool:
    """True if `path` differs from HEAD (tracked-file regression guard)."""
    rel = path.relative_to(WORKTREE_ROOT)
    result = subprocess.run(
        ["git", "-C", str(WORKTREE_ROOT), "diff", "--name-only", "HEAD", "--", str(rel)],
        capture_output=True, text=True, check=True,
    )
    return bool(result.stdout.strip())


class TestExistenceAndWiring(unittest.TestCase):
    """(1) — both reference files exist and Gen Mode Step 2 points at them."""

    def test_reference_files_exist(self):
        self.assertTrue(TYPOGRAPHY.exists(), f"{TYPOGRAPHY} must exist")
        self.assertTrue(AXES.exists(), f"{AXES} must exist")

    def test_step2_region_points_at_both_files(self):
        region = gen_step2_region(SKILL.read_text(encoding="utf-8"))
        self.assertIn(
            "references/typography-discipline.md", region,
            "Gen Mode Step 2 must point at the typography-discipline reference",
        )
        self.assertIn(
            "references/expression-axes.md", region,
            "Gen Mode Step 2 must point at the expression-axes reference",
        )


class TestLosslessTableMove(unittest.TestCase):
    """(2) — the extreme→value table moved verbatim to canonical-tokens.md."""

    @classmethod
    def setUpClass(cls):
        cls.canonical = CANONICAL.read_text(encoding="utf-8")
        cls.skill = SKILL.read_text(encoding="utf-8")

    def test_lookup_section_exists_in_canonical_tokens(self):
        self.assertIn("## Extreme → Value Lookup", self.canonical)

    def test_all_four_rows_verbatim_in_canonical_tokens(self):
        for row in EXTREME_ROWS:
            self.assertIn(
                row, self.canonical,
                f"canonical-tokens.md must carry this row verbatim: {row[:40]}...",
            )

    def test_moved_row_absent_from_skill(self):
        # Spot-check one moved row (極繁 maximal) is no longer in SKILL.md.
        self.assertNotIn(
            EXTREME_ROWS[1], self.skill,
            "SKILL.md must no longer carry the moved 極繁 table row",
        )

    def test_step1_derivation_invariants_still_present(self):
        # Guards test_design_skill_gen's invariant independently: the Step 1
        # region still names the capability tokens after the table move.
        region = gen_step1_region(self.skill)
        self.assertIn("--stagger-step", region)
        self.assertIn("--shadow-drama", region)


class TestWeightLadderInvariants(unittest.TestCase):
    """(3) — typography-discipline.md carries the ladder's enforcement form."""

    @classmethod
    def setUpClass(cls):
        cls.text = TYPOGRAPHY.read_text(encoding="utf-8")
        cls.lower = cls.text.lower()

    def test_per_view_monotonicity_present(self):
        self.assertIn("monotonic", self.lower)

    def test_small_text_floor_present(self):
        self.assertRegex(self.lower, r"floor")

    def test_both_mirrored_anti_patterns_named(self):
        self.assertIn(ANTI_PATTERN_BOLD, self.lower)
        self.assertIn(ANTI_PATTERN_LIGHT, self.lower)


class TestTextAdaptationTrio(unittest.TestCase):
    """(4) — the gotcha trio is expressed as IF-THEN rules."""

    @classmethod
    def setUpClass(cls):
        cls.text = TYPOGRAPHY.read_text(encoding="utf-8")

    def test_at_least_three_if_then_lines(self):
        # Rules may wrap across lines; count per paragraph-joined line first,
        # then fall back to counting lines that open an IF clause.
        if_then_lines = [
            line for line in self.text.splitlines()
            if "IF " in line and " THEN" in line
        ]
        if_lines = [line for line in self.text.splitlines() if "IF " in line]
        self.assertGreaterEqual(
            max(len(if_then_lines), len(if_lines)), 3,
            "typography-discipline.md must express >=3 IF-THEN rules",
        )
        self.assertGreaterEqual(
            self.text.count(" THEN"), 3,
            "each IF must pair with a THEN action",
        )

    def test_trio_subjects_represented(self):
        lower = self.text.lower()
        self.assertIn("orphan", lower)
        self.assertIn("truncat", lower)
        self.assertIn('lang="zh"', self.text)


class TestExpressionAxesShape(unittest.TestCase):
    """(5) — rung structure, defaults, floors, and INFORM framing."""

    @classmethod
    def setUpClass(cls):
        cls.text = AXES.read_text(encoding="utf-8")

    def test_four_texture_rungs_present(self):
        for rung in ("flat", "paper-grain", "structured-noise", "gradient"):
            self.assertIn(f"**{rung}**", self.text, f"texture rung {rung} missing")

    def test_flat_marked_default_on_its_rung_line(self):
        flat_lines = [
            line for line in self.text.splitlines()
            if "**flat**" in line and "DEFAULT" in line
        ]
        self.assertTrue(
            flat_lines, "the flat rung line must mark flat as the DEFAULT")

    def test_three_motion_rungs_present(self):
        for rung in ("none", "functional", "expressive"):
            self.assertIn(f"**{rung}**", self.text, f"motion rung {rung} missing")

    def test_reduced_motion_floor_present(self):
        self.assertIn("prefers-reduced-motion", self.text)

    def test_i3_restated(self):
        self.assertIn("static final state", self.text)

    def test_inform_framing_in_both_new_files(self):
        self.assertIn("INFORM", self.text)
        self.assertIn("INFORM", TYPOGRAPHY.read_text(encoding="utf-8"))


class TestNoNewTokenDefinitions(unittest.TestCase):
    """(6) — the new references describe tokens, never define them."""

    DEFINITION_RE = re.compile(r"^\s*--[a-z-]+\s*:")

    def test_no_definition_lines(self):
        for path in (TYPOGRAPHY, AXES):
            with self.subTest(file=path.name):
                for n, line in enumerate(
                        path.read_text(encoding="utf-8").splitlines(), 1):
                    self.assertIsNone(
                        self.DEFINITION_RE.match(line),
                        f"{path.name}:{n} looks like a token DEFINITION: {line!r}",
                    )


class TestOptionalityGuard(unittest.TestCase):
    """(7) — presets and check.py are byte-untouched (absence degrades safely)."""

    PRESET_DIRS = [
        REFS / "紙-preset",
        REFS / "swiss-preset",
        REFS / "google-design-preset",
    ]

    def test_preset_dirs_untouched(self):
        for preset_dir in self.PRESET_DIRS:
            with self.subTest(preset=preset_dir.name):
                self.assertFalse(
                    git_diff_touched(preset_dir),
                    f"{preset_dir.name} must not be touched by this cluster",
                )

    def test_check_py_content_hash_unchanged(self):
        actual = hashlib.sha256(CHECK_PY.read_bytes()).hexdigest()
        self.assertEqual(
            actual, CHECK_PY_SHA256,
            "check.py is explicitly OUT of this cluster's file scope — "
            "no new required tokens, sections, or schema numbers",
        )


class TestSlideLayoutRegistryFifteenTypes(unittest.TestCase):
    """(8) — canonical-tokens.md registry sentence upgraded 13 → 15."""

    @classmethod
    def setUpClass(cls):
        cls.text = CANONICAL.read_text(encoding="utf-8")

    def test_fifteen_slide_embeddable_wording(self):
        self.assertIn("15 slide-embeddable", self.text)
        self.assertNotIn("the 13 status=complete", self.text)

    def test_new_types_listed(self):
        self.assertIn("org-chart", self.text)
        self.assertIn("/ org-chart / class`", self.text)


if __name__ == "__main__":
    unittest.main()
