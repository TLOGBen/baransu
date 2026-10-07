# The critique loop — make the model look at its own frames

The single habit that separates the work people share from the work they post with "it's a bit mid": render, look, score, fix the worst three, repeat. It applies to every lane; only the "look" tool changes.

## Why it works

The model can read images. A rendered frame is evidence the code is not: text that overlaps during a swap, a dead beat where nothing happens, a node whose label spills out of its box, an accent painted on five things. None of that is visible in source. Reading the frame closes the gap between "the code says it moves" and "a viewer would see it move".

Several rounds are the normal route, not a sign that something went wrong. Public "one prompt" clips that held up under scrutiny were preceded by 100+ model calls and several hours; the honest ones said so.

## The loop

```
render stills ─▶ look (contact sheet / screenshots) ─▶ score 1–10 on the card
      ▲                                                       │
      └──────── fix the 3 worst problems ◀── list them with timestamps / element ids
```

Run at least three rounds before the full render, and stop when every score is 8 or higher. Fix at the module level: split, drop, or regroup; never "fix" a crowded frame by scaling everything down.

Which fix first, when a round scores low:

- the focus cannot be found → cut or dim what competes with it (equal brightness, equal detail); never enlarge the focus or add a second signal
- the frame cannot be read as a space → go back to the big shapes and the shot's still (`motion/storyboard.md`); detail comes last
- the look went bland after cleanup → check the `Keep:` list in `docs/style_guide.md`; hierarchy comes from value and position, not from greying the style away

## How to look, per lane

| Lane | Tool | What it gives |
|---|---|---|
| diagram | `python3 scripts/diagram/self_check.py <file>` then a browser screenshot (`node scripts/motion/verify-page.mjs <file> --selector svg`) | accessible-SVG contract, single-file safety, light + dark + phone captures |
| map | `node scripts/map/bin/archify.mjs finalize … --json` | validate → deliver → strict check → browser check receipt; `visual-check` for captures |
| motion | `node scripts/motion/render.mjs beats` (one frame per beat), `contact` (2 fps), `strip --t <time>` (12 consecutive frames), `phone` (360 px), `hash` (determinism) | the shape of the whole film, pops and overlaps around fast actions, phone legibility, identical re-render |
| page | `node scripts/motion/verify-page.mjs <page.html>` | every figure in light and dark, the full page at phone width, console errors, horizontal-scroll flag |

Open the images and read them. A render that exits 0 proves nothing.

## The scorecard

Score each item 1–10. Judge it the way a demanding director would, not the way its maker would.

| Item | What 8+ looks like |
|---|---|
| Hook in the first 2 s | the single most striking image is already on screen; frame 0 is not empty |
| Readability at phone size | labels survive 360 px wide; nothing below the type floor; nothing the viewer must read sits in the format's safe margins (`--safe` on the sheet) |
| Continuity | the same type scale, palette, screen direction and motion feel in every scene; an element that leaves on the right does not re-enter on the right |
| Motion quality | springs settle, nothing slides linearly, no dead frames, no pops between consecutive frames |
| Variety | something new every 2–4 s; no two consecutive shots use the same technique |
| Composition | the frame reads at three levels: a quiet base that fills most of it, a few supporting elements that lead to the focus, one focus that differs from its surroundings in *one* way (value, the accent, isolation, a clean edge) — not every way; the accent on ≤ 2 things; nothing in the corners by default |
| Brand / fact accuracy | real UI, real data, real names; nothing invented to fill a slot |
| Sound sync | hits land on measured peaks; a cut without a sound reads as a mistake |

For a static diagram, swap the motion rows for the diagram taste gate in `references/diagram/taste-gate.md`: the remove test, the signal test, the six connector rules, the accessibility contract.

## Hunt specifically for

- text overlapping during a swap (content entered before the morph started, or left after the next one began)
- anything sliding instead of easing; a value that restarts its spring instead of summing one per change
- corner labels, frame borders, a centered title on a gradient, everything fading in
- blurry scaled text (`will-change` on something the camera scales)
- a dead beat with nothing happening; a stutter at the loop seam (last frame ≠ first frame, cursor included)
- a legend floating inside the diagram, a diagonal connector, a label touching its stroke
- a second accent colour; a cold grey where the palette is warm
- several things equally bright or equally detailed; a texture or grid that runs edge to edge at the subject's density
- background motion louder than the shot's event; a background that is dead instead of quiet (life is ±2 %, never at the focus's brightness)
- after every camera move or transition on the strip, the eye is not yet on the next read
- a shot whose `why:` in the storyboard is blank or restates the previous shot's
- the last frame alone would not work as the poster (`render.mjs still --t <end>`); a logo on black is a weak close
- the mix without the picture (`checks.sh audio`): a cut or click with no peak on the waveform, an ending that does not resolve, a bed that is a flat band

## Notes like a director

The fix list reads better as director's notes than as bug reports — each is one timestamp, one verb, one target:

- "hard cut here, the fade is a slideshow" · "slow every zoom to 0.7×" · "push in on the button, the viewer is looking there"
- "the wipe fights the motion — flip it" · "carry the accent across, drop the black"
- "hold two more beats before the cut; the read isn't landing" · "the cursor arrives before the beat — move the click to 4.50"
- "type is under the 360 px floor on frame 12" · "two faces plus the accent; the third one goes"

## Record it

Keep `docs/review_log.md` in the output folder: round, scores, the three problems with timestamps or element ids and the evidence (which tile or strip frame shows it), what changed. The user reads the final scores in the completion report; the log is the audit trail that proves the loop ran. A resumed session reads it first and continues from the last logged round; a missing artifact from the film folder (`motion/pipeline.md`) is named before any new work.
