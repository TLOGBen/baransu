# Impl Checklist: library

## TASK-library-01: dao::update_book_source_tx + INT-1~4

- [x] `library/dao.rs` 新增 `pub fn update_book_source_tx(&mut self, novel_id: i64, new_src_url: &str, new_book_url: &str, new_chapters: &[ChapterMeta]) -> Result<i64>` （dao.rs:235-243）
- [x] tx 內順序：BEGIN → UPDATE novels(source_url, book_url) → DELETE chapters WHERE novel_id → INSERT new chapters → UPSERT progress(chapter_index=first_idx, scroll_offset=0, updated_at=now) → COMMIT （dao.rs:282-326）
- [x] `chapter_index` 設為 `new_chapters.first().unwrap().index`（不寫死 1）；空 vec 回 Err （dao.rs:274-279）
- [x] **INT-1** 成功路徑 assert 7 點（含 returned/source_url/book_url/chapters count/chapter_index/scroll_offset/progress row PK/updated_at）（dao.rs:505-567）
- [x] **INT-2a/2b/2c/2d** 4 個 DB step 各失敗一次 rollback 完整（dao.rs:593-611 + 571-591 共用 helper + Snapshot equality）
- [x] **INT-3** UPDATE 不刪 novels row → progress row 不被 CASCADE（dao.rs:615-640；PRAGMA foreign_keys=ON 由 open_in_memory 啟用）
- [x] **INT-4** new TOC first.index=5 → progress.chapter_index=5（dao.rs:644-663）
- [x] `cargo test library::dao` 8/8 + `cargo test` 全集 15/15 全綠
- Review 結果：advisory
- 備註：所有 7 條 acceptance 全綠。Fault injection 用 `#[cfg(test)] update_book_source_tx_with_fault` + 內部 inner helper（dao.rs:249-264, 266-327），4 個 step 在實際執行 SQL 後注入 Err，rollback 由 tx Drop 觸發；非 vacuous。Column 用 `source_url`（schema 對齊，ctx 提到 `book_source_url` 屬 prose drift）。UPSERT progress 比 ctx 描述的 plain UPDATE 更穩（cover defensive case「progress row 不存在」— 與 Constraints 段對齊）。Layer invariant grep 零命中。PRAGMA foreign_keys=ON 僅在 open_in_memory 啟用，production 維持 default（已於程式碼註解說明）— 建議後續 task 評估 production 是否也啟用。

## TASK-library-02: facade::switch_source_tx pass-through

- [x] `library/facade.rs` 新增 `pub fn switch_source_tx(db: &mut LibraryDb, novel_id, new_src_url, new_book_url, new_chapters) -> Result<i64>` 對 dao::update_book_source_tx 的薄包裝（facade.rs:45-53；body 單行 pass-through）
- [x] `grep -nE "use crate::catalog" src/library/facade.rs src/library/dao.rs` 零命中（exit=1 verified）
- [x] `library/facade.rs` 新增 `pub fn get_novel_by_book_url(db: &LibraryDb, book_url: &str) -> Result<Option<Novel>>`（facade.rs:33-35；SearchScreen 重複入架偵測）
- [x] dao 端對應方法也新增（dao.rs:154-175；query_row + optional() 與 get_novel 同形）
- [x] `cargo build` + `cargo test library::` 全綠（10/10 通過，含新 2 UT：returns_some_when_present / returns_none_when_absent）
- Review 結果：advisory
- 備註：5 條 AC 逐條核對全綠。switch_source_tx body 嚴格 pass-through（單行 `db.update_book_source_tx(...)`、無 logging / 無 validation / 無業務邏輯），符合「不藏業務邏輯」要求。UT Some 路徑檢核 8 個欄位（id / source_url / book_url / name / author / intro / cover_url / toc_url），over-spec 但無害。doc comment 明確標示「caller (presentation handler) 負責 catalog pipeline 與五類 pre-check」，REQ-007 layer invariant 內顯。cargo build 兩個 unused warning（switch_source_tx / get_novel_by_book_url）符合預期（presentation handlers 將於後續 TASK wire up）。
