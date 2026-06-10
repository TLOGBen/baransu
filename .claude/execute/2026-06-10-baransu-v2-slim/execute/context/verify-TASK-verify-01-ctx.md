# Context: TASK-verify-01（scripts/verify-skills.py＋負向 fixture）

```yaml
Goal: |
  baransu 16→12 技能瘦身的治理資產之一：scripts/verify-skills.py，
  讓「結構完整性由一條命令證明」。對應 goal.md 驗收標準：
  - C1：plugins/baransu/skills/ 僅含 12 個技能目錄＋ _shared/；被裁資產全部不存在
  - C2：word-boundary 掃描發行面（plugins/、tests/、CLAUDE.md、README.md、雙 manifest；
    排除 git 歷史）無被裁資產的功能性引用（upgrade/downgrade 等同形字樣不算）
  - C3：12 個存活 SKILL.md 開頭均有 Outcome Contract 四行（Outcome / Done when /
    Evidence / Output）；Done when 可驗證，think/write/book 允許事件型 done
  - C6：scripts/verify-skills.py 存在並綠燈；其負向 fixture 測試證明違規 stub 會 exit 1
  範圍（In scope）新增面明列：scripts/verify-skills.py、tests/scripts/ 的
  verify-skills 負向 fixture 測試。
  Out of scope：版本 codegen（VERSION + regenerate）不做 — 兩 manifest 的 drift 面
  太小，驗證器檢查即可；/health 對應物不做。

Requirements: |
  REQ-005: 治理資產與出貨鏈
  描述：anti-patterns 容器與 verify-skills 驗證器就位，測試套件修剪後全綠，
  發行 metadata 同步至 12 技能與 2.0.0。
  （本 task 對應其中「驗證器與負向 fixture」部分；anti-patterns 屬 governance 群、
  測試修剪屬 TASK-verify-02、metadata 屬 distribution 群。）

Scenarios: |
  REQ-005 Scenario 2: 驗證器與負向 fixture
  - Given scripts/verify-skills.py 新建
  - When 對倉庫執行
  - Then 檢查通過：12 技能 frontmatter 解析（容納兩種風格）、SKILL.md 引用的
    references/ 檔案存在、被裁名稱零功能殘留（掃描 glob 與排除規則寫死在腳本內）、
    雙 manifest 版本一致、契約四行齊備且 Done-when 非空 — exit 0
  - And 對負向 fixture（一份違規 SKILL stub）執行時 exit 1，
    該行為由 tests/ 內的 fixture 測試證明

  關聯 REQ-003 Scenario 3: frontmatter 相容（驗證器必須容納的輸入面）
  - Given 倉內現有兩種 frontmatter 風格（think 極簡式 vs read/learn 的
    Use When/Do/Trigger On 式）
  - When verify-skills.py 檢查契約
  - Then 兩種風格均通過；契約四行位於 SKILL.md 正文開頭區，不強改 frontmatter 結構

Task: |
  TASK-verify-01: scripts/verify-skills.py＋負向 fixture（task-verify.md）
  群組前置：reroute, contract, automation, governance, distribution
  （baseline 重生需在 CLAUDE.md 表更新後 — 該時序屬 TASK-verify-02）
  需求追溯：REQ-005
  目標：repo 根 scripts/（新建目錄）下的結構驗證器，一條命令證明 C1/C2/C3/C6。
  驗收標準：
  - [ ] 檢查項：技能目錄數=12；frontmatter 可解析（容納 think 極簡式與 read/learn
    完整式兩風格）＋官方約束（name ≤64 字元小寫連字符、description 非空 ≤1024、
    第三人稱啟發式）；SKILL.md 內 references/ 引用檔存在且一層深
    （無 references → references 巢狀）；被裁名稱零功能殘留（word-boundary，
    掃描 glob＝plugins/**/*.{md,py,json} + tests + CLAUDE.md + README.md，
    排除規則內嵌：同形字樣白名單、git 歷史不掃）；雙 manifest version 一致；
    Outcome Contract 四行齊備且 Done-when 非空；契約區塊內 automation 標注存在
  - [ ] advisory 輸出（不影響 exit code）：SKILL.md 本文 >500 行清單
    （官方上限；execute 為既有超限戶，列出供後續瘦身）
  - [ ] exit 語義：0=pass、1=violation（收集後一次輸出全部）、2=structural（檔案無法解析）
  - [ ] tests/scripts/test_verify_skills.py：正向（現倉 exit 0）＋負向 fixture
    （tests/scripts/fixtures/verify-skills/bad-skill/SKILL.md 缺契約行 → exit 1）
  - [ ] 對當前倉執行綠燈
  步驟（TDD：先寫測試）：
  - [ ] 寫 test_verify_skills.py 與 bad-skill fixture（紅）
  - [ ] 實作 verify-skills.py（綠）；標準函式庫 only

Design: |
  驗證器位置決策（design.md）：
  verify-skills.py 放 repo 根的 scripts/（dev/CI 工具），不放 plugins/baransu/scripts/
  （後者會被打包發行）。理由：驗證器是維護期工具，消費者是 CI 與維護者，不是安裝端
  使用者；放發行面只會增加安裝體積。這也讓「plugins/baransu/scripts/ 整個目錄刪空」
  成為乾淨的驗收條件。注意 repo 根 scripts/ 現不存在，須新建。

  verify-skills.py 檢查項 schema（design.md 資料模型表）：
  frontmatter 解析（兩風格）＋官方細目（name ≤64 小寫連字符、description 非空 ≤1024、
  第三人稱啟發式）、引用存在且一層深、殘留掃描（glob＋排除規則內嵌）、版本一致、
  契約四行＋第五行 Automation 標注、500 行 advisory；exit 0/1/2
  （2=結構錯誤，沿用倉內 gate 慣例）。depth 不變量的文字層計數（每 reference 檔 ≥2）
  可納入；行為層違反（agent 實際呼叫 skill）不納自動驗證，
  留給 spec review 與 execute 既有測試。

  官方 best practices 對齊（design.md，2026-06-10 查核）：
  - frontmatter 機器檢查：name ≤64 小寫連字符、description 非空 ≤1024、第三人稱
    — 納入 verify-skills.py
  - 500 行上限：官方明訂 SKILL.md 本文 <500 行 → verify-skills.py 對超限檔出
    advisory 清單（execute 為既有超限戶）
  - references 一層深：所有 reference 檔直接從 SKILL.md 連結，禁巢狀
    （官方警告巢狀導致 partial read）
  - 雙軸 automation 標注放 SKILL.md 契約區塊第五行，不放 frontmatter
    （官方建議僅用標準 frontmatter 欄位）
  - evaluation-first：verify-skills.py 採測試先行（負向 fixture 先紅）

  錯誤處理策略（design.md）：
  verify-skills.py 單項失敗收集後一次輸出全部違規（不 fail-fast），exit 1；
  無法解析的檔案 exit 2 並指名路徑。

  Outcome Contract 四行定式（驗證對象的結構，design.md 資料模型）：
  Outcome（一句）/ Done when（可驗證或事件型）/ Evidence（判定依據）/
  Output（產物形態）；第五行 - **Automation**: ultracode={...}, loop={...}
  （已由 automation 群落盤，格式見 tests/skills/test-automation-annotation.sh 檔頭）。

Test: |
  E2E（test.md）：
  - 結構完整性一條命令：python3 scripts/verify-skills.py → exit 0，輸出 12 技能
    逐項通過（含契約四行、第五行 Automation 標注、官方 frontmatter 細目）
    — 對應 C1, C2, C3, C4, C6
  - 驗證器可證偽：對負向 fixture stub 執行 → exit 1，指名違規項 — 對應 C6
  整合（test.md）：
  - repo scripts/ 新建：repo 根 scripts/ 存在、verify-skills.py 可直接以 python3
    執行；plugins/baransu/scripts/ 不存在
  - Outcome Contract 齊備：verify-skills.py 逐檔斷言四行非空＋Done-when 非空；
    負向 fixture 缺行 → exit 1
  關鍵邊界條件（test.md）：
  - 契約頭對兩種 frontmatter 風格（think 極簡式 / read-learn 完整式）都要通過解析；
    官方細目納入檢查
  - 事件型 Done when（think/write/book）：驗證器只查四行齊備與非空，
    語義品質由 spec review 把關
  - 自動化標注覆蓋：12 檔契約區塊第五行均含「Automation:」且值非空
    （缺漏 → verify-skills exit 1）
  - depth 文字層計數（每 orchestration-interface.md 檔 depth 語句 ≥2）可自動；
    行為層不納入
  - SKILL.md >500 行為 advisory 清單，不影響 exit code
  - word-boundary 掃描必須排除同形誤報；分類結果落盤為清單，
    不得以「grep 無輸出」單獨作為 C2 證據

  與既有結構測試的互補關係（contract/automation 群已落盤的 gate tests）：
  - tests/skills/test-outcome-contract-verifiable.sh：八個可驗證型技能契約四行
    「排序＋插入位置」（frontmatter 後、第一個 H2 前、四行有序非空）
  - tests/skills/test-automation-annotation.sh：第五行 Automation 標注格式與
    分級對表（含 hunt/analyze 的 Workflow hint）
  - tests/skills/test-orchestration-interface.sh：三技能 orchestration-interface.md
    存在、depth 語句 ≥2、一層深連結、指針段 ≤10 行
  - workspace 內 test-contract-02.sh：事件型四技能契約語義斷言
  互補分工：這些 .sh 驗「排序/位置/格式細節」，verify-skills.py 驗「全倉齊備性」
  （四行齊備非空＋目錄數＋殘留＋版本一致，一條命令）。contract-01/02 review 備註
  已明文：gate tests 屬補充非重複，最終去留路由給 verify 群決定 —
  本 task 可保留它們，不必合併。
  另：tests/skills/test-write-skill.sh、test-book-skill-stage0.sh 為既有技能測試，
  與本 task 無涉（book-stage0 現紅為 pre-existing，與本 task 無關）。

Constraints: |
  - repo 根 scripts/ 為新建目錄：dev/CI 工具，不入 packaging；
    禁放 plugins/baransu/scripts/（該目錄須保持不存在）。
  - TDD 先紅：tests/scripts/test_verify_skills.py 與
    tests/scripts/fixtures/verify-skills/bad-skill/SKILL.md（缺契約行）先寫先紅，
    再實作 verify-skills.py 轉綠。
  - 標準函式庫 only（無第三方依賴；可直接 python3 執行）。
  - 檢查項全列（缺一不可）：
    1. 技能目錄數 = 12
    2. frontmatter 兩風格（think 極簡式 / read-learn 完整式）皆可解析
       ＋官方細目：name ≤64 字元小寫連字符、description 非空 ≤1024、第三人稱啟發式
    3. SKILL.md 引用的 references/ 檔存在且一層深（references 內不得再巢狀 references）
    4. 被裁名稱（grade/triage/bridge/dev）word-boundary 零功能殘留：
       掃描 glob＝plugins/**/*.{md,py,json} + tests + CLAUDE.md + README.md，
       排除規則內嵌於腳本（不外部設定檔）；git 歷史不掃
    5. 雙 manifest（plugins/baransu/.claude-plugin/plugin.json 與
       .claude-plugin/marketplace.json）version 一致
    6. Outcome Contract 四行齊備且 Done-when 非空
    7. 契約區塊第五行 Automation 標注存在
  - 殘留掃描已知白名單（residue-scan-classification.md 與兩輪 review 已落盤，
    腳本內嵌排除規則須涵蓋）：
    * design preset HTML 樣本字樣：紙-preset 與 google-design-preset 的
      design-cores/dashboard.html 樣本表列 /dev /grade /triage /bridge
      （裝飾性 sample data）；gallery.html:5 的「/dev review」字樣
    * codex-skill-transfer/references/agent-mapping.md:30 的 /triage
      investigator-agent 例句
    * codex-skill-transfer transfer.py 註解歷史例（transfer.py:422 grade/CRON.md）
    * langchain.dev 外域 URL（book/evals/evals.json:82 blog.langchain.dev）
    * upgrade/downgrade（及 gradient/bridging）同形字樣
    * shell 慣用 2>/dev/null 之類非技能引用
  - tdd.md 等保留資產的功能性引用（如 _shared/tdd.md 改道句 7 處）為合法，不得誤判。
  - exit 語義：0=pass、1=violation、2=structural（檔案無法解析，指名路徑）；
    違規收集後一次輸出全部，不 fail-fast。
  - 500 行 advisory：SKILL.md 本文 >500 行僅列清單（execute 為既有超限戶），
    不影響 exit code。
  - 事件型 Done when 不做語義品質判定（只查齊備非空）。
  - 不修改 12 個 SKILL.md 本身 — 驗證器是唯讀檢查；若現倉跑出真實違規，
    先判定根因，不得為過閘放寬檢查。

Files:
  - scripts/verify-skills.py            # 新增（repo 根 scripts/ 新建目錄）
  - tests/scripts/test_verify_skills.py # 新增（pytest；正向 exit 0＋負向 exit 1）
  - tests/scripts/fixtures/verify-skills/bad-skill/SKILL.md # 新增（違規 stub：缺契約行）
```
