# Requirements

> **編號防撞聲明**：既有程式碼註解中出現的 `REQ-003` / `REQ-005` / `REQ-007` 等字樣屬於**舊一輪 spec**（搜尋 funnel 與換源基礎功能），與本檔編號**無關**。實作時凡引用需求編號，一律以本檔（`.claude/analyze/2026-07-19-legado-parity/requirement.md`）為準；不得因程式碼註解的舊編號而混淆。

## REQ-001: 規則 DSL `&` 自身選擇器（元素層）

**描述**：`extract_within` 與 `select_within` 對 selector 為 `&` 的 alternative，必須在呼叫 `Selector::parse` 之前先辨識並以「當前元素自身」作為候選節點，accessor / regex 取代 / `||` fallback 語意全部照常作用。

### Scenarios

**Scenario 1: `&` 取自身文字（C1）**
- **Given** 一個由 `Html::parse_fragment("<a href=\"/x\">第1章 起</a>")` 選出的 `<a>` 元素 `el`
- **When** 呼叫 `extract_within(el, "&")`
- **Then** 回傳 `Ok(Some("第1章 起"))`，不產生任何 selector parse 錯誤

**Scenario 2: `&` 加 accessor（C2）**
- **Given** 同上元素 `el`
- **When** 呼叫 `extract_within(el, "&@href")`
- **Then** 回傳 `Ok(Some("/x"))`
- **And** `&@html` / `&@outerHtml` 分別回傳自身 inner HTML / outer HTML

**Scenario 3: `&` 加 regex 取代（C3）**
- **Given** 元素文字為 `"第1章 起"`
- **When** 呼叫 `extract_within(el, "&##第##Ch.")`
- **Then** 回傳 `Ok(Some("Ch.1章 起"))`（自身取值後套用取代）

**Scenario 4: `||` fallback 任意位置（C4）**
- **Given** 元素 `el` 內無 `em.missing` / `em.x` 子節點且自身有文字
- **When** 呼叫 `extract_within(el, "em.missing || &")` 與 `extract_within(el, "& || em.x")`
- **Then** 兩者皆回傳自身文字（前者 fallback 到 `&`；後者 `&` 先命中即回傳）

**Scenario 5: `select_within` 自身（C5）**
- **Given** 任一元素 `el`
- **When** 呼叫 `select_within(el, "&")`
- **Then** 回傳 `Ok(vec![el])`（長度 1、即元素本身）

**Scenario 6: 既有行為不變（C6）**
- **Given** 既有 `catalog::service::rule::tests` 4 條測試與其他一切非 `&` 規則
- **When** 修復後執行 `cargo test`
- **Then** 全部原樣通過、無任何既有測試被修改

---

## REQ-002: `&` 於 document 層入口視為根元素（bonus）

**描述**：`extract_doc` / `select_nodes` / `extract_all_doc` 遇到 selector 為 `&` 的 alternative 時，以 `Html::root_element()`（文件根元素）作為候選節點，不報錯。

### Scenarios

**Scenario 1: `extract_doc` 根元素文字（C7）**
- **Given** `Html::parse_fragment("<p>alpha</p><p>beta</p>")`
- **When** 呼叫 `extract_doc(&doc, "&")`
- **Then** 回傳 `Ok(Some(...))` 且值為根元素整體 text（含 `alpha` 與 `beta`），不報 selector 錯誤

**Scenario 2: `select_nodes` / `extract_all_doc` 根元素（C7）**
- **Given** 同上文件
- **When** 呼叫 `select_nodes(&doc, "&")` 與 `extract_all_doc(&doc, "&")`
- **Then** 前者回傳長度 1 的 `vec![root_element]`；後者回傳單元素向量（根元素依 accessor 取值）

---

## REQ-003: 換源時的章名比對進度遷移

**描述**：`switch_source_core::run_with_deps` 在進入 DB 交易前，以固定演算法（精確相等 → 去空白相等 → 章號 token 相等，依序取最高優先級；同一規則內沿新 TOC idx 升冪取第一個命中）解析舊當前章名對新 TOC 的對應章，命中則以該 idx 寫入 progress，未命中則維持現行「重置到新 TOC 首章」行為；解析過程任何失敗（無 progress 列、舊章名查不到、DB 讀取錯誤）一律降級為未命中，**不新增任何 abort 類別**。

### Scenarios

**Scenario 1: 精確同名命中（C8）**
- **Given** 舊 progress 指向章名 `"第2章 破曉"`，新 TOC 為 `[(idx 0, "序"), (idx 3, "第1章 黎明"), (idx 5, "第2章 破曉")]`（idx 非稠密）
- **When** 執行換源
- **Then** 交易後 `progress.chapter_index == 5`、`scroll_offset == 0`
- **And** 回傳的 `SwitchOutcome` 標記為已遷移、含章名 `"第2章 破曉"` 與 idx 5

**Scenario 2: 去空白相等命中（C9）**
- **Given** 舊章名 `"第2章　破曉"`（全形空白），新 TOC 含 `(idx 4, "第2章 破曉")`（半形空白）且無精確同名
- **When** 執行換源
- **Then** `progress.chapter_index == 4`（規則 b 命中）

**Scenario 3: 章號 token 命中（C10）**
- **Given** 舊章名 `"第１２章 風起"`（全形數字），新 TOC 含 `(idx 20, "第12章 風起雲湧")` 且規則 a / b 皆不中
- **When** 執行換源
- **Then** `progress.chapter_index == 20`（`１２`→`12` 正規化後 token 相等）
- **And** 中文數字章名（如 `"第十二章"`) 的 token 為字面 `"十二"`，與 `"12"` **不**互轉、不命中

**Scenario 4: 全未命中維持現行重置（C11）**
- **Given** 舊章名與新 TOC 任何章依三規則皆不相符（或無 progress 列 / 舊章名無法解析）
- **When** 執行換源
- **Then** `progress.chapter_index` = 新 TOC 首章 idx、`scroll_offset == 0` —— 與修改前行為完全一致

**Scenario 5: abort 語意不變（C12）**
- **Given** 五類 abort（fetch_info 失敗 / fetch_toc 失敗 / 逾時 / 空 TOC / 全 fallback 章名）任一觸發
- **When** 執行換源
- **Then** 交易未被呼叫、DB 不變 —— 既有 abort-before-tx 測試原樣通過；章名解析步驟不得在 abort 判定之前引入新的失敗出口

---

## REQ-004: 換源結果之使用者呈現（遷移 vs 重置）

**描述**：`SwitchOutcome` 攜帶進度解析結果（`Migrated { idx, name }` 或 `Reset`），CLI handler 與 TUI toast 兩條路徑各自以繁中訊息呈現，遷移時含命中章名。

### Scenarios

**Scenario 1: CLI 遷移訊息（C13）**
- **Given** 換源成功且比對命中 `(idx 5, "第2章 破曉")`
- **When** CLI `switch-source` handler 格式化輸出
- **Then** stdout 訊息含「進度已遷移」與章名 `"第2章 破曉"`

**Scenario 2: CLI 重置訊息（C13）**
- **Given** 換源成功但比對未命中
- **When** CLI handler 格式化輸出
- **Then** stdout 訊息含「進度重置」字樣（沿用現行首章資訊）

**Scenario 3: TUI toast 兩態（C13）**
- **Given** TUI SwitchSourceScreen 執行換源成功
- **When** transition 回 ShelfScreen
- **Then** toast 依 `SwitchOutcome` 呈現「進度已遷移：{章名}」或「進度重置到首章：{首章名}」兩態之一

**Scenario 4: 純邏輯層測試覆蓋（C14）**
- **Given** `SwitchSourceDeps` fake（擴充後含舊章名解析）與 dao in-memory 測試
- **When** 執行 `cargo test`
- **Then** C8–C11 與 C13 的兩態各有至少一條具名斷言測試（斷言具體 idx 值與訊息內容，非「is ok」）

---

## REQ-005: 搜尋結果摺疊純函數

**描述**：TUI 跨源搜尋在 `assemble_rows` 之後增加純函數 post-pass `fold_rows`：`(name.trim(), author-or-empty.trim())` 相同的 `Hit` 列合併為一個攜帶全部 `(hit, source_name)` 的摺疊列，保留首次出現位置；`StatusLine` 與單源命中不受影響。

### Scenarios

**Scenario 1: 三源同書摺疊（C15）**
- **Given** rows 依序為源 A / B / C 各一筆 `("超維術士", "牧狐")` 的 Hit
- **When** 呼叫 `fold_rows(rows)`
- **Then** 輸出恰一列摺疊列，內含 3 筆 `(hit, source_name)`，來源名依出現順序為 `["A", "B", "C"]`
- **And** 渲染文字含書名、作者、`3` 與全部三個來源名

**Scenario 2: 同名不同作者不摺疊（C16）**
- **Given** rows 含 `("超維術士", "牧狐")` 與 `("超維術士", "另一人")`
- **When** 呼叫 `fold_rows(rows)`
- **Then** 兩列各自保留、互不合併；author 為 `None` 者以空字串參與比對（`None` 與 `Some("")`、`Some("  ")` 視為相同作者鍵）

**Scenario 3: 首位保留 + 單源原樣（C17）**
- **Given** rows = `[Hit X(源A), Hit Y(源B), Hit X(源C)]`（X 重複、Y 單源）
- **When** 呼叫 `fold_rows(rows)`
- **Then** 輸出 = `[Folded X{A,C}, Hit Y(源B)]` —— X 摺疊列停在原第 0 位，Y 仍為普通 `Hit` 列、渲染與現況相同

**Scenario 4: StatusLine 相對位置不變（C19）**
- **Given** rows = `[Hit X(A), StatusLine("源 B：逾時"), Hit X(C), StatusLine("源 D 未查")]`
- **When** 呼叫 `fold_rows(rows)`
- **Then** 輸出 = `[Folded X{A,C}, StatusLine("源 B：逾時"), StatusLine("源 D 未查")]` —— 兩條 StatusLine 相對於存活列的先後次序不變

**Scenario 5: 既有測試不變（C20）**
- **Given** `assemble_rows` 本體與其既有 5 條測試（含三源同書出三列的 scenario1）
- **When** 摺疊以 post-pass 實作、`do_search` 改為 `fold_rows(assemble_rows(...))`
- **Then** 既有 `assemble_rows` 測試原樣通過（摺疊不進 `assemble_rows` 本體）

---

## REQ-006: 摺疊列互動（Enter 與游標）

**描述**：Results 畫面對摺疊列的 Enter 行為 = 對其第一個來源的 hit 執行現行「入架 / 重複偵測」流程；j/k 游標與首選列邏輯把摺疊列視同命中列。

### Scenarios

**Scenario 1: Enter 作用於第一來源（C18）**
- **Given** 選中一個含 `[(hit_A, "A"), (hit_C, "C")]` 的摺疊列
- **When** 按 Enter
- **Then** 後續 `get_novel_by_book_url` / `fetch_novel_info` / `add_novel` 流程以 `hit_A`（第一來源之 hit）為輸入 —— 與單源列按 Enter 的既有流程一致

**Scenario 2: 首選列含摺疊列**
- **Given** rows 首列為摺疊列
- **When** 進入 Results 狀態
- **Then** `first_hit_idx` 選中該摺疊列（`Hit` 與摺疊列皆視為可選命中）
