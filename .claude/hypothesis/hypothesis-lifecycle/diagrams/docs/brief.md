# Brief — 假說的生命週期（五張狀態機圖）

Form: diagram
Delivery: 多件
Approach: diagram-system
When: cjk-labels
Why: 呼叫端（/hypothesis）指定 --lane diagram，讀者要一眼看懂假說在哪些狀態之間移動，這是結構（狀態與轉移），用靜態狀態機圖最直接；五張圖一張加一部分，各自是單件，由 /hypothesis 的 diagrams.html 以 iframe 串起來，不需要 /draw 組頁。

## What must be obvious, and to whom

讀者：要維護 baransu 的人（看 /hypothesis 產出的 diagrams.html）。每張圖要一眼看出：假說會在哪些狀態之間移動、什麼事件推動它、哪裡會壞掉。五張圖一張比一張多一個部分，前一張的狀態在下一張裡位置不變，讀者只要看新增的部分。

## Fixed facts (from the caller's brief — never changed, never invented)

Labels are exactly these user-facing words; never variable names.

1. d1 正常流程（≤ 7 states）：還沒有假說 → 已寫下，與來源同步〔寫下（看過失敗、看過成功）〕 → prove-it 證明通過〔prove-it 重跑〕 → 完成〔宣告完成〕。
2. d2 adds 「來源被改了」：已寫下、prove-it 證明通過、完成 each → 過期：模型停在舊版〔程式或文件被改了〕；過期 → 已寫下，與來源同步〔/hypothesis --maintain〕。
3. d3 adds 讀者：過期 → 三個讀者都回報「過期」〔prove-it／review／綠燈重跑〕；三個讀者都回報「過期」 → 已寫下，與來源同步〔自動交給 /hypothesis --maintain〕。
4. d4 two numbered bug paths, broken states marked：
   - P1：已寫下 → 「P1 程式被改，引入 bug」〔改動（沒有過期拒答）〕 → 「P1 prove-it 說通過，但程式有 bug」〔prove-it 重跑〕。
   - P2：已寫下 → 過期〔改了兩次〕 → 三個讀者都回報「過期」〔讀者重跑〕 → 「P2 永遠過期，完成走不到」〔沒有人叫維護〕。
   - Fixed edge：三個讀者都回報「過期」 → 已寫下〔修正後：讀者自動交給維護〕。
5. d5 three decisions and the paths they block：
   - 專案裡有 8.15.0 的舊檢查 → 「P4 prove-it 讀到沒人管的舊那份」〔允許新舊並存時〕。
   - 專案裡有舊檢查 → 「P5 用沒檢查過『做得到』的舊檢查宣告完成」〔prove-it 讀舊的，說通過〕。
   - 已寫下 → 「P3 程式被改，綠燈只提醒就放行」〔改動後綠燈重跑〕。
   - 舊檢查 → 搬家，標「嚴格檢查未完成」 → 已寫下〔維護一次，補上嚴格檢查〕。

Real assets: none needed (no logo, data, track). Missing: none.

## Decided picture choices (mine, written down, never asked)

- Type: State Machine (`references/diagram/type-state.md`), static, no animation.
- Files: `d1-happy.html`, `d2-change.html`, `d3-readers.html`, `d4-paths.html`, `d5-decisions.html` in this folder; each self-contained, inline SVG, theme-aware (light/dark via `prefers-color-scheme`), phone-safe (SVG scales by viewBox, no horizontal scroll), fits the 560 px iframe the caller embeds it in.
- One shared look across all five: same palette, same node shapes, same positions for the shared states (d1→d3 grow by adding, never moving).
- Colour meaning: neutral ink for normal states; accent for the happy path; amber for 過期 states; red with a dashed outline and a ✕ marker for broken (bug) states; the fixed edge in d4 and the fix edge in d5 drawn in green.
- Quick request (`--quick`, 「一個 seed 直出」「不用細修」): one seed, promoted without a judge, no critique loop.
