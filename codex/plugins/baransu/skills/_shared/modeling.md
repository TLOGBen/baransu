# modeling — mathematics as the working language, plain language for people

> Shared by `$baransu:think` (the 借鏡 step and the cost-against-effect question), `$baransu:review`'s
> tests principle (a declared tolerance and the n a comparison rests on) and `$baransu:health` (the relative size index).
> Mathematics is the precise language the work is done in; the person reads one sentence.
> Cue for every user-facing line: 「對人陳述時用白話」.

## 1. Name the problem class first

Before modelling anything, ask which known problem this is an instance of — by reduction:
can the design argument be rewritten as that problem's input and output? — and whether that
class is hard. Reducing a vague argument to a named problem gives the answer's known upper
bound and the standard instrument, and it stops a search for an optimum that cannot exist.

| Shape (the sign to recognise it) | Class | What to do |
|---|---|---|
| Pick a subset that covers / fills / schedules under a budget (set cover, partition, bin packing, constrained scheduling, TSP-like routing) | NP-hard | Stop searching for the optimum by hand. Take a greedy or approximation with its bound stated (greedy set cover ≤ ~ln n × optimum; first-fit bin packing ≤ ~1.7 × optimum), or shrink the instance until exact is cheap — a small 0/1 instance is solved exactly by integer programming and proven optimal by its LP bound and dual (next row). |
| A recurrence over a prefix, an interval or a subset, and the same subproblem recurs (optimal substructure + overlapping subproblems) | Dynamic programming | Write the recurrence and the table size; cost = states × transitions per state. |
| Linear objective, linear constraints (allocation, budgets, cut sizing, rate limits) | Linear / integer programming | State variables, objective, constraints. LP is cheap; integrality makes it hard — relax and round, or keep the instance small. The relaxation's dual is a certificate of a lower bound only: the integer answer is optimal when it meets that bound (gap 0), otherwise the gap is reported. A rounded answer whose correctness a rule decides goes back to the model checker (`../hypothesis/SKILL.md` §3). |
| Order things so every dependency comes first; the longest chain (dependency ordering, release phases) | Topological order, critical path | The critical path is the lower bound on sequential steps; everything off it is slack. |
| Who gets what, how much can flow, the shortest route (assignment, capacity, routing) | Matching, max-flow / min-cut, shortest path | Polynomial and exact — never approximate what the standard algorithm solves. |
| "Is X feasible?" is monotone in X (the largest batch that still fits, the smallest timeout that still passes) | Binary search on the answer | log₂(range) feasibility checks instead of a sweep. |
| A handful of items (subsets of ≤ ~20, permutations of ≤ ~8) | Brute force | Enumerate; no ceremony. |

One line in the stance names the class and its bound; a problem that fits none is modelled
directly in §2. When the request is to optimize something — faster, smaller, fewer, cheaper — or a model
written under §2 shows a cost the user named, go to `optimization.md` (its §2 starts from that
model) and name the kind first; that file owns the instrument, the proof and the
correctness re-check for each kind.

## 2. Write the model

Trigger: the question carries a quantity — cost against effect, capacity, rate, probability,
ordering, sample size, tolerance. Then write, in this order: variables (with units);
objective; constraints; which inputs are measured (command and quoted output, per
`fact-check.md`) and which are assumed; solve or bound; sensitivity (which input moves the
answer most, and by how much); and the number set beside the decision it changes. No quantity
→ one line saying so, and stop. A model with no decision to change is decoration.

Catalogue — the formula, and when it applies:

- **Three-point estimate**: E = (O + 4M + P) / 6, σ = (P − O) / 6. For any size the user
  insists on hearing as a number; σ is the point — report E ± σ, never E alone.
- **Expected cost**: Σ pᵢ × impactᵢ over the failure modes the attack named. Rank
  mitigations by the expected cost each removes per unit of cost it adds.
- **Break-even**: fixed cost ÷ saving per unit = the volume at which the investment pays;
  below it the minimal alternative wins.
- **Rule of three**: n clean trials with zero failures bound the failure rate at p < 3/n
  (95%). Ten fresh inputs with no difference bound the miss rate at 30%, not at zero —
  always say which n the claim rests on.
- **Median of N against the noise floor**: an improvement is real only when it exceeds the
  spread of repeated runs; take the median of N ≥ 5, report the spread; one timing is an
  anecdote.
- **Little's law**: L = λ × W (items in the system = arrival rate × time in the system).
  Queue depth, concurrency and latency are one equation: fix two and the third is forced.
- **Relative vs absolute tolerance**: numbers agree when |a − b| ≤ max(abs, rel × |b|).
  Relative for magnitudes, absolute near zero; a relative tolerance above 1%, or an absolute
  one wider than the last printed digit, is a different result, not rounding. Every tolerance
  carries a `why`.
- **Blast radius** = sites × centrality × boundary: sites counted by a command
  (`fact-check.md`), centrality the callers that reach it, boundary 1 inside one module and
  larger when the change crosses modules (state the factor). Ranks deltas and fixes; a site
  count alone ranks nothing.
- **Rewrite signal** = touched sites ÷ tree size. The share says whether a move keeps the
  code or replaces it, whatever the move is called; the share of sites needing judgment is
  secondary and never the gate.
- **Relative size index** = 2.94 × KSLOC^1.10, with KSLOC measured one way for every system
  compared. Orders systems or modules against each other and nothing else — never a
  timeline, a cost or a headcount.

## 3. Present in plain language

The model is the working language, not the presentation language. To the person: one
sentence per number saying what it means and which decision it changes, in Traditional
Chinese, the English term explained at first use. The equation, the derivation and the
sensitivity go in the plan file (Approach) or in one appendix line, never in the headline;
show the derivation when asked, not before.

Before: 「以 n=10 套用 rule of three，miss rate 上界 p<0.3（95% CI），建議提高 n。」

After: 「十筆新輸入都沒差異，只能說漏網率不超過三成；要說『幾乎不會漏』，大約要一百筆。這決定的是：再跑一輪，還是接受這個上界。」（附錄：rule of three，p < 3/n，n=10。）
