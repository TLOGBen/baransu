# Transitions — every seam is a decision

A film with twenty shots has twenty-one seams. A fade at each one is the slideshow look; a hard cut at each one is a stepped look. The storyboard names a transition at every seam, and the transition belongs to the story: it carries an element across, it moves in the direction the eye is already moving, it lands on the beat.

`assets/motion/motion.js` ships the geometry; the scene code does the drawing. The outgoing scene draws first and the incoming scene draws inside the clip or offset the helper returns, so the seam is a shape, not an alpha.

| Transition | Helper | When it belongs | How it is drawn |
|---|---|---|---|
| Hard cut | none | on action, on a downbeat, to smash into a new world | end one scene at t, start the next at t; nothing else |
| Match cut | none | the same shape or motion continues across the cut (a circle becomes a button, a swipe becomes a slide) | the incoming scene's first frame places its element where the outgoing scene's left it; springs keep velocity by starting with `track` keys that begin at the handoff value |
| Wipe | `wipe(t, t0, dur, W, H, dir)` | moving the eye across the frame; chapter changes | `g.save(); g.beginPath(); g.rect(x, y, w, h); g.clip(); drawIncoming(); g.restore()` |
| Iris | `iris(t, t0, dur, W, H, cx, cy)` | from a point of interest to the whole; endings | clip to `arc(cx, cy, r)`; put `cx, cy` on the thing the viewer is looking at |
| Whip pan | `whip(t, t0, dur, W, dir)` | fast, energetic, between parallel states | outgoing translated by `out`, incoming by `inn`; `g.filter = blur(${blur}px)` on both during the move |
| Push / camera carry | `camera(t, keys, W, H)` | the next state is somewhere in the same space | one camera key per state; the move *is* the transition |
| Accent carry | springs | between any two UI states | the accent element (a button, a bar, a cursor) travels from the old layout to the new one via `track`; never fade to black and back into the accent |
| Push from paper / brush wipe | hand-drawn lane | painterly or hand-drawn pieces | `references/motion/hand-drawn/motion.md` (node-canvas route) |

## Rules

- **Direction matches the eye.** A wipe moves the way the reader reads or the way the last motion went. A wipe against the motion feels like a mistake.
- **Duration from the beat.** 0.25–0.4 s for a wipe or whip; a push from one camera key to the next settles in ~0.6 s on `ui`. Land the end of the transition on a beat or a downbeat, not the start.
- **Something crosses the seam.** The accent, the cursor, a sound, a colour. A transition with nothing carried is a cut with extra steps.
- **No black.** Fading to black between two UI states throws the viewer out; keep the paper and move an element instead. Black is for the very end, if at all.
- **One vocabulary per film.** Pick two or three transitions and reuse them; a different wipe at every seam is a showreel of wipes, not a film. (A showreel is the exception: there, every seam is a new technique on purpose.)
- **Inside a shot too.** Props arrive on arcs or springs, never pop in; a content swap hides behind `swapBlur`.

## Director notes you can write on a contact sheet

"hard cut here" · "slow every zoom to 0.7×" · "push in on the button" · "the wipe fights the motion — flip it" · "iris on the cursor, not the centre" · "carry the accent across, drop the fade" · "hold two more beats before the cut". Each is one line in `docs/review_log.md` and one edit in the scene list.
