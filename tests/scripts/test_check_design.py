#!/usr/bin/env python3
"""Tests for plugins/baransu/skills/design/scripts/check.py.

Coverage — extending lint with path-triggered new rules for:
  - swiss-preset tokens.css (3 checks: preset comment, --accent token, no serif in font stack)
  - slide-cores HTML (4 checks: data-layout attr, YAML front-matter, figcaption, class prefix)

Regression invariants (既有規則 100% 保留):
  - 紙-preset/tokens.css behavior unchanged (same warm-tones / no-rgba / line-height findings)
  - 紙-preset/DESIGN.md behavior unchanged
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

# Resolve repo paths. Tests can run from either the worktree or main repo;
# we always invoke the check.py from this worktree, but lint targets live in
# the *main* working tree (Wave 1 artifacts are untracked in main).
THIS_FILE = Path(__file__).resolve()
WORKTREE_ROOT = THIS_FILE.parents[2]
MAIN_ROOT = Path("/home/vakarve/projects/baransu")

CHECK_PY = WORKTREE_ROOT / "plugins" / "baransu" / "skills" / "design" / "scripts" / "check.py"

SWISS_TOKENS = MAIN_ROOT / "plugins/baransu/skills/design/references/swiss-preset/tokens.css"
SLIDE_CORES_DIR = MAIN_ROOT / "plugins/baransu/skills/design/references/slide-cores"
KAMI_DIR = MAIN_ROOT / "plugins/baransu/skills/design/references/紙-preset"


def run_check(*targets: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CHECK_PY), *[str(t) for t in targets]],
        capture_output=True,
        text=True,
    )


class TestSwissPresetTokensLint(unittest.TestCase):
    """REQ-005 Scenario 1 / 2 — swiss-preset/ path triggers new tokens.css checks."""

    def test_real_swiss_preset_tokens_css_passes(self):
        """Scenario 1: actual swiss-preset/tokens.css linted against new rules — PASS."""
        self.assertTrue(SWISS_TOKENS.exists(), f"missing fixture: {SWISS_TOKENS}")
        result = run_check(SWISS_TOKENS)
        self.assertEqual(
            result.returncode, 0,
            f"swiss-preset/tokens.css must PASS but exit={result.returncode}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )

    def test_missing_accent_token_fails(self):
        """Scenario 2: synthetic swiss tokens.css without --accent — FAIL with explicit message."""
        with tempfile.TemporaryDirectory() as tmp:
            target_dir = Path(tmp) / "swiss-preset"
            target_dir.mkdir()
            css = target_dir / "tokens.css"
            css.write_text(textwrap.dedent("""\
                /* preset: swiss */
                :root {
                  --paper: #fafaf8;
                  --ink: #0a0a0a;
                  --font-sans: 'Inter', 'Helvetica Neue', sans-serif;
                }
            """))
            result = run_check(css)
            self.assertEqual(result.returncode, 1,
                             f"expected exit=1, got {result.returncode}\n{result.stdout}")
            self.assertIn("swiss preset 缺 --accent token", result.stdout,
                          f"expected diagnostic text not found in:\n{result.stdout}")

    def test_missing_preset_comment_fails(self):
        """Missing /* preset: swiss */ header → FAIL."""
        with tempfile.TemporaryDirectory() as tmp:
            target_dir = Path(tmp) / "swiss-preset"
            target_dir.mkdir()
            css = target_dir / "tokens.css"
            css.write_text(textwrap.dedent("""\
                :root {
                  --accent: #002FA7;
                  --font-sans: 'Inter', sans-serif;
                }
            """))
            result = run_check(css)
            self.assertEqual(result.returncode, 1)
            self.assertIn("preset", result.stdout.lower())

    def test_serif_in_font_stack_fails(self):
        """Font stack containing the standalone `serif` word — FAIL.

        Boundary-aware: `sans-serif` keyword must NOT trigger this check.
        """
        with tempfile.TemporaryDirectory() as tmp:
            target_dir = Path(tmp) / "swiss-preset"
            target_dir.mkdir()
            css = target_dir / "tokens.css"
            css.write_text(textwrap.dedent("""\
                /* preset: swiss */
                :root {
                  --accent: #002FA7;
                  --font-sans: 'Inter', 'Times New Roman', serif;
                }
            """))
            result = run_check(css)
            self.assertEqual(result.returncode, 1,
                             f"font stack with bare serif must FAIL\n{result.stdout}")
            self.assertIn("serif", result.stdout.lower())

    def test_sans_serif_keyword_does_not_trigger_serif_rule(self):
        """`sans-serif` is the canonical Swiss fallback — must NOT trigger no-serif rule."""
        with tempfile.TemporaryDirectory() as tmp:
            target_dir = Path(tmp) / "swiss-preset"
            target_dir.mkdir()
            css = target_dir / "tokens.css"
            css.write_text(textwrap.dedent("""\
                /* preset: swiss */
                :root {
                  --accent: #002FA7;
                  --font-sans: 'Inter', 'Helvetica Neue', sans-serif;
                }
            """))
            result = run_check(css)
            self.assertEqual(result.returncode, 0,
                             f"sans-serif keyword must NOT fail\n{result.stdout}")


class TestSlideCoresHtmlLint(unittest.TestCase):
    """REQ-005 Scenario 3 / 4 — slide-cores/ path triggers new HTML checks."""

    def test_all_nine_real_slide_cores_pass(self):
        """Scenario 3: all 9 real slide-core HTML files PASS new lint."""
        self.assertTrue(SLIDE_CORES_DIR.is_dir(), f"missing fixture dir: {SLIDE_CORES_DIR}")
        files = sorted(SLIDE_CORES_DIR.glob("*.html"))
        self.assertEqual(len(files), 9, f"expected 9 slide-cores, found {len(files)}: {files}")
        result = run_check(SLIDE_CORES_DIR)
        self.assertEqual(
            result.returncode, 0,
            f"slide-cores/ must PASS but exit={result.returncode}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )

    def test_missing_yaml_front_matter_fails(self):
        """Scenario 4: slide-core HTML without YAML front-matter — FAIL."""
        with tempfile.TemporaryDirectory() as tmp:
            target_dir = Path(tmp) / "slide-cores"
            target_dir.mkdir()
            html = target_dir / "cover.html"
            html.write_text(textwrap.dedent("""\
                <section data-layout="cover" class="swiss-slide swiss-slide--cover">
                  <h1>Cover</h1>
                  <figcaption>caption</figcaption>
                </section>
            """))
            result = run_check(html)
            self.assertEqual(result.returncode, 1,
                             f"missing YAML must FAIL\n{result.stdout}")
            self.assertIn("yaml", result.stdout.lower())

    def test_yaml_missing_layout_id_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            target_dir = Path(tmp) / "slide-cores"
            target_dir.mkdir()
            html = target_dir / "cover.html"
            html.write_text(textwrap.dedent("""\
                <!--
                ---
                applies_to:
                  role: body
                ---
                -->
                <section data-layout="cover" class="swiss-slide">
                  <figcaption>caption</figcaption>
                </section>
            """))
            result = run_check(html)
            self.assertEqual(result.returncode, 1)
            self.assertIn("layout_id", result.stdout)

    def test_yaml_missing_applies_to_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            target_dir = Path(tmp) / "slide-cores"
            target_dir.mkdir()
            html = target_dir / "cover.html"
            html.write_text(textwrap.dedent("""\
                <!--
                ---
                layout_id: cover
                ---
                -->
                <section data-layout="cover" class="swiss-slide">
                  <figcaption>caption</figcaption>
                </section>
            """))
            result = run_check(html)
            self.assertEqual(result.returncode, 1)
            self.assertIn("applies_to", result.stdout)

    def test_missing_data_layout_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            target_dir = Path(tmp) / "slide-cores"
            target_dir.mkdir()
            html = target_dir / "cover.html"
            html.write_text(textwrap.dedent("""\
                <!--
                ---
                layout_id: cover
                applies_to:
                  role: body
                ---
                -->
                <section class="swiss-slide">
                  <figcaption>caption</figcaption>
                </section>
            """))
            result = run_check(html)
            self.assertEqual(result.returncode, 1)
            self.assertIn("data-layout", result.stdout)

    def test_missing_figcaption_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            target_dir = Path(tmp) / "slide-cores"
            target_dir.mkdir()
            html = target_dir / "cover.html"
            html.write_text(textwrap.dedent("""\
                <!--
                ---
                layout_id: cover
                applies_to:
                  role: body
                ---
                -->
                <section data-layout="cover" class="swiss-slide">
                  <h1>Cover</h1>
                </section>
            """))
            result = run_check(html)
            self.assertEqual(result.returncode, 1)
            self.assertIn("figcaption", result.stdout.lower())

    def test_mixed_class_prefix_fails(self):
        """Same file mixing kami-* and swiss-* class prefixes — FAIL."""
        with tempfile.TemporaryDirectory() as tmp:
            target_dir = Path(tmp) / "slide-cores"
            target_dir.mkdir()
            html = target_dir / "cover.html"
            html.write_text(textwrap.dedent("""\
                <!--
                ---
                layout_id: cover
                applies_to:
                  role: body
                ---
                -->
                <section data-layout="cover" class="swiss-slide kami-cover-frame">
                  <figcaption class="swiss-cover-caption">cap</figcaption>
                </section>
            """))
            result = run_check(html)
            self.assertEqual(result.returncode, 1,
                             f"mixed prefix must FAIL\n{result.stdout}")
            self.assertIn("prefix", result.stdout.lower())

    def test_kami_only_prefix_passes(self):
        """All-kami-* prefix in slide-core HTML — PASS."""
        with tempfile.TemporaryDirectory() as tmp:
            target_dir = Path(tmp) / "slide-cores"
            target_dir.mkdir()
            html = target_dir / "cover.html"
            html.write_text(textwrap.dedent("""\
                <!--
                ---
                layout_id: cover
                applies_to:
                  role: body
                ---
                -->
                <section data-layout="cover" class="kami-slide kami-cover">
                  <h1 class="kami-cover-title">Title</h1>
                  <figcaption class="kami-cover-caption">cap</figcaption>
                </section>
            """))
            result = run_check(html)
            self.assertEqual(result.returncode, 0,
                             f"kami-only prefix must PASS\n{result.stdout}")


class TestExistingRulesRegression(unittest.TestCase):
    """Constraint: 既有 nine-section + Kami invariant lint 完全保留.

    Behavior on 紙-preset/ artifacts must be byte-equivalent to pre-change baseline.
    """

    # Pre-change baseline captured from running existing check.py on 紙-preset/
    # (see ctx — task requires "既有 fixture 跑出來行為等價"):
    #   2 violations in 紙-preset/tokens.css:
    #     L46 [#8 no-rgba] rgba() outside box-shadow
    #     L102 [#6 line-height] line-height 1.6 > 1.55 for body text
    #   0 violations in 紙-preset/DESIGN.md
    EXPECTED_KAMI_VIOLATION_COUNT = 2
    EXPECTED_KAMI_WARM_TONES_HITS = 0

    def test_kami_preset_directory_regression(self):
        self.assertTrue(KAMI_DIR.is_dir(), f"missing baseline dir: {KAMI_DIR}")
        result = run_check(KAMI_DIR)
        # Should still fail with exit=1 (baseline has 2 violations)
        self.assertEqual(result.returncode, 1,
                         f"baseline 紙-preset must still flag violations\n{result.stdout}")
        # Count specific violations to detect regression in either direction
        no_rgba_hits = result.stdout.count("[#8 no-rgba]")
        line_height_hits = result.stdout.count("[#6 line-height]")
        warm_tone_hits = result.stdout.count("[#3 warm-tones]")
        self.assertEqual(no_rgba_hits, 1,
                         f"expected exactly 1 no-rgba hit on 紙-preset, got {no_rgba_hits}\n{result.stdout}")
        self.assertEqual(line_height_hits, 1,
                         f"expected exactly 1 line-height hit on 紙-preset, got {line_height_hits}")
        self.assertEqual(warm_tone_hits, self.EXPECTED_KAMI_WARM_TONES_HITS,
                         f"cool-gray hit count regression on 紙-preset: "
                         f"baseline={self.EXPECTED_KAMI_WARM_TONES_HITS}, now={warm_tone_hits}")


if __name__ == "__main__":
    unittest.main()
