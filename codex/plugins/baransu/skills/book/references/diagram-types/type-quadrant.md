---
name: quadrant
status: complete
example: inline
---

## Contents

- Layout conventions
- Anti-patterns
- Examples

# Quadrant

**Best for**: priority ranking (Impact × Effort), positioning maps (Reach × Frequency), portfolio map, 2×2 decision frame, scenario planning.

## Layout conventions

- 2×2 grid; the axis line is a 1px `--ink` cross through the center; the axis arrow tip stops ~60–80px inside the viewBox edge, leaving breathing room for the label.
- **Axis label Jobs-minimal**: one **single word** per arrow tip, with no `↑` / `→` glyphs and no `(HIGH/LOW)` parenthetical modifiers; `--font-mono` 9px regular weight, tracked `0.18em`, uppercase; flanking the arrow tip, never sitting on the axis line.
- An item is a small labeled dot (`r=4`) distributed within the four quadrants; the label sits 8–10px from the dot and **must not cross the axis line**; cap item count at ~12, otherwise cluster them or split the diagram.
- `--brand` is reserved for the single "do first" item (usually landing in the top-right quadrant); it must not be applied to multiple items, nor used to fill an entire quadrant cell.

## Anti-patterns

- Filling each of the four quadrants with a different color block.
  - *Why fails*: a quadrant carries its information through "position + label"; color blocks are just noise; multi-color fills compete with the single `--brand` focal, and colorblind readers cannot distinguish the quadrants, violating the Kami three-semantic-color limit.
- An item landing on the axis line (ambiguous quadrant membership).
  - *Why fails*: the axis splits the plane into four regions on the premise that an item lies definitively within one region; landing on the line declares "both quadrants apply," breaking the decision power of the 2×2 frame, and the reader cannot answer "which category does this item belong to."
- Missing axis name, or labels carrying redundant modifiers like `↑ HIGH IMPACT`.
  - *Why fails*: without a name the reader does not know which dimension x/y each represent, so the diagram has effectively no coordinate system; the extra `↑` glyph and `HIGH / LOW` parentheses merely repeat the directional information the arrow already conveys, which is visually redundant and violates the Jobs-minimal principle.

## Examples

Inline example below — a 2×2 Impact × Effort priority matrix with 4 quadrant labels, 6 data dots, focal = the top-left "Quick Wins" quadrant. Complete `<defs>` with three chevron markers, two paper-mask layers, a single focal callout rect with a width whitelist of `{128}` (a single value, satisfying the ≤ 2-value rule), a legend strip, and all `x/y/width/height/cx/cy` as multiples of 4.

```html
<figure class="diagram">
  <svg viewBox="0 0 1000 600" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Impact by Effort prioritization quadrant">
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

    <!-- Paper-mask layer 1 (required) -->
    <rect width="100%" height="100%" fill="#f5f4ed"/>
    <!-- Paper-mask layer 2 (optional dotted overlay) -->
    <rect width="100%" height="100%" fill="url(#dots)" opacity="0.55"/>

    <!-- ===== AXIS CROSS (1px hairline) ===== -->
    <!-- Y axis (vertical) — with up-tip arrow (accent, on the focal dimension; marker-end lands at y=80 to align with the IMPACT label) -->
    <line x1="500" y1="480" x2="500" y2="80"
          stroke="#141413" stroke-width="1"
          marker-end="url(#arrow-accent)"/>
    <!-- X axis (horizontal) — with right-tip arrow (accent) -->
    <line x1="80" y1="280" x2="920" y2="280"
          stroke="#141413" stroke-width="1"
          marker-end="url(#arrow-accent)"/>

    <!-- ===== AXIS LABELS (Jobs-minimal: single word, no glyph, no parentheses) ===== -->
    <!-- Y top tip: IMPACT (flanking the arrow tip, not sitting on the axis line) -->
    <text x="476" y="72" fill="#141413" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="end" letter-spacing="0.18em">IMPACT</text>
    <!-- X right tip: EFFORT -->
    <text x="928" y="276" fill="#141413" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.18em">EFFORT</text>

    <!-- ===== QUADRANT LABELS ===== -->
    <!-- Top-right: BIG BETS (high impact, high effort) -->
    <text x="720" y="120" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.14em">BIG BETS</text>
    <!-- Bottom-left: FILL-INS (low impact, low effort) -->
    <text x="180" y="448" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.14em">FILL-INS</text>
    <!-- Bottom-right: MONEY PIT (low impact, high effort) -->
    <text x="708" y="448" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.14em">MONEY PIT</text>

    <!-- Top-left: QUICK WINS — FOCAL callout box (128 wide) -->
    <rect x="120" y="104" width="128" height="32" rx="4" fill="#f5f4ed"/>
    <rect data-role="focal"
          x="120" y="104" width="128" height="32" rx="4"
          fill="#EEF2F7" stroke="#1B365D" stroke-width="1.4"/>
    <text x="184" y="124" fill="#1B365D" font-size="10"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.14em">QUICK WINS</text>

    <!-- ===== DATA POINTS (6 dots, r=4) ===== -->
    <!-- A: Caching — Quick Wins quadrant -->
    <circle cx="232" cy="200" r="4" fill="#1B365D"/>
    <text x="244" y="204" fill="#141413" font-size="10"
          font-family="'Geist', system-ui, sans-serif">Caching</text>

    <!-- B: Auth fix — Quick Wins quadrant -->
    <circle cx="320" cy="240" r="4" fill="#1B365D"/>
    <text x="332" y="244" fill="#141413" font-size="10"
          font-family="'Geist', system-ui, sans-serif">Auth fix</text>

    <!-- C: Redesign — Big Bets quadrant -->
    <circle cx="720" cy="160" r="4" fill="#141413"/>
    <text x="732" y="164" fill="#141413" font-size="10"
          font-family="'Geist', system-ui, sans-serif">Redesign</text>

    <!-- D: ML pipeline — Big Bets quadrant -->
    <circle cx="800" cy="200" r="4" fill="#141413"/>
    <text x="812" y="204" fill="#141413" font-size="10"
          font-family="'Geist', system-ui, sans-serif">ML pipeline</text>

    <!-- E: Linting — Fill-ins quadrant -->
    <circle cx="240" cy="400" r="4" fill="#141413"/>
    <text x="252" y="404" fill="#141413" font-size="10"
          font-family="'Geist', system-ui, sans-serif">Linting</text>

    <!-- F: Legacy migration — Money Pit quadrant -->
    <circle cx="760" cy="400" r="4" fill="#141413"/>
    <text x="772" y="404" fill="#141413" font-size="10"
          font-family="'Geist', system-ui, sans-serif">Legacy migration</text>

    <!-- ===== LEGEND STRIP ===== -->
    <line x1="60" y1="540" x2="940" y2="540"
          stroke="#141413" stroke-opacity="0.10" stroke-width="0.8"/>
    <text x="60" y="560" fill="#504e49" font-size="8"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.14em">LEGEND</text>

    <circle cx="148" cy="556" r="4" fill="#141413"/>
    <text x="160" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Item</text>

    <circle cx="220" cy="556" r="4" fill="#1B365D"/>
    <text x="232" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Focal item</text>

    <rect x="320" y="548" width="16" height="12" rx="2"
          fill="#EEF2F7" stroke="#1B365D" stroke-width="1.2"/>
    <text x="340" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Focal quadrant</text>

    <line x1="460" y1="556" x2="480" y2="556"
          stroke="#141413" stroke-width="1" marker-end="url(#arrow-accent)"/>
    <text x="488" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Axis direction</text>

    <line x1="612" y1="556" x2="632" y2="556"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <text x="640" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Internal flow</text>

    <line x1="752" y1="556" x2="772" y2="556"
          stroke="#2D5A8A" stroke-width="1.2" marker-end="url(#arrow-link)"/>
    <text x="780" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">External link</text>
  </svg>
  <figcaption>圖：2×2 Impact × Effort 矩陣，6 個 data point；Quick Wins 為 focal 象限。</figcaption>
</figure>
```
