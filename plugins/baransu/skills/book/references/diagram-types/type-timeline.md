---
name: timeline
status: complete
example: inline
---

## Contents

- Layout conventions
- Anti-patterns
- Examples

# Timeline

**Best for**: release history, project milestones, incident timelines, roadmap, changelog visualization.

## Layout conventions

- A single central horizontal hairline baseline (`stroke-width=1`, `--color-muted`); tick marks land on time boundaries (quarters / months / sprints), with the date label below in `--font-mono`.
- An event is a small filled circle on the baseline (`r=4`, `--ink`); labels alternate above and below to avoid collisions, connecting back to the circle via a 1px hairline drop.
- A major milestone is a `--brand`-colored circle (`r=6`) + a `--font-sans` bold label; a single diagram highlights only the true "milestones" — not every event should be marked with brand.
- Time scale must be honest: when intervals are unequal, circle spacing must be unequal too; in over-dense segments do an explicit axis break, never faking linear spacing for aesthetics.

## Anti-patterns

- Spacing temporally unequal events at equal distances.
  - *Why fails*: a timeline's sole semantic promise is "the x-axis represents time"; equal spacing turns unequal into equal, and the reader misjudges release cadence or incident frequency — the diagram simply lies.
- Missing an axis unit label ("is this day / week / quarter?").
  - *Why fails*: a timeline's tick numbers (e.g. `2024-Q1`) need unit context, otherwise `Q1` and `Sprint 1` look the same visually; no unit = the reader must go back to the prose to guess, violating the principle that a diagram should be self-carrying.
- Multiple labels with no vertical offset, all crammed on one side of the baseline.
  - *Why fails*: labels of adjacent events overlap to the point of illegibility; the timeline convention that labels must alternate above and below exists precisely to use 2D to resolve collisions in a 1D space — omitting this offset means giving up readability.

## Examples

Inline example below — a 6-milestone release timeline (`v0.1 → v0.5 → v1.0[focal] → v1.1 → v1.2 → v2.0`), horizontal baseline + alternating date / label, chevron markers on each milestone connector. Complete `<defs>` with three chevron markers, two paper-mask layers, 1 `data-role="focal"` milestone (v1.0 release), a node-width whitelist of 2 values `{128, 160}`, a legend strip, and all `x/y/width/height` as multiples of 4. The baseline tick circle is a sub-primitive (< 40px) and does not count toward the node-width whitelist.

```html
<figure class="diagram">
  <svg viewBox="0 0 1000 600" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Project release timeline 2023-2026">
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

    <!-- ===== AXIS BASELINE ===== -->
    <line x1="80" y1="304" x2="920" y2="304"
          stroke="#504e49" stroke-opacity="0.6" stroke-width="1"/>
    <text x="60" y="308" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="end">2023</text>
    <text x="940" y="308" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace">2026</text>
    <text x="500" y="328" fill="#504e49" font-size="8"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.14em">RELEASE TIMELINE (quarters)</text>

    <!-- ===== MILESTONE CONNECTOR ARROWS (chevron between events) ===== -->
    <!-- v0.1 → v0.5 -->
    <line x1="156" y1="304" x2="220" y2="304"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <!-- v0.5 → v1.0 (accent, leads into focal) -->
    <line x1="320" y1="304" x2="380" y2="304"
          stroke="#1B365D" stroke-width="1.4" marker-end="url(#arrow-accent)"/>
    <!-- v1.0 → v1.1 (accent, leaves focal) -->
    <line x1="500" y1="304" x2="556" y2="304"
          stroke="#1B365D" stroke-width="1.4" marker-end="url(#arrow-accent)"/>
    <!-- v1.1 → v1.2 -->
    <line x1="640" y1="304" x2="700" y2="304"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <!-- v1.2 → v2.0 (external major bump, link) -->
    <line x1="780" y1="304" x2="840" y2="304"
          stroke="#2D5A8A" stroke-width="1.2" marker-end="url(#arrow-link)"/>

    <!-- ===== MILESTONE NODES (rect cards above/below baseline) ===== -->
    <!-- v0.1 (128, above) -->
    <text x="92" y="232" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace">2023-Q2</text>
    <rect x="92" y="240" width="128" height="48" rx="6" fill="#f5f4ed"/>
    <rect x="92" y="240" width="128" height="48" rx="6"
          fill="#faf9f5" stroke="#504e49" stroke-width="1"/>
    <rect x="100" y="248" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="114" y="257" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">REL</text>
    <text x="156" y="276" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">v0.1 alpha</text>
    <line x1="156" y1="288" x2="156" y2="300"
          stroke="#504e49" stroke-opacity="0.5" stroke-width="0.8"/>
    <circle cx="156" cy="304" r="4" fill="#141413"/>

    <!-- v0.5 (128, below) -->
    <circle cx="284" cy="304" r="4" fill="#141413"/>
    <line x1="284" y1="308" x2="284" y2="320"
          stroke="#504e49" stroke-opacity="0.5" stroke-width="0.8"/>
    <rect x="220" y="320" width="128" height="48" rx="6" fill="#f5f4ed"/>
    <rect x="220" y="320" width="128" height="48" rx="6"
          fill="#faf9f5" stroke="#504e49" stroke-width="1"/>
    <rect x="228" y="328" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="242" y="337" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">REL</text>
    <text x="284" y="356" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">v0.5 beta</text>
    <text x="284" y="384" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">2024-Q1</text>

    <!-- v1.0 — FOCAL (160, above) -->
    <text x="380" y="184" fill="#1B365D" font-size="9" font-weight="600"
          font-family="'Geist Mono', ui-monospace, monospace">2024-Q4</text>
    <rect x="380" y="192" width="160" height="56" rx="6" fill="#f5f4ed"/>
    <rect data-role="focal"
          x="380" y="192" width="160" height="56" rx="6"
          fill="#EEF2F7" stroke="#1B365D" stroke-width="1.4"/>
    <rect x="388" y="200" width="28" height="12" rx="2"
          fill="transparent" stroke="#1B365D" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="402" y="209" fill="#1B365D" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">GA</text>
    <text x="460" y="228" fill="#141413" font-size="14" font-weight="700"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">v1.0 release</text>
    <text x="460" y="244" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">general availability</text>
    <line x1="460" y1="248" x2="460" y2="300"
          stroke="#1B365D" stroke-opacity="0.6" stroke-width="1"/>
    <circle cx="460" cy="304" r="6" fill="#1B365D"/>

    <!-- v1.1 (128, below) -->
    <circle cx="600" cy="304" r="4" fill="#141413"/>
    <line x1="600" y1="308" x2="600" y2="320"
          stroke="#504e49" stroke-opacity="0.5" stroke-width="0.8"/>
    <rect x="536" y="320" width="128" height="48" rx="6" fill="#f5f4ed"/>
    <rect x="536" y="320" width="128" height="48" rx="6"
          fill="#faf9f5" stroke="#504e49" stroke-width="1"/>
    <rect x="544" y="328" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="558" y="337" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">REL</text>
    <text x="600" y="356" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">v1.1 patch</text>
    <text x="600" y="384" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">2025-Q2</text>

    <!-- v1.2 (128, above) -->
    <text x="676" y="232" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace">2025-Q4</text>
    <rect x="676" y="240" width="128" height="48" rx="6" fill="#f5f4ed"/>
    <rect x="676" y="240" width="128" height="48" rx="6"
          fill="#faf9f5" stroke="#504e49" stroke-width="1"/>
    <rect x="684" y="248" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="698" y="257" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">REL</text>
    <text x="740" y="276" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">v1.2 minor</text>
    <line x1="740" y1="288" x2="740" y2="300"
          stroke="#504e49" stroke-opacity="0.5" stroke-width="0.8"/>
    <circle cx="740" cy="304" r="4" fill="#141413"/>

    <!-- v2.0 (128, below) -->
    <circle cx="864" cy="304" r="4" fill="#141413"/>
    <line x1="864" y1="308" x2="864" y2="320"
          stroke="#504e49" stroke-opacity="0.5" stroke-width="0.8"/>
    <rect x="800" y="320" width="128" height="48" rx="6" fill="#f5f4ed"/>
    <rect x="800" y="320" width="128" height="48" rx="6"
          fill="#faf9f5" stroke="#2D5A8A" stroke-width="1"/>
    <rect x="808" y="328" width="28" height="12" rx="2"
          fill="transparent" stroke="#2D5A8A" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="822" y="337" fill="#2D5A8A" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">NEXT</text>
    <text x="864" y="356" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">v2.0 plan</text>
    <text x="864" y="384" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">2026-Q3</text>

    <!-- ===== LEGEND STRIP ===== -->
    <line x1="60" y1="540" x2="940" y2="540"
          stroke="#141413" stroke-opacity="0.10" stroke-width="0.8"/>
    <text x="60" y="560" fill="#504e49" font-size="8"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.14em">LEGEND</text>

    <circle cx="148" cy="556" r="4" fill="#141413"/>
    <text x="160" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Minor release</text>

    <circle cx="280" cy="556" r="6" fill="#1B365D"/>
    <text x="292" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Focal milestone</text>

    <line x1="420" y1="556" x2="440" y2="556"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <text x="448" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Step</text>

    <line x1="520" y1="556" x2="540" y2="556"
          stroke="#1B365D" stroke-width="1.4" marker-end="url(#arrow-accent)"/>
    <text x="548" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Into / out of focal</text>

    <line x1="680" y1="556" x2="700" y2="556"
          stroke="#2D5A8A" stroke-width="1.2" marker-end="url(#arrow-link)"/>
    <text x="708" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Major bump (next era)</text>
  </svg>
  <figcaption>圖：6-milestone release timeline（v0.1 → v0.5 → v1.0[focal] → v1.1 → v1.2 → v2.0），focal 標示 GA release。</figcaption>
</figure>
```
