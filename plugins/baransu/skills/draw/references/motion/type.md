# Type on screen — kinetic typography that reads at 360 px

Technique reference for type: Phase 1 chooses the faces (`1-design.md` § 5), Phase 3 sets the hook and every caption key at final size (`3-keys.md`), Phase 4 animates it.

Most reels open with words. The hook is five words of huge type, the metric is one number, captions either go huge (a lyric, a punchline) or sit like subtitles. Type is also where AI-made video gives itself away: a centred title fading in over a gradient, body text in a corner, three typefaces. These rules keep type a design decision instead of a default.

## Faces — one display face, one UI face

- **One display face, one UI face**, and the accent colour. The display face carries hooks and payoffs (900 weight, tight tracking); the UI face carries everything that pretends to be an interface. A third face needs a reason written in the storyboard.
- Load both through `document.fonts.ready` before the first frame; the renderer waits for it, the preview loop does not.
- CJK: 1.35–1.5 line-height, no fake italics, and the 360 px floor applies per glyph — a 48 px Latin caption is a 56 px Chinese one.

## The hook

- ≤ 5 words, at least a third of the frame height, within the first 2 s.
- Words land on their own springs, staggered 0.04–0.08 s (`Motion.words(t, text, t0, gap, 'heavy')`): scale from 0.92, rise 12–20 px, alpha on the first 0.1 s. Type is heavy — tiny overshoot, never bounce.
- Snap, then hold: the landing takes ~0.3 s; the hold is where the reader reads. A hook that keeps moving is unread.
- Exit by a decision, not a fade: a wipe that the next scene rides in on, a whip, the words collapsing into the UI they describe.

## Captions and lyrics

- Huge when the words *are* the event (a lyric, a line of narration that lands the joke); subtitle-sized at the lower third when they only accompany. Decide per line in the storyboard; mixing within a line is noise.
- One caption at a time, on screen for as long as it takes to read twice, and never less than 0.3 s per word + 0.5 s (a two-word title: 1.1 s). Text never moves while it is being read; a slow 2 % push on the frame keeps a hold alive instead.
- Text keeps 4.5 : 1 contrast on every frame, including over moving backgrounds (WCAG); never more than 3 flashes per second.
- Resting text snaps to whole pixels; render at 2× and scale down if it shimmers.
- Nothing in corners, and nothing in the format's safe margins (`L.safe`: the platform's caption bar and controls). Text sits in the composition or on the subject; corner text is a watermark.

## Numbers on screen

- One number that proves it works: `Motion.countUp(t, from, to, t0)` decelerates into the real value; format with `toLocaleString`, never a float.
- Tabular figures (`font-variant-numeric: tabular-nums` on DOM, a monospace numeral face on canvas) so the width does not jitter while counting.

## Type inside UI

- Labels inside a morphing container use `swapAlpha` (in late, out early) with `swapBlur` for the swap behind the morph; two labels never overlap.
- Typed text uses `Motion.typed(t, text, t0, cps, seed)`: seeded jitter per character, caret solid while typing.
- The UI face at UI sizes (14–18 px at 1× for a 1080-wide frame scaled by the camera, not 11 px scaled up).

## Type checks the frames will show

- `render.mjs phone` — every word still legible at 360 px wide; if not, the type is small or the hold is short.
- `render.mjs strip --t <hook start>` — the words land one at a time, none snap back toward a previous start.
- Count the faces in `contact.png`. Two plus the accent, or write down why.
