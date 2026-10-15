# Phase 3 — Keys (關鍵幀／首尾幀)

**Settles:** every frame the viewer will stop on, designed as a frame — first the first and last frames, then every key between them, each with its layout (framing, depth layers, focus plane). **Produces:** the bookend stills, `KEYS` as data in the film file, one still per key, a key contact sheet with scores. **Gate:** the bookends rhyme and every key passes the critique card as a still. **Next:** `4-shoot.md`.

This guide is not read whole. Each /draw step (`SKILL.md` § Lane: film) runs `python3 "<skill>/scripts/lookup.py" --step <step-id> --log "<project>/.claude/draw/<slug>"` first, which prints the chapters of this guide and of the library that the step needs; a question that comes up mid-step gets a single-topic lookup (`references/INDEX.md` lists the topics).

The working order for every film and every moving figure: **draw the first and the last frame, then the key frames between them, then design how each key travels to the next, and only then generate the animation.** Animators call it pose-to-pose. It works for a model for the same reason it works for a person: a still is cheap to judge and cheap to change, and once the keys are right, the motion between them is mostly a choice of feel, not a search. Code that animates first and looks later moves everything at once and finds out at second 9 that the composition never worked. Keys first means every frame the viewer stops on was designed as a frame.

## Keys concepts

- **The keys are the contract with the viewer.** They are the frames a person pauses on, screenshots, or sees as a thumbnail. Designing them as frames is what makes the film look composed rather than tweened.
- **The cheapest place to fix is the earliest.** A bookend is two stills, a key is one still, an interval is one line in the shot list, a render is minutes. Each step is approved before the next spends effort.
- **The motion inherits the design.** Because the in-betweens are computed from the key data (Phase 4), a change to a key moves every frame around it consistently; nothing drifts between the still that was approved and the film that ships.
- **It survives revisions.** Director's notes map onto one step: "hold B longer" is a key time, "glide, don't bounce" is an interval feel, "push in on the button" is an interval camera, "the end card is weak" is a bookend.
- **Layout belongs to the key.** As in an animation studio's layout stage, the framing of every key (its camera rect, depth layers, focus plane) is set with the key. Phase 4 only moves between framings already approved.

## The key card — what every finished key contains

A key is final when its card is complete and its still passes the critique card. Draft started the card (`2-draft.md` § 9); this phase fills every field and renders it. Keep the cards in `docs/keys.md` (one block per key) and the same values in `KEYS` in the film file.

```
KEY B  ·  t = 3.0 s (frame 90)  ·  shot A, exit          ← id, settled time, frame, which shot and whether it is the enter, a mid or the exit state
READ        completes: "the Ads card is the one that matters"        ← the read this key lands (from the storyboard)
WHY         the viewer now knows the cards can be picked up           ← what is known after this key that was not before
COMPOSITION 6 : 3 : 1 (composition.md) — 60 % stage: the desk surface, quiet · 30 % life: two other cards dimmed to 40 %, cursor · 10 % focus: the Ads card, lifted 8 px with the accent edge
            single difference: the only element with the accent and a shadow
FRAMING     shot size MS · angle eye level · lens feel normal (24mm)
            camera rect {x 480, y 160, w 1280, h 720} · depth layers: desk p 0.6, cards p 1.0, cursor p 1.0 (overlay) · focus plane p 1.0
SUBJECT     every element's state: position, size, radius, rotation, opacity, which content it shows
            card {x 780, y 300, w 360, h 220, r 18} · cursor {x 960, y 410, down}
TYPE        on-screen copy, exact: "Too many tabs." · face, size, weight, tracking · position · nothing in the safe margins
LOOK        palette in this key (from the colour script) · where the accent sits (one element) · light direction and contrast · texture
MOTION IN   how the previous interval arrives here (feel, what carries) — filled in Phase 4, noted here when known
MOTION OUT  how the next interval leaves (feel, camera move, transition if this key ends a shot)
SOUND       the cue on this key's frame, if any (type, frame + 1)
FORMATS     how the key reflows in the other two formats (what L.show hides in 9:16, what moves)
CHECKS      readable at 360 px · the 10 % found on the thumbnail · one focus · nothing in L.safe margins · matches the chosen style frame · still path: out/keys/B.png
```

Not every field carries weight on every key (a title card has no cursor; a mechanism key has a readout instead of copy), but every field is considered and either filled or marked "none".

## Keys steps

### 1. Bookends — the first frame and the last frame

Before anything else, render two stills and look at them side by side.

- **The first frame** is the hook. It is never empty: the viewer who sees only this frame in a feed decides here. It sets the palette, the type, the stage and the one focus.
- **The last frame** is the payoff and the poster (`out/<slug>.poster.png`): the CTA, the finished state, the answer. It must be strong enough to stand alone.
- **For a loop, the last frame is the first frame**, position and velocity included (`springs.md` § `loopT`). Then the bookends are one frame, and the film is a journey that comes home.

Both are built to the chosen direction's style frame (`2-draft.md` § 1); if they do not match it, the look has drifted. Judge the pair together: does the last frame answer what the first frame promised? Does the same world carry from one to the other (palette, motif, screen direction)? If the two do not rhyme, no amount of in-between will fix it. Fix the bookends first.

```
node scripts/motion/render.mjs stills --html <slug>.film.html --at 0,<dur − 1/fps>
```

### 2. Keys — every state where meaning changes

A key is a frame where something the viewer must understand is fully on screen and settled. Find them from the storyboard: every read's end state, every shot's `enter:` and `exit:` (`2-draft.md`), every UI state in a state list (`prompts.md` § L3), every beat with an event.

- **Each key is a complete, composed frame.** It passes the critique card as a still: stage, a few supporting elements, one focus marked by a single difference, readable at 360 px, nothing in the safe-area margins (`pipeline.md` § Formats).
- **Count keys by reads, not by seconds.** A 15-second product film usually has 6–10 keys; a dense explainer more. If two keys look the same, one of them is not a key.
- **Add breakdown keys only where the path matters**: the extreme of an anticipation, the top of an arc, the overshoot of a heavy landing, the mid-point of a morph where the container is half one state and half the next. Most transitions need none; a character or a complex morph needs one or two.
- **Type keys at final size**: the hook still and every caption key set as they will read (`type.md`).

### 3. Layout — the framing of each key

For each key, turn the camera plan's shot size, angle and lens feel (`2-draft.md` § 5) into numbers: the camera rect (what part of the world fills the frame), the depth layers present and their depth `p` (`camera.md` § The parallax rule), and the focus plane if a rack focus is planned. A push-in is simply a later key with a smaller rect. Shots that will use a move from `camera.md` get their start and end framing here; the move itself is executed in Phase 4.

### 4. Write the keys as data

One object per key in the film file; the time is when the state is **settled and readable**:

```js
// Every key is a full state of the scene at a time. Seconds are when the state is settled and readable.
const KEYS = [
  { id: 'A', t: 0.0, card: { x: 120, y: 340, w: 360, h: 220, r: 18 }, title: 'Too many tabs.', cam: { x: 0, y: 0, w: 1920, h: 1080 } },
  { id: 'B', t: 3.0, card: { x: 780, y: 300, w: 360, h: 220, r: 18 }, title: 'Too many tabs.', cam: { x: 480, y: 160, w: 1280, h: 720 } },
  { id: 'C', t: 7.0, card: { x: 360, y: 180, w: 1200, h: 720, r: 28 }, title: 'One clear view.', cam: { x: 0, y: 0, w: 1920, h: 1080 } },
  // …
];
```

The `seek(t)` of a keys-only build can simply draw the nearest key (a hold at each key, hard cuts between): that is a valid animatic, and it is what this phase reviews.

### 5. Review the keys as stills

Render one still per key and critique them as a contact sheet before anything moves:

```
node scripts/motion/render.mjs stills --html <slug>.film.html --at 0,3,7,12,14.97
```

Score the sheet on the critique card (`../critique-loop.md`): composition, type size, the one accent, the empty frame 0. Fix keys here; never plan to fix them with motion.

## Keys in the other lanes

- **Component** (`component.md`): the figure's `data-rest` frame is its key. Draw the rest frame first, then the frames where the figure's point changes, then animate between them.
- **Mechanism figure** (`../mechanism/mechanism.md`): the idle tour is a sequence of keys (rest, press, pull, release, settled); the live model computes the in-betweens.
- **Hand-drawn shorts** (`hand-drawn/workflow.md`): the beat sheet's end state per beat is the key; exposure (ones, twos, holds) is decided per interval.
- **Diagram seek overlay** (`../diagram/seek-overlay.md`): the static diagram is both bookends; each node lighting up is a key.

## Gate checklist

- [ ] first and last frames rendered and judged as a pair (one frame, for a loop)
- [ ] one key per state where meaning changes; breakdowns only where the path matters
- [ ] every key has its layout: camera rect, depth layers, focus plane
- [ ] every key card complete (or fields marked "none") in `docs/keys.md`
- [ ] `KEYS` written as data with settled times, matching the cards
- [ ] bookends and keys match the chosen style frame
- [ ] the key contact sheet scored; every key passes as a still
