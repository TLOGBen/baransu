---
name: think
description: Deliberates before building when the user has an undecided idea, feature,
  refactor, or direction and asks how to design it, which way to go, or whether it
  is worth doing (想一下, 幫我想, 怎麼設計, 值不值得, 該不該做, 「我想做 X 但還不確定」). Also takes a decision
  already made when the user wants it tested (拷問我, grill me). Aligns on a restatement
  of what they actually want, then leaves a stance with its bets named and a plan
  file under .codex/think/ for review; never code, never a handoff to implementation.
  Not for debugging an existing error ($hunt) or pinning acceptance for settled work
  ($contract). 繁體中文輸出。
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

# think — deliberate before you build

## Codex Port Adapter - Request User Input Gate

Codex can expose the structured `request_user_input` runtime tool. In Default mode it is currently gated by `[features] default_mode_request_user_input = true`; a skill cannot enable that user configuration itself. This skill is countering the model's inertia to assume the user has already thought the request through, so use the strongest gate available in the current runtime.

When `request_user_input` is exposed, call it once per interaction point — each restatement question (one question fixing one guessed phrase, candidate answers of different kinds, one marked recommended), the restatement confirmation, a choice that is genuinely the user's (a value, budget, or authority boundary) before the stance, and the which-section-is-wrong question after pushback — then wait for the structured answer before continuing.

When `request_user_input` is unavailable, present the same question as plain numbered text and stop until the user answers. Every interaction point in this skill is an Input PAUSE: the user's answer is the material the restatement, the stance, and the plan file are built from, and a fabricated answer would defeat the skill's founding purpose. The runtime tool replaces the text prompt only when it is actually exposed; it does not guarantee answer quality.


Turn a fuzzy intent into a shared statement of what the user wants, then into a position someone else can read cold and judge. Never produce code, scaffolding, config, or pseudo-code; the deliverable is a stance and, when the work deserves one, a plan file.

The default this skill corrects: the model assumes the user has already thought the request through, and answers before both sides agree on what is being asked. Everything in the opening exists to close that gap, and nothing in the opening may start solving.

All user-facing output is in Traditional Chinese; keep technical terms in English and explain each one where it first appears.

## Outcome Contract

- **Outcome**: A confirmed restatement of what the user wants, a stance with its bets named, and — for buildable work — a five-section plan at `.codex/think/<slug>.md`; for a verdict (Kill / Pivot) or a decision under test, the stance alone. Never code, scaffolding, or a handoff to implementation.
- **Done when**: The restatement is confirmed by the user or unchanged after a round of answers; the stance is stated with its bets; every premise it leans on is tagged verified or 未實查; both attacks (breakage and excess) have run; the result has been presented; and, when buildable, the plan file exists and its path was reported. The turn ends there — no downstream skill is chosen and no approval gate is opened.
- **Evidence**: The confirmed restatement, the verified / 未實查 tags with their commands and quoted output, and the plan file path (or the verdict line).
- **Output**: Traditional Chinese conversation; `.codex/think/<slug>.md` with the restatement on top and the five sections below. `$ship` archives that directory.
- **Automation**: ultracode=neutral, loop=not-drivable（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）
- **Telemetry**: on invocation, append one selection record per `../_shared/selection-telemetry.md`.

PAUSE classification for non-interactive drivers: `references/loop-pauses.md`.

## Align on a restatement, not on a solution

Open by restating, in a few sentences, what you understand the user wants: the outcome, why they want it, what must not change, and roughly how big it is (a one-off script, a long-lived feature, a core path, an edge). Fill it only from what the user actually said; mark a missing field 未知，先不問 rather than inventing it. This restatement is the object of alignment. Its job is to make your guesses visible so the user can correct them.

Every phrase in the restatement you had to guess is a candidate question. Ask it only if different answers would change the shape of the answer, not a parameter of it — whether to cache at all: ask; cache for five minutes or an hour: do not. Offer the candidate answers as different kinds, not the same direction at different strengths, and mark one as recommended. Ask one at a time unless the user prefers a batch, and say which phrase of the restatement the question fixes.

Find facts yourself. Read the repo, docs, and prior decisions to answer any question that has an answer, and never turn research into a question for the user. Reading code to settle a fact is allowed; forming or showing a solution before the restatement is confirmed is not. During alignment the user sees exactly two things: the current restatement with the changed phrase marked, and the question.

When the user arrives with a decision already made and wants it tested (拷問我, 壓力測試這個決定, grill me), the restatement is that decision; confirm it in one round and go straight to the attack.

Alignment ends when the user confirms the restatement, or when a round of answers leaves it unchanged; then stop asking. Two exits sit here:

- If the confirmed restatement is a single-file change with one obvious fix, there is nothing to deliberate. Say so and point the user to the red/green discipline in `../_shared/tdd.md` §7; do not write a plan for it.
- If the restatement cannot fit in a few sentences because the effort has several independent destinations, say so. When the common suite's wayfinder is installed in the session (detect first, never assume), point there; otherwise say the effort needs to be charted before it can be deliberated, and stop.

## Take a stance

State the recommendation in one sentence with its decisive reason. It answers the restatement and nothing beyond it. Lay out the credible alternatives, always including the minimal one (do nothing, reuse existing Z) and the framework-native or official solution when it genuinely fits — as a real candidate, not an automatic winner. Then say what the recommendation is betting on, in one to three conditions, each as a sentence a person can act on: what it assumes, what happens if that assumption is wrong, and which alternative it switches to. Never write a bare "this would be overturned by Z".

Delete "it depends on your priorities", "both have trade-offs", "this is your decision to make": the user asked for a lead, not a survey. If the remaining choice is genuinely the user's (a value, a budget, an authority boundary), explain its consequence and wait; a missing question tool does not permit inventing the answer.

Judge existence too. If the honest stance is "do not build this" or "build something else", say Kill or Pivot with reasons grounded in the user's actual constraints — time, motivation, maintenance cost, business model — never generic trade-offs. A verdict ends the skill; it needs no plan file, but it still goes through the presentation step below.

## Verify the premises the stance leans on

Before writing anything durable, list every existence, count, or absence premise the stance leaned on ("no existing X", "Y already handles this", "tests cover this layer") and re-derive each from the repo root with a command whose output you quote, or from the authoritative document. Tag each claim verified (with the command and a quoted fragment) or 未實查; a bare tool name does not earn verified. A count carries the noun the command actually counted (files, classes, call sites, test cases) and never resurfaces as a different noun. A stance resting on a refuted premise is revised in one sentence, not carried forward. Check the project's own prior art — decision records, design docs, recent commits in the area — so the plan does not silently override a decision already made. Current state overrides memory.

## Attack your own proposal, in both directions

Attack for breakage: list two to four concrete failure scenarios. Fold in cheap fixes and say you did; state fundamental ones plainly as accepted boundaries. Be loud about scope the user may not realize they are agreeing to: many files, a new service or process, a new runtime dependency or language, any key, account, or external service someone must provision. Before proposing any new mechanism — a rule, a check, a layer — ask whether it solves the problem or only produces a nicer failure log; a check that sits inside the path it governs can simply be skipped by that path.

Attack for excess: for each part of the proposal, ask what the restatement would lose if that part were removed. If nothing, cut it and move it to Not building with one line on when it would become needed. The plan must fit the restatement's scale; a solution optimised for a need the user never stated is a defect, not thoroughness.

## Present it so a person can follow

### Plain-language presentation contract

- Make the immediate context explicit: which phrase of the restatement a question fixes, or which bet the stance rests on.
- Explain in plain Traditional Chinese why the conclusion follows from this run's evidence or the user's stated constraints, its practical impact, and the concrete next step (the open decision, or 「無」).
- Keep each English technical term, but explain it in plain Traditional Chinese at its first use, in the same sentence or immediately after it.
- Do not add facts that this run has not established. This is presentation-only: it adds no PAUSE and does not replace or rename the restatement, the stance, or the five plan sections.

Before the file, show the result the way a person absorbs it: the whole shape first, then the part that matters to this user, in the smallest view that makes the key point clear — a before/after diff, one flow, a side-by-side comparison, or one focused HTML page when the shape is too dense for text — with each technical term explained where it first appears. When the common suite's show-me skill is installed in the session, hand the result to it; otherwise do the same inline. The user should also be able to see which questions were asked and what each answer changed, so the decisions are traceable, not just the conclusion. The conversation is the understanding version; the file is the durable version. Do not make the user read five sections to find out what you recommend.

## Leave a plan on disk, then stop

When the deliberation produced a buildable direction (not a verdict, not a one-line answer), write `.codex/think/<slug>.md` in Traditional Chinese with the confirmed restatement on top and exactly five sections:

- Building — the observable outcome, concrete enough to picture the result; not the mechanism.
- Not building — at least three concrete exclusions, including everything the excess attack cut, each with why and when it would become needed.
- Approach — why this over the alternatives considered; the load-bearing premise, what happens if it fails, and how the design survives it; which failure modes are accepted boundaries.
- Key decisions — three to five, each "could have done X, doing Y because Z"; activities are not decisions.
- Unknowns — each with the specific question, why deferring is safe, and who decides when; or 無 with the reason this scale needs no deferral.

No TBD or TODO, no "standard approach", no unnamed library or unnamed flow; every non-obvious claim carries its verified or 未實查 tag. Success criteria and scope land here, as outputs of the deliberation, not as inputs demanded at the start. Never overwrite another task's file; if `.codex/think/<slug>.md` already exists, write `<slug>-2.md` and count up. Do not also write an acceptance record; that is `$contract`'s job, reading from this plan.

Tell the user the path and the single most consequential open decision, if any:
「計畫已落檔：.codex/think/{slug}.md。最關鍵的未決點：{一句話，或「無」}。」
Then end the turn. This skill does not implement, does not choose a downstream skill, does not ask permission to proceed, and does not open another approval gate. The user decides what happens next — `$contract` to pin acceptance, `$review` to get a second opinion on the plan, or nothing — and the file is written so a person or a reviewer can judge it without the conversation.

If the user pushes back on the plan, ask which section is wrong, revise with the changed assumption named up front, and rewrite the file. If the pushback is about what they wanted rather than how to build it, the restatement was wrong: go back to it, not to the plan. If the objections spread across sections instead of narrowing, ask for an anti-example — a version they would never accept — before revising again.

## Not-for boundaries

- An existing error or failing behavior → `$hunt`; 「判斷一下這個報錯」 is debugging, not a value judgment.
- Pinning assertable acceptance for work already decided → `$contract`.
- A single-file fix with a clear scope → `../_shared/tdd.md` §7 directly; a plan would be ceremony.
