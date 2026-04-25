# Tasks: plugin-meta
**前置群組**：skill-execute

plugin.json 和 README 的更新需要在 SKILL.md 最終格式確定後才能準確撰寫版本號和功能說明。

---

## TASK-plugin-meta-01: plugin.json 版本號升級

**需求追溯**：REQ-007
**目標**：將 `plugins/baransu/.claude-plugin/plugin.json` 的版本號升級，並在 skills 列表中新增 execute skill 的條目，確保用戶安裝後能識別並使用 /baransu:execute。
**驗收標準**：
- [ ] `plugin.json` 中 `version` 欄位已升級（格式：semantic versioning，minor bump）
- [ ] `plugin.json` 的 skills 陣列中已新增 execute skill 的條目
- [ ] execute 的條目包含正確的 name、description、path 欄位
- [ ] `marketplace.json`（若有版本號）已同步更新

### 步驟

#### 讀取現有 plugin.json
- [ ] 讀取 `plugins/baransu/.claude-plugin/plugin.json`，確認當前版本號
- [ ] 讀取現有 skills 列表格式，確認新增條目的正確格式

#### 升級版本號
- [ ] 計算新版本號（在現有版本基礎上 minor bump）
- [ ] 更新 `version` 欄位

#### 新增 execute skill 條目
- [ ] 在 skills 陣列新增 execute 條目
- [ ] 確認 path 指向 `skills/execute/SKILL.md`

---

## TASK-plugin-meta-02: README.md 新增 /execute skill 說明

**需求追溯**：REQ-007
**目標**：在 `README.md` 中新增 `/baransu:execute` skill 的說明，包含核心目的、觸發條件、前置需求（需先跑 /analyze）、以及一個使用範例。
**驗收標準**：
- [ ] README.md 中新增 `/baransu:execute` 的描述段落
- [ ] 說明包含：核心目的（中大型任務自動執行引擎）
- [ ] 說明包含：前置需求（需先完成 /baransu:analyze，提供 spec 目錄路徑）
- [ ] 說明包含：agent-only skill 結構與 prompt cache 優化的說明（一句話）
- [ ] 說明包含：一個使用範例（`/baransu:execute .claude/analyze/2026-04-25-my-feature/`）
- [ ] README 的 Roadmap section 中 /execute 項目標記為已完成（移出計劃，移入已完成）
- [ ] plugin.json 版本號在 README 中同步更新（若 README 有顯示版本號）

### 步驟

#### 讀取現有 README
- [ ] 讀取 `README.md`，定位現有 skill 說明的格式
- [ ] 定位 Roadmap section 中 /execute 的位置

#### 新增 /execute 說明
- [ ] 在 Skills 表格或說明區塊新增 execute 條目
- [ ] 撰寫使用範例

#### 更新 Roadmap
- [ ] 將 /execute 從「計劃中」移至「已完成」
- [ ] 更新版本標記
