---
name: draft
description: "Drafts the shape of a change before its code: writes how callers will use it, sketches types and signatures with bodies left unimplemented, has it drawn twice by designers who cannot see each other, keeps the shape the next contributor can extend, and leaves the sketch as the contract to build against; --deepen finds shapes worth redrawing in existing code. Trigger On '$baransu:draft', '畫骨架', '先打骨架', '先設計介面', '形狀怎麼切', '改善架構', 'sketch the shape', 'architect this'. Not for an undecided direction ($baransu:think) or reviewing finished work ($baransu:review)."
compatibility: Designed for Claude Code; ported to Codex.
---

# draft — the shape before the code

The shape of a change — the modules it adds or touches, what each interface asks of its callers, where the seams go, who owns each piece of state — is the decision most expensive to undo, and code written straight from a request settles it by accident. This skill settles it on purpose: callers' usage first, then the types and signatures that serve it, drawn at least twice by designers who cannot see each other, screened by the same principles `$baransu:review` judges with, and left in the repo as a sketch the implementation is built against.

Use it when the direction is settled — by the user, or by a `$baransu:think` plan — and the shape is not obvious: a new module, a change across a seam, a shared engine, state with more than one writer. A change whose shape the surrounding code already dictates goes straight to `../_shared/tdd.md`.

The design screen is `../review/references/principles/structure.md`, `taste.md`, and `readability.md`, with their vocabulary: a module is anything with an interface and an implementation; its interface is everything a caller must know — signatures, invariants, ordering, errors; it is deep when much behaviour sits behind a small interface; a seam is where an interface lives, real only when something varies across it.

Arguments the user may give after `$baransu:draft`: `[change | plan path] [--deepen [area]]`.

## Codex Port Adapter - Independent Designers

Step 2 dispatches each designer with `spawn_agent` and `fork_turns="none"`: by default a spawned agent inherits this whole conversation, which would show it the session's preference and the other candidates. Pass the brief, the principle file paths, and the output location as the task input.

All user-facing output is in Traditional Chinese; code, identifiers, and paths stay as they are.

## Outcome Contract

- **Outcome**: One chosen shape for the change, written into the repo as a sketch the build accepts — types, signatures, module map, unimplemented bodies — with its rationale, seen by the user before any body is filled.
- **Done when**: The touched systems were grounded or the skip was stated; usage was written before types; at least two structurally distinct candidates came from designers who could not see each other; each was screened with the moves it breaks named; one was chosen with its grafts and rejections recorded; the sketch builds or type-checks where the language allows; the rationale file exists; the user was shown the shape and the turn stopped for their go, or under a driver the go took its default per `references/loop-pauses.md`.
- **Evidence**: The candidates' locations, the screen per candidate, and the build or type-check output of the sketch.
- **Output**: The sketch as an uncommitted change in the repo's own files; the rationale at `.codex/draft/<slug>.md`; the candidates under `.codex/draft/<slug>/`.
- **Automation**: ultracode=neutral, loop=assisted（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）

PAUSE classification for non-interactive drivers: `references/loop-pauses.md`.

## 1. Ground

Read the systems the change touches the way `$baransu:how` does — entry points, data flow, who owns each piece of state, the layering — and, when the change redefines ownership or layering, why the current shape is so the way `$baransu:why` does, so a past decision becomes a constraint rather than a guess. A `$baransu:think` plan's restatement and its Building and Not building sections are the goal; the repo's glossary (`CONTEXT.md`) names the modules. Skip this only for greenfield work with nothing around it to integrate, and say so.

## 2. Draw it twice

Write the brief once, as `references/candidate-brief.md` lays out: the goal, the grounding by path, the constraints every shape must honour (callers that cannot break, types it must interoperate with, invariants that cross the boundary), and the principle files. Dispatch at least two fresh agents in one message — on different model families when the host can run them, otherwise on the same model — each with the brief and its own output location (`.codex/draft/<slug>/candidate-<n>/`, or a git worktree), never another candidate or this session's preference. Give each a different pull, so the candidates differ in whole shape rather than in details: the smallest interface (one to three entry points, most behaviour hidden); the most common caller made trivial; or ports and adapters for a dependency that truly varies.

## 3. Screen and choose

Read every candidate end to end. Screen each against the three principle files and name each move it breaks, with the place. Compare on depth (what the interface hides against what a caller must learn), locality (where the next change will land), and seam placement (what varies across each seam). Prefer the shape where a change that looks right from one file is right for the whole repo: the next contributor is often an agent that sees only the file it opened and copies the nearest example.

When a hypothesis already covers the area the change lands in (`hypothesis-status.py --files <area files>`, read per `../hypothesis/references/reading.md`), screen every candidate against its rules too: a candidate under which a rule would no longer hold is rejected or kept only for a graft, with the rule's id named.

Choose the base a maintainer can extend most easily without breaking its invariants; on a tie, the smaller interface. Walk each other candidate once more for the one or two things worth grafting, and fold them in by hand so the result stays one idea. Candidates that converged are strong agreement: say so and graft nothing. Candidates that diverge wildly mean the brief was underspecified: fix the brief and draw again, never average them. Each trap another candidate's working-out found that the base also faces becomes a postcondition in the rationale. Remove each candidate's worktree, if it had one, once the choice and the grafts are made.

## 4. Write the sketch

Write the chosen shape into the repo's own files: types, signatures, the module map, doc comments stating intent and invariants, bodies that raise the language's not-implemented error, and pseudocode comments for the tricky logic. An invariant goes into a type first, then a check, and into prose last. A reader traces data from input to output by reading types and signatures alone. Build or type-check it: a sketch the compiler rejects is not a contract. Write `.codex/draft/<slug>.md` as `references/rationale.md` lays out.

When the chosen shape meets a row of H1–H8 in `../hypothesis/references/formal.md`, invoke `$baransu:hypothesis` on the sketch before this stop: a design-time hypothesis whose coverage is the sketch's files, so the same stop shows the shape, the rules in plain words with their diagrams, and the checker's verdict. Filling the bodies later makes it stale; the green step hands it to `--maintain`, which redraws the model from the real code.

Present the usage, the shape, and the choice in plain words, and stop for the user's go. The sketch is an uncommitted change they can read before any body is filled; what they push back on is grounding — re-ground and draw again rather than patching the sketch.

## 5. Build against it

Implementation fills the bodies under `../_shared/tdd.md` red/green; the usage's call sites and each postcondition in the rationale are the first tests. The sketch is the contract: a body that needs a parameter, a state, or a call the sketch did not anticipate is a signal to raise — the sketch was wrong, the requirement was missed, or the implementation overreaches — never friction to absorb.

Scrap the sketch when friction is a pattern, not an instance: the same workaround in unrelated places; edge cases that each need their own branch; types that need escape hatches (casts, `any`, optional fields always set) to compile; a lock where the sketch said nothing was shared; callers that must know the internals; two deviations of the same shape. Then re-ground on what was built, draw again as if the new constraints had been there from the start, and make the new sketch smaller than the old one before it grows.

## `--deepen [area]` — shapes worth redrawing in existing code

Unnamed, it turns on per `../_shared/auto-flags.md` when no change is named and the request asks where the structure should improve（「改善架構」「哪裡該重構」「這塊太亂」）, or when grounding shows the change cannot be shaped well until the area it lands in is deepened — then the candidates come first.

Scope first: the area the user names, otherwise where the code changes most (`git log` hot spots), since a deeper module pays back in future changes. Read the glossary and the recorded decisions there. Walk it for friction: one concept that needs bouncing between many small modules; interfaces nearly as large as their implementation; logic extracted for testability while the bugs hide in how it is called; coupling that leaks across a seam; code hard to test through its interface. Apply the deletion test to each suspect — complexity that would concentrate is the signal.

Present each candidate with its files, the problem, the change in plain words, what it buys in locality, leverage, and tests, and its strength（強烈建議／值得探索／推測）; draw a before and after when the structure is graph-shaped. A candidate that contradicts a recorded decision is shown only when the friction is worth reopening it, and says so. Stop for the user's pick; the picked candidate goes through steps 2 to 5.

## Not-for boundaries

- Whether to build it, or which direction → `$baransu:think`; it takes a stance and never writes code.
- A change whose shape the code already dictates → implement under `../_shared/tdd.md`.
- Judging a finished change → `$baransu:review`.
- Settling the domain's terms → `$baransu:domain-modeling`.
- A picture of the structure as it is → `$baransu:show-me` or `$baransu:draw`.
