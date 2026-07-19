Goal: |
  讓使用者在不離開 TUI 的前提下完成「搜尋蒐書 → 入架 → 閱讀 → 換源」整段 funnel。
  本 task 相關 Criteria：
  - C5 書架換源：書架頁按 `s`，彈出單行 URL 輸入框；確認後 fetch + tx 完成（成功路徑）；
    成功後 `progress.chapter_index` 重置到新 TOC 第一章 idx 並顯示「進度已重置」訊息。
  - C6 換源 atomicity：換源期間若 (a) fetch_novel_info 失敗、(b) fetch_toc HTTP 失敗、
    (c) fetch_toc 8s timeout、(d) fetch_toc 回 0 章、(e) fetch_toc 所有 chapter name
    落回 `Chapter {i+1}` fallback — 任一發生則 abort，書架的 source URL、TOC、content
    cache、progress 全部維持換源前狀態。
  Scope 相關：`presentation/handlers/tui/switch_source.rs` 屬於本期 In scope。
  Out of scope：async fetch 改造、TUI 互動 unit test（ratatui 0.28 無友善 TestBackend
  stateful screen 機制）。

Requirements:
  REQ-005:
    描述: |
      換源走「`catalog::facade::get_source` → `catalog::facade::fetch_novel_info` →
      `catalog::facade::fetch_toc` → `library::facade::switch_source_tx`」；前三步任一失敗
      則 abort、不進 tx、書架狀態完全不變；tx 內 UPDATE novels + DELETE chapters +
      INSERT new chapters + UPDATE progress 為新 TOC 首章 idx；tx 失敗整體 rollback。

Scenarios:
  REQ-005-Scenario-1:
    name: "TUI shelf 換源成功"
    Given: 書架 highlight 在 novel #1（原 source = X）；按 `s`
    When: 彈出輸入框，輸入新 book_url（已 import 過新源 Y）；確認
    Then: |
      - 依序呼叫 catalog::facade::get_source(Y) / fetch_novel_info(book_url) / fetch_toc(...) 都成功
      - library::facade::switch_source_tx 開 tx 完成 UPDATE+DELETE+INSERT+progress update
      - progress.chapter_index 為新 TOC 第一個 chapter 的 idx（注意不寫死 1）
      - 回 ShelfScreen 顯示「已換源至 Y、進度已重置」

Task:
  id: TASK-tui-05
  group: tui
  title: "SwitchSourceScreen — 單行 URL 輸入框 + 確認"
  目標: |
    跳出 modal-style 單行輸入框收新 book_url；輸入後問來源 URL；用兩個 SingleLineInput
    依序收，Tab 切換。Enter 後 call `switch_source_core::run`；成功 → ShelfScreen with
    toast；失敗 → ShelfScreen with error toast。
  驗收標準:
    - "`src/presentation/handlers/tui/switch_source.rs` 存在；`impl Screen for SwitchSourceScreen`"
    - "輸入：顯示兩行 prompt — 第一行「新書 URL」、第二行「新源 URL」；用兩個 SingleLineInput 依序收，Tab 切換"
    - "Esc → ShelfScreen（不執行任何 catalog/library 呼叫）"
    - "Enter 在第二行 → 同步 await `switch_source_core::run(...)`"
    - "成功：Transition::To(ShelfScreen::with_toast(format!(\"已換源至 ...，進度重置到第 {} 章: {}\", outcome.new_progress_idx + 1, outcome.new_first_chapter_name)))"
    - "失敗：Transition::To(ShelfScreen::with_toast(format!(\"換源失敗：{:#}\", err)))"
    - "書架狀態不變（由 switch_source_core 保證、SwitchSourceScreen 本身不寫 DB）"
  步驟:
    - 寫檔
    - 用 `tui::widgets::SingleLineInput` × 2
    - 確認顯示為「modal 樣式」（用 `Clear` widget 蓋背景 + 居中 layout）
    - Tab/Esc/Enter 行為靠 E2E 手動觀察、不寫獨立 UNIT（input 本身有 UNIT-6 覆蓋；雙欄狀態機簡單到不值得獨立 UT）
    - E2E-2 / E2E-3 / E2E-5 / E2E-6 手動跑（E2E-4 timeout 較難設、用 UNIT-5 自動覆蓋，本 screen 不重複跑）

Design:
  架構位置: |
    `src/presentation/handlers/tui/switch_source.rs` 為新檔，屬 tui handler 等價層。
    SwitchSourceScreen 為 modal-style 螢幕：由 ShelfScreen 按 `s` 鍵 transition 進入，
    Esc 或完成後 transition 回 ShelfScreen（成功/失敗都帶 toast）。

  data_model:
    SwitchOutcome:
      位置: presentation/handlers/switch_source_core.rs
      欄位:
        new_progress_idx: i64
        chapter_count: usize
        new_first_chapter_name: String
      說明: switch_source_core::run 成功返回此結構；toast 顯示用其欄位格式化訊息。
    AbortReason:
      位置: presentation/handlers/switch_source_core.rs
      variants:
        - EmptyToc
        - AllFallbackNames
        - FetchInfoFailed(_)
        - FetchTocFailed(_)
        - FetchTocTimeout
      說明: 五類 abort；對 SwitchSourceScreen 來說只需把 Err 字串化丟到 toast。
    ShelfScreen::with_highlight:
      位置: presentation/handlers/tui/shelf.rs
      簽名: "(initial_highlight: Option<i64>, initial_toast: Option<String>) -> ShelfScreen"
      說明: 給「重複入架」與「換源完成/失敗」場景帶 hint；本 task 呼叫時用 None highlight + Some(toast)。

  sequence_換源_use_case: |
    Caller (TUI shelf / SwitchSourceScreen / CLI handler)
      → Core (switch_source_core::run(novel_id, new_src_url, new_book_url, &ctx))
        → catalog::facade::get_source(db, new_src_url)
          - 失敗：Err(no such source) → 回 Caller
        → catalog::facade::fetch_novel_info(src, new_book_url)
          - (a) Err → Caller
        → catalog::facade::fetch_toc(src, toc_url, 8s timeout)
          - (b) HTTP Err → Caller
          - (c) Elapsed → Caller
        → evaluate_toc(&toc)
          - (d) toc.is_empty() → Err(EmptyToc) → Caller
          - (e) all fallback names → Err(AllFallbackNames) → Caller
        → library::facade::switch_source_tx(db, novel_id, new_src, new_book_url, &toc)
          - BEGIN → UPDATE novels SET book_source_url, book_url WHERE id=?
          - DELETE FROM chapters WHERE novel_id=?
          - INSERT INTO chapters(...) for each in toc
          - UPDATE progress SET chapter_index = first_idx
          - COMMIT
          - 任一 step 失敗 → tx auto rollback
        ← Ok(SwitchOutcome { new_progress_idx, chapter_count, new_first_chapter_name })
      ← Result<SwitchOutcome>

  invariant: |
    switch_source_core 保證 atomicity——五類 abort 任一觸發時不呼叫
    library::facade::switch_source_tx；novels / chapters / progress / sources 四表狀態
    完全等於 run() 呼叫前。SwitchSourceScreen 本身不直接寫 DB，僅 await core 並依
    Result 分流 transition。

  入口流程: |
    flowchart 片段（design.md）：
      ShelfS --s--> SwS[SwitchSourceScreen URL 輸入]
      SwS --Esc--> ShelfS
      SwS --Enter--> SwCore[switch_source_core::run]
      SwCore --成功--> ShelfReset[ShelfScreen toast 換源完成]
      SwCore --abort 五類--> ShelfErr[ShelfScreen toast 錯誤訊息]

Test:
  本_task_直接相關:
    - E2E-2 換源成功路徑：shelf 按 s → reader 進新源第一章（C5, C6）— 手動
    - E2E-3 換源 (a) fetch_novel_info 失敗：shelf 按 s，輸入不可達 URL → shelf 顯示錯誤、書本狀態未變 — 手動
    - E2E-5 換源 (d) 0 章：輸入解析後 TOC 0 章的 book_url → shelf 顯示「目錄為空」、書本狀態未變 — 手動
    - E2E-6 換源 (e) 全 fallback name：輸入觸發 `&@text` bug 的源 → shelf 顯示「章節名全部 fallback」、書本狀態未變 — 手動
  非本_task_直接覆蓋但相關:
    - E2E-4 換源 (c) 8s timeout：UNIT-5 自動覆蓋（本 screen 不重複跑）
    - UNIT-6 SingleLineInput key 行為：本 task 使用的 widget 由其覆蓋；本 task 不寫獨立 UT
  自動測試本_task: 無（驗收僅要求 cargo build pass + cargo test 不破）
  原則: |
    Tab/Esc/Enter 行為靠 E2E 手動觀察、不寫獨立 UNIT；雙欄狀態機簡單到不值得獨立 UT。

Constraints:
  必須:
    - 新檔 `src/presentation/handlers/tui/switch_source.rs`
    - "pub struct SwitchSourceScreen { novel_id: i64, book_url_input: SingleLineInput, source_url_input: SingleLineInput, focus: Focus }"
    - "Focus enum：BookUrl / SourceUrl"
    - impl Screen（含 ctx 參數版 trait）
    - draw：modal 樣式（Clear widget + 居中 layout）；上方 prompt「換源 #N」；兩個 SingleLineInput 上下排（focus 區塊高亮）
    - "handle_event Tab → focus toggle"
    - "handle_event Esc → Transition::To(ShelfScreen::new())"
    - "handle_event Enter（focus=BookUrl）→ 切到 source_url 輸入欄（focus=SourceUrl）"
    - "handle_event Enter（focus=SourceUrl）→ 取兩欄 text、await switch_source_core::run(ctx, novel_id, &source_url, &book_url)"
    - "成功 Ok(outcome) → Transition::To(ShelfScreen::with_highlight(None, Some(format!(\"✓ 已換源至 ...，進度重置到第 {} 章: {}\", outcome.new_progress_idx + 1, outcome.new_first_chapter_name))))"
    - "失敗 Err(e) → Transition::To(ShelfScreen::with_highlight(None, Some(format!(\"換源失敗：{:#}\", e))))"
  禁止:
    - SwitchSourceScreen 不寫 DB（atomicity 由 switch_source_core 保證）
    - 不在 SwitchSourceScreen 內呼叫 catalog::facade / library::facade（Esc 路徑保證零呼叫）
    - 不引入 async fetch 改造機制（沿用 inline await）
    - 不寫獨立 UNIT for 此 screen（Tab/Esc/Enter 靠 E2E 手動）
  驗收門檻:
    - "cargo build pass"
    - "cargo test 不破（既有測試保持綠燈）"
    - "E2E-2 / E2E-3 / E2E-5 / E2E-6 留手動"
  依賴前置:
    - "tui-03 (ShelfScreen，含 with_highlight ctor) 已完成"
    - "shared-03 (SingleLineInput widget) 已完成"
    - "hc-02 (switch_source_core::run + SwitchOutcome + AbortReason) 已完成"

Files:
  create:
    - /home/vakarve/project/others/NovelReader/src/presentation/handlers/tui/switch_source.rs
  modify:
    - /home/vakarve/project/others/NovelReader/src/presentation/handlers/tui/mod.rs  # 補 `pub mod switch_source;`
  reference_only:
    - /home/vakarve/project/others/NovelReader/src/presentation/handlers/tui/shelf.rs            # ShelfScreen::new / with_highlight
    - /home/vakarve/project/others/NovelReader/src/presentation/handlers/tui/widgets.rs         # SingleLineInput
    - /home/vakarve/project/others/NovelReader/src/presentation/handlers/switch_source_core.rs  # run / SwitchOutcome / AbortReason
