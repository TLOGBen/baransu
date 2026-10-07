# The seek(t) pipeline — a film as a program

## The core trick is determinism

The model cannot emit a video. It writes a program, and something else turns the program into frames. Write one function, `seek(t)`, that paints the exact frame for any instant. A headless browser calls it 900 times for a 15-second 60 fps piece, screenshots each call, and ffmpeg stitches the result. Nothing depends on a timer, so:

- the render is identical every run (`render.mjs hash` proves it: the same frame rendered twice must hash the same),
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

## Two routes

**Route A — zero dependencies (default).** One `index.html`, `motion.js`, Playwright, ffmpeg. This is what the model reaches for on its own, and it is enough for showreels, product reels, UI morphs, explainers. Everything in this skill is Route A.

**Route B — a framework** (React-based Remotion for series, templates and data-driven videos; HTML+GSAP frameworks when you think in web pages). Worth it only when the same timeline must be re-rendered with different data many times, or a team needs a studio preview. Those frameworks ship their own agent skills that fetch updates from the network; this skill stays self-contained and does not bundle them. If you need one, say so explicitly in the brief; the model otherwise picks Route A.

## Formats

Write scenes against a layout function, not fixed pixels, so one timeline exports 9:16, 1:1 and 16:9 in parallel; reflow type and UI per format, never crop a 16:9 render to vertical. Default canvases: 1080×1920 (vertical), 1440×1440 (square), 1920×1080 (wide).

## Motion blur

Each output frame is the average of `--sub` subframes (4 by default) rendered at `fps × sub` and blended with ffmpeg `tmix`; the shutter spans one full frame. It is what makes fast cursor moves and type slams look filmed rather than stepped. `--sub 1` for a quick preview.

## The commands

```
node scripts/motion/render.mjs still   --html index.html --t 3.2          # one frame
node scripts/motion/render.mjs hash    --html index.html --t 5            # determinism check (exit 1 if not)
node scripts/motion/render.mjs beats   --html index.html --beats beats.json   # one frame per beat → beats.png
node scripts/motion/render.mjs contact --html index.html --dur 15         # 2 fps, 6 across → contact.png
node scripts/motion/render.mjs strip   --html index.html --t 4.2 --n 12   # 12 consecutive frames → strip.png
node scripts/motion/render.mjs phone   --html index.html --dur 15         # 360 px tiles → phone.png
node scripts/motion/render.mjs full    --html index.html --dur 15 --fps 60 --sub 4 --audio out/mix.wav   # final.mp4
bash scripts/motion/checks.sh contact|strip|phone|loop|probe out/final.mp4   # the same looks on the encoded master
```

Defaults: `--out out`, viewport 1080×1920, screenshot of `#stage` / the first `<canvas>` / `body`. Encode is H.264 yuv420p CRF 16 with `+faststart`.

## Effort and time budget

Small fixes and re-renders at medium effort; a new film at high; a launch piece whose first three seconds carry the launch at the highest the session offers. Render only the affected seconds while iterating (`--dur` on a copy with scene offsets, or `strip` around the change); the full render is the last step, after the contact sheet scores 8+ on every row.
