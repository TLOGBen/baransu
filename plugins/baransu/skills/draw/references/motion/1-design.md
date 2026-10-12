# Phase 1 — Design (設計)

**Settles:** what the film is for, what must be real, what it looks, moves and sounds like, the route and formats. **Produces:** `docs/brief.md`, `docs/style_guide.md`, the film folder, the motion tokens, the plan message. **Gate:** every asset the brief calls real is present (or the film stops and names it), and the plan message has been stated. **Next:** `2-draft.md`.

The prompt is about 10 % of the result; the rest is what the work has to stand on. A one-liner tests the engine and never the idea, because it contains none. Design turns whatever the user said into decisions: facts that are fixed, choices that are made, numbers instead of adjectives, and the defaults banned by name. Nothing is drawn yet.

## Concepts

- **Facts are fixed; choices are yours.** Facts about the product (names, numbers, dates, screens, logo, the track) are asked for when missing and never invented. Choices about the film (opening, camera, rhythm) are proposed, not asked.
- **Real beats drawn.** Never redraw product UI from imagination; crop and animate the real thing. Invented UI shows: wrong spacing, placeholder boxes, fake-looking buttons, and anyone who uses good software feels it in a second.
- **A reference beats a description.** Without one the model falls back to its defaults: centred text, gradient background, everything fading in. Naming a style beats describing one; a frame or a video gives pacing, type and transitions to copy.
- **Every adjective replaced with a number is a decision taken back.** "Premium", "cool", "modern", "make it pop" leave every decision to the model, and its decisions are the look everyone has seen (`prompts.md` § The directed prompt shows the same subject from three adjectives and from 448 words of direction).
- **The ladder decides the harness.** A one-liner needs only the renderer; a brand film needs assets and sound; an idea needs a reference and a state list; a production needs a crew's brief. Climb it for the user rather than building a showreel nobody can tell from the thousand others (`prompts.md` § The prompt ladder).

## Steps

### 1. Write the brief — `docs/brief.md`

Short on purpose; the long director's brief (`prompts.md` § L4) is for productions.

```
FILM      goal in one sentence · audience · the one thing to remember · length · primary format (then the other two)
ASSETS    what must be real (screens, logo, colours, fonts, numbers, track) → path in assets/ or manifest.json
          what may be drawn (abstract shapes, placeholder data marked as such)
VISUAL    reference and what to borrow from it · palette (sampled) · type (two faces) · motion feel · banned looks
UNACCEPTABLE  what would make the result wrong even if it looks good (a replaced logo, an invented metric,
          the wrong product name, a cut that hides the feature)
DELIVER   final.mp4 (+ formats) · loop_check · poster · contact sheets · README with the render command
```

- A missing asset the brief lists as real is a **stop**, not a default (`../loop-pauses.md`). No brand decision is taken by default.
- A product URL the user pasted becomes real assets: `node scripts/motion/grab.mjs <url> --out assets` screenshots it at the three formats plus the full page and writes `assets/manifest.json` (title, og:image, theme colour, the body font and colours the page computes); list the manifest in the plan message before drawing.
- Component libraries the user already has (a design system, a UI kit, components installed from a registry such as 21st.dev) are inputs too — screenshot them, do not reinvent them.
- API keys go in `.env`; the prompt names the variable, never the key.
- The second film for the same brand copies the folder and replaces only this file and `assets/`.
- Client work or a sample: also the scope and the `Concept demo` rules (`commission.md` § 1).

### 2. Read the reference — `docs/style_guide.md`

The reference comes from the user (this skill does not browse galleries for one). When none is offered, ask for a frame, a clip or a folder of their own work before building, and say where one can be found: a gallery of shipped product and launch videos (such as whatships.com) where they pick one or two whose style they want matched. Read it for principles (typography, spacing, motion decisions, pacing), never as assets to copy.

- **A frame**: say what to take (palette, type, grain) and what not to take (subject).
- **A video**: `bash scripts/motion/checks.sh refs ref.mp4 [0.5]` extracts one frame every 0.5 s into `refs/frames/` plus a tile to read; describe pacing shot by shot before any code.
- **A library**: a folder of the user's own work; a reference nobody else can copy.
- **No reference at all**: propose a restrained typographic direction with an available licensed font and the single accent.

Then ten lines, every one a decision:

```
Palette: paper #…, ink #…, accent #…  (sampled, not guessed)
Type: display face / UI face, hook size as a fraction of frame height, width and scale ratio between them
Composition: where the eye goes first, and what fills the rest
Motion: the verbs it uses (snap, glide, overshoot, cut, hold) mapped to the feel table in springs.md
Shot length: typical / shortest / longest (measured from the reference)
Transitions: the two or three it uses, and the direction they travel
Camera: static / push-ins / whip; how much it moves per shot (the named moves are in camera.md)
Texture: grain, paper, none
Text enters / exits: how (snap, wipe, rise), and where it sits
Sound: cuts on downbeats? SFX per action?
Keep: what to borrow (grammar)      Leave: what not to copy (subject, logo)
```

When the reference reads two ways, render the hook still both ways and ask.

### 3. Direct with numbers

Write the directed prompt (`prompts.md` § The directed prompt) or its equivalent in the brief and style guide: GOAL first (if it cannot be said in one sentence, no easing curve will rescue the piece), then TIME, because every other number hangs off the frame count. Put the motion numbers in one place as the film's tokens (`springs.md` § Tokens): "use only these tokens, no inline numbers" stops values drifting between shots.

### 4. Ban the defaults, lock the identity

- **The ban list every film starts from:** purple or blue gradients, glow, lens flares; floating particles as decoration; everything fading in at once; fade-and-slide-up on every element; centred-everything layouts; text that moves while it is being read; corner labels, frame borders, glow on UI chrome, particle bursts, a fade to black between two UI states. A general line like "avoid a generic AI look" only swaps one default for another. After every first render, name the defaults the model used anyway and add them.
- **Identity locks:** what may not change, in numbers ("a 14 × 10 body, 3 × 2 arms, 2 × 3 legs, built from 0.1 voxels"; the logo's proportions; the product's real colours). Every style that must survive needs a line like that.
- **Pin versions and name the right parameter** when a library is involved (one three.js release reads `height`, not `depth`, for text extrusion, and silently replaces a `depth` value: letters meant to be 0.12 deep come out 50 deep).
- Specify the look and the constraints, not the library; let the technique be chosen.

### 5. Type and sound, decided now

- **Type** (`type.md` § Faces): one display face, one UI face, the accent; the hook's size and length; how captions behave.
- **A supplied track is measured now** (`beat-grid.md` § Measure a supplied track): the picture's timing hangs off its grid, so `beats.json` exists before the storyboard. Without a track, pick the film's tempo (120 BPM is the easiest to cut to: 0.5 s per beat, 2 s per bar).

### 6. Route, formats, folder

- **Route A** (one `index.html` + `motion.js`, rendered by `seek(t)`) unless the brief names a framework (`pipeline.md` § Routes and engines).
- **The primary format** and the other two, reflowed from it, never cropped (`pipeline.md` § Formats); choose the canvas before the first frame, because changing it later means re-directing every shot.
- **The film folder** from `assets/motion/seek-template.html` + `motion.js` (`pipeline.md` § The film folder).

### 7. The plan message

One message, then build (`SKILL.md` spine step 2): the lane, the film structure, the format and route, the palette decision, what the complexity budget forces out. For a mechanism figure, also its size (Figure / Hero / Epic, `../mechanism/mechanism.md` § Size it first). An interactive user may redirect; a non-interactive run proceeds and reports it.

## Effort and expectations

Medium effort is the default for iteration and small fixes; a new film at high; a launch piece whose first three seconds carry the launch at the highest the session offers; raise it when a from-scratch piece misses twice. Fast mode, where the host offers it, is for iteration sprints when speed matters more than cost. One of the most viewed 3D pieces of its launch week was captioned as the third iteration at medium effort. Budget for iteration; it is the method (`prompts.md` § The honest numbers).

## Gate checklist

- [ ] `docs/brief.md`: facts, real assets with paths, what may be drawn, UNACCEPTABLE, deliverables
- [ ] every real asset present, or the film stopped and named it
- [ ] `docs/style_guide.md`: ten decided lines, Keep / Leave
- [ ] numbers instead of adjectives; the ban list; identity locks
- [ ] faces chosen; track measured or tempo chosen
- [ ] route, primary format, folder created; plan message stated
