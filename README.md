# baransu

> バランス。動手前先想，做完後驗證。

baransu 是一個簡單的練習：把「該輕的任務走輕量路徑、該重的決策不省思考」這套平衡哲學，包成一個 Claude Code plugin。共 15 個 skill，每個都有清楚的觸發界線——什麼能省、什麼一定要做。

---

## 核心理念

每條理念都綁一個倉內機制錨點——無錨點的條款不入冊，錨點存在性由結構驗證器把關。

| 理念 | 一句話 | 機制錨點 |
|---|---|---|
| 規則是天花板 | 只寫防真實翻車的規則；容器只能變深、不能變長 | `plugins/baransu/rules/anti-patterns.md` |
| 結構是地板 | 確定性檢查全走腳本閘門，不靠模型自律；15 個技能是上限（2026-07 修憲，附 codex-skill-transfer 三個月零使用即退役回 14 的可證偽條款） | `scripts/verify-skills.py` |
| 人在授權點 | Input PAUSE 可走預設；Authorization PAUSE 不可覆寫 | `plugins/baransu/skills/_shared/loop-contract.md` |
| 證據優先 | 非顯然主張依賴前先引查證來源；乾淨的 review 也是有效的 review | `plugins/baransu/skills/review/SKILL.md` |
| 狀態落盤 | 長流程的結論落檔交付、不賭終端顯示 | `plugins/baransu/skills/_shared/output-journal.md` |

---

## Skills

| Skill | 用途 |
|---|---|
| `/think` | 動手前對焦：三輪提問收斂方向，五節計畫釘住細節，拿到明確批准才實作。 |
| `/review` | 在乾淨 context 重讀已完成的工作，抓邊界沒守住、邏輯跳格、宣稱與實作對不上。 |
| `/hunt` | 從症狀追到根因：選對觀測層、log 二分法定位，指到 file:line 才動手修。 |
| `/health` | 體檢專案的 agent 配置與 AI 可維護性：五層審計，預算姿態先行。 |
| `/analyze` | 大頻段全管線：把需求展開成五層 spec（條文釘到可退件），再經內建執行段跑到全綠、產出 final-report。 |
| `/design` | 寫 UI/UX 設計規格：`gen` 引導生成、`lint` 挑違規、`preset` 套內建模板。 |
| `/contract` | 中頻段開工合約：一頁釘死目標、可斷言條文、錯不起表面、照抄常數，實作前先立約；sealed 合約覆蓋前先歸檔。 |
| `/seal` | 中頻段收工封緘：派遣乾淨 context 的 verify-only seal-agent 跑五點驗收（逐條對約、掃未釘表面、跨介面一致、常數逐字比對、突變抽查），findings 回主 session 修＋補釘死測試，複驗上限 2，全清才在合約蓋 sealed 標記。 |
| `/write` | 雙語寫作／潤色：套排版與風格規則，輸出 Before/After 與每處改動理由。 |
| `/evolve` | 把既有 SKILL.md 對著固定標準一輪輪磨好，只保留確有改進的改動。 |
| `/read` | 萬用擷取：URL／路徑／glob／Chrome／剪貼簿轉成離線 Markdown。 |
| `/learn` | 把素材整理成五欄重點摘要，可續寫成完整大綱筆記。 |
| `/book` | 把任何來源渲染成紙質風格的瀏覽器 HTML 閱讀頁，含 SVG 圖解與排版。 |
| `/codex-skill-transfer` | 把 Claude 的 skill／plugin 單向轉成 Codex 對應格式。 |
| `/ship` | session 收尾：歸檔工作檔與 root 的 sealed 合約、commit、push、清理 worktree。 |

### 三頻段路由（v3.0 起）

- **小**：直接實作（紅綠紀律見 `_shared/tdd.md` §7），不走任何 skill。
- **中**：`/contract` 開工立約 → 實作 → `/seal` 收工封緘。
- **大**：`/analyze` 一條管線走完規格與執行段。

任務不遷就工具：小任務不硬上全套，大任務不偷走輕量路。證據錨：`.claude/experiments/2026-07-19-harness-matrix/`（10-arm 矩陣＋驗證輪盲評）。

> ⚠️ **seal-guard hook（隨 plugin 生效，預設阻擋）**：session 結束時若偵測到未 `/seal` 的 user-facing 變更，會擋下並提示補 seal。降級：`SEAL_GUARD=log`（只記錄）或 `SEAL_GUARD=off`。遙測集中在 `~/.claude/baransu/telemetry/{專案}/{類型}-{YYYY-MM}.jsonl`，月回看檢討誤擋率（過高即降回 log 預設——可證偽條款）。

---

## 安裝

### Claude Code

```
/plugin marketplace add https://github.com/TLOGBen/baransu.git
/plugin install baransu@baransu
```

### Codex CLI（衍生變體）

```
codex plugin marketplace add https://github.com/TLOGBen/baransu.git
codex plugin add baransu@baransu
```

Codex 版是 Claude 的單向衍生產物，放在 `codex/` 子樹；不要直接編輯，會在下次 `/codex-skill-transfer` 轉換時被覆蓋。
