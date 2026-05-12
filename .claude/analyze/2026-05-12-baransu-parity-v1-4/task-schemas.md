# Tasks: schemas

**前置群組**：shared, editorial

> 每 task 處理 2 個 schema × 3 preset × zh/en，計 12 個 .md schema 檔 + 12 個 HTML template。粒度上限：1 task ≈ 12 檔 = 一個 session 可完成。

## TASK-schemas-01: Resume + Portfolio schema × 3 preset × zh/en

**需求追溯**：REQ-002
**目標**：兩種人像 / 個人作品 schema，含 `object-position: center 35%` rule of thirds 強制。
**驗收標準**：
- [x] 三 preset 各含 `schemas/resume.md` + `schemas/portfolio.md`（共 6 schema 檔）
- [x] 三 preset 各含 `design-cores/resume.html` + `resume-en.html` + `portfolio.html` + `portfolio-en.html`（共 12 HTML 檔）
- [x] en variant `<link rel="stylesheet">` 引 en 對應 typography stack；不含 `Noto Serif TC` / `TsangerJinKai02`
- [x] 兩 schema 含 `<img>` 區塊 → CSS 必含 `object-position: center 35%`

### 步驟

#### 規格層（schema markdown）
- [x] 寫 6 個 schema markdown：每檔含 `schema-id`、`class-prefix`、`langs: [zh, en]`、`body-sections`、`image-requirements: {position: "center 35%"}`、`editorial-requirements: {dropcap: false, curly: true, widow-orphan: true}`
  - Resume `body-sections`：頭部姓名 + 聯絡 / 摘要 / 經歷 / 學歷 / 技能 / 專案
  - Portfolio `body-sections`：封面 + about / 作品 grid（4-6 個 case）/ 聯絡

#### 模板層
- [x] 紙 preset：`design-cores/resume.html` 採用 `kami-*` class prefix + `.kami-dropcap` 在「摘要」段示範 + 人像 `<img>` 含 `object-position: center 35%`
- [x] `resume-en.html`：同結構，font-stack 改 `Charter, Georgia, 'Palatino Linotype', serif`
- [x] portfolio.html / portfolio-en.html 同等
- [x] swiss preset 同等（class prefix `swiss-*`，無 dropcap）
- [x] google-design preset 同等（class prefix `google-*` per codebase convention，spec 寫的 `gd-*` 與既有 long-form.html 不符；採用 codebase convention）

#### 驗證
- [x] `grep -r "object-position: center 35%" plugins/baransu/skills/design/references/*-preset/design-cores/{resume,portfolio}*.html` 命中 ≥ 12（每檔至少一處）
- [x] `grep -L "Noto Serif TC\|TsangerJinKai02" .../resume-en.html` 列出全部 en variant（即都不含 zh 字體）

---

## TASK-schemas-02: One-Pager + Letter schema × 3 preset × zh/en

**需求追溯**：REQ-002
**驗收標準**：
- [x] 三 preset 各含 `schemas/one-pager.md` + `schemas/letter.md`
- [x] 三 preset 各含 `one-pager.html` + `one-pager-en.html` + `letter.html` + `letter-en.html`

### 步驟

#### 規格層
- [x] One-Pager `body-sections`：標題 / 核心數字 1 / 上下文 / 行動呼籲
- [x] Letter `body-sections`：日期 + 抬頭 / 引言段 / 主體 2-3 段 / 結尾敬辭

#### 模板層
- [x] 三 preset × 2 schema × zh/en = 12 HTML 檔
- [x] One-Pager 限制單頁（A4 / Letter 尺寸），CSS `@page` 設定
- [x] Letter 含 dropcap 在第一段（en variant 用 Charter 大寫字母 dropcap）

#### 驗證
- [x] 跑三 preset sanity.sh，無新增違規
- [x] 跑 editorial-sanity.sh 對 Letter 系列，dropcap check pass

---

## TASK-schemas-03: Equity-Report + Changelog schema × 3 preset × zh/en

**需求追溯**：REQ-002
**驗收標準**：
- [ ] 三 preset 各含 `schemas/equity-report.md` + `schemas/changelog.md`
- [ ] 三 preset 各含 `equity-report.html` + `equity-report-en.html` + `changelog.html` + `changelog-en.html`

### 步驟

#### 規格層
- [ ] Equity-Report：含投資論點 / 估值 / 風險三段；含至少 1 個 SVG quadrant 圖（angles：機會 × 風險）
- [ ] Changelog：semantic version 列表，每 release 含 added / changed / removed / fixed 四分類

#### 模板層
- [ ] 12 HTML 檔
- [ ] Equity-Report 含 SVG figure 範例（直接引用 task-svg-03 的 quadrant example）
- [ ] Changelog 用 `<ul>` 多層巢狀（class prefix 對應 preset）

#### 驗證
- [ ] 三 preset sanity.sh 全綠
- [ ] Equity-Report 內 SVG 通過 validate-output.ts GATE A-K

---

## TASK-schemas-04: 三 preset sanity.sh 加 object-position lint + schema-existence check

**需求追溯**：REQ-002 Scenario 3 + B5 邊界
**目標**：sanity script 機械擋住 schema 缺漏 / 缺 object-position 屬性。
**驗收標準**：
- [ ] 三 preset sanity.sh 新增兩 check：
  - Check 「schema 完整」：8 個 schema md 全在（含既有 long-doc + slides + 6 新 schema）
  - Check 「人像 schema object-position」：對 resume / portfolio template 必含 `object-position: center 35%`
- [ ] 對故意 strip 掉 object-position 的 fixture，sanity exit 1

### 步驟

#### 驗證層
- [ ] 在 `紙-sanity.sh` 加 8 schema 存在 check：`for s in long-doc slides resume portfolio one-pager letter equity-report changelog; do test -f schemas/$s.md || exit 1; done`
- [ ] 加 object-position check：對 `design-cores/{resume,portfolio,resume-en,portfolio-en}.html` grep `object-position: center 35%`
- [ ] swiss / google-design 同等

#### 驗證
- [ ] 跑三 preset sanity.sh 全綠
- [ ] 故意 mv 一個 schema 走，sanity exit 1
