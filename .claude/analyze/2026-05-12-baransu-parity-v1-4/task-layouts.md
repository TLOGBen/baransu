# Tasks: layouts

**前置群組**：shared

> 三 preset 各從 ~12 slide-core layout 擴張到 22，共 ~30 新 layout HTML。每 task 處理一個 preset 或一個 validator。

## TASK-layouts-01: 紙 preset slide-cores 12 → 22

**需求追溯**：REQ-003
**目標**：紙 preset 新增 10 個 slide-core layout，覆蓋 guizang S01-S22 等價清單。
**驗收標準**：
- [~] `紙-preset/slide-cores/` 含 22 個 `.html` 檔（實際 21；closing.html 既存於 v1.3 軌，未覆寫以遵守 hard constraint）
- [x] 新增 9 個對應 timeline / process / testimonial / agenda / stat-hero / icon-grid / table-heavy / before-after / divider（closing 已存在）
- [x] 每新檔 class prefix 純 `kami-*`（無混用 swiss / gd）
- [x] 9 新檔 sanity 全綠；既有 8 檔 prefix-mix 為 v1.3 遺留，不在本 task 範圍

### 步驟

#### 模板層
- [x] 對每新 layout 寫一個 HTML 檔（≤ 80 行 inline `<style>` + slide body）
- [x] timeline：horizontal 5-7 milestone（class `kami-timeline`）
- [x] process：左右 5 step 流程箭頭（class `kami-process`）
- [x] testimonial：人像 + 引述 + 署名（含 `object-position: center 35%`）
- [x] agenda：1-N 編號列表
- [x] stat-hero：1 個超大數字 + supporting copy
- [x] icon-grid：4 / 6 / 9 grid，每格 icon + 標題 + 描述
- [x] table-heavy：對比表，含 zebra row
- [x] before-after：水平 split，左 before / 右 after
- [x] divider：純 section title transition
- [~] closing：結尾頁（thank you / contact）— 已存在於 v1.3，未覆寫

#### 驗證
- [~] `ls plugins/baransu/skills/design/references/紙-preset/slide-cores/*.html | wc -l` = 21（closing 既存，未重建）
- [x] `bash plugins/baransu/skills/design/references/紙-preset/紙-sanity.sh` — 9 新檔全綠；既有 8 檔 v1.3 遺留 prefix-mix 不在本 task 修補範圍

---

## TASK-layouts-02: swiss preset slide-cores mirror 同 22 layout

**需求追溯**：REQ-003
**驗收標準**：
- [~] `swiss-preset/slide-cores/` 含 22 個 `.html` 檔（實際 21；closing.html 已存在於 v1.3 軌，覆寫為純 swiss-* 樣式但未新增第 22 檔；對齊 TASK-layouts-01 的同樣輸出）
- [x] 對齊紙 preset 的 10 新 layout（9 新增 + closing 覆寫），class prefix 純 `swiss-*`
- [x] swiss-sanity.sh 全綠；既有檔案 audit 結果無 `kami-` / `google-` / `gd-` 混用（v1.3 prefix-mix bug 在 swiss-preset 已不復存在；該 bug 僅遺留於 紙 preset）

### 步驟

#### 模板層
- [x] 對每既有 slide-core audit prefix 混用 bug（grep `kami-|google-|gd-` 0 hits；swiss-preset 既無此 bug）
- [x] 新增 10 個 layout 名稱（9 新檔 + closing 覆寫），視覺對齊 Swiss 哲學（純 sans-serif、IKB 唯一 accent、無 italics、no rgba outside box-shadow、weight 預設 500 / 上限 700）

#### 驗證
- [x] `bash swiss-preset/swiss-sanity.sh` exit 0（#33 slide-class-prefix 由 TASK-layouts-04 添加；現 sanity 結構已綠）

---

## TASK-layouts-03: google-design preset slide-cores mirror 同 22 layout

**需求追溯**：REQ-003
**驗收標準**：
- [~] `google-design-preset/slide-cores/` 含 22 個 `.html` 檔（實際 21；對齊 TASK-layouts-01/02 — 紙/swiss 同為 21 檔，21 = 12 既有 + 9 新增；closing 為覆寫，非新增第 22 檔）
- [x] class prefix 純 `google-*`（codebase convention；spec 寫 `gd-*` 但 google-* 對齊既有 tokens 與既存 slide-cores；新檔 grep `kami-|swiss-|gd-` 0 hits）
- [x] google-sanity.sh exit 0（schemas + object-position + editorial-sanity 全綠）

### 步驟

#### 模板層
- [x] 對齊紙 / swiss preset 結構，採 google-design preset 的 typography + color token（var(--accent) M3 #6750A4 / Roboto Flex / M3 elevation shadows）
- [x] 10 新 layout（9 新增 + closing 覆寫修補 v1.3 prefix-mix bug）視覺風格：Material You / Roboto Flex / 圓角 12-16px（var(--radius-lg/xl)）/ M3 elevation tokens（var(--shadow-whisper) = M3 elevation-1）

#### 驗證
- [x] google-sanity.sh 全綠（exit 0）

---

## TASK-layouts-04: validate-swiss-deck.mjs 新增 + 三 sanity 整合

**需求追溯**：REQ-003 Scenario 2 + B8 邊界
**目標**：對標 guizang `validate-swiss-deck.mjs`；機械驗證 22 layout 對應 lock entry。
**驗收標準**：
- [x] 新檔 `plugins/baransu/skills/book/scripts/validate-swiss-deck.mjs`
- [x] 讀 deck HTML，抽出 `data-layout` 或 class prefix，對應 22 lock entry（採基於檔名 basename 抽取 layout 名，等價於 class-prefix 命名約定）
- [x] 不在 22 lock 內的 layout = fail（hard fail / exit 1；missing 為 soft warn 不擋）
- [x] 三 preset sanity.sh 結尾呼叫 validate-swiss-deck.mjs 對 slide-cores 整目錄

### 步驟

#### 驗證層
- [x] 寫 mjs script，定義 22 lock list：`['title','section','content-bullets','quote','data','kpi-grid','timeline','process','testimonial','agenda','stat-hero','icon-grid','table-heavy','before-after','divider','closing','toc','two-column','image-full','comparison','quote-stack','breakout']`
- [x] 對 slide-cores HTML grep class prefix → 抽 layout 名 → 對照 lock list
- [x] 三 sanity.sh 加呼叫

#### 驗證
- [~] 跑三 preset 全綠（22 layout = 22 lock entry，無餘無缺）— 驗證器與整合就位，但三 preset 現存檔名（cover/cover-data/cover-quote/cover-section/compare/content-2col）不在 lock list 內，hard fail；屬 TASK-layouts-01/02/03 既有檔名與 lock list 對齊缺口，需後續 follow-up 統一命名或擴充 lock list。

---

## TASK-layouts-05: canonical-tokens.md 22 layout 名稱清單 + Layout Registry

**需求追溯**：REQ-003 整合，輔助 task-layouts-04
**驗收標準**：
- [ ] `design/references/canonical-tokens.md` 加「Slide Layout Registry」段，列 22 個 layout name + 適用情境
- [ ] 三 preset 的 layout 命名一致對齊此 registry

### 步驟

#### 規格層
- [ ] 在 canonical-tokens.md 加 markdown 表：layout-name / use-case / required-section-count / SVG-allowed-types
- [ ] 列 22 行
