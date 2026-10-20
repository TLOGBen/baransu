# Phase 1 — Design (設計)

**Settles:** what the film is for, what must be real, what it looks, moves and sounds like, the route and formats. **Produces:** `docs/brief.md`, `docs/style_guide.md`, the film folder, the motion tokens, the 開工狀態行. **Gate:** every asset the brief calls real is present (or the film stops and names it), and the 開工狀態行 has been sent. **Next:** `2-draft.md`.

This guide is not read whole. Each $baransu:draw step (`SKILL.md` § Lane: film) runs `python3 "<skill>/scripts/lookup.py" --step <step-id> --log "<project>/.codex/draw/<slug>"` first, which prints the chapters of this guide and of the library that the step needs; a question that comes up mid-step gets a single-topic lookup (`references/INDEX.md` lists the topics).

The prompt is about 10 % of the result; the rest is what the work has to stand on. A one-liner tests the engine and never the idea, because it contains none. Design turns whatever the user said into decisions: facts that are fixed, choices that are made, numbers instead of adjectives, and the defaults banned by name. Nothing is drawn yet.

## Design concepts

- **Facts are fixed; choices are yours.** Facts about the product (names, numbers, dates, screens, logo, the track) are never invented; one the brief needs and the user did not supply is the one reason to stop and ask. Choices about the film (opening, camera, rhythm, look) are decided and written down, never asked.
- **Real beats drawn.** Never redraw product UI from imagination; crop and animate the real thing. Invented UI shows: wrong spacing, placeholder boxes, fake-looking buttons, and anyone who uses good software feels it in a second.
- **A reference beats a description.** Without one the model falls back to its defaults: centred text, gradient background, everything fading in. Naming a style beats describing one; a frame or a video gives pacing, type and transitions to copy.
- **Every adjective replaced with a number is a decision taken back.** "Premium", "cool", "modern", "make it pop" leave every decision to the model, and its decisions are the look everyone has seen (`prompts.md` § The directed prompt shows the same subject from three adjectives and from 448 words of direction).
- **The ladder decides the harness.** A one-liner needs only the renderer; a brand film needs assets and sound; an idea needs a reference and a state list; a production needs a crew's brief. Climb it for the user — write the state list and the direction yourself — rather than building a showreel nobody can tell from the thousand others (`prompts.md` § The prompt ladder).

## Design steps

### 1. Write the brief — `docs/brief.md`

Short on purpose; the long director's brief (`prompts.md` § L4) is for productions.

```
FILM      goal in one sentence · audience · the one thing to remember · length · primary format (then the other two)
ASSETS    what must be real (screens, logo, colours, fonts, numbers, track) → path in assets/ or manifest.json
          what may be drawn (abstract shapes, placeholder data marked as such)
VISUAL    reference and what to borrow from it · palette (sampled) · type (two faces) · motion feel · banned looks
UNACCEPTABLE  what would make the result wrong even if it looks good (a replaced logo, an invented metric,
          the wrong product name, a cut that hides the feature)
DELIVER   out/<slug>.mp4 (+ formats <slug>-9x16.mp4 …) · loop_check · poster · contact sheets · README with the render command
```

- A missing asset the brief lists as real is a **stop**, not a default (`../loop-pauses.md`). No brand decision is taken by default.
- A product URL the user pasted becomes real assets: `node scripts/motion/grab.mjs <url> --out assets` screenshots it at the three formats plus the full page and writes `assets/manifest.json` (title, og:image, theme colour, the body font and colours the page computes); list the manifest in `docs/brief.md` before drawing.
- Component libraries the user already has (a design system, a UI kit, components installed from a registry such as 21st.dev) are inputs too — screenshot them, do not reinvent them.
- API keys go in `.env`; the prompt names the variable, never the key.
- The second film for the same brand copies the folder and replaces only this file and `assets/`.
- Client work or a sample: also the scope and the `Concept demo` rules (`commission.md` § 1).

### 2. Read the reference — `docs/style_guide.md`

The reference comes from the user (this skill does not browse galleries for one). When none was supplied, do not stop to ask for one: take the restrained typographic direction below, record it in `docs/style_guide.md` as the decided look, and note in the completion report that a frame, a clip or a folder of the user's own work would sharpen the next film (a gallery of shipped product and launch videos, such as whatships.com, is where they can pick one). Read any reference for principles (typography, spacing, motion decisions, pacing), never as assets to copy.

- **A frame**: say what to take (palette, type, grain) and what not to take (subject).
- **A video**: `bash scripts/motion/checks.sh refs ref.mp4 [0.5]` extracts one frame every 0.5 s into `refs/<base>/frames/` plus `refs/<base>/tile.png` to read; describe pacing shot by shot before any code.
- **A library**: a folder of the user's own work; a reference nobody else can copy.
- **No reference at all**: take a restrained typographic direction with an available licensed font and the single accent, and write it into the ten lines below as decisions.

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

When the reference reads two ways, render the hook still both ways, choose the stronger one against the brief, and log both stills and the reason in `docs/review_log.md`.

### 3. Direct with numbers

Write the directed prompt (`prompts.md` § The directed prompt) or its equivalent in the brief and style guide: GOAL first (if it cannot be said in one sentence, no easing curve will rescue the piece), then TIME, because every other number hangs off the frame count. Put the motion numbers in one place as the film's tokens (`springs.md` § Tokens): "use only these tokens, no inline numbers" stops values drifting between shots.

### 4. Ban the defaults, lock the identity

- **The ban list every film starts from:** purple or blue gradients, glow, lens flares; floating particles as decoration; everything fading in at once; fade-and-slide-up on every element; centred-everything layouts; text that moves while it is being read; corner labels, frame borders, glow on UI chrome, particle bursts, a fade to black between two UI states. A general line like "avoid a generic AI look" only swaps one default for another. After every first render, name the defaults the model used anyway and add them.
- **Identity locks:** what may not change, in numbers ("a 14 × 10 body, 3 × 2 arms, 2 × 3 legs, built from 0.1 voxels"; the logo's proportions; the product's real colours). Every style that must survive needs a line like that.
- **Pin versions and name the right parameter** when a library is involved (one three.js release reads `height`, not `depth`, for text extrusion, and silently replaces a `depth` value: letters meant to be 0.12 deep come out 50 deep).
- Specify the look and the constraints, not the library; let the technique be chosen.

### 5. Type and sound, decided now

- **Type** (`type.md` § Faces — one display face, one UI face): one display face, one UI face, the accent; the hook's size and length; how captions behave.
- **A supplied track is measured now** (`beat-grid.md` § Measure a supplied track): the picture's timing hangs off its grid, so `beats.json` exists before the storyboard. Without a track, pick the film's tempo (120 BPM is the easiest to cut to: 0.5 s per beat, 2 s per bar).

### 6. Route, formats, folder

- **Route A** (one `<slug>.film.html` + `motion.js`, rendered by `seek(t)`) unless the brief names a framework (`pipeline.md` § Routes and engines).
- **The primary format** and the other two, reflowed from it, never cropped (`pipeline.md` § Formats); choose the canvas before the first frame, because changing it later means re-directing every shot.
- **The film folder** gets `motion.js` and the `seek(t)` mechanics of `assets/motion/seek-template.html` (`pipeline.md` § The film folder). The template is a mechanics example — the render contract, `window.timeline()`, `FORMATS` and the layout object `L` — not a look: the shots, palette, type and composition come from this phase's decisions and the Draft, never from the template's own scene. Open the template only after `docs/brief.md` and `docs/style_guide.md` are written, and take only its mechanics; until then the folder holds only `docs/`.

### 7. The 開工狀態行

Every $baransu:draw build, in every form, sends this one line and then builds in the same turn without waiting (`SKILL.md` § The flow, step `brief-and-status-line`). It goes out at step `brief-and-status-line`, as soon as form, approach and delivery are decided — before the steps that settle the type and the size:

```
開工：形式 {diagram | map | film | component}／畫法 {diagram system | mechanism | free creative}／型別或結構 {visual type or film structure}／尺寸 {size preset, format, or Figure|Hero|Epic}／交付 {單件 | 多件 | 圖件＋$baransu:ui 組頁}／理由 {one sentence}
```

- **形式** is the form chosen in step `choose-form`; a film is `film`.
- **畫法** is the approach from `choose-approach`.
- **型別或結構** is the diagram type, the map type, the film structure, or the figure's object (a mechanism: the machine invented for it).
- **尺寸** is the diagram size preset, the film's primary format, or a mechanism's size class `Figure`, `Hero` or `Epic` (set by the part count and the number of moving systems, not by how many mechanisms the idea has). A size class is a name only: no time estimate, never a smaller tier.
- **交付** is `單件` (one piece), `多件` (one file per piece) or `圖件＋$baransu:ui 組頁` (checked pieces in their chosen forms, then $baransu:ui assembles the page in the same turn).
- **理由** is one sentence on why this form and approach carry the idea.
- **待定.** A 型別或結構 or 尺寸 not yet decided when the line goes out reads `待定` — the diagram type (step `diagram-plan`), the map type (`map-author`), the invented object (`mech-invent-object`), the film structure and primary format (`design-film-folder`). When the step that decides it is done, one progress line states the value (`型別或結構：…／尺寸：…`) and `docs/progress.md` records it (step `progress-notes`); the build never waits for it. A field already decided (a mechanism's size class from `mech-size`) is written in the line itself.

The route, the palette decision and the rest of the plan are in `docs/brief.md` (and, for a film, `docs/style_guide.md`). The line is a statement, not a question: nothing waits on a reply.

## Effort and expectations

A new film runs at high effort; a launch piece whose first three seconds carry the launch at the highest the session offers; small fixes to a finished film may run lower; raise it when a from-scratch piece misses twice. Never lower the effort or the scope to save time unless the user asked for something quick. One of the most viewed 3D pieces of its launch week was captioned as the third iteration: plan for iteration, it is the method (`prompts.md` § The honest numbers).

## Gate checklist

- [ ] `docs/brief.md`: facts, real assets with paths, what may be drawn, UNACCEPTABLE, deliverables
- [ ] every real asset present, or the film stopped and named it
- [ ] `docs/style_guide.md`: ten decided lines, Keep / Leave
- [ ] numbers instead of adjectives; the ban list; identity locks
- [ ] faces chosen; track measured or tempo chosen
- [ ] route, primary format, folder created; 開工狀態行 sent and the build started without waiting
- [ ] every step of this phase run after its step command (`lookup.py --step <id>`), logged in `docs/lookups.log`
