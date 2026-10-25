"""Known-answer exam for the optimizer adapters a design search uses (references/design.md).

An adapter is used only after it passes on the machine that will run it (references/formal.md
§ Let the question choose the tool). Every expected value below is recomputed by brute force,
so the exam does not trust its own key.

  HiGHS via scipy (0/1 holes): weighted set cover. The integer optimum must match brute force;
  the LP bound and its dual must be reported as they are, a nonzero gap included; an instance
  with an element no set covers must come back infeasible from the solver itself.
  z3 Optimize (numeric holes): retry count x interval with a product constraint (nonlinear).
  The optimum must match brute force; an impossible budget must come back unsat.

usage: uv run --with scipy --with z3-solver python exam.py      (exit 0 = passed)
"""
import itertools
import sys

import numpy as np
import z3
from scipy.optimize import Bounds, LinearConstraint, linprog, milp

COVER = [  # (elements, sets, costs, expected LP-to-integer gap)
    (5, [{0, 1, 2}, {1, 3}, {2, 3}, {3, 4}, {0, 4}], [1, 1, 1, 1, 1], 0.0),
    (6, [{0, 1}, {1, 2}, {2, 3}, {3, 4}, {4, 5}, {5, 0}, {0, 2, 4}, {1, 3, 5}], [1, 1, 1, 1, 1, 1, 2, 2], 0.0),
    (3, [{0, 2}, {0, 1}, {1, 2}], [1, 1, 1], 0.5),          # vertex cover of a triangle: LP 1.5, integer 2
]
COVER_INFEASIBLE = (4, [{0, 1}, {1, 2}], [1, 1])            # element 3 is in no set

RETRY = [  # (lower bounds, upper bounds, product at least, objective)
    ((1, 1), (1000, 50), 200, "r"),        # fewest retries with interval <= 50 covering 200
    ((3, 20), (1000, 1000), 70, "r*i"),    # least total wait, at least 3 retries of at least 20
]
RETRY_INFEASIBLE = ((1, 1), (2, 50), 200)


def cover_matrix(n, sets):
    return np.array([[1 if e in s else 0 for s in sets] for e in range(n)], float)


def exam_highs():
    ok = True
    for k, (n, sets, c, want_gap) in enumerate(COVER, 1):
        m, G = len(sets), cover_matrix(n, sets)
        brute = min(sum(c[i] for i in ch) for r in range(m + 1) for ch in itertools.combinations(range(m), r)
                    if set().union(*(sets[i] for i in ch)) == set(range(n)))
        mi = milp(c, constraints=LinearConstraint(G, 1, np.inf), integrality=np.ones(m), bounds=Bounds(0, 1))
        lp = linprog(c, A_ub=-G, b_ub=-np.ones(n), bounds=[(0, 1)] * m, method="highs")
        y, w = -lp.ineqlin.marginals, -lp.upper.marginals
        dual_ok = (y >= -1e-9).all() and (w >= -1e-9).all() and (np.array(c) - G.T @ y + w >= -1e-9).all()
        gap = mi.fun - lp.fun
        passed = (abs(mi.fun - brute) < 1e-9 and dual_ok and abs((y.sum() - w.sum()) - lp.fun) < 1e-7
                  and abs(gap - want_gap) < 1e-7)
        ok &= passed
        print(f"HiGHS cover {k}: brute {brute:g} milp {mi.fun:g} LP {lp.fun:g} gap {gap:g} "
              f"dual feasible {bool(dual_ok)} -> {'pass' if passed else 'FAIL'}")
    n, sets, c = COVER_INFEASIBLE
    mi = milp(c, constraints=LinearConstraint(cover_matrix(n, sets), 1, np.inf),
              integrality=np.ones(len(sets)), bounds=Bounds(0, 1))
    caught = not mi.success and mi.status == 2           # 2 = infeasible
    ok &= caught
    print(f"HiGHS infeasible cover reported infeasible: {caught} (status {mi.status})")
    return ok


def exam_z3():
    ok = True
    for k, (lo, hi, need, obj) in enumerate(RETRY, 1):
        val = (lambda r, i: r) if obj == "r" else (lambda r, i: r * i)
        brute = min(val(r, i) for r in range(lo[0], hi[0] + 1) for i in range(lo[1], hi[1] + 1) if r * i >= need)
        r, i = z3.Ints("r i")
        opt = z3.Optimize()
        opt.add(r >= lo[0], i >= lo[1], r <= hi[0], i <= hi[1], r * i >= need)
        h = opt.minimize(r if obj == "r" else r * i)
        sat = opt.check() == z3.sat
        got = opt.model().eval(r if obj == "r" else r * i).as_long() if sat else None
        passed = sat and got == brute
        ok &= passed
        print(f"z3 retry {k}: brute {brute} z3 {got} -> {'pass' if passed else 'FAIL'}")
    lo, hi, need = RETRY_INFEASIBLE
    r, i = z3.Ints("r i")
    opt = z3.Optimize()  # the proposer design.md uses, not a plain Solver
    opt.add(r >= lo[0], i >= lo[1], r <= hi[0], i <= hi[1], r * i >= need)
    opt.minimize(r)
    caught = opt.check() == z3.unsat
    ok &= caught
    print(f"z3 impossible budget reported unsat: {caught}")
    return ok


def main():
    import scipy
    print(f"scipy {scipy.__version__} (HiGHS), z3 {z3.get_version_string()}")
    ok = exam_highs() & exam_z3()
    print("EXAM", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
