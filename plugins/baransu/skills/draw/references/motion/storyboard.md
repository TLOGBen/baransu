# Storyboard and timing — model the viewer

Code moves every part at once, at the same speed, by the same amount. A storyboard with timed *reads* is what turns a set of drawings into something a viewer can follow. Write it before any scene code; fixing a storyboard costs seconds, fixing a render costs a re-render.

## The brief file

Before the storyboard, `docs/brief.md` separates facts about the product from choices about the film. Facts are fixed; choices are yours to improve — propose a stronger opening or a different camera, do not ask about them. It is short on purpose; the long director's brief in `prompt-ladder.md` is for productions.

```
FILM      goal in one sentence · audience · the one thing to remember · length · primary format (then the other two)
ASSETS    what must be real (screens, logo, colours, fonts, numbers, track) → path in assets/ or manifest.json
          what may be drawn (abstract shapes, placeholder data marked as such)
VISUAL    reference and what to borrow from it · palette (sampled) · type (two faces) · motion feel · banned looks
UNACCEPTABLE  what would make the result wrong even if it looks good (a replaced logo, an invented metric,
          the wrong product name, a cut that hides the feature)
DELIVER   final.mp4 (+ formats) · loop_check · poster · contact sheets · README with the render command
```

A missing asset the brief lists as real is a stop, not a default (`../loop-pauses.md`). The second film for the same brand copies the folder and replaces only this file and `assets/`.

## The storyboard file

Write `docs/storyboard.md` (or `STORYBOARD.md` for a long piece):

```
Logline: one sentence. [Subject] wants ___, but ___, so ___.
World: setting, a small palette, light, how colour changes across the piece.
Motif: the thing that recurs and pays off.
Arc: the emotional or informational keys across the whole piece, not per shot.
Shots:
  A  0.0–3.2  [transition in: ___]  what's seen · the EVENT · the reaction · camera
     frame:  stage ___ (what fills most of it, kept quiet) · life ___ (2–3 things that say who uses this place / the real data) · focus ___ (the one thing this shot is about, and the single difference that marks it)
     enter: ___ (the state the shot starts in)   exit: ___ (the state it hands to the next)   why: ___ (what the viewer knows afterwards that they did not before)
     reads:  0.0–0.8  the first thing the viewer must understand
             0.8–2.0  the next one (where is the viewer's eye when it starts?)
  B  3.2–6.0  [transition: ___]  ...
  [transition out: ___]
```

Check it against the rules below before building. If a shot's reads do not fit its length, lengthen the shot or cut a read; never squeeze them.

A shot whose `why:` cannot be written is cut, not polished. For a product piece the beats usually run HOOK (the problem in five words) → PROBLEM (the friction, shown) → REVEAL (the UI assembles) → PROOF (a real action, a real number) → CLOSE (a clean final state and a readable CTA; the last frame strong enough to be the poster).

Stage, life and focus are jobs, not screen-time shares: in a close-up the focus may fill the frame, and a push-in moves the focus from the stage to the subject. Change the focus with a camera move or a carry, never by lighting up a second thing.

## Reads: one at a time

- **Write the reads.** For each shot, list in order what the viewer has to understand. Each needs time to find, time to understand, and a moment to register. Small, distant, fast or subtle things take longer than big, central, obvious ones.
- **One read at a time.** Do not start a new read while the last is landing. Two things at once means the viewer sees one of them. Cause, then reaction, in sequence.
- **Fast actions, slow meanings.** A motion can be quick if it is anticipated; what it means needs held time. Move quickly through what does not matter, spend time on what does. That contrast is the rhythm; one constant speed is flat.
- **Lead the eye.** The viewer looks at what moves, is bright, is big, or is being looked at. Before an important read, get the eye there first.
- **Biggest and most-looked-at are two different things.** The stage fills the frame; the focus is often small. Make the small thing findable by the one difference around it, not by making it big.
- **Let the reads set the length.** A shot is as long as its reads need. The last read of the piece needs time to land before it ends.

## Every scene has an event

Something changes between a shot's first and last frame: the subject wants, finds, tries, fails, reacts, gets. "X stands there looking nice" is not a shot. One focal action at a time, staged with a clear silhouette. Pay off what you set up.

## Snap, then hold

A change that takes 0.04–0.07 s and then holds reads as intentional; a change that eases over 0.5 s reads as a slideshow transition. Put the ease on the settle, not on the change. Anticipation (a small move the opposite way first), overlap (parts arrive at different times: body first, details 2–3 frames later), and staggered groups (0.05–0.14 s apart) are what separate motion from tweening.

Holds need life: a breathing ±2 %, a blink every ~3 s, a drifting light band. A frozen frame reads as a bug.

## Transitions always

Every seam gets a transition — into the first shot, between every pair, out of the last. Choose one that belongs to the story (a wipe, an iris, a whip pan with a smear, a match cut, a cut on action, a camera move that carries through, a push from paper). A plain cut is fine on action or as a deliberate smash cut. Changes inside a shot are transitions too: props arrive on arcs, never pop in. `transitions.md` has the vocabulary and the helpers (`wipe`, `iris`, `whip`, `camera`).

## Variants, then stills, then motion

Before any scene code, write three storyboards that differ in *idea* (not three colourways): a different hook, a different motif, a different ending. Pick one in the plan message and say why the other two lost. Then render one still per shot (`render.mjs stills --at <first frame of every shot>`) and critique the stills as a contact sheet before anything moves: composition, type size, the one accent, the empty frame 0. Motion added to a weak still is a weak shot that moves.

## From a reference to `docs/style_guide.md`

When the user supplies a frame, a video or a library, write the style guide from it before the storyboard (`bash scripts/motion/checks.sh refs ref.mp4` extracts one frame per 0.5 s into `refs/frames/` plus a tile to read). Ten lines, every one a decision:

```
Palette: paper #…, ink #…, accent #…  (sampled, not guessed)
Type: display face / UI face, hook size as a fraction of frame height, width and scale ratio between them
Composition: where the eye goes first, and what fills the rest
Motion: the verbs it uses (snap, glide, overshoot, cut, hold) mapped to the feel table in springs.md
Shot length: typical / shortest / longest (measured from the reference)
Transitions: the two or three it uses, and the direction they travel
Camera: static / push-ins / whip; how much it moves per shot
Texture: grain, paper, none
Text enters / exits: how (snap, wipe, rise), and where it sits
Sound: cuts on downbeats? SFX per action?
Keep: what to borrow (grammar)      Leave: what not to copy (subject, logo)
```

## One piece

One world (a palette and a setting that carry through, with a colour arc), one thread (beginning, middle, end), the ending rhyming with the opening, motion continuing across cuts, screen direction consistent.

## Beat sheet variant (short pieces, hand-drawn or UI)

For a sub-minute piece use the beat-sheet form from `hand-drawn/workflow.md` and `scripts/hand-drawn/templates/beat-sheet.md`: every beat has a start, a duration, what the viewer notices, action → end state, camera, exposure (ones / twos / hold), and a sound cue. With narration, lock beats to word timestamps, not a stopwatch.

## The review

You cannot see motion by reading code. Render a contact sheet of every shot's first, middle and last frame; a strip of every fast action and transition (12 consecutive frames); a crop of every face or contact that carries the story. Then read the sheet like a first-time viewer: at each frame, where are they looking, and do they understand it yet? Count the frames each read gets; a read that flashes by in a few frames, or shares its frames with another, will be missed.

Attribution: distilled from `JohnHeibel/ClaudeAnimationBase` ANIMATION_GUIDE (MIT) and `buildwithhanif/claude-animation-skill` references (MIT); the full originals are in `hand-drawn/`.
