#!/usr/bin/env python3
"""Pytest suite pinning current behavior of the health skill checker scripts
(plan item health-4).

Each assertion maps 1:1 to a finding type documented in the health SKILL.md
Step 3 report section (including the rubrics it loads from
references/conditional-audits.md):

- check_doc_refs.py       -> "Broken doc references": referenced-but-missing
                             pointer reported with source file and line,
                             fenced code examples skipped, non-zero exit.
- check_maintainability.py -> "Missing stable verifier wrapper": Structural
                             WARN when a Makefile lacks check/test/verify;
                             "Broken Markdown references": deep audit only.
- check_agent_context.py  -> "Instruction drift across runtimes": AGENTS.md
                             and CLAUDE.md both substantial without
                             delegation.
- check_verifier_output.py -> "Stale verifier cache output": known
                             cache-clean action for recognized tools,
                             diagnostic rerun action for unknown tools.

The static fixture project lives in tests/fixtures/health-project/. The
tests pin what the checkers do today; they do not invent new behavior.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
import uuid
from pathlib import Path

THIS_FILE = Path(__file__).resolve()
REPO_ROOT = THIS_FILE.parents[2]
SCRIPTS_DIR = REPO_ROOT / "plugins" / "baransu" / "skills" / "health" / "scripts"
FIXTURE_PROJECT = REPO_ROOT / "tests" / "fixtures" / "health-project"


def run_checker(script: str, *args: object, home: Path) -> subprocess.CompletedProcess:
    """Run a health checker with an isolated HOME so global config never leaks in."""
    env = {**os.environ, "HOME": str(home)}
    env.pop("DOC_REF_CHECKER", None)
    return subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / script), *[str(a) for a in args]],
        capture_output=True,
        text=True,
        env=env,
    )


class HealthCheckerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._home = tempfile.TemporaryDirectory()
        self.home = Path(self._home.name)
        self.addCleanup(self._home.cleanup)


class TestCheckDocRefs(HealthCheckerTestCase):
    def test_missing_at_reference_detected_with_source_location(self) -> None:
        proc = run_checker("check_doc_refs.py", FIXTURE_PROJECT, home=self.home)
        self.assertEqual(1, proc.returncode, proc.stdout + proc.stderr)
        self.assertIn("MISSING: CLAUDE.md:", proc.stdout)
        self.assertIn("-> @ROADMAP.md", proc.stdout)

    def test_fenced_code_example_is_skipped(self) -> None:
        proc = run_checker("check_doc_refs.py", FIXTURE_PROJECT, home=self.home)
        self.assertNotIn("absent-in-fence", proc.stdout)
        missing_lines = [
            line for line in proc.stdout.splitlines() if line.startswith("MISSING:")
        ]
        # The resolvable docs/guide.md reference and the fenced example must
        # not be reported; only the @ROADMAP.md pointer is missing.
        self.assertEqual(1, len(missing_lines), proc.stdout)

    def test_clean_project_exits_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs").mkdir()
            (root / "docs" / "guide.md").write_text("# guide\n", encoding="utf-8")
            (root / "CLAUDE.md").write_text(
                "# Fixture\n\nSee docs/guide.md for details.\n", encoding="utf-8"
            )
            proc = run_checker("check_doc_refs.py", root, home=self.home)
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertIn("doc references: ok", proc.stdout)


class TestCheckMaintainability(HealthCheckerTestCase):
    def test_summary_missing_stable_wrapper_is_warn(self) -> None:
        proc = run_checker(
            "check_maintainability.py", FIXTURE_PROJECT, "summary", home=self.home
        )
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertIn("mode: summary", proc.stdout)
        self.assertIn("maintainability_status: WARN", proc.stdout)
        self.assertIn("wrapper_status: WARN", proc.stdout)
        self.assertIn(
            "multiple verification commands discovered but Makefile lacks"
            " check/test/verify wrapper",
            proc.stdout,
        )

    def test_summary_skips_markdown_link_scan(self) -> None:
        proc = run_checker(
            "check_maintainability.py", FIXTURE_PROJECT, "summary", home=self.home
        )
        self.assertIn("markdown_link_status: SKIPPED", proc.stdout)
        # Without DOC_REF_CHECKER the doc-ref delegation stays unavailable.
        self.assertIn("broken_doc_references: unavailable", proc.stdout)

    def test_deep_detects_broken_local_markdown_link(self) -> None:
        proc = run_checker(
            "check_maintainability.py", FIXTURE_PROJECT, "deep", home=self.home
        )
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertIn("mode: deep", proc.stdout)
        self.assertIn("markdown_link_status: WARN", proc.stdout)
        self.assertIn("-> ./nowhere.md", proc.stdout)
        self.assertIn("broken Markdown links", proc.stdout)

    def test_wrapper_script_delegates_doc_ref_checker_and_fails_overall(self) -> None:
        env = {**os.environ, "HOME": str(self.home)}
        env.pop("DOC_REF_CHECKER", None)
        proc = subprocess.run(
            [
                "bash",
                str(SCRIPTS_DIR / "check-maintainability.sh"),
                str(FIXTURE_PROJECT),
                "summary",
            ],
            capture_output=True,
            text=True,
            env=env,
        )
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertIn("broken_doc_references: fail", proc.stdout)
        self.assertIn("broken documentation references", proc.stdout)
        self.assertIn("maintainability_status: FAIL", proc.stdout)


class TestCheckAgentContext(HealthCheckerTestCase):
    def test_summary_reports_instruction_drift_without_delegation(self) -> None:
        proc = run_checker(
            "check_agent_context.py", FIXTURE_PROJECT, "summary", home=self.home
        )
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertIn("agent_instruction_status: WARN", proc.stdout)
        self.assertIn("claude_delegates_to_agents: no", proc.stdout)
        self.assertIn(
            "AGENTS.md and CLAUDE.md both contain substantial guidance"
            " without delegation",
            proc.stdout,
        )
        self.assertIn("conflict_status: WARN", proc.stdout)
        self.assertIn(
            "AGENTS.md and CLAUDE.md both exist; verify they do not diverge",
            proc.stdout,
        )
        # Isolated HOME has no Codex surface at all.
        self.assertIn("Codex surface not found", proc.stdout)


class TestCheckVerifierOutput(HealthCheckerTestCase):
    def _stale_path(self) -> str:
        path = f"/tmp/health-checker-stale-{uuid.uuid4().hex}/pkg/foo.go"
        self.assertFalse(Path(path).exists())
        return path

    def test_stale_tmp_path_with_known_tool_gets_cache_clean_action(self) -> None:
        stale = self._stale_path()
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "verifier.txt"
            log.write_text(
                "golangci-lint run\n"
                f'level=error msg="Running error: {stale}: no such file"\n',
                encoding="utf-8",
            )
            proc = run_checker("check_verifier_output.py", tmp, log, home=self.home)
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertIn("verifier_output_status: WARN", proc.stdout)
        self.assertIn(stale, proc.stdout)
        self.assertIn("golangci-lint cache clean", proc.stdout)
        self.assertIn("stale external verifier paths detected", proc.stdout)

    def test_stale_tmp_path_with_unknown_tool_gets_diagnostic_rerun_action(self) -> None:
        stale = self._stale_path()
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "verifier.txt"
            log.write_text(
                f"customverify: cannot open {stale}\n", encoding="utf-8"
            )
            proc = run_checker("check_verifier_output.py", tmp, log, home=self.home)
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertIn("verifier_output_status: WARN", proc.stdout)
        self.assertIn(
            "rerun the verifier after removing stale temporary worktrees",
            proc.stdout,
        )
        self.assertNotIn("golangci-lint cache clean", proc.stdout)

    def test_log_without_tmp_paths_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "verifier.txt"
            log.write_text("all checks passed\n", encoding="utf-8")
            proc = run_checker("check_verifier_output.py", tmp, log, home=self.home)
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertIn("verifier_output_status: PASS", proc.stdout)


if __name__ == "__main__":
    unittest.main()
