Goal: |
  baransu 從 16 技能瘦身為 12 技能（裁除 grade/triage/bridge/dev 及附屬資產），以 2.0.0 出貨。
  與本 task 直接相關的驗收標準：
  - C7：修剪後測試套件全綠（含重生的 claude-md-skills-table baseline、修剪後的 test_tdd_trigger）。
  - 改寫面包含「測試修剪」；範圍含刪除約 28 個耦合測試檔後的存活套件驗證。

Requirements: |
  REQ-005: 治理資產與出貨鏈
  描述：anti-patterns 容器與 verify-skills 驗證器就位，測試套件修剪後全綠，發行 metadata 同步至 12 技能與 2.0.0。
  （本 task 對應其中「測試套件修剪後全綠」部分。）

Scenarios: |
  REQ-005 Scenario 3: 測試修剪
  - Given 現有 37 個測試檔中約 28 個耦合被裁面（含今天就紅的 test-settings-registration.sh）
  - When 修剪完成
  - Then 刪除清單內的測試檔不存在；test-claude-md-skills-table.sh 的 baseline 重生為 12 技能列；
    test_tdd_trigger.sh 與其 fixtures 修剪 dev 觸發點、保留 impl-agent/review-agent 斷言
  - And 修剪後套件（約 6-8 檔）一次跑全綠

Task: |
  TASK-verify-02: 存活測試修剪（task-verify.md）
  需求追溯：REQ-005
  前置群組：reroute, contract, automation, governance, distribution（baseline 重生需在 CLAUDE.md 表更新後）
  目標：claude-md-skills-table baseline 重生、tdd_trigger 修剪，套件全綠。
  驗收標準：
  - [ ] tests/integration/claude-md-skills-baseline.txt 重生為 12 技能列；
        test-claude-md-skills-table.sh 的「恰 14 列」斷言改 12 並通過
  - [ ] test_tdd_trigger.sh 與 fixtures：移除 dev 觸發點斷言，保留 impl-agent/review-agent 斷言並通過
  - [ ] 存活套件清單落盤（test.md E2E 表的執行記錄）：6 個 .sh/.py ＋ 新增 test_verify_skills.py 全綠
  步驟（修剪）：
  - [ ] 待 distribution 群改完 CLAUDE.md 表後重生 baseline
        （與 distribution 協調：baseline 重生排在 CLAUDE.md 表更新後 — 若先跑，驗收時重跑一次）
  - [ ] Edit test_tdd_trigger.sh 與 fixtures
  - [ ] 逐一執行存活測試，記錄輸出
  前置狀態（派遣時提供）：CLAUDE.md 技能表已由 distribution-01 改為 12 列 — baseline 重生時序已滿足，可直接重生。

Design: |
  - 測試層 tests/（原 37 檔）：刪 ~28、改 2（baseline 重生、tdd_trigger 修剪）、增 1（verify-skills 負向 fixture 測試）、留 ~6。
  - Wave 順序：本 task 屬 Wave 3 verify（驗證器＋測試修剪），位於 Wave 2 各群之後、Wave 4 distribution 驗收之前；
    但 baseline 重生有明文時序依賴：distribution-01 完成 CLAUDE.md 表同步 → verify-02 重生 baseline → 重跑該測試（不可倒置）。
  - 錯誤處理策略：測試修剪後若存活測試出現非預期紅燈，先判定是裁併破壞還是既有紅燈
    （test-settings-registration 是已知既有紅燈，刪除即可），不得為過閘而改測試斷言語義。

Test: |
  E2E 表相關場景：
  - 「修剪後套件」：逐一執行存活測試（bash tests/.../*.sh、pytest tests/scripts/）→ 全綠，無 skip 掩蓋；存活清單落盤（C7）。
  - 「pytest import 健康檢查」：python3 -m pytest tests/scripts/ --collect-only → 無 import error；conftest/fixture 無殘缺（C7）。
  整合測試相關：
  - 「CLAUDE.md 表 ↔ baseline」：test-claude-md-skills-table.sh 以重生後 baseline 通過；表 12 列。
  - 「baseline 重生序列」：distribution-01 → verify-02 重生 → 重跑測試，時序依賴明文，不可倒置。
  - 「tdd.md 整併後消費者」：impl-agent/review-agent 對 tdd.md 的既有引用行不變；test_tdd_trigger.sh 修剪後通過。
  存活套件清單落盤要求（本波次實際範圍）：
  - 含本波次新增的四個 tests/skills/*.sh、test-distribution-metadata.sh、test_verify_skills.py，
    連同其餘存活 .sh/.py 一併逐一執行並記錄輸出，作為 test.md E2E 表的執行記錄。

Constraints: |
  - 不得為過閘改測試斷言語義：修剪是反映裁併後現實（dev/harness 已裁），非遷就紅燈；
    存活測試出現非預期紅燈須先判定根因（既有 vs 裁併破壞）。
  - test-settings-registration.sh 是既有紅燈（斷言對象即被裁 hooks），刪除它不得記為「修復」。
  - 全綠標準：無 skip 掩蓋；存活清單必須落盤，不得只口頭宣稱。
  - 已知環境性紅燈（pre-existing，非裁併破壞 — 記錄不修）：test_check_design.py 兩項
    （主 repo 路徑寫死＋untracked artifacts 漂移）。
  - baseline 重生時序：必須在 CLAUDE.md 表更新後（前置狀態已滿足）；若曾先跑，驗收時重跑一次。
  - 不修改 Analyze spec 目錄下任何文件。

Files: |
  - tests/integration/claude-md-skills-baseline.txt（重生為 12 技能列）
  - tests/integration/test-claude-md-skills-table.sh（「恰 14 列」斷言改 12，執行通過）
  - tests/scripts/test_tdd_trigger.sh 與其 fixtures（移除 dev 觸發點斷言，保留 impl-agent/review-agent 斷言，執行通過）
  - 存活套件執行記錄落盤（位置依 execute 工作目錄慣例；內容涵蓋四個 tests/skills/*.sh、
    test-distribution-metadata.sh、test_verify_skills.py 及其餘存活測試）
