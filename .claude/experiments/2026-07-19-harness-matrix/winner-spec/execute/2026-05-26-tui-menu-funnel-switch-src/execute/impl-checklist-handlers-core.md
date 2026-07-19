# Impl Checklist: handlers-core

## TASK-hc-01: evaluate_toc + AbortReason + UNIT-1/2/3

- [x] `src/catalog/service/scraper.rs` 抽 `pub(crate) fn fallback_chapter_name(idx: i64) -> String`
- [x] `src/presentation/handlers/switch_source_core.rs` 定義 `pub enum AbortReason { EmptyToc, AllFallbackNames, FetchInfoFailed(anyhow::Error), FetchTocFailed(anyhow::Error), FetchTocTimeout }`
- [x] `pub fn evaluate_toc(toc: &[ChapterMeta]) -> Result<(), AbortReason>`，用 fallback_chapter_name 比對（drift-resistant）
- [x] **UNIT-1** 空 vec → EmptyToc
- [x] **UNIT-2** 全 fallback → AllFallbackNames
- [x] **UNIT-3** 部分 fallback → Ok(())
- [x] `cargo test handlers::switch_source_core::tests` 全綠（20/20 全集）
- Review 結果：advisory
- 備註：所有驗收標準逐條核對通過。scraper.rs:117 的 `format!("Chapter {}", i + 1)` 已抽至 `fallback_chapter_name(i as i64)`，與 `evaluate_toc` 透過同一函式比對（drift-resistant invariant 成立）。AbortReason 五 variants 齊（a/b/c 三類 `#[allow(dead_code)]` 為 TASK-hc-02 保留，符合 ctx Constraints 第 116 行）。UT 三條都呼 `fallback_chapter_name` 構字串，沒有 literal "Chapter N"。Layer invariant 不破：`switch_source_core.rs` 只 import `catalog::service::scraper`（pure fn）與 `library::ChapterMeta`（PL）；無 rusqlite / dao。既有 4 條 catalog rule + library + tui widgets 測試全綠（20/20）。觀察點（非缺失）：handler 直接 `use crate::catalog::service::scraper::fallback_chapter_name` 跨越「handler 只呼 facade」的一般慣例，但 ctx 第 123 行 Constraints 明確授權（"handler 可同時 import catalog::service::scraper 與 library::ChapterMeta"），且這是 pure fn 非業務邏輯，drift-resistant 比一致性更重要。

## TASK-hc-02: switch_source_core::run cross-context

- [x] `pub async fn run(ctx: &mut AppContext, novel_id: i64, new_src_url: &str, new_book_url: &str) -> Result<SwitchOutcome>`
- [x] `pub struct SwitchOutcome { pub new_progress_idx: i64, pub chapter_count: usize, pub new_first_chapter_name: String }`
- [x] 內部依序 catalog::facade::get_source → fetch_novel_info → fetch_toc_with_timeout(8s) → evaluate_toc → library::facade::switch_source_tx
- [x] 五類失敗任一觸發都在進 tx 前 abort、不呼 library::facade
- [x] `grep -nE "use crate::catalog|use crate::library" src/presentation/handlers/switch_source_core.rs` 同時命中兩 context（handler 是組合點）
- [x] `cargo build` 過
- Review 結果：advisory
- 備註：六條驗收標準逐條核對通過。簽名（L71-76）、SwitchOutcome 三欄位（L60-64）、流程順序（get_source L78 → fetch_novel_info L82 → fetch_toc_with_timeout(8s) L93-98 → evaluate_toc L103 → switch_source_tx L117）皆精確對齊 ctx Constraints L281-295 sequence。五類 abort 全部在 L117 之前 propagate (`?`)，靜態驗證 switch_source_tx 不可能在 abort 後執行；C6 atomicity 持守。zh-TW 訊息齊（L79 找不到書源 / L84 (a) / L100 (b/c) / L104 (d) / L106 (e)），都帶「換源失敗：」前綴。toc_url 推導 `novel_info.toc_url.clone().unwrap_or_else(|| new_book_url.to_string())`（L87-90）與既有 sync handler `novel.toc_url.as_deref().unwrap_or(&novel.book_url)` 語義一致。first_idx 取自 `toc.first().index`（L111-112），不寫死 1。Grep 確認 handler 同時 import catalog + library（L13-16）；layer invariant grep `use crate::{catalog,library}::facade` on src/library + src/catalog 零命中，REQ-007 持守。catalog/facade.rs 與 library/facade.rs 本 commit 未動（commit stat 只改 switch_source_core.rs，88 ins / 5 del）。cargo test 20/20 全綠（4 catalog rule + 3 evaluate_toc + 3 tui widget + 10 library dao／含 INT-1/2a/2b/2c/2d/3/4 + get_novel_by_book_url ×2 + empty_new_chapters）。觀察點（非缺失）：(b) 與 (c) 共用一條 `with_context` 訊息，未在 message 層分辨 HTTP error vs Elapsed；ctx Scenario 3（L52-56）與 design table（L233-242）原本有區分意圖，但 Constraints L288-290 明確授權合併寫法，本實作從 Constraints。AbortReason 的 a/b/c 三 variants 仍 `#[allow(dead_code)]`，因 `run()` 用 anyhow chain 而非建構 variant；之後 hc-03+ TUI/CLI handler 若要 typed branch（如 timeout 重試）可改 `map_err` 拆 anyhow downcast。`.with_context(|| "...".to_string())` 的 `.to_string()` 多餘但純美觀，不值得 direct-fix。

## TASK-hc-03: CLI Option<Cmd> + SwitchSource cmd + menu handler

- [x] `presentation/cli.rs` 把 `cmd: Cmd` 改 `cmd: Option<Cmd>`、新增 `Cmd::SwitchSource { novel_id, new_book_url, source }`
- [x] dispatch 加 `None → handlers::menu::handle` + `Some(Cmd::SwitchSource(...)) → handlers::switch_source::handle`
- [x] `src/presentation/handlers/menu.rs` 新檔（薄；構造 App with EntryMode::Menu 進 tui::run_loop）— retry `2c5eb46` 已修正：menu.rs L21-24 以 `App::new(Box::new(StubMenuScreen), EntryMode::Menu, ctx)` + `run_loop(app).await` 取代原 eprintln stub
- [x] `src/presentation/handlers/switch_source.rs` 新檔（薄；呼 switch_source_core::run、印結果或錯誤）
- [x] `novel-looker --help` 列出 switch-source 子命令
- [x] `novel-looker --version` 不破
- [ ] 既有命令逐條跑（E2E-13）— 未跑（ctx 標 final stage；本 task 跳過 OK）
- Review 結果：advisory
- 備註（retry `2c5eb46`，amended from `6d8f03b`）：前次 finding 完全落實。menu.rs (L1-24) 是 3 行邏輯 + doc comment：`App::new(Box::new(StubMenuScreen), EntryMode::Menu, ctx)` → `run_loop(app).await`。App::new 簽名 (tui/mod.rs:103 `pub fn new(current: Box<dyn Screen>, entry_mode: EntryMode, ctx: AppContext) -> Self`) 對齊 ctx Design L94-99（"App 三欄位 owned 結構"，current / entry_mode / ctx 皆 owned by value）。REQ-001 Scenario 1 acceptance（"進入 TUI 主菜單畫面 + raw mode + alternate screen"）滿足：`run_loop` (tui/mod.rs:168-194) 第 170 行 `RawTerm::enter()?` 觸發 `enable_raw_mode()` + `EnterAlternateScreen`（tui/mod.rs:120-127），第 174 行 `term.terminal.draw(|f| app.current.draw(f))?` 呼 StubMenuScreen::draw 渲 placeholder paragraph；TASK-tui-01 之後 overwrite StubMenuScreen 為真 MenuScreen 時不必動 menu.rs。menu handler 仍是「薄」— 不放邏輯，僅 entry 接點。cargo test 23/23 全綠（20 既有 + 3 new clap parse UT 全 ok：cli_no_subcommand_parses_to_none / cli_switch_source_parses_with_three_fields / cli_existing_shelf_subcommand_still_parses 對應 REQ-001 Scenario 1+4 與 REQ-005 Scenario 6 parse leg）。--help 列 switch-source、--version 印 `novel-looker 0.1.0` 均驗證 OK。其他正向觀察延續：cli.rs Cli/Cmd/SwitchSource + dispatch arms 齊；main.rs `let cli = Cli::parse();` + `cli::run(cli, ctx).await`（owned ctx）符合 Constraint L142-143；switch_source.rs 成功格式對齊 ctx L156-157（含 1-based 顯示 + 註解），失敗 eprintln anyhow chain + exit 1。觀察點（非缺失）：5 個 dead_code warning（App/Screen/Transition/RawTerm/install_panic_hook/StubMenuScreen）+ 既有 a/b/c AbortReason / SwitchOutcome.chapter_count / get_novel_by_book_url 為 TUI 群組保留，皆符合 ctx 預期；E2E-13/14/11/12 留手動驗（ctx Test 策略 L131-133 明示 final stage，本 task 跳過 OK）。
