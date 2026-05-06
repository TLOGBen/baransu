---
topic: "Claude Skill vs Codex 格式規範差異與移植路徑"
sources:
  - slug: "claude-platform-agent-skills"
    url: "https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview"
  - slug: "claude-code-skills"
    url: "https://code.claude.com/docs/en/skills"
  - slug: "codex-skills"
    url: "https://developers.openai.com/codex/skills"
  - slug: "codex-agents-md"
    url: "https://developers.openai.com/codex/guides/agents-md"
  - slug: "agentskills-io-overview"
    url: "https://agentskills.io"
  - slug: "agentskills-io-specification"
    url: "https://agentskills.io/specification"
  - slug: "codex-cli-reference"
    url: "https://developers.openai.com/codex/cli/reference"
created_at: "2026-05-06T09:25:39Z"
language: "zh"
phases_completed:
  - collect
  - digest
  - outline
  - fill_in
  - refine
---

# Claude Skill vs Codex 格式規範差異與移植路徑

## 1. 總覽：兩個系統其實高度同源

最重要的結論放最前：**Codex 與 Claude Code 都採用 [agentskills.io](https://agentskills.io) 開放標準**，所以「Skill」這層的格式並非各做各的。Claude Code 文件直接寫明「Claude Code skills follow the Agent Skills open standard, which works across multiple AI tools」，而 Codex 文件把自家 Skill 系統稱為 *Codex Agent Skills*，目錄結構（`SKILL.md` + `scripts/` + `references/` + `assets/`）與 Claude 的範例一字不差。

但兩者在「Skill 之外的協作層」拆得不一樣：

| 層 | Claude | Codex |
|----|--------|-------|
| 模組化能力包 | `SKILL.md`（在 `.claude/skills/`） | `SKILL.md`（在 `.agents/skills/`） |
| 專案/全域記憶 | `CLAUDE.md` | `AGENTS.md` |
| UI/品牌/policy 元資料 | 全併入 SKILL.md frontmatter | 獨立檔 `agents/openai.yaml` |
| 工具依賴宣告 | 隱含於環境（`allowed-tools` 列名） | 顯式宣告 MCP server (`dependencies.tools`) |

`CLAUDE.md` 與 `AGENTS.md` 是 *記憶/常駐指令* 機制，跟 Skill 是兩件事。Codex 的 AGENTS.md 還多了 `AGENTS.override.md` 與 `project_doc_max_bytes`（預設 32 KiB）這類細節控制。

## 2. SKILL.md 規範對比（核心）

### 2.1 必填欄位 — 一致

兩邊都只強制兩個欄位：

```yaml
---
name: my-skill
description: Brief description of what this skill does and when to use it
---
```

`name` 規則 Claude 寫得最嚴：≤ 64 字元、僅小寫字母/數字/連字號、禁用 `anthropic`/`claude` 保留字。Codex 文件未明寫類似限制，但 baransu 既有命名（全小寫連字號）天然兼容。

### 2.2 Claude 獨有的擴充欄位

Claude Code 在 frontmatter 裡塞了 11 個附加欄位：

| 欄位 | 用途 | Codex 對應方式 |
|------|------|----------------|
| `disable-model-invocation` | 禁止隱式調用 | `agents/openai.yaml` 的 `policy.allow_implicit_invocation: false` |
| `user-invocable` | 是否出現在 `/` 選單 | 無對應，Codex 預設兩種調用都通 |
| `allowed-tools` | 預核准工具清單 | 無對應；Codex 走自己的 sandbox/approval 模型 |
| `argument-hint` / `arguments` | 參數提示與命名 | **無對應** |
| `model` / `effort` | 覆寫 session 模型 | **無對應**（Codex 模型由 CLI flag 控制） |
| `context: fork` + `agent` | 在 forked subagent 跑 | **無對應**（Codex 沒有 forked subagent 概念） |
| `hooks` | skill 生命週期 hook | **無對應** |
| `paths` | glob 限定觸發 | **無對應** |
| `shell` | bash 或 powershell | **無對應** |

### 2.3 Codex 的「拆檔」設計

Codex 沒有把 UI/policy/依賴塞進 SKILL.md，而是另起一個 `agents/openai.yaml`：

```yaml
interface:
  display_name: "..."
  short_description: "..."
  icon_small: "..."
  brand_color: "#..."
  default_prompt: "..."

policy:
  allow_implicit_invocation: true

dependencies:
  tools:
    - type: mcp
      url: "..."
      transport: "..."
```

這對 baransu 的意義：**現在 baransu 的 SKILL.md frontmatter（特別是 trigger 描述）可以原封不動移植；但若要在 Codex 裡呈現品牌一致的 UI，就要為每個 skill 額外寫一份 `agents/openai.yaml`。**

## 3. 目錄結構與發現機制

### 3.1 路徑差異

```
Claude Code:  .claude/skills/{skill-name}/SKILL.md
              ~/.claude/skills/{skill-name}/SKILL.md
              <plugin>/skills/{skill-name}/SKILL.md

Codex:        .agents/skills/{skill-name}/SKILL.md
              $REPO_ROOT/.agents/skills/{skill-name}/SKILL.md
              ~/.agents/skills/{skill-name}/SKILL.md
              /etc/codex/skills/{skill-name}/SKILL.md
```

Codex 比 Claude 多出 *parent dir* 與 *admin scope*，並且支援 symlink。

### 3.2 衝突解決

- **Claude**：層級覆蓋規則 — Enterprise > Personal > Project；Plugin 用 `plugin-name:skill-name` namespace 不衝突。
- **Codex**：同名 skill 不合併，**兩個都出現在選單**讓使用者選。

### 3.3 記憶層的 override 機制

只有 Codex 的 AGENTS.md 提供顯式臨時覆蓋：在同一目錄放 `AGENTS.override.md` 會讓 sibling `AGENTS.md` 不被讀取。Claude 的 CLAUDE.md 沒有對應機制（只能改檔）。

## 4. 載入與執行模型

### 4.1 Progressive Disclosure — 兩邊都有

兩個系統都採三段式載入：

| 階段 | Claude | Codex |
|------|--------|-------|
| Level 1（啟動時） | 所有 skill 的 name + description | 同 + path |
| Level 2（被觸發） | 讀整個 SKILL.md | 同 |
| Level 3（按需） | 讀 references/、執行 scripts/ | 同 |

### 4.2 Context Budget

| 系統 | 描述清單上限 |
|------|-------------|
| Claude Code | 動態 1% context window（fallback 8000 字元）；單一 skill 的 `description + when_to_use` 截斷在 1536 字元 |
| Codex | 「roughly 2% of the model's context window, or 8000 characters when unknown」 |

兩者數量級接近（千字元級）。實務意義：**baransu 的 description 寫法（trigger 短語放前面、避開 jargon）兩邊通用**。

### 4.3 隱式 vs 顯式調用

- **Claude**：預設兩種都通，用 `disable-model-invocation: true` / `user-invocable: false` 細分。
- **Codex**：預設兩種都通，用 `agents/openai.yaml` 的 `policy.allow_implicit_invocation` 開關。粒度比 Claude 粗。

## 5. Claude 特有、不可直接移植的功能

這幾個是 baransu 既有 skill 重度使用、但 Codex 沒有原生對應的功能，移植時需要替代方案：

1. **動態 context 注入** —— `` !`git diff HEAD` `` 預先執行 shell 把輸出嵌入 prompt。Codex 端只能在 SKILL.md 寫成「請執行 `git diff HEAD` 並讀取輸出」，把預處理改成 Codex 自己用工具呼叫。
2. **`$ARGUMENTS` / `$0..$N`** —— 命令列參數實字替換。Codex 沒有此機制，需在 SKILL.md 改寫成「使用者提供的關鍵字會在訊息中提供」。
3. **`context: fork` + `agent`** —— 啟動子代理跑 skill。Codex 沒有 forked subagent；要重寫成同 context 內的工作流，或拆成多個 skill 串接。
4. **`allowed-tools` 預核准** —— Codex 走自己的 approval/sandbox 模型，這欄位移過去無效；改用 Codex CLI 的 `--full-auto` 或 trust prompt。
5. **`hooks` / `paths` / `shell`** —— 三個都無對應，必須在 SKILL.md 內以指令方式表達或刪除。

## 6. Codex 獨有、Claude 沒有的能力

- **`agents/openai.yaml` UI 元資料**：圖示、品牌色、display_name 用於 Codex IDE 整合的 UI。
- **MCP server 依賴宣告**：Codex skill 可在 yaml 內顯式聲明所需的 MCP server，IDE/CLI 會代為提示安裝。Claude 沒有對等宣告（依賴 user 自行設定 mcp）。
- **AGENTS.override.md**：記憶層的臨時覆寫，Claude 端無對應。
- **`project_doc_fallback_filenames`**：可讓 `TEAM_GUIDE.md` 之類檔名也被 Codex 當 AGENTS.md 讀。

## 7. 把 baransu 移植到 Codex 的實作路徑

依「最小可行 → 完整對等」分四階段：

### 階段一：雙投放骨架

在 plugin repo 底下新增平行目錄：

```
plugins/baransu/
  skills/                 # 既有，給 Claude Code
    think/SKILL.md
    review/SKILL.md
    ...
  codex-skills/           # 新增，給 Codex（最終透過 install script 投放到 .agents/skills/）
    think/SKILL.md
    review/SKILL.md
    ...
```

不要直接共用同一份檔案 — 因為 frontmatter 與動態注入要改寫。

### 階段二：Frontmatter 翻譯表（自動化）

寫一個轉檔腳本（Python 或 bash）讀 Claude SKILL.md，輸出 Codex 版本，套以下規則：

| Claude 欄位 | Codex 處理 |
|-------------|-----------|
| `name`, `description`, `when_to_use` | 直接保留 |
| `disable-model-invocation: true` | 移到 `agents/openai.yaml` → `policy.allow_implicit_invocation: false` |
| `user-invocable: false` | 在 SKILL.md body 開頭加說明「此 skill 僅供模型自動調用」 |
| `allowed-tools`, `model`, `effort`, `hooks`, `paths`, `shell`, `context`, `agent` | 全部捨棄 |
| `argument-hint`, `arguments` | 捨棄；body 內 `$ARGUMENTS` 改寫成自然語言 |

baransu 的 14 個 skill 多半是「指令式 prompt」，frontmatter 簡單，自動轉檔可吃下大多數情況。

### 階段三：動態注入降級

`` !`...` `` 與 ` ```! ` 區塊全部需改寫。建議統一規則：把原本內嵌的 shell 命令搬到 SKILL.md 的「Stage 0 — Prerequisites」段落，要求 Codex 先執行該命令並把輸出讀進來。例如 `/dev` skill 內 `!`git status`` → 改寫為「請先執行 `git status` 並把結果作為 Stage 1 的輸入」。

### 階段四：Subagent fork 替代方案

baransu 重度依賴 subagent 的有 `/execute` 和 `/triage`。兩種替代策略：

- **內嵌串接**：把 forked agent 的工作直接合到主 skill 裡，用更明確的階段標記（已是繁中輸出習慣，影響不大）。
- **多 skill 鍊**：把 sub-flow 拆成獨立 Codex skill，由主 skill 在 instructions 裡指示「請接著呼叫 `/baransu-execute-impl`」。Codex 支援 skill 互調，但成本是 user prompt 體驗變繁瑣。

優先選第一種；只有當原 subagent 工作量極大、會塞滿主 context 時才考慮拆 skill。

### 階段五：記憶層

baransu 沒有專案級 CLAUDE.md（其 CLAUDE.md 是 baransu repo 自身的開發指南），所以 Codex 端不需要對應的 AGENTS.md。如果未來想做「baransu 安裝後自動補一段全域行為守則」，可以提供範本 `~/.codex/AGENTS.md` 片段給使用者參考，但 *不* 直接寫入使用者的全域檔。

### 階段六：分發

- Claude 走 `.claude-plugin/marketplace.json` + `plugin.json`。
- Codex 沒有等價的 marketplace；最簡做法是 README 指示 user 把 `codex-skills/*` 複製到 `~/.agents/skills/`，或提供 `install.sh` 自動 symlink。Codex 文件提到「plugin distribution system (bundling multiple skills)」但細節未公開，先保守處理。

---

## 結論：移植難度評估

| 維度 | 難度 |
|------|------|
| SKILL.md body（指令文字） | 🟢 低 — 多數可原封移植 |
| 必填 frontmatter（name/description） | 🟢 低 — 一致 |
| 進階 frontmatter（disable-model-invocation 等） | 🟡 中 — 需翻譯到 `agents/openai.yaml` |
| 動態注入 / `$ARGUMENTS` | 🟠 中高 — 全部要改寫 |
| `context: fork` 子代理 | 🔴 高 — 無原生對應，要重設計 |
| 分發機制 | 🟡 中 — Codex 缺 marketplace |

整體：baransu 14 個 skill 中，`/think`、`/write`、`/read`、`/learn`、`/design` 這類偏「指令式 prompt」的 skill 移植成本最低；`/execute`、`/triage`、`/dev` 因依賴 subagent 與 hooks，需要最多重設計。

## 附錄 A：agentskills.io 開放標準（補抓）

agentskills.io 是 **Anthropic 原創、釋為開放標準** 的 Agent Skills 規範。已被 **30+ 工具採用**：Cursor、Gemini CLI、GitHub Copilot、VS Code、OpenAI Codex、Junie、OpenCode、OpenHands、Goose、Letta、Roo Code、Kiro、Factory、Snowflake Cortex、Databricks Genie、Laravel Boost 等。也就是說，遵循 agentskills.io 的 SKILL.md 一次寫好，可在 Claude Code、Codex、Cursor、Gemini CLI 之間共享。

### A.1 標準 frontmatter 欄位（規範性）

| 欄位 | 必填 | 約束 |
|------|------|------|
| `name` | Yes | 1–64 字元；僅小寫 unicode 字母、數字、連字號；不可前後綴連字號；不可連續連字號；**必須與父目錄名稱相同** |
| `description` | Yes | 1–1024 字元 |
| `license` | No | 授權名稱或檔案引用 |
| `compatibility` | No | ≤ 500 字元，宣告環境需求（產品、套件、網路存取等） |
| `metadata` | No | 任意 key-value mapping |
| `allowed-tools` | No | **Experimental**，空格分隔的預核准工具清單 |

關鍵發現：**`allowed-tools` 已進入開放標準（雖標 Experimental）**，意味 Codex 雖未文件化支援，但同名欄位可能未來直接相容；先寫上不違反規範。

`compatibility` 是 **跨工具表達環境需求的官方方法**，例如 `compatibility: Designed for Claude Code (or similar products)` 或 `compatibility: Requires git, docker, jq, and access to the internet`。比硬寫進 SKILL.md body 更結構化。

### A.2 比規範多寫的欄位 = 廠商擴充

依此重新分類 baransu skill 用到的欄位：

| 欄位 | 開放標準？ | 備註 |
|------|-----------|------|
| `name`, `description` | ✅ 規範必填 | 完全可攜 |
| `license`, `compatibility`, `metadata` | ✅ 規範選填 | 完全可攜 |
| `allowed-tools` | ⚠️ 規範選填（experimental） | 寫上無害，Codex 可能會忽略 |
| `disable-model-invocation`, `user-invocable`, `argument-hint`, `arguments`, `model`, `effort`, `context`, `agent`, `hooks`, `paths`, `shell` | ❌ Claude Code 廠商擴充 | Codex 不認；要 fallback 處理 |
| `agents/openai.yaml` | ❌ Codex 廠商擴充 | Claude 不認 |

### A.3 標準內建驗證工具

`agentskills/agentskills` repo 提供 `skills-ref` CLI：

```bash
skills-ref validate ./my-skill
```

**baransu CI 應加入這道驗證**，確保所有 skill 至少符合開放標準（即使主要對象仍是 Claude Code）。

## 附錄 B：Codex CLI 操作面（補抓）

### B.1 Approval / Sandbox

| Flag | 值 | 用途 |
|------|----|----|
| `--ask-for-approval` / `-a` | `untrusted` / `on-request` / `never` | 何時暫停等人工核准 |
| `--sandbox` / `-s` | `read-only` / `workspace-write` / `danger-full-access` | sandbox 等級 |
| `--dangerously-bypass-approvals-and-sandbox` / `--yolo` | (bool) | 跳過所有保護，僅供專用 sandbox VM |

⚠️ **`--full-auto` 已 deprecated**，改用 `--sandbox workspace-write`。先前移植路徑階段四提到「改用 Codex CLI 的 `--full-auto`」需更正為 `--sandbox workspace-write`。

### B.2 Skill 調用

Codex CLI reference 文件**未公開** `--skill` flag。實務上 skill 透過：
- 自然語言 prompt 隱式觸發（`policy.allow_implicit_invocation` 控制）
- 對話內輸入 `/skills` 列表，或 `$skill-name` 顯式 mention

baransu 移植時，「使用者怎麼觸發 skill」會從 `/baransu:think` 變成 `$baransu-think` 或在 prompt 提及，使用體驗略有差異。

### B.3 對 baransu 的具體影響

- 若 baransu skill 內部呼叫 shell（特別是 `/dev`、`/ship`、`/grade`、`/triage`），跑在 Codex 端時須確認 user 啟動時帶 `--sandbox workspace-write`；若是 `read-only`，所有寫檔/git 操作都會被 sandbox 阻擋。
- baransu 的 `/baransu:execute` 重度依賴檔案寫入與 git 操作，文件應指引 user 用 `--sandbox workspace-write -a on-request`。

## 結論修訂

**移植難度重新評估** —— 由於 agentskills.io 是 30+ 工具的共通標準，移植成本比第一輪估計**更低**：

| 維度 | 修訂後難度 |
|------|-----------|
| SKILL.md frontmatter 必填部分 | 🟢 低 — 完全跨工具可攜 |
| SKILL.md body | 🟢 低 — 多數可原封移植 |
| `compatibility` / `metadata` 宣告 | 🟢 低 — 用標準欄位代替 vendor-specific |
| Claude 廠商擴充欄位 | 🟡 中 — 翻譯到 Codex `agents/openai.yaml` 或捨棄 |
| 動態注入 `` !`...` ``、`$ARGUMENTS` | 🟠 中高 — 改寫為自然語言指令 |
| `context: fork` 子代理 | 🔴 高 — 重設計為主 context 階段化 |

**建議落地動作**：
1. 把所有 baransu skill 的 SKILL.md 加上 `compatibility` 與 `metadata.version` 欄位（無痛、純加分）
2. 在 CI 加入 `skills-ref validate ./skills/*/`
3. 寫轉檔腳本 `scripts/skills-to-codex.py`：吃 Claude SKILL.md、輸出 `codex-skills/{name}/SKILL.md` + 必要時的 `agents/openai.yaml`
4. 文件指引 Codex user 用 `--sandbox workspace-write -a on-request` 啟動
