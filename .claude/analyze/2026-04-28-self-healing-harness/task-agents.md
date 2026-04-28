# Tasks: agents
**前置群組**：shared

1 個新 subagent：investigator-agent，perspective 類，read-only。

---

## TASK-agents-01: investigator-agent.md（perspective 類，read-only）

**需求追溯**：REQ-003 Scenario 2、INT-5、KD#1
**目標**：定義 investigator-agent 的 mission / principles / lane-keeping，鎖死「read-only、無 git ops」邊界，產 evidence bundle 給 /triage。
**驗收標準**：
- [ ] `plugins/baransu/agents/investigator-agent.md` 存在
- [ ] 與既有 perspective 三件套（architecture/quality/security-reviewer）的檔案結構一致（Perspective / Mission / Principles / Lane-keeping）
- [ ] 明寫禁止操作：不寫任何檔、不 stage / commit / push / branch / worktree、不啟動 subprocess 變更狀態
- [ ] 明寫允許操作：Read 文件、grep / find / glob、git log / git show / git blame（read-only git 子指令）、bash 純查詢指令
- [ ] 輸出 schema：evidence bundle 含 `root_cause_guess`（一句話）+ `citations`（array of `{file_path, line_range, excerpt}`）+ `confidence`（0-1）
- [ ] INT-5 測試可在 spec 中描述（跑前後 git status 一致）

### 步驟

#### 撰寫 agent.md
- [ ] 開新檔，套既有 perspective agent 的 frontmatter / 段落結構
- [ ] **Perspective**：「對某個 cluster 的 poor verdict，從程式 + git 歷史 + telemetry row 三邊讀取證據，產生根因推論，但不做任何修補。」
- [ ] **Mission**：明列輸入（cluster 描述 + member_session_ids）→ 輸出（evidence bundle）
- [ ] **Principles**：read-only 鐵則、citation-first、root cause guess 必含「為什麼這個推論可被否證」一句
- [ ] **Lane-keeping**：列允許/禁止操作清單

#### 與 /triage 的串接介面
- [ ] 描述 /triage 派發時傳入的 prompt 結構
- [ ] 描述 evidence bundle 回傳格式（如何被 /triage 寫入 triage.jsonl）

#### 不變量驗證
- [ ] 在 agent.md 末尾加一條 self-check：「跑完此 agent 後 `git status --porcelain` 應與跑前一致」
