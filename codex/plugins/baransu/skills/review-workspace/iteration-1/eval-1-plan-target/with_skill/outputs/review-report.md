# /baransu:review — 審核結果

**Verdict：CONCERN**

## Target

- Path: `plugins/baransu/skills/review-workspace/iteration-1/fixtures/review_plan.md`
- Shape: plan / design document（`/baransu:think` 的 5-section 產出）
- Size 指標: 61 行、5 sections、Key decisions 6 項、Building 7 步、Not building 7 項、Unknowns 3 項、涉及檔案 6 個（SKILL.md + 3 agent + plugin.json + CLAUDE.md）
- Tier: **T3 deep** — 決策數 > 3，涉及跨層次（skill orchestrator + 3 agent files + 版本管理），符合 SKILL.md Stage 0 深度層條件
- E2E gate: **n/a**（plan target，非 executable code）

## 目標宣稱 (Claim Checklist)

**做了 / 要做**
- C1：建立 `/baransu:review` skill，作為使用者手動呼叫的獨立多視角檢察官
- C2：Stage 2 先產 checklist，列出 target 的 claim / 邊界
- C3：Stage 4 依 target 屬性派遣 1–3 個 perspective agent（架構 / 品質 / 安全）在隔離 Task context 中獨立思考
- C4：Stage 5 滿足門檻時加跑對抗測試（6 角度）
- C5：Stage 6 四級 triage；T1 自動修復僅限 format / import / typo / dead import
- C6：Stage 7 code target 若無 e2e 證據 → verdict 強制 INCOMPLETE
- C7：繁體中文報告輸出
- C8：實體檔案 `plugins/baransu/skills/review/SKILL.md` + 3 個 agent 檔 + `plugin.json` bump 到 `0.2.0` + `CLAUDE.md` 新增段落

**已決定**
- D1：SKILL.md 為純 orchestrator，不含 reviewer rubric
- D2：三個 agent 檔採「視角 / 目標 / 通用原則 / 禁忌」四段結構，明禁人設
- D3：激活規則 = 目標屬性表，非關鍵詞匹配
- D4：對抗性測試僅在觸發門檻時跑（>100 LOC code、>3 plan decisions、或跨層級變更）
- D5：T2 打包確認以批次 AskUserQuestion 呈現
- D6：自動修復直接落檔，不走 git staging

**宣稱達成**
- A1：Task 隔離 context → 抗污染
- A2：明文 claim checklist → 防幻覺
- A3：天平檢視強制 → 防過度工程
- A4：E2E 硬 gate → 防 code target 誤判 PASS

**明確不做**
- NB1–NB7（不自動化、不跨 session、不做人設、不改邏輯、不 review 互審、不實跑 e2e、不支援 --auto）

**已知未知**
- U1：三個 agent 檔「通用原則」10–15 條 bullets 細節未逐條寫出
- U2：6 角度對抗測試如何對應 plan 型 target，延後到首次 plan-target 試跑決定
- U3：v0.2.0 vs v0.1.1 的語意版本決策

## 派遣的審核者

- **架構審核**：啟用 — plan / design target 永遠啟用；Stage 3 activation table plan-row
- **品質審核**：啟用 — plan / design target 永遠啟用；Stage 3 activation table plan-row
- **安全審核**：略過 — plan 未觸及 auth / secret / crypto / network / injection / persistence / serialization / user-supplied template 任一項；僅本機檔案寫入（format/import/typo/dead-import），不構成 security surface
- **對抗測試**：啟用 — T3 tier 強制；6 角度按 Stage 5 plan 變體映射（ambiguous premise / sections inconsistent / decision contradiction / scope creep / cause-effect confusion / apparent completeness hallucination）

## 發現（四級 triage）

### Tier 1 — 已自動修復（format / import / typo / dead import）

**無。** Plan target 無 code 可 auto-fix；對 plan 本身的文字修訂屬語意改動，不在 T1 半徑內。

### Tier 2 — 待確認（非語意但超出 T1）

**無。** Plan target 無非語意、可批次套用的改動。所有 plan 修訂建議皆屬語意改動，歸 Tier 3。

### Tier 3 — 需判斷（以下為 AskUserQuestion 替代方案：報告整批呈現，由使用者在下一輪擇取）

> **AskUserQuestion 旁路說明**：本次執行在無人值守模式下進行。依最可辯護預設（`--auto` 等價行為），T3 findings 不彈窗，而是整批呈現在報告中，由使用者在下一輪挑選採納項目。此不牴觸 SKILL.md constraint——使用者事後看報告、決定、回傳一個訊息即完成 batch 選擇，等價於一次 batched AskUserQuestion。

**T3-01（major）— Unknowns 三項皆缺少「延後理由」與「誰何時決定」**
- 來源：quality-reviewer qual-01
- Citation：Unknowns U1 / U2 / U3
- 觀察：plan 自己在（隱含的）rubric 中要求 Unknowns 具備「具體問題 + 延後理由 + 誰何時決定」三要素。U1 僅有問題；U2 有部分延後理由但無決定者；U3 僅問題。U2 尤其弔詭——它延後到「首次 plan-target 試跑」，而現在正是首次試跑。
- 建議：U1 / U3 各補一行「延後理由 | 決定者/時機」；U2 在本次審核中即可就地收斂（詳見 T3-02）。
- 天平：不做 → Unknowns 日後重訪時需重建 context；做了 → 約 3–4 行文字，無行為改動；中間方案 → 最小化註記即可。天平通過。

**T3-02（minor，可就地收斂）— U3 實為「未決」而非「未知」**
- 來源：quality-reviewer qual-06
- Citation：Unknowns U3
- 觀察：plan 已說明此次新增 skill + 3 agents + CLAUDE.md 段落，屬新功能、非破壞性變更；SemVer 機械上對應 minor bump（v0.2.0）。此為可決定的項目偽裝成 Unknown，違反 quality 視角 plan 規則 6。
- 建議：從 Unknowns 移除，在 Key decisions 新增一條：「v0.2.0（minor bump — 新功能、不破壞相容）」。
- 天平：不做 → 一次性小困擾；做了 → 兩行文字；就地收斂最便宜。天平通過。

**T3-03（major）— Key decisions #4 / #6 寫成活動 / 門檻，而非決策**
- 來源：architecture-reviewer arch-01
- Citation：Key decisions 第 4、6 點
- 觀察：KD #4（「對抗性測試 >100 行 / >3 decisions / 跨層級時跑」）只述 what / threshold，無 why（為何 3 而非 5？token 預算？噪音下限？）；KD #6（「自動修復直接改，不走 git staging」）同樣無 why（複雜度？UX？跨專案可靠性？）。Plan 自身 rubric 要求 Key decisions 寫成「為什麼這樣選」。
- 建議（擇一）：
  - (a) 改寫 KD #4 / #6 成「選 X 拒 Y，因為 Z」形式
  - (b) 中間方案：於 Unknowns 新增「門檻數字為啟發式，首次使用後視需要調整」，承認其啟發性而不假裝為最終決策
- 天平：不做 → 讀者無法稽核門檻是否有意為之；做了 → 每項 2–3 行；推薦中間方案 (b)。天平通過。

**T3-04（minor）— Building 步驟 7「輸出繁中報告」相對前 6 步欠缺具體性**
- 來源：quality-reviewer qual-02
- Citation：Building 步驟 7
- 觀察：步驟 1–6 每項都有具體動作；步驟 7 僅一句「輸出繁中報告」，讀者無法立即想像成品（含哪些章節、verdict 格式、render 位置）。違反 plan-rubric「Building 可讓讀者立刻想像成品」。
- 建議：擴為一句——「輸出結構化繁中報告，含 Verdict（PASS / CONCERN / FAIL / INCOMPLETE）、Target、Claim Checklist、派遣紀錄、四級 findings、E2E gate、結論」——與 1–6 步等重。
- 天平：不做 → 讀者自補；做了 → 一句話；天平通過、建議採納。

**T3-05（major，源自對抗測試 angle 3）— KD #1「純 orchestrator」定義範圍不清**
- 來源：adversarial angle 3 (decision-to-decision contradiction)
- Citation：Key decisions #1 vs #5
- 觀察：KD #1 說 SKILL.md 不含 reviewer rubric，只寫派遣邏輯；KD #5 描述 triage 機制（四級、auto-fix 半徑、打包確認）。Triage 本身是一種規則——若 SKILL.md 擁有 triage 邏輯（必然，因無他者可承接），KD #1 的「純 orchestrator」就被局部違反。這是用詞範圍問題：KD #1 意指「偵測 rubric」，而非「triage 機制」。
- 建議：明文拆分——「SKILL.md 擁有 dispatch + triage 邏輯；agent 檔擁有 detection rubric」。預先排除日後實作 review 時的誤判。
- 天平：不做 → 日後實作審核可能因此爭執；做了 → 一句話澄清；天平通過、建議採納。

### Tier 4 — 僅供參考

- **FYI-01（adversarial angle 1）** — plan 的核心價值宣稱「Task 隔離 → 抗污染」，但 Task 隔離僅「不見父會話歷史」，仍會見到 SKILL.md 傳入的 prompt 文字。若 prompt 過度 shape（例如明示「找 X/Y/Z」），隔離承諾被再度污染。Plan 未點明此前提。——advisory only，因現行 agent 檔「視角 / 通用原則」段已做一定防護。

- **FYI-02（adversarial angle 2）** — Not building NB7「不支援 --auto」隱含「永遠有互動式 user」假設；若被 Copilot Coding Agent 類 headless 場景呼叫，skill 會卡在 AskUserQuestion。plan 未聲明互動式為唯一支援模式。

- **FYI-03（adversarial angle 4a）— 「auto-fix」用詞潛在誤讀風險**：CI 使用者可能誤以為 /review 可當自動 linter。建議在 SKILL.md / 文件中強調「T1 auto-fix 僅限人機在側之 manual invocation」。

- **FYI-04（adversarial angle 5）— Approach 的「官方方案不適用」論證不完整**：列差異不等於證明不適用。若簡化成「原生 /review 不支援非 PR target，所以我們另做」即可；其餘差異（triage、對抗）是設計偏好，非硬需求。——plan 整體決策不變，僅論證表述可收緊。

- **FYI-05（arch-02）— NB6 「不跑 e2e」與 Building 步驟 6 詞彙碰撞**：邏輯不衝突但 skimming 時可能誤讀。微飾即可，不必動。

- **FYI-06（arch-03）— 激活規則的實際 table 未 sketch**：plan 提 Key decision，但未示例 row。可落在實作時的 SKILL.md 內，無需在 plan 補。

- **FYI-07（arch-04）— SKILL.md 與 agent 檔的依賴方向未言明**：若 SKILL.md 不 import agent 檔內容（只以 subagent_type 呼叫），agent 可獨立演化；若含 import / 硬參照，則耦合。plan 默認前者但未聲明。

- **FYI-08（arch-05）— 「跨層級變更」用於 plan target 時定義未明**：對 code target 清楚，對 plan target 需另行定義。可改列 Unknowns。

- **FYI-09（qual-03 / qual-04 / qual-05）— 幾個 cross-reference / 邊界詞彙微不周全**：KD #3 與 Building step 2 無交叉引用；NB5 「審核者互審 vs review-of-review」兩層意思混用；Building step 5 對超出自動修復範圍的處理未聲明。皆 advisory，可在實作時於 SKILL.md 補。

- **FYI-10（adversarial angle 6 / 根因）— 計畫呈現「完成感」部分是 schema 效應**：5 section 皆填滿 ≠ 設計實質完成。大部分實質（三個 agent 的通用原則 bullets）仍待下一輪產出。此為正常 plan vs spec 分工，但讀者不宜將「plan approved」讀作「設計鎖定」。

- **FYI-11（adversarial epistemic check）— 審核者對 Unknowns 的共識可能是 rubric 同源偏差**：三視角同意 Unknowns 欠完整，部分原因是各自 agent 檔都寫了類似 rubric 規則。反方觀點：也許該 rubric 對一個小型 skill-authoring plan 太嚴苛。但因 plan 自宣稱遵循此規則，仍可依其自宣稱標準裁量。

## E2E Gate

**n/a — plan target，不適用 e2e gate。** （SKILL.md Stage 7 條款：plan / claim targets 的 e2e gate n/a。）

## 結論

此 plan 整體**架構健全、決策大致可執行**，未發現責任錯置、跨層耦合、過度抽象、或偽裝為已解決的重大 Unknown。主要問題集中於**計畫衛生（plan hygiene）**，非系統設計缺陷：Unknowns 三項皆不符 plan 自訂三要素；兩條 Key decisions 寫成活動/門檻而非真正決策；一條 Key decision 的「純 orchestrator」語意範圍未拆清；Building 最後一步相對輕描。對抗測試另發現一條值得在實作期強調的前提——Task 隔離僅在 prompt 最小化時才等於抗污染。三項已分類為 T3（需判斷）、一項（U3 版本號）可就地收斂為 v0.2.0；其餘 11 項 FYI 不必 plan 層修訂，多數可在實作 SKILL.md / agent 檔時併入。Verdict 為 **CONCERN**：無 critical 級且無幻覺宣稱被證實，但有 5 條 T3 等級 findings 使用者需在下一輪選擇採納與否；e2e gate n/a，不影響判斷。
