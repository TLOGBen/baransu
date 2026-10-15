# Camera — name the move, then draw it

Technique reference for the cinematography: Phase 2 picks the film's camera language and plans each shot's move and duration (`2-draft.md` § 5), Phase 3 sets each key's framing and depth layers (`3-keys.md` § 3), Phase 4 executes the moves between approved framings (`4-shoot.md` § 3), and Phase 5 executes the sound-led cuts (`transitions.md`).

"Make it cinematic" gets the default look. A named move gets exactly that move: "dolly in on the card", "rack focus to the price", "whip pan to the dashboard". This file is the vocabulary: 24 names a director uses, what each one means, when it belongs, and how to draw it on a `seek(t)` canvas with `motion.js`. Write the name into the storyboard's `camera` field and into director's notes; the scene code follows the recipe. Each move is its own chapter; look up the one the shot uses. In `docs/camera_plan.md` every shot gets one line `Move: <name> — shot <id>, <start–end>, <curve or spring>`, where `<name>` is the chapter's id without `camera-` (`dolly`, `rack-focus`, …) or `hold` (`2-draft.md` § 5); the cuts between shots are `Seam:` lines in `docs/seams.md`, named from `transitions.md`.

The 24 come in three groups: how the camera itself moves (01–08), how the shot is taken and how time runs (09–16), and how one shot hands over to the next (17–24, mostly in `transitions.md`).

## The parallax rule — parallax tells the viewer what moved

A 2D canvas can fake a 3D camera because the eye reads camera motion from **parallax**: how differently near and far things move.

- **The camera rotates in place** (pan, tilt, zoom, dutch) → every layer moves or scales by the **same** amount. No parallax.
- **The camera travels** (dolly, tracking, crane, orbit, FPV) → near layers move **more** than far layers. Parallax.

Starting parallax speeds: 1.0 for the foreground, 0.5 for the middle, 0.2 for the background. So the scene is drawn in depth layers, each with a depth `p`: `0` the sky or far backdrop, `1` the subject's plane, above `1` the foreground (posts, leaves, the bezel of a phone held close). A rotating move applies one transform to all layers; a travelling move scales each layer's share of the move by `p`. Get this wrong and a "dolly" reads as a zoom and a "tracking shot" reads as a pan.

```js
// cam = Motion.camera(t, keys, W, H, feel) → {cx, cy, s}; p = layer depth (0 far … 1 subject … >1 near).
// mode 'rotate' (pan, tilt, zoom): every layer takes the whole move. mode 'travel' (dolly, track, crane): share by depth.
function layerCam(g, cam, p, W, H, mode = 'travel') {
  const k = mode === 'rotate' ? 1 : p;
  const s = 1 + (cam.s - 1) * k;
  const cx = W / 2 + (cam.cx - W / 2) * k, cy = H / 2 + (cam.cy - H / 2) * k;
  g.translate(W / 2, H / 2); g.scale(s, s); g.translate(-cx, -cy);
}
// per frame: for (const L of layers) { g.save(); layerCam(g, cam, L.p, W, H, mode); L.draw(g, t); g.restore(); }
```

Keep UI overlays, captions and the readout outside every camera transform (`hand-drawn/motion.md` § Camera). Nothing the camera scales carries `will-change` (`pipeline.md`).

## Group 1 — how the camera moves (01–08)

### 01 Pan

- **What it is.** The camera turns left or right on the spot.
- **When it belongs.** Reveal what is beside the subject; follow a gaze; scan a wide UI.
- **How to draw it.** `camera()` keys that shift `x` only, `mode 'rotate'`: all layers translate together. Slow: a full-frame pan over 1.5–3 s. A readout like `−18°` sells it.

### 02 Tilt

- **What it is.** The camera turns up or down on the spot.
- **When it belongs.** Reveal height (a tower, a tall list, a chart's peak); go from detail to sky.
- **How to draw it.** Keys that shift `y` only, `mode 'rotate'`. The horizon slides through the frame.

### 03 Dolly in / out

- **What it is.** The camera travels toward or away from the subject.
- **When it belongs.** Intimacy, emphasis, "this is the thing". The default push-in.
- **How to draw it.** A smaller rect key on the subject, `mode 'travel'`: the subject grows, the backdrop barely moves, the foreground grows fastest and can leave the frame. Feel `ui` or `heavy`.

### 04 Zoom in / out

- **What it is.** The lens changes focal length; the camera stays.
- **When it belongs.** Flat, observational, slightly mechanical; a snap zoom for comedy or alarm.
- **How to draw it.** The same rect key with `mode 'rotate'`: every layer scales by the same factor, so nothing slides past anything. Show a focal-length readout (`24mm → 70mm`) if the viewer should feel the lens.

### 05 Tracking shot

- **What it is.** The camera travels alongside a moving subject.
- **When it belongs.** Follow a journey: a cursor across a flow, a parcel through a pipeline.
- **How to draw it.** Key `cx` to the subject's `x` with lag (`track()` on the subject's path, feel `ui`), `mode 'travel'`: the subject holds its frame position, the backdrop drifts, foreground posts (`p ≈ 1.6`) whip past. Render with `--sub 4` so the near posts blur.

### 06 Orbit (arc shot)

- **What it is.** The camera circles the subject, which stays centred.
- **When it belongs.** Present a product or a hero object from several sides; a moment of reveal.
- **How to draw it.** A 2D orbit is parallax plus a turn: offset each layer horizontally by `R · sin θ · (1 − p)` (behind the subject moves with the camera, in front moves against it), squash the ground ellipse under the subject, and swap the subject's drawing to its side view past ~60°. More than ~90° needs real 3D (`../mechanism/mechanism.md` § Turning in 3D).

### 07 Crane up / down

- **What it is.** The camera rises or falls vertically, often tilting to keep the subject.
- **When it belongs.** Open a scene from above, or end one by lifting away to the whole.
- **How to draw it.** Travel in `y` with `mode 'travel'`, and move the horizon line in the frame the opposite way (rise → horizon drops). A height readout (`↑ 1.4m`) helps. Pair with a slight counter-tilt so the subject stays put.

### 08 Dolly zoom (Vertigo)

- **What it is.** The camera travels back while the lens zooms in (or the reverse): the subject keeps its size, the background stretches or shrinks.
- **When it belongs.** Realisation, dread, a world shifting under a fixed subject. Once per film, at most.
- **How to draw it.** Hold the subject layer at scale 1. Scale every other layer about the subject's ground point by `1 + (k − 1) · (1 − p)`, with `k` running 1 → 1.6 over 1.5–3 s on `Motion.ease.inOut` (a lens move, not a mass). Behind (`p < 1`) grows, in front (`p > 1`) shrinks.

## Group 2 — how the shot is taken and how time runs (09–16)

### Two clocks — story time and `retime`

Moves 13–16 change how fast **story time** runs while the film's own time `t` keeps going. Keep the two apart: the camera, the cursor's settle and the overlays run on `t`; the action runs on `st = retime(t, keys)`. A freeze frame can then push in while the action stands still, the same split `hand-drawn/motion.md` makes between drawing exposure and the camera.

```js
// keys: [[t0, r0], [t1, r1], …]: the playback rate at each time, linear between keys, constant outside.
// Returns story time. Continuous at every key, so nothing jumps; rate 0 holds (freeze).
function retime(t, keys) {
  let [pt, pr] = keys[0], acc = Math.min(t, pt) * pr;
  if (t <= pt) return acc;
  for (const [kt, kr] of keys.slice(1)) {
    const e = Math.min(t, kt), re = pr + (kr - pr) * (e - pt) / (kt - pt);
    acc += (e - pt) * (pr + re) / 2;
    if (t <= kt) return acc;
    [pt, pr] = [kt, kr];
  }
  return acc + (t - pt) * pr;
}
```

A rate key change is a ramp, not a step: put two keys 0.1–0.3 s apart (`[1.0, 2.4], [1.3, 0.25]`) so the speed eases. The final `window.timeline()` cues must use story-time positions mapped back to `t`, or the click sounds land at the wrong frame.

### 09 Rack focus

- **What it is.** Focus shifts from a near subject to a far one (or back) inside one shot.
- **When it belongs.** Move the viewer's attention without a cut: from the flower to the person, from the field to the button.
- **How to draw it.** Two or more depth layers; blur each by `maxBlur · |p − focus(t)|` (`g.filter = 'blur(…px)'`, `maxBlur` 8–12 px at 1080), with `focus` moving between the two depths on `Motion.ease.inOut` over 0.5–1.2 s. Focus brackets (`[ ]`) on the sharp subject make it legible. Blur each layer once into an offscreen canvas per frame; `ctx.filter` on many small draws is slow.

### 10 Handheld

- **What it is.** The camera is held, not mounted: a small, constant, organic drift.
- **When it belongs.** Documentary, urgency, "this is real"; never on a UI the viewer must read precisely.
- **How to draw it.** A seeded sum of slow sines as the outermost camera transform (below). Amplitude 4–8 px and 0.3° at 1080; double it for urgency. Overlays stay steady.

```js
// Handheld: deterministic (seeded), smooth (sum of slow sines), returns an offset for the outermost transform.
function handheld(t, seed = 7, amp = 1) {
  const r = Motion.rng(seed), TAU = Math.PI * 2;
  const axis = (size) => {
    let v = 0;
    for (const [f, w] of [[0.31, 0.6], [0.73, 0.3], [1.37, 0.1]]) v += w * Math.sin(TAU * f * (0.8 + 0.4 * r()) * t + TAU * r());
    return v * size * amp;
  };
  return { x: axis(6), y: axis(4), rot: axis(0.006) };
}
// g.translate(W/2 + h.x, H/2 + h.y); g.rotate(h.rot); g.translate(-W/2, -H/2);
```

Seeding a fresh `rng` inside the call keeps every frequency and phase fixed for the whole film, so `seek(t)` stays a pure function of `t` (`render.mjs hash` passes).

### 11 FPV (drone)

- **What it is.** A first-person drone: fast, low, banking through the space.
- **When it belongs.** Energy, a fly-through of a big system, an opening that dives in.
- **How to draw it.** A fast dolly toward a vanishing point (`mode 'travel'`, layers scaling up from the centre), roll `= c · lateral acceleration` banking into each turn (±8–15°), near objects (`p > 1.5`) whipping past the edges, a speed readout. `--sub 4` motion blur is what sells it.

### 12 Dutch angle

- **What it is.** The camera is rolled off level.
- **When it belongs.** Unease, disorientation, something wrong. Hold it; do not wobble it.
- **How to draw it.** Rotate the scene layer by θ (8–20°) about the frame centre and scale it up to cover the corners: `s = max((W·cosθ + H·sinθ)/W, (W·sinθ + H·cosθ)/H)` (1.35 at 12° on 1920 × 1080).

### 13 Slow motion

- **What it is.** Action runs slower than real time.
- **When it belongs.** The moment that matters: the impact, the click that changes everything, a reveal.
- **How to draw it.** `retime` to rate 0.25 (`120fps ×0.25`) for the beat, then back. Everything in the action slows, particles and petals included; the camera may keep its own pace. Sound drops in pitch or falls away. Never slow a UI's typing or loading: it reads as lag.

### 14 Speed ramp

- **What it is.** Speed changes inside the shot: fast, then slow at the key moment, then fast again.
- **When it belongs.** Action and launch reels; emphasise one instant inside a fast move.
- **How to draw it.** `retime` keys like `[[1.0, 2.4], [1.3, 0.25], [2.3, 0.25], [2.6, 1]]`. Land the slow part on a downbeat (`beat-grid.md`).

### 15 Time-lapse

- **What it is.** Hours pass in seconds.
- **When it belongs.** Show accumulation or change over time: a dashboard filling over a month, a city waking.
- **How to draw it.** `retime` at 30–600×: light, shadows and a clock readout (`06:00`) move; people become short ghost trails at low alpha; the subject either holds still in the moving world or is shown as several ghosts.

### 16 Freeze frame

- **What it is.** The action stops dead on one frame.
- **When it belongs.** Label a moment ("that's me"), a punchline, a comparison point.
- **How to draw it.** `retime` rate 0 for the hold. The camera may still push in, and overlays (a ring, a label, a desaturate) arrive on `t`. A 2-frame flash or a snap to grayscale marks the stop.

## Group 3 — how one shot hands over to the next (17–24)

These are drawn in `transitions.md`; each chapter here names the move and points there.

### 17 Jump cut

Same framing, time skips; the subject jumps. Drawn in `transitions.md` § Jump cut.

### 18 Match cut

A shape or motion continues across the cut. Drawn in `transitions.md` § Match cut.

### 19 Whip pan

A blurred pan so fast it becomes the cut. Drawn in `transitions.md` § Whip pan (`whip`).

### 20 Cross dissolve

One shot fades through the other. Drawn in `transitions.md` § Cross dissolve.

### 21 Wipe

A moving edge replaces one shot with the next. Drawn in `transitions.md` § Wipe (`wipe`).

### 22 Smash cut

A hard cut from loud to quiet, or fast to still. Drawn in `transitions.md` § Smash cut.

### 23 J-cut

The next shot's sound arrives before its picture. Drawn in `transitions.md` § J-cut.

### 24 L-cut

The last shot's sound carries over the next picture. Drawn in `transitions.md` § L-cut.

## Choosing the film's camera language

- **One camera language per film.** Pick the two or three moves the reference uses and repeat them; a new move in every shot is a showreel of moves. (A showreel is the exception.)
- **Every move has a reason in the storyboard.** A push-in moves the focus from the stage to the subject (`2-draft.md` § Draft concepts); a pan reveals; a crane opens or closes. If the `why:` line cannot name it, the camera holds still. A static camera on a strong composition is a choice too.
- **Moves land on beats.** Start a move a beat before the read it serves, and let it settle on the downbeat (`beat-grid.md`).
- **Readouts help the eye.** The small HUD numbers (`24mm`, `→ 1.7m/s`, `−54°`, `120fps ×0.25`) tell the viewer what kind of move they are watching; use them when the film's look allows a HUD.
- **Vertical needs a different path.** A 9:16 frame pans less and tilts more; re-plan the camera per format, never crop (`pipeline.md` § Formats).

## Director notes in camera words

Vague notes ("make it better") get random changes; camera words get exactly the change. Write notes on a contact sheet in this vocabulary, one line each in `docs/review_log.md`:

"dolly in on the button, not zoom" · "slow every zoom to 0.7×" · "hard cut here" · "rack focus from the chart to the CTA" · "lose the handheld on the pricing table" · "speed ramp into the click" · "freeze on the result, push in, ring it" · "whip pan out, match cut in" · "L-cut the click sound under the next shot" · "crane up and out for the end card".
