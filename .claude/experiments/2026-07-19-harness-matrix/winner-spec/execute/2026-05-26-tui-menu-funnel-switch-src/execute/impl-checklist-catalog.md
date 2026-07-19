# Impl Checklist: catalog

## TASK-catalog-01: fetch_toc_with_timeout

- [x] `catalog::facade` 新增 `pub async fn fetch_toc_with_timeout(scraper: &Scraper, src: &BookSource, toc_url: &str, deadline: Duration) -> Result<Vec<ChapterMeta>>`（src/catalog/facade.rs:75-86；參數順序為 scraper-first，與 ctx Constraints 一致；與 checklist 模板中 src-first 順序相反，採 ctx 為準）
- [x] 內部用 `tokio::time::timeout(deadline, scraper.fetch_toc(src, toc_url)).await`；Elapsed → `Err(anyhow!("fetch_toc timeout after {:?}", deadline))`（src/catalog/facade.rs:81-85）
- [x] 既有 `catalog::facade::sync_toc` 行為不變（diff 證實 line 53-66 zero change）
- [x] 既有 `cargo test catalog::` 全綠（4 passed; 0 failed — rule::tests parse_alternatives / parse_attr_and_replace / parse_basic / extract_text_with_fallback）
- [ ] **UNIT-5** test.md：`tokio::time::timeout(8s, pending)` 確認 Elapsed 變 anyhow err — **本 task 範疇外，spec line 71-73 明示留給 TASK-hc-01/02 一起寫**
- Review 結果：advisory
- 備註：commit da83137 (worktree catalog)；layer invariant 通過（facade 內無 `library::facade::` 呼叫，僅出現於 doc comments）；產生一個 `fetch_toc_with_timeout is never used` warning，屬預期（hc 群 wire up 後消失，已於 spec line 47-48 預告）；impl-agent 提及 `use anyhow::{anyhow, Result}` 升級已落實（src/catalog/facade.rs:15）
