# Tasks: governance（anti-patterns 容器）
**前置群組**：cut

## TASK-governance-01: rules/anti-patterns.md

**需求追溯**：REQ-005
**目標**：跨技能行為護欄容器就位，含自治條款與首批條目。
**驗收標準**：
- [ ] `plugins/baransu/rules/anti-patterns.md` 存在；檔頭自治條款：收斂不堆積（新條目須先找到既有原則折入，禁近義詞追加）＋ strip-provenance（規則靠防止什麼掙位置，不帶事故敘事與來源規模數字）
- [ ] 首批條目：自 CLAUDE.md Non-obvious Invariants 逐條評估 — 跨技能成立者入容器（例：subagent depth=1 禁巢狀 skill 呼叫；Read-before-write），技能專屬者（如 ship 的 -D 旗標、DESIGN.md 大小寫）留在原處並於容器註明分層原則
- [ ] 表格三欄式：慣性 / 錯誤示範 / 正確做法
- [ ] CLAUDE.md 增一行指向容器（不搬移技能專屬不變量）

### 步驟

#### 撰寫
- [ ] Read CLAUDE.md Non-obvious Invariants 全節，逐條分類（跨技能 / 技能專屬）
- [ ] 撰寫容器；首批 5-8 條，寧缺勿濫
- [ ] Edit CLAUDE.md 加指向行
