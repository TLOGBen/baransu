# Stage 4 — Validate & Report (detailed spec)

## §2 Visual render verification (Playwright)

After Stage 4 §1 GATE PASS, render the HTML in headless Chromium via the bundled helper (Playwright is guaranteed installed by Stage 0). A single invocation produces both the preview screenshot and a structural JSON probe:

```bash
PROBE=$(python3 "$CLAUDE_SKILL_DIR/scripts/verify-render.py" \
  ".claude/book/{$SLUG}.html" \
  ".claude/book/{$SLUG}-preview.png")
echo "$PROBE"
```

`$PROBE` is single-line JSON:

```json
{"overflow": false, "has_paper": true, "has_h1": true, "has_h2": true, "svg_count": 3, "title": "…"}
```

Interpretation:

- `overflow` is `true` → 「⚠ 跑版偵測：有橫向溢出，請開啟 .claude/book/{$SLUG}-preview.png 手動確認。」
- any of `has_paper` / `has_h1` / `has_h2` is `false` → 「⚠ 結構元素缺失：{element} 未出現在頁面中。」
- script non-zero exit (Playwright launch / navigation failure) → 「⚠ 視覺驗證無法執行，請手動開啟 .claude/book/{$SLUG}.html。」 and continue to the completion report
- all pass → 「✅ 視覺驗證通過」

> **Why Playwright (not browser-use)**: browser-use's headless Chromium silently fails to load `file://` URLs (readyState reports complete but the DOM is empty). Playwright handles `file://` correctly and is the project-standard E2E driver.

## §3 Completion report template

Final output (繁中):

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

Rules:

- The HTML line is **always present** (every format produces HTML)
- PDF line: appears only with `--format pdf` or `--format all`
- PPT line: appears only with `--format ppt` or `--format all`; on html2pptx failure, show 「PPT：失敗（詳見上方錯誤）」 instead
- Preview screenshot (PNG): always present (the Playwright screenshot runs in §2)
- Do not re-derive `$SLUG` in Stage 4; inherit the value derived in Stage 2A §4
