---
name: draw
description: "Draws any idea, system, process, dataset, or story as a self-contained visual: an editorial static diagram (44 types, HTML + inline SVG), an explorable interactive map (architecture / workflow / sequence / data flow / lifecycle, validated, exportable), a code-rendered motion video (seek(t) → MP4 / WebM, springs, beat grid, synthesized sound), or a one-page explainer with scrubbable animated figures. Use this skill whenever the user wants something visualized, diagrammed, animated, storyboarded, or turned into a reel, launch video, showreel, architecture map, flowchart, sequence diagram, timeline, chart, or explainer page — even if they only say 畫一下, 畫成圖, 圖解, 做成動畫, 做支影片, 架構圖, 流程圖, 時序圖, 說明頁, 'draw this', 'visualize', 'make a diagram', 'animate it', 'motion graphics', or paste Mermaid / draw.io / Excalidraw to redraw. Trigger On '/draw'. Not For: styling the UI of the user's own app (/ui), capturing a page as Markdown (/read), digesting sources into notes (/learn), or a numeric dashboard with live data."
argument-hint: "<what to draw | file | repo dir | pasted text> [--lane diagram|map|motion|page] [--format 9:16|1:1|16:9] [--dark]"
user-invocable: true
---

# draw — put it on screen

Turn what the user hands you into a visual that a person can open, scrub, explore, or watch. Four lanes share one spine: plan it in one message, build it, look at it the way a reviewer would, fix the worst three problems, deliver.

All user-facing output is Traditional Chinese (繁體中文); code, identifiers, file paths and the vendored references stay as written.

## Outcome Contract

- **Outcome**: A self-contained artifact under `.claude/draw/<slug>/` — `index.html` (diagram, map, page) or `out/final.mp4` plus its source (motion) — that passes the lane's mechanical check and a scored critique loop, built only from what the user supplied and what this skill bundles.
- **Done when**: The plan (lane, type, size, what the budget cuts) was stated before any file was written; the lane check exits 0 (`self_check.py` / `archify finalize` / `render.mjs hash` + contact sheet / `verify-page.mjs`); the critique scorecard shows every row ≥ 8 or three rounds were logged; the completion report names the file, the lane, the checks that ran, and the scores.
- **Evidence**: The check command output, `docs/review_log.md` in the output folder, and the captures (`contact.png` / screenshots / the finalize receipt).
- **Output**: `.claude/draw/<slug>/` with the artifact, its source, `docs/review_log.md`, captures; Traditional Chinese status and completion messages.
- **Automation**: ultracode=neutral, loop=assisted（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）
  In the same non-interactive pass, read `references/loop-pauses.md` for this skill's own PAUSE classification.
- **Telemetry**: on invocation, append one selection record per `../_shared/selection-telemetry.md`.

## Self-contained by design

Everything this skill needs is inside it: the diagram system (`references/diagram/`, `assets/diagram/`, `scripts/diagram/`), the map engine (`scripts/map/`, `references/map/`), the motion toolchain (`scripts/motion/`, `assets/motion/`, `references/motion/`), and the hand-drawn library (`scripts/hand-drawn/`). It never looks for another skill, a project design system or token file, or an update server, and it never searches the web for content. Inputs are exactly what the user hands over: a description, a file, a repository directory, pasted Mermaid / draw.io / Excalidraw, or a URL the user pasted (fetched once, as data). A diagram about a real codebase reads that codebase; it does not go looking elsewhere.

Runtime needs, by lane: Node 18+ (map, motion, page checks), Python 3 (diagram checks, beats), ffmpeg + a Chromium that Playwright can launch (motion render, page and map browser checks). When a tool is missing, say which lane step it blocks and deliver what still stands (a diagram needs no browser to be built; a motion piece without ffmpeg stops at the HTML source and says so).

## Choose the lane

| The user wants to… | Lane | Output | Read first |
|---|---|---|---|
| see structure, logic, data, or a comparison at a glance, in a doc, README, slide, or post | **diagram** | one HTML, inline SVG, light / dark / full-editorial variants, optional reveal / step / loop motion | `references/diagram/README.md` → `style-guide.md` → the type reference |
| explore a system: click a node, trace a path, see what is upstream, share a card, prove it against a repo | **map** | one HTML with the viewer runtime; `finalize` receipt | `references/map/README.md` → `authoring-defaults.md` |
| watch it: a reel, launch video, showreel, UI morph, music-driven piece, hand-drawn short | **motion** | `out/final.mp4` (and 1:1 / 16:9 siblings) from `index.html` + `motion.js` | `references/motion/pipeline.md` → `springs.md` → `beat-grid.md` |
| read and understand it, with figures that move and can be scrubbed, on a phone | **page** | one HTML page with 3–8 canvas figures | `references/motion/explainer-page.md` |

Decide by the verb and the audience, not by the subject: the same checkout flow is a flowchart for a README, a map for an engineer who will click through it, a reel for a launch tweet, and a page for someone learning it. When two lanes fit, pick the one the user will *use*, and say the other exists. `--lane` overrides the guess.

Before any of them, ask the upstream question the diagram system asks: *would a well-written paragraph or a 3-column table do the same job?* If yes, say so and offer the table.

## The spine (every lane)

1. **Brief.** Restate in one or two sentences what must be obvious to the viewer and who they are. Missing facts (a date, a number, a real service name) are asked for, never invented.
2. **Plan — one message, then build.** State the lane, the visual type or film structure, the size or format, the palette decision, and what the complexity budget forces out. This is an Input PAUSE: an interactive user may redirect; a non-interactive run proceeds and reports the plan (`references/loop-pauses.md`). Skip the pause only when the request already pins all of it.
3. **Build** under the lane's rules below. Write the full file; never a partial skeleton.
4. **Look.** Run the lane's check and open the captures. Score the card in `references/critique-loop.md`, list the three worst problems with ids or timestamps, fix them at module level, repeat; at least three rounds for motion and page, until every row ≥ 8. Log rounds in `docs/review_log.md`.
5. **Deliver** with the report at the end of this file.

Output folder: `.claude/draw/<slug>/` (slug from the title, ASCII, ≤ 60 chars; an all-CJK title falls back to a romanised or date-stamped slug). An existing slug gets `-2`, never overwritten.

## Lane: diagram

The vendored diagram system is the authority; this section is the route through it.

- **Philosophy.** The highest-quality move is deletion. Every node is a distinct idea; every connection carries information; the accent goes on 1–2 focal elements; target density 4/10; above 9 nodes it is two diagrams.
- **Selection.** When behaviour, state, enforcement or risk carries the meaning, pick one semantic pattern from `references/diagram/semantic-patterns.md` first, then the nearest visual type; otherwise pick the type from the table in `references/diagram/README.md`. Load that type reference before drawing, every time.
- **Design system.** Tokens and typography from `references/diagram/style-guide.md` (a warm-neutral paper, one accent, serif title + sans names + mono technical sublabels; CJK labels extend the family and keep a 12 px floor). The skin stays at the shipped default unless the user supplies a brand; then `onboarding.md` or a saved profile (`profiles.md`).
- **Markup.** Copy `assets/diagram/template.html` (or `-dark`, `-full`, `-motion`, `-terminal`), replace eyebrow, h1 and the SVG body, fill `<title>` and `<desc>` with slug-prefixed ids. Exact primitives and the six connector rules: `references/diagram/primitives-core.md`. Orthogonal elbows only, masked labels with a visible gap, no overlaps, fan attach points, no transit behind a non-endpoint box, mask before node. Arrows before boxes. Legend as a bottom strip. Every coordinate on the 4 px grid (`layout-budget.md`); type sizes from the ramp in `output-spec.md` for the chosen size preset.
- **Sizes and dials.** `output-spec.md`: format (`html` / `svg` / `png`), size preset (`doc-inline` default … `slide-16x9`, `social-og`, print), detail level, audience. An import (`import-mermaid.md`, `import-drawio.md`, `import-excalidraw.md`) extracts with `scripts/diagram/<format>_extract.py`, sets the four dials, redraws (never converts), and reports the fidelity ledger.
- **Motion** only when asked or when order genuinely needs it: `references/diagram/animation.md`; modes `reveal` / `step` / `loop`; the controller is copied verbatim from `assets/diagram/template-motion.html`; the static frame is complete without JavaScript and under reduced motion.
- **Check.** `python3 scripts/diagram/self_check.py <file>` must pass; the type reference may name a stricter verifier under `scripts/diagram/repo/` (`verify-geometry.py`, `verify-motion.py`, `lint-skin.py`, per-type `verify-*.py`); then a browser look via `node scripts/motion/verify-page.mjs <file> --selector svg`. Run the taste gate (remove test, signal test, technical list) from `references/diagram/README.md` § Export and checks.
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
- **Finalize.** `node scripts/map/bin/archify.mjs finalize <type> candidate.json <slug>.html --quality showcase --json [--repo-root <repo>]`. A passing receipt is the evidence. Non-zero is never success: repair the connected neighbourhood per `references/map/delivery-contract.md` § Failed finalize, within its repair limit, and rerun the complete command. Ignore the receipt's `update` block and never run `scripts/map/scripts/check-update.mjs`.
- **Motion and viewer features** (`meta.animation: "trace"`, share cards, presentation) are opt-in; read `references/map/viewer-runtime.md` only when asked.
- **No shell?** Hand-place architecture SVG into `scripts/map/assets/template.html` with the semantic CSS classes, and follow the visual-review contract in `delivery-contract.md`.

## Lane: motion

A film is a program: `window.seek(t)` paints the exact frame for any instant; Playwright samples it, ffmpeg stitches it. `references/motion/pipeline.md` is the contract; these are the rules that break films when ignored.

- **Determinism.** No CSS transitions, no timers, no `requestAnimationFrame` in render mode, no state between frames, seeded noise only (`Motion.rng`), fonts awaited. `node scripts/motion/render.mjs hash --html index.html --t <t>` must print `DETERMINISTIC`.
- **Start** from `assets/motion/seek-template.html` + `assets/motion/motion.js` copied into the film folder. One object per shot; everything derives from local t.
- **Springs, not curves** (`references/motion/springs.md`): `spring` for anything that moves, by the mass of the thing (snappy / ui / heavy / playful); a value with several targets is `track()` — one spring per change, never a restart; `stretch()` for two-edge indicators; `swapAlpha()` so content enters after a morph starts and leaves before the next; the last frame equals the first for a loop, cursor included.
- **Beat grid** (`references/motion/beat-grid.md`): a supplied track is measured with `python3 scripts/motion/beats.py` (`beats` → small changes, `downbeats` → cuts, `hits` → SFX); without one, synthesize at the film's tempo. UI sounds come from `window.timeline()` cues through `node scripts/motion/sfx.mjs`, placed by measured peak, mixed to about −14 LUFS.
- **Structure.** A storyboard with timed reads before scene code (`references/motion/storyboard.md`): one read at a time, snap then hold, an event in every shot, a transition at every seam, something new every 2–4 s, a hook in the first 2 s, frame 0 never empty. Longer than a minute → chapters, a shared `ANIMATION_GUIDE.md`, one file per chapter, subagents per chapter (`references/motion/chapters.md`).
- **Prompts and briefs.** When the user's ask is a one-liner, climb the ladder for them: ask for a reference and a state list before building a "showreel" nobody can tell from the thousand others (`references/motion/prompt-ladder.md`; the XML state-list spec and the director's brief template live there).
- **Hand-drawn look** (storybook, brush-ink, watercolour, low-poly, game feel, characters): the bundled canvas library under `scripts/hand-drawn/` (`npm install` there once for `@napi-rs/canvas`), its references under `references/motion/hand-drawn/` (start at `workflow.md`, `motion.md`, `traps.md`), its `templates/film-template.mjs` as the starting point. Original characters only.
- **Look before the full render.** `render.mjs beats` (one frame per beat), `contact`, `strip --t <time>` around every fast action, `phone`; score, fix, repeat ≥ 3 rounds. Only then `render.mjs full --fps 60 --sub 4 --audio out/mix.wav`, then `scripts/motion/checks.sh contact|strip|loop|probe` on the encoded master. A full render is an Authorization PAUSE under a non-interactive driver.
- **Formats.** Write scenes against a layout function so 9:16, 1:1 and 16:9 come from one timeline; reflow, never crop.

## Lane: page

The explainer page is 3–8 `seek(t)` figures inside a reading column, each with play / pause and a scrubber, the whole page theme-aware and phone-safe. `references/motion/explainer-page.md` has the mechanics; `assets/motion/explainer-template.html` is a complete worked example to copy mechanics from, never content. Write every caption first (a caption that cannot add a dimension means the figure has no point), draw rest frames, then animate, then `node scripts/motion/verify-page.mjs page.html` until it reports no errors and no horizontal scroll at phone width.

## Red lines

Scan these by the 🛑 marker. Each restates a rule above; breaking one means the output is compromised.

| 🛑 Anti-pattern | Why it fails | Correct approach |
|---|---|---|
| 🛑 Looking outside the skill for content, tokens, or another skill | breaks the self-contained contract; the result depends on something the user did not supply | use what the user gave and what is bundled; ask for what is missing |
| 🛑 Inventing data, names, dates, or UI to fill a slot | the viewer cannot tell invented from real; the artifact becomes a liar | keep the identifier, ask, or leave the slot visibly empty |
| 🛑 Writing files before the plan message | the user's one cheap chance to redirect is gone | one plan message, then build (Input PAUSE) |
| 🛑 Accent on more than two elements; a second hue; shadows; rounded-2xl; dark + neon glow | the signals that mark a generated diagram | one accent, borders not shadows, radius ≤ 8, the vendored style guide |
| 🛑 Diagonal connectors, labels on the stroke, overlapping paths, transit behind a box | automatic fail of the six connector rules | orthogonal elbows, masked labels with a gap, reroute or hop over the single crossing |
| 🛑 A map delivered after a non-zero `finalize` | the receipt is the evidence; without it there is none | repair and rerun; deliver the last passing artifact or report the gate |
| 🛑 `Math.random`, timers, or CSS transitions in a `seek(t)` film | frames depend on history; renders drift; parallel workers disagree | seeded noise, closed-form springs, `hash` check |
| 🛑 Full render before the contact sheet scores 8+ | an hour of rendering to find a dead beat at 4 s | beats → contact → strip → fix, three rounds, then full |
| 🛑 Centered title on a gradient, everything fading in, corner labels, frame borders | the default look everyone recognises | a reference and a state list; the anti-slop rows of the scorecard |
| 🛑 A caption that restates the title | adds nothing; reads as filler | a trade-off, a next step, or a dimension the figure does not show |
| 🛑 Claiming a visual check that did not run | the report lies about the evidence | name the command that ran and what it showed; say when a look was impossible |

## Completion report

```
✅ 已完成：.claude/draw/{slug}/{artifact}
Lane：{diagram | map | motion | page}　型別／結構：{type or film structure}　尺寸：{preset or format}
檢查：{command} → {result}（{captures or receipt path}）
評分：{hook}/{readability}/{motion}/{variety}/{composition}/{accuracy}/{sound}（{N} 輪，review_log.md）
砍掉的：{what the budget cut, or 無}
下一步可以更好：{one line}
```

Add the lines the lane needs: a fidelity ledger for an import; the finalize summary for a map; sibling formats for a film; 「此處採預設」 annotations under a non-interactive driver.

## Not for

- Styling, building or refining the UI of the user's own application → `/ui`.
- Fetching a page into Markdown → `/read`; digesting sources into a learning note → `/learn`.
- A dashboard over live numbers, or a chart whose point is the data pipeline rather than the picture.
- Editing a video someone shot, lip-sync, talking heads: nothing here renders pixels it did not draw.

## Attribution

Bundled third-party material and its licenses are listed in `NOTICE.md`; keep that file with the skill.
