# Proofread procedure — /write Stage 4

Full execution detail for the Proofread path. Read this file when Proofread mode is detected, before executing Stage 4. The SKILL.md body stub restates the red lines (report-don't-rewrite, never invent a page number, the three fixed labels, the `.claude/write/` target); this file holds the procedure.

## 1. Acquire the source (page tracking is mandatory)

The 頁數 column must be precise, so acquisition must preserve page provenance:

- **PDF** (`.pdf`): read page by page with the Read tool's `pages` parameter, recording each finding's page verbatim from the page being read. If the PDF exceeds 20 pages, read in successive 20-page windows (`pages: "1-20"`, then `"21-40"`, and so on) and accumulate findings from every window into one ordered list keyed by **absolute** page number — never reset the page counter per window, and never stop after the first window. If any window's Read returns no extractable text (scanned or image-only pages), record that page range as 「無法擷取」 in the completion report rather than dropping it silently.
- **Markdown / plain text / inline body**: there is no pagination. Set 頁數 = 「—」 and make 段落／上下文 carry the locating anchor (nearest heading + a verbatim snippet) so the user can still jump to the spot.
- **DOCX / PPTX / other office formats**: convert with `markitdown` (same tool /book Stage 1 uses). If `markitdown` errors out or returns empty / no extractable text for the file (a total conversion failure, distinct from the page-loss case below), do NOT proceed to scan an empty body — that would emit an empty findings table that falsely reads as a clean document. Instead emit the completion-report line 「⚠️ 校對未執行：{file} 轉換失敗（markitdown 無法擷取內容），請改提供 PDF／Markdown／純文字」 and stop. When conversion succeeds, markitdown drops page boundaries (the usual case), so do NOT attempt to recover or guess a page: set 頁數 = 「—」 for every finding and locate each one entirely through 段落／上下文 (nearest heading + a verbatim snippet). State the page-boundary limitation in the completion report rather than fabricating page numbers.

Never invent a page number. If a finding's page cannot be determined with confidence, write 「—」, not a guess.

## 2. Scan against the error taxonomy

Six author-facing concerns collapse into the **three fixed 錯誤類型 labels** that the output table uses — every finding must carry exactly one:

| Author concern | 錯誤類型 label |
|---|---|
| 錯別字（用錯的字）、漏字（缺字） | **錯別字** |
| 用詞不妥、不符合繁體中文（台灣）商業習慣 | **用語不妥** |
| 贅字（多餘字詞）、語意模糊、語句不通順 | **語句不通順** |

For zh, apply the **Taiwan business-usage lens** on top of typo detection — flag mainland-Chinese or non-idiomatic vocabulary and suggest the Taiwan business-standard term. Anchor examples (not exhaustive): 質量→品質、信息→資訊、軟件→軟體、硬件→硬體、視頻→影片、默認→預設、用戶→使用者、激活→啟用、登錄→登入、屏幕→螢幕、打印→列印、網絡→網路、數據→資料／數據（依語境）、項目→專案、優化→最佳化／優化（依語境）. The zh format/style rule sets embedded in SKILL.md (spacing, punctuation, numbers, anti-AI-voice) are also valid sources of 語句不通順 / 用語不妥 findings.

For en, scan the typo / word-choice subset only (misspellings, wrong-word, awkward phrasing) and map to the same three labels.

**Precision over recall — no false positives.** Report only genuine issues a professional editor would mark. Stylistic preference that is already correct is not an error. If the scan finds nothing, still render the HTML with an explicit 「未發現問題」 state rather than padding the table.

## 3. Build the findings

Each finding is a six-field record matching the output columns exactly:

- **頁數** — precise page, or 「—」 (per §1).
- **段落／上下文** — a verbatim, Ctrl+F-friendly snippet of the surrounding text (the sentence or clause the error sits in), so the user can locate it fast. Include the nearest heading when pages are unavailable.
- **原文內容** — the exact problematic 字詞 only (the smallest span that is wrong), not the whole sentence.
- **錯誤類型** — exactly one of 錯別字 ／ 用語不妥 ／ 語句不通順.
- **建議修正** — the corrected wording.
- **修改原因** — one concise sentence on why (e.g. 「『質量』為大陸用語，台灣商業慣用『品質』」).

## 4. Render to `錯字修改.html` (book visual language, self-contained)

Match /book's Kami visual style **without** routing through the /book pipeline — a proofreading table is analysis output (which /book's "no LLM commentary" red line forbids) and carries no SVG (which /book's quality gate requires). So render directly here:

1. **Palette / type tokens**: read `{project_root}/tokens.css` first line for the preset slug and reuse its canonical color/type tokens, inlined into a `<style>` block so the file opens standalone. If `tokens.css` is absent, fall back to a clean, modern, light-theme palette (neutral paper background, one restrained accent, system-ui / serif reading font) — do not abort; proofread does not depend on `/baransu:design preset` having been run.
2. **Structure**: a single self-contained HTML document — a header (document title + scan summary: total findings and a per-type count), then one `<table>` with the six columns in this order: 頁數 ｜ 段落／上下文 ｜ 原文內容 ｜ 錯誤類型 ｜ 建議修正 ｜ 修改原因. Render 錯誤類型 as a color-coded badge (one hue per label) and wrap the problematic span in 原文內容 with `<mark>` so it stands out. Keep the reading column comfortable and the table zebra-striped for scanability.
3. **No validate-output.ts**: that gate enforces SVG presence and long-form section structure, neither of which applies to a report table. Do not run it; do not add a decorative SVG just to satisfy a gate that is not invoked here.
4. **Write target**: `.claude/write/錯字修改.html` (create `.claude/write/` if absent). Write the full file in one operation. If `.claude/write/錯字修改.html` already exists (a prior proofread of a possibly different document), do NOT silently clobber it: write to `.claude/write/錯字修改-<YYYYMMDD-HHMMSS>.html` instead (the collision scheme defined in SKILL.md Stage 4 — timestamp suffixes stay collision-proof under concurrent runs) and report the renamed path in the completion line, so an earlier report is never lost.

## 5. Completion report (Traditional Chinese)

```
✅ 校對完成：.claude/write/錯字修改.html
共 {N} 處：錯別字 {a}｜用語不妥 {b}｜語句不通順 {c}
頁數來源：{PDF 逐頁 ／ 無分頁（以段落上下文定位）}
```

When nothing was found, still report the written path: 「✅ 校對完成：{path}，未發現問題（已產出空表 HTML）」.
