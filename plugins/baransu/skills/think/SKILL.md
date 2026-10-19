---
name: think
description: "Deliberates before building: aligns on what the user actually wants, takes a stance with its bets named, and leaves a plan under .claude/think/ — never code. Use when an idea, feature, refactor or direction is undecided, or a decision needs testing. Trigger On '/think', '想一下', '怎麼設計', '值不值得', '有沒有更好的做法', 'grill me'. Not for debugging an error (/hunt)."
---

# think — deliberate before you build

Turn a fuzzy intent into a shared statement of what the user wants, then into a position someone else can read cold and judge. Never produce code, scaffolding, config, or pseudo-code; the deliverable is a stance and, when the work deserves one, a plan file.

Two defaults this skill corrects. The model assumes the user has already thought the request through, and answers before both sides agree on what is being asked. And the model reaches for the answer that is hardest to call wrong — one more layer, one more guard, the problem quietly shrunk to the part it is sure of — instead of the answer that is right. Everything in the opening exists to close the first gap; the borrow, stance and attack sections exist to close the second.

All user-facing output is in Traditional Chinese; keep technical terms in English and explain each one where it first appears.

## Outcome Contract

- **Outcome**: A confirmed restatement of what the user wants, a stance with its bets named, and — for buildable work — a five-section plan at `.claude/think/<slug>.md`; for a verdict (Kill / Pivot) or a decision under test, the stance alone. Never code, scaffolding, or a handoff to implementation.
- **Done when**: The restatement is confirmed by the user or unchanged after a round of answers; the borrow step has run or its skip was stated; the stance is stated with its bets and answers the three named questions; every premise it leans on is tagged verified or 未實查; the attack has run for breakage and for size; the result has been presented; and, when buildable, the plan file exists and its path was reported. The turn ends there — no downstream skill is chosen and no approval gate is opened.
- **Evidence**: The confirmed restatement, the 借鏡 block (or its one-line skip), the verified / 未實查 tags with their commands and quoted output, and the plan file path (or the verdict line).
- **Output**: Traditional Chinese conversation; `.claude/think/<slug>.md` with the restatement on top and the five sections below. `/ship` archives that directory.
- **Automation**: ultracode=neutral, loop=not-drivable（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）
- **Telemetry**: on invocation, append one selection record per `../_shared/selection-telemetry.md`.

PAUSE classification for non-interactive drivers: `references/loop-pauses.md`.

## Align on a restatement, not on a solution

Open by restating, in a few sentences, what you understand the user wants: the outcome, why they want it, what must not change, and roughly how big it is (a one-off script, a long-lived feature, a core path, an edge). Fill it only from what the user actually said; mark a missing field 未知，先不問 rather than inventing it. This restatement is the object of alignment. Its job is to make your guesses visible so the user can correct them.

Every phrase in the restatement you had to guess is a candidate question. Ask it only if different answers would change the shape of the answer, not a parameter of it — whether to cache at all: ask; cache for five minutes or an hour: do not. Offer the candidate answers as different kinds, not the same direction at different strengths, and mark one as recommended. Ask one at a time unless the user prefers a batch, and say which phrase of the restatement the question fixes.

Words are guesses too. When the repo keeps a glossary (`CONTEXT.md`), write the restatement in its terms, and treat a word the user uses against that glossary, or one word that could name two things (an "account" that may be the customer or the login), as a guessed phrase like any other. Test a relationship the restatement asserts with a concrete edge case, and check what the code already does before taking either the user's or your own description of it as settled. When a term needs adding to or changing in the glossary, point to `/baransu:domain-modeling`; this skill does not edit `CONTEXT.md`.

Find facts yourself. Read the repo, docs, and prior decisions to answer any question that has an answer, and never turn research into a question for the user. Reading code to settle a fact is allowed; forming or showing a solution before the restatement is confirmed is not. During alignment the user sees exactly two things: the current restatement with the changed phrase marked, and the question.

When the user arrives with a decision already made and wants it tested (拷問我, 壓力測試這個決定, grill me), the restatement is that decision; confirm it in one round and go straight to the attack.

Alignment ends when the user confirms the restatement, or when a round of answers leaves it unchanged; then stop asking. Two exits sit here:

- If the confirmed restatement is a single-file change with one obvious fix, or a parameter choice inside a shape already settled, there is nothing to deliberate. Answer it in a line or point the user to the red/green discipline in `../_shared/tdd.md` §7; do not write a plan for it and do not run the sections below.
- If the restatement cannot fit in a few sentences because the effort has several independent destinations, say so. When the common suite's wayfinder is installed in the session (detect first, never assume), point there; otherwise say the effort needs to be charted before it can be deliberated, and stop.

## Borrow the discipline that already solved this

Most design problems are an old problem in a new costume, and the field that has lived with it longest has instruments the model will not reach for on its own. Before taking a stance, run this step with the model's own knowledge and the repo's prior art — no web research, no subagent; it is a few minutes of thinking, not a pipeline.

1. **Replace the nouns with verbs.** Restate the restatement as what it does, for whom, under what constraint: not "a notification service" but "getting a person to notice one thing among many without teaching them to ignore all of it". The verbs name the fields.
2. **Name the discipline, and the practitioner's instrument.** One or two fields or named practitioners whose standard problem this is — inside software or outside it: algorithmics (which named problem this reduces to and whether that class is hard — `../_shared/modeling.md` §1), queueing theory, double-entry accounting, cartography, aviation checklists, typography, library classification, epidemiology. For each, say the method they actually use (the instrument, the raw material they start from, the number they watch), not their vocabulary. Do what they do; never speak as them.
3. **Name the outside judge.** What, other than the model or the user, would show the result is right: a benchmark, a replay of real data, a property, a known-answer test, a user's own behaviour.
4. **Say what it changes.** One sentence: which part of the stance this borrowing moves, or 「不改」 with the reason. A borrowing that changes nothing is reported and dropped, not kept for decoration.

Output the step as a short 借鏡 block in the conversation (verbs → discipline → instrument → outside judge → what it changes), and carry the surviving line into the plan's Approach.

Trigger boundary, written so it can be checked: the step is **mandatory** when the restatement is a long-lived feature, a core path, a direction or architecture question, or a Kill / Keep / Pivot verdict. It is **skipped**, with the one-line skip stated, when the restatement is a parameter choice, a single-file change, or a decision brought for grilling — there the attack still borrows the field's known failure catalogue, nothing more. One or two disciplines, never a survey; the project's own prior decisions outrank any imported method. The quantitative case follows the same boundary: when the restatement carries a quantity — cost against effect, capacity, rate, probability, sample size, tolerance — write the model here per `../_shared/modeling.md` §2 (variables, objective, constraints, measured vs assumed, solve or bound, sensitivity) and carry its number into the cost-against-effect line; a parameter choice or a single-file change gets no model, and a restatement with no quantity says so in one line.

## Take a stance

State the recommendation in one sentence with its decisive reason. It answers the restatement and nothing beyond it. Lay out the credible alternatives, always including the minimal one (do nothing, reuse existing Z) and the framework-native or official solution when it genuinely fits — as a real candidate, not an automatic winner. When the borrow step was mandatory and the work will get a plan, have the strongest rival worked out by someone who has not seen the recommendation: before choosing, dispatch one fresh agent — on another model family when the host can run one, otherwise on the same model — with the confirmed restatement and the repo only, never this stance, to work out the strongest design it can as far as the recommendation goes: where it enters, what it changes, how it fails. Weigh the two against each other; each trap the rival's working-out finds that the recommendation also faces becomes a success criterion in the plan's Building section. Then say what the recommendation is betting on, in one to three conditions, each as a sentence a person can act on: what it assumes, what happens if that assumption is wrong, and which alternative it switches to. Never write a bare "this would be overturned by Z".

The stance answers three named questions, each in a line or two:

- **The goal behind the goal.** What does the outcome serve, and what should happen next once it exists? When the request serves an ultimate outcome (the user will hold meetings about it, or will ask for the next step the moment this ships), put the higher-altitude version on the table as a real candidate — "keep the app crash-free" beside "fix this crash" — and let the stance choose between them with reasons. Creative or exploratory work is exempt; say so instead of inflating it.
- **The aesthetic of the solution.** A good design has one idea a reader could restate in a sentence, and every part traces to it; name that idea, then write the 我不是什麼 list — two or three things this design refuses to be. A design that is right only because nothing in it can be called wrong — every case guarded, every choice deferred to a config, every concrete thing behind an interface — has no idea in it; that is hiding, not taste, and the stance says so when it sees it in its own draft.
- **Cost against effect.** Put the recommendation and the minimal alternative side by side with what each costs and what each buys, in numbers wherever a number exists: files and call sites touched, and that count as a share of the tree (the rewrite signal in `../_shared/modeling.md`: the share says whether this keeps the code or replaces it), new services or processes, new runtime dependencies, callers that change, operational surface — relative sizes, never a duration, which agentic work does not follow; against the gain stated as something observable — p95 latency, cases handled, a user step removed. A number from the model is written here the way a person reads it (modeling.md §3: what it means and which decision it changes); its derivation goes to the plan's Approach. When the ambitious target is reachable, name it as the target and name the cheap one as the fallback, not the reverse; when the numbers say the cheap one buys nine-tenths of the effect, the stance says that too.

Delete "it depends on your priorities", "both have trade-offs", "this is your decision to make": the user asked for a lead, not a survey. If the remaining choice is genuinely the user's (a value, a budget, an authority boundary), explain its consequence and wait; a missing question tool does not permit inventing the answer.

Judge existence too. If the honest stance is "do not build this" or "build something else", say Kill or Pivot with reasons grounded in the user's actual constraints — time, motivation, maintenance cost, business model — never generic trade-offs. A verdict ends the skill; it needs no plan file, but it still goes through the presentation step below.

## Verify the premises the stance leans on

Before writing anything durable, list every existence, count, or absence premise the stance leaned on ("no existing X", "Y already handles this", "tests cover this layer"), and every number the cost-against-effect line used, and re-derive each from the repo root with a command whose output you quote, or from the authoritative document. Tag each claim verified (with the command and a quoted fragment) or 未實查; a bare tool name does not earn verified. A count carries the noun the command actually counted (files, classes, call sites, test cases) and never resurfaces as a different noun. A stance resting on a refuted premise is revised in one sentence, not carried forward. Check the project's own prior art — decision records, design docs, recent commits in the area — so the plan does not silently override a decision already made. Current state overrides memory.

## Attack your own proposal, in both directions

Attack for breakage: list two to four concrete failure scenarios, starting from the borrowed discipline's known failure catalogue when one was named, and trace one of them end to end — the part that is down, what the user sees, what brings it back; 「之後再想」 is a finding, not a plan. When the restatement moves a version, runtime or dependency, the scenarios start from the delta: the known changes of that pair intersected with what this code actually uses, each cited file:line with its site count — a removed API nobody calls is no scenario — ranked by blast radius (modeling.md) and classed Mechanical (a codemod does it) or Judgment (a person decides); a change that compiles and runs with a different result (locale, encoding, ordering, floating point, a default) is test-before-touch, and its characterization test goes into Building ahead of the move. Any other restatement skips the delta. Fold in cheap fixes and say you did; state fundamental ones plainly as accepted boundaries. Be loud about scope the user may not realize they are agreeing to: many files, a new service or process, a new runtime dependency or language, any key, account, or external service someone must provision. Before proposing any new mechanism — a rule, a check, a layer — ask whether it solves the problem or only produces a nicer failure log; a check that sits inside the path it governs can simply be skipped by that path.

Attack for size — too big and too small:

- Attack for excess: for each part of the proposal, ask what the restatement would lose if that part were removed. If nothing, cut it and move it to Not building with one line on when it would become needed. Look hardest in the two places excess hides: abstraction — an interface with one implementation, an option or config nobody asked for, a layer kept "for later", a boundary (service, layer, module) that matches no seam where something varies today — and defence — a guard for a state no caller produces, error handling that swallows instead of failing, validation repeated behind a boundary that already validates. Never cut validation at a trust boundary, handling that prevents data loss, security, accessibility, or anything the user asked for. A shortcut kept on purpose is written down with its limit and the condition that upgrades it.
- Attack for under-reach: compare the stance against the restatement and the goal behind the goal. Did it solve a narrower problem — the happy path, the part it was sure of, the version that cannot be wrong — and leave the asked-for part as an Unknown? A plan whose every section is safe is a plan that avoided the question; name the piece it ducked and either bring it back into Building or move it to Not building with a reason the user can accept.

The plan must fit the restatement's scale; a solution optimised for a need the user never stated is a defect, and so is a solution that quietly stated a smaller need.

## Present it so a person can follow

### Plain-language presentation contract

- Make the immediate context explicit: which phrase of the restatement a question fixes, or which bet the stance rests on.
- Explain in plain Traditional Chinese why the conclusion follows from this run's evidence or the user's stated constraints, its practical impact, and the concrete next step (the open decision, or 「無」).
- Keep each English technical term, but explain it in plain Traditional Chinese at its first use, in the same sentence or immediately after it.
- Do not add facts that this run has not established. This is presentation-only: it adds no PAUSE and does not replace or rename the restatement, the stance, or the five plan sections.

Before the file, show the result the way a person absorbs it: the whole shape first, then the part that matters to this user, in the smallest view that makes the key point clear — a before/after diff, one flow, a side-by-side comparison, or one focused page when the shape is too dense for text — with each technical term explained where it first appears. Pick that view from the forms `../show-me/SKILL.md` lays out and draw it inline; that skill is invoked only by the user, so read it rather than calling it. The user should also be able to see which questions were asked and what each answer changed, so the decisions are traceable, not just the conclusion. The conversation is the understanding version; the file is the durable version. Do not make the user read five sections to find out what you recommend.

## Leave a plan on disk, then stop

When the deliberation produced a buildable direction (not a verdict, not a one-line answer), write `.claude/think/<slug>.md` in Traditional Chinese with the confirmed restatement on top and exactly five sections:

- Building — the observable outcome, concrete enough to picture the result; not the mechanism. The one idea the design has, in a sentence. Its success criteria are conditions a person can check（「第一片的所有 P0 行為經對比證實相同」）, never states（「P0 行為已證實」）and never a duration; a size, when one is wanted, is a share of the tree's complexity, not a time.
- Not building — at least three concrete exclusions, including everything the size attack cut and the 我不是什麼 list, each with why and when it would become needed.
- Approach — why this over the alternatives considered, with the cost-against-effect numbers and the model's derivation when one was written; the discipline borrowed and what it changed (or that it was skipped); the load-bearing premise, what happens if it fails, and how the design survives it; which failure modes are accepted boundaries. When the plan has more than one slice, the first slice is named as the pilot — the one that hits the riskiest premise, not the easiest — with the sentence that the plan is a hypothesis: what the pilot surfaces (a premise the reading missed, a prerequisite that reorders the slices, an environment fact nobody wrote down) is expected to revise it, the user's go covers the pilot only, and the rest is re-read after it. The surprises live in the build and the runtime, not in the source read. A single-slice plan says none of this.
- Key decisions — three to five, each "could have done X, doing Y because Z"; activities are not decisions.
  A decision that is hard to reverse, surprising to a later reader without this context, and the outcome of a real trade-off also deserves a decision record in the project (`docs/adr/`); name it in the plan and point to `/baransu:domain-modeling` to record it; this skill never writes it.
- Unknowns — each with the specific question, why deferring is safe, and who decides when; or 無 with the reason this scale needs no deferral. An Unknown may not hold a piece of the restatement the stance ducked.

No TBD or TODO, no "standard approach", no unnamed library or unnamed flow; every non-obvious claim carries its verified or 未實查 tag. Success criteria and scope land here, as outputs of the deliberation, not as inputs demanded at the start. Never overwrite another task's file; if `.claude/think/<slug>.md` already exists, write `<slug>-2.md` and count up.

Tell the user the path and the single most consequential open decision, if any:
「計畫已落檔：.claude/think/{slug}.md。最關鍵的未決點：{一句話，或「無」}。」
Then end the turn. This skill does not implement, does not choose a downstream skill, does not ask permission to proceed, and does not open another approval gate. The user decides what happens next — implement under the red/green discipline in `../_shared/tdd.md` (drawing the shape with `/draft` first when it is not obvious), bring the plan to `/review` for a second opinion, or nothing — and the file is written so a person or a reviewer can judge it without the conversation.

If the user pushes back on the plan, ask which section is wrong, revise with the changed assumption named up front, and rewrite the file. If the pushback is about what they wanted rather than how to build it, the restatement was wrong: go back to it, not to the plan. If the objections spread across sections instead of narrowing, ask for an anti-example — a version they would never accept — before revising again.

## Not-for boundaries

- An existing error or failing behavior → `/hunt`; 「判斷一下這個報錯」 is debugging, not a value judgment.
- Work already decided and ready to build → implement under `../_shared/tdd.md` §7 (with `/draft` first when its shape is not obvious), then `/review` for an independent re-verification; this skill writes no acceptance record.
- A single-file fix with a clear scope → `../_shared/tdd.md` §7 directly; a plan would be ceremony.
