# Springs — make motion feel expensive

Cheap motion eases from A to B on a fixed curve. Expensive motion has mass: it accelerates, overshoots a hair, settles. Use closed-form springs everywhere a thing *moves*; keep fixed easing for fades and camera settles where mass would be wrong.

`assets/motion/motion.js` ships the primitives. All are pure functions of t.

## `spring(t, k, d)`

The step response of a damped spring from 0 to 1. `k` is stiffness (how fast), `d` is damping (how much overshoot). It is closed-form, so `seek(t)` stays a pure function of time: no integration, no per-frame state.

Named feels, by the mass of the thing moving:

| Feel | k, d | Use on |
|---|---|---|
| `snappy` | 320, 30 | buttons, toggles, leading edges |
| `ui` (default) | 170, 26 | cards, containers, the camera |
| `heavy` | 120, 24 | big type, 3D objects, logo lockups |
| `playful` | 200, 14 | mascots, stickers — visible overshoot |

Tiny overshoot on UI, none on type, visible only on characters. A spring that bounces three times is a cartoon, not a product.

## `track(t, keys, k, d)` — many targets, one spring per change

The trick most people miss: when a value changes target several times (a cursor, a container's width, a tab indicator), do not restart the spring. Add one spring per change, each starting at its own time:

```
value(t) = v₀ + Σ Δᵢ · spring(t − tᵢ)
```

The motion stays continuous through every retarget, and frame 812 still renders without frames 0–811. `track(t, [[0, 120], [0.5, 640], [1.3, 320]])` is the whole implementation.

## `stretch(t, stops)` — two edges, two springs

A tab indicator or a knob that should elongate while moving: put the leading edge on a stiff spring and the trailing edge on a soft one. The element stretches ahead and catches up by itself; no extra keyframes.

## `swapAlpha(t, tIn, tOut)` — content inside a morphing container

Content enters 0.08 s after its container starts morphing and leaves 0.1 s before the next morph begins. Without this, two labels overlap during every swap, which is the first thing a reviewer notices on a contact strip.

## `loopT(t, dur)` and the seamless loop

Make the last frame equal the first — position, velocity, cursor included — or the loop stutters at the seam. For springs that means every `track()` ends on its starting value with enough time to settle, and the cursor's final key returns to its first position.

## When to use fixed easing instead

`Motion.ease.out / in / inOut / back` for: fades, a camera that settles after a cut, a progress bar whose rate is the data. Mass would lie there.

## The anti-patterns the frame will show you

- a restart instead of a sum: the element snaps back toward its previous start before heading to the new target
- bouncy easing on UI (`ease.back` with a big overshoot where `spring` with d=26 was meant)
- everything on the same spring: the whole frame moves in lock-step; stagger starts by 0.03–0.1 s and vary the feel by mass
- a value that moves linearly because it was written as `lerp(a, b, t/dur)` with no curve
