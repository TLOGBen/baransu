---
name: state
status: complete
example: inline
---

# State Machine

**Best for**: finite-state logic — order status、auth state、connection lifecycle、form wizard、job queue status.

## Layout conventions

- Layer 3 derived token: `state-active` = `--brand` (v1 ground truth `#1B365D`), `state-inactive` = `--ink @ 0.05` (v1 ground truth `#f1f0eb`); both are precomputed into solid hex and must not appear in alpha-channel CSS-function form — see `references/design-token-resolver.md`.
- States are rounded rectangles (`rx=8`) with the label in `--font-sans`; start = a filled `--ink` dot (`r=6`), end = a ringed dot (outer `r=8` outline, inner filled `r=5`).
- Transitions are curved arrows with the label in `--font-mono`, formatted `event [guard] / action`, omitting fields that aren't needed; a self-loop wraps back over the top of the state.
- Align the main flow direction along left→right or top→down; rearrange until transitions don't cross before you consider drawing.
- `--brand` / `state-active` may only go on the single state the reader should focus on most — usually the error state or the happy completion, pick one of the two.

## Anti-patterns

- The transition count exceeds `states × 2`.
  - *Why fails*: empirically this means you're forcing two independent state machines onto one canvas; a hairball appears visually, the reader can't trace any single path, and you should split it into two diagrams.
- A "from any state" transition drawn as one line from every state to the same target (e.g. everything → Error).
  - *Why fails*: the N duplicate lines carve up the canvas, but the meaning is only the single quantifier "any"; replace them with one annotation (`* → Error on timeout`) so visual density matches information density.
- An unlabeled transition.
  - *Why fails*: a state machine's core question is "under what condition does it jump from A to B"; dropping the label throws away the one question this diagram answers, and the remaining topology could just as well be shown as a list.

## Examples

Inline example below — 5-state connection lifecycle (`idle → connecting → active[focal] → closing → closed`, with retry / timeout return edges). A complete `<defs>` with three chevron markers, two paper-mask layers, 1 `data-role="focal"` node, the 2-step node-width whitelist `{128, 144}`, a legend strip, and all `x/y/width/height` as multiples of 4.

```html
<figure class="diagram">
  <svg viewBox="0 0 1000 600" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Connection lifecycle state machine">
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

    <!-- ===== START / END markers ===== -->
    <!-- Start solid dot -->
    <circle cx="80" cy="240" r="6" fill="#141413"/>
    <!-- End ringed dot -->
    <circle cx="920" cy="240" r="8" fill="none" stroke="#141413" stroke-width="1.2"/>
    <circle cx="920" cy="240" r="5" fill="#141413"/>

    <!-- ===== EDGES（先畫線） ===== -->
    <!-- start → idle -->
    <line x1="88" y1="240" x2="128" y2="240"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <!-- idle → connecting -->
    <line x1="272" y1="240" x2="320" y2="240"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <!-- connecting → active (focal flow, accent) -->
    <line x1="448" y1="240" x2="488" y2="240"
          stroke="#1B365D" stroke-width="1.4" marker-end="url(#arrow-accent)"/>
    <!-- active → closing (focal exit, accent) -->
    <line x1="632" y1="240" x2="672" y2="240"
          stroke="#1B365D" stroke-width="1.4" marker-end="url(#arrow-accent)"/>
    <!-- closed → end (L-shape: right from closed to end-ring's x, then up) -->
    <line x1="848" y1="392" x2="920" y2="392"
          stroke="#504e49" stroke-width="1.2"/>
    <line x1="920" y1="392" x2="920" y2="252"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <text x="928" y="328" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="start">→ end</text>

    <!-- retry edge: connecting → idle (curved upper) -->
    <path d="M 360 224 C 360 160, 232 160, 232 224"
          fill="none" stroke="#2D5A8A" stroke-width="1.2"
          stroke-dasharray="4 3" marker-end="url(#arrow-link)"/>
    <text x="296" y="156" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">on connect_failed / retry</text>

    <!-- timeout edge: active → closing (label) -->
    <text x="652" y="228" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">after idle_timeout</text>

    <!-- on_open label -->
    <text x="468" y="228" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">on_open</text>

    <!-- transition: idle → connecting label -->
    <text x="296" y="228" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">connect()</text>

    <!-- ===== NODES — 寬白名單 2 檔 {128, 144}；focal 用 144 ===== -->
    <!-- idle (128) -->
    <rect x="128" y="208" width="128" height="64" rx="8" fill="#f5f4ed"/>
    <rect x="128" y="208" width="128" height="64" rx="8"
          fill="#f1f0eb" stroke="#504e49" stroke-width="1"/>
    <rect x="136" y="216" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="150" y="225" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">STATE</text>
    <text x="192" y="248" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">idle</text>
    <text x="192" y="264" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">waiting</text>

    <!-- connecting (128) -->
    <rect x="320" y="208" width="128" height="64" rx="8" fill="#f5f4ed"/>
    <rect x="320" y="208" width="128" height="64" rx="8"
          fill="#f1f0eb" stroke="#504e49" stroke-width="1"/>
    <rect x="328" y="216" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="342" y="225" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">STATE</text>
    <text x="384" y="248" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">connecting</text>
    <text x="384" y="264" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">handshake</text>

    <!-- active — FOCAL (144) -->
    <rect x="488" y="208" width="144" height="64" rx="8" fill="#f5f4ed"/>
    <rect data-role="focal"
          x="488" y="208" width="144" height="64" rx="8"
          fill="#EEF2F7" stroke="#1B365D" stroke-width="1.4"/>
    <rect x="496" y="216" width="28" height="12" rx="2"
          fill="transparent" stroke="#1B365D" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="510" y="225" fill="#1B365D" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">FOCAL</text>
    <text x="560" y="248" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">active</text>
    <text x="560" y="264" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">streaming</text>

    <!-- closing (128) -->
    <rect x="672" y="208" width="128" height="64" rx="8" fill="#f5f4ed"/>
    <rect x="672" y="208" width="128" height="64" rx="8"
          fill="#f1f0eb" stroke="#504e49" stroke-width="1"/>
    <rect x="680" y="216" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="694" y="225" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">STATE</text>
    <text x="736" y="248" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">closing</text>
    <text x="736" y="264" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">drain</text>

    <!-- closed (128) -->
    <rect x="720" y="360" width="128" height="64" rx="8" fill="#f5f4ed"/>
    <rect x="720" y="360" width="128" height="64" rx="8"
          fill="#f1f0eb" stroke="#504e49" stroke-width="1"/>
    <rect x="728" y="368" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="742" y="377" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">STATE</text>
    <text x="784" y="400" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">closed</text>
    <text x="784" y="416" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">terminal</text>

    <!-- closing → closed redirected to lower row -->
    <line x1="784" y1="272" x2="784" y2="356"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <text x="816" y="320" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">on_close</text>

    <!-- ===== LEGEND STRIP ===== -->
    <line x1="60" y1="540" x2="940" y2="540"
          stroke="#141413" stroke-opacity="0.10" stroke-width="0.8"/>
    <text x="60" y="560" fill="#504e49" font-size="8"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.14em">LEGEND</text>

    <rect x="140" y="552" width="16" height="12" rx="2"
          fill="#f1f0eb" stroke="#504e49" stroke-width="1"/>
    <text x="160" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">State</text>

    <rect x="220" y="552" width="16" height="12" rx="2"
          fill="#EEF2F7" stroke="#1B365D" stroke-width="1.2"/>
    <text x="240" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Focal state</text>

    <line x1="360" y1="556" x2="380" y2="556"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <text x="388" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Transition</text>

    <line x1="500" y1="556" x2="520" y2="556"
          stroke="#1B365D" stroke-width="1.4" marker-end="url(#arrow-accent)"/>
    <text x="528" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Focal flow</text>

    <line x1="640" y1="556" x2="660" y2="556"
          stroke="#2D5A8A" stroke-width="1.2" stroke-dasharray="4 3" marker-end="url(#arrow-link)"/>
    <text x="668" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Retry / loop</text>
  </svg>
  <figcaption>圖：5-state connection lifecycle（idle → connecting → active[focal] → closing → closed），含 retry 與 idle_timeout transition。</figcaption>
</figure>
```
