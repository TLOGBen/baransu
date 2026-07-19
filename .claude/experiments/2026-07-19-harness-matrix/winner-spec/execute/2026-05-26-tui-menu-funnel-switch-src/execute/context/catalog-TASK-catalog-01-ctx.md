Goal: |
  C6 換源 atomicity：換源期間若 (a) fetch_novel_info 失敗、(b) fetch_toc HTTP 失敗、
  (c) fetch_toc 8s timeout、(d) fetch_toc 回 0 章、(e) fetch_toc 所有 chapter name 落回
  `Chapter {i+1}` fallback — 任一發生則 abort，書架的 source URL、TOC、content cache、
  progress 全部維持換源前狀態。
  C10 既有行為不破：cargo test（含 catalog::service::rule::tests 等既有測試）全綠；
  CLI 既有命令行為與輸出格式不變。
  本 task 範圍：catalog 端不動 dao；只在 facade 加「帶 timeout 的 fetch_toc 包裝」，
  給 switch_source_core 用，不影響既有 sync_toc 呼叫者。

Requirements:
  REQ-005: |
    換源 transaction（含失敗五類 abort）。
    描述：換源走「catalog::facade::get_source → catalog::facade::fetch_novel_info →
    catalog::facade::fetch_toc → library::facade::switch_source_tx」；前三步任一失敗則
    abort、不進 tx、書架狀態完全不變；tx 內 UPDATE novels + DELETE chapters +
    INSERT new chapters + UPDATE progress 為新 TOC 首章 idx；tx 失敗整體 rollback。

Scenarios:
  REQ-005-Scenario-3: |
    失敗類 (c) — fetch_toc 8s timeout
    - Given: 新源 toc 頁卡住超過 8s
    - When: catalog::facade::fetch_toc 觸發 timeout
    - Then: 不進 tx；錯誤訊息「換源失敗：目錄頁讀取逾時」
    - And: 書架狀態不變

Task:
  id: TASK-catalog-01
  title: catalog::facade::fetch_toc_with_timeout
  前置群組: 無（與 library 並行可）
  需求追溯: REQ-005（失敗類 c — 8s timeout）
  目標: |
    提供一個帶總 timeout 的 toc fetch，給 switch_source_core 用；
    不影響既有 catalog::facade::sync_toc 的呼叫者。
  驗收標準:
    - 新增 pub async fn fetch_toc_with_timeout(scraper: &Scraper, src: &BookSource, toc_url: &str, deadline: Duration) -> Result<Vec<ChapterMeta>>
    - 內部用 tokio::time::timeout(deadline, scraper.fetch_toc(src, toc_url)).await；Elapsed 變 Err(anyhow!("fetch_toc timeout after {:?}", deadline))
    - 既有 catalog::facade::sync_toc（line 53-64）行為不變（既有 sync 命令仍跑得通）
    - 既有 cargo test 全綠
  步驟:
    實作:
      - Read src/catalog/facade.rs 與 src/catalog/service/scraper.rs 確認 fetch_toc 簽名與呼叫者
      - 在 facade 加 fetch_toc_with_timeout 包裝（不動 service 層）
      - 加 use std::time::Duration
    測試:
      - 既有 cargo test catalog:: 全綠
      - UNIT-5 留給 TASK-hc-01/02 一起寫；本 task 只負責加 API + 驗證 build

Design:
  五類失敗的判定點（與本 task 相關）:
    - 類別 (c) fetch_toc timeout
    - 判定位置: switch_source_core::run
    - 判定條件: tokio::time::timeout(Duration::from_secs(8), fetch_toc).await → Err(Elapsed)
    - 對應錯誤訊息: 「換源失敗：目錄頁讀取逾時」
  其他相關判定點（context 用，本 task 不實作）:
    - (a) fetch_novel_info: catalog::facade::fetch_novel_info(...)? 任一 Err
    - (b) fetch_toc HTTP: catalog::facade::fetch_toc_with_timeout(...) Err 非 Elapsed
    - (d) 0 章: evaluate_toc(&toc)：toc.is_empty()
    - (e) 全 fallback name: evaluate_toc(&toc)：toc.iter().all(|c| c.name == scraper::fallback_chapter_name(c.index))
  錯誤處理策略（catalog::facade 層）:
    - propagate Scraper err；維持既有 anyhow chain
    - timeout 視為 catalog::facade 層的轉換點：Elapsed → anyhow!("fetch_toc timeout after {:?}", deadline)

Test:
  UNIT-5:
    位置: catalog/facade::tests 或 handlers/switch_source_core::tests
    驗證點: |
      用 tokio::time::sleep(11s) 包裝的 fake scraper 或直接
      tokio::time::timeout(Duration::from_secs(8), pending::<()>())；
      assert 8s 後變 Err 且訊息含 "timeout"
    本 task 範疇: |
      本 task 不必寫 UT；UNIT-5 留給 TASK-hc-01/02 一起寫。
      本 task 只負責加 API + 驗證 cargo build 過 + 既有 cargo test 全綠。

Constraints:
  - 在 src/catalog/facade.rs 新增 `pub async fn fetch_toc_with_timeout(scraper: &Scraper, src: &BookSource, toc_url: &str, deadline: Duration) -> Result<Vec<ChapterMeta>>`
  - 內部 `tokio::time::timeout(deadline, scraper.fetch_toc(src, toc_url)).await`；Elapsed → `Err(anyhow!("fetch_toc timeout after {:?}", deadline))`
  - 既有 `sync_toc`（line 53-64）行為不變
  - 既有 cargo test 全綠（C10 acceptance）
  - 不動 service 層 scraper.rs（task-hc-01 才會抽 fallback_chapter_name）
  - 簽名需加 use std::time::Duration
  - Cross-context layering: service/*.rs 不得 import rusqlite 或 dao 模組
  - facade 為 catalog context 唯一對外 entry；本 task 在此層加 API
  - 不在 catalog facade 呼叫 library::facade（C9 layer invariant）

Files:
  to_modify:
    - src/catalog/facade.rs  # 加 pub async fn fetch_toc_with_timeout + use std::time::Duration
  to_read_for_reference:
    - src/catalog/service/scraper.rs  # 確認 fetch_toc 簽名與行為（不修改）
    - src/catalog/mod.rs  # PL 類型：BookSource, ChapterMeta（不修改）
  acceptance_check:
    - cargo build  # 必須通過
    - cargo test catalog::  # 既有測試全綠
