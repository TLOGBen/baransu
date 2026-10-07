# The explainer page — several animated figures on one reading page

When the deliverable is "explain this to me", one video is the wrong shape: a reader wants to scrub, pause, re-read. The explainer page puts 4–8 `seek(t)` figures inside a reading column, each with its own play/pause and time scrubber, each a pure function of time so any instant can be reproduced exactly. `assets/motion/explainer-template.html` is a complete worked example (a 12-step course rendered as six scrubbable figures); copy its mechanics, not its content.

## Mechanics

- One `<figure class="fig" data-fig="<id>" data-dur="8" data-rest="7.4">` per figure: `data-dur` is the loop length, `data-rest` the time shown when paused or under reduced motion (choose the frame that carries the figure's point).
- A `<canvas width="1200" height="675">` inside an `overflow-x: auto` stage; the canvas keeps `min-width: 620px` so a phone scrolls the figure, not the page.
- One draw function per figure in a dictionary `D[id] = (g, t, C) => {…}`; `C` is the resolved colour tokens read from CSS custom properties at draw time, so figures follow the page theme.
- A single `requestAnimationFrame` loop advances only the figures that are visible (IntersectionObserver) and playing; the scrubber sets `t` directly and pauses.
- `prefers-reduced-motion: reduce` starts every figure paused at `data-rest`.
- Canvas sizing: `canvas.width = cssWidth × min(2, devicePixelRatio)`, then `setTransform(scale)` so draw code always works in the 1200×675 design space.
- Redraw everything on `resize`, on theme change (`prefers-color-scheme` media listener and a `data-theme` MutationObserver), and after `document.fonts.ready`.

## Page contract

- Colours as tokens on `:root`, redefined for dark under `@media (prefers-color-scheme: dark)` guarded by `:root:not([data-theme="light"])` and again under `:root[data-theme="dark"]`; `body` sets an explicit background.
- One reading column (~44 rem) for prose; figures break out to ~70 rem.
- A 16 px side gutter at every width; nothing wider than the screen except the figure stage, which scrolls locally.
- Fonts from Google Fonts with real fallback stacks; CJK body text gets a CJK face first.
- Every figure has an `aria-label` describing what the animation shows, a numbered title, and a caption that adds a dimension the figure does not show (a trade-off, a next step), never a restatement of the title.
- Self-contained: inline CSS and JS, no external scripts.

## Build order

1. Outline the page: what each figure must make obvious in one glance (write the caption first; if you cannot, the figure has no point).
2. Draw each figure's *rest frame* first and look at it; then animate.
3. `node scripts/motion/verify-page.mjs page.html` → light and dark captures of every figure, full page at phone width, console errors, horizontal-scroll flag. Fix what it shows. One more look, then deliver.

## What the template demonstrates

Figure types that recur in explainers and are already solved in the template: a pipeline with items flowing stage to stage; a ladder/bar chart with tiles unlocking in sequence; a curve comparison with a moving playhead; a single shape morphing through states with a cursor; a beat/timeline grid with a playhead, waveform and markers; a loop/cycle with a scorecard that fills over rounds. Reuse the drawing helpers (`tx`, `rr`, `arrow`, `spring`, `track`, `swapAlpha`) rather than inventing new ones.
