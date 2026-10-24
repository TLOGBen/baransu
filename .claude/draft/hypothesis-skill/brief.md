# Candidate brief — shape of the `/baransu:hypothesis` skill

You are one of several designers drawing the shape of the same change. Draw the best shape you can under your pull; do not hedge toward what another designer might draw. Work alone. Write ONLY inside your output location. Read-only everywhere else. Report in Traditional Chinese (台灣); identifiers, paths and file contents that are agent-facing prose stay in English (repo convention: every SKILL.md body and references file is English; user-facing output strings are Traditional Chinese).

## Goal

Read the plan first: `D:\Workspace\01_Plugin\baransu\.claude\think\formal-hypothesis.md` (Traditional Chinese; its restatement, Building and Not building sections are the goal). In one paragraph:

`/baransu:hypothesis` is a new skill that **writes down hypotheses**: a claim about how part of a system behaves, **always written as a formal model** (TLA+ checked by TLC by default; code-level verifiers for every-input properties), each part citing its source (`file:line` for code; quoted passage + location for documents), with plain-language rules and a progressive series of state diagrams (an HTML page opened for the user: diagram 1 happy path only, each next diagram adds one part, the last numbers each bug path). It is invoked by the user or proposed by other skills when one of the trigger rows H1–H8 in the plan matches. Inputs: code (a core module that "must not fail"), a `/hunt` intermittent symptom, documents (requirement interviews, meeting notes, RFP, SA, SD) and a comparison of two documents (refinement: one as rules, one as behaviour). It owns the artifact (`.claude/hypothesis/<area>/`) and its maintenance (`--maintain`, four outcomes). Readers — `/prove-it` (proves it: reruns the model, replays counterexamples on the real app), `/hunt` (turns counterexample paths into yes/no probes; hunt's informal guesses get renamed 「推測」), `/review` (each rule becomes a question; stale → reported), red/green TDD green step and `/draft` (definition of done = hypothesis X proved), `/health` (stale hypotheses in its verifier-coverage layer) — only read it. Every part not formalized gets a reason record (four fields, six reason classes, in the plan). Strictness: true to source; seen failing on a broken variant; seen succeeding (goal reachability, and seen unreachable when a transition is removed); scope stated; findings stay findings; stale when the source changed after the sync point (commit for code, version + content hash for documents).

## Grounding (read these)

- Plan: `D:\Workspace\01_Plugin\baransu\.claude\think\formal-hypothesis.md`
- Latest plugin source (8.15.0, read-only): `C:\Users\powde\.claude\plugins\marketplaces\baransu\` — especially `plugins/baransu/skills/prove-it/SKILL.md`, `plugins/baransu/skills/prove-it/references/formal.md` (the rules that move into the new skill), `plugins/baransu/skills/prove-it/references/recipe.md`, `plugins/baransu/skills/hunt/SKILL.md` (Tool Scan table ~line 103, side-effect rule ~line 178), `plugins/baransu/skills/review/references/principles/index.md`, `plugins/baransu/skills/show-me/SKILL.md` (how it writes an HTML page and opens it), `plugins/baransu/skills/read/SKILL.md` (document → Markdown), `plugins/baransu/skills/_shared/loop-contract.md`, `plugins/baransu/skills/ship/SKILL.md` (archive allowlist; kept products), and the repo `CLAUDE.md` (conventions: English body, versioning, invariants; Gate 10 in `scripts/verify-skills.py`).
- An existing skill to copy the file layout from: `plugins/baransu/skills/prove-it/` (SKILL.md, NOTICE.md, references/).
- Working known-answer example of a hypothesis: `C:\Users\powde\AppData\Local\Temp\claude\C--Users-powde--claude-spares-spare-xFHCWn\e8da0a53-75c1-4a55-8a09-3442b473ad13\scratchpad\tla\Approval.tla` with `Naive.cfg`/`Fixed.cfg` (TLC at `D:\Workspace\00_Env\tla\tla2tools.jar`, Java 25 on PATH).
- Design screen: `C:\Users\powde\.claude\plugins\marketplaces\baransu\plugins\baransu\skills\review\references\principles\structure.md`, `taste.md`, `readability.md`.

## Constraints every shape must honour

- Callers that cannot break: `/prove-it`'s every-case claims today live in `.claude/prove-it/formal/<area>/`; `/ship` keeps `prove-it/formal/` (never archived). A migration path must exist; until migrated, `/prove-it` keeps reading the old location.
- Only `/hypothesis` writes `.claude/hypothesis/`; every reader reads only. Review never writes (review/SKILL.md:39).
- No product code edits by `/hypothesis` (it writes models, harnesses, README, the HTML page).
- The skill is a Markdown skill: its "types" are the artifact layout (directory, README schema, verdict values, reason-record schema, coverage map, sync point) and its command surface (arguments, flags); its "bodies" are SKILL.md / references sections. English body.
- `loop=not-drivable` is the plan's default (no loop-pauses file, Gate 10 untouched); if you choose otherwise, say why.
- A Codex mirror exists for every file (`codex/plugins/baransu/...`); your shape should not depend on anything Codex cannot read, but you do not draft the mirror.

## Your pull

(see the dispatch message)

## What to return, at your output location

1. `usage.md` — two or three real call sites first: a user invocation on code, `/hunt` calling it on a symptom, a reader (`/prove-it` or `/review`) consuming the artifact, and a document comparison. The usage is the specification.
2. `sketch/` — the skill skeleton as files: `SKILL.md` (frontmatter + every section heading with a one-line intent and the body left as `(unimplemented)`), each `references/*.md` file you would create (headings + intent), and the artifact template(s): the `<area>/README.md` schema, the verdict values, the reason-record schema, the coverage map, the sync point fields, the HTML page structure.
3. `seams.md` — for each seam: what hides behind it, what varies across it, its adapters.
4. `state.md` — who owns each piece of state (files, sync points, verdicts), and what happens when two actors write it, or a step runs twice or stops halfway.
5. `tradeoffs.md` — each as 「我們接受 X，換到 Y」, and the alternatives you considered and dropped.
6. `traps.md` — the ways this shape can fail.

Keep the whole return under ~1,500 lines of files. End your final message with a ≤ 300-word Traditional Chinese summary of your shape.
