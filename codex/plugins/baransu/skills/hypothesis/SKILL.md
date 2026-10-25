---
name: hypothesis
description: "Use when a part of a system, a plan, or a document must not go wrong in any order or for any input and tests cannot reach the case — a race, a retry, a multi-step state, money, a permission, an irreversible effect, a schedule or plan that must be the best possible, a result needed under a time or memory limit, two documents that must agree, or code before and after a refactor that must behave the same. Trigger On '$baransu:hypothesis', '假說', '證明所有順序都不會壞', '最壞情況', '這個模組不能出錯', '文件有沒有矛盾', '是否滿足', '最佳化', '重構前後等價', 'model-check this'. Not for finding the cause of a failure ($baransu:hunt) or replaying on the real app ($baransu:prove-it)."
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

# hypothesis — a claim, a judge written first, and a certificate

A hypothesis establishes one claim: that something holds in every order, for every input, at every moment, that two versions behave the same, or that an answer is the best there is. It writes the rules a correct answer must satisfy before any answer exists, turns the question into the mathematics it really is, builds a judge that runs, and hands back a certificate a person can check without redoing the work. For questions of order the model is written in TLA+ and checked by TLC; other kinds of question take the tool their mathematics calls for. Chasing the cause of a failure is `$baransu:hunt`'s work, replaying on the real app is `$baransu:prove-it`'s, and changing the source is separate work the hypothesis only informs.

The defaults this corrects: the model solves before it knows what counts as correct, trusts the numbers a test or a spec states, reaches for its usual tool whatever the question is, checks the cases it thought of, lets a second opinion leak into the first, verifies a version it then keeps changing, and — once it can explain a result — bends the promise to fit it.

All user-facing output is in Traditional Chinese; identifiers, paths, model code and quoted source stay as they are. A rule is 守住 or 被打破.

## Codex Port Adapter - Request User Input Gate

Codex can expose the structured `request_user_input` runtime tool. In Default mode it is currently gated by `[features] default_mode_request_user_input = true`; a skill cannot enable that user configuration itself. The rules an answer is held to are the owner's to agree, so use the strongest gate available in the current runtime.

When `request_user_input` is exposed, call it once at §2's confirmation — every rule, every question, and every part left out — then wait for the structured answer before continuing. When it is unavailable, present the same content as plain numbered text and stop until the user answers. When no one can answer, follow §2: go on with the rules as written, check both readings of every open question, and mark the report 未經確認 (`references/loop-pauses.md`).

## Codex Port Adapter - Fresh Agent for the Second Derivation

`spawn_agent` inherits the parent's conversation by default. The second derivation of §2 must not see this run's model, answer or reasoning, so spawn it with `fork_turns="none"` and hand it only what §2 lists.

## Outcome Contract

- **Outcome**: one claim established or refuted with a certificate a person can check without redoing the work, its rules written before any answer, and each finding handed on to where it is acted on.
- **Done when**: the rules were confirmed, or marked 未經確認 when no one could answer; the kind is named and its judge ran before any answer code and was calibrated; the premises are 實測, 讀出 or 假設; the answer was frozen and §6 ran on it once, the sealed second derivation opened only there; the README holds the claim, coverage, version and both commands; no background process of this run is left.
- **Evidence**: the judge's and `model/check.py`'s output on the frozen answer, the checks that said no, the second derivation's comparison, and the hashes recorded at freezing.
- **Output**: a Traditional Chinese report in the conversation and `.codex/hypothesis/<area>/` (README, `model/`, `variants/`, `paths/`), never archived by `$baransu:ship`; no product code edited.
- **Automation**: ultracode=neutral, loop=assisted（the one stop is §2's confirmation; without a person the run goes on with the rules as written and marks the report 未經確認 — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）
- **Telemetry**: on invocation, append one selection record per `../_shared/selection-telemetry.md`.

PAUSE classification for non-interactive drivers: `references/loop-pauses.md`.

## When

Only on a part that is hard and hard to test — rows H1–H8 in `references/model.md`. A claim one run settles, a single sequential path, look and copy: not a hypothesis; say so in one line and leave it to red/green (`../_shared/tdd.md`). When the request is broad, choose the claim where a break harms people most and tests reach least, and say why.

## The order, and why

Each step uses only what the steps before it settled. The claim tells §2 what the rules are about. The rules are all the second derivation needs, so it leaves as soon as they are confirmed, sealed until §6. The rules tell §3 what kind of mathematics is being judged, and the kind turns them into a judge that runs before any answer exists. The kind tells §4 which premises matter, and §4 calibrates the judge. The premises give the answer its constants. The frozen answer is what §6 verifies, and §6 is where the sealed derivation is opened. The report says only what §6 verified.

Running a step early means doing it without what it depends on: a judge written after the answer copies the answer, a tool chosen before the kind fits the wrong question, a model built before measuring uses guessed numbers, a second opinion read before freezing stops being a second opinion, and a check run before freezing proves a version that is not handed over.

## 1. The claim, and what it is for

When the input is a `$baransu:hunt` case id, read its case file under `.claude/hunt-report/` first; the symptom's negation is the first candidate rule. Write two lines before anything else:

- **What the person ultimately needs** — the purpose behind the request, not its wording: that a test can be trusted again, that a plan runs tonight under real delays, that a schedule can be published and defended, that the answer shown at any moment is worth acting on, that the new code can replace the old.
- **The claim to establish, with its quantifier** — for every order, for every input, at every moment, there exists an example, the two versions agree, or this is the best. The quantifier decides the method in §3: one example settles "there exists"; "for every" needs exhaustive checking within a stated scope or a proof; "the best" needs a bound that meets the answer.

## 2. The rules, before any answer

Write what a correct answer must satisfy before solving, modelling, or explaining anything; rules written first come from the domain, rules written after come from the solution.

- **Promises are rules.** A promise is anything its owner wrote down: a spec, a contract, a doc comment, and a test — what a test asserts and what its comment says it guards. What a test or comment assumes about how the system runs — a duration, a number of workers, that its inputs differ, slack added to a bound — is a premise for §4, never a rule.
- **The document is not always the highest owner.** Ask once whether a law, a regulation, a safety rule or a contract above it constrains the same thing — a document that cites one law is a hint that others apply. List each as a rule with its source, or as a question when you cannot confirm it.
- **Readings that change the verdict.** Wording that allows more than one meaning becomes a question naming who can answer it. When two readings would change the verdict, both are checked later and both verdicts reported. The answer handed over follows the reading its owner would sign — the one a higher rule requires, otherwise the document's own wording — and the answer under each other reading is delivered beside it.

Write each rule in plain words — 不能發生, 終究會發生, or 做得到 — with no variable names, quoting its owner and location. Show the person once what this part does, in the smallest picture that makes it clear, then every rule, every question, and every part you will not model with its reason. Wait for their confirmation; this is the one stop of a first run. When no one can answer — a run nobody is watching — go on with the rules as written, check both readings of every open question, and mark the report 未經確認.

**Send the second derivation now, sealed.** Note the working tree's state (`git status`), then dispatch one fresh agent in the background with the plain rules, the source, a scratch directory that is the only place it may write, and §5's red line: every exhaustive run or solver run it starts goes through a runner it writes first, with a time limit and a memory limit (`references/model.md`). It derives the same thing another way: for a question of order, it tries to make each 不能發生 happen in the source; for an answer, it computes one with another method or tool. It writes everything — its answer, its numbers, its reasoning — to one result file in its scratch directory and replies only that the file is written. That file stays closed until §6; where the host returns from a dispatch only when the agent has finished, the seal is what keeps the two derivations apart. With no way to dispatch an agent, say so; the derivation is then missing, not done by you.

## 3. What kind of mathematics it is, and its judge

Write one line naming the kind, and when a question mixes kinds, which part is which (a concurrent data structure is order and complexity; a streaming selector is optimization under a limit plus bookkeeping state; a plan safe under every delay and finished as early as possible is robust optimization). Check which of the row's tools are installed and run here; when one is missing, use a method of the same kind — for order, an enumerator you write that explores every order within the scope — and say which tool was missing and how to install it.

The kind turns §2's rules into a judge, and fixes how to calibrate it, the certificate, how to show the checks can say no, and what a finding looks like:

| Kind | Judge | Calibrate it with | Certificate | Show the checks can say no | A finding is |
|---|---|---|---|---|---|
| **Order** — actors interleave; the scheduler decides | invariants and liveness over the source's observable state, checked over a state machine (TLA+) | the observable state on one real run | every state within scope explored; the worst case as K holds, K − 1 breaks | a broken variant of the source per rule; a goal unreachable with one transition removed | a trace |
| **Finite scenarios** — deterministic rules, inputs vary over a finite set | a simulator of the rules run on every scenario | a result the document states (a stated time, a stated outcome) | every scenario run; a bound and a scenario that reaches it | the answer broken once per rule; each change reverted, the failure returns | a scenario and the minute or step it fails |
| **Robust optimization** — safe in every scenario, and the worst scenario as good as possible | the finite-scenarios simulator; the objective is the worst over all scenarios | as finite scenarios | every scenario safe, and a lower bound from a relaxation — fewer actors, a dispatcher who knows the future — that some scenario reaches | as finite scenarios, and the bound one step tighter found infeasible | a scenario, or the relaxation's argument |
| **Optimization** — the best choice under constraints (`../_shared/optimization.md`) | a checker of every constraint and the objective | a small instance with a non-trivial answer known by brute force | a bound that meets the answer: a dual, a solver's proven bound, gap 0; a structural bound a person can check by hand | the answer broken once per rule; a valid but worse answer refused as best; each constraint dropped to see which ones bind | an instance or a counting argument |
| **Several objectives** — ranked, or traded against each other | the checker, returning the objective vector | as optimization | ranked: each level proven best with the levels above it locked; traded: each point on the curve is a turning point — the earlier objective one step tighter makes the later one worse or infeasible | as optimization, per level and per point | a point and what it costs |
| **Optimization under a limit** — one pass, an answer at any moment, a budget per item: an NP-hard objective approximated because the limit forbids solving it | the objective, the resource bound per step, and the required ratio, checked on each instance against a relaxation bound | an exact optimum on small or sampled instances (a sample, not a guarantee) | the proof, its lemmas checked as the code runs, the resource bound shown reached | mutants caught by the proof's intermediate steps, not only by the final ratio | an arrival order and the step a lemma fails |
| **Equivalence** — old and new code must behave the same | the same inputs run through both, comparing every observable: return values, errors, writes, calls out, and their order | a behaviour difference planted in the new version is caught | per change: a mechanical transformation, or a bounded equivalence check (guarantee); otherwise recorded and generated inputs with their coverage (within scope) | a planted difference caught | an input and the first observable that differs |
| **Every input** | a verifier on the code | a known-answer case | the verifier's proof | a planted bug caught | an input |
| **Complexity** — slow or large as input grows | the complexity bound, with outputs equal as in Equivalence | sizes small enough to compare by brute force | the class before and after, a lower bound when one is known, slopes measured at several sizes | a deliberately slower version detected by the measured slope | a size and its measured cost |
| **Two documents** (`references/documents.md`) | one document's rules over the other's model | a passage both state the same way | a contradicting trace, or every rule held | a broken passage caught | a trace in both documents' words |
| **Too big for one model** | each part by its own kind (`../_shared/optimization.md`) | per part | each part's certificate and why they combine | per part | per part |

Write the judge as code now, before any code that produces the answer exists, together with the area's `model/check.py` that every exhaustive run will go through (§5), brute-force calibration included. It shares no rule code with what will produce the answer; reading the answer's internal state to check a proof's lemma is a check of the proof, not shared rules. A judge never solves the hard problem the answer exists to avoid: an exact optimum is a calibration on small instances, not the judge of every instance. A property that must hold at every size, checked only within a bound, is reported as holding within that bound.

A source with no implementation yet — a `$baransu:draft` sketch of types and signatures — is calibrated against the contract it declares, its checks say no by breaking a declared guard in the model, and every premise about how it runs is 假設.

A refactor is built elsewhere — its shape under `$baransu:draft`, each slice under red/green in `../_shared/tdd.md` — and this skill gives it the equivalence judge before the first slice, a certificate per slice, and the report of which slices are guaranteed and which hold within scope.

## 4. What really happens

Before building anything, write the premises the answer and any explanation rest on, as a table in the README:

| 前提 | 以為 | 出處 | 怎麼確定 | 結果 |
|---|---|---|---|---|

Look for how much (a duration, a count, a size, a number of workers), whether a path is taken, whether the data really differ, whether things really run at the same time, and which code is the code that actually runs. Each premise is settled one of three ways: **實測** — a run settles it, so run the program once and observe that quantity, without opening a diagnosis; **讀出** — only the code or the data settles it, so cite the file and symbol or the record; **假設** — neither, so it becomes part of the scope. Then calibrate the judge with the fact §3's row names, and fix the judge before trusting it. A premise that turns out false is often the finding; it never changes a rule.

## 5. Build the answer, then freeze it

Build the model or the answer with the kind's tool, running quick checks as you go. Three aims, in this order: correct, then the smallest change, then the slack.

- **True to the source** (`references/model.md`): one step in the model is one indivisible step in the source; every part cites its source by file and symbol; every actor that can run twice at once gets two copies; the constants are the measured ones and the same as the answer handed over — when a tool forces different constants, say so in the report.
- **The smallest change.** When the answer is a change to a plan or code, change only what the claim needs; each change is a claim of its own, shown necessary by reverting it and seeing the failure return. The change lives in the model or a copy and is checked on the judge; applying it to the source is separate work after the report.
- **Use the slack.** A guarantee is a floor. Budget the requirements leave unused — evaluations, memory, time — may raise the actual result above it, as long as the guarantee still holds and no change is added only for it; slack that lets the answer hold under an open reading is worth a change.
- **Red line — exhaustive runs.** Every exhaustive run — a model checker, an enumerator, a parameter sweep, a solver on the full instance, a stress run, rendering a state graph — starts through `model/check.py` (`references/model.md`). The scope is the one the claim needs — the smallest that reaches the worst case and every reading — and a larger scope is run only when the claim's quantifier needs it, never to fill the budget. The budget is for the whole check (by default five minutes and a few gigabytes), not for each run: the runner runs the smallest scope first, estimates the rest from the states and seconds it saw — liveness separately, it is slower — refuses what would pass the budget, and gives each run a time limit, a memory limit and its own scratch directory that it cleans up. When it refuses, say the estimate and the risk in one line and switch to symmetry, a smaller scope with the reason it suffices, or a proof or a bound.

Then **freeze**: record the hash of every file handed over. From here the answer handed over does not change. A failure in §6 means fix, freeze again, and run §6 again.

## 6. Verify the frozen answer

Every check in this step runs on the frozen answer, once:

- **The certificate** of §3's row.
- **Tightness**: a bound you claim is reached by some case — set it one step tighter and see it fail. When no case reaches a bound you proved, keep the proven bound and say it is not shown tight.
- **The checks can say no**: §3's row, with a fixed count — each rule once, each change once. When the final property is too coarse to catch a break, check the steps the proof rests on.
- **Every condition cites its source**: list any guard in the model that does not — it is something the model made up.
- **The second derivation**: open its result file now and compare. First compare the working tree with the state noted at dispatch: anything that changed outside its directory is listed in the report, never removed — the comparison cannot tell who wrote it. For order, a refutation it backs with steps the source takes is a model error — fix it and return to §5; one it cannot back stays a question. For an answer, give both answers to the judge: when the other one passes and is better — a better objective, or for a guarantee a better proven bound; measured quality is reported, not compared — your certificate is wrong: return to §5; when they differ and both pass, the claim of best is wrong unless the objective ties. After a fix it checks only what the fix touched, once more, given the fix in plain words and the source, never your model; then stop.
- **The handed-over form**: the answer checked against the format and rules the request states, not only against your own judge.

## 7. Findings, and where they go

A finding is what §3's row says it is, written under `paths/P<n>.md` as numbered steps in the source's own words, with the harm in one sentence; a script that reproduces it stays beside it. Never weaken a rule, narrow a bound, or remove a transition to make a rule 守住. A step the real system cannot take is a model error.

Fixing is not this skill's work; the report hands each finding on and names where: replaying a path on the real app with forced order → `$baransu:prove-it` (`../prove-it/SKILL.md`); a cause not yet settled → `$baransu:hunt`; the change itself → red/green under `../_shared/tdd.md`, with each path as its first red test. When this run cannot invoke those skills, the report's next steps name them. When someone proposes a change, the same judge decides whether it keeps the claim. A change that moves code another hypothesis covers does not make this run maintain that one: name it as possibly stale.

## 8. Write it down

`.codex/hypothesis/<area>/` holds `README.md` (from `templates/README.md`), `model/`, `variants/`, and `paths/`. The README opens with the claim, whether its rules were confirmed or are 未經確認, what it covers (file and symbol), the version it describes, the hashes recorded at freezing, and two commands: a quick check and the full one, each with its running time. Its pictures are Mermaid blocks. For order: the normal path with at most seven states, each next picture adding one part, the last numbering every path as `paths/` does; never the whole state graph, which grows with the states. For other kinds: the smallest picture of the answer — a timeline, a table of scenarios, a curve. That is the whole record: whoever reads it later sees whether the covered code changed since that version, and reruns the command.

## 9. Report

Plain first: each finding, path and question opens with one sentence in everyday words, then its technical layer. Pictures in the conversation — here and in §2 — use the host's inline drawing tool when it offers one, otherwise text; Mermaid stays in the README. Then:

1. **The claim, and whether it holds** — with its certificate, and whether that is a guarantee or holds within a stated scope.
2. **The worst case** — the number and how it happens.
3. **Each stated bound or assumption** — right, or wrong with its counterexample; for documents, the contradictions, gaps and ambiguities, each counted.
4. **What the person can act on** — what §1 said they need, in their terms, and where each finding goes next.
5. **Open** — readings that change the verdict and the answer under each, premises still 假設, constants that differ from the answer handed over, conditions in the model with no source, bounds not shown tight, hypotheses possibly made stale, and 未經確認 when no one confirmed the rules.

Before handing back, stop every background process this run started. Close with one line:

「hypothesis 完成：{area}｜主張：{一句}｜{N} 條規則，{F} 條被打破（{paths}）｜最壞：{一句}｜證書：{種類}（保證／範圍內）｜前提：實測 {m}、讀出 {r}、假設 {a}｜描述的版本：{version}」

## Keeping it in step

Invoked with `--maintain` — by a person, or by a skill that reads hypotheses when the code they cover changed — and done per `references/maintain.md`; never folded into another hypothesis's run.

## Not-for boundaries

- Finding the cause of a failure → `$baransu:hunt`.
- Replaying a path on the real app, proving work done → `$baransu:prove-it`.
- Building a refactor → `$baransu:draft` and `../_shared/tdd.md`; this skill gives it the equivalence judge and certificates.
- A claim one run settles → red/green under `../_shared/tdd.md`.
