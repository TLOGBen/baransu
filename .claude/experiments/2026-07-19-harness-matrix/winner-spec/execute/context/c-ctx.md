# Context: task-c（跨源搜尋結果摺疊）

```yaml
Goal: >
  TUI 跨源搜尋結果依 (name.trim(), author-or-empty.trim()) 摺疊為單列：顯示書名、
  作者、來源數與全部來源名；摺疊列停在首次出現位置；StatusLine 與單源列不受影響；
  Enter 作用於第一來源之 hit。對應驗收 C15–C20（= 簡報 C1–C6）。

Requirements:
  - "REQ-005: 純函數 post-pass fold_rows —— 同鍵 Hit 併入首次出現位置；assemble_rows 本體與既有測試不動"
  - "REQ-006: Folded 列互動 —— Enter 取 hits[0]；first_hit_idx 把 Folded 視為命中列"
  - "注意：程式碼註解中的 REQ-003 為舊 spec 編號，與本 spec 無關"

Scenarios:
  - "三源同書（超維術士/牧狐 × A,B,C）→ 一列 Folded、hits.len==3、來源序 [A,B,C]、渲染含來源數與全部來源名"
  - "同名不同作者 → 兩列各自保留；author None / Some(\"\") / Some(\"  \") 視為同作者鍵"
  - "[Hit X(A), Hit Y(B), Hit X(C)] → [Folded X{A,C}, Hit Y(B)] —— 首位保留、單源維持 Hit variant"
  - "[Hit X(A), Status(源 B：逾時), Hit X(C), Status(源 D 未查)] → [Folded X{A,C}, Status, Status] —— StatusLine 相對存活列位置不變"
  - "Enter on Folded [(hit_A, A), (hit_C, C)] → 以 hit_A 走既有入架/重複偵測流程"
  - "rows 首列為 Folded 時 first_hit_idx 選中它"

Task: |
  TASK-c-01: 純函數 fold_rows post-pass（REQ-005, test_weight: full）
  驗收標準：
  - [ ] 三源同書 → 一列 Folded，hits.len == 3、來源名依出現順序（C15）
  - [ ] 同名不同作者（或同作者不同名）不摺疊（C16）；author: None / Some("") / Some("  ") 同鍵（邊界）
  - [ ] 首次出現位置保留；單源命中維持 Hit variant（渲染路徑不變）（C17）
  - [ ] StatusLine 相對存活列位置不變（C19）；fold_rows(vec![]) → vec![]（邊界）
  - [ ] 同一來源重複命中同書 → 照併、計數含重複（邊界，記決策日誌）
  - [ ] 既有 assemble_rows 5 條測試與其餘搜尋測試原樣通過（C20）

  TASK-c-02: Folded 列渲染與互動（REQ-005, REQ-006, test_weight: full）
  驗收標準：
  - [ ] Folded 顯示文字含書名、作者（無作者顯示 -）、來源數、全部來源名（格式例：超維術士 / 牧狐 [3源: A, B, C]）（C15 顯示半邊）
  - [ ] Enter on Folded → 取 hits[0].0.clone() 流入既有分支 —— selected_hit 抽取處（search.rs:186 附近）補 Folded arm（C18）
  - [ ] first_hit_idx 的 position 判斷改為 matches!(r, Hit{..} | Folded{..})（REQ-006）
  - [ ] j/k 行為不需改（列數已縮減即自然正確）
  - [ ] cargo test 全綠、無新警告（C21）

Design: >
  新 variant HitOrStatus::Folded { hits: Vec<(SearchHit, String)> }（不變式 len>=2；
  單源列維持 Hit → C17 由型別保證）。fold_rows：一次走訪 + HashMap<(String,String),
  usize> 記首次出現輸出位；Hit 遇已有鍵 → 首位元素升級 Folded 並 push (hit, source_name)；
  StatusLine 直接 push。do_search 末行改 fold_rows(assemble_rows(per_source)) ——
  assemble_rows 本體不動，其既有 5 條測試（含三源同書出三列的 scenario1，測的是
  assemble_rows 而非 fold_rows）原樣保留。draw() 加 Folded arm；顯示字串抽純函數
  folded_label(hits) -> String。handle_event Enter：Folded => hits.first() 之 hit clone。

Test: >
  RED 先行、斷言具名值（variant、位置、hits.len、來源名序列、標籤字串含 "3源" 與
  "A, B, C"）。C15/C16/C17/C19 各至少一條純函數測試；Enter 抽取斷言 == hits[0].0；
  first_hit_idx 首列 Folded 情境。首要交付釘死：C15 測試在摺疊缺席時 3 列（紅）、
  實作後 1 列（綠）。

Constraints:
  - "assemble_rows 本體與其既有 5 條測試一字不改；既有 req003_scenario1_three_sources_all_hit 不得刪改（它測 assemble_rows，摺疊以 post-pass 實作即不衝突）"
  - "摺疊鍵嚴格 = (name.trim(), author-or-empty.trim())；來源名依出現順序"
  - "presentation 層：可同時 import catalog/library facade（screen = handler 同權限）；不動 Catalog PL（SearchHit 不加欄位）"
  - "source-picker UI 屬 bonus 不要求 —— 最低要求 Enter 作用第一來源即可"
  - "禁止網路測試；不引入新警告；不碰 tui/search.rs 以外檔案"

Files:
  - src/presentation/handlers/tui/search.rs
```
