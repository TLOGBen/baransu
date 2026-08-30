---
name: design
description: 'Generates a UI/UX design spec or lints an existing DESIGN.md. Four modes
  — gen (guided DESIGN.md) / lint (preset-agnostic structure + consistency check,
  6 checks) / preset NAME / export-brief (cross-tool prompt-ready brief). Use when
  the user asks for a design system or visual spec. Trigger On ''$design'', ''生成設計規格'',
  ''設計規格''. Not For: technical-architecture design.md (lowercase); this skill only
  ever touches uppercase DESIGN.md (UI visual spec).'
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

> **STATUS: stub（5.3.0 退場預告）**

本 skill 已由 kamishibai plugin 的 design skill 承接（規格歸 DESIGN.md、渲染歸 SDK）；本 stub 於 6.0.0 移除。

UI/UX design specification skill（本版僅轉介）。All user-visible output is **Traditional Chinese (繁體中文)**.

## Outcome Contract

- **Outcome**: 接住 `$design` 觸發詞，把使用者轉介到 kamishibai plugin 的 design skill —— 觸發不落空、不留死巷。
- **Done when**: 使用者收到改裝指引（kamishibai plugin 的安裝式與新入口名），且本 skill 未寫出任何專案根工件。
- **Evidence**: 本 stub 回覆的改裝指引訊息，含 plugin 名 `kamishibai` 與新入口 `/kamishibai:design`。
- **Output**: 一則繁體中文改裝指引；本版起不再寫 `tokens.css` / `DESIGN.md` / `DESIGN.html` / `design-cores/` / `slide-cores/`。
- **Automation**: ultracode=neutral, loop=drivable（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）

## 唯一動作：轉介

1. 說明現況：baransu 的 design 管線已於 5.3.0 移交 kamishibai plugin；本 skill 只轉介，不生成規格、不寫檔、不跑任何本目錄下的腳本。
2. 指路（Claude Code 內）：
   ```
   /plugin marketplace add https://github.com/TLOGBen/kamishibai
   /plugin install kamishibai@kamishibai
   /kamishibai:design <草稿名> [原稿：截圖／舊產物／一段 CSS／網址]
   ```
   該 skill 走 臨摹 workflow（`init draft/<名>` → 寫 stylesheet → `render` + `snapshot` 對照 → 迭代 → `lint` → 人驗 → `promote`），視覺決策段（承諾的極端／記憶點／表現軸）在其 guided design decisions 內。
3. 指路（命令列，不經 plugin）：`npm i -g @kamishibai/sdk`，之後直接跑 `kamishibai init` / `kamishibai lint` / `kamishibai promote`。
4. 邊界照舊：本 skill 從不碰小寫 `design.md`（技術架構文件）；大寫 `DESIGN.md`（UI 視覺規格）的產出責任隨本次移交一併過去。
5. 使用者若堅持要舊四模式（gen / lint / preset / export-brief）：據實說明本版已無執行面，唯一路徑是裝 kamishibai；不得自行拼裝替代流程。

## 蟄伏機件與退役時程

蟄伏機件（scripts/references）本版一位元未動，6.0.0 隨目錄實體退役——git 歷史即唯一備份（/analyze 前例）。

本目錄下的 `scripts` 與 `references`（含三套 preset 與其 sanity 腳本）自 5.3.0 起是凍結資產，不再是任何現行流程的一部分：不得援引為現行步驟、不得被其他 skill 當作規格或閘門依據。等價能力一律走 kamishibai SDK。
