# /baransu:hypothesis 的形狀

## 問題

計畫（`.claude/think/formal-hypothesis.md`）要一個 skill，負責**寫下**假說：

- 一律是形式模型，附白話規則和逐張加元件的狀態圖
- 輸入可以是程式、`/hunt` 的症狀、文件，或兩份文件對照
- 它擁有 `.claude/hypothesis/`，負責維護；`/prove-it`、`/review`、`/hunt`、紅綠、`/health` 只讀

形狀不明顯的原因有三個：

- **讀者有五個以上**，每次改程式都會讀。只要其中一個把「過期」誤讀成「通過」，整套就變成假證明。
- **「過期」這個狀態沒有人會記得去更新**：存在檔案裡，一定會說謊。
- **生命週期假說**（`.claude/hypothesis/hypothesis-lifecycle/`）已經用 TLC 窮舉出五條必須擋下的路徑：
  - ① 過期時說通過
  - ② 過期後沒人維護，永遠做不完
  - ③ 綠燈只提醒，改壞的程式被放行
  - ④ 新舊兩份並存，讀到沒人管的那份
  - ⑤ 沒做過嚴格檢查的舊檢查，被拿來宣告完成

grounding 找到的限制：

- 8.15.0 的 `/prove-it` 已經用 `.claude/prove-it/formal/`，搬家前不能斷
- review 只讀不寫（`review/SKILL.md:39`）
- `/ship` 只歸檔白名單內的目錄
- 每個檔案都有 Codex 鏡像
- 本地 repo 停在 8.11.0（這份骨架寫在 8.11.0 上，見待決問題）

## 用法

寫的那一側（偶爾）：

```
/baransu:hypothesis src/approval/            → 第一行：「判斷為：程式」
/baransu:hypothesis HUNT-2026-014            → 第一行：「判斷為：症狀」
/baransu:hypothesis docs/簽核需求訪談.docx   → 第一行：「判斷為：文件」
/baransu:hypothesis docs/SD.md --satisfies docs/SA.md
/baransu:hypothesis --maintain approval
```

讀的那一側（每次改程式都會讀），所有讀者都只用這一行：

```
python3 "$CLAUDE_SKILL_DIR/../hypothesis/scripts/hypothesis-status.py" --diff <base>
approval  stale  3  a1b2c3d  changed: src/approval/service.py
```

讀者再拿 `state` 去查 `references/reading.md` 的「狀態 × 讀者」表，照表做事，不自己判斷。例如紅綠綠燈看到 `stale`，就是紅燈，並立刻叫 `/hypothesis --maintain approval`，維護完再重跑這一行，印出 `proved` 才過。

## 形狀

**資料結構**：一個區塊（area）一個目錄。

- `hypothesis.json`：機器讀的，最後才寫，靠比對 `generation` 防止互相覆蓋
- `README.md`：人讀的
- 模型
- `variants/`：故意改壞的版本
- `paths/`：反例劇本
- `diagrams.html`：狀態圖組

`hypothesis.json` 存三樣東西：涵蓋檔案的**內容雜湊**、對守護狀態的**寫入樣式**、看過失敗與看過成功的**證據**（`references/artifact.md`）。

**讀者看到的狀態不存檔**，由腳本在讀的那一刻算出來，只有七種，判定順序寫死：

`broken` → `draft` → `stale` → `legacy` → `proved` / `disproved` / `unformalized`

- 只有 `proved` 能算「通過」。
- 不是 `proved` 或 `disproved` 時，每條規則的結論都印成 `?`，讀者想誤讀也誤讀不了。這擋下路徑 ①。依據：`structure.md`（狀態只有一個主人）、`readability.md`（讀者不需要判斷）。

**一處寫、多處讀**：只有 `/hypothesis` 寫；讀者只跑腳本，`--check` 的重跑也在暫存目錄裡做，結果寫進讀者自己的紀錄。

**`--maintain` 由讀者自動叫起**（`loop=assisted`），只有在「承諾是刻意改的」時才停下來問人（`references/loop-pauses.md`）。這擋下路徑 ②、③。

**一個區塊只住一處**：舊位置還有同名區塊時，必須先搬。舊檢查不論搬了沒有，最好的結果都只是「嚴格檢查未完成」。這擋下路徑 ④、⑤。

**輸入種類由參數自己判斷**，第一行說出判斷結果讓使用者更正。唯一保留的旗標是 `--satisfies`，因為兩份文件哪份是規則、哪份是行為猜不出來。

**刻意不做的**：

- 沒有索引檔（多一份會漂移的狀態）
- 讀者不開 `hypothesis.json`，也不比對 commit
- `/review` 不叫寫入者（由主 session 叫）
- 沒有 `--tool`、`--doc` 之類的旗標

## 選擇

| 候選 | 位置 | 篩選結果 |
|---|---|---|
| 1 最小介面 | `.claude/draft/hypothesis-skill/candidate-1/` | 入口最小，判斷輸入種類的做法最好。但「讀者也從不叫起寫入者」違反生命週期 L1（路徑 ②）；「兩邊都有時用新的」違反 S4（路徑 ④）；`/prove-it`「照今天的方式讀舊的」違反 S5（路徑 ⑤） |
| **2 讀者最省事（基底）** | `.claude/draft/hypothesis-skill/candidate-2/` | 五條路徑全部擋下；讀者合約是一張表，不需要判斷。它做到一半讀到更新過的計畫，所以佔了資訊上的便宜，但結果仍然成立 |
| 3 驗證工具當埠口 | `.claude/draft/hypothesis-skill/candidate-3/` | 來源和工具分開設埠口，切法清楚。但 `not-drivable` 違反 L1（路徑 ②），沒有寫搬家前怎麼處理舊檢查 |

**嫁接進來的**：

- 從候選一：參數自動判斷輸入種類並在第一行說出（`SKILL.md` §2、`sources.md` §Symptom）；重跑結果和紀錄不符時算 `broken`（`reading.md` §Detail views）；網址文件每次維護都重抓（`sources.md` §One document）
- 從候選三：工具 adapter 要先通過已知答案考題才收錄（`formal.md`）

**不收的**：

- 候選三的完整埠口目錄結構：目前只有 TLC 一種工具真的跑過，接縫兩邊沒有東西在變（`structure.md` 第 4 條）。等第二種工具通過考題再拆。
- 候選一的「讀者不叫寫入者」：被模型推翻。

**三個候選的共識**：三個都獨立加了一支唯讀的 Python 狀態腳本，也都決定「過期不存檔，讀的時候現算」。這是強共識，原樣收下。repo 已有前例（`read/scripts/search-papers.py`）。

## 後置條件

實作時必須做到：

1. 讀者繞過腳本、直接讀 `hypothesis.json` 的舊結論：結構只防得住一半。`review` 的 principle 要明文禁止，`/health` 要能抓到。（候選二陷阱 1）
2. 腳本跑不起來，不能被當成「沒有假說」：exit 2 一律算 `broken`；Windows 上只有 `python` 沒有 `python3` 時要能解析。（候選二陷阱 2）
3. 過期太頻繁、大家開始忽略：要量。試行時記下每次 `--maintain` 的歸類，「沒有影響」佔太多就考慮把顆粒變細。（三個候選都列了）
4. 新的寫入者漏抓：寫入樣式是下限，`--maintain` 必須重新搜尋每個模型變數的寫入者，不能只看 diff。（三個候選都列了）
5. 「故意改壞」必須在暫存副本裡做，不能在工作目錄做；否則雜湊會算在壞掉的版本上。（候選二陷阱 10）
6. TLC 會在當下目錄留下 `states/`，讀者重跑必須在暫存目錄。（候選三）
7. Codex 鏡像的 `$CLAUDE_SKILL_DIR` 能不能解析到 `../hypothesis/scripts/`，要在鏡像時用 `/codex-skill-transfer` 查證。（候選二、三）
8. `/ship` 的「never archived」清單要加上 `hypothesis/`，Step 1 和 Step 2 兩處要一致。（候選二陷阱 16）
10. **`/prove-it` 的食譜**：拿掉「Formal checks」清單，改成一行「跑 `hypothesis-status.py --diff <base>`，照 `reading.md` 的表做」；Doctor 在有假說涵蓋時檢查 Java 與 TLC。（使用者決定：照建議）
11. **劇本步驟對應功能地圖**：不存檔。`/prove-it` 每次重現時現場對應，寫進它自己的紀錄。找不到對應功能的步驟，`/prove-it` 先補一份功能檔，再接著重現。（使用者決定：補一份）
12. **hunt 案件檔**：每個推測記下它來自哪條路徑（`P1`…）。修好之後，綠燈看到「過期」會自動維護；維護就算停下來問人，hunt 案件照樣結案，待回答的問題留在假說的「過期」狀態裡，由其他讀者繼續回報。（使用者決定：算結案）
13. **hunt 建案時機**：hunt 現在要到 Locate 階段才建案件檔（`hunt/SKILL.md:135`），但 Tool Scan 在它之前就可能選中形式假說，這時還沒有 HUNT-id。Tool Scan 選中形式假說時，要先建案件檔再叫 `/hypothesis <HUNT-id>`；或者交給 `/hypothesis` 一句症狀加上路徑，之後再把 HUNT-id 補回假說。
14. **hunt 改名是前提**：hunt 現在把一般猜測叫「假說」。在第三片改名為「推測」之前，「先幫我建立假說」在 hunt 裡會被讀成 hunt 自己的猜測清單。使用者決定：英文 hypothesis 全部改成 conjecture，中文「假說」改成「推測」，本文、範本、Claude 版與 Codex 版一起改。
15. **draft 的兩種用法**：
    - 已經有假說涵蓋要改的區域時，用假說篩選候選，每個候選逐條對照規則，像這次用生命週期假說篩選三個候選。
    - 選定的骨架碰到 H1–H8 時，對骨架寫一份設計期假說，涵蓋骨架檔案，在 draft 同一個停點給使用者看。

    填內容時涵蓋檔案會變，綠燈看到「過期」就自動維護，模型改成描述真程式。`reading.md` 現在只把 `/draft` 列成讀者，這兩種用法要寫進 draft 和 `reading.md`。
16. **兩份來源可以是程式**：`--satisfies` 的兩邊都可以是程式或文件，而且可以從「A 是否滿足 B」這類說法自動開啟（已改進 `sources.md` 與 `SKILL.md`）。
17. **（實測發現）被 git 忽略的來源**：文件放在 git 忽略的資料夾時（例如 `.claude/think/`），`git diff` 永遠看不到它的改動。所以 `--diff` 除了 git 的改動，也要列出內容雜湊已經變了的假說；已改進狀態腳本並測過。
18. **（實測發現）狀態腳本會擋下證據不完整的假說**：生命週期假說第一次用腳本檢查，就被判成「未完成」，原因是 S2 從沒「看過它失敗」，G1 從沒驗過「拿掉一步就走不到」。原本的 README 自稱嚴格檢查已完成，所以證據完整性一定要由程式檢查，不能靠撰寫者自己宣稱。
9. 觸發之後才發現沒有 Java 或 TLC：結果是 `unformalized` 加上一筆「沒有工具」的原因紀錄，不留半套目錄。（候選二陷阱 17）

## 接受的取捨

- 我們接受 plugin 多一支 Python 腳本，換到讀者一行就有答案，而且不需要判斷。
- 我們接受「改涵蓋檔案的一個註解也算過期」這種粗顆粒，換到判定完全機械、不可能誤判成通過。
- 我們接受新鮮度用內容雜湊，而不是計畫原文寫的 commit，換到沒提交的改動、切分支也看得到。commit 只當維護時的比對起點。
- 我們接受 `hypothesis.json` 和 README 有部分重複（規則、範圍），換到機器只讀 json、人只讀 README。
- 我們接受只保留 `--satisfies` 一個旗標，換到其他輸入全部自動判斷；代價是偶爾猜錯，靠第一行讓使用者更正。
- 骨架原本寫在 8.11.0 上，已在 2026-10-24 改用 HTTPS 拉 GitHub，把本地 main 快轉到 8.21.0，再把 `CLAUDE.md` 與 `loop-contract.md` 那兩行重新加上。`verify-skills` 在 8.21.0 上通過。8.15.0 之後改到相關檔案的有四處：prove-it 加 `benchmark.md`、hunt 先攻擊前提、review 資安原則拆分、health 錯誤類別模式；`formal.md` 沒變，前提仍成立。
- 我們接受 Codex 鏡像暫時缺檔（`make parity-check` 失敗），換到等內容寫好再用 `/codex-skill-transfer` 一次移植，不必移植兩次空殼。

## 待決問題與風險

- 〔已解決〕本地 repo 已用 HTTPS 快轉到 8.21.0。
- 「假說／hypothesis」這個詞用得比預期廣：hunt 的英文本文裡有幾十處 hypothesis，範本也用「假說」；why 的輸出有「競爭假說」一節；think 用來形容計畫本身。第三片的改名要涵蓋 hunt 的本文與範本。why 和 think 裡的用法是一般意思，不是 skill 名稱，也不在觸發詞裡，所以建議保留。這一點要使用者確認。
- 〔已決定〕新鮮度看內容雜湊；維護時照 `/how` 讀程式現在怎麼運作，照 `/why` 找改動的原因。計畫已改。
- 〔已決定〕`variants/` 進 git。
- 〔已決定〕試行目標是 darkroom 的核心功能。

## 第一步

先實作 `scripts/hypothesis-status.py` 的 `--area`：讀 `hypothesis.json`、算內容雜湊、輸出七種狀態之一。用生命週期模擬的那個區塊當第一個測試，並把它改成 `hypothesis.json` 格式。
