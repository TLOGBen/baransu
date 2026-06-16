---
name: layers
status: complete
example: inline
---

# Layer Stack

**Best for**: OSI model, CSS cascade, context hierarchy, tech stack, abstraction layer, memory hierarchy.

## Layout conventions

- Horizontal bands stacked vertically; each layer is a full-width rectangle (same x, same width), 4–6 layers max; layer height 56–72px, width typically 800–880px sitting inside the 1000px viewBox.
- Each row contains three segments, left to right: (1) **index tag** (`L3` / `07` / `APPLICATION`) `--font-mono` 8–9px eyebrow; (2) **layer name** slightly left of center, `--font-sans` 14–16px 600; (3) **sublabel / note** at the far right, `--font-mono` 9–10px `--color-muted`.
- Inter-layer borders are 1px hairline `--ink @ 0.12`; outer contour 1px `--ink` or `--color-muted`; fill is one of two options: alternating light tints (`--parchment` / paper-2) **or** all `--parchment` with hairline dividers — **pick one and stick to it**, never mix.
- Place a direction indicator outside the left margin (small up/down arrow + `--font-mono` label, e.g. `abstraction ↑` / `packets ↓`); `--brand` is applied only to the **single focal layer** (stroke + slight tint fill), representing the bottleneck / pay-rent layer / focus of discussion.

## Anti-patterns

- Forcing a genuinely non-hierarchical concept into a layer.
  - *Why fails*: a layer stack promises "upper layers depend on lower layers, lower layers provide abstraction to upper layers"; using it for a cross-cutting concern (like monitoring) or a peer relationship makes the reader infer a dependency that isn't there — use a swimlane or architecture diagram instead.
- Skipping a layer number (L3 → L5 with no L4 and no explanation).
  - *Why fails*: layer numbering is the only sequential promise a hierarchy has; a gap signals "something is in the middle but I didn't draw it", and the reader can't tell whether it's a design omission or a deliberate elision — the hierarchy's completeness breaks.
- A different color block per layer (rainbow stack).
  - *Why fails*: a layer's hierarchy is conveyed by vertical position + numbering, color blocks are just noise; multiple colors make the reader think "each layer represents a category" rather than "an upper/lower rank", and it clashes with the single-brand focal rule.

## Examples

Inline example below — 4-layer horizontal stack (typical web stack: UI / API / Service[focal] / Data), where each band is a sub-primitive full-width rect (not counted as a "node"), and the node role is carried by a centered 160-wide **function box** to match the allowlist. Complete `<defs>` with three chevron markers, two paper-mask layers, 1 `data-role="focal"` node (Service function box), all node `rect` widths of 160 (single-file allowlist), an abstraction ↑ direction indicator, a legend strip, and all `x/y/width/height` as multiples of 4.

```html
<figure class="diagram">
  <svg viewBox="0 0 1000 600" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="4-layer web stack with focal Service layer">
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

    <!-- ===== ABSTRACTION DIRECTION INDICATOR（左外緣） ===== -->
    <line x1="64" y1="160" x2="64" y2="92"
          stroke="#504e49" stroke-width="1" marker-end="url(#arrow)"/>
    <text x="56" y="180" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="end" letter-spacing="0.08em">abstraction</text>

    <!-- ===== LAYER BANDS（sub-primitive，非節點，不入寬白名單；提供視覺層次） ===== -->
    <!-- Layer 1: UI（top） -->
    <rect x="120" y="80" width="760" height="84" rx="6"
          fill="#f1f0eb" stroke="#504e49" stroke-width="1"/>
    <text x="140" y="100" fill="#141413" font-size="8"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.14em">L4 · UI</text>
    <text x="876" y="100" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="end">browser / client</text>

    <!-- Layer 2: API -->
    <rect x="120" y="172" width="760" height="84" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <text x="140" y="192" fill="#141413" font-size="8"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.14em">L3 · API</text>
    <text x="876" y="192" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="end">gateway / routing</text>

    <!-- Layer 3: Service — FOCAL band（slight accent tint） -->
    <rect x="120" y="264" width="760" height="84" rx="6"
          fill="#EEF2F7" stroke="#1B365D" stroke-width="1"/>
    <text x="140" y="284" fill="#1B365D" font-size="8"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.14em">L2 · SERVICE</text>
    <text x="876" y="284" fill="#1B365D" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="end">business logic</text>

    <!-- Layer 4: Data（bottom） -->
    <rect x="120" y="356" width="760" height="84" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <text x="140" y="376" fill="#141413" font-size="8"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.14em">L1 · DATA</text>
    <text x="876" y="376" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="end">persistence</text>

    <!-- ===== INTER-LAYER DEPENDENCY ARROWS（centerline，downward calls） ===== -->
    <!-- UI → API -->
    <line x1="500" y1="148" x2="500" y2="176"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <!-- API → Service (accent / focal flow) -->
    <line x1="500" y1="240" x2="500" y2="268"
          stroke="#1B365D" stroke-width="1.4" marker-end="url(#arrow-accent)"/>
    <!-- Service → Data -->
    <line x1="500" y1="332" x2="500" y2="360"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>

    <!-- ===== FUNCTION BOXES（每層中央 160-wide 節點，承擔 node 角色） ===== -->
    <!-- L4 UI function box -->
    <rect x="420" y="108" width="160" height="32" rx="6" fill="#f5f4ed"/>
    <rect x="420" y="108" width="160" height="32" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="428" y="112" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="442" y="121" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">UI</text>
    <text x="500" y="130" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">React App</text>

    <!-- L3 API function box -->
    <rect x="420" y="200" width="160" height="32" rx="6" fill="#f5f4ed"/>
    <rect x="420" y="200" width="160" height="32" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="428" y="204" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="442" y="213" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">API</text>
    <text x="500" y="222" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">FastAPI Gateway</text>

    <!-- L2 Service function box — FOCAL（160 width） -->
    <rect x="420" y="292" width="160" height="32" rx="6" fill="#f5f4ed"/>
    <rect data-role="focal"
          x="420" y="292" width="160" height="32" rx="6"
          fill="#EEF2F7" stroke="#1B365D" stroke-width="1.4"/>
    <rect x="428" y="296" width="28" height="12" rx="2"
          fill="transparent" stroke="#1B365D" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="442" y="305" fill="#1B365D" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">SVC</text>
    <text x="500" y="314" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Order Service</text>

    <!-- L1 Data function box -->
    <rect x="420" y="384" width="160" height="32" rx="6" fill="#f5f4ed"/>
    <rect x="420" y="384" width="160" height="32" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="428" y="388" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="442" y="397" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">DB</text>
    <text x="500" y="406" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Postgres</text>

    <!-- ===== LEGEND STRIP ===== -->
    <line x1="60" y1="540" x2="940" y2="540"
          stroke="#141413" stroke-opacity="0.10" stroke-width="0.8"/>
    <text x="60" y="560" fill="#504e49" font-size="8"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.14em">LEGEND</text>

    <rect x="140" y="552" width="16" height="12" rx="2"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <text x="160" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Layer band</text>

    <rect x="280" y="552" width="16" height="12" rx="2"
          fill="#EEF2F7" stroke="#1B365D" stroke-width="1.2"/>
    <text x="300" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Focal layer</text>

    <line x1="420" y1="556" x2="440" y2="556"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <text x="448" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Layer call</text>

    <line x1="560" y1="556" x2="580" y2="556"
          stroke="#1B365D" stroke-width="1.4" marker-end="url(#arrow-accent)"/>
    <text x="588" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Focal call</text>

    <line x1="700" y1="556" x2="720" y2="556"
          stroke="#2D5A8A" stroke-width="1.2" marker-end="url(#arrow-link)"/>
    <text x="728" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Cross-stack</text>
  </svg>
  <figcaption>圖：4-layer web stack（UI → API → Service[focal] → Data），每層中央 160-wide function box 承擔節點寬白名單合規；abstraction ↑。</figcaption>
</figure>
```
