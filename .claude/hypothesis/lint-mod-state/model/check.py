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

INVARIANTS = {"R1", "R2", "R4", "R6", "R7", "R8", "R9", "R10", "R11", "R12"}
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


# --mutants: which hook steps no rule can do without. Each mutant removes one step's core effect from the
# newest source (Mut in LintMod.tla); the rules it breaks say where a unit test must hold that step.
MUTANTS = {
    "prompt-take": "prompt.submit hands over what is owed",
    "start-reset": "turn.start resets the turn's flags",
    "stream-deaf": "turn.step text before a call is heard",
    "text-deaf": "text after the last call is heard",
    "call-take": "a main call takes the restates owed",
    "no-explain": "the first act with no words is flagged",
    "no-hold": "a delete is held for preview",
    "work-keeps-report": "a call that did work forgets the report before it",
    "no-edit-count": "an edit is counted",
    "no-owe": "turn.complete records the report owed",
    "review-ignored": "an answered /review is recorded",
    "reload-forgets": "a reload keeps the state",
    "clear-keeps": "/clear starts the state over",
}


def cfg(version: str, brk: str, rule: str, steps: int, mut: str = "none") -> str:
    rules = rule.split(",")
    kind = "INVARIANT" if rules[0] in INVARIANTS else "PROPERTY"
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
        f'  Mut = "{mut}"\n'
        + "".join(f"{kind} {r}\n" for r in rules)
    )


def run_one(fix: str, brk: str, rule: str, steps: int, mut: str = "none"):
    work = Path(tempfile.mkdtemp(prefix="lintmod-"))
    try:
        for name in ("LintRules.tla", "LintMod.tla"):
            shutil.copy(HERE / name, work / name)
        (work / "Run.cfg").write_text(cfg(fix, brk, rule, steps, mut), encoding="ascii")
        env = dict(os.environ, JAVA_TOOL_OPTIONS="-Xmx1g")
        t0 = time.time()
        cont = ["-continue"] if "," in rule else []
        try:
            out = subprocess.run(
                [TLC, "-workers", "1", "-deadlock", *cont, "-metadir", str(work / "meta"), "-config", "Run.cfg", "LintMod.tla"],
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


def mutants(steps: int) -> int:
    inv = ",".join(sorted(INVARIANTS, key=lambda r: int(r[1:])))
    spent = 0.0
    for mut, what in MUTANTS.items():
        broken = []
        for rule in [inv, "R3", "R5"]:
            if spent > BUDGET:
                print(f"budget spent ({spent:.0f}s): stopping at {mut}")
                return 2
            verdict, n, secs, text = run_one("now", "none", rule, steps, mut)
            spent += secs
            if verdict == "timeout" or verdict == "error":
                broken.append(f"{rule}:{verdict}")
            else:
                broken += sorted(set(re.findall(r"(?:Invariant|property) (R\d+) is violated", text)), key=lambda r: int(r[1:]))
        print(f"{mut:<18} {what:<52} breaks: {', '.join(broken) or '(none)'}")
    print(f"MaxSteps={steps}; {len(MUTANTS)} mutants; {spent:.0f}s")
    return 0


def main() -> int:
    # 7 is the smallest scope where the parallel double restate (R2) appears; quick runs it too.
    steps = 7 if "--quick" in sys.argv else 8
    if "--mutants" in sys.argv:
        return mutants(steps)
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
