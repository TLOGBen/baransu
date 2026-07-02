## Contents

- Color jobs — the five roles a chart color can play
- Anti-patterns — Claude's default chart-color mistakes
- Computable checks — pointer to `color_distance.py`

# Chart Color Reasoning — Claude Default Deviations

These entries correct Claude's observed chart-color defaults — the habits that
produce a chart that looks fine to the author but fails a colorblind reader, a
grayscale printout, or basic honesty about what the axes mean. Each entry
names the default pattern to avoid, spells out the causal mechanism that
makes it fail (not just "this is wrong"), and shows a concrete before/after
correction. This file is read only when `/book`'s Render stage generates a
`statistical`-type section under a declared chart-capability (SKILL.md Stage
3 §4's "Statistical-type color-capability degrade" note) — it does not affect
any of the other 13 diagram types. It absorbs the reasoning behind dataviz's
`color-formula.md` and `validate_palette.py`, not a copy of dataviz's own
prose or its full seven-step methodology (goal.md's out-of-scope note: 不整套
內化 dataviz 七步方法論 — only the color layer is absorbed here).

---

## Color jobs — the five roles a chart color can play

Source: adapted from dataviz's `color-formula.md` reasoning (absorbed, not
reproduced verbatim).

Claude's default here is reaching for whichever palette *looks* good, rather
than first asking what job the color is doing. A chart's color always encodes
one of five distinct information jobs; picking the wrong palette shape for
that job is a readability failure independent of which hex values get chosen.

---

**1. Categorical — distinct identities, no order**

Claude defaults to a lightness ramp (progressively darker/lighter shades of
one hue) even when the categories it's coloring (product lines, regions,
independent series) carry no inherent order.

| Before (default) | After (correction) |
|---|---|
| Product A / B / C colored as light-blue → mid-blue → dark-blue | Product A / B / C colored as three hue-distinct colors (e.g. the `--chart-cat-1/2/3` tokens) — hue carries the distinction, not lightness |

*Why it fails*: because a lightness ramp reads as "darker = more" to a viewer
regardless of the author's intent, unordered categories painted on a ramp
invent a false rank the underlying data does not have — the reader walks away
believing Product C outranks Product A.

---

**2. Ordinal — ordered categories need a single-hue ramp, not categorical hues**

Claude defaults to the mirror-image mistake for ordered data: reaching for a
discrete categorical palette (one hue per stage) to color low/medium/high or
funnel stages, instead of a single hue stepping through monotone lightness.

| Before (default) | After (correction) |
|---|---|
| Funnel stages Awareness → Interest → Purchase painted in four unrelated hues (blue, green, orange, purple) | Funnel stages painted in one hue, lightness stepping monotonically — lightest at Awareness, darkest at Purchase |

*Why it fails*: because unrelated hues carry no ordering signal on their own,
the reader has to memorize an arbitrary hue-to-rank mapping instead of just
reading the lightness gradient — and because each stage still looks
"distinct" under a categorical palette, this is the color-job mistake most
likely to pass a casual glance while silently discarding the one property
(order) that ordinal data is defined by.

---

**3. Sequential — continuous quantity needs a single-hue ramp**

Claude defaults to treating a continuous quantity (heatmap intensity,
density, magnitude) as an opportunity for a vivid multi-hue gradient rather
than a single-hue ramp. (The worst version of this mistake — a rainbow/jet
gradient — gets its own anti-pattern entry below; this entry covers the
general job-mismatch even for a modest two- or three-hue sequential ramp.)

| Before (default) | After (correction) |
|---|---|
| A density heatmap running teal → yellow (two unrelated hues) | A density heatmap running one hue, light → dark (e.g. `--accent` at increasing opacity or lightness) |

*Why it fails*: because a hue change reads as a category change to the eye,
any multi-hue sequential ramp — even a modest two-hue one — plants a
perceptual boundary inside data that has none; the reader sees "the yellow
region" as a distinct group rather than a point on a continuum.

---

**4. Diverging — two-hue ramp meeting at a neutral midpoint**

Claude defaults to a single hue (or a categorical palette) for values that
diverge around a meaningful midpoint — profit/loss, above/below target —
leaving the +/- sign as the only thing that distinguishes direction.

| Before (default) | After (correction) |
|---|---|
| Profit and loss bars both painted the same blue; only the sign label tells them apart | Profit bars in one hue (e.g. accent blue), loss bars in a second hue (e.g. semantic red), the two ramps meeting at a neutral paper-colored zero line |

*Why it fails*: because a single hue forces the reader to parse a small +/-
label to find direction instead of perceiving it at a glance, a diverging
quantity's meaningful pivot (zero, target, breakeven) needs a visual pivot
too — without one, the chart's central fact (which side of the line each
value falls on) is the hardest thing in it to see.

---

**5. Status — fixed semantic colors, never part of the categorical rotation**

Claude defaults to letting a chart's general categorical palette assign
whichever hue lands next in rotation to a success/warning/error state,
instead of reserving fixed semantic tokens for status.

| Before (default) | After (correction) |
|---|---|
| The "Error" state happens to get the third categorical hue (a green) because that's the next unused color in the palette's rotation | The "Error" state always renders in the fixed semantic red/`--danger` token, independent of rotation position |

*Why it fails*: because readers bring color associations (red = bad, green =
good) from every other chart they've ever read, a status color assigned by
rotation instead of semantics can mean "error" in one chart and "healthy" in
the next — defeating the one piece of transferable intuition a reader
actually has.

---

## Anti-patterns — Claude's default chart-color mistakes

Source: dataviz's named failure modes (task-book.md's own explicit examples),
grounded with the causal "why" from dataviz's `color-formula.md` /
`validate_palette.py` reasoning.

These three are compositional habits — mistakes in what the chart is
structured to show, not just which hex values were picked. Distinguishing
them from the five color-job entries above: a color-job mismatch picks the
wrong palette *shape* for a correctly-structured chart; an anti-pattern below
structures the chart itself in a way no palette can fix.

---

**1. 雙軸圖表 — Dual-axis charts sharing one plot area**

Claude defaults to overlaying two independently-scaled y-axes (e.g. revenue
on the left, headcount on the right) onto one shared plot area whenever two
series have different units or magnitudes, because it keeps both series in
"one chart."

| Before (default) | After (correction) |
|---|---|
| Revenue (left axis, $0–500K) and headcount (right axis, 0–50) drawn as two lines that cross mid-chart | Two stacked plots, each with its own honest single axis, aligned on a shared x-axis |

*Why it fails*: because the two scales are chosen independently of each other
(often tuned until the lines visually cross or track together), any crossing
point or apparent correlation on a dual-axis chart is an artifact of the axis
choice, not the data — the reader cannot even tell which series maps to
which axis without deliberately reading the legend, so the chart can be
tuned to imply a relationship that doesn't exist.

---

**2. 彩虹漸層 — Rainbow/jet gradient for sequential data**

Claude defaults to a multi-hue "rainbow" or "jet" colormap (blue → green →
yellow → orange → red) for continuous sequential data because it looks
vibrant and appears to "use more of the palette" than a single-hue ramp.

| Before (default) | After (correction) |
|---|---|
| A heatmap intensity scale running blue → green → yellow → orange → red | A single-hue ramp (e.g. `--accent` stepping light → dark) |

*Why it fails*: because a rainbow gradient is not perceptually uniform —
equal steps in hue do not read as equal steps in value — and passes through
several hue boundaries the eye reads as categorical breaks, it implies false
discontinuities inside data that is genuinely continuous; a reader sees "the
yellow band" as its own group instead of a point on a continuum. Verify any
generated sequential ramp with
`plugins/baransu/skills/_shared/scripts/color_distance.py` on the ramp's
sampled steps — the tool's CVD-separation check flags whether adjacent steps
remain distinguishable under color-vision-deficiency simulation, which a true
single-hue ramp should pass smoothly and a rainbow ramp routinely fails at
its hue-boundary crossings.

---

**3. 身份色僅靠顏色不給圖例 — Identity color with no legend**

Claude defaults to distinguishing 2+ categorical series by color alone,
without pairing each color to a legend entry or direct label — especially
when there are only 2 series and the distinction "feels obvious" from
context.

| Before (default) | After (correction) |
|---|---|
| Two lines, blue and orange, with no legend strip — the section text names them but the chart itself doesn't | Two lines, each paired with a legend-strip entry (§4.6) naming the series alongside its color swatch |

*Why it fails*: because color perception varies — colorblind readers,
grayscale printouts, low-contrast displays — a color-only encoding silently
excludes part of the audience; a series distinguishable only by hue isn't
actually resolvable to those readers at all, no matter how obvious the
difference looks to the author who chose it. Run
`plugins/baransu/skills/_shared/scripts/color_distance.py` on the palette's
hex values before finalizing: an "adequate" CVD-separation score confirms the
colors stay distinguishable under protan/deutan/tritan simulation, but it is
advisory only — it does not replace pairing each color with a legend entry or
direct label, which is the actual correction here.

---

## Computable checks — pointer to `color_distance.py`

dataviz's `validate_palette.py` runs six checks per palette: fixed hue order,
lightness band, chroma floor, CVD separation, contrast vs surface, and
ordinal-ramp step resolution. This file absorbs the reasoning behind those
checks into the entries above rather than reproducing the full six-check
suite (goal.md's out-of-scope note: 不整套內化 dataviz 七步方法論). The one
check with a working baransu implementation is CVD separation —
`plugins/baransu/skills/_shared/scripts/color_distance.py` (hex → linear
sRGB → Machado-Oliveira-Fernandes (2009) CVD simulation → CIELAB → CIE76 ΔE)
— already referenced above and wired into the statistical-type Render path
alongside this document (SKILL.md Stage 3 §4).
