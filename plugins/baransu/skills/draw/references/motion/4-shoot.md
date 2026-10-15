# Phase 4 — Shoot (攝影)

**Settles:** how each key becomes the next — what carries, the feel, the camera move, the timing — and the in-betweens, computed from the key data; then dailies until the motion holds. **Produces:** `docs/shotlist.md` (one line per interval), the animated film file, dailies (strips, contact sheets, phone sheets, animatic), `docs/review_log.md` rounds. **Gate:** the key times re-rendered still show the approved keys, settled; every gated score on the card ≥ 8, every round logged (rounds continue until then; there is no round cap); no full render yet. **Next:** `5-post.md`.

This guide is not read whole. Each /draw step (`SKILL.md` § Lane: film) runs `python3 "<skill>/scripts/lookup.py" --step <step-id> --log "<project>/.claude/draw/<slug>"` first, which prints the chapters of this guide and of the library that the step needs; a question that comes up mid-step gets a single-topic lookup (`references/INDEX.md` lists the topics).

In an animation studio this is in-betweening and photography: the keys are fixed, and the work is to move between them with weight and with a camera. The in-betweens are not drawn; they are computed from the keys, so the approved stills and the moving film can never disagree.

## Shoot concepts

- **The keys are the data.** Every animated property is a `track()` over the key times, so the numbers that made the approved stills drive the motion.
- **Mass decides the feel.** Springs by the mass of the thing (`snappy`, `ui`, `heavy`, `playful`); fixed easing only where mass would lie (fades, camera settles, data, wipes) (`springs.md`).
- **One hero per shot.** Everything else waits, dims, or follows at 50–70 % of the hero's travel, 100–200 ms later (`springs.md` § Hierarchy).
- **The camera moves only between approved framings.** Rotation reads as no parallax, travel as parallax (`camera.md` § The parallax rule).
- **You cannot see motion by reading code.** Every claim about the motion is checked on rendered frames.

## Shoot steps

### 1. Design each interval — how this key becomes the next

For every pair of adjacent keys, write one line in `docs/shotlist.md`:

```
A → B   2.4–3.0   what carries: the Ads card   verb: glide (ui spring)   camera: dolly in on B   transition: none (same space)   cue: whoosh at 2.4, tick at 3.0
B → C   6.2–7.0   what carries: all three cards merge into one   verb: gather (k 180 / d 22)   camera: pull back   transition: accent carry   cue: settle tone at 7.0
```

| Column | Choose from |
|---|---|
| what carries | the one element that crosses the interval and keeps the eye: the accent, a card, the cursor (`transitions.md` § Something crosses the seam) |
| verb | the feel: snap, glide, gather, land, overshoot, settle (`springs.md` feel table: `snappy`, `ui`, `heavy`, `playful`); text enters word by word (`type.md`) |
| camera | hold, or one named move (`camera.md`) between the two keys' framings |
| transition | for a seam between shots: the one chosen in Draft (`transitions.md`); inside a shot: none, the carry is the transition |
| timing | where the motion starts, so the key is settled at its time: a `ui` spring needs ~0.5–0.6 s, `heavy` ~0.8 s, `snappy` ~0.3 s. The motion into key B starts at `B.t − settle`, never at `B.t` |
| cue | the sound that marks the change (`beat-grid.md`), on the frame the change lands |

The draft rules apply per interval: one read at a time, cause then reaction, snap then hold, stagger groups by 0.05–0.14 s, nothing animates for no reason.

### 2. Generate the in-betweens from the keys

```js
const lead = { ui: 0.6, heavy: 0.8, snappy: 0.3 };
const at = (feel) => KEYS.map((k) => [Math.max(0, k.t - lead[feel]), k]);
const val = (t, feel, pick) => Motion.track(t, at(feel).map(([kt, k]) => [kt, pick(k)]), ...Motion.FEEL[feel]);

function seek(t) {
  const card = { x: val(t, 'ui', (k) => k.card.x), y: val(t, 'ui', (k) => k.card.y), /* w, h, r … */ };
  const cam = Motion.camera(t, at('ui').map(([kt, k]) => [kt, k.cam]), W, H);
  // draw with card and cam
}
```

Then add what keys cannot hold, straight ahead on top: secondary motion and overlap (details landing 2–3 frames after the body), ambient life during holds (breathing ±2 %, a drifting light band), particles, the cursor's path between clicks (`springs.md` § `cursor`). Apply the animation principles in numbers (anticipation, squash and stretch, overlap, follow-through, arcs, slow in and out, timing; exaggerate key poses 10–30 % for phone size) from `springs.md` § The animation principles.

### 3. Run the camera

Between the keys' framings, use the named moves (`camera.md`): `Motion.camera` for push-ins and reveals, `layerCam` with depth `p` for travel versus rotation, rack focus by layer blur, `handheld` as the outermost transform, `retime` for slow motion, speed ramps, time-lapse and freezes (the story clock separate from the camera clock). Moves start a beat before the read they serve and settle on the downbeat. Keep UI overlays, captions and readouts outside the camera transform.

### 4. Prove the keys still land

Re-render the key stills from the animated build. Every key time must show the approved key, **settled**. If a key frame now shows a card still in flight, the lead is too short or the spring too soft: move the motion earlier or stiffen the feel, never move the key.

```
node scripts/motion/render.mjs stills --html <slug>.film.html --at 0,3,7,12,14.97   # must match the approved key sheet
node scripts/motion/render.mjs hash --html <slug>.film.html --t 5                   # DETERMINISTIC
```

### 5. Dailies — review the motion between the keys

Keys were approved as stills; the in-betweens are reviewed as motion (`review.md` for every technique):

- `render.mjs strip --t <interval mid> --n 12` around every interval: no jump, no element passing through another, the carry visible in every frame.
- `render.mjs animatic` (24 fps, no blur, half size) for pacing: does each key get time to be read before the next interval starts?
- `render.mjs beats` (one frame per beat), `contact`, `phone` (360 px tiles), and the critique card (`../critique-loop.md`): score, list the three worst problems with frame numbers, fix, repeat — at least three rounds, and on until every gated row ≥ 8; there is no round cap, and every round is recorded. Write the fixes as director's notes in camera words.

A fault found here is fixed at the right level: a bad frame inside an interval is a timing or feel fix (step 1); a bad key is a key fix (Phase 3) and its intervals are re-designed; a bad story is a Draft fix. Never patch a bad key by tuning the in-betweens around it.

Render only the affected seconds while iterating (`--dur` on a copy with scene offsets, or `strip` around the change); the full render belongs to Post.

## Gate checklist

- [ ] one shot-list line per interval: carries, verb, camera, transition, timing, cue
- [ ] in-betweens computed from `KEYS`; secondary and ambient motion added on top
- [ ] every key re-renders settled at its time; `hash` prints `DETERMINISTIC`
- [ ] strips around every interval and fast action; animatic paced
- [ ] ≥ 3 dailies rounds logged, and rounds continued until every gated score ≥ 8 (no round cap; every round recorded in `docs/review_log.md`)
