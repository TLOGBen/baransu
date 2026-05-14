# Stage 4 — Validate & Report (detailed spec)

## §2 Visual render verification (Playwright)

After Stage 4 §1 GATE PASS，render the HTML in headless Chromium via the bundled helper (Playwright is guaranteed installed by Stage 0)。一次 invocation 同時產 preview screenshot 與 structural JSON probe：

```bash
PROBE=$(python3 "./scripts/verify-render.py" \
  ".claude/book/{$SLUG}.html" \
  ".claude/book/{$SLUG}-preview.png")
echo "$PROBE"
```

`$PROBE` 為 single-line JSON：

```json
{"overflow": false, "has_paper": true, "has_h1": true, "has_h2": true, "svg_count": 3, "title": "…"}
```

判讀：

- `overflow` 為 `true` → 「⚠ 跑版偵測：有橫向溢出，請開啟 .claude/book/{$SLUG}-preview.png 手動確認。」
- `has_paper` / `has_h1` / `has_h2` 任一為 `false` → 「⚠ 結構元素缺失：{element} 未出現在頁面中。」
- script non-zero exit（Playwright launch / navigation failure）→ 「⚠ 視覺驗證無法執行，請手動開啟 .claude/book/{$SLUG}.html。」 並繼續到 completion report
- 全通過 → 「✅ 視覺驗證通過」

> **Why Playwright (not browser-use)**：browser-use 的 headless Chromium silently fail 載入 `file://` URL（readyState 報 complete 但 DOM 空）。Playwright 正確處理 `file://` 且是 project-standard E2E driver。

## §3 Completion report template

最終輸出（繁中）：

```
✅ 已儲存：
  HTML：.claude/book/{$SLUG}.html
  PDF： .claude/book/{$SLUG}.pdf        （若 $FORMAT 包含 pdf，且生成成功）
  PPT： .claude/book/{$SLUG}.pptx       （若 $FORMAT 包含 ppt，且生成成功）
        PPT：失敗（詳見上方錯誤）         （若 html2pptx.js 回傳非零 exit code）
  預覽：.claude/book/{$SLUG}-preview.png
內容類型：{$CONTENT_TYPE}
SVG 圖解：{N} 張
字數：約 {word_count} 詞
```

規則：

- HTML 行**必有**（所有 format 都產 HTML）
- PDF 行：僅 `--format pdf` 或 `--format all` 時出現
- PPT 行：僅 `--format ppt` 或 `--format all` 時出現；html2pptx 失敗改顯「PPT：失敗（詳見上方錯誤）」
- 預覽截圖（PNG）：永遠出現（Playwright 截圖在 §2 執行）
- 不在 Stage 4 重新推導 `$SLUG`；繼承 Stage 2A §4 推導的值
