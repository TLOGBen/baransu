# Context: TASK-tui-04 — SearchScreen 輸入框 + 逐源 funnel + 15s deadline

Goal: |
  與此 task 相關的 goal 條目：

  - C3 搜尋蒐書 funnel：在主菜單按 Enter 進入搜尋頁，輸入關鍵字按 Enter，畫面顯示
    「正在搜 N/M (源名)…」逐源更新；全部源查完或 15 秒 deadline 到時截斷顯示已收結果；
    按 Enter 入架後跳回主菜單並顯示「已入架 #ID 書名」
  - C4 重複入架去重：搜尋結果按 Enter 入架時，若該 `book_url` 已在書架，**不** UPSERT，
    改顯示「已在書架第 N 本」並 highlight 對應書架列

Requirements:
  REQ-003:
    name: 搜尋蒐書 funnel（含全局 deadline 與進度顯示）
    description: |
      搜尋頁用 tui-textarea 收輸入；Enter 後對所有 `enabled` 書源序列查；每查完一源
      redraw 顯示「正在搜 N/M (源名)」；全局 deadline 15s 到時截斷後續源、保留已收結果。

  REQ-004:
    name: 入架與重複 book_url 去重
    description: |
      搜尋結果按 Enter 入架；若 `book_url` 已在書架，**不** UPSERT 任何欄位，
      改顯示提示並 highlight 對應書架列。

Scenarios:
  REQ-003:
    - "Scenario 1 多源序列查完無 timeout: Given 有 3 個 enabled 源；輸入「超維術士」。
       When 按 Enter。Then 依序 redraw 顯示「正在搜 1/3 (源 A)」→「正在搜 2/3 (源 B)」→
       「正在搜 3/3 (源 C)」。And 結果頁列出三源各自命中（書名 / 作者 / [來源]），順序為
       A→B→C 內各自插入順序。And 整體耗時 < 15s 完成。"
    - "Scenario 2 全局 deadline 截斷: Given 有 5 個 enabled 源，源 D 慢；源 A/B/C 都在 3s
       內回；源 D 在 9s 還沒回。When 累計超過 15s。Then 中止源 D 的等待、不查源 E；
       結果頁顯示 A/B/C 命中 + 一行警示「源 D 逾時、源 E 未查（時間預算用盡）」。"
    - "Scenario 3 單源錯誤不影響其他源: Given 源 B 規則寫錯、`scraper.search` 回 Err。
       When 序列查到源 B。Then 結果頁顯示「源 B：錯誤訊息」一行；繼續查源 C。
       And 不中止整體 funnel。"
    - "Scenario 4 Esc 中斷搜尋輸入: Given 在搜尋輸入框，尚未按 Enter。
       When 按 Esc。Then Transition::To(MenuScreen) 回主菜單。"
    - "Scenario 5 結果頁 Esc 回主菜單: Given 在搜尋結果列表。
       When 按 Esc。Then Transition::To(MenuScreen)。"
  REQ-004:
    - "Scenario 1 首次入架: Given 搜尋結果列表，highlight 在「超維術士 / 牧狐 / [czbooks]」；
       此 book_url 未在 `novels`。When 按 Enter。Then 呼叫
       catalog::facade::fetch_novel_info + library::facade::add_novel。
       And Transition::To(MenuScreen)。And 主菜單頂顯示 toast「已入架 #{ID} 超維術士」。"
    - "Scenario 2 重複 book_url 入架: Given 搜尋結果 highlight 的 book_url 已存在
       `novels` 表（例如該書曾被 add 過）。When 按 Enter。Then **不**呼叫 add_novel、
       **不** UPSERT 既有 row 的 name/author/intro。And Transition::To(ShelfScreen)。
       And ShelfScreen 開啟時 highlight 在該書架列、頂部顯示「已在書架第 N 本」。"

Task:
  id: TASK-tui-04
  title: SearchScreen — 輸入框 + 逐源 funnel + 15s deadline
  traceability: REQ-003, REQ-004
  目標: tui-textarea 收輸入；Enter 後跑搜尋；展現結果列表；Enter 入架（含重複偵測）。

  驗收標準:
    - "`src/presentation/handlers/tui/search.rs` 存在；`impl Screen for SearchScreen`"
    - "State machine（內部）：`Input → Searching(loop_state) → Results`"
    - "Input：tui-textarea 收字；Enter → Searching；Esc → MenuScreen"
    - "Searching：每跑完一源 redraw 顯示「正在搜 N/M (源名)…」；單源預算 =
       `max(2s, remaining/remaining_count)`；總 deadline 15s；超時 break；單源錯誤記下不中斷"
    - "Results：列出（書名 / 作者 / [來源]）；包括「源 X 錯誤訊息」/「源 Y 逾時」/
       「源 Z 未查（時間預算用盡）」這類訊息列"
    - |
      Enter on book hit：
        - 重複偵測：先呼 `library::facade::get_novel_by_url(new_book_url)`
          （既有有則用，否則加）→ Some(novel) →
          `Transition::To(ShelfScreen::with_highlight(novel.id, "已在書架第 N 本"))`
        - None → `catalog::facade::fetch_novel_info` + `library::facade::add_novel` →
          `Transition::To(MenuScreen::with_toast("已入架 #ID 書名"))`
    - "Esc on Results → MenuScreen"

  步驟:
    重複偵測_helper:
      - 檢查 `library::facade` 是否已有「by book_url 查 novel」的 fn；若無，
        加一條 `pub fn get_novel_by_book_url(db: &LibraryDb, book_url: &str) -> Result<Option<Novel>>`
        （這是合理的 library facade 純查詢、不破 invariant）。
    搜尋迴圈:
      - 寫單源搜尋（catalog::facade::list_sources → 過 enabled →
        對每個跑 scraper.search with per-source budget）。
      - redraw 中間態：handle_event 內 await 一個源、redraw、再 await 下一個
        （不開 tokio task — Not building 明示）。
    重複偵測:
      - Enter 上 hit 時：先用 `get_novel_by_book_url(hit.book_url)` 查；按結果分流。
    驗證:
      - cargo build 過。
      - E2E-1（funnel）、E2E-7（重複）、E2E-8a / 8b / 8c
        （單源錯誤 / 單源 timeout / 全局 deadline）手動跑。

Design:
  搜尋蒐書_funnel_sequence: |
    sequenceDiagram
      participant SearchS as SearchScreen
      participant Cat as catalog::facade
      participant Scr as Scraper
      participant DB as LibraryDb

      SearchS->>Cat: list_sources(db) → 拿 enabled 源
      Cat-->>SearchS: Vec BookSource (N)
      Note over SearchS: deadline = Instant::now() + 15s
      loop 每個源 (序列)
        alt now < deadline
          SearchS->>SearchS: redraw "正在搜 i/N (源名)"
          SearchS->>Scr: search(src, keyword) with per_source_budget =
                        max(2s, remaining/remaining_count)
          Scr-->>SearchS: Vec SearchHit or Err or Timeout
          SearchS->>SearchS: append hits / error_line / timeout_line
        else 超 deadline
          SearchS->>SearchS: 標記剩下源「時間預算用盡」、break
        end
      end
      SearchS->>SearchS: 切到結果列表畫面

  flowchart_relevant_branch: |
    SearchS -->|Esc| MenuS
    SearchS -->|輸入後 Enter| FetchLoop[逐源序列查 + redraw]
    FetchLoop -->|15s 到| Results[結果列表]
    FetchLoop -->|全查完| Results
    Results -->|Esc| MenuS
    Results -->|Enter 入架| AddCheck{book_url 已存在}
    AddCheck -->|否| AddDo[add_novel toast 已入架] --> MenuS
    AddCheck -->|是| ShelfHL[ShelfScreen highlight 既有列 toast 已在書架]

  per_source_budget_公式:
    formula: "per_source_budget = max(2s, remaining/remaining_count)"
    contract: |
      design 期建議值，**不**在 test acceptance 內 enforce 具體秒數。實作期可依實測調整
      （例如改成「前 2 源各 3s、之後吃剩」）；REQ-003 Scenario 的時間描述為示意，不是精確契約。
      E2E-8a/8b/8c 驗證的是「對應狀態列訊息有顯示」而非「每源預算 N 秒」。

  資料模型_相關: |
    - Screen trait（在 `presentation/handlers/tui/mod.rs`）：
      `draw(&mut self, frame)` + `handle_event(&mut self, KeyEvent) -> Transition`
    - Transition enum：`To(Box<dyn Screen>) / Stay / Quit`
    - ShelfScreen::with_highlight ctor 簽名：
      `(initial_highlight: Option<i64>, initial_toast: Option<String>) -> ShelfScreen`
    - library::facade::get_novel_by_book_url 新增（若無）：
      給 SearchScreen 重複入架偵測；純查詢、不破 invariant。

  錯誤處理策略_相關:
    - Scraper：HTTP / 解析 / timeout 回 `Result::Err`；不 panic。
    - catalog::facade：propagate Scraper err；維持既有 anyhow chain。
    - TUI screen：拿到 Result::Err 顯示為畫面內錯誤訊息（toast / 紅色一行）；
      Esc / 任意鍵繼續。

Test:
  E2E_相關:
    - "E2E-1 主菜單 funnel 一氣呵成：起點 `novel-looker`（無 args）；終點 reader
       顯示某章內文；對應 C1, C2, C3, C4, C7。"
    - "E2E-7 重複入架：搜尋既有書、Enter；shelf highlight 既有列 + toast
       「已在書架第 N 本」；對應 C4。"
    - "E2E-8a 單源錯誤訊息列出：搜尋時其中一源規則寫錯回 Err；結果列含
       「源 X：錯誤訊息」一行 + 其他源命中正常；對應 C3。"
    - "E2E-8b 單源 timeout 列出：搜尋時某源網路慢、超過 per-source budget；
       結果列含「源 Y：逾時」一行 + 後續源繼續查；對應 C3。"
    - "E2E-8c 全局 deadline 截斷：5 個源、累計超 15s；結果列含已收命中 +
       「源 Z 未查（時間預算用盡）」；對應 C3。"

  自動測試:
    狀態: 本 task 不要求 TUI 互動自動測試（goal Out-of-scope 已聲明）。
    通用驗證:
      - cargo build pass
      - cargo test 不破（E2E-16）

  關鍵邊界條件_相關:
    - "重複 book_url 入架 → REQ-004 Scenario 2 → E2E-7 覆蓋"
    - "15s 全局 deadline 觸發 → REQ-003 Scenario 2 → E2E-8 覆蓋（手動 smoke + 計時觀察）"
    - "單源錯誤不中斷整體 funnel → REQ-003 Scenario 3 → E2E-8 同場景觀察"

Constraints:
  從_spec_文件:
    - "Out-of-scope：async fetch 改造 — 搜尋 / sync / fetch_content 維持 inline await；
       只在搜尋頁的逐源迴圈間 redraw 顯示進度 — 不引入 tokio mpsc / select 機制。"
    - "Out-of-scope：多源結果摺疊 / dedup — 同一本書在 N 個源出現就顯示 N 行。"
    - "Out-of-scope：TUI 互動 unit test（ratatui 0.28 無官方 TestBackend 友善的
       stateful screen 機制）。"
    - "Layer invariant：實作後 `src/library/` 與 `src/catalog/` 內部不得 import
       對方的 `facade` 模組；所有跨 context 組合都在 `src/presentation/handlers/` 下進行。"
    - "重複 book_url 入架時：**不** UPSERT 任何欄位（不改 name/author/intro）。"
    - "搜尋頁是逐源序列（不平行）；單源錯誤記下不中斷整體 funnel。"
    - "全局 deadline 15s 到時截斷後續源、保留已收結果。"
    - "Screen::handle_event 返回 Transition；async await 在內進行（async fn）；
       inline await 卡 UI 5-15s 是 spec 接受。"

  從_user_prompt_實作取捨:
    - "tui-04 第一版接受「進入 Searching 後一次性 await 完所有源、no per-source redraw」
       — UX 比 spec 略遜但實作簡單。後續可加 tokio mpsc 改善（Not building 排除這個）。"
    - "Transition::To(ShelfScreen) / Transition::To(MenuScreen) 都依賴前置 task
       的 screen 存在；run_loop 與 ctx 已 ready 自 hc-03。"
    - "預期執行順序：先做 tui-01 (Menu)、tui-03 (Shelf)、再做 tui-04。"

  資料結構契約:
    - |
      enum SearchState {
          Input(SingleLineInput),
          Searching { progress: String },
          Results { hits: Vec<SearchHit>, list_state: ListState },
      }
    - "pub struct SearchScreen { state: SearchState }"
    - "impl Screen for SearchScreen（ctx 參數版本 — 假設 tui-03 已改 trait）"

  UI:
    - "Input state：tui_textarea 透過 widgets::SingleLineInput 顯示"
    - "Searching state：顯示「正在搜尋（請稍候，最多 15 秒）...」"
    - "Results state：列表顯示 hits（書名 / 作者 / [源名]）；status_line 用紅色"

Files:
  新增:
    - "src/presentation/handlers/tui/search.rs"
  修改:
    - "src/presentation/handlers/tui/mod.rs — 加 `pub mod search;`"
  可能修改_視既有_facade_狀況:
    - "src/library/facade.rs — 若無 `get_novel_by_book_url` 則新增"
  依賴_screen_須由其他_task_提供:
    - "src/presentation/handlers/tui/menu.rs — MenuScreen（tui-01 提供）"
    - "src/presentation/handlers/tui/shelf.rs — ShelfScreen::with_highlight（tui-03 提供）"
    - "src/presentation/handlers/tui/mod.rs — Screen trait / Transition / EntryMode / App / ctx
       （handlers-core 群組提供）"
  search_迴圈_inline_await_範本:
    location: src/presentation/handlers/tui/search.rs (handle_event Enter 路徑內)
    code: |
      let sources = catalog::facade::list_sources(&ctx.db)?
          .into_iter()
          .filter(|s| s.enabled)
          .collect::<Vec<_>>();
      let deadline = Instant::now() + Duration::from_secs(15);
      let mut hits = Vec::new();
      for (i, src) in sources.iter().enumerate() {
          if Instant::now() >= deadline {
              hits.push(SearchHit::status_line(format!(
                  "源 {} 未查（時間預算用盡）", src.book_source_name
              )));
              continue;
          }
          self.state = SearchState::Searching {
              progress: format!("正在搜 {}/{} ({})...",
                  i+1, sources.len(), src.book_source_name),
          };
          // 不能在 handle_event 內 redraw — 受限於 trait 簽名
          // 簡化：搜尋全程把 progress 累進 self.state.progress，run_loop 下一輪 redraw 顯示
          match ctx.scraper.search(src, keyword).await {
              Ok(items) => hits.extend(items),
              Err(e) => hits.push(SearchHit::status_line(
                  format!("源 {}：{}", src.book_source_name, e)
              )),
          }
      }
      self.state = SearchState::Results { hits, list_state };
