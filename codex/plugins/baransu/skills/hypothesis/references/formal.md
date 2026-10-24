# formal — when a claim is a hypothesis, and what makes its check trustworthy

Moved from `prove-it/references/formal.md` (8.15.0) and extended. This file is the single source of the trigger list: every other skill cites H1–H8 and the not-trigger list here and never restates them.

A hypothesis is always a formal model checked by a tool. A claim that cannot be modelled is not a hypothesis: it ends with a reason record (`templates/reason-record.md`) and goes back to red/green or to `$baransu:hunt`'s conjectures.

## Triggers H1–H8

A row triggers on a signal you can point at in the code, the request, or the document — never on a keyword alone. A request naming `$baransu:hypothesis` or one of H8's phrases triggers without a signal.

| # | Category (HAZOP guide word) | Visible signal | Default tool | Does not trigger |
|---|---|---|---|---|
| H1 | Order and concurrency (before / after, as well as) | one piece of state with ≥ 2 writers (requests, tabs, background jobs, webhooks); a read, a check and a write in separate steps with no lock, compare-and-swap or transaction between them; async callbacks, queues, event buses | TLA+ (TLC) | one writer, run in one sequential path |
| H2 | Retry, cancel, timeout (more, no, late) | retry, timeout, cancel, resume, at-least-once delivery, resend; a requirement of idempotence or of "data back as it was after a failure" | TLA+ | a timeout that only aborts a read |
| H3 | Multi-step state machine (other than) | ≥ 3 states with guarded transitions (approval, order, ticket, deploy stage); one state field written in ≥ 2 places | TLA+ | a two-state flag toggled in one place |
| H4 | Conservation of money and quantity (more, less) | amounts, balances, refunds, stock, quota, points, rounding; a sum that must stay equal | TLA+ for the flow; a code-level verifier for the arithmetic | a total computed once and only displayed |
| H5 | Permission and authorization (to the wrong party) | a decision that depends on mutable state (a role changed mid-flow, a delegate, a share link, tenant isolation) or composes several policies | TLA+, or an SMT solver when the policies are logic | one static role check on one endpoint |
| H6 | Irreversible external effect (reverse impossible) | delete, charge, send a mail or message, publish, deploy, migrate data, write outside the system; "never twice" or "only after X" | TLA+ | a dry run whose skipping was seen |
| H7 | A property of the code for every input (part of) | parser, decoder, serializer, memory-unsafe code, overflow, a data-structure invariant | a code-level verifier (Kani for Rust, Verus, Dafny) | input whose whole domain one test enumerates |
| H8 | The user asks | `$baransu:hypothesis`, 「假說」「先建立假說」「這個模組不能出錯」「畫狀態圖給我看」「文件有沒有矛盾」「A 是否滿足 B」, "model-check this" | chosen by the question | — |

H7 in a language with no installed or known verifier ends `unformalized`, class `no-tool`, naming the verifier missing. It never falls back to property-based testing: generated inputs sample, and a hypothesis is not a sample.

## Not triggers

Even when a row's words appear, none of these is a hypothesis:

1. A claim one run settles — a single sequential path with a deterministic result.
2. A static permission check on one endpoint.
3. A claim about look, copy, or how a text reads; a configuration value; a parameter choice. A document that states rules a system must follow is a source (H8, `sources.md`), not this case.
4. A read-only query with one reader.
5. A target already covered by a hypothesis making the same claim, whose state is `proved` or `disproved` — rerun it instead. A different claim about the same source (a comparison against another document, a new rule) is a new hypothesis. Decide this from `scripts/hypothesis-status.py --files <target>`, never from memory.
6. A prototype the user says will be thrown away.

A declined match is written as one reason record, class `non-trigger`, naming the row, in the output of whoever declined (this skill, `$baransu:hunt`).

## Let the question choose the tool

- Can steps happen in a bad order? A model checker over a small model of the design or the code; TLA+ with TLC is the default in any language.
- Does the code itself hold for every input? A verifier that runs on the code: Kani, Verus, Dafny.
- Does an authorization composed of policies grant what it should? An SMT solver.
- Must it hold at every size, where a bound is not enough? A proof (TLAPS, Dafny, Lean); decided the first time a user asks, because no prover is assumed installed.

Prefer a tool the repo's developers can install and run. Say which tool and why in the README. A tool adapter is used only after it has passed a known-answer exam on a real machine — a model with a planted bug it must catch, and the fixed one it must pass. Until then the row's result is `no-tool`, never a guess. TLC passed its exam on 2026-10-24 (TLC2 2.19, the approval model: 425 states with three violations; fixed, 78 states with none).

## Tool adapter output

Every tool used must yield, for publish:

- tool name and version, and one pinned command that reruns the check — a small script in `model/` (`check.sh`, `check.ps1`) when several configurations must run;
- per rule, `held` or `violated`;
- per violation, a counterexample trace whose steps map to model parts;
- the number of states or cases explored, and the seconds taken.

A tool that cannot yield one of these is not usable for a hypothesis. A tool's scratch output (TLC's `states/`) goes under the system temp dir, never into the area: pass `-metadir` or the tool's equivalent.

## Strict, every time

Each rule maps to the field that records it, so `scripts/hypothesis-status.py` enforces what can be enforced and shows the area as `draft` until it holds:

1. **True to the source** → `model_map` cites every model part (action, variable, constant): `file:line` for code; quoted passage plus location (file, section, page or line) for documents. One indivisible step in the source is one step in the model. Indivisible is what the code and its runtime guarantee — a held lock, a transaction, an atomic primitive — never what a comment or a name claims; a comment that claims more than the code does is a question or a path, never a merged step. Names follow the source; where the tool cannot take them (TLC rejects non-ASCII strings), use an ASCII identifier and map it back in `model_map` and the README's table. What the source leaves unclear — a document's wording, or code whose own text and behaviour disagree — becomes a question, never a filled-in guess; when the model cannot run without choosing, run every reading the ambiguity allows and report each reading's verdict under the question.
2. **Seen failing** → `check.seen_failing`: one entry per safety or liveness rule, the broken variant under `variants/` that the check caught. A rule the source as written already breaks has its evidence in the source itself: name it as the variant (`variants/as-written.md`, or the config that checks the source). The broken source is made in a scratch copy under the system temp dir and dropped; the variant file stays in the area and in git.
3. **Seen succeeding** → `check.seen_succeeding`: every goal in `goals` reached, and unreachable once one named transition is removed. A goal the source cannot reach is not missing evidence but a finding: record it as a rule of kind `goal` with verdict `violated` and a path, and keep `goals` to the outcomes the model does reach. Every safety and liveness rule is guarded by some goal. A model that passes only because nothing can happen is rejected.
4. **Scope stated** → `check.bounds`, `assumptions`, `left_out`. An exhaustive check holds within its bounds; a request for no bounds gets a proof. Bounds give every actor the source lets run more than once at a time at least two copies — two tabs of one approver, two workers — because one copy per actor hides every race between copies; the README says why each bound is enough.
5. **Findings stay findings** → a counterexample every step of which the source can take is a `path`. A step the source cannot take is a model error, fixed and said before publish, never published as a path.
6. **Unformalized parts recorded** → `unformalized[]`, each a complete reason record in one of the seven classes. An area with none says so in its README: 「全部形式化，沒有例外。」

## Never weaken to pass

No rule edited, no bound narrowed, no transition removed to reach `proved`. A rule changes only under `--maintain`'s `promise-changed` outcome, with the evidence cited and old and new wording kept in `history`.
