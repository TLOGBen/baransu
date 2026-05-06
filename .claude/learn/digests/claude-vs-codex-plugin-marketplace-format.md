---
topic: "Claude Code vs Codex plugin/marketplace 格式對照"
sources:
  - slug: "claude-marketplace-docs"
    url: "https://code.claude.com/docs/en/plugin-marketplaces"
  - slug: "claude-marketplace-real-example"
    url: "https://github.com/anthropics/claude-plugins-official/blob/main/.claude-plugin/marketplace.json"
  - slug: "codex-plugins-overview"
    url: "https://developers.openai.com/codex/plugins"
  - slug: "codex-plugin-build"
    url: "https://developers.openai.com/codex/plugins/build"
created_at: "2026-05-06T11:00:00Z"
language: "zh"
phases_completed:
  - collect
  - digest
  - outline
  - fill_in
  - refine
---

# Claude Code vs Codex plugin/marketplace 格式對照

## 一句話結論

兩邊都採「plugin = 一包 components；marketplace = plugin 的清單」雙層架構，**檔名與目錄路徑接近鏡像**（`.claude-plugin/` ↔ `.codex-plugin/`），baransu 可在同一 repo 雙投放，互不衝突。最大差異是 Codex 有內建「OpenAI Curated」marketplace 而 Claude 沒有。

## 1. 兩層架構：plugin manifest vs marketplace catalog

兩邊都把這兩件事拆開：

- **plugin manifest** = 「我這個 plugin 包含什麼 components、版本是多少、誰做的」
- **marketplace catalog** = 「這份清單列出哪些 plugin、各自從哪裡拉」

一個 plugin 可以脫離 marketplace 直接被安裝（local path）；一個 marketplace 可以包含 N 個 plugin（git-subdir 或 URL 引用）。

## 2. 路徑對照

| 用途 | Claude Code | Codex |
|------|-------------|-------|
| Plugin manifest | `.claude-plugin/plugin.json`（plugin 根目錄內） | `.codex-plugin/plugin.json`（plugin 根目錄內） |
| Marketplace catalog（repo） | `.claude-plugin/marketplace.json`（repo 根目錄） | `$REPO_ROOT/.agents/plugins/marketplace.json` |
| Marketplace catalog（個人） | （無對應；看自加 marketplace） | `~/.agents/plugins/marketplace.json` |
| 內建 marketplace | 無 | "OpenAI Curated"（隨 CLI 內建） |

⚠️ **Codex 命名一致性**：Codex 把 *使用者層級的東西*（subagents、skills、plugin marketplace）統一收在 `.agents/`：`.agents/skills/`、`.codex/agents/*.toml`（注意這條走 `.codex/` 而非 `.agents/`，是 OpenAI 自己的不一致）、`.agents/plugins/marketplace.json`。Claude 則一律走 `.claude-plugin/` 或 `.claude/`。

## 3. plugin.json 欄位對照

兩邊都簡單，差別在「什麼是必填」：

| 欄位 | Claude `.claude-plugin/plugin.json` | Codex `.codex-plugin/plugin.json` |
|------|------------------------------------|-----------------------------------|
| `name` | 必填 | 必填（kebab-case） |
| `version` | 選填（但官方建議寫，否則 git-host 把每個 commit 當一個版本） | **必填**（semver） |
| `description` | 選填但建議 | **必填** |
| `author` / `homepage` / `repository` / `license` / `keywords` | 選填 | 選填 |
| 元件指標 | 不需要（Claude 從檔案系統發現 `skills/`、`agents/`、`hooks/`、`commands/`） | 必須在 manifest 列出：`"skills": "./skills/"`、`"mcpServers": "./.mcp.json"`、`"apps": "./.app.json"`、`"hooks": "./hooks/hooks.json"` |
| UI 元資料 | 無單獨欄位 | `interface` 物件：`displayName` / `shortDescription` / `category` / `logo` / `screenshots` |

**核心哲學分歧**：
- Claude **filesystem-driven** — manifest 只標註 plugin 身份，components 由 Claude Code 掃目錄發現。對 baransu 重要：`plugin.json` 不該列 `skills` 陣列（之前在 v0.3.0 加過、立刻 revert，CLAUDE.md 已記載）。
- Codex **manifest-driven** — components 必須在 `plugin.json` 顯式指定路徑，且**所有路徑必須以 `./` 開頭**（這是 Codex 文件明確規定的 path convention）。

## 4. plugin 可以 bundle 哪些 components

| 類型 | Claude Code | Codex |
|------|-------------|-------|
| Skills | ✅ | ✅ |
| Agents（subagent definitions） | ✅（`agents/`） | ⚠️ Codex subagent 在 `.codex/agents/*.toml`（user-side），不在 plugin 包裡 |
| Hooks | ✅ | ✅ |
| MCP servers | ✅ | ✅ |
| LSP servers | ✅ | ❌ |
| App connectors | ❌ | ✅（GitHub / Slack / Google Drive / Gmail 整合） |
| Slash commands | ✅（合併進 skills） | ✅ |

baransu 含義：
- baransu 14 個 skill + 11 個 agent → skills 可投放兩邊；agents 在 Codex 端必須改用 `.codex/agents/*.toml`，**不能放進 plugin 包**（這跟前一篇 digest 的結論一致）。
- 沒用 LSP，沒用 app connector，這兩格不影響。

## 5. marketplace.json 欄位

### 5.1 Claude Code marketplace（從 anthropics/claude-plugins-official 實例）

```json
{
  "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
  "name": "claude-plugins-official",
  "description": "...",
  "owner": { "name": "Anthropic", "email": "support@anthropic.com" },
  "plugins": [
    {
      "name": "42crunch-api-security-testing",
      "description": "...",
      "author": { "name": "42Crunch" },
      "category": "security",
      "source": {
        "source": "git-subdir",
        "url": "https://github.com/42Crunch-AI/claude-plugins.git",
        "path": "plugins/api-security-testing",
        "ref": "v1.0.1",
        "sha": "56273e0e20762d76640838300a7431c4260cad32"
      },
      "homepage": "https://42crunch.com"
    }
  ]
}
```

**Source 四種變體**：
1. `git-subdir`（最常見）：含 `url` / `path` / `ref` / `sha`
2. `url`：整個 repo 就是一個 plugin
3. `github`：`{ "source": "github", "repo": "...", "commit": "..." }`
4. 字串路徑：`"./plugins/agent-sdk-dev"`（local）

⚠️ **Schema URL 是死連結**：`anthropic.com/claude-code/marketplace.schema.json` 實際 404，但欄位語意可從 anthropics/claude-plugins-official 與 hesreallyhim/claude-code-json-schema（社群非官方版）反推。

**`strict` 欄位**：
- `strict: true`（預設）：plugin manifest 是 component 定義的權威，marketplace 不能覆寫。
- `strict: false`：允許 marketplace 級別的覆寫。一般 plugin 應該用預設。

**版本解析機制**：
- Plugin manifest 有 `version` → user 只在 version bump 時收到更新。
- Plugin manifest 無 `version` 且 marketplace 走 git host → 每個 commit 都算一個新版本。
- 對 baransu：CLAUDE.md 已規定「每次發佈都 bump」，確保 user 收到更新。

### 5.2 Codex marketplace

文件本身對 marketplace.json 的 schema 沒有像 Claude 那樣完整公開（截至本次抓取），但已知：

- 內建 "OpenAI Curated" marketplace 是隨 CLI 預載的
- User 自製 marketplace 路徑 fixed：`~/.agents/plugins/marketplace.json`
- Repo 級 marketplace 路徑 fixed：`$REPO_ROOT/.agents/plugins/marketplace.json`
- CLI 提供 `/plugins` 命令，UI 內以 marketplace 為 tab 分組

⚠️ **後續可調查**：Codex marketplace 的 source 變體、version 解析、是否有 strict 對應欄位。`/codex/plugins/build` 文件對 manifest 寫得詳細，但 marketplace 的部分留白。

## 6. 安裝與調用流程

| 步驟 | Claude Code | Codex |
|------|-------------|-------|
| 加入 marketplace | `/plugin marketplace add <url-or-path>` | 透過 `/plugins` UI 切 marketplace tab，或寫進 config 自動載入 |
| 更新 marketplace | `/plugin marketplace update` | 透過 `/plugins` UI |
| 安裝 plugin | `/plugin install <plugin>@<marketplace>` | 透過 `/plugins` UI 點安裝 |
| 開關 plugin | 透過 `/plugins` UI | `enabled = false` 寫在 `~/.codex/config.toml` |
| 調用 plugin 內 skill | `/plugin-name:skill-name` 或自然語言 | `@plugin-name` mention 或自然語言 |

互動方式差異：Claude 偏 CLI 命令導向，Codex 偏 UI 命令導向（雖然 `/plugins` 也是命令，但底下走的是互動 UI）。

## 7. 對 baransu 的具體實作建議

### 7.1 雙投放結構（不需要新 repo）

baransu 既有目錄已是 Claude 形態：

```
.claude-plugin/marketplace.json     # Claude marketplace catalog
plugins/baransu/
  .claude-plugin/plugin.json        # Claude plugin manifest
  skills/                            # 14 個 skill
  agents/                            # 11 個 agent
```

加入 Codex 投放只需新增三條路徑，**不動既有檔**：

```
.agents/plugins/marketplace.json    # 新增：Codex marketplace catalog
plugins/baransu-codex/               # 新增：Codex plugin 根
  .codex-plugin/plugin.json         # 新增：Codex plugin manifest（required: name/version/description）
  skills/                            # codex-skill-transfer 產出處
.codex/agents/                       # （optional）為 /execute 等 forked-agent skill 預備樣板
  impl-agent.toml
  investigator-agent.toml
  ...
```

`.claude-plugin/`、`.codex-plugin/`、`.agents/`、`.codex/` 互不衝突 — 一個 repo 同時對兩邊發佈完全可行。

### 7.2 plugin.json 對照寫法

Claude 端（既有）：
```json
{
  "name": "baransu",
  "version": "1.1.3",
  "description": "..."
}
```

Codex 端（新增）：
```json
{
  "name": "baransu",
  "version": "1.1.3",
  "description": "...",
  "skills": "./skills/",
  "interface": {
    "displayName": "Baransu",
    "shortDescription": "Deliberate before executing, verify after.",
    "category": "productivity"
  }
}
```

差三件事：必填的 `description`、必填的 component 指標 `skills`、選填但 UI 會用的 `interface`。

### 7.3 marketplace.json（給其他人安裝 baransu 用）

Claude 端（既有 `.claude-plugin/marketplace.json`）已正常。

Codex 端（新增 `.agents/plugins/marketplace.json`）：

```json
{
  "name": "baransu",
  "owner": { "name": "ben.tsai" },
  "plugins": [
    {
      "name": "baransu",
      "source": "./plugins/baransu-codex",
      "description": "..."
    }
  ]
}
```

User 端安裝步驟：複製整個 repo（或 git clone），用 `/plugins` UI 加入 marketplace。

### 7.4 codex-skill-transfer 應該擴展嗎？

目前 `codex-skill-transfer` 只處理單一 SKILL.md 的轉檔。要擴展到「整個 plugin」轉檔，需要新增：

1. 讀 `.claude-plugin/plugin.json` → 寫 `.codex-plugin/plugin.json`（補必填欄位、加 `skills` 指標、加 `interface`）
2. 處理 `agents/` 目錄 → 不放進 plugin 包，而是 emit 到 `.codex/agents/{name}.toml`（user-side）
3. 處理 marketplace 對應（？）— 但 baransu 自己就是 marketplace 主，這個對外發佈的工作不在 transfer skill 的職責範圍。

**建議**：暫不擴展 codex-skill-transfer 到 plugin/marketplace 層。維持「single skill 轉檔」的清楚邊界，plugin 級別的對應由 baransu 自己手寫一份 `.codex-plugin/plugin.json` 就夠（一次性工作）。

## 結論

兩個生態系在 plugin/marketplace 層的設計**驚人地對稱**：

| 維度 | 結論 |
|------|------|
| 雙投放可行性 | 🟢 高 — 路徑無衝突，一個 repo 即可 |
| plugin manifest 移植 | 🟢 低成本 — 加三個欄位即成 |
| marketplace.json 移植 | 🟡 中等 — 結構相近，source 變體待確認 |
| Components 涵蓋 | 🟡 中 — agents 必須移到 user-side TOML，LSP/app-connector 兩邊獨有 |
| 內建 marketplace | Codex 有 "OpenAI Curated" 是它的 distribution 優勢 |

**立即可做的下一步**（成本最低）：寫一份 `plugins/baransu/.codex-plugin/plugin.json` 樣板（10 行 JSON），baransu 就**已經是雙投放 ready**，user 可手動把目錄當 local plugin 安裝到 Codex。後續再考慮要不要正式上 Codex marketplace。
