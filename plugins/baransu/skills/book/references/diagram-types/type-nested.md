---
name: nested
status: complete
example: inline
---

# Nested Containment

**Best for**: 透過 containment 表達 hierarchy——scope boundary、CLAUDE.md cascade、trust zone、folder nesting、blast radius。外 = 寬泛，內 = 具體。

## Layout conventions

- 3–5 個 rounded rectangle（`rx=8`）巢狀，inset padding 一致（建議 horizontal 24–32px、vertical 32–36px）；padding 不規則 = 看起來像意外。
- 每層 label 落在左上以 `--font-mono` eyebrow 風格（7–8px、letter-spacing 0.14em）；label 坐在 `--parchment` 色 mask rect 上，遮住與 ring 頂邊的交會處避免線壓字。
- Stroke 階梯：最外圈 faint（`--color-muted` 淡）→ 中層 `--color-muted` → 內層 `--ink` → 最內層 focal 走 `--brand`；fill 同樣從外到內 opacity 漸升，最內層用 `--brand-tint`。
- 可選 file-icon glyph（折角 rect）放在每層內側暗示 scope content；italic `--font-serif` 旁注（參見 `references/primitive-annotation.md`）最多 1–2 條，多了會搶 hierarchy 主軸。

## Anti-patterns

- 超過 6 層 nesting。
  - *Why fails*：每多一層內側面積便砍半，最內層字會小到看不見、stroke 也與背景混；超過 6 層代表 hierarchy 本身結構過深，應拆 sub-diagram 而非硬塞在一張圖。
- 各層 padding 不對稱（左右不等、上下不等）。
  - *Why fails*：規則 padding 是讀者辨識「這是 hierarchy 而非任意圖形」的視覺信號；padding 不均勻會讓圖看起來像草稿或 bug，破壞 nested containment 的 grammar，讀者無法立即判斷層級關係。
- 內容物放在 ring 裡但其實不屬於該層級（如 metadata、legend、unrelated note）。
  - *Why fails*：nested 的承諾是「ring 邊界 = scope 邊界」，放入無關物件會讓 scope 語意鬆動，讀者無法區分「這是該層級的成員」還是「這只是恰好畫在這」，hierarchy 表達失效。

## Examples

Inline example below — 3-level containment（1 outer system context → 2 middle bounded contexts → 3 inner aggregate nodes，其中最內層 aggregate root 為 focal）。完整 `<defs>` 三 chevron marker、兩層 paper-mask、節點寬 2 檔白名單 `{128, 160}`（僅 leaf node 受 whitelist 約束；scope ring 為結構容器不計入）、legend strip 與所有 leaf node `x/y/width/height` 為 4 的倍數。

```html
<figure class="diagram">
  <svg viewBox="0 0 1000 600" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="3-level nested containment: System / Bounded contexts / Aggregates">
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

    <!-- ===== OUTER RING (Level 1: System Context — scope container, faint stroke) ===== -->
    <rect x="80" y="80" width="840" height="400" rx="12"
          fill="#f5f4ed" stroke="#504e49" stroke-opacity="0.45" stroke-width="1"
          stroke-dasharray="6 4"/>
    <!-- Outer label mask + eyebrow -->
    <rect x="100" y="72" width="160" height="16" fill="#f5f4ed"/>
    <text x="108" y="84" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.14em">SYSTEM CONTEXT</text>

    <!-- ===== MIDDLE RING A (Level 2: Bounded context — UI domain) ===== -->
    <rect x="120" y="128" width="376" height="320" rx="10"
          fill="#f3f1ec" stroke="#504e49" stroke-width="1"/>
    <!-- Middle A label mask + eyebrow -->
    <rect x="140" y="120" width="160" height="16" fill="#f3f1ec"/>
    <text x="148" y="132" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.14em">UI DOMAIN</text>

    <!-- ===== MIDDLE RING B (Level 2: Bounded context — Order domain) ===== -->
    <rect x="504" y="128" width="376" height="320" rx="10"
          fill="#f3f1ec" stroke="#504e49" stroke-width="1"/>
    <!-- Middle B label mask + eyebrow -->
    <rect x="524" y="120" width="160" height="16" fill="#f3f1ec"/>
    <text x="532" y="132" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.14em">ORDER DOMAIN</text>

    <!-- ===== INNER LEAF NODES (Level 3: Aggregates — whitelist {128, 160}) ===== -->

    <!-- Inner A1: Frontend SPA aggregate (160) — inside UI DOMAIN -->
    <rect x="200" y="240" width="160" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="200" y="240" width="160" height="64" rx="6"
          fill="#ebeae5" stroke="#141413" stroke-width="1"/>
    <rect x="208" y="248" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="222" y="257" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">AGG</text>
    <text x="280" y="280" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Frontend SPA</text>
    <text x="280" y="296" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">session aggregate</text>

    <!-- Inner B1: Order Service aggregate (128) — inside ORDER DOMAIN -->
    <rect x="560" y="192" width="128" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="560" y="192" width="128" height="64" rx="6"
          fill="#ebeae5" stroke="#141413" stroke-width="1"/>
    <rect x="568" y="200" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="582" y="209" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">AGG</text>
    <text x="624" y="232" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Order Service</text>
    <text x="624" y="248" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">command handler</text>

    <!-- Inner B2: Aggregate Root — FOCAL (160) — inside ORDER DOMAIN -->
    <rect x="720" y="320" width="160" height="64" rx="6" fill="#f5f4ed"/>
    <rect data-role="focal"
          x="720" y="320" width="160" height="64" rx="6"
          fill="#EEF2F7" stroke="#1B365D" stroke-width="1.4"/>
    <rect x="728" y="328" width="28" height="12" rx="2"
          fill="transparent" stroke="#1B365D" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="742" y="337" fill="#1B365D" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">FOCAL</text>
    <text x="800" y="360" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Order Root</text>
    <text x="800" y="376" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">aggregate root</text>

    <!-- ===== EDGES（跨層 / 同層） ===== -->
    <!-- Frontend SPA → Order Service（cross-domain，arrow-link） -->
    <line x1="360" y1="272" x2="560" y2="224"
          stroke="#2D5A8A" stroke-width="1.2" marker-end="url(#arrow-link)"/>
    <!-- Order Service → Order Root（同 domain，focal flow accent） -->
    <line x1="624" y1="256" x2="720" y2="352"
          stroke="#1B365D" stroke-width="1.4" marker-end="url(#arrow-accent)"/>

    <!-- ===== LEGEND STRIP ===== -->
    <line x1="60" y1="540" x2="940" y2="540"
          stroke="#141413" stroke-opacity="0.10" stroke-width="0.8"/>
    <text x="60" y="560" fill="#504e49" font-size="8"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.14em">LEGEND</text>

    <rect x="140" y="552" width="16" height="12" rx="2"
          fill="#f5f4ed" stroke="#504e49" stroke-opacity="0.45" stroke-width="1"
          stroke-dasharray="3 2"/>
    <text x="160" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Outer scope</text>

    <rect x="280" y="552" width="16" height="12" rx="2"
          fill="#f3f1ec" stroke="#504e49" stroke-width="1"/>
    <text x="300" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Bounded context</text>

    <rect x="436" y="552" width="16" height="12" rx="2"
          fill="#ebeae5" stroke="#141413" stroke-width="1"/>
    <text x="456" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Aggregate</text>

    <rect x="556" y="552" width="16" height="12" rx="2"
          fill="#EEF2F7" stroke="#1B365D" stroke-width="1.2"/>
    <text x="576" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Focal aggregate root</text>

    <line x1="744" y1="556" x2="764" y2="556"
          stroke="#1B365D" stroke-width="1.4" marker-end="url(#arrow-accent)"/>
    <text x="772" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Focal flow</text>

    <line x1="852" y1="556" x2="872" y2="556"
          stroke="#2D5A8A" stroke-width="1.2" marker-end="url(#arrow-link)"/>
    <text x="880" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Cross-domain</text>

    <line x1="60" y1="580" x2="80" y2="580"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <text x="88" y="584" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Internal link</text>
  </svg>
  <figcaption>圖：3-level nested containment（System Context → UI / Order domains → Order Root focal aggregate）。</figcaption>
</figure>
```
