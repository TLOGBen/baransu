#!/usr/bin/env python3
"""Tests for the two mechanical gates added to scripts/verify-skills.py:

Gate 10 (--loop-registry <skills-root> / repo mode): loop-pauses registry
completeness. Encoded variant (calibrated to current HEAD, see the check's
docstring): every `loop=drivable`/`loop=assisted` skill must ship
references/loop-pauses.md AND own a canonical row in
_shared/loop-contract.md §4 — with no exemption (the historical
codex-skill-transfer exemption was removed once that skill shipped its
table and registry row). `loop=not-drivable` skills
are exempt from shipping, but ANY shipped loop-pauses.md must be registered
(no orphans — think ships one and is registered), and every registry row
must resolve to an existing file (no dead links) with matching skill names.

Gate 11 (--green-proof <repo-root> / repo mode): green_proof field-name
cross-file consistency. The four keys test_command / exit_code /
output_tail / tests_correspondence must each appear in all four green_proof
surfaces (agents/review-agent.md, execute/references/{green-proof-verify,
orchestration-interface,output-formats}.md). Stale variants: `run_command`
is specific enough to flag anywhere in those files; `passed`/`collected`
are only flagged when anchored to a green_proof context (a key line inside
a `green_proof:` block, or a dotted `green_proof.passed` reference) —
output-formats.md legitimately uses passed:/collected: inside its
e2e_evidence block, which must NOT be flagged.

Negative fixtures are synthesized under a tempdir (no committed fixture
tree needed): each proves the targeted sub-rule alone flips exit 0 -> 1.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

THIS_FILE = Path(__file__).resolve()
REPO_ROOT = THIS_FILE.parents[2]
VERIFY = REPO_ROOT / "scripts" / "verify-skills.py"

GREEN_PROOF_FILES = (
    "plugins/baransu/agents/review-agent.md",
    "plugins/baransu/skills/analyze/references/green-proof-verify.md",
    "plugins/baransu/skills/analyze/references/orchestration-interface.md",
    "plugins/baransu/skills/analyze/references/output-formats.md",
)


def run_verify(*args: object) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(VERIFY), *[str(a) for a in args]],
        capture_output=True,
        text=True,
    )


# ---------------------------------------------------------------------------
# fixture builders
# ---------------------------------------------------------------------------
def build_loop_fixture(
    root: Path,
    skills: dict[str, tuple[str, bool]],
    registry_rows: list[str],
) -> Path:
    """skills: name -> (loop value, ships references/loop-pauses.md).

    registry_rows: raw markdown rows for the §4 table.
    """
    skills_root = root / "skills"
    shared = skills_root / "_shared"
    shared.mkdir(parents=True)
    table = "\n".join(
        ["## 4. PAUSE classification registry", "", "| Skill | PAUSE classification |", "|---|---|"]
        + registry_rows
    )
    (shared / "loop-contract.md").write_text(table + "\n", encoding="utf-8")
    for name, (loop, ships) in skills.items():
        d = skills_root / name
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text(
            "---\nname: %s\ndescription: stub\n---\n\n## Outcome Contract\n"
            "- **Automation**: ultracode=neutral, loop=%s（stub）\n" % (name, loop),
            encoding="utf-8",
        )
        if ships:
            refs = d / "references"
            refs.mkdir()
            (refs / "loop-pauses.md").write_text("# PAUSE table stub\n", encoding="utf-8")
    return skills_root


def row(name: str, target: str | None = None) -> str:
    target = target or name
    return f"| /{name} | `../{target}/references/loop-pauses.md` |"


GREEN_OK = {
    "plugins/baransu/agents/review-agent.md": (
        "green_proof:\n"
        "  test_command: {cmd}\n"
        "  exit_code: {int}\n"
        "  output_tail: {tail}\n"
        "  tests_correspondence: {map}\n"
    ),
    "plugins/baransu/skills/analyze/references/green-proof-verify.md": (
        "REQUIRE green_proof.test_command present\n"
        "REQUIRE green_proof.exit_code == 0\n"
        "REQUIRE green_proof.output_tail non-empty\n"
        "REQUIRE green_proof.tests_correspondence declared\n"
    ),
    "plugins/baransu/skills/analyze/references/orchestration-interface.md": (
        "| green_proof | `test_command`, `exit_code`, `output_tail`, "
        "`tests_correspondence` |\n"
    ),
    "plugins/baransu/skills/analyze/references/output-formats.md": (
        "green_proof: `{test_command}` exit {exit_code}\n"
        "output_tail and tests_correspondence cited\n"
        "e2e_evidence:\n"
        "  collected: {N}\n"
        "  passed: {N}\n"
    ),
}


def build_green_fixture(root: Path, overrides: dict[str, str] | None = None) -> Path:
    content = dict(GREEN_OK)
    content.update(overrides or {})
    for rel, text in content.items():
        if text is None:
            continue
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    return root


# ---------------------------------------------------------------------------
# repo mode: both gates pass on current HEAD and print their ✅ lines
# ---------------------------------------------------------------------------
class TestRepoGatesPass(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = run_verify()
        cls.out = cls.result.stdout + cls.result.stderr

    def test_exit_zero(self):
        self.assertEqual(self.result.returncode, 0, self.out)

    def test_loop_registry_pass_line(self):
        self.assertIn("loop-pauses 註冊表", self.out)

    def test_green_proof_pass_line(self):
        self.assertIn("green_proof 欄位名跨檔一致", self.out)


# ---------------------------------------------------------------------------
# Gate 10 negatives (--loop-registry)
# ---------------------------------------------------------------------------
class TestLoopRegistryGate(unittest.TestCase):
    def _run(self, skills, rows):
        with tempfile.TemporaryDirectory() as tmp:
            skills_root = build_loop_fixture(Path(tmp), skills, rows)
            result = run_verify("--loop-registry", skills_root)
            return result, result.stdout + result.stderr

    def test_clean_fixture_passes(self):
        skills = {
            "alpha": ("drivable", True),
            "beta": ("assisted", True),
            "gamma": ("not-drivable", False),
            "delta": ("not-drivable", True),  # think-style: ships + registered
        }
        result, out = self._run(skills, [row("alpha"), row("beta"), row("delta")])
        self.assertEqual(result.returncode, 0, out)

    def test_no_exemption_codex_skill_transfer_is_enforced(self):
        # The historical LOOP_PAUSES_EXEMPT entry is gone: an assisted
        # codex-skill-transfer without loop-pauses.md + registry row now
        # fails Gate 10 like any other skill.
        skills = {
            "alpha": ("drivable", True),
            "codex-skill-transfer": ("assisted", False),
        }
        result, out = self._run(skills, [row("alpha")])
        self.assertEqual(result.returncode, 1, out)
        self.assertIn("codex-skill-transfer", out)

    def test_drivable_missing_file_flagged(self):
        skills = {"alpha": ("drivable", False)}
        result, out = self._run(skills, [row("alpha")])
        self.assertEqual(result.returncode, 1, out)
        self.assertIn("alpha", out)
        self.assertIn("loop-pauses.md", out)

    def test_assisted_missing_registry_row_flagged(self):
        skills = {"beta": ("assisted", True)}
        result, out = self._run(skills, [])
        self.assertEqual(result.returncode, 1, out)
        self.assertIn("beta", out)

    def test_orphan_file_on_not_drivable_flagged(self):
        skills = {"gamma": ("not-drivable", True)}
        result, out = self._run(skills, [])
        self.assertEqual(result.returncode, 1, out)
        self.assertIn("gamma", out)

    def test_dead_registry_row_flagged(self):
        skills = {"alpha": ("drivable", True)}
        result, out = self._run(skills, [row("alpha"), row("ghost")])
        self.assertEqual(result.returncode, 1, out)
        self.assertIn("ghost", out)

    def test_row_name_mismatch_flagged(self):
        skills = {"alpha": ("drivable", True), "beta": ("assisted", True)}
        result, out = self._run(
            skills, [row("alpha", target="beta"), row("beta")]
        )
        self.assertEqual(result.returncode, 1, out)

    def test_malformed_row_flagged(self):
        skills = {"alpha": ("drivable", True)}
        rows = [
            row("alpha"),
            "| alpha | ../alpha/references/loop-pauses.md |",  # no /, no backticks
        ]
        result, out = self._run(skills, rows)
        self.assertEqual(result.returncode, 1, out)


# ---------------------------------------------------------------------------
# Gate 11 negatives (--green-proof)
# ---------------------------------------------------------------------------
class TestGreenProofGate(unittest.TestCase):
    def _run(self, overrides=None):
        with tempfile.TemporaryDirectory() as tmp:
            root = build_green_fixture(Path(tmp), overrides)
            result = run_verify("--green-proof", root)
            return result, result.stdout + result.stderr

    def test_clean_fixture_passes(self):
        result, out = self._run()
        self.assertEqual(result.returncode, 0, out)

    def test_missing_key_flagged(self):
        overrides = {
            "plugins/baransu/skills/analyze/references/orchestration-interface.md":
                "| green_proof | `test_command`, `exit_code`, `output_tail` |\n",
        }
        result, out = self._run(overrides)
        self.assertEqual(result.returncode, 1, out)
        self.assertIn("orchestration-interface.md", out)
        self.assertIn("tests_correspondence", out)

    def test_run_command_flagged_anywhere(self):
        overrides = {
            "plugins/baransu/skills/analyze/references/green-proof-verify.md":
                GREEN_OK["plugins/baransu/skills/analyze/references/green-proof-verify.md"]
                + "legacy prose mentioning run_command here\n",
        }
        result, out = self._run(overrides)
        self.assertEqual(result.returncode, 1, out)
        self.assertIn("run_command", out)

    def test_stale_key_inside_green_proof_block_flagged(self):
        overrides = {
            "plugins/baransu/agents/review-agent.md": (
                "green_proof:\n"
                "  test_command: x\n"
                "  exit_code: 0\n"
                "  output_tail: y\n"
                "  tests_correspondence: z\n"
                "  passed: 3\n"
            ),
        }
        result, out = self._run(overrides)
        self.assertEqual(result.returncode, 1, out)
        self.assertIn("passed", out)

    def test_dotted_stale_reference_flagged(self):
        overrides = {
            "plugins/baransu/skills/analyze/references/green-proof-verify.md":
                GREEN_OK["plugins/baransu/skills/analyze/references/green-proof-verify.md"]
                + "REQUIRE green_proof.collected > 0\n",
        }
        result, out = self._run(overrides)
        self.assertEqual(result.returncode, 1, out)
        self.assertIn("collected", out)

    def test_e2e_evidence_block_not_false_positive(self):
        # passed:/collected: under e2e_evidence: (and 'passed' in prose) are
        # legitimate — the default output-formats fixture carries them and
        # the clean run must stay green.
        overrides = {
            "plugins/baransu/skills/analyze/references/green-proof-verify.md":
                GREEN_OK["plugins/baransu/skills/analyze/references/green-proof-verify.md"]
                + "# else Green failed, not a passed review\n",
        }
        result, out = self._run(overrides)
        self.assertEqual(result.returncode, 0, out)

    def test_missing_surface_file_flagged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = build_green_fixture(Path(tmp))
            (root / "plugins/baransu/agents/review-agent.md").unlink()
            result = run_verify("--green-proof", root)
            out = result.stdout + result.stderr
        self.assertEqual(result.returncode, 1, out)
        self.assertIn("review-agent.md", out)


if __name__ == "__main__":
    unittest.main()
