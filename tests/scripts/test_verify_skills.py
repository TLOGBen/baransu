#!/usr/bin/env python3
"""Tests for scripts/verify-skills.py — structure verifier (REQ-005 Scenario 2).

Positive: the current repo passes every check (exit 0); the per-skill pass
list covers all 12 skills; the >500-line advisory is emitted (execute is the
known oversize SKILL.md) without affecting the exit code.

Negative: a fixture SKILL.md stub missing the Outcome Contract block makes
the verifier exit 1 and name the violation (falsifiability proof for C6).

Layout: the verifier lives in the repo-root scripts/ directory (maintenance
tool, not packaged); the packaged plugins/baransu/scripts/ directory must
stay absent.
"""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

THIS_FILE = Path(__file__).resolve()
REPO_ROOT = THIS_FILE.parents[2]
VERIFY = REPO_ROOT / "scripts" / "verify-skills.py"
FIXTURE_SKILLS_ROOT = THIS_FILE.parent / "fixtures" / "verify-skills"

EXPECTED_SKILLS = [
    "analyze",
    "book",
    "codex-skill-transfer",
    "design",
    "execute",
    "hunt",
    "learn",
    "read",
    "review",
    "ship",
    "think",
    "write",
]


def run_verify(*args: object) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(VERIFY), *[str(a) for a in args]],
        capture_output=True,
        text=True,
    )


class TestRepoLayout(unittest.TestCase):
    """Integration: repo-root scripts/ is new; packaged scripts/ dir stays absent."""

    def test_verifier_lives_in_repo_root_scripts(self):
        self.assertTrue(VERIFY.is_file(), f"missing verifier: {VERIFY}")

    def test_packaged_scripts_dir_stays_absent(self):
        packaged = REPO_ROOT / "plugins" / "baransu" / "scripts"
        self.assertFalse(
            packaged.exists(),
            f"{packaged} must not exist — the verifier is a maintenance tool, "
            "not a packaged asset",
        )


class TestCurrentRepoPasses(unittest.TestCase):
    """E2E positive path: one command proves structural integrity (exit 0)."""

    @classmethod
    def setUpClass(cls):
        cls.result = run_verify()
        cls.out = cls.result.stdout + cls.result.stderr

    def test_exit_zero_on_current_repo(self):
        self.assertEqual(
            self.result.returncode, 0,
            f"verify-skills must PASS on the current repo but "
            f"exit={self.result.returncode}\noutput:\n{self.out}",
        )

    def test_per_skill_pass_list_covers_all_12_skills(self):
        for name in EXPECTED_SKILLS:
            self.assertIn(name, self.out, f"per-skill pass list missing: {name}")

    def test_oversize_advisory_lists_execute_without_failing(self):
        # execute SKILL.md is the known >500-line file: it must appear in the
        # ADVISORY list, while the overall run still exits 0 (asserted above).
        advisory_lines = [
            line for line in self.out.splitlines() if "ADVISORY" in line
        ]
        self.assertTrue(advisory_lines, "no ADVISORY line in output")
        self.assertTrue(
            any("execute" in line for line in advisory_lines),
            f"ADVISORY must list the oversize 'execute' SKILL.md; "
            f"got: {advisory_lines}",
        )


class TestNegativeFixture(unittest.TestCase):
    """E2E negative path: a violating stub is rejected with exit 1 (C6)."""

    @classmethod
    def setUpClass(cls):
        cls.result = run_verify(FIXTURE_SKILLS_ROOT)
        cls.out = cls.result.stdout + cls.result.stderr

    def test_fixture_skills_root_exists(self):
        self.assertTrue(
            (FIXTURE_SKILLS_ROOT / "bad-skill" / "SKILL.md").is_file(),
            f"missing fixture: {FIXTURE_SKILLS_ROOT}/bad-skill/SKILL.md",
        )

    def test_missing_contract_exits_one(self):
        self.assertEqual(
            self.result.returncode, 1,
            f"verifier must exit 1 on the bad-skill stub but "
            f"exit={self.result.returncode}\noutput:\n{self.out}",
        )

    def test_violation_names_skill_and_missing_contract(self):
        self.assertIn("bad-skill", self.out, "violation must name the skill")
        self.assertIn(
            "Outcome Contract", self.out,
            "violation must name the missing Outcome Contract block",
        )


if __name__ == "__main__":
    unittest.main()
