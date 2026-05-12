---
name: sequence
status: complete
example: inline
---

# Sequence

**Best for**: request / response 流程、protocol 交握、多 actor 隨時間的互動、API call trace、事故重建（incident reconstruction）。

## Layout conventions

- Layer 3 derived token：`lifeline-color` 由 `--ink @ 0.30` 預計算為 solid hex（v1 ground truth `#b6b5af`），不得出現 alpha-channel CSS 函式形式；計算方式參見 `references/design-token-resolver.md`。
- Actor 為頂端水平排列的 box；每個 actor 下垂一條 dashed vertical line 作 lifeline，stroke 走上述 `lifeline-color`，stroke-width=1、stroke-dasharray="3,3" 固定。
- Message 為 lifeline 之間的 horizontal arrow，**時間 top→down**；activation bar 為 lifeline 上窄 rect（`w=8`，`--ink @ 0.06` fill，0.8 hairline stroke），跨越該 actor 持有控制權的區間，巢狀呼叫往內堆疊。
- Self-message 用 U 型短 loop 回到同一條 lifeline，label 放 loop 右側；return message 用 dashed line，**顏色同發起該 call 的線**。
- `--brand` 只能用在主要 success response 或 headline message，一條最多兩條，不可每條都上色。

## Anti-patterns

- Message arrow 向上指（時間倒流）。
  - *Why fails*：sequence diagram 唯一的 invariant 就是 y 軸代表單向時間；arrow 向上等於否定 y 軸語意，讀者無法判斷因果順序，整張圖的 grammar 崩壞。
- Activation bar 沒有 close（懸而未收）。
  - *Why fails*：activation bar 的語意是「這個 actor 在這個區間持有 control」，未 close 等於宣告 control 從未交還，與實際系統行為不符；同時破壞 nested call 的視覺對稱性。
- Label 坐在另一條 lifeline 之上。
  - *Why fails*：lifeline 是視覺骨架，label 壓在上面會讓 lifeline 與文字互相吃光，讀者掃讀時 y 位置就會錯位；應縮短 label 或將 y 移到 lifeline 間隔處。

## Examples

Inline example below — 3-actor login protocol（Client → Server[focal] → DB），含 dashed lifeline、activation bar、alt branch（password mismatch）、return message（dashed line）、1 個 sidenote box。Server actor 標 `data-role="focal"`，所有 actor/sidenote 寬走 2 檔白名單 `{128, 160}`，alt frame 用 `<path>` 而非 rect 以避開非白名單寬度。

```html
<figure class="diagram">
  <svg viewBox="0 0 1000 720" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Login protocol sequence diagram">
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
