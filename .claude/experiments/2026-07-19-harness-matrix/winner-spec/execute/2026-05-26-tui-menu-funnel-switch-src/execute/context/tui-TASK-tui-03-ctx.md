# Context: TASK-tui-03 — ShelfScreen + 換源觸發

Goal: |
  C2 主菜單：主菜單顯示「書架 / 搜尋蒐書 / 設定 / 離開」四項；j/k 上下、Enter
  進入、q 離開 process。（本 task 由「書架」項目進入 ShelfScreen）

  C5 書架換源：書架頁按 `s`，彈出單行 URL 輸入框；確認後 fetch + tx 完成（成功
  路徑）；成功後 `progress.chapter_index` 重置到新 TOC 第一章 idx 並顯示「進度
  已重置」訊息。（本 task 負責 ShelfScreen 上的 `s` 鍵觸發路由到
  SwitchSourceScreen）

Requirements:
  REQ-002: |
    TUI 主菜單 shell 與 screen 路由 — TUI 主迴圈用 `Box<dyn Screen>` 單軌路由；
    `Screen::handle_event(KeyEvent) -> Transition::{To(Box<dyn Screen>), Stay,
    Quit}`；主菜單列「書架 / 搜尋蒐書 / 設定 / 離開」。
  REQ-005: |
    換源 transaction（含失敗五類 abort）— 換源走「catalog::facade::get_source
    → catalog::facade::fetch_novel_info → catalog::facade::fetch_toc →
    library::facade::switch_source_tx」；前三步任一失敗則 abort、不進 tx、書架
    狀態完全不變；tx 內 UPDATE novels + DELETE chapters + INSERT new chapters
    + UPDATE progress 為新 TOC 首章 idx；tx 失敗整體 rollback。

Scenarios:
  REQ-002:
    - Scenario 1 (主菜單 navigation): Given 在主菜單；When 按 j/k；Then highlight
      在四個選項間上下移動
    - Scenario 2 (Enter 進子畫面): Given highlight 在「搜尋蒐書」；When 按
      Enter；Then Transition::To(SearchScreen)
    - Scenario 3 (主菜單 q 離開): Given 在主菜單；When 按 q；Then
      Transition::Quit；TUI 收尾、process exit 0
    - Scenario 4 (設定為空殼): Given 在主菜單，highlight 在「設定」；When 按
      Enter；Then 顯示「尚未實作」訊息一秒後回主菜單（本 task 不負責；列出僅
      為背景）
  REQ-005:
    - Scenario 1 (TUI shelf 換源成功): Given 書架 highlight 在 novel #1（原
      source = X）；按 `s`；When 彈出輸入框，輸入新 book_url（已 import 過新源
      Y）；確認；Then 依序呼叫 catalog::facade::get_source(Y) /
      fetch_novel_info(book_url) / fetch_toc(...) 都成功；library::facade::
      switch_source_tx 開 tx 完成 UPDATE+DELETE+INSERT+progress update；progress.
      chapter_index 為新 TOC 第一個 chapter 的 idx（不寫死 1）；回 ShelfScreen
      顯示「已換源至 Y、進度已重置」
    - Scenario 2 (失敗類 a fetch_novel_info HTTP 失敗): 不進 switch_source_tx；
      錯誤訊息「換源失敗：取得詳情頁失敗（HTTP 5xx）」；書架狀態完全不變
    - Scenario 3 (失敗類 c fetch_toc 8s timeout): 不進 tx；錯誤訊息「換源失敗：
      目錄頁讀取逾時」；書架狀態不變
    - Scenario 4 (失敗類 d 0 章): 不進 tx；錯誤訊息「換源失敗：新源目錄為空，
      可能規則錯誤」；書架狀態不變
    - Scenario 5 (失敗類 e 全 fallback name): 不進 tx；錯誤訊息「換源失敗：新源
      章節名解析全部失敗，疑為書源規則 bug」；書架狀態不變
    （本 task 只負責 `s` 鍵觸發 SwitchSourceScreen 的 Transition；五類 abort
    的偵測 / 訊息實作在 switch_source_core 與 SwitchSourceScreen 的後續 task）

Task:
  id: TASK-tui-03
  name: ShelfScreen + 換源觸發
  目標: 書架列表 + `s` 觸發 SwitchSourceScreen + Enter 進 reader + Esc/q 回主
    菜單。
  驗收標準:
    - "`src/presentation/handlers/tui/shelf.rs` 存在；`impl Screen for ShelfScreen`"
    - "顯示書架 list（從 `library::facade::list_shelf`）：`#{ID} {書名} / {作者}
      [{source}]`"
    - "j/k 移動；Enter → `Transition::To(ReaderScreen::new(EntryMode::Menu,
      novel_id))`"
    - "`s` → `Transition::To(SwitchSourceScreen::for(novel_id))`"
    - "Esc / q → MenuScreen"
    - "接受可選的「highlight_id」與「toast message」初始化（給「重複入架」場景
      用）"
    - "空書架顯示提示「（書架空、回主菜單按 q）」"
  步驟:
    - 寫檔
    - 構造接收 `Option<i64> highlight_id` + `Option<String> toast`
    - "寫 **UNIT-7**：`ShelfScreen::with_highlight(Some(novel_id),
      Some(\"msg\"))` 構造後用 `ratatui::backend::TestBackend` draw 一個 frame；
      assert frame buffer 含 \"msg\" 且預設 index 對齊 highlight 列"
    - 手動 smoke：menu → 書架 → 看到既有書

Design:
  操作流程_shelf: |
    （from design.md「整體操作流程」mermaid）
    ShelfS -->|Enter| ReaderM[ReaderScreen Menu mode]
    ShelfS -->|s| SwS[SwitchSourceScreen URL 輸入]
    ShelfS -->|Esc/q| MenuS
    SwS -->|Esc| ShelfS
    SwS -->|Enter| SwCore[switch_source_core run]
    SwCore -->|成功| ShelfReset[ShelfScreen toast 換源完成]
    SwCore -->|abort 五類| ShelfErr[ShelfScreen toast 錯誤訊息]
  畫面關聯_shelf: |
    （from design.md「畫面關聯」mermaid）
    Shelf --> ReaderM[ReaderScreen Menu]
    Shelf --> SwitchSrc[SwitchSourceScreen]
    Shelf --> Menu
    SwitchSrc -- Esc --> Shelf
    SwitchSrc -- run + 成功/失敗 toast --> Shelf
    Search -- 重複 book_url + highlight --> Shelf
  資料模型_ShelfScreen_with_highlight: |
    結構 / 欄位: `ShelfScreen::with_highlight` ctor
    位置: `presentation/handlers/tui/shelf.rs`
    變更: 新增
    說明: 簽名 `(initial_highlight: Option<i64>, initial_toast: Option<String>)
      -> ShelfScreen`；給「重複入架」與「換源完成」場景帶 hint
  資料模型_Transition: |
    結構: `Transition` enum；位置: `presentation/handlers/tui/mod.rs`；
    新增；定義 `To(Box<dyn Screen>) / Stay / Quit`
  資料模型_Screen_trait: |
    結構: `Screen` trait；位置: `presentation/handlers/tui/mod.rs`；
    新增；簽名 `draw(&mut self, frame)` + `handle_event(&mut self, KeyEvent)
    -> Transition`（注意：design.md 給的是這個簽名；本 task 補充說明的 ctx 參數
    取得問題見 Constraints）

Test:
  UNIT-7: |
    位置: `presentation/handlers/tui/shelf::tests`
    驗證點: `ShelfScreen::with_highlight(novel_id, "msg")` 構造後 `draw` 到
    `TestBackend`；assert frame buffer 含 "msg" 字串且預設 index 落在 highlight
    novel_id 對應列。
    （task 描述同步建議簡化版：toast 渲染需 ctx + DB；單測只驗 field 存放即可；
    真實渲染留 E2E-7 手動）
  E2E_對應:
    - E2E-7 重複入架 → 搜尋既有書、Enter → shelf highlight 既有列 + toast
      「已在書架第 N 本」（對應 C4，UNIT-7 自動覆蓋）
  邊界條件:
    - 空書架 → 顯示提示「（書架空、回主菜單按 q）」
    - highlight_id 對應的 novel 不存在於當前 list_shelf 結果 → 預設 select 第 0
      列（toast 仍顯示）
  TUI互動自動測試立場: |
    本期不做完整 ratatui::backend::TestBackend 自動測試（goal Out-of-scope
    聲明）；UNIT-7 是少數例外，僅驗 field 存放。

Constraints:
  範圍限制:
    - 新檔 `src/presentation/handlers/tui/shelf.rs`
    - "pub struct ShelfScreen { novels: Vec<Novel>, list_state: ListState,
      toast: Option<String> }"
    - 兩個 ctor：`pub fn new() -> Self` + `pub fn with_highlight(
      highlight_book_url: Option<String>, toast: Option<String>) -> Self`
      （with_highlight 構造後 draw 時用 highlight_book_url 比對 novels list 找
      對應 idx 把 list_state.select 設過去）
    - "impl Screen for ShelfScreen { draw / handle_event }"
  鍵綁定:
    - j/k navigate
    - Enter 進 reader：Transition::To(ReaderScreen::new(EntryMode::Menu, ctx,
      novel_id))
    - s 進 SwitchSourceScreen：Transition::To
    - Esc/q 回 MenuScreen
  Screen_trait_設計矛盾_需在此task解:
    - 問題: "Screen trait fn `draw(&mut self, frame)` 與 `handle_event(&mut
      self, key)` 都沒 ctx 參數 — ShelfScreen 需要呼 library::facade::list_shelf
      (&ctx.db) 才能拿 novels；reader/search/switch_source 同樣問題。"
    - 已評估方案: |
        a) ctor 預載 novels（持 cached），新增 refresh fn 給 Transition 回
           ShelfScreen 時重新拉資料 — 仍需 ctor 接 &AppContext
        b) Screen trait 進化成 `handle_event(&mut self, key, ctx: &mut
           AppContext) -> Transition` + `draw(&mut self, frame, ctx:
           &AppContext)` — 違反 tui/mod.rs 既有定義（trait 已定 2 參數）
    - 決策: |
        **修改 Screen trait** 加 `ctx: &mut AppContext` 第三參數（並對應
        draw）。run_loop 走 `self.current.handle_event(key, &mut self.ctx)`。
        需要回頭改 tui-01 StubMenuScreen 對應簽名 — 但 tui-01 之前還沒 impl 真
        MenuScreen 所以無影響；reader 搬遷時一併考慮。
    - 此task範圍: |
        (1) 改 Screen trait（兩 method 加 ctx 參數）— 也更新 StubMenuScreen 樣
        板；(2) 新建 ShelfScreen impl Screen with new ctx 簽名。
  禁忌_layer_invariant:
    - "C9: `src/library/` 與 `src/catalog/` 內部不得 import 對方的 facade 模組
      （本 task 不直接受影響，但 ShelfScreen 屬 presentation handler，可同時
      import library/catalog facade）"
  依賴與順序:
    - 此 task 依賴 tui-01（MenuScreen）+ tui-02（ReaderScreen）— 但 MenuScreen
      / ReaderScreen / SwitchSourceScreen 都還沒實作
    - "Transition::To 對未實作 screens 暫保 stub Transition::Stay + 內部
      toast；tui-05 / tui-06 完成時 wire 上，或在所有 7 task 完成後 final-fix
      整體 wire"
  驗收:
    - cargo build pass
    - cargo test 25/25 + 新 UNIT-7（共 26 條），既有不破
  UNIT-7_範例代碼: |
    #[cfg(test)] mod tests {
        use super::*;
        use ratatui::backend::TestBackend;
        #[test] fn unit7_with_highlight_renders_toast_text() {
            let mut shelf = ShelfScreen::with_highlight(
                None, Some("已在書架第 1 本".into()));
            // 不能直接呼 draw 因為要 frame；用 TestBackend
            let backend = TestBackend::new(80, 24);
            let mut term = ratatui::Terminal::new(backend).unwrap();
            // 用 mock empty AppContext？或讓 shelf 不需要 ctx 即可 draw
            // （toast 只是 string）
            // 簡化：assert toast field 真的存進 struct
            assert_eq!(shelf.toast.as_deref(), Some("已在書架第 1 本"));
        }
    }

Files:
  modify:
    - src/presentation/handlers/tui/mod.rs   # Screen trait 加 ctx 參數 +
                                              # StubMenuScreen 同步 + run_loop
                                              # 改用新 trait
  create:
    - src/presentation/handlers/tui/shelf.rs # ShelfScreen + UNIT-7 tests mod
