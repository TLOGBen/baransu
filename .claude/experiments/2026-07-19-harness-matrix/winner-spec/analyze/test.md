# Test Strategy

全部測試離線（簡報硬規則：不得觸網）。本專案無 web endpoint，「E2E」= 以最外層可離線驅動的入口（dao in-memory 交易、`run_with_deps` + fake deps、純函數 helper）驗證整條主路徑分支。

## E2E 測試策略

| 場景（主路徑分支） | 真實入口（方法名＋file:line，已 read 驗證存在） | 具體斷言（具名值） | 對應 Criteria |
|------|------|------|--------------|
| A: `&` 取自身文字 | `extract_within` `src/catalog/service/rule.rs:142` | `== Ok(Some("第1章 起"))` | C1 |
| A: `&@href` / `&@html` / `&@outerHtml` | `extract_within` `rule.rs:142` | `&@href == Some("/x")`；`&@outerHtml` 含 `<a` 起始標籤 | C2 |
| A: `&##regex##repl` | `extract_within` `rule.rs:142` | `"&##第##Ch." == Some("Ch.1章 起")` | C3 |
| A: `"em.missing \|\| &"` 落自身 | `extract_within` `rule.rs:142` | `== Some(自身文字)` | C4 |
| A: `"& \|\| em.x"` 自身先中 | `extract_within` `rule.rs:142` | `== Some(自身文字)`（不因 em.x 缺席出錯） | C4 |
| A: `select_within(el, "&")` | `select_within` `rule.rs:111` | `len == 1` 且 `[0].id() == el.id()` | C5 |
| A: doc 層 `&`（bonus） | `extract_doc` `rule.rs:125`、`select_nodes` `rule.rs:97`、`extract_all_doc` `rule.rs:165` | `extract_doc == Some(含 "alpha" 與 "beta")`；`select_nodes.len == 1`；`extract_all_doc.len == 1` | C7 |
| B: 精確同名遷移（idx 非稠密） | `run_with_deps` `src/presentation/handlers/switch_source_core.rs:154`（fake deps）＋ `update_book_source_tx` `src/library/dao.rs:260`（in-memory） | fake 層：`SwitchOutcome.progress == Migrated { idx: 5, name: "第2章 破曉" }`；dao 層：`SELECT chapter_index == 5`、`scroll_offset == 0` | C8 |
| B: 去空白相等遷移 | `find_migration_target`（新純函數，switch_source_core.rs） | `== Some((4, "第2章 破曉"))`（舊名含全形空白） | C9 |
| B: 章號 token 遷移 | `find_migration_target` | 全形 `第１２章` vs `第12章…` `== Some((20, …))`；`第十二章` vs `第12章` `== None`（不互轉） | C10 |
| B: 全未命中重置 | `run_with_deps`（fake：`current_chapter_name` 回 `None` / 回不相干名） | `SwitchOutcome.progress == Reset` 且 `new_progress_idx == 新TOC首idx` | C11 |
| B: abort-before-tx 不變 | 既有 `req005_s2_*` / `req005_s3_*`（switch_source_core.rs:321,344）＋ dao fault-injection 既有測試 | 原樣通過；`switch_tx_called == false` | C12 |
| B: 呈現兩態 | `ProgressResolution` 訊息組裝（CLI/TUI 共用格式邏輯或各自 format） | 遷移訊息含 `"進度已遷移"` 與 `"第2章 破曉"`；重置訊息含 `"進度重置"` | C13 |
| C: 三源同書摺疊 | `fold_rows`（新純函數，`src/presentation/handlers/tui/search.rs`，接在 `assemble_rows` search.rs:236 之後） | 輸出 `len == 1`、`Folded.hits.len == 3`、來源序 `["A","B","C"]` | C15 |
| C: 同名異作者不摺疊 | `fold_rows` | 輸出 `len == 2`、兩列皆 `Hit` | C16 |
| C: 首位保留＋單源原樣 | `fold_rows` | `[Folded X{A,C}, Hit Y(B)]` 依序斷言 variant 與位置 | C17 |
| C: StatusLine 相對位置 | `fold_rows` | `[Folded, StatusLine("源 B：逾時"), StatusLine("源 D 未查")]` 逐列斷言 | C19 |
| C: Folded 標籤與 Enter 互動 | `folded_label`（新純函數）＋ selected_hit 抽取邏輯（`handle_event` `src/presentation/handlers/tui/search.rs:141`） | 標籤含 `"3源"` 與 `"A, B, C"`；Enter on Folded 抽出的 hit `== hits[0].0`（第一來源） | C15, C18 |
| 全域：既有 48 條測試 | `cargo test`（基線已實測 48 passed） | `48 + 新增 N` passed、0 failed；無新警告 | C6, C12, C14, C20, C21 |

## 整合測試策略

| 測試目標 | 涉及層 | 關鍵驗證點（具名斷言，禁同義反覆） |
|---------|--------|-----------|
| dao tx 帶 `progress_idx: Some(5)` | library dao（in-memory SQLite） | tx 後 `SELECT chapter_index FROM progress WHERE novel_id=? == 5`（非首章 idx）；`scroll_offset == 0`；chapters 表為新 TOC 內容 |
| dao tx 帶 `progress_idx: None` | library dao | `chapter_index == 新 TOC 首 idx` —— 與既有 `int1` 斷言相同值（機械適配 `None` 後原斷言不變） |
| dao fault-injection rollback 不受新參影響 | library dao | 既有 fault step 1–4 測試補 `None` 後原樣通過：Snapshot 前後相等 |
| `run_with_deps` 端到端遷移 | presentation core + fake deps | fake `current_chapter_name == Some("第2章 破曉")` → `deps.switch_source_tx` 收到 `progress_idx == Some(5)`（fake 記錄收到的參數並斷言） |
| 解析失敗降級不 abort | presentation core + fake deps | fake `current_chapter_name` 回 `Err(...)` → `run_with_deps` 回 `Ok`、`progress == Reset`、`switch_tx_called == true` |
| 分層不變式（收尾驗證，非 cargo test） | 全部四 context | `grep -rn "rusqlite\|::dao" src/catalog/service src/library/service` 零命中；`grep -rnE "use crate::(catalog\|library)::facade" src/catalog src/library` 零命中 |

## 關鍵邊界條件

- `&` 取值為空字串（元素無文字）→ 落入下一個 `||` alternative；全部為空回 `Ok(None)` — REQ-001 — 由 TASK-a-01 製造的風險
- `&` 前後帶空白（`" & "` 經 `parse_alt` trim 後 == `"&"`）→ 仍走自身分支 — REQ-001 — 由 TASK-a-01 製造的風險
- `&@不存在的attr` → 空字串 → 視為未命中落 fallback，不 panic — REQ-001 — 由 TASK-a-01 製造的風險
- doc 層 `&` 於 `parse_fragment`（根為 `<html>` wrapper）→ `root_element()` 取整體，不報錯 — REQ-002 — 由 TASK-a-02 製造的風險
- 舊章名去空白後為空字串 → 規則 b 跳過（否則會誤中任何全空白新章名） — REQ-003 — 由 TASK-b-02 製造的風險
- 舊章名命中新 TOC 多章（同名重複）→ 取 idx 升冪第一個 — REQ-003 — 由 TASK-b-02 製造的風險
- 規則 c 僅單邊有章號 token → 不命中 — REQ-003 — 由 TASK-b-02 製造的風險
- 無 progress 列（`get_progress == None`）→ `current_chapter_name == None` → Reset，換源照常成功 — REQ-003 — 由 TASK-b-03 製造的風險
- progress 指向的 idx 不存在於舊 chapters（TOC 曾重排）→ `None` → Reset — REQ-003 — 由 TASK-b-03 製造的風險
- `current_chapter_name` 回 `Err` → 降級 Reset、不新增 abort 出口、tx 照常執行 — REQ-003 — 由 TASK-b-03 製造的風險
- dao `progress_idx: Some(idx)` 且 idx 非首章 → UPSERT 寫該 idx；回傳值 == 該 idx — REQ-003 — 由 TASK-b-01 製造的風險
- 摺疊鍵：`author: None` vs `Some("")` vs `Some("  ")` 視為同鍵 — REQ-005 — 由 TASK-c-01 製造的風險
- 同一來源對同書回兩筆 → 照併（計數含重複來源名） — REQ-005 — 由 TASK-c-01 製造的風險
- `fold_rows(vec![])` → `vec![]` — REQ-005 — 由 TASK-c-01 製造的風險
- Enter 落在 `Folded` 列 → 取 `hits[0]`；`first_hit_idx` 對 `Folded` 首列成立 — REQ-006 — 由 TASK-c-02 製造的風險

## 冗餘與首要交付掃描

- kept：上表每列各對應唯一 (REQ, TASK) 風險組合，逐列掃描無重複斷言標的。
- removed：不為 `select_nodes`/`extract_all_doc` 的每個 accessor 組合單獨立列（與 `extract_doc` 共用同一 `&`-分支程式路徑，C7 一列覆蓋三入口已足）。
- removed：CLI handler 的 stdout 捕捉測試（handler 呼叫 `std::process::exit`，測試代價高；C13 的訊息內容在 `ProgressResolution` → 訊息字串的組裝層驗證，CLI/TUI 僅薄轉發）。
- 首要交付釘死：本次首要交付 = 三項行為各有一條「破壞即紅」測試 —— C1（`&` 修復前必 Err、修復後 Some）、C8（遷移前 chapter_index 必為首 idx、遷移後為 5）、C15（摺疊前 3 列、摺疊後 1 列）。三條皆為修復前必然失敗的斷言，feature 壞則測試紅。
- 逐 task 對應：TASK-a-01/02 → C1–C7 列；TASK-b-01 → dao 整合列；TASK-b-02 → 純函數列；TASK-b-03 → run_with_deps 列；TASK-b-04 → 呈現兩態列；TASK-c-01 → fold_rows 列；TASK-c-02 → 互動列。無孤懸測試。
