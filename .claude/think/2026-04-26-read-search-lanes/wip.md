---
topic: "/read 三條搜尋型 lane（--web / --gh / --x）+ 選單升級為 AskUserQuestion"
status: "wip — 計畫已通過 /review 修訂、四主題已決，等使用者回來決定 handoff 目標（/analyze vs /dev）"
created_at: "2026-04-26T01:30:00+08:00"
think_stage: "G — 已通過 review 折回，等 Stage G 第二次 gate"
parent_context: "/learn 試跑時發現痛點 → 先用 /think 強化 /read"
---

# WIP — /read 搜尋型 lane 強化

## 一、起點

使用者試跑 `/learn 我想學一下上下文的知識` 時注意到：

1. WebSearch 是手動由 Claude 在 /learn 外部跑的，沒被內建
2. `/read --topic` 的論文清單是 free-text 編號選擇，可改用 AskUserQuestion
3. 同樣的「關鍵字搜尋型」入口可以擴展到 gh / X

於是把 /learn 暫停（已抓 5 篇實務文章 + --topic 待選），開 /think 設計 `/read` 增強。

---

## 二、/learn 暫停狀態（一併記錄，方便回來續跑）

### 已抓進 .claude/read/material/

| slug | source |
|------|--------|
| effective-context-engineering-for-ai-agents | https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents |
| harness-design-long-running-apps | https://www.anthropic.com/engineering/harness-design-long-running-apps |
| context-engineering-langchain | https://blog.langchain.com/context-engineering-for-agents/ |
| jetbrains-smarter-context-management | https://blog.jetbrains.com/research/2025/12/efficient-context-management/ |
| recursive-language-models | https://www.primeintellect.ai/blog/rlm |

### 學術論文（search-papers.py 候選）

關鍵詞 `long context window LLM survey` 返 10 篇，建議勾選 `4 5 10`：

- 4: A survey on large language model based autonomous agents (2024)
- 5: Mamba: Linear-Time Sequence Modeling with Selective State Spaces (2023)
- 10: Retrieval-Augmented Generation for Large Language Models: A Survey (2023)

清單未確認、Stage 2 評分未開始。

**回來續跑路徑**：直接告訴 Claude「繼續 /learn」並挑論文編號，或重跑 `/learn` 給五個 slug。

---

## 三、/think 對焦結論

| 維度 | 鎖定值 |
|------|--------|
| 目的 | 只補今天遇到的兩個痛點：WebSearch 內建 + 論文選單 AskUserQuestion |
| 範圍 | 擴大為三條搜尋 lane：--web / --gh / --x |
| 採集者原則 | 不做內部評分，schema-level health check 不算審判 |
| 跨 skill 改動 | 不改 /learn（受 Stage 0 spike 結果條件約束） |
| 抽提承諾 | 無。三份 ref 就是三份 |

---

## 四、修訂版計畫（五段式）

### Building

**Stage 0 — Spike (30 min)**：實作前驗證 `/learn → /read → AskUserQuestion` 三層巢狀透傳。
- 透傳成功 → KD4 完整執行
- 透傳失敗 → KD4 改為 academic-search 不升級（保留 numbered list）

**Stage 1 — 三條搜尋 lane**

1. `--web "keyword"`：WebSearch → AskUserQuestion → 走 URL pipeline
2. `--gh "keyword"`：`gh search repos --limit 12 --sort stars "{keyword}"` → AskUserQuestion → 走 GitHub URL pipeline
3. `--x "keyword"`：x-search.md 薄殼引用 web-dynamic.md WSL2 path → schema check → 抽 tweet URL → AskUserQuestion → 選定走 web-dynamic
4. `--topic` 選單：條件升級

**Stage 2 — 補 AskUserQuestion 互動 spec**：在 SKILL.md 新增一節，寫死容量、escape、多輪語意、跨 skill surface 預期。

### Not building

- /learn 程式碼修改（受 Stage 0 約束）
- everything-cli 4-tier acquisition
- Jina 預處理層
- gh search code
- X thread / reply tree 全貌
- AskUserQuestion 模板抽提承諾（**整條刪除**）

### Approach

extend /read + 條件升級 --topic。

**Schema-level health check**：
- WebSearch：API 錯誤即停 / 0 結果即停 / 1-11 結果 collapse 為單輪
- gh search：rate limit 錯誤即停；0 repos 即停；100+ 由 `--limit` 截斷
- --x：navigate 後 substring + 長度 check：login wall / rate limit / 文字長度 < 500 即 fail-fast
- 既有 fail-fast：WebSearch 美國地理限定、gh CLI 必裝、Chrome MCP 必連線

### Key decisions

1. 3 lane 各寫獨立 ref，**不承諾未來抽提**
2. `--x` 階段化 Chrome MCP：搜尋階段必經，採集階段交回 URL pipeline 自動路由
3. 3 lane 不做 1-5 評分；schema-level health check 視為 acquire 失敗，不算審判
4. 新增 4 個 ref 檔：`web-search.md` / `gh-search.md` / `x-search.md`（薄殼引用 web-dynamic）；`academic-search.md` 改動受 Stage 0 約束
5. AskUserQuestion 互動規格：3 輪×4，每輪 1 槽 escape，**實際 result slots = 9**；N≤3 → 1 輪、4-6 → 2 輪、N≥7 → 3 輪；單選即終止

### Unknowns（三要素齊備）

- **AskUserQuestion 跨 skill 透傳**
  延後理由：當前無法在 unit test 模擬跨 skill 呼叫鏈
  決定者/時點：實作前 30min spike (Stage 0)，失敗即退回 academic-search 不升級
- **Chrome MCP 在 x.com 的 DOM 路徑**
  延後理由：x.com DOM 易變，selector 寫死必失效
  決定者/時點：v1 用 get_page_text 全頁文字 + LLM 抽取；改版後由 /hunt 觸發更新
- **gh CLI 缺失處理**
  延後理由：不引入安裝指引邏輯
  決定者/時點：v1 fail-fast 顯示安裝命令；v2 由 /think 重啟

---

## 五、/review 結果摘要（已折回）

兩位 reviewer（architecture + quality）平行派遣 + adversarial 一輪。

四個主題已決：

| Theme | 決議 |
|-------|------|
| A — AskUserQuestion 互動 spec（含 P0 跨 skill 透傳） | 實作前先 spike + 實作後補 spec |
| B — `--x` 失敗模式 + lane 薄殼化 | Approach 明寫 schema check + x-search.md 薄殼化 |
| C — 搜尋 lane 邊界條件 | 寫進 Approach |
| D — 「先複製後抽提」缺觸發條件 | 刪「後抽提」承諾 |

Packaged confirm：Unknowns 三要素已補齊（理由 + 決定者/時點）。

Advisory（未動）：
- A-1：「採集者不審判」定義模糊 → KD3 已加定義（schema check 不算審判）
- A-2：4 lane 共用骨架抽到 SKILL.md → 過度工程，留意即可
- A-3：plan 加「AskUserQuestion 互動 spec」一節 → 已採納，列入 Stage 2

---

## 六、回來時的下一步

`/think` Stage G 第二次 gate 待回答：

| 選項 | 說明 |
|------|------|
| 1. 批准實作（中型 → /analyze）【推薦】 | 8 個檔以上 + 條件分支 + 跨層，建議走 analyze 展開為 spec 後再 execute |
| 2. 中型任務但走 /dev | 跳過 analyze 直接 TDD；風險：條件分支可能超出單 session |
| 3. 還有地方要對焦 | 修訂後仍有不收斂處 |
| 4. 放棄 | 結束 |

回來時直接喊「繼續 think」或「批准送 analyze」即可。

---

## 七、相關檔案

- 既有：`plugins/baransu/skills/read/SKILL.md`
- 既有：`plugins/baransu/skills/read/references/acquisition/{academic-search,chrome-tab,clipboard,local-file,web-static,web-dynamic}.md`
- 既有：`plugins/baransu/skills/read/scripts/search-papers.py`
- 既有：`plugins/baransu/skills/learn/SKILL.md`（Stage 1.2 是 P0 trigger 來源）
- 預計新增：`plugins/baransu/skills/read/references/acquisition/{web,gh,x}-search.md`
- 預計修改：`plugins/baransu/skills/read/SKILL.md`（Stage 1 路由 + AskUserQuestion 互動 spec 一節）、`plugins/baransu/skills/read/references/acquisition/academic-search.md`（受 Stage 0 約束）

---

## 八、參考素材

- `~/project/clis/everything-cli/skills/research/SKILL.md`：4-tier deterministic acquisition、Jina 預處理層、Chrome MCP 完整工具表（不採用，但可參考失敗模式）
