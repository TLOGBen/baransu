"""Write tests.csv (claim B) from git history by fixed rules (criteria.md), plus the rows the record states.

Rules, per commit before 8.0.0 (b505b8ae) that touched tests/:
- OVERRIDES name commits whose message or body says what turned the test red.
- a `test` commit adds tests: original-bug, not counted.
- any other commit that modified or deleted an existing test file: intent (the behaviour was meant to change).
- a commit that only added test files: original-bug, not counted.
Usage: uv run build_tests.py   (run from this folder; writes tests.csv)
"""
import csv
import subprocess
from pathlib import Path

HERE = Path(__file__).parent
REPO = HERE.parents[3]

OVERRIDES = {
    # diff (second derivation): two tests exposed latent Windows defects (cleanup-worktree.sh, transfer/health
    # output) - counted as regression to lean against claim B; two were wrong tests (str(...), a harness that
    # drops blank arguments on Windows)
    "2574bc67": [("regression", 2), ("wrong-test", 2)],
    # 「圖片守門測試放寬」: the test was too strict
    "59d7a3bb": [("wrong-test", 1)],
    # body: "fixes two test-design bugs surfaced by shipping"; plus the hardcoded version assertion bumped
    "702156f4": [("wrong-test", 2), ("intent", 1)],
    # body: drop hardcoded MAIN_ROOT (worktree-safe) = wrong test; recalibrate baseline = intent
    "471de2e4": [("wrong-test", 1), ("intent", 1)],
    # body: new test red on old SKILL.md (original); A3a/A3b/A4c updated to the new early stop (intent)
    "0123fc1e": [("intent", 1)],
}


def git(*args):
    return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True, encoding="utf-8", check=True).stdout


def main():
    out = []
    for line in git("log", "--format=%h|%s", "b505b8ae~1", "--", "tests").splitlines():
        h, subject = line.split("|", 1)
        kind = subject.split(":", 1)[0].split("(", 1)[0].rstrip("!")
        if h in OVERRIDES:
            for cause, n in OVERRIDES[h]:
                out.append({"id": h, "turned_red_because": cause, "count": n, "source": subject[:80]})
            continue
        status = git("show", "--format=", "--name-status", h, "--", "tests").split()
        touched = sum(1 for s in status if s in {"M", "D"} or s.startswith("R"))
        cause = "original-bug" if kind == "test" or touched == 0 else "intent"
        out.append({"id": h, "turned_red_because": cause, "count": 1, "source": subject[:80]})
    # This session (2026-11-04): 8.46.0 changed card behaviour on purpose; 21 kit tests went red, none caught a
    # regression in six runs (after.txt … after5.txt in the session scratchpad).
    out.append({"id": "kit-8.46.0", "turned_red_because": "intent", "count": 21, "source": "lint mod kit tests, 8.46.0 intent change"})
    with open(HERE / "tests.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "turned_red_because", "count", "source"])
        w.writeheader()
        w.writerows(out)
    print(f"wrote {len(out)} rows")


if __name__ == "__main__":
    main()
