# Tasks: verify（驗證器＋測試修剪）
**前置群組**：reroute, contract, automation, governance, distribution（baseline 重生需在 CLAUDE.md 表更新後）

## TASK-verify-01: scripts/verify-skills.py＋負向 fixture

**需求追溯**：REQ-005
**目標**：repo 根 scripts/（新建目錄）下的結構驗證器，一條命令證明 C1/C2/C3/C6。
**驗收標準**：
- [ ] 檢查項：技能目錄數=12；frontmatter 可解析（容納 think 極簡式與 read/learn 完整式兩風格）＋官方約束（name ≤64 字元小寫連字符、description 非空 ≤1024、第三人稱啟發式）；SKILL.md 內 references/ 引用檔存在且一層深（無 references → references 巢狀）；被裁名稱零功能殘留（word-boundary，掃描 glob＝plugins/**/*.{md,py,json} + tests + CLAUDE.md + README.md，排除規則內嵌：同形字樣白名單、git 歷史不掃）；雙 manifest version 一致；Outcome Contract 四行齊備且 Done-when 非空；契約區塊內 automation 標注存在
- [ ] advisory 輸出（不影響 exit code）：SKILL.md 本文 >500 行清單（官方上限；execute 為既有超限戶，列出供後續瘦身）
- [ ] exit 語義：0=pass、1=violation（收集後一次輸出全部）、2=structural（檔案無法解析）
- [ ] `tests/scripts/test_verify_skills.py`：正向（現倉 exit 0）＋負向 fixture（tests/scripts/fixtures/verify-skills/bad-skill/SKILL.md 缺契約行 → exit 1）
- [ ] 對當前倉執行綠燈

### 步驟

#### 實作（TDD：先寫測試）
- [ ] 寫 test_verify_skills.py 與 bad-skill fixture（紅）
- [ ] 實作 verify-skills.py（綠）；標準函式庫 only

## TASK-verify-02: 存活測試修剪

**需求追溯**：REQ-005
**目標**：claude-md-skills-table baseline 重生、tdd_trigger 修剪，套件全綠。
**驗收標準**：
- [ ] tests/integration/claude-md-skills-baseline.txt 重生為 12 技能列；test-claude-md-skills-table.sh 的「恰 14 列」斷言改 12 並通過
- [ ] test_tdd_trigger.sh 與 fixtures：移除 dev 觸發點斷言，保留 impl-agent/review-agent 斷言並通過
- [ ] 存活套件清單落盤（test.md E2E 表的執行記錄）：6 個 .sh/.py ＋ 新增 test_verify_skills.py 全綠

### 步驟

#### 修剪
- [ ] 待 distribution 群改完 CLAUDE.md 表後重生 baseline（與 distribution 協調：baseline 重生排在 CLAUDE.md 表更新後 — 若先跑，驗收時重跑一次）
- [ ] Edit test_tdd_trigger.sh 與 fixtures
- [ ] 逐一執行存活測試，記錄輸出
