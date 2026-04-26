# /think plan — rewrite review skill + 3 perspective agents

## Context

baransu 的 `/baransu:review` skill 已存在於 `plugins/baransu/skills/review/SKILL.md`（181 行）。三個 perspective agent 已存在於 `plugins/baransu/agents/{architecture,quality,security}-reviewer.md`（本對話稍早分別新增了大量 reference 段落）。本計畫要 in-place rewrite 這 4 個檔案。

設計依據：
- `project/others/leet/lecture/ch2-擴充Agent/04-SubAgents.md`（已讀）
- 使用者透過 /baransu:think 給的 spec 與 7 條警告（核心：原則保持原則，不翻譯成 schema/matrix；不加防禦性段落；不偷其他 ecosystem 詞彙；body 英文 / user-facing 繁中；goal input + 天平第四題；agent 三段+選擇性禁忌；對自己用天平）

## Building（要做什麼）

1. **architecture-reviewer.md**：5 sections — `Language` (KEEP as-is, already English) → `Perspective` → `Mission` → `Principles` → `Lane-keeping`。把現有 視角/目標/通用原則/禁忌 內容翻譯成英文進入後 4 段，**翻譯時 Perspective / Mission / Principles / Lane-keeping 段必須使用 Language section 定義的 vocab（Module / Interface / Seam / Adapter / Depth / Leverage / Locality），避免 component / boundary / API 等被 Language 段明確 reject 的詞彙 —— 否則 Language 段會與其他段自相矛盾**。Language 段（Module / Interface / Implementation / Depth / Seam / Adapter / Leverage / Locality + Principles + Relationships + Rejected framings）保留原文不動。
2. **security-reviewer.md**：9 sections — 4 段骨架 (Perspective / Mission / Principles / Lane-keeping) 在前；後接 5 段防禦素材 (Focus / OWASP Checklist / Code Pattern Red Flags / Common False Positives / Analysis Commands)，全部 KEEP as-is（已英文）。CUT：Target Adaptation / Evaluation Framework / Triage Protocol。
3. **quality-reviewer.md**：4 sections — `Perspective` (含 +1 bullet「For code targets, also assess whether existing tests test the right things — not just whether tests exist」) → `Mission` → `Principles` → `Lane-keeping`。CUT 全 3 段新增 (Focus / Evaluation Framework / Triage Protocol)。
4. **review SKILL.md**：保留 Stage 1–7 + E2E + Output shape；保留 `## Three perspectives (agent files)` 段，其中段名引用同步替換為 `Perspective / Mission / Principles / Lane-keeping`；移除 Core constraints 段，但 absorb 2 條（Re-read before Stage 6 → Stage 6 段首一句、No recursion → Stage 4 段尾保留 3 個 sub-facts: /review 不喚起 /review、adversarial 僅一輪、reviewers 不互審）；移除 Gotchas 段標題，absorb 規則為：Trap 1 → Stage 6 balance check 段尾兩三句；Trap 2 拆兩半 absorb（goal-input / live-review 半 → Stage 1 goal 段尾兩三句、fourth-balance-question / skill-editing 半 → Stage 6 段尾與 Trap 1 共存）；line 167 meta-summary 兩句（「複雜度需要證明自己的價值」for additions、「精簡不能讓 load-bearing 機制變成默認」for cuts）保留為 SKILL.md 末段獨立兩行，不附段標題。

Frontmatter（name / description / tools）四個檔案皆不變。

## Not building（明確不做的事）

- 不新增 brief 6 要素 schema（04-SubAgents.md §6 提到的）—— 與 #2 警告衝突
- 不重寫 Stage 編號或 stage logic —— 現有 1–7 + E2E 結構已涵蓋設計概念
- 不改 frontmatter（name / description / tools）—— description 是委派依據，已足夠精準
- 不為 LOC tier 表新增第四檔
- 不為 4-tier 響應加 verdict enum（PASS/CONCERN/FAIL）；natural prose 維持
- 不寫 markdown skeleton 給最終報告填空
- 不加「Constraints (hard) / What this skill is NOT / Iron Rules」段
- 不加 dogfood / e2e 流程到 SKILL.md（使用者選 Deliberation-only）
- 不刪除任一 agent（arch / security / quality）的目標段 6 類別（含第 6 類「Plan 型 target 專用」）—— 全部翻譯保留，不合併不刪減
- 不把 Trap 1/2 內容完全刪除 —— 是 observed failure，必須 absorb 不能消失
- 不把 architecture-reviewer 的 Language section 翻譯（已英文，as-is 保留）
- 不把 security-reviewer 的 5 段保留素材改寫 —— as-is 保留
- 不為 quality-reviewer 重建任何 schema-style test taxonomy

## Approach（選了哪個方案）

走的是「結構重組為主、內容重寫為輔」的中間路線：

- agent body 從繁中翻成英文（與 SKILL.md body 慣例對齊；user-facing 字串保繁中）
- 4-section 骨架（Perspective / Mission / Principles / Lane-keeping）替代既有 視角/目標/通用原則/禁忌；Lane-keeping 命名直接對應使用者 #6 警告自舉的合格理由
- 本對話稍早新增的 12 個 reference 段，逐段套天平四問後判決：arch 全 KEEP（使用者明確要求）；security 5 KEEP / 3 CUT（使用者校準「防禦重點」範圍）；quality 0 KEEP（使用者 deferred）+ 1 bullet fold
- SKILL.md 走 net reduction：Core constraints 與 Gotchas 兩個包裝段移除，但 load-bearing 內容（Re-read protocol、No recursion、Trap 1/2）absorb 進相關 stage，不消失

已接受的失效邊界：
- security-reviewer 的「防禦重點」完整保留（含 OWASP Checklist 與 Code Pattern Red Flags），意味著 security 的 review 行為會帶入較多 schema 化內容；這是使用者明確選擇的 trade-off，非過度設計
- arch 與 quality 走 minimal style；security 走 reference-rich style；agent 之間風格不一致是預期結果

## Key decisions（關鍵決策）

1. **Section name 翻譯為 Perspective / Mission / Principles / Lane-keeping**：選 Lane-keeping 不選 Anti-patterns，因為 Anti-patterns 易與設計模式混淆；Lane-keeping 是使用者 #6 警告中親自舉的合格範例，直接對應「不做 X — 那是 Y reviewer 的事」這個 observable lane-keeping 失效。
2. **architecture-reviewer 全段保留 Language**：使用者明確標注是個人認同的核心，不論天平 4 結果為何，覆寫此判決。
3. **security-reviewer 留 5 段防禦素材，砍 3 段**：使用者校準「防禦重點」= Focus + OWASP + Code Pattern Red Flags + Common False Positives + Analysis Commands；其餘 3 段（Target Adaptation / Evaluation Framework / Triage Protocol）非防禦本身（前者是 scope 規則、中者是視角重述、後者是錯層的 output 規則），CUT。
4. **quality-reviewer 全 3 段 CUT，1 bullet fold**：使用者 deferred 給我；天平 4 結果一致 CUT；test-fitness 概念不丟，併進 Perspective 段一個 bullet。
5. **Core constraints 段全砍但 absorb 2 條**：8 條中 6 條是 stage 重述（典型 #1 警告「7 條 Iron Rules 把原則再濃縮一次」），2 條是真正的程序約束（Re-read protocol 進 Stage 6、No recursion 進 Stage 4）。
6. **Gotchas 段標題砍但 Trap 1/2 absorb，Trap 2 拆兩半**：標題違反 #1 警告但內容是 SKILL.md 自己標記為 observed 的 load-bearing failure。Trap 1 absorb 進 Stage 6 一處；Trap 2 因內文並列引用 Stage 1 goal 與 Stage 6 fourth balance-check question 兩個範例（line 165）且 line 161 明聲明 live-review + skill-editing 雙模式，必須拆兩半 absorb 才不丟內容；line 167 meta-summary 雙句保留為 SKILL.md 末段獨立兩行（不附段標題），對應 additions 與 cuts 兩端的 anchoring。
7. **不採納 04-SubAgents.md 的 brief 6 要素 schema**：本 SKILL.md Stage 4 給的 3 樣（target / checklist / goal）+ agent 文件本身的 4 段定義已經是 Self-Contained Brief；再加 6 要素 schema 違 #2 警告。
8. **`## Three perspectives (agent files)` 段內段名引用同步**：SKILL.md lines 16–21 那段顯式引用「視角/目標/通用原則/禁忌」舊段名；agent 段名重新命名後，這段必須同步更新為 `Perspective / Mission / Principles / Lane-keeping`，否則 SKILL.md 會 grep 不到對應 agent 段，違反 plan 自己的 cross-file 一致性要求。
9. **Translation faithfulness across 3 agents**：將 視角 / 目標 / 通用原則 / 禁忌 翻成 Perspective / Mission / Principles / Lane-keeping 時，必須保留三項 spec 內容核心，不得在翻譯過程中流失：(a) 通用原則中的「天平檢視（強制）」**四問完整結構**，Q4「是否服務於本次 review 的 goal」維持為**第四問**且不被合併、弱化或拆散 —— 這是 user spec #5 警告的 mandate；(b) 中文原 imperative voice — must / never / always 對應，不轉成 should / may / consider —— 這是 spec 的 surgical 鋒利感所在；(c) Lane-keeping 段內的 cross-reference 名稱（architecture-reviewer / quality-reviewer / security-reviewer）逐字保留，不抽象化成「另一個 reviewer」 —— 否則 lane-keeping 機制失去 anchoring。

## Unknowns（已知不知道的事）

- **quality-reviewer 那一 bullet 放在 Perspective 內還是 Mission 內**：傾向 Perspective（擴展「從哪個角度讀」），但 Mission（新增「會回報哪幾類 finding」）也通。差異很小；執行時自決。
- **Trap 1 / Trap 2 三個 absorb 落點的具體措辭**：結構決定 closed in Building #4（Trap 1 → Stage 6 一處；Trap 2 → Stage 1 + Stage 6 兩處；line 167 meta-summary → SKILL.md 末段獨立兩行）；剩下純文字層的「具體一兩句怎麼寫」，執行時自決。
- **Lane-keeping 段內容措辭風格**：英文翻譯時保留現有「不做 A、不做 B、不做 C」的列舉式（直譯），還是收成段落式（更英語化但失去清單感）。傾向直譯保持掃讀性；執行時自決。
