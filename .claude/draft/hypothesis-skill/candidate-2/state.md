# state — 每份狀態歸誰，兩人同時寫、跑兩次、跑一半會怎樣

## 擁有者表

| 狀態 | 擁有者（唯一寫入者） | 讀者 | 放在哪 |
|---|---|---|---|
| area 的全部檔案（模型、variants、paths、README、diagrams、check.log） | `/hypothesis` | 人；`/hunt` 讀 `paths/`；`/prove-it` 讀 `model/` 跑 `--check` | `.claude/hypothesis/<area>/` |
| `hypothesis.json`（發佈紀錄：涵蓋、同步點、規則、結論、證據） | `/hypothesis` 的 publish 步驟 | 只有 `hypothesis-status.py` | 同上 |
| **讀者看到的狀態**（proved／stale／…） | **沒有人存它**——腳本每次讀時現算 | 所有讀者 | 不存在於磁碟 |
| 同步點（`sync.commit`、`sync.files` 雜湊、`sync.watch`、`sync.artifact`） | publish 步驟，只在檢查跑過之後 | 腳本 | `hypothesis.json` |
| `generation` | publish 步驟 | publish 步驟自己（CAS） | `hypothesis.json` |
| 重跑的結果 | 讀者自己（`/prove-it` 的紀錄、hunt 的 case file） | `/review` 讀 prove-it 紀錄 | 讀者自己的目錄，**永遠不回寫 area** |
| 舊位置 `.claude/prove-it/formal/<area>/` | 8.15.0 的 `/prove-it`（凍結，不再新增）；搬家時 `/hypothesis --maintain` 用 `git mv` 整個移走——同一個 area 任何時刻只在一處，舊的在時新位置拒寫 | `/prove-it`（legacy 讀法，結果最多「嚴格檢查未完成」）、腳本（列為 `legacy`） | 原位 |
| 文件的 Markdown 副本 | `/read --save` | `/hypothesis` | `.claude/read/` |
| 被拒絕寫假說的原因紀錄 | 拒絕的那個 skill（hunt、review） | 人 | 那個 skill 的輸出 |

關鍵設計：**「通過」不是一份存下來的狀態**。存下來的只有「在這些雜湊下，結論是 X」；「現在這些雜湊還對不對」每次都重算。所以沒有任何一份會過期的「通過」可以被讀到。

## 兩個寫入者同時寫同一個 area

情境：兩個 session（或同一個 repo 的兩個視窗）同時對 `approval` 跑 `--maintain`。

1. 兩者開始時都讀到 `generation = 4`。
2. 兩者都寫模型、variants……（area 檔案互相覆蓋——此時讀者看到 `draft`，因為 `sync.artifact` 雜湊對不上）。
3. A 先 publish：重讀 `generation` 還是 4 → 換上 tmp，`generation = 5`。
4. B 要 publish：重讀 `generation` 是 5 ≠ 4 → 停下、丟掉 tmp、回報「另一個 session 剛發佈了 approval，請重跑」。
5. 結果：B 寫過的模型檔可能蓋掉了 A 的 → `sync.artifact` 對不上 A 發佈的雜湊 → 讀者看到 `draft`，不會看到 `proved`。B 重跑後才回到乾淨狀態。

這不是完美的鎖（比較和換檔之間仍有極短的窗口），但失敗的方向一律是 `draft`／`stale`，不會是假的 `proved`：任何不一致都會讓雜湊對不上。

不同分支／worktree 各自發佈：`hypothesis.json` 跟著 git 走，合併時衝突是看得見的 JSON 衝突；解法是合併後跑 `--maintain`，不是手動挑一邊。

## 同一步跑兩次

- **寫下跑兩次**：第二次在 §1 就會看到已有 area。狀態是 `proved`／`disproved` → 不觸發，改成重跑。狀態是 `draft`（上次跑一半）→ 從 §2 重來，覆蓋 area 檔案，publish 時 `generation` 照常 +1。
- **`--maintain` 跑兩次**：第一次發佈後狀態已是 fresh，第二次的工作清單是空的，什麼都不做。冪等。
- **讀者跑兩次**：腳本唯讀，兩次輸出相同（除非中間有人改了檔案——那正是它要看見的）。

## 跑到一半停下

| 停在哪 | 磁碟上留下什麼 | 讀者看到什麼 |
|---|---|---|
| 確認規則前 | 什麼都沒寫（或只有 area 目錄） | 沒有 `hypothesis.json` → `draft` |
| 寫模型中 | 部分模型檔 | 首次：`draft`；維護中：舊 `hypothesis.json` 的 artifact 雜湊對不上 → `draft` |
| 跑完檢查、還沒 publish | 完整 area，舊 `hypothesis.json` | `draft`（artifact 變了） |
| 寫 tmp 時 | `hypothesis.json.tmp` | 腳本不讀 tmp → 同上 |
| `os.replace` 之後 | 完整新紀錄 | 新狀態 |
| 建 broken variant 的暫存副本時 | 系統暫存目錄裡的副本；product code 沒碰 | 不影響；下一次執行刪掉殘留副本 |

不存在「讀者看到新結論、卻配著舊模型」或反過來的組合：結論和模型的雜湊在同一個檔案裡，一次換上。

## 移動同步點的唯一條件

同步點只在 publish 時移動，而 publish 只在兩關證據都過了之後發生。`--maintain` 碰到無法分類的改動（`blocked`）時不 publish，讀者繼續看到 `stale`。沒有任何一條路徑能「只把雜湊更新到現在」而不重跑檢查。
