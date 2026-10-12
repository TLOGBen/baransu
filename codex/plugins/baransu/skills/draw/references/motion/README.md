# Motion references — how to read them

Where this sits in the skill: `SKILL.md` § The flow runs preflight (`node scripts/motion/doctor.mjs --install` until `READY`) → form → approach → production → check. Steps 1–2 there (form, approach, brief, plan) are Phase 1 below; step 3 is Phases 2–5 for anything that moves; step 4 is the review. A seamless loop starts from `assets/motion/loop-template.html`.

Two layers. **Layer 1** is the work itself: five phase guides, read in order, each saying what the phase is for, the concepts that govern it, the steps, what it produces, and the gate it must pass. **Layer 2** is the technique library: the deeper methods, numbers, recipes and commands a phase guide points to when you are executing a step. Read layer 1 front to back; open layer 2 only at the step that needs it.

The order is the one an animation studio runs: setting and design → storyboard and animatic → layout and key animation → in-betweens and photography → post. Cheap decisions come first: a design line costs seconds, a draft a few stills, a key one still, a shoot minutes of render, post a full encode. Each phase ends at a gate the director (you, the lead session) signs off; nothing in a later phase starts on an unsigned gate.

## Layer 1 — the five phases

| Phase | Guide | What it settles | Gate |
|---|---|---|---|
| 1 Design (設計) | `1-design.md` | what the film is for, what must be real, the look and sound, numbers instead of adjectives, the route and formats | `docs/brief.md` + `docs/style_guide.md`; every real asset present or the film stops |
| 2 Draft (草稿) | `2-draft.md` | the direction chosen 6 → 3 → 1 (art concept, theme, story idea, with style frames); the colour script; the story with timed reads and events; the cinematography plan (shot size, angle, lens feel, moves and their durations, holds, screen direction); a transition for every seam; the pacing curve and timing sheet; draft key cards | the checklist passes; a keys-only animatic with temp sound reads as a story |
| 3 Keys (關鍵幀／首尾幀) | `3-keys.md` | the first and last frames as a pair, then every key finalised on its key card (read, composition, framing, subject state, type, look, motion in / out, sound, formats, checks) and written as data | every key card complete; every key passes the critique card as a still |
| 4 Shoot (攝影) | `4-shoot.md` | each interval designed, the in-betweens computed from the keys, the camera moving between approved framings, dailies | keys re-render settled; every score ≥ 8 or three rounds logged |
| 5 Post (後製) | `5-post.md` | seams executed, sound scored and synced, the master rendered, loops and exports finished, the encoded file reviewed, delivery | the encoded master passes its review; the report names files, checks, scores |

## Layer 2 — the technique library

| Technique | File | Used in phase |
|---|---|---|
| The render contract, film folder, routes and engines, formats, motion blur, commands, runtime | `pipeline.md` | all; set up in 1, renders in 4–5 |
| The prompt ladder (L1–L4), the directed-prompt template, the XML state list, the director's brief, honest numbers | `prompts.md` | 1 |
| Springs and easing primitives, the motion numbers (cubic-beziers, damping ratio, durations, stagger, holds), hierarchy, the animation principles | `springs.md` | 1 (tokens), 4 |
| 24 named camera moves and how time runs (slow motion, ramps, freezes), the parallax rule, director's camera words | `camera.md` | 2 (language), 3 (layout), 4 (moves) |
| Every transition and when it belongs, sound-led cuts (J / L) | `transitions.md` | 2 (choose), 5 (execute) |
| Type on screen: faces, the hook, captions, numbers, type in UI | `type.md` | 1 (faces), 3 (hook and caption keys), 4 |
| The beat grid, measuring a track, synthesized score and SFX, cues, sync and loudness measurement | `beat-grid.md` | 1 (measure a track), 5 (score and sync) |
| How to look: contact sheets, notes by frame number, onion skin, speed graph, follow-up prompts, feelings → numbers, the export review, fixes for common failures, receipts | `review.md` (+ `../critique-loop.md` for the scorecard) | 3–5 |
| Loops without a seam, the 180° look, MP4 / GIF export, the GIF timing trap, platform limits | `finishing.md` | 5 |
| Long pieces: chapters, `ANIMATION_GUIDE.md`, subagents per chapter, chunked renders | `chapters.md` | 2 (split), 4–5 |
| Client work: scope, building for revisions, packaging, Route B Remotion, finding, pricing and answering a brief | `commission.md` | 1, 5 |
| The page lane: several scrubbable figures in a reading column | `explainer-page.md` | all, for a page |
| Mechanism figures: an idea drawn as a working machine, the 52-idea catalog, inventing your own — a cross-lane unit with its own folder | `../mechanism/mechanism.md`, `../mechanism/mechanism-catalog.md` (`SKILL.md` § Mechanism figures) | all, for a how-it-works figure |
| The hand-drawn look (storybook, brush-ink, watercolour, characters) | `hand-drawn/workflow.md` (vendored library) | all, for a hand-drawn piece |

## Look-up index

| You need | Go to |
|---|---|
| the `seek(t)` rules, determinism, `hash` | `pipeline.md` § The render contract |
| render commands (`still`, `stills`, `strip`, `contact`, `phone`, `animatic`, `full`, chunks) | `pipeline.md` § Commands |
| formats 9:16 / 1:1 / 16:9 (and 4:5), safe areas | `pipeline.md` § Formats |
| Remotion, HyperFrames, Three.js, GSAP, Motion | `pipeline.md` § Routes and engines |
| the one-line showreel prompt, the XML state list, the director's brief | `prompts.md` |
| GOAL / OUTPUT / TIME / … template, adjectives → numbers, the ban list | `prompts.md` § The directed prompt, `1-design.md` § Ban the defaults |
| cubic-bezier values, damping ratio, durations, stagger, holds | `springs.md` § The numbers |
| `spring`, `track`, `stretch`, `swapAlpha`, `cursor`, `typed`, `drag`, `camera` | `springs.md` § The primitives |
| 24 named camera moves and transitions | `camera.md`, `transitions.md` |
| hook size, faces, captions, count-ups | `type.md` |
| sound one frame after picture, phone-band loudness, AAC padding | `beat-grid.md` § Sync and measurement |
| notes in camera words, onion skin, speed graph, follow-up prompts | `review.md` |
| GIF timing trap, X limits, loop seam | `finishing.md` |
| failures everyone hits (flicker, wrong font, seam hiccup, drift) | `review.md` § Fixes |

## Rules that hold in every phase

- Every frame is a pure function of `t`. No timers, no CSS transitions, no unseeded randomness, fonts awaited.
- Facts about the subject are fixed and asked for; choices about the picture are proposed, not asked.
- One read at a time, one hero move per shot, one accent.
- Stills before motion; motion before the full render; the encoded file before delivery.
- A problem goes back to the phase that owns it: a bad story to Draft, a bad key to Keys, a bad interval to Shoot. Never patch a later phase around an earlier mistake.
- A check that did not run is never reported as passed.
