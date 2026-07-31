# CONTRACT — book 產出單檔自足化（CSS 內嵌、tokens.css 降為驗證來源）

## 目標
所有 /book 產出（long-form HTML 與 PPT per-slide HTML）單檔自足：CSS 全內嵌，
拷走即可開；{project_root}/tokens.css 僅剩兩個角色 — render 時的內容來源、
validate-output.ts 的比對來源 — 不再是產出的 runtime 依賴。

## 前提（Premises）
- P1 已驗：既有 4 份產出實際上已內嵌 tokens（grep 無 <link>；首個 <style> 為 tokens 全文副本）
- P2 已驗：SKILL.md:343 寫「linked tokens.css」，與實況相反（文件債）
- P3 已驗：slide-cores/*.html 含 `<link href="../tokens.css">`；render-pipelines §6b 未要求剝除，
  slide 寫到 .claude/book/slides-{slug}/ 後該相對路徑斷裂（slide 非自足、Playwright 渲染吃不到 tokens）
- P4 已驗：validate-output.ts 無自足性檢查；10 個 fixtures 皆無 <link>，新增檢查不破 fixtures
- P5 已驗：validate-output.ts:895 讀 project-root tokens.css 做 GATE-F tie-break（= tokens.css 的驗證用途，保留）
- P6 已驗：版本 bump 需同步 4 處（plugin.json / marketplace.json / codex mirror / test_codex_skill_transfer.py:971 硬編 "3.1.8"）；mirror 用 `make mirror` 重生

## 可斷言條文
- [x] A1: SKILL.md Stage 3 §2 head 規格改為「內嵌 <style>（完整 tokens.css 內容，含首行 preset 註解）」；全檔不再出現 "linked tokens.css" 字樣
- [x] A2: SKILL.md Constraints 新增自足條（prohibition 式）：輸出 HTML 禁含 `<link rel="stylesheet"` 與 `@import`；tokens.css 僅為 render 內容來源＋validator 比對來源，永不為 runtime 依賴
- [x] A3: render-pipelines.md §6b Step 1 明定：取 slide-cores skeleton 時剝除 `<link rel="stylesheet" href="../tokens.css">`、改內嵌 tokens.css 全文 <style>；Step 2 驗證清單 3 項→4 項，第 4 項字面「不含 `<link rel="stylesheet">`」
- [x] A4: validate-output.ts 新增核心檢查 self-contained（所有模式執行，同 structure check 層級）：文件存在 `link[rel="stylesheet"]` → FAIL＋exit 1；<style> 內容 match `/@import\b/` → FAIL；通過印 `OK  self-contained`；訊息照 Verbatim Constants 逐字
- [x] A5: tests/scripts/test_book_skill_validator.py 新增：負向×2（link / @import → exit 1＋對應 FAIL 行）、正向×1（swiss-positive.html → exit 0＋stdout 含 `OK  self-contained`）；既有 fixtures exit code 全部不變
- [x] A6: 版本 3.1.8 → 3.1.9，P6 的 4 處同步完成
- [x] A7: `make test` exit 0 且 `make mirror-check` 輸出「== mirror in sync」

## 錯不起表面（Surface Inventory）
| 表面 | 格式 | 釘死測試 |
|------|------|----------|
| validator OK 行 | `OK  self-contained` | test_self_contained_positive |
| validator FAIL 行（link） | 見 Verbatim | test_self_contained_link_fail |
| validator FAIL 行（@import） | 見 Verbatim | test_self_contained_import_fail |
| 跨面一致性 | long-form 與 per-slide 走同一段檢查碼（單一實作，無鏡寫） | 同上三條即釘 |

## Verbatim Constants
```
OK  self-contained
FAIL self-contained: external stylesheet <link href="{href}"> found — /book output must inline all CSS
FAIL self-contained: @import inside <style> — /book output must inline all CSS
link[rel="stylesheet"]
/@import\b/
3.1.9
```
