---
name: draw
description: "Draws an idea, system, dataset or story as a self-contained piece: a static diagram, an interactive architecture map, a motion video, or an interactive animated figure. Trigger On '/draw', '畫一下', '圖解', '架構圖', '做成動畫', 'visualize'. Not For: restyling an app's UI or laying out a whole page (/ui)."
argument-hint: "<what to draw | file | repo dir | pasted text> [--lane diagram|map|film|component] [--format 9:16|1:1|16:9] [--dark]"
user-invocable: true
---

# draw — put it on screen

Turn what the user hands you into a piece a person can open, scrub, explore or watch. This file is a **step guide and a table of contents**: run the steps in order, each after its step command, which prints the chapters the step needs; nothing is read up front, no file is read whole. /draw is the user's only entry point and delivers end to end without asking. User-facing output is Traditional Chinese (繁體中文).

**Paths** (absolute): `<skill>` this folder, `<project>` the user's project, `<out>` = `<project>/.claude/draw/<slug>`. Scripts run by absolute path from `<out>`; file names below are relative to `<out>`.

**The step command.** `Before: lookup.py --step <id>` in a row means:

```
python3 "<skill>/scripts/lookup.py" --step <id> --log "<out>" [--value key=value ...]
```

It prints every chapter the step names (`{…}` topics filled from `--value`, aliases resolved: `--value move=push-in`) and logs it to `docs/lookups.log`. A question mid-step gets `lookup.py <topic> --log "<out>"`. `references/steps.json` holds each step's do and done-when; `ledger-check.py` checks the log against it.

**Principles.**

- **Full quality.** Every applicable step and check runs to its done-when; time and cost never lower quality unless the user asked for something quick.
- **No mid-run questions.** Form, approach, size, direction and whether a page is needed come from the content; an explicit user choice wins. The one stop: a real asset or fact the brief names that the user did not supply.
- **Time-aware, never rushed.** Within the first hour, send the user a first version that opens in a browser (no waiting for a reply), then keep deepening it. A step running past twice what you expected gets one progress line — where it stands, what remains — and the build goes on: no wait, no question. A critique row with no gain over two consecutive rounds goes under 未做到的 with its last score and reason; move on.
- **Examples are mechanics, not looks.** Templates and examples supply contracts (`seek(t)`, the scrubber, render hooks, `L`, the kit); look and interaction come from the references and the brief. Read an example's source for the API you need; anything built from one goes only into `<out>/scratch/`.
- **Chromium only through `launchChromium()`** (`scripts/motion/browser.mjs`) or a vendored seeded launcher; never an unseeded `chromium.launch()` or another browser tool: on Windows ten fresh profiles lock the user's account. The user's own Chrome through Claude in Chrome is fine.
- **Meaningful names.** `<slug>` is an ASCII slug of the title (an existing folder gets `-2`). Diagram `<slug>.html`; map `<slug>.map.html`; film `<slug>.film.html` → `out/<slug>.mp4` in the primary format the page declares (`--all` adds suffixed siblings `out/<slug>-1x1.mp4`, …), `out/<slug>.animatic.mp4`, `out/<slug>.contact.png`, `out/<slug>.poster.png`; component `<name>.html` named for its figure (the slug names the folder); a page from /ui `<page-name>.html`, distinct from component names. Never `index` or `final`.

## Outcome Contract

- **Outcome**: the requested pieces in `<out>/`, each through every applicable step, its lane check and a scored critique loop; a page, when needed, made by /ui around them in the same turn.
- **Done when**: the 開工狀態行 was sent and the build started in the same turn; a first version reached the user within the first hour; every applicable done-when holds; `ledger-check.py` exits 0; lane checks pass; `docs/scorecard.md` rows ≥ 8 or stalled and named under 未做到的 (≥ 3 rounds for film and component, no round cap); the completion report is written from the evidence.
- **Evidence**: `docs/lookups.log`, `ledger-check.py` output, lane-check output, `docs/review_log.md`, `docs/scorecard.md`, captures.
- **Output**: `<out>/` with pieces, sources, `docs/`, captures; Traditional Chinese messages.
- **Automation**: ultracode=neutral, loop=assisted（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）
  In the same non-interactive pass, read `references/loop-pauses.md` for this skill's own PAUSE classification.
- **Telemetry**: on invocation, append one selection record per `../_shared/selection-telemetry.md`.

## Self-contained by design

Inputs are what the user hands over (text, a file, a repository, pasted Mermaid / draw.io / Excalidraw, a URL fetched once) plus the bundle; no web search for content. The one skill it calls is /ui. **A missing tool is installed, not reported** (step 0); a new environment failure goes into `references/motion/pipeline.md` § Known environment failures.

## The flow (every request)

Steps 0–2 and 4 run for every request; step 3 runs the form's lane and the approach's steps. *(x)*: only for that form or approach, or when x is on the brief's `When:` line.

### 0. Preflight — the route with the fewest surprises

| Before | Do → Done |
|---|---|
| `lookup.py --step preflight` | `node "<skill>/scripts/motion/doctor.mjs" --install` until `READY`; export its `CHROME_PATH`; Python with `PYTHONUTF8=1 PYTHONIOENCODING=utf-8` → `docs/preflight.txt` ends `READY` |

### 1. Choose the form — what the user will do with it

| The user wants to… | Form |
|---|---|
| see structure, data or a comparison at a glance; or scrub something through it | **diagram** — inline SVG; optional reveal / step / loop or a seek overlay |
| explore a system: click a node, trace a path, prove it against a repo | **map** — the viewer runtime and a `finalize` receipt |
| watch it: a reel, demo, logo sting, kinetic type, explainer film, hand-drawn short, loop | **film** — `out/<slug>.mp4` and sibling formats |
| play with it: scrub, drag, press, see how it works | **component** — one interactive figure per file, no page frame |

Pick by the verb, the one the user will *use*. Delivery: **one piece**, **several pieces**, or **a page** when the request needs reading too (explain X, 說明頁, 教學): form component, `needs-page` on `When:`, the checked components handed to /ui in the same turn.

| Before | Do → Done |
|---|---|
| `lookup.py --step choose-form` | → `docs/brief.md` `Form:` (the value only), delivery, `Why:` (the reason) |

### 2. Choose the approach — how the picture explains

| Approach | When the point is |
|---|---|
| **Diagram system** | structure: who connects to whom, data flow, order of steps, a comparison, a dataset |
| **Mechanism** | behaviour: what the parts *do*, a rule enforced, a limit hit, the failure the idea prevents |
| **Free creative** | feeling, brand, story, rhythm |

A map always uses the diagram system; structure plus one hard-to-see behaviour is a diagram plus a mechanism.

| Before | Do → Done |
|---|---|
| `lookup.py --step choose-approach` | → `docs/brief.md` `Approach:`, `When:` (needs-page, seek-overlay, webgl, 3d, pipes, import, track, loop, …), values only — prose goes on `Why:` |
| `lookup.py --step mech-size` *(mechanism)* | Figure, Hero or Epic by part count and moving systems, not mechanism count; the name only → `Size:` |
| `lookup.py --step brief-and-status-line` | → `docs/brief.md`; send the 開工狀態行, keep building |
| `lookup.py --step progress-notes` | `date` per step, a progress line past twice a step's share → `docs/progress.md` |

- **Brief.** Facts (a date, a number, a name, a logo, a track) are never invented; picture choices are yours, decided and written down, never asked.
- **開工狀態行.** One line once form, approach and delivery are set, then build in the same turn without waiting; a 型別或結構 or 尺寸 a later step decides reads `待定` until a progress line fills it:

```
開工：形式 {diagram | map | film | component}／畫法 {diagram system | mechanism | free creative}／型別或結構 {visual type or film structure}／尺寸 {size preset, format, or Figure|Hero|Epic}／交付 {單件 | 多件 | 元件＋/ui 組頁}／理由 {one sentence}
```

### 3. Production — the lane's steps

Run § Lane for the form; add § Mechanism figures for a mechanism and § Lane: diagram for anything drawn with the diagram system (a component included). Free-creative steps sit in the film lane. A diagram, a component or a film starts as three seeds — independent first versions built in parallel by subagents up to the pick step — and only the blind judge's winner is refined (`references/seed-hunt.md`); a map runs none. One step is a milestone in time, not a place in the list:

| Before | Do → Done |
|---|---|
| `lookup.py --step seed-hunt` *(diagram, component, film)* | three seeds under `scratch/seed-{a,b,c}`, each from the brief alone, up to the pick step → `docs/seed_hunt.md` |
| `lookup.py --step seed-pick` *(diagram, component)* / `seed-pick-film` *(film)* | shuffled captures, a judge in a fresh context, the winner promoted and its log appended → `docs/seed_hunt.md`, `shots/seeds/` |
| `lookup.py --step first-version` | the moment the piece first opens and works, at the latest one hour in: send its path, keep deepening → `docs/first_version.md` |

### 4. Check and deliver

| Before | Do → Done |
|---|---|
| `lookup.py --step critique-loop --value form=<form> --value approach=<approach>` | rounds: machine checks, captures, shared + form + approach rows, the three worst fixed → `docs/scorecard.md`, `docs/review_log.md` |
| `lookup.py --step assemble-page` *(needs-page)* | `docs/ui_brief.md`; /ui (`baransu:ui`) via the Skill tool in the same turn; `verify-page.mjs`, `perf-check.mjs` on its page → `<page-name>.html` |
| `lookup.py --step ledger-check` | `python3 "<skill>/scripts/ledger-check.py" "<out>"` → exit 0 |
| `lookup.py --step deliver-report` | the completion report from the evidence |

## Lane: film

Phases, gates, rules (determinism, `Motion.cursor`, `Motion.camera`, `Motion.words`, springs, formats, sound, hand-drawn): `references/lanes/motion.md`.

| Before | Do → Done |
|---|---|
| `lookup.py --step design-film-brief` | → `docs/brief.md` FILM, REAL/assets, UNACCEPTABLE, DELIVERABLES |
| `lookup.py --step design-commission` *(commission)* | `Concept demo`; copy, colours, assets in a config |
| `lookup.py --step design-grab-assets` *(product-url)* | `grab.mjs <url>` → `manifest.json` |
| `lookup.py --step design-style-guide` *(film, free creative)* | → `docs/style_guide.md` |
| `lookup.py --step design-type-sound` | faces, accent, hook, BPM |
| `lookup.py --step design-measure-track` *(track)* | `beats.py` → `out/beats.json` |
| `lookup.py --step design-loop` *(loop)* | seam plan, `loopT` |
| `lookup.py --step design-hand-drawn` *(hand-drawn)* | `film.mjs`; three detail layers |
| `lookup.py --step design-film-folder` | → `<slug>.film.html`, `motion.js`, `FORMATS`, `L` |
| `lookup.py --step draft-direction-funnel` *(film, free creative)* | → `docs/direction.md` |
| `lookup.py --step draft-art-direction` *(film, free creative)* | → `docs/colour_script.md` |
| `lookup.py --step draft-long-split` *(long)* | `ANIMATION_GUIDE.md`, chapters |
| `lookup.py --step draft-storyboard` | → `docs/storyboard.md` |
| `lookup.py --step draft-camera-plan --value move=<each Move>` | a `Move:` line per shot → `docs/camera_plan.md` |
| `lookup.py --step draft-seams --value name=<each Seam>` | a `Seam:` line per seam → `docs/seams.md` |
| `lookup.py --step draft-pacing-timing` | → `docs/timing_sheet.md` |
| `lookup.py --step draft-key-list` | → `docs/keys.md` |
| `lookup.py --step draft-animatic` | → `out/<slug>.animatic.mp4` |
| `lookup.py --step keys-bookends` | → `out/keys/bookends.png` |
| `lookup.py --step keys-layout` | → `docs/key_layout.md` |
| `lookup.py --step seed-pick-film` | the seeds stop here; the winner goes on → `docs/seed_hunt.md` |
| `lookup.py --step keys-data-and-stills` | `KEYS` as data → `out/keys/contact.png` |
| `lookup.py --step shoot-intervals` | → `docs/shotlist.md` |
| `lookup.py --step shoot-animate` | → `docs/hash.txt` `DETERMINISTIC` |
| `lookup.py --step shoot-dailies` | ≥ 3 rounds → `out/<slug>.contact.png` |
| `lookup.py --step post-seams` | → `out/seams/` |
| `lookup.py --step post-sound` | `sfx.mjs` → `out/mix.wav` |
| `lookup.py --step post-render-master` | `render.mjs full --html <slug>.film.html` (`--all` adds siblings) → `out/<slug>.mp4` |
| `lookup.py --step post-finish` | → `out/<slug>.poster.png` |
| `lookup.py --step post-review-export` | `checks.sh` → `docs/export_review.md` |
| `lookup.py --step post-package` | README with the exact render line |

## Lane: component

Rules and the /ui hand-off: `references/lanes/component.md`. One interactive figure per `<name>.html`, theme-aware, phone-safe, no page frame or prose; several pieces run the steps per file. Drawn with the diagram system, it also runs § Lane: diagram's plan, layout, markup (into `<name>.html`), check and taste-gate. A mechanism component runs, in order: caption-states, perf-plan; `mech-catalog-and-example` … `mech-painters-order`; figure-card, `mech-frame-card`, rest-frame (the seeds stop here: `seed-pick`); `mech-make-live`, `mech-join-lane`, interaction; `mech-audit` … `mech-review-checklist`; component-check.

| Before | Do → Done |
|---|---|
| `lookup.py --step component-caption-states` | → `docs/figure_states.md` |
| `lookup.py --step component-perf-plan` | → `docs/perf_plan.md` |
| `lookup.py --step component-figure-card` | → `<name>.html` |
| `lookup.py --step component-rest-frame` | both themes, before animation → `shots/rest/` |
| `lookup.py --step component-interaction` | pointer and keyboard by default → `shots/states/` |
| `lookup.py --step component-check` | → `docs/verify-page.txt`, `docs/perf.txt` |

## Mechanism figures (any form)

A real, nameable machine whose moving parts behave the way the idea does — a queue as a marble run — for "explain how X works", 怎麼運作, 原理, 機制. No boxes, arrows or floating labels. `references/mechanism/mechanism.md` routes into the vendored `scripts/anatomy/ANATOMY-SKILL.md` and holds /draw's overrides. It lands as a **component** by default, as the shot in a **film**, or as a still in a **diagram**.

| Before | Do → Done |
|---|---|
| `lookup.py --step mech-catalog-and-example` | catalog rows near the idea; an example's source only for an API you need |
| `lookup.py --step mech-truth` | → `docs/truth.md`, `model.mjs` |
| `lookup.py --step mech-invent-object` | a new object → `docs/mapping.md` |
| `lookup.py --step mech-parts-list` | → `docs/parts.md` ≥ 40 |
| `lookup.py --step mech-plan-world` | → `view.mjs` |
| `lookup.py --step mech-route-pipes` *(pipes)* | pipes port to port |
| `lookup.py --step mech-build-geometry --value fn=<each kit builder>` | kit by path, never copied → `geometry.mjs` |
| `lookup.py --step mech-painters-order` | a settled order the audit checks → `build.mjs` |
| `lookup.py --step mech-3d` *(3d)* | turning groups |
| `lookup.py --step mech-frame-card` | four corners, legend, caption |
| `lookup.py --step mech-still` *(diagram)* | rest or apart pose |
| `lookup.py --step mech-make-live` *(component, film)* | `tourAt(t)` behind `seek(t)` → `live.js` |
| `lookup.py --step mech-join-lane --value form=<form>` *(component, film)* | `kitScript()` once in `<name>.html`, or `window.seek` |
| `lookup.py --step mech-audit` | → `docs/audit.txt` `audit passed` |
| `lookup.py --step mech-line-ends` | → `shots/lines.png`, `line ends: 0` |
| `lookup.py --step mech-closeups` | → `shots/zoom-*.png` |
| `lookup.py --step mech-3d-check` *(3d)* | → `docs/turn-check.txt` |
| `lookup.py --step mech-review-checklist` | → `docs/verify_checklist.md` |

## Shader layers (any form)

Fire, water, plasma, steam or lamp light in any piece is a shader layer, bound by the performance rules in `references/motion/component.md`.

| Before | Do → Done |
|---|---|
| `lookup.py --step webgl-layer` *(webgl)* | parallel compile, fallback → `gl.mjs` |
| `lookup.py --step webgl-check` *(webgl)* | → `shots/slow-*.png`, no pop |

## Lane: diagram

Rules: `references/lanes/diagram.md`.

| Before | Do → Done |
|---|---|
| `lookup.py --step diagram-import --value format=<format>` *(import)* | redraw, never convert → `docs/fidelity_ledger.md` |
| `lookup.py --step diagram-brand` *(brand)* | → `docs/skin.md` |
| `lookup.py --step diagram-semantic-pattern` *(behaviour-pattern)* | one pattern, before the type |
| `lookup.py --step diagram-plan` | → `docs/diagram_plan.md` |
| `lookup.py --step diagram-layout --value chosen=<type> --value size=<size>` | → `docs/layout.md` |
| `lookup.py --step diagram-markup` | → `<slug>.html` (a component: `<name>.html`) |
| `lookup.py --step diagram-cjk-labels` *(cjk-labels)* | no CJK label under 12 px |
| `lookup.py --step diagram-animate` *(animated-diagram)* | controller from `template-motion.html` |
| `lookup.py --step diagram-seek-overlay` *(seek-overlay)* | static twin via `seek_split.py` |
| `lookup.py --step diagram-check` | → `docs/self_check.txt` |
| `lookup.py --step diagram-taste-gate` | → `docs/taste_gate.md` |
| `lookup.py --step diagram-export` *(export)* | → `<slug>.svg` / `<slug>.png` |

## Lane: map

Rules: `references/lanes/map.md`.

| Before | Do → Done |
|---|---|
| `lookup.py --step map-author --value type=<diagram_type>` | → `candidate.json`, `meta.output` `<slug>.map.html` |
| `lookup.py --step map-repository` *(repository)* | pinned commit, sources on nodes |
| `lookup.py --step map-viewer` *(viewer-features)* | only the requested features |
| `lookup.py --step map-finalize` | → `docs/finalize.json` |
| `lookup.py --step map-perceptual-review` | → `<slug>.map.visual-check.*` |

## Table of contents

`lookup.py <id>` prints one chapter; several words search; `references/INDEX.md` lists every topic. Lanes: `references/lanes/`. Diagram, map: `references/diagram/`, `references/map/` (vendored). Motion: `references/motion/README.md`, phases `references/motion/1-design.md`, `references/motion/2-draft.md`, `references/motion/3-keys.md`, `references/motion/4-shoot.md`, `references/motion/5-post.md`, library (`camera.md`, `transitions.md`, `type.md`, `component.md`, …). Mechanism: `references/mechanism/mechanism.md`, `scripts/anatomy/ANATOMY-SKILL.md`. Toolchain: `scripts/motion/`, `assets/motion/`, `scripts/diagram/`, `scripts/map/`, `scripts/anatomy/`.

## Red lines

| 🛑 Never | Instead |
|---|---|
| 🛑 Inventing data, names, UI or assets | the user's input; stop on a missing real asset |
| 🛑 Asking to choose form, approach, size or a page; waiting after a status or progress line | decide, say it, build |
| 🛑 A page frame or paragraphs built by /draw | components, then /ui |
| 🛑 A step before its step command; a check or round cut to save time | `lookup.py --step`, then do |
| 🛑 Chromium started any way but a seeded launcher | `launchChromium()` |
| 🛑 A film with `Math.random`, timers or CSS transitions | seeded noise, springs, `hash` |
| 🛑 Claiming a check that did not run | the command and what it showed |

## Completion report

```
✅ 已完成：.claude/draw/{slug}/{file}（多件時逐一列出；組頁時先列頁面）
交付：{單件 | 多件 | 元件＋/ui 組頁}　形式：{…}　畫法：{…}　型別／結構：{…}　尺寸：{…}
用時：{total}；第一版於 {elapsed} 送出
檢查：{command} → {result}（{captures or receipt path}）
查詢紀錄：docs/lookups.log（{N} 個步驟）；ledger-check.py → {result}
評分：{each applicable row}（{N} 輪，docs/review_log.md）
未做到的：{rule not met, last score and why — a stalled row, a missing asset, an impossible environment — or 無}
提問：本輪未向使用者提問｜停下來等使用者提供：{the real asset or fact}
下一步可以更好：{one line}
```

Add per form: an import's fidelity ledger; a map's finalize summary; a film's siblings, poster, 「素材清單」, 「待人工確認」, 「重渲指令」 (the exact `render.mjs full …` line); a page's checks; 「此處採預設」 under a non-interactive driver.

## Not for

- The user's own app UI → `/ui`; Markdown of a page → `/read`; notes → `/learn`; live dashboards; editing footage.

## Attribution

Bundled third-party material and its licenses are listed in `NOTICE.md`; keep that file with the skill.
