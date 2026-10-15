# Review — how to look at your own frames

Technique reference for looking: key stills in Phase 3, dailies in Phase 4, the export in Phase 5. The scorecard and the loop shape (render → look → score → fix the worst three → repeat, at least three rounds, and on until every gated row ≥ 8 — no round cap, every round recorded) are in `../critique-loop.md`; this file is how to look at motion and how to write the notes.

You cannot see motion by reading code. Every claim about the film is checked on rendered frames; the first render is a draft, and two to four rounds of notes is normal.

## Read the sheet like a first-time viewer — the six looks

Render a contact sheet of every shot's first, middle and last frame; a strip of every fast action and transition (12 consecutive frames); a crop of every face or contact that carries the story. Then read the sheet like a first-time viewer: at each frame, where are they looking, and do they understand it yet? Count the frames each read gets; a read that flashes by in a few frames, or shares its frames with another, will be missed.

| Look | Command | Shows |
|---|---|---|
| one frame per beat | `render.mjs beats` | dead beats, a beat with nothing happening |
| contact sheet | `render.mjs contact` (2 fps, 6 across); or from frames: `ffmpeg -framerate 24 -i out/frames/%04d.png -vf "select='not(mod(n\,12))',scale=400:-1,tile=4x3" -frames:v 1 out/<slug>.contact.png` | composition, hierarchy, two things moving at once |
| strip | `render.mjs strip --t <time> --n 12` | jumps, restarts, overlap during a swap, a carry lost mid-seam |
| phone | `render.mjs phone` (360 px tiles) | type too small, a hold too short; the thumbnail test — is the 10 % still found (`composition.md`) |
| keys | `render.mjs stills --at <key times>` | a key no longer settled at its time |
| animatic | `render.mjs animatic` (24 fps, no blur, half size) | pacing: does each read get its time |

## Look at one frame by URL

While iterating, make any instant openable on its own: a page that handles `?t=` calls `seek(t)` once on load and after `document.fonts.ready`, and starts no loop. Then `<slug>.film.html?t=2.5` is the exact frame at 2.5 s, and it can be screenshotted and read. A generic version for any page with a render hook:

```html
<script>
// Paste right before </body>. Open <slug>.film.html?t=2.5 to see the exact frame at 2.5 s.
(function () {
  var q = new URLSearchParams(location.search);
  if (!q.has('t')) return;
  var t = parseFloat(q.get('t')) || 0;
  function freeze() {
    if (typeof window.seek === 'function') window.seek(t); else if (typeof window.renderAt === 'function') window.renderAt(t);
    document.getAnimations().forEach(function (a) { a.pause(); a.currentTime = t * 1000; });
  }
  freeze();
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(freeze);
  window.addEventListener('load', freeze);
})();
</script>
```

While iterating, also show a frame counter and a playhead, and a key to pause; pin on-screen labels to the frames their events should happen on, so a move that runs late shows up as a label lighting before its move. Remove all of them before the final render.

## Two views borrowed from animators

Draw them as PNGs and read them.

### Onion skin

A run of consecutive frames stacked at low opacity. Even spacing means robotic motion; spacing that tightens near the keys means the easing works.

### Speed graph

The hero's position and scale per frame, plotted. Straight lines are linear motion; sharp corners are dead starts and stops.

## Write notes with frame numbers, in camera words

A note that names a frame gets exactly that change; a note that names a feeling gets a random one. Vague notes ("make it better") get random changes; camera words get exactly the change (`camera.md` § Director notes in camera words: "dolly in on the button, not zoom", "slow every zoom to 0.7×", "hard cut here", "rack focus from the chart to the CTA", "freeze on the result, push in, ring it", "L-cut the click sound under the next shot"). Write each note as one line in `docs/review_log.md` and one edit in the scene list, with the frame, the problem and the exact change ("the punch at frame 84 peaks late, move it 2 frames earlier").

### Follow-up prompts that work

Pick one or two per round; all seven at once turns a fix into a rewrite.

```
Render stills at frames 0, 24, 48, 72 and 96. Describe each in one sentence as a viewer would. Does that match the shot list? Fix what does not.
Make a contact sheet of every 12th frame. Mark every frame where two things move at once, then fix the hierarchy.
Onion-skin frames 24 to 47 at 25 % opacity. Spacing should tighten near the keys. Adjust the easing until it does.
Plot the hero's x position and scale per frame as a PNG chart. Show where the motion is linear or stops dead, then fix it with our tokens.
Review this like a senior motion designer: 10 notes ordered by impact, each with a frame number and the exact code change. Apply the top 5.
It is too busy. Remove 30 % of the motion and keep only the moves that guide the eye.
The ending is abrupt. Add a 36-frame hold with a 2 % push, then let it settle on a spring at damping ratio 0.8.
```

"Render X, open frames 0, 24 and 48, and say what you see before changing anything" is the habit under all of them.

### Translate a feeling into numbers before acting on it

| The note says | Do |
|---|---|
| make it pop | scale 1.0 → 1.08 → 1.0 over 6 frames, peak on the beat |
| make it feel premium | ease-out-quint on entrances, springs at damping ratio 0.8, no overshoot on text |
| it drags | shorten each hold by 12 frames (one beat at 120 BPM and 24 fps), so every cut stays on the grid |
| it feels busy | one hero move at a time; everything else starts 150 ms later at 60 % of its travel |
| it looks like AI | list the defaults it used by name, ban each one, render again |

### Which fix first when a round scores low

The order is in `../critique-loop.md` § Which fix first (the focus cannot be found → cut or dim what competes; the frame cannot be read as a space → back to the big shapes and the key; the look went bland → the style guide's Keep list). Fix at the right phase: a bad frame inside an interval is a Shoot fix, a bad key a Keys fix, a bad story a Draft fix.

### When a fix does not hold

Render the frames on either side of the problem (83 and 85 around 84), put them side by side, list every difference, find the one line of code that causes it, fix only that line, render both again. Spotting what changed between two images is what the model's vision is best at.

## Audit the numbers, not just the look

Read the live scene on every frame and compare it with the brief's numbers: a label lights on its printed frame, a foot touches its pad on its landing frame, a blink happens on frame 432, a key is settled at its time. One loop ran 71 such checks; the first run failed 6, all fixed before the final render. The labels pinned to frames double as this test.

## Review the export

Review the encoded file, not the page (Phase 5). Each look below is part of one review; repeat it until the master passes.

- A contact sheet at one-second intervals **and around every scene boundary** (`checks.sh contact|strip` on the master); read it for readable text at phone size, spacing, cursor continuity, scene coverage, and the **final three-second hold**.
- Probe the export: duration, dimensions, frame rate, and that an audio stream exists (`checks.sh probe`).
- Watch it once muted and once with sound: does the story still make sense? Can the closing line be read without pausing?
- A loop is checked separately at its seam: matching positions, movement and audio take more than restarting the timeline (`checks.sh loop`; `finishing.md` § Loops).
- Check the decoded audio (`beat-grid.md` § Sync and measurement); when the mix cannot be heard, list it in the completion report's 「待人工確認」 (the mix was measured but not heard).
- Fix the three most important defects, then repeat until the master passes; there is no pass cap. Save every pass's timestamped findings in `docs/review_log.md`. **Never mark a check that could not run as passed**; return the files and the remaining issues.

## Fixes for the failures everyone hits

| Symptom | Fix |
|---|---|
| flicker or jitter | every value a pure function of `t`; a seeded generator instead of `Math.random`; no timers or CSS transitions |
| wrong or fallback font | load it with `display=block` and wait for `document.fonts.ready` before the first frame |
| hiccup at the loop seam | render frames 0 to N − 1; drive the loop from `phase = frame / N` with whole cycles |
| audio drifts off the beat | compute each beat as `n × 60 / BPM` and round per beat; never add a rounded frame count |
| jank or dropped frames (live preview) | animate only transform and opacity; no width, height, top or left |
| banding in the GIF | no gradients; flat colours, or dither the palette |
| blurry or shimmering text | snap resting text to whole pixels; render at 2× and scale down; no `will-change` on anything the camera scales |
| text moves before it can be read | hold every text state 0.3 s per word + 0.5 s before it moves |
| everything moves at once | one hero move at a time; others start 150 ms later at 60 % of its travel |
| an element snaps back before heading to a new target | a restarted spring; use `track()` (one spring per change) |
| two labels overlap during a swap | `swapAlpha` + `swapBlur` (`springs.md`) |
| a fix does not hold | render the frames either side, list every difference, fix the one line |

## Keep receipts

Count the creative follow-ups (notes that change how it looks or moves; technical fixes such as a capture hook or font loading are logged apart) and keep every prompt with the piece in `docs/review_log.md`. Honest published counts are in `prompts.md` § The honest numbers. **Fixes become the contract:** when a fix works, write its rule into the film's `docs/style_guide.md`, or into the render contract (`pipeline.md`) if it is general.
