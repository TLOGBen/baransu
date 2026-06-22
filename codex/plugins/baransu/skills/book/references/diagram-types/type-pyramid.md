---
name: pyramid
status: complete
example: inline
---

## Contents

- Layout conventions
- Anti-patterns
- Examples

# Pyramid / Funnel

**Best for**: hierarchy of needs, prioritization rank, value pyramid, conversion funnel, content importance stack.

## Layout conventions

- **Pick one orientation, never mix**: pyramid (apex up) = the top is the most important / rarest / most valuable, the bottom is the most foundational; funnel (apex down) = the bottom is conversion (smallest group), the top is the widest audience.
- 4–6 levels max; the visual is built from a `<path>` trapezoid contour + a `<rect>` callout per level (**Kami spec forbids `<polygon>`**, see the Examples section below), with **uniform level height** (56–72px); width decreases linearly from base to apex (pyramid) or top to bottom (funnel) — when showing real funnel data the width must be honest (proportional to count / percentage).
- Three pieces of info per level: name label centered, `--font-sans` 12–14px 600; sublabel below or beside the name, `--font-mono` 9–10px; optional side annotation on the right or left (the funnel's drop-off percentage, e.g. `−40%`).
- 1px hairline divider between levels, outer contour 1px `--color-muted` or `--ink`; fill is one of two options: a subtle gradient tint **or** all paper-2 + hairline dividers; `--brand` is applied only to a **single level** (the pyramid's apex, the funnel's conversion level, or a key bottleneck).

## Anti-patterns

- More than 7 levels.
  - *Why fails*: once there are many trapezoid levels the vertical space per level gets squeezed too tight to fit a label, and the reader struggles to count the levels at a glance; compress (merge semantically close levels) or split into two diagrams.
- Using a pyramid for non-hierarchical data (pure categorization, parallel comparison).
  - *Why fails*: a pyramid's visual promise is "an up/down rank relationship exists" (rarity / importance / scale); using it on rankless data misleads the reader into building a hierarchy that doesn't exist — use a tree or bar chart instead.
- Faking the width (disguising unequal drop-offs as an equal-width taper).
  - *Why fails*: a funnel's only quantitative promise is "width reflects the actual funnel proportions"; an equal-width taper visually flattens the real conversion drop, the reader can't see which stage loses the most, and the diagram directly violates the honest-data-viz principle.

## Examples

Inline example below — 5-level value pyramid (Vision[focal] / Strategy / Tactics / Execution / Foundation). **Kami spec forbids `<polygon>`**, so the trapezoid visual is built from a `<path>` outer contour + 5 `<rect>` level callouts (widths alternating between the {128, 160} two-value allowlist); the node width allowlist still holds. Complete `<defs>` with three chevron markers, two paper-mask layers, 1 `data-role="focal"` node (apex Vision), all `x/y/width/height` as multiples of 4, and a legend strip.

```html
<figure class="diagram">
  <svg viewBox="0 0 1000 600" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="5-level value pyramid with focal Vision apex">
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

    <!-- ===== PYRAMID SILHOUETTE（path，非 polygon）===== -->
    <!-- 外輪廓三角形：apex (500, 96) → base-left (200, 460) → base-right (800, 460) → close -->
    <path d="M 500 96 L 200 460 L 800 460 Z"
          fill="#f1f0eb" stroke="#504e49" stroke-width="1"/>

    <!-- ===== LEVEL DIVIDERS（4 條 hairline 內部分層） ===== -->
    <line x1="440" y1="168" x2="560" y2="168"
          stroke="#141413" stroke-opacity="0.12" stroke-width="0.8"/>
    <line x1="380" y1="240" x2="620" y2="240"
          stroke="#141413" stroke-opacity="0.12" stroke-width="0.8"/>
    <line x1="320" y1="312" x2="680" y2="312"
          stroke="#141413" stroke-opacity="0.12" stroke-width="0.8"/>
    <line x1="260" y1="384" x2="740" y2="384"
          stroke="#141413" stroke-opacity="0.12" stroke-width="0.8"/>

    <!-- ===== LEVEL CALLOUTS（5 rect 節點，alternating {128, 160}，max 2 tiers） ===== -->
    <!-- L5 Apex: Vision — FOCAL（128，最窄符合 apex 視覺） -->
    <rect x="436" y="108" width="128" height="32" rx="6" fill="#f5f4ed"/>
    <rect data-role="focal"
          x="436" y="108" width="128" height="32" rx="6"
          fill="#EEF2F7" stroke="#1B365D" stroke-width="1.4"/>
    <rect x="444" y="112" width="28" height="12" rx="2"
          fill="transparent" stroke="#1B365D" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="458" y="121" fill="#1B365D" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">L5</text>
    <text x="500" y="130" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Vision</text>

    <!-- L4: Strategy（160） -->
    <rect x="420" y="184" width="160" height="32" rx="6" fill="#f5f4ed"/>
    <rect x="420" y="184" width="160" height="32" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="428" y="188" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="442" y="197" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">L4</text>
    <text x="500" y="206" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Strategy</text>

    <!-- L3: Tactics（128） -->
    <rect x="436" y="256" width="128" height="32" rx="6" fill="#f5f4ed"/>
    <rect x="436" y="256" width="128" height="32" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="444" y="260" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="458" y="269" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">L3</text>
    <text x="500" y="278" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Tactics</text>

    <!-- L2: Execution（160） -->
    <rect x="420" y="328" width="160" height="32" rx="6" fill="#f5f4ed"/>
    <rect x="420" y="328" width="160" height="32" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="428" y="332" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="442" y="341" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">L2</text>
    <text x="500" y="350" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Execution</text>

    <!-- L1: Foundation（128） -->
    <rect x="436" y="400" width="128" height="32" rx="6" fill="#f5f4ed"/>
    <rect x="436" y="400" width="128" height="32" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="444" y="404" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="458" y="413" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">L1</text>
    <text x="500" y="422" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Foundation</text>

    <!-- ===== UPWARD-VALUE ARROW（左外緣，accent，指向 focal apex） ===== -->
    <line x1="160" y1="440" x2="160" y2="120"
          stroke="#1B365D" stroke-width="1.4" marker-end="url(#arrow-accent)"/>
    <text x="148" y="284" fill="#1B365D" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="end" letter-spacing="0.08em">value ↑</text>

    <!-- ===== BREADTH ANNOTATION（右外緣，普通箭頭，向下） ===== -->
    <line x1="840" y1="120" x2="840" y2="440"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <text x="852" y="284" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.08em">breadth ↓</text>

    <!-- ===== LEGEND STRIP ===== -->
    <line x1="60" y1="540" x2="940" y2="540"
          stroke="#141413" stroke-opacity="0.10" stroke-width="0.8"/>
    <text x="60" y="560" fill="#504e49" font-size="8"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.14em">LEGEND</text>

    <rect x="140" y="552" width="16" height="12" rx="2"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <text x="160" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Level callout</text>

    <rect x="280" y="552" width="16" height="12" rx="2"
          fill="#EEF2F7" stroke="#1B365D" stroke-width="1.2"/>
    <text x="300" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Focal apex</text>

    <line x1="420" y1="556" x2="440" y2="556"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <text x="448" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Breadth axis</text>

    <line x1="560" y1="556" x2="580" y2="556"
          stroke="#1B365D" stroke-width="1.4" marker-end="url(#arrow-accent)"/>
    <text x="588" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Value axis</text>

    <line x1="700" y1="556" x2="720" y2="556"
          stroke="#2D5A8A" stroke-width="1.2" marker-end="url(#arrow-link)"/>
    <text x="728" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Cross-pyramid ref</text>
  </svg>
  <figcaption>圖：5-level value pyramid（Vision[focal] / Strategy / Tactics / Execution / Foundation）。梯形外輪廓走 `<path>`（無 polygon），階層 callout 寬交替 {128, 160}。</figcaption>
</figure>
```
