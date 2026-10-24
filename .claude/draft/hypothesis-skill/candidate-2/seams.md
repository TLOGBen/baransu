# seams — 每條接縫後面藏什麼、跨過它會變的是什麼、有哪些轉接器

依 `structure.md` #4：一條接縫要有東西真的在變，至少兩個轉接器才算數。這個形狀只有五條，並刻意刪掉一條（索引檔）。

## 1. 讀者接縫：`hypothesis-status.py`（這個形狀的主軸）

- **藏起來的**：目錄結構、`hypothesis.json` 的 schema 版本、雜湊演算法（`sha256-lf`）、watch pattern 的 `git grep`、狀態的判定順序、舊位置 `.claude/prove-it/formal/` 的存在、「過期時把結論藏起來」這條規則。
- **跨過它會變的**：
  - 讀者這一側：`/review`、`/hunt`、`/prove-it`、`/health`、紅綠綠燈、`/draft`——六個讀者，問的問題不同（誰涵蓋我改的檔案／某個 area 過了沒／全部列出來）。
  - 儲存這一側：schema v1、舊位置（legacy）、以後的 v2。
- **轉接器**：
  - 選擇器：`--diff`、`--files`、`--area`、`--all`（讀者問「誰涵蓋」的四種問法）
  - 細節檢視：`--rules`、`--paths`、`--scope`、`--check`
  - 儲存：`compute_state`（v1）、`legacy_rows`（舊位置）
  - 輸出：表格行、`--json`
- **為什麼是深模組**：讀者要知道的只有「7 個狀態 + 一張表」，背後的雜湊、grep、CAS、schema 都不用知道。刪掉它，複雜度會散回六個讀者 skill 各自去比 commit——正是會有人把過期讀成通過的地方。
- **接縫的另一半：`references/reading.md`**。腳本回答「是什麼狀態」，reading.md 的「狀態 × 讀者」表回答「那我該做什麼」。各讀者 skill 只加一行引用，不各自重寫規則（單一來源）。

各讀者 skill 要改的（不在本草稿內畫，但形狀依賴它們）：

| 讀者 | 改的地方 | 一行的內容 |
|---|---|---|
| `/review` | `principles/index.md` 加一列 `hypothesis.md`（walk 階段，觸發：`--diff` 有列） | 跑腳本；照 reading.md 表 |
| `/hunt` | Tool Scan 加一列；side-effect rule 後加一句；「假說」改名「推測」 | 跑腳本；`disproved` → `--paths` 變探針 |
| `_shared/tdd.md` | §7.2 第 4 步 | 綠 = exit 0 或 10 |
| `/draft` | 定義完成的寫法 | 驗收 = `--area X` exit 0 |
| `/prove-it` | §3 的 every-case 那條、Output、recipe 的 Formal checks 節 | 跑腳本；legacy 照舊 |
| `/health` | 驗證覆蓋層 | `--all`，列非 proved/disproved |

## 2. 工具接縫：檢查器轉接器

- **藏起來的**：各工具的指令列、輸出格式、反例軌跡的長相。
- **跨過它會變的**：TLC（預設）、Kani／Verus／Dafny（H7）、SMT（H5）、以後的證明工具（不設範圍時）。
- **轉接器的共同輸出**（`formal.md` § Tool adapter output）：工具＋版本、一條鎖定的指令、每條規則 held/violated、每個違反的軌跡對到模型部件、探索了多少、秒數。做不到其中一項的工具，不能拿來寫假說。
- 這條接縫現在只有 TLC 一個真的跑過（簽核考題）。依 #4，它是「有第二個轉接器的承諾」，在 H7 第一次出現時才補第二個；在那之前，`formal.md` 只寫輸出合約，不寫 Kani 的細節。

## 3. 來源接縫：程式／症狀／文件／兩份文件

- **藏起來的**：怎麼讀來源、怎麼引用（`file:line` 或 原文＋位置）、雜湊什麼（程式檔 或 文件原檔）、有沒有 watch pattern（文件沒有）。
- **跨過它會變的**：四種輸入；但產出同一種 area。
- **轉接器**：`references/sources.md` 的四節；文件轉換交給 `/read --save`（不自己解析 PDF）。
- 讀者完全看不到這條接縫：文件 area 和程式 area 在狀態表上長得一樣，只是 `--files` 給的是文件路徑。

## 4. 呈現接縫：模型 → 圖組

- **藏起來的**：怎麼從模型挑出「正常流程」、加元件的順序、Mermaid 語法。
- **跨過它會變的**：程式來源與文件來源的標籤用詞；只有一個轉接器（Mermaid HTML）。
- 依 #4 這不是真接縫，所以不做成可替換的東西：`diagrams.md` 就是規則本身。使用者要簡報級的圖，手動叫 `/draw`，那是另一個 skill，不是這裡的第二個轉接器。

## 5. 寫入接縫：publish（CAS on `generation`）

- **藏起來的**：寫檔順序、雜湊、tmp + `os.replace`、generation 比對。
- **跨過它會變的**：`/hypothesis` 的兩種寫入者：首次寫下（§2–§5）與 `--maintain`（§6）。兩者都只透過同一個 publish 步驟讓讀者看到結果。
- **為什麼值得**：讀者看到的狀態只會在 publish 的那一刻改變；中途停下、兩個 session 同時寫，都不會讓讀者看到半套東西（見 `state.md`）。

## 刪掉的接縫：索引檔

考慮過 `.claude/hypothesis/INDEX.md` 或 `index.json`（檔案 → area 的反查表），刪掉了：

- 它是第二份狀態，要跟每個 `hypothesis.json` 保持一致；兩個寫入者會讓它跟 area 各自漂移。
- 反查要的資料（`sync.files`、`sync.watch`）本來就在每個 `hypothesis.json` 裡；腳本每次讀時現算，成本是讀幾個 JSON、雜湊幾十個檔案、跑幾次 `git grep`，一秒內。
- 刪除測試：刪掉索引，複雜度消失；所以它原本只是轉手。
