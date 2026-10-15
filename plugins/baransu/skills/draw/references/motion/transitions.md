# Transitions — every seam is a decision

Technique reference for the cut: Phase 2 chooses a transition for every seam (`2-draft.md` § 6), Phase 4 uses the in-shot ones (carries, camera pushes), Phase 5 executes the seams and writes J- and L-cuts as cue times (`5-post.md` § 1).

A film with twenty shots has twenty-one seams. A fade at each one is the slideshow look; a hard cut at each one is a stepped look. The storyboard names a transition at every seam, and the transition belongs to the story: it carries an element across, it moves in the direction the eye is already moving, it lands on the beat. Each transition below is its own chapter; look up the one the seam uses, then the rules. In `docs/seams.md` every seam gets one line `Seam: <name> — <from> → <to>, <time>, <how>`, where `<name>` is the chapter's id without `transition-` (`whip-pan`, `match-cut`, …) (`2-draft.md` § 6).

The camera moves inside a shot (pan, dolly, rack focus, speed ramp, and the rest of the 24 named moves) are in `camera.md`.

## How a seam is drawn

`assets/motion/motion.js` ships the geometry; the scene code does the drawing. The outgoing scene draws first and the incoming scene draws inside the clip or offset the helper returns, so the seam is a shape, not an alpha.

## Hard cut

- **Helper.** None.
- **When it belongs.** On action, on a downbeat, to smash into a new world.
- **How it is drawn.** End one scene at t, start the next at t; nothing else.

## Match cut

- **Helper.** None.
- **When it belongs.** The same shape or motion continues across the cut (a circle becomes a button, a swipe becomes a slide).
- **How it is drawn.** The incoming scene's first frame places its element where the outgoing scene's left it; springs keep velocity by starting with `track` keys that begin at the handoff value.

## Wipe

- **Helper.** `wipe(t, t0, dur, W, H, dir)`.
- **When it belongs.** Moving the eye across the frame; chapter changes.
- **How it is drawn.** `g.save(); g.beginPath(); g.rect(x, y, w, h); g.clip(); drawIncoming(); g.restore()`.

## Iris

- **Helper.** `iris(t, t0, dur, W, H, cx, cy)`.
- **When it belongs.** From a point of interest to the whole; endings.
- **How it is drawn.** Clip to `arc(cx, cy, r)`; put `cx, cy` on the thing the viewer is looking at.

## Whip pan

- **Helper.** `whip(t, t0, dur, W, dir)`.
- **When it belongs.** Fast, energetic, between parallel states.
- **How it is drawn.** Outgoing translated by `out`, incoming by `inn`; `g.filter = blur(${blur}px)` on both during the move.

## Push / camera carry

- **Helper.** `camera(t, keys, W, H)`.
- **When it belongs.** The next state is somewhere in the same space.
- **How it is drawn.** One camera key per state; the move *is* the transition.

## Accent carry

- **Helper.** Springs.
- **When it belongs.** Between any two UI states.
- **How it is drawn.** The accent element (a button, a bar, a cursor) travels from the old layout to the new one via `track`; never fade to black and back into the accent.

## Push from paper / brush wipe

- **Helper.** The hand-drawn lane.
- **When it belongs.** Painterly or hand-drawn pieces.
- **How it is drawn.** `references/motion/hand-drawn/motion.md` (node-canvas route).

## Jump cut

- **Helper.** None.
- **When it belongs.** Time passes in the same place; restless energy; three or more in a row become a rhythm.
- **How it is drawn.** Keep the framing identical (same camera key) and cut the subject's story time forward (`retime`, `camera.md`); the subject's position jumps. Cut on beats. A near-identical framing that differs by a few percent reads as a mistake: either the same framing exactly, or a scale change of 20 % or more.

## Cross dissolve

- **Helper.** None.
- **When it belongs.** Time has passed, a memory, two places that are one idea.
- **How it is drawn.** Draw the outgoing shot, then the incoming one at `globalAlpha = ease.inOut((t − t0) / dur)` over 0.5–1.5 s. It is not a fade to black (the paper never shows), but it is the slideshow look if it sits at every seam: one or two per film.

## Smash cut

- **Helper.** None.
- **When it belongs.** A hard cut on the biggest contrast: loud to silent, chaos to calm, fast to still.
- **How it is drawn.** A hard cut on a downbeat with the sound cut at the same frame (the music stops, a room tone or one small sound starts). The picture contrast and the sound contrast together are the joke or the shock; either one alone is just a cut.

## J-cut

- **Helper.** None (sound).
- **When it belongs.** Lead the viewer into the next shot by ear: a voice, a crowd, a click before we see it.
- **How it is drawn.** In `window.timeline()`, give the incoming shot's sound cues a time 0.3–1.0 s before the picture cut, so `sfx.mjs` places them under the outgoing picture. Bring the incoming sound up under the outgoing sound, not on top of it.

## L-cut

- **Helper.** None (sound).
- **When it belongs.** Let a moment linger: the last line, a ring-out, an ambience.
- **How it is drawn.** Let the outgoing shot's sound cues run 0.3–1.5 s past the picture cut (cue tails past the seam) and fade them under the new picture. Check the seam with `checks.sh audio`: the mix should have a shape without the picture.

## Rules

### Direction matches the eye

A wipe moves the way the reader reads or the way the last motion went. A wipe against the motion feels like a mistake.

### Duration from the beat

0.25–0.4 s for a wipe or whip; a push from one camera key to the next settles in ~0.6 s on `ui`. Land the end of the transition on a beat or a downbeat, not the start.

### Something crosses the seam

The accent, the cursor, a sound, a colour. A transition with nothing carried is a cut with extra steps.

### No black

Fading to black between two UI states throws the viewer out; keep the paper and move an element instead. Black is for the very end, if at all.

### One vocabulary per film

Pick two or three transitions and reuse them; a different wipe at every seam is a showreel of wipes, not a film. (A showreel is the exception: there, every seam is a new technique on purpose.)

### Transitions inside a shot

Props arrive on arcs or springs, never pop in; a content swap hides behind `swapBlur`.

## Director notes you can write on a contact sheet

"hard cut here" · "slow every zoom to 0.7×" · "push in on the button" · "the wipe fights the motion — flip it" · "iris on the cursor, not the centre" · "carry the accent across, drop the fade" · "hold two more beats before the cut". Each is one line in `docs/review_log.md` and one edit in the scene list.
