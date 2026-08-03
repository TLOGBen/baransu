# CONTRACT — mifb 吸收 v2（design/book 動效與排版紀律）

## 目標
/design 三 preset 與 /book 模板吸收 mifb 工藝原則（阻尼動效、同心圓角、筆畫配重、
text-wrap 邊界）；Kami 動效曲線與自家權威表對齊；B2/B3/B4 明確不做。完工雙綠。

## 前提（Premises）
- P1 已驗 紙-preset DESIGN.md:251 與 root DESIGN.md:251 存在 overshoot spring 行
- P2 已驗 紙-preset/tokens.css:73 `--ease: cubic-bezier(0.4, 0, 0.2, 1)`
- P3 已驗 三 golden template 已有 pretty、無 balance；editorial-sanity 不作用於 book 模板
- P4 已驗 Makefile:19-27 mirror-check 刻意不在 make test 內
- P5 已驗 test_codex_skill_transfer.py:1009 硬編 "3.1.10"；plugin.json:3 現值 3.1.10
- P6 已驗 check.py Check D 驗九段標題存在＋內文禁 v1.2 token 名
- P7 已驗 google DESIGN.md:351 高頻禁令帶 progress 例外

## 可斷言條文
- [ ] A1: 紙-preset 與重套後 root DESIGN.md 不含 `BANNED` 字串；替代行含 `CALM`（與 tokens.css --ease byte 相同）
- [ ] A2: 紙 §8 新增過衝禁令（含「過衝」＋ BANNED 字串本身）；三 preset §8 各新增一行含字面 `transition: all` 的禁令
- [ ] A3: 紙/swiss §7 各新增恰三條（可中斷 transition/keyframe 分工、退場時長<進場、動效非唯一回饋）；google §7 僅新增可中斷＋退場時長一句，:351 例外行 byte 不變
- [ ] A4: 紙/swiss §5 同心圓角 advisory 含三要素（公式「外＝內＋padding」、「padding>24px 不強制」、「§4 既有元件不回溯」）；google §5 無此公式
- [ ] A5: 紙/swiss §6 stroke 行改配對句（400→1.5px、500–600→2px、同面單一粗細）；google §6 為 Symbols weight 軸跟隨文字一句、無 px 配對
- [ ] A6: expression-axes.md §2 Budget rules 恰新增一條 bullet ＝ `AXES_LINE` 逐字（英文、無數字）
- [ ] A7: typography-discipline.md 新增 text-wrap 段（英文）：balance＝標題且≤6行（Chromium）、pretty＝中短內文、長文皆不用；含「pretty 為基線、§3.3 sweep 處理殘餘」分層句＋「既有骨架 pretty 視為合規」
- [ ] A8: 三 golden template h1、h2 含 `text-wrap: balance`；既有 pretty 全數保留（diff 無刪除行）
- [ ] A9: golden-template.html 不含 `DANGLING` 字串；替代註解含字面 `deliberate exception` 與 `inv #9`
- [ ] A10: 版本鏈四處同值 `3.1.11`：plugin.json / marketplace.json / test_codex_skill_transfer.py:1009 / CLAUDE.md:25
- [ ] A11: root 重套為本地同步（root 工件被 .gitignore:40-46 刻意排除、不可 commit——實作中修正原兩 commit 前提）；單一 commit 含九項＋`make mirror` 重產之 codex/＋版本鏈
- [ ] A12: `make test` exit 0 且 `make mirror-check` 輸出 `== mirror in sync`
- [ ] A13（G2）: 新增內文不含 v1.2 banned token 名、不含 `oklch(`、不含 italic；preset DESIGN.md 繁中、references/*.md 英文
- [ ] A14（G2 撤銷防線）: diff 不含 lightbox 動畫、svg-rendering-rules 配對表、golden template `tabular-nums`

## 錯不起表面（Surface Inventory）
| 表面 | 格式 | 釘死測試 |
|------|------|----------|
| 紙 §7 easing 行 | `CALM` 恰一次 | seal byte-diff（VC↔檔） |
| 三 preset §8 禁令 | 各含字面 `transition: all` | grep 三檔各 ≥1 |
| golden ×3 標題 | `text-wrap: balance` | grep 三檔各 ≥1 且 pretty 計數不減 |
| 版本鏈 | `3.1.11` 恰四處 | grep 舊值 `3.1.10` 於四處 0 hits |
| google :351 例外行 | byte 不變 | git diff 不含該行 |
| AXES_LINE | 逐字 | seal byte-diff |

## Verbatim Constants
```text
CALM      = cubic-bezier(0.4, 0, 0.2, 1)
BANNED    = cubic-bezier(0.34, 1.56, 0.64, 1)
VERSION   = 3.1.11
BALANCE   = text-wrap: balance
AXES_LINE = Motion is never the only feedback channel — every animated state change pairs with a static cue (color, icon, or label).
DANGLING  = /design § paper-craft
```
