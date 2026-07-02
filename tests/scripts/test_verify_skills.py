#!/usr/bin/env python3
"""Tests for scripts/verify-skills.py — structure verifier (REQ-005 Scenario 2).

Positive: the current repo passes every check (exit 0); the per-skill pass
list covers all 14 skills; no >500-line advisory remains (execute was slimmed
under the cap in v2.1.0).

Negative: a fixture SKILL.md stub missing the Outcome Contract block makes
the verifier exit 1 and name the violation (falsifiability proof for C6).
Further negative fixtures (B2: pw-1/pw-3/pw-4/pw-8) prove the name==dir,
XML-tag, reserved-word, listing-budget, and agent-ignored-field checks can
each fail on a stub whose only defect is the targeted one.

Layout: the verifier lives in the repo-root scripts/ directory (maintenance
tool, not packaged); the packaged plugins/baransu/scripts/ directory must
stay absent.
"""

from __future__ import annotations

import re
import subprocess
import sys
import unittest
from pathlib import Path

THIS_FILE = Path(__file__).resolve()
REPO_ROOT = THIS_FILE.parents[2]
VERIFY = REPO_ROOT / "scripts" / "verify-skills.py"
FIXTURE_SKILLS_ROOT = THIS_FILE.parent / "fixtures" / "verify-skills"
FIXTURE_FRONTMATTER_ROOT = THIS_FILE.parent / "fixtures" / "verify-skills-frontmatter"
FIXTURE_AGENTS_DIR = THIS_FILE.parent / "fixtures" / "verify-skills-agents"

# Mirrors LISTING_TOTAL_ADVISORY in scripts/verify-skills.py (v2.1.x default
# 1% listing budget ≈7,000 chars; settings-tunable, hence advisory-only).
LISTING_TOTAL_ADVISORY = 7000

EXPECTED_SKILLS = [
    "analyze",
    "book",
    "codex-skill-transfer",
    "design",
    "evolve",
    "execute",
    "health",
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

    def test_per_skill_pass_list_covers_all_14_skills(self):
        for name in EXPECTED_SKILLS:
            self.assertIn(name, self.out, f"per-skill pass list missing: {name}")

    def test_no_oversize_advisory_remains(self):
        # v2.1.0 slimmed execute/SKILL.md under the 500-line official cap
        # (sections moved verbatim to execute/references/). No skill should
        # trigger the ADVISORY list any more; a reappearing line means a
        # SKILL.md regressed past the cap.
        advisory_lines = [
            line for line in self.out.splitlines() if "ADVISORY" in line
        ]
        self.assertFalse(
            advisory_lines,
            f"unexpected oversize ADVISORY lines: {advisory_lines}",
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


class TestListingBudgetAdvisory(unittest.TestCase):
    """B2 pw-4: repo mode prints the combined-listing total; the advisory
    line fires exactly when the printed total exceeds the 7,000-char
    threshold (baseline 7,198 chars on 2026-07-02 — it fires today) and
    never affects the exit code."""

    TOTAL_RE = re.compile(r"listing 總量：description\+when_to_use 合計 (\d+) 字元")

    @classmethod
    def setUpClass(cls):
        cls.result = run_verify()
        cls.out = cls.result.stdout + cls.result.stderr

    def test_total_line_printed(self):
        self.assertRegex(self.out, self.TOTAL_RE)

    def test_advisory_fires_iff_total_exceeds_threshold(self):
        m = self.TOTAL_RE.search(self.out)
        self.assertIsNotNone(m, f"total line missing:\n{self.out}")
        total = int(m.group(1))
        if total > LISTING_TOTAL_ADVISORY:
            self.assertIn("listing 預算警示", self.out)
        else:
            self.assertNotIn("listing 預算警示", self.out)

    def test_advisory_does_not_affect_exit_code(self):
        self.assertEqual(self.result.returncode, 0, self.out)


class TestFrontmatterNegativeFixtures(unittest.TestCase):
    """B2 falsifiability: pw-1 (name==dir), pw-3 (XML tag / reserved word),
    pw-4 (per-skill 1536 listing cap) each fail on a dedicated stub whose
    only defect is the targeted one."""

    STUBS = ("name-mismatch", "xml-tag", "claude-helper", "oversize-listing")

    @classmethod
    def setUpClass(cls):
        cls.result = run_verify(FIXTURE_FRONTMATTER_ROOT)
        cls.out = cls.result.stdout + cls.result.stderr

    def test_fixture_stubs_exist(self):
        for stub in self.STUBS:
            self.assertTrue(
                (FIXTURE_FRONTMATTER_ROOT / stub / "SKILL.md").is_file(),
                f"missing fixture: {FIXTURE_FRONTMATTER_ROOT}/{stub}/SKILL.md",
            )

    def test_exits_one(self):
        self.assertEqual(
            self.result.returncode, 1,
            f"verifier must exit 1 on the frontmatter stubs but "
            f"exit={self.result.returncode}\noutput:\n{self.out}",
        )

    def test_name_mismatch_flagged(self):
        self.assertIn("name-mismatch: frontmatter name ≠ 目錄名", self.out)

    def test_xml_tag_flagged(self):
        self.assertIn("xml-tag: description 含 XML tag", self.out)

    def test_reserved_word_flagged(self):
        self.assertIn("claude-helper: name 含保留字 'claude'", self.out)

    def test_listing_cap_flagged(self):
        self.assertIn(
            "oversize-listing: description+when_to_use 合計 1600 字元", self.out
        )

    def test_each_stub_contributes_exactly_one_violation(self):
        # Every stub is otherwise valid, so the four targeted checks are the
        # only violations — proof each check alone flips exit 0 → 1.
        self.assertIn("共 4 項違規", self.out)


class TestAgentsNegativeFixture(unittest.TestCase):
    """B2 pw-8 falsifiability: an agent stub carrying permissionMode is
    rejected with exit 1 in --agents mode; the shipped agents dir passes."""

    @classmethod
    def setUpClass(cls):
        cls.result = run_verify("--agents", FIXTURE_AGENTS_DIR)
        cls.out = cls.result.stdout + cls.result.stderr

    def test_fixture_agent_exists(self):
        self.assertTrue(
            (FIXTURE_AGENTS_DIR / "bad-agent.md").is_file(),
            f"missing fixture: {FIXTURE_AGENTS_DIR}/bad-agent.md",
        )

    def test_exits_one(self):
        self.assertEqual(
            self.result.returncode, 1,
            f"verifier must exit 1 on the bad-agent stub but "
            f"exit={self.result.returncode}\noutput:\n{self.out}",
        )

    def test_violation_names_agent_and_ignored_field(self):
        self.assertIn("bad-agent.md", self.out)
        self.assertIn("permissionMode", self.out)
        self.assertIn("被靜默忽略欄位", self.out)

    def test_shipped_agents_dir_passes(self):
        result = run_verify("--agents", REPO_ROOT / "plugins" / "baransu" / "agents")
        self.assertEqual(
            result.returncode, 0,
            f"shipped agents dir must stay clean\n{result.stdout}{result.stderr}",
        )


if __name__ == "__main__":
    unittest.main()
