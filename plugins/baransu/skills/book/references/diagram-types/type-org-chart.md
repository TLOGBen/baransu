---
name: org-chart
status: complete
example: inline
---

## Contents

- Layout conventions
- Anti-patterns
- Examples

# Org Chart

**Best for**: accountable ownership / who-owns-what routing / invocation + escalation paths / coverage-gap map / agent-team responsibility.

## Layout conventions

- **Root owner top-center; the single focal slot goes to the front door**: the accountable root sits top-center, and `data-role="focal"` marks whichever node receives ambiguous work (usually the root); the reader's first question is "where do I send this?", and one accent-contrast node answers it in a single fixation instead of a full scan.
- **Orthogonal connectors only, no arrowheads**: parent bottom-center drops a vertical 1px `--text-muted` line to a horizontal bus; each child rises from the bus with its own vertical drop. No diagonals. Reporting lines are symmetric relationships, so they carry NO chevron markers — an org chart with no other arrows therefore defines zero `<marker>` ids inside `<defs>` (the legitimate bijective-zero case of §4.3; defining an unreferenced marker is a GATE-D fail).
- **Node anatomy, 3 lines max**: owner name (12px sans, primary), invocation route as a 9px mono sublabel (handle / queue / trigger — how work actually reaches this owner), then an optional 2–4-word scope line. Never full job descriptions — the chart answers routing, not performance review, and description prose buries the route the reader came for.
- **Budgets**: ≤12 visible nodes per chart (past 12, split into one overview chart + per-pod detail charts); ≤4 tiers deep; ≤5 direct reports per parent (a 6th report means a grouping node is missing); exactly ≤1 accent-focal node — past these budgets "who owns X" stops resolving in one pass and the chart degrades into a directory lookup.
- **Planned / not-yet-wired owners stay visible**: an owner whose route is not wired yet is drawn dashed (`stroke-dasharray="4,3"`) at reduced stroke-opacity — never omitted: a missing route is operational information, and hiding the gap draws a healthier org than the one that exists, and readers route work into a void.
- **Escalation and approval rules are footer content**: escalation paths, approval thresholds, and on-call rotations go into a footer strip or one side callout — never modeled as extra hierarchy nodes — rules are not owners, and drawing them as boxes inflates the node budget and fakes reporting lines that do not exist.
- **Disambiguation vs `tree`**: choose org-chart when nodes are accountable OWNERS and the reader's question is ownership or routing ("who owns X, how do I reach them, who covers the gap"); generic parent-child structure (taxonomy, file tree, decision breakdown) stays with `type-tree.md`. §4.9 encodes this by row position: the Org Chart row sits above the Tree row precisely so ownership content is not swallowed by the broader hierarchy first-match.
- **Variant — consultant scenario matrix (2×2 named futures)**: when the ownership decision splits across two independent drivers instead of a reporting line ("who owns this depends on X and on Y"), drop the hierarchy and draw a 2×2 named-scenario grid. Base geometry comes from `type-quadrant.md` (axis cross, Jobs-minimal labels); the grammar difference: a quadrant's axes hold a measured range and an item's position carries meaning — here each axis holds a RANGE of one driver, each cell holds a NAMED future, and position inside a cell carries no meaning. Concretely: double-ended axes (both `marker-start` and `marker-end` chevrons, because the range runs both ways), one single-word mono label beyond each arrow tip (no `↑`/`→` glyphs, no `(HIGH/LOW)` parentheticals, never sitting on the axis line), every cell carries a NAMED scenario + a 1–2-line description (never "Scenario 1/2/3/4"), exactly one focal cell (tinted `#EEF2F7` fill + accent stroke) marking the planning baseline, and a corner tag whose words repeat the two axis labels exactly — an unnamed cell forces the reader to reconstruct the future from coordinates — the names are the whole payload of a scenario matrix.

## Anti-patterns

- **Identical boxes for every rank**
  - *Why fails*: with no focal front door, every routing question restarts a full scan; the one decision the chart exists to answer — "where does ambiguous work go?" — is the one it refuses to answer.
- **Full job descriptions inside nodes**
  - *Why fails*: routing information (name + invocation route) drowns in evaluation prose; the reader must read every box to find any box, and free-length text bursts the {128, 144, 160} node-width rhythm.
- **An unwired owner drawn as an active one**
  - *Why fails*: the chart promises a route that does not exist — work sent there silently disappears, and one broken promise teaches the reader to distrust every solid box on the chart.
- **Swimlane chosen when the question is ownership, not process**
  - *Why fails*: a swimlane answers "in what order does work move across roles"; an ownership question needs a stable who-owns-what map — forcing it into lanes buries the owners inside process steps the reader never asked about.
- **More than one accent-focal node**
  - *Why fails*: focal is a relative contrast; two front doors is no front door, and ambiguous work gets routed by coin flip.
- **Unnamed scenario cells in the matrix variant**
  - *Why fails*: "Scenario 3" carries zero content — the reader must re-derive the future from axis coordinates, which is exactly the work the named grid was supposed to have already done.

## Examples

Inline example below — a 3-tier, 9-node agent-team ownership chart (Team Lead [focal front door] → 3 pod owners → 5 agents, one of them dashed "not wired yet"). Complete `<defs>` with the dots pattern and **zero marker definitions** (reporting lines are symmetric — this is §4.3's bijective-zero case: no `<marker>` defined, no `url(#…)` referenced), two paper-mask layers, drop-bus-drop orthogonal `<line>` connectors, the 2-step node-width whitelist `{144, 160}`, §4.5 type tags on every node, 1 `data-role="focal"` node, one dashed planned-owner node, a legend strip with an escalation footer line, and all `<rect>/<line>` geometry as multiples of 4.

```html
<figure class="diagram">
  <svg viewBox="0 0 1000 600" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Agent team ownership and routing org chart">
    <defs>
      <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">
        <circle cx="1" cy="1" r="0.9" fill="#E3E2DC"/>
      </pattern>
    </defs>

    <!-- Paper-mask layer 1（強制） -->
    <rect width="100%" height="100%" fill="#f5f4ed"/>
    <!-- Paper-mask layer 2（可選 dotted overlay） -->
    <rect width="100%" height="100%" fill="url(#dots)" opacity="0.55"/>

    <!-- ===== REPORTING LINES（drop → bus → drop；對稱關係，無箭頭） ===== -->
    <!-- Root → tier-2 bus -->
    <line x1="500" y1="128" x2="500" y2="176" stroke="#504e49" stroke-width="1"/>
    <line x1="208" y1="176" x2="792" y2="176" stroke="#504e49" stroke-width="1"/>
    <line x1="208" y1="176" x2="208" y2="224" stroke="#504e49" stroke-width="1"/>
    <line x1="500" y1="176" x2="500" y2="224" stroke="#504e49" stroke-width="1"/>
    <line x1="792" y1="176" x2="792" y2="224" stroke="#504e49" stroke-width="1"/>
    <!-- Build pod → its 2 agents -->
    <line x1="208" y1="288" x2="208" y2="336" stroke="#504e49" stroke-width="1"/>
    <line x1="120" y1="336" x2="296" y2="336" stroke="#504e49" stroke-width="1"/>
    <line x1="120" y1="336" x2="120" y2="384" stroke="#504e49" stroke-width="1"/>
    <line x1="296" y1="336" x2="296" y2="384" stroke="#504e49" stroke-width="1"/>
    <!-- Review pod → its 2 agents -->
    <line x1="500" y1="288" x2="500" y2="336" stroke="#504e49" stroke-width="1"/>
    <line x1="448" y1="336" x2="600" y2="336" stroke="#504e49" stroke-width="1"/>
    <line x1="448" y1="336" x2="448" y2="384" stroke="#504e49" stroke-width="1"/>
    <line x1="600" y1="336" x2="600" y2="384" stroke="#504e49" stroke-width="1"/>
    <!-- Infra pod → its planned agent（虛線：路由尚未接線） -->
    <line x1="792" y1="288" x2="792" y2="384"
          stroke="#504e49" stroke-width="1" stroke-opacity="0.55" stroke-dasharray="4,3"/>

    <!-- ===== TIER 1 — Team Lead（front door，FOCAL，160） ===== -->
    <rect x="420" y="64" width="160" height="64" rx="6" fill="#f5f4ed"/>
    <rect data-role="focal"
          x="420" y="64" width="160" height="64" rx="6"
          fill="#EEF2F7" stroke="#1B365D" stroke-width="1.4"/>
    <rect x="428" y="72" width="28" height="12" rx="2"
          fill="transparent" stroke="#1B365D" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="442" y="81" fill="#1B365D" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">LEAD</text>
    <text x="500" y="104" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Team Lead</text>
    <text x="500" y="120" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace" text-anchor="middle">@lead</text>

    <!-- ===== TIER 2 — pod owners（144） ===== -->
    <rect x="136" y="224" width="144" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="136" y="224" width="144" height="64" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="144" y="232" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="158" y="241" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">POD</text>
    <text x="208" y="264" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Build Pod</text>
    <text x="208" y="280" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace" text-anchor="middle">#build-queue</text>

    <rect x="428" y="224" width="144" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="428" y="224" width="144" height="64" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="436" y="232" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="450" y="241" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">POD</text>
    <text x="500" y="264" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Review Pod</text>
    <text x="500" y="280" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace" text-anchor="middle">#review-queue</text>

    <rect x="720" y="224" width="144" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="720" y="224" width="144" height="64" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="728" y="232" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="742" y="241" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">POD</text>
    <text x="792" y="264" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Infra Pod</text>
    <text x="792" y="280" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace" text-anchor="middle">#infra-queue</text>

    <!-- ===== TIER 3 — agents（144） ===== -->
    <rect x="48" y="384" width="144" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="48" y="384" width="144" height="64" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="56" y="392" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="70" y="401" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">AGT</text>
    <text x="120" y="424" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Impl Agent</text>
    <text x="120" y="440" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace" text-anchor="middle">impl-agent</text>

    <rect x="224" y="384" width="144" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="224" y="384" width="144" height="64" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="232" y="392" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="246" y="401" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">AGT</text>
    <text x="296" y="424" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Test Agent</text>
    <text x="296" y="440" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace" text-anchor="middle">test-agent</text>

    <rect x="376" y="384" width="144" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="376" y="384" width="144" height="64" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="384" y="392" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="398" y="401" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">AGT</text>
    <text x="448" y="424" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Style Review</text>
    <text x="448" y="440" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace" text-anchor="middle">style-agent</text>

    <rect x="528" y="384" width="144" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="528" y="384" width="144" height="64" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="536" y="392" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="550" y="401" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">AGT</text>
    <text x="600" y="424" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Sec Review</text>
    <text x="600" y="440" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace" text-anchor="middle">sec-agent</text>

    <!-- Planned owner — 尚未接線（dashed，降不透明度，絕不省略） -->
    <rect x="720" y="384" width="144" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="720" y="384" width="144" height="64" rx="6"
          fill="#f1f0eb" stroke="#504e49" stroke-width="1"
          stroke-opacity="0.55" stroke-dasharray="4,3"/>
    <rect x="728" y="392" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="742" y="401" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">AGT</text>
    <text x="792" y="424" fill="#504e49" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Deploy Agent</text>
    <text x="792" y="440" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace" text-anchor="middle">needs setup</text>

    <!-- ===== LEGEND STRIP + escalation footer ===== -->
    <line x1="60" y1="540" x2="940" y2="540"
          stroke="#141413" stroke-opacity="0.10" stroke-width="0.8"/>
    <text x="60" y="560" fill="#504e49" font-size="8"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.14em">LEGEND</text>

    <rect x="140" y="552" width="16" height="12" rx="2"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <text x="160" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Owner (route wired)</text>

    <rect x="316" y="552" width="16" height="12" rx="2"
          fill="#EEF2F7" stroke="#1B365D" stroke-width="1.2"/>
    <text x="336" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Front door (ambiguous work)</text>

    <rect x="556" y="552" width="16" height="12" rx="2"
          fill="#f1f0eb" stroke="#504e49" stroke-width="1"
          stroke-opacity="0.55" stroke-dasharray="4,3"/>
    <text x="576" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Planned (not wired)</text>

    <line x1="740" y1="556" x2="760" y2="556" stroke="#504e49" stroke-width="1"/>
    <text x="768" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Reporting line</text>

    <text x="60" y="592" fill="#504e49" font-size="8"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.10em">ESCALATION · agent → pod owner → @lead (3-strike)</text>
  </svg>
  <figcaption>圖：agent 團隊職責路由（3 層 9 節點）：模糊工作一律先送 focal 前門 <span class="hl">@lead</span>；Deploy Agent 路由尚未接線（虛線）——下一步是補上 infra pod 的部署佇列再轉為實線。</figcaption>
</figure>
```
