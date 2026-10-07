# Seek overlay — a diagram-design diagram with a time axis

Two orthogonal questions decide any visual: *what is on this frame* and *how does it change over time*. The diagram system answers the first; the `seek(t)` method answers the second. A seek overlay is the two combined on one SVG: the complete static diagram, plus a decorative layer driven by `window.seek(t)` with a scrubber. The reader drags the timeline and watches the request flow along the real connectors and the real nodes light up in order.

Use it when the user wants to *see something travel* through a diagram they could also read statically — a request path, a propagation, a lifecycle walk. Do not use it to rescue an over-dense or unlabeled diagram; the static twin still has to stand on its own.

## The contract

| Layer | Owns | Rule |
|---|---|---|
| **Semantic** — the diagram | nodes, connectors, labels, legend, `<title>` / `<desc>` | drawn exactly as `README.md` routes it: type reference, connector rules, 4 px grid, accent on ≤ 2, accessible-SVG contract. Never hidden, moved, re-labeled, or re-colored by the overlay. |
| **Decorative** — `<g data-seek-decorative aria-hidden="true">` | guide paths that retrace connectors, a flow token, highlight outlines on node bounds, a clock | `display: none` until the script adds `.seek-ready`; hidden under `prefers-reduced-motion` and in print; carries no meaning the static diagram lacks. |
| **Script** — one `<script data-seek-overlay>` | `window.seek(t)`, `window.timeline()`, the scrubber | pure functions of t: no timers for state, no CSS transitions, no `Math.random`; closed-form springs are fine (they are functions of t). Preview loop only when `!navigator.webdriver && !window.__RENDER__`. |

The upstream `animation.md` modes (`reveal` / `step` / `loop`) stay the right choice for a short ordered explanation that should also work without JavaScript as an *animation*; the seek overlay is for the scrubbing, filmable case, and its static twin is the no-JS fallback.

## Build

1. Draw the static diagram first, from `../../assets/diagram/template.html` or a type example, and run `python3 scripts/diagram/self_check.py` on it until it passes. The time axis is added to a finished diagram, never used to finish one.
2. Copy the overlay parts from `../../assets/diagram/template-seek.html`: the overlay CSS block, the `[data-seek-decorative]` group, the `[data-seek-controls]` div, and the `<script data-seek-overlay>`. Replace `[EDIT]` regions: `DUR`, the `LEGS` (which guide path the token rides, over which window of t) and the `LIGHTS` (which node outline rises, when).
3. Guide paths retrace the semantic connectors exactly (same coordinates, same elbows), so the token never leaves the drawn line. Highlights sit 2 px outside node bounds. Place every hit on the beat if the piece has a tempo (`Motion.beatGrid` in `../../assets/motion/motion.js`, or hand-written windows).
4. Keep the overlay quiet: one token, one highlight at a time, the accent colour only; no glow, no particles, no pulsing that never stops.

## Check

```
python3 scripts/diagram/seek_split.py out/diagram.seek.html   # writes the static twin, runs self_check on it
node scripts/motion/render.mjs hash --html out/diagram.seek.html --selector svg --t 2.0   # DETERMINISTIC (an SVG frame may pass on the ≥ 80 dB PSNR rule: rasterizer noise after an element toggles, DOM identical)
node scripts/motion/verify-page.mjs out/diagram.seek.html --selector svg                 # light / dark / phone, no errors
```

Deliver both files: `<slug>.seek.html` (interactive) and its static twin `<slug>.html` (what exports and no-JS readers get). The type reference's own verifier (`scripts/diagram/repo/verify-*.py`) runs on the twin.

## Export to video

Because the page exposes `window.seek(t)` and `window.timeline()`, the motion toolchain renders it like any film: `node scripts/motion/render.mjs full --html out/diagram.seek.html --selector svg --w 1200 --h 750 --dur 6` gives an MP4 of the request flowing through the diagram; `beats` / `contact` / `strip` work the same way for the critique loop. The video is the overlay's third surface after the scrubber and the static twin; the semantic diagram is identical in all three.

## Anti-patterns

- Overlay elements that are not `aria-hidden` or that duplicate semantic text.
- A guide path that cuts a corner the connector does not cut; the token then floats off the line.
- Highlighting three nodes at once; the reader loses the one thing the frame is about.
- A `seek(t)` that reads the previous frame (counters, last positions): breaks scrubbing and the `hash` check.
- Using the overlay to show an edge the static diagram does not draw.
