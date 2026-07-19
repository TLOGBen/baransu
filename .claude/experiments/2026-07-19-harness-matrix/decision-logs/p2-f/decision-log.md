
## [1784435006] p2-f/spec
- Situation: Item B 演算法步驟 2「the first chapter satisfying the highest-precedence rule wins」有兩種讀法：規則優先（rule-major：a 整掃 → b 整掃 → c 整掃）或章節優先（chapter-major：逐章試 a/b/c）。
- Options: rule-major；chapter-major（低優先規則的較小 idx 章可能贏過高優先規則的較大 idx 章）。
- Decision: rule-major——每一規則各自對新 TOC 依 idx 升冪整掃，高優先規則有任何命中即定案，同規則內取 idx 最小者。
- Why: 「highest-precedence rule wins」語意指規則層級裁決先於位置裁決；chapter-major 會讓規則 c 搶走規則 a 的正確目標，違反 precedence 一詞。
- Spec-gap: brief 未明寫兩讀法之別；已在 requirement.md REQ-003 Scenario 4 釘死並要求測試覆蓋。

## [1784435006] p2-f/spec
- Situation: dao 交易需接收比中的 progress_idx，但 B5 要求既有 dao 測試（呼叫 4 參數 update_book_source_tx）原樣通過；直接改簽名須改 7+ 條既有測試。
- Options: (1) 改 4 參數簽名、機械調整全部既有 dao 測試；(2) 新增 update_book_source_tx_with_progress、原 4 參數方法降為 #[cfg(test)] 相容 wrapper（first-idx 語意委派）。
- Decision: 選 (2)。facade 改呼叫新方法；wrapper 僅供既有測試使用（cfg(test) 內有使用者、不產生新 dead_code 警告）。
- Why: 既有 dao 測試零改動最大化滿足 B5「every existing test still passes」；binary crate 中 prod fn 若僅被測試使用會觸發 dead_code 新警告，cfg(test) 同時解掉警告約束（brief 全域約束 5）。
- Spec-gap: brief 未規範簽名演進手法；none 之外補：fault 注入既有 5 參數 helper 亦簽名不動，另立 cfg(test) 的 with_progress_fault 供遷移路徑 rollback 新測試。

## [1784435006] p2-f/spec
- Situation: SwitchSourceDeps trait 需新增 get_progress / list_old_chapters 與 switch_source_tx 的 progress_idx 參數，既有兩條 FakeDeps 測試（req005_s2/s3）必須機械補齊才能編譯。
- Options: (1) trait default impl（FakeDeps 零改動）；(2) 無 default、FakeDeps 機械補方法與參數。
- Decision: 選 (2)，並在 spec 中明記此為 B5 允許的「斷言行為不變的機械調整」。
- Why: default impl 回 Ok(None)/Ok(vec![]) 會讓 RealDeps 忘記覆寫時靜默永遠走 Reset——編譯期強制實作比測試期補救可靠；req005_s2/s3 的斷言（switch_tx_called==false）一字不動。
- Spec-gap: B5 的「adapted ONLY if asserted behavior superseded」是否涵蓋純編譯性適配——判定為涵蓋（斷言未動），已記錄供評審檢視。

## [1784435006] p2-f/spec
- Situation: 遷移前的唯讀讀取（get_progress / list_old_chapters）若回 Err，走哪條路？
- Options: 靜默 fallback 到 Reset；propagate 整體換源失敗（tx 不執行）。
- Decision: propagate Err、abort（不新增第六類 abort 分類，沿用一般 Err 路徑）。
- Why: 唯讀失敗代表 DB 異常而非「查無資料」；靜默 Reset 會掩蓋錯誤且悄悄丟掉使用者進度。「查無」（None/空 TOC/比不中）才走 Reset。
- Spec-gap: brief 步驟 1 只寫「No progress row / unresolvable name → fallback」，未涵蓋讀取本身出錯；已在 REQ-004 Scenario 3 與 test.md 邊界條件釘死。

## [1784435006] p2-f/spec
- Situation: Item C 摺疊放哪一層、如何不動既有 assemble_rows 測試（req003_scenario1 造了三源同名同作者 hits，若改 assemble_rows 本體該測試必被摺疊破壞）。
- Options: (1) 改 assemble_rows 本體（C6 取代規則調整既有測試）；(2) 獨立純函數 fold_hit_rows 後處理 pass，do_search 尾端接線。
- Decision: 選 (2)。既有 5 條 assemble_rows 測試維持有效（它們測組裝層），摺疊層另測。
- Why: brief C6 明示「extend assemble_rows or add a post-pass」；post-pass 讓既有測試零改動、兩層各自可單測，符合摺疊語意是顯示層決策的定位。
- Spec-gap: 同一源重覆回報同書是否摺疊——brief 未規範；決定一樣按鍵合併（來源名可重覆出現於列表），因鍵定義只看 name/author。

## [1784435006] p2-f/spec
- Situation: A7（doc 層 & = 文件根元素）標為 bonus，是否納入 spec。
- Options: 排除（省工）；納入（select_nodes/extract_doc/extract_all_doc 以 doc.root_element() 為節點）。
- Decision: 納入（C7），與 A5 同放 TASK-a-02。
- Why: 實作面與 extract_within 修法同構（parse 前攔截 &），邊際成本低；scraper.rs 消費這三入口，legado 源含 & 的 doc 層規則可直接受益。
- Spec-gap: none。

## [1784435006] p2-f/spec
- Situation: 隱藏不變式盤點（讀碼發現、寫入 spec 防踩雷）。
- Options: —
- Decision: 記錄如下：(1) chapters.idx 非稠密（czbooks volume 列造洞），所有遷移 fixture 必須用非稠密 idx；(2) ReadProgress.scroll_offset 是 u16、dao 寫 0_i64，遷移仍寫 0 不受影響；(3) src 內既有註解 REQ-003/005/007 指涉舊 spec，與本 spec REQ 編號無關（requirement.md 已加編號範圍註記）；(4) 現有 SwitchOutcome 欄位 new_progress_idx/new_first_chapter_name 將被 ProgressMigration 變體取代，呼叫點恰兩處（CLI handler、TUI screen）；(5) fallback_chapter_name 是 pub(crate)，core 已 import，遷移不需動它；(6) 全形空白 U+3000 在 Rust char::is_whitespace 為 true，規則 b 直接用標準庫即可。
- Why: 這些是實作者最可能誤判的點；已分別錨進 requirement/design/test 對應條目。
- Spec-gap: none。

## [1784435006] p2-f/spec
- Situation: 測試策略總路線。
- Options: 端到端（真 DB 檔案/網路）；純邏輯 + in-memory 整合。
- Decision: 三 Item 全走「純函數單測（rule.rs 直呼、比對 helper 直呼、fold_hit_rows 直呼）+ FakeDeps 編排測試 + in-memory SQLite dao 整合測試」；不測 ratatui 渲染字面、不碰網路。
- Why: brief 明令離線；house style（SwitchSourceDeps fake、dao open_in_memory、assemble_rows 純測）已建立此路線；CLI/TUI 訊息屬 thin formatting，語意斷言下沉到 SwitchOutcome 變體層（test_weight: full 全task 適用）。
- Spec-gap: none。

## [1784435770] p2-f/impl
- Situation: 三 Item 的實作路線選擇。
- Options: 依 spec design.md 逐條實作；或自行變更設計。
- Decision: 全程照 spec：Item A parse 前攔 `&`（五入口全改、C7 bonus 一併做）；Item B dao 新 `update_book_source_tx_with_progress` + 4 參數降 cfg(test) shim + core step 4.5 純比對 + `ProgressMigration` 變體；Item C `fold_hit_rows` 後處理 pass + `FoldedHit`，`assemble_rows` 不動。
- Why: spec 設計已對齊全部準則與分層鐵律，讀碼未發現使其失效的事實；照做成本最低、可審計性最高。
- Spec-gap: none。

## [1784435770] p2-f/impl
- Situation: Item A C3 測試——spec requirement.md Scenario 3 期望值 `"Chapter 1章 風起"`（取代字串含尾隨空白）實測不可達：`parse_rule` 對每個 `||` 片段先 `trim()`，取代字串的尾隨空白必被剝除（既有解析行為，非本次引入）。
- Options: (1) 改 parse_rule 不 trim（動既有解析語意，風險外溢）；(2) 換用不含尾隨空白的取代字串（`Chapter-`）並在測試註解記載。
- Decision: 選 (2)，斷言 `"Chapter-1章 風起"`。
- Why: C3 要驗的是「`&` 分支照常走 regex 取代」，取代字面內容非準則本體；動 trim 行為會影響所有既有規則字串。
- Spec-gap: spec 例句未考慮 parse_rule 的 piece-level trim；已偏離 spec 字面、保留其意圖。

## [1784435770] p2-f/impl
- Situation: test.md 邊界條件「`"& || ###"` → `&` 分支不觸發 parse；壞 alternative 才報錯」——實測 `"###"` 在 `parse_alt` 就因空 selector 整條規則 bail（rule-level parse 先於逐 alternative CSS parse），該字面無法演示「lazy CSS parse」。
- Options: (1) 照字面測 Err（測不到本意）；(2) 換 CSS 層壞選擇器 `"& || :::bad"`（parse_alt 可過、Selector::parse 必炸），斷言 `&` 非空時整體 Ok。
- Decision: 選 (2)（測試 `amp_branch_skips_css_parse_entirely`）。
- Why: 邊界條件的意圖是「`&` 分支永不進 Selector::parse」；`:::bad` 恰好把懶惰求值釘死——若實作先 parse 全部 alternative 此測試必紅。
- Spec-gap: spec 例字面在 rule-level parse 就失敗；以同意圖等價字面替代並記錄。

## [1784435770] p2-f/impl
- Situation: 既有測試的機械調整實況（C12/C20 取代規則）。
- Options: —
- Decision: 共兩處：(1) switch_source_core 兩條 req005_s2/s3 的 FakeDeps 字面以 `..FakeDeps::base()` 補齊新欄位（斷言零改動；spec 已預告）；(2) search.rs `req003_scenario1` 的 match 因 `FoldedHit` 新變體非窮盡，機械補一個 panic arm（與其 StatusLine arm 同語意；spec 未預告此處——spec 寫「既有搜尋測試零改動」，但該測試對 enum 做窮盡 match，加變體必然觸碰）。dao 既有測試零改動（shim 生效）。
- Why: 兩處皆編譯性適配、斷言行為不變，落在 brief B5/C6 的 supersede-mechanical 範圍。
- Spec-gap: spec 未預見 req003_scenario1 的窮盡 match 需補 arm；此為 C20「零改動」的最小必要偏離。

## [1784435770] p2-f/impl
- Situation: 基線警告數——brief 說 2 條預期 dead_code，實測 `cargo build` 基線是 3 條（多一條 `chapter_count` is never read，pre-existing）。
- Options: (1) 順手讓訊息用上 chapter_count 消警告；(2) 完全不動，只保證不新增。
- Decision: 選 (2)。重構後的 SwitchOutcome 保留 chapter_count 欄位（spec 資料模型明列），警告維持原樣；實測改動前後皆為同 3 條。
- Why: brief 約束是「不引入新警告」；消 pre-existing 警告屬未受託的行為變更（訊息格式會偏離 spec 字面）。
- Spec-gap: brief 的「2 條」計數與實況不符，已如實記錄。

## [1784435770] p2-f/impl
- Situation: 測試策略執行結果。
- Options: —
- Decision: 照 spec 三線：rule.rs 純函數直呼（8 新測）、switch_source_core 純 helper 直呼＋FakeDeps 編排（6 helper 測 + 6 編排測，其中含 spec 未列但 test.md 邊界要求的「無 progress 列 → Reset」「比中首章仍為 Migrated」「兩讀取 Err 各自 abort」）、dao in-memory（INT-5 遷移寫入、INT-6 遷移路徑四步 rollback）、search.rs fold 純函數（7 新測含 hit_for_enter C18）。CLI/TUI 訊息維持 thin formatting 不測 ratatui 字面（語意斷言下沉到 ProgressMigration 變體）。測試數 48 → 77（+29）。
- Why: 與 spec test.md 的「E2E＝可達最高層入口」路線一致；首要交付釘死條（fake 收到 progress_idx==15、C1 非 Err、C15 3→1 列）全數落地。
- Spec-gap: none。
