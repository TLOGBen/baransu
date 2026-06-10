task_id: TASK-distribution-02
group: distribution

Goal: |
  baransu 從 16 技能瘦身為 12 技能，以 2.0.0 破壞性改版出貨。
  本 task 對應驗收標準 C8 的 codex/ 部分：「codex/ 鏡像已重產為 12 技能」。
  Scope 明文：「codex/ 鏡像以 /codex-skill-transfer 重產」（In scope）。

Requirements: |
  REQ-005: 治理資產與出貨鏈
  描述：anti-patterns 容器與 verify-skills 驗證器就位，測試套件修剪後全綠，
  發行 metadata 同步至 12 技能與 2.0.0。
  （本 task 僅承接其中 codex/ 鏡像重產部分，見 Scenarios。）

Scenarios: |
  REQ-005 Scenario 5: codex/ 鏡像重產
  - Given: codex/ 為 CLAUDE.md 明訂的 canonical Codex output path，現含 16 技能
  - When: 以 /codex-skill-transfer 重產
  - Then: codex/ 反映 12 技能與更新後的 SKILL.md 內容，無 grade/triage/bridge/dev 目錄

Task: |
  TASK-distribution-02: codex/ 鏡像重產（task-distribution.md）
  前置群組：cut, reroute, contract, automation（codex 重產需鏡像最終態的 SKILL.md）
  需求追溯：REQ-005
  目標：codex/ 反映 12 技能最終態。
  驗收標準：
  - [ ] 以 /codex-skill-transfer 對更新後的 plugin 全量重產（原子動作；失敗即回報阻塞，不手補）
  - [ ] codex/ 技能目錄數 = 12；無 grade/triage/bridge/dev
  - [ ] 抽查 think/hunt 鏡像交接點與 plugins/ 版本一致
  步驟（重產）：
  - [ ] 清掉 codex/ 舊技能輸出 → 跑 /codex-skill-transfer → 抽查 parity

Design: |
  - 發行 metadata 區塊（design.md 系統架構表）：雙 manifest、CLAUDE.md、README、codex/
    全部同步至 12 技能；codex/ 重產。
  - 執行序：Wave 4「distribution manifests/CLAUDE/README/codex/bump」位於
    Wave 3 verify 之後，終點為「驗收: verify-skills + plugin validate + 套件全綠」。
  - 錯誤處理策略（design.md）：codex/ 重產失敗（/codex-skill-transfer 拒絕或部分輸出）：
    不手補 codex/ — 重產是原子動作，失敗就回報並把 codex/ 重產列為阻塞項。
  - 重產工具（已 Read 確認 transfer.py 用法）：
    - 調用：`python3 plugins/baransu/skills/codex-skill-transfer/scripts/transfer.py <source-dir> <output-dir>`
      （恰好 2 個位置參數；本 task 即 `plugins/baransu` → `codex`，相對 repo 根）
    - 模式自動偵測：source 含 `.claude-plugin/plugin.json` → plugin 模式（本 task 走此模式）
    - plugin 模式輸出樹：`<output>/.codex-plugin/plugin.json`、`<output>/skills/<name>/...`、
      `<output>/.codex-agents-templates/*.toml`、`<output>/.agents/plugins/marketplace.json`
    - 依賴 pyyaml（缺少時 exit 2）
    - exit 2：參數數錯誤、source 非目錄、source/output 路徑重疊（防 rmtree 資料毀損）、
      無法辨識的 source 形狀
    - 注意：`context: fork` 技能會被 skip，且 skip/manual-review 仍 exit 0、
      僅 stderr 出 `⚠️ N skipped, M need manual review` — 故 exit 0 不等於成功，
      必須以 stderr 警告 + parity 抽查共同判定；部分輸出即視為失敗（原子動作）

Test: |
  整合測試（test.md）：
  - codex/ 鏡像 parity | 涉及層：codex/ × 技能層 | 關鍵驗證點：codex/ 技能目錄數=12；
    鏡像內 think/hunt 交接點與 plugins/ 版本一致（抽查比對）
  關鍵邊界條件（test.md）：
  - codex/ 重產是原子動作：失敗即阻塞出貨（C8 不達成），不手補 — REQ-005

Constraints:
  - 原子動作：/codex-skill-transfer 失敗（拒絕、exit != 0）或部分輸出（stderr 出現
    skipped/manual-review 警告、目錄數不符）即回報阻塞，不得手補 codex/。
  - 重產前先清掉 codex/ 舊技能輸出（避免被裁技能的 16 技能時代殘檔留存）。
  - codex/ 是 CLAUDE.md 載明的 canonical Codex output path（commit f5ebe9b），
    輸出路徑不得另立。
  - 重產工具為 plugins/baransu/skills/codex-skill-transfer/scripts/transfer.py，
    plugin 模式：`python3 .../transfer.py plugins/baransu codex`（兩個位置參數，
    無 --help / 其他旗標；source 與 output 不得重疊，腳本會 refuse exit 2）。
  - 抽查 parity 三項：(1) codex/ 技能目錄數 = 12；(2) 無 grade/triage/bridge/dev 目錄；
    (3) think/hunt 鏡像的交接句與 plugins/ 新版一致 —「直接實作，依 _shared/tdd.md
    紀律自建紅綠 task list」語式（含 tdd.md §7 改道語式），不得殘留 baransu:dev 指向。
  - 前置依賴：cut/reroute/contract/automation 群組須已完成（鏡像對象是最終態 SKILL.md）；
    同群 TASK-distribution-01（manifest/CLAUDE.md 同步）亦應先完成，使鏡像帶入 2.0.0 metadata。
  - transfer.py 為一方向移植：不得反向修改 plugins/ 來源；不得修改 transfer.py 本身。

Files:
  - codex/ （整棵刪舊重產：.codex-plugin/plugin.json、skills/<12 技能>/、
    .codex-agents-templates/*.toml、.agents/plugins/marketplace.json）
