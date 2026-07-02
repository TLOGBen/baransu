---
name: statistical
status: complete
example: inline
---

## Contents

- Layout conventions
- Anti-patterns
- Examples

# Statistical Chart

**Best for**: any section whose content carries an axis, a legend, and multiple data points — quarterly / trend line (single or multi-series), Candlestick (OHLC / per-day price), Waterfall (+/- contributions summing to a total), Donut (one series, sums to ~100%, items ≤ 6), Horizontal Bar (one series, sums to ~100%, items ≥ 7), Line (two or more time series), Bar (one time series dominated by large changes), Grouped Bar (multi-category snapshot at one time, 2+ series). This is the ONE unified reference §4.9's 7 statistical data-shape rows resolve to (see §4.10) — a section is never routed to a finer-grained per-shape reference; the shape hint from §4.9's Data shape column stays informative context only.

## Layout conventions

- **Axis**: a plot area has exactly one x-axis (bottom, category or time) and one y-axis (left, value), each a 1px hairline `--text-muted` baseline with tick marks landing on real category/time boundaries; a mono-font axis-unit label (e.g. `REVENUE (USD THOUSANDS), BY FISCAL QUARTER`) sits above the plot area so the reader never has to guess the unit — omitting it repeats timeline's "missing axis unit" anti-pattern.
- **Legend**: every series gets exactly one legend-strip entry (§4.6) pairing its stroke/fill color with its label; a chart with 2+ series and no legend is incomplete — color alone must never be the only way to tell series apart (this is the single most common statistical-chart error and is call out explicitly in Anti-patterns below).
- **Data points**: each data point is an explicit small filled circle (`r=4`, matches the `--ink`-scale marker size used by `type-timeline.md`'s events) landing exactly on its series' line/bar position — a line/curve alone (no discrete point markers) hides how many samples actually exist, which fails the "multiple data points" visual promise this type exists to keep.
- **Series color discipline (ties into the SKILL.md degrade branch — never bypasses it)**: this reference does not itself decide the color palette, and exactly-2-series content is **not** exempt from SKILL.md Stage 3 §4's undeclared-capability degrade check — per that check's L1/L2 boundary, 2 mutually-unrelated series sits squarely inside L2's "2 or more" threshold, not a silent third path. Before painting anything, Render must first run the declared/undeclared check: when **declared**, a 2-series section may use the two existing marker hues (`--accent` `#1B365D` for the primary/focal series, `--brand-light` `#2D5A8A` for a secondary series), as the inline example below does; when **undeclared**, a genuine 2-independent-identity section follows the L2 degrade (small-multiples / `table.cmp`) instead of this 2-hue overlay. A declared-capability multi-series render beyond 2 series additionally consumes the `--chart-cat-N` tokens baked by `/design` (out of scope for this reference — see SKILL.md's degrade paragraph). See `references/color-reasoning.md` for the fuller default-mistake/why/fix reasoning behind this discipline (SKILL.md's Declared branch is the authoritative read-step; this is a supplementary cross-reference).
- **Annotation callouts**: a callout card highlighting one data point (peak, plateau, inflection) reuses the exact node-width whitelist ({128, 144, 160}, §4.7) and type-tag (§4.5) primitives that node-based diagrams use for their boxes — the callout is a "node" borrowed from the flowchart/timeline vocabulary, not a new shape; a hairline drop-connector ties the card to its data point, following `type-timeline.md`'s milestone-card convention.
- **Honesty**: equal time/category intervals get equal axis spacing (never faked for aesthetics, same rule as `type-timeline.md`); bar/line values must be drawn to scale against the y-axis ticks, not eyeballed.

## Anti-patterns

- Distinguishing 3+ series by color alone, with no legend.
  - *Why fails*: colorblind readers (and grayscale print) cannot separate hues without a shape/pattern/label anchor; a legend-less multi-color chart silently excludes part of the audience — every series must resolve through the legend strip (§4.6), never through color memory alone.
- A dual/secondary y-axis sharing one plot area.
  - *Why fails*: two independently-scaled axes sharing one visual plane let the reader freely mis-attribute a crossing point as meaningful correlation when the two scales are unrelated; split into two stacked plots (each with its own honest axis) instead of overlaying scales.
- A rainbow gradient standing in for categorical identity.
  - *Why fails*: a continuous gradient visually implies an ordered/continuous relationship between categories; when categories are actually independent identities (not a ranked or sequential scale), a gradient invents a false ordering — use the discrete `--chart-cat-N` palette (when declared) or the L1/L2 degrade fallback (when undeclared), never a generated hue ramp across unrelated categories.
- Rendering a trend line with no discrete data-point markers.
  - *Why fails*: a bare curve implies continuous/interpolated data even when the underlying data is a handful of discrete samples (e.g. quarterly figures); omitting the `r=4` point markers overstates the sampling density and hides exactly how many real data points back the trend.

## Examples

Inline example below — a 2-series quarterly revenue trend line chart (Product A [focal, accent] vs Product B [secondary, link color], 6 quarters `23-Q1 → 24-Q2`). Complete `<defs>` with three chevron markers (all three referenced: `arrow-accent` closes Product A's trend line toward its final point, `arrow` and `arrow-link` each appear once in the legend strip), two paper-mask layers, a y-axis (4 ticks, `$0K–$150K`) + x-axis (6 quarter ticks) with a mono axis-unit label, 12 `<circle>` data-point markers (6 per series), 2 node-width-whitelist annotation callout cards ({128, 160}), 1 `data-role="focal"` callout (the Product A peak), a legend strip naming both series plus the callout meaning, and all `x/y/width/height/x1/y1/x2/y2/cx/cy` as multiples of 4.

```html
<figure class="diagram">
  <svg viewBox="0 0 1000 700" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Quarterly revenue trend, Product A vs Product B">
    <defs>
      <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">
        <circle cx="1" cy="1" r="0.9" fill="#E3E2DC"/>
      </pattern>
      <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto">
        <path d="M2 1 L8 5 L2 9" fill="none" stroke="#504e49"
              stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      </marker>
      <marker id="arrow-accent" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto">
        <path d="M2 1 L8 5 L2 9" fill="none" stroke="#1B365D"
              stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      </marker>
      <marker id="arrow-link" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto">
        <path d="M2 1 L8 5 L2 9" fill="none" stroke="#2D5A8A"
              stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      </marker>
    </defs>

    <!-- Paper-mask layer 1（強制） -->
    <rect width="100%" height="100%" fill="#f5f4ed"/>
    <!-- Paper-mask layer 2（可選 dotted overlay） -->
    <rect width="100%" height="100%" fill="url(#dots)" opacity="0.55"/>

    <!-- ===== TITLE + AXIS-UNIT LABEL ===== -->
    <text x="500" y="44" fill="#141413" font-size="14" font-weight="700"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Quarterly revenue trend</text>
    <text x="500" y="64" fill="#504e49" font-size="8"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.14em">REVENUE (USD THOUSANDS), BY FISCAL QUARTER</text>

    <!-- ===== Y AXIS（4 ticks，$0K–$150K） ===== -->
    <line x1="120" y1="88" x2="120" y2="480"
          stroke="#504e49" stroke-opacity="0.6" stroke-width="1"/>
    <line x1="116" y1="480" x2="120" y2="480" stroke="#504e49" stroke-width="1"/>
    <text x="108" y="484" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace" text-anchor="end">$0K</text>
    <line x1="116" y1="360" x2="120" y2="360" stroke="#504e49" stroke-width="1"/>
    <text x="108" y="364" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace" text-anchor="end">$50K</text>
    <line x1="116" y1="240" x2="120" y2="240" stroke="#504e49" stroke-width="1"/>
    <text x="108" y="244" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace" text-anchor="end">$100K</text>
    <line x1="116" y1="120" x2="120" y2="120" stroke="#504e49" stroke-width="1"/>
    <text x="108" y="124" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace" text-anchor="end">$150K</text>

    <!-- ===== X AXIS（6 個季度 tick） ===== -->
    <line x1="120" y1="480" x2="920" y2="480"
          stroke="#504e49" stroke-opacity="0.6" stroke-width="1"/>
    <line x1="120" y1="480" x2="120" y2="484" stroke="#504e49" stroke-width="1"/>
    <text x="120" y="496" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace" text-anchor="middle">23-Q1</text>
    <line x1="280" y1="480" x2="280" y2="484" stroke="#504e49" stroke-width="1"/>
    <text x="280" y="496" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace" text-anchor="middle">23-Q2</text>
    <line x1="440" y1="480" x2="440" y2="484" stroke="#504e49" stroke-width="1"/>
    <text x="440" y="496" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace" text-anchor="middle">23-Q3</text>
    <line x1="600" y1="480" x2="600" y2="484" stroke="#504e49" stroke-width="1"/>
    <text x="600" y="496" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace" text-anchor="middle">23-Q4</text>
    <line x1="760" y1="480" x2="760" y2="484" stroke="#504e49" stroke-width="1"/>
    <text x="760" y="496" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace" text-anchor="middle">24-Q1</text>
    <line x1="920" y1="480" x2="920" y2="484" stroke="#504e49" stroke-width="1"/>
    <text x="920" y="496" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace" text-anchor="middle">24-Q2</text>

    <!-- ===== SERIES B — Product B (secondary, link color, no marker) ===== -->
    <path d="M120 452 L280 440 L440 424 L600 412 L760 396 L920 380"
          fill="none" stroke="#2D5A8A" stroke-width="1.4"/>
    <circle cx="120" cy="452" r="4" fill="#2D5A8A"/>
    <circle cx="280" cy="440" r="4" fill="#2D5A8A"/>
    <circle cx="440" cy="424" r="4" fill="#2D5A8A"/>
    <circle cx="600" cy="412" r="4" fill="#2D5A8A"/>
    <circle cx="760" cy="396" r="4" fill="#2D5A8A"/>
    <circle cx="920" cy="380" r="4" fill="#2D5A8A"/>

    <!-- ===== SERIES A — Product A (focal / primary trend, accent, marker-end on final leg) ===== -->
    <path d="M120 420 L280 392 L440 356 L600 320 L760 280 L920 232"
          fill="none" stroke="#1B365D" stroke-width="1.6" marker-end="url(#arrow-accent)"/>
    <circle cx="120" cy="420" r="4" fill="#1B365D"/>
    <circle cx="280" cy="392" r="4" fill="#1B365D"/>
    <circle cx="440" cy="356" r="4" fill="#1B365D"/>
    <circle cx="600" cy="320" r="4" fill="#1B365D"/>
    <circle cx="760" cy="280" r="4" fill="#1B365D"/>
    <circle cx="920" cy="232" r="4" fill="#1B365D"/>

    <!-- ===== ANNOTATION CALLOUT — Product B plateau observation（160，非 focal） ===== -->
    <line x1="600" y1="384" x2="600" y2="408"
          stroke="#504e49" stroke-opacity="0.5" stroke-width="0.8"/>
    <rect x="520" y="336" width="160" height="48" rx="6" fill="#f5f4ed"/>
    <rect x="520" y="336" width="160" height="48" rx="6"
          fill="#f1f0eb" stroke="#504e49" stroke-width="1"/>
    <rect x="528" y="344" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="542" y="353" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">OBS</text>
    <text x="600" y="368" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Growth plateaus</text>

    <!-- ===== ANNOTATION CALLOUT — Product A peak — FOCAL（128） ===== -->
    <line x1="920" y1="200" x2="920" y2="228"
          stroke="#1B365D" stroke-opacity="0.5" stroke-width="0.8"/>
    <rect x="792" y="144" width="128" height="56" rx="6" fill="#f5f4ed"/>
    <rect data-role="focal"
          x="792" y="144" width="128" height="56" rx="6"
          fill="#EEF2F7" stroke="#1B365D" stroke-width="1.4"/>
    <rect x="800" y="152" width="28" height="12" rx="2"
          fill="transparent" stroke="#1B365D" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="814" y="161" fill="#1B365D" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">KPI</text>
    <text x="856" y="180" fill="#141413" font-size="12" font-weight="700"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">$130K peak</text>
    <text x="856" y="192" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace" text-anchor="middle">24-Q2</text>

    <!-- ===== LEGEND STRIP ===== -->
    <line x1="60" y1="560" x2="940" y2="560"
          stroke="#141413" stroke-opacity="0.10" stroke-width="0.8"/>
    <text x="60" y="580" fill="#504e49" font-size="8"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.14em">LEGEND</text>

    <line x1="140" y1="576" x2="156" y2="576"
          stroke="#1B365D" stroke-width="1.6"/>
    <circle cx="148" cy="576" r="4" fill="#1B365D"/>
    <text x="168" y="581" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Product A (focal trend)</text>

    <line x1="380" y1="576" x2="396" y2="576"
          stroke="#2D5A8A" stroke-width="1.4"/>
    <circle cx="388" cy="576" r="4" fill="#2D5A8A"/>
    <text x="408" y="581" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Product B</text>

    <rect x="580" y="568" width="16" height="12" rx="2"
          fill="#EEF2F7" stroke="#1B365D" stroke-width="1.2"/>
    <text x="600" y="581" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Key data point (peak)</text>

    <line x1="780" y1="576" x2="800" y2="576"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <text x="808" y="581" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Axis</text>

    <line x1="860" y1="576" x2="880" y2="576"
          stroke="#2D5A8A" stroke-width="1.2" marker-end="url(#arrow-link)"/>
    <text x="888" y="581" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Ref</text>
  </svg>
  <figcaption>圖：Quarterly revenue trend（Product A[focal] vs Product B，6 季度），focal 標示 Product A 的 24-Q2 峰值。</figcaption>
</figure>
```
