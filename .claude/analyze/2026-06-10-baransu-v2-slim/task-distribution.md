# Tasks: distribution（發行 metadata＋codex 重產＋版本）
**前置群組**：cut, reroute, contract, automation（codex 重產需鏡像最終態的 SKILL.md）

## TASK-distribution-01: manifests／CLAUDE.md／README 同步

**需求追溯**：REQ-001, REQ-005
**目標**：發行 metadata 全面反映 12 技能與新治理資產。
**驗收標準**：
- [ ] plugin.json：description 「sixteen governance skills」→ twelve（敘述同步改寫，去 harness 描述）；keywords 去 dev/tdd/harness 殘留；version = 2.0.0
- [ ] marketplace.json：description/tags 同步；版本欄位與 plugin.json 一致
- [ ] CLAUDE.md：技能表 12 列（去 grade/triage/bridge/dev 四列）；Layout 區塊 skills/agents 清單更新；Non-obvious Invariants 中 harness/dev 專屬條目移除或改寫；「self-healing harness」相關敘述全面修訂
- [ ] README：技能清單與兩條工作流鏈（/think→/dev→/ship、/hunt→/dev）改道為直接實作＋tdd.md
- [ ] release notes 草稿（.claude/execute/ 工件）：含 16→12 清單、閘門語義降級聲明、settings.json 升級註記

### 步驟

#### 同步
- [ ] 逐檔 Read → Edit；CLAUDE.md 表改完即通知 verify 群可重生 baseline
- [ ] `claude plugin validate`（或 /plugin validate）通過

## TASK-distribution-02: codex/ 鏡像重產

**需求追溯**：REQ-005
**目標**：codex/ 反映 12 技能最終態。
**驗收標準**：
- [ ] 以 /codex-skill-transfer 對更新後的 plugin 全量重產（原子動作；失敗即回報阻塞，不手補）
- [ ] codex/ 技能目錄數 = 12；無 grade/triage/bridge/dev
- [ ] 抽查 think/hunt 鏡像交接點與 plugins/ 版本一致

### 步驟

#### 重產
- [ ] 清掉 codex/ 舊技能輸出 → 跑 /codex-skill-transfer → 抽查 parity
