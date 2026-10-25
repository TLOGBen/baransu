# design — solving for the cheapest design that keeps the rules

A hypothesis usually checks a design someone already chose. When the choice itself is open — which steps a lock must cover, how many retries and how far apart, which operations may share a queue — the same model can choose it: leave the choice as holes, let a proposer suggest the cheapest filling, let the model checker attack it, and turn each attack into a constraint. Correctness is never approximated and never decided by the proposer: every design is judged by the model checker, and the chosen one is published as an ordinary hypothesis under all three evidence gates. Cost is what the proposer optimizes, and its optimum comes with a certificate a reader can check by arithmetic.

## 1. Holes and cost

- **Holes** are named model constants the design leaves open (`Locked ⊆ Steps`, `Retries ∈ 1..20`). Everything else in the model is the source as it is, per `formal.md` § Strict.
- **The design space** is written as constraints on the holes before any search: what a design may be at all (a lock is one held region, so the steps it covers are contiguous; a timeout is positive). These belong in the proposer's problem and in the bound below; a bound computed without them is valid but loose.
- **Cost** is what `../../_shared/optimization.md` calls the target; this file covers the kinds a model checker must judge (a protocol, a lock, a retry policy — rows 4 and 5 there). Here it is a linear function of the holes with every coefficient labelled measured (command and output, per `../../_shared/fact-check.md`) or assumed. When two plausible costs exist (step count, estimated time), run both; a conclusion that changes between them is reported as both.

## 2. The loop

Counterexample-guided search, with a cap on rounds (default 30; a run that hits it ends as an `unformalized` record of class `out-of-scope`, naming the rounds and the time):

1. The proposer returns the cheapest filling that meets every constraint so far.
2. The model checker runs the safety rules on it, one configuration, one worker (`formal.md` § Tool adapter output).
3. A counterexample becomes a constraint, and the loop repeats; no counterexample ends it.

**Which proposer** — by the kind of hole:

| Holes | Proposer | Why |
|---|---|---|
| 0/1 (include a step, enable a guard) | integer programming (HiGHS through scipy) | exact; the same problem relaxed gives the bound in §3 |
| integers or reals, linear or not (retry count × interval, a timeout) | SMT optimization (z3 `Optimize`) | handles numeric constraints exactly; on nonlinear ones it may answer `unknown`, which ends the search as an `unformalized` record (`out-of-scope`), never as a design |

Either is used only after passing `../evals/known-answer/solver/exam.py` on the machine that runs the search; without it the result is `no-tool` (`formal.md` § Let the question choose the tool).

**Which constraint a counterexample becomes** — the strongest that is sound:

- **Monotone holes** — opening a hole only removes behaviours (covering one more step with the lock can only forbid interleavings), so a counterexample for design S is one for every design that opens a subset of S's holes. Then the constraint is 「S 沒開的洞至少要再開一個」: Σ_{h ∉ S} x_h ≥ 1. Monotonicity is a claim about the model, not about the code: check it by brute force over every design at a small bound before using this cut, and record the check.
- **Otherwise** — the safe constraint excludes only S itself (a no-good cut: at least one hole differs from S). Slower, never wrong.
- Only safety rules produce cuts. Liveness rules and goals are checked on the final design, since a design can break them by making things impossible rather than by allowing them; a final design that fails one gets a no-good cut and the loop goes back to step 1 — the next cheapest design is proposed, never the failing one published.

## 3. Optimality and its certificate

- **The optimum** is the proposer's exact optimum over the final constraints — integer programming with zero integrality gap, or z3's optimum — and, when the space is small, the same answer by brute force.
- **The bound** is the linear-programming relaxation of the final integer problem, design-space constraints included. Its dual solution `(y, w)` is the certificate: `y, w ≥ 0`, `c − Gᵀy + w ≥ 0` and `h·y − Σw` equal to the bound — anyone can check it by substitution, without solving anything.
- **Report both, and the gap.** A gap of 0 is a proof that no cheaper design exists within the model; a positive gap is reported as such (「最佳是 4，下界是 2，差距 2」) and never rounded away. A loose bound usually means a design-space constraint is missing from the relaxation, not that a cheaper design exists.

## 4. From the chosen design to a hypothesis

1. **Write the design where the source is**: if it is what the code already does, the code is the source; otherwise draw it as a `/draft` sketch (§4 of that skill) or change the code under `../../_shared/tdd.md`, so the model's parts have something to cite.
2. **Publish it as an ordinary hypothesis** of that source (`sources.md` § Code or § A sketch), the holes filled with the chosen values: seen failing, seen succeeding, seen faithful, as for any other.
3. **Keep the search** under `model/design/` (the model with holes and the search script) and in the record's `design` block (§5); the README states the chosen design, why each cheaper one fails (its counterexample in plain words), the cost model, and the gap.

## 5. Record

`hypothesis.json` gains a `design` block:

```json
"design": {
  "holes": { "Locked": "subset of {read, change, write, adopt}" },
  "space": ["the held region is contiguous"],
  "cost": { "steps": "1 per step (measured: count)", "time": "read 1, change 5, write 3, adopt 1 (assumed)" },
  "proposer": "scipy 1.18.1 HiGHS milp", "cut": "monotone (checked by brute force: 11 designs)",
  "rounds": 11,
  "chosen": { "Locked": ["read", "change", "write", "adopt"] },
  "optimum": 4, "bound": 4, "gap": 0,
  "dual": { "y": [0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 0, 1, 1, 0], "w": [0, 0, 0, 0] },
  "rejected": [ { "design": { "Locked": ["read", "change", "write"] }, "breaks": "R3",
                  "why": "畫面在鎖外更新時，另一個行程剛好寫入，畫面記下了新的時間戳卻是舊內容，之後永遠不會重讀" } ]
}
```

## 6. A worked example

A lock region in an organising operation with four steps — read the index, compute the change, write the index, update the in-memory view: two processes, rules no lost update, own change visible after the update, and 「a view whose stamp says current is current」. The loop took 11 rounds; every design that left out a step broke a rule, and the one that left out only the view update broke the third — the view takes a fresh stamp after another process's write but keeps the old content, and nothing reloads it. The chosen design locks all four steps, which is what the code already did. The relaxation without the contiguity constraint gave a bound of 2 against an optimum of 4; with it, a bound of 4, gap 0, and a dual anyone can check. Brute force over all 11 contiguous regions agreed, and monotonicity held.

## Never

Let the proposer decide correctness; publish a design the model checker has not checked; call a design optimal with a positive gap; use the monotone cut without its check.
