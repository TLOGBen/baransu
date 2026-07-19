Goal: |
  讓使用者在不離開 TUI 的前提下完成「搜尋蒐書 → 入架 → 閱讀 → 換源」整段
  funnel；`novel-looker` 不帶參數時不再印 help，而是進入主菜單 shell；既有
  CLI 子命令全部保留。

  本 task 對應 C1（入口分流）：
  - `novel-looker`（無參數）進入 TUI 主菜單
  - `novel-looker tui <id>` 維持直接進 reader（不經主菜單）
  - 兩條路徑都收斂到同一個 `App`，差別只在 ctor 與 `entry_mode`

Requirements:
  REQ-001: 入口分流與 CLI 結構
    描述: |
      `Cli.cmd` 改為 `Option<Cmd>`；`None` 時走主菜單 handler，`Some(_)`
      維持既有 dispatch；`--help` / `--version` / 既有子命令行為不變。
    scenarios:
      - Scenario 1 (無參數進入主菜單):
          Given: 使用者執行 `novel-looker`（無任何參數）
          When:  main.rs 解析 args 並 dispatch
          Then:  進入 TUI 主菜單畫面、terminal 進入 alternate screen + raw mode
      - Scenario 2 (tui <id> 維持直入 reader):
          Given: 使用者執行 `novel-looker tui 1`
          When:  main.rs dispatch
          Then:  直接進入 reader 顯示 novel_id=1、不經主菜單
      - Scenario 3 (clap 預設行為):
          Given: 使用者執行 `novel-looker --help` 或 `--version`
          When:  main.rs dispatch
          Then:  clap 印 help / version 後 exit 0、不進入 TUI
      - Scenario 4 (既有子命令不變):
          Given: 任一既有子命令
          When:  main.rs dispatch
          Then:  輸出與行為跟 v1 一致

Scenarios: (同上 REQ-001 的四個 Scenario，本 task 直接負責 Scenario 1 與 2 的 ctor 接通)

Task:
  id: TASK-tui-06
  title: 接通 App::new_with_menu / new_with_direct_reader
  需求追溯: REQ-001
  目標: |
    App 構造分兩個入口；handlers/menu.rs 與 handlers/tui.rs 各自呼一個。
  驗收標準:
    - 在 `src/presentation/handlers/tui/mod.rs` 補:
        `App::new_with_menu(ctx: AppContext) -> Self`
        constructs `{ current: Box::new(MenuScreen::new()), entry_mode: EntryMode::Menu, ctx }`
    - 在 `src/presentation/handlers/tui/mod.rs` 補:
        `App::new_with_direct_reader(novel_id: i64, ctx: AppContext) -> Self`
        (本 task 的 Constraints 段把簽名落地為:
         `new_with_direct_reader(ctx: AppContext, novel_id: i64) -> Result<Self>`，
         因為 `ReaderScreen::new` 需要 `&ctx` 與 `novel_id` 並可能回 Result)
        constructs `{ current: Box::new(ReaderScreen::new(EntryMode::DirectReader, &ctx, novel_id)?), entry_mode: EntryMode::DirectReader, ctx }`
    - 兩條路徑都進 `run_loop`
    - 進入 reader 走 ShelfScreen → ReaderScreen 時 ReaderScreen.entry_mode
      仍是 Menu（從 App.entry_mode 抄）；direct 路徑時 ReaderScreen.entry_mode
      = DirectReader
  步驟:
    - 修 `tui::mod` 補兩個 ctor
    - 驗 ReaderScreen 構造帶對的 entry_mode
  Constraints (本 task 的精確 ctor 簽名):
    在 `src/presentation/handlers/tui/mod.rs` 補:
      ```
      impl App {
          pub fn new_with_menu(ctx: AppContext) -> Self {
              Self::new(Box::new(menu::MenuScreen::new()), EntryMode::Menu, ctx)
          }
          pub fn new_with_direct_reader(ctx: AppContext, novel_id: i64) -> Result<Self> {
              let reader = reader::ReaderScreen::new(EntryMode::DirectReader, &ctx, novel_id)?;
              Ok(Self::new(Box::new(reader), EntryMode::DirectReader, ctx))
          }
      }
      ```
    改 `src/presentation/handlers/menu.rs`:
      用 `App::new_with_menu(ctx)` 取代手動構造
    改 `src/presentation/handlers/tui.rs`（既有薄 CLI handler）:
      用 `App::new_with_direct_reader(ctx, novel_id)?` 然後 run_loop

Design:
  TUI App 元件職責:
    App 的 `entry_mode: EntryMode::{Menu, DirectReader}` 欄位記錄啟動入口；
    reader screen 收到 `m` 鍵時依此分流（Menu → Transition::To(MenuScreen)；
    DirectReader → Transition::Quit）。

  資料模型新增（與本 task 相關）:
    - EntryMode enum:
        位置: `presentation/handlers/tui/mod.rs`
        值: `Menu` / `DirectReader`
        用途: 給 reader 的 `m` 鍵語意分流；給 App 構造時帶入；
              視為 implementation detail，不在 goal.md 範圍清單。
    - Transition enum:
        位置: `presentation/handlers/tui/mod.rs`
        值: `To(Box<dyn Screen>) / Stay / Quit`
    - Screen trait:
        位置: `presentation/handlers/tui/mod.rs`
        簽名: `draw(&mut self, frame)` + `handle_event(&mut self, KeyEvent) -> Transition`
    - ReaderScreen::new ctor:
        位置: `presentation/handlers/tui/reader.rs`
        簽名: `(entry_mode: EntryMode, novel_id: i64) -> ReaderScreen`
        本 task constraint 落地版: `(entry_mode, &ctx, novel_id) -> Result<Self>`
        entry_mode 在構造時抄自 `App.entry_mode`

  dispatch 圖（節錄與本 task 相關段落）:
    Main[main.rs] --> Cli{Cli.cmd}
    Cli -- None --> Menu[handlers::menu::run]      → App::new_with_menu
    Cli -- Some(Tui id) --> TuiSub[handlers::tui::handle]  → App::new_with_direct_reader
    App --> EvLoop --> Screen --> Transition --> ...

  Reader 搬遷不變清單（與本 task 上下游有關的點）:
    - 鍵綁定（j/k/J/K/Space/PgUp/PgDn/n/p/Tab/g/G/q）與 v1 一致
    - q 在 DirectReader 模式 = exit process（與 v1 q 同）；
      在 Menu 模式 = 回主菜單
    - `m` 是唯一新增行為（依 entry_mode 分流）

Test:
  本 task 沒有獨立 UNIT；它的正確性透過:
    - UNIT-4a / UNIT-4b（reader m 鍵 EntryMode 分流）間接驗 ctor 帶對 entry_mode
        UNIT-4a: ReaderScreen::new(EntryMode::Menu, novel_id) 餵 'm' → Transition::To(MenuScreen)
        UNIT-4b: ReaderScreen::new(EntryMode::DirectReader, ...) 餵 'm' → Transition::Quit
    - E2E-1（無 args → menu funnel）驗 new_with_menu
    - E2E-9（`tui <id>` → reader → m = exit）驗 new_with_direct_reader
    - E2E-10（menu→shelf→reader → m = 回主菜單）驗 entry_mode 在 menu 路徑下保持 Menu
    - E2E-14（--help / --version exit 0）clap 預設行為
    - E2E-16（既有 cargo test 全綠 — 25/26/27... 維持綠）

  本 task 自我驗收（task description 列出）:
    - cargo build pass
    - 既有 cargo test 全綠
    - `novel-looker` 與 `novel-looker tui <id>` 兩入口都連到 App 構造

Constraints:
  ctor 簽名（本 task 精確版）:
    - `new_with_menu(ctx: AppContext) -> Self`
    - `new_with_direct_reader(ctx: AppContext, novel_id: i64) -> Result<Self>`
      （注意參數順序為 ctx 在前、novel_id 在後；回 Result 因 ReaderScreen::new 可能 fail）

  entry_mode 在不同路徑下的值:
    - 直入 reader (`tui <id>`) → ReaderScreen.entry_mode = DirectReader
    - menu → shelf → Enter 進 reader → ReaderScreen.entry_mode = Menu
      （從 App.entry_mode 抄；本 task 不直接寫這條路徑，但要確保 ctor 不把
       App.entry_mode 鎖死成 DirectReader）

  Layer invariant（不破 REQ-007）:
    - 本 task 改的三檔（tui/mod.rs、handlers/menu.rs、handlers/tui.rs）都在
      `presentation/handlers/` 下，跨 context 組合本來就允許。
    - 但本 task 不應觸發 `use crate::catalog::facade` 或 `use crate::library::facade`
      新增在 `src/library/` 或 `src/catalog/` 內部；本 task 範圍純粹是 presentation 層。

  禁忌:
    - 不要改 `Screen` trait / `Transition` enum / `EntryMode` enum 的定義
      （由 task-tui-01 ~ task-tui-05 與更早的 shared task 建立）
    - 不要改 ReaderScreen / MenuScreen 內部行為；只呼它們的 ctor
    - 不要碰 `presentation/cli.rs` 的 `Cli.cmd: Option<Cmd>` 結構（那是別的 task）

Files:
  modify:
    - src/presentation/handlers/tui/mod.rs    # 補 impl App 的兩個 ctor
    - src/presentation/handlers/menu.rs        # 改用 App::new_with_menu(ctx)
    - src/presentation/handlers/tui.rs         # 改用 App::new_with_direct_reader(ctx, novel_id)?

  prerequisite (依賴但不修改):
    - src/presentation/handlers/tui/menu.rs           # MenuScreen::new() — 來自 task-tui-01
    - src/presentation/handlers/tui/reader.rs         # ReaderScreen::new(EntryMode, &AppContext, i64) -> Result<Self> — 來自 task-tui-02
    - src/presentation/mod.rs                          # AppContext 定義（已存在）
