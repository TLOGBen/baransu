# Stage 2B — Slide synthesis (PPT 模式專用)

僅在 `$FORMAT` 為 `ppt` 或 `all` 時執行。使用與 Stage 2A 相同的 `$RAW_CONTENT`，`$SLUG` 繼承自 Stage 2A。

從 `$RAW_CONTENT` 提取投影片結構 `$STRUCTURE_SLIDES`。**layout 不寫死**：本階段從 project root 動態讀取 `slide-cores/` 並建立決策表，再以 first-match + positional override 決定每張投影片的 `layout_type`。

## 讀取 project root slide-cores

讀檔路徑：`{project_root}/slide-cores/*.html`（由 `/baransu:design preset <name>` 複製到 project root；本階段只讀，不改）。

演算法：

1. 列出 `{project_root}/slide-cores/` 下所有 `.html` 檔。
2. 對每個 HTML 解析開頭的 YAML front-matter，欄位：
   - `layout_id`（string，e.g. `"content-bullets"`，與檔名一致）
   - `applies_to.bullet_count`（range，e.g. `"0"` / `"1-3"` / `"4-5"`）
   - `applies_to.has_image`（enum：`required` | `optional` | `forbidden`）
   - `applies_to.role`（enum：`body` | `positional_first` | `positional_last` | `section_divider`）
   - 可選 `image_slot.{aspect_ratio, object_position, fit}`
3. 將每筆 `(layout_id, applies_to)` 註冊進**動態決策表**；表的可用 `layout_id` 集合就是 `$STRUCTURE_SLIDES.slides[*].layout_type` 的 enum。
4. 不寫死 layout 名單 — 9 個 layout 若被刪、被加，決策表隨之變動。

## 決策邏輯（first-match + positional override）

**優先序原則**：positional 規則永遠 rank 高於 content-driven 規則。即使首頁有 1-3 條 bullets 完全匹配 `content-bullets`，仍走 `cover`（位置驅動 > 內容驅動）。

| Row | 條件 | layout_type | role |
|---|---|---|---|
| 1 | 位置 = 首頁（固定） | `cover` | positional_first（取 H1 + subtitle） |
| 2 | 位置 = 末頁（條件式，見下方 CTA/致謝辨識） | `closing` | positional_last |
| 3 | heading-only（無 body） | `section` | section_divider |
| 4 | 50 字以內金句 | `quote` | body |
| 5 | A vs B 對比段 | `compare` | body |
| 6 | 4-6 個 stat number | `kpi-grid` | body |
| 7 | 含 inline SVG 或大表 | `data` | body |
| 8 | 左文右視覺一張圖 | `content-2col` | body |
| 9 | 1-3 條 bullets | `content-bullets` | body |
| 10 | 其他（fallback → row 9 同 layout） | `content-bullets` | body |

**Fallback layout**：任何 row 3-9 都不 match 的 body slot，最終 fallback 至 `content-bullets`（row 10 為 row 9 的 alias，不算新 layout）。

**Cover 為首頁固定**：第一張投影片永遠走 `cover`，取 markdown 的 H1 作主標、緊跟其後的引言或副標作 subtitle，無 bullets。

**Closing 為末頁條件式**：依優先序檢查 source 末段是否有以下任一存在：

- (a) markdown link 含動詞「聯絡 / 訂閱 / 下單 / contact / subscribe / cta / book a call」之一；
- (b) 含「致謝 / Acknowledgement / Thanks」heading；
- (c) 含 `mailto:` 或聯絡資訊 block。

三者皆無 → row 2 不適用，**closing omit**（不強制插入空 closing），末頁退化至 row 9 (`content-bullets`)。

## 缺檔 / 解析失敗的 graceful degradation

- **`{project_root}/slide-cores/` 不存在或為空**：發出 warning「請先跑 `/baransu:design preset <name>` 取得 slide-cores」，**不中止**；退化為 hardcoded fallback 三 layout 集合 `{cover, closing, content-bullets}`，body slot 一律走 `content-bullets`，cover/closing 仍依 positional rule 套用。
- **某 slide-core HTML 的 YAML 解析失敗**：warning 該檔名與失敗原因，**將該 layout 從決策表移除**，其他 layout 仍可用；觸發該 layout 的內容退化為 fallback `content-bullets`。
- 上述兩種降級皆**不中止** Stage 2B，後續 Stage 3 仍正常渲染（GATE-G 在後續 validator 階段視需要 SKIP）。

## $STRUCTURE_SLIDES schema

```typescript
interface SlideStructure {
  slides: Slide[];
}

interface Slide {
  // 動態 enum：取自決策表已註冊的 layout_id 集合
  // 完整 preset 下為 cover | section | content-bullets | content-2col | data | kpi-grid | compare | quote | closing
  // fallback 模式下為 cover | content-bullets | closing
  layout_type: string;
  heading: string;
  body_bullets?: string[];  // 用於 content-bullets / content-2col，通常 1-3 條
  has_svg?: boolean;        // 若 true，在此 slide 生成 inline SVG
}
```

## 數量與結構約束

- 總 slide 數量：**6-12 張**
- 第一張固定為 `cover`；末頁依 CTA/致謝辨識決定是否為 `closing`（無則 omit，末頁走 body layout）
- `heading` 為必填；`body_bullets` 和 `has_svg` 為可選

儲存結果為 `$STRUCTURE_SLIDES`。

## 投影片字級與限高硬規則（PPT 產出品質）

Render 期 standing instruction：Stage 3 PPTX 路徑（render-pipelines.md 步驟一「生成 slide HTML」）為每張 slide 套用大字時，**必須**遵守下列可二值判定的硬規則。違反任一條 → 在 final-report 自查標 fail，render 前先修文案或拆頁。slide 容器是 16:9（PPTX 路徑固定 `960×540px`，故 `100vw=960px`、`100vh=540px`、寬高比 960/540≈1.778）。

### 1. 大字雙約束 `font-size: min(Xvw, Yvh)`，且 `Y ≥ X × 1.6`

只用 `vw` 單約束在 16:9 容器會被截到縮水 ~20%（可復現 bug）：`min(7vw, 10vh)` 在 960×540 下 `7vw = 67.2px = 12.4vh`，被 `10vh = 54px` 截斷，實際只剩 ~80% → 大字莫名變小、版面失衡。失敗分支：**只看到 `vw` 沒看到 `vh`、或 `Y < X × 1.6` → 該大字 fail**。

速查表（直接套用，不另推導）：

| 角色 | `font-size` |
|---|---|
| h-hero 宣言/封面巨標 | `min(11.6vw, 19vh)` |
| 章節標題 h-xl | `min(7vw, 12vh)` ~ `min(7.4vw, 13vh)` |
| KPI 大數字 | `min(8.4vw, 14vh)` |
| 副標 | `min(7.6vw, 13vh)` |
| 中數字 | `min(4.6vw, 8.5vh)` ~ `min(5.6vw, 10vh)` |

### 2. 中文標題先分檔再定字級（方塊字視覺面積大）

先數標題行數與每行字數選檔，再定字級。失敗分支：**3 行仍塞不下 → 改寫文案縮短，不得把字級降到檔位以下**。

| 檔位 | `font-size` |
|---|---|
| 1 行 ≤8 字 | `min(6.4vw, 11.2vh)` |
| 2 行各 ≤8 字 | `min(5.8vw, 10.2vh)` |
| 2 行任一行 9-12 字 | `min(5.2vw, 9.2vh)` |
| 3 行（優先改寫，不得已） | `min(4.6vw, 8.2vh)` |

### 3. 演示最小字號下限（投屏不能用網頁的 10-12px）

投影片在投屏/遠看，下限比網頁高。失敗分支：**內容放不下 → 先刪文案 / 拆頁 / 換 `layout_type`，禁壓字號到下限以下**。

| 角色 | 最小字號 |
|---|---|
| 正文 / 主說明 | `≥ 18px` |
| 卡片描述 / 列表 / 時間線 / caption | `≥ 16px` |
| meta / kicker / 圖表標籤 | `≥ 14px` |
