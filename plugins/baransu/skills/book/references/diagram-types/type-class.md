---
name: class
status: complete
example: inline
---

## Contents

- Layout conventions
- Anti-patterns
- Examples

# Class

**Best for**: code entity structure / fields + methods compartments / inheritance + composition relations / interface contracts / module API surface.

## Layout conventions

- **Compartment node = one rect + hairline separators**: each class is ONE whitelist-width rect (144 or 160) divided internally by hairline `<line>` separators into title band / fields / methods. Internal separators are `<line>`s, never stacked sub-rects — one rect per class keeps the node-width rhythm intact and GATE-J trivially clean — sub-rects read as extra nodes and multiply the perceived node count.
- **Member lines are trimmed, not dumped**: 2–4 members per compartment max, 9px mono, trimmed to `name: Type` — never full signatures with parameter lists or generics — a signature dump turns the structure diagram back into source code; the reader came for shape, and the code itself is one click away.
- **Relationship vocabulary — one chevron, labeled lines**: inheritance = solid line + the standard chevron marker (`d="M2 1 L8 5 L2 9"`) pointing at the parent; composition / aggregation / implements = line style (solid vs dashed `stroke-dasharray="4,3"`) + a ≤14-char uppercase mono edge label (`EXTENDS` / `HAS-A` / `IMPL`) sitting on a small opaque mask rect — never filled UML diamond / hollow-triangle glyphs — the single stroked chevron across all 17 types is what makes consecutive diagrams read as one system; per-type glyph endings break that unity, and GATE-K forbids `<polygon>` markers outright.
- **Class budget ≤6–7 per diagram**: a deeper model splits along aggregate / module boundaries into sister diagrams, one per aggregate, each with its own focal class — past ~7 compartment nodes the relationship web stops being traceable — every added class multiplies edge crossings, not understanding.
- **Focal = the contract everyone depends on**: give the single `data-role="focal"` slot (tinted `#EEF2F7` fill + accent stroke) to the interface or base class the other classes converge on — the reader's first structural question is "what is the stable contract here" — contrast answers it before a single edge is traced.
- **Disambiguation vs `er`**: persistence / data relationships with cardinality (1:N, N:M, keys) → `type-er.md`; code structure that carries behavior (methods, interface contracts) → class. A box with fields and no methods is data, not a class.

## Anti-patterns

- **Full method signatures in compartments**
  - *Why fails*: parameter lists and return generics force text wider than the node-width whitelist allows and bury the one thing a member line must convey — that the member exists and what type it carries; the diagram becomes unreviewable source code.
- **More than 7 classes in one canvas**
  - *Why fails*: relationship edges grow roughly quadratically with class count; past ~7 nodes the crossings dominate and the reader traces lines with a finger instead of reading — split along aggregate seams instead.
- **Filled-glyph UML arrowheads (hollow triangle / filled diamond)**
  - *Why fails*: they break the one-chevron marker unity that lets 17 diagram types read as one system, they render inconsistently across print pipelines, and GATE-K rejects `<polygon>` markers anyway — line style + a mono edge label carries the same distinction legibly.
- **Mixing the data model into a behavior diagram**
  - *Why fails*: entity cardinality and code inheritance answer different questions; overlaying both doubles the edge vocabulary in one canvas so each half hides the other — persistence relationships route to `er`.
- **Every class equally emphasized**
  - *Why fails*: with no focal contract the reader cannot tell the stable interface from its replaceable implementations; the hierarchy reads as a flat list with lines, and the API surface the diagram exists to expose stays invisible.

## Examples

Inline example below — a 4-class Repository aggregate (Repository [interface, focal] ← SqlRepository / MemoryRepository via EXTENDS; UnitOfWork → Repository via dashed HAS-A). Complete `<defs>` with the dots pattern and exactly one chevron marker (`#arrow`, referenced by the inheritance riser, the HAS-A line, and both legend samples — defs ↔ refs bijective), two paper-mask layers, compartment nodes at the 2-step width whitelist `{144, 160}` divided by internal hairline `<line>` separators, uppercase mono edge labels on opaque mask rects (≤36px wide, below the node threshold), §4.5 type tags, 1 `data-role="focal"` node, a legend strip, and all `<rect>/<line>` geometry as multiples of 4.

```html
<figure class="diagram">
  <svg viewBox="0 0 1000 600" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Repository aggregate class structure">
    <defs>
      <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">
        <circle cx="1" cy="1" r="0.9" fill="#E3E2DC"/>
      </pattern>
      <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto">
        <path d="M2 1 L8 5 L2 9" fill="none" stroke="#504e49"
              stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      </marker>
    </defs>

    <!-- Paper-mask layer 1（強制） -->
    <rect width="100%" height="100%" fill="#f5f4ed"/>
    <!-- Paper-mask layer 2（可選 dotted overlay） -->
    <rect width="100%" height="100%" fill="url(#dots)" opacity="0.55"/>

    <!-- ===== RELATION EDGES（先畫線，後畫節點） ===== -->
    <!-- EXTENDS：children rise to a bus, one riser points at the parent -->
    <line x1="300" y1="320" x2="300" y2="264" stroke="#504e49" stroke-width="1.2"/>
    <line x1="556" y1="320" x2="556" y2="264" stroke="#504e49" stroke-width="1.2"/>
    <line x1="300" y1="264" x2="556" y2="264" stroke="#504e49" stroke-width="1.2"/>
    <line x1="500" y1="264" x2="500" y2="176"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <!-- HAS-A：dashed line + mono label, chevron at the owned side -->
    <line x1="756" y1="128" x2="580" y2="128"
          stroke="#504e49" stroke-width="1.2" stroke-dasharray="4,3"
          marker-end="url(#arrow)"/>

    <!-- ===== Repository — interface contract（FOCAL，160，compartments） ===== -->
    <rect x="420" y="80" width="160" height="96" rx="6" fill="#f5f4ed"/>
    <rect data-role="focal"
          x="420" y="80" width="160" height="96" rx="6"
          fill="#EEF2F7" stroke="#1B365D" stroke-width="1.4"/>
    <line x1="420" y1="112" x2="580" y2="112"
          stroke="#1B365D" stroke-opacity="0.35" stroke-width="0.8"/>
    <line x1="420" y1="144" x2="580" y2="144"
          stroke="#1B365D" stroke-opacity="0.35" stroke-width="0.8"/>
    <rect x="428" y="88" width="28" height="12" rx="2"
          fill="transparent" stroke="#1B365D" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="442" y="97" fill="#1B365D" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">IFC</text>
    <text x="516" y="104" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Repository</text>
    <text x="428" y="126" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace">entity: T</text>
    <text x="428" y="138" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace">spec: Query</text>
    <text x="428" y="158" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace">find: T[]</text>
    <text x="428" y="170" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace">save: void</text>

    <!-- ===== SqlRepository（144） ===== -->
    <rect x="228" y="320" width="144" height="96" rx="6" fill="#f5f4ed"/>
    <rect x="228" y="320" width="144" height="96" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <line x1="228" y1="352" x2="372" y2="352"
          stroke="#141413" stroke-opacity="0.20" stroke-width="0.8"/>
    <line x1="228" y1="384" x2="372" y2="384"
          stroke="#141413" stroke-opacity="0.20" stroke-width="0.8"/>
    <rect x="236" y="328" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="250" y="337" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">CLS</text>
    <text x="316" y="344" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">SqlRepository</text>
    <text x="236" y="370" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace">pool: Conn</text>
    <text x="236" y="398" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace">find: T[]</text>
    <text x="236" y="410" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace">save: void</text>

    <!-- ===== MemoryRepository（144） ===== -->
    <rect x="484" y="320" width="144" height="96" rx="6" fill="#f5f4ed"/>
    <rect x="484" y="320" width="144" height="96" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <line x1="484" y1="352" x2="628" y2="352"
          stroke="#141413" stroke-opacity="0.20" stroke-width="0.8"/>
    <line x1="484" y1="384" x2="628" y2="384"
          stroke="#141413" stroke-opacity="0.20" stroke-width="0.8"/>
    <rect x="492" y="328" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="506" y="337" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">CLS</text>
    <text x="572" y="344" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">MemoryRepository</text>
    <text x="492" y="370" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace">items: Map</text>
    <text x="492" y="398" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace">find: T[]</text>
    <text x="492" y="410" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace">save: void</text>

    <!-- ===== UnitOfWork（144） ===== -->
    <rect x="756" y="80" width="144" height="96" rx="6" fill="#f5f4ed"/>
    <rect x="756" y="80" width="144" height="96" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <line x1="756" y1="112" x2="900" y2="112"
          stroke="#141413" stroke-opacity="0.20" stroke-width="0.8"/>
    <line x1="756" y1="144" x2="900" y2="144"
          stroke="#141413" stroke-opacity="0.20" stroke-width="0.8"/>
    <rect x="764" y="88" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="778" y="97" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">CLS</text>
    <text x="844" y="104" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">UnitOfWork</text>
    <text x="764" y="126" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace">repos: Repo[]</text>
    <text x="764" y="158" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace">commit: void</text>

    <!-- ===== EDGE LABELS（不透明遮罩 + mono 標籤，蓋在線上） ===== -->
    <rect x="480" y="208" width="36" height="16" rx="2" fill="#f5f4ed"/>
    <text x="498" y="219" fill="#504e49" font-size="8"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.04em">EXTENDS</text>
    <rect x="648" y="120" width="36" height="16" rx="2" fill="#f5f4ed"/>
    <text x="666" y="131" fill="#504e49" font-size="8"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.04em">HAS-A</text>

    <!-- ===== LEGEND STRIP ===== -->
    <line x1="60" y1="516" x2="940" y2="516"
          stroke="#141413" stroke-opacity="0.10" stroke-width="0.8"/>
    <text x="60" y="536" fill="#504e49" font-size="8"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.14em">LEGEND</text>

    <rect x="140" y="528" width="16" height="12" rx="2"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <text x="160" y="537" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Class (title / fields / methods)</text>

    <rect x="356" y="528" width="16" height="12" rx="2"
          fill="#EEF2F7" stroke="#1B365D" stroke-width="1.2"/>
    <text x="376" y="537" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Focal contract</text>

    <line x1="504" y1="532" x2="524" y2="532"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <text x="532" y="537" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">EXTENDS (points at parent)</text>

    <line x1="716" y1="532" x2="736" y2="532"
          stroke="#504e49" stroke-width="1.2" stroke-dasharray="4,3"
          marker-end="url(#arrow)"/>
    <text x="744" y="537" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">HAS-A / IMPL (labeled)</text>
  </svg>
  <figcaption>圖：Repository 契約的類別結構（4 類別、EXTENDS／HAS-A 兩種關係）：兩個實作可互換而 UnitOfWork 只依賴介面；超過 7 個類別時沿 aggregate 邊界拆成姊妹圖，而不是縮小塞進同一張。</figcaption>
</figure>
```
