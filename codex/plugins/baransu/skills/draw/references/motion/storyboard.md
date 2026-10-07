# Storyboard and timing — model the viewer

Code moves every part at once, at the same speed, by the same amount. A storyboard with timed *reads* is what turns a set of drawings into something a viewer can follow. Write it before any scene code; fixing a storyboard costs seconds, fixing a render costs a re-render.

## The storyboard file

Write `docs/storyboard.md` (or `STORYBOARD.md` for a long piece):

```
Logline: one sentence. [Subject] wants ___, but ___, so ___.
World: setting, a small palette, light, how colour changes across the piece.
Motif: the thing that recurs and pays off.
Arc: the emotional or informational keys across the whole piece, not per shot.
Shots:
  A  0.0–3.2  [transition in: ___]  what's seen · the EVENT · the reaction · camera
     reads:  0.0–0.8  the first thing the viewer must understand
             0.8–2.0  the next one (where is the viewer's eye when it starts?)
  B  3.2–6.0  [transition: ___]  ...
  [transition out: ___]
```

Check it against the rules below before building. If a shot's reads do not fit its length, lengthen the shot or cut a read; never squeeze them.

## Reads: one at a time

- **Write the reads.** For each shot, list in order what the viewer has to understand. Each needs time to find, time to understand, and a moment to register. Small, distant, fast or subtle things take longer than big, central, obvious ones.
- **One read at a time.** Do not start a new read while the last is landing. Two things at once means the viewer sees one of them. Cause, then reaction, in sequence.
- **Fast actions, slow meanings.** A motion can be quick if it is anticipated; what it means needs held time. Move quickly through what does not matter, spend time on what does. That contrast is the rhythm; one constant speed is flat.
- **Lead the eye.** The viewer looks at what moves, is bright, is big, or is being looked at. Before an important read, get the eye there first.
- **Let the reads set the length.** A shot is as long as its reads need. The last read of the piece needs time to land before it ends.

## Every scene has an event

Something changes between a shot's first and last frame: the subject wants, finds, tries, fails, reacts, gets. "X stands there looking nice" is not a shot. One focal action at a time, staged with a clear silhouette. Pay off what you set up.

## Snap, then hold

A change that takes 0.04–0.07 s and then holds reads as intentional; a change that eases over 0.5 s reads as a slideshow transition. Put the ease on the settle, not on the change. Anticipation (a small move the opposite way first), overlap (parts arrive at different times: body first, details 2–3 frames later), and staggered groups (0.05–0.14 s apart) are what separate motion from tweening.

Holds need life: a breathing ±2 %, a blink every ~3 s, a drifting light band. A frozen frame reads as a bug.

## Transitions always

Every seam gets a transition — into the first shot, between every pair, out of the last. Choose one that belongs to the story (a wipe, an iris, a whip pan with a smear, a match cut, a cut on action, a camera move that carries through, a push from paper). A plain cut is fine on action or as a deliberate smash cut. Changes inside a shot are transitions too: props arrive on arcs, never pop in.

## One piece

One world (a palette and a setting that carry through, with a colour arc), one thread (beginning, middle, end), the ending rhyming with the opening, motion continuing across cuts, screen direction consistent.

## Beat sheet variant (short pieces, hand-drawn or UI)

For a sub-minute piece use the beat-sheet form from `hand-drawn/workflow.md` and `scripts/hand-drawn/templates/beat-sheet.md`: every beat has a start, a duration, what the viewer notices, action → end state, camera, exposure (ones / twos / hold), and a sound cue. With narration, lock beats to word timestamps, not a stopwatch.

## The review

You cannot see motion by reading code. Render a contact sheet of every shot's first, middle and last frame; a strip of every fast action and transition (12 consecutive frames); a crop of every face or contact that carries the story. Then read the sheet like a first-time viewer: at each frame, where are they looking, and do they understand it yet? Count the frames each read gets; a read that flashes by in a few frames, or shares its frames with another, will be missed.

Attribution: distilled from `JohnHeibel/ClaudeAnimationBase` ANIMATION_GUIDE (MIT) and `buildwithhanif/claude-animation-skill` references (MIT); the full originals are in `hand-drawn/`.
