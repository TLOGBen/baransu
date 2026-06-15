# Render DESIGN.html — shared spec for gen mode & preset mode

Both gen mode 和 preset mode 跑完 DESIGN.md 後產出 `{project_root}/DESIGN.html` —— **使用該 preset 自家 tokens 自我展示**（不引用 Kami 或外部模板）。

## 必含 7 個 section

1. **Sticky sidebar TOC** — 九段連結，色彩用該 preset primary/background tokens
2. **Color palette section** — 每個 named color 一個 `<div>` swatch + hex label；swatch background 為實際色值
3. **Typography section** — live text samples 用 spec font stacks（headings / body / captions）；使用 `@font-face` 或 safe web-font fallback，**不**用 CDN link
4. **Component stylings section** — 視覺描述或 code snippet，保留 DESIGN.md 用語
5. **Do / Don't section** — 兩欄比較表，用綠/紅 accent 表 pass/fail
6. **AI Prompt Guide section** — copy-ready `<code>` block 含完整 reproducer prompt
7. **Remaining sections** — 標準 `<h2>` + prose 呈現

## 技術需求

- Fully offline（無 external script、無 CDN font）
- 單檔，無 external asset
- Valid HTML5 含 `<meta charset="utf-8">` 與 `<meta name="viewport">`
- 頁面自身 background / text / accent 顏色須對應 DESIGN.md §2 的 token

## 可驗品質門檻（render 後自查）

七段結構齊全只是結構檢查；render 完後逐條核對下列可量測門檻，任一不過即重排，**不准用空話帶過**：

- 色數 ≤3–4（1 主 + 1 輔 + 1 強調 + 灰階；accent 覆蓋 ≤5% 表面）（理由：色數爆炸是 AI 美學最常見破綻，強調色滿屏即不再是強調）
- 正文 vs 背景對比 ≥4.5:1（WCAG AA），大字（≥24px 或 bold ≥19px）≥3:1（理由：低於此值在投影 / 強光下不可讀，是世界級產出的硬下限）
- 留白 ≥40% 總面積（理由：Kami「less but better」的呼吸節奏，欠白即顯廉價密集）
- body line-height 中文 1.5–1.55；禁 ≥1.6（理由：Kami「印刷比網頁更緊」，≥1.6 是網頁漂浮腔，破壞長文連讀節奏）
- 閱讀流 `max-width` ≤65ch（理由：超過 65 字元/行回掃疲勞，editorial 排版鐵則）

### 編輯級微排版（gen mode 自製 preset 的盲點 — DESIGN.html 編輯級自查清單）

色數 / 對比 / 留白都過、仍可能輸出「AI 通用感」editorial：分水嶺在下列微排版。這四條對標 Kami 編輯級排版（digests/10-kami.md §5），是把產出從「AI 通用感」拉到「編輯級克制」最大的單一槓桿。

> 🔴 **誠實聲明**：此層 `editorial-sanity.sh`（只覆蓋 design-cores HTML 的 kami/swiss/google prefix）**尚未覆蓋** DESIGN.html，無腳本可跑，一律手動逐條執行。render 完 DESIGN.html 後**依序**跑 E1–E4，**任一不過即重排**，不准空話帶過。每條 pass 判據已明寫於「預期」欄——做不到量測就視同不過。

- **E1 — 列點用 native `<li>` marker 上 accent 色，禁 `::before` en-dash 假 bullet**（根因：`::before` 破折號 bullet 是 AI 預設輸出一眼可辨，非編輯排版）。
  - 做法：`li::marker { color: var(--accent) }`，不用 `::before` 造 bullet。
  - 自查：`grep -nE "li::before|content:\s*['\"][-–—]" DESIGN.html`
  - 預期 pass：**輸出空（0 行）**。
- **E2 — CJK 列點旁禁圓點 bullet，改 8px×1.5px 的 `var(--accent)` 短橫條**（根因：圓點配中文讀來幼稚，短橫條才是編輯級節制）。
  - 做法：含 CJK 的 `<li>` 區段 `list-style: none` + `::before` 畫 `width:8px;height:1.5px;background:var(--accent)` 短橫條。
  - 自查：`grep -nE "list-style(-type)?:\s*disc" DESIGN.html`（CJK 區段不得有 disc）＋目視確認橫條尺寸＝8px×1.5px。
  - 預期 pass：**grep disc 輸出空（0 行）；目視橫條尺寸符合**。
- **E3 — 箭頭一律 `→` 禁 `->`；中文引號用「」禁直引號 `"`；% 前不空格、數字加千分位（`5,000`／`90%`）**（根因：ASCII 箭頭與直引號是未經編輯的機器輸出指紋；與 `editorial-sanity.sh` Check 3 同精神，但此處覆蓋 DESIGN.html 而非 design-core）。
  - 做法：prose 內 ASCII 箭頭改 `→`、直引號改「」。
  - 自查：`grep -nE -- "->" DESIGN.html`（ASCII 箭頭）＋目視 prose（非 HTML attribute）內無直引號 `"`。
  - 預期 pass：**grep `->` 輸出空（0 行）；prose 內直引號計數＝0**。
- **E4 — 印刷／長文取向的 preset 禁 italic**（唯一例外：screen-only 詩意句；根因：印刷模板用 italic 即露網頁腔；gen mode 自製非 swiss preset 目前無此 gate）。
  - 做法：強調改 `var(--accent)` 上色或字重，不走 italic。
  - 自查：`grep -nE "font-style:\s*italic|<i>|<em>" DESIGN.html`
  - 預期 pass：**輸出空（0 行）；若有命中，逐處確認確為 screen-only 詩意句例外，否則改回上色／字重表達層級**。

## 寫入位置

`{project_root}/DESIGN.html`。已存在則覆寫。

## 成功訊息

「✅ 已產出 DESIGN.html（設計系統視覺預覽，可直接用瀏覽器開啟）」
