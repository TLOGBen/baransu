---
task_id: TASK-handlers-core-03
group: handlers-core
spec_dir: .claude/analyze/2026-05-26-tui-menu-funnel-switch-src/

Goal: |
  讓使用者在不離開 TUI 的前提下完成「搜尋蒐書 → 入架 → 閱讀 → 換源」整段 funnel；
  `novel-looker` 不帶參數時不再印 help，而是進入主菜單 shell；既有 CLI 子命令全部保留，
  並新增 `switch-source` 對應的 CLI 形式給 script / cron 使用。

  與本 task 直接相關的驗收：
  - C1 入口分流：`novel-looker`（無參數）進入 TUI 主菜單；`novel-looker tui <id>` 維持直接進 reader；
    `novel-looker --help / --version` 維持 clap 預設行為
  - C8 CLI switch-source：`novel-looker switch-source <novel_id> <new_book_url> --source <new_source_url>`
    跟 TUI shelf 的 `s` 鍵跑同一個 use case 函式；成功 / 失敗判定與 atomicity 跟 C6 一致
  - C10 既有行為不破：`cargo test` 全綠；CLI 既有命令行為與輸出格式不變

Requirements:
  REQ-001: |
    入口分流與 CLI 結構

    描述：`Cli.cmd` 改為 `Option<Cmd>`；`None` 時走主菜單 handler，
    `Some(_)` 維持既有 dispatch；`--help` / `--version` / 既有子命令行為不變。

  REQ-005 (Scenario 6 only): |
    換源 transaction 中 CLI 子命令對應條目

Scenarios:
  REQ-001 Scenario 1 (無參數進入主菜單):
    Given: 使用者執行 `novel-looker`（無任何參數）
    When: main.rs 解析 args 並 dispatch
    Then: 進入 TUI 主菜單畫面
    And: terminal 進入 alternate screen + raw mode

  REQ-001 Scenario 2 (tui <id> 維持直入 reader):
    Given: 使用者執行 `novel-looker tui 1`
    When: main.rs dispatch
    Then: 直接進入 reader 顯示 novel_id=1
    And: 不經主菜單

  REQ-001 Scenario 3 (clap 預設行為):
    Given: 使用者執行 `novel-looker --help` 或 `--version`
    When: main.rs dispatch
    Then: clap 印 help / version 後 exit 0
    And: 不進入 TUI

  REQ-001 Scenario 4 (既有子命令不變):
    Given: 使用者執行任何既有子命令（`source list` / `search foo` / `shelf` / `read 1 0` 等）
    When: main.rs dispatch
    Then: 輸出與行為跟 v1 一致

  REQ-005 Scenario 6 (CLI switch-source 子命令):
    Given: 終端執行 `novel-looker switch-source 1 https://czbooks.net/n/abc --source https://czbooks.net`
    When: main.rs dispatch
    Then: 呼叫與 TUI shelf 同一個 use case fn（`handlers::switch_source_core::run` 之類）
    And: 成功 / 失敗判定與 atomicity 跟上述 Scenario 1-5 完全一致
    And: 終端輸出純文字結果（成功：「✓ 已換源 #1 至 ...，進度重置到第 N 章」；失敗：上述對應錯誤訊息）

Task:
  id: TASK-handlers-core-03
  title: CLI switch-source 子命令 + 入口分流
  需求追溯: REQ-001, REQ-005 Scenario 6, REQ-006
  目標: |
    `presentation/cli.rs` 把 `cmd: Cmd` 改 `cmd: Option<Cmd>`、新增 `Cmd::SwitchSource`；
    `main.rs` 處理 None；新增 `handlers/switch_source.rs`（CLI handler，薄）；
    新增 `handlers/menu.rs`（None-path 入口，薄）。

  驗收標準:
    - "Cli { #[command(subcommand)] cmd: Option<Cmd> } + Cmd::SwitchSource { novel_id: i64, new_book_url: String, #[arg(long)] source: String }"
    - "main.rs 分流：None → handlers::menu::run(&mut ctx).await?、Some(c) → 既有 dispatch"
    - "handlers/menu.rs：thin — 構造 App::new_with_menu(ctx) 然後 run_loop(app).await"
    - "handlers/switch_source.rs：thin — 呼 switch_source_core::run(...)、stdout 印結果或 stderr 印錯誤"
    - "novel-looker --help 印出新增的 switch-source 子命令"
    - "novel-looker --version 還能用"
    - "E2E-14 / E2E-11 / E2E-12 手動跑通"

  步驟:
    CLI 結構:
      - Read src/presentation/cli.rs 確認既有 dispatch 形狀
      - 修 Cli 結構：cmd: Option<Cmd>
      - 加 Cmd::SwitchSource { novel_id, new_book_url, source } variant
      - dispatch fn 加 Cmd::SwitchSource(...) 分支呼 handlers::switch_source::handle
      - 加 None 分支呼 handlers::menu::handle
    main.rs:
      - Read src/main.rs 確認 entry
      - 確保 None 分流走到 menu handler
    兩個薄 handler:
      - 寫 src/presentation/handlers/menu.rs — 用 EntryMode::Menu 進 tui::run_loop
      - 寫 src/presentation/handlers/switch_source.rs — 呼 switch_source_core::run、印結果
    驗證:
      - cargo build --bin novel-looker 過
      - novel-looker --help 列出 switch-source
      - novel-looker --version 不破
      - 跑 E2E-13 列出的 7 條既有命令對應 stdout 首行 / 結尾 pattern；逐條打勾

Design:
  系統架構 (與本 task 直接相關):
    既有結構 (不動):
      - src/main.rs              clap entry; bootstraps AppContext
      - src/presentation/cli.rs  Cli / Cmd enums + dispatch
      - src/presentation/handlers/ 每個 CLI 子命令一檔
      - src/presentation/mod.rs   AppContext { db, scraper, config }

    本次新增 / 變更:
      - src/presentation/cli.rs                 ★ Cli { cmd: Option<Cmd> }；新增 Cmd::SwitchSource
      - src/presentation/handlers/menu.rs       ★ None-path 入口（薄；轉呼 tui::run_menu）
      - src/presentation/handlers/switch_source.rs   ★ CLI handler（薄；轉呼 switch_source_core::run）

  Cli 分流 flow (mermaid 摘要):
    Main -> Cli { cmd }
      None              -> handlers::menu::run
      Some(Tui id)      -> handlers::tui::handle
      Some(SwitchSource)-> handlers::switch_source::handle
      Some(others)      -> 既有 handlers

  資料模型 (與本 task 直接相關):
    Cli.cmd:
      位置: presentation/cli.rs
      變更: Cmd → Option<Cmd>
      說明: None 走 menu
    Cmd::SwitchSource variant:
      位置: presentation/cli.rs
      變更: 新增
      欄位: "{ novel_id: i64, new_book_url: String, source: String }"

  錯誤處理策略 (與本 task 相關):
    CLI handler: 拿到 Result::Err → 透過 main.rs 的 Result<()> propagate → exit 1 + stderr 印錯誤

Test:
  策略:
    - 本 task 範圍：cargo build / --help / --version 驗證
    - E2E-13 列出的 7 條既有命令（驗證不破）— 留 final stage
    - E2E-14 (CLI switch-source 成功路徑) / E2E-11 / E2E-12 — 手動驗，本 task 不必跑
  邊界條件:
    - 既有 reader/sync/add 等 handler 簽名是 &mut AppContext — 不動
    - menu handler 簽名是 owned AppContext — owned by App
    - cli::run 內：None branch move ctx 進 menu handler；Some branch 借出 &mut

Constraints:
  - 既有 handler 簽名（&mut AppContext）不可動
  - menu handler 必須走 owned ctx（App 持有 owned AppContext）
  - cli::run 簽名改為 `pub async fn run(cli: Cli, ctx: AppContext) -> Result<()>`（ctx by value）
  - main.rs 對應改為 `cli::run(cli, ctx).await`
  - 既有 cargo test 必須全綠，不破壞既有測試
  - CLI 既有命令的輸出格式 / 行為不變
  - handlers/switch_source.rs 是薄 handler：只呼 switch_source_core::run、印結果，不重做業務邏輯
  - handlers/menu.rs 是薄 handler：構造 App / 進 run_loop，不放邏輯
  - dispatch 結構（建議）:
      pub async fn run(cli: Cli, mut ctx: AppContext) -> Result<()> {
          match cli.cmd {
              Some(c) => dispatch(c, &mut ctx).await,
              None => handlers::menu::handle(ctx).await,  // move
          }
      }
  - switch_source handler 成功訊息格式：
      "✓ 已換源 #{novel_id} 至 {new_book_url}，進度重置到第 {N} 章: {chapter_name}"
  - 失敗訊息走 stderr 並 propagate Err

Files:
  modify:
    - src/presentation/cli.rs                  # cmd: Option<Cmd>、加 Cmd::SwitchSource、dispatch 改
    - src/presentation/handlers/mod.rs         # pub mod menu; pub mod switch_source;
    - src/main.rs                              # 一行：cli::run(cli, ctx).await (ctx by value)
  create:
    - src/presentation/handlers/menu.rs        # pub async fn handle(ctx: AppContext) -> Result<()>
    - src/presentation/handlers/switch_source.rs  # pub async fn handle(novel_id, new_book_url, source, ctx: &mut AppContext) -> Result<()>
  read_only_dependencies:
    - src/presentation/handlers/switch_source_core.rs  # 由 TASK-handlers-core-02 產出；handle 呼 switch_source_core::run
    - src/presentation/handlers/tui/mod.rs             # 由 TUI 群組產出；menu handler 用其 App / run_loop / EntryMode::Menu
---
