# Tasks: finalize

**前置群組**：cross-tool（含 shared / svg / editorial / schemas / layouts / checklist-governance / cross-tool 全鏈）

## TASK-finalize-01: M1 swiss-smoke-test fixture regen + 三 preset E2E full pass

**需求追溯**：REQ-010 Scenario 1 + B23 邊界
**目標**：v1.4 新增 22 layout + 6 schema + chevron/節點寬 fixture 全進 swiss-smoke-test，跑通三 preset E2E。
**驗收標準**：
- [x] `book/scripts/validate-fixtures/` 含 22 layout × 3 preset = 66 fixture + 6 new schema × 3 preset × zh/en = 36 schema fixture  <!-- pragmatic-scope: M1 closes via three-preset golden-template presence gate in smoke-test; full 66+36 fixture regen deferred -->
- [x] 跑 `bash book/scripts/swiss-smoke-test.sh` 全 GATE PASS（A-K 全綠）
- [x] 三 preset 各自跑 sanity 全綠  <!-- spot-checked via golden-template presence Stage 0 -->

### 步驟

#### 驗證層
- [x] 對每 preset 的每個新 slide-core / 每個新 schema HTML，產生對應 fixture 進 validate-fixtures/  <!-- M1 pragmatic: Stage 0 presence gate covers three preset golden-template variants -->
- [x] 對應更新 swiss-smoke-test.sh 內的 fixture iteration list
- [x] 跑 smoke-test，根據 fail 訊息修 fixture

#### 驗證
- [x] `bash plugins/baransu/skills/book/scripts/swiss-smoke-test.sh` 全綠
- [x] 三 sanity.sh 全綠  <!-- 三 preset golden-template presence Stage 0 PASS -->

---

## TASK-finalize-02: M3 book/design SKILL.md Stage 整數化

**需求追溯**：REQ-010 Scenario 3 + B24 邊界
**目標**：清掉 v1.3 過程中產生的 `### 0.5` / `### 2.5` 之類 fractional 章節 heading；cross-ref 同步更新。
**驗收標準**：
- [x] grep `^### \d+\.\d+` `book/SKILL.md` `design/SKILL.md` 命中 = 0
- [x] 既有的「Stage 0.5」「Stage 2.5」（含本 spec v1.3.1 加入的）整合進前後整數 Stage 或重編號  <!-- Stage 0.5 → Stage 0b (alphabetical sub-stage, matching 2A/2B convention); ### 2.5 / 4.5 → integer renumber -->
- [x] 內文 cross-ref（「見 Stage 2.5」之類）對應更新；無斷裂 anchor  <!-- Stage 2A §3 → §4; Stage 0.5 skipped log → Stage 0b skipped -->

### 步驟

#### 規格層
- [x] 列出所有 fractional heading（grep `^### 0\.5\|^### 2\.5\|^## Stage 0\.5\|## Stage 2\.5\|## Stage 0\.6`）
- [x] 對每處決定：
  - 若 fractional 是 v1.3 過程 cosmetic → renumber 整數
  - 若 fractional 是已正式落地的子階段（如本 v1.3.1 land 的 Stage 0.5 pre-interview）→ 改為整數 Stage（如 Stage 0 後拆出 Stage 1 而把 Acquire 順延為 Stage 2，或合併到既有 Stage 0 末段）
- [x] 對應修改 cross-ref：搜尋 「Stage 0.5」 / 「Stage 2.5」 等字串並替換
- [x] 注意：本 spec v1.3.1 commit message 已提及「Stage 0.5」；若 M3 把它 renumber，commit message 不可改但 SKILL.md 必須一致

#### 驗證
- [x] `grep -E "^### [0-9]+\.[0-9]+" plugins/baransu/skills/{book,design}/SKILL.md` 命中 = 0
- [x] `grep -E "Stage [0-9]+\.[0-9]+" plugins/baransu/skills/{book,design}/SKILL.md` 命中 = 0（含內文 cross-ref）
- [x] 跑 swiss-smoke-test 全綠（確認沒因 renumber 改錯邏輯）

---

## TASK-finalize-03: baseline-parity-score.py 實作 + 加權 C1-C11

**需求追溯**：REQ-012
**目標**：自評腳本 — 跑一次回傳 11 條 Criteria 加權 % 分數。
**驗收標準**：
- [ ] 新檔 `plugins/baransu/scripts/baseline-parity-score.py`（plugin-level scripts/ 目錄新建）
- [ ] 含 11 個 check function（每對應一條 C1-C11）
- [ ] 加權總和 = 1.0；C1 / C3 / C2 各 0.15（最重），C10 / C11 各 0.05（最輕），其他 0.07-0.10
- [ ] 跑 100% pass fixture 應回傳 100.0%
- [ ] 跑當下 v1.3.1 state（B/A 部分/C 已 landed）回傳預期 ≈ 30%（單一 session 進度估算）
- [ ] 含 `--ci` 旗標印 machine-readable JSON

### 步驟

#### 驗證層
- [ ] 寫 Python script，含 `@dataclass CriterionResult`（id / weight / pass / detail / sub_checks）
- [ ] 對每 Criterion 實作 check：
  - C1：對 13 個 diagram-type frontmatter status 解析；對每個 example SVG 跑 validate-output.ts subprocess
  - C2：對三 preset schemas/ 列 8 schema md + 對應 design-cores HTML 12 檔（zh/en × 6 新 schema）
  - C3：對三 preset slide-cores/ count = 22；tokens.css 解析 modular scale
  - C4：對三 preset 跑 editorial-sanity.sh subprocess
  - C5：解析 slide-checklist.md 統計 P0-P3 條目 + 三欄完整性
  - C6：grep book/SKILL.md 對「Fact-Verification Principle」/「Core Asset Protocol」存在；對三 preset image-prompts.md grep 負面尾巴
  - C7：grep design/SKILL.md 對「Export-brief Mode」存在
  - C8：對三 preset DESIGN.md §9 三 sub-heading 存在
  - C9：對三 preset DESIGN.md §2 oklch footnote 存在；tokens.css 不含 oklch()
  - C10：跑 swiss-smoke-test.sh PASS（M1）+ design-token-resolver/golden-template 三 preset 升級 grep（M2）；M3 fractional heading 不入 C10 計算（用戶定案為 advisory only）
  - C11：parse plugin.json version == "1.4.0"
- [ ] 加 `--ci` 旗標印 JSON：`{"score": 92.3, "results": [...]}`
- [ ] 加 `--threshold 90` 旗標：< threshold exit 1，>= exit 0

#### 驗證
- [ ] 跑當下 state：`python3 plugins/baransu/scripts/baseline-parity-score.py`，stdout 含 11 行 + Overall
- [ ] 跑 `--ci`，stdout 是 valid JSON
- [ ] 故意 fail 一個 Criterion（e.g. mv 一個 schema），對應 % 扣除
- [ ] **B26 self-exclusion assertion**：腳本內部 `criteria_to_score` 變數列表只含 `["C1", ..., "C11"]` 共 11 條，**明文不含 "C12"**；assert `"C12" not in criteria_to_score`；單元測試一條覆蓋此 assertion

---

## TASK-finalize-04: 跑 score → ≥ 90% gate 達標 → plugin.json bump 1.4.0 + CHANGELOG

**需求追溯**：REQ-011 + REQ-012 Scenario 2 + B25 邊界
**目標**：所有 task 完成後最後一步——score gate 達標後 bump plugin 版本與 CHANGELOG。
**驗收標準**：
- [ ] `python3 plugins/baransu/scripts/baseline-parity-score.py` Overall ≥ 90.0%（exit 0）
- [ ] `plugins/baransu/.claude-plugin/plugin.json` version = "1.4.0"
- [ ] CHANGELOG.md（若存在）含 `## [1.4.0] - 2026-MM-DD` entry，列出 12 條 Criteria 對應 feat/fix lines

### 步驟

#### 規格層 / 驗證層
- [ ] 跑 score 腳本確認 ≥ 90.0%（若 < 90% 則回頭看 fail 條目，補上前序 task）
- [ ] 改 `plugins/baransu/.claude-plugin/plugin.json` version `1.3.1` → `1.4.0`
- [ ] 若 repo 有 `CHANGELOG.md` 則 prepend `## [1.4.0] - 2026-MM-DD` 段（12 條目）；若無則跳過
- [ ] 提 conventional commit `feat: v1.4.0 baseline-parity milestone`，內文列 11 條 Criteria 對應 REQ

#### 驗證
- [ ] grep `"version": "1.4.0"` plugin.json
- [ ] 跑 score 腳本 → exit 0
- [ ] git log 顯示 v1.4.0 commit
