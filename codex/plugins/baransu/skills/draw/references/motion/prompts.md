# Prompts — the ladder, the directed prompt, the director's brief

Technique reference for Phase 1 (`1-design.md`). Use it to write the brief the user did not write: pick the rung of the ladder the request needs, then fill the matching template.

## The prompt ladder

The viral "one prompt" clips and the 12-hour autonomous runs sit on the same ladder. Climbing it adds very little to the prompt and a lot to the harness: references, a render engine, a state list, a beat grid, a critique loop. The prompt is about 10 % of the result.

| Level | Prompt | What it tests | Harness it needs |
|---|---|---|---|
| L1 one-liner | ~190 characters | the engine | `seek(t)` renderer |
| L2 brand | + product URL, "real screenshots, real logo", "must have music" | assets + sound | screenshots, beat grid, synthesized score |
| L3 reference + state list | reference frame / video / library + a beat-by-beat state list | the idea | `style_guide.md`, shot list, measured beats |
| L4 director's brief | 9 000–19 000 characters, written as a crew | a production | character bible, workflow gates, subagents, critique log |

### L1 — the showreel sentence

"Make a dynamic 15-second motion graphics video that shows what an incredible motion designer you are, like it's your showreel for a résumé. Go all out." Why it works: *showreel* is a genre with known rules (fast cuts, a new technique every shot, the best first); *you* makes the model the subject so it shows technique instead of explaining a product; *15 seconds* is one pass and 6–8 shots; *go all out* multiplies effort. It makes a great model demo because there is no brief to miss, so nothing can come out wrong.

Its weakness is **brief contagion**: hundreds of people ran the same sentence and the reels rhyme with each other (the public dataset of 1 100+ clips shows the same centred-title / gradient / fade-in defaults recurring). Use L1 to test the pipeline, then move on. Pointed at your own launch, a one-liner says nothing about your product, your words or your timing, all of which can come out wrong.

Variants that shipped and still worked: a 60-second 16:9 reel with an original piano score and "S-tier sound design, no generic synth pads"; an anti-slop guardrail ("avoid frames and text in the corners, the usual giveaways of AI-made video"); a story instead of techniques ("the history of X from Y to today, surprise me with the storyboard"); an agency persona ("as if you were a niche branding studio; one accent colour; every shot a different technique").

### What the public collections show

Two public collections of code-rendered motion are large enough to say where the defaults come from and where a reference is worth looking for (their own analyses, restated; sources in `NOTICE.md`). The counts describe what was posted, not what works.

- **A domain mostly has one look — except where it does not.** Of 1 119 classified files, games / interactive are 3D renders seven times in ten (161 / 230) and ads / launches are motion graphics / UI seven times in ten (154 / 215); those two cells alone hold 28 % of the sample, and they are where L1's rhyming reels live. Education and stories have no majority look (37 % motion graphics, 33 % flat cartoon): for them decide the explanation or the narrative first (`1-design.md` § 1) and pick the treatment that serves it, instead of inheriting a cell's look.
- **One style is not one palette.** The 350 motion-graphics files split 198 dark-neutral / 152 light-neutral; music videos carry a median 45.5 % visibly colourful pixels, ads 17.6 %. A brief that says "motion graphics" has chosen neither a value nor a colourfulness; state the background value, the dominant and accent colours and the shot-to-shot consistency (`composition.md` § Colour, `2-draft.md` § 2).
- **A short prompt can carry a long input.** Five public briefs run from 172 to 17 664 characters, and a two-line request often hands over a skill, a product repository, footage or a song. The ladder counts the harness, not the sentence: list the inputs before deciding the model's job (§ References and inputs).
- **"One prompt" is not "one pass".** Creators who report a single human prompt also report the model rejecting its own intermediate renders many times. Keep three counts apart in the delivery log: human prompts, internal review passes (`../critique-loop.md`), and the time to the accepted master; compare whole-task cost with revisions, services and assets, never the price of one call.
- **Where the mechanism approach stands.** In a gallery of 821 code-made motion pieces (2026-10-13: 3D & interactive 199, education 159, product 155, motion design 108, narrative 81, music 63, characters 56) a set of working-machine illustrations, at 6 400 bookmarks, is among the first pieces shown: a how-it-works object (`../mechanism/mechanism.md`) travels as far as a showreel.

### L2 — point it at a product

Three lines did the work in the published examples: the product URL, "use actual product screenshots, logo, assets", "must have music" (`grab.mjs`, `1-design.md` § 1). Keep one session per brand: the renderer, audio synth and export pipeline already exist, so the second video is faster.

```
Make a dynamic 20-second motion graphics video for [PRODUCT] ([URL]), with the energy
of a motion designer's showreel. Go all out.
Assets: real screenshots, the real logo, real colours and fonts, saved to ./assets; list them first.
Story (one beat each, 2–4 s): hook in 5 words of huge type → the UI assembles itself →
three features, each a UI moment with a cursor doing a real action → one number that proves it → logo + CTA.
Sound: original music at 120 BPM synthesized in code; clicks and whooshes on the beat.
Format: [primary format] first, then the other two from the same timeline; a contact sheet for each.
Before the full render, render a contact sheet of one frame per beat and score it.
```

### L3 — a reference and a state list

Reference handling is `1-design.md` § 2. Then write the **state list**, not the vibe. The most-bookmarked prompts of the trend were XML specs: `<inputs>` to gather, `<direction>`, a beat-by-beat `<structure>`, `<build>` rules, `<gotchas>`, `<start>`. The concept behind them: **one shape, never cut** — a single element morphs size, radius and colour from state to state, a cursor drives each change with real clicks, and the last frame equals the first so it loops.

```
<inputs>  product + URL · 8–12 UI states that tell its story · the real data in each · brand colours + fonts + one accent · the two or three features the look must keep (what would make it stop being this brand) · a royalty-free track near 120 BPM · formats </inputs>
<direction> Product-film UI motion. A single container that never cuts away: each state is that same element changing size, radius and fill while its contents swap under a brief blur. A cursor drives every change. Warm neutral canvas, one accent. Every frame: one quiet base that fills most of it, a few supporting elements that point at the focus, one focus marked by value or the accent, never by extra detail. Springs with at most a tiny overshoot. Not allowed: bouncy easing, glows, gradients on UI chrome, particle bursts, dead time. </direction>
<structure> 120 BPM, 8 bars, something happens on every beat. logo → CTA button → email field (typed) → loader → success check → dashboard card → chart draws itself → tooltip → ⌘K palette → toast → logo. </structure>
<build> One HTML file, one canvas, window.seek(t); no CSS transitions, timers, or carried state. Closed-form springs; a value with many targets = sum of one spring per change. Text inside a morphing container enters after the morph starts, leaves before the next. Tab indicators: leading and trailing edges on different springs. Beat grid from the track; start on a downbeat; UI sounds on measured peaks. Headless Chrome at 60 fps, 4 subframes blended for motion blur. </build>
<gotchas> Never will-change on anything the camera scales. The last frame equals the first, cursor position and velocity included. </gotchas>
<start> State the inputs you were given and the ones you assumed, lay the state list on the beat grid, then write code without waiting. </start>
```

Let the model pick the technique: specify the look and the constraints, not the library.

### L4 — the director's brief

A five-minute dictated brief became a 142-second music video after a 12-hour run: the "one prompt" was a spoken brief plus 12 hours of autonomous work, and direction did the heavy lifting. The published briefs (9 500 and 19 000 characters) share one skeleton: they do not describe a video, they staff a production.

- **The film in one line.** The logline and the joke, so every decision can be checked against it.
- **References.** Source video, song, image library, a repo of prior work; what to keep, what to push.
- **Tools and keys.** Skills to load, APIs available (image, video, voice), where docs live.
- **Character bible.** Proportions, palette sampled from a sheet, expressions, an identity lock that survives every style change.
- **Beat sheet.** Acts with timestamps; a visual payoff every 3–5 s; a hook in the first 2.
- **Text on screen.** When lyrics/captions go huge, when they sit like subtitles; composition leaves room for them.
- **Workflow gates.** Plan → rig → stills → animatic → full pass → polish → audio → render. Do not skip gates (they are the five phases, `README.md`).
- **Critique loop.** Render stills, score them, write the three worst problems, fix, repeat until every score is 8+ (`../critique-loop.md`).
- **Deliverables.** Final MP4, loop check, poster frame, contact sheet, clean source with a README.

#### Generate-then-trace — footage as an input

The *generate-then-trace* move: an external video model renders base shots with characters and physics, then the code layer redraws the whole video on top, so the viewer only sees the drawn layer. Video models give motion that is hard to hand-code; the code layer gives a consistent, ownable look. This skill does not call image, video or voice models itself (it renders only pixels it drew): base shots or a voice track the user already has are *inputs* — trace over the frames in `refs/`, lock beats to the words' `timings.json` — and the brief names them as such.

#### The director's brief template

Fill every bracket; cut sections the piece does not need.

```
Act as director, animator, sound designer and render engineer on a [DURATION] film made entirely in code.
This is a multi-session production; the final render comes last, not first.
## The film in one line
[LOGLINE. What the viewer should feel at the end.]
## References and inputs
- ./refs/ : [video / frames / image library]. Borrow the grammar, not the content.
- ./audio/track.wav : use it unchanged. Measure beats with beats.py first.
- APIs in .env: [NAMES] (inputs only; $baransu:draw renders only pixels it drew).
## Look
[3–5 lines: palette, type, texture, camera language. What fills the frame / what leads the eye / what the viewer must find, and the single difference that marks it. Banned looks.]
## Beat sheet
0:00–0:02 hook: [the single most striking image]
0:02–0:10 [act 1] … a new visual payoff every 3–5 seconds
[END] the last frame sets up the first frame (loop)
## Workflow, with gates
0. docs/brief.md + assets/manifest.json: every asset the brief names as real is present, or stop and say which is missing. No brand decision is taken by default.
1. docs/style_guide.md + docs/shotlist.md (every shot: enter state, exit state, why it exists, frames, camera, text, SFX). Write the shot list and continue without waiting; only the asset list can stop the run. When the reference reads two ways, render the hook still both ways, choose one, and log the reason in docs/review_log.md.
2. Stills for every shot → contact sheet → critique.
3. Animatic at 960×540 with placeholder audio; fix pacing before polish.
4. Full animation, polish pass, sound pass, final render.
5. Split work across subagents per chapter; write docs/ANIMATION_GUIDE.md first so every subagent codes in the same style.
## Critique loop (every shot, at least 3 rounds)
Render 3–5 stills, score 1–10 on hook / readability at 360 px / motion / composition / depth / sound sync / polish. Log scores + 3 biggest problems in docs/review_log.md. Fix. Repeat until all are 8+.
## Deliverables
out/<slug>.mp4 · out/check/<slug>.loop_check.mp4 · out/<slug>.poster.png · out/<slug>.contact.png · README.md
```

## The directed prompt

### The directed-prompt template

The compact form of a brief, for a single loop, a figure or a one-shot ask; `docs/brief.md` + `docs/storyboard.md` carry the same content for a film. Fill every line before building; each removes one decision the model would otherwise make.

```
GOAL:    what the viewer should feel or do, in one sentence
OUTPUT:  one self-contained HTML file (Route A) or a named framework with its numbers; W × H
TIME:    seconds × fps = total frames; BPM and frames per beat; loop yes / no
MODEL:   (3D or mechanism) real sizes in units, parts, materials
LOOK:    palette in hex, one accent, typeface + weight + size + tracking; lights with colour and strength;
         the 6 : 3 : 1 order — what is the quiet 60 %, the leading 30 %, the found 10 % (composition.md has a scene prompt structure)
MOTION:  easing as cubic-bezier, springs as damping ratio, durations in frames, stagger
SHOTS:   frame ranges, one hero move per shot, how each shot hands off (a cut, a match cut, a wipe)
CAMERA:  field of view, distance, the named moves with their curves
BANNED:  the defaults you never want to see, by name
QA:      stills at named frames, a contact sheet, fix, then the full render
```

Write GOAL first, then TIME. SHOTS is where the story lives: default to the cut; a transition should be a decision. The QA line makes the work check stills before rendering the whole clip.

### The A/B evidence — adjectives become numbers

Same model, same subject (wireless earbuds), same technical line (one HTML file, three.js, 960 × 1080 per side, a 6-second loop). Prompt A: "Create a cool 3D product animation for a pair of wireless earbuds. Make it look premium and modern." It came back, untouched, as dark navy space, a glowing halo ring, bloom, particles, spinning buds and a made-up tagline — most of the other prompt's ban list. Prompt B, 448 words of direction, became a studio product film after 15 follow-ups in four review rounds. What changed:

| Adjective | Became |
|---|---|
| premium | materials: satin ceramic at roughness 0.38 with a 0.35 clearcoat, chrome at roughness 0.05, the accent on one surface only |
| cool | a studio: key, fill and rim lights with exact colours and strengths, reflections from an environment built in code, soft contact shadows, no glow anywhere |
| modern | a camera: 30° field of view, never parked, an orbit from 34° to 10° and one push-in on ease-out-expo at 2.0 s |
| animation | beats and springs: 120 BPM, a 3-frame anticipation before the lid springs open at damping ratio 0.6, parts rising at 0.7 with a looser 0.5 follow-through |
| (unspoken defaults) | a ban list by name: bloom, glow orbs, neon, lens flares, particles, spinning turntables, dark backgrounds, text |

### A prompt full of numbers — the liquid-chrome loop

A prompt full of numbers (a 6-second liquid-chrome title loop, 416 words) specifies: the render hooks (`renderAt(t)`, periodic noise, quarter-pixel camera jitter from `frac(t·60)`), the geometry (one signed-distance shape for blob, droplets and text, smooth-min k 0.35 falling to 0.1 as droplets part), the material (chrome F0 0.92, roughness 0.04, three bounces), the studio (softboxes, black flags, a rim strip at an exact azimuth and elevation, a 2° glint strip sweeping 3.3 → 4.1 s), a timeline to the tenth of a second (breathe 3 % every 1.5 s, squash 10 %, stretch 2.4× and pinch into 7 droplets, overshoot 7 %, letters forming 3 frames apart, a 3-bounce wobble at 14 % running through frame 0), the camera (30° lens, dolly 5.6 → 7.2, orbit 7° each way) and the post (bloom threshold 1.0, strength 0.3, vignette 7 %, grain 1.5 % seeded by frame). Every drop, light and camera move came from a number in the prompt or a follow-up.

## The honest numbers

Plan for iteration; it is the method. These are what full quality took, not limits to work within.

- A 45-second hand-painted short that was upfront about its process: 163 model calls, about 6¾ hours (1½ hands-on), ~62 M tokens (96 % cache reads), ~$34 at API list price, a 12-minute render on a laptop.
- A launch-day showreel with 1.7 M views had visible cleanup rounds.
- The liquid-chrome loop: 10 picture follow-ups and 5 sound follow-ups, about 2 h plus 45 min for sound. The directed A/B film: about 30 min for the vague side, 90 for the directed side, 90 for sound (12 sound follow-ups). A 3D mascot loop: 4 follow-ups, about 2 h plus 70 min for sound, none needed for sound.
- A gravitational-lensing explainer: one prompt, then three overnight polish rounds, 5 h 28 min, about $90 at API prices — the polish rounds are the product.
- A design studio's launch video: 3 prompts. A made-up app's launch video (name, logo, UI, animation, soundtrack, all in code) from one prompt in about 8 hours. A 3-minute history film: about 7 400 lines of React and TypeScript, every frame rendered from code, no stock footage.

Receipts convince people; "one prompt" makes them suspicious. Count follow-ups and keep every prompt with the piece (`review.md` § Keep receipts).
