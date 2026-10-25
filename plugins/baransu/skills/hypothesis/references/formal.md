# formal — when a claim is a hypothesis, and what makes its check trustworthy

Moved from `prove-it/references/formal.md` (8.15.0) and extended. This file is the single source of the trigger list: every other skill cites H1–H8 and the not-trigger list here and never restates them.

A hypothesis is always a formal model checked by a tool. A claim that cannot be modelled is not a hypothesis: it ends with a reason record (`templates/reason-record.md`) and goes back to red/green or to `/hunt`'s conjectures.

## Triggers H1–H8

A row triggers on a signal you can point at in the code, the request, or the document — never on a keyword alone. A request naming `/hypothesis` or one of H8's phrases triggers without a signal.

| # | Category (HAZOP guide word) | Visible signal | Default tool | Does not trigger |
|---|---|---|---|---|
| H1 | Order and concurrency (before / after, as well as) | one piece of state with ≥ 2 writers (requests, tabs, background jobs, webhooks); a read, a check and a write in separate steps with no lock, compare-and-swap or transaction between them; async callbacks, queues, event buses | TLA+ (TLC) | one writer, run in one sequential path |
| H2 | Retry, cancel, timeout (more, no, late) | retry, timeout, cancel, resume, at-least-once delivery, resend; a requirement of idempotence or of "data back as it was after a failure" | TLA+ | a timeout that only aborts a read |
| H3 | Multi-step state machine (other than) | ≥ 3 states with guarded transitions (approval, order, ticket, deploy stage); one state field written in ≥ 2 places | TLA+ | a two-state flag toggled in one place |
| H4 | Conservation of money and quantity (more, less) | amounts, balances, refunds, stock, quota, points, rounding; a sum that must stay equal | TLA+ for the flow; a code-level verifier for the arithmetic | a total computed once and only displayed |
| H5 | Permission and authorization (to the wrong party) | a decision that depends on mutable state (a role changed mid-flow, a delegate, a share link, tenant isolation) or composes several policies | TLA+, or an SMT solver when the policies are logic | one static role check on one endpoint |
| H6 | Irreversible external effect (reverse impossible) | delete, charge, send a mail or message, publish, deploy, migrate data, write outside the system; "never twice" or "only after X" | TLA+ | a dry run whose skipping was seen |
| H7 | A property of the code for every input (part of) | parser, decoder, serializer, memory-unsafe code, overflow, a data-structure invariant | a code-level verifier (Kani for Rust, Verus, Dafny) | input whose whole domain one test enumerates |
| H8 | The user asks | `/baransu:hypothesis`, 「假說」「先建立假說」「這個模組不能出錯」「畫狀態圖給我看」「文件有沒有矛盾」「A 是否滿足 B」「SD 有沒有滿足 SA」「證明所有順序都不會壞」, "model-check this" | chosen by the question | — |

H7 in a language with no installed or known verifier ends `unformalized`, class `no-tool`, naming the verifier missing. It never falls back to property-based testing: generated inputs sample, and a hypothesis is not a sample.

## Not triggers

Even when a row's words appear, none of these is a hypothesis:

1. A claim one run settles — a single sequential path with a deterministic result.
2. A static permission check on one endpoint.
3. A claim about look, copy, or how a text reads; a configuration value; a parameter choice. A document that states rules a system must follow is a source (H8, `sources.md`), not this case.
4. A read-only query with one reader.
5. A target already covered by a hypothesis making the same claim, whose state is `established` — rerun it instead. A different claim about the same source (a comparison against another document, a new rule) is a new hypothesis. Decide this from `scripts/hypothesis-status.py --files <target>`, never from memory.
6. A prototype the user says will be thrown away.

A declined match is written as one reason record, class `non-trigger`, naming the row, in the output of whoever declined (this skill, `/hunt`).

## Let the question choose the tool

- Can steps happen in a bad order? A model checker over a small model of the design or the code; TLA+ with TLC is the default in any language.
- Does the code itself hold for every input? A verifier that runs on the code: Kani, Verus, Dafny.
- Does an authorization composed of policies grant what it should? An SMT solver.
- Must it hold at every size, where a bound is not enough? A proof (TLAPS, Dafny, Lean); decided the first time a user asks, because no prover is assumed installed.
- Which of the possible designs keeps the rules, and which of those costs least? The model with the choice left as holes, a proposer — integer programming for 0/1 holes, an SMT optimizer for numeric ones — and the model checker as the judge, per `design.md`.

Prefer a tool the repo's developers can install and run. Say which tool and why in the README. A tool adapter is used only after it has passed a known-answer exam on a real machine — a model with a planted bug it must catch, and the fixed one it must pass. Until then the row's result is `no-tool`, never a guess. TLC passed its exam on 2026-10-24 (TLC2 2.19: a model with a planted bug was caught, and the same model without it passed). For an optimizer the exam is `../evals/known-answer/solver/exam.py`: the optimum matches brute force, the bound and its dual are reported as they are — a nonzero gap included — and an infeasible instance is reported infeasible. HiGHS (scipy 1.18.1) and z3 5.3.1 passed it on 2026-10-25.

## Tool adapter output

Every tool used must yield, for publish:

- tool name and version, and one pinned command that reruns the check — a small `model/check.py` when several configurations must run (Python runs on every OS and does not break when a checkout turns LF into CRLF); TLC stops at the first violation, so each safety or liveness rule, each goal and each variant gets its own configuration;
- the same counterexample on every run: pin the tool to one worker (TLC `-workers 1`), so a trace written into `paths/` is the one the rerun prints;
- per rule, `held` or `violated`;
- per violation, a counterexample trace whose steps map to model parts;
- the number of states or cases explored, and the seconds taken.

A tool that cannot yield one of these is not usable for a hypothesis. A tool's scratch output (TLC's `states/`) goes under the system temp dir, never into the area: pass `-metadir` or the tool's equivalent.

## Strict, every time

Each rule maps to the field that records it, so `scripts/hypothesis-status.py` enforces what can be enforced and shows the area as `draft` until it holds:

1. **True to the source** → `model_map` cites every model part (action, variable, constant) as `path:line`; for a document the line is where the passage starts, and the quoted passage goes in the part's `quote`. A variable the model adds only to state a rule — a history flag, a counter of payouts — is an observer: list it in `model_map` with `"observer": true` and the rules it serves instead of a citation, and keep it out of every guard. A fairness assumption a liveness rule needs (a worker that never stops forever) goes in `assumptions`, in plain words, citing what in the source makes it true — a scheduler that runs every worker, a retry loop that ends — and it is an item of the never-happens list (§ Strict, 7: 「X 不會永遠不發生」); a fairness added only because a liveness rule failed without it, with nothing in the source behind it, is weakening the model. What the model takes as one indivisible step is one indivisible step in the source: in code, a held lock, a transaction or an atomic primitive of the runtime makes it so — never a comment or a name; in a document, the document states it as one step. Steps the source does not make indivisible stay separate in the model. Names follow the source; where the tool cannot take them (TLC rejects non-ASCII strings), use an ASCII identifier and map it back in `model_map` and the README's table. What the source leaves unclear — a document's wording, or code whose own text and behaviour disagree — becomes a question, never a filled-in guess; when the model cannot run without choosing, run every reading the ambiguity allows and report each reading's verdict under the question.
2. **Seen failing** → `check.seen_failing`: one entry per safety or liveness rule, the broken variant under `variants/` that the check caught. A rule the source as written already breaks has its evidence in the source itself: name it as the variant (`variants/as-written.md`, or the config that checks the source). The broken source is made in a scratch copy under the system temp dir and dropped; the variant file stays in the area and in git.
3. **Seen succeeding** → `check.seen_succeeding`: every goal in `goals` reached, and unreachable once one named transition is removed. A goal the source cannot reach is not missing evidence but a finding: record it as a rule of kind `goal` with verdict `violated` and a path, and keep `goals` to the outcomes the model does reach. Every safety and liveness rule is guarded by some goal. A model that passes only because nothing can happen is rejected.
4. **Scope stated** → `check.bounds`, `assumptions`, `left_out`. An exhaustive check holds within its bounds; a request for no bounds gets a proof. Bounds give every actor the source lets run more than once at a time at least two copies — two tabs of one approver, two workers — because one copy per actor hides every race between copies; when the source does not say whether an actor can run twice at once, that is a question, and every reading is run (§ 1). The README says why each bound is enough.
5. **Findings stay findings** → a counterexample every step of which the source can take is a `path`. A step the source cannot take is a model error, fixed and said before publish, never published as a path. A broken rule's path counts as a finding only once replayed — `paths[].replay` is 證實 or 無法到達 (`../SKILL.md` §5); until then the area is `draft`. **Every edit of the model reruns everything**, whatever found the need — an item refuted by the agent or by the person, a counterexample step the source cannot take, a path `/prove-it` refutes, a difference a comparison traces to a model, a fairness assumption added: every check, all three gates (the never-happens list derived again and refuted again), and the replay of every path of a broken rule — a `replay` recorded on the old model is dropped, since the path may no longer be the same — before the area is published again.
6. **Unformalized parts recorded** → `unformalized[]`, each a complete reason record in one of the seven classes. An area with none says so in its README: 「全部形式化，沒有例外。」
7. **Seen faithful** → `check.seen_faithful`. Gates 2 and 3 test the rules and the goals inside the model; a model stricter than its source — one step where the source has two, a branch left out, a writer missed — passes both while the break it would have shown is gone, and a strict model that says 守住 is never replayed on the app. So the model's claims of impossibility are put to the source by someone who did not write the model:
   - **The never-happens list is derived, not chosen.** Every `model_map` part carries its `kind` (`action`, `variable` or `constant`). Each non-observer action gets at least one item negating its guard (「鎖空著的時候，不會有人回報 conflict」); each non-observer variable gets at least one closed-world item — who writes it (`writers`: 「只有 A、B 會改 X」) or what it can hold (`values`: 「X 只會是 {…}」); each fairness assumption gets one item (`kind: fairness`, 「X 不會永遠不發生」). The closed-world items are the ones that catch a step the model left out, which has no guard to negate.
   - **Refuted by an agent that never saw the model.** A fresh agent gets the source and the list only, with the task of finding, for each item, an order the source can take that makes it happen; it reads backwards from each write of the shared state, not from the entry points the modeller started at. On a first write the person who confirmed the rules sees the same list once the model exists and answers before publish — an Input PAUSE (`../SKILL.md` §4, `loop-pauses.md`); an unattended `--maintain` relies on the agent alone.
   - **Refuted items change the model.** Each item refuted — by the agent, or by the person — is fixed from the source, with `fixed` naming what changed, and everything reruns (§ Strict, 5). An item can also be refuted because it claims more than the model does (「一定」 where the model leaves a choice to a constant or an assumption): then the item is rewritten to say what the model says, `fixed` says so, and the rewritten item goes back to the refuter — it is never dropped.
   - **Bound to the model and the source it judged.** `model` records the hash of every file under `model/` except the check script and tool scratch output — configurations included, since one can change a constant an item relies on — and `sources` the hash of every cited source the refuter read, both copied from `scripts/hypothesis-status.py --model-hash <area>` right after the refutation — never filled in later, which would bind an old refutation to a new source. A model edit, or a source change — even one the maintainer sorts `no-effect`, since that sorting is the modeller's own judgement — shows the area as `draft` until the list is refuted again.
   Code against code (`sources.md`) keeps each side's parts and items under its `role`, so one side's list never stands in for the other's. The script enforces the record — the kinds, one `guard` item per action and one closed-world item per variable (per role), a verdict per item, a fix per refuted item, the hashes — and cannot see who wrote it: that the checker was independent is the writer's to honour, and the boundary is stated, not enforced.

## Never weaken to pass

No rule edited, no bound narrowed, no transition removed to make a rule 守住. A rule changes only under `--maintain`'s `promise-changed` outcome, with the evidence cited and old and new wording kept in `history`.
