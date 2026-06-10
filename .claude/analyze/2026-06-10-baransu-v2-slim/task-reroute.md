# Tasks: reroute（TDD 整併與交接改道）
**前置群組**：cut

## TASK-reroute-01: tdd.md 整併為唯一知識源

**需求追溯**：REQ-002
**目標**：dev 的閘門紀律併入 _shared/tdd.md，無第二份 TDD 檔，failure_count 權威不複製。
**驗收標準**：
- [ ] tdd.md 含「直接實作時的紅綠閘」段落（自建紅綠 task list、先紅後綠、紅燈確認再實作）
- [ ] tdd.md scope 行與 §8 觸發點表僅列存活消費者（impl-agent、review-agent、think/hunt 改道句）
- [ ] 「compile error 不計入 failure_count」在 tdd.md 中僅以「見 execute/SKILL.md」形式出現，全倉權威表述恰一處
- [ ] 不存在 tdd-gate.md

### 步驟

#### 整併
- [ ] Read tdd.md 全文與 dev/SKILL.md 閘門段（自 git 歷史或裁前快照取 dev 文字）
- [ ] 撰寫「直接實作時的紅綠閘」段，融入既有結構（不重複既有原則）
- [ ] scope 行去 /dev、§8 表去 dev 列、加 think/hunt 改道列

## TASK-reroute-02: 四處交接與錨點改道

**需求追溯**：REQ-002
**目標**：think/hunt/review/ship/review-agent 全部脫離 dev 引用，語義不變。
**驗收標準**：
- [ ] think/SKILL.md:381 與 :175：小任務 → 「直接實作，依 _shared/tdd.md 紀律自建紅綠 task list」
- [ ] hunt/SKILL.md:230：同上改道
- [ ] review/SKILL.md:210：regression-first 歸屬句改為「/baransu:execute 或依 tdd.md 的直接實作」
- [ ] ship/SKILL.md：.claude/dev/ 自歸檔清單移除，其餘目錄行為不變
- [ ] agents/review-agent.md:71：cosmetic 四分類錨點改掛 tdd.md 對應段；execute/SKILL.md 零 diff
- [ ] codex-skill-transfer/SKILL.md:116 舉例與 scripts/transfer.py:819 註解改寫（換存活例子）

### 步驟

#### 改道
- [ ] 逐檔 Read → Edit 上列七處
- [ ] word-boundary grep `baransu:dev` 與 `\.claude/dev` 確認 plugins/ 內零殘留
