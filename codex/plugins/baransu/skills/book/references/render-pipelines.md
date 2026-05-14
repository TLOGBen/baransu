# Render Pipelines — Stage 3 §5 (PDF) & §6 (PPTX)

僅在 `--format` 包含 `pdf` 或 `ppt` 或 `all` 時讀本檔。

## §5 PDF pipeline（`--format` 包含 `pdf` 或 `all`）

僅當 `$FORMAT` 為 `pdf` 或 `all` 時執行。

**步驟一：HTML 預處理**

取 Stage 3 §2-§4 生成的 long-form HTML 內容，注入下列 `<style>` 於 `<head>` 末尾：

```html
<style>
  .toc-wrap { display: none; }
  @page { margin: 2cm; }
  body { font-family: var(--font-serif); }
</style>
```

> v1.3 用 canonical `var(--font-serif)` 替代 hardcoded font stack；該變數由 project root tokens.css 解析（kami → serif stack；swiss/google-design → sans alias）。

將修改後的 HTML 存至臨時路徑 `{patched_html}`（例如 `.claude/book/{$SLUG}-pdf-patch.html`）。

**步驟二：呼叫 WeasyPrint**

```bash
python3 -m weasyprint "{patched_html}" ".claude/book/{$SLUG}.pdf"
```

若命令失敗（exit code ≠ 0）：輸出警告 `⚠️ PDF 生成失敗：WeasyPrint 錯誤`，繼續執行其他格式，不停止整個流程。

---

## §6 PPTX pipeline（`--format` 包含 `ppt` 或 `all`）

僅當 `$FORMAT` 為 `ppt` 或 `all` 時執行。依賴 Stage 2B 生成的 `$STRUCTURE_SLIDES`。

**步驟一：生成 slide HTML**

依 `$STRUCTURE_SLIDES` 的每個 slide 物件，從 `{project_root}/slide-cores/<layout-id>.html` 讀骨架（`<layout-id>` = Stage 2B 動態決策表結果，例如 `cover.html` / `content-bullets.html` / `closing.html`），生成 slide HTML 檔案。

若 `{project_root}/slide-cores/<layout-id>.html` 缺失（與 Stage 2B graceful-degradation 行為一致）：warning「請先跑 `/baransu:design preset <style>` 取得 slide-cores」，body slot 退化為 hardcoded fallback 三 layout (`cover` / `closing` / `content-bullets`) 的內嵌骨架；不中止 Stage 3。

每張 slide 的輸出規格：

- `<body style="width:960px; height:540px; margin:0; padding:0;">`
- 每個 slide 包在 `<div class="slide" data-layout="{layout_type}">` 中
- 文字內容使用 `<h1>`/`<h2>` 和 `<ul><li>` 呈現
- 若 `has_svg` 為 true，插入對應的 inline SVG

**步驟二：驗證 slide HTML**

在呼叫 html2pptx.js 之前，驗證三項：

1. `<body>` 的 `width` 樣式包含 `960`
2. 文件包含至少一個 `.slide` 元素（`class="slide"`）
3. 不含 `background-image`

若任何一項驗證失敗：輸出 `⚠️ Slide HTML 驗證失敗：{失敗原因}`，不呼叫 html2pptx.js，其他格式繼續。

**步驟三：呼叫 html2pptx.js**

```bash
node "./scripts/html2pptx.js" "{slide_html_path}" ".claude/book/{$SLUG}.pptx"
```

若命令失敗（exit code ≠ 0）：標記 `PPT：失敗（詳見上方錯誤）`，繼續其他格式，不停止整個流程。
