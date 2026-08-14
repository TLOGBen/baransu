#!/usr/bin/env python3
"""Tests for the loop-pauses registry gate in scripts/verify-skills.py:

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

Gate 11 (green_proof field-name consistency) was retired in v4.0.0 along
with the /analyze execution pipeline that owned all four of its surfaces —
there is no longer a green_proof field anywhere in plugins/, so the gate had
nothing left to check. Its negative fixtures are removed with it.

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


# ---------------------------------------------------------------------------
# repo mode: the gate passes on current HEAD and prints its ✅ line
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


if __name__ == "__main__":
    unittest.main()
