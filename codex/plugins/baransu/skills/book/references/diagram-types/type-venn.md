---
name: venn
status: complete
example: inline
---

## Contents

- Layout conventions
- Anti-patterns
- Examples

# Venn / Set Overlap

**Best for**: concept / domain intersections, shared attributes across categories, "where A meets B", ikigai-style frame (desirable × feasible × viable), locating a sweet spot.

## Layout conventions

- **Prefer 2 or 3 circles**, avoid 4+ (unreadable — switch to matrix); circle stroke 1px hairline, one color per set (`--ink` / `--color-muted` / soft).
- Circle fill uses an extremely low-opacity tint (`--ink @ 0.04` or `--color-muted @ 0.05`), so the overlap region naturally builds a darker ground; radii are equal when sets are comparable in size and scaled proportionally when the difference is meaningful — **do not fake equal sizes for aesthetics**.
- **Place set labels outside the circles**, never crossing a stroke; `--font-sans` 12–14px 600 for the set name, optional `--font-mono` 9px sublabel.
- **Intersection labels** go inside the overlap region, `--font-sans` 12px 600 centered; when the overlap is too small, pull the label out to clear space with a leader line; `--brand` is applied only to the **single focal intersection** (sweet spot), optionally as a brand stroke or clipPath-bounded brand tint fill; circle centers and radii are all divisible by 4.

## Anti-patterns

- Regions left unlabeled (the reader can't tell which circle is which set).
  - *Why fails*: the entire value of a venn is the meaning carried by "set name + intersection label"; without labels only the topology remains (two overlapping circles) and the reader must go back to the prose to work out what each circle represents — the diagram is effectively useless.
- Circles that should overlap don't (drawn tangent or separate).
  - *Why fails*: the visual promise of a venn is "an overlap region exists = elements belong to multiple sets at once"; no overlap declares the intersection empty, directly contradicting the sweet-spot meaning you're trying to convey.
- Sets that are clearly different in size drawn as equal circles.
  - *Why fails*: circle area maps to set scale in the reader's subconscious; equal circles mislead the judgment of relative size — e.g. putting a 1% edge case and an 80% mainstream scenario on equal circles makes the diagram lie about magnitude.

## Examples

Inline example below — classic 3-circle Venn (ikigai-style: Desirable × Feasible × Viable), all 7 regions present (3 single + 3 double + 1 triple intersection at the center [focal]). `<circle>` is not on the rect width allowlist; the 128-wide title callout `<rect>` at the top satisfies the allowlist. Complete `<defs>` with three chevron markers (all referenced in the legend), two paper-mask layers, 1 `data-role="focal"` node (triple-intersection callout), and all `cx/cy/r` and `x/y/width/height` as multiples of 4.

```html
<figure class="diagram">
  <svg viewBox="0 0 1000 600" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="3-circle Venn — ikigai sweet spot">
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

    <!-- ===== TITLE CALLOUT（128-wide rect 對齊白名單） ===== -->
    <rect x="436" y="56" width="128" height="32" rx="6" fill="#f5f4ed"/>
    <rect x="436" y="56" width="128" height="32" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="444" y="60" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="458" y="69" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">VENN</text>
    <text x="500" y="78" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Ikigai frame</text>

    <!-- ===== 3 CIRCLES（hairline stroke + extremely low-opacity tint） ===== -->
    <!-- Set A：Desirable（top-left） -->
    <circle cx="420" cy="288" r="140"
            fill="#141413" fill-opacity="0.04"
            stroke="#504e49" stroke-width="1"/>
    <!-- Set B：Feasible（top-right） -->
    <circle cx="580" cy="288" r="140"
            fill="#141413" fill-opacity="0.04"
            stroke="#504e49" stroke-width="1"/>
    <!-- Set C：Viable（bottom） -->
    <circle cx="500" cy="400" r="140"
            fill="#141413" fill-opacity="0.04"
            stroke="#504e49" stroke-width="1"/>

    <!-- ===== SET LABELS（位於圓外，絕不跨 stroke） ===== -->
    <text x="280" y="184" fill="#141413" font-size="13" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Desirable</text>
    <text x="280" y="200" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">users want it</text>

    <text x="720" y="184" fill="#141413" font-size="13" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Feasible</text>
    <text x="720" y="200" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">we can build it</text>

    <text x="500" y="568" fill="#141413" font-size="13" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Viable</text>
    <text x="500" y="584" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">business sustains it</text>

    <!-- ===== PAIRWISE INTERSECTION LABELS（3 double regions） ===== -->
    <!-- A ∩ B（top） -->
    <text x="500" y="232" fill="#141413" font-size="11" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Mission</text>
    <text x="500" y="248" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">A ∩ B</text>

    <!-- A ∩ C（left） -->
    <text x="412" y="372" fill="#141413" font-size="11" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Passion</text>
    <text x="412" y="388" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">A ∩ C</text>

    <!-- B ∩ C（right） -->
    <text x="592" y="372" fill="#141413" font-size="11" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Vocation</text>
    <text x="592" y="388" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">B ∩ C</text>

    <!-- ===== TRIPLE INTERSECTION — FOCAL via data-role on backdrop rect ===== -->
    <!-- Focal node 為一個小型 rect callout（width=128 仍於白名單），停在 triple 中心 -->
    <rect x="436" y="332" width="128" height="32" rx="6" fill="#f5f4ed"/>
    <rect data-role="focal"
          x="436" y="332" width="128" height="32" rx="6"
          fill="#EEF2F7" stroke="#1B365D" stroke-width="1.4"/>
    <rect x="444" y="336" width="28" height="12" rx="2"
          fill="transparent" stroke="#1B365D" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="458" y="345" fill="#1B365D" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">FIT</text>
    <text x="500" y="356" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Ikigai</text>

    <!-- ===== LEGEND STRIP ===== -->
    <line x1="60" y1="540" x2="940" y2="540"
          stroke="#141413" stroke-opacity="0.10" stroke-width="0.8"/>
    <text x="60" y="560" fill="#504e49" font-size="8"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.14em">LEGEND</text>

    <rect x="140" y="552" width="16" height="12" rx="2"
          fill="#141413" fill-opacity="0.04"
          stroke="#504e49" stroke-width="1"/>
    <text x="160" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Set circle</text>

    <rect x="280" y="552" width="16" height="12" rx="2"
          fill="#EEF2F7" stroke="#1B365D" stroke-width="1.2"/>
    <text x="300" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Focal sweet spot</text>

    <line x1="420" y1="556" x2="440" y2="556"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <text x="448" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Leader line</text>

    <line x1="560" y1="556" x2="580" y2="556"
          stroke="#1B365D" stroke-width="1.4" marker-end="url(#arrow-accent)"/>
    <text x="588" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Focal callout</text>

    <line x1="700" y1="556" x2="720" y2="556"
          stroke="#2D5A8A" stroke-width="1.2" marker-end="url(#arrow-link)"/>
    <text x="728" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Cross-frame ref</text>
  </svg>
  <figcaption>圖：3-circle Venn — ikigai frame（Desirable × Feasible × Viable），triple-intersection [focal] 為 Ikigai sweet spot。</figcaption>
</figure>
```
