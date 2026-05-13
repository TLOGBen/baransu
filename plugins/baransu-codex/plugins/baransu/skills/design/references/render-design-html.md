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

## 寫入位置

`{project_root}/DESIGN.html`。已存在則覆寫。

## 成功訊息

「✅ 已產出 DESIGN.html（設計系統視覺預覽，可直接用瀏覽器開啟）」
