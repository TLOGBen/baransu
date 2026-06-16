---
name: architecture
status: complete
example: inline
---

# Architecture

**Best for**: system overview、data-flow diagrams、integration map、infra topology（infrastructure topology）、components & connections.

## Layout conventions

- Group by tier or trust boundary (frontend → backend → data; public → private); align same-group nodes horizontally or vertically, separate groups with spacing — don't rely on connections to imply layering.
- Pick one main flow direction, LTR or TTB, and stick to it; never mix two main flow directions within one diagram. Secondary feedback lines (callback, retry) may run in reverse, but their arrows must be explicitly marked.
- Draw lines first, boxes second: in the SVG, arrow `<line>` elements enter the DOM first and node `<rect>` / `<g>` elements after, so that z-order pushes connections beneath nodes and arrow tails don't pierce node outlines.
- Mark 1–2 focal nodes with the `data-role="focal"` attribute (**not** a class); focal nodes use `--brand-tint` fill + `--brand` stroke and terminate with `marker-end="url(#arrow-accent)"`. At most 2 focal per SVG — beyond that the "emphasis" disappears.
- A dashed boundary rectangle marks a region (VPC, security group, trust zone); the boundary label sits on a `--parchment`-colored mask that covers the intersection of the dashed line and the label, so the line doesn't cross the text.
- Use only the 3-step width whitelist {128 / 144 / 160} (Kami diagrams.md L79; mix at most 2 steps per SVG); don't let each node's width vary freely — readers scan at a stable speed only when the visual rhythm is consistent.
- Node embedded text is 14–24px: above 24 it looks like a hero, below 14 it blurs in a 1× SVG. Use `--font-sans` for titles, `--font-mono` for metric / id, and `--color-muted` for units.
- The three markers (`arrow` / `arrow-accent` / `arrow-link`) are defined once inside `<defs>` with fixed attributes `markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto"`; never hand-write arrow paths, to avoid alignment drift under viewBox scaling.

## Anti-patterns

- **Every box is focal** (all `--brand-tint` fill, `--brand` stroke).
  - *Why fails*: focal is inherently a relative comparison — when every node is "emphasized," the visual hierarchy collapses, the reader can't lock onto the main path or principal integration point within 3 seconds, and the diagram effectively has no emphasis.
- **A bidirectional arrow where the one-way meaning is already clear** (e.g. `Browser ↔ CDN`, when only the read path actually matters).
  - *Why fails*: the bidirectional arrow adds noise in one extra direction, forcing the reader to spend an extra beat deciding "which side of this line do I read"; it also robs the nodes that genuinely need bidirectional semantics (such as cache write-back) of their distinctiveness.
- **The legend floats inside the diagram canvas**, overlapping nodes or connections.
  - *Why fails*: the legend is meta-information, at a different reading level from the diagram body; placed inside the canvas it collides with nodes and gets crossed by connections, forcing the reader to shift focus back and forth between "reading the diagram" and "consulting the legend." Put it in a legend strip about 60px from the bottom of the SVG (separated by a hairline, horizontal items) or outside the canvas.
- **Marking node type by color rather than by shape** (e.g. all services red, all datastores blue).
  - *Why fails*: the Kami spec gives only three semantic colors (`--brand` / `--brand-tint` / `--color-muted`); extra colors over-load the palette system, conflict with the semantics of focal, and can't be distinguished by colorblind readers. Type distinction should go through shape (rect / cylinder / hexagon) or a dashed border, leaving color for focal and boundary.

## Examples

Inline example below — 6-node microservice topology (User → CDN → API[focal] → DB; side branches Auth, Cache, Queue). A complete `<defs>` with three chevron markers (`#arrow` / `#arrow-accent` / `#arrow-link`, all stroke-drawn chevrons via `path d="M2 1 L8 5 L2 9"`), two paper-mask layers, 1 `data-role="focal"` node, the 2-step node-width whitelist `{128, 160}`, a legend strip, and all `x/y/width/height` as multiples of 4. Copy this `<figure class="diagram">` block and swap the nodes to reuse it.

```html
<figure class="diagram">
  <svg viewBox="0 0 1000 600" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Microservice architecture topology">
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

    <!-- ===== EDGES（先畫線，後畫節點以遮邊尾） ===== -->
    <!-- User → CDN（HTTP，link 色） -->
    <line x1="208" y1="128" x2="288" y2="128"
          stroke="#2D5A8A" stroke-width="1.2" marker-end="url(#arrow-link)"/>
    <!-- CDN → API（focal 主流，accent 色） -->
    <line x1="416" y1="128" x2="416" y2="240"
          stroke="#1B365D" stroke-width="1.4" marker-end="url(#arrow-accent)"/>
    <!-- Auth → API（驗證回填，內部箭頭） -->
    <line x1="560" y1="160" x2="496" y2="240"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <!-- API → DB（focal flow，accent） -->
    <line x1="496" y1="304" x2="480" y2="384"
          stroke="#1B365D" stroke-width="1.4" marker-end="url(#arrow-accent)"/>
    <!-- API → Cache（內部 read-through） -->
    <line x1="432" y1="304" x2="304" y2="384"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <!-- API → Queue（事件外送） -->
    <line x1="560" y1="304" x2="656" y2="384"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>

    <!-- ===== NODES — 寬白名單 2 檔 {128, 160}；focal 用 160 ===== -->
    <!-- Tier 1：External user（128） -->
    <rect x="80" y="96" width="128" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="80" y="96" width="128" height="64" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="88" y="104" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="102" y="113" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">EXT</text>
    <text x="144" y="136" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Users</text>
    <text x="144" y="152" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">browser</text>

    <!-- Tier 1：CDN（128） -->
    <rect x="288" y="96" width="128" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="288" y="96" width="128" height="64" rx="6"
          fill="#f1f0eb" stroke="#504e49" stroke-width="1"/>
    <rect x="296" y="104" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="310" y="113" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">CDN</text>
    <text x="352" y="136" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">CloudFront</text>
    <text x="352" y="152" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">edge cache</text>

    <!-- Tier 1：Auth service（128） -->
    <rect x="496" y="96" width="128" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="496" y="96" width="128" height="64" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="504" y="104" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="518" y="113" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">SSO</text>
    <text x="560" y="136" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Auth</text>
    <text x="560" y="152" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">OIDC</text>

    <!-- Tier 2：API server — FOCAL（160） -->
    <rect x="416" y="240" width="160" height="64" rx="6" fill="#f5f4ed"/>
    <rect data-role="focal"
          x="416" y="240" width="160" height="64" rx="6"
          fill="#EEF2F7" stroke="#1B365D" stroke-width="1.4"/>
    <rect x="424" y="248" width="28" height="12" rx="2"
          fill="transparent" stroke="#1B365D" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="438" y="257" fill="#1B365D" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">API</text>
    <text x="496" y="280" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">API Gateway</text>
    <text x="496" y="296" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">FastAPI :8000</text>

    <!-- Tier 3：Cache（128） -->
    <rect x="176" y="384" width="128" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="176" y="384" width="128" height="64" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="184" y="392" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="198" y="401" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">CACHE</text>
    <text x="240" y="424" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Redis</text>
    <text x="240" y="440" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">read-through</text>

    <!-- Tier 3：Database（128） -->
    <rect x="416" y="384" width="128" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="416" y="384" width="128" height="64" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="424" y="392" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="438" y="401" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">DB</text>
    <text x="480" y="424" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Postgres</text>
    <text x="480" y="440" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">primary</text>

    <!-- Tier 3：Message queue（128） -->
    <rect x="656" y="384" width="128" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="656" y="384" width="128" height="64" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="664" y="392" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="678" y="401" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">MQ</text>
    <text x="720" y="424" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Kafka</text>
    <text x="720" y="440" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">events</text>

    <!-- ===== LEGEND STRIP ===== -->
    <line x1="60" y1="540" x2="940" y2="540"
          stroke="#141413" stroke-opacity="0.10" stroke-width="0.8"/>
    <text x="60" y="560" fill="#504e49" font-size="8"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.14em">LEGEND</text>

    <rect x="140" y="552" width="16" height="12" rx="2"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <text x="160" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Service node</text>

    <rect x="280" y="552" width="16" height="12" rx="2"
          fill="#EEF2F7" stroke="#1B365D" stroke-width="1.2"/>
    <text x="300" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Focal node</text>

    <line x1="420" y1="556" x2="440" y2="556"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <text x="448" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Internal call</text>

    <line x1="560" y1="556" x2="580" y2="556"
          stroke="#1B365D" stroke-width="1.4" marker-end="url(#arrow-accent)"/>
    <text x="588" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Focal flow</text>

    <line x1="700" y1="556" x2="720" y2="556"
          stroke="#2D5A8A" stroke-width="1.2" marker-end="url(#arrow-link)"/>
    <text x="728" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">External / HTTP</text>
  </svg>
  <figcaption>圖：6-node 微服務拓樸（User → CDN → API[focal] → DB；側支 Auth / Cache / Queue）。</figcaption>
</figure>
```
