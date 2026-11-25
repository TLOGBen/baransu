"""Run every TLC question of the lint-cards hypothesis.

Each run: its own scratch directory, -workers 1, a time limit, a Java heap limit; one rule per run (TLC reports
only the first rule a state breaks), stopping at its first violation, so each trace is one shortest path.

  python check.py           # MaxSteps 8
  python check.py --quick   # MaxSteps 6
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
TIME_LIMIT = 240
BUDGET = 900
RULES = ["A", "B", "D", "Q1"]

# (variant, KeepFirst, Cap, expected rules broken). Cap 1 makes the trim happen with two calls.
RUNS = [
    ("old", True, 2, {"A", "B", "Q1"}),       # the source now
    ("new", True, 2, set()),                  # the change
    ("new", True, 1, set()),                  # the change, with the trim
    ("new", False, 2, None),                  # the change if the card were kept after the row is drawn: a question
    ("nogroup", True, 2, {"Q1"}),             # the checks can say no: each part of the change removed once
    ("noempty", True, 2, {"B"}),
    ("double", True, 2, {"D"}),
    ("new", True, 2, "reading"),              # the open reading: a group the person closed stays closed
]


def cfg(variant, keep, cap, steps, rules):
    return (
        "SPECIFICATION Spec\nCONSTANTS\n  Calls = {1, 2}\n"
        f'  Variant = "{variant}"\n  KeepFirst = {"TRUE" if keep else "FALSE"}\n  Cap = {cap}\n  MaxSteps = {steps}\n'
        + "".join(f"INVARIANT {r}\n" for r in rules)
    )


def run(variant, keep, cap, steps, rules):
    work = Path(tempfile.mkdtemp(prefix="cards-"))
    try:
        for name in ("CardRules.tla", "CardRender.tla"):
            shutil.copy(HERE / name, work / name)
        (work / "Run.cfg").write_text(cfg(variant, keep, cap, steps, rules), encoding="ascii")
        env = dict(os.environ, JAVA_TOOL_OPTIONS="-Xmx1g")
        t0 = time.time()
        try:
            out = subprocess.run([TLC, "-workers", "1", "-deadlock", "-metadir", str(work / "meta"),
                                  "-config", "Run.cfg", "CardRender.tla"],
                                 cwd=work, env=env, capture_output=True, text=True, timeout=TIME_LIMIT)
            text = out.stdout + out.stderr
        except subprocess.TimeoutExpired:
            return None, 0, time.time() - t0, ""
        states = re.findall(r"(\d+) distinct states found", text)
        broken = set(re.findall(r"Invariant (\w+) is violated", text))
        if not broken and "No error has been found" not in text:
            return "error", 0, time.time() - t0, text
        return broken, int(states[-1]) if states else 0, time.time() - t0, text
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main():
    steps = 6 if "--quick" in sys.argv else 8
    spent, bad = 0.0, 0
    traces = HERE / "traces"
    traces.mkdir(exist_ok=True)
    for variant, keep, cap, expected in RUNS:
        if spent > BUDGET:
            print(f"budget spent ({spent:.0f}s)")
            return 2
        rules = ["UserClose"] if expected == "reading" else RULES
        # TLC reports only the first rule a state breaks, so each rule runs on its own.
        broken, states, secs, text = set(), 0, 0.0, ""
        for r in rules:
            b, s, t, x = run(variant, keep, cap, steps, [r])
            secs += t
            if b in (None, "error"):
                broken, text = b, x
                break
            broken |= b
            states = max(states, s)
            if b:
                (traces / f"{variant}-KeepFirst{keep}-Cap{cap}-{r}.txt").write_text(x, encoding="utf-8")
        spent += secs
        label = f"{variant:<8} KeepFirst={keep!s:<5} Cap={cap}"
        if broken in (None, "error"):
            print(f"BAD {label} {broken or 'timeout'}")
            if broken == "error":
                print(text[-2000:])
            bad += 1
            continue
        if expected in (None, "reading"):
            print(f"?   {label} {', '.join(sorted(broken)) or 'nothing'} broken ({' '.join(rules)}) states={states} {secs:.1f}s")
        else:
            ok = broken == expected
            bad += not ok
            print(f"{'ok ' if ok else 'BAD'} {label} broken: {', '.join(sorted(broken)) or 'none'} (expected {', '.join(sorted(expected)) or 'none'}) states={states} {secs:.1f}s")
    print(f"MaxSteps={steps}; {spent:.0f}s; {bad} unexpected")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
