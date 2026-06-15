# Codex Port 施工圖：反慣性配重的牙齒重建

> **定位**：這不是「功能對映清單」，是「行為配重存續清單」。
>
> 每個 baransu 機制的本質，是對抗模型某個慣性的**配重**——不是 feature。所以 port 到
> Codex 的正確問句不是「Codex 有沒有對應的 API」，而是 **「降級後，還夠不夠力把模型
> 從那條捷徑上拽回來」**。
>
> 排序鍵：**牙齒是否 UI-bound × 對抗的慣性強弱**。降級最危險的地方，恰好是價值最高的
> 地方——把唯一的牙齒（UI 硬停）拔掉，留給模型的是它本來就最想走的捷徑。

---

## 通則：牙齒搬家，而不是降級

當原本的執行面（UI 硬停）沒得 port，**不要退而求其次變成 prompt 提示**——把牙齒搬到
一個能在 Codex 存活的面上。Codex 有這些可用面：

- **檔案前置條件**（artifact-gate）：下一步結構上需要上一步的產物檔。
- **phase 切分**：把「會抄捷徑」的階段與「無捷徑可抄」的階段拆開。
- **sandbox / approval gate**：deterministic 的機器閘。

共同原理：**模型沒法用嘴穿過去，因為下一步結構上需要上一步的產物。**

---

## Tier 0 — 強慣性 × UI 硬停：必須搬牙，不可降成提示

### T0-1　`/think` 對焦閘 → phase-split + alignment artifact

| 欄位 | 內容 |
|------|------|
| **對抗項目** | 模型「不跟使用者對焦就直接動手寫」的慣性 |
| **原因** | Claude 靠 AskUserQuestion 硬停；Codex 降成「列編號選項並等待」是軟約定，而 `/think` 對抗的*正是*穿過去的慣性本身——牙齒拔掉等於把模型放回它最想走的捷徑。全盤風險最高的一格。 |
| **Codex 動作** | 把 `/think` 切成兩段。**Phase 1 只產對焦問句然後停**，此階段在結構上沒有通往五段計畫的出口。**Phase 2 以使用者答案檔（`alignment.md`）為前置輸入**，缺檔則拒絕產出計畫。把「請對焦」（軟）變成「沒有對焦紀錄就生不出計畫」（硬）。 |
| **完成判準** | 在 Codex runtime 餵一個模糊需求，驗證它*無法*在未產生 `alignment.md` 的情況下吐出五段計畫；且 Phase 1 的輸出不含任何實作 / scaffolding / pseudo-code。 |

### T0-2　`/review`、`/health` 隔離牙齒 → 先驗證 Codex subagent context 是否真隔離

| 欄位 | 內容 |
|------|------|
| **對抗項目** | 模型「自我背書、橡皮圖章自己剛產出的東西」的慣性 |
| **原因** | 這兩個 skill 的反幻覺價值*來自乾淨的獨立 context*。若 Codex subagent 與主程共享 context 或更弱，隔離牙齒就鈍了——而這格在原 P-list 裡根本沒被標成風險。**這是 sleeper。** |
| **Codex 動作** | (a) 先做一次 runtime 探針——同一審查任務，確認 Codex subagent 拿到的是 fresh context 還是繼承主程記憶；(b) 若**真隔離** → 直接 port，標綠；(c) 若**不隔離** → 改用「獨立 invocation / 獨立 session 跑每個 perspective，結果寫檔再彙整」重建隔離，不可用同一 context 內連續提問假裝多視角。 |
| **完成判準** | 有一份探針結論文件說明 Codex subagent 隔離等級；review / health 的 Codex 版按該結論落定 port 策略（直 port 或 session 拆分）。 |

---

## Tier 1 — 牙齒不靠 UI 的好案例：port 成本低，別過度設計

### T1-1　`/execute` 紅綠閘 → 確認 runner 真的跑、gate 真的讀 exit code

| 欄位 | 內容 |
|------|------|
| **對抗項目** | 模型「沒測試就宣稱完成」的慣性 |
| **原因** | 這格牙齒是 deterministic 事實（測試紅 / 綠），兩個 runtime 都成立，**不需要搬牙**。風險只在於 Codex 端 gate 是否真去執行測試、而非讀 LLM 自述。 |
| **Codex 動作** | 確保 Codex 版 `/execute` 的紅綠判定來自實際 test runner 的 exit code（machine gate），sandbox 內網路 / 依賴可跑。維持 `failure_count` 排除 compile error 的語義（既有 invariant，勿合併計數器）。 |
| **完成判準** | Codex 端跑一個會失敗的測試，gate 確實 exit≠0 並擋住「宣稱完成」。 |

### T1-2　`/execute` 任務狀態 → TaskCreate/Update 改 durable `task-map.md`

| 欄位 | 內容 |
|------|------|
| **對抗項目** | 模型「多步驟丟失狀態、口頭宣稱 done」的慣性 |
| **原因** | Claude 的 Task tool 是內建狀態面；Codex 沒有對應內建，降成「口頭追蹤」= 慣性復活。 |
| **Codex 動作** | 以 `task-map.md` 作 durable source of truth，每次狀態轉移寫檔；有 `update_plan` 之類 runtime 顯示層時當*顯示*用，但真值永遠在檔。 |
| **完成判準** | 殺掉 session 後重啟，任務狀態能從 `task-map.md` 完整重建，無口頭依賴。 |

---

## Tier 2 — 機制收斂：把散落降級收成一張表

### T2-1　capability 降級表（帶**執行強度等級**，不只 strategy）

| 欄位 | 內容 |
|------|------|
| **對抗項目** | 跨 13 skill 的降級話術各寫各的，新 skill 會漏配重 |
| **原因** | ask_user / send_artifact / browser / tools→mcp 是同一 pattern 的多個 instance。但表的每格**必須記執行強度**（硬停 / artifact-gate / 軟提示），否則會把「AskUser→純文字」誤標成半綠。 |
| **Codex 動作** | 建 registry，每個 Claude 能力 token 對應 `{codex 等級, strategy, 對抗的慣性強度}`。transfer.py 掃到 token 查表注入。**strong-habit × 軟提示的格子一律退回 Tier 0 走搬牙路線**，不准只留提示。 |
| **完成判準** | 表存在；任一新 skill 的 port 不需手寫降級語彙即繼承正確等級；表能產出加權後的風險清單。 |

### T2-2　cosmetic AskUser → 直接降純文字編號選項

| 欄位 | 內容 |
|------|------|
| **對抗項目** | 無（這些是選模式，不是對抗慣性） |
| **原因** | `/read`、`/book`、`/design` 的 AskUser 只是選 gen/lint/source，無行為配重，降級無傷。**明確標為低優先，避免把力氣花錯地方。** |
| **Codex 動作** | 統一降成「列編號選項、停止等待回覆」即可，不需搬牙。 |
| **完成判準** | 三者 port 後選單可用；不投入 artifact-gate。 |

---

## Tier 3 — 低價值：降級無傷，最後做

### T3-1　`SendUserFile`（execute / review / think）→ 寫檔後列路徑

| 欄位 | 內容 |
|------|------|
| **對抗項目** | 無（純交付便利） |
| **原因** | weak-habit × 軟降級，自然排到最後。 |
| **Codex 動作** | 寫檔後列出絕對路徑；runtime 有附件面再用。 |
| **完成判準** | 檔案產出且路徑可見即可。 |

---

## 兩條貫穿全表的邊界（寫進每個 Codex 工作項的前提）

1. **目標上限是「重建逼停的牙齒」，不是「重建對焦 / 判斷的品質」。** Artifact-gate 能保證
   「沒答案就不准往下」，攔不住敷衍的答案——那是 runtime + 人的問題，不是 adapter 能補的。
   釘住這條，就不會掉進 differential testing 無底洞。
2. **authorization-PAUSE 與 input-PAUSE 要分開**：前者（驗收 / 授權）在任何 runtime 都維持
   硬停；後者（選項對焦）才適用降級。13 個 skill 幾乎都有 PAUSE，別一刀切。

---

## 優先序一覽

| 序 | 工作項 | 對抗慣性強度 | 牙齒來源 | 性質 |
|----|--------|:---:|------|------|
| 1 | T0-1　think 對焦閘 | 強 | UI → 搬到 artifact | 搬牙 |
| 2 | T0-2　review/health 隔離驗證 | 強 | UI → 驗證 runtime | 先探針再定 |
| 3 | T1-1　execute 紅綠 runner | 強 | deterministic（不搬） | 低成本 port |
| 4 | T1-2　execute task-map | 強 | 內建 → durable 檔 | 搬到檔 |
| 5 | T2-1　capability 降級表 | 機制 | — | 收斂 |
| 6 | T2-2　cosmetic AskUser | 無 | 直降 | 雜項 |
| 7 | T3-1　SendUserFile | 無 | 直降 | 雜項 |

---

## 機制歸位（grounding 依據）

以下為 canonical skills 的執行面原語掃描結果，本施工圖據此把機制安到正確的 skill：

- **AskUserQuestion**：analyze, book, design, hunt, read, review, think
  → 其中 think 為強慣性（對焦）；analyze/review/hunt 中等；read/book/design 為 cosmetic（選模式）。
- **隔離 subagent**：analyze, execute, health, review
  → 隔離*作為牙齒*的關鍵在 review / health。
- **紅綠 / 測試先行**：execute（核心）, health, hunt, learn, think
- **TaskCreate/Update / 狀態檔**：execute（唯一）
- **SendUserFile**：execute, review, think
- **PAUSE / gate**：13 skill 幾近全覆蓋 → 必須區分 authorization vs input PAUSE。
