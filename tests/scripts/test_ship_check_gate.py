#!/usr/bin/env python3
"""F8b-stub R3-b — `make ship-check` is the mirror-drift gate's only entrypoint.

`mirror-check` is deliberately outside `make test` (mid-development skill edits
would stay red until regen), and this repo has no CI and no cron to pick it up.
That left the drift gate defended by nothing but memory. `ship-check` bundles
`test` + `mirror-check` so one command covers both before a release.

Pinned here by expanding the target with `make -n` and asserting the mirror
regen/diff step actually appears in the plan — dropping `mirror-check` from the
prerequisites turns this red.
"""

from __future__ import annotations

import os
import subprocess
import unittest
from pathlib import Path

WORKTREE_ROOT = Path(__file__).resolve().parents[2]
MAKEFILE = WORKTREE_ROOT / "Makefile"

# Substrings that only the mirror-check recipe can contribute to the plan.
MIRROR_CHECK_MARKERS = ("mirror in sync", "MIRROR DRIFT", "transfer.py")
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
    def test_ship_check_runs_mirror_check(self):
        plan = expand("ship-check")
        for marker in MIRROR_CHECK_MARKERS:
            self.assertIn(
                marker, plan,
                f"`make ship-check` 展開缺 mirror-check 步驟標記「{marker}」——"
                "鏡射漂移閘門無 CI／cron 承接，ship-check 是唯一入口，"
                "拿掉即等於沒有防線",
            )

    def test_ship_check_runs_the_full_suite(self):
        plan = expand("ship-check")
        for marker in TEST_MARKERS:
            self.assertIn(
                marker, plan,
                f"`make ship-check` 展開缺 test 步驟標記「{marker}」——"
                "ship-check 必須是 test ＋ mirror-check 串跑，不是 mirror-check 別名",
            )

    def test_mirror_check_stays_out_of_make_test(self):
        """Policy guard: bundling is ship-check's job, never test's."""
        plan = expand("test")
        self.assertNotIn(
            "mirror in sync", plan,
            "mirror-check 被併入 `make test`——開發中途未 regen 即紅，"
            "此為明文禁止的越權；串跑歸 ship-check",
        )


if __name__ == "__main__":
    unittest.main()
