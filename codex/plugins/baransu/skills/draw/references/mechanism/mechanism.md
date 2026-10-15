# Mechanism figures — the object is the explanation

A cross-lane unit: `SKILL.md` § Mechanism figures decides when it applies (a request to understand how or why something works) and which form it lands in (a component by default, a shot in a film, or a still in a diagram). This file is a router, not a method. The method is the vendored Anatomy skill in `../../scripts/anatomy/`, followed step by step; this file is its step table (what to look up before each of the ten steps), the upstream rules $baransu:draw overrides, the checks, how the finished figure joins the component and film forms, and where the performance rules live.

Nothing here is read up front, and no file is read whole. Before each step, run its step command, then do the step (`<skill>` is the absolute path of the skill folder, `<project>` the absolute path of the user's project):

```
python3 "<skill>/scripts/lookup.py" --step <step-id> --log "<project>/.codex/draw/<slug>" [--value fn=<builder> ...]
```

It prints every chapter the step's row names (the table below lists them so you know what to expect) and logs the step to `docs/lookups.log`; `references/steps.json` holds the same steps with their done-when lines, and `scripts/ledger-check.py` checks that each applicable step's command ran and printed its chapters. Any other chapter is looked up when a question comes up that it answers (`lookup.py <topic> --log …`). Inside the upstream files "SKILL.md" means `ANATOMY-SKILL.md`, and every path (`kit/…`, `scripts/…`, `examples/…`, `references/…`) is relative to `../../scripts/anatomy/`.

## The one rule

**The object is the explanation.** No boxes, no arrows, no labels floating in space. Invent a real, well-made thing whose working *is* the concept, and say in one sentence what moves and what that motion means. A queue is a marble run, an LRU cache is a bookcase, a bloom filter is a fruit machine. Every number the figure shows comes from the same model that moves its parts.

## Overrides: where $baransu:draw departs from upstream

These replace the upstream text wherever the two disagree. The upstream files stay unedited (`NOTICE.md` records this override layer).

- **Size is a class name, nothing more.** Upstream workflow step 1 (Figure / Hero / Epic) names the size class, written in the 尺寸 field of the 開工狀態行 (for example `尺寸 Hero`). The class follows the part count and the number of moving systems, not how many mechanisms the idea has: Figure 40–80 parts and one moving system (at most one shader layer); Hero 80–150 parts, or several shader layers, or one turning subject; Epic past that, or many moving systems (a whole vehicle or plant), or turning in more than one subject. No time estimate is stated to the user; the progress clock stays, for progress notes only (next rule). The Epic tier's instruction not to start, to give an estimate, to propose a Hero version and to wait for the user's choice does not apply: an Epic is built directly. Never announce and wait, never propose a smaller tier, never ask the user to choose a size. Trade detail for time only when the user explicitly asked for something quick.
- **The progress clock is kept, for progress notes only.** Step 1's timing stands, as $baransu:draw's own time rule (`SKILL.md` § Principles): a working page that opens in the browser within the first hour, sent to the user without waiting for a reply, then deepened; `date` at the start and at each step; when a step runs past twice what you expected, one progress line — where it stands, what is left — and the build goes on. The clock never becomes a question, a pause or a reason to cut the size.
- **Invent your own object, even when the idea is listed.** The collection (`mechanism-catalog.md`) is a study of how concepts became objects, not a menu: a figure $baransu:draw builds is a new object invented for this request (§ Inventing your own), never a redraw of a published figure, even when the same idea has a row (binary search is not drawn as the lab balance with sixteen brass weights). Borrow the finish and the craft, never the machine.
- **Examples are read for their source, not built by default.** Upstream says to open the closest example before starting. In $baransu:draw an example's source is read when the figure needs an API it shows (§ Study an example, then build with the upstream kit); the closest example is not built or captured by default, because for an idea outside the collection it helps little and its look pulls the figure toward it. When seeing an example run is worth it, it is built only in `<out>/scratch/`, and it never becomes the figure.
- **No whole-file pre-reads.** `ANATOMY-SKILL.md` says to read `references/webgl.md` before writing any shader and `references/craft.md` before designing. Both are cancelled: look up the chapters the current step names (`webgl-*`, `craft-*`, `kit-*`), and any other chapter when a question comes up that it answers.
- **The 4× detail sweep covers the whole drawing at every size.** Upstream scopes it to the subject and mechanism for a Figure; in $baransu:draw every figure gets the full-drawing sweep, in both themes, assembled and apart.
- **Interactive is the default.** Any figure delivered as a component answers pointer and keyboard (upstream workflow step 9 and `motion.md`) without the user writing "interactive". Only a request for a still, or the diagram lane, drops input.
- **WebGL and 3D are chosen by the idea, not by the prompt's words.** When the idea needs fire, exhaust, water, plasma, steam or real lamp light, the figure gets a shader layer (`webgl.md`); when a part turning in depth is the idea (a dial, a turntable, a globe whose axis holds its direction), it gets the 3D mode (`3d.md`). The user does not have to say "WebGL" or "3D". Both remain bound by § Performance below.
- **No questions mid-build.** Real numbers and behaviour are researched and written into the model; the only stop is a fact only the user can supply (their own system's figures, a logo, a named asset), per `SKILL.md`.
- **No publishing.** `references/publish.md` and `scripts/publish.mjs` (not vendored) belong to the upstream community gallery. $baransu:draw never publishes a figure there.
- **Output location and names.** Everything a build writes (the figure's `build.mjs`, `model.mjs`, `live.js`, the component `<name>.html`, `shots/`, `docs/`) lives in `.codex/draw/<slug>/`, never inside the skill; the built file is named for what it shows, never a generic `index` or `page` name.
- **Never build inside the skill, never outside `scratch/`.** An upstream example's `build.mjs` writes its page next to itself, so it is never run in place; when one is built, only the one example you study goes into `<out>/scratch/`, with the `kit/` and `scripts/` folders its imports resolve to (the command in § Study an example), never the whole vendored folder and never into the output folder itself. `ledger-check.py` never scans `<out>/scratch/` or `node_modules/`, so a scratch copy cannot be mistaken for the figure's code; anything outside `scratch/` is scanned as the figure.

## The anatomy step table

The ten upstream workflow steps (`anatomy-workflow`), each with the topics its step command prints and the $baransu:draw step in `references/steps.json` that carries its done-when line. Before step 1, step `mech-catalog-and-example` prints `mech-catalog-index` and `anatomy-examples-table`: read three or four catalog rows near the idea to see how concepts became objects, and note which example's source shows an API the figure will need; the figure itself is invented at step 3.

| # | Upstream step (ANATOMY-SKILL.md § Workflow) | Look up first | $baransu:draw step |
|---|---|---|---|
| 1 | Size it before you start | `anatomy-size-classes`, `mech-overrides` | `mech-size` |
| 2 | Truth first | `anatomy-truth-first`, `walkthrough-truth` | `mech-truth` |
| 3 | Invent the object | `anatomy-invent-object`, `mech-invent-verb-family`, `mech-mapping-template`, `mech-mapping-tests` | `mech-invent-object` |
| 4 | Parts list | `anatomy-parts-list`, `craft-parts-vocabulary`, `craft-anti-patterns` | `mech-parts-list` |
| 5 | Plan the world | `anatomy-plan-world`, `kit-camera`, `craft-camera-composition`; with pipes, cables or turned parts also `craft-round-parts`, `craft-pipes-waypoints`, `craft-contacts-junctions`, `craft-clearance-crossings` | `mech-plan-world`, `mech-route-pipes` |
| 6 | Build geometry once | `anatomy-build-geometry`, `craft-tones`, `mechanism-kit-limits`, and `kit-{fn}` for every kit builder the geometry calls | `mech-build-geometry` |
| 7 | Paint back to front, bottom to top | `anatomy-painters-order`, `craft-painters-order`, `mechanism-draw-order-dynamic-scenes`, `kit-audit-hook` | `mech-painters-order` |
| 8 | Frame it | `anatomy-frame-card`, `kit-card-page` | `mech-frame-card` |
| 9 | Make it live | `anatomy-make-live`, `anatomy-motion-pointer`, `anatomy-motion-keyboard`, `anatomy-motion-vanilla-loop`, `mech-tour-as-seek`, `component-seek-idle-tour`, then `mech-join-{form}` (`mech-join-component` or `mech-join-film`) | `mech-make-live`, `mech-join-lane` (a still: `mech-join-diagram`, `type-exploded`, step `mech-still`) |
| 10 | Verify like a critic | `anatomy-verify-critic`, `verify-audit`, `mechanism-verification-side-effects`, `verify-line-ends`, `verify-capture`, `verify-drive`, `verify-closeups`, `verify-review-checklist`, `verify-common-faults` | `mech-audit`, `mech-line-ends`, `mech-closeups`, `mech-review-checklist` |

When the idea needs them:

- **A shader layer** (before writing any shader, in any form or approach): `webgl-layer-stack`, `webgl-camera-contract`, `webgl-nothing-pops`, `webgl-light-theme`, `webgl-fallback`, `perf-shader-link`, `perf-small-shaders`, `perf-parallel-compile`; checked with `verify-light-theme-shaders`, `webgl-verify`. Steps `webgl-layer`, `webgl-check`.
- **Turning groups** (before any turning group): `3d-model`, `3d-part-kinds`, `3d-painters-order`, `3d-performance`; checked with `verify-orbit`. Steps `mech-3d`, `mech-3d-check`.
- **A React or Next.js destination:** `anatomy-react` and its sections.

**The kit is looked up per tool, never read whole.** `kit.md` is the API: one topic per function row (`kit-cylinder`, `kit-slabOf`, `kit-tubePieces`, `kit-extrude`, `kit-lathe`, `kit-translateAlong`, `kit-fillet`, `kit-recorder`, `kit-settle`, `kit-auditOrExit`, …). Step `mech-build-geometry` prints the row of every builder you name: `--value fn=cylinder --value fn=slabOf …`, one per kit builder `geometry.mjs` calls; `python3 "<skill>/scripts/lookup.py" --list kit` lists them all. Read § Kit limits before choosing builders.

## Study an example, then build with the upstream kit

An example is a source to read, not a picture to start from. When the figure needs an API you have not used — the tour and pointer mapping, an explode with springs, a recorder and audit, a shader layer, a turning group — open the example that uses it (table below) and read its `build.mjs`, `geometry.mjs` and live script for exactly that API. `dial-indicator` is the smallest complete one and usually the most useful. Do not build or capture the closest example by default: for an idea outside the collection it teaches little, and its look pulls the figure toward it.

When seeing an example run is worth it (a motion feel you cannot read from code), build only that one example, only in scratch, never inside the skill and never into the output folder itself. Copy that example's folder and the two folders its `../../kit/` and `../../scripts/` imports resolve to — never the whole vendored `scripts/anatomy/` folder:

```
mkdir -p "<project>/.codex/draw/<slug>/scratch/anatomy/examples"
cp -r "<skill>/scripts/anatomy/kit" "<skill>/scripts/anatomy/scripts" "<project>/.codex/draw/<slug>/scratch/anatomy/"
cp -r "<skill>/scripts/anatomy/examples/<name>" "<project>/.codex/draw/<slug>/scratch/anatomy/examples/"
node "<project>/.codex/draw/<slug>/scratch/anatomy/examples/<name>/build.mjs"     # add --light for the light page
```

A capture of it, when taken, is `shots/example-<name>.png` (a picture, not code the ledger scans). The two React examples are read as source only. Nothing from `scratch/` is delivered, and `ledger-check.py` does not scan it.

| Example | What it is the reference for |
|---|---|
| `dial-indicator` | the smallest complete figure (~300 lines): build script, tour, pointer mapping, keyboard stops |
| `desk-computer` | ~85 solids; text and a picture drawn in the plane of a face (a CRT), power-off collapse |
| `arcade-cabinet` | a Hero cutaway (~240 solids, 15 cables): camera placed so the mechanism stays in view, a coin rolled at true speed, `--audit` |
| `raptor-engine` | dense pipework (`lathe.mjs`, `tube.mjs`), an 11-assembly explode with staggered springs and per-frame re-sort, the full audit, a plume shader |
| `ripple-tank` | two registered WebGL layers driven by a pure physics model, a change travelling through a history texture |
| `turning-dial` | the 3D mode: turn, hinge and free groups, materials, a shader following moving parts; `stress.mjs` for performance |
| `test-rig` (React, read `rig.ts` → `live.tsx`) | the quality bar for the drawing: springs, probe, dial gauge, the walkthrough's figure |
| `spot-plate` (React, read as source) | shapes that morph into each other, one control driving many parts |

Build the figure itself with the upstream kit, imported from the skill (`scripts/anatomy/kit/iso-kit.mjs`, `lathe.mjs`, `tube.mjs`, `audit.mjs`, `gl.mjs`, `turn*.mjs`) and inlined into the page with `scripts/anatomy/scripts/inline-kit.mjs` (`kitScript()`, `glScript()`, `turnScript()`). Import it by path from the figure's `build.mjs` in the output folder; never copy and edit the kit. `references/mechanism/collection/` holds the 52 published figures, indexed by `mechanism-catalog.md`; it is never read whole. Look up three or four catalog rows near the idea (`mech-catalog-index`, then a row's collection page only when it has one) to learn how a concept became an object and what a finished card says; the object for this request is still invented (§ Inventing your own).

## Kit limits

Limits of the upstream kit that a builder otherwise finds by hitting them. Look this chapter up before choosing builders at step `mech-build-geometry`; a new limit found during a build is added here before the run ends.

- **`extrude` has no holes.** A floor outline is one ring; a ring wall (a dial rim, a track, a well) cannot be one `extrude` with an inner hole. Build it from pieces: split the ring into arc segments (each a convex or `convex: false` outline) and depth-sort them like any other parts, or use `lathe` with `hole` when the part is turned. A ring drawn as a filled disc with a second disc painted over the middle breaks the audit and the line-end check.
- **Hashed placements collide.** Many objects placed at hashed or random positions on a ring or grid (keys on a hash ring, items in buckets) will overlap: with a few dozen items on a ring some land within one part's width of each other. Use thin parts (ticks, pins, narrow tabs) that can sit close without intersecting, or pick the names or keys so their positions are spread; never jitter positions by hand to hide a collision the model would produce.
- **Solids are upright prisms.** `slabOf`, `cylinder` and `extrude` stand on the floor (z up); a part tilted out of that plane comes from `prismOf` in a frame, `lathe`, or a `tubePieces` route, not from a rotated prism.
- **A `kit-{fn}` row is a signature, not a tutorial.** For how a builder is used in a finished figure, read it in an example's `geometry.mjs` (§ Study an example).

## Draw order for dynamic scenes

The painter's order of the upstream steps assumes parts that stay in their slots. A figure where parts are added or removed (items arriving in a queue, keys joining a hash ring), change slots (an item moving between buckets) or rotate (a ring or turntable turning) needs an order that is recomputed from the scene, and one the audit can check.

- **Order by footprint, topologically.** For the parts on screen at a moment, build a "drawn before" graph from their floor footprints: A before B when A's footprint lies behind B's along the camera's depth axis where they overlap on screen (the same test `A.settle` makes). Sort that graph topologically; break ties with `depthOf` of the footprint centre. A plain sort by centre depth is wrong for long or wrapped parts (a ring segment, a rail) and flips as they rotate.
- **Wrap what surrounds.** A part that encircles another (a ring around a hub, a cage around an item) is split into a back half and a front half, each ordered on its own.
- **Recompute only on a change of state.** Recompute the order when a part is added, removed or changes slot, and at the rotation angles where two footprints start or stop overlapping (precompute those angles once); between them the order is fixed, which is also what keeps the reorder cheap (`../motion/component.md` § SVG reorder performance).
- **Give the audit the settled order.** For each state the tour reaches, record the parts with `A.recorder` and set the order the page will actually draw (`R.settled`, or the order passed to `A.auditOrExit`) from the same function the page uses, so `--audit` checks the real order of every state, not a hand-tuned static one. Include the states mid-rotation at the overlap-change angles.

## Checks (the mechanism lane check)

All of these run to their pass line before the figure is delivered; the `verify-*` topics say how to read each output.

- `node scripts/motion/doctor.mjs` first (step `preflight`). It reports the Chromium it found as `CHROME_PATH`; export that in the shell, because `capture.mjs`, `drive.mjs` and `lines.mjs` read only `CHROME_PATH`.
- `node build.mjs --audit` ends `audit passed`, saved to `docs/audit.txt` (every figure with pipes, cables, round parts or an explode wires `kit/audit.mjs`; a 3D figure also ends `turn audit passed`, full run, in the background).
- `node "<skill>/scripts/anatomy/scripts/lines.mjs" <name>.html --out shots/lines.png` prints `line ends: 0` on both themes and in every resting pose (`drive.mjs` `["lines"]`, run last: § Verification side effects).
- `capture.mjs` desktop, 390 px, hover, `--times` across the tour, `--reduced`, and `--zoom` 4× crops covering the whole drawing in both themes, assembled and apart; `drive.mjs` for sequences, `["slow", 0.05]` contact sheets across every shader transition, and `--no-webgl`. Read every PNG.
- The upstream review checklist (`verify-review-checklist`), every box, written to `docs/verify_checklist.md`.
- `node "<skill>/scripts/motion/perf-check.mjs" <name>.html` passes (§ Performance).
- As a component, `node "<skill>/scripts/motion/verify-page.mjs" <name>.html --out shots` too; in a film, `render.mjs hash` (§ How it joins $baransu:draw).

## Verification side effects

The verify tools act on the live page, and two of their actions change what later actions see.

- **`drive.mjs` `["lines"]` mutates the page.** The line-end check walks and marks the drawing (it adds its rings to the page, and with an output path captures and then removes them). Put `["lines", …]` last in a drive sequence, or run it in its own `drive.mjs` invocation, never before a `["shot"]` or a sheet that must show the untouched figure.
- **`Escape` starts the resume timer.** Pressing `Escape` (or any key or pointer action) to take the figure over from the idle tour arms the figure's "resume the tour after N s" timer. A capture taken a few seconds later shows the tour moving again. Before shots, stop the timer: preload a stub for it (the "Slow mode doesn't slow timers" note in `verify-drive`), or call the figure's own seek, which cancels it (`../motion/component.md` § Seek and the idle tour), then wait for rest with `["until", …]`.
- **Slow mode does not slow timers.** `["slow", f]` slows the rAF clock, not `setTimeout`; the same resume timer fires mid-sheet unless it is stubbed (upstream `verify.md`).

## How it joins $baransu:draw

The anatomy figure is the drawing; $baransu:draw supplies the lane around it.

- **Component (the default).** The figure is a component file `<name>.html` (`../motion/component.md`): its own `<figure>` holding the anatomy card (`plateHtml`: `Fig n`, title, hint, live readout, legend keys, caption under the card), with no page frame or prose. The caption follows the component rule: it adds a dimension the figure does not show. Inline `ISO_CSS` and `kitScript()` (plus `glScript()` / `turnScript()`) once per file, not once per figure: a second `const smooth` in the same module script is a SyntaxError. Put `class="iso"` on the figure's wrapper and switch its `data-theme` with the root theme; a shader that must follow a theme change takes `uLight` as a per-frame uniform or rebuilds its layer. When the request needs a whole page, $baransu:ui embeds the component (`../lanes/component.md` § Handing a page to $baransu:ui).
- **The idle tour is `seek(t)`.** Write the tour as a pure function of time: `tourAt(t)` gives the targets, and the pose at `t` comes from the model in closed form, or from a deterministic replay of `step()` at a fixed `dt` from 0 to `t`. `seek(t)` writes that pose through the same refs the live loop uses. The figure carries `data-dur` (the tour length) and `data-rest` (the frame that carries the point), the component's scrubber calls the figure's `seek`, and reduced motion shows `data-rest`. The tour's keys are a key sequence (`keys-other-lanes`). Live input (pointer, keyboard, the take-over rules in `motion.md`) is a layer on top that stops the tour and leaves the state where it is. A seek clears the tour's queued future events, cancels the idle resume timer, and replays at a fixed step all the way to `t` (`../motion/component.md` § Seek and the idle tour).
- **Film (the shot).** The machine running is the shot. Expose `window.seek(t)` and `window.timeline()` (or `window.DUR`) so `render.mjs` renders it, and `render.mjs hash` returns matching md5s (no wall-clock time, no `Math.random` without a seed, no state carried between seeks). Shaders draw from `t`, never from a running clock. The card's corners become the film's own type or drop out, per the film's type rules (`../motion/type.md`).
- **Diagram.** A still is the figure at its rest or apart pose, built and checked with the same kit (`--audit`, `lines.mjs`); the exploded or cut-away conventions are in `../diagram/type-exploded.md`.

## Performance

Measured on the collection's turbofan figure: a 38 KB fragment shader that never finished linking on ANGLE D3D11 (Windows Chrome's backend) froze the whole browser, because the synchronous link status call blocks the GPU process that drives every tab. SwiftShader linked it in 2 ms, so a headless default run does not catch it. The rules bind every figure with a canvas, and every page $baransu:ui assembles from more than one heavy component. They are chapters of `../motion/component.md`; look up each one before the step it governs:

| Rule | Topic |
|---|---|
| Shader link ≤ 200 ms on ANGLE D3D11, hard fail above 1 s | `perf-shader-link` |
| About 8 KB of GLSL after the prelude, ≤ 2 nested loops, helpers called at most twice | `perf-small-shaders` |
| Compile through `KHR_parallel_shader_compile`; SVG fallback until ready | `perf-parallel-compile` |
| Start compiling a screen or two early; one offscreen draw before the first visible frame | `perf-warm-up` |
| One heavy figure initialises at a time | `perf-one-heavy-at-a-time` |
| Mount ≤ 200 ms, no later task over 50 ms, frame callback p90 ≤ 4 ms and p99 ≤ 16 ms | `perf-mount-budget` |
| The loop runs only while something moves and is on screen | `perf-loop-while-moving` |
| Redraw only the moving parts; re-sort through one DocumentFragment only when the order changed | `perf-redraw-moving-parts` |
| Many SVG parts reordering: cached, quantised order keys; reorder only on change | `../motion/component.md` § SVG reorder performance |
| No forced layout in observers | `perf-no-forced-layout` |
| DPR capped at 1.5 (1.0 below 480 px), live canvas pixels under ~2 M | `perf-dpr-pixel-budget` |

One addition for mechanism figures: past about 1000 depth-sorted items, precompute the points where the order changes instead of sorting per frame. `scripts/motion/perf-check.mjs` (`perf-check-usage`) measures shader link time, long tasks, frame-callback time, draw calls and rAF callbacks once every figure is off screen, and per-canvas draw time; it runs at device pixel ratio 1, so shader size, parallel compile, warm-up, staggered initialisation, the DPR cap, depth re-sort and observers are checked by reading the code.

## Inventing your own

Upstream workflow step 3 says to invent the object and craft.md shows what a good one looks like; it does not say how to find one. Every $baransu:draw figure is invented this way, including an idea the collection already drew: write this into `docs/mapping.md` before any geometry, and record there the catalog rows read and why the object chosen is not one of theirs.

### 1. Find the idea's verb

Write what the idea *does* as one verb phrase, ignoring its nouns: "files items into slots and piles up on clashes" (hash map), "halves the candidates each try" (binary search), "lets one through per window" (throttle), "only the holder may act" (mutex). The verb, not the subject, picks the machine.

### 2. Pick a mechanism family with that verb

These families cover every figure in the collection; start from the one whose verb matches, then choose a specific, nameable object in it that the collection did not use for this idea.

| The idea's verb | Mechanism family | Objects that have it |
|---|---|---|
| store in slots, evict, look up by position | shelving and filing | bookcase, pigeonholes, drawers, rotary card file, trays in a rack, a chest of drawers sized by bytes |
| wait in order, flow, hand over | conveyance | marble run with an escapement, pneumatic tubes, mail ropeway, conveyor, model railway |
| compare, measure, search | instruments | lab balance, dial gauge, caliper, profile gauge, contour model with survey pins |
| permit, exclude, prove identity | locks and interlocks | pin-tumbler lock, interlock key, two-key strongbox, safety catch |
| limit a rate, smooth, delay | regulators | tank with a pump and relief valve, dashpot, escapement, ratchet and click, pin disc |
| choose by probability | games of chance | roulette wheel with frets, fruit machine reels, lottery drum |
| share space or force | springs and clamps | vise with spring-loaded blocks, sprung carriage, load cell |
| reach, connect, collect | wiring | patch cables on a modular synth, switchboard, track and points |
| transform an input along a curve | cams and followers | lead screw and follower on a bent band, cam shaft, pantograph |
| reorder, merge | handling | chime rack with an overhead traveller, sorting desk, card collator |
| render, compute, pass through stages | bench and shop equipment | plotter with one print head, lens bench, lightbox, die set on guide pillars, studio with lamps |
| convert energy, heat, flow (a real machine) | the machine itself, cut away | engine on a thrust stand, pump cut at the shaft, ladle and mould, reactor in half section |

When the idea is itself a physical machine (an engine, a watch, a reactor), skip the metaphor: draw the real thing, cut away where the mechanism is, on a stand, bench or frame that measures it.

### 3. Map part to meaning, one to one

```
CONCEPT     one sentence: what it does
OBJECT      the machine, one sentence: "When ___ moves, it means ___."
PARTS       idea element → part            (every element of the idea has a part)
            moving part → meaning          (every moving part means something; nothing moves for decoration)
NUMBERS     the true values the model holds: sizes, counts, rates, thresholds (researched, never invented)
INPUT       the reader's verb → the idea's input   (drag = set a rate, tap = send one, press = acquire, key = step)
FAILURE     the case the idea exists to handle, made triggerable: the collision, the overfill without the key,
            the arc from the wrong switching order, the cavitation, the false positive
TOUR        the keys of the idle tour: rest → the normal case → the failure case → settled
READOUT     the live line, in true units: "block 2 · reads 14.0 px"
```

### 4. Test the mapping before building

- **Recognisable.** A stranger names the object at a glance. A "box with slots" fails; a "post-office sorting desk" passes.
- **Plausible.** It could be built: real materials, real joints, parts holding parts.
- **One to one.** Read the PARTS table both ways: no element of the idea without a part, no moving part without a meaning.
- **Honest at the edges.** Run the idea's edge cases through the object. A bloom-filter machine must be able to pay out wrongly (a false positive) and never fail to pay out for a word that was added. A metaphor that shows a property the concept lacks teaches something false; pick another object.
- **The failure is the best moment.** The strongest figures let the reader cause the bug: run two pumps without the key, open the disconnector first, starve the suction. If the failure cannot be shown, the figure explains only the easy half.
- **The lit part is the subject.** Exactly one part carries the accent: the thing whose motion *is* the idea.

Then continue at upstream workflow step 4 (parts list): the table becomes the model (step 2) and the parts groups.

## Pointers kept for other files

Other $baransu:draw references link here by these names; each now points upstream.

- **Drawing rules** — `craft.md` §§ 1–7 and the craft rules in `ANATOMY-SKILL.md` (`anatomy-craft-rules`).
- **Turning in 3D** — `3d.md` (`3d-model`, `3d-painters-order`, `3d-performance`).
- **Verify** — `verify.md` (the `verify-*` topics) and § Checks above.
