---
name: draw
description: 'Draws an idea, system, dataset or story as a self-contained visual: a static diagram,
  an interactive architecture map, a code-rendered motion video, or an explainer page
  with scrubbable figures (including how-it-works machine figures). Use when the user
  wants something drawn, diagrammed, animated or explained visually — 畫一下, 圖解, 架構圖, 流程圖,
  做成動畫, 做支影片, 說明頁, 原理, 怎麼運作, 運鏡, ''visualize'', ''animate it''. Trigger On ''$baransu:draw''.'
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

# draw — put it on screen

## Codex Port Adapter - Bundled Agent Resolution

This plugin does not assume package-local TOMLs are auto-registered as custom
agents. The required definitions for this skill are bundled at
`../../.codex-agents/<agent-name>.toml`: `verifier`.

Before every named-agent dispatch:

1. Resolve the exact bundled TOML from this `SKILL.md` directory (strip a
   leading `baransu:` namespace from the requested name).
2. Verify the file exists, then pass its absolute path and the task input to a
   generic Codex subagent. The first instruction to that subagent is to read
   the TOML's `developer_instructions` completely before doing any task work
   and to treat relative paths as relative to the TOML file.
3. If the TOML is missing or unreadable, stop with
   `AGENT_DEFINITION_MISSING: <path>`. Never invent, summarize, or substitute a
   role from the agent name.


Turn what the user hands you into a visual that a person can open, scrub, explore, or watch. Two orthogonal questions decide every visual: **what is on this frame** (composition: what to delete, where the one accent goes, how connectors run — the diagram system) and **how it changes over time** (motion: `seek(t)` determinism, springs, a beat grid, looking at your own frames — the motion method). A static diagram is a frame × no time; a film is every frame × time; an explainer page is several frames × their own scrubbers; a seek-overlay diagram is one diagram-system frame × a scrubber. The four lanes below are the common combinations, and they share one spine: plan it in one message, build it, look at it the way a reviewer would, fix the worst three problems, deliver.

All user-facing output is Traditional Chinese (繁體中文); code, identifiers, file paths and the vendored references stay as written.

## Outcome Contract

- **Outcome**: A self-contained artifact under `.codex/draw/<slug>/` — `index.html` (diagram, map, page) or `out/final.mp4` plus its source (motion) — that passes the lane's mechanical check and a scored critique loop, built only from what the user supplied and what this skill bundles.
- **Done when**: The plan (lane, type, size, what the budget cuts) was stated before any file was written; the lane check exits 0 (`self_check.py` / `archify finalize` / `render.mjs hash` + a contact sheet for every delivered format / `verify-page.mjs`); the critique scorecard shows every row ≥ 8 or three rounds were logged; the completion report names the file, the lane, the checks that ran, and the scores.
- **Evidence**: The check command output, `docs/review_log.md` in the output folder, and the captures (`contact.png` / screenshots / the finalize receipt).
- **Output**: `.codex/draw/<slug>/` with the artifact, its source, `docs/review_log.md` (and for a film `docs/brief.md`, the folder in `references/motion/pipeline.md`), captures; Traditional Chinese status and completion messages.
- **Automation**: ultracode=neutral, loop=assisted（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）
  In the same non-interactive pass, read `references/loop-pauses.md` for this skill's own PAUSE classification.
- **Telemetry**: on invocation, append one selection record per `../_shared/selection-telemetry.md`.

## Self-contained by design

Everything this skill needs is inside it: the diagram system (`references/diagram/`, `assets/diagram/`, `scripts/diagram/`), the map engine (`scripts/map/`, `references/map/`), the motion toolchain (`scripts/motion/`, `assets/motion/`, `references/motion/`), and the hand-drawn library (`scripts/hand-drawn/`). It never searches the web for content and never depends on another skill being installed. Inputs are exactly what the user hands over: a description, a file, a repository directory, pasted Mermaid / draw.io / Excalidraw, or a URL the user pasted (fetched once, as data). A diagram about a real codebase reads that codebase; it does not go looking elsewhere. One exception, by the user's request only: **brand matching** may read a brand source the user points at — a site URL, a pasted token set, a local design-system folder, another installed skill's token file, or a brand `$baransu:ui` already captured in `.codex/design/reference-<slug>.md` — through `references/diagram/onboarding.md`; that reading is input, not a dependency, and the resulting skin is saved as a profile so later runs need none of it.

Runtime needs, by form: Node 18+ (map, motion, page checks), Python 3 (diagram checks, beats), ffmpeg + a Chromium that Playwright can launch (motion render, page and map browser checks). **A missing tool is installed, not reported** (step 0 below does it). Only when an install is impossible (no network, no permission) say which step it blocks and deliver what still stands (a diagram needs no browser to be built; a motion piece without ffmpeg stops at the HTML source and says so). Every new environment failure met in a run is added to `references/motion/pipeline.md` § Known environment failures before the run ends, so the next run passes first time.

## The flow (every request)

Four decisions in order, each settled before the next starts: **form → approach → production → check**. Before them, one command makes sure nothing in the toolchain can fail halfway.

### 0. Preflight — the route with the fewest surprises

For anything that will move, be screenshotted, or be checked in a browser (motion, page, map, a diagram with a seek overlay), run first:

```
node scripts/motion/doctor.mjs --install
```

It checks Node, ffmpeg, Playwright, a launchable Chromium and Python's UTF-8 mode, installs whatever is missing with the platform's official command, then renders the shipped template twice in headless Chromium (determinism) and encodes it with ffmpeg. Build only after it prints `READY`. On Windows run Python with `PYTHONUTF8=1 PYTHONIOENCODING=utf-8`; check films and pages with `render.mjs` / `verify-page.mjs`, never an app's preview pane (it does not load `motion.js`). A static diagram skips this step.

### 1. Choose the form — what the user will do with it

| The user wants to… | Form | Output | Read first |
|---|---|---|---|
| read and understand it, with figures that move and can be scrubbed, on a phone | **page** | one HTML page with 3–8 figures | `references/motion/explainer-page.md` |
| see structure, logic, data, or a comparison at a glance, in a doc, README, slide, or post; or watch something travel through it on a scrubber | **diagram** | one HTML, inline SVG, light / dark / full-editorial variants, optional reveal / step / loop motion, or a seek overlay (scrubber + exportable to video) | `references/diagram/README.md` → `style-guide.md` → the type reference; `seek-overlay.md` for the scrubber |
| explore a system: click a node, trace a path, see what is upstream, share a card, prove it against a repo | **map** | one HTML with the viewer runtime; `finalize` receipt | `references/map/README.md` → `authoring-defaults.md` |
| watch it: a reel, launch video, showreel, UI morph, cursor-driven product demo, logo sting, kinetic-type piece, music or lyric video, animated explainer or history film, hand-drawn short, a seamless loop | **motion** | `out/final.mp4` (and 1:1 / 16:9 / 4:5 siblings from the same timeline) from `index.html` + `motion.js` | `references/motion/README.md` |

Each form is a lane: its rules are in § Lane: page / diagram / map / motion below, and `--lane` names it. Decide by the verb and the audience, not by the subject: the same checkout flow is a flowchart for a README, a map for an engineer who will click through it, a reel for a launch tweet, and a page for someone learning it. When two forms fit, pick the one the user will *use*, and say the other exists. `--lane` overrides the guess. Before any of them, ask the upstream question the diagram system asks: *would a well-written paragraph or a 3-column table do the same job?* If yes, say so and offer the table.

### 2. Choose the approach — how the picture explains

| Approach | When the point is | Rules |
|---|---|---|
| **Diagram system** | structure: who connects to whom, where data flows, the order of steps, a comparison, a dataset | `references/diagram/` (and the map engine for the map form): deletion first, one accent, orthogonal connectors, the type reference |
| **Mechanism** | behaviour: what the parts *do*, state changing over time, a rule enforced, a limit hit, the failure the idea prevents — "explain how X works", 怎麼運作, 原理 | § Mechanism figures; `references/mechanism/` |
| **Free creative** | feeling, brand, story, rhythm: a launch reel, a logo sting, a title sequence, an abstract loop, a hand-drawn short | the direction funnel (wide → 3 → 1) with style frames (`references/motion/2-draft.md` § 1), the reference read into a style guide, numbers instead of adjectives (`references/motion/1-design.md`); the hand-drawn library for a drawn look |

Form and approach cross: page × mechanism is an interactive machine in an explainer, motion × mechanism a film whose shot is the machine running, diagram × mechanism a cut-away still, motion × diagram a diagram that animates into a video (seek overlay), page × free creative an editorial page with illustrated figures. The map form always uses the diagram system. When both structure and behaviour matter, draw the structure as a diagram and the one hard-to-see behaviour as a mechanism.

Then the **brief and the plan message** — one message, then build:

- **Brief.** Restate in one or two sentences what must be obvious to the viewer and who they are; for a film also which elements must be real and what would make the result unacceptable even if it looks good (`docs/brief.md`, `references/motion/1-design.md`). Facts about the subject are fixed and asked for when missing (a date, a number, a real service name — never invented); choices about the picture are yours to improve, so propose rather than ask. A real asset the brief names and the user did not supply stops a film (`references/loop-pauses.md`).
- **Plan.** State the form, the approach, the visual type or film structure, the size or primary format (and for a film the route: A unless the brief says otherwise), the palette decision, and what the complexity budget forces out (for a mechanism, its Figure / Hero / Epic size). This is an Input PAUSE: an interactive user may redirect; a non-interactive run proceeds and reports the plan (`references/loop-pauses.md`). Skip the pause only when the request already pins all of it.

### 3. Production — build it; if it moves, make it like a studio

A static diagram or map is built under its form's rules below and goes straight to step 4. **Anything that moves** — a film, a page figure, a diagram seek overlay, a mechanism tour, a loop — runs the motion production phases in `references/motion/` (the brief and look decided in steps 1–2 are its Phase 1):

| Phase | Guide | A film | A page figure, seek overlay or mechanism tour |
|---|---|---|---|
| 2 Draft (草稿) | `2-draft.md` | direction funnel, 6 : 3 : 1 per shot, colour script, storyboard, camera plan, timing sheet, keys-only animatic | the figure's point (its caption), the sequence of states it steps through |
| 3 Keys (關鍵幀／首尾幀) | `3-keys.md` | first and last frames as a pair, every key card, `KEYS` as data | the rest frame (`data-rest`) and each state as a still |
| 4 Shoot (攝影) | `4-shoot.md` | interval design, in-betweens from `KEYS`, camera, dailies ≥ 3 rounds | in-betweens from the states, springs by mass |
| 5 Post (後製) | `5-post.md` | seams, sound on frame + 1, full render, loops, export | the page check (`verify-page.mjs`) |

A seamless loop starts from `assets/motion/loop-template.html` and passes its seam check (`references/motion/finishing.md` § Loops). Write the full file; never a partial skeleton.

### 4. Check and deliver

Run the form's check and open the captures: `self_check.py` (diagram), `archify finalize` (map), `render.mjs hash` + a contact sheet per delivered format (motion), `verify-page.mjs` (page). Score the card in `references/critique-loop.md`, list the three worst problems with ids, frame numbers or timestamps, fix them at the phase that owns them, repeat — at least three rounds for motion and page, until every row ≥ 8 — and log rounds in `docs/review_log.md` (`references/motion/review.md` has the techniques). A film's encoded master is reviewed on its own (`review.md` § Review the export). Deliver with the report at the end of this file; never claim a check that did not run.

Output folder: `.codex/draw/<slug>/` (slug from the title, ASCII, ≤ 60 chars; an all-CJK title falls back to a romanised or date-stamped slug). An existing slug gets `-2`, never overwritten.

## Lane: diagram

The vendored diagram system is the authority; this section is the route through it.

- **Philosophy.** The highest-quality move is deletion. Every node is a distinct idea; every connection carries information; the accent goes on 1–2 focal elements; target density 4/10; above 9 nodes it is two diagrams.
- **Selection.** When behaviour, state, enforcement or risk carries the meaning, pick one semantic pattern from `references/diagram/semantic-patterns.md` first, then the nearest visual type; otherwise pick the type from the table in `references/diagram/README.md`. Load that type reference before drawing, every time.
- **Design system.** Tokens and typography from `references/diagram/style-guide.md` (a warm-neutral paper, one accent, serif title + sans names + mono technical sublabels; CJK labels extend the family and keep a 12 px floor). **Style-guide gate** (upstream §0): on the first diagram in a project whose skin is still the shipped default and that has no `.diagram-design` marker, ask once whether to match a brand (URL / tokens / folder / installed skill / `$baransu:ui`'s `reference-<slug>.md` / saved profile / keep default) — an Input PAUSE, default *keep default*; a resolved marker or profile skips it. Branding then follows `onboarding.md` and is saved per `profiles.md`.
- **Markup.** Copy `assets/diagram/template.html` (or `-dark`, `-full`, `-motion`, `-terminal`), replace eyebrow, h1 and the SVG body, fill `<title>` and `<desc>` with slug-prefixed ids. Exact primitives and the six connector rules: `references/diagram/primitives-core.md`. Orthogonal elbows only, masked labels with a visible gap, no overlaps, fan attach points, no transit behind a non-endpoint box, mask before node. Arrows before boxes. Legend as a bottom strip. Every coordinate on the 4 px grid (`layout-budget.md`); type sizes from the ramp in `output-spec.md` for the chosen size preset.
- **Sizes and dials.** `output-spec.md`: format (`html` / `svg` / `png`), size preset (`doc-inline` default … `slide-16x9`, `social-og`, print), detail level, audience. An import (`import-mermaid.md`, `import-drawio.md`, `import-excalidraw.md`) extracts with `scripts/diagram/<format>_extract.py`, sets the four dials, redraws (never converts), and reports the fidelity ledger.
- **Motion** only when asked or when order genuinely needs it. Two kinds: the upstream modes `reveal` / `step` / `loop` (`references/diagram/animation.md`; controller copied verbatim from `assets/diagram/template-motion.html`) for a short ordered explanation; or a **seek overlay** (`references/diagram/seek-overlay.md`, start from `assets/diagram/template-seek.html`) when the user wants to scrub a token travelling the real connectors while nodes light up in order — the same `window.seek(t)` contract as a film, so `render.mjs` can also export it as video. Either way the static frame is complete without JavaScript and under reduced motion; a seek overlay ships with its static twin (`scripts/diagram/seek_split.py` writes it and runs `self_check.py` on it).
- **Check.** `python3 scripts/diagram/self_check.py <file>` must pass; the type reference may name a stricter verifier under `scripts/diagram/repo/` (`verify-geometry.py`, `verify-motion.py`, `lint-skin.py`, per-type `verify-*.py`); then a browser look via `node scripts/motion/verify-page.mjs <file> --selector svg`. Then run `references/diagram/taste-gate.md` (universal anti-patterns, remove test, signal test, technical and typography rows) on the finished file; one failing row is a fix.
- **Export** to PNG or SVG only when asked: `references/diagram/export.md`, `scripts/diagram/export_svg.py`.

## Lane: map

The vendored engine renders typed JSON into an explorable HTML and refuses to ship an unchecked one.

### Type router

| Type | Use for | Schema | Example |
|---|---|---|---|
| `architecture` | components, services, boundaries, infrastructure; what something everyday is made of | `scripts/map/schemas/architecture.schema.json` | `scripts/map/examples/web-app.architecture.json`; deployments: `production-deployment.architecture.json` |
| `workflow` | processes, approval gates, tool calls, runbooks, CI/CD; step-by-step plans | `workflow.schema.json` | `agent-tool-call.workflow.json` |
| `sequence` | API call chains, request lifecycles, async traces; a back-and-forth between people | `sequence.schema.json` | `cache-miss-request.sequence.json` |
| `dataflow` | pipelines, ETL/ELT, lineage, consumers; where money or documents go | `dataflow.schema.json` | `product-analytics.dataflow.json` |
| `lifecycle` | state / status transitions, retries, waiting and terminal states | `lifecycle.schema.json` | `deployment-release.lifecycle.json` |

Ambiguous? `node scripts/map/bin/archify.mjs guide "<scenario>" --json`.

- **Author** per `references/map/authoring-defaults.md`: composition led by the main user journey, boundaries that express real isolation, labels with meaning, placement by actual connections before coordinates, automatic routes first. Examples teach shape, not facts. Set `meta.output` to a portable relative `.html`, `meta.quality_profile: "showcase"` unless dense `standard` was asked for. For a real repository follow `references/map/repository-authoring.md`: pin the commit, attach `sources` to every asserted node, pass `--repo-root`.
- **Environment first.** The browser gate only finds a browser through `ARCHIFY_CHROME`; it does not look for Playwright's Chromium on its own. Before the first `finalize`, export it (and the sandbox opt-out in a container), and switch off the package's network update check:

  ```bash
  export ARCHIFY_CHROME="${CHROME_PATH:-$(ls -d ${PLAYWRIGHT_BROWSERS_PATH:-$HOME/.cache/ms-playwright}/chromium-*/chrome-linux*/chrome 2>/dev/null | tail -1)}"
  export ARCHIFY_CHROME_NO_SANDBOX=1 ARCHIFY_UPDATE_CHECK_DISABLED=1
  ```

  (macOS: `ARCHIFY_CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"`.) A receipt that says `chrome-unavailable` / `browser-check: skipped` is an environment failure: set the variable and rerun — never "repair" a candidate for it.
- **Finalize.** `node scripts/map/bin/archify.mjs finalize <type> candidate.json <slug>.html --quality showcase --json [--repo-root <repo>]`. A passing receipt is the evidence. Non-zero is never success: repair the connected neighbourhood per `references/map/delivery-contract.md` § Failed finalize, within its repair limit, and rerun the complete command. With `ARCHIFY_UPDATE_CHECK_DISABLED=1` set the receipt's `update` block reads `disabled`; ignore it either way and never run `scripts/map/scripts/check-update.mjs`.
- **Motion and viewer features** (`meta.animation: "trace"`, share cards, presentation) are opt-in; read `references/map/viewer-runtime.md` only when asked.
- **No shell?** Hand-place architecture SVG into `scripts/map/assets/template.html` with the semantic CSS classes, and follow the visual-review contract in `delivery-contract.md`.

## Lane: motion

A film is a program: `window.seek(t)` paints the exact frame for any instant; Playwright samples it, ffmpeg stitches it. It is made the way an animation studio makes one, in **five phases with a gate each** — Design → Draft → Keys → Shoot → Post — and a **technique library** each phase opens only at the step that needs it. `references/motion/README.md` is the map; read the phase guides in order.

| Phase | Guide | Settles | Gate |
|---|---|---|---|
| 1 Design (設計) | `references/motion/1-design.md` | facts vs choices and the real assets (`docs/brief.md`); the reference read into `docs/style_guide.md`; numbers instead of adjectives, the ban list, identity locks; faces; a supplied track measured; route, formats, folder; the plan message | every real asset present or the film stops |
| 2 Draft (草稿) | `references/motion/2-draft.md` | the direction funnel wide → 3 → 1 (art concept, theme, story idea, a style frame each for the three); every shot's 6 : 3 : 1 hierarchy (`references/motion/composition.md`); the colour script; the storyboard with timed reads and an event per shot; the cinematography plan (shot size, angle, lens feel, named move with its duration and curve, hold, screen direction); a transition per seam; the pacing curve and timing sheet; draft key cards | a keys-only animatic with temp sound reads as a story |
| 3 Keys (關鍵幀／首尾幀) | `references/motion/3-keys.md` | the first and last frames judged as a pair; every key finished on its key card (read, composition, framing, subject state, type, look, motion in / out, sound, formats, checks) and written as `KEYS` data | every key passes the critique card as a still |
| 4 Shoot (攝影) | `references/motion/4-shoot.md` | one shot-list line per interval; in-betweens computed from `KEYS`; the camera moving between approved framings; dailies (beats, contact, strip, phone, animatic) ≥ 3 rounds | keys re-render settled; `hash` prints `DETERMINISTIC`; every score ≥ 8 or three rounds logged |
| 5 Post (後製) | `references/motion/5-post.md` | seams executed; sound on frame + 1, measured on the decoded file; the full render; loops and exports; the encoded master reviewed; the package and report | the master passes its review; the report names only checks that ran |

The technique library (`references/motion/`): `pipeline.md` (the render contract, film folder, routes and engines, formats and safe areas, motion blur, commands), `prompts.md` (the prompt ladder L1–L4, the directed prompt, the XML state list, the director's brief, the honest numbers), `springs.md` (the `motion.js` primitives and the motion numbers: cubic-beziers, damping ratio, durations, stagger, hierarchy, the animation principles), `camera.md` (24 named moves, the parallax rule, the story clock), `transitions.md`, `type.md`, `beat-grid.md` (the grid, synthesized score and SFX, sync and loudness measurement), `review.md` (how to look, notes by frame number, the export review, fixes), `finishing.md` (loops, export, platform limits), `chapters.md` (over a minute), `commission.md` (client work).

The rules that break films when ignored:

- **Determinism.** No CSS transitions, no timers, no `requestAnimationFrame` in render mode, no state between frames, seeded noise only (`Motion.rng`), fonts awaited, only pinned libraries. `node scripts/motion/render.mjs hash --html index.html --t <t>` must print `DETERMINISTIC`.
- **Start** from `assets/motion/seek-template.html` + `assets/motion/motion.js` copied into the film folder. One object per shot; everything derives from local t.
- **Direct with numbers, not adjectives.** When the ask is a one-liner, climb the ladder for the user: ask for a reference and a state list before building a "showreel" nobody can tell from the thousand others (`prompts.md`). A product URL the user pastes becomes real assets through `node scripts/motion/grab.mjs <url>` (screenshots at the three formats, `manifest.json` with the computed fonts and colours); a reference video becomes frames through `checks.sh refs`; both are written into `docs/style_guide.md` before the draft.
- **Keyframes first.** Bookends, then keys, then interval design, then in-betweens computed from the key data — never motion before the keys are approved as stills (`3-keys.md`, `4-shoot.md`).
- **Springs, not curves** (`springs.md`): `spring` for anything that moves, by the mass of the thing (snappy / ui / heavy / playful); a value with several targets is `track()` — one spring per change, never a restart; `stretch()` for two-edge indicators; `swapAlpha()` + `swapBlur()` so content enters after a morph starts and leaves before the next; the last frame equals the first for a loop, cursor included. Fixed easing only where mass would lie: fades, `drawOn` (a chart drawing itself), `countUp` (one number that proves it), wipes, lens moves. One hero move per shot; secondary moves at 50–70 % of its travel, 100–200 ms later.
- **What the viewer sees.** A cursor that really clicks, types and drags (`Motion.cursor / typed / drag`), each click on a beat with the UI answering a frame later; a camera that re-frames every state (`Motion.camera`, push-ins as smaller rects) and whose moves are named — pan, tilt, dolly vs zoom, tracking, orbit, crane, dolly zoom, rack focus, handheld, FPV, dutch, slow motion, speed ramp, time-lapse, freeze frame — each drawn by the parallax rule in `camera.md`; type that lands word by word (`Motion.words`, `type.md`: one display face + one UI face + the accent, hook ≤ 5 words ≥ ⅓ frame height, nothing in corners, text held 0.3 s per word + 0.5 s); a named transition at every seam, drawn as geometry (`wipe / iris / whip`, `transitions.md`, which also has jump, match, smash, dissolve, J- and L-cuts), never a fade to black between UI states. Director's notes are written in camera words and frame numbers, never "make it better" (`review.md`).
- **Sound** (`beat-grid.md`): a supplied track is measured with `python3 scripts/motion/beats.py` (`beats` → small changes, `downbeats` → cuts, `hits` → SFX); without one, synthesize at the film's tempo. UI sounds come from `window.timeline()` cues through `node scripts/motion/sfx.mjs`, each hit's peak on frame + 1, 3–6 dB over the bed, about −14 LUFS, checked in the phone band and on the decoded file.
- **Look before the full render.** Dailies (`render.mjs beats`, `contact`, `strip --t <time>` around every fast action, `phone`, `animatic`) scored ≥ 3 rounds; only then `render.mjs full --fps 60 --sub 4 --audio out/mix.wav`, then `scripts/motion/checks.sh contact|strip|loop|probe` on the encoded master. A full render is an Authorization PAUSE under a non-interactive driver.
- **Formats.** Scenes draw against the layout object `L` derived from `W×H`, so 9:16, 1:1 and 16:9 come from one timeline (`?f=` on the page, `render.mjs --format` / `--all`); reflow, never crop — vertical gets fewer simultaneous elements (`L.show`), not smaller ones. Nothing the viewer must read sits in the format's safe area (`L.safe`; `--safe` draws it on every sheet). A contact sheet per delivered format (`contact --all`) before the siblings ship.
- **Long pieces** (over a minute): chapters, a shared `ANIMATION_GUIDE.md`, one file per chapter, subagents per chapter, chunked renders (`chapters.md`).
- **Client work** (`commission.md`): a sample is labelled `Concept demo` and uses no third-party logos or invented results; the story is written in frame ranges that cover every frame; copy, colours and asset paths sit apart from the motion; the export itself is reviewed (a sheet every second and at every scene boundary, a probe of duration / size / fps / audio, a final three-second hold, at most three fix passes, an unrun check never reported as passed) and packaged with its source and render commands. Help with finding, pricing or answering a brief only when asked, and nothing is sent on the user's behalf.
- **Hand-drawn look** (storybook, brush-ink, watercolour, low-poly, game feel, characters): the bundled canvas library under `scripts/hand-drawn/` (`npm install` there once for `@napi-rs/canvas`), its references under `references/motion/hand-drawn/` (start at `workflow.md`, `motion.md`, `traps.md`), its `templates/film-template.mjs` as the starting point. Original characters only.

## Lane: page

The explainer page is 3–8 `seek(t)` figures inside a reading column, each with play / pause and a scrubber, the whole page theme-aware and phone-safe. A figure that *is* a diagram (an architecture, a flow) should be a seek-overlay SVG built under the diagram lane's rules and embedded here, not a canvas approximation of one; canvas figures are for charts, timelines, and abstract mechanisms. A figure that must show *how* something works is a mechanism figure (§ Mechanism figures). `references/motion/explainer-page.md` has the mechanics; `assets/motion/explainer-template.html` is a complete worked example to copy mechanics from, never content. Write every caption first (a caption that cannot add a dimension means the figure has no point), draw rest frames, then animate, then `node scripts/motion/verify-page.mjs page.html` until it reports no errors and no horizontal scroll at phone width.

## Mechanism figures (any form)

A mechanism figure explains how something works by drawing a real, nameable machine whose moving parts behave the way the idea does: a queue as a marble run, an LRU cache as a bookcase, a bloom filter as a fruit machine, a mutex as a tank with an interlock key. It is a way of explaining, not a lane: it lands in whichever lane the output calls for.

**When it applies.** The user wants to understand *how* or *why* something works, not only what is connected to what — "explain how X works", "怎麼運作", "原理", "機制", "為什麼會這樣", "make it intuitive", "an interactive explainer of X", "機構圖" — and the subject is an algorithm, a data structure, a protocol, a system behaviour, a physical machine or process (an engine, a watch, a reactor). Also when the user names an object to build ("a metronome on a plinth, swinging at 120 bpm").

**Mechanism or diagram — decide by what carries the meaning.**

| The point is | Draw |
|---|---|
| who is connected to whom, where data flows, what calls what, the order of steps | a diagram (flowchart, architecture, sequence) — diagram lane |
| what the parts *do*: state changing over time, a rule enforced, a limit hit, a race, the failure the idea exists to prevent | a mechanism figure |
| both | the diagram for the structure, a mechanism figure for the one behaviour that is hard to see |

**Where it lands.**

| The user wants | Lane | Form |
|---|---|---|
| to understand it, read, scrub, play with it (default) | **page** | one or more mechanism figures in the explainer page; pointer and keyboard only when they asked for an interactive figure |
| a film or reel that shows it working | **motion** | the machine running is the shot; its tour keys are the film's keys |
| a still for a doc or slide | **diagram** | a cut-away or exploded still (`references/diagram/type-exploded.md`) built by the same rules |

**How.** `references/mechanism/mechanism.md`: the one rule (the object is the explanation — no boxes, arrows or floating labels), the Figure / Hero / Epic size stated in the plan message before any work, the ten steps (truth first, invent the object, at least 40 parts, one lit part, numbers from one model), the drawing, motion, shader, 3D and verification rules, and § Inventing your own (find the idea's verb → a mechanism family → a part-to-meaning table → test the mapping, including the failure case). `references/mechanism/mechanism-catalog.md` lists 52 published ideas with their machines; start from a row when the idea is there, read three or four rows to see how a mapping is made when it is not. Its idle tour is a sequence of keys (`references/motion/3-keys.md`), so it scrubs, renders to video, and passes `render.mjs hash` like any figure.

## Red lines

Scan these by the 🛑 marker. Each restates a rule above; breaking one means the output is compromised.

| 🛑 Anti-pattern | Why it fails | Correct approach |
|---|---|---|
| 🛑 Looking outside the skill for content, or depending on another skill being installed | breaks the self-contained contract; the result depends on something the user did not supply | use what the user gave and what is bundled; a brand source the user points at is input, read it once and save a profile |
| 🛑 Inventing data, names, dates, or UI to fill a slot | the viewer cannot tell invented from real; the artifact becomes a liar | keep the identifier, ask, or (diagram and map) leave the slot visibly empty; a film stops on a missing real asset |
| 🛑 Writing files before the plan message | the user's one cheap chance to redirect is gone | one plan message, then build (Input PAUSE) |
| 🛑 Accent on more than two elements; a second hue; shadows; rounded-2xl; dark + neon glow | the signals that mark a generated diagram | one accent, borders not shadows, radius ≤ 8, the vendored style guide |
| 🛑 Diagonal connectors, labels on the stroke, overlapping paths, transit behind a box | automatic fail of the six connector rules | orthogonal elbows, masked labels with a gap, reroute or hop over the single crossing |
| 🛑 A map delivered after a non-zero `finalize` | the receipt is the evidence; without it there is none | repair and rerun; deliver the last passing artifact or report the gate |
| 🛑 `Math.random`, timers, or CSS transitions in a `seek(t)` film | frames depend on history; renders drift; parallel workers disagree | seeded noise, closed-form springs, `hash` check |
| 🛑 Animating before the first frame, the last frame and the keys are approved as stills | the motion inherits a composition nobody judged; a bad key is found after every interval around it was built | bookends → keys → interval design → in-betweens computed from the key data (`references/motion/3-keys.md`, `4-shoot.md`) |
| 🛑 A how-it-works figure drawn as labelled boxes, floating plates, or one slab with a few lines | too abstract or too flat: it says the parts exist, not what they do | a nameable machine of 40+ parts whose motion *is* the idea, one lit part, numbers from one model (`references/mechanism/mechanism.md`) |
| 🛑 Full render before the contact sheet scores 8+ | an hour of rendering to find a dead beat at 4 s | beats → contact → strip → fix, three rounds, then full |
| 🛑 Centered title on a gradient, everything fading in, corner labels, frame borders, glow on UI chrome, particle bursts, a fade to black between two UI states | the default look everyone recognises | a reference and a state list; the anti-slop rows of the scorecard; a transition drawn as geometry with the accent carried across |
| 🛑 A caption that restates the title | adds nothing; reads as filler | a trade-off, a next step, or a dimension the figure does not show |
| 🛑 Claiming a visual check that did not run | the report lies about the evidence | name the command that ran and what it showed; say when a look was impossible |

## Completion report

```
✅ 已完成：.codex/draw/{slug}/{artifact}
Lane：{diagram | map | motion | page}　型別／結構：{type or film structure}　尺寸：{preset or format}
檢查：{command} → {result}（{captures or receipt path}）
評分：{hook}/{readability}/{continuity}/{motion}/{variety}/{composition}/{accuracy}/{sound}（{N} 輪，review_log.md）
砍掉的：{what the budget cut, or 無}
下一步可以更好：{one line}
```

Add the lines the lane needs: a fidelity ledger for an import; the finalize summary for a map; for a film the sibling formats with their contact sheets, `out/loop_check.mp4`, the poster frame (`render.mjs still --t <best frame>` → `out/poster.png`), 「素材清單」 (the real assets used, from `manifest.json`), 「待人工確認」 (what could not be verified: brand colour exactness, the track's licence, a number the user gave), and 「重渲指令」 (the exact `render.mjs full …` line, also in the folder's README); 「此處採預設」 annotations under a non-interactive driver.

## Not for

- Styling, building or refining the UI of the user's own application → `$baransu:ui`. Placing a finished diagram *inside* that application or docs site is `$baransu:ui`'s step too: export the SVG with `scripts/diagram/export_svg.py`, hand the file over. A brand `$baransu:ui` captured in `.codex/design/reference-<slug>.md` is a valid brand source for `onboarding.md`; a profile `$baransu:draw` saved is reusable by both.
- Fetching a page into Markdown → `$baransu:read`; digesting sources into a learning note → `$baransu:learn`.
- A dashboard over live numbers, or a chart whose point is the data pipeline rather than the picture.
- Editing a video someone shot, lip-sync, talking heads: nothing here renders pixels it did not draw.

## Attribution

Bundled third-party material and its licenses are listed in `NOTICE.md`; keep that file with the skill.
