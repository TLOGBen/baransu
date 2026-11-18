# Codex 版 lint hook 打包成一個檔，是 repo 唯一的建置步驟

---
status: accepted
---

這個 repo 原本不帶任何建置工具鏈。Codex 版的 lint hook 是例外：`plugins/baransu/hooks/` 的共用引擎加上 `adapters/codex/`，用固定版本的 esbuild（`make codex-lint`）打包成 `codex/plugins/baransu/hooks/lint.mjs`，並把產物 commit 進 repo。

原因：Codex 每個 hook 事件都要啟動一支新的 Node 程式，一個工具呼叫會觸發改檔前、改檔後兩次。在這台機器實測，一次 hook 呼叫的時間如下：

| 做法 | 一次 hook 呼叫 |
|---|---|
| 打包版 | 約 310 ms |
| 直接執行 TS 原始碼（Node 22 去型別，加 resolve hook） | 約 740 ms |
| 直接執行 TS 原始碼，再開編譯快取 | 沒有改善 |

兩者每個動作相差將近 1 秒，同事每改一次檔都要多等這麼久。

## Considered Options

- **直接執行 TS**：引擎一行不改就能跑，也不需要建置步驟。但每次呼叫多花約 430 ms。
- **常駐的 MCP server**：沒有每次呼叫的啟動成本。但這條路沒有實測過，而且要多維護一個常駐程式。

## Consequences

- 改了 `plugins/baransu/hooks/{engine,util,adapters/codex}/` 之後，要重跑 `make codex-lint`，並 commit 產生出來的 `lint.mjs`。
- `lint.mjs` 不能手改，檔頭有標示。
- `lint.mjs` 第一行記著一個雜湊，涵蓋 `Makefile` 裡的 esbuild 指令和所有打包用的原始碼（`scripts/verify-codex-parity.py --lint-hash`）。`make parity-check` 重算後比對：原始碼或打包參數改了卻沒重新打包，就會失敗。它不重新打包，所以手改 `lint.mjs` 第一行以外的內容抓不到；重新打包要用到 npx 和網路，不放進每次都跑的檢查。
