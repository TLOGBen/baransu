# Bounds — how each kind raises what is proven and lowers what is best possible

SKILL.md §3's table names a method per cell. This file holds, for each method, the theorem behind it, what it gives — **P** raises the proven bound, **B** lowers the best possible, **U** turns "within scope" into "proven" — its premises, and the name it goes by in the literature, so it can be looked up. Read the section of the kind §3 named. A method whose premise is not shown gives no bound; the premise goes to §4 as a question, and an unmet one is said in the report.

## For every kind

- **Relaxation.** Enlarge the feasible set, or replace the objective by one never worse on it: the relaxed optimum bounds the original. B. Premise: the enlarged set really contains every allowed answer — "fewer actors" and "knowing the future" are relaxations only once that containment is shown.
- **Weak duality.** Any dual-feasible point bounds every primal-feasible one. B, and a certificate a person can recheck. Premise: dual feasibility checked in exact or safely rounded arithmetic (Neumaier–Shcherbina safe bounds); a floating-point "feasible" may not be.
- **Strong duality, complementary slackness.** For a linear program with a finite optimum, the dual optimum equals the primal; a primal–dual pair satisfying complementary slackness is optimal. P = B. Premise: linear, or convex with a constraint qualification (Slater); integer programs in general keep a duality gap.
- **Lagrangian relaxation.** Move hard constraints into the objective with multipliers λ ≥ 0; every L(λ) bounds the optimum, and the best λ gives the bound of the convex hull of the easy part intersected with the hard constraints (Geoffrion 1974). B, usually tighter than the plain linear relaxation.
- **Integrality gap.** The worst ratio, over all instances, between a relaxation and the integer optimum: no rounding of that relaxation proves a better ratio. On one instance, a gap between the relaxation and the best answer found is closed by a stronger relaxation (cuts, Lagrangian, a semidefinite one) or by branch-and-bound raising the bound — never by searching for better answers alone.
- **Certifying algorithm.** The algorithm outputs a witness — dual values, a cut, a counterexample — that a small checker verifies (McConnell–Mehlhorn–Näher–Schweitzer 2011; VIPR certificates for mixed-integer programs, Cheung–Gleixner–Steffy 2017). Trust the checker, not the solver.
- **Tightness of an asymptotic ratio** needs a family of cases that approaches it; one case shows only that instance.

## Order

- **Explicit-state model checking** (TLC): every reachable state within the constants. P within scope; one violating trace refutes.
- **Inductive invariant.** Init ⇒ Inv, Inv ∧ Next ⇒ Inv′, Inv ⇒ P: P holds in every reachable state, at any length. U. TLC checks inductiveness for fixed constants (start from Inv over bounded type sets); TLAPS proves it for every constant; Apalache checks it with SMT. Finding Inv is the hard part; candidates can be inferred on small instances (endive, Ivy, I4).
- **k-induction, IC3/PDR.** Automatic proofs or counterexamples for finite-state systems; no ready IC3 tool exists for TLA+.
- **Cutoff theorems.** For some classes — identical processes on a token ring, guards with existential or universal conditions, finite data, properties indexing a fixed number of processes — checking up to c copies settles every n (Emerson–Namjoshi 1995, Emerson–Kahlon 2000). U within the class; parameterized verification is undecidable in general (Apt–Kozen 1986).
- **Symmetry reduction** shrinks a fixed scope and never extends it; TLC's SYMMETRY is sound only for safety.
- **Small-scope hypothesis** (Jackson): most bugs show in small scopes. An observation that makes a scoped result worth having, never a proof.
- **Trace validation.** A recorded run checked as a behaviour the spec allows (Cirstea–Kuppe–Loillier–Merz 2024). It finds divergence between model and code and proves nothing; use it when the two may disagree, not as the table's calibration — it sees only the runs recorded.
- **Impossibility under the same assumptions.** Deterministic consensus with one possible crash in a fully asynchronous system cannot be guaranteed (Fischer–Lynch–Paterson 1985; escaped by randomisation, partial synchrony, failure detectors); Byzantine agreement needs n ≥ 3f + 1 with unsigned messages, and under partial synchrony even with signatures (Lamport–Shostak–Pease 1982; Dwork–Lynch–Stockmeyer 1988), while a synchronous system with signatures tolerates any f (Dolev–Strong 1983); synchronous crash consensus needs f + 1 rounds in the worst case; linearizability and availability under partition cannot both hold (Gilbert–Lynch 2002). B, with each result's premises.
- **Indistinguishability.** Two executions a process cannot tell apart force the same action; built on, it constructs a schedule that defeats or slows every protocol of a class (Lynch 1996; Attiya–Ellen 2014). B: the general way to show a worst case K cannot go lower for any protocol — the K − 1 trace only shows K tight for this answer.
- **Quorums.** Safety needs any two quorums to intersect — a majority under crashes; under f Byzantine faults, an intersection of at least f + 1 when the data verify themselves (dissemination quorums) and 2f + 1 otherwise (masking quorums; Malkhi–Reiter 1998). Checked as an invariant or by counting.
- **Durations** — timeouts, leases, periodic work. A protocol with clocks goes to timed automata, where reachability is decidable by zones (Alur–Dill 1994; UPPAAL); a lease's safety rests on a bound on clock drift, which is a premise. A set of tasks on processors goes to response-time analysis: the least fixed point of R_i = C_i + B_i + Σ over higher-priority tasks j of ⌈R_i/T_j⌉C_j — exact for preemptive fixed priority on one processor with deadlines at most the periods and no blocking or jitter, a sufficient bound once blocking or jitter enter — with each C a true worst-case execution time: a measured time is a floor, never the worst (Joseph–Pandya 1986). Necessary conditions no schedule beats: utilisation at most 1, the demand bound (Liu–Layland 1973; Baruah–Rosier–Howell 1990).

## Finite scenarios, robust optimization

- **Exhaustion of a finite set** is a proof when the set is shown complete from its source; a generated set stays within scope.
- **Robust counterpart.** min over plans of the max over finitely many scenarios is one ordinary model — min z with z ≥ f(x, s) for each s — solvable with a proven bound.
- **Scenario subset.** The min–max over a subset of scenarios bounds the min–max over all of them. B, the cheapest one; adding the violated scenario one at a time is column-and-constraint generation (Zeng–Zhao 2013).
- **Clairvoyant bound.** In each scenario a plan does no better than the best plan for that scenario known in advance, so the worst is at least max over scenarios of OPT(s). B: the dispatcher who knows the future.
- **Fewer actors** is a relaxation only when every full plan restricted to the remaining actors stays valid and no worse; an actor that brings a resource breaks it.
- **Static against adjustable.** A fixed plan, a policy that reacts to the scenario, and the clairvoyant are three different questions, in that order of value.

## Optimization, several objectives

- **Solver bounds.** A branch-and-bound dual bound bounds the optimum; it holds within the solver's tolerance unless rechecked in exact arithmetic or by a certificate.
- **Combinatorial bounds** a person can check: max-flow = min-cut, König (bipartite only), the critical path, counting and pigeonhole.
- **Several objectives.** Lexicographic: each level with the levels above locked at their optimum, zero gap at each — a tolerance on one level is carried into the next. A curve: the ε-constraint method gives weakly non-dominated points; the augmented form gives non-dominated ones (Mavrotas 2009); "one step better on the earlier objective makes the later one worse" is exact only for integer objectives. The best possible of a whole curve is a lower bound set from relaxed weighted sums (Ehrgott–Gandibleux 2007).

## A guaranteed ratio

The exact optimum is out of reach because of a limit — information (decisions before the future is known), memory (one pass), or time (polynomial, for an NP-hard objective) — so a ratio to it is promised. Which limit it is decides how the ceiling is shown.

- **Proven ratio.** LP rounding: ALG ≤ α·OPT_LP ≤ α·OPT, α never below the integrality gap. Primal–dual: the algorithm also builds a dual y with ALG ≤ α·Σy — every instance carries its own bound (Williamson–Shmoys). Local ratio (Bar-Yehuda et al.). Exchange arguments; greedy is optimal for every weighting exactly on a matroid (Edmonds 1971). Monotone submodular under a cardinality bound: greedy ≥ (1 − 1/e)·OPT (Nemhauser–Wolsey–Fisher 1978), and for any set S, OPT ≤ f(S) + the k largest marginal gains with respect to S — a cheap per-instance bound (Leskovec et al. 2007). Potential functions for amortised and competitive bounds, over the whole sequence.
- **Ceiling for the class.** Deterministic online: an adversary that predicts the algorithm and builds the input (Borodin–El-Yaniv; paging k, ski rental 2). Randomised against an oblivious adversary: Yao's principle — a hard input distribution for every deterministic algorithm bounds every randomised one; for a ratio, write E[ALG] − c·E[OPT]. Memory in one pass: a one-pass algorithm with s bits is a one-way protocol, so s is at least the problem's one-way communication complexity, and divided by 2p − 1 for p passes (Alon–Matias–Szegedy 1999); one-pass monotone submodular maximization reaches 1/2 − ε, and beating 1/2 needs memory linear in n (Feldman–Norouzi-Fard–Svensson–Zenklusen 2020). Polynomial time: inapproximability unless P = NP (PCP; set cover ln n, max coverage 1 − 1/e — the value-oracle 1 − 1/e for submodular is unconditional); some rest on the Unique Games Conjecture, said when used.
- **Parameterized.** When a parameter k is small in the real data — a premise to measure — an f(k)·n^c algorithm gives the exact optimum, turning an approximation question back into an optimization one (Cygan et al. 2015).
- **Sketches** give (ε, δ) guarantees — Count-Min: width e/ε, depth ln(1/δ) — with hashes from a pairwise-independent family chosen independently of the input; an adaptive input can break a linear sketch.
- **Smoothed and average analysis** bound the expected cost under a stated perturbation or distribution; they belong to Probability, never to the worst case.

## Equivalence

- **What "the same" means** decides the judge. Trace equivalence keeps every safety property but not deadlock under interaction; failures equivalence adds what each side refuses after each trace; bisimulation keeps every branching property and may reject a correct refactor (Milner; van Glabbeek 2001). For a deterministic program, comparing inputs with outputs and the sequence of effects is enough. When the new version may be more deterministic, the claim is refinement — Impl ⇒ Spec through a state mapping, with history or prophecy variables when needed (Abadi–Lamport 1991) — not equality.
- **Proven per change.** Translation validation of this pair (Necula 2000); a bounded check of old ≠ new being unsatisfiable (CBMC, Kani) is complete for the type only when every unwinding assertion passes, otherwise within the unwinding.
- **Within scope → proven.** Regression verification: match the two versions' functions, prove each body equal assuming their calls equal, by induction on depth — partial equivalence, termination shown apart (Godlin–Strichman 2013; REVE, SymDiff). A product program turns equivalence, or noninterference — one program on two inputs differing only in a secret, a 2-safety property — into one program's safety (Barthe et al.). Differential testing only refutes.

## Every input

- **Deductive verification** (Dafny, Verus): preconditions, loop invariants and termination measures prove the property for every input; every `assume`, axiom and trusted item is part of what is trusted and is listed.
- **Bounded model checking** (Kani, CBMC): complete when every unwinding assertion passes, otherwise within the unwinding. Contracts or k-induction turn a bounded proof unbounded.
- **Vacuity.** Assumptions that exclude every input make anything hold; a cover check (`kani::cover!`) shows inputs remain.

## Complexity

- **Proven:** counting, a recurrence, a potential for amortised cost — under a stated cost model; tight by an input family that attains it.
- **Best possible**, always in a stated model of computation: decision-tree counting (comparison sorting needs log₂ n! — broken on the word RAM), an adversary argument, a reduction, a conditional bound under SETH, 3SUM or APSP, cell-probe bounds for data structures, and always the size of the input plus the output.
- **Measured slopes** on worst-case inputs (searched for when unknown) refute "is O(f)" and never prove it.

## Two documents, and a split too big for one model

- **Refinement.** One document refines another when each of its behaviours, mapped, is a behaviour of the other (Lamport, *Specifying Systems* ch.10).
- **Composition.** Parts' proofs combine by assume–guarantee: each part guarantees G_i assuming A_i, the others' guarantees imply A_i, and a circular argument is cut by induction — directly sound for safety only. Parts' best possibles add up only for a separable objective; a coupled split's best possible comes from its coordination, a Lagrangian dual (`../../_shared/optimization.md` §2 steps 3 and 6).

## Probability

- **Exact probability** on a Markov chain or decision process, worst over every resolution of the nondeterminism (PRISM, Storm), with sound or interval iteration — plain value iteration can stop far from the value. P.
- **Concentration.** Chernoff and Hoeffding for independent sums, Azuma for martingales with bounded differences. P, with the independence or martingale premise shown.
- **Best possible:** Yao's principle, counting and birthday bounds.
- **Statistical model checking** fixes a sample size by Hoeffding or Clopper–Pearson for error ε at confidence 1 − δ: within scope, with that confidence, never proven.

## Numerical error

- **Standard model.** fl(x op y) = (x op y)(1 + δ), |δ| ≤ u, expanded through the computation; FPTaylor and Gappa give a sound bound over an input range with a certificate (Higham 2002; Solovyev et al. 2019). P. Premise: no overflow or underflow, and the build's flags — fast-math, FMA contraction, extended precision — are part of the claim.
- **Best possible:** the correctly rounded result, half an ulp, which higher working precision can reach even for an ill-conditioned function; when the inputs are themselves known only to working precision, the condition number times the unit roundoff, which a backward-stable algorithm reaches within a constant.
- **Eigenvectors** and other computed subspaces move with perturbation by the Davis–Kahan sin θ theorem.

## A domain across kinds: clustering

A domain is not a kind. Clustering spreads over five rows, and each method goes where its question is:

| Question | Row | Proven | Best possible |
|---|---|---|---|
| k-center, small instance or the best answer | Optimization | exact optimum by integer programming | k + 1 points pairwise more than 2r apart show OPT > r — a certificate checked by hand |
| k-center, any instance | A guaranteed ratio | farthest-first (Gonzalez 1985) or Hochbaum–Shmoys 1985: 2; the (k + 1)-th farthest distance d gives ALG ≤ d and OPT ≥ d/2 on every instance | no polynomial (2 − ε) unless P = NP (Hsu–Nemhauser 1979); needs a metric |
| k-median, facility location | Optimization; A guaranteed ratio | local search 3 + ε; k-median 2 + ε (Cohen-Addad et al. 2025); facility location 1.488 (Li 2013), primal–dual 3 with its dual (Jain–Vazirani 2001) | 1 + 2/e for k-median (Jain–Mahdian–Saberi 2002), 1.463 for facility location (Guha–Khuller 1999); per instance, the linear relaxation or the primal–dual's dual |
| k-means with Lloyd | Optimization | only the value reached — a local optimum, no ratio; exponentially many rounds in the worst case (Vattani 2011), polynomial under smoothing | the Peng–Wei semidefinite relaxation bounds OPT on the instance, and is exact on well-separated data; exact solvers (column generation, SOS-SDP branch-and-bound) calibrate and can close the gap at moderate size |
| k-means++ seeding | Probability | E[cost] ≤ 8(ln k + 2)·OPT — an expectation, not every run (Arthur–Vassilvitskii 2007) | APX-hard in high dimension (Awasthi et al. 2015); NP-hard already for k = 2 |
| single linkage | Optimization | cutting the k − 1 longest minimum-spanning-tree edges maximizes the smallest gap between clusters, exactly (exchange argument; single linkage is Kruskal's merge order) | equal to proven: gap zero |
| hierarchical clustering beyond single linkage | A guaranteed ratio, once an objective is named | average linkage 1/3 for the revenue objective (Moseley–Wang 2017); complete linkage O(log k) for the diameter objective in fixed dimension (Ackermann–Blömer–Kuntze–Sohler 2014); a top-down sparsest-cut algorithm O(√log n) for Dasgupta's cost | no constant for Dasgupta's cost under small-set expansion; with no objective named, there is no best possible to state |
| DBSCAN against its definition | Equivalence | brute force over the core-point graph as reference; border points depend on processing order, so a claim of a unique result is checked — DBSCAN* treats them as noise | the definition itself; speed in d ≥ 3 has a Hopcroft-type lower bound, and a ρ-approximate version runs in O(n) (Gan–Tao 2015) |
| spectral clustering | A guaranteed ratio, Numerical error | Cheeger, with λ₂ of the normalized Laplacian: the sweep cut of the second eigenvector has conductance ≤ √(2λ₂); k-way conductance is bounded the same way by higher-order Cheeger (Lee–Oveis Gharan–Trevisan 2014) | λ₂/2 ≤ the least conductance — one theorem gives both bounds; recovering the clusters themselves needs an eigengap premise measured in §4 (Peng–Sun–Zanetti 2017) |
| correlation clustering | Optimization; A guaranteed ratio; Probability | pivoting at random: 3 in expectation (Ailon–Charikar–Newman 2008); 1.73 with a stronger relaxation (Cohen-Addad et al. 2023) | APX-hard on complete graphs; the standard linear relaxation's integrality gap is 2, so no analysis of it alone goes below 2 |
| streaming or coreset clustering | A guaranteed ratio (memory) | a coreset keeps every set of centres' cost within 1 ± ε; merge-and-reduce makes it streaming; an α-approximation on a (1 ± ε) coreset gives about α(1 + ε)/(1 − ε) — carry the error through | memory lower bounds by communication complexity, with the class stated |

Two clustering facts sit outside the bounds. **Kleinberg's impossibility** (2002): no clustering function has scale-invariance, richness and consistency together — rules that cannot all hold, raised at §2: fixing k gives up richness, and single linkage with fixed k is then characterised by axioms of this kind (Zadeh–Ben-David 2009). **Stability assumptions** — perturbation resilience, separation conditions — make some algorithms provably near-optimal; they are premises about the input class, settled in §4, usually 假設, and the argument names them as the class it holds for.
