task_id: TASK-governance-01
group: governance
source_spec: .claude/analyze/2026-06-10-baransu-v2-slim

Goal: |
  baransu v2 瘦身案的治理資產之一：建立 rules/anti-patterns.md 跨技能行為護欄容器。
  對應總目標驗收標準 C5：
  - C5：`rules/anti-patterns.md` 存在，含自治條款（收斂不堆積、strip-provenance）
    與首批跨技能不變量。
  範圍歸屬：本任務屬「新增面」（_shared/loop-contract.md、rules/anti-patterns.md、
  scripts/verify-skills.py 三項治理資產之一）。

Requirements: |
  REQ-005: 治理資產與出貨鏈
  描述：anti-patterns 容器與 verify-skills 驗證器就位，測試套件修剪後全綠，
  發行 metadata 同步至 12 技能與 2.0.0。
  （本任務只承接 REQ-005 中的 anti-patterns 容器部分；驗證器、測試修剪、
  發行 metadata、codex/ 重產分屬 verify 與 distribution 群組任務。）

Scenarios: |
  REQ-005 Scenario 1: anti-patterns 容器
  - Given: rules/anti-patterns.md 新建
  - When: 檢視其內容
  - Then: 檔頭含自治條款（收斂不堆積：新條目須折入既有原則；
    strip-provenance：規則不帶事故敘事）
  - And: 首批條目來自 CLAUDE.md Non-obvious Invariants 中跨技能成立者
    （逐條評估，技能專屬者留在原處）
  （REQ-005 Scenario 2-5 涉及 verify-skills.py、測試修剪、發行 metadata、
  codex/ 鏡像，與本任務無關，不納入。）

Task: |
  ## TASK-governance-01: rules/anti-patterns.md
  前置群組：cut（Wave 1 刪除面）
  需求追溯：REQ-005
  目標：跨技能行為護欄容器就位，含自治條款與首批條目。

  驗收標準：
  - [ ] `plugins/baransu/rules/anti-patterns.md` 存在；檔頭自治條款：
        收斂不堆積（新條目須先找到既有原則折入，禁近義詞追加）
        ＋ strip-provenance（規則靠防止什麼掙位置，不帶事故敘事與來源規模數字）
  - [ ] 首批條目：自 CLAUDE.md Non-obvious Invariants 逐條評估 —
        跨技能成立者入容器（例：subagent depth=1 禁巢狀 skill 呼叫；
        Read-before-write），技能專屬者（如 ship 的 -D 旗標、DESIGN.md 大小寫）
        留在原處並於容器註明分層原則
  - [ ] 表格三欄式：慣性 / 錯誤示範 / 正確做法
  - [ ] CLAUDE.md 增一行指向容器（不搬移技能專屬不變量）

  步驟（撰寫）：
  - [ ] Read CLAUDE.md Non-obvious Invariants 全節，逐條分類（跨技能 / 技能專屬）
  - [ ] 撰寫容器；首批 5-8 條，寧缺勿濫
  - [ ] Edit CLAUDE.md 加指向行

Design: |
  波次定位（執行序）：
  - Wave 1: cut 刪除面 → Wave 2: governance anti-patterns（與 reroute /
    contract / automation 平行，互不依賴）→ Wave 3: verify → Wave 4: distribution。
  - 刪除先行的理由：所有後續編輯的殘留掃描以「刪除後」狀態為基準。

  官方 best practices 對齊（2026-06-10 官方文件查核結果，與本任務相關者）：
  - 自訂 frontmatter 欄位：官方建議僅用標準欄位（跨平台相容；非標準欄位被忽略）。
  - 500 行上限：官方明訂 SKILL.md 本文 <500 行；新增內容一律走 references/ 一層深。
  - references 一層深：所有新 reference 檔直接從 SKILL.md 連結，禁巢狀
    （官方警告巢狀導致 partial read）。
  - evaluation-first：與官方「Build evaluations BEFORE writing extensive
    documentation」一致。
  - headless/cron 場景官方未覆蓋 → 插件層慣例需自我聲明非官方標準。
  （anti-patterns 容器屬文件層新資產，發行面五區塊表未含 rules/ 目錄 —
  此為新建目錄 `plugins/baransu/rules/`。）

Test: |
  整合測試策略（與本任務直接相關的一列）：
  | 測試目標 | 涉及層 | 關鍵驗證點 |
  | anti-patterns 容器就位 | rules × 文件層 | rules/anti-patterns.md 存在；
    自治條款（收斂不堆積、strip-provenance）明文；首批 5-8 條來自
    CLAUDE.md Non-obvious Invariants 逐條評估；三欄表完整 |
  注意：本任務無自動化測試檔；驗證為檔案存在性與內容結構檢視。
  後續 Wave 4 distribution 會大改 CLAUDE.md，相關 baseline 測試
  （test-claude-md-skills-table.sh）的重生屬 verify/distribution 群組，
  本任務不觸碰。

Constraints: |
  - 首批 5-8 條，寧缺勿濫 — 不為湊數而收錄。
  - 分層判準（跨技能 vs 技能專屬）：
    * 跨技能成立者入容器 — 例：subagent depth=1 禁巢狀 skill 呼叫、
      Read-before-write。
    * 技能專屬者留在原處 — 例：ship 的 `-D` 旗標、`DESIGN.md` vs `design.md`
      大小寫語義；容器內須註明此分層原則。
  - 自治條款兩條必須寫在檔頭：
    * 收斂不堆積：新條目須先找到既有原則折入，禁近義詞追加。
    * strip-provenance：規則靠「防止什麼」掙位置，不帶事故敘事與來源規模數字。
  - 條目格式：三欄表（慣性 / 錯誤示範 / 正確做法）。
  - CLAUDE.md 只加一行指向容器，不搬移技能專屬不變量、不刪原節。
  - 波次衝突面控制：Wave 4 distribution 將對 CLAUDE.md 做大改
    （技能表 12 列等）；本任務僅加一行指向，刻意縮小與 distribution
    波次的 CLAUDE.md 衝突面。
  - 前置群組 cut 須已完成（Wave 1 刪除後狀態為編輯基準）。
  - 不得修改 `.claude/analyze/` spec 目錄下任何文件。

Files: |
  新增：
  - plugins/baransu/rules/anti-patterns.md（新建 rules/ 目錄）
  修改：
  - CLAUDE.md（repo 根；僅增一行指向容器，不搬移 Non-obvious Invariants）
