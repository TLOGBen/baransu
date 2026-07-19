Goal: |
  從 goal.md 摘要與 TASK-hc-02 直接相關的驗收標準：

  - **C5 書架換源**：書架頁按 `s`，彈出單行 URL 輸入框；確認後 fetch + tx
    完成（成功路徑）；成功後 `progress.chapter_index` 重置到新 TOC 第一章
    idx 並顯示「進度已重置」訊息。
  - **C6 換源 atomicity**：換源期間若 (a) fetch_novel_info 失敗、
    (b) fetch_toc HTTP 失敗、(c) fetch_toc 8s timeout、
    (d) fetch_toc 回 0 章、(e) fetch_toc 所有 chapter name 落回
    `Chapter {i+1}` fallback — 任一發生則 abort，書架的 source URL、TOC、
    content cache、progress 全部維持換源前狀態。
  - **C8 CLI switch-source**：`novel-looker switch-source <novel_id>
    <new_book_url> --source <new_source_url>` 跟 TUI shelf 的 `s` 鍵跑同一個
    use case 函式；成功 / 失敗判定與 atomicity 跟 C6 一致。

Requirements: |
  ## REQ-005: 換源 transaction（含失敗五類 abort）

  **描述**：換源走「`catalog::facade::get_source` →
  `catalog::facade::fetch_novel_info` → `catalog::facade::fetch_toc` →
  `library::facade::switch_source_tx`」；前三步任一失敗則 abort、不進 tx、
  書架狀態完全不變；tx 內 UPDATE novels + DELETE chapters + INSERT new
  chapters + UPDATE progress 為新 TOC 首章 idx；tx 失敗整體 rollback。

  ## REQ-007: 跨 context layer invariant 維持

  **描述**：實作完成後，`src/library/` 與 `src/catalog/` 內部不得 import
  對方的 `facade` 模組；所有跨 context 組合都在 `src/presentation/handlers/`
  下進行。

Scenarios: |
  ### REQ-005 Scenarios

  **Scenario 1: TUI shelf 換源成功**
  - **Given** 書架 highlight 在 novel #1（原 source = X）；按 `s`
  - **When** 彈出輸入框，輸入新 book_url（已 import 過新源 Y）；確認
  - **Then** 依序呼叫 catalog::facade::get_source(Y) /
    fetch_novel_info(book_url) / fetch_toc(...) 都成功
  - **And** library::facade::switch_source_tx 開 tx 完成
    UPDATE+DELETE+INSERT+progress update
  - **And** progress.chapter_index 為新 TOC 第一個 chapter 的 idx
    （注意不寫死 1）
  - **And** 回 ShelfScreen 顯示「已換源至 Y、進度已重置」

  **Scenario 2: 失敗類 (a) — fetch_novel_info HTTP 失敗**
  - **Given** 新 source URL 可達但詳情頁 5xx
  - **When** catalog::facade::fetch_novel_info 回 Err
  - **Then** **不**進 switch_source_tx
  - **And** 顯示錯誤訊息「換源失敗：取得詳情頁失敗（HTTP 5xx）」
  - **And** 書架狀態完全不變

  **Scenario 3: 失敗類 (c) — fetch_toc 8s timeout**
  - **Given** 新源 toc 頁卡住超過 8s
  - **When** catalog::facade::fetch_toc 觸發 timeout
  - **Then** **不**進 tx；錯誤訊息「換源失敗：目錄頁讀取逾時」
  - **And** 書架狀態不變

  **Scenario 4: 失敗類 (d) — fetch_toc 回 0 章**
  - **Given** 新源規則寫錯但 HTTP 200，fetch_toc 回 Vec::new()
  - **When** 偵測到 chapters.is_empty()
  - **Then** **不**進 tx；錯誤訊息「換源失敗：新源目錄為空，可能規則錯誤」
  - **And** 書架狀態不變

  **Scenario 5: 失敗類 (e) — `&` self bug fallback 全命中**
  - **Given** 新源 ruleToc 用了 `&@text` self selector，scraper.rs:117 落到
    `format!("Chapter {}", i + 1)` fallback
  - **When** 偵測到 100% 章節名為 `Chapter {n}` pattern
  - **Then** **不**進 tx；錯誤訊息「換源失敗：新源章節名解析全部失敗，
    疑為書源規則 bug」
  - **And** 書架狀態不變

  **Scenario 6: CLI switch-source 子命令**
  - **Given** 終端執行 `novel-looker switch-source 1
    https://czbooks.net/n/abc --source https://czbooks.net`
  - **When** main.rs dispatch
  - **Then** 呼叫與 TUI shelf 同一個 use case fn
    （`handlers::switch_source_core::run` 之類）
  - **And** 成功 / 失敗判定與 atomicity 跟上述 Scenario 1-5 完全一致
  - **And** 終端輸出純文字結果（成功：「✓ 已換源 #1 至 ...，進度重置到第 N
    章」；失敗：上述對應錯誤訊息）

  ### REQ-007 Scenarios

  **Scenario 1: grep 驗證**
  - **Given** 實作完成、merge 前
  - **When** 執行 goal.md C9 列出的 grep 命令
    （`grep -nE "use crate::catalog::facade|use crate::library::facade"
    src/library src/catalog`）
  - **Then** 零命中（backup 的 conformist 例外不在此 grep 範圍內，
    本期 backup 不動）
  - **And** test.md E2E-15 使用同一條命令

  **Scenario 2: switch_source 跨 context 組合位置**
  - **Given** 換源 use case 實作完成
  - **When** Read `src/library/facade.rs`
  - **Then** `switch_source_tx` 只接受純資料參數（new_src_url /
    new_book_url / &new_toc / new_progress_idx）、**不**呼叫
    `catalog::facade::*`

  **Scenario 3: handler 是組合點**
  - **Given** 換源 use case
  - **When** Read `src/presentation/handlers/switch_source_core.rs`
    （共用 use case）
  - **Then** 該檔同時 import `catalog::facade` 與 `library::facade`、
    組合兩者

Task: |
  ## TASK-handlers-core-02: switch_source_core::run（TUI + CLI 共用）

  **需求追溯**：REQ-005, REQ-007, REQ-001（CLI dispatch）
  **目標**：在 `presentation/handlers/switch_source_core.rs` 提供
  `pub async fn run(ctx, args) -> Result<SwitchOutcome>`；TUI 的
  SwitchSourceScreen 確認後與 CLI 的 `switch-source` handler 都呼此函式。

  **驗收標準**：
  - [ ] 函式簽名：`pub async fn run(ctx: &mut AppContext, novel_id: i64,
    new_src_url: &str, new_book_url: &str) -> Result<SwitchOutcome>`
  - [ ] `SwitchOutcome { new_progress_idx: i64, chapter_count: usize,
    new_first_chapter_name: String }`
  - [ ] 內部依序：`catalog::facade::get_source` →
    `catalog::facade::fetch_novel_info` →
    `catalog::facade::fetch_toc_with_timeout(8s)` → `evaluate_toc` →
    `library::facade::switch_source_tx`
  - [ ] 五類失敗各自包裝為具體錯誤訊息（zh-TW），caller 拿 `Err` 直接顯示
  - [ ] 不修改 catalog / library facade（純組合）
  - [ ] `grep -nE "use crate::catalog|use crate::library"
    src/presentation/handlers/switch_source_core.rs` 顯示同時 import
    兩 context — 確認 handler 是組合點

  ### 步驟

  #### 實作
  - [ ] 寫 `src/presentation/handlers/switch_source_core.rs`：定義
    SwitchOutcome、AbortReason、`run` fn
  - [ ] 呼叫順序與五類錯誤處理依 design.md sequence diagram
  - [ ] 用 `anyhow::Context::context` 加中文錯誤訊息

  #### 測試
  - [ ] UNIT-1/2/3（evaluate_toc）已在 TASK-handlers-core-01 完成
  - [ ] **不**寫端到端 run() 的 UT（會碰網路）；E2E 階段手動驗

  #### 驗證
  - [ ] `cargo build` 過
  - [ ] grep 驗 layer invariant 仍維持（library/catalog 內部不互呼）

Design: |
  ### 換源 use case sequence（TUI 與 CLI 共用）

  ```mermaid
  sequenceDiagram
    participant Caller as Caller (TUI shelf 或 CLI handler)
    participant Core as switch_source_core::run
    participant Cat as catalog::facade
    participant Scr as Scraper
    participant Lib as library::facade
    participant DB as LibraryDb (rusqlite)

    Caller->>Core: run(novel_id, new_src_url, new_book_url, &ctx)
    Core->>Cat: get_source(db, new_src_url)
    Cat->>DB: SELECT FROM sources
    DB-->>Cat: BookSource
    Cat-->>Core: Some(BookSource)
    alt 找不到書源
      Cat-->>Core: None → Err
      Core-->>Caller: Err(no such source)
    end

    Core->>Cat: fetch_novel_info(src, new_book_url)
    Cat->>Scr: scraper.fetch_info(src, book_url)
    Scr-->>Cat: Novel info or Err
    Cat-->>Core: Result Novel
    alt (a) info 失敗
      Core-->>Caller: Err(fetch_novel_info failed)
    end

    Core->>Cat: fetch_toc(src, toc_url, 8s timeout)
    Cat->>Scr: scraper.fetch_toc(...)
    Scr-->>Cat: Vec ChapterMeta or Err
    Cat-->>Core: Result Vec ChapterMeta
    alt (b) HTTP fail / (c) 8s timeout
      Core-->>Caller: Err(toc fetch failed)
    end
    alt (d) 0 章
      Core-->>Caller: Err(empty TOC)
    end
    alt (e) 100% chapter name 是 "Chapter {n}" fallback
      Core-->>Caller: Err(name parse all fallback)
    end

    Note over Core,Lib: 通過五類檢查後才進 tx
    Core->>Lib: switch_source_tx(db, novel_id, new_src, new_book_url, &toc)
    Lib->>DB: BEGIN
    Lib->>DB: UPDATE novels SET book_source_url, book_url WHERE id=?
    Lib->>DB: DELETE FROM chapters WHERE novel_id=?
    Lib->>DB: INSERT INTO chapters(...)+ for each in toc
    Lib->>DB: UPDATE progress SET chapter_index = first_idx
    Lib->>DB: COMMIT
    Lib-->>Core: Ok(first_idx)
    Core-->>Caller: Ok(SwitchOutcome { new_progress_idx, chapter_count })
  ```

  ### 資料模型（與此 task 相關）

  | 結構 / 欄位 | 位置 | 變更 | 說明 |
  |---|---|---|---|
  | `SwitchOutcome` struct |
    `presentation/handlers/switch_source_core.rs` | 新增 |
    `{ new_progress_idx: i64, chapter_count: usize,
    new_first_chapter_name: String }` |
  | `AbortReason` enum |
    `presentation/handlers/switch_source_core.rs` | 新增 |
    `EmptyToc / AllFallbackNames / FetchInfoFailed(_) /
    FetchTocFailed(_) / FetchTocTimeout`（五類） |

  ### 錯誤處理策略（與此 task 相關層級）

  | 層 | 錯誤類型 | 處理 |
  |---|---|---|
  | Scraper | HTTP / 解析 / timeout | 回 `Result::Err`；不 panic |
  | catalog::facade | propagate Scraper err | 維持既有 anyhow chain |
  | switch_source_core | 五類 abort 偵測 | 各自轉成具體錯誤訊息（zh-TW）；
    **不進 library::facade** |
  | **switch_source_core invariant** | abort 五類任一觸發時 |
    **保證不呼叫 `library::facade::switch_source_tx`；
    novels / chapters / progress / sources 四表狀態完全等於 run() 呼叫前**
    （這是 REQ-005 Scenario 2-5 與 goal C6 的核心契約） |
  | library::facade::switch_source_tx | rusqlite err | tx 自動 rollback
    （rusqlite `Transaction` Drop 行為）；err 包裝為 anyhow |
  | CLI handler | 拿到 Result::Err | 透過 main.rs 的 `Result<()>`
    propagate → exit 1 + stderr 印錯誤 |

  ### 五類失敗的判定點

  | 類別 | 判定位置 | 判定條件 |
  |---|---|---|
  | (a) fetch_novel_info | `switch_source_core::run` |
    `catalog::facade::fetch_novel_info(...)?` 任一 Err |
  | (b) fetch_toc HTTP | 同上 |
    `catalog::facade::fetch_toc_with_timeout(...)` Err 非 Elapsed |
  | (c) fetch_toc timeout | 同上 |
    `tokio::time::timeout(Duration::from_secs(8),
    fetch_toc).await → Err(Elapsed)` |
  | (d) 0 章 | `evaluate_toc(&toc)` | `toc.is_empty()` |
  | (e) 全 fallback name | `evaluate_toc(&toc)` |
    `toc.iter().all(|c| c.name == scraper::fallback_chapter_name(c.index))`
    ，其中 `fallback_chapter_name(idx)` 為 scraper.rs:117 抽出的共用函式
    （drift-resistant） |

  **邊界 — 部分 fallback 不算失敗**：若 `toc` 內混合「真名」與「`Chapter N`
  fallback」（例如 50 章中只有 3 章 fallback），`all(...)` 評估為 false →
  `evaluate_toc` 回 `Ok(())`，視為成功；UI 不警告、不阻擋。

Test: |
  ### 與此 task 相關的測試項目

  - **UNIT-1 / UNIT-2 / UNIT-3 evaluate_toc**：已在 TASK-handlers-core-01
    完成；本 task 不重複新增。
  - **UNIT-5 fetch_toc_with_timeout 觸發 8s Elapsed**：
    `catalog/facade::tests` 或 `handlers/switch_source_core::tests`；
    用 `tokio::time::sleep(11s)` 包裝的 fake scraper 或直接
    `tokio::time::timeout(Duration::from_secs(8), pending::<()>())`；
    assert 8s 後變 Err 且訊息含 "timeout"。
  - **不寫**端到端 `run()` 的 UT（會碰網路）；E2E 階段手動驗
    （E2E-11 / E2E-12 對應 REQ-005 Scenario 6 + C8）。
  - **layer invariant grep**：對應 REQ-007 → E2E-15 覆蓋。

  ### 關鍵邊界條件（與此 task 直接相關）

  - **空 TOC（0 章）** → REQ-005 Scenario 4 → UNIT-1（已在 hc-01）+ E2E-5
  - **全 fallback name TOC** → REQ-005 Scenario 5 → UNIT-2（已在 hc-01）
    + E2E-6
  - **部分 fallback name TOC（不算失敗）** → REQ-005 邊界 →
    UNIT-3（已在 hc-01）

Constraints:
  - 函式簽名固定：`pub async fn run(ctx: &mut AppContext, novel_id: i64,
    new_src_url: &str, new_book_url: &str) -> Result<SwitchOutcome>`。
  - 必須新增 `pub struct SwitchOutcome { pub new_progress_idx: i64,
    pub chapter_count: usize, pub new_first_chapter_name: String }`。
  - 流程順序（依 design sequence）：
    1. `let src = catalog::facade::get_source(&ctx.db, new_src_url)?
       .ok_or_else(|| anyhow!("找不到書源 {}", new_src_url))?;`
    2. `let novel = catalog::facade::fetch_novel_info(&ctx.scraper, &src,
       new_book_url).await
       .context("換源失敗：取得詳情頁失敗 (a)")?;` — FetchInfoFailed 路徑
    3. `let toc_url = novel.toc_url.unwrap_or_else(|| new_book_url
       .to_string());` — 用 toc_url 或詳情頁 url
    4. `let toc = catalog::facade::fetch_toc_with_timeout(&ctx.scraper,
       &src, &toc_url, Duration::from_secs(8)).await
       .context("換源失敗：目錄頁讀取失敗或逾時 (b/c)")?;`
    5. `evaluate_toc(&toc).map_err(|reason| anyhow!("換源失敗：{:?}",
       reason))?;` — EmptyToc / AllFallbackNames 路徑
    6. `library::facade::switch_source_tx(&mut ctx.db, novel_id,
       new_src_url, new_book_url, &toc)?;`
    7. 回 `SwitchOutcome { first_idx, toc.len(), first chapter name }`
  - 不在 catalog::facade 或 library::facade 內呼跨 context — 全在
    handler 層組合。
  - `grep -nE "use crate::catalog|use crate::library"
    src/presentation/handlers/switch_source_core.rs` 應同時命中兩 context
    （handler 是組合點）。
  - 任一階段失敗都在進 `library::facade::switch_source_tx` 之前 propagate
    Err（不會走到 tx），spec C6 atomicity 保證。
  - 不修改 catalog / library facade（純組合）。
  - 不寫端到端 `run()` 的 UT（要碰網路）；evaluate_toc 的 UT 已在 hc-01。
  - 五類失敗各自包裝為具體錯誤訊息（zh-TW），caller 拿 `Err` 直接顯示。
  - 用 `anyhow::Context::context` 加中文錯誤訊息。

  ### 驗收
  - `cargo build` 過
  - handler 內既有 evaluate_toc UT 仍綠
  - grep 命中兩 context import

Files:
  - src/presentation/handlers/switch_source_core.rs  # 在 hc-01 已建立的檔案上加 SwitchOutcome + run
