# Springs, easing and the motion numbers

Technique reference for how things move. Phase 1 picks the film's tokens from § The numbers; Phase 4 builds every in-between from § The primitives under § Hierarchy and § The animation principles. Each primitive, each number family and each principle is its own chapter.

## Why springs, not curves

A fixed easing curve reads as cheap: the value simply slides from A to B. Motion that reads as expensive behaves like something with mass — it gets going, overshoots a touch, and settles. Use closed-form springs everywhere a thing *moves*; keep fixed easing for fades and camera settles where mass would be wrong. `assets/motion/motion.js` ships the primitives; all are pure functions of `t`.

## The primitives

### `spring(t, k, d)` and the named feels

The step response of a damped spring from 0 to 1. `k` is stiffness (how fast), `d` is damping (how much overshoot), unit mass. Closed-form, so `seek(t)` stays a pure function of time: no integration, no per-frame state, and frame 84 renders without computing frames 0–83.

Named feels, by the mass of the thing moving (`Motion.FEEL`, `Motion.feel(name, t)`):

| Feel | k, d | Damping ratio | Use on |
|---|---|---|---|
| `snappy` | 320, 30 | ≈ 0.84 | micro UI: buttons, toggles, leading edges |
| `ui` (default) | 170, 26 | ≈ 1.0 | panels: cards, containers; the camera (near critical damping — smooth, almost invisible) |
| `heavy` | 120, 24 | ≈ 1.1 | headlines: big type, 3D objects, logo lockups |
| `playful` | 200, 14 | ≈ 0.49 | mascots, stickers — visible overshoot |

Tiny overshoot on UI, none on type, visible only on characters. A spring that bounces three times is a cartoon, not a product. A gather of several cards into one view starts at k 180, d 22 (Remotion's `spring()` with mass 1, stiffness 180, damping 22 is the same); if the cards still bounce when the viewer should be reading, raise the damping.

### `track(t, keys, k, d)` — many targets, one spring per change

When a value changes target several times (a cursor, a container's width, a tab indicator), do not restart the spring. Add one spring per change, each starting at its own time:

```
value(t) = v₀ + Σ Δᵢ · spring(t − tᵢ)
```

The motion stays continuous through every retarget, and frame 812 still renders without frames 0–811. `track(t, [[0, 120], [0.5, 640], [1.3, 320]])` is the whole implementation; it is also how in-betweens are computed from `KEYS` (`4-shoot.md` § 2).

### `stretch(t, stops)` — two edges, two springs

A tab indicator or a knob that should elongate while moving: the leading edge on a stiff spring, the trailing edge on a soft one. The element stretches ahead and catches up by itself; no extra keyframes.

### `swapAlpha(t, tIn, tOut)` and `swapBlur` — content inside a morphing container

Content enters 0.08 s after its container starts morphing and leaves 0.1 s before the next morph begins; `swapBlur` hides the swap behind a brief blur. Without this, two labels overlap during every swap, which is the first thing a reviewer notices on a contact strip.

### `loopT(t, dur)` and the seamless loop

Make the last frame equal the first — position, velocity, cursor included — or the loop stutters at the seam. For springs that means every `track()` ends on its starting value with enough time to settle, and the cursor's final key returns to its first position (`finishing.md` § Loops).

### `cursor(t, keys, clicks)` — the hand the viewer trusts

A product reel is a cursor doing real things. `cursor(t, [[t, x, y], …], [clickT, …])` moves on the `ui` spring through its positions (one spring per leg via `track`, so a retarget mid-flight stays smooth) and returns `{x, y, down, scale}`; draw an arrow or a 2 px ring at `x, y` and let `scale` dip on the press so the click reads at 360 px. Place each click on a beat (`GRID.at(n)`) and give the state change it causes its own spring starting at that click time — the cursor presses, *then* the UI answers, 1–2 frames later. For a loop the last key returns to the first position with time to settle.

### `typed(t, text, t0, cps, seed)` — typing

`typed(t, text, t0, cps, seed)` types with seeded per-character jitter (caret solid while typing).

### `drag(t, grabT, releaseT, held, rest)` — direct manipulation

`drag(t, grabT, releaseT, held, rest)` is direct manipulation — while held the value is exactly what the hand says, on release it springs back from where it was let go.

### `camera(t, keys, W, H, feel)` — re-frame every state

Keys are the rects each state should fill (`[[t, {x, y, w, h}], …]`); the helper tracks every field on one spring and returns `{cx, cy, s}` to apply as `translate(W/2, H/2) · scale(s) · translate(-cx, -cy)`. A push-in is a later key with a smaller rect; a reveal is a larger one. "Slow every zoom to 0.7×" is a longer gap between keys or the `heavy` feel, never a different curve. Nothing the camera scales may carry `will-change`. Parallax, rack focus, handheld and time effects: `camera.md`.

### `words(t, text, t0, gap, feel)` — kinetic type

Per-word springs for kinetic type (`type.md`).

### `wipe`, `iris`, `whip` — transition geometry

The seam helpers; how each is drawn is in `transitions.md`.

### `drawOn(t, t0, dur)` — a line drawing itself

A line drawing itself, on fixed easing.

### `countUp(t, from, to, t0, dur)` — one number that proves it

One number that proves it, decelerating into the real value (`type.md` § Numbers on screen).

### `beatGrid(bpm)` — the beat grid

Beats and bars as functions of time (`beat-grid.md`).

### `rng(seed)` — seeded noise

Seeded noise; never `Math.random`.

### When to use fixed easing instead — `ease.out / in / inOut / back`

`Motion.ease.out / in / inOut / back` for: fades, a camera that settles after a cut, a progress bar whose rate is the data, a wipe or iris, a count-up, a line drawing itself, a lens move (rack focus, dolly zoom). Mass would lie there. This is the one place the skill departs from "replace every easing curve with a spring": a chart that overshoots its own value is a lie about the data.

## The numbers

Give the work curves and frames, the units motion designers talk in. Put the chosen values in one place as the film's tokens.

### Easing curves to name

| Name | cubic-bezier | Use it for |
|---|---|---|
| ease-out-expo | 0.16, 1, 0.3, 1 | text and logo reveals |
| ease-out-quint | 0.22, 1, 0.36, 1 | premium entrances |
| ease-in-out-quart | 0.76, 0, 0.24, 1 | moves and camera pushes |
| ease-in-expo | 0.7, 0, 0.84, 0 | fast exits |
| ease-out-back | 0.34, 1.56, 0.64, 1 | a playful pop with overshoot |

Enter with ease-out, exit with ease-in, and make exits 40–50 % shorter (a 400 ms entrance pairs with a 200 ms exit). Move across the screen with ease-in-out. Linear only for rotation, progress bars and the phase of a loop: linear on a move is the fastest way to make a render look like a render. Camera moves get the softest curves (ease-in-out-quart); objects get the snappier ones.

### Springs as one number: the damping ratio

Every library names its knobs differently; the **damping ratio** translates between all of them: `ζ = d / (2·√(k·m))`.

| ζ | Feels |
|---|---|
| 1.0 | never bounces |
| 0.7–0.85 | premium |
| 0.4–0.6 | playful |
| under 0.3 | a cartoon |

Remotion's default spring (mass 1, damping 10, stiffness 100) is 0.5; react-spring's default (tension 170, friction 26) is 1.0. **Position and size may bounce; opacity and colour never do.** When a prompt names a ratio and a speed instead of k and d, convert: `k = (2π·f)²`, `d = 2·ζ·√k` (f in Hz, unit mass), then `Motion.spring(t, k, d)`; both stay closed-form in `t`.

### Durations

| What | Duration |
|---|---|
| UI feedback | 100–200 ms (100 ms feels instant) |
| UI moves | 200–500 ms |
| hero reveals | 600–900 ms |
| a change that should read as intentional | 0.04–0.07 s, then hold (`2-draft.md` § 7) |
| text hold | at least 0.3 s per word + 0.5 s (a two-word title: 1.1 s) |

For video, say it in frames: at 24 fps one frame is about 42 ms, so a 400 ms move is 10 frames and a 750 ms reveal is 18. During a hold, a slow 2 % push keeps the frame alive while the words stay readable.

### Stagger

| What | Stagger |
|---|---|
| letters | 1 frame apart |
| words | 60–120 ms (`Motion.words` gap 0.04–0.08 s for a hook, `type.md`) |
| list items | 40–80 ms |
| groups and supporting elements | 0.03–0.14 s |

Start the next element when the previous one is 30–50 % done: fully sequential looks robotic, all at once looks cheap.

### Tokens, not inline numbers

`motion.js` exports `FEEL` and `ease`; a film adds its own constants at the top of its file, for example:

```js
const EASE = { enter: 'cubic-bezier(0.16, 1, 0.3, 1)', move: 'cubic-bezier(0.76, 0, 0.24, 1)', exit: 'cubic-bezier(0.7, 0, 0.84, 0)', pop: 'cubic-bezier(0.34, 1.56, 0.64, 1)' };
const MS = { feedback: 150, move: 400, hero: 750, exit: 240 };
const STAGGER = { letter: 1 /* frame */, word: 90, item: 60 };
const dampingRatio = (k, d, m = 1) => d / (2 * Math.sqrt(k * m));
```

"Use only these tokens, no inline numbers" stops values drifting between shots.

## Hierarchy — one hero per shot

A single orchestrated moment lands better than scattered effects. Each shot has **one hero move**; everything else waits, dims to about 40 %, or holds still.

- **Secondary** moves travel 50–70 % as far as the hero and start 100–200 ms after it.
- **Ambient** motion stays under 5 % of the hero's travel, runs on a slow sine and never stops.
- Vary the feel by mass and stagger starts; everything on the same spring moves the whole frame in lock-step.

## The animation principles, in numbers

Five of the twelve classic principles do most of the work in a short loop, and each can be written as frames and sizes. The numbers in the chapters below come from a 3D mascot loop.

### Anticipation

Winds up before the move. Write it as an 11-frame crouch (1.2 × 0.75); a 3-frame wind-up before a lid springs open.

### Squash and stretch

Shows weight and speed. Write it as stretch 0.85 × 1.28 at takeoff, squash 1.25 × 0.7 on landing.

### Overlapping action

Limbs start later than the body. Write it as arms lagging 4 frames, legs 6; details land 2–3 frames after the body.

### Follow-through

Parts keep moving after the body stops. Write it as arms settling at 2.2 Hz, damping 0.22; a looser 0.5 spring on what hangs off.

### Arcs

Motion feels natural. Write it as a flip along a dotted arc, 3.5 high; props arrive on arcs, never pop in.

### Slow in and slow out

Speeds up and settles softly. Write it as a spring back at damping 0.55.

### Timing — frame count sets weight

Write it as 25 frames of air per hop, 18 frames of crouch before the flip.

### Staging, exaggeration and living holds

Staging is the one-hero rule. **Exaggeration** matters more at phone size: push key poses 10–30 % further than feels right, because the feed shrinks everything. Holds need life (breathing ±2 %, a blink every ~3 s); a frozen frame reads as a bug.

## The anti-patterns the frame will show you

- a restart instead of a sum: the element snaps back toward its previous start before heading to the new target
- bouncy easing on UI (`ease.back` with a big overshoot where `spring` with d = 26 was meant)
- everything on the same spring: the whole frame moves in lock-step; stagger starts by 0.03–0.1 s and vary the feel by mass
- a value that moves linearly because it was written as `lerp(a, b, t/dur)` with no curve
- opacity or colour that overshoots
- text that moves while it is being read
