# Film lane — a film made like a studio

A film is a program: `window.seek(t)` paints the exact frame for any instant; Playwright samples it, ffmpeg stitches it. It is made the way an animation studio makes one, in five phases with a gate each — Design → Draft → Keys → Shoot → Post — and a technique library looked up at the step that needs it. `references/motion/README.md` is the map of the phases and the library. The steps are in `SKILL.md` § Lane: film, each run after its step command (`lookup.py --step <id>`), which prints that step's chapters of the phase guides and the library; no guide is read whole. This chapter holds the rules that break films when they are ignored.

## The five phases and their gates

| Phase | Guide | Settles | Gate |
|---|---|---|---|
| 1 Design (設計) | `references/motion/1-design.md` | facts vs choices and the real assets (`docs/brief.md`); the reference read into `docs/style_guide.md`; numbers instead of adjectives, the ban list, identity locks; faces; a supplied track measured; route, formats, folder; the 開工狀態行 | every real asset present or the film stops |
| 2 Draft (草稿) | `references/motion/2-draft.md` | the direction funnel wide → 3 → 1; every shot's 6 : 3 : 1 hierarchy; the colour script; the storyboard with timed reads; the cinematography plan; a transition per seam; the pacing curve and timing sheet; draft key cards | a keys-only animatic with temp sound reads as a story |
| 3 Keys (關鍵幀／首尾幀) | `references/motion/3-keys.md` | the first and last frames judged as a pair; every key finished on its key card and written as `KEYS` data | every key passes the critique card as a still |
| 4 Shoot (攝影) | `references/motion/4-shoot.md` | one shot-list line per interval; in-betweens computed from `KEYS`; the camera moving between approved framings; dailies | keys re-render settled; `hash` prints `DETERMINISTIC`; every score ≥ 8 after at least three dailies rounds |
| 5 Post (後製) | `references/motion/5-post.md` | seams executed; sound on frame + 1, measured on the decoded file; the full render; loops and exports; the encoded master reviewed; the package and report | the master passes its review; the report names only checks that ran |

"Approved" in the phase guides means scored ≥ 8 on the critique card by you, the director; no gate waits on the user.

### Motion inside the other forms

Anything else that moves — a component, a diagram seek overlay, a mechanism tour, a loop — runs the same phases at its own scale: its caption is the brief, its sequence of states is the draft, its rest frame (`data-rest`) and each state are the keys, in-betweens come from the states with springs by mass, and its lane check is the post.

## Rules that break films when ignored

### Determinism

No CSS transitions, no timers, no `requestAnimationFrame` in render mode, no state carried between frames, seeded noise only (`Motion.rng`), fonts awaited, only pinned libraries. `node "<skill>/scripts/motion/render.mjs" hash --html <slug>.film.html --t <t>` must print `DETERMINISTIC`.

### The film folder

It gets `assets/motion/motion.js` and only the `seek(t)` mechanics of `assets/motion/seek-template.html`: the render contract, `window.timeline()`, `FORMATS` and the layout object `L`. Open the template after the step's lookups; the shots, look and composition are designed from the references and the brief, and nothing of the template's scene, palette or type remains. One object per shot; everything derives from local t. Write the full file, never a partial skeleton. Names follow the subject: the source is `<slug>.film.html`, the master `out/<slug>.mp4`, the format siblings `out/<slug>-9x16.mp4`, `out/<slug>-1x1.mp4`, `out/<slug>-16x9.mp4`, and every sheet `render.mjs` writes starts with the same slug (it takes it from the `--html` file name).

### Direct with numbers, not adjectives

When the ask is a one-liner, climb the prompt ladder for the user (`references/motion/prompts.md`): write the state list yourself. When no reference was supplied, take the restrained typographic direction in `1-design.md` § 2 and record it in `docs/style_guide.md` — never stop to ask for a reference. A product URL the user pastes becomes real assets through `node scripts/motion/grab.mjs <url>` (screenshots at the three formats, `manifest.json` with the computed fonts and colours); a reference video becomes frames through `scripts/motion/checks.sh refs`. Both are written into `docs/style_guide.md` before the draft.

### Keyframes first

Bookends, then keys, then interval design, then in-betweens computed from the key data — never motion before the keys pass as stills (`3-keys.md`, `4-shoot.md`).

### Springs, not curves

From `references/motion/springs.md`: `spring` for anything that moves, by the mass of the thing (snappy / ui / heavy / playful); a value with several targets is `track()` — one spring per change, never a restart; `stretch()` for two-edge indicators; `swapAlpha()` + `swapBlur()` so content enters after a morph starts and leaves before the next; the last frame equals the first for a loop, cursor included. Fixed easing only where mass would lie: fades, `drawOn` (a chart drawing itself), `countUp` (one number that proves it), wipes, lens moves. One hero move per shot; secondary moves at 50–70 % of its travel, 100–200 ms later.

### What the viewer sees

- A cursor that really clicks, types and drags (`Motion.cursor`, `Motion.typed`, `Motion.drag`), each click on a beat with the UI answering a frame later.
- A camera that re-frames every state (`Motion.camera`, push-ins as smaller rects) and whose moves are named — each one looked up as its own chapter in `references/motion/camera.md` and drawn by its parallax rule.
- Type that lands word by word (`Motion.words`; `references/motion/type.md`: one display face + one UI face + the accent, a hook of at most 5 words at least ⅓ of the frame height, nothing in corners, text held 0.3 s per word + 0.5 s).
- A named transition at every seam, drawn as geometry (`references/motion/transitions.md`, one chapter per transition), never a fade to black between UI states.
- Director's notes in camera words and frame numbers, never "make it better" (`references/motion/review.md`).

### Sound

From `references/motion/beat-grid.md`: a supplied track is measured with `python3 scripts/motion/beats.py` (`beats` → small changes, `downbeats` → cuts, `hits` → SFX); without one, synthesize at the film's tempo. UI sounds come from `window.timeline()` cues through `node scripts/motion/sfx.mjs`, each hit's peak on frame + 1, 3–6 dB over the bed, about −14 LUFS, checked in the phone band and on the decoded file.

### Look before the full render

Dailies (`render.mjs beats`, `contact`, `strip --t <time>` around every fast action, `phone`, `animatic`) are scored for at least three rounds and until every row is 8 or higher; only then `render.mjs full --fps 60 --sub 4 --audio out/mix.wav`, then `scripts/motion/checks.sh contact|strip|loop|probe` on the encoded master. The full render is part of the deliverable; the gate before it is the dailies' score, never the render time.

### Formats

Scenes draw against the layout object `L` derived from `W×H`, so 9:16, 1:1 and 16:9 come from one timeline (`?f=` on the page, `render.mjs --format` / `--all`). Reflow, never crop: vertical gets fewer simultaneous elements (`L.show`), not smaller ones. Nothing the viewer must read sits outside the format's safe area (`L.safe`; `--safe` draws it on every sheet). A contact sheet per delivered format (`contact --all`) before the siblings ship.

### Long pieces

Over a minute: chapters, a shared `ANIMATION_GUIDE.md`, one file per chapter, subagents per chapter, chunked renders (`references/motion/chapters.md`).

### Client work

From `references/motion/commission.md`: a sample is labelled `Concept demo` and uses no third-party logos or invented results; the story is written in frame ranges that cover every frame; copy, colours and asset paths sit apart from the motion. The export itself is reviewed — a sheet every second and at every scene boundary, a probe of duration / size / fps / audio, a final three-second hold — and fixed and reviewed again until no defect is open; an unrun check is never reported as passed. It is packaged with its source and render commands. Help with finding, pricing or answering a brief only when asked; nothing is sent on the user's behalf.

## Hand-drawn look

For storybook, brush-ink, watercolour, low-poly, game feel and characters: the bundled canvas library under `scripts/hand-drawn/` (run `npm install` there once for `@napi-rs/canvas`). Original characters only.

### The library's guides

All under `references/motion/hand-drawn/`, each looked up by topic when its question comes up:

- `workflow.md` — an original animation from a brief, end to end; the order of work.
- `traps.md` — traps that each cost a render or a pass, with their fixes.
- `motion.md` — timing, acting and camera for 24 fps storybook films.
- `detail.md` — the detail bible: the three detail layers and line weight by depth (read with the override below).
- `styles.md` — the style presets; pick one per film and write its recipe into the style bible.
- `characters.md` — the bundled character rigs and how to pose them; a new film's characters are original.
- `sound.md` — cues from the picture's timeline, landing on the contact frame.
- `clawd-animation-guide.md` — the upstream guide to a short hand-painted cartoon; its subject rules yield to the brief.
- `prior-art.md` — the animation skills the library took ideas from.

`scripts/hand-drawn/templates/film-template.mjs` is the library's mechanics example: the `run()` set-up, the frame function, and the `sheet` / `strip` / `verify` / `render` commands. Copy it to `film.mjs` after the step's lookups and take only those mechanics; its scene (an ant on a textured-editorial set, a sprout, a bee) is replaced whole by the film designed from the references and the brief. `templates/beat-sheet.md` is the beat sheet to fill before writing drawing code.

### Override on detail.md — all three layers on every surface

This override on vendored material wins wherever `hand-drawn/detail.md` is read: its "If you can only afford two, drop nothing from the hero and simplify the background" does not apply. All three layers go on every surface; depth changes their weight, not their presence (the background's layers are lighter and simpler, per its line weight by depth).
