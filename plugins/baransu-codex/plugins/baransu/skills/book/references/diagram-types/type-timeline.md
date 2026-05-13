---
name: timeline
status: complete
example: inline
---

# Timeline

**Best for**: release 歷史、project milestone、事故時間線（incident timeline）、roadmap、changelog 視覺化。

## Layout conventions

- 中央一條 horizontal hairline baseline（`stroke-width=1`，`--color-muted`）；tick marks 落在 time boundary（quarters / months / sprints），下方 date label 用 `--font-mono`。
- Event 為 baseline 上 small filled circle（`r=4`，`--ink`）；label 上下交替排列以避免碰撞，靠 1px hairline drop 連回 circle。
- Major milestone 為 `--brand` 顏色的 circle（`r=6`）+ `--font-sans` bold label；一張圖只 highlight 真正的「里程碑」，不可每個 event 都標 brand。
- 時間刻度必須誠實：間隔不等時 circle 間距也必須不等；密度過高的區段顯式做 axis break，不為美觀偽造 linear spacing。

## Anti-patterns

- 把時間上不等距的 event 等距排列。
  - *Why fails*：timeline 唯一的語意承諾就是「x 軸代表時間」；等距排列把不等變相等，讀者會誤判 release cadence 或事故頻率，圖直接說謊。
- 缺少 axis 單位 label（「這是 day / week / quarter？」）。
  - *Why fails*：timeline 的 tick 數字（如 `2024-Q1`）必須有單位 context，否則 `Q1` 跟 `Sprint 1` 在視覺上長一樣；缺單位 = reader 必須回 prose 推測，違背 diagram 自我承載的原則。
- 多個 label 沒做垂直 offset，全擠在 baseline 一側。
  - *Why fails*：相鄰 event 的 label 會互相 overlap 到看不清字；timeline 規範 label 必須上下交替排列正是為了在 1D 空間用 2D 來解決碰撞，省略此 offset 等於放棄可讀性。

## Examples

Inline example below — 6-milestone release timeline（`v0.1 → v0.5 → v1.0[focal] → v1.1 → v1.2 → v2.0`），horizontal baseline + alternating date / label，chevron markers 在每個 milestone connector 上。完整 `<defs>` 三 chevron marker、兩層 paper-mask、1 個 `data-role="focal"` milestone（v1.0 release）、節點寬 2 檔白名單 `{128, 160}`、legend strip、所有 `x/y/width/height` 為 4 的倍數。Baseline tick circle 屬於 sub-primitive（< 40px），不計入 node-width 白名單。

```html
<figure class="diagram">
  <svg viewBox="0 0 1000 600" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Project release timeline 2023-2026">
    <defs>
      <pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse">
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

    <!-- ===== AXIS BASELINE ===== -->
    <line x1="80" y1="304" x2="920" y2="304"
          stroke="#504e49" stroke-opacity="0.6" stroke-width="1"/>
    <text x="60" y="308" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="end">2023</text>
    <text x="940" y="308" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace">2026</text>
    <text x="500" y="328" fill="#504e49" font-size="8"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.14em">RELEASE TIMELINE (quarters)</text>

    <!-- ===== MILESTONE CONNECTOR ARROWS（chevron between events） ===== -->
    <!-- v0.1 → v0.5 -->
    <line x1="156" y1="304" x2="220" y2="304"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <!-- v0.5 → v1.0 (accent, leads into focal) -->
    <line x1="320" y1="304" x2="380" y2="304"
          stroke="#1B365D" stroke-width="1.4" marker-end="url(#arrow-accent)"/>
    <!-- v1.0 → v1.1 (accent, leaves focal) -->
    <line x1="500" y1="304" x2="556" y2="304"
          stroke="#1B365D" stroke-width="1.4" marker-end="url(#arrow-accent)"/>
    <!-- v1.1 → v1.2 -->
    <line x1="640" y1="304" x2="700" y2="304"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <!-- v1.2 → v2.0 (external major bump, link) -->
    <line x1="780" y1="304" x2="840" y2="304"
          stroke="#2D5A8A" stroke-width="1.2" marker-end="url(#arrow-link)"/>

    <!-- ===== MILESTONE NODES (rect cards above/below baseline) ===== -->
    <!-- v0.1 (128, above) -->
    <text x="92" y="232" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace">2023-Q2</text>
    <rect x="92" y="240" width="128" height="48" rx="6" fill="#f5f4ed"/>
    <rect x="92" y="240" width="128" height="48" rx="6"
          fill="#faf9f5" stroke="#504e49" stroke-width="1"/>
    <rect x="100" y="248" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="114" y="257" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">REL</text>
    <text x="156" y="276" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">v0.1 alpha</text>
    <line x1="156" y1="288" x2="156" y2="300"
          stroke="#504e49" stroke-opacity="0.5" stroke-width="0.8"/>
    <circle cx="156" cy="304" r="4" fill="#141413"/>

    <!-- v0.5 (128, below) -->
    <circle cx="284" cy="304" r="4" fill="#141413"/>
    <line x1="284" y1="308" x2="284" y2="320"
          stroke="#504e49" stroke-opacity="0.5" stroke-width="0.8"/>
    <rect x="220" y="320" width="128" height="48" rx="6" fill="#f5f4ed"/>
    <rect x="220" y="320" width="128" height="48" rx="6"
          fill="#faf9f5" stroke="#504e49" stroke-width="1"/>
    <rect x="228" y="328" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="242" y="337" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">REL</text>
    <text x="284" y="356" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">v0.5 beta</text>
    <text x="284" y="384" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">2024-Q1</text>

    <!-- v1.0 — FOCAL (160, above) -->
    <text x="380" y="184" fill="#1B365D" font-size="9" font-weight="600"
          font-family="'Geist Mono', ui-monospace, monospace">2024-Q4</text>
    <rect x="380" y="192" width="160" height="56" rx="6" fill="#f5f4ed"/>
    <rect data-role="focal"
          x="380" y="192" width="160" height="56" rx="6"
          fill="#EEF2F7" stroke="#1B365D" stroke-width="1.4"/>
    <rect x="388" y="200" width="28" height="12" rx="2"
          fill="transparent" stroke="#1B365D" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="402" y="209" fill="#1B365D" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">GA</text>
    <text x="460" y="228" fill="#141413" font-size="14" font-weight="700"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">v1.0 release</text>
    <text x="460" y="244" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">general availability</text>
    <line x1="460" y1="248" x2="460" y2="300"
          stroke="#1B365D" stroke-opacity="0.6" stroke-width="1"/>
    <circle cx="460" cy="304" r="6" fill="#1B365D"/>

    <!-- v1.1 (128, below) -->
    <circle cx="600" cy="304" r="4" fill="#141413"/>
    <line x1="600" y1="308" x2="600" y2="320"
          stroke="#504e49" stroke-opacity="0.5" stroke-width="0.8"/>
    <rect x="536" y="320" width="128" height="48" rx="6" fill="#f5f4ed"/>
    <rect x="536" y="320" width="128" height="48" rx="6"
          fill="#faf9f5" stroke="#504e49" stroke-width="1"/>
    <rect x="544" y="328" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="558" y="337" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">REL</text>
    <text x="600" y="356" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">v1.1 patch</text>
    <text x="600" y="384" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">2025-Q2</text>

    <!-- v1.2 (128, above) -->
    <text x="676" y="232" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace">2025-Q4</text>
    <rect x="676" y="240" width="128" height="48" rx="6" fill="#f5f4ed"/>
    <rect x="676" y="240" width="128" height="48" rx="6"
          fill="#faf9f5" stroke="#504e49" stroke-width="1"/>
    <rect x="684" y="248" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="698" y="257" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">REL</text>
    <text x="740" y="276" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">v1.2 minor</text>
    <line x1="740" y1="288" x2="740" y2="300"
          stroke="#504e49" stroke-opacity="0.5" stroke-width="0.8"/>
    <circle cx="740" cy="304" r="4" fill="#141413"/>

    <!-- v2.0 (128, below) -->
    <circle cx="864" cy="304" r="4" fill="#141413"/>
    <line x1="864" y1="308" x2="864" y2="320"
          stroke="#504e49" stroke-opacity="0.5" stroke-width="0.8"/>
    <rect x="800" y="320" width="128" height="48" rx="6" fill="#f5f4ed"/>
    <rect x="800" y="320" width="128" height="48" rx="6"
          fill="#faf9f5" stroke="#2D5A8A" stroke-width="1"/>
    <rect x="808" y="328" width="28" height="12" rx="2"
          fill="transparent" stroke="#2D5A8A" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="822" y="337" fill="#2D5A8A" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">NEXT</text>
    <text x="864" y="356" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">v2.0 plan</text>
    <text x="864" y="384" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">2026-Q3</text>

    <!-- ===== LEGEND STRIP ===== -->
    <line x1="60" y1="540" x2="940" y2="540"
          stroke="#141413" stroke-opacity="0.10" stroke-width="0.8"/>
    <text x="60" y="560" fill="#504e49" font-size="8"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.14em">LEGEND</text>

    <circle cx="148" cy="556" r="4" fill="#141413"/>
    <text x="160" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Minor release</text>

    <circle cx="280" cy="556" r="6" fill="#1B365D"/>
    <text x="292" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Focal milestone</text>

    <line x1="420" y1="556" x2="440" y2="556"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <text x="448" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Step</text>

    <line x1="520" y1="556" x2="540" y2="556"
          stroke="#1B365D" stroke-width="1.4" marker-end="url(#arrow-accent)"/>
    <text x="548" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Into / out of focal</text>

    <line x1="680" y1="556" x2="700" y2="556"
          stroke="#2D5A8A" stroke-width="1.2" marker-end="url(#arrow-link)"/>
    <text x="708" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Major bump (next era)</text>
  </svg>
  <figcaption>圖：6-milestone release timeline（v0.1 → v0.5 → v1.0[focal] → v1.1 → v1.2 → v2.0），focal 標示 GA release。</figcaption>
</figure>
```
