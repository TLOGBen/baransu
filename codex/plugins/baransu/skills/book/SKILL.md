---
name: book
description: Converts any content source into a browser-ready, Kami-themed HTML book
  with SVG diagrams — Acquire (URL / slug / local path / text) → Synthesize → Render
  (quality-gated). Trigger On '$book', '轉成 book', '做成 HTML book', '存成 book'. Not for
  editable Markdown output ($read to capture, $learn to digest) — $book only emits
  rendered HTML.
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

> **STATUS: stub（5.3.0 退場預告）**

本 skill 已由 kamishibai plugin 的 book skill 承接（渲染走 `kamishibai render`，@kamishibai/sdk）；本 stub 於 6.0.0 移除。

**User-facing language**: 繁體中文. All output shown to the user must be in Traditional Chinese.

## Outcome Contract

- **Outcome**: 接住 `$book` 觸發詞，把使用者轉介到 kamishibai plugin 的 book skill —— 觸發不落空、不留死巷。
- **Done when**: 使用者收到改裝指引（kamishibai plugin 的安裝式與新入口名），且本 skill 未產出任何檔案。
- **Evidence**: 本 stub 回覆的改裝指引訊息，含 plugin 名 `kamishibai` 與新入口 `/kamishibai:book`。
- **Output**: 一則繁體中文改裝指引；本版起不再輸出 HTML／PDF／PPTX。
- **Automation**: ultracode=neutral, loop=drivable（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）

## 唯一動作：轉介

1. 說明現況：baransu 的 book 管線已於 5.3.0 移交 kamishibai plugin；本 skill 只轉介，不合成內容、不產檔、不跑任何本目錄下的腳本。
2. 指路（Claude Code 內）：
   ```
   /plugin marketplace add https://github.com/TLOGBen/kamishibai
   /plugin install kamishibai@kamishibai
   /kamishibai:book <url | 檔案 | slug | 一段文字>
   ```
3. 指路（命令列，不經 plugin）：`npm i -g @kamishibai/sdk`，之後直接跑 `kamishibai render` / `kamishibai lint` / `kamishibai export --to pdf|pptx`。
4. 分流（與本次移交無關的需求，照舊）：只要可編輯 Markdown 走 `$read`（擷取）或 `$learn`（消化）。
5. 使用者若堅持要舊管線：據實說明本版已無執行面，唯一路徑是裝 kamishibai；不得自行拼裝替代流程。

## 蟄伏機件與退役時程

蟄伏機件（scripts/references）本版一位元未動，6.0.0 隨目錄實體退役——git 歷史即唯一備份（/analyze 前例）。

本目錄下的 `scripts` 與 `references` 自 5.3.0 起是凍結資產，除 Gate 10 loop-pauses 登記（驗證器仍解析 `references/loop-pauses.md`，該指標之實體收殮屬 6.0.0）外，不再是任何現行流程的一部分：不得援引為現行步驟、不得被其他 skill 當作渲染或閘門依據。等價能力一律走 kamishibai SDK。


## Codex Port Adapter - Bundled Agent Resolution

This plugin does not assume package-local TOMLs are auto-registered as custom
agents. The required definitions for this skill are bundled at
`../../.codex-agents/<agent-name>.toml`: `style-reviewer`.

Before every named-agent dispatch:

1. Resolve the exact bundled TOML from this `SKILL.md` directory (strip a
   leading `baransu:` namespace from the requested name).
2. Verify the file exists, then pass its absolute path and the task input to a
   generic Codex subagent. The first instruction to that subagent is to read
   the TOML's `developer_instructions` completely before doing any task work
   and to treat relative paths as relative to the TOML file.
3. If the TOML is missing or unreadable, stop with
   `AGENT_DEFINITION_MISSING: <path>`. Never invent, summarize, or substitute a
   role from the agent name.
