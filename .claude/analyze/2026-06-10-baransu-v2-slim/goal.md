# Goal

## 目標（Goal）
baransu 從 16 技能瘦身為 12 技能：裁除從未實際運轉的自癒 harness（grade/triage/bridge）與最少使用的 dev 及其全部附屬資產與發行面殘留，同時建立四個治理資產（Outcome Contract 四行頭、_shared/loop-contract.md、rules/anti-patterns.md、scripts/verify-skills.py），以 2.0.0 破壞性改版出貨 — 完成後安裝者看到的是 12 個常用技能、每個技能可被 /goal 式外部驗證者與 loop 驅動、結構完整性由一條命令證明。

## 驗收標準（Criteria）
- [ ] C1：`plugins/baransu/skills/` 僅含 12 個技能目錄＋ `_shared/`；grade/triage/bridge/dev 目錄、3 個 telemetry hooks（.py）、9 個 harness scripts、investigator-agent.md、_shared 三份遙測 schema 全部不存在。
- [ ] C2：以 word-boundary 模式掃描發行面（plugins/、tests/、CLAUDE.md、README.md、雙 manifest；排除 git 歷史），無任何指向被裁資產的功能性引用或行文殘留（upgrade/downgrade 等同形字樣不算）。
- [ ] C3：12 個存活 SKILL.md 開頭均有 Outcome Contract 四行（Outcome / Done when / Evidence / Output）；Done when 為可驗證條件，think/write/book 等允許事件型 done。
- [ ] C4：`_shared/loop-contract.md` 存在且含 review/execute/learn 的逐互動點 PAUSE 分類表；review/execute/learn 三技能含「單一內部介面＋Workflow 薄 adapter」契約（依官方 progressive-disclosure 慣例置於各技能 `references/orchestration-interface.md`，SKILL.md 留 ≤10 行指針段；同形 finding schema、depth 不變量逐模重述、Stage 0 模式釘死）；12 技能於 SKILL.md 契約區塊內帶雙軸自動化相容標注（不用非標準 frontmatter 欄位）。
- [ ] C5：`rules/anti-patterns.md` 存在，含自治條款（收斂不堆積、strip-provenance）與首批跨技能不變量。
- [ ] C6：`scripts/verify-skills.py` 存在並綠燈；其負向 fixture 測試證明違規 stub 會 exit 1。
- [ ] C7：修剪後測試套件全綠（含重生的 claude-md-skills-table baseline、修剪後的 test_tdd_trigger）；`/plugin validate` 通過。
- [ ] C8：雙 manifest description 為 12 技能、keywords/tags 無 dev/harness 殘留；CLAUDE.md 技能表 12 列；README 工作流鏈改道；codex/ 鏡像已重產為 12 技能；plugin.json version = 2.0.0。

## 範圍（Scope）

### 包含（In scope）
- 刪除面：4 技能目錄、hooks 3 檔（903 行）、scripts 9 檔（2,889 行）、investigator-agent.md、_shared 三份遙測 schema、約 28 個耦合測試檔。
- 改寫面：_shared/tdd.md（閘門文字併入、§8 去 dev、scope 行去 /dev）、agents/review-agent.md:71 錨點、think:175,381、hunt:230、ship 的 .claude/dev/ 通道、codex-skill-transfer 兩處行文、12 個 SKILL.md 契約頭與標注、CLAUDE.md、README、雙 manifest、測試修剪。
- 新增面：_shared/loop-contract.md、rules/anti-patterns.md、scripts/verify-skills.py、tests/scripts/verify-skills 負向 fixture 測試。
- codex/ 鏡像以 /codex-skill-transfer 重產。
- 升級註記與閘門語義降級寫入 release notes 草稿。

### 不包含（Out of scope）
- 事後遙測的任何替代品 — 要 loop 用官方 /loop、/goal、cron、Workflow；git 歷史是回收站。
- 版本 codegen（VERSION + regenerate）— 兩個 manifest 的 drift 面太小，驗證器檢查即可。
- /health 對應物 — 能力擴張另開 plan。
- deprecation stub / 別名 — 破壞性改版已拍板。
- TDAID 與五平面語義重寫 — execute 只加標注與薄 adapter 章節，不動 subagent 迴圈邏輯。
- 12 技能的 automation 深度整合（夜巡配方等）— 等真實 loop 需求出現再做。
- 對外發佈動作（git push、tag、marketplace 發佈）— 實作完成後由使用者透過 /ship 決定。
