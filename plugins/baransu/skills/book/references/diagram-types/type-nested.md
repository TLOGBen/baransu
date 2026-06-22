---
name: nested
status: complete
example: inline
---

## Contents

- Layout conventions
- Anti-patterns
- Examples

# Nested Containment

**Best for**: expressing hierarchy through containment — scope boundary, CLAUDE.md cascade, trust zone, folder nesting, blast radius. Outer = broad, inner = specific.

## Layout conventions

- 3–5 rounded rectangles (`rx=8`) nested, with consistent inset padding (recommended horizontal 24–32px, vertical 32–36px); irregular padding = looks like an accident.
- Each level's label sits at the top-left in `--font-mono` eyebrow style (7–8px, letter-spacing 0.14em); the label rests on a `--parchment`-colored mask rect, covering its intersection with the ring's top edge to avoid the line crossing the text.
- Stroke ladder: outermost ring faint (`--color-muted`, light) → middle layer `--color-muted` → inner layer `--ink` → innermost focal goes `--brand`; fill likewise increases in opacity from outer to inner, with the innermost using `--brand-tint`.
- An optional file-icon glyph (folded-corner rect) placed inside each level hints at scope content; italic `--font-serif` side-notes (see `references/primitive-annotation.md`) are at most 1–2, as more would steal the hierarchy's main axis.

## Anti-patterns

- More than 6 levels of nesting.
  - *Why fails*: each additional level halves the inner area, and the innermost text becomes too small to see while the stroke blends into the background; more than 6 levels means the hierarchy itself is structurally too deep and should be split into a sub-diagram rather than crammed into one figure.
- Asymmetric padding across levels (left and right unequal, top and bottom unequal).
  - *Why fails*: regular padding is the visual signal by which the reader recognizes "this is a hierarchy and not an arbitrary shape"; uneven padding makes the diagram look like a draft or a bug, breaks the grammar of nested containment, and the reader cannot immediately judge the level relationships.
- Content placed inside a ring that does not actually belong to that level (e.g. metadata, legend, unrelated note).
  - *Why fails*: nesting's promise is "ring boundary = scope boundary," and putting unrelated objects in loosens the scope semantics, so the reader cannot distinguish "this is a member of that level" from "this just happens to be drawn here," and the hierarchy expression fails.

## Examples

Inline example below — 3-level containment (1 outer system context → 2 middle bounded contexts → 3 inner aggregate nodes, where the innermost aggregate root is focal). Full `<defs>` with three chevron markers, two paper-mask layers, node-width 2-value whitelist `{128, 160}` (only leaf nodes are bound by the whitelist; the scope ring is a structural container and is not counted), legend strip and all leaf-node `x/y/width/height` multiples of 4.

```html
<figure class="diagram">
  <svg viewBox="0 0 1000 600" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="3-level nested containment: System / Bounded contexts / Aggregates">
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

    <!-- ===== OUTER RING (Level 1: System Context — scope container, faint stroke) ===== -->
    <rect x="80" y="80" width="840" height="400" rx="12"
          fill="#f5f4ed" stroke="#504e49" stroke-opacity="0.45" stroke-width="1"
          stroke-dasharray="6 4"/>
    <!-- Outer label mask + eyebrow -->
    <rect x="100" y="72" width="160" height="16" fill="#f5f4ed"/>
    <text x="108" y="84" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.14em">SYSTEM CONTEXT</text>

    <!-- ===== MIDDLE RING A (Level 2: Bounded context — UI domain) ===== -->
    <rect x="120" y="128" width="376" height="320" rx="10"
          fill="#f3f1ec" stroke="#504e49" stroke-width="1"/>
    <!-- Middle A label mask + eyebrow -->
    <rect x="140" y="120" width="160" height="16" fill="#f3f1ec"/>
    <text x="148" y="132" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.14em">UI DOMAIN</text>

    <!-- ===== MIDDLE RING B (Level 2: Bounded context — Order domain) ===== -->
    <rect x="504" y="128" width="376" height="320" rx="10"
          fill="#f3f1ec" stroke="#504e49" stroke-width="1"/>
    <!-- Middle B label mask + eyebrow -->
    <rect x="524" y="120" width="160" height="16" fill="#f3f1ec"/>
    <text x="532" y="132" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.14em">ORDER DOMAIN</text>

    <!-- ===== INNER LEAF NODES (Level 3: Aggregates — whitelist {128, 160}) ===== -->

    <!-- Inner A1: Frontend SPA aggregate (160) — inside UI DOMAIN -->
    <rect x="200" y="240" width="160" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="200" y="240" width="160" height="64" rx="6"
          fill="#ebeae5" stroke="#141413" stroke-width="1"/>
    <rect x="208" y="248" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="222" y="257" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">AGG</text>
    <text x="280" y="280" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Frontend SPA</text>
    <text x="280" y="296" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">session aggregate</text>

    <!-- Inner B1: Order Service aggregate (128) — inside ORDER DOMAIN -->
    <rect x="560" y="192" width="128" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="560" y="192" width="128" height="64" rx="6"
          fill="#ebeae5" stroke="#141413" stroke-width="1"/>
    <rect x="568" y="200" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="582" y="209" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">AGG</text>
    <text x="624" y="232" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Order Service</text>
    <text x="624" y="248" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">command handler</text>

    <!-- Inner B2: Aggregate Root — FOCAL (160) — inside ORDER DOMAIN（32px right padding to middle ring） -->
    <rect x="688" y="320" width="160" height="64" rx="6" fill="#f5f4ed"/>
    <rect data-role="focal"
          x="688" y="320" width="160" height="64" rx="6"
          fill="#EEF2F7" stroke="#1B365D" stroke-width="1.4"/>
    <rect x="696" y="328" width="28" height="12" rx="2"
          fill="transparent" stroke="#1B365D" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="710" y="337" fill="#1B365D" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">FOCAL</text>
    <text x="768" y="360" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Order Root</text>
    <text x="768" y="376" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">aggregate root</text>

    <!-- ===== EDGES（跨層 / 同層） ===== -->
    <!-- Frontend SPA → Order Service（cross-domain，arrow-link） -->
    <line x1="360" y1="272" x2="560" y2="224"
          stroke="#2D5A8A" stroke-width="1.2" marker-end="url(#arrow-link)"/>
    <!-- Order Service → Order Root（同 domain，focal flow accent；landing 點 x=688 為 focal 左緣） -->
    <line x1="624" y1="256" x2="688" y2="352"
          stroke="#1B365D" stroke-width="1.4" marker-end="url(#arrow-accent)"/>

    <!-- ===== LEGEND STRIP ===== -->
    <line x1="60" y1="540" x2="940" y2="540"
          stroke="#141413" stroke-opacity="0.10" stroke-width="0.8"/>
    <text x="60" y="560" fill="#504e49" font-size="8"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.14em">LEGEND</text>

    <rect x="140" y="552" width="16" height="12" rx="2"
          fill="#f5f4ed" stroke="#504e49" stroke-opacity="0.45" stroke-width="1"
          stroke-dasharray="3 2"/>
    <text x="160" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Outer scope</text>

    <rect x="280" y="552" width="16" height="12" rx="2"
          fill="#f3f1ec" stroke="#504e49" stroke-width="1"/>
    <text x="300" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Bounded context</text>

    <rect x="436" y="552" width="16" height="12" rx="2"
          fill="#ebeae5" stroke="#141413" stroke-width="1"/>
    <text x="456" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Aggregate</text>

    <rect x="556" y="552" width="16" height="12" rx="2"
          fill="#EEF2F7" stroke="#1B365D" stroke-width="1.2"/>
    <text x="576" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Focal aggregate root</text>

    <line x1="744" y1="556" x2="764" y2="556"
          stroke="#1B365D" stroke-width="1.4" marker-end="url(#arrow-accent)"/>
    <text x="772" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Focal flow</text>

    <line x1="852" y1="556" x2="872" y2="556"
          stroke="#2D5A8A" stroke-width="1.2" marker-end="url(#arrow-link)"/>
    <text x="880" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Cross-domain</text>

    <line x1="60" y1="580" x2="80" y2="580"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <text x="88" y="584" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Internal link</text>
  </svg>
  <figcaption>圖：3-level nested containment（System Context → UI / Order domains → Order Root focal aggregate）。</figcaption>
</figure>
```
