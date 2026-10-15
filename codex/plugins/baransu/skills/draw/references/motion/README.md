# Motion references — step guides and a technique library

## Where motion sits in the skill flow

`SKILL.md` § The flow runs preflight (`node scripts/motion/doctor.mjs --install` until `READY`) → form → approach → production → check. Steps 1–2 there (form, approach, brief, 開工狀態行) are Phase 1 below; step 3 is Phases 2–5 for anything that moves; step 4 is the review. A component runs the same phases at its own scale (`component.md` § Build order): its caption stands in for the film brief, and the figure goes through draft, keys, shoot and post.

## The mechanics examples in `assets/motion/`

The three files in `assets/motion/` (`seek-template.html`, `component-example.html`, `loop-template.html`) are mechanics examples — the `seek(t)` / timeline contract, the scrubber, the render hooks, the layout object `L`. Open one at the step that needs its mechanics (`1-design.md` § 6, `finishing.md` § Loop mechanics from `loop-template.html`, `component.md` § What the example demonstrates), after the look is decided in `docs/style_guide.md`; the look and composition come from the guides and the brief, never from an example.

## Looking up a topic at each step

These files are a book with an index, not a reading list. **Layer 1** is the work itself: five phase guides, each saying what the phase is for, the concepts that govern it, the steps, what each step produces, and the gate it must pass. **Layer 2** is the technique library: one chapter per technique (a camera move, a transition, a spring, a loop rule), which a step points to by `file § chapter`.

Before each step, run its step command: `python3 "<skill>/scripts/lookup.py" --step <step-id> --log "<project>/.codex/draw/<slug>"` (absolute paths: `<skill>` the skill folder, `<project>` the user's project) prints every chapter that step needs — from the phase guide and from the library — and logs the step to `docs/lookups.log`. The phase guides are reached this way, a chapter at a time; none is read whole. Any other chapter is looked up (`lookup.py <topic> --log …`) when a question comes up that it answers; `references/INDEX.md` lists every topic. `python3 "<skill>/scripts/ledger-check.py" "<project>/.codex/draw/<slug>"` checks that every step's required topics were looked up before that step's files were written.

## The studio order of the phases

The order is the one an animation studio runs: setting and design → storyboard and animatic → layout and key animation → in-betweens and photography → post. Early decisions are the easiest to change: a design line, a draft still, a key still, then a shoot's renders, then a full encode. Each phase ends at a gate the director (you, the lead session) signs off; nothing in a later phase starts on an unsigned gate. The director decides; no gate waits on the user.

## Layer 1 — the five phases

| Phase | Guide | What it settles | Gate |
|---|---|---|---|
| 1 Design (設計) | `1-design.md` | what the film is for, what must be real, the look and sound, numbers instead of adjectives, the route and formats | `docs/brief.md` + `docs/style_guide.md`; every real asset present or the film stops |
| 2 Draft (草稿) | `2-draft.md` | the direction funnel wide → 3 → 1 (art concept, theme, story idea, with style frames); every shot's 6 : 3 : 1 hierarchy and the colour script; the story with timed reads and events; the cinematography plan (shot size, angle, lens feel, moves and their durations, holds, screen direction); a transition for every seam; the pacing curve and timing sheet; draft key cards | the checklist passes; a keys-only animatic with temp sound reads as a story |
| 3 Keys (關鍵幀／首尾幀) | `3-keys.md` | the first and last frames as a pair, then every key finalised on its key card (read, composition, framing, subject state, type, look, motion in / out, sound, formats, checks) and written as data | every key card complete; every key passes the critique card as a still |
| 4 Shoot (攝影) | `4-shoot.md` | each interval designed, the in-betweens computed from the keys, the camera moving between approved framings, dailies | keys re-render settled; every gated score ≥ 8, with every round logged (no round cap) |
| 5 Post (後製) | `5-post.md` | seams executed, sound scored and synced, the master rendered, loops and exports finished, the encoded file reviewed, delivery | the encoded master passes its review; the report names files, checks, scores |

## Layer 2 — the technique library

| Technique | File | Used in phase |
|---|---|---|
| The render contract, film folder, routes and engines, formats, motion blur, commands, runtime | `pipeline.md` | all; set up in 1, renders in 4–5 |
| The prompt ladder (L1–L4), the directed-prompt template, the XML state list, the director's brief, honest numbers | `prompts.md` | 1 |
| Springs and easing primitives, the motion numbers (cubic-beziers, damping ratio, durations, stagger, holds), hierarchy, the animation principles | `springs.md` | 1 (tokens), 4 |
| 16 named camera moves and how time runs (slow motion, ramps, freezes), the parallax rule, director's camera words | `camera.md` | 2 (language), 3 (layout), 4 (moves) |
| Every transition and when it belongs, sound-led cuts (J / L) | `transitions.md` | 2 (choose), 5 (execute) |
| Visual hierarchy, the 6 : 3 : 1 rule: foundation 60 % / dressing 30 % / focal anchor 10 % in composition, light, colour, layout, form and density; space → life → plot focus in film; the scene prompt structure; the thumbnail test | `composition.md` | 2 (art direction), 3 (every key), review |
| Type on screen: faces, the hook, captions, numbers, type in UI | `type.md` | 1 (faces), 3 (hook and caption keys), 4 |
| The beat grid, measuring a track, synthesized score and SFX, cues, sync and loudness measurement | `beat-grid.md` | 1 (measure a track), 5 (score and sync) |
| How to look: contact sheets, notes by frame number, onion skin, speed graph, follow-up prompts, feelings → numbers, the export review, fixes for common failures, receipts | `review.md` (+ `../critique-loop.md` for the scorecard) | 3–5 |
| Loops without a seam, the 180° look, MP4 / GIF export, the GIF timing trap, platform limits | `finishing.md` | 5 |
| Long pieces: chapters, `ANIMATION_GUIDE.md`, subagents per chapter, chunked renders | `chapters.md` | 2 (split), 4–5 |
| Client work: scope, building for revisions, packaging, Route B Remotion, finding, pricing and answering a brief | `commission.md` | 1, 5 |
| The component form: one interactive figure in its own file, its contract and performance rules | `component.md` | all, for a component |
| Mechanism figures: an idea drawn as a working machine, the 52-idea catalog, inventing your own — a cross-lane unit with its own folder | `../mechanism/mechanism.md`, `../mechanism/mechanism-catalog.md` (`SKILL.md` § Mechanism figures) | all, for a how-it-works figure |
| The hand-drawn look (storybook, brush-ink, watercolour, characters) | `hand-drawn/workflow.md` (vendored library) | all, for a hand-drawn piece |

## Look-up index

| You need | Go to |
|---|---|
| the `seek(t)` rules, determinism, `hash` | `pipeline.md` § The render contract |
| render commands (`still`, `stills`, `strip`, `contact`, `phone`, `animatic`, `full`, chunks) | `pipeline.md` § The commands |
| formats 9:16 / 1:1 / 16:9 (and 4:5), safe areas | `pipeline.md` § Formats |
| Remotion, HyperFrames, Three.js, GSAP, Motion | `pipeline.md` § Routes and engines |
| the one-line showreel prompt, the XML state list, the director's brief | `prompts.md` § The prompt ladder |
| GOAL / OUTPUT / TIME / … template, adjectives → numbers, the ban list | `prompts.md` § The directed prompt, `1-design.md` § 4. Ban the defaults, lock the identity |
| cubic-bezier values, damping ratio, durations, stagger, holds | `springs.md` § The numbers |
| `spring`, `track`, `stretch`, `swapAlpha`, `cursor`, `typed`, `drag`, `camera` | `springs.md` § The primitives |
| 24 named camera moves and transitions | `camera.md`, `transitions.md` |
| hook size, faces, captions, count-ups | `type.md` |
| why a frame has no focus, 60 / 30 / 10, the scene prompt structure | `composition.md` |
| sound one frame after picture, phone-band loudness, AAC padding | `beat-grid.md` § Sync and measurement |
| notes in camera words, onion skin, speed graph, follow-up prompts | `review.md` |
| GIF timing trap, X limits, loop seam | `finishing.md` |
| failures everyone hits (flicker, wrong font, seam hiccup, drift) | `review.md` § Fixes for the failures everyone hits |

## Rules that hold in every phase

- Every frame is a pure function of `t`. No timers, no CSS transitions, no unseeded randomness, fonts awaited.
- Facts about the subject are fixed: a real asset or fact the brief names and the user did not supply is the one reason to stop and ask. Choices about the picture are decided and written down, never asked.
- Full quality is the default: every phase, every gate, every review round; nothing is cut to save time unless the user asked for something quick.
- One read at a time, one hero move per shot, one accent.
- Stills before motion; motion before the full render; the encoded file before delivery.
- A problem goes back to the phase that owns it: a bad story to Draft, a bad key to Keys, a bad interval to Shoot. Never patch a later phase around an earlier mistake.
- A check that did not run is never reported as passed.
