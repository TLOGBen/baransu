# Mechanism figures — the object is the explanation

A cross-lane unit: `SKILL.md` § Mechanism figures decides when it applies (a request to understand how or why something works) and which lane it lands in (page by default, a shot in a film, or a still). It maps onto the five phases: size, truth and the invented object are Design; the parts list and mapping table are Draft; the world plan, geometry and rest pose are Keys; motion and the idle tour are Shoot; verification is Post.

Most "how it works" pictures are boxes and arrows: they say the parts exist, not what the parts do, and the reader has to imagine the motion the arrows stand for. A mechanism figure draws the thing itself: **a real, well-made object whose moving parts behave the way the idea does.** A queue is a marble run, an LRU cache is a bookcase, a bloom filter is a fruit machine. The reader understands the idea because they recognise the machine, and every number the figure shows comes from the same model that moves its parts.

Use it on the **page** lane (a figure in an explainer, with a scrubber and, when asked, pointer and keyboard), as a shot in a **motion** film (the machine running is the shot), or as a still in the **diagram** lane (an exploded or cut-away object, `../diagram/type-exploded.md`). `mechanism-catalog.md` lists 52 published ideas with their machines; this file is the method, and § Inventing your own is the guideline for a new one.

## The one rule

**The object is the explanation.** No boxes, no arrows, no labels floating in space. Invent a real thing whose working *is* the concept, and say in one sentence what moves and what that motion means.

A figure fails in two ways:

- **Too abstract.** Stacked plates, floating slabs, labelled boxes: they do not read as anything. Layers become drawers, trays in a rack, plates on guide pillars, cards in a holder.
- **Too flat.** One big slab with a few lines: no volume, no parts, nothing to discover. Break it into a base, a carriage and parts; add a groove, screws, a ruler, a label plate.

The cure for both is the same: a recognisable machine built from many small parts that each do something.

## Writing the request

The prompt is the idea, not the drawing: "explain how an LRU cache evicts entries" is enough, and choosing the bookcase is the work. Three words change what is built, and are used only when the user writes them:

| Word | What it adds |
|---|---|
| **interactive** | the figure answers the pointer and the keyboard (drag, press, hold a key). Without it: a still, or a scrubbable tour on the page lane. |
| **WebGL** | shaders for fire, water, plasma, moving air and light, inside the same camera as the parts |
| **3D** | parts that really turn in depth, re-projected and re-sorted every frame. Slow: hours, not minutes. |

When the user already knows the object, they name it with its true numbers ("a mechanical metronome on a small wooden plinth, swinging at 120 bpm, with a sliding weight you can drag"). When the figure has a destination, they say where ("as React components for our Next.js docs, dark theme"): the build follows that, and this skill's own default is one self-contained HTML file.

## Size it first

Every request lands in one of three sizes. Say which, and roughly how long, before any other work (the plan message, `SKILL.md` spine step 2).

| Size | What it holds | Time |
|---|---|---|
| **Figure** | one mechanism, 40–80 parts, at most one shader layer | 30–90 min; build it without asking |
| **Hero** | a dense object, 80–150 parts, several shader layers or one turning part | 2–4 h; announce it, then build unless the user asked for something quick |
| **Epic** | a whole vehicle, building or plant with many moving systems | 6 h or more; never start it unasked: give the estimate, propose a Hero that keeps the core idea, list what the full version adds |

Whatever the size, a working page opens in the browser within the first hour; the rest of the time deepens it. Note the time at each step, and when a step runs past twice its share, say where it stands. Measured active times from the published figures: a watch movement 1 h 54 min in one pass; a 3D tellurion 1 h 57 min; a rocket engine 38 min to a first working version and 10 h 33 min to right; a turbofan 4 h 41 min to a first build and 14 h after five review rounds. The first version comes fast; the time goes into the second look at four times the size.

## The ten steps

Most of the quality is decided in the first four, before any geometry exists. Write the concept and the parts list down first: once a drawing is on screen it is tempting to polish the wrong machine.

1. **Size it** (above).
2. **Truth first.** Collect the real numbers and behaviour: sizes, counts, thresholds, curves, rates. Write them as one small pure model (`model.js`: state plus `step(state, input, dt)` and `poseOf(state)`). The motion, the readout, the screen-reader text and the caption all read from it, so none of them can disagree. Facts are asked for when missing, never invented (`SKILL.md` red lines).
3. **Invent the object** (§ Inventing your own). One sentence: what moves, and what that motion means.
4. **List the parts.** At least 40, grouped: **base** (plate, feet, groove, corner screws, label plate, ruler strip), **structure** (posts, rails, frame bars, end stops), **mechanism** (carriage, bushings, springs, plunger, needle), **controls** (knurled knob, thumb screw, crown, lever), and **the subject**, the one lit part. Each part sits on another part and has a job.
5. **Plan the world.** World units of about one pixel of the real thing; x and y on the floor, z up. Plans as rounded rectangles `{x, y, w, d, r}` and circles. Choose the camera (§ Drawing rules), then fit the drawing to the card.
6. **Build the geometry once.** Compute every static path ahead of time. Moving parts are built once at rest and moved with a transform; only parts whose shape changes (a compressing spring, a swelling capsule, a turning needle) are rebuilt per frame.
7. **Paint back to front, bottom to top** (§ Drawing rules).
8. **Frame it** in a card (§ The card).
9. **Make it live** (§ Motion).
10. **Verify like a critic** (§ Verify).

## Drawing rules

These are what make it read as a solid, made thing rather than a sketch.

- **One camera, no perspective.** Orthographic, looking down from a corner, so parallel edges stay parallel and a part keeps its size anywhere. The diagram lane's 2:1 dimetric `iso(x, y, z)` (`../diagram/type-exploded.md` § Projection) is the default and lands edges on whole pixels. When the mechanism's face must turn to the viewer, use the general camera with azimuth `A` (45° default, 35–60° to show a long side) and elevation `E` (30° default; ~44° to look into something open, like a tank):
  `x′ = ox + k·(x·sinA − y·cosA)`, `y′ = oy + k·((x·cosA + y·sinA)·sinE − z·cosE)`, with depth toward the viewer `depth = (x·cosA + y·sinA)·cosE + z·sinE`. With `k = scale·√1.6`, one floor unit is one scale unit long at the default view.
- **Solids, not wireframes.** Every part is filled with the paper colour and painted in order, so what is in front hides what is behind. No see-through edges, no dashed hidden lines.
- **Four tones by facing.** Draw only the sides that face the viewer; put each in one of four shades by how squarely it faces the light (the light comes from the viewer's left and turns with the camera: `lit = (n·L + 1)/2`, `shade = floor(lit·4)`), and give tops their own lighter fill. Keep the four shades close, about 3 % apart in luminance.
- **Tone hierarchy.** Base and feet `lo`, structure `mid`, the subject `hi`, and **exactly one `lit` accent**: the part the reader should watch now. Grooves `faint`, minor ticks `lo`, major ticks `mid`, the zero mark `hi`, screws as 0.4–0.55 dots.
- **Monochrome unless colour is the subject** (red, green and blue channels; a hot body's blackbody colour). A fluid is a tint of the figure's own inks, not a new hue.
- **Lines resolve.** Every line ends on a face, another line or a terminal dot. No leader lines, balloons, dimension arrows or floating labels. A seam on a box wraps its visible corners; ticks hang from a ruler strip's edge; a texture that must stop fades out. The only lines that may stop on a bare face are rule lines standing for printed text, a needle's tail and a pointer's tip.
- **Small precise detail, never noise.** Bevels 0.4–1.6, grooves inset 3–5 from an edge, screws with a ring at plate corners, knurls on knobs, ruler ticks every 4–5 units with a major every fifth, a label plate with three rule lines. Every detail belongs to a part; density comes from structure (feet, rails, stops, bushings, knobs), not texture.
- **Detail at 4×.** At 1× it reads as one clear machine. Zoomed to 4×, every region still has something true to find; a bare face or an empty corner is unfinished work.
- **No words inside.** Text lives around the drawing, never on it, apart from at most one tiny engraved label. Text the machine itself displays (a counter, a typed line on a screen) is part of the object: draw it in the face's plane, fit its widest string, clip it to its window.
- **Painter's order.** Base first, then what stands on it; repeated parts sorted by depth, far before near. **Split anything that wraps another part**: a coil spring round a rod is drawn as back half, rod, front half; a frame round a carriage likewise. A moving part is drawn in the slot where it physically sits; if it can pass both in front of and behind a neighbour, split the neighbour or bound the motion. Past a few dozen overlapping parts, measure true depth per overlapping pair rather than tuning order by eye.
- **No pipe or cable passes through anything**, at rest, apart or mid-motion. Lines run beside the structure, cross on straights well apart in depth, and end on a flange, connector or terminal dot.
- **Curves shade smoothly.** A round body is shaded from one continuous curve, never a staircase of flat tone blocks.
- **Volume.** Real thickness, parts standing on parts, a soft halo under the base and under anything lifted.
- **Composition.** The object fills about 55–65 % of the card, centred, clear of the corner labels, and still reads at 390 px wide. Keep one scale across a set of figures.

## The card

A figure sits in a card with four corners: **`Fig n`** top left, a short **title** top right, the **interaction hint** bottom left (`Drag crown ↑ to wind · S slow · E apart`), and the **live readout** bottom right (`120.0 × 32.0 · lean 10.6 px`). Legend keys and a true caption sit under the card; the caption follows the page lane's rule and adds a dimension the figure does not show. On a page with margins, the hint and readout may move into the margin beside the figure so the drawing stands alone.

Colours are tokens with one job each, so a theme is a token set (light, dark, paper, blueprint and sepia all come from the same roles):

| Role | Paints |
|---|---|
| card · paper | the card, and the fill under every solid (keep them equal, so fills hide what is behind without showing as patches) |
| top · shade 0–3 | top faces; side faces from turned furthest from the light (0) to facing it squarely (3) |
| face · lit-top · lit-shade | the body, top and sides of the one lit part |
| hi · mid · lo · faint | the subject's outline; structure, major ticks and engraved labels; base, feet and minor lines (the default); grooves and the faintest guides |
| dot · halo | dot grids and screw heads; the soft shadow under the base and lifted parts (about 0.32 opacity in light, 0.9 in dark) |
| lit | the one accent |
| red · green · blue | only where colour is the subject |
| text · muted · strong | figure number and readout; title and hint; the brightest text drawn |
| weight · mono | every line's width (0.6 px); the corner and engraved-label font (a monospace) |

Design light first: on paper, a glow is ink, not added light (§ Shaders). A cavity that holds light (a furnace mouth, a vessel, a water column) gets its own darker token set (soot, refractory, depth), so a glow has a ground.

## Motion

Calm, time-based and true to the model.

- **On a film or a scrubber, the tour is `seek(t)`.** The idle tour (rest → the action → the result → settled) is a sequence of keys (`../motion/3-keys.md`) whose in-betweens come from the model in closed form, so it renders to video, scrubs, and passes `render.mjs hash`. Live input is an extra layer on the page lane only.
- **Live, motion is time-based, never per-frame.** Take `dt` from the frame timestamp and clamp it to 1/30 s. Input sets a target; the part follows by exponential easing `x += (target − x)·(1 − e^(−dt/τ))` with τ = 0.1–0.3 s (a pointer finger 0.09 s), or by a real spring sub-stepped about 240 times a second, snapping once error and velocity fall below ~5e-4. Parts never snap to the cursor.
- **A level that must arrive without overshoot** (a needle, a reserve, a brightness) rides a critically damped spring. **A one-off event** (a flash, a click, a spark) rides an envelope: a smoothstep attack of 40–120 ms and an exponential decay, computed from the event's age, so overlapping events add and nothing pops.
- **Idle tour.** Starts ~1.4 s after the figure comes into view and loops (the glass-button rig: every 7.6 s: rest, press, pull 80, release, settle). It pauses on hover, focus or press, resumes ~3.6 s after the last input, and drives the same targets the user would. When the user acts mid-tour, stop the tour and leave the state where it is; a step key steps from the value the reader sees, not the tour's target.
- **Slow time and take apart.** A key that slows the world to 1/20 and 1/100 lets the reader watch a fast mechanism (a pallet fork letting an escape wheel through half a tooth); a key or hover that lifts the assemblies apart shows what is underneath. For an explode: one spring per assembly (just under critical: stiffness ~64, damping ~14), starts staggered ~35 ms in an order where whoever is outside leaves first, closing in reverse, depth re-sorted each frame; every part keeps a home and still ends on something when apart.
- **Arming.** If an action needs the machine in a state (assembled before firing), bring it there first, say so in the readout, and start the action only when every spring has arrived.
- **Readout from the parts, not the targets.** It says `taking apart` while springs move and `apart · 11 assemblies` only after; a phase word and its number come from the same instant.
- **Restraint.** Stop the loop when everything has settled or the figure is off screen (IntersectionObserver, rootMargin 120 px; read the newest entry). Under reduced motion, springs become critically damped or jump to targets, no tour runs, and the figure still answers input. Rebuild a rotating part per frame, or precompute enough frames that one step moves at most 0.25 px.
- **Accessibility.** The figure root is focusable, `role="slider"` (or a group of buttons for discrete choices) with an `aria-label` explaining the controls and `aria-valuetext` in words, written when the reader's choice changes, not every frame. Phase changes (`arming`, `main stage`, `cold`) go to a polite live region, never per-frame numbers. Keys: arrows step (Shift for bigger steps), Home and End go to the extremes, Space or Enter presses or toggles, Escape releases. A visible focus ring.

## Three layers

| Layer | When | Rule |
|---|---|---|
| **SVG** (or canvas solids) | nearly always | four tones by facing, painter's order re-solved when parts move apart; redraw only what moves |
| **Shader (WebGL)** | only for what lines cannot draw: fire, exhaust, moving air, water, caustics, lamp light, plasma, steam | if deleting the effect leaves the explanation standing, the effect goes |
| **3D** | only when a part moving in depth is the idea (a globe whose axis keeps its direction, a dial that turns) | still a beta even at its source: one turning subject, the rest static |

### Shaders inside the drawing

- **Stack it:** a back layer with what the effect can cover, the canvas (`pointer-events: none`), a front layer with what covers it. Split a part that is on both sides.
- **Same camera, world space.** Hand the shader the drawing's own projection numbers, so a glow on the floor lands on the floor's lines; size everything in world units.
- **Nothing pops.** Every uniform rides an envelope; a phase change is a crossfade driven by the physical quantity (pressure, temperature), never a flag; every term reaches zero before any bound or canvas edge; a fade-out only gets darker.
- **Light on paper is ink.** Decide the colour the paper should show and solve for the ink, with an alpha floor so a pale core hides the lines behind it. A glow is a saturated body with a pale core and a coloured rim, never a darkened dark-theme colour (that reads as "red ink smoke"). Smoke and steam are light grey; hot bodies follow one blackbody table.
- **Tonemap and dither**; cap the device pixel ratio at 1.5; render only while the effect is active and visible; reduced motion gets one representative still; without WebGL the drawing still reads.

### Turning in 3D

A turn by θ about the vertical is the same picture as the camera at azimuth `A − θ`, because the light turns with the camera: rebuild the camera, not the points. Turning parts are convex, every pair that can overlap gets a separating plane at build time, and each frame the sign of the plane's normal against the view says which is in front; a stable topological sort keyed by the previous order swaps two parts only when it must. Prove it with a sweep over every angle (fine steps for order and for continuity). A small turning figure runs at 60 fps; a 380-part hand ran at about 20.

## Verify

The figure is code the model cannot watch, so every check ends in something readable: a picture, a number, an exit code. Most of the time goes here.

- **Captures.** Desktop, phone (390 px), hover, and several moments of the motion (`node scripts/motion/verify-page.mjs page.html` for the page lane; `render.mjs stills | strip | contact` for a film). Read every PNG.
- **Slow the clock for fast events.** Run the tour at 0.05× and take a contact sheet across every transition: no one-frame flash, no colour switch, nothing cut off.
- **4× crops of every junction, in both themes, assembled and apart**: every flange, clamp, spring, crossing and curved body. Faults hide at 1×: a cable through a duct, a nozzle shaded in steps, a blade folding into a sliver at a cut.
- **Line ends.** In the browser, walk both ends of every drawn line; each must land on a stroke, a dot or an outline within a pixel, or sit under a fill painted after it. Count the ones that float; the count must be 0.
- **Depth order and clearance.** Wherever two parts overlap on screen, the nearer one is drawn later, at rest, apart, and in every frame between; no line passes through a solid. Past a few dozen overlaps, compute it instead of eyeballing (cast a ray through each overlapping pair and compare depths). A pair that cannot be ordered interlocks: fix it with a cut in the geometry, never by nudging an order key.
- **Then look like a critic.** Is it instantly a real object, rich in small parts with volume, every line ending on something? Rewarding at 4×? Does the readout change as things move, in true units? Do keyboard, focus ring and reduced motion work? The audit and the line check are necessary, not sufficient: neither replaces looking.
- **Fresh eyes for big figures.** A Hero or an Epic is built in rounds: a builder, reviewers who each look through one lens and rebuild and re-capture for themselves instead of trusting the builder's report, then a fixer, until a round finds nothing (`/review` dispatches the fresh verifier). Keep a progress file (done, next, open decisions) after every step so a stopped run resumes.

## Inventing your own

The catalog's 52 rows are examples, not a menu. A new idea gets its own machine through these steps; write the result into the plan message before any geometry.

### 1. Find the idea's verb

Write what the idea *does* as one verb phrase, ignoring its nouns: "files items into slots and piles up on clashes" (hash map), "halves the candidates each try" (binary search), "lets one through per window" (throttle), "only the holder may act" (mutex). The verb, not the subject, picks the machine.

### 2. Pick a mechanism family with that verb

These families cover every row in the catalog; start from the one whose verb matches, then choose a specific, nameable object in it.

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

Fill a table before drawing anything; every row is a commitment the figure must keep.

```
CONCEPT     one sentence: what it does
OBJECT      the machine, one sentence: "When ___ moves, it means ___."
PARTS       idea element → part            (every element of the idea has a part)
            moving part → meaning          (every moving part means something; nothing moves for decoration)
NUMBERS     the true values the model holds: sizes, counts, rates, thresholds (asked for if unknown)
INPUT       the reader's verb → the idea's input   (drag = set a rate, tap = send one, press = acquire, key = step)
FAILURE     the case the idea exists to handle, made triggerable: the collision, the overfill without the key,
            the arc from the wrong switching order, the cavitation, the false positive
TOUR        the keys of the idle tour: rest → the normal case → the failure case → settled
READOUT     the live line, in true units: "block 2 · reads 14.0 px"
SIZE        Figure / Hero / Epic, and why
```

### 4. Test the mapping before building

- **Recognisable.** A stranger names the object at a glance. A "box with slots" fails; a "post-office sorting desk" passes.
- **Plausible.** It could be built: real materials, real joints, parts holding parts. Bench instruments, brass, steel, wood and glass in one era read as one world.
- **One to one.** Read the PARTS table both ways: no element of the idea without a part, no moving part without a meaning.
- **Honest at the edges.** Run the idea's edge cases through the object. Does the machine do what the idea does in the failure case, and nothing the idea does not? A bloom-filter machine must be able to pay out wrongly (a false positive) and never fail to pay out for a word that was added. A metaphor that shows a property the concept lacks teaches something false; pick another object.
- **The failure is the best moment.** The strongest figures let the reader cause the bug: run two pumps without the key, open the disconnector first, starve the suction. If the failure case cannot be shown, the figure explains only the easy half.
- **The lit part is the subject.** Exactly one part carries the accent: the thing whose motion *is* the idea (the needle, the capsule, the marble at the escapement).
- **Not from a reference.** A photograph or a style gives the finish, the materials and the mood; the object is invented for the idea, never copied.

### 5. Then the ten steps

Continue at step 4 (parts list) of § The ten steps: the mapping table becomes the model (step 2) and the parts groups.

## Limits

- The model is better at building than at seeing: a part can be right in every number and still look wrong. The fixes that matter come from watching the figure play and saying what feels off; treat the first figure as a draft, then play with it, note what is wrong, and ask again.
- Good is slow. At least forty parts is the floor; when the user needs something quick, offer a Figure, not a Hero.
- 3D costs hours and a long proof run; ask for it only when a part must really move in depth.
