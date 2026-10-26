---
name: hypothesis
description: "Use when a part of a system, a plan, or a document must not go wrong in any order or for any input and tests cannot reach the case — a race, a retry, a multi-step state, money, a permission, an irreversible effect, a schedule or plan that must be the best possible, a result needed under a time or memory limit, two documents that must agree, or code before and after a refactor that must behave the same. Trigger On '/hypothesis', '假說', '證明所有順序都不會壞', '最壞情況', '這個模組不能出錯', '文件有沒有矛盾', '是否滿足', '最佳化', '重構前後等價', 'model-check this'. Not for finding the cause of a failure (/hunt) or replaying on the real app (/prove-it)."
---

# hypothesis — define good, bound it from both sides, close the gap

A hypothesis hands a person a conclusion they can act on, true of the thing they will use, with exactly the evidence that makes it trustworthy. It gets there one way. First it writes what good means — **the ideal**, in the person's terms. Then it keeps two bounds on it, both named toward good: **what is proven** — what this answer is proven to give, raised as the work goes on — and **what is best possible** — what no answer allowed by the rules can beat, lowered as the work goes on; when some answer reaches the ideal, the ideal is the best possible. The distance between them is the gap: room to improve when a better answer is known, or what is not yet known when neither bound is shown tight. The report says which. The work stops when the two bounds meet, or when the gap left could not change what the person will do; the gap is then the honest answer to "how could it be better".

Every question this skill asks closes one of three ways: **proven** for every case, **refuted** by one counterexample, or **holding within a stated scope**. Time does not move a question between them. More runs of the same kind never turn "within scope" into "proven" — only an argument does — and no amount of thought rescues a claim one counterexample breaks. So the budget protects the machine; it never decides how much to do.

A worst case is the same idea: the answer's worst is proven when K holds, and shown tight when K − 1 breaks. A rule holding for every order is the proven bound reaching the ideal. An optimum is a checked answer and a proven bound with nothing between them.

For questions of order the model is written in TLA+ and checked by TLC; other kinds of question take the tool their mathematics calls for. Chasing the cause of a failure is `/hunt`'s work, replaying on the real app is `/prove-it`'s, and changing the source is separate work the hypothesis only informs.

The defaults this corrects: the model asks only how bad things can get and never how good they could be; solves before it knows what counts as correct; trusts the numbers a test or a spec states; reaches for its usual tool whatever the question is; checks the cases it thought of, and keeps checking after the answer can no longer change, as if more runs could prove what only an argument proves; lets a second opinion leak into the first; verifies a version it then keeps changing; and, once it can explain a result, bends the promise to fit it.

All user-facing output is in Traditional Chinese; identifiers, paths, model code and quoted source stay as they are. A rule is 守住 or 被打破.

## Outcome Contract

- **Outcome**: one claim with its ideal, its proven and best-possible bounds, the gap between them and what would close it, each bound backed by evidence a person can check without redoing the work, and each finding handed on to where it is acted on.
- **Done when**: the ideal and the rules were written before any answer, the rules confirmed or marked 未經確認 when no one could answer; every question in the README's tables is closed — proven, refuted, or holding within a stated scope — or left open with the reason it cannot change the verdict; the judge ran before any answer code and was calibrated; the answer was frozen and §6 ran on it, the sealed second derivation opened only there; the README holds the ledger, the coverage, the version and both commands; no background process of this run is left.
- **Evidence**: each question's evidence — the judge's and `model/check.py`'s output on the frozen answer, the arguments, the checks that said no, the second derivation's comparison — and the hashes recorded at freezing.
- **Output**: a Traditional Chinese report in the conversation and `.claude/hypothesis/<area>/` (README, `model/`, `variants/`, `paths/`), never archived by `/ship`; no product code edited.
- **Automation**: ultracode=neutral, loop=assisted（the one stop is §2's confirmation; without a person the run goes on with the rules as written and marks the report 未經確認 — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）
- **Telemetry**: on invocation, append one selection record per `../_shared/selection-telemetry.md`.

PAUSE classification for non-interactive drivers: `references/loop-pauses.md`.

## When

Only on a part that is hard and hard to test — rows H1–H8 in `references/model.md`. A claim one run settles, a single sequential path, look and copy: not a hypothesis; say so in one line and leave it to red/green (`../_shared/tdd.md`). When the request is broad, choose the claim where a break harms people most and tests reach least, and say why.

## The ledger

The README (`templates/README.md`) is the only work list. Its head holds the ideal, the two bounds and the gap. Its tables hold every question whose answer could move a bound or change the verdict: the rules in the rules table, the premises in the premise table, the readings in the readings table, and in the ledger table only what those tables do not hold — each bound, the translation into mathematics, a larger scope. Each question names the cheapest evidence that settles it and closes proven, refuted, or within a stated scope. Every run, measurement and agent of this skill answers one question; a run that answers none is not started, however much budget is left. A change to the answer reopens only the questions it touches.

## The order, and why

Each step uses only what the steps before it settled. The ideal tells §2 what the rules protect. The rules mark out what any answer may be, so they are what the best possible is taken over, and they tell §3 what kind of mathematics is being judged. The rules and the kind are all the second derivation needs, so it leaves as soon as the kind is named, sealed until §6; the kind then turns the rules into a judge that runs before any answer exists, and names how each bound is shown. The kind tells §4 which premises matter, and §4 calibrates the judge. The premises give the answer its constants. The frozen answer is what §6 verifies, and §6 is where the sealed derivation is opened. The report says only what §6 verified.

Running a step early means doing it without what it depends on: an answer found before the ideal is written becomes the ideal, a judge written after the answer copies the answer, a tool chosen before the kind fits the wrong question, a model built before measuring uses guessed numbers, a second opinion read before freezing stops being a second opinion, and a check run before freezing proves a version that is not handed over.

## 1. What good is

When the input is a `/hunt` case id, read its case file under `.claude/hunt-report/` first; the symptom's negation is the first candidate rule. Then open the README with:

- **What the person will do with the answer** — the decision behind the request, not its wording: trust a test again, run a plan tonight under real delays, publish a schedule and defend it, act on what a board shows at any moment, replace old code with new.
- **The ideal** — what good means for that decision, and how it is measured: no photo ever made twice, every train home safe and the last one parked as early as possible, every requested day off granted and nobody on six days in a row, the board's ten worth as much as the best ten. Say it as the person would; a number when one exists.
- **The claim, with its quantifier** — for every order, for every input, at every moment, there exists an example, the two versions agree, or this is the best. The quantifier decides how the bounds are shown in §3: one example settles "there exists"; "for every" needs every case within a stated scope, or a proof; "the best" needs a bound that meets the answer.
- **The bounds, unknown** — the questions that would settle what is proven and what is best possible go in the ledger table.

## 2. The rules, before any answer

Write what a correct answer must satisfy before solving, modelling, or explaining anything; rules written first come from the domain, rules written after come from the solution. The rules mark out every answer allowed, so the best possible is taken over them.

- **Promises are rules.** A promise is anything its owner wrote down: a spec, a contract, a doc comment, and a test — what a test asserts and what its comment says it guards. What a test or comment assumes about how the system runs — a duration, a number of workers, that its inputs differ, slack added to a limit — is a premise for §4, never a rule.
- **The document is not always the highest owner.** Ask once whether a law, a regulation, a safety rule or a contract above it constrains the same thing — a document that cites one law is a hint that others apply. List each as a rule with its source, or as a question when you cannot confirm it.
- **Readings that change the verdict.** Wording that allows more than one meaning becomes a question naming who can answer it, in the readings table. When two readings would change the verdict, both are checked later and both verdicts reported. The answer handed over follows the reading its owner would sign — the one a higher rule requires, otherwise the document's own wording — and the answer under each other reading is delivered beside it.

Write each rule in plain words — 不能發生, 終究會發生, or 做得到 — with no variable names, quoting its owner and location. Show the person once what this part does, in the smallest picture that makes it clear, then the ideal, every rule, every question, and every part you will not model with its reason. Wait for their confirmation; this is the one stop of a first run. When no one can answer — a run nobody is watching — go on with the rules as written, check both readings of every open question, and mark the report 未經確認.

## 3. What kind of mathematics it is, and its judge

Write one line naming the kind, and when a question mixes kinds, which part is which (a concurrent data structure is order and complexity; a streaming selector is optimization under a limit plus bookkeeping state; a plan safe under every delay and finished as early as possible is robust optimization). Check which of the row's tools are installed and run here; when one is missing, use a method of the same kind — for order, an enumerator you write that explores every order within the scope — and say which tool was missing and how to install it.

**Send the second derivation now, sealed** — a fresh agent in the background, briefed only as `references/second-derivation.md` sets out. It attacks the claim straight from the source and tries to beat the proven bound, and writes everything to one result file that stays closed until §6. Its job is the one no other check here does: to find a wrong translation of the problem into mathematics, or a better answer.

The kind turns §2's rules into a judge, names how each bound is shown, and fixes how to calibrate the judge, how to show the checks can say no, and what a finding looks like:

| Kind | Judge | Calibrate it with | Proven (raise it) | Best possible (lower it) | Show the checks can say no | A finding is |
|---|---|---|---|---|---|---|
| **Order** — actors interleave; the scheduler decides | invariants and liveness over the source's observable state, checked over a state machine (TLA+) | the observable state on one real run | every state within scope explored; the worst case K holds, shown tight by K − 1 broken | the ideal, when a variant — the source with a proposed change — reaches it in the model; beyond the scope, an argument | a broken variant of the source per rule; a goal unreachable with one transition removed | a trace |
| **Finite scenarios** — deterministic rules, inputs vary over a finite set | a simulator of the rules run on every scenario | a result the document states (a stated time, a stated outcome) | every scenario run, its result | the ideal, when some plan reaches it in every scenario; otherwise a bound no plan beats | the answer broken once per rule; each change reverted, the failure returns | a scenario and the minute or step it fails |
| **Robust optimization** — safe in every scenario, and the worst scenario as good as possible | the finite-scenarios simulator; the objective is the worst over all scenarios | as finite scenarios | the answer's worst over every scenario | a relaxation — fewer actors, a dispatcher who knows the future — that no plan can beat | as finite scenarios, and the best possible one step better found infeasible | a scenario, or the relaxation's argument |
| **Optimization** — the best choice under constraints (`../_shared/optimization.md`) | a checker of every constraint and the objective | a small instance with a non-trivial answer known by brute force | the answer's value, checked | a dual, a solver's proven bound, a structural bound a person can check by hand | the answer broken once per rule; a valid but worse answer refused as best; each constraint dropped to see which ones bind | an instance or a counting argument |
| **Several objectives** — ranked, or traded against each other | the checker, returning the objective vector | as optimization | each level's value with the levels above it locked; each point on the curve | each level proven with no gap; each point a turning point — the earlier objective one step better makes the later one worse or infeasible | as optimization, per level and per point | a point and what it costs |
| **Optimization under a limit** — one pass, an answer at any moment, a budget per item: an NP-hard objective approximated because the limit forbids solving it | the objective, the resource bound per step, and the required ratio, checked on each instance against a relaxation bound | an exact optimum on small or sampled instances (a sample, not a guarantee) | the proven ratio, its lemmas checked as the code runs; the measured worst against the relaxation | the ceiling no algorithm under the same limit can beat | mutants caught by the proof's intermediate steps, not only by the final ratio | an arrival order and the step a lemma fails |
| **Equivalence** — old and new code must behave the same | the same inputs run through both, comparing every observable: return values, errors, writes, calls out, and their order | a behaviour difference planted in the new version is caught | per change: a mechanical transformation or a bounded equivalence check (proven); otherwise recorded and generated inputs, with their coverage (within scope) | equal on every input | a planted difference caught | an input and the first observable that differs |
| **Every input** | a verifier on the code | a known-answer case | the verifier's proof | the property on every input | a planted bug caught | an input |
| **Complexity** — slow or large as input grows | the complexity bound, with outputs equal as in Equivalence | sizes small enough to compare by brute force | the class before and after, slopes measured at several sizes | a known lower bound for the problem | a deliberately slower version detected by the measured slope | a size and its measured cost |
| **Two documents** (`references/documents.md`) | one document's rules over the other's model | a passage both state the same way | every rule held within scope | the ideal — every rule held — unless a contradicting trace shows otherwise | a broken passage caught | a trace in both documents' words |
| **Too big for one model** | each part by its own kind (`../_shared/optimization.md`) | per part | each part's bounds and why they combine | per part | per part | per part |

Write the judge as code now, before any code that produces the answer exists, together with the area's `model/check.py`, whose list of runs is the questions that a run settles (§5). The judge shares no rule code with what will produce the answer; reading the answer's internal state to check a proof's lemma is a check of the proof, not shared rules — the judge declares the hooks it reads, and the answer implements them. A judge never solves the hard problem the answer exists to avoid: an exact optimum is a calibration on small instances, not the judge of every instance. A property that must hold at every size, checked only within a scope, is reported as holding within that scope.

A source with no implementation yet — a `/draft` sketch of types and signatures — is calibrated against the contract it declares, its checks say no by breaking a declared guard in the model, and every premise about how it runs is 假設.

A refactor is built elsewhere — its shape under `/draft`, each slice under red/green in `../_shared/tdd.md` — and this skill gives it the equivalence judge before the first slice, a certificate per slice, and the report of which slices are proven and which hold within scope.

## 4. What really happens

A bound is only as true as what it rests on. Before building anything, settle the premises the answer and any explanation rest on, in the README's premise table. Ask of each: how much (a duration, a count, a size, a number of workers), whether a path is taken, whether the data really differ — test data included — whether things really run at the same time, and which code is the code that actually runs. Each premise is settled one of three ways: **實測** — a run settles it, so run the program once and observe that quantity, without opening a diagnosis; **讀出** — only the code or the data settles it, so cite the file and symbol or the record; **假設** — neither, so it becomes part of the scope. Then calibrate the judge with the fact §3's row names, and fix the judge before trusting it. A premise that turns out false is often the finding; it never changes a rule.

## 5. Raise the proven bound, then freeze it

Build the model or the answer with the kind's tool, running quick checks as you go. Three aims, in this order: correct, then the smallest change, then closer to the ideal.

- **True to the source** (`references/model.md`): one step in the model is one indivisible step in the source; every part cites its source by file and symbol; every actor that can run twice at once gets two copies; the constants are the measured ones and the same as the answer handed over — when a tool forces different constants, say so in the report.
- **The smallest change.** When the answer is a change to a plan or code, change only what the claim needs; each change is a claim of its own, shown necessary by reverting it and seeing the failure return. The change lives in the model or a copy and is checked on the judge; applying it to the source is separate work after the report.
- **Closer to the ideal.** A guarantee is a floor. Budget the requirements leave unused — evaluations, memory, time — may raise the actual result above it, as long as the guarantee still holds and no change is added only for it; slack that lets the answer hold under an open reading is worth a change. When the proven bound cannot rise further, try to lower the best possible: a tighter relaxation, a sharper argument.
- **Runs come from the questions.** `model/check.py` runs the questions a run settles, each at the smallest scope that settles it — the scope where the worst case first appears, each reading once — and nothing else (`references/model.md`). A larger scope is a new question, written only when its answer could move a bound; it cannot turn "within scope" into "proven", which takes an argument. Every exhaustive run — a model checker, an enumerator, a parameter sweep, a solver on the full instance, a stress run, rendering a state graph — starts through `model/check.py`, which gives it a time limit, a memory limit and its own scratch directory, estimates from the smallest scope before a larger one, and refuses what would pass the budget (by default five minutes and a few gigabytes for the whole list). A refusal means the question is too expensive as written: say the estimate in one line and settle it another way — symmetry, a smaller scope with the reason it suffices, a proof or a bound.

Then **freeze**: record the hash of every file handed over. From here the answer handed over does not change; a report the request asks for, written after §6 because it carries §6's numbers, is hashed when it is handed over. A failure in §6 means fix, reopen the questions the fix touches, freeze again, and run those checks of §6 again.

## 6. Verify the frozen answer, and close the ledger

Every check in this step runs on the frozen answer, once, and closes a question:

- **Both bounds** of §3's row, shown on the frozen answer. Where they meet, say so; where a gap remains, give its size and whether it is room to improve or not yet known. A bound that rests on your own argument, with no source and no second reader, is reported as such.
- **Tightness**: a proven bound is reached by some case — one step better fails. When no case reaches it, keep the proven bound and say it is not shown tight.
- **The checks can say no**: §3's row, with a fixed count — each rule once, each change once. When the final property is too coarse to catch a break, check the steps the proof rests on.
- **Every condition cites its source**: list any guard in the model that does not — it is something the model made up.
- **The second derivation** (`references/second-derivation.md`): open its result file now and compare. First compare the working tree with the state noted at dispatch: anything that changed outside its directory is listed in the report, never removed — the comparison cannot tell who wrote it. A refutation it backs with steps the source takes is a model error — fix it and return to §5; one it cannot back stays a question. For an answer, give both answers to the judge: when the other one passes and raises the proven bound — a better objective, or for a guarantee a better proven bound; measured quality is reported, not compared — your answer was not the best you could prove: return to §5; when both pass and the other is no better, your claim stands; when they tie on the objective, the one with the smaller change comes first, as §5 orders, and both are delivered. After a fix it checks only what the fix touched, once, as that reference sets out; then stop.
- **The handed-over form**: the answer checked against the format and rules the request states, not only against your own judge.

The ledger is closed when every question is proven, refuted, or holding within a stated scope, or left open with the reason its answer cannot change the verdict or the person's decision.

## 7. Findings, and where they go

A finding is what §3's row says it is, written under `paths/P<n>.md` as numbered steps in the source's own words, with the harm in one sentence; a script that reproduces it stays beside it. Never weaken a rule, narrow the scope, or remove a transition to make a rule 守住. A step the real system cannot take is a model error.

Fixing is not this skill's work; the report hands each finding on and names where: replaying a path on the real app with forced order → `/prove-it` (`../prove-it/SKILL.md`); a cause not yet settled → `/hunt`; the change itself → red/green under `../_shared/tdd.md`, with each path as its first red test. When this run cannot invoke those skills, the report's next steps name them. When someone proposes a change, the same judge decides whether it keeps the claim and which bound it moves. A change that moves code another hypothesis covers does not make this run maintain that one: name it as possibly stale.

## 8. Write it down

`.claude/hypothesis/<area>/` holds `README.md` (from `templates/README.md`), `model/`, `variants/`, and `paths/`. The README opens with the claim, the ideal, the two bounds and the gap, whether its rules were confirmed or are 未經確認, what it covers (file and symbol), the version it describes, the hashes recorded at freezing, and two commands: a quick check and the full one, each with its running time; the closed ledger follows. Its pictures are Mermaid blocks. For order: the normal path with at most seven states, each next picture adding one part, the last numbering every path as `paths/` does; never the whole state graph, which grows with the states. For other kinds: the smallest picture of the answer — a timeline, a table of scenarios, a curve, the two bounds and the answer between them. That is the whole record: whoever reads it later sees whether the covered code changed since that version, and reruns the command.

## 9. Report

Plain first: each finding, path and question opens with one sentence in everyday words, then its technical layer. Pictures in the conversation — here and in §2 — use the host's inline drawing tool when it offers one, otherwise text; Mermaid stays in the README. Then:

1. **Good, and where this answer stands** — the ideal; what is proven and how (proven for every case, or within a stated scope); what is best possible and how; the gap, and whether it is room to improve or not yet known.
2. **How it could be better** — what would raise the proven bound or lower the best possible, and what each would cost; or that they meet.
3. **Each stated limit or assumption** — right, or wrong with its counterexample, the worst case among them; for documents, the contradictions, gaps and ambiguities, each counted.
4. **What the person can act on** — what §1 said they will do, in their terms, and where each finding goes next.
5. **Open** — readings that change the verdict and the answer under each, premises still 假設, constants that differ from the answer handed over, conditions in the model with no source, bounds not shown tight, questions left open and why, hypotheses possibly made stale, and 未經確認 when no one confirmed the rules.

Before handing back, stop every background process this run started. Close with one line:

「hypothesis 完成：{area}｜理想：{一句}｜已證明：{值與依據}｜最好可能：{值與依據}｜差距：{大小與性質：還能改進／還不知道，或「相遇」}（{證明／範圍內}）｜{N} 條規則，{F} 條被打破（{paths}）｜前提：實測 {m}、讀出 {r}、假設 {a}｜描述的版本：{version}」

## Keeping it in step

Invoked with `--maintain` — by a person, or by a skill that reads hypotheses when the code they cover changed — and done per `references/maintain.md`; never folded into another hypothesis's run.

## Not-for boundaries

- Finding the cause of a failure → `/hunt`.
- Replaying a path on the real app, proving work done → `/prove-it`.
- Building a refactor → `/draft` and `../_shared/tdd.md`; this skill gives it the equivalence judge and certificates.
- A claim one run settles → red/green under `../_shared/tdd.md`.
