# Goal

## 目標（Goal）

novel-looker 補齊三項 legado 對等能力：規則 DSL 的 `&` 自身選擇器可用（不再 EmptySelector）、換源時盡力遷移閱讀進度（章名比對，失敗才重置）、TUI 跨源搜尋結果依（書名, 作者）摺疊為單列 —— 全部離線測試綠、不破壞既有 DDD 分層與交易原子性。

## 驗收標準（Criteria）

每條冠 `C{n}`，並附實驗簡報（EXPERIMENT-BRIEF.md）原始編號對照。

### Item A — 規則 DSL `&` 自身選擇器（`src/catalog/service/rule.rs`）

- [ ] C1: `extract_within(el, "&")` 回傳該元素自身的 text（不再回 `EmptySelector` 錯誤）。
- [ ] C2: `extract_within(el, "&@href")` 及任意 attribute / `html` / `outerHtml` accessor 都從元素自身讀值。
- [ ] C3: `extract_within(el, "&##<regex>##<repl>")` 對自身取出的值套用 regex 取代。
- [ ] C4: `||` fallback 中 `&` 任意位置皆可用：`"em.missing || &"` 落到自身；`"& || em.x"` 先用自身。
- [ ] C5: `select_within(el, "&")` 回傳 `vec![el]`（不報錯）。
- [ ] C6: 既有測試全數不變且通過（`catalog::service::rule::tests` 4 條與其餘全部）。
- [ ] C7:（bonus）document 層入口（`extract_doc` / `select_nodes` / `extract_all_doc`）將 `&` 視為文件根元素而非報錯。

### Item B — 換源盡力遷移閱讀進度

- [ ] C8: 章名完全相同 → `progress.chapter_index` 遷移到新 TOC 中比對命中的 idx（idx 非稠密 0..N-1，嚴禁假設 第N章 → idx N-1）。
- [ ] C9: 章名去除全部 Unicode 空白後相等 → 視為命中（規則 b）。
- [ ] C10: 章號 token 相等（regex `第\s*([0-9０-９一二三四五六七八九十百千零〇两兩]+)\s*[章回節节卷]` 首捕獲組，全形數字正規化為半形後以字串比較）→ 視為命中（規則 c）；阿拉伯數字與中文數字互轉不要求。
- [ ] C11: 三規則皆未命中 → 行為與現況完全相同：重置到新 TOC 首章 idx、`scroll_offset = 0`。
- [ ] C12: 五類 pre-tx abort 與單一交易原子性完全不動；既有 dao / switch-source 測試全過（既有測試僅在其斷言行為被本準則明文取代時才可改，並記入決策日誌）。
- [ ] C13: 兩條路徑都向使用者呈現結果：`SwitchOutcome` 攜帶「已遷移 vs 已重置」（遷移時含命中章名/idx）；CLI handler 印出、TUI toast 顯示（例：「進度已遷移：第12章 風起」／「進度重置到首章」）。
- [ ] C14: 新增 unit / integration 測試在純邏輯層覆蓋 C8–C11 與 C13（比照既有 `SwitchSourceDeps` fake 與 dao in-memory 測試風格）。

### Item C — 跨源搜尋結果摺疊

- [ ] C15: `(name.trim(), author-or-empty.trim())` 相等的命中列摺疊為一列；顯示文字含書名、作者、來源數與全部來源名（格式自由，例 `超維術士 - 牧狐 [3源: A, B, C]`）。
- [ ] C16: 同名不同作者（或反之）不摺疊、維持獨立列。
- [ ] C17: 摺疊列保留首次出現的列位；單一來源的列渲染與現況相同。
- [ ] C18: 在摺疊列按 Enter：最低要求 = 作用於第一個來源（來源迭代順序）的命中；source-picker UI 屬 bonus 不要求。
- [ ] C19: StatusLine 列（錯誤/逾時/未查）不受影響，相對於存活列的位置不變。
- [ ] C20: 摺疊邏輯放在純函數、可單測的 helper（擴充 `assemble_rows` 或增加 post-pass）；新 unit 測試覆蓋 C15/C16/C17/C19；既有搜尋測試全過（取代規則同 C12）。

### 全域（Global）

- [ ] C21: `cargo test` 全綠；不引入新編譯警告（既有兩條 `dead_code` 警告屬預期、保留）。
- [ ] C22: DDD 4-context × 5-layer 不變式成立：`service/*.rs` 不 import rusqlite / dao；facade 不跨 context 互呼（backup→library 唯一例外）；跨 context 組合只在 `presentation/handlers/`；`mod.rs` PL 無邏輯。驗證：`grep -rn "rusqlite\|::dao" src/catalog/service src/library/service` 零命中、`grep -rnE "use crate::(catalog|library)::facade" src/catalog src/library` 零命中。

## 簡報編號對照表

| 簡報編號 | 本 spec 編號 | | 簡報編號 | 本 spec 編號 | | 簡報編號 | 本 spec 編號 |
|---|---|---|---|---|---|---|---|
| A1 | C1 | | B1 | C8 | | C1 | C15 |
| A2 | C2 | | B2 | C9 | | C2 | C16 |
| A3 | C3 | | B3 | C10 | | C3 | C17 |
| A4 | C4 | | B4 | C11 | | C4 | C18 |
| A5 | C5 | | B5 | C12 | | C5 | C19 |
| A6 | C6 | | B6 | C13 | | C6 | C20 |
| A7 | C7 | | B7 | C14 | | 全域1/2/5 | C22/C21/C21 |

## 範圍（Scope）

### 包含（In scope）

- `src/catalog/service/rule.rs` 五個入口的 `&` 語意修復（元素層必修、文件層 bonus）。
- 換源流程（`switch_source_core` → `library::facade` → `library::dao`）加入章名比對遷移與結果呈現（CLI + TUI 兩路徑）。
- `src/presentation/handlers/tui/search.rs` 摺疊 post-pass 純函數 + 顯示 + Enter 行為。
- 上述各項之新 unit / integration 測試（全部離線）。

### 不包含（Out of scope）

- 阿拉伯數字 ↔ 中文數字互轉比對（簡報明列不要求；屬 bonus 且增加正規化風險）。
- 摺疊列的 source-picker UI（C18 明列 bonus；最低要求為作用於第一來源即可）。
- 任何網路測試（簡報禁止）、`book-sources/`、`.claude/skills/` 與三項無關的檔案。
- `replace_toc` 的 content 保留改造、真正 async fetch 等 CLAUDE.md 提及的既有已知課題（與本次三項無關）。
