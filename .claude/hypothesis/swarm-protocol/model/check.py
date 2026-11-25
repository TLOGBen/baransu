"""Run every TLC check of the swarm-protocol hypothesis.

Each entry answers one question of the README ledger: the protocol against
the rules in a scope, or one broken variant that must be caught. Every run
gets its own scratch directory, a time limit and a JVM heap limit; a list
whose limits add up past the budget is refused.

    python check.py              # every entry
    python check.py quick        # the protocol's safety runs only
    python check.py safety1 v-noAsk
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
BUDGET_SECONDS = 3600
HEAP = "-Xmx3g"

SAFETY = ["TypeOK", "R1", "R3", "R4", "R5", "R9", "R11"]
SAFETY_PROPS = ["R2", "R10", "R12"]

ALL = '{"t1", "t2", "t3"}'

# scope -> (module, tasks, workers, late tasks, attempts per task)
SCOPES = {
    "s1": ("MC.tla", ALL, "{w1, w2}", '{"t3"}', 2),  # shared path, dependency, late task
    # three independent tasks, two seats: only asks whether questions can use up
    # every seat, which needs no second attempt (with two it passed 600 s, 11M states)
    "s2": ("MC2.tla", ALL, "{w1, w2}", "{}", 1),
    # liveness needs the smallest case of each rule: with three tasks it passed
    # 600 s (0.6M-0.8M states) because a lasso search cannot drop the step label
    "ld": ("MC.tla", '{"t1", "t3"}', "{w1}", '{"t3"}', 2),  # t3 depends on t1, added late
    "li": ("MC2.tla", '{"t1", "t2"}', "{w1}", "{}", 2),     # two independent tasks
}

# name: (scope, spec, invariants, properties, variant, expected exit, seconds, question)
RUNS = {
    "safety1": ("s1", "Spec", SAFETY, SAFETY_PROPS, "none", 0, 600, "Q1 safety, scope 1"),
    "safety2": ("s2", "Spec", SAFETY, SAFETY_PROPS, "none", 0, 600, "Q1 safety, scope 2 (seats)"),
    "live-answer-dep": ("ld", "SpecAnswer", [], ["R4live", "R6", "R7"], "none", 0, 600, "Q2 liveness, user answers, dependency"),
    "live-silent-dep": ("ld", "Spec", [], ["R4live", "R7", "R8"], "none", 0, 600, "Q2 liveness, user silent, dependency"),
    "live-answer-ind": ("li", "SpecAnswer", [], ["R4live", "R6"], "none", 0, 600, "Q2 liveness, user answers, independent"),
    "live-silent-ind": ("li", "Spec", [], ["R4live", "R8"], "none", 0, 600, "Q2 liveness, user silent, independent"),
    # each broken variant must be caught (12 = invariant, 13 = temporal or action property)
    "v-verifyNoEv": ("s2", "Spec", ["R1"], [], "verifyNoEv", 12, 120, "R1 can say no"),
    "v-workerWrites": ("s2", "Spec", [], ["R2"], "workerWrites", 13, 120, "R2 can say no"),
    "v-noPathCheck": ("s1", "Spec", ["R3"], [], "noPathCheck", 12, 120, "R3 can say no"),
    "v-wrongAwait": ("s2", "Spec", ["R4"], [], "wrongAwait", 12, 120, "R4 can say no"),
    "v-noPathWait": ("s1", "Spec", ["R5"], [], "noPathWait", 12, 120, "R5 can say no (path wait)"),
    "v-seatHeld": ("s2", "Spec", ["R5"], [], "seatHeld", 12, 120, "R5 can say no (seats)"),
    "v-noAsk": ("s2", "Spec", ["R5"], [], "noAsk", 12, 120, "R5 can say no (question never shown)"),
    "v-reportDuringJob": ("s2", "Spec", ["R9"], [], "reportDuringJob", 12, 120, "R9 can say no"),
    "v-noCap": ("s2", "Spec", ["R11"], [], "noCap", 12, 120, "R11 can say no"),
    "v-volatileReport": ("s2", "Spec", [], ["R10"], "volatileReport", 13, 120, "R10 can say no"),
    "v-waves": ("s2", "Spec", [], ["R12"], "waves", 13, 120, "R12 can say no (waves)"),
    "v-noCascade": ("ld", "Spec", [], ["R7"], "noCascade", 13, 300, "R7 can say no"),
    "v-unboundedBlocks": ("li", "SpecAnswer", [], ["R6"], "unboundedBlocks", 13, 300, "R6 can say no"),
}
QUICK = ["safety1", "safety2"]


def config(scope, spec, invariants, properties, variant):
    _, tasks, workers, late, attempts = SCOPES[scope]
    lines = ["CONSTANTS",
             f"    Tasks = {tasks}",
             f"    Workers = {workers}",
             "    None = none",
             f"    MaxAttempt = {attempts}",
             f"    LateTasks = {late}",
             f'    Variant = "{variant}"',
             "    Deps <- DepsDef",
             "    PathsOf <- PathsDef",
             f"SPECIFICATION {spec}"]
    lines += [f"INVARIANT {i}" for i in invariants]
    lines += [f"PROPERTY {p}" for p in properties]
    lines.append("CHECK_DEADLOCK FALSE")
    if spec == "Spec" and not any(p.startswith(("R4live", "R6", "R7", "R8")) for p in properties):
        lines += ["VIEW StateView", "SYMMETRY WorkerSym"]
    return "\n".join(lines) + "\n"


def run(name):
    scope, spec, invariants, properties, variant, expect, limit, question = RUNS[name]
    module = SCOPES[scope][0]
    work = Path(tempfile.mkdtemp(prefix=f"swarm-{name}-"))
    for f in HERE.glob("*.tla"):
        shutil.copy(f, work)
    cfg = f"{name}.cfg"
    (work / cfg).write_text(config(scope, spec, invariants, properties, variant), encoding="ascii")
    env = dict(os.environ, JAVA_TOOL_OPTIONS=HEAP)
    tlc = shutil.which("tlc") or shutil.which("tlc.cmd")
    start = time.time()
    log = open(work / "tlc.out", "w", encoding="utf-8")
    p = subprocess.Popen([tlc, "-workers", "1", "-metadir", str(work / "meta"), "-config", cfg, module],
                         cwd=work, env=env, stdout=log, stderr=subprocess.STDOUT, text=True)
    try:
        code = p.wait(timeout=limit)
    except subprocess.TimeoutExpired:
        # the tlc shim starts java as a child: end the whole tree, not only the shim
        if os.name == "nt":
            subprocess.run(["taskkill", "/T", "/F", "/PID", str(p.pid)], capture_output=True)
        else:
            p.kill()
        p.wait()
        code = "timeout"
    log.close()
    out = (work / "tlc.out").read_text(encoding="utf-8", errors="replace")
    secs = time.time() - start
    found = re.findall(r"([\d,]+) distinct states found", out)
    states = found[-1] if found else "?"
    verdict = {0: "held", 11: "deadlock", 12: "violated (safety)", 13: "violated (liveness)"}.get(code, f"exit {code}")
    broke = re.findall(r"(?:Invariant|Action property|Temporal properties?) (\w+)? ?(?:is )?violated", out)
    ok = code == expect
    print(f"{'OK ' if ok else 'BAD'} {name:18} {verdict:20} states={states:>11} {secs:7.1f}s  {question}"
          f"{'  ' + ','.join(b for b in broke if b) if broke else ''}  ({work / 'tlc.out'})", flush=True)
    return ok


def main():
    args = sys.argv[1:]
    names = QUICK if args == ["quick"] else (args or list(RUNS))
    total = sum(RUNS[n][6] for n in names)
    if total > BUDGET_SECONDS:
        sys.exit(f"refused: the limits add up to {total}s, over the {BUDGET_SECONDS}s budget")
    results = [run(n) for n in names]
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
