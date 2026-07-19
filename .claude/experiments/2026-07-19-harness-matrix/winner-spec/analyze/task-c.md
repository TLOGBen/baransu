# Tasks: c（跨源搜尋結果摺疊）
**前置群組**：無

> 唯一觸及檔案：`src/presentation/handlers/tui/search.rs`。
> 硬規則：`assemble_rows` 本體與其既有 5 條測試一字不改（C20 以 post-pass 達成）；既有 `req003_scenario1_three_sources_all_hit` 測的是 `assemble_rows`（非 `fold_rows`），不受影響、不得刪改。
> 程式碼註解中的舊 `REQ-003` 編號與本 spec 無關。

## TASK-c-01: 純函數 `fold_rows` post-pass

**需求追溯**：REQ-005
**測試重量建議**：full
**目標**：新增 `HitOrStatus::Folded { hits: Vec<(SearchHit, String)> }` variant 與 `pub fn fold_rows(rows: Vec<HitOrStatus>) -> Vec<HitOrStatus>`：同鍵 `(name.trim(), author-or-empty.trim())` 的 `Hit` 併入首次出現位置（第二筆起首筆升級為 `Folded`）；`StatusLine` 原樣通過；`do_search` 末行改為 `fold_rows(assemble_rows(per_source))`。
**驗收標準**：
- [ ] 三源同書 → 一列 `Folded`，`hits.len == 3`、來源名依出現順序（C15）
- [ ] 同名不同作者（或同作者不同名）不摺疊（C16）；`author: None` / `Some("")` / `Some("  ")` 同鍵（邊界）
- [ ] 首次出現位置保留；單源命中維持 `Hit` variant（渲染路徑不變）（C17）
- [ ] `StatusLine` 相對存活列位置不變（C19）；`fold_rows(vec![])` → `vec![]`（邊界）
- [ ] 同一來源重複命中同書 → 照併、計數含重複（邊界，記決策日誌）
- [ ] 既有 `assemble_rows` 5 條測試與其餘搜尋測試原樣通過（C20）

### 步驟

#### 實作
- [ ] 加 `Folded` variant（`#[allow(dead_code)]` 不需要 —— draw/handle_event 會用到）
- [ ] `fold_rows`：一次走訪 + `HashMap<(String, String), usize>` 記首次出現輸出位；`Hit` 命中已有鍵 → 將首位元素升級 `Folded` 並 push `(hit, source_name)`；`StatusLine` 直接 push
- [ ] `do_search` 接上 post-pass

#### 測試（RED 先行）
- [ ] 覆蓋上列驗收標準（C15/C16/C17/C19 各至少一條；斷言 variant、位置、`hits.len`、來源名序列等具名值）

---

## TASK-c-02: Folded 列渲染與互動

**需求追溯**：REQ-005, REQ-006
**測試重量建議**：full
**目標**：`draw()` 渲染 `Folded` 列為「書名 / 作者 [N源: 全部來源名]」；Results 的 Enter 對 `Folded` 取 `hits[0].0`（第一來源 hit）走既有 `handle_enter_on_hit`；`first_hit_idx` 把 `Folded` 視為命中列。
**驗收標準**：
- [ ] `Folded` 顯示文字含書名、作者（無作者顯示 `-`）、來源數、全部來源名（格式例：`超維術士 / 牧狐 [3源: A, B, C]`）（C15 顯示半邊）
- [ ] Enter on `Folded` → 取 `hits[0].0.clone()` 流入既有分支 —— selected_hit 抽取處（search.rs:186 附近）補 `Folded` arm（C18）
- [ ] `first_hit_idx` 的 `position` 判斷改為 `matches!(r, Hit{..} | Folded{..})`（REQ-006 Scenario 2）
- [ ] j/k 行為不需改（列數已縮減即自然正確）
- [ ] `cargo test` 全綠、無新警告（C21）

### 步驟

#### 實作
- [ ] `draw()` 加 `Folded` match arm（顯示字串建議抽成純函數 `fn folded_label(hits: &[(SearchHit, String)]) -> String` 便於單測）
- [ ] `handle_event` Enter：`Folded { hits } => hits.first().map(|(h, _)| h.clone())`
- [ ] `first_hit_idx` 判斷式更新

#### 測試（RED 先行）
- [ ] `folded_label` unit test：斷言含 `"3源"` 與 `"A, B, C"`
- [ ] first_hit_idx 情境：rows 首列 `Folded` 時被預選（可直接對 rows 的 position 邏輯測，或構造 Results state 測 handle_event 前置）
