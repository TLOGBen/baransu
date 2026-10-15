# The seek(t) pipeline — a film as a program

Technique reference for rendering: the contract every phase obeys, the film folder created in Phase 1, the routes and engines, formats, motion blur, and every render command used from Phase 2 (animatic) to Phase 5 (master).

## The core trick is determinism

The model cannot emit a video. It writes a program, and something else turns the program into frames ("it does not generate pixels; it writes code that paints pixels"). Write one function, `seek(t)`, that paints the exact frame for any instant. A headless browser calls it 900 times for a 15-second 60 fps piece, screenshots each call, and ffmpeg stitches the result. Nothing depends on a timer, so:

- the render is identical every run (`render.mjs hash` proves it: a canvas frame rendered twice must hash the same; an SVG/DOM frame may differ by rasterizer noise after an element toggles, so `hash` also accepts ≥ 80 dB PSNR with the DOM unchanged) — every pixel is a pure function of `t`,
- frame 812 renders without simulating frames 0–811, so workers can render in parallel and a reviewer can jump to any instant,
- a change is a one-line edit plus a re-render of the affected seconds, not a re-roll of a video model,
- the model can check its own work: a contact sheet of the film is a dense image it reads well, and spotting what changed between two versions is what its vision is best at.

## The render contract

The page must obey these, or the renderer and the review loop both break:

| Rule | Why |
|---|---|
| `window.seek(t)` paints frame t and returns (sync or promise) | the only entry point the renderer calls |
| No CSS transitions, no `setTimeout` / `setInterval`, no `Date.now`, no `requestAnimationFrame` in render mode, no state carried between frames | any of these makes frame t depend on history; renders drift and parallel workers disagree |
| Seeded noise only (`Motion.rng(seed)`), never `Math.random` | two renders of the same t must be pixel-identical; unseeded randomness makes shapes jitter frame to frame |
| Every value derives from t in closed form: springs, `track()`, easing on a window | lets `seek` jump anywhere |
| Live preview only when `!navigator.webdriver && !window.__RENDER__` | the preview loop is for a human browser; the renderer sets `__RENDER__` and drives `seek` itself |
| Optional `window.timeline()` → `{ duration, cues: [{t, type}] }` | the renderer writes `out/cues.json` from it so `sfx.mjs` can place sounds by measured peak |
| `primary` in `window.timeline()` (`'9:16'`, `'1:1'`, `'16:9'` or `'4:5'`; or `window.PRIMARY_FORMAT`) | the format `render.mjs` writes unsuffixed (`out/<slug>.mp4`); every other format is suffixed (`out/<slug>-9x16.mp4` …). `--primary` overrides it; with neither, `--format` names the primary, else 9:16. Each run prints which it used |
| Never put `will-change` on anything the camera scales | the browser rasterises it once and the text goes blurry when scaled |
| Fonts via `document.fonts.ready` before the first frame (load with `display=block`) | the renderer waits for it; a canvas drawn before fonts load shows the fallback face |
| One self-contained file; only the libraries the brief names, pinned to a version; no network requests except fonts and those pinned libraries | a library update or a network hiccup changes the film |
| Loops render frames 0 to N − 1; frame N − 1 flows into frame 0 | frame N is frame 0 again; showing it twice is the hiccup at the seam |

Other engines state the same contract with their own hook (`window.renderAt(t)` is a common name). CSS keyframes and the Web Animations API are deterministic only when the renderer pauses every animation at `t` (`document.getAnimations().forEach(a => { a.pause(); a.currentTime = t * 1000; })`); this skill's renderer calls `seek(t)` only, so in Route A everything animates in code. When a fix works, add its rule to the contract: every line in it is a failure you never have to see again.

### Where the contract's mechanics come from

Copy `assets/motion/motion.js` into the film folder and take the contract's mechanics from `assets/motion/seek-template.html`: `window.seek(t)`, `window.timeline()`, `FORMATS` and the layout object `L`, the render hooks. A seamless loop takes its mechanics from `assets/motion/loop-template.html` instead (whole-cycle motion, loopable noise, a settle through frame 0, a `?seam=1` side-by-side check; `finishing.md` § Loops). Both are mechanics examples, opened at the step that needs them (`1-design.md` § 6, `finishing.md` § Loop mechanics from `loop-template.html`) after the look is decided: the shots, look, composition and camera are designed from the references and the brief, never copied from the example's scene.

## The studio in five layers

Every film has these five, each with a file; a layer with no file was skipped, and the model filled that decision with its safest default.

| Layer | What it decides | Its file |
|---|---|---|
| Director | what the film is for, what must be real, what is unacceptable | `docs/brief.md` (`1-design.md`) + `docs/direction.md`, `docs/storyboard.md` (`2-draft.md`) |
| Reference | what it looks like and moves like | `docs/style_guide.md` + `refs/` (`checks.sh refs`) |
| Timeline | what happens when, and on which beat | `docs/camera_plan.md`, `docs/keys.md`, `docs/shotlist.md` + `beats.json` + `window.timeline()` |
| Renderer | the frame at time t | `<slug>.film.html` + `motion.js` → `render.mjs` |
| Critic | whether the frames are good, and what to fix first | `review.md`, `../critique-loop.md` → `docs/review_log.md` |

## The film folder

```
.claude/draw/<slug>/
  <slug>.film.html  motion.js    the film (Route A)
  assets/  (+ manifest.json)      the real screens, logo, fonts — from grab.mjs or the user
  refs/<base>/                    reference frames and tile (checks.sh refs)
  beats.json                      the measured grid (beats.py), if a track was supplied
  docs/brief.md  style_guide.md  direction.md  storyboard.md  camera_plan.md  keys.md  shotlist.md  review_log.md
  out/cues.json  mix.wav  <slug>.beats.png  <slug>[-<fmt>].contact.png  <slug>.strip.png  <slug>[-<fmt>].phone.png  <slug>[-<fmt>].stills.png  keys/
      <slug>.animatic.mp4  <slug>.mp4 (+ <slug>-1x1.mp4 / <slug>-16x9.mp4)  <slug>.poster.png
      check/   checks.sh on the encoded files: <slug>[-<fmt>].contact.png  .strip-<t>.png  .phone.png  .loop_check.mp4  .audio.wav  .waveform.png
  README.md                       the exact render commands, so anyone re-renders without the chat
```

### Resuming a film from its folder

A resumed session reads `docs/review_log.md` first: the last logged round is the gate it resumes from, and any file from this list that is missing is named in the report before new work starts. "The last command exited 0" is never the evidence that the film is done; the files are.

## Routes and engines

### Route A — zero dependencies (default)

One `<slug>.film.html`, `motion.js`, Playwright, ffmpeg. This is what the model reaches for on its own, and it is enough for showreels, product reels, UI morphs, explainers, and 2D loops of type, shapes and UI under ~10 s. Everything in this skill is Route A.

Code-rendered motion is the right tool for product films, UI motion, data stories, typography, diagrams and explainers. Photoreal scenes, characters with organic movement and anything shot are footage: not this lane; when the user has such footage it is an input to trace over (`prompts.md` § L4).

### Route B — a framework, only when the brief names one

Worth it when the same timeline must be re-rendered with different data many times, or a team needs a studio preview. Those frameworks ship their own agent skills that fetch updates from the network; this skill stays self-contained and does not bundle them. If you need one, say so explicitly in the brief; the model otherwise picks Route A. Put the engine in the OUTPUT line with its numbers ("a Remotion composition, 1920 × 1080, 30 fps, 450 frames") so nothing is left to guess.

### Engines compared

| Engine | What it is | Pick it when |
|---|---|---|
| plain HTML + Canvas / SVG / CSS (Route A) | zero installs; `seek(t)` renders it | one idea under ~10 s; 2D loops; anything this skill builds by default |
| Three.js | 3D scenes, lights, materials and shaders on WebGL | anything 3D; drive time from the frame number, never the clock; start the field of view at 35–50°; render on a real GPU when possible |
| Remotion | video as React components, frame-exact (`useCurrentFrame()`, `useVideoConfig()`, `spring()`), with its own agent skills | a series, a template or a data-driven video; free for individuals and companies up to 3 people, larger companies need a licence |
| HyperFrames | HTML, CSS and GSAP timelines in, MP4 out (Apache 2.0; Node 22+ and ffmpeg) | you think in web pages and GSAP timelines |
| GSAP | the web's timeline library, now free including its plugins (its licence bars only building a competing no-code animation builder) | timelines inside a page or a HyperFrames film |
| Motion (formerly Framer Motion) | animates live React interfaces (MIT); no video renderer | the motion lives in a product, not a video |

Licence terms, prices and versions in this table are as of 2026-10; check them before a commercial job.

### Install and render commands for Remotion and HyperFrames

```
# Remotion
npx create-video@latest ; cd my-video ; npm i ; npx remotion skills add ; npx remotion studio
npx remotion render MyComp out/video.mp4
# (commission.md § Route B has the blank-project variant and composition setup)

# HyperFrames
npx hyperframes init my-video ; cd my-video
claude plugin marketplace add heygen-com/hyperframes ; claude plugin install hyperframes@hyperframes
npx hyperframes preview ; npx hyperframes render
```

### The contract holds on every engine

Whatever the engine, the render contract holds: every frame a pure function of `t`, seeded randomness only, no timers, fonts awaited, frames 0 to N − 1.

## Formats

### One timeline, three formats — the layout object `L`

Write scenes against a layout object, not fixed pixels, so one timeline exports 9:16, 1:1 and 16:9; reflow type and UI per format, never crop a 16:9 render to vertical. The template reads `?f=9:16|1:1|16:9` from the URL, sizes the canvas from `FORMATS`, and derives every position from `L` (the layout) once; `render.mjs --format 1:1` opens the page with that query and the matching viewport, `--all` renders the three in one run: the primary format (declared as `primary` in `window.timeline()`, or `--primary`; 9:16 when neither is set) is written unsuffixed as `<slug>.mp4`, and the others as `<slug>-9x16.mp4`, `<slug>-1x1.mp4`, `<slug>-16x9.mp4`; `contact`, `phone` and `stills` follow the same rule (`<slug>.contact.png`, `<slug>-1x1.contact.png` …) so every delivered format gets its own look. A single `--format X` run with no declaration makes X the primary and writes it unsuffixed; with a different declared primary it is suffixed, so it never overwrites the master `<slug>.mp4`. Default canvases: 1080×1920 (vertical), 1440×1440 (square), 1920×1080 (wide). For a 4:5 feed post (1080 × 1350), `render.mjs --format 4:5` renders it (`--all` stays 9:16, 1:1, 16:9); `loop-template.html` already lists 4:5, and a film started from `seek-template.html` adds `'4:5': [1080, 1350]` to its `FORMATS` and reflows it like the others; platforms such as X accept 1:3 to 3:1. Choose the canvas before the first frame: changing it later means re-directing every shot.

### Reflow, never crop

The brief names the primary format; the other two are reflowed from it, not cropped. Reflow is more than sizes: vertical needs larger type, fewer simultaneous elements and a different camera path (`L.show` hides secondary elements per format), square needs shorter holds; a vertical cut is a tighter story, not a narrower one.

### Safe areas

Each format has a **safe area** (`L.safe`): the margins a platform's own UI covers — on 9:16 the caption and action bar take the bottom ~340 px and the top ~220 px; on 1:1 and 16:9 keep 5 %. Nothing the viewer must read sits in the margins; `render.mjs contact|phone|stills --safe` draws the rectangle on every tile so the sheet shows it.

## Two render paths

Everything above is the browser path: `<slug>.film.html` + `motion.js`, `render.mjs`, `checks.sh`. The hand-drawn library under `scripts/hand-drawn/` renders with node-canvas at 24 fps through its own `film.mjs`; its references live in `references/motion/hand-drawn/`. Pick one path per film; the phases and the review loop are the same on both.

## Motion blur

Each output frame is the average of `--sub` subframes (4 by default) rendered at `fps × sub` and blended with ffmpeg `tmix`; the shutter spans one full frame (a 360° shutter). It is what makes fast cursor moves and type slams look filmed rather than stepped. `--sub 1` for a quick preview. A film camera's 180° shutter spans half a frame, which looks crisper on fast motion; for that look, spread the subframes over half the interval and blend in linear light (the published 3D loops did this on a GPU at 60 fps). Either way the blur comes from real subframes, never from a CSS or canvas blur faked on top.

## The commands

### The render and check commands

```
node scripts/motion/render.mjs still   --html paper-plane.film.html --t 3.2          # one frame → out/paper-plane.still-3.20.png
node scripts/motion/render.mjs stills  --html paper-plane.film.html --at 0,3.2,6     # one tile per listed time (bookends, every key, first frame of every shot) → out/paper-plane.stills.png
node scripts/motion/render.mjs hash    --html paper-plane.film.html --t 5            # determinism check (exit 1 if not)
node scripts/motion/render.mjs beats   --html paper-plane.film.html --beats beats.json   # one frame per beat → out/paper-plane.beats.png (+ out/cues.json)
node scripts/motion/render.mjs contact --html paper-plane.film.html --dur 15         # 2 fps, 6 across → out/paper-plane.contact.png
node scripts/motion/render.mjs strip   --html paper-plane.film.html --t 4.2 --n 12   # 12 consecutive frames → out/paper-plane.strip.png
node scripts/motion/render.mjs phone   --html paper-plane.film.html --dur 15         # 360 px tiles → out/paper-plane.phone.png
node scripts/motion/render.mjs animatic --html paper-plane.film.html --dur 15        # 24 fps, no blur, half size: judge pacing before polish → out/paper-plane.animatic.mp4
node scripts/motion/render.mjs full    --html paper-plane.film.html --dur 15 --fps 60 --sub 4 --audio out/mix.wav   # the master → out/paper-plane.mp4
node scripts/motion/render.mjs full    --html paper-plane.film.html --all            # the three formats from one timeline → out/paper-plane.mp4 (the primary, 9:16 unless declared) + -1x1.mp4, -16x9.mp4
node scripts/motion/render.mjs full    --html paper-plane.film.html --from 10 --to 20   # one chunk → out/paper-plane.part-10.00-20.00.mp4 (long pieces: 10 s chunks, concat at the end)
bash scripts/motion/checks.sh contact|strip|phone|loop|probe out/paper-plane.mp4   # the same looks on the encoded master → out/check/paper-plane.contact.png …
bash scripts/motion/checks.sh refs ref.mp4 [0.5]                          # a reference video → refs/ref/frames/ + refs/ref/tile.png to read
bash scripts/motion/checks.sh audio out/paper-plane.mp4                   # the mix alone → out/check/paper-plane.audio.wav + .waveform.png: does it have a shape without the picture?
```

### Renderer defaults

Defaults: `--out out`, viewport 1080×1920, screenshot of `#stage` / the first `<canvas>` / `body`. Encode is H.264 yuv420p CRF 16 with `+faststart`. Before the first measured frame the renderer sweeps the whole timeline once so every canvas font and weight has loaded (a canvas only requests a web font the first time `ctx.font` names it).

### Chunked renders for long pieces

A long piece renders in chunks: `--from/--to` per chapter (a crash costs one chunk; `--keep` leaves the frames), then `ffmpeg -f concat` joins the parts and adds `out/mix.wav` once — the command is printed after each chunk.

### Iterate on the affected seconds; the full render is last

Render only the affected seconds while iterating (`--dur` on a copy with scene offsets, or `strip` around the change); the full render is the last step, after the contact sheet scores 8+ on every row. Effort per task: `1-design.md` § Effort and expectations.

### The whole renderer in thirty lines

With this skill's scripts, `render.mjs` is the renderer and opens Chromium through `launchChromium()` in `scripts/motion/browser.mjs`. On a machine without them, the whole renderer is this (Playwright + ffmpeg); it starts Chromium on a temp profile whose `Local State` is seeded first, the same seed `launchChromium()` writes (see § Known environment failures, the locked Windows account):

```js
// render.mjs   usage: node render.mjs paper-plane.film.html 6 24   (file, seconds, fps); freezes the page at t = i / fps
import { chromium } from 'playwright';
import { pathToFileURL } from 'node:url';
import { mkdirSync, mkdtempSync, writeFileSync, rmSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
const [file = 'paper-plane.film.html', secs = '6', fps = '24'] = process.argv.slice(2);
const FPS = Number(fps), N = Math.round(Number(secs) * FPS);   // frames 0 to N-1
mkdirSync('out/frames', { recursive: true });
const profile = mkdtempSync(join(tmpdir(), 'render-'));
writeFileSync(join(profile, 'Local State'), JSON.stringify({ password_manager: { os_password_blank: false, os_password_last_changed: String(BigInt(Date.now() + 3153600000000) * 1000n + 11644473600000000n) } })); // /draw: skips Windows Chromium's blank-password LogonUser probe, which locks the account
const ctx = await chromium.launchPersistentContext(profile, { viewport: { width: 1200, height: 675 } }); // your canvas
try {
  const page = await ctx.newPage();
  await page.goto(pathToFileURL(file).href, { waitUntil: 'networkidle' });
  await page.evaluate(async () => { await document.fonts.ready; });
  for (let i = 0; i < N; i++) {
    await page.evaluate((t) => {
      if (window.renderAt) window.renderAt(t);
      document.getAnimations().forEach((a) => { a.pause(); a.currentTime = t * 1000; });
    }, i / FPS);
    await page.screenshot({ path: `out/frames/${String(i).padStart(4, '0')}.png` });
  }
} finally {
  await ctx.close();
  rmSync(profile, { recursive: true, force: true, maxRetries: 10, retryDelay: 200 });
}
// ffmpeg -framerate 24 -i out/frames/%04d.png -c:v libx264 -pix_fmt yuv420p -crf 18 -movflags +faststart out/paper-plane.mp4
```

It builds the file URL with `pathToFileURL`, so Windows paths work. Every frame is exact because every PNG is the page frozen at one precise `t`, however slow the machine. Never shorten it to a bare `launch()`: that opens a fresh, unseeded profile on every run.

## The runtime on a fresh machine

The motion lane needs Node, ffmpeg and a Chromium that Playwright can launch (`SKILL.md` § Runtime needs). A missing tool is installed with the one official command, then the run continues:

### Install per platform

| Platform | Install |
|---|---|
| macOS | `brew install node ffmpeg`, then `npm i -g playwright` and `npx playwright install chromium` |
| Windows 11 | `winget install --id OpenJS.NodeJS.LTS -e` and `winget install --id Gyan.FFmpeg -e` (winget puts `ffmpeg` / `ffprobe` on PATH through its Links folder; a terminal opened before the install needs reopening), then `npm i -g playwright` and `npx playwright install chromium` |
| Linux | `sudo apt-get install -y nodejs npm ffmpeg` (or the distro's equivalent), then `npm i -g playwright` and `npx playwright install --with-deps chromium` |

### How `browser.mjs` finds Playwright and Chromium

`scripts/motion/browser.mjs` (shared by `render.mjs`, `grab.mjs`, `verify-page.mjs`) finds Playwright in `--playwright` / `$PLAYWRIGHT_MODULE`, a local install, or the global npm root, and finds **any** installed Chromium build in `$CHROME_PATH`, `$PLAYWRIGHT_BROWSERS_PATH`, or the per-OS Playwright cache (`%LOCALAPPDATA%\ms-playwright` on Windows, `~/Library/Caches/ms-playwright` on macOS, `~/.cache/ms-playwright` on Linux), newest first. When either is missing it prints the install lines above. Windows PowerShell 5.1 has no `&&` (use `;`), and if it refuses to run `npx`, type `npx.cmd`.

### Without any install; software WebGL

Without any install, a single HTML file can still be previewed and screen-recorded, but a recording is not frame-exact and drops frames: fine for a first look, never for a portfolio or a delivery. Software WebGL on a headless box runs around 1–2 s per 1080p frame; plan a 3D render's time around that and iterate on strips.

## Known environment failures

Every failure met in a real run, with the fix that made the next run pass first time. Add a row whenever a run meets a new one.

| You see | Cause | Fix |
|---|---|---|
| `playwright not found` | no local or global Playwright, or (before `browser.mjs`) an absolute `$PLAYWRIGHT_MODULE` path on Windows that `import()` rejected | `npm i -g playwright && npx playwright install chromium`; or point `PLAYWRIGHT_MODULE` at an existing `…/node_modules/playwright/index.js` — absolute Windows paths work now |
| `browserType.launch: Executable doesn't exist at …chromium_headless_shell-NNNN…` | Playwright wants the exact build it shipped with; a different build is installed | nothing, when a Chromium build is in the per-OS cache: `browser.mjs` passes the newest one as `executablePath`. Otherwise `npx playwright install chromium`, or `CHROME_PATH=<…/chrome.exe>` |
| `ffmpeg not found on PATH` | ffmpeg not installed, or installed after the terminal opened | install per the table above; reopen the terminal (Windows) |
| a `node` command waits on `Node.js vX is not installed. Install now? [y/N]` | a version-manager shim pins a version (an `.nvmrc` or a default) that is not installed; in a non-interactive shell it blocks until timeout | install that version with the manager, or call an installed `node` binary by its full path for the run; never start a long command behind a prompt |
| `UnicodeDecodeError: 'cp950'` (or another code page) from Python on Windows | Python reads files in the system code page; the skill's files are UTF-8 | run Python with `PYTHONUTF8=1 PYTHONIOENCODING=utf-8` |
| `window.seek is not a function` when checking a film in an app's preview pane | the pane shows a static snapshot and does not load sibling files such as `motion.js` | check films and pages with `render.mjs` / `verify-page.mjs` (a real Chromium through Playwright), never a preview pane |
| `bed sample rate 44100 ≠ 48000` from `sfx.mjs` (older version) | `music.mjs` and `chiptune.mjs` write 44.1 kHz beds; the mixer works at 48 kHz | nothing: `sfx.mjs` now converts any bed to 48 kHz 16-bit PCM with ffmpeg before mixing |
| the Windows account is locked (Windows Hello and the PIN are rejected after Win+L, `0xC0000234`); Security log event 4625 (logon type 2, `Advapi`, sub-status `0xC000006A`) with `ms-playwright\chromium-*\chrome.exe` as the caller, about one per browser opened, and 4740 after ten | Windows Chromium calls `LogonUser(user, ".", "")` the first time a profile opens a tab, to learn whether the account has a blank password (`password_manager_util_win.cc`); the result is cached in the profile's `Local State`, but Playwright's `launch()` makes a fresh profile every run, so every run is a failed logon. Machines in a domain skip the check | nothing, when the browser is started by the skill: `browser.mjs` `launchChromium()` and every vendored launcher seed the profile's `Local State` before Chromium starts (`tests/scripts/test_draw_skill.py` fails on any launcher that does not). A new script that opens Chromium must use `launchChromium()` (or seed `Local State` itself, as § The whole renderer in thirty lines does); never Playwright's own `launch()` on a fresh profile |
| `unknown --format 4:5` (older `render.mjs`) | 4:5 was not a known format | `render.mjs --format 4:5` is supported now; `--all` still renders 9:16, 1:1 and 16:9 |
