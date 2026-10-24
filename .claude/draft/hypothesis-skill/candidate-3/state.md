# state — 誰擁有哪份狀態，兩個人同時寫、跑兩次、跑到一半停掉會怎樣

## 擁有者

| 狀態 | 位置 | 唯一的寫入者 | 讀者 |
|---|---|---|---|
| 假說本體（README、model/、sources/、page.html） | `.claude/hypothesis/<area>/` | `/hypothesis` | 全部讀者，透過狀態腳本 |
| 進行中的執行 | `.claude/hypothesis/.staging/<area>-<run-id>/` | 該次 `/hypothesis` 執行 | 沒有；讀者略過 |
| 同步點 | README frontmatter `sources[]` | `/hypothesis`，只在關卡 2 於新來源上再過一次之後才移動 | 狀態腳本 |
| `status`、每條規則的結果、關卡紀錄 | README frontmatter 和規則表 | `/hypothesis` | 狀態腳本 |
| `stale`、`legacy` | **不存**，每次由狀態腳本算 | 沒有 | 全部讀者 |
| `revision` | README frontmatter | `/hypothesis`，每次換入 +1 | 第 8 步的衝突檢查 |
| 文件快照 | `sources/<slug>.md` | `/hypothesis`；每個同步點一份，同步點不動就不改 | 來源 adapter 的 Cite／Diff |
| 舊位置的檢查 | `.claude/prove-it/formal/<area>/` | 本次改版後**沒有人寫**；只有 `--maintain` 的搬家會 `git mv` 它 | `/prove-it`（搬家前）、狀態腳本（標 `legacy`） |
| prove-it 的紀錄（重跑結果、真實 app 重現） | `.claude/prove-it/records/` | `/prove-it` | `/review` |
| hunt 的探針與原因紀錄 | `.claude/hunt-report/HUNT-*.md` | `/hunt` | — |
| 重跑時的暫存輸出（TLC `states/`、cargo `target/`） | `$HYP_TMP`，由呼叫者指定 | 呼叫者 | 沒有 |
| 改壞的副本 | repo 外的暫存目錄，或 `model/` 裡的變體 cfg | 該次 `/hypothesis` 執行 | 沒有 |

`stale` 不存，是這個形狀最重要的一個決定。假說不可能知道來源什麼時候被改，寫進檔案的「新鮮」只會說謊。

## 兩個寫入者

- **兩個 `/hypothesis` 在同一個工作樹、同一個 area**：各自在 `.staging/` 下有自己的 run-id，互不干擾。第 8 步換入前，比對磁碟上 README 的 `revision` 和開始時讀到的值：
  - 一樣 → 換入，`revision` +1
  - 不一樣 → 不覆蓋。回報「approval-withdraw 在這次執行期間被另一次執行更新過（revision 4 → 5），這次的結果留在 `.staging/…`」，交給使用者決定要不要重跑
- **兩個 worktree 各自更新同一個 area**：兩邊的 `.claude/hypothesis/` 都進 Git（它是保留產物），合併時在 README 上衝突，照 `/ship` 的衝突處理。frontmatter 的 `revision` 衝突本身就是訊號：兩邊都要重跑一次，不能挑一邊的數字。
- **讀者想寫**：結構上不可能自然發生，因為讀者只呼叫腳本和 `tool.command`。唯一的漏洞是重跑指令本身有副作用（TLC 會在當下目錄寫 `states/`），所以工具 port 規定指令一定要把暫存輸出導到 `$HYP_TMP`。關卡紀錄裡加一條檢查：在產物目錄跑過一次指令後，`git status` 在 `<area>/` 底下必須是乾淨的。
- **`/prove-it` 和 `/hypothesis --maintain` 同時跑**：prove-it 開始時拿到的是 revision N 的指令和路徑。maintain 換入 N+1 之後，prove-it 的紀錄寫的是 N 的同步點和模型雜湊，所以它證明的是舊版。讀者用的時候，比對紀錄裡的 revision 跟現在的 revision，不一樣就當成沒證明過。

## 跑兩次

- **同一個來源、同一個同步點，再跑一次 `/hypothesis`**：觸發清單的「不觸發」第五條（已經有一份同步中的假說）讓它變成**重跑**，不是重寫：只跑 `check.cfg`，結果一樣就不換入（`revision` 不動），page 不重產。
- **`--maintain` 跑兩次**：第二次時，同步點已經移到 HEAD，`Diff since sync` 是空的，每份都是 `in sync`，不寫任何東西。
- **搬家跑兩次**：第一次 `git mv` 之後舊目錄已經不在；第二次找不到 legacy，什麼也不做。如果搬到一半（新目錄已經建好、舊目錄還在），腳本會看到同一個 area 出現在兩處，回報衝突，**新位置優先**，舊位置標 `legacy: true, shadowed: true`。下一次 maintain 會把殘留的舊目錄收掉（先問使用者，因為這是刪除）。

## 跑到一半停掉

| 停在哪裡 | 留下什麼 | 下一次怎麼處理 |
|---|---|---|
| 規則確認前／後 | `.staging/<run>/claim-sheet.md` | 下次同一個 area 開始時，看到 staging 就問：「上次停在規則確認，要接著做還是丟掉？」丟掉要使用者同意 |
| 模型寫到一半、關卡跑到一半 | staging 裡的 model 和關卡紀錄 | 同上；從頭跑關卡 1，因為關卡的順序是保證的一部分 |
| 改壞的副本建了還沒清 | repo 外的暫存目錄 | staging 的 `manifest` 記錄每一個暫存路徑；接續或丟棄時清掉。**改壞的版本永遠不碰使用者的工作樹**，所以停掉不會留下壞掉的產品程式碼 |
| 換入當中 | 先寫新 README 到 `<area>/README.md.new`，其他檔案已換好 | 換入的最後一步是把 `.new` 改名成 `README.md`。腳本只讀 `README.md`，所以讀者看到的一定是舊的完整版或新的完整版；`revision` 也是跟 README 一起變 |
| page 開不起來 | 檔案已在，瀏覽器沒開 | 結尾那一行照樣印出路徑，不算失敗 |

## 同步點的生命週期

```
（沒有）──第 8 步首次換入──▶ 同步點 S0
S0 ──來源改了──▶ stale（腳本算出來，不寫）
stale ──--maintain：四類分類、更新、關卡 2 在新來源再過一次──▶ S1
stale ──--maintain：blocked──▶ 同步點不動，維護紀錄寫一列 blocked，仍是 stale
```
