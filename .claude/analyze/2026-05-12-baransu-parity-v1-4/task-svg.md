# Tasks: svg

**前置群組**：shared

## TASK-svg-01: 升級 architecture / flowchart / sequence 三個 high-traffic type 到 status=complete

**需求追溯**：REQ-001
**目標**：3 個最常用 diagram-type 含完整 example SVG，通過 chevron / 節點寬白名單 / focal 視覺 / 4 倍數座標四項規格。
**驗收標準**：
- [ ] `type-architecture.md` / `type-flowchart.md` / `type-sequence.md` frontmatter `status: complete`
- [ ] 每檔含 ≥ 1 個完整 example `<svg>` block，含三 marker chevron defs + 兩層 paper-mask + ≥ 1 焦點節點
- [ ] 跑 `validate-output.ts` 對每 example 全 GATE PASS

### 步驟

#### 規格層
- [ ] 讀 `book/references/diagram-types/type-architecture.md` 既有 ref-only 內容
- [ ] frontmatter `status: ref-only` → `status: complete`
- [ ] flowchart / sequence 同步處理

#### 模板層（example SVG）
- [ ] 對 architecture：寫一段 5-7 節點的微服務拓撲 example，含 1-2 個 `data-role="focal"` 節點，所有節點寬 ∈ {128, 144, 160}
- [ ] 對 flowchart：寫一段含 2-3 個 decision diamond + 5-7 個 process node 的 example
- [ ] 對 sequence：寫一段 3-actor protocol（含 alt / opt branch）的 example，使用 horizontal swimlane 變體

#### 驗證
- [ ] 將每 example SVG 抽出單檔，跑 `validate-output.ts` 對該檔
- [ ] 確認 GATE-A focal-cap / GATE-B paper-mask / GATE-D marker-integrity / GATE-E deny-list 全 PASS

---

## TASK-svg-02: 升級 state / er / timeline 到 status=complete

**需求追溯**：REQ-001
**目標**：3 個結構化 diagram-type 升級。
**驗收標準**：
- [ ] 三檔 frontmatter `status: complete`
- [ ] 各檔 example 通過 validator

### 步驟

#### 模板層
- [ ] state：寫一段 finite state machine example（4-5 state，含 2 transition condition label）
- [ ] er：寫一段 3-entity ER 圖 example（含 1-to-many 關係箭頭，cardinality 用 chevron marker）
- [ ] timeline：寫一段含 5-7 個 milestone 的 horizontal timeline，每 milestone 含日期 + label

#### 驗證
- [ ] 三 example 通過 GATE A-G

---

## TASK-svg-03: 升級 swimlane / quadrant / nested 到 status=complete

**需求追溯**：REQ-001
**驗收標準**：
- [ ] 三檔 frontmatter `status: complete`
- [ ] 各 example 通過 validator

### 步驟

#### 模板層
- [ ] swimlane：3 horizontal lane example，每 lane 含 2-3 node，跨 lane 箭頭走 `arrow-link`
- [ ] quadrant：標準 2×2 example，4 個象限各標示 + 5-7 個 data point dots
- [ ] nested：3 層 containment example（外層 1 個、中層 2 個、內層 3 個），用 rect 巢狀

#### 驗證
- [ ] 三 example 通過 GATE A-G

---

## TASK-svg-04: 升級 tree / layers / venn / pyramid 到 status=complete

**需求追溯**：REQ-001
**驗收標準**：
- [ ] 四檔 frontmatter `status: complete`
- [ ] 各 example 通過 validator

### 步驟

#### 模板層
- [ ] tree：3-level hierarchy example，含 1 root → 3 child → 6 leaf
- [ ] layers：4-layer 水平堆疊 example（每 layer 一個 rect band，含 label）
- [ ] venn：3-circle Venn example，含 7 區（3 single + 3 double + 1 triple intersection），無填色重疊以 stroke 分區
- [ ] pyramid：5-level pyramid example，從上窄到下寬，每 level 標 label

#### 驗證
- [ ] 四 example 通過 GATE A-G

---

## TASK-svg-05: validate-output.ts 加 node-width whitelist + chevron strict gate

**需求追溯**：REQ-001 Scenario 3/4 機械化
**目標**：把 v1.3.1 落地的 spec 規則（節點寬白名單 + chevron 必選）寫成 validator gate，從 advisory 升級為 blocking。
**驗收標準**：
- [ ] `validate-output.ts` 新增 GATE-J node-width-whitelist：每 SVG node `<rect>` width ∈ {128, 144, 160}，或 viewBox<360 走 2-tier 例外
- [ ] 新增 GATE-K chevron-strict：所有 marker defs 必含 `<path d="M2 1 L8 5 L2 9"` + `fill="none"` + `stroke-width="1.5"`；不可含 `<polygon` element
- [ ] 跑 fixture：v1.3.1 golden-template.html PASS；故意違規 fixture FAIL（exit 1）

### 步驟

#### 驗證層
- [ ] 讀 `book/scripts/validate-output.ts` GATE-D 既有 marker integrity 實作模式
- [ ] 加 GATE-J function（query 所有 SVG node rect + 解析 viewBox 寬度，依例外條件 assert 白名單合規）
- [ ] 加 GATE-K function（query marker defs → path / polygon 判定）
- [ ] 加新 fixture：`validate-fixtures/svg-node-width-fail.html`（含 width=192 的 rect）；確認 validator exit 1
- [ ] 加新 fixture：`validate-fixtures/svg-polygon-fail.html`（含 marker polygon）；確認 validator exit 1
- [ ] swiss-smoke-test.sh 串入新 fixture

#### 驗證
- [ ] `bash plugins/baransu/skills/book/scripts/swiss-smoke-test.sh` 全綠（含新 GATE-J / GATE-K 對 golden-template.html PASS）
- [ ] 故意違規 fixture exit 1
