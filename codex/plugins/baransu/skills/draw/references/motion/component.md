# Components — one interactive figure, delivered on its own

Technique reference for the component form: a single interactive, animated figure (a mechanism, a draggable chart, a scrubbable process, a small animated widget) in one self-contained file. The five motion phases still apply at the figure's scale: the caption and point are its design (Phase 1), its states are the draft (Phase 2), its rest frame is the key (Phase 3), the animation is the shoot (Phase 4), the checks are the post (Phase 5). Each mechanic, each contract rule and each performance rule below is its own chapter; look up the ones the current step names.

## What a component is

A component is the drawing and nothing around it: the card, the figure, the control hint, the scrubber and play / pause, the live readout, the legend or caption that belongs to the figure. It carries no page frame, no headline, no reading column, no paragraphs. A request that needs those (an explainer of X, a tutorial, several figures read together) is still answered by $baransu:draw end to end: $baransu:draw builds and checks each component, then hands them to $baransu:ui in the same turn, which designs the page and embeds them (`../lanes/component.md` § Handing a page to $baransu:ui). The component's own look (palette, line weight, motion feel) is $baransu:draw's decision; the page's look is $baransu:ui's.

Each component is one file named for what it shows: `.codex/draw/<slug>/<name>.html`, where `<name>` is an ASCII slug of the figure's subject (`token-bucket.html`, `merge-sort-chimes.html`), never a generic `index` name. A request for one figure uses the run's slug as the name.

`assets/motion/component-example.html` is a mechanics example (one figure card): open it at the step that builds the component, after the look is decided, take the mechanics below from it, and design the figure, its look and its interaction from the references and the brief — never from the example's look or figure.

## Mechanics

### Figure registration — `data-fig`, `data-dur`, `data-rest`

One `<figure class="fig" data-fig="<id>" data-dur="8" data-rest="7.4">`: `data-dur` is the loop or tour length, `data-rest` the time shown when paused or under reduced motion (choose the frame that carries the figure's point, with every spring settled). The figure has `tabindex="0"` when it takes keys, and an `aria-label` that says what the animation shows.

### The canvas stage

A canvas drawn in a fixed design space (for example 1200 × 675) and scaled to the card's width with `aspect-ratio`, so the figure fits a phone without scrolling the page. A figure whose labels would fall under 12 px at phone width gets a phone layout (fewer parts in view, larger labels) rather than a horizontal scroll; if it must scroll, only its stage scrolls (`overflow-x: auto`), never the document. An SVG figure (a diagram, an anatomy plate) follows the same rule with its `viewBox`.

### The draw dictionary and colour tokens

One draw function per figure, `D(g, t, C)` (a dictionary `D[id]` when a file holds several figures of one component); `C` is the resolved colour tokens read from CSS custom properties at draw time, so the figure follows the theme.

### The visible-only frame loop and the scrubber

A single `requestAnimationFrame` loop advances the figure only while it is playing and visible (IntersectionObserver, 120 px margin); it stops otherwise and is re-armed on visibility or play. The scrubber sets `t` directly and pauses; play / pause is a real `<button>` with an `aria-label`.

### Reduced motion

`prefers-reduced-motion: reduce` starts the figure paused at `data-rest`; input still works and moves the figure without the idle tour.

### Canvas sizing and the device-pixel-ratio cap

`canvas.width = cssWidth × min(1.5, devicePixelRatio)` (1.0 below a 480 px viewport), then `setTransform(scale)` so draw code always works in the design space. The canvas box is read once per resize and cached.

### Redraw triggers — resize, theme, fonts

Redraw on `resize`, on theme change (`prefers-color-scheme` media listener and a `data-theme` MutationObserver on the root), and after `document.fonts.ready`.

### The theme switch and `seek(t)`

The component works in both themes on its own: colour tokens on `:root` for light, redefined for dark (§ Component contract), and a small switch that sets `data-theme` on the root, so a reviewer and a host page can flip it. `window.seek(t)` paints frame `t` and pauses, and `window.DUR` (or `window.timeline()`) gives the length: `render.mjs` can film the component, the checks can land on any instant, and a host page can drive it.

### Seek and the idle tour

A component whose idle tour is driven by `seek(t)` (every mechanism component, any scripted demo) keeps three rules; each was a real bug in a shipped figure.

- **A seek clears the queued future.** The tour's event queue (pending pulses, scheduled key presses, spawned items with a start time) is rebuilt from `t` on every seek: drop every event whose time is after the new `t` and replay the ones before it from a clean state. A queue kept across a backwards seek fires events from the old timeline and the pose no longer matches `t`.
- **A seek cancels the idle timer.** Any pending "resume the tour after N s of no input" timer is cleared by `seek(t)` and by every user input; the scrubber and the checks then own the clock until the timer is re-armed on purpose. A timer left running restarts the tour under a screenshot or a drag.
- **A fixed-step replay never stops early.** When the pose at `t` comes from replaying `step()` at a fixed `dt`, loop until the accumulated time reaches `t` (`while (acc + dt <= t) step(dt)`, then one partial step for the remainder), never a fixed count derived from the frame's variable `dt`. A loop that steps only while the frame's `dt` exceeds 1/60 s stops early on a 120 Hz display or a fast seek, and the pose lags `t`.

Check it: `seek(a)`, `seek(b)`, `seek(a)` give identical readouts and identical captures, and a capture taken 5 s after a seek with no input still shows the pose at that `t`.

## Component contract

- Colours as tokens on `:root`, redefined for dark under `@media (prefers-color-scheme: dark)` guarded by `:root:not([data-theme="light"])` and again under `:root[data-theme="dark"]`; `body` sets an explicit background.
- Usable at phone width: a 16 px gutter, no horizontal scroll of the document at 400 px, controls at least 32 px tall, no label under 12 px.
- Every figure has an `aria-label` describing what the animation shows, and a caption or readout that adds a dimension the figure does not show (a true number, a trade-off), never a restatement of its title.
- Embeddable: no page frame or prose, no global styles beyond `:root` tokens, `body` and the figure's own classes; works in an iframe of any width from 320 px up; fonts are system or bundled stacks with real fallbacks, CJK text gets a CJK face first.
- Self-contained: inline CSS and JS, no external scripts.

## Performance

A heavy component (a mechanism, a shader, hundreds of parts) can freeze the whole browser, not just its tab: on Windows, Chrome compiles WebGL through ANGLE on D3D11, where the shader link runs on the GPU process's main thread, and a 38 KB fragment shader linked synchronously at mount never finished (> 279 s). The same rules hold for several components on one page, which $baransu:ui assembles: each component must already respect them on its own. The rules are the chapters below. `perf-check.mjs` measures shader link time, long tasks, frame-callback time, draw calls and rAF callbacks once the figure is off screen, and per-canvas draw time, and on Windows refuses any renderer without "D3D11" as not evidence; it runs at device pixel ratio 1, so check the others (shader size, parallel compile, warm-up, one heavy figure at a time, observers, pixel budget, idle fps, loop stop while on screen) by reading the code.

### Shader link time on ANGLE D3D11

Shader link ≤ 200 ms on ANGLE D3D11 (hard fail > 1 s). SwiftShader and macOS timings are not evidence: SwiftShader linked that same shader in 2 ms.

### Small shaders

About 8 KB of GLSL at most after the kit prelude, at most two nested loops, no long chains of intersection tests generated from data, no supersampling by calling a large function once per sub-ray, each non-trivial helper called at most twice (HLSL inlines every call; compile time grows faster than the inlined size). A bigger effect is split into small programs on separate canvases or precomputed into a texture.

### Never block on compile

Compile and link through `KHR_parallel_shader_compile` when present and poll `COMPLETION_STATUS_KHR` from the figure's frame loop; keep the SVG or 2D fallback visible until the program is ready, then fade the canvas in. Read `COMPILE_STATUS` / `LINK_STATUS` only after completion is reported. If it is not ready within 2 s, stay on the fallback for the session.

### Warm up before showing

Start the compile when the figure is one or two screens away (a second IntersectionObserver with a wider `rootMargin` than the mount one) and draw once offscreen at 1×1 before the first visible frame; the driver builds its pipeline on the first draw (0.13–1.26 s measured).

### One heavy figure at a time

Inside one component, and across components a host page holds, the next figure's mount, compile or first draw starts only after the previous one's mount task finished (chain on a promise or a frame), even when a scroll lands on both. A lazy iframe counts as a heavy figure.

### Mount and main-thread budget

The mount task (insert the SVG, wire the controller, first layout) ≤ 200 ms; after mount no task longer than 50 ms; per figure, frame-callback time p90 ≤ 4 ms and p99 ≤ 16 ms. Over it: split the SVG insert from the controller setup across frames, cut the path count, or move geometry rebuilds to a Worker.

### The loop runs only while something moves

A figure's frame loop runs only while a spring, an envelope or the tour is above its rest threshold *and* the stage is on screen (120 px margin), and stops within 2 s of rest. Idle motion that never rests (a spinning spool, a pilot flame) runs at ≤ 30 fps.

### Redraw only the moving parts

Rebuild geometry only for parts that changed (more than 0.25 px on screen); cache per-row results by their quantised phase so stationary rows cost nothing. Depth order keeps a static key plus a lift, sorts indices, and re-appends through one `DocumentFragment` only when the order changed.

### No forced layout in observers

Never read `scrollHeight`, `getBoundingClientRect` or `offsetWidth` inside a MutationObserver or ResizeObserver that fires every frame; read sizes once per resize, cache the canvas box, and send at most one message per frame to a parent page.

### Pixel budget

Device pixel ratio capped at 1.5 (1.0 below 480 px wide); the live canvases on screen together under about 2 M pixels; each canvas ≤ 8 ms of GPU time per frame in steady state.

### SVG reorder performance

A pure-SVG figure with many parts that move in depth (a ring of a few hundred keys, items changing slots) blows the frame-callback budget (p90 ≤ 4 ms) as surely as a shader does, through sorting and DOM re-appends rather than the GPU. Keep it inside the budget:

- **Cache the order keys.** Compute each part's depth key once from its static footprint and store it on the part; per frame add only the lift of the parts that moved, never recompute keys from the DOM or from `getBBox()`.
- **Quantise the keys.** Round each moving part's key to a step (a tenth of a part's depth, or the settled slot index) so that sub-pixel motion does not flip the order back and forth every frame.
- **Reorder only on change.** Sort an index array, compare it with the last frame's order, and re-append through one `DocumentFragment` only the run that changed; when nothing changed, touch no node. Attribute writes (transforms) go to moved parts only.
- **Precompute order changes for long tours.** Past about 1000 depth-sorted items, compute the times at which the order changes along the tour once and look them up per frame.

`perf-check.mjs` measures the result (frame-callback p90 / p99 per figure); the caching and quantisation are checked by reading the code.

## Build order

1. Write the caption or readout first: what the figure must make obvious in one glance. If you cannot write it, the figure has no point yet.
2. Draw the *rest frame* first, as a composed still in both themes, and look at it; then animate, with springs by mass (`springs.md`).
3. `node scripts/motion/verify-page.mjs <name>.html --out shots` → light and dark captures of the figure, the file at phone width, console errors, horizontal-scroll flag. Fix what it shows.
4. `node scripts/motion/perf-check.mjs <name>.html` → shader link times, long tasks, frame-callback times, loop stop after rest (no draw call and no rAF callback once the figure is off screen), per-canvas draw time against the measured rules above; read the code for the rest. It must pass alongside `verify-page.mjs`; both are the component's lane check, run on every component file. One more look, then deliver.

## What the example demonstrates

The mechanics `component-example.html` solves and that a component reuses: figure registration (`data-fig`, `data-dur`, `data-rest`), the draw function reading colour tokens at draw time, the visible-only frame loop (stops when paused or off screen, re-armed on visibility or play, a looping figure at ≤ 30 fps), canvas sizing with the DPR cap and the canvas box cached per resize, the scrubber and play / pause, the theme switch, reduced motion, scaling to the design space, `window.seek(t)`, and the `spring` / `track` helpers. Its figure (a dot sprung between three stops) only shows the mechanics running; it is not a figure to draw. The component's form, composition and interaction come from what its caption must make obvious, the references and the brief.

## Mechanism figures as components

When a component must show *how something works*, not only that it happens, draw it as a machine whose moving parts behave the way the idea does: follow `../mechanism/mechanism.md` (the router into the vendored anatomy skill, `../../scripts/anatomy/ANATOMY-SKILL.md`) step by step, each step after its step command (`lookup.py --step <id>`); the published collection is indexed in `../mechanism/mechanism-catalog.md` as a study of how concepts became objects, never as figures to redraw. A mechanism component keeps this contract — a `data-rest` frame, a scrubbable tour, colour tokens read at draw time, reduced motion, the performance rules above — and adds the four-corner card and direct manipulation with pointer and keyboard by default; it is a still only when the user asks for one.
