Goal: |
  從 goal.md 提取與 TASK-shared-03 相關的目標段落（C3 / C4 / C5）：

  - C3 搜尋蒐書 funnel：在主菜單按 Enter 進入搜尋頁，輸入關鍵字按 Enter，
    畫面顯示「正在搜 N/M (源名)…」逐源更新；全部源查完或 15 秒 deadline
    到時截斷顯示已收結果；按 Enter 入架後跳回主菜單並顯示「已入架 #ID 書名」。
  - C4 重複入架去重：搜尋結果按 Enter 入架時，若該 book_url 已在書架，
    不 UPSERT，改顯示「已在書架第 N 本」並 highlight 對應書架列。
  - C5 書架換源：書架頁按 s，彈出單行 URL 輸入框；確認後 fetch + tx 完成（成功路徑）；
    成功後 progress.chapter_index 重置到新 TOC 第一章 idx 並顯示「進度已重置」訊息。

  本 task 的角色：抽出 C3 搜尋輸入框 / C4 入架後 toast / C5 換源 URL 輸入框
  與錯誤訊息 line 等三類 UI 共用元件，避免每個 screen 重寫；輕量、不暴露
  tui-textarea 給上層 screen。

Requirements: |
  REQ-003: 搜尋蒐書 funnel（含全局 deadline 與進度顯示）
    描述：搜尋頁用 tui-textarea 收輸入；Enter 後對所有 enabled 書源序列查；
    每查完一源 redraw 顯示「正在搜 N/M (源名)」；全局 deadline 15s 到時
    截斷後續源、保留已收結果。
    （本 task 提供 SingleLineInput 作為搜尋輸入的底層元件；單源錯誤訊息
    用 error_line 紅字一行顯示。）

  REQ-004: 入架與重複 book_url 去重
    描述：搜尋結果按 Enter 入架；若 book_url 已在書架，不 UPSERT，改顯示
    提示並 highlight 對應書架列。
    （本 task 提供 toast 用於顯示「已入架 #{ID} 書名」與「已在書架第 N 本」。）

  REQ-005: 換源 transaction（含失敗五類 abort）
    描述：換源走「catalog::facade::get_source → fetch_novel_info → fetch_toc
    → library::facade::switch_source_tx」；前三步任一失敗則 abort、不進 tx、
    書架狀態完全不變。
    （本 task 提供 SwitchSourceScreen 用的 SingleLineInput URL 輸入框；
    失敗訊息以 error_line 與 toast(Error) 呈現。）

Scenarios: |
  REQ-003 相關 scenario（input + 錯誤顯示底層元件）:
    Scenario 4 (Esc 中斷搜尋輸入): 在搜尋輸入框未按 Enter 時按 Esc → 回主菜單
      → 對應 SingleLineInput::handle_event 攔截 Esc → SingleLineEvent::Cancel。

    Scenario 3 (單源錯誤不影響其他源): 結果頁顯示「源 B：錯誤訊息」一行
      → 對應 error_line(text) -> Paragraph 紅色字一行。

  REQ-004 相關 scenario（入架後 toast）:
    Scenario 1 (首次入架): 主菜單頂顯示 toast「已入架 #{ID} 超維術士」
      → ToastKind::Info。
    Scenario 2 (重複 book_url 入架): ShelfScreen 開啟時 highlight 在該書架列、
      頂部顯示「已在書架第 N 本」 → ToastKind::Info。

  REQ-005 相關 scenario（URL 輸入 + 錯誤 toast）:
    Scenario 1 (TUI shelf 換源成功): 書架按 s 後彈出輸入框 → SingleLineInput
      接 URL，Enter 確認 → SingleLineEvent::Submit(url)。
    Scenario 2~5 (失敗五類): 顯示錯誤訊息「換源失敗：xxx」→ ToastKind::Error
      或 error_line 紅字。

Task: |
  TASK-shared-03: tui::widgets.rs — toast / 單行 input 包裝 / 錯誤訊息 line
    需求追溯：REQ-003, REQ-004, REQ-005
    目標：抽出通用 widget，避免每個 screen 重寫；輕量。

  驗收標準：
    - pub fn toast(frame: &mut Frame, msg: &str, kind: ToastKind)（ToastKind::Info/Error）
    - pub struct SingleLineInput（內部包 tui-textarea，限制單行：handle_event
      攔截 Enter / Newline）
    - pub fn error_line(text: &str) -> ratatui::widgets::Paragraph<'_>（紅色字一行）
    - 不暴露 tui-textarea 給上層 screen — screen 只用 SingleLineInput

  步驟（widget 實作）：
    - 寫 src/presentation/handlers/tui/widgets.rs
    - SingleLineInput::new(prompt: &str)、handle_event(KeyEvent) -> Option<String>
      （Enter → Some(content)、Esc → None=cancel、其他 → 寫入 textarea）
    - toast 走 ratatui::widgets::Block + Paragraph 浮在上層；簡單版 = 螢幕頂 1 列

  步驟（驗證）：
    - cargo build 過
    - 寫 UNIT-6（test.md）：構造 SingleLineInput → 餵 'h'/'i' + Enter 回 Some("hi")；
      新 instance 餵 Esc 回 None；連按多 Enter 維持單行

  注意：上層下達的 Constraints 將回傳值類型從 task-shared.md 的 Option<String>
  精化為 SingleLineEvent enum（Submit(String) / Cancel / Edit），以及 toast
  簽名增加 area: Rect 參數。實作以 Constraints 為準。

Design: |
  資料模型表中與本 task 相關的列：

  | 結構 / 欄位 | 位置 | 變更 | 說明 |
  |---|---|---|---|
  | Transition enum | presentation/handlers/tui/mod.rs | 新增 | （由 TASK-shared-02 提供，本 task 不需新增） |
  | Screen trait | presentation/handlers/tui/mod.rs | 新增 | （由 TASK-shared-02 提供） |

  widgets.rs 不在資料模型表中明列為新結構，但屬於設計圖中：

    src/presentation/handlers/tui/
      ├── mod.rs           App / EventLoop / Screen trait / Transition
      └── widgets.rs       通用 widget（toast、modal、輸入框 wrapper）

  上下游關係（design.md 操作流程圖）：
    - SearchScreen / SwitchSourceScreen 是本 task 的下游消費者
    - SwitchSourceScreen 走 "Enter → switch_source_core::run" 路徑時，
      Enter 訊號由本 task 的 SingleLineInput::handle_event 產生 Submit

  錯誤處理策略表中：
    - TUI screen 拿到 Result::Err → 顯示為畫面內錯誤訊息（toast / 紅色一行）
      → 對應 toast(ToastKind::Error) 與 error_line() 兩條呈現管道

Test: |
  UNIT-6 SingleLineInput key 行為
    位置：presentation/handlers/tui/widgets::tests
    驗證點：
      - 餵 'h' / 'i' + Enter → Some("hi")（依 Constraints 精化為
        SingleLineEvent::Submit("hi")）
      - 新 instance 餵 Esc → None（依 Constraints 精化為 SingleLineEvent::Cancel）
      - 連按多 Enter 維持單行不換行

  測試光譜：Unit 層、cargo test、不需 sqlite / 不需網路。

  關鍵邊界條件（test.md「關鍵邊界條件」段落中無直接列 UNIT-6 對應的
  business 邊界 — 本 task 為 UI 元件 baseline；C2 / C3 在覆蓋對應表中
  以 UNIT-6 作為「input baseline」自動測試覆蓋）。

Constraints: |
  - 新檔位置：src/presentation/handlers/tui/widgets.rs
  - 公開 API（依上層派遣指令，精化自 task-shared.md 的描述）：
      * pub fn toast(frame: &mut Frame, area: Rect, msg: &str, kind: ToastKind)
      * pub enum ToastKind { Info, Error }
      * pub struct SingleLineInput（內含 tui_textarea::TextArea）
          - pub fn new(prompt: &str) -> Self
          - pub fn handle_event(&mut self, key: KeyEvent) -> SingleLineEvent
      * pub enum SingleLineEvent { Submit(String), Cancel, Edit }
      * pub fn error_line(text: &str) -> Paragraph<'_>（紅色字一行）

  - SingleLineInput 攔截 Enter → Submit、Esc → Cancel；其他鍵餵給 tui_textarea
  - 不暴露 tui-textarea 給上層 screen（封裝為 implementation detail）
  - 單行限制：連按多 Enter 不會換行（透過攔截 Enter 自然達成；不可讓 TextArea
    內部插入 newline）
  - 依賴 task-shared-02（mod.rs 必須先存在；本 task 在 mod.rs 加 `pub mod widgets;`）
  - 依賴 task-shared-01（tui-textarea 已在 Cargo.toml）

  驗收：
    - cargo build 過
    - cargo test handlers::tui::widgets::tests 全綠

  專案層 coding-style（user CLAUDE.md）：
    - 不可變優先（函式回傳新值，避免修改既有物件 — 本 task 的 SingleLineInput
      handle_event 內部修改 self 為合理例外，因 widget 即狀態載體）
    - 函式 < 50 行、檔案 < 800 行
    - 完整錯誤處理（key event 解析、Submit 時 trim/驗證留給上層 screen 決定）

Files:
  create:
    - src/presentation/handlers/tui/widgets.rs
  modify:
    - src/presentation/handlers/tui/mod.rs  # 加 `pub mod widgets;`
