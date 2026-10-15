# The critique loop — make the model look at its own frames

The single habit that separates the work people share from the work they post with "it's a bit mid": render, look, score, fix the worst three, repeat. It applies to every form and every approach; only the "look" tool and the approach rows change.

## Why it works

The model can read images. A rendered frame is evidence the code is not: text that overlaps during a swap, a dead beat where nothing happens, a node whose label spills out of its box, an accent painted on five things. None of that is visible in source. Reading the frame closes the gap between "the code says it moves" and "a viewer would see it move".

Several rounds are the normal route, not a sign that something went wrong. Public "one prompt" clips that held up under scrutiny were preceded by 100+ model calls and several hours; the honest ones said so.

## The loop

```
ledger-check ─▶ render stills ─▶ look (contact sheet / screenshots) ─▶ score 1–10 on the card
                      ▲                                                        │
                      └──────── fix the 3 worst problems ◀── list them with timestamps / element ids
```

### The order of a round

Each round runs in this order:

1. **The ledger passes so far.** `python3 "<skill>/scripts/ledger-check.py" "<project>/.claude/draw/<slug>" --upto critique-loop` exits 0 (§ The reference ledger); `--upto` leaves out the steps that come after the critique (the /ui page assembly, the final check), which the `ledger-check` step covers at delivery. A round is not scored on a failing ledger: look up the missing chapter, apply it, and rerun.
2. **The machine checks run.** Every machine-checked row of the approach (§ Approach rows) runs its command; a failing command is the first of the three problems.
3. **Look and score.** Open the captures and score the shared card and the approach rows.
4. **Fix the three worst**, at the phase that owns them, and log the round.

### Rounds until every gated row is 8 — no round cap

Run at least three rounds for anything that moves and for a component, and keep running rounds until every approach row and every applicable shared row is 8 or higher, or has stalled (§ A stalled row moves on). There is no round cap: the loop ends when the scores reach 8 or the remaining rows have stalled, never when a count of rounds or the clock runs out. Record every round in `docs/review_log.md` (§ Record it), and report the number of rounds in the completion report. Fix at the module level: split, drop, or regroup; never "fix" a crowded frame by scaling everything down. A row that cannot reach 8 for a reason outside the build (a real asset that was not supplied, an environment where the check cannot run) is named in the completion report under 未做到的 with that reason; it is never lowered to fit time.

### A stalled row moves on

A gated row that does not improve over two consecutive rounds (its score after round n + 2 is no higher than after round n, despite a fix aimed at it each round) has stalled. Write it under 未做到的 in the completion report with its last score and the reason the fixes did not move it (what was tried, what blocks it), mark it `stalled` in `docs/scorecard.md` and `docs/review_log.md`, and spend the next rounds on the rows that still move. A stalled row is never re-scored upward to close the loop, and it is never a reason to wait or to put a question to the user. Rows that are still rising keep their rounds.

Time is tracked, not traded: each round's start time goes into its `R<n>` heading. When a round runs past twice what you expected, send the user one progress line (the round, the rows still under 8, what the next fix is) and continue in the same turn.

### Which fix first

Which fix first, when a round scores low:

- the focus cannot be found → cut or dim what competes with it (equal brightness, equal detail); never enlarge the focus or add a second signal
- the frame cannot be read as a space → go back to the big shapes and the shot's still (`motion/2-draft.md`, `motion/3-keys.md`); detail comes last
- the look went bland after cleanup → check the `Keep:` list in `docs/style_guide.md`; hierarchy comes from value and position, not from greying the style away

## How to look, per form

Open the images and read them. A render that exits 0 proves nothing.

### Looking at a diagram

- **Tool.** `python3 scripts/diagram/self_check.py <file>` then a browser screenshot (`node scripts/motion/verify-page.mjs <file> --selector svg`).
- **What it gives.** The accessible-SVG contract, single-file safety, light + dark + phone captures.

### Looking at a map

- **Tool.** `node scripts/map/bin/archify.mjs finalize … --json`.
- **What it gives.** Validate → deliver → strict check → browser check receipt; `visual-check` for captures.

### Looking at motion

- **Tool.** `node scripts/motion/render.mjs beats` (one frame per beat), `contact` (2 fps), `strip --t <time>` (12 consecutive frames), `phone` (360 px), `hash` (determinism).
- **What it gives.** The shape of the whole film, pops and overlaps around fast actions, phone legibility, identical re-render.

### Looking at a component

- **Tool.** `node scripts/motion/verify-page.mjs <name>.html` and `node scripts/motion/perf-check.mjs <name>.html`.
- **What it gives.** The figure in light and dark, the file at phone width, console errors, horizontal-scroll flag; shader link time, long tasks, per-figure frame cost, drawing stopped offscreen.

### Looking at a mechanism figure

- **Tool.** `scripts/anatomy/scripts/capture.mjs` (desktop, 390 px phone, `--zoom` close-ups) and `scripts/anatomy/scripts/drive.mjs` (sequences, the apart pose, `--no-webgl`, `--reduced`) with `CHROME_PATH` exported from `node scripts/motion/doctor.mjs`; `scripts/anatomy/references/verify.md` has the commands.
- **What it gives.** 1× and 4× in both themes, every resting pose, pointer and keyboard sequences, the fallback.

## The reference ledger

The references are not read up front and no file is read whole. Each step of the flow names the topics it needs (`references/steps.json` holds, per form and approach, every step and its required topics; `references/INDEX.md` lists every topic and its chapter). At each step, before writing that step's files, the builder runs the step command:

```
python3 "<skill>/scripts/lookup.py" --step <step-id> --log "<project>/.claude/draw/<slug>" [--value key=value ...]
```

It prints every chapter the step names (a `{…}` topic filled from `--value`, aliases resolved) and appends to `docs/lookups.log` in the output folder one `step` line (UTC time, step id, the filled topic ids) and one line per topic. That log is the reference ledger. Any other chapter is looked up when a question comes up that it answers (`lookup.py <topic> --log …`), and it is logged the same way.

- A rule that the product does not follow is still looked up; the review-log round that names why it was not followed goes with it, and the reason goes under 未做到的 in the completion report.
- `python3 "<skill>/scripts/ledger-check.py" "<project>/.claude/draw/<slug>"` verifies the log against `references/steps.json`: every applicable step (from the brief's `Form:`, `Approach:` and `When:` lines, plus kit, WebGL, 3D and seek-overlay use detected in the figure's own files) has a `step` record, every topic a record lists was printed with it, and a step with a `{…}` template filled at least one topic from it. It proves the step commands ran, nothing more: file names and times are not read, and whether the printed chapters were applied is judged on the scorecard. It exits 0 only when every check passes; scoring starts after that.

## The shared scorecard

Score each item 1–10. Judge it the way a demanding director would, not the way its maker would. Rows about time and sound apply to anything that moves; a still scores them n/a and says so.

| Item | What 8+ looks like |
|---|---|
| Hook in the first 2 s | the single most striking image is already on screen; frame 0 is not empty |
| Readability at phone size | labels survive 360 px wide; nothing below the type floor; nothing the viewer must read sits in the format's safe margins (`--safe` on the sheet) |
| Continuity | the same type scale, palette, screen direction and motion feel in every scene; an element that leaves on the right does not re-enter on the right |
| Motion quality | springs settle, nothing slides linearly, no dead frames, no pops between consecutive frames |
| Variety | something new every 2–4 s; no two consecutive shots use the same technique |
| Composition | the frame reads at three levels, about 6 : 3 : 1 (`motion/composition.md`): a quiet base that fills most of it, a few supporting elements that lead to the focus, one focus that differs from its surroundings in *one* way (value, the accent, isolation, a clean edge) — not every way; the accent on ≤ 2 things; nothing in the corners by default |
| Brand / fact accuracy | real UI, real data, real names; nothing invented to fill a slot |
| Sound sync | hits land on measured peaks; a cut without a sound reads as a mistake |

## Approach rows — the 8-point gate

Each approach adds its own rows. **The 8-point gate applies to these rows**: delivery needs every approach row of every approach in the build at 8 or higher (a component × mechanism build carries both the component rows and the mechanism rows). A **machine** row names its command; the command must pass before the row is scored at all, and a failing command scores the row 0. A **judged** row is scored from the captures, with the capture or element id that shows it in `docs/review_log.md`.

### Mechanism rows (`scripts/anatomy/ANATOMY-SKILL.md`, `scripts/anatomy/references/craft.md`, `verify.md`)

| Row | What 8+ looks like | Checked by |
|---|---|---|
| One object | at a glance it reads as one real, well-made machine you can name; what moves and what that means fits in one sentence; not abstract plates, not one plain slab | judged |
| Isometric, one camera | every part projected through the one `fitProjection` camera (azimuth 45° by default, 35–60° for a long side, elevation 30° unless looking into something open); no part drawn in a second projection | judged |
| Four tones by facing | sides shaded in four tones by facing with lighter tops, from the kit's `extrude`; base `lo`, structure `mid`, subject `hi`; monochrome unless colour is the subject | judged |
| 0.6 px line weight | thin 0.6 px lines throughout, at 1× and at 4×; no heavier outline added by hand | judged (4× capture) |
| No words in the drawing | no labels, leader lines, balloons or dimension arrows inside the drawing; at most one tiny engraved label; `Fig n`, title, hint and live readout in the card's corners, legend and caption under the card | judged |
| 40+ parts, each with a job | the parts list (upstream workflow step 4 in `scripts/anatomy/ANATOMY-SKILL.md`, written to `docs/parts.md`) has at least 40 parts grouped as base, structure, mechanism, controls and subject; every part rests on another and does something | judged against the parts list |
| One lit part | exactly one `lit` accent, on the part the reader should watch | judged |
| Lines resolve | every line ends on a face, another line or a terminal dot; `node scripts/anatomy/scripts/lines.mjs <name>.html --out shots/lines.png` prints `line ends: 0` on both themes and in every resting pose; with pipes, cables or round parts, `node build.mjs --audit` ends `audit passed` | machine |
| 4× detail | at 4×, across the whole drawing at every size (Figure, Hero and Epic alike; `references/mechanism/mechanism.md` overrides the upstream Figure scope), every region still has something true to find; junction close-ups in both themes read | judged (`capture.mjs --zoom`) |
| Direct manipulation | the figure answers the pointer and the keyboard (drag, press, hold a key), the focus ring shows, `aria-valuetext` reads the state in words; an idle tour runs when nobody touches it and pauses on interaction | machine + judged (`drive.mjs` sequences with `move` / `click` / `key` actions change the readout) |
| Numbers from one model | the readout, the motion, the screen-reader text and the caption all read from one model; the readout's words and numbers come from the same instant | judged |
| Performance | `node scripts/motion/perf-check.mjs <name>.html` prints `RESULT: PASS` (no FAIL row): shader link, long tasks, per-figure frame cost, drawing stopped offscreen | machine |

### Diagram rows (`references/diagram/taste-gate.md`)

| Row | What 8+ looks like | Checked by |
|---|---|---|
| Accessible, single-file | `python3 scripts/diagram/self_check.py <file>` passes | machine |
| Six connector rules | orthogonal elbows, masked labels with a gap, no overlaps, distinct attach points, no transit behind a box, no mask under a later node; `python3 scripts/diagram/repo/verify-geometry.py <file>` passes, and the type's own `scripts/diagram/repo/verify-*.py` when its reference names one | machine |
| Remove test | no node, arrow or label can be removed or merged without the reader losing something | judged |
| Signal test | the accent on ≤ 2 elements; at ~320 px the focal nodes and the main path read first; the legend covers every type used and nothing extra | judged (`verify-page.mjs --selector svg` phone capture) |
| Type fit | the semantic pattern (when behaviour matters) and the visual type match the point; the type reference's own rules hold | judged |
| Typography and skin | the style guide's families and ramp, the 4 px grid, no universal anti-pattern from the taste gate | judged |

### Motion and camera rows (`references/motion/1-design.md` … `5-post.md`, `camera.md`, `composition.md`)

| Row | What 8+ looks like | Checked by |
|---|---|---|
| Phase gates | every phase's `## Gate checklist` passed before the next phase started, each signed in `docs/review_log.md` | judged (review log) |
| Keys approved as stills | bookends and every key rendered (`render.mjs stills`) and scored as stills before any in-between existed; `KEYS` matches `docs/keys.md` | judged (review log rounds precede the shoot) |
| Named camera moves | every move in `docs/camera_plan.md` is one of the named moves in `camera.md`, with duration, curve and a `why:`; parallax tells the viewer what moved; one camera language per film | judged (strip around each move) |
| 6 : 3 : 1 per shot | every key and every contact-sheet tile reads as one quiet 60 %, one leading 30 %, one 10 % focus at thumbnail size (`composition.md` § The check) | judged |
| Determinism | `node scripts/motion/render.mjs hash --html <slug>.film.html --t <t>` prints `DETERMINISTIC` | machine |
| Every format | a contact sheet per delivered format (`contact --all --safe`), reflowed rather than cropped | machine + judged |

### Component rows (`references/motion/component.md`)

| Row | What 8+ looks like | Checked by |
|---|---|---|
| Caption adds a dimension | the caption or readout gives a trade-off, a next step or what the figure does not show; none restates the title | judged |
| Rest frame carries the point | the figure's `data-rest` frame alone makes its point; reduced motion shows it | judged (`verify-page.mjs` captures) |
| Component contract | no console or page errors, no horizontal scroll at phone width, light and dark both read: `node scripts/motion/verify-page.mjs <name>.html` exits 0 | machine |
| Performance | `node scripts/motion/perf-check.mjs <name>.html` prints `RESULT: PASS` (no FAIL row) | machine |

### Map rows (`references/map/delivery-contract.md`)

| Row | What 8+ looks like | Checked by |
|---|---|---|
| Finalize receipt | `node scripts/map/bin/archify.mjs finalize … --json` exits 0 with the browser check run, not skipped | machine |
| Composition | led by the main user journey; boundaries express real isolation; labels carry meaning | judged (`visual-check` captures) |

### Free creative rows (`references/motion/1-design.md`, `2-draft.md`)

| Row | What 8+ looks like | Checked by |
|---|---|---|
| Direction funnel | wide → 3 → 1 ran, with a style frame for each of the three, and the chosen one is the one built | judged (`docs/direction.md`) |
| Numbers, not adjectives | the style guide states its look in numbers, the ban list holds in every frame, the `Keep:` list survives cleanup | judged |

## Hunt specifically for

- text overlapping during a swap (content entered before the morph started, or left after the next one began)
- anything sliding instead of easing; a value that restarts its spring instead of summing one per change
- corner labels, frame borders, a centered title on a gradient, everything fading in
- blurry scaled text (`will-change` on something the camera scales)
- a dead beat with nothing happening; a stutter at the loop seam (last frame ≠ first frame, cursor included)
- a legend floating inside the diagram, a diagonal connector, a label touching its stroke
- a second accent colour; a cold grey where the palette is warm
- several things equally bright or equally detailed; a texture or grid that runs edge to edge at the subject's density
- background motion louder than the shot's event; a background that is dead instead of quiet (life is ±2 %, never at the focus's brightness)
- after every camera move or transition on the strip, the eye is not yet on the next read
- a shot whose `why:` in the storyboard is blank or restates the previous shot's
- the last frame alone would not work as the poster (`render.mjs still --t <end>`); a logo on black is a weak close
- the mix without the picture (`checks.sh audio`): a cut or click with no peak on the waveform, an ending that does not resolve, a bed that is a flat band
- a mechanism line that stops in the air, a bare face or empty corner at 4×, a second lit part, a word floating inside the drawing

## Notes like a director

The fix list reads better as director's notes than as bug reports — each is one timestamp, one verb, one target:

- "hard cut here, the fade is a slideshow" · "slow every zoom to 0.7×" · "push in on the button, the viewer is looking there"
- "the wipe fights the motion — flip it" · "carry the accent across, drop the black"
- "hold two more beats before the cut; the read isn't landing" · "the cursor arrives before the beat — move the click to 4.50"
- "type is under the 360 px floor on frame 12" · "two faces plus the accent; the third one goes"

## Record it

Keep `docs/review_log.md` in the output folder: one section per round headed `R<n>` with its start time, every round recorded (there is no round cap), the ledger-check result, any row marked `stalled` with its last score and reason, the machine checks that ran and their output, the shared and approach scores, the three problems with timestamps or element ids and the evidence (which tile or strip frame shows it), what changed. The user reads the final scores in the completion report; the log is the audit trail that proves the loop ran. A resumed session reads it first and continues from the last logged round; a missing artifact from the film folder (`motion/pipeline.md`) is named before any new work.
