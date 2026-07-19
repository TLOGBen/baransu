Goal: |
  從 goal.md 提取與本 task 直接相關段落（C1 入口分流、C7 Reader m 鍵）：

  - C1 入口分流：`novel-looker`（無參數）進入 TUI 主菜單；`novel-looker tui <id>`
    維持直接進 reader（不經主菜單）；`novel-looker --help / --version` 維持
    clap 預設行為。
  - C7 Reader m 鍵語意：reader 中按 `m`：經主菜單進入時 → 回主菜單；
    經 `tui <id>` 進入時 → exit process；其餘 reader 既有鍵不變。

  Scope 內本 task 涉及項目：
  - `presentation/handlers/tui/` 子目錄：本 task 建立 `mod.rs` 骨架
    （`menu.rs / search.rs / shelf.rs / reader.rs / switch_source.rs / widgets.rs`
    其他檔由後續 task 建立）

Requirements: |
  ### REQ-002: TUI 主菜單 shell 與 screen 路由
  **描述**：TUI 主迴圈用 `Box<dyn Screen>` 單軌路由；
  `Screen::handle_event(KeyEvent) -> Transition::{To(Box<dyn Screen>), Stay, Quit}`；
  主菜單列「書架 / 搜尋蒐書 / 設定 / 離開」。

  ### REQ-006: Reader m 鍵雙語意
  **描述**：reader 中按 `m` 的行為依「啟動入口」而定 — 主菜單→reader 時
  `m` = 回主菜單；`tui <id>` 直入 reader 時 `m` = exit process。

Scenarios: |
  ### REQ-002 Scenarios（本 task 關聯：定義 Transition 三變體所需的契約）
  - Scenario 1 主菜單 navigation：j/k 上下 highlight。
  - Scenario 2 主菜單 Enter 進子畫面：`Transition::To(SearchScreen)`。
  - Scenario 3 主菜單 q 離開：`Transition::Quit`；TUI 收尾、process exit 0。
  - Scenario 4 「設定」項目為空殼：顯示「尚未實作」訊息一秒後回主菜單。

  ### REQ-006 Scenarios（本 task 關聯：EntryMode 兩變體的存在動機）
  - Scenario 1 主菜單路徑下按 m → `Transition::To(MenuScreen)`；不 exit process。
  - Scenario 2 `tui <id>` 路徑下按 m → `Transition::Quit`；TUI 收尾、exit 0。
  - Scenario 3 既有 reader 鍵不變。

Task: |
  ## TASK-shared-02: 在 presentation/handlers/tui/ 建空殼 + Screen trait + Transition + EntryMode

  **需求追溯**：REQ-002, REQ-006
  **目標**：建立 `presentation/handlers/tui/mod.rs`、定義 `Screen` trait、
  `Transition` enum、`EntryMode` enum、`App` 結構與 `run_loop`；尚不接任何
  screen 實作。

  **驗收標準**：
  - [ ] `src/presentation/handlers/tui/mod.rs` 存在
  - [ ] 內含 `pub enum Transition { To(Box<dyn Screen>), Stay, Quit }`、
        `pub enum EntryMode { Menu, DirectReader }`、
        `pub trait Screen { fn draw(&mut self, frame: &mut Frame);
         fn handle_event(&mut self, key: KeyEvent) -> Transition; }`
  - [ ] `pub struct App { current: Box<dyn Screen>, entry_mode: EntryMode,
        ctx: AppContext }` 與 `pub async fn run_loop(app: App) -> Result<()>`
        框架就緒
  - [ ] `App::Drop` 與 `panic::set_hook` 保證 raw mode + alternate screen 清理
        （搬遷自既有 `presentation/reader.rs` 的 setup/teardown）
  - [ ] `cargo build` 過（搭配 stub MenuScreen 暫時可空）

  ### 步驟

  #### 建檔
  - [ ] `mkdir -p src/presentation/handlers/tui`
  - [ ] 寫 `src/presentation/handlers/tui/mod.rs`：trait / enum / App / run_loop 骨架
  - [ ] 在 `src/presentation/handlers/mod.rs` 加 `pub mod tui;`

  #### 終端管理
  - [ ] 抽 `RawTerm` RAII guard（enable_raw_mode + EnterAlternateScreen / Drop 反之）
  - [ ] `panic::set_hook` 安裝清理鉤
  - [ ] `App::Drop` 也呼叫清理（雙保險）

  #### 驗證
  - [ ] `cargo build` 通過（無 warning unused 過量）

Design: |
  ### 系統架構（本次新增 — 與 task 直接相關段落）
  ```
  src/presentation/handlers/tui/          ★ 新目錄；每個 screen 一檔 = handler 等價
      ├── mod.rs           App / EventLoop / Screen trait / Transition   ← 本 task
      ├── menu.rs          MenuScreen                                    （後續 task）
      ├── search.rs        SearchScreen                                  （後續 task）
      ├── shelf.rs         ShelfScreen                                   （後續 task）
      ├── reader.rs        ReaderScreen（從 presentation/reader.rs 搬遷+改）
      ├── switch_source.rs SwitchSourceScreen
      └── widgets.rs       通用 widget（toast、modal、輸入框 wrapper）
  ```

  ### TUI App 元件職責（與 task 相關段落）
  App 的 `entry_mode: EntryMode::{Menu, DirectReader}` 欄位記錄啟動入口；
  reader screen 收到 `m` 鍵時：
  - `entry_mode == Menu` → `Transition::To(Box::new(MenuScreen::new()))`
  - `entry_mode == DirectReader` → `Transition::Quit`

  事件迴圈核心契約：
  - `current: Box<dyn Screen>` 單軌路由
  - 每輪 draw → handle_event → 根據 Transition 切換 current 或 break

  ### 資料模型表（本 task 新增結構）
  | 結構 / 欄位 | 位置 | 變更 | 說明 |
  |---|---|---|---|
  | `EntryMode` enum | `presentation/handlers/tui/mod.rs` | 新增（internal） | `Menu` / `DirectReader`；給 reader 的 `m` 鍵語意分流；視為 implementation detail，不在 goal.md 範圍清單 |
  | `Transition` enum | `presentation/handlers/tui/mod.rs` | 新增 | `To(Box<dyn Screen>) / Stay / Quit` |
  | `Screen` trait | `presentation/handlers/tui/mod.rs` | 新增 | `draw(&mut self, frame)` + `handle_event(&mut self, KeyEvent) -> Transition` |

  ### 錯誤處理策略（與本 task 相關列）
  | 層 | 錯誤類型 | 處理 |
  |---|---|---|
  | TUI 致命錯誤 / panic | crossterm raw mode 殘留 | App 的 `Drop` 實作 + `std::panic::set_hook` 都呼叫 disable_raw_mode + leave_alternate_screen |

Test: |
  ### 測試光譜（本 task 相關列）
  本 task 為骨架建立，不直接觸發自動測試；但骨架需支援後續 UNIT-4a/4b 測試
  的構造需求（ReaderScreen::new + KeyEvent('m') 路由 Transition 結果）。

  ### UNIT-4a Reader m 鍵 EntryMode::Menu → To(Menu)
  - 位置：`presentation/handlers/tui/reader::tests`
  - 驗證點：構造 `ReaderScreen::new(EntryMode::Menu, novel_id)`，
    餵 `KeyEvent::Char('m')`；assert `Transition::To(_)` 且型別是 MenuScreen
  - 對本 task 的隱含要求：`Transition::To(Box<dyn Screen>)` 變體必須能容納
    後續 MenuScreen；EntryMode 必須是 Copy 或 Clone 以便構造時抄入 ReaderScreen

  ### UNIT-4b Reader m 鍵 EntryMode::DirectReader → Quit
  - 位置：同上
  - 驗證點：構造 `EntryMode::DirectReader`；同上輸入；assert `Transition::Quit`
  - 對本 task 的隱含要求：`Transition::Quit` 變體存在且可被 PartialEq 或
    pattern match 比對

  ### 邊界條件（與本 task 相關）
  - panic 路徑：std::panic::set_hook + App::Drop 雙保險清理 raw mode +
    alternate screen（避免 panic 後 terminal 進不可用狀態 — 此為 v1
    presentation/reader.rs 已有的行為，本 task 搬遷）

Constraints: |
  - `src/presentation/handlers/tui/` 為新目錄；`mod.rs` 是入口。
  - Screen trait 簽名固定：
      `fn draw(&mut self, frame: &mut Frame)`
      `fn handle_event(&mut self, key: KeyEvent) -> Transition`
  - Transition enum 三變體固定：`To(Box<dyn Screen>) / Stay / Quit`
  - EntryMode enum 兩變體固定：`Menu / DirectReader`
  - App struct 三欄位固定：`current: Box<dyn Screen>`,
    `entry_mode: EntryMode`, `ctx: AppContext`
  - `run_loop` 是 `async fn`（既有 `ctx.scraper` 等是 async）
  - `RawTerm` RAII guard 抽出來、`enable_raw_mode + EnterAlternateScreen +
    DisableMouseCapture` 對稱清理；`panic::set_hook + Drop` 雙保險
  - 本 task 只搭骨架；MenuScreen 用 stub（顯示「Stub」）讓 `cargo build`
    過即可。
  - 在 `src/presentation/handlers/mod.rs` 加 `pub mod tui;`
  - 不動：`cli.rs / main.rs / 既有 reader.rs`（reader 搬遷在 TASK-tui-02）
  - 不得在 `src/library/` 或 `src/catalog/` 內部 import 對方的 `facade`
    模組（REQ-007 layer invariant；本 task 不會碰到 library/catalog，
    但需在 mod.rs 中避免越層 import）。
  - 不暴露 tui-textarea 給上層（屬 TASK-shared-03，但本 task 不可預先在
    mod.rs 引入 tui-textarea 物件）。
  - 既有 v1 `presentation/reader.rs` 的 setup/teardown 邏輯為搬遷來源（參考
    對照），但 v1 檔案本身**不動**。
  - 不可破壞既有 cargo test、不可造成 unused warning 過量。

Files:
  create:
    - src/presentation/handlers/tui/mod.rs
  modify:
    - src/presentation/handlers/mod.rs   # 加 `pub mod tui;`
  reference_only_do_not_modify:
    - src/presentation/reader.rs         # v1 setup/teardown 邏輯搬遷來源
    - src/presentation/mod.rs            # AppContext 定義位置
    - src/presentation/cli.rs            # 不動（TASK-cli 階段才改）
    - src/main.rs                        # 不動
