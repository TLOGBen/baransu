---
name: architecture
status: complete
example: inline
---

# Architecture

**Best for**: 系統概覽（system overview）、資料流圖（data-flow）、整合 map（integration map）、基礎設施拓樸（infra topology）、元件 + 連線（components & connections）。

## Layout conventions

- 依 tier 或 trust boundary 分群（frontend → backend → data；public → private）；同群節點水平或垂直對齊，群間以間距區隔，不靠連線去暗示分層。
- 主流方向選 LTR 或 TTB 一個守一個；不要在同一張圖內混用兩個主流方向。次要回饋線（callback、retry）可逆向，但箭頭一定要顯式標出。
- 線先畫、boxes 後畫：SVG 內箭頭 `<line>` 先進 DOM，節點 `<rect>` / `<g>` 後進，z-order 才會把連線壓在節點底下，避免箭頭尾巴穿過節點外框。
- 1–2 個焦點節點用 `data-role="focal"` 屬性標記（**非** class）；焦點節點視覺走 `--brand-tint` 填色 + `--brand` 描邊，並以 `marker-end="url(#arrow-accent)"` 收尾。每張 SVG 最多 2 個 focal，超過則「重點」就消失。
- Dashed boundary rectangle 標 region（VPC、security group、trust zone）；boundary 標籤坐在 `--parchment` 色 mask 上，覆蓋 dashed 線條與標籤交會處，避免線壓字。
- 節點寬度走 grid 的 12 檔之一（如 96 / 144 / 192 / 240px），不要每個節點寬度自由發揮；視覺節律一致時讀者掃讀速度才會穩定。
- 節點內嵌字 14–24px：超過 24 看起來像 hero、低於 14 在 1× SVG 下會糊。標題用 `--font-sans`、metric / id 用 `--font-mono`、單位用 `--color-muted`。
- 三個 marker（`arrow` / `arrow-accent` / `arrow-link`）在 `<defs>` 內統一定義，屬性固定 `markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"`；不再手寫箭頭 path，避免 viewBox 縮放下對位偏差。

## Anti-patterns

- **每個 box 都 focal**（全部 `--brand-tint` 填、`--brand` 描邊）。
  - *Why fails*：focal 的本質是相對比較——當所有節點都「重點」，視覺階層就崩，讀者無法在 3 秒內鎖定主流路徑或主整合點，圖等同沒有重點。
- **雙向箭頭當單向意義已經明確**（例如 `Browser ↔ CDN`，但實際只關心讀取路徑）。
  - *Why fails*：雙向箭頭增加一個方向的雜訊，讀者得多花一拍判斷「這條線到底要看哪一邊」；同時讓真正需要雙向語意的節點（如 cache write-back）失去辨識度。
- **Legend 飄在 diagram canvas 內**，與節點或連線重疊。
  - *Why fails*：legend 是 meta-information，與 diagram body 屬不同閱讀層級；放在 canvas 內會與節點碰撞、被連線穿過，讀者得在「讀圖」與「對照 legend」之間反覆切換視焦。應放在 SVG 底部約 60px 的 legend strip（hairline 隔開、horizontal items）或 canvas 外。
- **用顏色標 node type 而非用 shape**（例如所有 service 用紅色、所有 datastore 用藍色）。
  - *Why fails*：Kami 規格僅給三個語意色（`--brand` / `--brand-tint` / `--color-muted`），多餘的色彩會 over-load 配色系統，與 focal 的語意衝突，色盲讀者也無法分辨；type 區分應走 shape（rect / cylinder / hexagon）或 dashed border，把色彩留給 focal 與 boundary。

## Examples

Inline example below — 6-node microservice topology（User → CDN → API[focal] → DB；側支 Auth、Cache、Queue）。完整 `<defs>` 三 chevron marker（`#arrow` / `#arrow-accent` / `#arrow-link`，皆 `path d="M2 1 L8 5 L2 9"` 描線 chevron）、兩層 paper-mask、1 個 `data-role="focal"` 節點、節點寬 2 檔白名單 `{128, 160}`、legend strip 與所有 `x/y/width/height` 為 4 的倍數。複製此 `<figure class="diagram">` block 後改節點即可重用。

```html
<figure class="diagram">
  <svg viewBox="0 0 1000 600" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Microservice architecture topology">
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

    <!-- ===== EDGES（先畫線，後畫節點以遮邊尾） ===== -->
    <!-- User → CDN（HTTP，link 色） -->
    <line x1="208" y1="128" x2="288" y2="128"
          stroke="#2D5A8A" stroke-width="1.2" marker-end="url(#arrow-link)"/>
    <!-- CDN → API（focal 主流，accent 色） -->
    <line x1="416" y1="128" x2="416" y2="240"
          stroke="#1B365D" stroke-width="1.4" marker-end="url(#arrow-accent)"/>
    <!-- Auth → API（驗證回填，內部箭頭） -->
    <line x1="560" y1="160" x2="496" y2="240"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <!-- API → DB（focal flow，accent） -->
    <line x1="496" y1="304" x2="480" y2="384"
          stroke="#1B365D" stroke-width="1.4" marker-end="url(#arrow-accent)"/>
    <!-- API → Cache（內部 read-through） -->
    <line x1="432" y1="304" x2="304" y2="384"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <!-- API → Queue（事件外送） -->
    <line x1="560" y1="304" x2="656" y2="384"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>

    <!-- ===== NODES — 寬白名單 2 檔 {128, 160}；focal 用 160 ===== -->
    <!-- Tier 1：External user（128） -->
    <rect x="80" y="96" width="128" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="80" y="96" width="128" height="64" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="88" y="104" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="102" y="113" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">EXT</text>
    <text x="144" y="136" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Users</text>
    <text x="144" y="152" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">browser</text>

    <!-- Tier 1：CDN（128） -->
    <rect x="288" y="96" width="128" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="288" y="96" width="128" height="64" rx="6"
          fill="#f1f0eb" stroke="#504e49" stroke-width="1"/>
    <rect x="296" y="104" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="310" y="113" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">CDN</text>
    <text x="352" y="136" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">CloudFront</text>
    <text x="352" y="152" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">edge cache</text>

    <!-- Tier 1：Auth service（128） -->
    <rect x="496" y="96" width="128" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="496" y="96" width="128" height="64" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="504" y="104" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="518" y="113" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">SSO</text>
    <text x="560" y="136" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Auth</text>
    <text x="560" y="152" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">OIDC</text>

    <!-- Tier 2：API server — FOCAL（160） -->
    <rect x="416" y="240" width="160" height="64" rx="6" fill="#f5f4ed"/>
    <rect data-role="focal"
          x="416" y="240" width="160" height="64" rx="6"
          fill="#EEF2F7" stroke="#1B365D" stroke-width="1.4"/>
    <rect x="424" y="248" width="28" height="12" rx="2"
          fill="transparent" stroke="#1B365D" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="438" y="257" fill="#1B365D" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">API</text>
    <text x="496" y="280" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">API Gateway</text>
    <text x="496" y="296" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">FastAPI :8000</text>

    <!-- Tier 3：Cache（128） -->
    <rect x="176" y="384" width="128" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="176" y="384" width="128" height="64" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="184" y="392" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="198" y="401" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">CACHE</text>
    <text x="240" y="424" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Redis</text>
    <text x="240" y="440" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">read-through</text>

    <!-- Tier 3：Database（128） -->
    <rect x="416" y="384" width="128" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="416" y="384" width="128" height="64" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="424" y="392" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="438" y="401" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">DB</text>
    <text x="480" y="424" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Postgres</text>
    <text x="480" y="440" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">primary</text>

    <!-- Tier 3：Message queue（128） -->
    <rect x="656" y="384" width="128" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="656" y="384" width="128" height="64" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="664" y="392" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="678" y="401" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">MQ</text>
    <text x="720" y="424" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Kafka</text>
    <text x="720" y="440" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">events</text>

    <!-- ===== LEGEND STRIP ===== -->
    <line x1="60" y1="540" x2="940" y2="540"
          stroke="#141413" stroke-opacity="0.10" stroke-width="0.8"/>
    <text x="60" y="560" fill="#504e49" font-size="8"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.14em">LEGEND</text>

    <rect x="140" y="552" width="16" height="12" rx="2"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <text x="160" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Service node</text>

    <rect x="280" y="552" width="16" height="12" rx="2"
          fill="#EEF2F7" stroke="#1B365D" stroke-width="1.2"/>
    <text x="300" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Focal node</text>

    <line x1="420" y1="556" x2="440" y2="556"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <text x="448" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Internal call</text>

    <line x1="560" y1="556" x2="580" y2="556"
          stroke="#1B365D" stroke-width="1.4" marker-end="url(#arrow-accent)"/>
    <text x="588" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Focal flow</text>

    <line x1="700" y1="556" x2="720" y2="556"
          stroke="#2D5A8A" stroke-width="1.2" marker-end="url(#arrow-link)"/>
    <text x="728" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">External / HTTP</text>
  </svg>
  <figcaption>圖：6-node 微服務拓樸（User → CDN → API[focal] → DB；側支 Auth / Cache / Queue）。</figcaption>
</figure>
```
