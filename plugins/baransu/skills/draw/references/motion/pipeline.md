# The seek(t) pipeline — a film as a program

## The core trick is determinism

The model cannot emit a video. It writes a program, and something else turns the program into frames. Write one function, `seek(t)`, that paints the exact frame for any instant. A headless browser calls it 900 times for a 15-second 60 fps piece, screenshots each call, and ffmpeg stitches the result. Nothing depends on a timer, so:

- the render is identical every run (`render.mjs hash` proves it: a canvas frame rendered twice must hash the same; an SVG/DOM frame may differ by rasterizer noise after an element toggles, so `hash` also accepts ≥ 80 dB PSNR with the DOM unchanged),
- frame 812 renders without simulating frames 0–811, so workers can render in parallel and a reviewer can jump to any instant,
- a change is a one-line edit plus a re-render of the affected seconds.

## The render contract

The page must obey these, or the renderer and the critique loop both break:

| Rule | Why |
|---|---|
| `window.seek(t)` paints frame t and returns (sync or promise) | the only entry point the renderer calls |
| No CSS transitions, no `setTimeout`, no `requestAnimationFrame` in render mode, no state carried between frames | any of these makes frame t depend on history; renders drift and parallel workers disagree |
| Seeded noise only (`Motion.rng(seed)`), never `Math.random` | two renders of the same t must be pixel-identical |
| Every value derives from t in closed form: springs, `track()`, easing on a window | lets `seek` jump anywhere |
| Live preview only when `!navigator.webdriver && !window.__RENDER__` | the preview loop is for a human browser; the renderer sets `__RENDER__` and drives `seek` itself |
| Optional `window.timeline()` → `{ duration, cues: [{t, type}] }` | the renderer writes `out/cues.json` from it so `sfx.mjs` can place sounds by measured peak |
| Never put `will-change` on anything the camera scales | the browser rasterises it once and the text goes blurry when scaled |
| Fonts via `document.fonts.ready` before the first frame | the renderer waits for it; a canvas drawn before fonts load shows the fallback face |

Start from `assets/motion/seek-template.html` plus `assets/motion/motion.js`; copy both into the film folder.

## The studio in five layers

Every film has these five, each with a file; a layer with no file was skipped, and the model filled that decision with its safest default.

| Layer | What it decides | Its file |
|---|---|---|
| Director | what the film is for, what must be real, what is unacceptable | `docs/brief.md` + `docs/storyboard.md` (`storyboard.md`) |
| Reference | what it looks like and moves like | `docs/style_guide.md` + `refs/` (`checks.sh refs`) |
| Timeline | what happens when, and on which beat | `docs/shotlist.md` + `beats.json` + `window.timeline()` |
| Renderer | the frame at time t | `index.html` + `motion.js` → `render.mjs` |
| Critic | whether the frames are good, and what to fix first | `../critique-loop.md` → `docs/review_log.md` |

## The film folder

```
.claude/draw/<slug>/
  index.html  motion.js          the film (Route A)
  assets/  (+ manifest.json)      the real screens, logo, fonts — from grab.mjs or the user
  refs/                           reference frames (checks.sh refs)
  beats.json                      the measured grid (beats.py), if a track was supplied
  docs/brief.md  style_guide.md  storyboard.md  shotlist.md  review_log.md
  out/cues.json  mix.wav  beats.png  contact*.png  strip.png  phone*.png  stills*.png
      animatic.mp4  final.mp4 (+ final-1x1 / final-16x9)  loop_check.mp4  poster.png  audio.wav  waveform.png
  README.md                       the exact render commands, so anyone re-renders without the chat
```

A resumed session reads `docs/review_log.md` first: the last logged round is the gate it resumes from, and any file from this list that is missing is named in the report before new work starts. "The last command exited 0" is never the evidence that the film is done; the files are.

## Two routes

**Route A — zero dependencies (default).** One `index.html`, `motion.js`, Playwright, ffmpeg. This is what the model reaches for on its own, and it is enough for showreels, product reels, UI morphs, explainers. Everything in this skill is Route A.

Code-rendered motion is the right tool for product films, UI motion, data stories, typography, diagrams and explainers. Photoreal scenes, characters with organic movement and anything shot are footage: not this lane; when the user has such footage it is an input to trace over (`prompt-ladder.md` § L4).

**Route B — a framework** (React-based Remotion for series, templates and data-driven videos; HTML+GSAP frameworks when you think in web pages). Worth it only when the same timeline must be re-rendered with different data many times, or a team needs a studio preview. Those frameworks ship their own agent skills that fetch updates from the network; this skill stays self-contained and does not bundle them. If you need one, say so explicitly in the brief; the model otherwise picks Route A.

## Formats

Write scenes against a layout object, not fixed pixels, so one timeline exports 9:16, 1:1 and 16:9; reflow type and UI per format, never crop a 16:9 render to vertical. The template reads `?f=9:16|1:1|16:9` from the URL, sizes the canvas from `FORMATS`, and derives every position from `L` (the layout) once; `render.mjs --format 1:1` opens the page with that query and the matching viewport, `--all` renders the three in one run as `final-9x16.mp4`, `final-1x1.mp4`, `final-16x9.mp4`, and does the same for `contact`, `phone` and `stills` (`contact-9x16.png` …) so every delivered format gets its own look. Default canvases: 1080×1920 (vertical), 1440×1440 (square), 1920×1080 (wide). The brief names the primary format; the other two are reflowed from it, not cropped. Reflow is more than sizes: vertical needs larger type, fewer simultaneous elements and a different camera path (`L.show` hides secondary elements per format), square needs shorter holds; a vertical cut is a tighter story, not a narrower one.

Each format has a **safe area** (`L.safe`): the margins a platform's own UI covers — on 9:16 the caption and action bar take the bottom ~340 px and the top ~220 px; on 1:1 and 16:9 keep 5 %. Nothing the viewer must read sits in the margins; `render.mjs contact|phone|stills --safe` draws the rectangle on every tile so the sheet shows it.

## Two render paths

Everything above is the browser path: `index.html` + `motion.js`, `render.mjs`, `checks.sh`. The hand-drawn library under `scripts/hand-drawn/` renders with node-canvas at 24 fps through its own `film.mjs`; its references live in `references/motion/hand-drawn/`. Pick one path per film; the critique loop and the storyboard rules are the same on both.

## Motion blur

Each output frame is the average of `--sub` subframes (4 by default) rendered at `fps × sub` and blended with ffmpeg `tmix`; the shutter spans one full frame. It is what makes fast cursor moves and type slams look filmed rather than stepped. `--sub 1` for a quick preview.

## The commands

```
node scripts/motion/render.mjs still   --html index.html --t 3.2          # one frame
node scripts/motion/render.mjs stills  --html index.html --at 0,3.2,6     # one tile per listed time (first frame of every shot)
node scripts/motion/render.mjs hash    --html index.html --t 5            # determinism check (exit 1 if not)
node scripts/motion/render.mjs beats   --html index.html --beats beats.json   # one frame per beat → beats.png
node scripts/motion/render.mjs contact --html index.html --dur 15         # 2 fps, 6 across → contact.png
node scripts/motion/render.mjs strip   --html index.html --t 4.2 --n 12   # 12 consecutive frames → strip.png
node scripts/motion/render.mjs phone   --html index.html --dur 15         # 360 px tiles → phone.png
node scripts/motion/render.mjs animatic --html index.html --dur 15        # 24 fps, no blur, half size: judge pacing before polish
node scripts/motion/render.mjs full    --html index.html --dur 15 --fps 60 --sub 4 --audio out/mix.wav   # final.mp4
node scripts/motion/render.mjs full    --html index.html --all            # the three formats from one timeline
node scripts/motion/render.mjs full    --html index.html --from 10 --to 20   # one chunk → part-10.00-20.00.mp4 (long pieces: 10 s chunks, concat at the end)
bash scripts/motion/checks.sh contact|strip|phone|loop|probe out/final.mp4   # the same looks on the encoded master
bash scripts/motion/checks.sh refs ref.mp4 [0.5]                          # a reference video → refs/frames/ + a tile to read
bash scripts/motion/checks.sh audio out/final.mp4                         # the mix alone → audio.wav + waveform.png: does it have a shape without the picture?
```

Defaults: `--out out`, viewport 1080×1920, screenshot of `#stage` / the first `<canvas>` / `body`. Encode is H.264 yuv420p CRF 16 with `+faststart`. Before the first measured frame the renderer sweeps the whole timeline once so every canvas font and weight has loaded (a canvas only requests a web font the first time `ctx.font` names it).

A long piece renders in chunks: `--from/--to` per chapter (a crash costs one chunk; `--keep` leaves the frames), then `ffmpeg -f concat` joins the parts and adds `out/mix.wav` once — the command is printed after each chunk.

## Effort and time budget

Small fixes and re-renders at medium effort; a new film at high; a launch piece whose first three seconds carry the launch at the highest the session offers. Render only the affected seconds while iterating (`--dur` on a copy with scene offsets, or `strip` around the change); the full render is the last step, after the contact sheet scores 8+ on every row.
