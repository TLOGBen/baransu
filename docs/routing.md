# 三頻段路由（v3.0 起）

[← 回文件索引](README.md)

任務先看大小，再決定走哪條路。

| 頻段 | 什麼樣的任務 | 怎麼走 | 收尾證據 |
|---|---|---|---|
| **小** | 單檔、範圍清楚 | 直接實作，照 `plugins/baransu/skills/_shared/tdd.md` §7 的紅綠紀律；不走任何 skill | 一次紅 → 綠 的測試執行 |
| **中** | 一個功能、幾個檔案 | `/contract` 開工立約 → 實作 → `/seal` 收工封緘 | seal 五點驗收結果 |
| **大** | ≥ 2 個互相依賴的模組，context rot 是真的 | 先把整件事畫成決策圖、切成片，每片各自走中頻段（`/contract` → 實作 → `/seal`） | 每一片的 seal 結果 |

- **小頻段的紅綠紀律**：行為測試要斷言具名的值，不寫「有回應」「全綠」這類套套邏輯；功能壞掉時一定要有測試轉紅。
- **中頻段**：`/seal` 派一個 verify-only 的 seal-agent 做一次窄範圍驗證，findings 回主 session 修（複驗上限 2），全清才蓋 sealed 標記。
- **大頻段**：裝了 common 套件（wayfinder／delegate／strategic-advance）時，畫圖與執行可以走那條路——先偵測，不要假設有裝。

任務不遷就工具：小任務不硬上全套，大任務不偷走輕量路。

## 頻段之外的 skill

路由只規定「實作」怎麼走。其他 skill 依需要穿插：

- 方向未定 → 先 `/think`
- 出錯了 → `/hunt`
- 任何產出想要第二雙眼睛 → `/review`
- 收工 → `/ship`

## seal-guard hook

> ⚠️ **seal-guard hook（隨 plugin 生效，預設阻擋）**：session 結束時若偵測到未 `/seal` 的 user-facing 變更，會擋下並提示補 seal。降級：`SEAL_GUARD=log`（只記錄）或 `SEAL_GUARD=off`。遙測集中在 `~/.claude/baransu/telemetry/{專案}/{類型}-{YYYY-MM}.jsonl`，月回看檢討誤擋率（過高即降回 log 預設——可證偽條款）。

細節見 [驗證家族 · seal-guard hook](skills/verify.md#seal-guard-hook)。
