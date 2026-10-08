#!/usr/bin/env python3
"""`make ship-check` is the Codex parity gate's only entrypoint.

The Codex copy under codex/plugins/baransu/ is maintained by hand. `parity-check`
(scripts/verify-codex-parity.py) is deliberately outside `make test`
(mid-development edits may lag on one side), and this repo has no CI and no
cron to pick it up. `ship-check` bundles `test` + `parity-check` so one command
covers both before a release.

Pinned here by expanding the target with `make -n` and asserting the parity
step actually appears in the plan — dropping `parity-check` from the
prerequisites turns this red. The plan must never regenerate the Codex copy
with transfer.py. The parity script itself is exercised on fixtures below.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

WORKTREE_ROOT = Path(__file__).resolve().parents[2]
PARITY_SCRIPT = WORKTREE_ROOT / "scripts" / "verify-codex-parity.py"

# Substring that only the parity-check recipe contributes to the plan.
PARITY_MARKERS = ("verify-codex-parity.py",)
# ...and the ones only the test recipe contributes.
TEST_MARKERS = ("verify-skills.py", "pytest")


def expand(target: str) -> str:
    """Dry-run expansion of a make target (no recipe is executed)."""
    env = dict(os.environ)
    env.pop("MAKEFLAGS", None)  # never inherit the outer `make test` invocation
    result = subprocess.run(
        ["make", "-n", "--no-print-directory", target],
        cwd=WORKTREE_ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, (
        f"`make -n {target}` 失敗（exit {result.returncode}）：{result.stderr.strip()}"
    )
    return result.stdout


class TestShipCheckGate(unittest.TestCase):
    def test_ship_check_runs_parity_check(self):
        plan = expand("ship-check")
        for marker in PARITY_MARKERS:
            self.assertIn(
                marker, plan,
                f"`make ship-check` 展開缺 parity-check 步驟標記「{marker}」——"
                "Codex 版配對閘門無 CI／cron 承接，ship-check 是唯一入口",
            )

    def test_ship_check_never_regenerates_with_transfer_script(self):
        plan = expand("ship-check")
        self.assertNotIn(
            "transfer.py", plan,
            "Codex 版改為手動維護，ship-check 不得再以 transfer.py 重產或比對",
        )

    def test_ship_check_runs_the_full_suite(self):
        plan = expand("ship-check")
        for marker in TEST_MARKERS:
            self.assertIn(
                marker, plan,
                f"`make ship-check` 展開缺 test 步驟標記「{marker}」——"
                "ship-check 必須是 test ＋ parity-check 串跑，不是 parity-check 別名",
            )

    def test_parity_check_stays_out_of_make_test(self):
        """Policy guard: bundling is ship-check's job, never test's."""
        plan = expand("test")
        self.assertNotIn(
            "verify-codex-parity.py", plan,
            "parity-check 被併入 `make test`——開發中途單邊未同步即紅；串跑歸 ship-check",
        )


def make_pair(root: Path, claude_files: list[str], codex_files: list[str],
              claude_version: str = "1.0.0", codex_version: str = "1.0.0"):
    claude = root / "claude"
    codex = root / "codex"
    for base, files in ((claude / "skills", claude_files), (codex / "skills", codex_files)):
        for rel in files:
            path = base / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("x\n", encoding="utf-8")
    (claude / ".claude-plugin").mkdir(parents=True, exist_ok=True)
    (claude / ".claude-plugin" / "plugin.json").write_text(
        json.dumps({"name": "p", "version": claude_version}), encoding="utf-8")
    codex.mkdir(parents=True, exist_ok=True)
    (codex / "plugin.json").write_text(
        json.dumps({"name": "p", "version": codex_version}), encoding="utf-8")
    return claude, codex


def run_parity(claude: Path, codex: Path) -> subprocess.CompletedProcess:
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
    return subprocess.run(
        [sys.executable, str(PARITY_SCRIPT), str(claude), str(codex)],
        capture_output=True, text=True, encoding="utf-8", env=env, timeout=60,
    )


class TestParityScript(unittest.TestCase):
    def test_matching_pair_passes_and_allows_codex_only_openai_yaml(self):
        with tempfile.TemporaryDirectory() as tmp:
            claude, codex = make_pair(
                Path(tmp),
                ["a/SKILL.md", "a/templates/t.md"],
                ["a/SKILL.md", "a/templates/t.md", "a/agents/openai.yaml"],
            )
            proc = run_parity(claude, codex)
            self.assertEqual(0, proc.returncode, proc.stdout)
            self.assertIn("codex parity OK", proc.stdout)

    def test_missing_codex_file_fails_and_names_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            claude, codex = make_pair(
                Path(tmp), ["a/SKILL.md", "a/templates/t.md"], ["a/SKILL.md"])
            proc = run_parity(claude, codex)
            self.assertEqual(1, proc.returncode, proc.stdout)
            self.assertIn("skills/a/templates/t.md", proc.stdout)

    def test_extra_codex_file_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            claude, codex = make_pair(
                Path(tmp), ["a/SKILL.md"], ["a/SKILL.md", "b/SKILL.md"])
            proc = run_parity(claude, codex)
            self.assertEqual(1, proc.returncode, proc.stdout)
            self.assertIn("skills/b/SKILL.md", proc.stdout)

    def test_version_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            claude, codex = make_pair(
                Path(tmp), ["a/SKILL.md"], ["a/SKILL.md"], "1.0.0", "0.9.0")
            proc = run_parity(claude, codex)
            self.assertEqual(1, proc.returncode, proc.stdout)
            self.assertIn("version 不一致", proc.stdout)


if __name__ == "__main__":
    unittest.main()
