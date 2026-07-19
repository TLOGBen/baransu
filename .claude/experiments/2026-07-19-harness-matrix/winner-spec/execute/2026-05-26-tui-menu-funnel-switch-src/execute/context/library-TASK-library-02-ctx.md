Goal: |
  C5 書架換源：書架頁按 `s`，彈出單行 URL 輸入框；確認後 fetch + tx 完成（成功路徑）；
  成功後 `progress.chapter_index` 重置到新 TOC 第一章 idx 並顯示「進度已重置」訊息。

  C9 Layer invariant：實作後 `grep -nE "use crate::catalog::facade|use crate::library::facade" src/library src/catalog`
  （catalog/ 與 library/ 內部）零命中 — 兩 context 的 facade **不互呼**；
  跨 context 組合都在 `presentation/handlers/` 下。

  In-scope（節選與本 task 相關）：
  - `library/facade.rs`：新增 `switch_source_tx(db, novel_id, new_src_url, new_book_url, &new_toc) -> Result<i64>`（回新進度 idx）
  - （依需要）`list_chapters` / `get_novel_by_book_url` 補齊
  - 對應 happy-path test（library facade 跨 dao tx 一條）

Requirements:
  - REQ-005 換源 transaction（含失敗五類 abort）：
    換源走「catalog::facade::get_source → catalog::facade::fetch_novel_info → catalog::facade::fetch_toc → library::facade::switch_source_tx」；
    前三步任一失敗則 abort、不進 tx、書架狀態完全不變；
    tx 內 UPDATE novels + DELETE chapters + INSERT new chapters + UPDATE progress 為新 TOC 首章 idx；
    tx 失敗整體 rollback。
  - REQ-007 跨 context layer invariant 維持：
    實作完成後，src/library/ 與 src/catalog/ 內部不得 import 對方的 `facade` 模組；
    所有跨 context 組合都在 src/presentation/handlers/ 下進行。

Scenarios:
  REQ-005:
    - Scenario 1 (TUI shelf 換源成功):
        Given: 書架 highlight 在 novel #1（原 source = X）；按 `s`
        When: 彈出輸入框，輸入新 book_url（已 import 過新源 Y）；確認
        Then: 依序呼叫 catalog::facade::get_source(Y) / fetch_novel_info(book_url) / fetch_toc(...) 都成功
        And: library::facade::switch_source_tx 開 tx 完成 UPDATE+DELETE+INSERT+progress update
        And: progress.chapter_index 為新 TOC 第一個 chapter 的 idx（注意不寫死 1）
        And: 回 ShelfScreen 顯示「已換源至 Y、進度已重置」
    - Scenario 6 (CLI switch-source 子命令):
        Given: 終端執行 `novel-looker switch-source 1 <book_url> --source <src_url>`
        When: main.rs dispatch
        Then: 呼叫與 TUI shelf 同一個 use case fn
        And: atomicity 跟 Scenario 1-5 完全一致

  REQ-007:
    - Scenario 1 (grep 驗證):
        Given: 實作完成、merge 前
        When: 執行 `grep -nE "use crate::catalog::facade|use crate::library::facade" src/library src/catalog`
        Then: 零命中
    - Scenario 2 (switch_source 跨 context 組合位置):
        Given: 換源 use case 實作完成
        When: Read src/library/facade.rs
        Then: `switch_source_tx` 只接受純資料參數（new_src_url / new_book_url / &new_toc / new_progress_idx）、
              **不**呼叫 catalog::facade::*
    - Scenario 3 (handler 是組合點):
        Given: 換源 use case
        When: Read src/presentation/handlers/switch_source_core.rs
        Then: 該檔同時 import catalog::facade 與 library::facade、組合兩者

Task:
  id: TASK-library-02
  title: facade::switch_source_tx（純包裝）
  需求追溯: [REQ-005, REQ-007]
  前置: TASK-library-01（先有 update_book_source_tx 才能包裝）
  目標: |
    在 `library/facade.rs` 新增 `pub fn switch_source_tx(...)` 對
    `dao::update_book_source_tx` 的薄包裝；**不**呼任何 `catalog::*`。
    另新增 `pub fn get_novel_by_book_url(db: &LibraryDb, book_url: &str) -> Result<Option<Novel>>`
    給 SearchScreen 重複入架偵測；dao 端也需 `LibraryDb::get_novel_by_book_url`。
  驗收標準:
    - 函式簽名：`pub fn switch_source_tx(db: &mut LibraryDb, novel_id: i64, new_src_url: &str, new_book_url: &str, new_chapters: &[ChapterMeta]) -> Result<i64>`
    - 內部只一行：`db.update_book_source_tx(novel_id, new_src_url, new_book_url, new_chapters)`
    - 函式簽名：`pub fn get_novel_by_book_url(db: &LibraryDb, book_url: &str) -> Result<Option<Novel>>`
    - dao 端：`LibraryDb::get_novel_by_book_url(&self, book_url: &str) -> Result<Option<Novel>>`
    - `grep -nE "use crate::catalog" src/library/facade.rs src/library/dao.rs` 零命中
    - cargo build 過
    - `cargo test library::` 全綠
    - get_novel_by_book_url 短 UT：tmp db insert novel + 呼 fn → Some(novel)；不存在 book_url → None
  步驟:
    - 編輯 `src/library/facade.rs` 加 `switch_source_tx`（薄包裝，純 pass-through）
    - 編輯 `src/library/facade.rs` 加 `get_novel_by_book_url`
    - 編輯 `src/library/dao.rs` 加 `LibraryDb::get_novel_by_book_url`
    - 為 `get_novel_by_book_url` 寫 happy-path UT（Some / None 各一）
    - `cargo build` 過
    - `cargo test library::` 全綠
    - grep 驗證 layer invariant：`grep -nE "use crate::catalog" src/library/facade.rs src/library/dao.rs` 零命中

Design:
  資料模型（與本 task 相關）:
    - library::facade::switch_source_tx (新增):
        位置: library/facade.rs
        簽名: pub fn switch_source_tx(db: &mut LibraryDb, novel_id: i64, new_src_url: &str, new_book_url: &str, new_chapters: &[ChapterMeta]) -> Result<i64>
        說明: 對 dao 的薄包裝；不呼 catalog
    - library::facade::get_novel_by_book_url (新增；若無):
        位置: library/facade.rs
        簽名: pub fn get_novel_by_book_url(db: &LibraryDb, book_url: &str) -> Result<Option<Novel>>
        說明: 給 SearchScreen 重複入架偵測；純查詢、不破 invariant
    - library::dao::update_book_source_tx (前置 TASK-library-01 已實作):
        位置: library/dao.rs
        說明: 純 tx：UPDATE novels + DELETE chapters + INSERT new chapters + UPDATE progress
        本 task 只是 facade 包裝它

  Schema（不變）:
    sources / novels / chapters / progress 四表 schema 完全不動。
    換源只是改 novels.book_source_url + book_url、重 chapters、progress.chapter_index 換新首章 idx。

  API Sequence（本 task 在 sequence 中的位置）:
    Note over Core,Lib: 通過五類檢查後才進 tx
    Core->>Lib: switch_source_tx(db, novel_id, new_src, new_book_url, &toc)
    Lib->>DB: BEGIN
    Lib->>DB: UPDATE novels SET book_source_url, book_url WHERE id=?
    Lib->>DB: DELETE FROM chapters WHERE novel_id=?
    Lib->>DB: INSERT INTO chapters(...)+ for each in toc
    Lib->>DB: UPDATE progress SET chapter_index = first_idx
    Lib->>DB: COMMIT
    Lib-->>Core: Ok(first_idx)

  錯誤處理:
    library::facade::switch_source_tx 在 rusqlite err 時：
    tx 自動 rollback（rusqlite Transaction Drop 行為）；err 包裝為 anyhow。

Test:
  關聯 INT / UNIT（本 task 對應）:
    - INT-1 switch_source_tx 成功路徑（library::facade + dao）:
        tmp sqlite：先 add 一本書 + 假 TOC + progress(chapter_index=10)；
        呼 switch_source_tx 帶新 src + 新 book_url + 新 TOC (first.index=3, 共 4 章)；
        assert: (i) novels.book_source_url 已換 (ii) novels.book_url 已換
                (iii) SELECT COUNT(*) FROM chapters WHERE novel_id=? == 4
                (iv) progress.chapter_index == 3 (v) progress row 同 id
                (vi) updated_at 已更新
        備註：facade 是 pass-through 不必再寫獨立 INT；dao test passes 即足
    - get_novel_by_book_url UT（本 task 必寫）:
        tmp db insert novel + 呼 fn → Some(novel)
        不存在 book_url → None
  測試光譜:
    - Unit + Integration via cargo test + tmp sqlite
  E2E（手動 smoke；參考、本 task 無需執行）:
    - E2E-2 換源成功路徑
    - E2E-11 CLI switch-source
    - E2E-15 layer invariant grep
    - E2E-16 既有 cargo test 全綠

Constraints:
  - 在 src/library/facade.rs 新增 `pub fn switch_source_tx(db: &mut LibraryDb, novel_id: i64, new_src_url: &str, new_book_url: &str, new_chapters: &[ChapterMeta]) -> Result<i64>` — 純薄包裝
  - 內部一行：`db.update_book_source_tx(novel_id, new_src_url, new_book_url, new_chapters)`
  - 另新增 `pub fn get_novel_by_book_url(db: &LibraryDb, book_url: &str) -> Result<Option<Novel>>` 給 SearchScreen 重複入架偵測
  - dao 端也需 `LibraryDb::get_novel_by_book_url(&self, book_url: &str) -> Result<Option<Novel>>`
  - **不**呼任何 catalog::facade
  - grep src/library/facade.rs / src/library/dao.rs 不應含 `use crate::catalog`
  - 依賴 TASK-library-01（先有 update_book_source_tx 才能包裝）
  - Layer invariant: service/*.rs 不得 import rusqlite 或任何 dao 模組（本 task 改動的是 facade 與 dao，不涉及 service）
  - 跨 context facade 不互呼（本 task 嚴禁 import catalog::facade）

Files:
  modify:
    - src/library/facade.rs       # 加 switch_source_tx + get_novel_by_book_url
    - src/library/dao.rs          # 加 LibraryDb::get_novel_by_book_url
  read_for_context:
    - src/library/facade.rs       # 看既有 import 與函式佈局
    - src/library/dao.rs          # 看 LibraryDb 既有 method 佈局 + update_book_source_tx（TASK-library-01）位置
    - src/library/mod.rs          # 確認 Novel / ChapterMeta 型別 re-export
  test_files:
    - src/library/dao.rs          # get_novel_by_book_url 之 UT（同檔內 #[cfg(test)] 模組）
