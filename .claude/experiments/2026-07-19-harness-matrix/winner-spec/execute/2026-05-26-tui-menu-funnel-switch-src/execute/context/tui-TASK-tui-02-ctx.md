Goal: |
  C7 Reader m 鍵語意：reader 中按 `m` 的行為依「啟動入口」而定 —
  經主菜單進入時 → 回主菜單；經 `tui <id>` 進入時 → exit process；
  其餘 reader 既有鍵不變。

  本 task 將既有 `src/presentation/reader.rs`（338 行）搬遷至
  `src/presentation/handlers/tui/reader.rs`，並改寫為 `impl Screen for
  ReaderScreen`；構造時帶 `entry_mode: EntryMode`，handle_event 收 `m`
  依 entry_mode 分流 Transition::To(MenuScreen) 或 Transition::Quit。

Requirements:
  - id: REQ-006
    name: Reader m 鍵雙語意
    description: |
      reader 中按 `m` 的行為依「啟動入口」而定 — 主菜單→reader 時
      `m` = 回主菜單；`tui <id>` 直入 reader 時 `m` = exit process。

Scenarios:
  - req: REQ-006
    name: "Scenario 1: 主菜單路徑下按 m"
    given: 從主菜單→書架→Enter 進入 reader
    when: 在 reader 按 `m`
    then: Transition::To(MenuScreen)；不 exit process
  - req: REQ-006
    name: "Scenario 2: tui <id> 路徑下按 m"
    given: 從 `novel-looker tui 1` 直接啟動 reader
    when: 在 reader 按 `m`
    then: Transition::Quit；TUI 收尾、exit 0
  - req: REQ-006
    name: "Scenario 3: 既有 reader 鍵不變"
    given: 任一入口進入 reader
    when: 按 `j/k/J/K/Space/PgUp/PgDn/n/p/Tab/g/G/q`
    then: 行為與 v1 一致（章節 navigate、scroll、進度儲存、quit 等）

Task:
  id: TASK-tui-02
  name: ReaderScreen 搬遷 + m 鍵雙語意
  prereq_group: [shared, handlers-core]
  goal: |
    把既有 `src/presentation/reader.rs`（338 行）拆進
    `src/presentation/handlers/tui/reader.rs`，實作 `Screen` trait；
    `m` 鍵依 `entry_mode` 分流。
  acceptance_criteria:
    - "`src/presentation/handlers/tui/reader.rs` 存在；`impl Screen for ReaderScreen`"
    - 既有鍵 j/k/J/K/Space/PgUp/PgDn/n/p/Tab/g/G/q 行為跟 v1 完全一致
    - "m 鍵：構造時帶 entry_mode；handle_event 收 m 依 entry_mode 回 `Transition::To(MenuScreen)` 或 `Transition::Quit`"
    - "q 鍵：MenuMode 下 = 回主菜單；DirectMode 下 = exit"
    - 進度儲存（save_progress）的時機點不變
    - 既有 `src/presentation/reader.rs` 刪除或留薄 re-export（建議刪除、`handlers/tui.rs`（既有）轉呼新 ReaderScreen）
    - "`tui <id>` CLI handler `handlers/tui.rs` 改為構造 App::new_with_direct_reader(novel_id, ctx) + run_loop"
  steps:
    搬遷:
      - Read `src/presentation/reader.rs`（既有 338 行）抓出兩 pane 排版、key dispatch、async fetch（inline await）、save_progress 時機
      - "新 `src/presentation/handlers/tui/reader.rs`：把上述以 `Screen` trait 重組"
      - async fetch 在 handle_event 內 await — 沿用 inline 模式（Not building 明示）
    m_鍵:
      - "ReaderScreen struct 含 `entry_mode: EntryMode`"
      - "handle_event KeyCode::Char('m'): match entry_mode { Menu => Transition::To(MenuScreen), DirectReader => Transition::Quit }"
    既有_tui_handler_改造:
      - "`src/presentation/handlers/tui.rs` 改為構造 `App::new_with_direct_reader(novel_id, ctx)` 呼 `run_loop`；舊 `reader::run` 函式移除"
      - 刪除 `src/presentation/reader.rs`
      - 把 `src/presentation/mod.rs` 對 `pub mod reader` 的 line 拿掉
    驗證:
      - "`cargo build --bin novel-looker` 過"
      - "寫 UNIT-4a：構造 `ReaderScreen::new(EntryMode::Menu, novel_id)` → 餵 `KeyEvent::Char('m')` → assert `Transition::To(_)` 為 MenuScreen"
      - "寫 UNIT-4b：構造 `EntryMode::DirectReader` → 同上輸入 → assert `Transition::Quit`"
      - E2E-9（tui <id> + m = exit）手動跑
      - E2E-10（menu→reader + m = 回主菜單）手動跑

Design:
  reader_搬遷不變清單:
    description: |
      `presentation/reader.rs` (v1) → `presentation/handlers/tui/reader.rs` (v2)
      搬遷時以下行為不變。
    invariants:
      - 鍵綁定：j/k（章節 navigate）、J/K（scroll）、Space/PgUp/PgDn（scroll）、n/p（前後章節）、Tab（pane 切換）、g/G（頭尾）、q（退出 — Menu 模式 = 回主菜單；Direct 模式 = exit process，與 v1 q 同）
      - progress 儲存時機：每次章節切換、quit、`m` 鍵觸發 transition 時皆儲存
      - 章節 fetch：cache hit → 從 library 讀；miss → fetch + 寫回 library；inline await
      - 兩 pane 排版：左 TOC、右內文；focus 切換
    new_behavior:
      - "唯一新增：`m` 鍵在 Menu 模式 = `Transition::To(MenuScreen)`、Direct 模式 = `Transition::Quit`"
      - "`q` 鍵語意維持 v1（在 Menu 模式下 `q` 與 `m` 在現實效果上相同 — 都回主菜單；本期不刻意區分以維持手感）"
  entry_mode:
    location: presentation/handlers/tui/mod.rs
    type: enum (internal)
    values: [Menu, DirectReader]
    purpose: 給 reader 的 `m` 鍵語意分流；視為 implementation detail
  transition:
    location: presentation/handlers/tui/mod.rs
    type: enum
    values: ["To(Box<dyn Screen>)", "Stay", "Quit"]
  screen_trait:
    location: presentation/handlers/tui/mod.rs
    methods:
      - "draw(&mut self, frame)"
      - "handle_event(&mut self, KeyEvent) -> Transition"
  reader_screen_ctor:
    location: presentation/handlers/tui/reader.rs
    signature: "ReaderScreen::new(entry_mode: EntryMode, novel_id: i64) -> ReaderScreen"
    note: entry_mode 在構造時抄自 `App.entry_mode`
  m_鍵_dispatch:
    Menu: "Transition::To(Box::new(MenuScreen::new()))"
    DirectReader: "Transition::Quit"
  reader_screen_struct_recommended: |
    pub struct ReaderScreen {
        entry_mode: EntryMode,
        novel_id: i64,
        novel: Novel,
        chapters: Vec<ChapterMeta>,
        toc_state: ListState,
        current: usize,
        content: Vec<String>,
        raw_content: String,
        scroll: u16,
        focus: Focus,
        status: String,
    }
    pub fn new(entry_mode: EntryMode, ctx: &AppContext, novel_id: i64) -> Result<Self>

Test:
  unit_4a:
    location: presentation/handlers/tui/reader::tests
    description: "Reader m 鍵 EntryMode::Menu → To(Menu)"
    verification: |
      構造 `ReaderScreen::new(EntryMode::Menu, novel_id)`，
      餵 `KeyEvent::Char('m')`；assert `Transition::To(_)` 且型別是 MenuScreen
  unit_4b:
    location: presentation/handlers/tui/reader::tests
    description: "Reader m 鍵 EntryMode::DirectReader → Quit"
    verification: |
      構造 `EntryMode::DirectReader`；餵 `KeyEvent::Char('m')`；
      assert `Transition::Quit`
  unit_test_skeleton: |
    #[cfg(test)] mod tests {
        use super::*;
        fn mock_reader(mode: EntryMode) -> ReaderScreen { /* with empty chapters, etc. */ }
        #[test] fn unit4a_menu_mode_m_to_menu() {
            let mut r = mock_reader(EntryMode::Menu);
            let t = r.handle_event(KeyEvent::new(KeyCode::Char('m'), KeyModifiers::empty()));
            assert!(matches!(t, Transition::To(_)));
        }
        #[test] fn unit4b_direct_mode_m_quits() {
            let mut r = mock_reader(EntryMode::DirectReader);
            let t = r.handle_event(KeyEvent::new(KeyCode::Char('m'), KeyModifiers::empty()));
            assert!(matches!(t, Transition::Quit));
        }
    }
  e2e_manual:
    - id: E2E-9
      desc: "`tui <id>` 直入 + m 鍵 = exit"
      start: "`novel-looker tui 1` → reader 按 m"
      end: process exit 0
      criteria: C7
    - id: E2E-10
      desc: "menu→reader m 鍵 = 回主菜單"
      start: "menu→shelf→Enter 進 reader → m"
      end: 回主菜單
      criteria: C7
  acceptance_test_commands:
    - "cargo build --bin novel-looker"
    - "cargo test"
    - "cargo test catalog::service::rule (既有測試不破)"

Constraints:
  - 把 src/presentation/reader.rs（338 lines）搬到 src/presentation/handlers/tui/reader.rs
  - 改寫成 `impl Screen for ReaderScreen { draw / handle_event }`
  - 既有鍵 j/k/J/K/Space/PgUp/PgDn/n/p/Tab/g/G/q 行為不變（搬遷時邏輯保留）
  - "新增鍵 m：依 entry_mode 分流：EntryMode::Menu → Transition::To(Box::new(menu::MenuScreen::new()))；EntryMode::DirectReader → Transition::Quit"
  - "q 鍵語意 v1 不變（在兩種 mode 都 Quit）。設計討論：spec design.md 註「q 在 Menu 模式下與 m 在現實效果上相同 — 都回主菜單」— 暫採取 q 也 Transition::To(MenuScreen) for Menu mode，DirectReader mode 仍 Quit"
  - "務實：q 行為跟 m 相同（Menu→To(Menu)、Direct→Quit）— 維持 v1「q 是退出」的直覺"
  - 進度儲存：每次章節切換 + 退出（Transition::To / Transition::Quit）時都 save_progress；用 ctx.db 訪問 library facade
  - 刪除既有 src/presentation/reader.rs
  - 更新 src/presentation/mod.rs：移除 `pub mod reader;`
  - "更新 src/presentation/handlers/tui.rs（既有薄 CLI handler）：構造 App::new_with_direct_reader 或直接 App::new(ReaderScreen::new(EntryMode::DirectReader,...), EntryMode::DirectReader, ctx) → run_loop"
  - "更新 src/presentation/handlers/tui/mod.rs：加 `pub mod reader;`"
  - reader 的 fetch_content / load_chapter / save_progress 等 inline await 邏輯保留 — 不引入 async refactor（Not building 明示）
  - "Layer invariant：本 task 修改範圍在 presentation/，不會新增 catalog/library 互引；reader 透過 ctx.db 走 library::facade 與 catalog::facade（cross-context 組合在 handler/screen 層合法）"

Files:
  create:
    - path: src/presentation/handlers/tui/reader.rs
      desc: 搬遷自既有 reader.rs + Screen impl + m 鍵分流 + UNIT-4a/4b tests
  delete:
    - path: src/presentation/reader.rs
      desc: 既有 338 行 reader 模組（已搬遷）
  modify:
    - path: src/presentation/mod.rs
      desc: 移除 `pub mod reader;`
    - path: src/presentation/handlers/tui.rs
      desc: 既有薄 CLI handler 改用新 App + run_loop 入口（構造 App::new_with_direct_reader(novel_id, ctx)）
    - path: src/presentation/handlers/tui/mod.rs
      desc: 加 `pub mod reader;`
