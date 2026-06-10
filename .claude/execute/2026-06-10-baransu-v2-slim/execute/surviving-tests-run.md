# 存活測試套件執行記錄（TASK-verify-02）

- 日期：2026-06-10
- 執行位置：`/home/vakarve/projects/baransu/.claude/worktrees/learn-waza-research`
- 對應驗收：REQ-005 / C7（測試套件修剪後全綠）
- 執行方式：逐一 `bash tests/integration/*.sh`、`bash tests/skills/*.sh`、
  `bash tests/scripts/*.sh`、`python3 -m pytest tests/scripts/`；無 skip 掩蓋。

## 修剪內容（本 task）

| 項目 | 變更 |
|---|---|
| `tests/integration/claude-md-skills-baseline.txt` | 重生為 12 技能列（自當前 CLAUDE.md 表 `grep -E '^\| \`/'` 提取；distribution-01 已先完成表同步，時序滿足） |
| `tests/integration/test-claude-md-skills-table.sh` | 「恰 14 列」斷言改 12；B3 改驗 dev/grade/triage/bridge 缺席；B4–B6 改驗 12 存活技能與重生 baseline 同步 |
| `tests/scripts/test_tdd_trigger.sh` | 移除 dev 觸發點斷言（§8 cites dev/SKILL.md、整段 Check 2 /dev SKILL.md citation）；保留 impl-agent/review-agent 斷言；檢查項重編號 [1]–[5] |
| `tests/scripts/fixtures/tdd-trigger/`（prompt.md / acceptance-spec.md / check_acceptance.sh） | 移除 `/baransu:dev` 觸發點文字，改指 `/execute` impl-agent loop 與 tdd.md §7 直接實作路徑；lure 與 anti-leak 內容不變 |

Red 閘證據：修剪前兩測試均紅（exit 1）——table 測試紅因 = 表已是 12 列但斷言仍是 14 列＋grade/triage/bridge/dev；
tdd_trigger 紅因 = tdd.md §8 已無 dev 引用、`skills/dev/SKILL.md` 已不存在。紅因皆為「裁併後現實 vs 舊斷言」，非新行為缺失。

## 執行結果

| # | 測試 | 指令 | 結果 | 摘要 |
|---|---|---|---|---|
| 1 | claude-md-skills-table | `bash tests/integration/test-claude-md-skills-table.sh` | 綠（exit 0） | 43/43 passed（12 列、4 裁除技能缺席、12 存活技能與 baseline 同步） |
| 2 | distribution-metadata | `bash tests/integration/test-distribution-metadata.sh` | 綠（exit 0） | 11 passed, 0 failed |
| 3 | automation-annotation | `bash tests/skills/test-automation-annotation.sh` | 綠（exit 0） | all 12 skills carry a correctly graded Automation contract line |
| 4 | book-skill-stage0 | `bash tests/skills/test-book-skill-stage0.sh` | 紅（exit 1）— pre-existing，非裁併破壞 | 見下方「pre-existing 紅燈」§2 |
| 5 | orchestration-interface | `bash tests/skills/test-orchestration-interface.sh` | 綠（exit 0） | 15 passed, 0 failed |
| 6 | outcome-contract-verifiable | `bash tests/skills/test-outcome-contract-verifiable.sh` | 綠（exit 0） | all 8 verifiable skills carry a well-formed Outcome Contract |
| 7 | write-skill | `bash tests/skills/test-write-skill.sh` | 綠（exit 0） | All structural assertions passed |
| 8 | install-deps-format | `bash tests/scripts/test-install-deps-format.sh` | 綠（exit 0） | 10 passed, 0 failed |
| 9 | tdd_trigger | `bash tests/scripts/test_tdd_trigger.sh` | 綠（exit 0） | ALL CHECKS PASSED（修剪後 [1]–[5]） |
| 10 | pytest tests/scripts/ | `python3 -m pytest tests/scripts/` | 12 passed, 2 failed | 2 紅皆為已知 pre-existing（test_check_design.py，見下方 §1）；其餘全綠、無 skip |
| 11 | pytest collect 健康檢查 | `python3 -m pytest tests/scripts/ --collect-only -q` | 綠 | 14 tests collected, 無 import error |
| 12 | test_verify_skills.py | — | 由 verify-01 交付 | verify-01 平行施工中（執行時 `tests/scripts/test_verify_skills.py` 尚未存在）；其結果由 verify-01 自行落盤 |

## Pre-existing 紅燈（記錄，不修不掩蓋）

### 1. `tests/scripts/test_check_design.py` 兩項（ctx 已知）

- `TestSlideCoresHtmlLint::test_all_nine_real_slide_cores_pass` — fixture dir 指向主 repo 寫死路徑，目錄缺失。
- `TestExistingRulesRegression::test_kami_preset_directory_regression` — 主 repo `紙-preset` untracked artifacts 漂移，violation 計數與 baseline 不符。
- 根因類別：主 repo 路徑寫死＋untracked artifacts 漂移（環境性）。ctx 明文列為 pre-existing，記錄不修。

### 2. `tests/skills/test-book-skill-stage0.sh`（本次執行新判定的 pre-existing）

- 症狀：T1–T5 失敗（§0 缺 `--format` guard / default=html / `$FORMAT`）。
- 根因判定（裁併破壞 vs 既有紅燈）：**既有紅燈**，證據：
  1. 測試寫死主 repo 絕對路徑 `SKILL_MD="/home/vakarve/projects/baransu/plugins/baransu/skills/book/SKILL.md"`（與 test_check_design.py 同類的主 repo 路徑寫死問題）。
  2. 在主 repo HEAD（b09b093，任何 slim commit 之前）原樣執行即紅（exit 1，同組 T 失敗）。
  3. 主 repo 與 worktree 的 book/SKILL.md 皆只剩一個 `### 0.` 標題＝`Fact-Verification Principle #0`；`### 0. --format 旗標解析` 標題在 b09b093（feat(design,book) Kami 對齊）之前已不存在，awk 抽取段落落空。
  4. 本波次對 book/SKILL.md 的 diff 僅 +8 行（Outcome Contract / Automation 標頭），未觸及 §0 結構。
- 處置：依約束「不得為過閘改測試斷言語義」，不修不掩蓋，落盤記錄。建議後續波次另開 task 處理（路徑改 worktree-relative＋斷言對齊現行 SKILL.md 結構）。

## 範圍外（依派遣指示）

- `scripts/verify-skills.py` 與 `tests/scripts/test_verify_skills.py`：verify-01 平行施工，本 task 未觸碰；其執行結果由 verify-01 落盤。
- 已刪除的 ~28 個耦合測試檔（含既有紅燈 test-settings-registration.sh）由 cut 群處理；其刪除不記為「修復」。
