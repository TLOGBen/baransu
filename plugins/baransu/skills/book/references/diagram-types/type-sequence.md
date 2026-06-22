---
name: sequence
status: complete
example: inline
---

## Contents

- Layout conventions
- Anti-patterns
- Examples

# Sequence

**Best for**: request / response flows、protocol handshakes、multi-actor interactions over time、API call trace、incident reconstruction.

## Layout conventions

- Layer 3 derived token: `lifeline-color` is precomputed from `--ink @ 0.30` into a solid hex (v1 ground truth `#b6b5af`) and must not appear in alpha-channel CSS-function form; for the computation see `references/design-token-resolver.md`.
- Actors are boxes laid out horizontally across the top; each actor drops a dashed vertical line as its lifeline, with the stroke set to the `lifeline-color` above, stroke-width=1 and stroke-dasharray="3,3" fixed.
- Messages are horizontal arrows between lifelines, **time runs top→down**; an activation bar is a thin rect on a lifeline (`w=8`, `--ink @ 0.06` fill, 0.8 hairline stroke) spanning the interval that actor holds control, with nested calls stacking inward.
- A self-message uses a short U-shaped loop back to the same lifeline, with the label on the right of the loop; a return message uses a dashed line, **colored the same as the line that initiated that call**.
- `--brand` may be used only on the main success response or a headline message — at most two in total — never colored on every line.

## Anti-patterns

- A message arrow points upward (time running backward).
  - *Why fails*: a sequence diagram's only invariant is that the y axis represents one-way time; an upward arrow negates the y-axis semantics, the reader can't judge causal order, and the entire diagram's grammar collapses.
- An activation bar with no close (left hanging).
  - *Why fails*: an activation bar means "this actor holds control during this interval"; leaving it unclosed declares that control was never handed back, which doesn't match the actual system behavior and also breaks the visual symmetry of nested calls.
- A label sitting on top of another lifeline.
  - *Why fails*: the lifeline is the visual skeleton; a label pressed on top makes the lifeline and the text consume each other, so the reader's y position drifts while scanning. Shorten the label or move its y into the gap between lifelines.

## Examples

Inline example below — 3-actor login protocol (Client → Server[focal] → DB), with a dashed lifeline, an activation bar, an alt branch (password mismatch), a return message (dashed line), and 1 sidenote box. The Server actor is marked `data-role="focal"`, all actor/sidenote widths follow the 2-step whitelist `{128, 160}`, and the alt frame uses `<path>` rather than rect to avoid a non-whitelist width.

```html
<figure class="diagram">
  <svg viewBox="0 0 1000 720" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Login protocol sequence diagram">
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

    <!-- Paper-mask Layer 1（強制） -->
    <rect width="100%" height="100%" fill="#f5f4ed"/>
    <!-- Paper-mask Layer 2（dotted overlay，可選） -->
    <rect width="100%" height="100%" fill="url(#dots)" opacity="0.55"/>

    <!-- ===== LIFELINES（dashed，stroke=#b6b5af 即 --ink @ 0.30 pre-flatten） ===== -->
    <line x1="160" y1="128" x2="160" y2="608"
          stroke="#b6b5af" stroke-width="1" stroke-dasharray="3,3"/>
    <line x1="500" y1="128" x2="500" y2="608"
          stroke="#b6b5af" stroke-width="1" stroke-dasharray="3,3"/>
    <line x1="840" y1="128" x2="840" y2="608"
          stroke="#b6b5af" stroke-width="1" stroke-dasharray="3,3"/>

    <!-- ===== ACTIVATION BARS（w=8 thin rect 即規格 §4.x） ===== -->
    <rect x="496" y="176" width="8" height="320" fill="#141413" fill-opacity="0.06"
          stroke="#504e49" stroke-width="0.8"/>
    <rect x="836" y="240" width="8" height="64" fill="#141413" fill-opacity="0.06"
          stroke="#504e49" stroke-width="0.8"/>

    <!-- ===== ALT BRANCH FRAME（path，非 rect，以避開 width whitelist） ===== -->
    <path d="M 96 384 L 904 384 L 904 480 L 96 480 Z"
          fill="none" stroke="#1B365D" stroke-width="0.8" stroke-dasharray="4,2"/>
    <rect x="96" y="384" width="128" height="16" rx="2"
          fill="#EEF2F7" stroke="#1B365D" stroke-width="0.8"/>
    <text x="160" y="396" fill="#1B365D" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">ALT</text>
    <text x="240" y="396" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace">[password matches]</text>

    <!-- ===== MESSAGES ===== -->
    <!-- M1 Client → Server: POST /login（external, link 色） -->
    <line x1="160" y1="176" x2="492" y2="176"
          stroke="#2D5A8A" stroke-width="1.2" marker-end="url(#arrow-link)"/>
    <text x="326" y="168" fill="#2D5A8A" font-size="10"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.06em">POST /login</text>

    <!-- M2 Server → DB: SELECT user（focal 主流） -->
    <line x1="504" y1="240" x2="832" y2="240"
          stroke="#1B365D" stroke-width="1.4" marker-end="url(#arrow-accent)"/>
    <text x="668" y="232" fill="#1B365D" font-size="10"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.06em">SELECT user</text>

    <!-- M3 DB → Server: row (return, dashed) -->
    <line x1="836" y1="304" x2="504" y2="304"
          stroke="#504e49" stroke-width="1" stroke-dasharray="4,3" marker-end="url(#arrow)"/>
    <text x="668" y="296" fill="#504e49" font-size="10"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">row + hash</text>

    <!-- M4 Server self-message: verify bcrypt -->
    <path d="M 504 352 C 540 352 540 372 504 372"
          fill="none" stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <text x="548" y="364" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace">verify bcrypt</text>

    <!-- M5（alt branch 內）Server → Client: 200 OK + JWT（focal flow） -->
    <line x1="496" y1="432" x2="168" y2="432"
          stroke="#1B365D" stroke-width="1.4" marker-end="url(#arrow-accent)"/>
    <text x="332" y="424" fill="#1B365D" font-size="10"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.06em">200 OK + JWT</text>

    <!-- M6（alt else 區）Server → Client: 401 Unauthorized -->
    <line x1="496" y1="492" x2="168" y2="492"
          stroke="#504e49" stroke-width="1.2" stroke-dasharray="4,3" marker-end="url(#arrow)"/>
    <text x="332" y="484" fill="#504e49" font-size="10"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">[else] 401 Unauthorized</text>

    <!-- ===== ACTORS（頂部 horizontal swimlane variant） ===== -->
    <!-- Client（160） -->
    <rect x="80" y="64" width="160" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="80" y="64" width="160" height="64" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="88" y="72" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="102" y="81" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">ACTOR</text>
    <text x="160" y="104" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Client</text>
    <text x="160" y="120" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">browser SPA</text>

    <!-- Server（160）— FOCAL -->
    <rect x="420" y="64" width="160" height="64" rx="6" fill="#f5f4ed"/>
    <rect data-role="focal"
          x="420" y="64" width="160" height="64" rx="6"
          fill="#EEF2F7" stroke="#1B365D" stroke-width="1.4"/>
    <rect x="428" y="72" width="28" height="12" rx="2"
          fill="transparent" stroke="#1B365D" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="442" y="81" fill="#1B365D" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">SVR</text>
    <text x="500" y="104" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Auth Server</text>
    <text x="500" y="120" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">FastAPI</text>

    <!-- DB（160） -->
    <rect x="760" y="64" width="160" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="760" y="64" width="160" height="64" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="768" y="72" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="782" y="81" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">DB</text>
    <text x="840" y="104" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Postgres</text>
    <text x="840" y="120" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">users table</text>

    <!-- Sidenote box（128，附帶說明 — 2 tier 多樣性） -->
    <rect x="80" y="544" width="128" height="48" rx="4" fill="#f5f4ed"/>
    <rect x="80" y="544" width="128" height="48" rx="4"
          fill="#f1f0eb" stroke="#504e49" stroke-width="0.8"
          stroke-dasharray="3,2"/>
    <rect x="88" y="552" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="102" y="561" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">NOTE</text>
    <text x="144" y="580" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">JWT TTL 15 min</text>

    <!-- ===== LEGEND STRIP ===== -->
    <line x1="60" y1="652" x2="940" y2="652"
          stroke="#141413" stroke-opacity="0.10" stroke-width="0.8"/>
    <text x="60" y="672" fill="#504e49" font-size="8"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.14em">LEGEND</text>
    <rect x="140" y="664" width="16" height="12" rx="2"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <text x="160" y="673" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Actor</text>
    <rect x="232" y="664" width="16" height="12" rx="2"
          fill="#EEF2F7" stroke="#1B365D" stroke-width="1.2"/>
    <text x="252" y="673" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Focal actor</text>
    <line x1="344" y1="668" x2="364" y2="668"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <text x="372" y="673" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Message</text>
    <line x1="448" y1="668" x2="468" y2="668"
          stroke="#1B365D" stroke-width="1.4" marker-end="url(#arrow-accent)"/>
    <text x="476" y="673" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Focal flow</text>
    <line x1="568" y1="668" x2="588" y2="668"
          stroke="#2D5A8A" stroke-width="1.2" marker-end="url(#arrow-link)"/>
    <text x="596" y="673" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">External HTTP</text>
    <line x1="680" y1="668" x2="700" y2="668"
          stroke="#504e49" stroke-width="1" stroke-dasharray="4,3" marker-end="url(#arrow)"/>
    <text x="708" y="673" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Return / dashed</text>
  </svg>
  <figcaption>圖：Login protocol sequence（Client → Server[focal] → DB；含 alt branch、activation bar、return message）。</figcaption>
</figure>
```
