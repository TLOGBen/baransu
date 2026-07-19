task_id: TASK-shared-01
group: shared

Goal: |
  讓使用者在不離開 TUI 的前提下完成「搜尋蒐書 → 入架 → 閱讀 → 換源」整段 funnel；
  `novel-looker` 不帶參數時不再印 help，而是進入主菜單 shell；既有 CLI 子命令全部保留，
  並新增 `switch-source` 對應的 CLI 形式給 script / cron 使用。

  與本 task 相關的驗收標準：
  - C10 既有行為不破：`cargo test`（含 catalog::service::rule::tests 等既有測試）全綠；
    CLI 既有命令行為與輸出格式不變。
  - 本 task 為「加入 tui-textarea 依賴」的最小變更，作為 REQ-002（TUI 主菜單 shell）
    與 REQ-003（搜尋蒐書 funnel，使用 tui-textarea 收輸入）後續實作的前置依賴。

Requirements:
  REQ-002: |
    TUI 主菜單 shell 與 screen 路由

    描述：TUI 主迴圈用 `Box<dyn Screen>` 單軌路由；
    `Screen::handle_event(KeyEvent) -> Transition::{To(Box<dyn Screen>), Stay, Quit}`；
    主菜單列「書架 / 搜尋蒐書 / 設定 / 離開」。

  REQ-003: |
    搜尋蒐書 funnel（含全局 deadline 與進度顯示）

    描述：搜尋頁用 tui-textarea 收輸入；Enter 後對所有 `enabled` 書源序列查；
    每查完一源 redraw 顯示「正在搜 N/M (源名)」；全局 deadline 15s 到時截斷後續源、
    保留已收結果。

Scenarios:
  REQ-002:
    - "Scenario 1 主菜單 navigation：在主菜單按 j/k 時 highlight 在四個選項間上下移動"
    - "Scenario 2 主菜單 Enter 進子畫面：highlight 在「搜尋蒐書」按 Enter 時切換到搜尋頁"
    - "Scenario 3 主菜單 q 離開：按 q 時 Transition::Quit、TUI 收尾、process exit 0"
    - "Scenario 4 設定項目為空殼：highlight 在「設定」按 Enter 顯示「尚未實作」"
  REQ-003:
    - "Scenario 1 多源序列查完無 timeout：3 個 enabled 源 + 關鍵字「超維術士」，redraw 進度逐源更新，結果 < 15s"
    - "Scenario 2 全局 deadline 截斷：累計超過 15s 中止剩餘源查詢，顯示「時間預算用盡」"
    - "Scenario 3 單源錯誤不影響其他源：源 B 規則錯誤回 Err，結果頁列出該源錯誤訊息但繼續查源 C"
    - "Scenario 4 Esc 中斷搜尋輸入：在搜尋輸入框按 Esc 回主菜單"
    - "Scenario 5 結果頁 Esc 回主菜單"
  注: |
    本 task 僅為加依賴，scenarios 本身在後續 task（shared-03 widgets、search/menu screen）才會被覆蓋；
    這裡列出供 impl-agent 理解此依賴後續服務的目標。

Task: |
  TASK-shared-01: 加入 tui-textarea 依賴 + 確認既有 import 不衝突

  需求追溯：REQ-002, REQ-003

  目標：`Cargo.toml` 加入 `tui-textarea` 並通過 `cargo build`；無版本衝突。

  驗收標準：
  - [ ] `Cargo.toml` 含 `tui-textarea`（與 ratatui 0.28 / crossterm 0.28 相容版本）
  - [ ] `LIBCLANG_PATH=/usr/lib/llvm-18/lib cargo build --bin novel-looker` 成功
  - [ ] 無新增 transitive dep 出現安全警示（`cargo audit` 若有跑）

  步驟（加 dep + 驗證）：
  - [ ] 編輯 `Cargo.toml` 在 `[dependencies]` 加 `tui-textarea`（先試最新；若 build 失敗、
        降到 ratatui 0.28 對應版本）
  - [ ] `cargo build --bin novel-looker` 跑通
  - [ ] `cargo build --tests` 跑通

  使用者重點補充（覆蓋 task-shared.md 的版本選擇）：
  - 使用 `tui-textarea = "0.6"`（已驗 build 過、與 ratatui 0.28 + crossterm 0.28 相容）
  - 不動 ratatui / crossterm 版本
  - 改動只在 Cargo.toml 加一行

Design: |
  本次新增 / 變更（與本 task 相關的部分 — Cargo.toml 行）：

  | 路徑 | 變更 |
  |---|---|
  | Cargo.toml | ★ + tui-textarea（task-shared.md 列 "0.7"；使用者覆蓋為 "0.6"） |

  後續依賴此 dep 的元件（純資訊，本 task 不實作）：
  - `presentation/handlers/tui/widgets.rs` 的 `SingleLineInput` 將內包 tui-textarea
    （screen 不直接暴露 tui-textarea）
  - `presentation/handlers/tui/search.rs` 的 SearchScreen 用於關鍵字輸入框
  - `presentation/handlers/tui/switch_source.rs` 的 SwitchSourceScreen 用於 URL 輸入框

Test: |
  本 task 自動測試對應：
  - 無新增 unit / integration test。
  - 驗證以「build 通過 + 既有 cargo test 全綠（E2E-16 / C10）」為準。

  測試光譜中與本 task 相關的層級：
  - Manual smoke 與 TUI 互動自動測試（TestBackend）皆不在本 task 範圍。
  - 「既有 cargo test 全綠」對應 E2E-16，本 task 加 dep 後須仍滿足。

  驗證指令：
  - `LIBCLANG_PATH=/usr/lib/llvm-18/lib cargo build --bin novel-looker`
  - `LIBCLANG_PATH=/usr/lib/llvm-18/lib cargo build --tests`
  - （可選）`cargo audit`

Constraints:
  - ratatui 鎖在 0.28，crossterm 鎖在 0.28；本 task 不動兩者版本。
  - 使用 `tui-textarea = "0.6"`（已驗證 build 過；task-shared.md 文件原寫 "0.7" 為待驗值，
    以使用者明確指示的 "0.6" 為準）。
  - 改動範圍：只能在 `Cargo.toml` 加一行 `tui-textarea = "0.6"`，其他 0 動。
  - 不修改 `.claude/analyze/` 下任何文件。
  - 加完 dep 後第一次 build 會觸發 BoringSSL 編譯（~2-3 分鐘）為正常現象；
    後續為 incremental。
  - `LIBCLANG_PATH=/usr/lib/llvm-18/lib` 在 build 時必須帶上（wreq → boring → bindgen 需要）。
  - 不暴露 tui-textarea 給上層 screen（屬未來 task-shared-03 的限制，列在此供
    後續 task 參考；本 task 不涉及該層）。

Files:
  modify:
    - path: /home/vakarve/project/others/NovelReader/Cargo.toml
      change: |
        在 [dependencies] 區段加入一行：
          tui-textarea = "0.6"
        既有狀態（不動）：
          ratatui = "0.28"
          crossterm = "0.28"
  add: []
  delete: []
