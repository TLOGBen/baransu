# The prompt ladder — from one line to a director's brief

The viral "one prompt" clips and the 12-hour autonomous runs sit on the same ladder. Climbing it adds very little to the prompt and a lot to the harness: references, a render engine, a state list, a beat grid, a critique loop. The prompt is about 10 % of the result; the rest is what the model has to work with.

| Level | Prompt | What it tests | Harness it needs |
|---|---|---|---|
| L1 one-liner | ~190 characters | the engine | `seek(t)` renderer |
| L2 brand | + product URL, "real screenshots, real logo", "must have music" | assets + sound | screenshots, beat grid, synthesized score |
| L3 reference + state list | reference frame/video/library + a beat-by-beat state list | the idea | `style_guide.md`, shot list, measured beats |
| L4 director's brief | 9 000–19 000 characters, written as a crew | a production | character bible, workflow gates, subagents, critique log |

## L1 — the showreel sentence

"Make a dynamic 15-second motion graphics video that shows what an incredible motion designer you are, like it's your showreel for a résumé. Go all out." Why it works: *showreel* is a genre with known rules (fast cuts, a new technique every shot, the best first); *you* makes the model the subject so it shows technique instead of explaining a product; *15 seconds* is one pass and 6–8 shots; *go all out* multiplies effort.

Its weakness is **brief contagion**: hundreds of people ran the same sentence and the reels rhyme with each other (the public dataset of 1 100+ clips shows the same centred-title / gradient / fade-in defaults recurring). Use L1 to test the pipeline, then move on. A one-liner tests the engine; it never tests the idea, because it contains none.

Variants that shipped and still worked: a 60-second 16:9 reel with an original piano score and "S-tier sound design, no generic synth pads"; an anti-slop guardrail ("avoid frames and text in the corners, the usual giveaways of AI-made video"); a story instead of techniques ("the history of X from Y to today, surprise me with the storyboard"); an agency persona ("as if you were a niche branding studio; one accent colour; every shot a different technique").

## L2 — point it at a product

Three lines did the work in the published examples: the product URL, "use actual product screenshots, logo, assets", "must have music". The model gathers the assets itself (with a browser it can screenshot). Keep one session per brand: the renderer, audio synth and export pipeline already exist, so the second video is faster. Never redraw product UI from imagination; crop and animate the real thing. API keys go in `.env`; the prompt names the variable, never the key.

Template:

```
Make a dynamic 20-second motion graphics video for [PRODUCT] ([URL]), with the energy
of a motion designer's showreel. Go all out.
Assets: real screenshots, the real logo, real colours and fonts, saved to ./assets; list them first.
Story (one beat each, 2–4 s): hook in 5 words of huge type → the UI assembles itself →
three features, each a UI moment with a cursor doing a real action → one number that proves it → logo + CTA.
Sound: original music at 120 BPM synthesized in code; clicks and whooshes on the beat.
Format: 1080×1920 first, then 1:1 and 16:9 from the same timeline.
Before the full render, show me a contact sheet of one frame per beat.
```

## L3 — a reference and a state list

Without a reference the model falls back to its defaults: centred text, gradient background, everything fading in. Naming a style beats describing one; a frame or a video gives pacing, type and transitions to copy.

- **A frame**: attach it; say what to take (palette, type, grain) and what not to take (subject).
- **A video**: extract one frame every 0.5 s with ffmpeg; describe pacing shot by shot before any code.
- **A library**: a folder of the user's own work; write `docs/style_guide.md` from it first. Their own library is a reference nobody else can copy.

Then write the **state list**, not the vibe. The most-bookmarked prompts of the trend were XML specs: `<inputs>` to ask for, `<direction>`, a beat-by-beat `<structure>`, `<build>` rules, `<gotchas>`, `<start>`. The concept behind them: **one shape, never cut** — a single element morphs size, radius and colour from state to state, a cursor drives each change with real clicks, and the last frame equals the first so it loops.

```
<inputs>  product + URL · 8–12 UI states that tell its story · the real data in each · brand colours + fonts + one accent · a royalty-free track near 120 BPM · formats </inputs>
<direction> Product-film UI motion. One container never cuts: every state is the same element changing size, radius and fill while its content swaps behind a short blur. A cursor drives every change. Warm neutral canvas, one accent. Springs with at most a tiny overshoot. Banned: bouncy easing, glows, gradients on UI chrome, particle bursts, dead time. </direction>
<structure> 120 BPM, 8 bars, something happens on every beat. logo → CTA button → email field (typed) → loader → success check → dashboard card → chart draws itself → tooltip → ⌘K palette → toast → logo. </structure>
<build> One HTML file, one canvas, window.seek(t); no CSS transitions, timers, or carried state. Closed-form springs; a value with many targets = sum of one spring per change. Text inside a morphing container enters after the morph starts, leaves before the next. Tab indicators: leading and trailing edges on different springs. Beat grid from the track; start on a downbeat; UI sounds on measured peaks. Headless Chrome at 60 fps, 4 subframes blended for motion blur. </build>
<gotchas> Never will-change on anything the camera scales. The last frame equals the first, cursor position and velocity included. </gotchas>
<start> Ask for the inputs, then show the state list on the beat grid before writing code. </start>
```

Let the model pick the technique: specify the look and the constraints, not the library.

## L4 — the director's brief

A five-minute dictated brief became a 142-second music video after a 12-hour run. The published briefs (9 500 and 19 000 characters) share one skeleton: they do not describe a video, they hire a crew.

- **The film in one line.** The logline and the joke, so every decision can be checked against it.
- **References.** Source video, song, image library, a repo of prior work; what to keep, what to push.
- **Tools and keys.** Skills to load, APIs available (image, video, voice), budget, where docs live. "Spend it economically."
- **Character bible.** Proportions, palette sampled from a sheet, expressions, an identity lock that survives every style change.
- **Beat sheet.** Acts with timestamps; a visual payoff every 3–5 s; a hook in the first 2.
- **Text on screen.** When lyrics/captions go huge, when they sit like subtitles; composition leaves room for them.
- **Workflow gates.** Plan → rig → stills → animatic → full pass → polish → audio → render. Do not skip gates.
- **Critique loop.** Render stills, score them, write the three worst problems, fix, repeat until every score is 8+ (`../critique-loop.md`).
- **Deliverables.** Final MP4, loop check, poster frame, contact sheet, clean source with a README.

The *generate-then-trace* move: an external video model renders base shots with characters and physics, then the code layer redraws the whole video on top, so the viewer only sees the drawn layer. Video models give motion that is hard to hand-code; the code layer gives a consistent, ownable look.

Template (fill every bracket; cut sections the piece does not need):

```
You are the director, animator, sound designer and render engineer for a [DURATION] film made in code.
Treat this as a multi-session production. Don't rush to a final render.
## The film in one line
[LOGLINE. What the viewer should feel at the end.]
## References and inputs
- ./refs/ : [video / frames / image library]. Take the grammar, never the content.
- ./audio/track.wav : use it unchanged. Measure beats with beats.py first.
- APIs in .env: [NAMES]. Budget: [$X]. Be economical.
## Look
[3–5 lines: palette, type, texture, camera language. Banned looks.]
## Beat sheet
0:00–0:02 hook: [the single most striking image]
0:02–0:10 [act 1] … a new visual payoff every 3–5 seconds
[END] the last frame sets up the first frame (loop)
## Workflow, with gates
1. docs/style_guide.md + docs/shotlist.md (every shot: frames, camera, text, SFX). Show the shot list; continue without waiting if no answer in 10 minutes.
2. Stills for every shot → contact sheet → critique.
3. Animatic at 960×540 with placeholder audio; fix pacing before polish.
4. Full animation, polish pass, sound pass, final render.
5. Split work across subagents per chapter; write docs/ANIMATION_GUIDE.md first so every subagent codes in the same style.
## Critique loop (every shot, at least 3 rounds)
Render 3–5 stills, score 1–10 on hook / readability at 360 px / motion / composition / depth / sound sync / polish. Log scores + 3 biggest problems in docs/review_log.md. Fix. Repeat until all are 8+.
## Deliverables
out/final.mp4 · out/loop_check.mp4 · out/poster.png · out/contact.png · README.md
```

## The honest numbers

A 45-second hand-painted short that was upfront about its process: 163 model calls, about 6¾ hours (1½ hands-on), ~62 M tokens (96 % cache reads), ~$34 at API list price, a 12-minute render on a laptop. A launch-day showreel with 1.7 M views had visible cleanup rounds. Budget for iteration; it is the method.

Attribution: the ladder, the showreel analysis and the brief skeleton paraphrase a public X article by @0xMovez (2026-09-27) and the public posts it cites; the dataset figures come from `athemeroy/awesome-opus-5-5-videos` (CC BY 4.0) and `guanmo-ai/awesome-ai-motion` (MIT). Nothing here is copied verbatim beyond the widely-shared one-line showreel prompt.
