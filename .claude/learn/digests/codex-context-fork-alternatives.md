---
topic: "Codex 替代 Claude context fork 的方案"
sources:
  - slug: "codex-subagents-spec"
    url: "https://developers.openai.com/codex/subagents"
  - slug: "codex-agents-sdk-guide"
    url: "https://developers.openai.com/codex/guides/agents-sdk"
  - slug: "codex-skills"
    url: "https://developers.openai.com/codex/skills"
created_at: "2026-05-06T10:30:00Z"
language: "zh"
phases_completed:
  - collect
  - digest
  - outline
  - fill_in
  - refine
---

# Codex 替代 Claude `context: fork` 的方案

## 重要修正

先前 `claude-skill-vs-codex-format-differences-porting.md` 與 `codex-skill-transfer` skill 都寫過「Codex 沒有 forked subagent 概念」「`context: fork` 無法直接移植」。這個結論**錯了**。Codex 有原生的 **Subagents** 系統（`developers.openai.com/codex/subagents`），是 `context: fork` 的最直接對應。本份 digest 修正這個誤判，並補上實作對照。

## 三條替代路徑

從最直接到最重型排：

### 路徑 1：Codex 原生 Subagents（最直接對應）

Codex 把 subagent 做成獨立的 TOML 檔，與 SKILL.md 平行存在：

```
~/.codex/agents/{name}.toml          # 個人層
.codex/agents/{name}.toml             # 專案層
```

每個 TOML 定義一個 agent，必填 `name` / `description` / `developer_instructions`，選填 `model` / `model_reasoning_effort` / `sandbox_mode` / `mcp_servers` / `skills.config` / `nickname_candidates`。內建三個預設 agent：`default`、`worker`、`explorer`（同名自訂會覆蓋）。

**並發語意**：

- Spawn 是 *explicit* —「Codex only spawns a new agent when you explicitly ask it to do so」。
- 多 agent 平行跑時，Codex 等到所有結果都回來才一次匯整給 parent。
- 全域上限：`agents.max_threads = 6`（預設）、`agents.max_depth = 1`（預設，避免遞迴爆量）。

**Sandbox / Approval 繼承**：

- 子 agent 自動繼承 parent session 的 sandbox policy 與 approval 模式（含 interactive session 內 `--yolo` 等臨時覆寫）。
- TOML 內若另寫 `sandbox_mode`，當 parent session 有 runtime override 時 **以 parent 為準**。

**對 baransu 的意義**：所有 `context: fork` + `agent: <type>` 的 Claude skill，可以一比一對應到 Codex 的 `.codex/agents/{name}.toml`：

| Claude (SKILL.md frontmatter) | Codex (`.codex/agents/{name}.toml`) |
|------|------|
| `context: fork` | （隱含 — 開了 TOML 就是 forked thread） |
| `agent: Explore` | 用 `name = "explorer"` 或自訂同義 agent |
| `agent: general-purpose` | `name = "default"` |
| `model: opus` | `model = "gpt-5.4"`（Codex 端對應） |
| `effort: high` | `model_reasoning_effort = "high"` |
| `allowed-tools: ...` | 透過 `mcp_servers = [...]` 限定可用工具 |

差異：Claude 的 forked context 是把 SKILL.md body 當成 task prompt 直接餵給子 agent；Codex 則是 skill 在 body 裡 **顯式指示** 「請 spawn 一個 explorer agent 處理 X」，由 Codex orchestrator 接手。觸發語法是自然語言指令（例如「Spawn one agent per point, wait for all of them, and summarize...」），不是 frontmatter 欄位。

**已知限制**（來自 GitHub issue tracker）：
- Issue #20077：`MultiAgentV2 spawn_agent` 預設用 full-history fork，會忽略 `agent_type` / `model` 覆寫。
- Issue #8664：原生 `spawn_subagents` / `chain_subagents` API 仍是 feature request 狀態 — 程式化呼叫的成熟度低於 Claude 的 Task tool。

⚠️ **命名衝突注意**：Codex 同時用 `agents/openai.yaml`（在 skill 內，做 UI/policy 元資料）與 `.codex/agents/*.toml`（在配置目錄，做 subagent 定義）。兩者**不是同一件事**。先前 `codex-skill-transfer` 把前者的位置寫成 `agents/openai.yaml`，正確；但若移植 `context: fork` 還要外加產出 `.codex/agents/{name}.toml`（在 user 配置層，不在 skill 包裡）。

### 路徑 2：Skill chain（輕量替代）

不用 subagent，把原本一個 forked skill 拆成兩個獨立 skill，第一個在 body 末尾告訴使用者（或模型）「請接著 invoke `$skill-2`」。Codex 支援 `$skill-name` mention 與 `/skills` 列表，所以 skill 互調是內建路徑。

**何時選這個**：原 forked skill 工作量小、無需獨立 context、且 parent 可以承受多消化幾百 token。對大多數 baransu skill（`/think`、`/write`、`/learn`）這條路徑足夠。

**何時不夠**：當 forked agent 是為了**避免污染 parent context**（像 `/execute` 的 impl-agent、`/triage` 的 investigator-agent，會讀大量檔案），skill chain 仍會把所有讀檔結果塞回 parent，達不到隔離目的，要走路徑 1。

### 路徑 3：Codex MCP server + Agents SDK（最重型）

把 Codex CLI 啟成 MCP server（`codex mcp-server`），再用 OpenAI Agents SDK 在外面寫多 agent 編排。SDK 的 `handoffs` 機制提供顯式 agent → agent 委派，每個 agent 看到的 context 由 SDK 控制。

**何時選這個**：
- 需要**程式化、可審計**的多 agent pipeline（CI / 自動化情境）
- 需要 multi-agent 之間有 git worktree 等級的隔離（每個 agent 自己的 worktree）
- 已經在用 Agents SDK 構建，Codex 只是其中一條 tool

**何時不選**：互動式開發、單機使用 — 殺雞用牛刀。baransu 的目標使用情境（CLI plugin）不需走這條。

## 對 codex-skill-transfer 的修正建議

`codex-skill-transfer` 目前對 `context: fork` 的處理是 **拒絕產出** 並要求人工重設計（見 transfer.py:327-333）。這個保守選擇仍合理——因為：

1. Skill 內部不知道 user 是否安裝了對應的 `.codex/agents/{name}.toml`
2. Subagent 觸發是自然語言指令，不是 frontmatter 翻譯
3. 路徑 1 牽涉 user 端配置（在 skill 包之外），自動化會跨越邊界

但**可以改進** transfer 報告的訊息：從目前的「Codex 無 forked subagent，請人工重設計」改成：

> `context: fork` / `agent: {X}` 偵測到。Codex 對應方案有三條：
> 1. **原生 Subagents**（推薦）：在 `~/.codex/agents/{name}.toml` 建對應 agent，並在 SKILL.md body 改寫為「請 spawn `{name}` agent 處理...」。
> 2. **Skill chain**：拆成兩個 skill，body 末加 `$next-skill` mention。
> 3. **Agents SDK + MCP**：跑 `codex mcp-server`、SDK 端做 handoff。
>
> 自動轉換無法替你決定哪條路徑。請手動處理。

這個修改一行報告字串就好，不需要改邏輯。

## 結論

`context: fork` 在 Codex 端**有對應**，只是分散在三個層級：

| 層級 | 路徑 1（推薦） | 路徑 2 | 路徑 3 |
|------|---------------|--------|--------|
| 隔離強度 | 完整 thread 隔離 | 無（共用 context） | 完整 worktree + thread |
| 設定位置 | `.codex/agents/*.toml` + SKILL.md | 純 SKILL.md | SDK 程式碼 + `codex mcp-server` |
| 觸發方式 | 自然語言 spawn 指令 | `$skill-name` mention | SDK `handoffs` 物件 |
| 適合情境 | 重 IO 的 forked skill | 輕量 skill chain | 程式化 pipeline |
| 移植成本 | 中（需建 TOML + 改寫 body） | 低（純拆 skill） | 高（外部框架） |

**對 baransu 的具體建議**：

1. `/execute` 與 `/triage` 重度依賴 forked agent — 走路徑 1，為每個既有 Claude agent（impl-agent、investigator-agent、merge-agent 等）建一份 `.codex/agents/{name}.toml`，連同 baransu plugin 一起發佈樣板。
2. 其餘 forked skill（如 `/baransu:review` 的三個 perspective agent）可考慮路徑 2 — skill chain 即可。
3. 完全不需走路徑 3，除非未來想做雲端版 baransu。

⚠️ **後續可調查**：
- `.codex/agents/{name}.toml` 的 `skills.config` 欄位細節（讓 subagent 預載特定 skill）
- Codex 的 `spawn_agents_on_csv`（experimental）對批次任務的成熟度
