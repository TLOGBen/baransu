# Phase 2 — Draft (草稿)

**Settles:** the direction (art concept, theme, story idea) chosen through the direction funnel (wide → 3 → 1); every shot's 6 : 3 : 1 hierarchy; the story — what the viewer understands, in what order, with what events, in which shots; the cinematography plan — shot sizes, angles, camera moves and how long each move and hold lasts; the art direction across the piece (colour script, light, texture); a seam for every cut; and a first key list. **Produces:** `docs/direction.md` (the 6-3-1 record and style frames), `docs/storyboard.md` (or `STORYBOARD.md` for a long piece), `docs/camera_plan.md`, the colour script, a key list in draft (key cards, `3-keys.md` § The key card), a keys-only animatic with temp sound; for long pieces `ANIMATION_GUIDE.md` and the chapter split. **Gate:** the checklist at the end passes and the animatic reads as a story. **Next:** `3-keys.md`.

This guide is not read whole. Each /draw step (`SKILL.md` § Lane: film) runs `python3 "<skill>/scripts/lookup.py" --step <step-id> --log "<project>/.claude/draw/<slug>"` first, which prints the chapters of this guide and of the library that the step needs; a question that comes up mid-step gets a single-topic lookup (`references/INDEX.md` lists the topics).

Code moves every part at once, at the same speed, by the same amount. A draft with chosen direction, timed *reads* and a camera plan is what turns a set of drawings into something a viewer can follow. Write it before any scene code: fixing a draft costs seconds, fixing a render costs a re-render, and you only find out scene 4 is wrong after the whole thing is animated.

## Draft concepts

- **The direction funnel: wide → 3 → 1.** (Not the 6 : 3 : 1 composition rule below — that one orders every frame.) Generate wide, develop few, commit to one. Six one-line directions cost nothing and escape the first idea; three developed directions show which one holds up as a picture; one is chosen with reasons. Picking among directions beats fixing the first idea the model had.
- **Directions differ in idea, not colourway.** A different hook, motif, world, camera language or ending — never three palettes of one concept.
- **Model the viewer, not the timeline.** Each shot is a list of things the viewer must understand, in order; the reads set the length, not a stopwatch.
- **Every scene has an event.** Something changes between a shot's first and last frame: the subject wants, finds, tries, fails, reacts, gets. "X stands there looking nice" is not a shot. One focal action at a time, staged with a clear silhouette. Pay off what you set up.
- **A shot whose `why:` cannot be written is cut, not polished.**
- **6 : 3 : 1 in every frame.** About 60 % quiet foundation, 30 % supporting structure that leads, 10 % focal anchor — in composition, light, colour, spatial layout, object form and information density alike; taking up the most of the frame and drawing the most attention are two different things (`composition.md`).
- **Stage, life, focus** is the same rule named by job. Every frame is a quiet stage (what fills most of it), a little life (2–3 things that say who uses this place, or the real data), and one focus marked by a single difference. These are jobs, not screen-time shares: in a close-up the focus may fill the frame, and a push-in moves the focus from the stage to the subject. Change the focus with a camera move or a carry, never by lighting up a second thing.
- **The camera is planned, not improvised.** Every move has a reason (a push-in moves the focus, a pan reveals, a crane opens or closes) and a duration; a static camera on a strong composition is a choice too.
- **One piece.** One world (a palette and a setting that carry through, with a colour arc), one thread (beginning, middle, end), the ending rhyming with the opening, motion continuing across cuts, screen direction consistent.

## Draft steps

### 1. Direction funnel, wide → 3 → 1 — `docs/direction.md`

A direction is the art concept and the story idea together: **theme** (what it is about underneath: speed, calm, order out of chaos), **world** (setting, materials, palette family, light), **hook** (the first image), **motif** (what recurs and pays off), **camera language** (the two or three moves it lives by), **ending**.

- **Wide — generate.** Six directions, one line each, all honouring `docs/brief.md` and the style guide's Keep / Leave. Force spread: at least one that breaks the reference's obvious reading, one that is the most literal, one built on a single motif. Cheap: text only.
- **3 — develop.** Pick the three strongest and develop each into: a logline, a world line, a hook, the camera language, the ending, and **one style frame** — a single still at final quality that shows the look (palette, type, texture, light, composition) of that direction's most important moment (`render.mjs still`). Render the three style frames side by side.
- **1 — choose.** Pick one in `docs/direction.md` and write why the other two lost (and what, if anything, it borrows from them). The chosen style frame becomes the look reference for every key.

### 2. Art direction — the colour script and the look per shot

Every line below is decided with the 6 : 3 : 1 rule (`composition.md`): name, per shot, the quiet 60 % (the space foundation), the leading 30 % (the dressing and structure that carry life and point the way), and the 10 % that must be found (the plot focus) — then how light, colour and detail each keep that order. First write what the style must keep, so hierarchy is built in brightness or position rather than by greying out the look.

From the chosen direction, write the look across time:

- **Colour script.** One line (or one small swatch strip) per shot: dominant colour, value (light / dark), where the accent appears, and how colour changes across the piece (the colour arc: e.g. cold and grey in the problem, warm with the accent in the reveal). The accent stays one hue; what changes is everything around it.
- **Light and texture** per shot: key direction, contrast, grain / paper / none, held consistent unless the arc says otherwise.
- **Theme in every shot.** Each shot's line says how it expresses the theme (the motif present, the material, the rhythm). A shot that does not serve the theme is a candidate for cutting.

### 3. The storyboard file — `docs/storyboard.md`

```
Logline: one sentence. [Subject] wants ___, but ___, so ___.
Theme: what it is about underneath.
World: setting, a small palette, light, how colour changes across the piece (the colour script).
Motif: the thing that recurs and pays off.
Arc: the emotional or informational keys across the whole piece, not per shot.
Shots:
  A  0.0–3.2  [transition in: ___]  what's seen · the EVENT · the reaction · camera (from the camera plan)
     frame:  stage ___ (what fills most of it, kept quiet) · life ___ (2–3 things that say who uses this place / the real data) · focus ___ (the one thing this shot is about, and the single difference that marks it)
     enter: ___ (the state the shot starts in)   exit: ___ (the state it hands to the next)   why: ___ (what the viewer knows afterwards that they did not before)
     reads:  0.0–0.8  the first thing the viewer must understand
             0.8–2.0  the next one (where is the viewer's eye when it starts?)
  B  3.2–6.0  [transition: ___]  ...
  [transition out: ___]
```

For a product piece the beats usually run **HOOK** (the problem in five words) → **PROBLEM** (the friction, shown) → **REVEAL** (the UI assembles) → **PROOF** (a real action, a real number) → **CLOSE** (a clean final state and a readable CTA; the last frame strong enough to be the poster).

**Write it in frame ranges when the timing is fixed** (a commissioned spot, a loop on a beat), so every frame is covered and nothing is left undecided. Example, 15 s at 30 fps (450 frames):

| Frames | Seconds | On screen |
|---|---|---|
| 0–89 | 0–3 | three disconnected report cards; headline "Too many tabs." |
| 90–209 | 3–7 | a cursor selects the cards; they move into one shared view |
| 210–359 | 7–12 | the overview settles; headline "One clear view." |
| 360–449 | 12–15 | a readable closing card: "Explore the demo." |

List the exact copy, assets, frame ranges, transitions and sound cues. Read the storyboard back: you should be able to say what the viewer learns before any animation exists.

### 4. Time the reads

- **Write the reads.** For each shot, list in order what the viewer has to understand. Each needs time to find, time to understand, and a moment to register. Small, distant, fast or subtle things take longer than big, central, obvious ones.
- **One read at a time.** Do not start a new read while the last is landing. Two things at once means the viewer sees one of them. Cause, then reaction, in sequence.
- **Fast actions, slow meanings.** A motion can be quick if it is anticipated; what it means needs held time. Move quickly through what does not matter, spend time on what does. That contrast is the rhythm; one constant speed is flat.
- **Lead the eye.** The viewer looks at what moves, is bright, is big, or is being looked at. Before an important read, get the eye there first.
- **Biggest and most-looked-at are two different things.** The stage fills the frame; the focus is often small. Make the small thing findable by the one difference around it, not by making it big.
- **Let the reads set the length.** A shot is as long as its reads need; text needs at least 0.3 s per word + 0.5 s (`springs.md` § Durations). The last read of the piece needs time to land before it ends.
- If a shot's reads do not fit its length, lengthen the shot or cut a read; never squeeze them.

### 5. The cinematography plan — `docs/camera_plan.md`

Plan the camera shot by shot: how each shot is framed, how the camera moves, and how long each move and hold lasts. Start from the chosen direction's camera language (two or three moves, reused); `camera.md` has the named moves and how to draw each.

Under the table, write one `Move:` line per shot, in this fixed format, naming the move by its chapter id in `camera.md` without the `camera-` prefix (`pan`, `tilt`, `dolly`, `zoom`, `tracking`, `orbit`, `crane`, `dolly-zoom`, `rack-focus`, `handheld`, `fpv`, `dutch`, `slow-motion`, `speed-ramp`, `time-lapse`, `freeze-frame`), or `hold` for a still camera:

```
Move: dolly — shot A, 2.4–3.0 s, ui spring
Move: pan — shot B, 0.0–1.8 s, ease-in-out-quart
Move: rack-focus — shot C, 0.4–1.2 s, ease.inOut
```

These lines list the move chapters that are due; each named move's chapter is printed by the step command with that move as a value (`lookup.py --step draft-camera-plan --value move=<name>`, once per move; aliases such as `push-in` resolve) before the line is written. The table's prose may use any words ("push-in", "tracking the cursor"); only the `Move:` lines name chapters. A cut between shots is not a camera move: it goes in `docs/seams.md` (§ 6).

```
Shot  size   angle       lens feel       move (named)        move: start–end, curve / feel     hold        why
A     WS     eye level   normal (24mm)   hold → dolly in     2.4–3.0 s, ui spring               3.0–3.6 s   moves the focus from the desk to the card
B     MS     high 20°    normal          pan right           0.0–1.8 s, ease-in-out-quart        1.8–2.6 s   reveals the second card beside the first
C     CU     eye level   long (70mm)     rack focus          0.4–1.2 s, ease.inOut               1.2–3.0 s   hands attention from the chart to the CTA
```

- **Shot size** (how much of the subject fills the frame): extreme wide (the whole world, the subject tiny), wide (the subject whole, with its place), medium (the subject from the middle up, or one UI region), close-up (one element: a button, a face, a number), extreme close-up (a detail: a cursor tip, a digit). Vary sizes between neighbouring shots; two consecutive shots of the same size and angle read as a jump cut.
- **Angle**: eye level (neutral), high (looking down: overview, smallness), low (looking up: importance), top-down (diagrams, desks, maps), dutch (unease, `camera.md` § 12 Dutch angle).
- **Lens feel**: wide (more space, stronger parallax, near things loom), normal, long (flattened depth, shallow focus, calm). On a canvas this is how much the depth layers separate and how strongly they scale (`camera.md` § The parallax rule); a focal-length readout (`24mm → 70mm`) tells the viewer when it changes.
- **Move and its duration**: one named move per shot at most (or a hold), with its start and end time, its curve or spring, and why. Starting points: a full-frame pan 1.5–3 s; a dolly or push-in settling in ~0.6 s on `ui` (~0.8 s on `heavy`); a rack focus 0.5–1.2 s; a whip 0.25–0.4 s; a dolly zoom 1.5–3 s; a crane or orbit 2–4 s; slow motion and speed ramps for one beat. A move starts a beat before the read it serves and settles on a downbeat. "Slow every zoom to 0.7×" is a longer gap between framings, never a different curve.
- **Holds**: how long the camera is still after each move so the read lands (at least the read's time; text: 0.3 s per word + 0.5 s). A slow 2 % push during a hold keeps the frame alive.
- **Shot length**: typical / shortest / longest, measured from the reference (`docs/style_guide.md`); a fast piece cuts every 1–2 s, a calm one holds 4–6 s.
- **Screen direction and the 180° rule**: pick which way the story travels (left → right reads as forward in left-to-right languages) and keep it; a cursor, a parcel or a character that exits right enters the next shot from the left. Crossing the line (reversing direction) is a choice that needs a neutral shot or a visible camera move across it.
- **Vertical needs a different plan**: 9:16 pans less and tilts more; plan the camera per format, never crop (`pipeline.md` § Formats).

### 6. A transition at every seam

Every seam gets a transition — into the first shot, between every pair, out of the last. Choose one that belongs to the story (a wipe, an iris, a whip pan with a smear, a match cut, a cut on action, a camera move that carries through, a push from paper). A plain cut is fine on action or as a deliberate smash cut. Changes inside a shot are transitions too: props arrive on arcs, never pop in. One vocabulary per film: two or three transitions, reused (a showreel is the exception). `transitions.md` has the vocabulary; the seams are executed in Post.

Write `docs/seams.md` as one `Seam:` line per seam (shots + 1 lines), in this fixed format, naming the transition by its chapter id in `transitions.md` without the `transition-` prefix (`hard-cut`, `match-cut`, `wipe`, `iris`, `whip-pan`, `camera-carry`, `accent-carry`, `brush-wipe`, `jump-cut`, `cross-dissolve`, `smash-cut`, `j-cut`, `l-cut`, …):

```
Seam: iris — in → A, 0.0 s, on the first downbeat
Seam: whip-pan — A → B, 3.6 s, smear 0.3 s toward the incoming card
Seam: match-cut — B → C, 5.4 s, the button becomes the chart's bar
Seam: hard-cut — C → out, 8.0 s, on the last hit
```

Each named transition's chapter is printed by the step command with that seam as a value (`lookup.py --step draft-seams --value name=<name>`) before its line is written; only the `Seam:` lines name chapters, so notes under them may use any words.

### 7. Rhythm — the pacing curve

Sketch the intensity of the piece across time (a line from calm to peak per shot): where it builds, where it peaks, where it breathes. Then check the rules against it:

- **A hook in the first 2 s; frame 0 never empty.** Something new every 2–4 s; a visual payoff every 3–5 s.
- **Snap, then hold.** A change that takes 0.04–0.07 s and then holds reads as intentional; a change that eases over 0.5 s reads as a slideshow transition. Put the ease on the settle, not on the change. Anticipation (a small move the opposite way first), overlap (parts arrive at different times: body first, details 2–3 frames later), and staggered groups (0.05–0.14 s apart) are what separate motion from tweening (`springs.md` § The animation principles).
- **Holds need life:** a breathing ±2 %, a blink every ~3 s, a drifting light band. A frozen frame reads as a bug.
- **Cut on the beat, change the layout on the bar** (every 4 beats); changing everything on every beat wears the viewer out (`beat-grid.md`).
- **Contrast is the rhythm**: fast through what does not matter, held on what does; a flat intensity line means a flat film.

### 8. The timing sheet

One row per shot, in frames as well as seconds (an X-sheet in miniature): shot, start frame, end frame, reads and their frames, camera move frames, hold frames, transition frames, cue frames, beat numbers. At 24 fps one frame is about 42 ms; compute beat frames from time (`n × 60 / BPM`), never by adding rounded frame counts. The animatic and every later phase read their times from this sheet.

### 9. The key list, in draft

From the storyboard, list every key the film will need (every read's end state, every shot's enter and exit, every state in a state list) and start one **key card** per key (`3-keys.md` § The key card): its time, the read it completes, its shot size and framing, its focus and the single difference, its copy. Phase 3 finishes and approves them.

### 10. The beat-sheet variant (short pieces)

For a sub-minute piece, hand-drawn or UI, the storyboard can be a beat sheet (`hand-drawn/workflow.md`, `scripts/hand-drawn/templates/beat-sheet.md`): every beat has a start, a duration, what the viewer notices, action → end state, camera, exposure (ones / twos / hold), and a sound cue. With narration, lock beats to word timestamps, not a stopwatch (`chapters.md` § Narration and lyrics).

### 11. Long pieces: split before drafting chapters

Longer than a minute: write `ANIMATION_GUIDE.md` (palette, type, camera language, transition vocabulary, exposure, line weights, what is banned) and the chapter split now, before any chapter is drafted (`chapters.md`).

### 12. The keys-only animatic, with temp sound

Render one still per shot (`render.mjs stills --at <first frame of every shot>`), or a `seek(t)` that holds each shot's still and hard-cuts between them, and play it at the timing sheet's times with a temp track or a click on the beat (`render.mjs animatic`). It must read as a story, with the pacing curve felt, before any key is refined. Motion added to a weak still is a weak shot that moves.

## Gate checklist

- [ ] the direction funnel: six one-line directions → three developed with a style frame each → one chosen; why the other two lost
- [ ] every shot's 6 : 3 : 1 named (quiet 60 %, leading 30 %, found 10 %) in composition, light, colour and detail; the style's defining features kept
- [ ] theme, world, motif, arc written; the colour script covers every shot
- [ ] every shot: event, reads with times, stage / life / focus, enter, exit, `why:`
- [ ] reads fit their shots; one read at a time; text holds long enough
- [ ] the camera plan: size, angle, lens feel, move with start–end and curve, hold, why — every shot; sizes vary between neighbours; screen direction consistent
- [ ] a hook in 2 s; frame 0 not empty; something new every 2–4 s; the pacing curve has build, peak and breath; the last frame can be the poster
- [ ] a named transition at every seam; two or three in the whole film
- [ ] the timing sheet in frames; beats computed from time
- [ ] a draft key card for every key
- [ ] the keys-only animatic with temp sound reads as a story
