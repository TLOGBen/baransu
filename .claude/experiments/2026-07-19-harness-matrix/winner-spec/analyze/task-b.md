# Tasks: b（換源盡力遷移閱讀進度）
**前置群組**：無

> 觸及檔案：`src/library/dao.rs`、`src/library/facade.rs`、`src/presentation/handlers/switch_source_core.rs`、`src/presentation/handlers/switch_source.rs`、`src/presentation/handlers/tui/switch_source.rs`。
> 硬規則：五類 abort 與單一交易原子性完全不動（C12）；比對步驟位於 abort 判定之後、tx 之前，任何解析失敗降級 Reset、不新增 abort 出口。既有測試僅允許機械適配（呼叫點補 `None` 參數、訊息斷言被 C13 明文取代者），一律記入 `.exp/decision-log.md`。
> 程式碼註解中的舊 `REQ-005/007` 編號與本 spec 無關；追溯一律用本 spec 的 REQ-003/REQ-004。

## TASK-b-01: dao / facade 交易加 `progress_idx: Option<i64>` 參數

**需求追溯**：REQ-003
**測試重量建議**：full
**目標**：`update_book_source_tx`（dao.rs:260）與 `switch_source_tx`（facade.rs:45）各加尾參 `progress_idx: Option<i64>`；step 4 UPSERT 寫 `progress_idx.unwrap_or(first_idx)` 並回傳該值；`None` = 現行行為。
**驗收標準**：
- [ ] `Some(5)`（非首章 idx、模擬非稠密 TOC）→ tx 後 `progress.chapter_index == 5`、`scroll_offset == 0`、回傳 `5`（C8 dao 半邊）
- [ ] `None` → `chapter_index == 新 TOC 首 idx` —— 既有 `int1` 斷言值不變（C11）
- [ ] 既有 fault-injection（step 1–4）與整合測試僅補 `None` 即原樣通過；rollback 語意不變（C12）
- [ ] facade 仍不 import 任何 `catalog::*`（C22）

### 步驟

#### dao（`src/library/dao.rs`）
- [ ] `update_book_source_tx` / `update_book_source_tx_with_fault` / `update_book_source_tx_inner` 三簽名各加 `progress_idx: Option<i64>`
- [ ] step 4 UPSERT 與回傳值改用 `progress_idx.unwrap_or(first_idx)`；其餘四步一字不動
- [ ] 既有 dao 測試呼叫點補 `None`（機械適配，記入決策日誌）

#### facade（`src/library/facade.rs`）
- [ ] `switch_source_tx` 加同名尾參、直傳 dao

#### 測試（RED 先行）
- [ ] 新增 in-memory 整合測試：`Some(5)` 情境斷言上列具名值（沿用既有 Fixture/Snapshot 風格）

---

## TASK-b-02: 純函數 `find_migration_target`（三規則比對）

**需求追溯**：REQ-003
**測試重量建議**：full
**目標**：在 `switch_source_core.rs` 實作 `pub fn find_migration_target(old_name: &str, new_toc: &[ChapterMeta]) -> Option<(i64, String)>`，規則 a（精確相等）→ b（去全部 Unicode 空白後相等）→ c（章號 token 相等）依優先級；同一規則內沿 `new_toc` 向量順序（= idx 升冪）取第一命中。
**驗收標準**：
- [ ] 規則 a：`"第2章 破曉"` 對 `[(0,"序"),(3,"第1章 黎明"),(5,"第2章 破曉")]` → `Some((5, "第2章 破曉"))`（C8）
- [ ] 規則 b：全形空白 vs 半形空白命中（C9）；舊名去空白後為空字串 → 跳過規則 b（邊界）
- [ ] 規則 c：regex `第\s*([0-9０-９一二三四五六七八九十百千零〇两兩]+)\s*[章回節节卷]` 首捕獲組、全形數字正規化半形、字串比較；`第１２章` vs `第12章 風起雲湧` 命中（C10）；`第十二章` vs `第12章` 不命中（不互轉）；單邊無 token 不命中（邊界）
- [ ] 三規則皆不中 → `None`（C11 純函數半邊）
- [ ] 同名多章 → 取 idx 升冪第一個（邊界）
- [ ] 高優先規則命中即短路：規則 a 有命中時，縱使更低 idx 處存在規則 b/c 命中，仍回規則 a 者

### 步驟

#### 實作（`switch_source_core.rs`，比照 `evaluate_toc` 純 helper 先例）
- [ ] helper `strip_ws(&str) -> String`（filter `!c.is_whitespace()`）
- [ ] helper `chapter_number_token(&str) -> Option<String>`（regex 每次呼叫編譯即可 —— 換源一次一呼；全形 `０-９` map 到 `0-9`）
- [ ] 主函數三段依序掃描

#### 測試（RED 先行）
- [ ] 逐條覆蓋上列驗收標準，斷言具名 `(idx, name)` tuple

---

## TASK-b-03: `run_with_deps` 接線 —— 解析舊章名、傳遞 `progress_idx`

**需求追溯**：REQ-003, REQ-004
**測試重量建議**：full
**目標**：`SwitchSourceDeps` 新增 `fn current_chapter_name(&self, novel_id: i64) -> Result<Option<String>>`；`run_with_deps` 於 `evaluate_toc` 通過後解析舊章名、呼叫 `find_migration_target`、將結果傳入 `switch_source_tx(..., progress_idx)`，並在 `SwitchOutcome` 加 `progress: ProgressResolution`（`Migrated { idx, name }` / `Reset`）。
**驗收標準**：
- [ ] `RealDeps::current_chapter_name` = `library::facade::get_progress` 的 `chapter_index` → `library::facade::list_chapters` 中同 idx 者之 `name`；任一環節 `None` 即 `Ok(None)`
- [ ] fake `current_chapter_name` 回 `Some("第2章 破曉")` 且新 TOC 含 `(5, "第2章 破曉")` → fake 記錄到的 `progress_idx == Some(5)`、`SwitchOutcome.progress == Migrated { idx: 5, name: "第2章 破曉" }`（C8）
- [ ] fake 回 `None` 或不相干名 → `progress_idx == None`、`progress == Reset`、`new_progress_idx == 首 idx`（C11）
- [ ] fake 回 `Err(...)` → `run_with_deps` 仍 `Ok`、`Reset`、tx 有被呼叫（降級不 abort；邊界）
- [ ] 既有 `req005_s2/s3` abort-before-tx 測試原樣通過（FakeDeps 補新方法即可；C12）
- [ ] `select` 時序：`current_chapter_name` 的呼叫在 `evaluate_toc` 之後、`switch_source_tx` 之前

### 步驟

#### 型別與 trait
- [ ] `pub enum ProgressResolution { Migrated { idx: i64, name: String }, Reset }`（derive Debug、PartialEq）
- [ ] `SwitchOutcome` 加 `pub progress: ProgressResolution`（既有三欄不動）
- [ ] trait + RealDeps + 測試 FakeDeps 補 `current_chapter_name`

#### 接線
- [ ] `run_with_deps`：`let old_name = deps.current_chapter_name(novel_id).ok().flatten();` → `let target = old_name.as_deref().and_then(|n| find_migration_target(n, &toc));` → tx 傳 `target.as_ref().map(|(i, _)| *i)`
- [ ] `SwitchOutcome.new_progress_idx` = tx 回傳值（遷移時 = 命中 idx）

#### 測試（RED 先行）
- [ ] FakeDeps 加 `recorded_progress_idx: Mutex<Option<Option<i64>>>` 之類欄位以斷言 tx 收到的參數

---

## TASK-b-04: CLI / TUI 兩路徑呈現「已遷移 vs 已重置」

**需求追溯**：REQ-004
**測試重量建議**：full
**目標**：CLI handler（switch_source.rs:19）與 TUI toast（tui/switch_source.rs:134 的 Ok 分支）依 `SwitchOutcome.progress` 輸出兩態繁中訊息。
**驗收標準**：
- [ ] 遷移態訊息含「進度已遷移」與命中章名（例：`進度已遷移：第2章 破曉（idx 5）`）；不得以 `idx+1` 推導「第N章」（idx 非稠密，C8 註記）
- [ ] 重置態訊息含「進度重置」與首章名（可沿用既有 `new_first_chapter_name`）（C13）
- [ ] 訊息組裝抽成可單測的純函數（建議 `switch_source_core.rs` 內 `pub fn describe_progress(outcome: &SwitchOutcome) -> String`），CLI/TUI 共用；unit test 斷言兩態字串內容（C13, C14）
- [ ] CLI 既有成功訊息「進度重置到第 N 章」字樣被本準則明文取代 —— 若既有測試斷言該字樣（現況無），適配並記錄決策日誌

### 步驟

#### 實作
- [ ] `describe_progress` 純函數 + 兩態 unit test（RED 先行）
- [ ] CLI Ok 分支與 TUI toast 改用該函數輸出

#### 收尾
- [ ] `cargo test` 全綠；`grep -rnE "use crate::(catalog|library)::facade" src/catalog src/library` 零命中（C22）
