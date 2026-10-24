# seams — 每條接縫後面藏什麼、跨過它會變什麼、有哪些轉接頭

判斷標準照 `review/references/principles/structure.md` #4、#5：接縫要有兩個真的轉接頭才算數；深模組＝小介面蓋住大行為。這個形狀的取向是「讀者能不知道的，全部不讓他知道」，所以先列刻意**拿掉**的接縫，再列留下來的。

## 刻意拿掉的接縫

| 拿掉的東西 | 為什麼不需要 |
|---|---|
| `--doc`、`--compare`、`--symptom`、`--tool` 旗標 | 輸入種類從參數本身判斷（SKILL.md §1 的表），判斷結果在第一行說出來讓使用者更正。工具由問題決定（formal.md §Tool），不是使用者的事 |
| 獨立的 `maintain` 指令 | 同一個 `/hypothesis` 看到涵蓋的 area 過期就自動維護；`--maintain` 只是 auto-flags 規定的捷徑 |
| `.claude/hypothesis/index.md` 總表 | 腳本直接 glob `*/README.md`，沒有清單可以跟目錄脫節。prove-it 的 recipe 也不用再列形式檢查 |
| 給讀者看的 `references/reading.md` | 讀者要的東西由腳本印出來；讀者如果得開 `area.md` 才做得了事，就是介面漏了（area.md 開頭寫明） |
| 程式用 commit、文件用版本＋雜湊，兩種同步點 | 統一成「每個涵蓋檔案的 git blob hash」。`sync` commit 只留給 `--maintain` 當 diff 起點和給人看 |
| 讀者自己判斷過期 | 腳本在過期時不印「成立」，四個讀者結構上沒辦法誤報通過 |

## 留下來的接縫

### 1. 寫的一邊 ↔ 讀的一邊（`/hypothesis` ↔ `scripts/hypothesis.py`）

- **藏住的**：README 格式、同步點怎麼算、舊位置 `.claude/prove-it/formal/` 的存在、工具怎麼叫、TLC jar 在哪、寫入中的 draft 目錄。
- **跨過會變的**：讀者有六個（prove-it、hunt、review、紅綠確認綠燈、draft、health），各自拿去做不同的事；儲存位置有兩個（新、舊）。
- **轉接頭**：讀的一邊有兩個載入器——新 area（解析 front matter）、舊 area（不解析，一律顯示 `舊位置`）。讀者的用法差異不在腳本裡，在各自的 SKILL.md 一兩行。
- **為什麼是腳本、不是 skill 旗標**：讀者如果叫 `/hypothesis --status`，就是「讀者叫起寫入者」，只讀只能靠紀律；腳本根本沒有寫檔的程式碼，只讀由結構保證（計畫前提三）。

### 2. 輸入種類（`references/sources.md`）

- **藏住的**：怎麼讀來源、引用怎麼寫、什麼算一步、有哪些發現種類、哪些檔案進 `covers`。
- **跨過會變的**：程式、症狀、單一文件、兩份文件對照。
- **轉接頭**：四段，各回答同樣五個問題。SKILL.md §2–§7 不依種類分支；README、腳本、圖頁對每種輸入都一樣（`input` 欄位腳本不讀）。
- **試行就有兩個以上真的轉接頭**：程式考題和文件考題同一片（計畫「試行」段）。

### 3. 檢查工具（`hypothesis.py` 的 `ADAPTERS`，加上 `formal.md` §Tool）

- **藏住的**：執行檔、怎麼從輸出判斷成立或不成立、目標規則要反過來讀（`~Goal` 被違反＝目標到得了）。
- **跨過會變的**：TLC 安全規則、TLC 目標可達、之後的 Kani／Verus／Dafny／SMT。
- **轉接頭**：第一片只有 `tlc` 和 `tlc-reach` 兩個，都是試行會用到的。其他工具第一次用到時才加——現在寫就是只有一個轉接頭的假接縫。
- **順帶擋掉的風險**：執行檔由轉接頭決定，README 只能給參數，一份被動過手腳的 README 叫不起任意程式。

### 4. 開啟圖頁的環境

- **藏住的**：WSL2、Windows、Linux、macOS 各自怎麼開預設瀏覽器。
- **轉接頭**：照 `/show-me` 的寫法（`wslview`／`pwsh.exe Start-Process`／`xdg-open`／`open`），不另立規則。

## 不是接縫的東西（只是同一個事實的單一來源）

- **觸發清單 H1–H8**：只寫在 `formal.md` §Triggers。hunt 要知道 H1–H3 才知道何時提議，所以 hunt 引用這個錨點——這是讀者唯一要讀的規則文字，見 traps.md 第 9 條。
- **原因紀錄的格式**：只寫在 `formal.md` §Reason record。讀者只有在「使用者說不要寫」時才自己寫一行；其他所有「沒形式化」都由 `/hypothesis` 寫成一份 `cannot` 的 area，讀者不用懂四欄。
- **圖組規則**：只有 Mermaid 一個轉接頭，所以留在 `page.md` 裡，不立接縫。

## 讀者那一側要改的地方（不在這次草圖裡，列出來確認介面夠用）

| 讀者 | 加的一兩行 | 用到的介面 |
|---|---|---|
| `/prove-it` §3 | 宣稱的檔案有假說涵蓋 → `check <files>`；過期 → 判定過期、交回；不成立 → 照 README `## 發現` 在真 app 用強制順序重現。舊位置照今天的作法 | `check`、`## 發現` |
| `/hunt` Tool Scan | 多一列形式模型；H1–H3 或「加 log 行為就變」→ 提議 `/hypothesis <HUNT-id>`；每條 finding 轉成一個 yes/no 探針；一般猜測改叫「推測」 | `status`、`## 發現`、formal.md §Triggers |
| `/review` | 新 principle（或 `evidence.md` 一步）：改動檔案丟給 `status`，每條規則是必答題；過期回報 `coverage stale: needs /hypothesis` | `status` |
| `_shared/tdd.md` 綠燈 | `check` exit 0 才算綠 | `check` |
| `/draft` | 完成條件可寫成「`check <area>` 印出成立」 | `check` |
| `/health` | 驗證覆蓋那一層跑 `status`，列出過期與舊位置；環境急診認得 Java 與 `TLA2TOOLS_JAR` | `status` |
| `/ship` | `hypothesis/` 加進「永不歸檔」的說明與輸出字串；`ARCHIVE_DIRS` 不動 | 無 |
