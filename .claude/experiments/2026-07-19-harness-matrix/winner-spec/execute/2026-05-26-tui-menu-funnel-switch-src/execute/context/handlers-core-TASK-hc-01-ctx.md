Goal: |
  C6 換源 atomicity（goal.md line 13）：
  換源期間若 (a) fetch_novel_info 失敗、(b) fetch_toc HTTP 失敗、(c) fetch_toc 8s timeout、
  (d) fetch_toc 回 0 章、(e) fetch_toc 所有 chapter name 落回 `Chapter {i+1}` fallback —
  任一發生則 abort，書架的 source URL、TOC、content cache、progress 全部維持換源前狀態。

  本 task 聚焦 (d) 與 (e) 兩類的純函式判定，抽出供 UT 不靠網路。

Requirements:
  REQ-005 換源 transaction（含失敗五類 abort）:
    描述: |
      換源走「catalog::facade::get_source → catalog::facade::fetch_novel_info →
      catalog::facade::fetch_toc → library::facade::switch_source_tx」；前三步任一失敗
      則 abort、不進 tx、書架狀態完全不變。

Scenarios:
  REQ-005 Scenario 4 失敗類 (d) — fetch_toc 回 0 章:
    Given: 新源規則寫錯但 HTTP 200，fetch_toc 回 Vec::new()
    When: 偵測到 chapters.is_empty()
    Then: 不進 tx；錯誤訊息「換源失敗：新源目錄為空，可能規則錯誤」
    And: 書架狀態不變

  REQ-005 Scenario 5 失敗類 (e) — `&` self bug fallback 全命中:
    Given: 新源 ruleToc 用了 `&@text` self selector，scraper.rs:117 落到 `format!("Chapter {}", i + 1)` fallback
    When: 偵測到 100% 章節名為 `Chapter {n}` pattern
    Then: 不進 tx；錯誤訊息「換源失敗：新源章節名解析全部失敗，疑為書源規則 bug」
    And: 書架狀態不變

Task:
  id: TASK-handlers-core-01
  title: 抽 evaluate_toc 純函式（給 UT）
  目標: |
    把「TOC 0 章」與「全 fallback chapter name」的判定抽成純函式
    evaluate_toc(&[ChapterMeta]) -> Result<(), AbortReason>，方便 UT 不靠網路。
  驗收標準:
    - pub fn evaluate_toc(toc: &[ChapterMeta]) -> Result<(), AbortReason>，AbortReason enum 至少含 EmptyToc / AllFallbackNames
    - "name == format!(\"Chapter {}\", c.index + 1)" 的判定跟 scraper.rs:117 的 fallback 一致
    - UNIT-1 / UNIT-2 / UNIT-3 三條 UT 全綠
  步驟:
    - 在 src/catalog/service/scraper.rs 把 fallback name 邏輯抽成 pub(crate) fn fallback_chapter_name(idx: i64) -> String（與 scraper.rs:117 同公式），讓 evaluate_toc 與 UT 都呼同一函式（drift-resistant）
    - 在 src/presentation/handlers/switch_source_core.rs 內定義 pub enum AbortReason { ... } + pub fn evaluate_toc，內部呼 catalog::service::scraper::fallback_chapter_name 比對
    - 寫 #[cfg(test)] mod tests：UNIT-1（空 vec → EmptyToc）、UNIT-2（全部呼 fallback_chapter_name 產生的字串 → AllFallbackNames）、UNIT-3（混合 → Ok(())）
    - cargo test handlers::switch_source_core::tests 全綠

Design:
  五類失敗判定點表（design.md line 270-279）:
    "(a) fetch_novel_info":
      判定位置: switch_source_core::run
      判定條件: catalog::facade::fetch_novel_info(...)? 任一 Err
    "(b) fetch_toc HTTP":
      判定位置: switch_source_core::run
      判定條件: catalog::facade::fetch_toc_with_timeout(...) Err 非 Elapsed
    "(c) fetch_toc timeout":
      判定位置: switch_source_core::run
      判定條件: tokio::time::timeout(Duration::from_secs(8), fetch_toc).await → Err(Elapsed)
    "(d) 0 章":
      判定位置: evaluate_toc(&toc)
      判定條件: toc.is_empty()
    "(e) 全 fallback name":
      判定位置: evaluate_toc(&toc)
      判定條件: |
        toc.iter().all(|c| c.name == scraper::fallback_chapter_name(c.index))，
        其中 fallback_chapter_name(idx) 為 scraper.rs:117 抽出的共用函式（drift-resistant）

  邊界規則: |
    部分 fallback 不算失敗：若 toc 內混合「真名」與「Chapter N fallback」（例如 50 章中只有 3 章 fallback），
    all(...) 評估為 false → evaluate_toc 回 Ok(())，視為成功；UI 不警告、不阻擋。
    對應 REQ-005 邊界與 UNIT-3。

  資料模型 — ChapterMeta（library/mod.rs:40）:
    struct: |
      pub struct ChapterMeta {
          pub index: i64,
          pub name: String,
          pub url: String,
      }

  AbortReason enum（design.md line 246）:
    位置: presentation/handlers/switch_source_core.rs
    內容: |
      EmptyToc / AllFallbackNames / FetchInfoFailed(_) / FetchTocFailed(_) / FetchTocTimeout（五類）

  scraper.rs:117 既有公式: |
    .unwrap_or_else(|| format!("Chapter {}", i + 1))
    其中 i 是 enumerate position；在第 120 行 cast 為 ChapterMeta.index: i as i64。
    抽出後 fallback_chapter_name(idx: i64) -> String 必須對 idx == c.index 仍滿足
    "name == format!(\"Chapter {}\", c.index + 1)" 不變式。

Test:
  UNIT-1 evaluate_toc 0 章 → EmptyToc:
    位置: presentation/handlers/switch_source_core::tests
    驗證點: evaluate_toc(&[]) 回 Err(AbortReason::EmptyToc)

  UNIT-2 evaluate_toc 全 fallback name → AllFallbackNames:
    位置: 同上
    驗證點: |
      用 scraper fallback 同公式（drift-resistant）構造 vec，全部 fallback；
      assert 回 Err(AllFallbackNames)。
      實作要求：用 catalog::service::scraper::fallback_chapter_name(idx) 產字串，
      不要在 test 內各自寫 literal "Chapter N"。

  UNIT-3 evaluate_toc 部分 fallback 不算失敗:
    位置: 同上
    驗證點: |
      「Chapter 1, 第 2 章 真名」混合；assert Ok(())。

  Drift-resistant 比對策略（test.md line 67-73）:
    - 在 catalog::service::scraper 內把 fallback 抽成 pub(crate) fn fallback_chapter_name(idx: i64) -> String
    - evaluate_toc 與 UNIT-2 都呼叫此函式比對；公式由單一來源產生

Constraints:
  - 在 src/catalog/service/scraper.rs 加 `pub(crate) fn fallback_chapter_name(idx: i64) -> String { format!("Chapter {}", idx + 1) }` — 與 scraper.rs:117 既有 fallback 表達式同步（drift-resistant）
  - 更新 scraper.rs:117 既有處 fetch_toc 內 `.unwrap_or_else(|| format!("Chapter {}", i + 1))` 改呼新 fn；注意 i 是 usize（enumerate）需 cast 為 i64 才能傳入 fallback_chapter_name(idx: i64)
  - 新建 src/presentation/handlers/switch_source_core.rs：
      AbortReason enum 五類：EmptyToc / AllFallbackNames / FetchInfoFailed(anyhow::Error) / FetchTocFailed(anyhow::Error) / FetchTocTimeout
      （anyhow::Error 比 String 更有資訊；本 task 只需 EmptyToc 與 AllFallbackNames 被 evaluate_toc 用到，其他三類保留給 TASK-hc-02 的 run() 用）
      pub fn evaluate_toc(toc: &[ChapterMeta]) -> Result<(), AbortReason>:
        - empty → EmptyToc
        - 全 fallback: `toc.iter().all(|c| c.name == crate::catalog::service::scraper::fallback_chapter_name(c.index))` → AllFallbackNames
        - 否則 Ok(())
  - 在 src/presentation/handlers/mod.rs 加 `pub mod switch_source_core;`
  - Layer invariant：switch_source_core 是 handler 不屬於 catalog/library；evaluate_toc 是純函式不碰網路、不碰 SQL
  - Cross-context：handler 可同時 import catalog::service::scraper 與 library::ChapterMeta（library 的 PL）；不破壞 layer rule
  - 既有 dead-code 警告（rule.rs 的 select_within / BackupReceipt.filename）應該保持原狀

Files:
  - src/catalog/service/scraper.rs（抽 fallback_chapter_name fn + 替換 line 117）
  - src/presentation/handlers/switch_source_core.rs（新檔，含 AbortReason enum + evaluate_toc fn + #[cfg(test)] mod tests 三條 UNIT）
  - src/presentation/handlers/mod.rs（pub mod switch_source_core;）

驗收:
  - cargo test handlers::switch_source_core::tests 3/3 全綠
  - 既有 cargo test 全綠（regression — 包含 catalog::service::rule::tests）
  - cargo build 過
  - layer invariant grep 不變（switch_source_core 是 handler 不屬於 catalog/library）
