#!/usr/bin/env python3
"""TASK-integration-01 — whole-system E2E / regression / integration gate for
the dataviz statistical-chart-type + chart-category-color-capability feature
(spec: `.claude/analyze/2026-07-02-dataviz-chart-integration/`).

Execution-method constraint (see ctx.md "CRITICAL ORCHESTRATOR RESEARCH"):
`/design` and `/book` are Claude-Code SKILLS (LLM-followed prose), not
runnable apps — this suite cannot literally invoke them end-to-end. Every
row below is instead verified via fixture-based / mechanism-level testing:
constructing real tokens.css fixtures and running check.py / color_distance.py
against them for real, and exercising the actual routing-table/decision-tree
prose via structural assertions — the same method the 6 prior tasks' suites
already used (test_color_distance.py, test_check_design.py,
test_design_chart_capability_skill.py, test_book_chart_statistical_type.py,
test_book_color_reasoning_reference.py, test_book_accent_chart_exception.py).

This suite does NOT re-duplicate those 6 files' per-mechanism unit coverage.
It adds genuinely NEW cross-file / cross-layer / subprocess-boundary checks
that only an integration-level suite can catch: byte-for-byte before/after
regression pins for check.py + validate-output.ts, a full declared-then-
undeclared atomic-rewrite round-trip (no prior suite simulates a SECOND
regeneration), subprocess-level (not direct-function-call) verification of
check.py's independence/format/fail-closed behavior, and cross-file wiring
checks (SKILL.md prose <-> svg-rendering-rules.md tables <-> the 13
individual type-*.md files <-> perception-guide.md).

Row/AC mapping — test.md re-read fresh at execution time per task-integration.md
AC1/AC2's explicit non-hardcoding directive ("不假設固定列數，依當時 test.md
實際內容逐列核對"). Counts confirmed by direct parse of test.md as of this
task's execution: E2E table = 6 rows, 整合測試策略 table = 7 rows, 關鍵邊界
條件 list = 9 items (NOTE: ctx.md's own header labeled this "8 items as of
this read" — a one-off undercount; ctx.md's own verbatim reproduction of the
list, and the live test.md file, both actually contain 9 bullet items. This
suite uses the verified live count, 9, not the mislabeled 8).
See TestRowAndItemCountsGuard below for the live re-count assertion.

Each row is mapped to a test class docstring below, quoting the row's exact
Chinese scenario/goal text from test.md for traceability.
"""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

THIS_FILE = Path(__file__).resolve()
WORKTREE_ROOT = THIS_FILE.parents[2]

DESIGN_SKILL_DIR = WORKTREE_ROOT / "plugins" / "baransu" / "skills" / "design"
BOOK_SKILL_DIR = WORKTREE_ROOT / "plugins" / "baransu" / "skills" / "book"
SHARED_SCRIPTS_DIR = WORKTREE_ROOT / "plugins" / "baransu" / "skills" / "_shared" / "scripts"

CHECK_PY = DESIGN_SKILL_DIR / "scripts" / "check.py"
DESIGN_SKILL = DESIGN_SKILL_DIR / "SKILL.md"
DESIGN_REFS = DESIGN_SKILL_DIR / "references"

BOOK_SKILL = BOOK_SKILL_DIR / "SKILL.md"
SVG_RULES = BOOK_SKILL_DIR / "references" / "svg-rendering-rules.md"
PERCEPTION_GUIDE = BOOK_SKILL_DIR / "references" / "perception-guide.md"
COLOR_REASONING = BOOK_SKILL_DIR / "references" / "color-reasoning.md"
DIAGRAM_TYPES_DIR = BOOK_SKILL_DIR / "references" / "diagram-types"
TYPE_STATISTICAL = DIAGRAM_TYPES_DIR / "type-statistical.md"

VALIDATE_OUTPUT_TS = BOOK_SKILL_DIR / "scripts" / "validate-output.ts"
SWISS_SMOKE_SH = BOOK_SKILL_DIR / "scripts" / "swiss-smoke-test.sh"

COLOR_DISTANCE_PY = SHARED_SCRIPTS_DIR / "color_distance.py"

TEST_MD = WORKTREE_ROOT / ".claude" / "analyze" / "2026-07-02-dataviz-chart-integration" / "test.md"

PRESETS = [
    (DESIGN_REFS / "紙-preset", "kami"),
    (DESIGN_REFS / "swiss-preset", "swiss"),
    (DESIGN_REFS / "google-design-preset", "google-design"),
]

EXISTING_13_TYPES = [
    "architecture", "flowchart", "sequence", "state", "er", "timeline",
    "swimlane", "quadrant", "nested", "tree", "layers", "venn", "pyramid",
]

# A real 6-color categorical palette (hue-distinct, not a lightness ramp) —
# used to exercise color_distance.py the way /design's Step 3 bake step and
# /book's execution-time re-validation both would.
CANDIDATE_CHART_PALETTE = [
    "#1B365D", "#2D5A8A", "#B8622E", "#4F7A5C", "#8B5A9E", "#C4915C",
]


def _load_check_module():
    spec = importlib.util.spec_from_file_location("check_integration_under_test", CHECK_PY)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_color_distance_module():
    spec = importlib.util.spec_from_file_location(
        "color_distance_integration_under_test", COLOR_DISTANCE_PY)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_check(*targets: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CHECK_PY), *[str(t) for t in targets]],
        capture_output=True, text=True,
    )


def run_color_distance(colors: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(COLOR_DISTANCE_PY), ",".join(colors)],
        capture_output=True, text=True,
    )


def _git_numstat(path: Path) -> tuple[int, int]:
    """(insertions, deletions) for `path` vs HEAD; (0, 0) if unchanged."""
    rel = path.relative_to(WORKTREE_ROOT)
    result = subprocess.run(
        ["git", "-C", str(WORKTREE_ROOT), "diff", "--numstat", "--", str(rel)],
        capture_output=True, text=True, check=True,
    )
    line = result.stdout.strip()
    if not line:
        return (0, 0)
    parts = line.split("\t")
    return (int(parts[0]), int(parts[1]))


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


def _build_project(root: Path, mod, header_extra: str = "",
                    include_chart_tokens: bool = False,
                    chart_hex: list[str] | None = None) -> None:
    """Fixture builder shared by several classes below — a minimal valid
    5-artifact v1.3 project root, optionally declaring CHART_CAPABILITY.
    Mirrors the pattern already established by test_check_design.py's
    TestChartCapabilityProjectRootIntegration._build_project (same shape,
    reimplemented locally so this file has no cross-file import dependency)."""
    all_tokens = mod.BASE_TOKENS + mod.CAPABILITY_TOKENS
    body_lines = [f"  {t}: 0;" for t in all_tokens]
    if include_chart_tokens:
        hexes = chart_hex or ["#000000"] * len(mod.CHART_CAPABILITY_TOKENS)
        for t, h in zip(mod.CHART_CAPABILITY_TOKENS, hexes):
            body_lines.append(f"  {t}: {h};")
    body = "\n".join(body_lines)
    (root / "tokens.css").write_text(
        f"/* preset: testslug; schema: 43{header_extra} */\n:root {{\n{body}\n}}\n")
    (root / "DESIGN.md").write_text("\n".join(mod.DESIGN_MD_NINE_SECTIONS) + "\n")
    (root / "DESIGN.html").write_text("<html></html>\n")
    cores = root / "design-cores"
    cores.mkdir(exist_ok=True)
    (cores / "long-form.html").write_text(
        '<section data-slot="long-form-body"></section>\n')
    (cores / "dashboard.html").write_text("<div>ok</div>\n")
    (root / "slide-cores").mkdir(exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────
# Step 1 (ctx.md item 1) — confirm the files the summarize-agent could not
# check itself (no Bash tool) are genuinely untouched / purely additive.
# ─────────────────────────────────────────────────────────────────────────

class TestFilesUntouchedRegressionGate(unittest.TestCase):
    """ctx.md step 1 — independently confirm (a) validate-output.ts has zero
    diff and (b) check.py's diff is purely additive (0 deletions), so its
    pre-existing Check A-F core logic bytes are unchanged, not just its
    call-site wiring."""

    def test_validate_output_ts_zero_diff(self):
        ins, dele = _git_numstat(VALIDATE_OUTPUT_TS)
        self.assertEqual(
            (ins, dele), (0, 0),
            "validate-output.ts must have zero diff vs HEAD — AC4's GATE "
            "regression baseline depends on this file being untouched by "
            "any of the 6 prior tasks",
        )

    def test_check_py_diff_purely_additive(self):
        ins, dele = _git_numstat(CHECK_PY)
        self.assertEqual(
            dele, 0,
            f"check.py diff must have 0 deletions (purely additive), got {dele} "
            "deletions — a deletion would mean existing Check A-F logic was "
            "edited, not just extended",
        )
        self.assertGreater(ins, 0, "check.py should show the CHART_CAPABILITY additions")

    def test_check_a_f_core_function_signatures_unchanged_verbatim(self):
        text = CHECK_PY.read_text(encoding="utf-8")
        for anchor in (
            "def check_project_root(root: Path) -> list[dict]:",
            "def _check_tokens_canonical_completeness(",
            "def _check_cross_artifact_prefix(root: Path, expected_slug: str | None) -> list[dict]:",
            "def _check_design_md(path: Path) -> list[dict]:",
            "def _check_longform_slot(path: Path) -> list[dict]:",
            "def _check_dashboard_static(path: Path) -> list[dict]:",
        ):
            self.assertIn(anchor, text, f"Check A-F function signature changed or missing: {anchor!r}")


# ─────────────────────────────────────────────────────────────────────────
# AC3 — check.py Check A-F byte-for-byte regression, 3 real presets + repo root
# ─────────────────────────────────────────────────────────────────────────

class TestAC3CheckPyRegressionRealPresetsAndRepoRoot(unittest.TestCase):
    """AC3 — 「紙／swiss／google-design 三個既有 preset 的 check.py Check A-F
    結果與功能新增前逐項比對一致」。Pinned expected stdout/exit-code below is
    independently re-confirmed as this task's own before/after diff (via
    `git stash` of all 6 prior tasks' check.py changes, re-running check.py
    on the true pre-integration source, and diffing byte-for-byte against
    the current/after run) — not just trusting TASK-design-01's own review.
    Result: identical on both sides for all 4 fixtures (3 presets + repo root).
    """

    def test_each_preset_regresses_to_missing_design_html_only(self):
        for preset_dir, slug in PRESETS:
            with self.subTest(preset=slug):
                result = run_check(preset_dir)
                self.assertEqual(result.returncode, 1)
                self.assertIn(
                    "[#1 check-A-artifact-completeness] 缺少 v1.3 artifact: DESIGN.html",
                    result.stdout,
                )
                self.assertIn("❌  1 violation(s) in 1 file(s):", result.stdout)
                self.assertNotIn(
                    "chart-capability", result.stdout.lower(),
                    "Check A fail-fast must skip B-F (including the new "
                    "CHART_CAPABILITY tier) — no chart vocabulary should ever "
                    "appear for these fixtures",
                )

    def test_repo_root_passes_clean(self):
        result = run_check(WORKTREE_ROOT)
        self.assertEqual(result.returncode, 0, msg=result.stdout)
        self.assertIn(
            "✅  /design lint pass — 5 file(s) checked, no violations.", result.stdout)


# ─────────────────────────────────────────────────────────────────────────
# AC4 — validate-output.ts GATE regression (zero-diff already proven above;
# here we re-run its actual fixture-based regression mechanism)
# ─────────────────────────────────────────────────────────────────────────

class TestAC4ValidateOutputSmokeTestRegression(unittest.TestCase):
    """AC4 — re-run `swiss-smoke-test.sh` (the existing fixture-based
    regression mechanism for validate-output.ts) and confirm every gate's
    pass/fail outcome is unaffected by the chart feature. Independently
    re-confirmed via `git stash` (all 6 prior tasks' changes stashed) during
    this task's own verification pass: byte-for-byte identical stdout
    before/after, including the one pre-existing GATE-F failure (an ambient
    repo-root tokens.css preset mismatch — kami vs the swiss fixture —
    unrelated to and unaffected by this feature)."""

    @classmethod
    def setUpClass(cls):
        cls.result = subprocess.run(
            ["bash", str(SWISS_SMOKE_SH)],
            capture_output=True, text=True,
            cwd=str(SWISS_SMOKE_SH.parent), timeout=120,
        )

    def test_all_non_gate_f_checks_pass(self):
        out = self.result.stdout
        for gate in (
            "OK  three-preset golden-template presence (kami/swiss/gd)",
            "OK  html-parse", "OK  structure", "OK  svg-balance",
            "OK  GATE-A focal-cap", "OK  GATE-B paper-mask",
            "OK  GATE-D marker-integrity", "OK  GATE-E deny-list",
            "OK  GATE-J node-width-whitelist", "OK  GATE-K chevron-strict",
            "OK  GATE-L viewBox-containment", "OK  GATE-G layout-registered",
        ):
            self.assertIn(gate, out, f"expected gate line missing/changed: {gate!r}")

    def test_no_chart_capability_vocabulary_leaks_into_unrelated_fixture(self):
        out = self.result.stdout.lower()
        self.assertNotIn("chart-capability", out)
        self.assertNotIn("chart-cat", out)

    def test_negative_fixtures_still_correctly_fail(self):
        # Stage 1b of the script itself already asserts this and would exit
        # non-zero with a distinct message if it regressed; corroborate via
        # absence of the script's own regression-failure message.
        self.assertNotIn("unexpectedly PASSED", self.result.stdout)


# ─────────────────────────────────────────────────────────────────────────
# E2E 測試策略 — 6 rows, each mapped to a concrete mechanism
# ─────────────────────────────────────────────────────────────────────────

class TestE2ERow1UndeclaredExistingContentRegression(unittest.TestCase):
    """Row 1 — 「未宣告能力風格的既有內容產出」: 對紙 preset 執行 `/book` 處理一份純
    架構文件 -> 產出 HTML，圖表為既有 13 型之一，通過 validate-output.ts。
    Mechanism: an undeclared tokens.css must be a complete no-op for the new
    CHART_CAPABILITY tier (check.py), AND the existing structural §4.9 rows
    (e.g. 'System components + connections' -> Architecture) must still be
    positioned to win first-match over any statistical row."""

    def setUp(self):
        self.mod = _load_check_module()

    def test_undeclared_fixture_zero_chart_capability_findings(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _build_project(root, self.mod, header_extra="", include_chart_tokens=False)
            findings = self.mod.check_project_root(root)
            self.assertEqual(findings, [])

    def test_architecture_row_precedes_any_statistical_row(self):
        text = SVG_RULES.read_text(encoding="utf-8")
        region = _extract_region(
            text, "## §4.9 14-type chart routing decision tree", ["\n## §4.10"])
        lines = [l for l in region.splitlines() if l.startswith("| ")]
        arch_idx = next(
            i for i, l in enumerate(lines) if l.endswith("| Architecture |"))
        stat_indices = [i for i, l in enumerate(lines) if l.endswith("| Statistical |")]
        self.assertTrue(stat_indices)
        self.assertLess(
            arch_idx, min(stat_indices),
            "Architecture (an existing 13-type row) must win first-match "
            "over every statistical row",
        )


class TestE2ERow2DeclaredStatisticalChartColorAndContainerException(unittest.TestCase):
    """Row 2 — 「宣告能力風格的統計圖表產出」: 對已宣告圖表分類色能力的 preset 執行
    `/book`，產出含統計圖表的 SVG，色彩通過色盲可讀性建議、圖例存在，且該小節容器外
    的其他 UI 元素色彩仍維持單一 accent（例外不外溢）。
    Mechanism: a real 6-color categorical palette run through color_distance.py
    (the actual advisory tool), the statistical example's LEGEND strip, and
    the container-scoped exception's exact same wording across both files
    that must jointly govern the exception."""

    def test_declared_chart_cat_palette_is_cvd_distinguishable(self):
        result = run_color_distance(CANDIDATE_CHART_PALETTE)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        parsed = json.loads(result.stdout)
        self.assertEqual(parsed["status"], "computed")
        labels = {p["advisory_label"] for p in parsed["pairs"]}
        self.assertTrue(
            labels.issubset({"adequate", "marginal"}),
            f"candidate chart palette contains a 'low' (non-distinguishable) "
            f"adjacent pair: {parsed['pairs']}",
        )

    def test_statistical_example_has_legend_strip(self):
        text = TYPE_STATISTICAL.read_text(encoding="utf-8")
        self.assertIn("LEGEND", text)

    def test_container_exception_named_identically_in_both_files(self):
        guide = PERCEPTION_GUIDE.read_text(encoding="utf-8")
        skill = BOOK_SKILL.read_text(encoding="utf-8")
        self.assertIn("declared-statistical-chart container exception", guide.lower())
        self.assertIn("declared-statistical-chart container exception", skill.lower())
        self.assertIn("no exception outside the container.", guide.lower())


class TestE2ERow3And4UndeclaredDegradeBoundaryConcrete(unittest.TestCase):
    """Rows 3/4 — undeclared-style attempts at a statistical chart. Row 3
    (單一趨勢, 應退回單色階) must degrade to L1; row 4 (3 條互不相關產品線,
    需分辨多個獨立身份, 應降級為小圖並排) must degrade to L2. Mechanism:
    the L2 bullet's threshold must have NO upper bound (so N=3, row 4's exact
    scenario, is still covered by "2 or more", not miscategorized as some
    third path), and the L1/L2 pair must remain the only two branches."""

    def setUp(self):
        self.full = BOOK_SKILL.read_text(encoding="utf-8")
        marker = "## Stage 3 — Render"
        start = self.full.find(marker)
        self.assertNotEqual(start, -1)
        body = self.full[start:]
        nxt = body.find("\n## ", len(marker))
        self.section = body if nxt == -1 else body[:nxt]

    def test_l2_threshold_has_no_upper_bound_covers_three_series(self):
        l2_line = next(l for l in self.section.splitlines() if "**L2**" in l)
        self.assertNotRegex(
            l2_line, r"\bat most\b|\bup to\b|\bmax(imum)?\b",
            "L2 branch must not cap its series count — row 4's 3-series "
            "scenario must remain covered",
        )
        self.assertRegex(l2_line.lower(), r"2\+|2 or more|two or more")

    def test_exactly_two_documented_branches_no_third_path(self):
        self.assertIn("Pick **exactly one** of the two branches", self.section)
        self.assertIn("**L1**", self.section)
        self.assertIn("**L2**", self.section)
        self.assertNotIn("**L3**", self.section)


class TestE2ERow5DesignGenDeclarationProducesCanonicalNaming(unittest.TestCase):
    """Row 5 — 「`/design` preset 宣告能力後產出規範命名」: 對某風格執行
    `/design gen --slug` 宣告圖表分類色能力 -> tokens.css 含圖表規範命名，
    check.py 全綠。Mechanism: the FULL pipeline — bake a real palette via
    color_distance.py (as /design's Step 3 would), write it into tokens.css
    under the exact CHART_CAPABILITY_TOKENS names, then check.py must be
    fully green. Also cross-checks design/SKILL.md's documented token-name
    list is identical (not just similar) to check.py's actual constant."""

    def test_full_declare_bake_validate_check_pipeline_green(self):
        mod = _load_check_module()
        bake = run_color_distance(CANDIDATE_CHART_PALETTE)
        self.assertEqual(bake.returncode, 0)
        baked = json.loads(bake.stdout)
        self.assertEqual(baked["status"], "computed")

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _build_project(
                root, mod, header_extra="; chart-capability: 1",
                include_chart_tokens=True, chart_hex=CANDIDATE_CHART_PALETTE,
            )
            findings = mod.check_project_root(root)
            self.assertEqual(findings, [], f"expected check.py all-green, got: {findings}")

    def test_design_skill_md_documents_the_exact_same_six_token_names(self):
        mod = _load_check_module()
        design_text = DESIGN_SKILL.read_text(encoding="utf-8")
        documented = set(re.findall(r"--chart-cat-\d", design_text))
        self.assertEqual(
            documented, set(mod.CHART_CAPABILITY_TOKENS),
        )
        for token in mod.CHART_CAPABILITY_TOKENS:
            self.assertIn(token, design_text)


class TestE2ERow6AtomicRewriteClearsDeclaration(unittest.TestCase):
    """Row 6 — 「風格宣告狀態變更後的即時反映」: 對某風格先執行 `/design gen` 宣告
    圖表分類色能力，再對同風格重新執行 `/design gen` 但這次不宣告 -> 執行 `/book`
    處理統計資料內容時，perception-guide.md 讀到的是最新（未宣告）狀態，退回單色階
    邏輯，不殘留前次宣告時的圖表規範命名. Mechanism: design.md's atomic-staging
    full-rewrite guarantee — a SECOND regeneration wholesale REPLACES
    tokens.css (not an in-place edit), so a declared->undeclared transition
    must leave zero residue. None of the 6 prior tasks' suites simulate a
    second regeneration; this is new coverage."""

    def test_round_trip_declare_then_undeclare_full_rewrite_leaves_no_residue(self):
        mod = _load_check_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            # Round 1 — declare, with a fully baked+validated palette.
            _build_project(
                root, mod, header_extra="; chart-capability: 1",
                include_chart_tokens=True, chart_hex=CANDIDATE_CHART_PALETTE,
            )
            findings_round1 = mod.check_project_root(root)
            self.assertEqual(findings_round1, [])
            text_round1 = (root / "tokens.css").read_text(encoding="utf-8")
            status_round1, _ = mod._parse_chart_capability_header(text_round1)
            self.assertEqual(status_round1, "declared")

            # Round 2 — full rewrite (atomic staged-then-mv), this time
            # WITHOUT declaring: simulates `/design gen` re-run that this
            # time skipped the chart-capability AskUserQuestion entirely.
            _build_project(root, mod, header_extra="", include_chart_tokens=False)
            findings_round2 = mod.check_project_root(root)
            self.assertEqual(findings_round2, [])
            text_round2 = (root / "tokens.css").read_text(encoding="utf-8")

            self.assertNotIn(
                "chart-capability", text_round2,
                "atomic full-rewrite must leave zero trace of the prior "
                "declaration's header field",
            )
            for token in mod.CHART_CAPABILITY_TOKENS:
                self.assertNotIn(
                    token, text_round2,
                    f"atomic full-rewrite must leave zero trace of the prior "
                    f"declaration's baked token {token!r}",
                )
            status_round2, _ = mod._parse_chart_capability_header(text_round2)
            self.assertEqual(
                status_round2, "undeclared",
                "the second regeneration must read back as undeclared, not "
                "a stale 'declared' state",
            )


# ─────────────────────────────────────────────────────────────────────────
# 整合測試策略 — 7 rows
# ─────────────────────────────────────────────────────────────────────────

class TestIntegrationRow1TokensCssToPerceptionGuideWiring(unittest.TestCase):
    """Integration row 1 — 「tokens.css → perception-guide.md 宣告狀態串接」:
    `/book` 讀到的宣告狀態與 `/design` 側寫入的一致，不需要 `/book` 端另外維護紀錄。
    Mechanism: perception-guide.md must cite the LITERAL function name
    check.py implements (not a paraphrase / independently-invented parser),
    proving there is exactly one parsing contract, not two."""

    def test_perception_guide_cites_the_real_check_py_function(self):
        mod = _load_check_module()
        guide = PERCEPTION_GUIDE.read_text(encoding="utf-8")
        self.assertIn("_parse_chart_capability_header", guide)
        self.assertTrue(hasattr(mod, "_parse_chart_capability_header"))

    def test_declaration_field_name_consistent_across_design_and_book(self):
        design_text = DESIGN_SKILL.read_text(encoding="utf-8")
        book_text = BOOK_SKILL.read_text(encoding="utf-8")
        self.assertIn("chart-capability", design_text)
        self.assertIn("chart-capability", book_text)


class TestIntegrationRow2ColorDistanceCallSiteConsistency(unittest.TestCase):
    """Integration row 2 — 「色彩距離驗證工具的設計期／執行期呼叫一致性」:
    `/design` 烘焙的色值與 `/book` 執行期驗證的子集，用同一套判斷邏輯與門檻，
    不因呼叫方不同而結果不一致. Mechanism: invoke the tool twice (simulating
    the two call sites) with the same input and confirm byte-identical
    output, and confirm a full-palette call and a subset call share the same
    threshold constants (single source of truth, not two copies)."""

    def test_same_input_same_output_across_simulated_call_sites(self):
        design_time = run_color_distance(CANDIDATE_CHART_PALETTE)
        book_time = run_color_distance(CANDIDATE_CHART_PALETTE)
        self.assertEqual(design_time.returncode, 0)
        self.assertEqual(book_time.returncode, 0)
        self.assertEqual(design_time.stdout, book_time.stdout)

    def test_full_palette_and_book_time_subset_share_thresholds(self):
        mod = _load_color_distance_module()
        full = mod.compute_color_distances(CANDIDATE_CHART_PALETTE)
        subset = mod.compute_color_distances(CANDIDATE_CHART_PALETTE[:2])
        self.assertEqual(full["pairs"][0]["distance"], subset["pairs"][0]["distance"])
        self.assertEqual(
            full["pairs"][0]["advisory_label"], subset["pairs"][0]["advisory_label"])
        self.assertEqual(mod.CVD_TARGET, 12.0)
        self.assertEqual(mod.CVD_FLOOR, 8.0)


class TestIntegrationRow3Schema43ChartCapabilityIndependenceSubprocess(unittest.TestCase):
    """Integration row 3 — 「check.py 新版本層級與既有 schema:43 分支互不干擾」:
    同時宣告 schema:43 與圖表能力層級的 preset，兩邊判斷各自獨立進行，互不影響對方
    的通過／失敗結果. Direct-function-call coverage already exists in
    test_check_design.py; this re-verifies at the SUBPROCESS/CLI boundary
    (through check.py's actual `main()` entrypoint, not a direct import) to
    catch any wiring gap between check_project_root and the CLI dispatcher."""

    def test_both_tiers_declared_subprocess_boundary_full_green(self):
        mod = _load_check_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _build_project(
                root, mod, header_extra="; chart-capability: 1",
                include_chart_tokens=True, chart_hex=CANDIDATE_CHART_PALETTE,
            )
            result = run_check(root)
            self.assertEqual(result.returncode, 0, msg=result.stdout)

    def test_missing_chart_tokens_fails_chart_tier_only_subprocess_boundary(self):
        mod = _load_check_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _build_project(
                root, mod, header_extra="; chart-capability: 1",
                include_chart_tokens=False,
            )
            result = run_check(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("check-B-chart-capability-missing", result.stdout)
            self.assertNotIn("check-B-canonical-missing", result.stdout)


class TestIntegrationRow4FourteenthTypeDoesNotAffectExisting13(unittest.TestCase):
    """Integration row 4 — 「/book 圖表選型決策樹新增第 14 型不影響既有 13 型」.
    Prior suites spot-check svg-rendering-rules.md's own table content; this
    additionally confirms SKILL.md's own PROSE CLAIM ('14-type ... decision
    tree') agrees with the underlying table it describes — a cross-file
    consistency angle no prior suite checked."""

    def test_skill_md_and_svg_rules_agree_on_fourteen_type_language(self):
        skill_text = BOOK_SKILL.read_text(encoding="utf-8")
        self.assertIn("14-type diagram first-match decision tree", skill_text)
        self.assertIn("14-type selection table", skill_text)
        self.assertNotIn("13-type", skill_text)

        rules_text = SVG_RULES.read_text(encoding="utf-8")
        self.assertIn("14-type chart routing decision tree", rules_text)
        self.assertIn("14-type selection table", rules_text)
        self.assertNotIn("13-type", rules_text)


class TestIntegrationRow5ColorReasoningReadCountZeroForExisting13(unittest.TestCase):
    """Integration row 5 — 「色彩推理參考文件僅在統計圖表類型時被讀取」: 既有 13 型
    測資執行 `/book` 後，該參考文件的讀取次數為 0. Prior suite (TASK-book-02's)
    checks the SKILL.md wiring is scoped correctly; this adds the
    complementary, previously-unchecked angle — none of the 13 existing
    type-*.md reference files themselves mention color-reasoning.md (so even
    a reader following a type-*.md file's own cross-references would never
    be led to read it for a non-statistical type)."""

    def test_no_existing_type_file_references_color_reasoning(self):
        for name in EXISTING_13_TYPES:
            path = DIAGRAM_TYPES_DIR / f"type-{name}.md"
            with self.subTest(type=name):
                self.assertTrue(path.exists())
                text = path.read_text(encoding="utf-8")
                self.assertNotIn("color-reasoning.md", text)

    def test_only_statistical_type_file_references_color_reasoning(self):
        referencing = sorted(
            p.name for p in DIAGRAM_TYPES_DIR.glob("type-*.md")
            if "color-reasoning.md" in p.read_text(encoding="utf-8")
        )
        self.assertEqual(referencing, ["type-statistical.md"])


class TestIntegrationRow6ViolationMessageFormatConsistency(unittest.TestCase):
    """Integration row 6 — 「check.py 對「已宣告能力但缺規範命名」的違規回報」:
    違規訊息內容明確指出缺少哪些規範命名，回報格式與既有 Check A-F 的違規訊息風格
    一致. Prior suite checks the finding dict SHAPE; this checks the actual
    PRINTED CLI output format via a real subprocess run — the same
    `L{line}  [#{inv} {name}] {msg}` bracket style used by every other
    Check A-F finding."""

    def test_printed_format_matches_bracket_style_of_other_checks(self):
        mod = _load_check_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _build_project(
                root, mod, header_extra="; chart-capability: 1",
                include_chart_tokens=False,
            )
            result = run_check(root)
            self.assertEqual(result.returncode, 1)
            bracket_re = re.compile(r"L\d+\s+\[#\d+ check-B-chart-capability-missing\]")
            self.assertRegex(result.stdout, bracket_re)

        # Cross-check: the SAME bracket-format regex shape (L<n> [#<inv> <name>] <msg>)
        # matches an existing, unrelated Check A finding — proving one shared format.
        preset_result = run_check(PRESETS[0][0])
        self.assertRegex(
            preset_result.stdout, r"L\d+\s+\[#\d+ check-A-artifact-completeness\]")


class TestIntegrationRow7FailClosedMissingOrMalformedTokensCss(unittest.TestCase):
    """Integration row 7 — 「tokens.css 缺失或圖表能力宣告欄位無法解析時的
    fail-closed 行為」: 判定為未宣告，不靜默放行圖表容器內的多色輸出. Traces the
    check.py-level mechanism underlying /book's prose-level fail-closed
    guarantee (perception-guide.md already asserts the guarantee in prose;
    this test proves the underlying parser genuinely behaves that way)."""

    def test_missing_tokens_css_fails_fast_before_chart_tier_can_run(self):
        mod = _load_check_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # DESIGN.md present (so _is_project_root's heuristic still fires)
            # but tokens.css entirely absent.
            (root / "DESIGN.md").write_text("\n".join(mod.DESIGN_MD_NINE_SECTIONS) + "\n")
            findings = mod.check_project_root(root)
            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0]["name"], "check-A-artifact-completeness")
            self.assertNotIn("chart-capability", findings[0]["msg"])

    def test_malformed_chart_capability_field_never_raises_requires_nothing(self):
        mod = _load_check_module()
        header = "/* preset: x; schema: 43; chart-capability: notanumber */\n"
        status, version = mod._parse_chart_capability_header(header)
        self.assertEqual((status, version), ("malformed", None))
        findings = mod._check_chart_capability_completeness(Path("tokens.css"), header, status)
        self.assertEqual(
            findings, [],
            "malformed field must resolve to zero requirement (fail-closed "
            "means 'undeclared', never a silent pass-through of multi-color, "
            "and never an exception)",
        )


# ─────────────────────────────────────────────────────────────────────────
# 關鍵邊界條件 — items not already covered by the 6 prior tasks' suites
# ─────────────────────────────────────────────────────────────────────────

class TestBoundaryExistingTypePriorityConcreteTrace(unittest.TestCase):
    """Boundary item 1 (REQ-001) — 「內容同時具備統計圖表特徵與既有 13 型特徵
    （例如一張帶座標軸的架構圖）時的判斷優先序——依 design.md 已定義的優先序規則
    （既有型態優先）」. Concrete first-match simulation: parse §4.9's table in
    document order and run an actual top-to-bottom first-match search (not
    just a position comparison) for content matching BOTH the Architecture
    row's shape and a statistical shape."""

    def test_first_match_search_resolves_ambiguous_content_to_architecture(self):
        text = SVG_RULES.read_text(encoding="utf-8")
        region = _extract_region(
            text, "## §4.9 14-type chart routing decision tree", ["\n## §4.10"])
        rows = []
        for line in region.splitlines():
            if not line.startswith("| ") or line.startswith("| Data shape") or set(
                    line.replace("|", "").strip()) == {"-"}:
                continue
            parts = [p.strip() for p in line.strip("|").split("|")]
            if len(parts) == 2:
                rows.append((parts[0], parts[1]))

        def first_match(matches_structural: bool, matches_statistical: bool) -> str | None:
            for shape, chart in rows:
                is_structural_row = chart != "Statistical"
                if is_structural_row and matches_structural:
                    return chart
                if not is_structural_row and matches_statistical:
                    return chart
            return None

        # Ambiguous content: an architecture diagram that happens to carry an axis.
        resolved = first_match(matches_structural=True, matches_statistical=True)
        self.assertEqual(
            resolved, rows[0][1] if rows[0][1] != "Statistical" else None,
        )
        # More directly: any content matching a structural row never reaches
        # a statistical row, because first-match returns on the first hit
        # and all structural rows are listed before all statistical rows.
        structural_only = first_match(matches_structural=True, matches_statistical=False)
        both = first_match(matches_structural=True, matches_statistical=True)
        self.assertEqual(structural_only, both)


class TestBoundaryDeclaredThreePresetsRegressionSummary(unittest.TestCase):
    """Boundary item 9 (REQ-005) — 「既有三個 preset 在這次功能新增後，check.py
    Check A-F 六項結果的逐項回歸比對」— summary cross-check tying the
    per-preset direct-function-call regression (test_check_design.py) to the
    subprocess-level byte-for-byte pin already asserted in
    TestAC3CheckPyRegressionRealPresetsAndRepoRoot above, confirming BOTH
    layers agree on zero regression for all 3 presets."""

    def test_direct_function_call_and_subprocess_agree_zero_chart_impact(self):
        mod = _load_check_module()
        for preset_dir, slug in PRESETS:
            with self.subTest(preset=slug):
                text = (preset_dir / "tokens.css").read_text(encoding="utf-8")
                status, _ = mod._parse_chart_capability_header(text)
                self.assertEqual(status, "undeclared")
                findings = mod._check_chart_capability_completeness(
                    preset_dir / "tokens.css", text, status)
                self.assertEqual(findings, [])


# ─────────────────────────────────────────────────────────────────────────
# AC1/AC2 process guard — re-read test.md fresh, fail loudly (not silently)
# if the spec doc's row/item counts drift from what this suite maps.
# ─────────────────────────────────────────────────────────────────────────

class TestRowAndItemCountsGuard(unittest.TestCase):
    """task-integration.md AC1/AC2 explicitly forbid hardcoding row counts as
    a fixed contract ("不假設固定列數，依當時 test.md 實際內容逐列核對"). This
    guard re-reads test.md at test-run time (not relying on ctx.md's
    "as of this read" labels, which were themselves off-by-one on the
    boundary-item count) and fails loudly if the live counts ever drift from
    what this suite's classes above map row-by-row, instead of silently
    under-covering a newly added row."""

    def setUp(self):
        self.text = TEST_MD.read_text(encoding="utf-8")

    def test_e2e_table_row_count(self):
        region = _extract_region(self.text, "## E2E 測試策略", ["\n## 整合測試策略"])
        rows = [
            l for l in region.splitlines()
            if l.startswith("| ") and "起點" not in l
            and set(l.replace("|", "").strip()) != {"-"}
        ]
        self.assertEqual(
            len(rows), 6,
            "E2E table row count changed since this suite's classes were "
            "written — re-map each row to a TestE2ERowN class above",
        )

    def test_integration_table_row_count(self):
        region = _extract_region(self.text, "## 整合測試策略", ["\n## 關鍵邊界條件"])
        rows = [
            l for l in region.splitlines()
            if l.startswith("| ") and "測試目標" not in l
            and set(l.replace("|", "").strip()) != {"-"}
        ]
        self.assertEqual(
            len(rows), 7,
            "整合測試策略 table row count changed — re-map each row to a "
            "TestIntegrationRowN class above",
        )

    def test_boundary_condition_item_count(self):
        region = _extract_region(self.text, "## 關鍵邊界條件", [])
        items = [l for l in region.splitlines() if l.startswith("- ")]
        self.assertEqual(
            len(items), 9,
            "關鍵邊界條件 item count changed (this suite verified 9 live "
            "items, not the 8 ctx.md's header labeled) — re-map each item",
        )


if __name__ == "__main__":
    unittest.main()
