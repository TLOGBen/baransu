#!/usr/bin/env python3
"""Pytest suite pinning current behavior of the hunt skill's bundled
catalog script scripts/hunt-search.py (plan item hunt-6).

The tests pin what the script does today; they do not invent new behavior.

Known limitation pinned deliberately: ``parse_frontmatter`` strips
everything after the first ``#`` in a value (``val.split("#")[0]``) so
that inline YAML comments in the shipped case template are dropped
(e.g. ``status: scoping  # scoping | investigating | ...``). As a side
effect, a value that legitimately contains ``#`` (e.g. an issue
reference like ``crash on issue #42``) is silently truncated. Fixing
the parser is a script behavior change and is out of scope for this
suite; see test_hash_in_value_is_truncated_known_limitation.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

THIS_FILE = Path(__file__).resolve()
REPO_ROOT = THIS_FILE.parents[2]
HUNT_DIR = REPO_ROOT / "plugins" / "baransu" / "skills" / "hunt"
SCRIPT = HUNT_DIR / "scripts" / "hunt-search.py"
TEMPLATE = HUNT_DIR / "references" / "hunt-case-template.md"


def load_module():
    """Import hunt-search.py (hyphenated filename) as a module."""
    spec = importlib.util.spec_from_file_location("hunt_search", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_search(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
    )


def write_case(
    report_dir: Path,
    hunt_id: str,
    status: str,
    target: str,
    root_cause: str = "",
) -> None:
    (report_dir / f"{hunt_id}.md").write_text(
        "---\n"
        f"hunt_id: {hunt_id}\n"
        f"target: {target}\n"
        f"status: {status}\n"
        "created: 2026-07-02\n"
        f'root_cause: "{root_cause}"\n'
        "---\n\n"
        f"# {hunt_id}\n",
        encoding="utf-8",
    )


class TestParseFrontmatter(unittest.TestCase):
    def setUp(self):
        self.mod = load_module()

    def test_shipped_case_template_parses(self):
        fm = self.mod.parse_frontmatter(TEMPLATE.read_text(encoding="utf-8"))
        self.assertEqual(fm.get("hunt_id"), "HUNT-YYYY-NNN")
        # Inline YAML comment after the value is stripped.
        self.assertEqual(fm.get("status"), "scoping")
        self.assertEqual(fm.get("created"), "YYYY-MM-DD")
        self.assertEqual(fm.get("target"), "一句話描述狩獵目標")
        # Indented (nested) lines are skipped, top-level keys survive.
        self.assertIn("scope", fm)
        self.assertNotIn("files", fm)

    def test_no_frontmatter_returns_empty_dict(self):
        self.assertEqual(self.mod.parse_frontmatter("# just a heading\n"), {})

    def test_hash_in_value_is_truncated_known_limitation(self):
        # KNOWN LIMITATION (pinned, not endorsed): val.split("#")[0] cannot
        # distinguish an inline YAML comment from a literal '#' inside the
        # value, so 'crash on issue #42' is truncated to 'crash on issue'.
        # A parser fix is a script behavior change — out of scope here.
        fm = self.mod.parse_frontmatter(
            "---\nhunt_id: HUNT-2026-009\ntarget: crash on issue #42\n---\n"
        )
        self.assertEqual(fm.get("target"), "crash on issue")


class TestCliFilters(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.report_dir = Path(self.tmp.name) / "hunt-report"
        self.report_dir.mkdir()
        write_case(
            self.report_dir,
            "HUNT-2026-001",
            status="fixed",
            target="stale cache in useUser",
            root_cause="missing userId in the dependency array",
        )
        write_case(
            self.report_dir,
            "HUNT-2026-002",
            status="scoping",
            target="login timeout",
        )
        # A file without hunt_id frontmatter is ignored by load_cases.
        (self.report_dir / "notes.md").write_text("scratch\n", encoding="utf-8")

    def run_dir(self, *args: str) -> subprocess.CompletedProcess:
        return run_search("--dir", str(self.report_dir), *args)

    def test_no_filter_lists_all_cases(self):
        proc = self.run_dir()
        self.assertEqual(proc.returncode, 0)
        self.assertIn("HUNT-2026-001", proc.stdout)
        self.assertIn("HUNT-2026-002", proc.stdout)
        self.assertIn("2 cases", proc.stdout)

    def test_status_filter(self):
        proc = self.run_dir("--status", "fixed")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("HUNT-2026-001", proc.stdout)
        self.assertNotIn("HUNT-2026-002", proc.stdout)

    def test_keyword_filter_matches_target_case_insensitively(self):
        proc = self.run_dir("--keyword", "CACHE")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("HUNT-2026-001", proc.stdout)
        self.assertNotIn("HUNT-2026-002", proc.stdout)

    def test_keyword_filter_matches_root_cause(self):
        proc = self.run_dir("--keyword", "userId")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("HUNT-2026-001", proc.stdout)
        self.assertNotIn("HUNT-2026-002", proc.stdout)

    def test_id_filter_exact_lookup(self):
        proc = self.run_dir("--id", "HUNT-2026-002")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("HUNT-2026-002", proc.stdout)
        self.assertNotIn("HUNT-2026-001", proc.stdout)

    def test_no_match_prints_empty_catalog_and_exits_zero(self):
        proc = self.run_dir("--status", "closed")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("（無符合的狩獵案例）", proc.stdout)


class TestMissingReportDir(unittest.TestCase):
    def test_missing_dir_exits_zero_with_message(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = run_search("--dir", str(Path(tmp) / "does-not-exist"))
        self.assertEqual(proc.returncode, 0)
        self.assertIn("（尚無狩獵報告）", proc.stdout)


if __name__ == "__main__":
    unittest.main()
