# Context: task-b（換源盡力遷移閱讀進度）

```yaml
Goal: >
  換源時以章名比對盡力遷移閱讀進度（規則 a 精確相等 → b 去全部 Unicode 空白相等 →
  c 章號 token 相等；同規則內沿新 TOC idx 升冪取第一命中），命中寫該 idx、未命中
  維持現行重置到首章；SwitchOutcome 攜帶「已遷移 vs 已重置」並在 CLI 與 TUI 兩路
  徑呈現。對應驗收 C8–C14（= 簡報 B1–B7）。

Requirements:
  - "REQ-003: 章名比對進度遷移 —— 比對於 abort 判定之後、tx 之前；解析任何失敗（無 progress、名不可解析、Err）一律降級未命中，不新增 abort 類別"
  - "REQ-004: SwitchOutcome.progress（Migrated{idx,name} / Reset）由 CLI println 與 TUI toast 兩路徑呈現"
  - "注意：程式碼註解中的 REQ-005/REQ-007 為舊 spec 編號，與本 spec 無關；追溯用本 spec 的 REQ-003/REQ-004"

Scenarios:
  - "精確同名：舊名 第2章 破曉、新 TOC [(0,序),(3,第1章 黎明),(5,第2章 破曉)]（idx 非稠密）→ chapter_index==5、scroll_offset==0、Migrated{5, 第2章 破曉}"
  - "去空白：第2章　破曉（全形空白）vs (4, 第2章 破曉) → idx 4（規則 b）"
  - "章號 token：第１２章 風起（全形數字）vs (20, 第12章 風起雲湧) → idx 20；第十二章 vs 第12章 不互轉、不命中"
  - "全未命中 / 無 progress / 舊名不可解析 → 重置到新首 idx、scroll_offset 0 —— 與現況完全一致"
  - "五類 abort 任一觸發 → tx 不被呼叫（既有 req005_s2/s3 測試原樣通過）"
  - "CLI 遷移訊息含「進度已遷移」+ 章名；重置訊息含「進度重置」；TUI toast 同兩態"

Task: |
  TASK-b-01: dao / facade 交易加 progress_idx: Option<i64> 參數（REQ-003, test_weight: full）
  驗收標準：
  - [ ] Some(5)（非首章 idx、模擬非稠密 TOC）→ tx 後 progress.chapter_index == 5、scroll_offset == 0、回傳 5（C8 dao 半邊）
  - [ ] None → chapter_index == 新 TOC 首 idx —— 既有 int1 斷言值不變（C11）
  - [ ] 既有 fault-injection（step 1–4）與整合測試僅補 None 即原樣通過；rollback 語意不變（C12）
  - [ ] facade 仍不 import 任何 catalog::*（C22）

  TASK-b-02: 純函數 find_migration_target（REQ-003, test_weight: full）
  驗收標準：
  - [ ] 規則 a：第2章 破曉 對 [(0,序),(3,第1章 黎明),(5,第2章 破曉)] → Some((5, "第2章 破曉"))（C8）
  - [ ] 規則 b：全形空白 vs 半形空白命中（C9）；舊名去空白後為空字串 → 跳過規則 b（邊界）
  - [ ] 規則 c：regex 第\s*([0-9０-９一二三四五六七八九十百千零〇两兩]+)\s*[章回節节卷] 首捕獲組、全形數字正規化半形、字串比較；第１２章 vs 第12章 風起雲湧 命中（C10）；第十二章 vs 第12章 不命中；單邊無 token 不命中（邊界）
  - [ ] 三規則皆不中 → None（C11 純函數半邊）
  - [ ] 同名多章 → 取 idx 升冪第一個（邊界）
  - [ ] 高優先規則命中即短路：規則 a 有命中時，縱使更低 idx 處存在規則 b/c 命中，仍回規則 a 者

  TASK-b-03: run_with_deps 接線（REQ-003, REQ-004, test_weight: full）
  驗收標準：
  - [ ] RealDeps::current_chapter_name = library::facade::get_progress 的 chapter_index → library::facade::list_chapters 中同 idx 者之 name；任一環節 None 即 Ok(None)
  - [ ] fake current_chapter_name 回 Some("第2章 破曉") 且新 TOC 含 (5, "第2章 破曉") → fake 記錄到的 progress_idx == Some(5)、SwitchOutcome.progress == Migrated { idx: 5, name: "第2章 破曉" }（C8）
  - [ ] fake 回 None 或不相干名 → progress_idx == None、progress == Reset、new_progress_idx == 首 idx（C11）
  - [ ] fake 回 Err(...) → run_with_deps 仍 Ok、Reset、tx 有被呼叫（降級不 abort；邊界）
  - [ ] 既有 req005_s2/s3 abort-before-tx 測試原樣通過（FakeDeps 補新方法即可；C12）
  - [ ] 時序：current_chapter_name 的呼叫在 evaluate_toc 之後、switch_source_tx 之前

  TASK-b-04: CLI / TUI 兩路徑呈現（REQ-004, test_weight: full）
  驗收標準：
  - [ ] 遷移態訊息含「進度已遷移」與命中章名（例：進度已遷移：第2章 破曉（idx 5））；不得以 idx+1 推導「第N章」（idx 非稠密）
  - [ ] 重置態訊息含「進度重置」與首章名（可沿用既有 new_first_chapter_name）（C13）
  - [ ] 訊息組裝抽成可單測純函數（建議 switch_source_core.rs 內 describe_progress(outcome) -> String），CLI/TUI 共用；unit test 斷言兩態字串（C13, C14）
  - [ ] CLI 既有「進度重置到第 N 章」字樣被本準則明文取代；若有測試斷言該字樣（現況無）適配並記決策日誌

Design: >
  比對純函數與 ProgressResolution enum 放 switch_source_core.rs（先例：evaluate_toc）。
  SwitchSourceDeps trait 加 current_chapter_name(novel_id) -> Result<Option<String>>；
  RealDeps 組合 library::facade（get_progress + list_chapters）。dao update_book_source_tx
  三簽名（含 _with_fault/_inner）各加尾參 progress_idx: Option<i64>，step 4 UPSERT 與
  回傳值改 progress_idx.unwrap_or(first_idx)，其餘四步不動；facade switch_source_tx
  直傳。SwitchOutcome 加 progress: ProgressResolution 欄（既有三欄不動，重置訊息仍
  用 new_first_chapter_name）。ProgressResolution derive Debug + PartialEq。
  regex 於函數內編譯即可（換源一次一呼）。

Test: >
  RED 先行、斷言具名值。三層：純函數層（find_migration_target tuple 斷言）、
  fake deps 層（FakeDeps 加 recorded_progress_idx 記錄 tx 收到的參數；Err 降級
  情境斷言 Ok + Reset + switch_tx_called==true）、dao in-memory 層（Some(5) 情境
  SELECT chapter_index==5；沿用既有 Fixture/Snapshot 風格）。describe_progress
  兩態字串 unit test。首要交付釘死：C8 測試在功能缺席時 chapter_index 必為首 idx
  （紅）、實作後為 5（綠）。

Constraints:
  - "五類 pre-tx abort 與單一交易原子性完全不動（C12 = 簡報 B5）；比對步驟不得新增 abort 出口"
  - "idx 非稠密 0..N-1 —— 嚴禁 第N章 → idx N-1 假設；訊息不得以 idx+1 推導章號（CLAUDE.md 已證實 czbooks 首列 idx 空洞）"
  - "分層：service/*.rs 禁 rusqlite/dao；facade 不跨 context 互呼；跨 context 組合只在 presentation/handlers/；不動任何 mod.rs（ProgressResolution 屬 presentation 內部型別，不進 Library PL）"
  - "既有測試僅允許機械適配（呼叫點補 None、FakeDeps 補新方法）；任何斷言行為變更須被 C 準則明文取代並記 .exp/decision-log.md"
  - "禁止網路測試；不引入新警告"

Files:
  - src/library/dao.rs
  - src/library/facade.rs
  - src/presentation/handlers/switch_source_core.rs
  - src/presentation/handlers/switch_source.rs
  - src/presentation/handlers/tui/switch_source.rs
```
