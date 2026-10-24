# seams — 每條接縫後面藏什麼、什麼會變、有哪些 adapter

判準照 `review/references/principles/structure.md` 第 4 條：接縫兩邊要真的有東西在變，而且今天就有兩個以上的 adapter。只有一個 adapter 的接縫是假想的，要內聯回去。下表最後一欄就是這個檢查。

## 1. 來源 port（`references/sources/`）——真的接縫

- **藏住的東西**：怎麼讀（直接讀程式／經 `/read --save` 轉 Markdown）、引用長什麼樣、引用怎麼驗證（`git show` 有那幾行／原文逐字出現在快照裡）、什麼叫「一步」和「不可分割」、同步點欄位、過期規則、改壞的版本怎麼做、反例怎麼對回來源、發現叫什麼名字、維護時改動怎麼列。
- **會變的**：上面十件事每一件，在程式和文件之間都不一樣。這是今天就看得到的差異，不是預留彈性。
- **adapter**：
  - `code`：任何語言。語言只影響工具選擇，不影響這個 adapter。
  - `document`：訪談、會議紀錄、RFP、SA、SD。
  - `pair`：**組合型**。包住另外兩種 adapter，自己只加「誰當規則、誰當行為」和精化對應。所以「文件對文件」「程式對文件」「新版程式對舊版程式」都不用新 adapter。
- **不是 adapter 的**：
  - **文件子類型**（RFP、SA…）：citation、sync、stale 完全一樣，只差「先找什麼」，所以是 `document.md` § Profiles 的一列。
  - **hunt 的症狀**：是主張的起點（`--seed`），來源還是 `code`。
  - 會讓我開新 adapter 的，是**引用或同步方式不同**的來源，例如 BPMN、OpenAPI、Figma 流程。
- **新增一種來源**：加一個 `sources/<kind>.md`（十節固定標題），在 `hypothesis-status.py` 的 `STALE` 加一個函式，通過該 kind 的已知答案考題。核心和工具 adapter 都不動。

## 2. 工具 port（`references/tools/`）——真的接縫

- **藏住的東西**：模型語言、安裝檢查、版本、怎麼把規則表寫成模型、安全規則怎麼寫、「看過它成功」怎麼做（TLC：`~Goal` 當不變式必須被違反；Kani：`kani::cover!`）、改壞怎麼落地、唯一的重跑指令和它的暫存輸出放哪、輸出怎麼讀回正規化路徑、範圍怎麼寫。
- **會變的**：模型的形狀（轉移系統 vs. 直接驗程式）、反例的形狀（`path` vs. `witness`）、範圍的意義（常數 vs. unwind）、副作用（TLC 的 `states/`、cargo 的 `target/`）。
- **adapter**：`tlc`（預設，本機已有已知答案考題可跑）、`kani`（H7 的代表）。兩個的差異涵蓋了 port 的兩種形狀，所以這條接縫今天就有兩邊。
- **還沒收錄的**：Verus、Dafny、SMT（H5）、證明工具（`--unbounded`）。需要時結果是「無法寫成假說」，原因類別「沒有工具」，具體情況寫「adapter 未收錄」。新增一個工具 = 一個 `tools/<name>.md` + 它的考題。
- **選工具**在核心（SKILL.md 第 3 步）：拿規則表的 `shape`、觸發列的預設、語言、`--unbounded`，去比對每個 adapter 的 § Capability。adapter 不參與挑選，只回答「我能不能」。

## 3. 兩個 port 交會的地方（`references/ports.md` 的表單）

這是跨接縫唯一的語言。沒列在這裡的欄位，就不准跨接縫。

| 表單 | 誰產生 | 誰消費 | 為什麼放在中間 |
|---|---|---|---|
| 規則表（claim sheet） | 來源 § Extract | 核心第 2 步、工具 § Encode、圖組 | 讓工具不用知道來源是程式還是文件 |
| 對應表 | 工具 § Encode | 核心關卡 1、來源 § Replay | 動作名 → 引用，兩邊都要 |
| 改壞紀錄 | 來源 § Mutate 寫「改哪裡」 | 工具 § Realize 寫「怎麼跑」 | 「看過它失敗」需要兩邊合作：來源知道什麼叫壞，工具知道怎麼跑壞的版本 |
| 正規化路徑（`path`／`witness`） | 工具 § Read the result | 來源 § Replay、圖組、hunt 的探針 | 圖組和 hunt 因此跟工具無關 |
| 判定值 | 核心 | README、狀態腳本、讀者 | 一套詞彙 |

## 4. 讀者介面（`scripts/hypothesis-status.py`）——facade，不是 port

- **藏住的東西**：README frontmatter 的解析、舊位置（`prove-it/formal/`）的相容、每種來源的過期判斷。
- **會變的**：讀者有六個，但它們要的都是同一件事：「哪些假說涵蓋這些檔案、狀態是什麼、過期了沒、怎麼重跑、反例是什麼」。所以這裡是**一個介面給很多呼叫端**，沒有 adapter。
- **為什麼要是程式而不是文字**：計畫的成功標準要求四個讀者都回報「過期」、沒有一處回報「通過」。四份文字各自描述過期規則，一定會飄掉；一個函式只有一份。
- 它裡面的 `STALE` 表，是來源 port 唯一需要能執行的那一節。

## 5. 刻意不設的接縫

| 候選接縫 | 為什麼不設 |
|---|---|
| 圖的繪製器（Mermaid／Graphviz／`/draw`） | 只有 Mermaid 一個 adapter；`/draw` 由人手動叫用。設了就是假想的接縫 |
| 每個 H 列一個流程 | H 列決定「要不要寫」和預設工具，不改流程；一張表就夠 |
| 每種程式語言一個來源 adapter | `file:line` 對所有語言都一樣；語言差異只在工具能力 |
| 讀者 adapter（prove-it 版、review 版…） | 讀者在別的 skill 裡；這邊只提供一個 facade |
| 規則確認的互動方式 | 只有對話一種；loop=not-drivable |
