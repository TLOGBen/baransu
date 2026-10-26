# model — when a claim deserves a model, and what makes the model honest

## When: H1–H8

A row triggers on a signal you can point at in the code, the request, or the document — never on a keyword alone.

| # | Kind | Visible signal | Default tool | Does not trigger |
|---|---|---|---|---|
| H1 | Order and concurrency | one piece of state with ≥ 2 writers; a read, a check and a write in separate steps with no lock, compare-and-swap or transaction between them; queues, callbacks, event buses | TLA+ (TLC) | one writer in one sequential path |
| H2 | Retry, cancel, timeout | retry, timeout, cancel, resume, at-least-once delivery; "idempotent", "back as it was after a failure" | TLA+ | a timeout that only aborts a read |
| H3 | Multi-step state machine | ≥ 3 states with guarded transitions; one state field written in ≥ 2 places | TLA+ | a two-state flag toggled in one place |
| H4 | Conservation of money and quantity | amounts, balances, stock, quota, rounding; a sum that must stay equal | TLA+ for the flow; a code-level verifier for the arithmetic | a total computed once and only displayed |
| H5 | Permission | a decision on mutable state (a role changed mid-flow, a share link, tenant isolation) or composed policies | TLA+, or an SMT solver for policy logic | one static role check |
| H6 | Irreversible external effect | delete, charge, send, publish, migrate; "never twice", "only after X" | TLA+ | a dry run |
| H7 | A property of the code for every input | parser, decoder, unsafe memory, overflow, a data-structure invariant | a verifier that runs on the code (Kani, Verus, Dafny) | an input domain one test enumerates |
| H8 | The user asks, or the best or a guarantee is at stake | 「假說」「證明所有順序都不會壞」「最壞情況」「最好可能」「文件有沒有矛盾」「A 是否滿足 B」「最佳化」「重構前後等價」「機率至少」「浮點誤差」, a plan or schedule that must be the best, a result needed under a time or memory limit, a probability or an error bound that must hold, code before and after a refactor that must behave the same, "model-check this" | chosen by SKILL.md §3 | — |

## Let the kind choose the tool

SKILL.md §3 names the kind; the tool follows. For order, TLA+ with TLC: the model stands apart from the code, so the next person can rerun it, read it, and check a change against it. For finite scenarios with deterministic rules, a simulator run on every scenario is the complete check; a model checker there only re-enumerates the same scenarios. For robust optimization, the same simulator, and a model checker only on a relaxation small enough to explore — the actors that set the bound, a dispatcher free to act at any moment — to show no plan beats the bound. For optimization, a solver with a proven bound, and a checker that shares nothing with it. For a guaranteed ratio, a proof first; model checking only for the state the algorithm keeps (counts, sizes, what it may drop), never for the ratio itself. For probability, a probabilistic model checker (PRISM, Storm) or a concentration proof; simulation gives a confidence, not a proof. For numerical error, a bound tool over the input range (FPTaylor, Gappa, interval arithmetic) against a high-precision reference. For durations, timed automata (UPPAAL) for clocks in a protocol, response-time analysis for tasks on processors. For equivalence, both versions run on the same inputs with every observable compared; a bounded equivalence checker where the language has one (CBMC for C, Kani for Rust) turns a slice from within scope into guaranteed. For every input, a verifier on the code; with none for this language, say so and do not fall back to sampling. For every size, a proof; no prover is assumed installed.

An enumerator you write against the real functions may confirm a model or cover what a tool cannot express; when the tool is missing, it takes the tool's place if it explores every case within the scope.

## True to the source

- **One step is one indivisible step.** In code, a held lock, a transaction, or an atomic primitive makes a step indivisible — never a comment or a name. Steps the source does not make indivisible stay separate.
- **Every part cites its source** by file and symbol (`photo_library.py::_ThumbQueue.submit`), with a line as a hint only.
- **Constants are the measured ones** (SKILL.md §4) and the ones the answer handed over uses. A tool that cannot hold them (TLC integers are 32-bit) gets a scaled model; the report says which conclusions are about the scaled model.
- **Two copies** of every actor that can run twice at once — two workers, two tabs, two requests. When the source does not say whether an actor can run twice, check both readings.
- **Unclear source** becomes a question; when the model cannot run without choosing, check each reading and report each verdict.
- **Scope stated**: the scope, the premises marked 假設, and what is left out, each in a sentence.

## Making two bounds meet

A worst case is a proven bound shown tight. State the count as an invariant (`Redo <= K`) and raise K until it holds: K holding is what is proven, the trace that breaks K − 1 shows it tight and shows how, and the smallest K that holds is the worst case within scope. An optimum is the same idea across all answers: a checked answer proven, and a bound no answer can beat, with nothing between them. When the scope is smaller than the real case, say how the result extends to the real size and mark that as reasoning.

## TLC in practice

- Pin one worker (`-workers 1`) so a safety trace is the same on every run; liveness traces can still differ.
- Give every run its own scratch directory (`-metadir <temp>/<area>-<n>`); runs sharing the system temp directory overwrite each other's files.
- A `.cfg` cannot hold a sequence or a set of records: define the value in the model as an operator and substitute it with `CONSTANT Name <- Def`.
- One configuration per rule, per goal, and per variant: TLC stops at the first violation.
- An action that computes a large set with `LET` inside one step is slow: split it into smaller steps with a phase variable and check rules only between whole steps.
- On Windows, write `.cfg` and `.tla` files with an editor, not through PowerShell strings, which eat backticks; TLC rejects non-ASCII strings, so map source names to ASCII identifiers in the README's table.
- One command reruns every configuration — a small `model/check.py` — and prints, per configuration, held or violated, the states explored, and the seconds; take the count from the last `distinct states found` line. Its list of configurations is the README's questions that a run settles, each at the smallest scope that settles it — nothing else; a larger scope is added only as a new question whose answer could move a bound, and it never turns "within scope" into "proven". Every exhaustive run goes through it, the first one included. Before a larger scope it estimates from the smaller one's states and seconds — liveness configurations on their own, as they run several times slower — and refuses what would pass the budget for the whole list; the budget catches a wrong row, it is never a target to fill. Each run gets a time limit, a memory limit — a Java heap limit (`-Xmx`) for TLC; for other processes on Windows, which has no `ulimit`, a Job Object or a watchdog that stops the process past its limit, leaving a solver room it needs — and its own scratch directory, deleted afterwards. A check that does not grow with a scope is timed once on its smallest instance before the list is estimated. Give it a quick mode for use while building; a smaller scope can change what a rule's expected verdict is, so the quick mode lists its own expected verdicts.
- On Windows, keep each `.cfg` in the same directory as its `.tla` when you run it — TLC does not find a `-config` file in another directory — copying both into the run's scratch directory when variants live elsewhere.
