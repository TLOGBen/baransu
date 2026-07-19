Goal: |
  C2 主菜單：主菜單顯示「書架 / 搜尋蒐書 / 設定 / 離開」四項；j/k 上下、Enter 進入、q 離開 process。
  （上游目標：讓使用者在不離開 TUI 的前提下完成「搜尋蒐書 → 入架 → 閱讀 → 換源」整段 funnel；
  novel-looker 不帶參數時不再印 help，而是進入主菜單 shell。）

Requirements:
  REQ-002:
    描述: |
      TUI 主菜單 shell 與 screen 路由。
      TUI 主迴圈用 Box<dyn Screen> 單軌路由；Screen::handle_event(KeyEvent) -> Transition::{To(Box<dyn Screen>), Stay, Quit}；
      主菜單列「書架 / 搜尋蒐書 / 設定 / 離開」。

Scenarios:
  REQ-002-Scenario-1-主菜單-navigation:
    Given: 在主菜單
    When: 按 j / k
    Then: highlight 在四個選項間上下移動

  REQ-002-Scenario-2-主菜單-Enter-進子畫面:
    Given: highlight 在「搜尋蒐書」
    When: 按 Enter
    Then: Transition::To(SearchScreen)；畫面切換到搜尋頁

  REQ-002-Scenario-3-主菜單-q-離開:
    Given: 在主菜單
    When: 按 q
    Then: Transition::Quit；TUI 收尾、process exit 0

  REQ-002-Scenario-4-設定項目為空殼:
    Given: 在主菜單，highlight 在「設定」
    When: 按 Enter
    Then: 顯示「尚未實作」訊息一秒後回主菜單（或進空白頁顯示提示，按任意鍵回）；本期不展開

Task:
  id: TASK-tui-01
  name: MenuScreen
  需求追溯: REQ-002
  目標: 四選項主菜單；j/k 移動、Enter 路由、q 退出；「設定」項顯示 stub。
  驗收標準:
    - src/presentation/handlers/tui/menu.rs 存在；impl Screen for MenuScreen
    - 渲染：標題 + 4 個 item + 底部 hint「j/k 移動，Enter 進入，q 離開」
    - j/k 移動 highlight；Enter on「書架」→ Transition::To(Box::new(ShelfScreen::new(ctx)))；on「搜尋蒐書」→ SearchScreen；on「設定」→ stub message 後 Stay；on「離開」→ Quit；q → Quit
    - m 鍵在 MenuScreen Stay（無語意，但不該 panic）
  步驟:
    - 寫檔
    - 在 tui::App::new_with_menu 構造時 current = Box::new(MenuScreen::new())
    - 手動 smoke：novel-looker（無 args）能看到主菜單
  UNIT對應註記: |
    MenuScreen 的 trait dispatch UT 由 task-tui-02 一起完成（UNIT-4 originally 設計為 Screen trait dispatch 通用驗證、
    已拆 UNIT-4a/4b 給 reader m 鍵；MenuScreen 自己的 j/k/Enter 路由不獨立寫 UT，靠 E2E-1 smoke）。

Design:
  TUI-App-元件職責: |
    App 用單軌路由：current: Box<dyn Screen>，每輪 handle_event 回 Transition::{To(Box<dyn Screen>), Stay, Quit}，
    To 時 swap current screen，Quit 時 teardown + exit。
    App 含 entry_mode: EntryMode::{Menu, DirectReader} 欄位記錄啟動入口。
    Cli.cmd == None 路徑 → handlers::menu::run → tui::App（entry_mode=Menu, current=Box::new(MenuScreen::new()))。
  整體操作流程-menu部分: |
    Start (novel-looker 無 args) → MenuS[MainMenu]
    MenuS --j/k--> MenuS（移動 highlight）
    MenuS --q--> Exit（process exit）
    MenuS --Enter「書架」--> ShelfS[ShelfScreen]
    MenuS --Enter「搜尋蒐書」--> SearchS[SearchScreen]
    MenuS --Enter「設定」--> Stub[Stub 提示]
    Stub --任意鍵--> MenuS
  畫面關聯: |
    MenuScreen → SearchScreen
    MenuScreen → ShelfScreen
    MenuScreen → Settings stub（任意鍵回 Menu）
    SearchScreen --Esc--> MenuScreen
    ShelfScreen --Esc/q--> MenuScreen
    ReaderScreen(Menu mode) --m--> MenuScreen
  相關資料模型:
    Transition_enum:
      位置: presentation/handlers/tui/mod.rs
      狀態: 新增（前置 task 已建立）
      欄位: To(Box<dyn Screen>) / Stay / Quit
    Screen_trait:
      位置: presentation/handlers/tui/mod.rs
      狀態: 新增（前置 task 已建立）
      簽名: |
        draw(&mut self, frame)
        handle_event(&mut self, KeyEvent) -> Transition
    EntryMode_enum:
      位置: presentation/handlers/tui/mod.rs
      欄位: Menu / DirectReader
      說明: 主菜單入口時為 Menu；MenuScreen 不直接依賴此值，但 App 攜帶。

Test:
  關聯E2E:
    E2E-1:
      場景: 主菜單 funnel 一氣呵成
      起點: novel-looker（無 args）
      終點: reader 顯示某章內文
      對應Criteria: C1, C2, C3, C4, C7
      說明: MenuScreen 的 j/k/Enter/q 行為靠 E2E-1 smoke 覆蓋；無獨立 UNIT。
  關聯Unit: |
    本 task 不獨立寫 UNIT（spec 明示：MenuScreen 自己的 j/k/Enter 路由靠 E2E-1 smoke）。
  其他既有測試: cargo test 既有 23/23 須維持全綠（不破壞既有）。

Constraints:
  - 新檔 src/presentation/handlers/tui/menu.rs 內含 pub struct MenuScreen { selected: usize }；四個項目：「書架」/「搜尋蒐書」/「設定」/「離開」；impl Screen for MenuScreen { draw / handle_event }。
  - 鍵綁定：j/Down → selected = (selected+1) mod 4；k/Up → selected = (selected + 3) mod 4；Enter → 根據 selected 走 Transition；q → Transition::Quit；m → Stay（無語意但不 panic）。
  - Enter 行為：
      selected==0「書架」→ Transition::To(Box::new(crate::presentation::handlers::tui::shelf::ShelfScreen::new()))（理想終態）。
      selected==1「搜尋蒐書」→ Transition::To(Box::new(crate::presentation::handlers::tui::search::SearchScreen::new()))（理想終態）。
      selected==2「設定」→ 顯示「尚未實作」 stub 狀態（內部 flag、draw 顯示）、任意鍵回 selected=0 → Transition::Stay。
      selected==3「離開」→ Transition::Quit。
  - 實作順序務實策略：ShelfScreen / SearchScreen 是 tui-03/04 才建立；tui-01 對「書架」/「搜尋蒐書」分支可暫保留 toast「等 tui-03/04」+ Transition::Stay（內部 flag 顯示 placeholder 訊息）；tui-03/04 完成時再 wire 上實際 Transition。spec task-tui.md 順序是 01→07，依 spec 走。
  - 「設定」按 Enter 用同樣的「尚未實作」邏輯（與「書架」/「搜尋蒐書」placeholder 機制共用）。
  - 更新 src/presentation/handlers/tui/mod.rs：加 `pub mod menu;`；menu.rs 內讓 handler 能從 tui::MenuScreen import（透過 mod.rs 或 menu.rs 的 pub use 公開）。
  - 替換 handlers/menu.rs 內的 StubMenuScreen 為 MenuScreen：
      use crate::presentation::handlers::tui::{App, EntryMode, run_loop, menu::MenuScreen};
      let app = App::new(Box::new(MenuScreen::new()), EntryMode::Menu, ctx);
  - 不得讓 service/*.rs 引入 rusqlite 或 dao 模組（此 task 不觸及 service / dao 層，仍須保持 layer invariant）。
  - 不得修改 .claude/analyze/ 下任何文件。
  - 不破壞既有：cargo build 必過、cargo test 須維持 23/23（既有不破）。E2E-1 smoke 留 final stage 跑。
  - Worktree 狀態：tui 從 main 最新（L2 merge 後 head）fork，已含 MenuScreen 所需所有 deps（StubMenuScreen / App / run_loop / EntryMode）。

Files:
  create:
    - src/presentation/handlers/tui/menu.rs
  modify:
    - src/presentation/handlers/tui/mod.rs        # 新增 pub mod menu;（並確保 MenuScreen 可被 import）
    - src/presentation/handlers/menu.rs           # 用 MenuScreen 取代 StubMenuScreen
