# Component lane — an interactive figure on its own

A component is one interactive, animated figure in a self-contained file `<name>.html`: a mechanism, a scrubbable process, a draggable chart, a small animated widget. It is theme-aware, usable at phone width, and has no page frame and no prose. `references/motion/component.md` holds the mechanics, the component contract, the performance rules and the build order; this chapter is /draw's route through it, and how a request that needs a whole page is finished through /ui. The steps are in `SKILL.md` § Lane: component.

## Which kind of figure

- **A figure that is a diagram** (an architecture, a flow) that must move or scrub is a seek-overlay SVG built under the diagram lane's rules (`references/lanes/diagram.md`) — never a canvas approximation of one. A component drawn with the diagram system runs the diagram lane's steps as well as this lane's: `diagram-semantic-pattern` (when a behaviour pattern applies), `diagram-plan`, `diagram-layout`, `diagram-markup` (the SVG goes into the component's `<name>.html`), `diagram-check` and `diagram-taste-gate`, each after its step command (`SKILL.md` § Lane: diagram).
- **A canvas figure** is for charts, timelines and abstract motion.
- **A figure that must show how something works** is a mechanism figure (`SKILL.md` § Mechanism figures), interactive with pointer and keyboard by default; it is a still only when the user asks for one.

## One piece, several pieces, or a page

Decide from the content, never by asking:

- **One piece** — the request names one thing to see or play with ("draw how a token bucket works", "an animated sorting widget"): one component, delivered as `<name>.html`, named for the figure.
- **Several pieces** — the request names several figures but no reading around them ("three figures for these three ideas"): one component file per figure, each named for what it shows, each checked on its own.
- **A whole page** — the request needs reading as well as figures: explain X, a tutorial, a walkthrough, several figures meant to be read together (說明頁, 教學, 圖解一整篇). For a component request the form stays component and the brief's `When:` line carries `needs-page`; page delivery never changes another form into component. Build every piece in its own lane first, then hand the page to /ui (below, step `assemble-page`).

When in doubt between several pieces and a page, choose the page if a reader would need sentences between the figures to follow them.

Follow `references/page-handoff.md`, the shared hand-off for all four forms.

## Build order: caption, rest frame, then motion

Write the caption or readout first: one that cannot add a dimension the figure does not show means the figure has no point yet. Then the figure's states and its rest frame (`data-rest`, the frame that carries the point and the one reduced motion shows). Draw the rest frame as a composed still and look at it in both themes; only then animate (a mechanism captures it right after its card, `mech-frame-card`, and only then makes it live; a diagram-system component right after its markup), with springs by mass (`references/motion/springs.md`). The figure runs the motion phases at its own scale (`references/lanes/motion.md` § Motion inside the other forms).

## The mechanics example and the component's look

`assets/motion/component-example.html` is a mechanics example: figure registration, the draw function, the visible-only loop, the scrubber, the theme switch, reduced motion, `seek(t)`. Open it after the step's lookups and take only those mechanics. The component contract (`component.md` § Component contract) requires colours as tokens on `:root`, redefined for dark mode under both guards, with an explicit body background; the token *values*, the type, the figure's design and its interaction come from the references and the brief, never from the example's look.

## Performance is part of done

Heavy figures — a mechanism, a shader, hundreds of parts — follow `component.md` § Performance:

- no synchronous shader compile in mount: parallel compile, a fallback until ready, small shaders that link fast on Windows (D3D11);
- one heavy figure initialised at a time;
- a loop that runs only while something moves and the figure is on screen;
- only the moving parts redrawn;
- device pixel ratio capped at 1.5 (1.0 below 480 px);
- no forced layout inside observers.

Plan these in `docs/perf_plan.md` (step `component-perf-plan`) before writing the figure, not after the first freeze.

## The lane check

For each component file, run `node scripts/motion/verify-page.mjs <name>.html --out shots` until it reports no console errors and no horizontal scroll at phone width, and `node scripts/motion/perf-check.mjs <name>.html` until it exits 0 (on Windows, on a D3D11 renderer). Save their output as `docs/verify-page.txt` and `docs/perf.txt` (one section per file). Then read the code for the performance rules the tools cannot measure. Both scripts start Chromium through `scripts/motion/browser.mjs` `launchChromium()`; never open the file with any other browser tool.
