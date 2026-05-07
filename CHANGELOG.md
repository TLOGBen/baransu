# Changelog

格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-TW/1.1.0/)，版本號遵循 [Semantic Versioning](https://semver.org/lang/zh-TW/)。

## [1.1.14] — 2026-05-07

### 變更

- **`/baransu:write` 加 voice cue + long-input mode-aware suppression**（輕量版改動，SKILL.md +13/-2 行）
  - Stage 0 後加 **Voice cue 段**：optional `voice="..."` 參數；preset name（讀 `references/{name}-voice.md`）/ 具名作者 / 自由描述三種輸入；不覆蓋 rules 5/7/8（anti-AI 味底線）；Generate 模式忽略
  - Stage 2 Refine 末加 **Long input handling 段**：輸入 ≥ 5 段 OR ≥ 800 字（zh）/ ≥ 500 words（en）時，命中規則只改最影響的一處（mode-aware suppression）；rules 5/7/8 例外，仍每處套用
  - Rule tag examples 末新增 zh `voice 套用` / en `Voice applied`
- **零回歸保證** — 規則本文（zh rules 1-9 / en rules 1-7）零修改；`references/writing-principles.md` 整份零修改；既有 Refine 輸出格式（Before/After/修正說明）三 header 零修改；既有 zh/en prefix 行為零修改；/learn Stage 5 內部呼叫 `/write {LANG}`（不帶 voice）byte-for-byte backward compat。
- **新增結構測試** — `tests/skills/test-write-skill.sh`，14 個 bash 結構斷言（A1-A4 Voice cue 段、B1-B4 Long input handling、C1-C2 Rule tag、D1-D4 backward compat invariants），exit 0/1/2 標準閘門 contract，與既有 `tests/skills/test-{skill}-skill.sh` 命名慣例一致。

[1.1.14]: https://git.hy-tech.com.tw/ben.tsai/baransu/-/compare/1.1.13...1.1.14

## [1.1.13] — 2026-05-07

### 變更

- **Skill descriptions 統一三段式格式** — 全部 15 個 SKILL.md 的 `description` 改寫為 `Use When … Do … Trigger On …` 三段結構（analyze / bridge / codex-skill-transfer / design / dev / execute / grade / hunt / learn / read / review / ship / think / triage / write）。對模型 trigger 判斷與人類掃讀都更友善；繁中觸發短語全部保留。
- **codex-skill-transfer 工具映射補完 Plan Mode 差異** — `references/skill-mapping.md` §6 工具映射表新增兩列：
  - `AskUserQuestion` → 標註 Codex 的 `request_user_input` 只在 Plan mode 可用，不能當 drop-in
  - `EnterPlanMode` / `ExitPlanMode` → 明寫 Codex 沒有 skill-callable 等價物（active mode 由 developer message 切換），需改寫成 prompt-driven plan gate
- **Codex 端同步** — `codex/plugins/baransu/` 重生，反映新 description 格式 + plugin.json 版本。

[1.1.13]: https://git.hy-tech.com.tw/ben.tsai/baransu/-/compare/1.1.12...1.1.13

## [1.1.12] — 2026-05-07

### 新增 Codex CLI 支援

baransu 從本版起同時發行 Claude Code 與 Codex CLI 兩種變體。Claude 端是源頭，Codex 端是單向衍生產物。

- **Codex 變體目錄** — 整棵 Codex plugin tree 落在 `codex/`，獨立於 Claude 本體（`plugins/baransu/`），互不污染。
- **Repo-root marketplace catalog** — 新增 `.agents/plugins/marketplace.json`，讓使用者直接 `codex plugin marketplace add <git-url>` 即可安裝（不需 `--sparse` 或其他 flag）。
- **轉換工具 `/baransu:codex-skill-transfer`** — 一鍵把 Claude 端的 plugin / skills / marketplace 重生成 Codex 格式：
  - 自動轉 `disable-model-invocation` → `agents/openai.yaml`
  - 改寫 `$ARGUMENTS` 系列、bang-backtick shell injection 為 Codex 認得的自然語言
  - 描述超過 Codex 上限 1024 字元時自動剝除 Claude 觸發片語句子並收斂句尾
  - Plugin mode 自動產出 schema-合規的 marketplace catalog（`source` object 形、必選 `policy.installation` / `policy.authentication`、`category`）+ 巢狀 `plugins/<name>/` layout
- **Codex agent stubs** — `codex/plugins/baransu/.codex-agents-templates/` 內附 12 份 TOML stub，使用者自行複製到 `~/.codex/agents/` 啟用。
- **AGENTS.md** — Codex 版的 project-level instructions 檔，與 `CLAUDE.md` 對應。
- **README** — 新增 Codex CLI 安裝區（HTTPS / SSH / `--ref` pin tag）+「衍生產物別手改」警語。

### 修正

- 修掉 `codex-skill-transfer` SKILL.md 內殘留的 `` !`cmd` `` 字面 pattern，避免 slash-command 解析器把它當成 bash injection 而觸發 `command not found: cmd`。
- 修正 `grade` SKILL.md frontmatter — 描述含裸 colon（`tune_review_due: true`、`(00:00)`）導致 PyYAML 嚴格解析失敗。改用單引號包裹。

[1.1.12]: https://git.hy-tech.com.tw/ben.tsai/baransu/-/compare/1.1.4...1.1.12
