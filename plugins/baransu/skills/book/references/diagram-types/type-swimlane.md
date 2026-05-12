---
name: swimlane
status: complete
example: inline
---

# Swimlane

**Best for**: 跨職能流程、RACI-style flow、vendor handoff、multi-team shipping workflow、跨團隊責任歸屬視覺化。

## Layout conventions

- Layer 3 derived token：`lane-A` = `--ink @ 0.08`、`lane-B` = `--ink @ 0.04`、`lane-C` = `--ink @ 0.02`（v1 ground truth 分別為 `#ebeae5` / `#f3f1ec` / `#f6f5f0`），預計算為 solid hex，不得出現 alpha-channel CSS 函式形式；參見 `references/design-token-resolver.md`。
- Horizontal lane（或 vertical column）一個 actor / team 一條；lane 底色循環 `lane-A` / `lane-B` / `lane-C` 區分；lane label 在左 margin（或頂部）以 `--font-mono` eyebrow 標示。
- Lane divider 為 1px hairline；process step 為 rect，**只能放在執行該 step 的 actor 所屬 lane 內**；step 間以 arrow 連接表流向。
- Handoff（跨 lane 邊界的 arrow）是 swimlane 圖最重要的邊；`--brand` 留給導致最大耦合或延遲的那一個 handoff，一張圖一個；不要強迫每個 lane 步數相等，一 lane 一個 step 也可以。

## Anti-patterns

- Lane 沒有 label。
  - *Why fails*：swimlane 的整個價值就是「告訴讀者哪個步驟由誰負責」；缺 lane label 等於丟掉這個唯一資訊，整張圖退化成普通 flowchart 而且多了視覺雜訊。
- 一個 step 跨在兩條 lane 之間（責任不明）。
  - *Why fails*：lane 的語意承諾是 single owner；step 跨 lane 等於宣告「兩個 owner 共同負責」，但實際運作必有一方先動手，視覺上的 ambiguity 直接對應流程上的 ambiguity，圖反過來助長協作 bug。
- Arrow 在 lane 間 snake back-and-forth 來回鑽。
  - *Why fails*：來回鑽的 arrow 視覺上像迷宮，讀者無法 trace 主流向；應重排 step 順序讓 flow 大致直線，若無法 straighten 代表流程本身設計過於混亂，圖反映了該事實但無解決它。

## Examples

Inline example below — 3-lane cross-team flow（Frontend → Backend[focal=Persist DB] → DB）。每 lane 含 2–3 node、cross-lane arrow 走 `arrow-link`、1 focal node。完整 `<defs>` 三 chevron marker、兩層 paper-mask、節點寬 2 檔白名單 `{128, 160}`、legend strip 與所有 `x/y/width/height` 為 4 的倍數。

```html
<figure class="diagram">
  <svg viewBox="0 0 1000 600" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Three-lane swimlane: Frontend / Backend / DB">
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

    <!-- ===== LANE SEPARATOR HAIRLINES（兩條，把畫面切成三 lane） ===== -->
    <line x1="60" y1="200" x2="940" y2="200"
          stroke="#141413" stroke-opacity="0.10" stroke-width="0.8"/>
    <line x1="60" y1="320" x2="940" y2="320"
          stroke="#141413" stroke-opacity="0.10" stroke-width="0.8"/>

    <!-- ===== LANE LABELS（左 margin，Geist Mono eyebrow） ===== -->
    <text x="68" y="148" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.14em">FRONTEND</text>
    <text x="68" y="268" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.14em">BACKEND</text>
    <text x="68" y="388" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.14em">DATABASE</text>

    <!-- ===== EDGES（先畫線） ===== -->
    <!-- A → B（lane1 內，內部箭頭） -->
    <line x1="256" y1="136" x2="288" y2="136"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <!-- B → C（跨 lane 1→2，arrow-link） -->
    <line x1="352" y1="168" x2="192" y2="224"
          stroke="#2D5A8A" stroke-width="1.2" marker-end="url(#arrow-link)"/>
    <!-- C → D（lane2 內，內部箭頭） -->
    <line x1="256" y1="256" x2="288" y2="256"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <!-- D → E（lane2 內 focal 主流，accent） -->
    <line x1="416" y1="256" x2="448" y2="256"
          stroke="#1B365D" stroke-width="1.4" marker-end="url(#arrow-accent)"/>
    <!-- E → F（跨 lane 2→3，arrow-link，focal 落地寫入） -->
    <line x1="528" y1="288" x2="512" y2="344"
          stroke="#2D5A8A" stroke-width="1.2" marker-end="url(#arrow-link)"/>
    <!-- F → G（lane3 內，內部箭頭，audit fan-out） -->
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
