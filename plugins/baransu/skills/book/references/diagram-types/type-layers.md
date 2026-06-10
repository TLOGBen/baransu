---
name: layers
status: complete
example: inline
---

# Layer Stack

**Best for**: OSI model、CSS cascade、context hierarchy、tech stack、abstraction layer、memory hierarchy。

## Layout conventions

- 水平 band 垂直堆疊；每層為 full-width rectangle（同 x、同 width），4–6 層為限；layer 高度 56–72px，寬度通常 800–880px 落在 1000px viewBox 內。
- 每列由左至右含三段：(1) **index tag**（`L3` / `07` / `APPLICATION`）`--font-mono` 8–9px eyebrow；(2) **layer name** 略偏左中`--font-sans` 14–16px 600；(3) **sublabel / note** 靠最右`--font-mono` 9–10px `--color-muted`。
- 層間 border 為 1px hairline `--ink @ 0.12`；外輪廓 1px `--ink` 或 `--color-muted`；fill 二擇一：交替淡色（`--parchment` / paper-2）**或**全 `--parchment` 配 hairline divider，**選定後守一個**不可混用。
- 左 margin 外側放方向指示（small up/down arrow + `--font-mono` label，如 `abstraction ↑` / `packets ↓`）；`--brand` 只上在**單一 focal layer**（stroke + 微 tint fill），代表 bottleneck / pay-rent layer / 討論主軸。

## Anti-patterns

- 把實際非 hierarchical 的概念硬塞成 layer。
  - *Why fails*：layer stack 的承諾是「上層依賴下層、下層為上層提供 abstraction」；用它表達 cross-cutting concern（如 monitoring）或 peer relationship 會讓讀者誤建依賴關係，應改用 swimlane 或 architecture。
- 層編號跳號（L3 → L5 中間沒 L4 也沒解釋）。
  - *Why fails*：layer 編號是 hierarchy 唯一可用的序列承諾；跳號代表「中間有東西但我沒畫」，讀者無法判斷是設計漏掉還是刻意省略，hierarchy 的完整性破功。
- 每層上不同色塊（rainbow stack）。
  - *Why fails*：layer 的 hierarchy 是靠垂直位置 + 編號傳遞，色塊只是噪音；多色讓讀者誤以為「每層代表一種類別」而非「上下層級」，且與 single-brand focal 規則衝突。

## Examples

Inline example below — 4-layer 水平堆疊（典型 web stack：UI / API / Service[focal] / Data），每層 band 為 sub-primitive full-width rect（不算「節點」），node 角色由置中 160-wide **function box** 承擔以對齊白名單。完整 `<defs>` 三 chevron marker、兩層 paper-mask、1 個 `data-role="focal"` 節點（Service function box）、所有節點 `rect` 寬度均為 160（單檔白名單）、abstraction ↑ 方向指示、legend strip、所有 `x/y/width/height` 為 4 的倍數。

```html
<figure class="diagram">
  <svg viewBox="0 0 1000 600" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="4-layer web stack with focal Service layer">
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

    <!-- ===== ABSTRACTION DIRECTION INDICATOR（左外緣） ===== -->
    <line x1="64" y1="160" x2="64" y2="92"
          stroke="#504e49" stroke-width="1" marker-end="url(#arrow)"/>
    <text x="56" y="180" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="end" letter-spacing="0.08em">abstraction</text>

    <!-- ===== LAYER BANDS（sub-primitive，非節點，不入寬白名單；提供視覺層次） ===== -->
    <!-- Layer 1: UI（top） -->
    <rect x="120" y="80" width="760" height="84" rx="6"
          fill="#f1f0eb" stroke="#504e49" stroke-width="1"/>
    <text x="140" y="100" fill="#141413" font-size="8"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.14em">L4 · UI</text>
    <text x="876" y="100" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="end">browser / client</text>

    <!-- Layer 2: API -->
    <rect x="120" y="172" width="760" height="84" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <text x="140" y="192" fill="#141413" font-size="8"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.14em">L3 · API</text>
    <text x="876" y="192" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="end">gateway / routing</text>

    <!-- Layer 3: Service — FOCAL band（slight accent tint） -->
    <rect x="120" y="264" width="760" height="84" rx="6"
          fill="#EEF2F7" stroke="#1B365D" stroke-width="1"/>
    <text x="140" y="284" fill="#1B365D" font-size="8"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.14em">L2 · SERVICE</text>
    <text x="876" y="284" fill="#1B365D" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="end">business logic</text>

    <!-- Layer 4: Data（bottom） -->
    <rect x="120" y="356" width="760" height="84" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <text x="140" y="376" fill="#141413" font-size="8"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.14em">L1 · DATA</text>
    <text x="876" y="376" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="end">persistence</text>

    <!-- ===== INTER-LAYER DEPENDENCY ARROWS（centerline，downward calls） ===== -->
    <!-- UI → API -->
    <line x1="500" y1="148" x2="500" y2="176"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <!-- API → Service (accent / focal flow) -->
    <line x1="500" y1="240" x2="500" y2="268"
          stroke="#1B365D" stroke-width="1.4" marker-end="url(#arrow-accent)"/>
    <!-- Service → Data -->
    <line x1="500" y1="332" x2="500" y2="360"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>

    <!-- ===== FUNCTION BOXES（每層中央 160-wide 節點，承擔 node 角色） ===== -->
    <!-- L4 UI function box -->
    <rect x="420" y="108" width="160" height="32" rx="6" fill="#f5f4ed"/>
    <rect x="420" y="108" width="160" height="32" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="428" y="112" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="442" y="121" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">UI</text>
    <text x="500" y="130" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">React App</text>

    <!-- L3 API function box -->
    <rect x="420" y="200" width="160" height="32" rx="6" fill="#f5f4ed"/>
    <rect x="420" y="200" width="160" height="32" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="428" y="204" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="442" y="213" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">API</text>
    <text x="500" y="222" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">FastAPI Gateway</text>

    <!-- L2 Service function box — FOCAL（160 width） -->
    <rect x="420" y="292" width="160" height="32" rx="6" fill="#f5f4ed"/>
    <rect data-role="focal"
          x="420" y="292" width="160" height="32" rx="6"
          fill="#EEF2F7" stroke="#1B365D" stroke-width="1.4"/>
    <rect x="428" y="296" width="28" height="12" rx="2"
          fill="transparent" stroke="#1B365D" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="442" y="305" fill="#1B365D" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">SVC</text>
    <text x="500" y="314" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Order Service</text>

    <!-- L1 Data function box -->
    <rect x="420" y="384" width="160" height="32" rx="6" fill="#f5f4ed"/>
    <rect x="420" y="384" width="160" height="32" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="428" y="388" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="442" y="397" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">DB</text>
    <text x="500" y="406" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Postgres</text>

    <!-- ===== LEGEND STRIP ===== -->
    <line x1="60" y1="540" x2="940" y2="540"
          stroke="#141413" stroke-opacity="0.10" stroke-width="0.8"/>
    <text x="60" y="560" fill="#504e49" font-size="8"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.14em">LEGEND</text>

    <rect x="140" y="552" width="16" height="12" rx="2"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <text x="160" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Layer band</text>

    <rect x="280" y="552" width="16" height="12" rx="2"
          fill="#EEF2F7" stroke="#1B365D" stroke-width="1.2"/>
    <text x="300" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Focal layer</text>

    <line x1="420" y1="556" x2="440" y2="556"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <text x="448" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Layer call</text>

    <line x1="560" y1="556" x2="580" y2="556"
          stroke="#1B365D" stroke-width="1.4" marker-end="url(#arrow-accent)"/>
    <text x="588" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Focal call</text>

    <line x1="700" y1="556" x2="720" y2="556"
          stroke="#2D5A8A" stroke-width="1.2" marker-end="url(#arrow-link)"/>
    <text x="728" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Cross-stack</text>
  </svg>
  <figcaption>圖：4-layer web stack（UI → API → Service[focal] → Data），每層中央 160-wide function box 承擔節點寬白名單合規；abstraction ↑。</figcaption>
</figure>
```
