# /// script
# requires-python = ">=3.10"
# ///
"""Run every TLC configuration the README's questions need, with a time and memory limit each.

usage: python check.py            # every run
       python check.py NAME ...   # only these runs
Each run: its own scratch directory (deleted afterwards), -workers 1, -Xmx, a time limit; prints
expected / got / states / seconds. The whole list must fit BUDGET seconds.
"""
import os, re, shutil, subprocess, sys, tempfile, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
TIME_LIMIT = 120
BUDGET = 300
XMX = "-Xmx2g"

DESIGN = dict(LockMode='"pid"', Order='"outfirst"', GiveUpDeny="FALSE", GiveUpOn="TRUE", MaxKills="1",
              Stalls="0", WriteGuard="TRUE")
ANSWERING = {**DESIGN, "GiveUpOn": "FALSE", "MaxKills": "0"}
# The lock as adapters/codex/store.ts writes it (8.49.0): two-step reaping under a reap lock, heartbeat, write guard.
CODE = {**DESIGN, "LockMode": '"code"'}
ALL = ["C1", "C2", "C3", "C4", "C5", "C6"]
NOT_C4 = ["C1", "C2", "C3", "C5", "C6"]

# name: (constants, invariants, expected) -- expected "held" or the invariant that must break
RUNS = {
    "design":          (DESIGN, NOT_C4, "held"),
    "design-c4":       (DESIGN, ["C4"], "C4"),
    "answering":       (ANSWERING, ALL, "held"),
    "answering-plus-kill": ({**ANSWERING, "MaxKills": "1"}, ["C4"], "C4"),
    "design-c2-tight": (DESIGN, ["C2Strict"], "C2Strict"),
    "design-2-kills":  ({**DESIGN, "MaxKills": "2"}, NOT_C4, "held"),
    "design-no-kill":  ({**DESIGN, "MaxKills": "0"}, NOT_C4 + ["C2Strict"], "held"),
    "no-lock":         ({**DESIGN, "LockMode": '"none"'}, ["C1"], "C1"),
    "timeout-break":   ({**DESIGN, "LockMode": '"timeout"'}, ["C1"], "C1"),
    "no-reclaim":      ({**DESIGN, "LockMode": '"noreclaim"'}, ["C6"], "C6"),
    "write-first-c3":  ({**DESIGN, "Order": '"writefirst"'}, ["C3"], "C3"),
    "giveup-deny":     ({**DESIGN, "GiveUpDeny": "TRUE"}, ["C5"], "C5"),
    # the code's lock (README Q2, --maintain 2026-11-18)
    "code":            (CODE, NOT_C4, "held"),
    "code-c4":         (CODE, ["C4"], "C4"),
    "code-answering":  ({**CODE, "GiveUpOn": "FALSE", "MaxKills": "0"}, ALL, "held"),
    "code-2-kills":    ({**CODE, "MaxKills": "2"}, NOT_C4, "held"),
    "code-stall":      ({**CODE, "Stalls": "1"}, NOT_C4, "held"),
    "code-stall-2-kills": ({**CODE, "Stalls": "1", "MaxKills": "2"}, NOT_C4, "held"),
    "code-stall-noguard": ({**CODE, "Stalls": "1", "WriteGuard": "FALSE"}, ["C1"], "C1"),
}


def cfg(consts, invs):
    lines = ["SPECIFICATION Spec", "CONSTANTS"]
    lines += [f"  {k} = {v}" for k, v in consts.items()]
    lines += [f"INVARIANT {i}" for i in invs]
    return "\n".join(lines) + "\n"


def run(name):
    consts, invs, expected = RUNS[name]
    work = Path(tempfile.mkdtemp(prefix=f"codex-lint-{name}-"))
    try:
        for f in ("CodexHooks.tla", "CodexRules.tla"):
            shutil.copy(HERE / f, work / f)
        (work / "CodexHooks.cfg").write_text(cfg(consts, invs), encoding="ascii")
        env = {**os.environ, "JAVA_TOOL_OPTIONS": XMX}
        t0 = time.time()
        try:
            p = subprocess.run(
                ["tlc", "-deadlock", "-workers", "1", "-metadir", str(work / "meta"), "-config", "CodexHooks.cfg", "CodexHooks.tla"],
                cwd=work, env=env, capture_output=True, text=True, timeout=TIME_LIMIT, shell=(os.name == "nt"),
            )
            out = p.stdout + p.stderr
        except subprocess.TimeoutExpired:
            return name, expected, "timeout", "-", time.time() - t0, ""
        secs = time.time() - t0
        m = re.findall(r"([\d,]+) distinct states found", out)
        states = m[-1] if m else "?"
        v = re.search(r"Invariant (\w+) is violated", out)
        if v:
            got = v.group(1)
        elif "No error has been found" in out:
            got = "held"
        else:
            got = "error"
        trace = out if got not in ("held",) else ""
        return name, expected, got, states, secs, trace
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main():
    names = sys.argv[1:] or list(RUNS)
    start = time.time()
    ok = True
    for n in names:
        if time.time() - start > BUDGET:
            print(f"{n}: refused, budget {BUDGET}s spent")
            ok = False
            continue
        name, exp, got, states, secs, trace = run(n)
        mark = "OK " if got == exp else "BAD"
        ok &= got == exp
        print(f"{mark} {name:16} expected={exp:9} got={got:9} states={states:>10} {secs:6.1f}s")
        if got == "error":
            print(trace[-3000:])
        if got not in ("held", "timeout", "error"):
            (HERE / "traces").mkdir(exist_ok=True)
            (HERE / "traces" / f"{name}.txt").write_text(trace, encoding="utf-8")
    print("all as expected" if ok else "SOME RUNS NOT AS EXPECTED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
