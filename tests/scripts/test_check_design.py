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

import importlib.util
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

# Resolve repo paths relative to this file so the suite passes from any
# checkout (main repo or git worktree). All lint fixtures are tracked.
THIS_FILE = Path(__file__).resolve()
WORKTREE_ROOT = THIS_FILE.parents[2]
MAIN_ROOT = WORKTREE_ROOT

CHECK_PY = WORKTREE_ROOT / "plugins" / "baransu" / "skills" / "design" / "scripts" / "check.py"

SWISS_TOKENS = MAIN_ROOT / "plugins/baransu/skills/design/references/swiss-preset/tokens.css"
SLIDE_CORES_DIR = MAIN_ROOT / "plugins/baransu/skills/design/references/紙-preset/slide-cores"
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

    def test_all_real_slide_cores_pass(self):
        """Scenario 3: all real slide-core HTML files PASS new lint (21 as of 2.1.2)."""
        self.assertTrue(SLIDE_CORES_DIR.is_dir(), f"missing fixture dir: {SLIDE_CORES_DIR}")
        files = sorted(SLIDE_CORES_DIR.glob("*.html"))
        self.assertEqual(len(files), 21, f"expected 21 slide-cores, found {len(files)}: {files}")
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


def _load_check_module():
    """Import check.py as a module to access its constants directly."""
    spec = importlib.util.spec_from_file_location("check_design_under_test", CHECK_PY)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestCanonicalTokenSplit(unittest.TestCase):
    """TASK-gate-01 — canonical truth source splits into BASE + CAPABILITY constants.

    REQ-005 Scenario 1: count 機制版本化——BASE_TOKENS(38) + CAPABILITY_TOKENS(5),
    combined CANONICAL_TOKENS == 43. grain-opacity intentionally excluded.
    """

    EXPECTED_CAPABILITY = [
        "--ease", "--duration", "--stagger-step", "--font-display", "--shadow-drama",
    ]

    def setUp(self):
        self.mod = _load_check_module()

    def test_base_tokens_has_38(self):
        self.assertEqual(len(self.mod.BASE_TOKENS), 38)

    def test_capability_tokens_exact_five(self):
        self.assertEqual(self.mod.CAPABILITY_TOKENS, self.EXPECTED_CAPABILITY)
        self.assertEqual(len(self.mod.CAPABILITY_TOKENS), 5)

    def test_canonical_tokens_is_combined_43(self):
        self.assertEqual(len(self.mod.CANONICAL_TOKENS), 43)
        self.assertEqual(
            self.mod.CANONICAL_TOKENS,
            self.mod.BASE_TOKENS + self.mod.CAPABILITY_TOKENS,
        )

    def test_grain_opacity_excluded(self):
        self.assertNotIn("--grain-opacity", self.mod.CANONICAL_TOKENS)
        self.assertNotIn("--grain-opacity", self.mod.CAPABILITY_TOKENS)


class TestExistingRulesRegression(unittest.TestCase):
    """Constraint: 既有 nine-section + Kami invariant lint 完全保留.

    Behavior on 紙-preset/ artifacts must be byte-equivalent to pre-change baseline.
    """

    # Baseline recalibrated after 30231f3 (kami preset lint-clean, v2.1.2):
    # tokens.css / DESIGN.md / cores are now violation-free. The only remaining
    # hit is check-A artifact-completeness — reference presets ship sources
    # only; DESIGN.html is generated when the preset is applied to a project.
    #   1 violation in 紙-preset/:
    #     L1 [#1 check-A-artifact-completeness] 缺少 v1.3 artifact: DESIGN.html
    EXPECTED_KAMI_VIOLATION_COUNT = 1
    EXPECTED_KAMI_WARM_TONES_HITS = 0

    def test_kami_preset_directory_regression(self):
        self.assertTrue(KAMI_DIR.is_dir(), f"missing baseline dir: {KAMI_DIR}")
        result = run_check(KAMI_DIR)
        # Should still fail with exit=1 (baseline has exactly 1 known violation)
        self.assertEqual(result.returncode, 1,
                         f"baseline 紙-preset must still flag violations\n{result.stdout}")
        # Count specific violations to detect regression in either direction
        artifact_hits = result.stdout.count("[#1 check-A-artifact-completeness]")
        no_rgba_hits = result.stdout.count("[#8 no-rgba]")
        line_height_hits = result.stdout.count("[#6 line-height]")
        warm_tone_hits = result.stdout.count("[#3 warm-tones]")
        self.assertEqual(artifact_hits, 1,
                         f"expected exactly 1 artifact-completeness hit on 紙-preset, "
                         f"got {artifact_hits}\n{result.stdout}")
        self.assertEqual(no_rgba_hits, 0,
                         f"no-rgba regression on lint-clean 紙-preset: got {no_rgba_hits}\n{result.stdout}")
        self.assertEqual(line_height_hits, 0,
                         f"line-height regression on lint-clean 紙-preset: got {line_height_hits}")
        self.assertEqual(warm_tone_hits, self.EXPECTED_KAMI_WARM_TONES_HITS,
                         f"cool-gray hit count regression on 紙-preset: "
                         f"baseline={self.EXPECTED_KAMI_WARM_TONES_HITS}, now={warm_tone_hits}")


class TestParsePresetHeader(unittest.TestCase):
    """TASK-gate-02 — PRESET_HEADER_RE tolerates optional `; schema: <N>`;
    _parse_preset_header returns (slug, version|None)."""

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_check_module()

    def test_legacy_header_no_schema(self):
        """/* preset: kami */ → (kami, None)."""
        self.assertEqual(
            self.mod._parse_preset_header("/* preset: kami */\n"),
            ("kami", None))

    def test_header_with_schema_version(self):
        """/* preset: bold-x; schema: 43 */ → (bold-x, 43)."""
        self.assertEqual(
            self.mod._parse_preset_header("/* preset: bold-x; schema: 43 */\n"),
            ("bold-x", 43))

    def test_malformed_schema_treated_as_no_version(self):
        """Malformed schema field → version None, slug still captured, no error."""
        self.assertEqual(
            self.mod._parse_preset_header("/* preset: bold-x; schema: abc */\n"),
            ("bold-x", None))


class TestCheckBVersionAware(unittest.TestCase):
    """TASK-gate-03 — Check B canonical-completeness is version-aware.

    _check_tokens_canonical_completeness accepts a schema version (default None):
      - version None / 38  → require BASE_TOKENS only (legacy 38-token file passes)
      - version 43         → require BASE + CAPABILITY; missing capability → finding
      - unknown int (99)   → require BASE only + stderr warn, NEVER a finding
    """

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_check_module()

    def _css(self, tokens: list[str]) -> str:
        """Synthetic tokens.css body defining each name as `--x: 0;`."""
        body = "\n".join(f"  {t}: 0;" for t in tokens)
        return ":root {\n" + body + "\n}\n"

    def _findings(self, version, tokens):
        css = self._css(tokens)
        return self.mod._check_tokens_canonical_completeness(
            Path("tokens.css"), css, version)

    def test_legacy_38_no_version_passes(self):
        """version None + only 38 BASE tokens → no findings (legacy file not broken)."""
        self.assertEqual(self._findings(None, self.mod.BASE_TOKENS), [])

    def test_version_38_only_base_required(self):
        """version 38 + only 38 BASE tokens → no findings."""
        self.assertEqual(self._findings(38, self.mod.BASE_TOKENS), [])

    def test_version_43_missing_capability_fails(self):
        """version 43 + only 38 BASE tokens → finding listing missing capability name."""
        findings = self._findings(43, self.mod.BASE_TOKENS)
        self.assertTrue(findings, "schema:43 with only 38 tokens must produce a finding")
        msg = " ".join(f["msg"] for f in findings)
        self.assertIn("--ease", msg)

    def test_version_43_full_43_passes(self):
        """version 43 + all 43 tokens → no findings."""
        self.assertEqual(
            self._findings(43, self.mod.BASE_TOKENS + self.mod.CAPABILITY_TOKENS), [])

    def test_unknown_version_99_never_fails(self):
        """version 99 + only 38 BASE tokens → no findings (BASE required, warn only)."""
        self.assertEqual(self._findings(99, self.mod.BASE_TOKENS), [])


class TestRealPresetsCarry43(unittest.TestCase):
    """TASK-assets-01 — the three real preset tokens.css carry the full 43.

    For each shipped preset: the first-line header must parse to (slug, 43),
    and _check_tokens_canonical_completeness against version 43 must yield
    ZERO findings (all 38 BASE + 5 CAPABILITY tokens defined).
    """

    REFS = MAIN_ROOT / "plugins/baransu/skills/design/references"
    PRESETS = [
        (REFS / "紙-preset/tokens.css", "kami"),
        (REFS / "swiss-preset/tokens.css", "swiss"),
        (REFS / "google-design-preset/tokens.css", "google-design"),
    ]

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_check_module()

    def test_each_preset_header_is_slug_and_43(self):
        for path, slug in self.PRESETS:
            with self.subTest(preset=slug):
                self.assertTrue(path.exists(), f"missing preset: {path}")
                text = path.read_text(encoding="utf-8")
                self.assertEqual(
                    self.mod._parse_preset_header(text), (slug, 43),
                    f"{slug} tokens.css header must parse to ({slug!r}, 43)")

    def test_each_preset_canonical_completeness_zero_findings(self):
        for path, slug in self.PRESETS:
            with self.subTest(preset=slug):
                text = path.read_text(encoding="utf-8")
                findings = self.mod._check_tokens_canonical_completeness(
                    path, text, 43)
                self.assertEqual(
                    findings, [],
                    f"{slug} tokens.css must define all 43 canonical tokens "
                    f"under schema:43 but got findings: {findings}")


if __name__ == "__main__":
    unittest.main()
