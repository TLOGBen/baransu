---
name: swimlane
status: complete
example: inline
---

## Contents

- Layout conventions
- Anti-patterns
- Examples

# Swimlane

**Best for**: cross-functional processes, RACI-style flow, vendor handoff, multi-team shipping workflow, visualizing cross-team ownership boundaries.

## Layout conventions

- Layer 3 derived tokens: `lane-A` = `--ink @ 0.08`, `lane-B` = `--ink @ 0.04`, `lane-C` = `--ink @ 0.02` (v1 ground truth is `#ebeae5` / `#f3f1ec` / `#f6f5f0` respectively), pre-computed to solid hex; the alpha-channel CSS function form must not appear; see `references/design-token-resolver.md`.
- One horizontal lane (or vertical column) per actor / team; lane background cycles through `lane-A` / `lane-B` / `lane-C` to distinguish them; the lane label sits in the left margin (or at the top) as a `--font-mono` eyebrow.
- The lane divider is a 1px hairline; a process step is a rect that **may only sit within the lane of the actor executing that step**; steps connect with arrows to show flow direction.
- The handoff (an arrow crossing a lane boundary) is the most important edge in a swimlane diagram; `--brand` is reserved for the single handoff causing the greatest coupling or delay, one per diagram; do not force every lane to have an equal number of steps — a lane with a single step is fine.

## Anti-patterns

- A lane with no label.
  - *Why fails*: the entire value of a swimlane is "telling the reader who owns each step"; a missing lane label throws away this sole piece of information, degrading the whole diagram into an ordinary flowchart plus extra visual noise.
- A step straddling two lanes (unclear ownership).
  - *Why fails*: a lane's semantic promise is single ownership; a step crossing lanes declares "two owners share responsibility," but in actual operation one side must act first; the visual ambiguity maps directly to process ambiguity, so the diagram ends up encouraging collaboration bugs.
- An arrow snaking back-and-forth between lanes.
  - *Why fails*: a back-and-forth arrow looks like a maze, and the reader cannot trace the main flow; reorder steps so the flow is roughly a straight line; if it cannot be straightened, that means the process itself is overly tangled — the diagram reflects that fact but does not solve it.

## Examples

Inline example below — a 3-lane cross-team flow (Frontend → Backend[focal=Persist DB] → DB). Each lane holds 2–3 nodes, the cross-lane arrow uses `arrow-link`, and there is 1 focal node. Complete `<defs>` with three chevron markers, two paper-mask layers, a node-width whitelist of 2 values `{128, 160}`, a legend strip, and all `x/y/width/height` as multiples of 4.

```html
<figure class="diagram">
  <svg viewBox="0 0 1000 600" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Three-lane swimlane: Frontend / Backend / DB">
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

    <!-- ===== LANE SEPARATOR HAIRLINES (two lines splitting the canvas into three lanes) ===== -->
    <line x1="60" y1="200" x2="940" y2="200"
          stroke="#141413" stroke-opacity="0.10" stroke-width="0.8"/>
    <line x1="60" y1="320" x2="940" y2="320"
          stroke="#141413" stroke-opacity="0.10" stroke-width="0.8"/>

    <!-- ===== LANE LABELS (left margin, Geist Mono eyebrow) ===== -->
    <text x="68" y="148" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.14em">FRONTEND</text>
    <text x="68" y="268" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.14em">BACKEND</text>
    <text x="68" y="388" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.14em">DATABASE</text>

    <!-- ===== EDGES (draw lines first) ===== -->
    <!-- A → B (within lane1, internal arrow) -->
    <line x1="256" y1="136" x2="288" y2="136"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <!-- B → C (cross lane 1→2, arrow-link) -->
    <line x1="352" y1="168" x2="192" y2="224"
          stroke="#2D5A8A" stroke-width="1.2" marker-end="url(#arrow-link)"/>
    <!-- C → D (within lane2, internal arrow) -->
    <line x1="256" y1="256" x2="288" y2="256"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <!-- D → E (within lane2, focal main flow, accent) -->
    <line x1="416" y1="256" x2="448" y2="256"
          stroke="#1B365D" stroke-width="1.4" marker-end="url(#arrow-accent)"/>
    <!-- E → F (cross lane 2→3, arrow-link, focal landing write) -->
    <line x1="528" y1="288" x2="512" y2="344"
          stroke="#2D5A8A" stroke-width="1.2" marker-end="url(#arrow-link)"/>
    <!-- F → G (within lane3, internal arrow, audit fan-out) -->
    <line x1="576" y1="376" x2="608" y2="376"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>

    <!-- ===== LANE 1: FRONTEND — 2 nodes ===== -->
    <!-- A: UI Form (128) -->
    <rect x="128" y="104" width="128" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="128" y="104" width="128" height="64" rx="6"
          fill="#f3f1ec" stroke="#504e49" stroke-width="1"/>
    <rect x="136" y="112" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="150" y="121" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">UI</text>
    <text x="192" y="144" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">UI Form</text>
    <text x="192" y="160" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">submit</text>

    <!-- B: Validate (128) -->
    <rect x="288" y="104" width="128" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="288" y="104" width="128" height="64" rx="6"
          fill="#f3f1ec" stroke="#504e49" stroke-width="1"/>
    <rect x="296" y="112" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="310" y="121" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">UI</text>
    <text x="352" y="144" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Validate</text>
    <text x="352" y="160" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">client-side</text>

    <!-- ===== LANE 2: BACKEND — 3 nodes including FOCAL ===== -->
    <!-- C: API Handler (128) -->
    <rect x="128" y="224" width="128" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="128" y="224" width="128" height="64" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="136" y="232" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="150" y="241" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">API</text>
    <text x="192" y="264" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">API Handler</text>
    <text x="192" y="280" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">POST /orders</text>

    <!-- D: Business Logic (128) -->
    <rect x="288" y="224" width="128" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="288" y="224" width="128" height="64" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="296" y="232" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="310" y="241" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">SVC</text>
    <text x="352" y="264" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Order Service</text>
    <text x="352" y="280" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">domain logic</text>

    <!-- E: Persist DB — FOCAL (160) -->
    <rect x="448" y="224" width="160" height="64" rx="6" fill="#f5f4ed"/>
    <rect data-role="focal"
          x="448" y="224" width="160" height="64" rx="6"
          fill="#EEF2F7" stroke="#1B365D" stroke-width="1.4"/>
    <rect x="456" y="232" width="28" height="12" rx="2"
          fill="transparent" stroke="#1B365D" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="470" y="241" fill="#1B365D" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">FOCAL</text>
    <text x="528" y="264" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Persist DB</text>
    <text x="528" y="280" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">transactional write</text>

    <!-- ===== LANE 3: DATABASE — 2 nodes ===== -->
    <!-- F: Postgres (128) -->
    <rect x="448" y="344" width="128" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="448" y="344" width="128" height="64" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="456" y="352" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="470" y="361" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">DB</text>
    <text x="512" y="384" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Postgres</text>
    <text x="512" y="400" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">primary</text>

    <!-- G: Audit Log (128) -->
    <rect x="608" y="344" width="128" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="608" y="344" width="128" height="64" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="616" y="352" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="630" y="361" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">LOG</text>
    <text x="672" y="384" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Audit Log</text>
    <text x="672" y="400" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">append-only</text>

    <!-- ===== LEGEND STRIP ===== -->
    <line x1="60" y1="540" x2="940" y2="540"
          stroke="#141413" stroke-opacity="0.10" stroke-width="0.8"/>
    <text x="60" y="560" fill="#504e49" font-size="8"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.14em">LEGEND</text>

    <rect x="140" y="552" width="16" height="12" rx="2"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <text x="160" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Lane step</text>

    <rect x="260" y="552" width="16" height="12" rx="2"
          fill="#EEF2F7" stroke="#1B365D" stroke-width="1.2"/>
    <text x="280" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Focal step</text>

    <line x1="380" y1="556" x2="400" y2="556"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <text x="408" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">In-lane flow</text>

    <line x1="520" y1="556" x2="540" y2="556"
          stroke="#1B365D" stroke-width="1.4" marker-end="url(#arrow-accent)"/>
    <text x="548" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Focal flow</text>

    <line x1="660" y1="556" x2="680" y2="556"
          stroke="#2D5A8A" stroke-width="1.2" marker-end="url(#arrow-link)"/>
    <text x="688" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Cross-lane handoff</text>
  </svg>
  <figcaption>圖：3-lane swimlane（Frontend → Backend[Persist DB focal] → DB），跨 lane handoff 走 arrow-link。</figcaption>
</figure>
```
