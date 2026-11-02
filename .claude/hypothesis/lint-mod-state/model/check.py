"""Run every TLC question of the lint-mod-state hypothesis.

Each run: its own scratch directory (copied .tla files and a generated .cfg),
-workers 1, a time limit, a Java heap limit. Prints held/violated, states, seconds,
and whether that matches the expected verdict.

  uv run python check.py           # full list
  uv run python check.py --quick   # MaxSteps 5 (same expected verdicts)
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
TLC = shutil.which("tlc") or str(Path.home() / ".local" / "bin" / "tlc")
TIME_LIMIT = 120  # seconds per run
BUDGET = 1500     # seconds for the whole list

INVARIANTS = {"R1", "R2", "R4", "R6", "R7", "R8", "R9", "R10", "R11"}
PROPERTIES = {"R3", "R5"}

# (version, break, rule, expected)  expected: "held" or "violated"
# version: "v1" the source before the first fix, "v2" the source at 0917b911, "now" the source now.
ALL = ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "R9", "R10", "R11"]
V2_BROKEN = {"R1", "R4", "R5", "R6", "R7", "R8", "R11"}  # what the review of 0917b911 found, each a path below
RUNS = (
    [("v1", "none", r, "held" if r == "R3" else "violated") for r in ALL]
    + [("v2", "none", r, "violated" if r in V2_BROKEN else "held") for r in ALL]
    + [("now", "none", r, "held") for r in ALL]
    # the checks can say no: one planted bug per rule the newest source keeps that it would otherwise hold
    + [("now", r, r, "violated") for r in ["R2", "R3", "R5", "R7", "R8", "R11"]]
)
CONSTS = {"v1": ("FALSE", "FALSE"), "v2": ("TRUE", "FALSE"), "now": ("TRUE", "TRUE")}


def cfg(version: str, brk: str, rule: str, steps: int) -> str:
    kind = "INVARIANT" if rule in INVARIANTS else "PROPERTY"
    fix, now = CONSTS[version]
    return (
        "SPECIFICATION Spec\n"
        "CONSTANTS\n"
        "  Blocks = {1, 2}\n"
        '  Cmds = {"c1", "c2"}\n'
        f"  Fix = {fix}\n"
        f"  Now = {now}\n"
        f'  Break = "{brk}"\n'
        f"  MaxSteps = {steps}\n"
        f"{kind} {rule}\n"
    )


def run_one(fix: str, brk: str, rule: str, steps: int):
    work = Path(tempfile.mkdtemp(prefix="lintmod-"))
    try:
        for name in ("LintRules.tla", "LintMod.tla"):
            shutil.copy(HERE / name, work / name)
        (work / "Run.cfg").write_text(cfg(fix, brk, rule, steps), encoding="ascii")
        env = dict(os.environ, JAVA_TOOL_OPTIONS="-Xmx1g")
        t0 = time.time()
        try:
            out = subprocess.run(
                [TLC, "-workers", "1", "-deadlock", "-metadir", str(work / "meta"), "-config", "Run.cfg", "LintMod.tla"],
                cwd=work, env=env, capture_output=True, text=True, timeout=TIME_LIMIT,
            )
            text = out.stdout + out.stderr
        except subprocess.TimeoutExpired:
            return "timeout", 0, time.time() - t0, ""
        secs = time.time() - t0
        states = re.findall(r"(\d+) distinct states found", text)
        n = int(states[-1]) if states else 0
        if re.search(r"Error: (Invariant|Action property|Temporal properties)", text) or "is violated" in text:
            verdict = "violated"
        elif "No error has been found" in text:
            verdict = "held"
        else:
            verdict = "error"
        return verdict, n, secs, text
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main() -> int:
    # 7 is the smallest scope where the parallel double restate (R2) appears; quick runs it too.
    steps = 7 if "--quick" in sys.argv else 8
    spent = 0.0
    bad = 0
    traces = HERE / "traces"
    traces.mkdir(exist_ok=True)
    for fix, brk, rule, expected in RUNS:
        if spent > BUDGET:
            print(f"budget spent ({spent:.0f}s): stopping before {rule} {fix} break={brk}")
            return 2
        verdict, n, secs, text = run_one(fix, brk, rule, steps)
        spent += secs
        ok = verdict == expected
        bad += not ok
        label = f"{rule:<4} {fix:<4} break={brk:<4}"
        print(f"{'ok ' if ok else 'BAD'} {label} {verdict:<8} (expected {expected}) states={n} {secs:.1f}s")
        if verdict == "violated" and brk == "none":
            (traces / f"{rule}-{fix}.txt").write_text(text, encoding="utf-8")
    print(f"MaxSteps={steps}; {len(RUNS) - bad}/{len(RUNS)} as expected; {spent:.0f}s")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
