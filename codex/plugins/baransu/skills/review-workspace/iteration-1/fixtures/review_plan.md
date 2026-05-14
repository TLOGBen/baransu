# /baransu:think 產出 — 建立 /baransu:review skill 的計畫

這是經 Stage A 三輪對焦 → Stage B/C/D/E 檢視 → Stage F 產出的 5-section 計畫。Stage G 使用者已 Option 1 批准。

## Building（要做什麼）

建立 `/baransu:review` skill，作為使用者手動呼叫的**獨立多視角檢察官**。使用者把任意 target（git diff、檔案集、directory、一段文字、/think 的計畫文件、任何宣稱）交給它，它會：

1. 先條列一份 checklist，說明「這份產出在宣稱什麼 / 做到什麼 / 邊界在哪」。
2. 依 target 規模與激活規則決定派遣 1~3 個獨立 perspective agent（架構 / 品質 / 安全），各 agent 在乾淨 Task context 中隔離獨立思考。
3. 達門檻時加跑一輪對抗性測試（六角度：違反假設、組合失敗、上下級串聯錯、濫用場景、根因辨識、epistemic 共識幻覺檢查）。
4. 彙總後分成四級：安全修復直修 / 大概對的打包確認 / 需判斷詢問 / FYI 僅告知。
5. 執行第一級自動修復（僅限 formatter / imports / typo / dead import）。
6. 若 target 為程式變更，未偵測到 e2e 跑過 → verdict 強制降為 INCOMPLETE。
7. 輸出繁中報告。

實體檔案：
- `plugins/baransu/skills/review/SKILL.md`
- `plugins/baransu/agents/architecture-reviewer.md`
- `plugins/baransu/agents/quality-reviewer.md`
- `plugins/baransu/agents/security-reviewer.md`
- `plugins/baransu/.claude-plugin/plugin.json` 版本 bump 到 `0.2.0`
- `CLAUDE.md` 新增段落

## Not building（明確不做的事）

- 不做 pipeline gate：不自動在任何 skill 宣告 done 前插入，不讀 flow-state.json，不產 handoff envelope。
- 不做跨 session 記憶：每次 run stateless。
- 不做 agent 人設：三個 agent 檔明文禁止「你是資深 XX 工程師」類人格描述。
- 不替使用者改動邏輯行為：自動修復半徑鎖死在 format/import/typo/dead import。
- 不做審核者互審或 review-of-review。
- 不跑 e2e：不嘗試執行 target 專案的測試指令，只偵測並用 INCOMPLETE verdict 施壓。
- 不支援 `--auto` 模式跳過 AskUserQuestion。

## Approach（選了哪個方案及理由）

選 7 階段 orchestrator + 3 獨立 perspective agent 檔 + 1 動態對抗 Task，而非：
- 極簡方案（單 subagent + inline rubric） —— 失去隔離思考、失去 perspective 切分、違反核心理念。
- 極繁方案（審核者互審 / 每人一次對抗） —— token 爆炸、違反「複雜度需自證」。

官方方案（原生 /review 與 /security-review）不適用：兩者都是單 pass、無 perspective 切分、無分級、無對抗、無 triage、無 auto-fix、不支援非 PR target。

已接受的邊界：
- 審核者過度保守時靠 agent 檔的「通用原則」段自我約束，極端情況下仍可能被個別 agent 繞過 —— 接受此為邊界。
- 審 /think 輸出時陷入遞迴靠 SKILL.md 明文規則禁止 —— 無法 100% 防止某個 agent 在自由文字中暗示。

## Key decisions（關鍵決策）

1. Skill 本體是純 orchestrator / 任務分析師，不擔任 reviewer：主 SKILL.md 不寫任何「該找什麼問題」的 rubric，只寫派遣邏輯。換得責任清晰、agent 可獨立演化。
2. 三個 perspective agent 檔走「視角/目標/通用原則/禁忌」四段結構，明禁人設：對應使用者「角色扮演只會讓模型產生莫名幻覺」的觀察。
3. 激活規則 = 目標屬性表，非關鍵詞匹配。對 /think 輸出這種非 code target 也能正確派遣。
4. 對抗性測試只在觸發門檻時跑（>100 行 code，或 >3 decision points in plan，或跨層級變更）。
5. 四級 triage 的「打包確認」批次彈 AskUserQuestion，一次一批，避免逐題騷擾。
6. 自動修復落檔直接改，不走 git staging。

## Unknowns（已知不知道的事）

- 三個 agent 檔的具體 rubric 細節（各自「通用原則」段的 10~15 條 bullets）尚未逐條寫出。
- 對抗性測試六角度如何對應到 plan 型 target 需要翻譯，延後到首個 plan-target 試跑時決定。
- v0.2.0 vs v0.1.1 的語意版本決策。
