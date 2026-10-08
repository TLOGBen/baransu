# 構想家族：think · contract

<img src="../images/family-plan.png" width="320" alt="構想家族概念圖">

> 動手之前，先把「要什麼」和「怎樣才算做完」說清楚。

`/think` 處理還沒定案的方向；`/contract` 處理已經定案、要開工的中型任務。兩者都不寫程式。

[← 回文件索引](../README.md)

---

## `/think`

Claude Code：`/baransu:think`　Codex：`$baransu:think`

**用途**　動手前審議：先復述你要的東西對焦，表態並說明押在什麼上，查證前提，正反兩向攻擊，呈現，落一份五段計畫到 `.claude/think/`。不寫程式、不交棒；已定的決定也可拿來拷問。

**什麼時候用**
- 有一個還沒決定的點子、功能、重構或方向，想問怎麼設計、走哪條路、值不值得做。
- 觸發語：想一下、幫我想、怎麼設計、值不值得、該不該做、「我想做 X 但還不確定」。
- 已經做好的決定想被拷問：拷問我、grill me。
- 存廢判決（Kill / Keep / Pivot）也在這裡做——`/hunt` 的「值不值得修」、`/evolve` 的「這個 skill 該不該存在」都轉來這裡。

**流程**　對焦復述 → 表態並點名押注 → 查證前提（每條標「已查證」或「未實查」）→ 兩向攻擊（會壞在哪、哪裡做過頭）→ 用一般人看得懂的方式呈現 → 落計畫檔後停。

**產出**
- 對話中：確認過的復述、立場與押注、前提查證標記。
- 可落地的工作：`.claude/think/<slug>.md`，最上面是復述，下面五段計畫。
- 判決（Kill / Pivot）或拷問既有決定：只給立場，不寫計畫檔。
- `/ship` 收工時會歸檔 `.claude/think/`。

**不適用**
- 排查既有錯誤 → `/hunt`
- 已定案的工作要釘驗收條文 → `/contract`
- 單檔小修 → 直接實作，照 `_shared/tdd.md` §7 的紅綠紀律

**非互動驅動**　`loop=not-drivable`（需要使用者確認復述，不適合 /loop、cron、Workflow 無人驅動）。

---

## `/contract`

Claude Code：`/baransu:contract`　Codex：`$baransu:contract`

**用途**　中頻段開工合約：一頁釘死目標、可斷言條文、錯不起表面、照抄常數，實作前先立約；sealed 合約覆蓋前先歸檔。

**什麼時候用**
- 一個值得釘住驗收的中型功能，實作之前。
- 觸發語：`/contract`、寫合約、一頁合約、開工合約、pin the criteria。
- 參數：`<一句話任務描述>`

**合約四段**（約 35 行，寫在專案根目錄的 `CONTRACT.md`，或你指定的路徑）

| 段落 | 內容 |
|---|---|
| 目標 | 這次要達成什麼 |
| 可斷言條文 | 每條都能被測試判定；使用者看得到的文字一律寫成精確格式或禁止清單，不接受「包含某字串」 |
| 錯不起表面（Surface Inventory） | 改錯就出事、必須逐一檢查的介面 |
| Verbatim Constants | 必須逐字照抄的常數 |

**產出**　`CONTRACT.md`，以及確認時逐條列出的可斷言判定（可斷言／已改寫）。使用者確認一輪即完成。

**合約生命週期**
- `/contract` 擁有 sealed 標記的語法；`/seal` 全清時才在合約第 2 行蓋 `> STATUS: sealed`。
- 偵測 sealed 只讀檔案前 3 行（`head -3 "$f" | grep -qF '> STATUS: sealed'`），不做全檔搜尋，避免合約自己的 Verbatim Constants 裡出現同一字串而誤判。
- 要寫新合約、而現有合約已 sealed：先歸檔到 `.claude/archived/{filename}-{unix_timestamp}`（一律加時間戳），再寫新的。

**不適用**
- 跨多模組、尚未切片的大型工作 → 先切片，每片各立一份合約
- 做完之後的驗收 → `/seal`

**非互動驅動**　`loop=drivable`。
