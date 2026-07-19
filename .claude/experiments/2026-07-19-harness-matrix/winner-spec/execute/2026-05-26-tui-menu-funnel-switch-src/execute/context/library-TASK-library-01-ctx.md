Goal: |
  從 goal.md 提取與 TASK-library-01 直接相關的目標段落：

  - C5 書架換源：書架頁按 `s`，彈出單行 URL 輸入框；確認後 fetch + tx 完成（成功路徑）；
    成功後 `progress.chapter_index` 重置到新 TOC 第一章 idx 並顯示「進度已重置」訊息。
  - C6 換源 atomicity：換源期間若 (a) fetch_novel_info 失敗、(b) fetch_toc HTTP 失敗、
    (c) fetch_toc 8s timeout、(d) fetch_toc 回 0 章、(e) fetch_toc 所有 chapter name
    落回 `Chapter {i+1}` fallback — 任一發生則 abort，書架的 source URL、TOC、content
    cache、progress 全部維持換源前狀態。

  Scope (本 task 對應子項)：
  - `library/dao.rs`：新增 `update_book_source_tx`（內部 BEGIN→UPDATE
    novels.book_source_url+book_url→DELETE chapters→INSERT new chapters→UPDATE
    progress→COMMIT）。

Requirements: |
  ## REQ-005: 換源 transaction（含失敗五類 abort）

  **描述**：換源走「`catalog::facade::get_source` → `catalog::facade::fetch_novel_info` →
  `catalog::facade::fetch_toc` → `library::facade::switch_source_tx`」；前三步任一失敗則
  abort、不進 tx、書架狀態完全不變；tx 內 UPDATE novels + DELETE chapters + INSERT new
  chapters + UPDATE progress 為新 TOC 首章 idx；tx 失敗整體 rollback。

  ## REQ-007: 跨 context layer invariant 維持

  **描述**：實作完成後，`src/library/` 與 `src/catalog/` 內部不得 import 對方的 `facade`
  模組；所有跨 context 組合都在 `src/presentation/handlers/` 下進行。

Scenarios: |
  ## REQ-005 Scenarios

  **Scenario 1: TUI shelf 換源成功**
  - **Given** 書架 highlight 在 novel #1（原 source = X）；按 `s`
  - **When** 彈出輸入框，輸入新 book_url（已 import 過新源 Y）；確認
  - **Then** 依序呼叫 catalog::facade::get_source(Y) / fetch_novel_info(book_url) /
    fetch_toc(...) 都成功
  - **And** library::facade::switch_source_tx 開 tx 完成 UPDATE+DELETE+INSERT+progress
    update
  - **And** progress.chapter_index 為新 TOC 第一個 chapter 的 idx（注意不寫死 1）
  - **And** 回 ShelfScreen 顯示「已換源至 Y、進度已重置」

  **Scenario 2: 失敗類 (a) — fetch_novel_info HTTP 失敗**
  - **Then** **不**進 switch_source_tx；書架狀態完全不變

  **Scenario 3: 失敗類 (c) — fetch_toc 8s timeout**
  - **Then** **不**進 tx；書架狀態不變

  **Scenario 4: 失敗類 (d) — fetch_toc 回 0 章**
  - **Then** **不**進 tx；書架狀態不變

  **Scenario 5: 失敗類 (e) — `&` self bug fallback 全命中**
  - **Then** **不**進 tx；書架狀態不變

  ## REQ-007 Scenarios

  **Scenario 1: grep 驗證**
  - **Then** `grep -nE "use crate::catalog::facade|use crate::library::facade"
    src/library src/catalog` 零命中

  **Scenario 2: switch_source 跨 context 組合位置**
  - **Then** `switch_source_tx` 只接受純資料參數（new_src_url / new_book_url / &new_toc /
    new_progress_idx）、**不**呼叫 `catalog::facade::*`

Task: |
  ## TASK-library-01: dao::update_book_source_tx（純 tx）

  **需求追溯**：REQ-005, REQ-007
  **目標**：在 `library/dao.rs` 新增 `pub fn update_book_source_tx(db: &mut LibraryDb,
  args) -> Result<i64>`；單一 transaction 內 UPDATE novels + DELETE chapters + INSERT
  new chapters + UPDATE progress；任一步驟失敗 → rollback；回傳 `progress.chapter_index`
  設定為的新 idx。

  **驗收標準**：
  - [ ] 函式簽名：`pub fn update_book_source_tx(db: &mut LibraryDb, novel_id: i64,
        new_src_url: &str, new_book_url: &str, new_chapters: &[ChapterMeta]) -> Result<i64>`
  - [ ] tx 內順序：BEGIN → UPDATE novels SET book_source_url=?, book_url=? WHERE id=? →
        DELETE FROM chapters WHERE novel_id=? → INSERT INTO chapters(novel_id,idx,name,
        url,content) VALUES(?,?,?,?,NULL) for each → UPDATE progress SET chapter_index=?,
        scroll_offset=0, updated_at=now WHERE novel_id=? → COMMIT
  - [ ] `chapter_index` 設為 `new_chapters.first().unwrap().index`（不寫死 1；若 caller
        傳空 vec — caller 已過五類檢查不該空，但 fn 仍 defensive 回 Err）
  - [ ] INT-2 整合測試：故意製造 INSERT 失敗（unique violation 或 fk 違反）後 assert
        novels / chapters / progress 全部 revert 到呼叫前狀態
  - [ ] INT-3 確認非 cascade（progress row 未被 FK CASCADE 拔，因為我們用 UPDATE 不刪
        novels）
  - [ ] INT-4 progress.chapter_index 對應 new TOC 首章 idx（特別測 idx = 1 起的
        czbooks-like 情境）

  ### 步驟

  #### 實作
  - [ ] Read `src/library/dao.rs` 找到 `replace_toc`（catalog 端、不是 library 端） — 確認
        本 fn 在 library/dao.rs 的位置
  - [ ] 加 fn `update_book_source_tx`；用 `conn.transaction()?` 取得 rusqlite Transaction
  - [ ] 順序執行四階段；中途 `?` propagate err 自動 rollback（rusqlite Transaction Drop
        without commit = rollback）
  - [ ] 最後 `tx.commit()?` 與 `Ok(first_idx)`

  #### 測試
  - [ ] **INT-1**（成功）：用 tmp sqlite + 既有測試 fixture；先 `upsert_novel` +
        `replace_toc`(舊 TOC) + `save_progress`(chapter_index=10)；呼
        `update_book_source_tx`(novel_id, new_src, new_url, &new_toc with first.index=3,
        len=4)；assert 全部 6 點：novels.book_source_url 換新、**novels.book_url 換新**、
        `SELECT COUNT(*) FROM chapters WHERE novel_id=?` == 4、progress.chapter_index == 3、
        progress row id 同、progress.updated_at 已更新
  - [ ] **INT-2a/2b/2c/2d**（rollback × 4 step）：實作期選一個可注入失敗的具體手段；讓 4 個
        DB step（UPDATE novels / DELETE chapters / INSERT chapters / UPDATE progress）各
        失敗一次；4 個都要 assert DB 三表狀態完全等於呼叫前
  - [ ] **INT-3**（CASCADE 不觸發）：呼叫前 progress 存在 + chapter_index=10；呼成功的
        update_book_source_tx；assert progress row 仍在（id 同），只 chapter_index 改
  - [ ] **INT-4**（idx 對應）：new TOC first.index = 5 → assert progress.chapter_index = 5

  #### 驗證
  - [ ] `cargo test library::dao::update_book_source_tx` 全綠
  - [ ] `cargo test` 整體仍綠（既有測試不破）

Design: |
  ## 資料模型（與本 task 相關列）

  | 結構 / 欄位 | 位置 | 變更 | 說明 |
  |---|---|---|---|
  | `library::dao::update_book_source_tx` | `library/dao.rs` | 新增 fn | 純 tx：
    UPDATE novels + DELETE chapters + INSERT new chapters + UPDATE progress |
  | `library::facade::switch_source_tx` | `library/facade.rs` | 新增 fn | 對 dao 的薄包裝；
    不呼 catalog |
  | `progress.novel_id` FK | `library/dao.rs` schema（既有） | 已有 | `FOREIGN KEY
    (novel_id) REFERENCES novels(id) ON DELETE CASCADE`；本期 update_book_source_tx 用
    UPDATE 不刪 novels row，**故意**避開 CASCADE 以保留 progress row（再用 UPDATE 改
    chapter_index） |

  ### Schema（不變）
  `sources / novels / chapters / progress` 四表 schema 完全不動。換源只是改
  `novels.book_source_url + book_url`、重 `chapters`、`progress.chapter_index` 換新首章 idx。

  ## 五類失敗的判定點（本 task 不負責偵測，但供 caller 契約理解）

  | 類別 | 判定位置 | 判定條件 |
  |---|---|---|
  | (a) fetch_novel_info | `switch_source_core::run` | `catalog::facade::fetch_novel_info(...)?`
    任一 Err |
  | (b) fetch_toc HTTP | 同上 | `catalog::facade::fetch_toc_with_timeout(...)` Err 非 Elapsed |
  | (c) fetch_toc timeout | 同上 | `tokio::time::timeout(Duration::from_secs(8),
    fetch_toc).await → Err(Elapsed)` |
  | (d) 0 章 | `evaluate_toc(&toc)` | `toc.is_empty()` |
  | (e) 全 fallback name | `evaluate_toc(&toc)` | `toc.iter().all(|c| c.name ==
    scraper::fallback_chapter_name(c.index))` |

  **錯誤處理（本 task 對應列）**：
  - `library::facade::switch_source_tx`：rusqlite err → tx 自動 rollback（rusqlite
    `Transaction` Drop 行為）；err 包裝為 anyhow。

  ## API Sequence — tx 內部步驟（本 task 實作部分）

  ```
  Lib->>DB: BEGIN
  Lib->>DB: UPDATE novels SET book_source_url, book_url WHERE id=?
  Lib->>DB: DELETE FROM chapters WHERE novel_id=?
  Lib->>DB: INSERT INTO chapters(...) for each in toc
  Lib->>DB: UPDATE progress SET chapter_index = first_idx
  Lib->>DB: COMMIT
  Lib-->>Core: Ok(first_idx)
  ```

Test: |
  ## INT-1 `switch_source_tx` 成功路徑（library::facade + dao）

  tmp sqlite：先 add 一本書 + 假 TOC + progress(chapter_index=10)；呼 switch_source_tx 帶
  新 src + 新 book_url + 新 TOC (first.index=3, 共 4 章)；assert 全部以下：
  (i) novels.book_source_url 已換
  (ii) **novels.book_url 已換**
  (iii) `SELECT COUNT(*) FROM chapters WHERE novel_id=?` == 4
  (iv) progress.chapter_index == 3
  (v) progress row 同 id
  (vi) updated_at 已更新

  ## INT-2a tx rollback @ UPDATE novels

  注入手段：實作期挑一個可重現方式（例：先 PRAGMA foreign_keys=ON + UPDATE 觸發違反、或
  mock conn.execute 在第一句失敗）；assert 全 DB 三表狀態同呼叫前。

  ## INT-2b tx rollback @ DELETE chapters

  注入點挪到 DELETE 階段；assert 同上。

  ## INT-2c tx rollback @ INSERT chapters

  注入點挪到 INSERT 階段（最自然 — 例如預先在 chapters 塞一個 (novel_id, idx) 衝突 row
  配合 schema 加 UNIQUE，或在實作期決定具體手段）；assert 同上。

  ## INT-2d tx rollback @ UPDATE progress

  注入點挪到最後 progress UPDATE；assert 同上。

  > INT-2a~2d 的具體失敗注入手段保留給實作期決定（chapters schema 不一定有 UNIQUE 約束、需
  > Read dao.rs 確認；可用 `rusqlite::Connection::execute_batch` 在 tx 中途丟有效但語意錯
  > 的 SQL 強制失敗、或 mock 一個會在指定 step 失敗的 wrapper）。**重點是 4 個 DB step 任一
  > 失敗都必須 rollback、不能只測其中一個**。

  ## INT-3 `update_book_source_tx` 不會 cascade 掉 progress

  progress 是 FK CASCADE on novels；本 tx 用 UPDATE 不刪 novel row，assert progress row
  不消失（只 chapter_index / updated_at 改）。

  ## INT-4 `progress.chapter_index` 設為 list_chapters().first().idx

  新 TOC 第一個 ChapterMeta 的 index 不一定是 0 或 1（czbooks 的 i=1 例）；assert progress
  對應到該值，不寫死。

  ## 關鍵邊界（本 task 涵蓋）
  - **progress 對應到新 TOC 首章 idx（不寫死 1）** → REQ-005 Scenario 1 → INT-4 覆蓋

Constraints: |
  ## 函式簽名與位置
  - 在 `src/library/dao.rs` `impl LibraryDb` 內新增
    `pub fn update_book_source_tx(&mut self, novel_id: i64, new_src_url: &str,
    new_book_url: &str, new_chapters: &[ChapterMeta]) -> Result<i64>`

  ## tx 執行順序（不可變）
  BEGIN → UPDATE novels SET source_url=?, book_url=? WHERE id=?
        → DELETE FROM chapters WHERE novel_id=?
        → INSERT INTO chapters(novel_id,idx,name,url,content) for each in new_chapters
        → UPDATE progress SET chapter_index=?, scroll_offset=0, updated_at=? WHERE novel_id=?
        → COMMIT

  ## Transaction 機制
  - 用 `self.conn.transaction()?` 取 rusqlite Transaction
  - 中途 `?` propagate err 自動 rollback（rusqlite Transaction Drop without commit = rollback）

  ## Defensive 處理
  - `chapter_index` 設為 `new_chapters.first().expect("caller responsibility").index`
  - caller 應已過 evaluate_toc 不會傳空 vec — 但 fn 應 defensive：若
    `new_chapters.is_empty()` 回 `Err(anyhow!("update_book_source_tx: empty new_chapters
    — caller should have aborted"))`
  - 若 progress row 不存在（沒有讀過進度），INSERT 新的進度 row（chapter_index = first_idx,
    scroll_offset=0）— 與既有 save_progress 的 UPSERT 模式類同；簡化做法：用
    `INSERT OR REPLACE` 或先 SELECT 看在不在再 INSERT/UPDATE
  - 回傳 first_idx (Ok(i64))

  ## Layer invariant（唯讀規則）
  - 不動 catalog dao 或 catalog facade
  - `src/library/` 內不得 import `crate::catalog::facade`（REQ-007 / C9）
  - service 層不得 import rusqlite 或 dao 模組（CLAUDE.md layering rule）— 本 task 修改
    dao.rs 不違反此規則

  ## FK CASCADE 邊界
  - `progress.novel_id` 有 `FOREIGN KEY ... ON DELETE CASCADE`
  - 故意用 UPDATE novels（不刪 row）避開 CASCADE 以保留 progress row
  - INT-3 必須驗證 progress row id 在 tx 後仍然相同

  ## chapter_index 不寫死
  - 用 `new_chapters.first().index`，不寫死 0 或 1
  - czbooks 等源的 first idx = 1，但其他源可能不同（INT-4 驗）

  ## Test helper
  - 因為 sqlite open_in_memory 不需 `dirs` crate 與 `data_dir()`，新增
    `LibraryDb::open_in_memory() -> Result<Self>` 作為 test-only ctor（用
    `#[cfg(test)] pub fn ...`），對 production 無影響
  - INT 測試（`#[cfg(test)] mod tests`）：用 tmp sqlite（`Connection::open_in_memory` + 跑
    SCHEMA）。可參考既有 `LibraryDb::open()` 邏輯但走 in-memory

  ## 驗收
  - cargo build 過
  - `cargo test library::dao::` 全綠（含 INT-1/2/3/4 + 既有不破）
  - layer invariant grep 零命中

Files: |
  ## 預計修改
  - `src/library/dao.rs`
    - 新增 `pub fn update_book_source_tx(&mut self, novel_id: i64, new_src_url: &str,
      new_book_url: &str, new_chapters: &[ChapterMeta]) -> Result<i64>`
    - 新增 `#[cfg(test)] pub fn open_in_memory() -> Result<Self>` test-only ctor
    - 新增 `#[cfg(test)] mod tests`：INT-1 / INT-2a / INT-2b / INT-2c / INT-2d / INT-3 / INT-4

  ## 預計讀取（不修改）
  - `src/library/dao.rs`（既有 `LibraryDb::open()`、`upsert_novel`、`save_progress`、SCHEMA
    定義）— 參考 in-memory ctor、UPSERT 模式
  - `src/library/mod.rs`（PL：`ChapterMeta` 定義）
  - `src/catalog/dao.rs`（既有 `replace_toc` 模式參考；不修改）

  ## 不動
  - `src/catalog/` 全部
  - `src/library/facade.rs`（由 TASK-library-02 處理）
  - `src/library/service/`
  - `src/presentation/`
  - `src/backup/`
  - schema 本身（sources / novels / chapters / progress 四表結構不動）
