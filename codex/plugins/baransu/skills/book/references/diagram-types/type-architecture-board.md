---
name: architecture-board
status: complete
example: inline
---

## Contents

- Layout conventions
- Anti-patterns
- Examples

# Architecture Board

**Best for**: full-system panorama / multi-layer platform map / control plane + governance + roadmap in one view / owner map / report-scale board (10–25 blocks).

## Layout conventions

- **A board earns its pixels by answering questions**: a reader should leave with three answers, in this order — (1) the inventory of parts, (2) the flow and dependency structure between them, (3) the landing point of the next intervention. Any block, line, or label that helps with none of the three is cut before layout begins; past ~25 unfiltered blocks a panorama stops being scannable and becomes a lookup chore the reader abandons.
- **Fixed horizontal information bands, one question each**, top to bottom: title / judgment → business roles & consumers → system modules & control plane → runtime paths (data / event / permission) → governance (monitoring, owners, roadmap). No cross-band leakage: no protocol detail in the roles band, no module catalog in governance — a fixed band order lets a returning reader drop straight to the altitude of their question without re-orienting the whole canvas.
- **Bands, not cards**: peers at the same altitude sit side by side within a single band, split by hairline vertical `<line>` dividers; each band carries an uppercase mono scan-anchor label (e.g. `ROLES`, `MODULES`, `RUNTIME`, `GOVERNANCE`); blocks never nest — one level of block per band, no box-in-box. Bands are delimited by hairlines + labels only, never by wide background fill rects: a wide band-fill rect reads as one giant node, competes with every block inside it, and would also register on the node-width whitelist (GATE-J); hairlines carry the same grouping for free.
- **Block budget 10–25**: below 10 blocks this is not a board — route back to the single embedded figure (`type-architecture.md`); past 25, merge blocks into named domains before adding any pixels — 10 is where a single figure's ≤9-node budget ends; 25 is where even banded scanning ends.
- **Block anatomy**: title + 1–3 short committing sublines ("from X to Y", "owned by X", "measured by X") — never paragraphs, never noun trains — a subline that commits to a direction can be wrong and is therefore useful; a noun train can only be vague.
- **Line discipline**: orthogonal only; collapse the connection web to 1–2 main flows carrying chevron markers; a relation that cannot be drawn cleanly becomes a caption below the band, not a line — an unparseable line teaches nothing and costs trust in every parseable one.
- **Corner text is metadata only**: date basis / version / data scope — set in 8px mono at a canvas corner. Opinions and viewpoint captions never go there (see Anti-patterns) — corner position borrows the credibility of a stamp; only verifiable facts may spend it.
- **Scale routing**: a board that still overflows after domain-merging splits into sister boards along domain seams — never an endless-scroll canvas. When the board is repo-maintained, record each sister's boundary in the intent file's sister-boundaries block (see `maintained-diagrams.md`) — a canvas that grows forever is a dump, not a map; seam-recorded sisters keep each board redraw-able without re-negotiating scope every quarter.

## Anti-patterns

- **An inflated single figure posing as a board** (a >9-node architecture diagram with no bands)
  - *Why fails*: without band altitudes the reader has no scan order — 15 free-floating nodes is the worst of both worlds: too many for one visual pass, no structure for indexed reading. ≤9 nodes routes to `type-architecture.md`; ≥10 gets bands.
- **Paragraph-length block copy**
  - *Why fails*: a board is scanned at arm's length; a paragraph forces close reading, which breaks the panorama contract and makes every terser block around it look under-explained by comparison.
- **Per-block color coding**
  - *Why fails*: N block colors mean N legend entries the reader must memorize before reading anything; one accent + warm neutrals keeps focal meaningful and survives grayscale print and colorblind reading. Zero new colors — the accent discipline does not scale up with block count.
- **Endless vertical scroll**
  - *Why fails*: a board's entire value is co-presence — everything visible at once; the moment the reader scrolls, cross-band relations leave the viewport and the "one view" promise silently breaks. Split into sister boards along domain seams instead.
- **Viewpoint / opinion captions in the corners**
  - *Why fails*: the board presents structure the reader can verify; an editorial opinion placed in the corner-metadata position borrows the credibility of the date/version stamp it displaces. Corner text is date basis / version / data scope only.

## Examples

Inline example below — a 4-band, 12-block content-platform panorama (`viewBox="0 0 1000 700"`): ROLES (3 blocks) → MODULES (4 blocks, Pipeline focal) → RUNTIME (2 blocks) → GOVERNANCE (3 pill blocks). Complete `<defs>` with a paper-grain overlay pattern (a deliberately re-authored variant of the §4.4 dotted overlay: finer 16px cell, lower opacity) and two chevron markers (`#arrow-accent` on the single main flow Creator→Ingest→Pipeline→Store, `#arrow` on the one secondary path — both referenced, defs ↔ refs bijective), two paper-mask layers, horizontal band hairlines + uppercase mono band labels, hairline vertical peer dividers, the 2-step block-width whitelist `{128, 160}`, §4.5 type tags, 1 `data-role="focal"` block, corner metadata (date basis / version / scope), a legend strip, and all `<rect>/<line>` geometry as multiples of 4.

```html
<figure class="diagram">
  <svg viewBox="0 0 1000 700" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Content platform architecture board, four bands">
    <defs>
      <pattern id="grain" width="16" height="16" patternUnits="userSpaceOnUse">
        <circle cx="2" cy="2" r="0.7" fill="#e5e3d8"/>
      </pattern>
      <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto">
        <path d="M2 1 L8 5 L2 9" fill="none" stroke="#504e49"
              stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      </marker>
      <marker id="arrow-accent" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto">
        <path d="M2 1 L8 5 L2 9" fill="none" stroke="#1B365D"
              stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      </marker>
    </defs>

    <!-- Paper-mask layer 1（強制） -->
    <rect width="100%" height="100%" fill="#f5f4ed"/>
    <!-- Paper-mask layer 2（可選 grain overlay，本檔自訂變體） -->
    <rect width="100%" height="100%" fill="url(#grain)" opacity="0.4"/>

    <!-- ===== TITLE + corner metadata（日期基準／版本／資料範圍——僅此三類） ===== -->
    <text x="500" y="36" fill="#141413" font-size="14" font-weight="700"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Content platform panorama</text>
    <text x="940" y="36" fill="#504e49" font-size="8"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="end" letter-spacing="0.10em">BASIS 2026-07 · V2 · PROD</text>

    <!-- ===== MAIN FLOW（先畫線；accent chevron 僅上單一主流） ===== -->
    <line x1="144" y1="160" x2="144" y2="232"
          stroke="#1B365D" stroke-width="1.4" marker-end="url(#arrow-accent)"/>
    <line x1="208" y1="264" x2="304" y2="264"
          stroke="#1B365D" stroke-width="1.4" marker-end="url(#arrow-accent)"/>
    <line x1="464" y1="264" x2="560" y2="264"
          stroke="#1B365D" stroke-width="1.4" marker-end="url(#arrow-accent)"/>
    <!-- Secondary path：Pipeline → Event bus（muted） -->
    <line x1="384" y1="296" x2="384" y2="368"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>

    <!-- ===== BAND 1 — ROLES（hairline + mono 標籤定界，非填色大框） ===== -->
    <line x1="40" y1="56" x2="960" y2="56"
          stroke="#141413" stroke-opacity="0.10" stroke-width="0.8"/>
    <text x="48" y="76" fill="#504e49" font-size="8"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.14em">ROLES</text>
    <line x1="328" y1="96" x2="328" y2="160"
          stroke="#141413" stroke-opacity="0.10" stroke-width="0.8"/>
    <line x1="684" y1="96" x2="684" y2="160"
          stroke="#141413" stroke-opacity="0.10" stroke-width="0.8"/>

    <rect x="80" y="96" width="128" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="80" y="96" width="128" height="64" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="88" y="104" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="102" y="113" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">ROLE</text>
    <text x="144" y="136" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Creator</text>
    <text x="144" y="152" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace" text-anchor="middle">writes drafts</text>

    <rect x="436" y="96" width="128" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="436" y="96" width="128" height="64" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="444" y="104" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="458" y="113" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">ROLE</text>
    <text x="500" y="136" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Reviewer</text>
    <text x="500" y="152" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace" text-anchor="middle">gates quality</text>

    <rect x="792" y="96" width="128" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="792" y="96" width="128" height="64" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="800" y="104" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="814" y="113" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">ROLE</text>
    <text x="856" y="136" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Reader</text>
    <text x="856" y="152" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace" text-anchor="middle">consumes published</text>

    <!-- ===== BAND 2 — MODULES & CONTROL PLANE ===== -->
    <line x1="40" y1="192" x2="960" y2="192"
          stroke="#141413" stroke-opacity="0.10" stroke-width="0.8"/>
    <text x="48" y="212" fill="#504e49" font-size="8"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.14em">MODULES</text>
    <line x1="256" y1="232" x2="256" y2="296"
          stroke="#141413" stroke-opacity="0.10" stroke-width="0.8"/>
    <line x1="512" y1="232" x2="512" y2="296"
          stroke="#141413" stroke-opacity="0.10" stroke-width="0.8"/>
    <line x1="736" y1="232" x2="736" y2="296"
          stroke="#141413" stroke-opacity="0.10" stroke-width="0.8"/>

    <rect x="80" y="232" width="128" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="80" y="232" width="128" height="64" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="88" y="240" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="102" y="249" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">MOD</text>
    <text x="144" y="272" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Ingest</text>
    <text x="144" y="288" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace" text-anchor="middle">from source to raw</text>

    <rect x="304" y="232" width="160" height="64" rx="6" fill="#f5f4ed"/>
    <rect data-role="focal"
          x="304" y="232" width="160" height="64" rx="6"
          fill="#EEF2F7" stroke="#1B365D" stroke-width="1.4"/>
    <rect x="312" y="240" width="28" height="12" rx="2"
          fill="transparent" stroke="#1B365D" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="326" y="249" fill="#1B365D" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">MOD</text>
    <text x="384" y="272" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Pipeline</text>
    <text x="384" y="288" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace" text-anchor="middle">raw to published</text>

    <rect x="560" y="232" width="128" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="560" y="232" width="128" height="64" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="568" y="240" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="582" y="249" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">MOD</text>
    <text x="624" y="272" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Store</text>
    <text x="624" y="288" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace" text-anchor="middle">owned by infra pod</text>

    <rect x="784" y="232" width="128" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="784" y="232" width="128" height="64" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="792" y="240" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="806" y="249" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">CTL</text>
    <text x="848" y="272" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Control plane</text>
    <text x="848" y="288" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace" text-anchor="middle">flags + quotas</text>

    <!-- ===== BAND 3 — RUNTIME PATHS ===== -->
    <line x1="40" y1="328" x2="960" y2="328"
          stroke="#141413" stroke-opacity="0.10" stroke-width="0.8"/>
    <text x="48" y="348" fill="#504e49" font-size="8"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.14em">RUNTIME</text>
    <line x1="512" y1="368" x2="512" y2="432"
          stroke="#141413" stroke-opacity="0.10" stroke-width="0.8"/>

    <rect x="320" y="368" width="128" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="320" y="368" width="128" height="64" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="328" y="376" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="342" y="385" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">BUS</text>
    <text x="384" y="408" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Event bus</text>
    <text x="384" y="424" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace" text-anchor="middle">publish events</text>

    <rect x="560" y="368" width="128" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="560" y="368" width="128" height="64" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="568" y="376" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="582" y="385" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">ACL</text>
    <text x="624" y="408" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Permissions</text>
    <text x="624" y="424" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace" text-anchor="middle">who reads what</text>

    <!-- ===== BAND 4 — GOVERNANCE（pill 高度 32） ===== -->
    <line x1="40" y1="464" x2="960" y2="464" stroke="#141413" stroke-opacity="0.10" stroke-width="0.8"/>
    <text x="48" y="484" fill="#504e49" font-size="8" font-family="'Geist Mono', ui-monospace, monospace" letter-spacing="0.14em">GOVERNANCE</text>
    <line x1="328" y1="504" x2="328" y2="536" stroke="#141413" stroke-opacity="0.10" stroke-width="0.8"/>
    <line x1="576" y1="504" x2="576" y2="536" stroke="#141413" stroke-opacity="0.10" stroke-width="0.8"/>

    <rect x="80" y="504" width="128" height="32" rx="6" fill="#f5f4ed"/>
    <rect x="80" y="504" width="128" height="32" rx="6" fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="88" y="512" width="28" height="12" rx="2" fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="102" y="521" fill="#141413" font-size="7" font-family="'Geist Mono', ui-monospace, monospace" text-anchor="middle" letter-spacing="0.08em">GOV</text>
    <text x="156" y="524" fill="#141413" font-size="10" font-weight="600" font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Monitoring</text>

    <rect x="368" y="504" width="128" height="32" rx="6" fill="#f5f4ed"/>
    <rect x="368" y="504" width="128" height="32" rx="6" fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="376" y="512" width="28" height="12" rx="2" fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="390" y="521" fill="#141413" font-size="7" font-family="'Geist Mono', ui-monospace, monospace" text-anchor="middle" letter-spacing="0.08em">GOV</text>
    <text x="444" y="524" fill="#141413" font-size="10" font-weight="600" font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Owners</text>

    <rect x="616" y="504" width="128" height="32" rx="6" fill="#f5f4ed"/>
    <rect x="616" y="504" width="128" height="32" rx="6" fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="624" y="512" width="28" height="12" rx="2" fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="638" y="521" fill="#141413" font-size="7" font-family="'Geist Mono', ui-monospace, monospace" text-anchor="middle" letter-spacing="0.08em">GOV</text>
    <text x="692" y="524" fill="#141413" font-size="10" font-weight="600" font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Roadmap</text>

    <!-- ===== LEGEND STRIP ===== -->
    <line x1="60" y1="616" x2="940" y2="616" stroke="#141413" stroke-opacity="0.10" stroke-width="0.8"/>
    <text x="60" y="636" fill="#504e49" font-size="8" font-family="'Geist Mono', ui-monospace, monospace" letter-spacing="0.14em">LEGEND</text>
    <rect x="140" y="628" width="16" height="12" rx="2" fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <text x="160" y="637" fill="#504e49" font-size="9" font-family="'Geist', system-ui, sans-serif">Block (role / module)</text>
    <rect x="332" y="628" width="16" height="12" rx="2" fill="#EEF2F7" stroke="#1B365D" stroke-width="1.2"/>
    <text x="352" y="637" fill="#504e49" font-size="9" font-family="'Geist', system-ui, sans-serif">Focal (next intervention)</text>
    <line x1="548" y1="632" x2="568" y2="632" stroke="#1B365D" stroke-width="1.4" marker-end="url(#arrow-accent)"/>
    <text x="576" y="637" fill="#504e49" font-size="9" font-family="'Geist', system-ui, sans-serif">Main flow</text>
    <line x1="680" y1="632" x2="700" y2="632" stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <text x="708" y="637" fill="#504e49" font-size="9" font-family="'Geist', system-ui, sans-serif">Secondary path</text>
  </svg>
  <figcaption>圖：內容平台全景 board（4 帶 12 塊）：主流程 Creator→Ingest→Pipeline→Store 收斂為單一可讀路徑；GOVERNANCE 帶尚未逐 module 標註 owner——下一步把每個 module 的 owner 填進 Owners 塊。</figcaption>
</figure>
```
