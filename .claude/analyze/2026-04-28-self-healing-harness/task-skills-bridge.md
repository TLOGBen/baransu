# Tasks: skills-bridge
**前置群組**：hooks, scripts

/bridge skill — head-to-head replay。Manual-only。實作載體在 bridge-replay script。

---

## TASK-skills-bridge-01: /bridge SKILL.md + references

**需求追溯**：REQ-005 Scenarios 1-4、INT-8、INT-9、KD#6
**目標**：寫 /bridge SKILL.md，描述「手動觸發、worktree 隔離（mktemp + trap）、N 條歷史 prompt replay、Δ ≥ 0.15 fail / 否則 pass」的完整流程；引用 bridge-replay script。
**驗收標準**：
- [ ] `plugins/baransu/skills/bridge/SKILL.md` 存在
- [ ] description 含 trigger phrases（「比較 skill 兩版本」「shadow run」「regression demo」）
- [ ] SKILL body 明寫：手動 only（不接 cron）；輸入是 target branch + 要比的 skill 名（可選 N corpus 大小、可選 `--allow-untrusted` flag）
- [ ] 流程包含：trust check → corpus check → mktemp → git worktree add → trap 設定 → 開 per-run report 檔 → replay 迴圈 → statistical gate → 寫 per-run report → cleanup
- [ ] 明寫「主 repo working tree 永不被 touch」這條 invariant
- [ ] **target branch trust check（S-F3 防本機 RCE）**：Stage 0 比對 target branch 最新 commit author email vs `git config user.email`，不一致 → 預設拒跑，`--allow-untrusted` 才綠燈；SKILL.md 明寫警語「v2 SKILL body 會以你的身分本機執行；只對自己信任的 branch 用 /bridge」
- [ ] **per-run report（A-F2 audit trail）**：每次 invocation 寫一個 jsonl 檔到 `.claude/harness/bridge-runs/bridge-{ISO_ts}-{branch_or_cluster}.jsonl`；單 writer、檔名隔離、無 race；內容含起始時間 / target branch / corpus size / 每筆 prompt v1/v2 score / Δ / 結論 / top-N 退化 prompt
- [ ] 引用 bridge-replay script 路徑

### 步驟

#### Frontmatter
- [ ] description 含 trigger phrases

#### Stage 描述
- [ ] Stage 0：環境檢查（telemetry corpus ≥ N、target branch 存在、無未 commit changes 在主 repo、**target branch trust check** — author email 比對 + 視 flag 決定拒跑或續跑）
- [ ] Stage 1：corpus 撈取（從 telemetry filter completed.prompt_text）
- [ ] Stage 1.5：開 per-run report 檔 `.claude/harness/bridge-runs/bridge-{ts}-{branch}.jsonl`、寫入 metadata（target / corpus_size / start_at）
- [ ] Stage 2：跑 bridge-replay script，每筆 prompt 結果 append 進 per-run report
- [ ] Stage 3：解析 script 結果（pass / fail / inconclusive）寫進 per-run report 結論欄；同時 echo 給 user
- [ ] Stage 4：cleanup 確認（再次驗證 worktree 已清，per-run report 已關）

#### 不變量檢查段落
- [ ] 明寫 invariant 1：worktree 在 `/tmp/baransu-bridge-XXX`，不在 repo 內
- [ ] 明寫 invariant 2：trap SIGINT EXIT 必須掛上
- [ ] 明寫 invariant 3：跑前後對主 repo `git status --porcelain` 結果一致（per-run report 寫入 `.claude/harness/bridge-runs/` 已 gitignore，不影響此 invariant）
- [ ] 明寫 invariant 4：target branch 預設拒非信任 author，flag 顯式覆寫

---

## TASK-skills-bridge-02: corpus 不足與 inconclusive 處理

**需求追溯**：REQ-005 設計 §錯誤處理策略
**目標**：定義 /bridge 在 corpus 太小或統計樣本不足時的 user-facing 行為。
**驗收標準**：
- [ ] /bridge 在 telemetry completed corpus < N（建議預設 N=20，可參數覆寫）時拒跑並印明確訊息（繁中）
- [ ] 跑完統計閘門但樣本太少 → 印 inconclusive，不誤回 pass / fail
- [ ] 拒跑 / inconclusive 時 worktree 仍正確清理（不留殘餘）

### 步驟

- [ ] /bridge SKILL Stage 0 加 corpus size 檢查
- [ ] bridge-replay script 在 inconclusive 情境也走 trap cleanup path
- [ ] 寫具體 user-facing 訊息（建議：「corpus 僅 X 條 completed row（門檻 N），暫時無法跑 head-to-head；累積至 N 條後再呼叫」）
