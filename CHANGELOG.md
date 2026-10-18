# Changelog

格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-TW/1.1.0/)，版本號遵循 [Semantic Versioning](https://semver.org/lang/zh-TW/)。

## [8.9.0] - 2026-10-18

### Changed（`/review`：決定看哪裡的原則提早載入；`/evolve`：考卷本身也要保持可信）
- **原則分兩階段載入**：`principles/index.md` 加一欄「階段」。決定要看哪裡的四個原則（`goal`、`evidence`、`blast-radius`、`single-source`）在列清單前載入，其餘走到每一處才載入。原因：盲考裡三次漏掉（沒讀 CI、沒追 hook、沒追共用狀態）都是「該看哪裡」的規則在清單定案後才被讀到。SKILL 第 2 步的 Lifecycle 原本是 `blast-radius.md` 的重述，改成指回它。
- **change map 從 `git diff -W` 列**：被碰到的函式整段一起看，沒改的行也跟著改動一起跑；只讀某個狀態的改動行（條件、守衛、分支）也把那個狀態列成事實。
- **`blast-radius.md` #9**：列出改動寫入或讀取的每個狀態的所有讀者與寫者（用搜尋，不靠呼叫鏈）；帶有時間承諾的狀態（pending、鎖、重試、逾時）把這些地方按執行時間排成一條線，檢查每一步、每一種順序之後承諾是否成立。時序這一半參考 pstack `create-formal-verification-skill`。
- **`evidence.md` #9**：一份紀錄只證明它實際走過的路徑；測試專用入口、內部 setter、越過正式邊界的 mock、沒人確認過跳過什麼的 dry-run，都不能證明使用者那條路。參考 pstack `create-verification-skill`。
- **`goal.md` #9**：偏離若讓使用者依賴的行為壞掉，怎麼改合約都不算解決；只有優化才讓合約跟上程式。參考 pstack `maintain-verification-skill` 的 doc drift／regression 之分。
- **`/evolve` 的 `references/exam.md` 新增「Keeping the exam honest」**：每個答案項目先證明在題目範圍內找得到（範圍外的舊問題不算漏）；考卷只寫公平性規定，不准有一句擋住正確審查會讀的來源；考生走使用者的路；評分記錄每個答案位置有沒有被走到；漏掉先分類（skill／答案卷／考卷／只能跑才知道），只有 skill 的算分。
- Codex 版、`docs/skills/verify.md` 同步。

### 依據與限制
- 兩階段載入、`git diff -W`、共用狀態讀者：按鈕功能題探路 9 場（Opus low 6、high 1、medium 2）找回不變（都是 0）、無誤報、花費不增，照「沒退化就收」放入；**沒有證明有效**。探路顯示該題兩個答案是 diff 之前就存在的舊問題，從「這次改動」出發的審查很可能本來就看不到。
- 時序視角、`evidence.md` #9、`goal.md` #9、`/evolve` 的考卷維護：**未考試**。
- 模型比較（同日）：Haiku max 4.5、Opus medium 3.5、Fable low 3.5、Sonnet medium 2.5；GPT 側在 Windows 測試題沒讀 CI 是考卷措辭所致，拿掉限制後 Sol 一場讀了 CI 就兩項全中、另一場沒讀。

## [8.8.0] - 2026-10-18

### Changed（`/review`：每個問題標影響、嚴重程度、信心；「成立」也要舉證）
- **問題的定義改成「偏離原則」**：每條原則講的是「應該怎樣」，偏離了就是問題，嚴重程度看偏離的程度，不論偏離讓事情變好還是變壞。這條總綱和量表只寫在 `principles/index.md` 一處。
- **每個問題一行表頭**：`<principle file #n>：<影響（白話；風險就用原則自己點名的風險名稱）>　嚴重程度 N　信心 高|中|低`（例如 `goal.md #3：…`）。
  - 嚴重程度 0～5：0 風格；1 不一致或簡單措辭；2 輕微 bug、不影響正常使用；3 中等 bug、有 workaround；4 高級 bug、無法繼續使用；5 整體無法運行、部署或啟動。UI／UX 不直觀或錯位、不影響使用的是 2。還沒發生的風險（資料遺失、暴露、競態）取「真的發生時的等級」再減 0.5。
  - 信心綁證據層級：高＝兩段引文直接證明，或作者這一版的紀錄顯示失敗；中＝逐一走過分支推出來、沒有紀錄直接證明；低＝指得出位置與風險但沒走完路徑，或合約允許、有沒有害靠判斷。
  - `--full` 時由 verifier 確認或調整每一項的嚴重程度與信心。
- **判定看嚴重程度**：有嚴重程度 ≥3 的問題成立、或紀錄顯示目標宣稱或釘住範圍內的失敗，才是 NOT PROVEN；只有 0～2 的問題時最多 PARTLY PROVEN，逐項列出表頭；PROVEN 不變。收尾一行改成「{N} 項問題（嚴重程度 ≥3 的 {M} 項）、{K} 項不確定」。這條只改判定的計算，沒考過試（考試評的是找回，不看判定）。
- **偏離需求或合約就列**：`goal.md` #9——偏離需求或寫下來的合約就是問題，那份文字當第二段引文；偏離其實是優化時，基石寫成「讓合約跟程式一致」。合約允許了某條原則點名的風險時，原則條文跟合約並列引用，照證據層級給信心。`risk.md` 每一條、`goal.md` #3／#4 都點名它防的風險。
- **成立要正向證明**：reviewer 判一個地方「成立」也是宣稱，理由要正向表述，至少附一個 `file:line` 加原文；「沒說相反的話」不算理由（`principles/evidence.md` #8，來源 prove-it-works；`evidence.md` 改為每次都載入）。
- **三種判定**：成立／不成立／不確定。寫不出正向證明、也還證明不了問題的就是「不確定」，附一行「怎樣才能定案」；只能靠跑才能定案的也算不確定（那一行寫 coverage lost: needs X）；三題（做到了／多做了／做小了）說不準的也寫「不確定」。原本重疊的不確定、coverage lost、未驗證併成一類。
- **「說法一致」改成正向定義**：任何講到這個事實的地方，講的是新的；「該寫的有寫」只管該寫的地方有沒有寫。
- **排除看得到**：曾懷疑有問題、後來判成立的地方叫「排除」，附證明。報告尾巴兩份一行一項的清單：「不確定」與「排除」；主體不再另列 coverage lost 段；有不確定就最多 PARTLY PROVEN。
- **`--full` 的 verifier**：拿到 change map，逐項重讀排除附的證明；丟掉 finding 只有兩種情況——目標側在這個版本不存在，或拿得出「這個地方成立」的那一行；其他都算不確定。
- `principles/risk.md` #4 改回一般寫法（寫入失敗、中斷或重跑時，已有的資料不能遺失）：原本的具體情境是看過保留題答案後寫的，屬於污染，拿掉。
- Codex 版、`docs/skills/verify.md` 同步。

### 依據（`/baransu:evolve` 盲考；答案卷不進 repo，考生與寫改動的人都沒看答案）
- 同一份考卷模板、同一時段重考 8.7.0 作基準；每題 a、b 兩次；評分者只看到匿名編號。三道練習題：文件對不上 7 項、Windows 測試 2 項、按鈕功能 3 項。
- 8.7.0：找回 3.5；每場約 34.6 萬 token、9.8 分；每份平均 3.7 項問題。
- 成立要舉證這一版（第 5 輪）：找回 4.5；花費持平；保留題裡「超出合約上限」那一項，從 8.7.0 的 4 次「無害」丟掉，變成 2 次都留在「不確定」。條文盲評 3 位都判嚴格改善。
- 中間試過把偏離做成獨立的「標示」類別（第 6 輪），確定的錯被降成標示、找回掉到 2.0～2.5，撤掉。
- 加上嚴重程度與信心（第 7 輪）：找回 4.0、無誤報；「確定的錯被降級」修回來。
- 偏離合約就列、總綱（第 8 輪）：找回 4.5；每場約 34.2 萬 token、9.8 分（與 8.7.0 持平）；無誤報，信心標錯的多為「只指出風險卻標中」；每份平均 5.5 項問題，但不確定與排除變少，總長度約多 1 項。
- 試過再加「多做的一律列成問題、兩種讀法取較窄者」（第 9 輪），保留題那一項仍沒列成問題、報告變長，撤掉。

### Known limitations
- 保留題「程式比合約寬（超出上限）」那一項，第 8～9 輪 6 次只有 1 次列成問題：reviewer 常把它寫在「多做了」那一行判「無害」，或把合約的兩種讀法丟給使用者。
- 沒找到的問題大多仍是「讀到了、判成立」；按鈕功能那題要追到沒改的下游程式才看得到的兩項，所有版本都是 0。
- Windows 測試那題偶爾整場沒去讀 CI 紀錄（8.7.0 與新版各一次），屬於模型隨機性，條文沒碰到。

## [8.7.0] - 2026-10-18

### Changed（`/review`：重做——問題就是「有一個地方跟改動對不上」）
- **定義**：一個改動是對的，當且僅當每個擁有、重述或依賴它所改內容的地方都還對得上；使用者的需求是第一個地方。「對得上」分三種：說法一致（沒有地方講相反的話）、該寫的有寫（負責講這件事的表格、清單、說明、規格、範例要寫到新事實）、該給的有給（呼叫端、下一步、平台、使用者拿得到它依賴的值、狀態、時間點、環境）。每個問題附兩段引文；第二段可以是從使用端程式推出來的需求，原則條文只在沒有任何地方說話時才當第二段。
- **只讀不跑**：review 判讀已經存在的證據——程式、測試的斷言、歷史、作者這一版的執行紀錄（CI 等）；要跑才能確認的地方寫成「coverage lost: needs X」交給作者。原本的 canary、fresh inputs、mutation 探針與 `references/verification-effort.md` 移除。
- **流程**：列出改動改了哪些事實 → 只用指令輸出（git log／blame／grep、CI 列表）找出每個事實還出現在哪裡，每處配一個要回答的問題（歷史用 `/why` 的錨點、生命週期用 `/how` 的流程，不整個跑那兩個 skill）→ 每一處打開讀一次、每一處都給判定 → 五段鏈（現象／影響／根源／基石／驗證）與照規則算出的判定；基石附「該在哪一層修」（架構 → 型別 → 檢查 → 測試 → 文件）。
- **預設單一 reviewer、`--full` 才兩階段**：預設派一個全新 reviewer 從頭做到尾，主 session 的 context 保持乾淨；`--full`（或「完整審」）由主 session 列位置、reviewer 逐處讀，再派 verifier 只核對每個問題的兩段引文。`--model`／`--effort` 對兩種模式都有效。
- **原則庫**（新增 `references/principles/`）：目錄加 12 個原則——需求、單一來源、影響範圍、風險、證據、測試、信任邊界（以內建 `/security-review` 的排除清單與判例為準）、業務領域（含 DDD 與 BDD 的 Given／When／Then）、結構、品味、可讀性、效能。每個原則是一句原則、Why、最多 10 條做法、The test、跳過的徵兆（pstack 的寫法），碰到才載入。看似衝突的原則以一條能同時解釋兩邊的基石統一：結構＝「邊界放在改變理由不同的地方，其他地方不放」；重構＝「大膽刪複雜度，絕不大膽加」。
- **agents**：新增 `reviewer.md`（補上 reviewer 沒有定義檔、每次由主流程臨時寫提示詞的缺口）；`verifier.md` 改為只核對引文；**移除** `quality-reviewer`、`architecture-reviewer`、`security-reviewer`、`domain-reviewer` 四個鏡頭 agent，內容併入原則庫（含 8.6.0 期間 architecture-reviewer 新增的「業務邏輯散在條件判斷」，見 `principles/domain.md` #5）。外部若直接派這四個 agent 類型會失效。
- **description** 從 755 字縮到約 300 字，機制細節留在正文。
- **其他 12 個 skill 的 description 一併縮短**（ui、think、health、evolve、domain-modeling、draw、codex-skill-transfer、hunt、ship、write、read、learn）：只留「做什麼、什麼時候用、代表性觸發詞、真的容易混淆的鄰居」，health、hunt 的 when_to_use 併入 description；全部 skill 的 listing 從 9527 字降到約 5100 字，回到 7000 字門檻以下。Codex 版同步。

### 依據（盲測，每題跑兩次；答案卷不進 repo）
- 三道練習題（文件對不上 7、Windows 測試 2、按鈕功能 3）：新預設 1／2、2／2、0／0，reviewer 每組約 11 分、24 萬 token；8.2.1 為 3、0、0，12～18 分、30～46 萬；內建 `/code-review` 1／1、0／0、0／0，約 5.5 分、10 萬；第 6 版最高 4／5、2／2、0／0，但約 69 萬。
- 兩道保留題：新預設在 darkroom 匯出找回 1／1（8.2.1 為 0），draw 時間軸各碰到 2 項的一部分（8.2.1 為 1），花費約 8.2.1 的一半，且不執行任何東西（8.2.1 跑了 513 個測試、10 個 canary）。
- 迭代紀錄：第 1～5 版以花費換找回不算成功；第 7 版多一步沒省到錢；第 8 版的流失集中在「讀到答案位置卻判成立」與「把沒寫、沒給當成不衝突」，修正版因此把「對得上」分成三種、改成每處只讀一次。

### Known limitations
- reviewer 判讀時仍常把「該寫的有寫」「該給的有給」收窄成「沒說相反的話」：多處答案位置被讀到後判成成立，或以錯誤理由自己丟掉；同一題兩次的命中項目可能完全不重疊。
- 只能靠跑型別檢查才看得到的錯（例如 tsc 錯誤）review 本來就抓不到，只會判成「沒有這一版的執行紀錄」。
- Codex 版的 `fork_turns="none"` 是否完全隔離上層 memory 尚未實測。

## [8.6.0] - 2026-10-18

### Changed（`/evolve`：把 review 基石迭代驗證過的演進方法收進來）
- **每一處改動走同一條鏈**：現象 → 影響 → 根源 → 基石 → 驗證。diagnostician 的 finding 改成「現象與證據、害到使用者的哪個結果、肇事條文與它的 flaw、當初要解的問題、怎樣算修好」，再加一份給種子的 brief；brief 用通用措辭寫，不含答案、不含案例字眼、不提寫法。diagnostician 看過答案，所以不再寫替換文。flaw 新增 `subject`：條文沒說誰對什麼做事，模型就會用最省事的讀法補上主詞。
- **Seed Hunter**（新增 `references/seed-hunt.md`）：三位互相看不到的種子作者照同一份 brief 各寫一版基石，各自過減法閘與禁用字閘，洗牌換代號後由一位全新的評審（rank 用法）盲選。只有勝者會經過結構閘、考試和三人評審；落選的想法記進 `log.md` 的 `deferred_ideas`，不拼進勝者。挑選者不參與保留判斷，基準版也不參加挑選。
- **四種操作都要有證據**：新增只限「沒有任何條文解釋得了」的現象，而且要寫成正面定義；刪除與合併要靠考試的消融，或光讀文字就能證明（懸空參照、矛盾、完全重述）。新增 `merge (absorbs: …)`，合併後的句子要涵蓋原本每一句解釋的現象；多個基石可以並存，不硬併。修改要比另外三種強，保持原樣也是合法結果。每份種子都要寫一行 `why_kind`，說明為什麼選這種操作、不選另外三種。
- **減法閘改寫**：「add 一定要擠掉一條」拿掉。只加不刪的 diff 只有在 `implicated: none` 時放行，其他一律在挑選前退回。字數不設上限，必要的字不算成本。
- **盲考**（新增 `references/exam.md`）：可以 real-exec 時，效果軸改成已知答案的考試。
  - 答案卷由使用者寫或確認，只交給考卷評分者和評審。
  - 考試範本是考生的整份提示詞，只有兩個欄位可以填，雜湊記在 `decisions.tsv`。每次派出前都比對雜湊，不一致就算污染：重考，被污染的那份不計分。
  - 每道題考 a、b 兩次。只出現在一次的項目算半分，並且成為下一輪的現象。
  - 雜訊範圍取兩版各自 a、b 差距中較大的那一個（只考兩次，估計很薄，不能讓另一版剛好兩次很像就被拿來壓人），時間和 token 取兩次的平均。
  - 考卷由一位 exam 用法的評審，在不知道是哪一版考的情況下評分。
- **禁用字閘**：Stage 0 從考題和答案卷導出 `case-terms.txt`，由使用者確認。種子新增的字只要含其中任何一個詞，就退回；brief 也要先過同一個 grep。
- **成功的定義**：找回不輸、花費不增，靠的是位置正確，不是砍規則、少跑東西。保留條件變成「三人評審判定嚴格進步」再加上「有考試時，找回不低於、時間和 token 不高於現行版超出雜訊範圍」；用花費換來的進步不保留。沒經過考試的刪除與合併標記為「未經消融」，held-out 是延後的消融。
- **rubric**：第 3 維，正面定義勝過補上的禁止句；第 4 維，每條指示都講清楚誰對什麼做事；第 5 維，必要的字不算成本；第 7 維，有答案卷時讀考卷兩次的找回數。cluster 說明配合新增的規則改寫。
- **否證判準與 checkpoint**：每條條文都要用它換到的結果證明自己。有兩種情況算否證：一是輸出顯示條文規定的工作確實做了、也花了成本，但在看過的每一次考試裡都沒有換到結果；二是 `log.md` 顯示它一輪輪被加強，對應的現象卻始終沒動。被否證的條文要拿掉，或從 checkpoint 換方向重寫，種子不能再加強它。diagnostician 的 flaw 新增 `falsified`，finding 新增 `checkpoint`，內容是該方向開始前最近的快照與當時的條文，以及使用者指定的對照組；brief 也帶上 checkpoint，讓種子先看它怎麼做，再從那裡換方向。`report.md` 列出每個被否證的方向，包括試了幾輪、增加多少成本、換到什麼結果、退回哪個 checkpoint。
- **決策軌跡**：新增 `decisions.tsv`，每個決定寫一行，附上證據指標；使用者中途改規則、改 benchmark、改成功門檻，以及污染重考，也各記一行。Stage 7 收尾前對帳，指標要找得到檔案、每次保留或還原都有對應的一行、對話中改變流程的指示都有記錄，對不上的寫進 `report.md`。
- **evolve-judge** 分成 pair、rank、exam 三種用法；**evolve-diagnostician** 分成 diagnose、seed 兩種用法。沒有新增 agent 類型。
- **nightly-evolve.workflow.js** 改成「診斷 → 3 份種子 → 盲選 → 套用 → 三人評審」。只跑結構軸，所以沒有考試和禁用字表；光讀文字證明不了的刪除與合併提案標記為「未經消融」。
- `loop-pauses.md` 新增 Stage 0 答案卷與禁用字表那一列；`output-contract.md` 新增 seeds、`decisions.tsv`、`exam/` 的格式與 `report.md` 欄位；`provenance.md` 新增兩列來源；`orchestration-interface.md` 補上種子與考生的派工方式。
- **依據**：review 基石迭代（2026-10-17～18）的迭代紀錄、決策紀錄與第 1～5 輪盲考原始資料（盲評材料不進 repo）。這次迭代為了找回數，第 1～5 輪付出了 2～3 倍的時間和 token；第 5 輪有一份考生提示詞多了一句話，改變了考生的行為，必須重考；第 1 輪同一版考兩次，保留下來的發現一次 15 項、一次 6 項。

### Changed（連動）
- `CLAUDE.md` skill 表與機制錨點、`README.md`、`docs/philosophy.md`、`docs/skills/ops.md` 的 `/evolve` 說明，以及 evals 第 1、2 題的預期行為，照新流程改寫。Codex 鏡像同步。
## [8.5.0] - 2026-10-17

### Changed（`/ship`：單向合併、自己解衝突、commit 跟著 repo）
- **一次指定多個目標，單向合併**：`/ship uat main` 這類寫法會先 push 目前分支，再依序從它併入每個目標並各自 push；目標不會併回目前分支，目標之間也不互併，一律 merge、不 rebase，已回報的 commit hash 不變（新增 INV-11）。有目標時也照樣 push 目前分支：每個目標都是從它獨立併入、可能隔好幾天，分支必須在 origin 上留著，拆 worktree 的安全檢查因此一律以 `origin/{分支}` 為準。併入前先把本地目標 fast-forward 到 origin，結束時把主 checkout 放回原本的分支。Step 1 逐一檢查 HEAD 是否已在每個目標裡，已 push、但還沒進某個目標的分支照樣往下走。
- **合併衝突自己解**：Step 2b 原本「機械性衝突直接解、需要判斷就停」那句，改成三種情況——兩邊都要的內容兩邊都留、算得出來的值依合併後的結果重算、意圖互相矛盾才停下來並說明哪個檔、哪一段、兩邊各想做什麼。目標合併有衝突時不再 `merge --abort` 丟回給使用者，而是在那次合併裡照同一套規則解，通過 Step 2b item 5 的檢查才 commit；意圖矛盾時才中止那次合併，回報哪些目標已落地、哪些還沒跑。
- **commit 身分跟著 repo**：commit 前先看這個 repo 最近 commit 的作者和遠端的主機、擁有者；跟 git config 不一致時用 `-c user.name/-c user.email` 帶上判斷結果（不改 config），判斷不出來就停下來問。起因是這台電腦的 global config 切換過，私人 repo 用了公司帳號、公司 repo 用了私人帳號兩種方向都發生過。commit message 改成沿用 repo 過去的格式和語言，預設不加 `Co-Authored-By`。INV-8 改寫成涵蓋身分、格式與語言。
- **封存區不再跟著 worktree 消失**：實測確認封存放在 worktree 自己的 `.claude/archived/` 時，`git worktree remove` 會正常結束並把被 ignore 的封存一起刪掉。封存根目錄改成主工作樹的 `.claude/archived/`，忽略規則從 `.gitignore` 改放 repo 共用的 `.git/info/exclude`：不用 commit，主工作樹切到哪個分支都有效，也不會讓主 checkout 因為封存而變成「有未提交變更」。INV-9 改寫。
- `loop-pauses.md`：衝突那列改成「意圖矛盾」（Step 2b 與目標合併共用），新增「commit 身分判斷不出來」一列；push 那列涵蓋目標分支的 push。evals 新增 `/ship uat main`。

### Fixed
- Codex 版 `/ship` Step 1 偵測用的是 `.claude/`，跟它實際歸檔的 `.codex/` 對不上，改成 `.codex/`。

### Changed（連動）
- `CLAUDE.md` skill 表、`docs/skills/ops.md` 的 `/ship` 說明照新行為改寫。

## [8.4.0] - 2026-10-17

### Changed（`/codex-skill-transfer` 0.20.0：從快照對照表改成即時查官方來源）
- **對照表和轉換腳本退役**：四份對照表（`skill-mapping.md`、`plugin-mapping.md`、`agent-mapping.md`、`marketplace-mapping.md`）是 2026-10-08 那天兩邊規則的快照（Claude Code 2.1.293／Codex 0.161.0）；九天後本機已是 Claude Code 2.1.302、Codex 最新 release 0.163.0。另外刪掉 `CODEX_PORT_PLAN.md`、`scripts/transfer.py`、`assets/` 的兩個 template；「保留牙齒、不降級成提示」這條原則濃縮進 SKILL.md。整個 skill 從 219,832 字元縮到 16,372 字元（約 7.4%），Codex 版同步。
- **SKILL.md 只留方法**：列出來源實際有的元件 → 記下兩邊版本 → 每種元件去對應的官方頁查，文件沒寫的去讀該 release tag 的 Codex 原始碼（附網址對照表）→ 照 repo 自己的鏡像慣例 → 只改結構、保留每個觸發詞與防慣性停點 → 報告的每條規則都附網址或 `path@tag`。模式從四種改成三種：Audit（預設、唯讀）、Port、Question；Generate 模式隨 `transfer.py` 拿掉。
- **新增 `references/unverified-facts.md`**：只收官方文件和原始碼都沒寫明、靠推論或實測得到的 10 條事實，每條附日期、出處和重新驗證的方法。`loop-pauses.md` 移除 Generate 模式的兩列，新增「官方頁或原始碼抓不到 → 標待查、不憑記憶補」。evals 第 1、2、3、7 題的預期行為改成方法層的描述。
- **依據**：用 `health`（含 3 個 inspector）和 common-dev-plugin 的 `common-mod` 做三組對照。只說「轉成 Codex 版」的那組，盲評判了 3 項平台事實錯誤：description 的 20 個觸發詞只留 3 個；派 inspector 時沒指定 `fork_turns="none"`，而 Codex 原始碼寫明預設會繼承整段 parent 對話。照新方法的那組 0 項。所以保留精簡的 skill，不整個退役。

### Added
- `docs/development.md` 新增「本 repo 的鏡像慣例」：檔案逐一對應、共用檔留在 `skills/_shared/`、agent 對應 `.codex-agents/*.toml`、`$baransu:` 前綴、`.codex/` 工作目錄（但 skill 處理的對象路徑不改）、frontmatter 觸發詞不能少、Request User Input Gate、manifest 版本一致。原本這些只存在於轉換腳本和對照表裡。

### Changed（連動）
- `CLAUDE.md` skill 表、`AGENTS.md`、`docs/skills/ops.md`、`Makefile` 與兩支驗證腳本的註解，拿掉 `transfer.py` 與「對照表／檢查清單」的說法；`scripts/verify-skills.py` 刪掉只為 `transfer.py` 存在的殘留白名單條目。

## [8.3.0] - 2026-10-17

- 新增單句 skill `/huh`（白話重述上一則訊息）與 `/sayagain`（白話重述使用者的目標）；移除「技能數上限」理念，`verify-skills.py` 改為比對技能目錄與 CLAUDE.md skill 表。
- 新增 `/domain-modeling`：把 common plugin 的同名 skill（MIT，Matt Pocock）收進 baransu，負責維護 `CONTEXT.md`／`CONTEXT-MAP.md` 詞彙表與 `docs/adr/` 決策紀錄，能力全數保留，附 `NOTICE.txt`／`LICENSE.txt`；`/think` 的用詞與 ADR 兩句改成指向它（`/think` 只審議、不寫專案檔），Codex 版同步。
- 新增 `/why`（查出程式為什麼長這樣，每條主張分五級信心、寫明查不到什麼）、`/how`（講清楚一塊程式怎麼運作）、`/teach-me`（用對話把程式或 `/learn` 筆記教懂），改編自 Cursor pstack 的 why、how、teach（MIT，Lauren Tan），各附 `NOTICE.md`。`/why` 的證據改成這台機器實際有的四類並由近到遠查；`/how` 先讀入口再決定要不要分頭追；`/teach-me` 素材可以是程式或 `/learn` 筆記，文風引用 `/write`。
- `/write` 併入 pstack unslop 的去 AI 腔規則：根部改成「講機制不講感覺、細節只能來自原文或使用者」，writing-principles 新增中英共通五條與 en 7–10，floor 規則不變。
- `/learn` 寫完 brief 或 digest 時提示可以用 `/teach-me` 讀懂；技能數照實改為 18（含 domain-modeling），Claude／Codex 兩版同步。

## [8.2.1] - 2026-10-16

### Fixed
- `rules/anti-patterns.md` 舉例的「execution pipeline 的 `failure_count` 計數規則」屬於 v4.0.0 已退役的流程，刪掉這個例子；Codex 版原本指向 AGENTS.md 裡不存在的 Non-obvious Invariants 段，改回指向 CLAUDE.md（AGENTS.md 以它為準）。
- `docs/development.md` 的殘留掃描說明補上 `/book`、`/design`、`style-reviewer`，並註明 `.claude/design/` 目錄名不算。

## [8.2.0] - 2026-10-16

### Removed（清掉 book／design 的殘留）
- book 與 design 已重做成 `/ui` 與 `/draw`，只為它們服務的檔案一併退役：`agents/style-reviewer.md`（依賴 design preset 的 DESIGN.md／tokens.css，`/review` 從未派發它）、`_shared/aesthetics-foundation.md`、`_shared/typography-discipline.md`、`_shared/scripts/color_distance.py`，Codex 版對應檔同步刪除。CLAUDE.md layout 與 domain-reviewer 的分工句同步。
- `codex-skill-transfer`：`transfer.py` 拿掉 book／design 的 AskUserQuestion 分級、book 專用的 3+1 問題拆分與 design `slide-checklist.md` 豁免；`CODEX_PORT_PLAN.md`、`skill-mapping.md` 的列舉與範例改成現存技能。
- `read`、`learn` 的 evals 不再期待路由到 book，改為 `draw`。

### Changed
- `scripts/verify-skills.py` 的 C2 殘留掃描加入 `/book`、`/design`、`baransu:book`、`baransu:design` 與 `style-reviewer`，之後再出現會被擋下；`.claude/design/`（`/ui` 的參考筆記目錄）不受影響。

## [8.1.1] - 2026-10-16

### Fixed（Codex 版同步）
- Codex 版 `draw` 的 frontmatter `description` 還停在改版前（「explainer page」、沒有整頁交棒 `$baransu:ui`、少了 'show me'／'draw it' 觸發詞與 Not For 子句），改成與 Claude 版一致。其餘 12 個技能、`_shared/` 與 11 個 agent 逐檔核對過，差異都是 Codex 必要的改寫。

## [8.1.0] - 2026-10-15

### Changed（`/health` 以證據而非庫存判健康）
- **Step 0 改為「建立證據基礎」**：四類證據——風險（哪些路徑會丟資料、花錢、發布或部署、跨信任邊界、造成難以回復的狀態）、不明顯的限制（哪些穩定決定無法從程式碼或 manifest 便宜地還原，而且 agent 能否只在相關時才取得）、失效證據（使用者糾正、重複修復鏈、過期的產生物、壞掉的參照、空殼驗證器）、驗證器涵蓋（重要結果在它會失敗的那一層有沒有可執行的檢查）——取代以 git 追蹤檔案數分級的 Simple／Standard／Complex 表與每級「應有幾條 rule、幾個 skill」的庫存清單。少一張地圖、一個大檔、skill 多或少、TODO 數高，在綁到四類之一前都只是資訊；依證據與風險校準，不依 repo 大小。原本補在表格後面那段「不要把計數差距當 finding」的守衛是貼在症狀上的，連同根因一起刪。
- **分級的每個消費端同步改寫**：升級 deep 審計不再看規模——「Complex 級」觸發刪除，改為摘要輸出解不開 Step 0 記下的失效證據或無法歸類的安全／控制問題時才升級；Step 2 路由由三級合併為摘要／深入兩路；inspector 改餵 Step 0 證據紀錄而非「偵測到的級別」，inspector 內的 SIMPLE／STANDARD+／COMPLEX 條件全部改成綁定風險、限制、失效證據或驗證器涵蓋；基準原則涵蓋與 docs／specs／HANDOFF 缺席的嚴重度改由證據類別決定，缺席本身永不 FAIL；報告標頭與「依級別評分」改為依證據類別。`collect-data.sh` 保留各項計數為資訊輸出，拿掉 `detected_tier` 與門檻（`=== TIER METRICS ===` 改名 `=== PROJECT METRICS ===`；`auto deep` 呼叫方式不變）。涉及 `skills/health/SKILL.md`、`references/baseline-principles.md`、`evals/evals.json`、`scripts/collect-data.sh`、`agents/health-inspector-context.md`／`-control.md`／`-maintainability.md`；Codex 版 `skills/health/**` 與 `.codex-agents/health-inspector-*.toml` 手動同步。
- 這是 `CLAUDE.md` 新段落「從根部修、值不值得三問」的第一次套用：證據是檔內已經補上的守衛，改法是以更合身的原則取代條文、不在旁邊再加一條守衛，而 Waza 另外兩項判斷（nested AGENTS.md 實際載入什麼、permission 與 instruction 層的校準）因本 repo 尚無 `/health` 在那裡失誤的證據而不收。

### Removed（盲評材料不進 repo）
- `tests/ab/`（`/ui` 的 A/B 盲評題目與結果）移出 repo 並加入 `.gitignore`；8.0.0 條目裡「保留在原處」的說法自此作廢。實驗紀錄一律不進 repo。

## [8.0.0] - 2026-10-15

### Removed（`/contract` 與 `/seal` 退役，skill 數 14 → 12）
- **`/contract` 與 `/seal` 整個退役**（兩個 skill 目錄、`agents/seal-agent.md`、Codex 版的 `.codex-agents/seal-agent.toml`、`_shared/contract-gate.md`，Claude 與 Codex 兩邊同步）。contract 當初是取代過重的 `analyze` 的輕量版，建在模型還無法一次做完一件事、答應了又不照做的年代。之後的經驗是：有沒有立約、有沒有封緘，會出錯的照樣出錯、會做對的照樣做對；seal 的突變抽查尤其沒有看到任何效益。兩者皆不以新 skill 補位，上限收到 12（codex-skill-transfer 的三個月零使用退役條款沿用，觸發時上限收回 11）。
- **seal-guard Stop hook 退役**：`hooks/hooks.json`、`seal-guard.sh`、`seal-guard.ps1`（兩邊）與 Codex manifest 的 `extensions."com.openai".hooks` 接線一併移除；plugin 自此不附任何 lifecycle hook。`SEAL_GUARD` 環境變數不再有作用。
- `_shared/selection-telemetry.md` 的 seal-guard 機械錨點與 Phase 3 閘門事件段（現實接觸強制閘／Critical 硬停／R10 證據異議——三者只住在 contract 與 seal 裡）隨之移除；miss rate 只算 `"miss": true` 紀錄，並明寫零 miss 的月份只是弱證據。
- 這是使用者流程的破壞性變更：`/baransu:contract`、`/baransu:seal`（Codex 的 `$baransu:contract`、`$baransu:seal`）不再存在，故升 major。

### Changed（中頻段改走「直接實作 → `/review`」）
- 三頻段路由：中頻段改為「照 `_shared/tdd.md` 的紅綠紀律直接實作，再 `/review` 獨立重驗」，收尾證據是一次紅 → 綠執行加 review 判定；大頻段切片後每片走同一條中頻段。`CLAUDE.md`、`README.md`、`docs/routing.md`、`docs/skills/plan.md`／`verify.md`／`ops.md`、`docs/install.md`、`docs/philosophy.md`、`docs/development.md` 同步。
- `/ship`：拿掉 sealed 合約的偵測與歸檔（`SEALED_CONTRACTS`、`head -3 | grep '> STATUS: sealed'`、INV-1 的第二個歸檔來源、Step 3 的合約刪除例外），Step 1 改為三項輸入；`ARCHIVE_DIRS` 移除 `seal`。其餘流程不動。
- `/hunt`：修復範圍跨多檔時，改為切片後每片「實作 → `/baransu:review`」，不再開合約。`_shared/tdd.md` 的 scope 句改稱 medium-band slice；`codex-skill-transfer` 的 `skill-mapping.md` 派遣範例改以 `verifier` 示範；`_shared/loop-contract.md` §4 移除 contract／seal 兩列。
- `scripts/verify-skills.py`：技能數上限 14 → 12；殘留掃描新增被裁指令 `/contract`、`/seal`、`baransu:contract`、`baransu:seal`（slash 形式，`../contract/references/` 之類路徑段與 `loop-contract.md`、draw 的 `delivery-contract.md` 不命中）、被裁名稱 `seal-agent`、`seal-guard`，與 sealed 標記字面 `STATUS: sealed`。
- `plugin.json`／`marketplace.json`／Codex `plugin.json`：描述「Fourteen」→「Twelve」，關鍵字移除 `contract`、`seal`。

### Removed（單元測試全部退役）
- **`tests/skills/`、`tests/integration/`、`tests/scripts/`、`tests/fixtures/` 全部移除**（含 `claude-md-skills-baseline.txt`）。理由：skill 好不好用跟單元測試無關，skill 壞掉也跟它們無關；skill 改版時壞的是這些沒用的測試、不是 skill。這是刻意的實驗：一支都不留。`tests/ab/` 是 `/ui` 的 A/B 盲評題目與結果，不是單元測試，原地保留。
- `Makefile` 的 `test` 改為只跑 `scripts/verify-skills.py`（結構驗證是理念表綁定的機制錨點，不是單元測試）；`parity-check`、`ship-check` 不變。`CLAUDE.md` 與 `AGENTS.md` 的 Verification 段明寫「此 plugin 不做任何單元測試」與理由。`verify-skills.py` 的 skills-root／agents／loop-registry 模式保留給臨時驗證用，docstring 不再指向已移除的 pytest 檔。

### Changed（`/think`、`/review` 更專家、更有野心）
- `/think` 在對焦之後、表態之前新增「借鏡」一步：把名詞換成動詞，點名已經解過這類問題的學門或實務者與其真正使用的工具、原始材料、外部裁判，寫一行「改了立場的哪裡」或「不改」；長命功能、核心路徑、方向題、存廢判決必做，參數選擇、單檔小修、拷問既有決定則略過並說明。
- `/think` 表態必答三題：目標背後的目標（高一層的版本列為真候選）、方案的美感（一句話說得出的主意加「我不是什麼」清單；靠「沒有一處會錯」撐住的設計是躲避不是品味）、成本對效果（能給數字就給數字，與最小方案並列）。攻擊改為兩向：會壞在哪，以及尺寸——做過頭（藏在抽象與防禦裡）與做太小（偷偷解了比復述更小的題）。
- `/review` 沒有驗收條文時以三個常設問題為題：做到了沒、多做了什麼（防呆、分層、選項）、做小了沒；一屏以內的 diff 走快速路徑（一個 verifier、既有測試、不派視角）；找得到該領域的標準工具（dry run、交錯執行、已知答案測試、重放真資料、瞇眼看）就點名並實跑；建議修法先刪、再複用、再平台、再一行，才輪到新機制，只因「比較安全」的建議只進 advisory，一份只加防禦的 review 要自承沒回答三題；報告每題一行（做到了／多做了／做小了）。
- `verification-effort.md` 從 seal 搬到 `review/references/` 並去掉 seal 詞彙；`agents/verifier.md` 與 `quality-reviewer.md` 加上「做小了」與「過度防禦」判準（信任邊界驗證、資料遺失處理、使用者要求的東西永不列為過度）。think／review evals 各加兩案。來源：Rieseberg〈How to be more ambitious〉（Altitude／Depth／Range）與 ponytail skill（最小完整改動、不砍信任邊界）。

### Changed（`/evolve`：以減法取代加規則）
- diagnostician 每輪改交一筆 finding——肇事的既有條文（原則瑕疵／與他條矛盾／負面副作用）、該條文當初要解的問題（條文理由 → `log.md` → `git log -S`／CHANGELOG → unknown）、以及用更少字解掉原始問題的替換文；只有讀完整份都找不到肇事條文時才准「加」，且必須指明取代哪一條。`finding: none` 是合法結果，不再把最低分維度硬湊成弱點。
- rubric 第 5 維由 Constraint Explicitness 換成 Economy（每條都要改變一個決定、不重述、不矛盾、決定相同時短者高分），第 3／4 維改計涵蓋整類的原則而非逐案清單，權重不動。Stage 3 新增機械式減法閘：diff 沒有刪改任何既有非空白行的候選直接 `append-only-refused`，不送盲評。
- `log.md`／`report.md` 記錄 finding 與字數起訖；`provenance.md` 新增條文溯源章節；終態裁決改為 `verify-skills.py` 結構閘；`nightly-evolve.workflow.js` 的 schema／提示對齊 finding 形狀並在評審前拒絕純增補，技能清單改為現行 12 個。棘輪、盲評三席、held-out、Authorization PAUSE 不變。參考：cursor/plugins `pstack`（概念對齊，措辭自寫）。

### Added（`_shared/modeling.md`：數學是工作語言、白話是陳述語言）
- 新增 `skills/_shared/modeling.md`（Claude／Codex 兩邊同步）三段：先叫出問題的類別——用歸約問這是哪一個已知問題、那一類難不難（NP-hard 的形狀就停止找最佳解，改走帶上界的 greedy／近似或縮小實例；有最佳子結構與重疊子問題就動態規劃；目標與限制皆線性就線性／整數規劃；相依排序走拓撲序與關鍵路徑；配對、最大流／最小割、最短路徑；可行性單調就對答案二分；幾件東西直接暴力）；問題帶數量（成本對效果、容量、速率、機率、排序、樣本數、容差）才寫模型——變數、目標、限制、實測對假設、解或界、敏感度、數字放在它改變的決定旁邊，沒有數量就一行說明後停；公式目錄各一行（三點估計、期望成本、損益兩平、rule of three、中位數對雜訊底、Little's law、相對對絕對容差、blast radius＝sites × centrality × boundary、rewrite signal＝touched sites ÷ tree size、相對規模指數 2.94 × KSLOC^1.10 只排序不排程）；對人只講一句「這個數字是什麼意思、改變哪個決定」（「對人陳述時用白話」），推導放計畫檔或附錄一行，附前後對照例。
- `/think` 的借鏡步明列 algorithmics 為範例學門並指向 modeling.md §1；量化情形沿用借鏡步既有的觸發邊界（長命功能、核心路徑、方向題、存廢判決必做；參數選擇、單檔小修略過）寫模型，數字進成本對效果那一行、推導進 Approach。`/review` 的 verifier 引用它談容差、樣本數與涵蓋；`/health` 引用它談相對規模指數。

### Changed（借鏡 Anthropic code-modernization：判定用規則算、證據是跑出來的）
- `/review`：結尾判定改由印在報告裡的固定規則計算，不由模型意見——PROVEN（該跑的都跑了且沒有失敗）／PARTLY PROVEN（沒有失敗，但有該跑的跑不了：工具缺席、沒有獨立 pass、某題未驗證，逐項列出）／NOT PROVEN（有後果的發現成立、某項失敗、或根本沒跑）；每次都從本輪證據重算，快速路徑也算。證據是跑出來的輸出（結果檔、貼上的 log 片段），打進去的數字或「Canary: 已跑」只是主張。兩個固定觸發的儀器：canary（在拋棄式副本裡弄壞一行要緊的、測試必須變紅；比較器本身則翻一個 byte 驗證）——完整路徑且 pass 靠的是同一次改動寫或改的測試時必做，測試早於改動（紅→綠已證明會失敗）或快速路徑略過；fresh inputs（≥10 筆開發沒用過的輸入：邊界、空、巨大、亂序，要求逐 byte 相同時才試壞格式，輸出不得與開發案例相同）——主張「行為跟以前一樣」（遷移、移植、重構、版本升級）時必做；十筆乾淨只把漏網率壓到三成，報告要寫出 n。比較只認逐 byte 相同或派遣時宣告的容差（相對 ≤1%、絕對封頂），每個容差與每個 mask 都帶 why 並列在報告裡。工具三態：present／runnable here／actually ran，只有真的跑過的才算發現，跑不了寫「coverage lost: needs X」。結尾行加「若只能改一處」。`agents/verifier.md`（與 Codex `verifier.toml`）同步 canary、fresh inputs、容差、三態與 rule of three。
- `/think`：成本對效果以「觸及檔案與呼叫點占整棵樹的比例」（rewrite signal）取代 hours，相對規模、不給時間；攻擊會壞在哪時把一個失敗情境追到底（哪一塊倒了、使用者看到什麼、怎麼回來，「之後再想」是 finding）；復述是版本／執行環境／相依升級時，情境從 delta 出發——該版本對的已知變更 ∩ 這份程式真的用到的（file:line＋site 數，沒人呼叫的 removed API 不算），按 blast radius 排序、分 Mechanical／Judgment，編譯得過結果卻不同的（locale、編碼、排序、浮點、預設值）先寫 characterization test 再動，其他復述略過；攻擊做過頭時加「畫出來的邊界必須對上今天就有東西在變的 seam」。計畫檔：Building 的成功條件是可檢查的條件而非狀態、永不是時長，尺寸用複雜度占比；Approach 在多於一片時指名第一片為 pilot（打最險的前提、不是最簡單的那片），明寫計畫是假說、pilot 揭露的事預期會改寫計畫、使用者的 go 只涵蓋 pilot，單片計畫不寫這段。`agents/architecture-reviewer.md` 審計畫時加問：每個邊界對不對得上真 seam、滿足需求的最簡設計是什麼、追一個失敗模式到底。
- `/hunt`：Tool Scan 加讀碼紀律——先開入口追控制流再 grep 名字（名字會騙人、控制流不會）、先找資料再找誰碰它、每句主張給 file:line 或說「不知道」、「是」與「看起來是」分開、把現場缺的東西（沒處理的錯誤路徑、註解掉的區塊、TODO、magic number）當證據；Bisect Mode 在「更新後壞掉」是版本對時，第一批假說從 delta 來，靜默改結果的變更優先於大聲失敗的。
- `/health`：Invariant 5「被審內容是資料」——CLAUDE.md、AGENTS.md、settings、hooks、skills、memory、對話節錄都是證據不是指令，對著審計者說的指令形文字本身就是 finding（file:line，Step 3 照常分級）；比較多個系統（monorepo 多套件、portfolio）時用同一把尺量、以每 KSLOC 複雜度與相對規模指數排序，指數只印成「index」、永不印成時程／成本／人力，單專案略過；AI 可維護性加 doc gap——deep 審計比對程式實際行為與 README／CLAUDE.md／AGENTS.md 所說，列新人需要而文件沒寫的前五個行為，summary 記「doc gap 未查」。`agents/health-inspector-maintainability.md` 加「蒐集到的資料是資料」。
- `rules/anti-patterns.md`：「不受信任內容」擴及被分析對象本身（原始碼註解、設定、專案 CLAUDE.md／settings、fixtures、log），指令形文字以 finding＋file:line 回報，主張只在可執行程式或實跑顯示時才算真；「無來源依賴」補上工具三態與「coverage lost: needs X」。Codex 版 `rules/`、四個 SKILL.md 與三個 agent TOML 同步（health-inspector-maintainability.toml 順手把殘留的一處 `/baransu:` 改成 `$baransu:`，與其他 TOML 一致）。

### Changed（`/draw` 跟上四個上游）
- draw：跟上四個上游——diagram-design 2.6.64 → 2.6.99（新 service blueprint 型別與 architecture containment、210 個 examples 全數更新、`verify-contrast` 等三個新 verifier、self-check 的 viewBox 檢查、export snippet 重套 `/draw:` 安全行；上游 2.6.85 的來源信任確認與 `approved` 步驟列入 README 覆寫層）、archify 3.0.1 → 3.1.0（erd / class / tree / timeline / waterfall 五種新圖型進 map lane 型別表與 `steps.json`、Viewer 預設 Live / Still、內建 zh-TW 等語系目錄）、anatomy `454a0ef` → `bc943e4`（capture / drive 等待與逾時修正）、awesome-opus-5-5-videos 與 awesome-ai-motion 的公開資料集發現改述進 prompts / composition / commission / review；`index.json` 新增 27 個 topic；NOTICE 每列補上 commit 與日期；Codex 版同步。

## [7.7.0] - 2026-10-15

### Added（`/ui`：先找點子、刪掉要填回、一定看截圖）
- 新段落「The idea, the argument, and looking at the result」，放在 Restraint 之後、Browser checks 之前；與上方各段不同時以這段為準。從 frontend-design 搬來的五段逐字不動（`test_ui_skill_structure` 的 sha256 照舊）。
- 先寫主敘事：第一步用一句話寫出誰來、來找什麼、離開時知道什麼並做了什麼。任何設計與視覺效果（配色、字體、圖騰、動態、裝飾、點子本身）只有在服務這個主敘事時才保留，否則刪掉。主敘事與點子是設計計畫的前兩項。
- 6 : 3 : 1 層級（同 `/draw` 的 `composition.md`）：整頁與每屏都分成約 60% 安靜的舞台、30% 引導的中段、10% 主敘事需要的焦點，焦點只靠一個差異被找到；配色、字級、密度、段落輕重都照這個分。計畫裡要寫出整頁與每屏的舞台、中段、焦點；Squint 檢查改為在縮圖尺寸看 6 : 3 : 1，且首屏焦點必須是主敘事的焦點。
- 先點子後配色：配色前列 8–12 項只屬於這個題材的清單，寫成點子句「On this page, [something only this subject has] becomes [the device that carries it].」，並用競爭對手測試審查計畫（取代原本「拿類似 prompt 想想看」）。點子是設計計畫的第一項。
- 先論點後版面：每段一個主張加證據，沒有主張的段落刪掉。
- 刪掉要填回：拿掉裝飾後只能用放大主角、完整內容、真實圖片或整片色塊填回，整頁刻意空白最多一處；範例細節列在收尾給使用者確認，絕不捏造客戶、推薦語、評論、媒體、logo 或營運數字。
- 截圖自評改為必做：用 draw 的 `verify-page.mjs` 截圖，跑七項檢查（one-second focus · squint · cover the name · left edges · neighbouring sections · fullness · phone），只判通過或不通過，每輪修最多三項，最多兩輪。
- 點子承載第一個問題、不取代它：首屏用大字回答需求裡訪客最想知道的事（價錢與時間、工具做什麼與怎麼裝、時間地點），點子是這個答案的呈現方式。One-second focus 檢查加上「首屏在桌面與手機都回答了第一個問題」；Phone 檢查禁止寬圖、表格、程式碼區塊在區塊內左右捲動。這兩條來自 A/B 第一輪的敗因。
- 修改既有 UI 的模式不跑題材清單、點子與論點，也不新增段落或事實；fullness 不過時只能用放大或色塊處理。
- 新測試 `test_codex_copy_body_matches_claude_with_known_substitutions`：Codex 版 SKILL.md 內文必須等於 Claude 版只做兩種替換的結果。`verify-codex-parity.py` 只檢查檔案是否成對，封緘時的突變探針證明，Codex 副本停在舊內容也能通過所有關卡。
- 概念改寫自 tasteskill v2（Leonxlnx，MIT），NOTICE 已註明；未收錄其腳本或資料。

### Added（A/B 盲評工具組 `tests/ab/ui/`）
- 3 個題目、builder 與評審提示、`shuffle.py`（隨機分 A/B、對照表放在 `blind/` 外、不覆寫既有結果、`--shots` 指定截圖資料夾）。結果 `results-phase1.md`：第一輪新版 2 勝 1 負，輸掉的那題是點子佔滿首屏、把價目擠到下面；補上「點子承載第一個問題」、主敘事與 6 : 3 : 1 之後，第二輪新版 3 題全勝（三題新版剛好都洗在 A，位置偏差無法排除）。

## [7.5.0] - 2026-10-13

### Changed（`/draw`：只畫單件作品，需要整頁時自動交給 `/ui`）
- 形式改為四種：diagram（靜態圖，可加 seek overlay）、map（可探索的架構圖）、film（影片，含運鏡）、component（可互動的動畫元件：機構圖、可拖動的圖、動畫小元件）。拿掉 page 形式：版面、閱讀欄、內文與多圖頁面不再由 draw 做。`--lane` 改收 `diagram|map|film|component`，`SKILL.md` 的 lane 章節改為 `Lane: film`、`Lane: component`，另新增「Shader layers (any form)」。
- component 交付一個自足的 `<name>.html`：只有作品本身（圖、操作提示、讀數、圖說），主題感知、手機寬度可用，沒有頁面外框與段落文字，可被 `/ui` 用 iframe 嵌入，或把標記與腳本抽進頁面。`verify-page.mjs`、`perf-check.mjs` 直接對每個元件檔跑。`references/motion/explainer-page.md` 改為 `component.md`（元件的機制、元件契約、效能規則、建置順序），`references/lanes/page.md` 改為 `lanes/component.md`，`assets/motion/explainer-template.html` 改為單件元件的機制範例 `component-example.html`。
- 自動交棒 `/ui`：使用者的用法是「幫我 draw xxx」「show me & draw it」，所以 draw 是唯一入口，負責端到端交付。由內容判斷要一件、多件，還是一整頁（說明 X、教學、多張圖一起看）。需要整頁時，brief 的 `When:` 加上 `needs-page`，各元件做完並通過檢查後走 `assemble-page` 一步：寫 `docs/ui_brief.md`，同一回合用 Skill 工具載入 `/ui`，不問使用者，預設不開 subagent。最後交付 `<slug>.html` 頁面加上各元件。開工狀態行與完成報告多一欄「交付」（單件／多件／元件＋/ui 組頁）。紅線新增：不准停下來問要不要做成頁面，也不准由 draw 自己做頁框、閱讀欄或段落。
- `/ui`：描述與內文新增「說明頁、教學頁、含圖解的頁面由 `/ui` 設計，嵌入 `/draw` 產出的元件」。新增一節「Pages built around /draw components」：照交棒內容直接做、不等回覆；每個元件可選用 iframe 或抽出標記；保留元件自己的外觀，只調頁面。Not For 改為「單件圖、影片、機構、互動元件 → `/draw`」。`CLAUDE.md` 技能表同步更新。
- 評分卡：page 列改為 component 列（圖說要補上圖沒畫出的資訊、rest frame 本身就能說明重點、元件契約、效能）。`critique-loop.md` 的「Looking at a page」改為「Looking at a component」，mechanism 列的指令改對 `<name>.html` 跑。mechanism 的「How it joins /draw」改為 component（預設）、film、diagram 三種接法，對應 `mech-join-component`、`mech-join-film`、`mech-join-diagram`。
- `evals.json` 的期望輸出改為 film lane 與「元件＋/ui 組頁」。

### Changed（`/draw`：有意義的檔名）
- 檔名以主題 slug 命名，副檔名標出種類：film 原始檔 `<slug>.film.html`；母帶 `out/<slug>.mp4`，其他格式 `<slug>-9x16.mp4`、`<slug>-1x1.mp4`；diagram 是 `<slug>.html` 加上匯出的 `<slug>.svg`／`.png`；map 是 `<slug>.map.html`；component 是 `<name>.html`。`index.html`、`final.mp4` 不再當作 draw 的輸出名（`steps.json` 明文禁止）。
- `render.mjs`：slug 取自 `--html` 檔名（去掉 `.film.html` 或 `.html`）。所有輸出都是 `out/<slug>[-<格式>][.<種類>].<副檔名>`，例如 `paper-plane.contact.png`、`paper-plane.animatic.mp4`、`paper-plane.part-10.00-20.00.mp4`。主格式不加後綴、其他格式一律加後綴（見下方「主格式」），兄弟格式不會再蓋掉母帶。新增 `--name SLUG`（換 slug）與 `--out-file PATH`（指定確切輸出檔；與 `--all` 一起用時，在啟動瀏覽器前就拒絕）。
- `checks.sh`、`doctor.mjs`（smoke test 改用 `smoke.film.html`）、`verify-page.mjs`、`perf-check.mjs` 的用法說明，以及 `pipeline.md`、`1-design.md`、`3-keys.md`、`4-shoot.md`、`5-post.md`、`review.md`、`beat-grid.md`、`finishing.md`、`prompts.md`、hand-drawn 的 `sound.md`／`workflow.md`、seek／loop 範本的開頭註解，全部改用新檔名。diagram 的 `lint-skin.py` 改為一律從檔名取 slug，不再特別處理 `index.html`。

### Changed（`/draw`：索引、步驟與參照帳，本輪整合）
- 索引拆細：主題從 1764 增加到 1836，每個主題印出不超過 80 行。`map-delivery-validate-and-deliver`、`map-delivery-output-path-contracts`、`kit-round-parts`、`kit-audit`、`anatomy-page-in-your-code` 各拆成數個子主題，原 id 改為總覽（例如 `kit-audit-hook`、`kit-round-parts-solids`）。作品集每一頁各拆成圖的一半（`mech-collection-<頁>`）與安裝、使用的一半（`mech-collection-<頁>-code`）。
- `lookup.py`：沒有子標題的長章節可用行範圍選取（`from`／`to`）。`--check` 另外列出沒有任何主題指到的標題，原有的 120 行上限與「`whole` 必須附理由」照舊。`--rebuild-index` 支援 `--rename`、`--add`、`--dry-run`。改名後的主題 id 一律改成 component 開頭（`component-contract`、`component-build-order`、`component-mechanics`、`lane-component-*`、`critique-rows-component` 等），不保留舊 id 當別名。另新增 `component-ui-handoff`、`skill-shader-layers`、`component-theme-switch-seek`。Codex 副本多一個 `codex-port-adapter` 主題，讓 adapter 章節也有主題指到。
- `steps.json`：依四種形式重寫，共 82 步。新增 `component-caption-states`、`component-perf-plan`、`component-figure-card`、`component-rest-frame`、`component-interaction`、`component-check`、`assemble-page`，並補上 anatomy 上游的五章（`anatomy-invent-object`、`anatomy-build-geometry`、`anatomy-painters-order`、`anatomy-make-live`、`anatomy-verify-critic`）。preflight 適用所有形式。新增兩個步驟旗標：`ordered`（依列出的順序印出，例如 `mech-size` 先印 `mech-overrides` 再印 `anatomy-size-classes`）與 `all_products`（該步要交出每一個產出，例如 `assemble-page` 的 `docs/ui_brief.md` 與頁面），兩者都是給建置者的指引，`ledger-check.py` 不檢查。`camera-{move}`、`transition-{name}` 認得 push-in、whip pan、crossfade 這類別名。`mech-join-{form}` 依形式代入。
- `ledger-check.py` 改為依四種形式判斷適用步驟（判斷方式見下方「參照帳簡化」）。`SKILL.md` 每個步驟表的列與 `steps.json` 逐列一致（82 步，必查主題完全相同）。查詢指令統一寫成 `python3 "<skill>/scripts/lookup.py" <主題> --log "<out>"`，腳本一律用絕對路徑呼叫。

### Changed（`/draw`：步驟紀錄 `lookup.py --step`）
- 每一步動手前只跑一條指令：`python3 "<skill>/scripts/lookup.py" --step <步驟 id> --log "<project>/.claude/draw/<slug>" [--value key=value ...]`。它印出該步 `lookup_before` 列的每一章（`camera-{move}`、`transition-{name}`、`type-{chosen}`、`type-ramp-{size}`、`kit-{fn}` 等範本由 `--value` 代入，別名經 `steps.json` 與索引解析，例如 `--value move=push-in` → `camera-dolly`；`{form}`／`{approach}` 預設讀 brief 的 `Form:`／`Approach:`），並在 `docs/lookups.log` 追加一筆 `step` 紀錄（UTC 時間、步驟 id、代入後的主題 id）與各主題的查詢列。未知的步驟或值以 exit 1 結束、什麼都不記。步驟中途冒出的問題仍用單一主題查詢 `lookup.py <主題> --log …`。新增 `--sync-aliases`，把範本別名寫進索引。
- `SKILL.md` 每列改成 `Before: lookup.py --step <id>`，完整指令只在開頭定義一次，列內不再列主題清單（29.6 KB → 20.2 KB）。84 個步驟（新增 `progress-notes`、`first-version`）與 `steps.json` 一一對應，每張步驟表的列序與 `steps.json` 一致。各階段指引與 `motion/README.md` 改為「經由步驟指令一次查一章，不整份讀」。
- `ledger-check.py` 改以 `step` 紀錄為準：每個適用的步驟都要有 `step` 紀錄；條件式步驟在成品出現其標記時適用（例如用到 WebGL 卻沒走 WebGL 步驟就 FAIL）；`<out>/scratch/` 與 `node_modules/` 一律不掃。實際檢查的項目見下方「參照帳簡化」。
- 檔名與工具實際寫出的一致：`out/<slug>.mp4`、`out/<slug>.contact.png`、`out/<slug>.animatic.mp4`、`out/<slug>.poster.png`（原 `out/poster.png`，`3-keys.md`、`5-post.md`、`finishing.md`、`prompts.md` 同步）、元件 `<name>.html`、`/ui` 組的頁面 `<page-name>.html`（名稱不得與任何元件相同）。
- 步驟 3 與 component lane 明寫：用 diagram system 畫的元件也要走 `diagram-plan`、`diagram-layout`、`diagram-markup`（寫進 `<name>.html`）、`diagram-check`、`diagram-taste-gate`。`diagram-semantic-pattern` 移到 `diagram-plan` 之前；`mech-line-ends` 列寫出 `shots/lines.png`；`mech-size` 依零件數與運動系統數判斷，不看機構數。

### Changed（`/draw`：時間紀律與卡關規則）
- 時間只記錄、不拿來換品質：每一步記下 `date` 到 `docs/progress.md`（`progress-notes` 步驟），某一步超過預期份額兩倍時送一行進度給使用者，然後在同一回合繼續。最晚開工一小時內送出第一個能開、能動的版本（`first-version` 步驟，`docs/first_version.md`），之後繼續加深。開工狀態行多一欄「交付」，完成報告多一行「用時：{總計}；第一版於 {經過時間} 送出」。原則、完成條件與紅線同步。
- 卡關規則（`critique-loop.md` §「A stalled row moves on」）：一個門檻列連續兩輪、每輪都對它修正卻沒有提高分數，就判為 `stalled`，寫進完成報告的「未做到的」（最後分數、試過什麼、卡在哪），在 `docs/scorecard.md` 與 `docs/review_log.md` 標記，後續回合用在還會進步的列。卡住的列不得往上改分來結束迴圈，也不得因此停下來問使用者。每輪的開始時間寫進 `R<n>` 標題，超過預期兩倍時送一行進度。

### Added（`/draw`：實作時踩到的技巧章節）
- `mechanism.md`：「Kit limits」（`extrude` 不能挖洞、雜湊擺放會相撞、實體都是直立柱體等上游 kit 的限制，`mech-build-geometry` 前查）、「Draw order for dynamic scenes」（零件會增減、換位或旋轉時，依地面投影做拓撲排序、環狀物拆前後兩半、只在狀態改變時重算）、「Verification side effects」（`drive.mjs` 的 `["lines"]` 會改動頁面要放最後、`Escape` 會啟動恢復導覽的計時器、slow 模式不放慢 timer）。
- `component.md`：「Seek and the idle tour」（seek 清掉排程中的未來事件、取消閒置計時器、固定步長重播不提早停）、「SVG reorder performance」（純 SVG 大量深度排序時快取並量化排序鍵、只在順序改變時用一個 `DocumentFragment` 重排、長導覽預先算好換序時間）。
- 索引重建為 1842 個主題，`lookup.py --check` 0 個未解析。

### Changed（`/ui`：組頁交棒的安全規則）
- 新增「Browser checks」一節：截圖、讀 computed style、檢查頁面只能用兩種工具——使用者真正的 Chrome（有連上驅動它的工具時），或 `/draw` 已 seed 的 `verify-page.mjs`、`perf-check.mjs`、`grab.mjs`（都經 `browser.mjs` 的 `launchChromium()` 啟動）。不准開全新的 Playwright 瀏覽器、agent-browser、Playwright MCP 或其他瀏覽器工具，因為 Windows 上全新 profile 開分頁會以空白密碼探測帳號，幾次就鎖住使用者的 Windows 帳號。兩種都沒有就略過截圖並在結尾說明。
- 交棒契約：輸入是 `<project>/.claude/draw/<slug>/docs/ui_brief.md` 加元件路徑；輸出是同資料夾的 `<page-name>.html`，名稱不與任何元件相同、不用 `index.html`、不覆蓋元件；保留每個元件自己的外觀；這條路上不問使用者，不清楚的地方依 brief 決定並在結尾說明。步驟 1 先讀 `docs/ui_brief.md`，步驟 5 對頁面跑 `verify-page.mjs` 與 `perf-check.mjs` 直到通過，步驟 6 回報兩者結果。Codex 副本同步。

### Fixed（`render.mjs --all` 的母帶檔）
- `render.mjs --all` 原本只寫 `out/<slug>-9x16.mp4` 等帶後綴的檔，從不寫出無後綴的 `out/<slug>.mp4`。現在主格式直接寫成無後綴的主檔（`out/<slug>.mp4`，`.animatic.mp4`、`.contact.png` 等同理），不再另外複製（見下方「主格式」）；`renderFull()`、`renderSheet()` 改為回傳寫出的檔案路徑。

### Changed（`/draw`：參照帳簡化）
- `ledger-check.py` 重寫（約 600 行 → 330 行），只證明步驟指令有跑，不再從檔名或檔案時間推論。PASS 的條件只有四項：`docs/lookups.log` 存在；`ledger-check` 之前每個適用的步驟都有 `step` 紀錄（適用與否看 brief 的 `Form:`／`Approach:`／`When:`，加上成品裡的四種標記：用到 anatomy kit 視為 `approach:mechanism`、WebGL、3D 轉動群組、有 `<svg>` 的 diagram 上的 seek overlay）；紀錄列出的每個主題都有同一時間的查詢列；`lookup_before` 有範本的步驟至少代入一個主題（可為 `none` 的範本如 `camera-{move}` 除外）。
- 拿掉的檢查：產出檔是否存在與 `all_products`、產出檔時間、`kit-{fn}` 呼叫掃描（`set`、`draw`、`ring` 這類通用名稱會讓誠實的 `geometry.mjs` 被誤判）、從 `Move:`／`Seam:`／`Type:`／`Size:`／`candidate.json` 讀範本值、`ordered`、`docs/ui_brief.md` 的 `Page:` 行，以及會誤中 `fillet(` 的管線偵測（`when:pipes` 只看 brief）。`<out>/scratch/` 與 `node_modules/` 照舊不掃；每步一列的表照舊印出（`pass N record(s), M topic(s) printed`，跑了但 brief 不要求的步驟註明 ran; not required）。沒有 `Form:` 也偵測不到時仍 FAIL。
- 只提示、不判失敗：第一版晚於第一筆查詢 60 分鐘以上；紀錄裡出現 `steps.json` 沒有的步驟。
- 新增 `--upto <步驟>`：只檢查該步驟之前的步驟。評分迴圈每一輪改跑 `ledger-check.py <out> --upto critique-loop`，否則整頁說明的情況下，評分時還沒輪到的 `/ui` 組頁步驟會被誤判缺紀錄。
- map：`references/lanes/map.md` 新增「Overrides on the delivery contract」，取消上游「最多兩輪修正」與修復次數上限，改由卡關規則收尾；`map-finalize` 與 `map-perceptual-review` 先印這一章。
- 手繪影片：`design-hand-drawn` 改為只看 `film-template.mjs` 的機制，`film.mjs` 畫這支片自己的場景；影片 brief 的必填欄位改用範本實際的 FILM／ASSETS／VISUAL／UNACCEPTABLE／DELIVER；`pipeline.md` 的格式說明改為主格式不加後綴。
- 散文同步：`critique-loop.md`「The reference ledger」、`mechanism.md`、`2-draft.md`（`Move:`／`Seam:` 行只用來列出該查的章節）、`5-post.md` 的檢查清單、`steps.json` 的 `_about`。

### Changed（`/draw`：diagram 覆寫先讀、§3.9 章節接上步驟）
- 每個 diagram 步驟（`diagram-import`、`-brand`、`-semantic-pattern`、`-plan`、`-layout`、`-markup`、`-cjk-labels`、`-animate`、`-seek-overlay`、`-check`、`-taste-gate`、`-export`）與 `mech-still` 的 `lookup_before` 第一個都是 `diagram-overrides`（`"ordered": true`），照步驟走的建置者一定先看到覆寫，例如品牌網址改用 `grab.mjs` 或一般 fetch，不用 agent-browser。
- `diagram-markup`：範本只當設計系統骨架與 token 參考，SVG 構圖來自 type reference 與 `docs/layout.md`，元件不帶 eyebrow、h1 或頁框；另印出 `lane-diagram-templates-are-design-system-skeleton`。
- `map-finalize` 多印 `lane-map-finalize`（完整的 `archify.mjs finalize … --quality showcase --json` 指令與 `docs/finalize.json`）。`map-perceptual-review` 改為一律執行 `archify.mjs visual-check`，產出照工具實際寫出的 `<slug>.map.visual-check.json` 與 `.<WxH>.<theme>.png`，不再要求沒有工具會寫的 `shots/map-*.png`。
- §3.9 的章節接上步驟：`mechanism-kit-limits` → `mech-build-geometry`；`mechanism-draw-order-dynamic-scenes` → `mech-painters-order`；`mechanism-verification-side-effects` → `mech-line-ends`、`mech-closeups`；`component-seek-idle-tour` → `mech-make-live`、`component-interaction`；`component-svg-reorder-performance` → `component-perf-plan`；`perf-warm-up` → `webgl-layer`。
- 開工狀態行：形式、畫法與交付確定就送出；型別或結構與尺寸在決定它們的步驟之前寫「待定」。

### Changed（`render.mjs`：主格式）
- 新增 `--primary 9:16|1:1|16:9|4:5`，未知值以 exit 2 拒絕。主格式依序取：`--primary`、頁面宣告（`window.timeline()` 的 `primary`，或 `window.PRIMARY_FORMAT`；不合法的宣告會被拒絕）、單獨的 `--format X`、9:16。主格式的輸出不加後綴（`out/<slug>.mp4`、`.animatic.mp4`、`.contact.png`、`.poster.png`），其他格式一律加後綴。`--all` 渲染 9:16、1:1、16:9（主格式是 4:5 時再加 4:5），不再複製檔案。沒有 `--format` 與 `--w`／`--h` 時渲染主格式；每次執行印出用了哪個主格式與原因，例如 `primary format 16:9 (declared by the page)`。
- 16:9 的短片因此寫出 `out/<slug>.mp4`，不再是 `out/<slug>-16x9.mp4`。`design-film-folder` 要求在頁面宣告主格式，`post-render-master` 的完成條件改為「`out/<slug>.mp4` 是主格式，兄弟格式加後綴」；`pipeline.md` 的 render 契約表加上 `primary` 一列。

### Changed（`checks.sh`：輸出以輸入檔命名）
- 輸出以輸入檔名（去掉副檔名）命名，並放在輸入檔旁的 `check/` 資料夾：`out/<slug>.mp4` → `out/check/<slug>.contact.png`，兄弟 `out/<slug>-1x1.mp4` → `out/check/<slug>-1x1.contact.png`；`strip` 帶時間（`<slug>.strip-4.2.png`），另有 `.phone.png`、`.loop_check.mp4`、`.audio.wav`、`.waveform.png`。檢查母帶與每個兄弟格式不再互相覆蓋，也不會蓋掉 `render.mjs` 對頁面拍的 dailies（`out/<slug>.contact.png`、`.phone.png`）。`refs` 寫到 `refs/<base>/frames/` 與 `refs/<base>/tile.png`。`OUT=dir` 照舊可改輸出位置。
- `pipeline.md`、`1-design.md`、`5-post.md`、`finishing.md`、`prompts.md` 與 `steps.json` 的 `post-finish`、`post-review-export` 同步新檔名。

### Fixed（本輪整合）
- `render.mjs` 用法錯誤時當掉：`die()` 用到一個還沒宣告的變數，任何用法錯誤都以 exit 1 當掉，而不是印出訊息、以 exit 2 結束。現在 `--all --out-file` 與缺少 `--html` 都會正確以 exit 2 結束。
- `render.mjs` 印出的分段合併指令無法執行：ffmpeg 會以清單檔所在位置解讀清單裡的檔名，改為先 `cd <out>` 再合併，寫出 `<slug>.parts.txt` 與 `<slug>.mp4`。
- 啟動檢查加嚴：`test_draw_skill.py` 對 Claude 與 Codex 兩份副本逐一檢查每個啟動點；手寫的 `Local State` seed 必須帶 `/draw:` 標記。同步腳本保留這個標記，不把它轉成 `$baransu:draw:`。
- `test-draw-toolchain.sh` 拿掉找不到 `component-example.html` 時退回 `explainer-template.html` 的備援。
- `test_draw_skill.py`、`test_draw_lookup.py` 的斷言改為 film／component 與新的主題 id（例如 lane 章節、表單區的 `**film**`／`**component**`、`### Component rows`、`mech-join-{form}` 的代入值）。

### Changed（`/draw`：完整品質、不中途停下來問）
- 拿掉預算：計畫、完成條件與完成報告不再有「預算」與「砍掉的」欄位。原因是模型會為了填這一欄而主動刪減內容。改成一條原則：預設做到 reference 要求的完整品質，不拿時間或成本換品質，只有使用者明說要快才降。完成報告的「砍掉的」改為「未做到的（原因）」，只在真的做不到（缺素材、環境不允許）時填。motion 各階段指引裡的 complexity budget 與 budget cuts 措辭一併移除。
- 不中途確認：計畫訊息從 Input PAUSE 改為固定格式的「開工狀態行」（形式／畫法／型別或結構／尺寸／理由），送出後直接開工。拿掉的停點：計畫確認、品牌關卡（預設用內建外觀，使用者提到品牌才讀 `onboarding.md`）、「請提供參考」（改走 `1-design.md` 的克制字體方向並記入 `docs/style_guide.md`）、「兩種都渲染再問」（改為都渲染、自己選、理由記入 `review_log`）、「`<start>` Ask for the inputs」（改為寫明給定與假設的輸入），以及 diagram README 的「先確認計畫」。唯一保留的停點是 brief 指名、使用者卻沒給的真實素材或事實（數字、日期、logo、音軌）。完成報告加上「本輪未向使用者提問」一行。紅線「先寫檔再發計畫」換成「停下來問使用者選形式、畫法或規模」。`loop-pauses.md` 同步：只剩缺素材一個錯誤出口，full render 不再需要授權（只寫進本次輸出資料夾，品質門檻仍是 contact sheet 8 分）。
- 自動路線：形式、畫法、尺寸依內容判斷，使用者明確指定的優先，不再問要哪一條路。原本「兩種都行就說另一種存在／附上表格」移到完成報告的附註。
- 範本改稱「機制範例」：`component-example.html`（原 `explainer-template.html`）、`loop-template.html` 與 seek 範本只示範 `seek(t)` 契約、scrubber 與 render hooks，視覺、構圖與互動方式來自 reference，不照抄範例的樣子。起因是兩次實際執行都照範本畫、沒讀 reference。三個範本的開頭註解都改成同一句：只拿機制、設計來自 reference 與 brief，走到需要它的那一步、外觀定案後才打開，打開前先用 `lookup.py` 查該步的主題（seek／loop 範本原本的「複製這個檔再改 [EDIT] 區」拿掉，`component-example.html` 新增開頭註解）。diagram 的 `template*.html` 是設計系統骨架，維持原說法，只補一句 SVG 內容的構圖來自 type reference。

### Changed（`/draw`：步驟指引＋書的目錄，用到再查）
- `SKILL.md` 改寫成步驟指引加檔案目錄（46.7 KB → 29.6 KB）：每一步一列，寫明做什麼、做到什麼算完成、動手前要查哪些主題（topic id）。分成 0. Preflight、1. 選形式、2. 選畫法、各 lane 的步驟、機構圖步驟與 4. 檢查交付，後面是 reference 目錄、紅線與完成報告範本。各 lane 的細節移到新的 `references/lanes/diagram.md`、`map.md`、`motion.md`、`component.md`。不要求開工前把 reference 全文讀完：走到一步先查它指的章節再動手，其餘 reference 遇到問題才查。
- 一主題一章：draw 自有的 reference 重整成一個主題一章。`camera.md` 24 種運鏡各一章、`transitions.md` 每種轉場與每條規則各一章、`springs.md` 每個 primitive、數值家族與動畫原則各一章、`composition.md` 每種應用各一章，motion 其餘 15 份與 `critique-loop.md` 同樣處理。被其他檔案引用的標題保留原名。原樣收錄的上游檔案不切，粒度由索引做到。
- 機構圖路由（`mechanism.md`）改成 anatomy 十個步驟的步驟表，每步對到上游檔案的章節；`kit.md` 只在寫程式時依主題查（cylinder、slab、tube 各是獨立主題）。

### Added（`/draw`：索引、查詢與查詢紀錄）
- `references/index.json` 與由它產生的 `references/INDEX.md`（書末索引）：1836 個主題，指到檔案的章節，必要時指到表格某一列、清單某一項或某幾行指令。126 份檔案的每個標題都有主題；`kit.md` §2–8、§10–15 每個函式各一個主題（如 `kit-cylinder`、`kit-slabOf`、`kit-tubePieces`），24 種運鏡與 13 種轉場各一章。
- `scripts/lookup.py <主題> [--log <輸出資料夾>]`：只印出那一章或那一列；`--log` 把每次查詢追加到 `docs/lookups.log`（時間、主題、檔案、章節、列）。另有關鍵字搜尋、`--list`、`--render-index`（重產 `INDEX.md`）與 `--check`（每個指標都解析得到、`INDEX.md` 與資料一致）。
- `references/steps.json`：每個形式×畫法的步驟資料（適用條件、做什麼、完成條件、必查主題、產出檔案），共 82 步，與 `SKILL.md` 的步驟表一致。
- `scripts/ledger-check.py`：參照帳就是 `lookups.log`。依 brief 的 `Form:`／`Approach:`／`When:` 判斷哪些步驟適用；每個適用步驟的必查主題都要由它的步驟指令印出並記在 log 裡（不看檔名與檔案時間，見「參照帳簡化」）。成品偵測保留：用到 anatomy kit 視為 mechanism，用到 WebGL、3D 或 diagram SVG 上的 `window.seek` 會加上對應條件。輸出每步一列，退出 0 才算完成。
- `critique-loop.md`：每輪順序是查詢帳通過 → 機械檢查 → 評分。評分卡保留共用列，另加各畫法專用列（mechanism、diagram、motion／運鏡、component、map、free creative），8 分門檻看專用列，每列註明是機械檢查（附指令）還是人工判斷。
- `tests/scripts/test_draw_lookup.py`：每個索引指標都解析到唯一章節、每個標題都有主題、cylinder／slab／tube 是三個主題、每個 kit 函式各一個主題、`steps.json` 的必查主題都解析得到、`--log` 的格式。`verify-skills.py` 的殘留掃描白名單加上索引逐字引用的 vendored 標題「Crossing arrows — bridge / hop」。

### Added（`/draw`：anatomy 完整收錄）
- `scripts/anatomy/`：上游 [wheresryan22/anatomy](https://github.com/wheresryan22/anatomy) commit `454a0ef`（2026-10-13）整份收錄，119 個檔案除 `capture.mjs`、`drive.mjs`、`turn-check.mjs` 各加一行 `/draw:` 安全修補（見 Fixed 的帳號被鎖）外，與上游逐位元組相同。`SKILL.md` 改名為 `ANATOMY-SKILL.md`，避免被當成獨立的 skill 載入。收：references（含 `publish.md`）、kit、8 個範例的原始碼、scripts、tests 與 `*.test.mjs`、evals、agents、LICENSE、README、CHANGELOG、CONTRIBUTING、`.github/assets/`。不收：範例建置出的 `*.html`（`node scripts/anatomy/examples/<name>/build.mjs` 可重建，已離線驗證 dial-indicator 重建結果與上游相同、raptor-engine `--audit` 通過）、`publish.mjs`、`session.mjs`、`fingerprint.mjs` 及其測試（會連網、git push、讀 `~/.claude` 逐字稿）。
- `references/mechanism/collection/`：作品集 52 頁的說明與 prompt 逐字收錄，另有 `INDEX.md`。授權依 anatomy 首頁原文「MIT, for the skill and for the figures」。`mechanism-catalog.md` 改為索引，每列連到對應頁。
- `references/mechanism/anatomy-page.md`：anatomy 首頁（skills.wheresryan.sh/anatomy）全文依閱讀順序收錄成 Markdown，`01 Objects, not diagrams` 到 `12 Questions`、程式碼區塊、三張表與註腳都在，開頭註明來源網址、擷取日期與 MIT 授權。
- `references/mechanism/mechanism.md` 改為步驟表：照 anatomy 的十個步驟走，每步查 `ANATOMY-SKILL.md` 與 craft、walkthrough、kit、motion、verify（需要時 webgl、3d、react）裡對應的章節，開最接近的上游範例，用上游 kit 與 `build.mjs --audit`、`lines.mjs`。draw 只補與 component／film／diagram 的接合與效能規則，並明文覆寫上游兩處降規：Figure／Hero／Epic 只是尺寸類別的名稱，寫進開工狀態行，不估時間、不先問、不縮小、不拒做 Epic；4× 細節檢查不分尺寸，一律涵蓋整張圖；預設加上指標與鍵盤操作，內容需要時直接用 WebGL 或 3D，使用者說要靜態圖才不做。上游檔案一律不改，覆寫記在 `NOTICE.md`。
- `NOTICE.md`、`verify-skills.py` 的 vendored 清單加上 `scripts/anatomy/` 與 `references/mechanism/collection/`；新增 `.gitignore` 排除建置出的範例頁與上游檢查輸出。

### Added（`/draw`：效能檢查）
- 「Two big machines」頁面讓整個瀏覽器卡死，根因是渦輪扇圖的 38 KB fragment shader 在 Windows ANGLE D3D11 上同步 link 超過 279 秒，卡住 GPU process 主執行緒。`component.md`（原 `explainer-page.md`）與 mechanism 路由加入效能規則：D3D11 上 link ≤ 200 ms、shader 尺寸上限、`KHR_parallel_shader_compile`、預熱、多張重圖錯開初始化、long task ≤ 50 ms、只在有動時跑 loop、只重畫動的零件、DPR 上限 1.5、不在 observer 內強制 layout。
- `scripts/motion/perf-check.mjs`：headless 量測每張圖、全部一起與靜止時的表現，以及 shader link 與 draw 時間；設硬性逾時，超時就關掉瀏覽器並印出最後一個 GL 呼叫。Windows 上指定 `--backend d3d11` 而 renderer 不是 D3D11 時判為 NOT-EVIDENCE。component 與 mechanism 的 lane 檢查加跑它。
- `doctor.mjs` 找到 Chromium 後印出 `export CHROME_PATH=…`，anatomy 的 `capture.mjs`／`drive.mjs` 只認這個變數。

### Changed（`/draw`：驗證回合的修正）
- diagram 覆寫層：`references/diagram/README.md` 新增「Overrides: where /draw departs from upstream」一節，逐句點名上游 diagram 檔案裡會停下來問的地方（四個參數、taste-gate 的確認列、匯入時的頁面／區塊／大小、品牌路徑、type reference 的 halt and ask、讀不到的品牌來源、匯出），一律改為自己決定並記入 `docs/brief.md`。只保留使用者必須提供的事實（空白標籤、圖片或讀不到的來源、沒給意義的識別碼、圖表缺的數值、匯入來源裡沒有的元件、完全沒給檔案）。品牌路徑不再需要核准、不改已安裝的 `style-guide.md`，profile 直接存檔，`.diagram-design` 只在使用者要求時才寫。「三欄表格能說清楚就不畫」改為照畫，表格放進完成報告的附註。上游檔案不改，`NOTICE.md` 記下這一層。
- `ledger-check.py` 的成品偵測：用到 WebGL 或 3D、anatomy kit、`tubePieces(`／`fillet(`，或 SVG 頁面上有 `window.seek`，就加上對應的畫法或條件，那些步驟的必查主題也要在 `lookups.log` 裡；掃描範圍是 .html／.js／.mjs／.ts／.svg 等，不看 `node_modules`。
- `perf-check.mjs` 加嚴：Windows 上不論 `--backend` 為何，renderer 不是 D3D11 都判為 NOT-EVIDENCE、退出碼非 0（`--backend swiftshader` 也不能在 Windows 上 PASS），且同時有 FAIL 列時 RESULT 仍是 NOT-EVIDENCE（量測環境不對，FAIL 也不算數）；靜止時只要還有 draw call 或 rAF 回呼就 FAIL（loop 停不下來）。`component.md` 改為照實寫出 perf-check 量得到與量不到的項目，量不到的（shader 大小、平行編譯、預熱、錯開重圖、observer、像素預算、閒置 fps）列為讀程式碼檢查。
- 機制範例 `component-example.html` 照自己的效能規則改寫：靜止或圖全部捲出畫面時 frame loop 停止，可見或按下播放時重新啟動；循環圖每張最多 30 fps；DPR 上限 1.5（視窗寬度小於 480 px 時為 1）；canvas 尺寸在 resize 時才重新量。

### Fixed
- Windows 帳號被鎖：Windows 上的 Chromium 用全新 profile 開分頁時會呼叫 `LogonUser` 檢查空白密碼，每次都記一筆登入失敗，10 分鐘內 10 次就鎖帳號。`browser.mjs` 的 `launchChromium()` 改為先在 profile 的 `Local State` 寫入已檢查紀錄再啟動；五支 motion 腳本、anatomy 的 capture／drive／turn-check、map 的 `visual-check.mjs` 與 diagram 的 `lint-render.py` 都改走這條路。關閉或強制結束瀏覽器後，暫存 profile 資料夾改為重試刪除（最多 10 次、間隔 200 ms），等 Windows 放開檔案鎖，不再每跑一次就留下一個資料夾。
- 範例程式也會鎖帳號：`references/diagram/export.md` 的 PNG 匯出範例與 `references/motion/pipeline.md` 的「三十行渲染器」原本直接 `chromium.launch()`，改為先在暫存 profile 寫入 `Local State` 再用 persistent context 開啟，用完刪掉 profile（export.md 的改動逐行標 `/draw:`，NOTICE 記錄）。`test_draw_skill.py` 的啟動檢查改掃 .md 的程式碼區塊與 .js／.sh 等檔，任何未 seed 的啟動都會讓測試失敗。
- 暫存資料夾外漏：`render.mjs` 開啟瀏覽器後出錯不再直接 `process.exit`，改由 `finally` 關瀏覽器並刪掉所有自建的暫存影格資料夾（`beats`、`strip` 原本從不刪）；`doctor.mjs` 在 `finally` 關閉仍開著的瀏覽器；`perf-check.mjs` 逾時發生在啟動途中時，等啟動完成（最多 4 秒）再關掉瀏覽器並刪 profile。
- 拿掉輪數上限：評分迴圈與匯出審查原本的「最多三輪」「at most three passes」全部移除（`4-shoot.md`、`motion/README.md`、`critique-loop.md`、`review.md` 等）。motion 與 component 至少三輪，之後一直跑到每個列都 ≥ 8，每一輪都記進 `docs/review_log.md`。
- 措辭修正：`SKILL.md` 的「theme tokens」改為「`:root` 上的色彩 token，數值來自 brief」；mechanism 的尺寸只寫類別名稱；hand-drawn 不再「以範本為起點」，改為 `film.mjs` 只拿機制、場景整個換掉。
- diagram 匯出：`export.md` 的「說明比例不合並提議重畫」改為直接用相符的 preset 重畫、匯出那一份，並在完成報告註明。motion 的 `review.md` 聽不到混音時不再請使用者聽，改列入完成報告的「待人工確認」。
- `tests/skills/test-draw-toolchain.sh`：Windows 上瀏覽器測試原本因裸 `import()` C 槽路徑失敗而整段略過，改用 `browser.mjs` 找 Playwright；T10 的 `file://` URL 改用 `pathToFileURL` 建立。新增 T11–T16（perf-check 語法、範本通過且靜止時 loop 停止、卡住的頁面在逾時內失敗、非 D3D11 renderer 判為 NOT-EVIDENCE、Windows 上 `--backend swiftshader` 判為 NOT-EVIDENCE、非 D3D11 下同時有 FAIL 列仍判為 NOT-EVIDENCE）。

## [7.4.2] - 2026-10-12

### Fixed（`/draw` 後製，實際做一支 15 秒影片時發現）
- `sfx.mjs`：配樂底的取樣率或位元深度不符時，自動用 ffmpeg 轉成 48 kHz 16-bit 再混音。`music.mjs`、`chiptune.mjs` 輸出 44.1 kHz，原本照 `beat-grid.md` 的流程串起來一定會失敗。已記入 `pipeline.md` § Known environment failures。
- `beat-grid.md` 的 true peak 規則：AAC 抬高峰值的幅度依瞬態而不同，實測從約 1 dB 到 2.6 dB。改成先對 WAV 做響度標準化，再量解碼後的 MP4，峰值不到 −1 dBTP 就把 WAV 的上限往下壓（−2.2 → −3.2）。並註明不可直接對 MP4 做標準化，實測會把峰值推到 +0.2 dBTP。

## [7.4.1] - 2026-10-12

### Added（`/draw`：6 : 3 : 1 畫面層級原則）
- 新增技術手冊 `references/motion/composition.md`：60 % 空間基底（低頻、安靜）／30 % 敘事陳設與過渡（中頻、引導視線）／10 % 視覺錨點（高對比），比例是經驗起點而非硬性規定。內容包括：適用面向（構圖、光照、配色、空間布置、物件形體、資訊密度）；配色先決定要保留什麼，用明暗而不是去飽和來建立主次；光照寫清楚「從哪來、照到哪」；細節要有放的地方，也要有停的地方；電影的三層「空間底盤 → 人物生活 → 劇情重點」，附《布達佩斯大飯店》《沙丘》《寄生上流》《全面啟動》《辛德勒的名單》的讀法；開工的五個問題、縮圖檢查、場景 prompt 結構，以及影片的延伸（不把秒數切成 6:3:1，焦點可以移動、可以放大）。
- 接入各處：草稿的美術方針逐鏡頭寫出 6 : 3 : 1；key card 的構圖欄改成 60／30／10，檢查項加入縮圖檢查；評分卡的構圖列；directed prompt 的 LOOK 行；review 的 phone 檢查。

### Changed
- 原本草稿階段的「6 → 3 → 1」更名為「方向收斂（廣 → 3 → 1）」，避免和 6 : 3 : 1 畫面原則撞名；內容不變。

## [7.4.0] - 2026-10-12

### Changed（`/draw` motion：重組為「五階段工作指引＋技術手冊」）
- `references/motion/` 改為兩層：第 1 層是五個階段的工作指引，依序閱讀——`1-design.md`（設計）→ `2-draft.md`（草稿）→ `3-keys.md`（關鍵幀／首尾幀）→ `4-shoot.md`（攝影）→ `5-post.md`（後製）。每份寫明這一步解決什麼、核心觀念、步驟、產出與過關清單。第 2 層是技術手冊，執行到某一步才翻：`pipeline`、`prompts`、`springs`、`camera`、`transitions`、`type`、`beat-grid`、`review`、`finishing`、`chapters`、`commission`、`explainer-page`、`mechanism`、`mechanism-catalog`。`README.md` 是地圖與查詢索引。
- 退役 `storyboard.md`、`prompt-ladder.md`，內容拆入 `1-design.md`、`2-draft.md`、`prompts.md`、`review.md`。重組前後以腳本比對每個數字、程式碼片段與程式碼行，再逐句比對 4-gram，確認資訊未遺漏。
- 草稿階段新增：方向以 6 → 3 → 1 收斂（6 個一句話方向 → 3 個各做一張 style frame → 選 1，並寫下落選理由）、color script、攝影計畫 `docs/camera_plan.md`（景別、角度、焦段感、具名運鏡與時長曲線、停留、畫面方向與 180° 規則）、節奏強度曲線、時長表（X-sheet），以及配臨時聲音的 keys-only animatic。
- 關鍵幀階段新增 key card：每張 key 定稿時須含 read、why、構圖（stage／life／focus）、framing（鏡頭框、深度層、焦平面）、主體狀態、文字、look、motion in／out、聲音、各格式重排、檢查項。layout 跟著 key 一起定，攝影階段只在已核准的 framing 之間移動。
- `SKILL.md` 的 motion lane 改為五階段表＋技術手冊清單；新增測試鎖住結構（五階段與過關清單、README 不留孤兒檔、退役檔不再出現）。
- 出處段落移出 reference：12 份 motion reference 底部的 `Attribution:` 段落，搬到 `NOTICE.md` 的「Sources by reference file」，agent 讀的檔案只留指示。會過時的事實（X 上傳限制、引擎的授權與價格）改在原句旁標「截至 2026-10」。
- draw 的 `description` 精簡為三句（做什麼、何時用加觸發詞、何時不用），從約 1010 字元降到 476；全 repo listing 總量從 8259 降到 7500。

### Changed（`/draw` 整體流程：preflight → 形式 → 畫法 → 產製 → 檢查）
- `SKILL.md` 改成一條固定流程：**0. Preflight**（`node scripts/motion/doctor.mjs --install` 直到 `READY`）→ **1. 選形式**（page／diagram／map／motion，map 為獨立形式）→ **2. 選畫法**（Diagram 系統／機構／自由創意，與形式交叉成立）→ **3. 產製**（靜態直接做；會動的走草稿 → 關鍵幀 → 攝影 → 後製，並依形式調整份量）→ **4. 檢查與交付**。
- 環境原則改為「缺工具就安裝，不回報停工」；每次執行遇到新的環境錯誤，都要在結束前補進 `pipeline.md` § Known environment failures。

### Added（工具鏈）
- `scripts/motion/doctor.mjs`：開工前一次檢查 Node、ffmpeg、Playwright、Chromium、Python UTF-8，`--install` 自動用官方指令補裝；最後實際渲染範本兩次比對 hash，並用 ffmpeg 編碼，通過才印 `READY`。
- `scripts/motion/browser.mjs`：render／grab／verify-page 共用的 Playwright 與 Chromium 搜尋，修正 Windows 上絕對路徑 `import()` 失敗，涵蓋 Windows、macOS 的 Playwright 快取位置與 `chrome-win64`、`chrome-mac-arm64`；任何已安裝的 Chromium 版本都能用；找不到時印出各平台安裝指令。
- `assets/motion/loop-template.html`：首尾銜接的 loop 範本（整數圈運動、沿圓周取樣的 `loopNoise()`、跨接縫的 `wrappedSpring()`、`?seam=1` 並排檢查），已驗證最後一格與第 0 格連續。
- `render.mjs --format 4:5`（`--all` 仍為三種格式）。
- `finishing.md` § Loops 補上：強調元素也要跑整數圈、文字不跨接縫、渲染前用 stills 檢查接縫。

### Added（`/draw` motion 新內容）
- `camera.md`：24 種具名運鏡與轉場（pan、tilt、dolly、zoom、tracking、orbit、crane、dolly zoom、rack focus、handheld、FPV、dutch、slow motion、speed ramp、time-lapse、freeze frame…），以 parallax 規則在 canvas 上實作，並附 `layerCam`、`retime`、`handheld`。`transitions.md` 補上 jump cut、cross dissolve、smash cut、J-cut、L-cut。
- 機構圖（跨 lane 的獨立章節 `SKILL.md` § Mechanism figures，檔案在 `references/mechanism/`）：寫明觸發情境（「X 怎麼運作」、原理、機制、互動式說明）、與流程圖的分界（重點在連接與流向→流程圖；重點在零件行為、狀態變化與失敗情境→機構圖），以及落在哪條 lane（預設 page；影片裡是一個鏡頭；靜態需求用剖視或爆炸圖）。`mechanism.md`（「物件本身就是解釋」、Figure／Hero／Epic 規模、十步驟、繪製／動態／shader／3D／驗證規則，以及「自己發明機構」的指引：動詞 → 機構家族對照表、零件與意義的對照模板、上線前檢驗）；`mechanism-catalog.md`（Anatomy collection 全部 52 個概念與機構）。
- `commission.md`：接案流程（範圍、方便改版的建置方式、匯出審查、打包、Remotion Route B、找案子、報價公式、提案寫法）。
- 動作數字與審查技法：cubic-bezier 表、damping ratio 換算（含本 skill 各 feel 的對應值）、時長與 stagger、一個主角動作的層級規則、動畫原則寫成數字、以影格編號下筆記、onion skin、速度曲線、把感覺翻成數字的對照、常見故障修正表。
- 聲音同步與量測：命中點落在畫面後 1 影格（保留「緩慢接觸前約 0.03 s」作為例外並寫明取捨）、高出 bed 3–6 dB、手機頻段響度、AAC 補白與 true peak、cosine phase 起音；收尾：GIF 延遲陷阱、X 上傳限制、4:5 版面、180° 快門外觀。
- 出處列入 `NOTICE.md`：@showheyohtaki、@flxrnc、@0xCodila、@rexan_wong 的公開貼文，以及 wheresryan22/anatomy（MIT）。

## [7.3.3] - 2026-10-08

### Fixed（Codex skill 圖示載入）
- 將 14 個 skill 的 `icon-small.png`／`icon-large.png` 原檔移至各 skill 的 `assets/`，同步 `agents/openai.yaml`，避免 Codex 以 `icon path must be under assets/` 忽略圖示。
- Codex parity 檢查的專屬圖檔規則改為 `assets/icon-*.png`；Claude 與 Codex plugin 版號同步為 7.3.3。

## [7.3.2] - 2026-10-08

### Added（plugin icon 與 skill icon，Krea 2 產生）
- `assets/icon.png`（256）、`logo.png`、`logo-dark.png`（512），水墨平衡意象：Claude 版 `plugin.json` 設 `icon`（Anthropic plugin 目錄用，Claude Code 執行時不讀）；Codex 版 `extensions."com.openai".interface` 設 `composerIcon`、`logo`、`logoDark`、`brandColor`（#C2452D）。
- Codex 版 14 個 skill 在 `agents/` 放 `icon-small.png`（128）、`icon-large.png`（512），新增 `agents/openai.yaml` 設 `icon_small`、`icon_large`、`brand_color`。`verify-codex-parity.py` 的 Codex 專屬樣式加上 `agents/icon-*.png`。
- `transfer.py`（選用草稿腳本）把 plugin 頂層 `assets/` 視為已知元件並原樣複製，不再列為無轉換規則的 component。

## [7.3.1] - 2026-10-08

### Changed（`/write`：標準用字「介接」）
- zh 規則新增「標準用字」說明（不編號，不影響既有規則編號）：模型常把「介接」寫成「界接」，讀起來通順但不是政府標準用字；Refine／Generate 一律寫「介接」。
- Proofread 的台灣商業用語對照補上「界接→介接」，列為 用語不妥。Codex 版同步。

## [7.3.0] - 2026-10-08

### Docs（README 改為概念首頁，細節移到 docs/）
- README 改寫為短首頁：橫幅概念圖、核心理念、五個家族卡片（各一張概念圖）、一件事怎麼走（三頻段）、快速開始與範例 prompt。
- 細節移到 `docs/`：`README.md`（索引與 skill 總表）、`philosophy.md`、`routing.md`、`install.md`、`development.md`、`skills/{plan,verify,make,learn,ops}.md`；舊 README 內容逐段搬入。
- 新增概念圖 `docs/images/hero.png`、`docs/images/family-*.png`（GPT-6 Astra 產生）。skill 內容未變。

### Changed（`/codex-skill-transfer` 0.19.0：從轉換器改為手動維護的對照表＋檢查清單）
- **定位**：Claude 版與 Codex 版改為並列手動維護、各自是自己平台的正本。SKILL.md 改成四種模式——Checklist（預設，唯讀，輸入一對 Claude／Codex 目錄、輸出落差報告）、Port by hand、Generate（選用，`transfer.py` 只寫 scratch 目錄，不得覆蓋手動維護的 Codex 版）、Reference question；Outcome Contract、報告骨架（一致／需修正／刻意省略／降級風險／待查＋`Next-port follow-ups`，新增 `fix-now` 處置）與 Boundaries 同步改寫。
- **對照基準更新到 Claude Code 2.1.293／Codex CLI 0.161.0（`rust-v0.161.0`，2026-10-08）**，並保留【推論】／官方未公布標記（*(inferred)*／*(unpublished)*）不升格為事實。Step 2 刷新清單改指 `learn.chatgpt.com/docs/*`、`developers.openai.com/plugins/*` 與 OpenAI 的 Claude plugin 移植指引。
- **新增 Step 3 檢查清單**：skill（Codex 只讀 `name`／`description`／`metadata.short-description`、內文無路徑變數改相對路徑、`$plugin:skill` 呼叫、工具改寫、`templates/` 等額外資料夾一律保留）、plugin（manifest 格式二選一、欄位去向、bundled agent 選項 A／B／C、hooks 12 事件）、Claude 專用元件表（mods、monitors、userConfig、dependencies、LSP 等）、marketplace 讀取順序與 `.claude-plugin` fallback、版本與快取。
- **references**：`skill-mapping.md` 加「Codex reads?」欄、補 `disallowed-tools`／`background` 列、修正 description 長度說明與 `agents/openai.yaml` 全欄位、工具表補 `Monitor`／`Artifact`／`Workflow` 等列、32 KiB 上限標為未驗證、`copy_aux` 改為「手動保留全部資料夾，腳本行為是已知缺口」；`plugin-mapping.md` 重寫（讀取順序、格式選擇、欄位去向、元件表、hooks 細節、選項 A／B／C、新增版本與快取段）；`agent-mapping.md` 補 `spawn_agent` v1／v2 參數與乾淨 context 寫法、resolver 改建議內嵌 `developer_instructions`；`marketplace-mapping.md` 補讀取順序、來源對照、啟用方式；`CODEX_PORT_PLAN.md`、`loop-pauses.md`、`evals.json` 對齊新模式。範例改用通用名稱。
- `AGENTS.md` 的 Codex 版說明改為「手動維護、腳本選用」。
- Codex 版 `codex/plugins/baransu/skills/codex-skill-transfer/` 手動同步（未用腳本產生），frontmatter 加 `metadata.short-description`；`test_codex_skill_transfer.py` 的 skill 版本釘選改為 0.19.0。
- **Makefile**：移除以腳本重產 Codex 版的 `mirror`，`mirror-check` 換成 `parity-check`——新增 `scripts/verify-codex-parity.py`，不跑 `transfer.py`，只檢查 `plugins/baransu/skills/**` 與 `codex/plugins/baransu/skills/**` 逐檔對應（允許 Codex 專有的 `agents/openai.yaml`）及兩份 manifest 版本一致；`ship-check` = `test` + `parity-check`。`test_ship_check_gate.py` 改釘新閘門（plan 不得出現 `transfer.py`），並加 parity 腳本的 fixture 測試。
- `README.md`（技能表與 Codex 版說明）、`CLAUDE.md` 技能表 `/codex-skill-transfer` 列與 `tests/integration/claude-md-skills-baseline.txt` 同步改為「手動維護的移植對照＋檢查清單，草稿腳本選用」。

## [7.2.0] - 2026-10-07

### Added（motion lane：三篇文章的 gap review 全部併入）
- **畫面上出現什麼的詞彙**（@0xMovez 文章 review）：`motion.js` 新增 `cursor`（沿 UI 彈簧移動、按下縮放）、`typed`（seeded 逐字打字）、`drag`（握住時聽手、放開回彈）、`camera`（每個狀態一個 rect，push-in 即較小的 rect）、`words`（逐字落地）、`wipe / iris / whip`（轉場為幾何而非淡出）、`drawOn`、`swapBlur`、`countUp`。新 reference `references/motion/type.md`（兩個字型＋accent、hook ≤ 5 字 ≥ ⅓ 畫面高、不放角落）與 `transitions.md`（每個接縫一個決定、accent 帶過去、不黑場）；`springs.md` 補 cursor／camera 段與 ease 的唯一例外。
- **一條 timeline 三種格式**：`seek-template.html` 讀 `?f=9:16|1:1|16:9`、所有位置從 layout 物件 `L` 推導（`L.safe` 安全區、`L.show` 直式少放東西）；範本改為 hook 逐字落地 → UI 自組裝＋游標真的點＋一個數字 → morph，接縫用 wipe。`render.mjs` 新增 `--format` / `--all`（full、animatic、contact、phone、stills 皆可，輸出加 `-9x16` 等後綴）、`--safe`（每格畫出安全區）、`stills --at`、`animatic`（24 fps、無模糊、半尺寸看節奏）、`--from/--to --keep` 分段渲染並印出 concat 指令。
- **素材與參考**：`scripts/motion/grab.mjs`（使用者貼的 URL → 三格式截圖＋整頁＋`manifest.json` 含計算後的字型與顏色）；`checks.sh refs`（參考影片每 0.5 s 一格＋拼圖）、`checks.sh audio`（純音訊＋波形圖：閉眼聽有沒有形狀）；`music.mjs` / `chiptune.mjs` 明列為任何影片可用的 Route A 音樂底；`beats.py` 限制說明（漂移節奏給 `--bpm --start`）。
- **流程規矩**（@0xwhrrari「Motion Engineering」review）：`storyboard.md` 新增 `docs/brief.md` 骨架（事實 vs 選擇、什麼算不可接受、主要格式）、三個分鏡變體先選一、每鏡 `enter / exit / why`（寫不出 why 的鏡頭砍掉）、HOOK→PROBLEM→REVEAL→PROOF→CLOSE、style_guide 補 Composition／Motion 欄；`pipeline.md` 新增五層工作室對照表（每層一個檔，沒檔就是跳過）、片夾固定結構、續跑先讀 review_log；`loop-pauses.md` 新增素材清單與每鏡 stills 兩個 Input PAUSE，**brief 點名的真實素材缺了就是錯誤出口**不是預設；`critique-loop.md` 加 Continuity 列、安全區、海報幀、純音訊、鏡頭移動後眼睛在哪等 hunt 項，review_log 要寫證據（哪一格）；完成報告加「素材清單／待人工確認／重渲指令」。
- **631 構圖原理**（南鸢文章 review）：計分卡 Composition 改為三層讀圖（安靜底、引導層、單一差異的焦點）；「先修什麼」診斷順序（找不到焦點→砍競爭者而非放大主角；空間看不懂→回大形；風格變淡→查 Keep 清單）；storyboard 每鏡 `stage / life / focus` 欄與「最大 ≠ 最被看」規則；prompt-ladder `<inputs>` 加「風格必須保留的二三特徵」、`<direction>` 與 L4 Look 加三層句；taste-gate 加縮圖測試（320 px 寬焦點是否先被看到）；手繪 lane `detail.md` 加光的三個職責（主光／補光／局部光，不是三盞燈）與 set dressing。色相三分與 6:3:1 數字不進（與一色 accent 衝突，依文章自己的「保留顏色、改變亮度」處理）。
- evals 6–9：L2 品牌 reel（grab → 三格式）、歌詞 kinetic type 落拍、90 秒長片分章＋animatic＋分段渲染、手繪短片。

### Fixed
- `render.mjs` warm-up 先把整條 timeline 掃一遍：canvas 第一次 `ctx.font` 指到某個字重才會觸發載入，`fonts.ready` 不知道，第一幀畫到 fallback 導致 `hash` 非決定性。
- `lint-skin.py`：輸出檔是 `<slug>/index.html` 時 a11y ID 前綴取資料夾名，不再要求 `index-title`。
- SKILL.md：lane 觸發詞補 cursor-driven demo／logo sting／kinetic type／lyric video／history film；紅線加 glow on UI chrome、particle bursts、UI 狀態間黑場；「visibly empty」只適用 diagram／map。

### Verified
- 五個 evals prompt 以子代理實跑（1 map／2 diagram／3 motion／4 page／5 mermaid 匯入）全部產出符合 expected_output 並獨立複驗；子代理環境解析不到 plugin skill，自動觸發那一半需在真實 session 驗。

## [7.1.1] - 2026-10-07

### Fixed（獨立 review 的 7 項發現）
- **Taste gate 補齊**：新增 `references/diagram/taste-gate.md`（上游 §4 反模式表 + §9 畫前檢查表，路徑改指本 skill）；SKILL.md、critique-loop、import-*、output-spec、primitives-core、type-high-level、commands/* 原本指向不存在的「SKILL.md §9」全部改指此檔。
- **map lane 環境提示**：SKILL.md 與 `references/map/README.md` 明寫 archify 的瀏覽器閘只認 `ARCHIFY_CHROME`（容器加 `ARCHIFY_CHROME_NO_SANDBOX=1`），附指向 Playwright Chromium 的一行；`chrome-unavailable` 是環境問題不是候選問題。同一行設 `ARCHIFY_UPDATE_CHECK_DISABLED=1`，`finalize` 收據實測 `update: disabled`、四道閘全過。
- **品牌來源明示允許**：自包含段改寫——不連網找內容、不依賴其他 skill 安裝，但使用者指定的品牌來源（網址、token、資料夾、其他 skill 的 token 檔、`/ui` 的 `reference-<slug>.md`）可經 `onboarding.md` 讀一次並存成 profile；style-guide gate 改為上游 §0 的「第一張圖先問」Input PAUSE，與 `loop-pauses.md` 對齊。
- **路徑改寫補漏**：`animation.md`、`type-architecture-delta.md` 與各型 reference 的 `scripts/verify-*.py` 改指 `scripts/diagram/repo/`；上游 `test-verify-*` 標為未 bundled。
- **seek overlay**：模板預設不自動播放（開頁停在 t=0）；`seek-overlay.md` 明列與 `animation.md` 的三處刻意差異（JS 驅動屬性、彈簧、runtime path measurement）及 `.seek.html` 本體不受 `self_check` 管、由雙胞胎＋verify-page＋hash 把關；`pipeline.md` 說明 SVG 幀的 PSNR 容忍。
- **授權聲明對齊事實**：補 `LICENSE-ClaudeAnimationBase`；NOTICE 改為 62 份 reference、說明 verifier 搬家與 taste-gate 再安置；prompt-ladder／springs／critique-loop 把貼近文章原文的句子改成自己的措辭，attribution 改為「依其方法重述」。
- **與 `/ui` 的交接**：draw 的 Not-for 寫明「嵌進使用者站內 → `export_svg.py` 後交 `/ui`」、`/ui` 的品牌筆記是合法品牌來源；`/ui` 的 reference 筆記段落補一句讓圖的工作交給 `/draw` 並重用筆記。

## [7.1.0] - 2026-10-07

### Added
- **`/draw` seek overlay：diagram × 時間軸**。SKILL.md 開頭改用兩個正交軸說明——「這一格上有什麼」（diagram 系統）與「它怎麼隨時間變」（`seek(t)` 方法）——四條 lane 是常見組合。diagram lane 新增 `references/diagram/seek-overlay.md` 與 `assets/diagram/template-seek.html`：完整的靜態圖 + 一層 `aria-hidden` 裝飾（沿真實連接線走的 token、節點高亮、時鐘）+ 一支 `<script data-seek-overlay>` 提供 `window.seek(t)` 與時間軸；reduced-motion／列印／無 JS 看到的是原本的靜態圖。`scripts/diagram/seek_split.py` 剝掉 overlay 產出靜態雙胞胎並跑 `self_check.py`；同一個 `seek(t)` 契約讓 `render.mjs` 能把圖直接輸出成影片。page lane 補一句：圖本身是架構圖／流程圖時用 seek-overlay SVG，不用 canvas 近似。
- 測試：`test_draw_skill.py` 新增 seek 模板拆分＋`verify-geometry` 通過；`test-draw-toolchain.sh` T5 用 `--selector svg` 跑 hash 決定性。

## [7.0.0] - 2026-10-07

### Added
- **`/draw`——把任何東西畫出來的獨立 skill**（以裁換建：退 `/book`、進 `/draw`，技能數維持 14）。四條 lane 共一條骨幹（一則訊息出計畫 → 建 → 自己看圖 → 計分修到 8 分 → 交付到 `.claude/draw/<slug>/`）：
  - **diagram**：vendored `cathrynlavery/diagram-design` v2.6（MIT）全部內容——44 型 reference、語意模式、風格指南、六條連接線規則、無障礙 SVG 契約、可選 reveal/step/loop 動畫、draw.io／Mermaid／Excalidraw 匯入、211 個範例與全部模板、`self_check.py` 與上游 `verify-*.py`／`lint-*.py` 驗證器（`scripts/diagram/repo/`）。
  - **map**：vendored `tt-a1i/archify` v3.0.1（MIT）整包 CLI（`scripts/map/`）——architecture／workflow／sequence／dataflow／lifecycle 五型 JSON IR → 可探索互動 HTML，`finalize` 收據（validate → deliver → strict check → browser check）為交付證據；repo-backed 證據引用；update notifier 明示不跑。
  - **motion**：自寫的 `seek(t)` 工具鏈——`assets/motion/motion.js`（closed-form spring／track／stretch／swapAlpha／loopT／seeded rng／beatGrid）、`scripts/motion/render.mjs`（still／hash／beats／contact／strip／phone／full，子格 tmix 動態模糊）、`beats.py`（numpy 節拍網格：beats／downbeats／hits）、`sfx.mjs`（由 `window.timeline()` cue 合成 UI 音效、依量測峰值對位、混音）、`checks.sh`、`verify-page.mjs`；手繪風子 lane vendored `buildwithhanif/claude-animation-skill`（MIT）lib／scripts／templates／references，附 `ClaudeAnimationBase` 動畫規則（MIT，裁去角色套件）。
  - **page**：多圖解說頁——`assets/motion/explainer-template.html` 為完整範本（六張可拖時間軸的 canvas 圖、雙主題、手機寬度）。
  - references：`critique-loop.md`（計分卡＋三輪規則）、`motion/{pipeline,springs,beat-grid,storyboard,chapters,prompt-ladder,explainer-page}.md`（prompt 階梯 L1–L4、XML 狀態清單、導演 brief 範本、長片分章與子代理模式，皆為改寫並附出處）、`loop-pauses.md`（全片渲染為 Authorization PAUSE）。`NOTICE.md` 列出全部第三方來源、授權與路徑改寫。
- `scripts/verify-skills.py` 殘留掃描新增 `RESIDUE_VENDORED_PREFIXES`：vendored 第三方目錄整體排除並計數（上游文件裡的 dev／bridge 是一般用語）。
- `tests/scripts/test_draw_skill.py`、`tests/skills/test-draw-toolchain.sh`：結構、授權檔、vendored 工具可執行（archify doctor、self_check、驗證器）、motion.js 數學、sfx 合成；Playwright＋ffmpeg 存在時實跑 render hash／contact 與 verify-page。

### Removed
- **`/book` 整個退役**（目錄、`validate-output.ts`／`html2pptx.js`／`install-deps.ts`、17 型 diagram-types、golden templates、十一支 `test_book_*`／`test-book-*`／`test-install-deps-format` 測試、codex 鏡像）。它依賴 `tokens.css` 與已退役的 `/design`，PDF／PPTX 管線與 Stage 0b 訪談不再提供；等價能力走 `/draw`。

### Changed
- 跨 skill 改指：`read`／`learn`／`ui` description 的 Not-For、`ship` 的保留產物清單（`read/learn/draw/design`）、`write` proofread 不再對照 book 視覺語言、`evolve` 的 `card.html` 改經 `/draw` page lane、`_shared/output-journal.md` 渲染基準改指 `draw/assets/motion/explainer-template.html`、`_shared/loop-contract.md` §4 註冊列、`agents/style-reviewer.md` 技術閘門指向、`.gitignore` 新增 `.claude/draw/`。`codex-skill-transfer` reference 裡對 `/book` 四題訪談的歷史描述與 `transfer.py` 的對應改寫規則保留不動（歷史敘述，非現行路由）。
- `CLAUDE.md`／`README.md` 技能表與 `tests/integration/claude-md-skills-baseline.txt` 同步；`plugin.json`／`marketplace.json` 關鍵字 `book` → `draw`。

## [6.2.1] - 2026-10-03

### Fixed
- **`/read` peek 失敗字串統一**：Stage 2 §2 在 peek 模式記錄的失敗字串補上「（未存檔）」，和 Peek finish 實際回報的 `{slug}: markitdown 轉換失敗（未存檔）` 一致，避免日後為了「對齊」而改壞回報常數。
- **`/learn` 路由 eval 改指向 `/read --save`**：「只要離線原文」的 eval 原本寫 routes to /read，6.2.0 之後那樣不會存檔。
- **peek 圖片守門測試放寬**：`test-read-peek-default.sh` 改為抓任何提到 image／`assets/` 的下載指示，不再只認 `download relevant images` 一種措辭。

## [6.2.0] - 2026-10-03

### Changed
- **`/read` 預設改為只讀不存**：沒有 `--save`、也沒有「存下來／存檔／離線保存」這類說法時，`/read` 只把來源抓下來轉成 Markdown 交給 Claude 讀，`.claude/read/` 底下什麼都不寫、也不下載圖片，暫存檔用完即刪；回報改為「📄 已讀取（未存檔）」格式。加 `--save`（或用存檔說法）才走原本的完整離線存檔流程，行為不變。
- **`/read` 的 description 改寫**：照官方 skill 撰寫建議，只寫「做什麼＋什麼時候用」與觸發詞，拿掉旗標清單（`argument-hint` 已列），字數由 441 降到 377。
- **`/learn` 一律以 `/read --save` 擷取來源**：研究流程需要 `.claude/read/material/` 的存檔，URL、`--topic` 與候選擷取步驟都改帶 `--save`。

## [6.1.1] - 2026-09-23

### Fixed
- **`/codex-skill-transfer` 不再默默丟掉 frontmatter 欄位**（skill metadata 0.18.0）：`when_to_use` 改為併入 Codex `description`（`{description} Also use when: {when_to_use}`，在 1024 字截短之前），`health`／`hunt` 的中文觸發詞在 Codex 版保留下來；其他未列入對應表的欄位（如 `disallowed-tools`、`background`）一律列入報告「已捨棄」，不再無聲消失。

## [6.1.0] - 2026-09-23

### Changed
- **`/codex-skill-transfer` 對齊 Codex 現行格式（rust-v0.156.1）**，skill metadata 0.16.0 → 0.17.0：
  - plugin 模式改輸出 portable root `plugin.json`（`$schema` agent-plugins.org），`hooks`、`interface` 移到 `extensions."com.openai"`；不再產生 `.codex-plugin/plugin.json`，也不再寫 `skills` 指標。來源缺 `version`／`description` 時直接省略，不再補 `0.1.0-codex`。
  - plugin 模式的 skill 提及改寫為 `$<plugin>:<skill>`（Codex 以完整名稱比對，舊的 `$review` 在 plugin 內解析不到）；單 skill／batch 模式維持 `$<skill>`。
  - hooks 保留 `SessionEnd`（Codex 0.145.0 起支援），`timeout` 超過 3 秒會改成 3 並列入報告；`mcp_tool` handler 改為保留（`SessionEnd` 下的 `mcp_tool` Codex 不執行，捨棄並報告）。
  - `context: fork` 的跳過訊息只列兩條路徑：Codex 0.154.0 已移除 `codex mcp-server`。
  - agent stub 改用 `# [mcp_servers.<id>]` 表格註解（舊的陣列寫法取消註解後會讓 role 檔解析失敗），model 註解改為「省略則繼承」，拿掉寫死的 `gpt-5.x`；表格註解移到 stub 最後，取消註解時頂層鍵不會被吞進表格。
  - namespaced 提及改寫後若 description 超過 1024 字會再截一次；輸出後仍檢查長度作為最後防線。
  - references 同步：plugin-mapping 全面改寫；marketplace-mapping 依 loader 實際行為修正必填說法、補 `npm` 來源，並結案 `git-subdir` 未解衝突；Codex 文件連結改到 `learn.chatgpt.com/docs/*`。
- `scripts/verify-skills.py` 的三發行面版本檢查改讀 `codex/plugins/baransu/plugin.json`；`codex/` 鏡像已重產。

### Removed
- **退役 `hooks/wiki-sync.sh` 與 SessionEnd hook**：腳本在 `.claude/wiki/` 不存在時直接結束，而 plugin 內已無任何 skill 建立 `.claude/wiki/` 或 `wiki-schema.md`，hook 長期空轉。另查官方文件：SessionEnd 全體 hook 共用 1.5 秒預算，腳本同步執行的 `claude -p` 本就會被砍。`hooks.json` 只剩 Stop／seal-guard；`.gitignore` 移除 `.claude/wiki/`、`.codex/wiki/`，新增 `.claude/research/`。

## [6.0.3] - 2026-09-17

### Fixed
- **`/ship` Step 1 不再漏推已提交的 commit**：提前結束的條件從三項改為四項，新增 `UNLANDED`（HEAD 上還沒落到 origin 的 commit）。現行分支模式比對所有 remote 分支（新分支有 commit 也算）；`/ship <target>` 比對 `origin/<target>`（已推送但還沒併進目標分支也算）。遠端 ref 只是落後時，只會讓它偏向繼續往下跑（Step 4 的 push 此時是 no-op）；上次 fetch 之後遠端分支被刪除或倒退的情況不在 Step 1 的偵測範圍內。早停訊息改為「沒有可歸檔的工作檔案，git 也乾淨，root 無 sealed 合約，也沒有待落地的 commit，結束。」。起因：6.0.2 先 commit 再跑 /ship，工作樹乾淨，照原條文會在 Step 1 結束，commit 留在本地沒推。
- `tests/skills/test-contract-lifecycle.sh` 同步更新 A3a／A3b／A4c 字面，新增 A3b2／A3b3 釘住 `UNLANDED` 偵測與早停判斷。

## [6.0.2] - 2026-09-17

### Changed
- **`/contract` 影響欄補上思考指引與範例**（Step 2 模板後）：說明「資產 → 後果｜類別」這一欄的用途，是讓 `/seal` 開工前就知道哪些 findings 必須擋下封緘。指引寫成四個依序回答的問題：誰的什麼受損 → 擁有者實際會遇到什麼 → 最壞的實際後果屬哪一類 → 這裡出錯該不該擋封緘。附一張報帳匯出範例表（不可逆／資料、上下游契約、UI/UX 各一列），並舉出兩列不該入表的例子。起因：kamishibai F7a 因表面輕重沒有事先定下，封緘遞迴了三輪。
- **`/contract` Step 3 確認時逐列列出影響類別與對應的封緘層級**（必修／可翻轉先驗），讓 G4 規定的「立約時由使用者確認」真正執行。
- 移除 `/contract` 現實接觸強制閘與 `/seal` R10 上的「大膽包 A」標籤。這是 v3.1.0 改版分組時留下的名字，B 包已隨 v4.0.0 `/analyze` 退役；規則內容不變。

## [6.0.1] - 2026-09-11

### Changed
- **`/ship` commit 前先在本地整合上游**（新 Step 2b、INV-10）：fetch 後若落後 origin，依序 stash（含 untracked）→ `pull --no-rebase` → `stash pop` → 在工作樹解衝突（明文處理 diff3 基底段；版本號等機械衝突直接解，需判斷者停下保留衝突與 stash）→ 逐項驗證（無 unmerged、無衝突標記、結構化檔可解析、專案測試入口綠）後才 commit。Mode A push 被拒改為提示重跑 /ship，不在 commit 後 pull。明文禁止把整合、commit、push 串成單一 `&&`／`set -e` 指令鏈。起因：6.0.0 發版時合併後才整合，解衝突腳本中止但後續步驟照跑，帶衝突標記的版本檔被推上 origin（733a6bf，a0bb8d4 補修）。
- `loop-pauses.md` 登記 Step 2b 兩個停下點（拉取衝突、需判斷的衝突，皆 Input 綁定停下回報）；新增 `tests/skills/test-ship-upstream-integration.sh` 釘死以上字面與順序。

## [6.0.0] - 2026-09-08

### Changed
- **`/design` 重做並更名為 `/ui`（「你 repo 裡的 UI 設計主導」），取代 frontend-design**。更名原因：Claude Code 內建的 `/design` 指令（Claude Design 權限管理）會先攔截 `/design`，`-p` 實測兩次皆被接走。擷取筆記路徑仍為 `.claude/design/`。單檔散文：逐字吸收 Anthropic frontend-design 五節（Apache 2.0，授權與修改聲明放 `LICENSE.txt`／`NOTICE.txt`，本文不提出處），新增「從參考物學設計語言」（五個觀察面、三層工具階梯、紅線「只抽性質，不抽素材、文案、logo」、筆記落 `.claude/design/reference-<slug>.md`）與「修整既有 UI」（先列差異再原地改，不補原頁沒有的事實）兩節；`loop=not-drivable`。skill 內零腳本、零固定格式。行為證據走 skill-creator evals（`evals/evals.json` 三案例），觸發準確度以 `claude -p --plugin-dir plugins/baransu` 實測（`run_eval.py` 受已安裝的同名舊 skill 干擾，結果不採）。
- 併入上游 5.5.1／5.6.2 的 `/write` 規則：`## Direct language and response shape`（直接用語、清單使用時機、澄清意圖時簡短回覆即停）。
- **自用提醒**：安裝 6.0.0 後停用 frontend-design plugin（`frontend-design@claude-plugins-official`），否則兩個 skill 搶同一觸發。

### Removed
- design 的 preset 系統（紙／swiss／google）、design-cores、slide-cores、DESIGN.html、lint `check.py`、export-brief、Stage 0 CLAUDE.md 注入；根目錄 `DESIGN.md`／`DESIGN.html`／`tokens.css`／`design-cores/`／`slide-cores/`；CLAUDE.md 頂端注入區塊、Design Artifacts 段、`DESIGN.md ≠ design.md` 不變量。
- `write` proofread 不再讀 `tokens.css`；`ship` 的 `ARCHIVE_DIRS` 移除 `design`，`design` 改列 keep-list。
- 9 個以已刪工件為受試對象的測試檔退場；新增 `tests/scripts/test_ui_skill_structure.py`（位元組層級：逐節逐字、LICENSE sha256、NOTICE 逐字、目錄清單）。
- 片二範圍只改路由與路徑：`skills/book/` 兩處路徑（兩份 reference 搬到 `_shared/`）、`skills/hunt/` 三處改指 `/ui`；`agents/style-reviewer.md` 未動，其餘 book／style-reviewer 內容留片二處理。

## [5.6.1] - 2026-09-08

### Reverted
- **`/contract` 與 `/seal` 回歸 5.4.1 形**。5.5.0 把兩者換成 Common Lab 定稿本體時，contract 模板刪掉「錯不起表面（Surface Inventory）」節，但 `_shared/contract-gate.md` 的 G4 一位元未動、且仍宣告自己是 seal 分級真源——G4 因此成了無錨條款（全倉零引用、seal 不讀、無測試釘）。使用者裁定整體回歸：`contract/SKILL.md`、`seal/SKILL.md`、兩者的 `loop-pauses.md`、`agents/seal-agent.md`、`tests/skills/test-contract-lifecycle.sh`、`test-inertia-distillation-contracts.sh` 全數自 `288f13d^` 還原；`contract/references/acceptance.md` 退場。`seal/references/verification-effort.md` 保留（5.5.0 的 `/review` 仍引用）。think／review 的 5.5.0 本體不動。
- CLAUDE.md／README／`tests/integration/claude-md-skills-baseline.txt` 的 contract／seal 兩列與三頻段 Medium／Large 列回原文；agents 名冊同時列 seal-agent（seal 派遣）與 verifier（review 派遣）。codex 鏡像隨 `make mirror` 重產（agent TOML 11→12）。

## [5.6.0] - 2026-09-07

### Removed
- **kamishibai 退場**。kamishibai SDK／plugin 由使用者宣告放棄，5.3.0（book／design 薄提示 stub）與 5.4.x（write proofread 改道 `kamishibai render`）兩輪遷移整批退回。全 repo 現在式提及 kamishibai 歸零，僅存本 CHANGELOG 的歷史條目。
- 退場測試兩支：`tests/scripts/test_stub_redirect_kamishibai.py`（三枚 stub 轉介斷言）、`tests/skills/test-write-proofread-kamishibai.sh`（proofread 改道釘死）——所釘的行為已不存在。

### Changed
- **`/book`、`/design` 回復 5.2.0 手寫 HTML 形**。兩份 `SKILL.md` 由 39／40 行 stub 復原為 506／491 行全本（Acquire → Synthesize → Render 三階段；gen／lint／preset／export-brief 四模式），`validate-output.ts`、`check.py`、`editorial-sanity.sh`、`紙-sanity.sh` 調用行全部回役。`scripts/` 與 `references/`（golden-template 三兄弟、126 骨架、三套 preset）自始未動，本輪由「凍結資產」回復為在役機件。
- **`/write` proofread 回復自產 HTML 流程**。`SKILL.md` 與 `references/proofread.md` §4 回到「比照 book 視覺語言、但不走 /book 產線」的手寫路徑（tokens.css 讀取 → 六欄表 → `.claude/write/錯字修改.html`）；frontmatter description 回 `book-styled`。**防撞守衛仍前置**——488e7bc 形的步驟 4 把守衛與寫檔寫在同一步（先確認目標不存在，已存在改時間戳名，然後才寫），5.4.1 F-1 的教訓在此形下本就成立。`markitdown` 出處註腳回 `(same tool /book Stage 1 uses)`。
- **bleed 面改指還原**：`agents/style-reviewer.md`（技術閘門回 GATE-F／GATE-G／`check.py`）、`skills/_shared/output-journal.md`（渲染基準回 `book/references/golden-template.html`）、`skills/codex-skill-transfer/SKILL.md`（單檔慣例例證回 `validate-output.ts`）、`skills/evolve/SKILL.md` 與 `references/output-contract.md`（`/kamishibai:book` 回 `/book`）、`CLAUDE.md`（Layout 註記、Design Artifacts 段、技能表 `/book`／`/design` 兩列回原形，stub 不變量整條移除；`plugin.json` 註記改為不寫版號，避免每次發版都要改一次註解）。`skills/review/SKILL.md` 的 F8b 指向行已於 5.5.0 隨 HTML 工作日誌一併刪除，本輪無可還原之處，故不動。

### Tests
- **58 筆 `@unittest.skip` 全數解除**。5.3.0 因 book／design SKILL.md 本文移出本倉而轉為 skip 的斷言（分佈於 12 個 `tests/scripts/test_{book,design}_*.py` 與 `test_integration_dataviz_chart_e2e.py`）隨 prose 回歸重新武裝；`tests/skills/test-book-skill-stage0.sh` 的「Stage 0 標題不存在即 SKIP」gate 一併移除回原形。
- `tests/integration/claude-md-skills-baseline.txt` 的 `/book`／`/design` 兩列隨 CLAUDE.md 技能表回原形。
- **保留**（與 kamishibai 無關的改良）：`tests/scripts/test_ship_check_gate.py` 與 Makefile 的 `ship-check` 目標（9d62eb7 F2，鏡射漂移閘門唯一入口），以及 5.5.0 的 Common Lab 全部測試面。

## [5.5.0] - 2026-09-07

### Changed
- **think／contract／seal／review 四技能改以 Common Lab 實驗版定稿為本體**（common-lab 0.6.0），輸出目錄回歸 baransu 慣例：think → `.claude/think/<slug>.md`、contract → 專案根目錄 `CONTRACT.md`（sealed 標記文法不變）、seal → 收據 `.claude/seal/<slug>-<run>.md` ＋ seal-log ＋ 合約 line 2 標記、review → 對話報告，需要時 `.claude/review/<slug>.md`。
- **think**：對焦改為「復述」（結果／目的／不能動的／規模），只問會改變答案形狀的題；表態附「押在什麼上、押錯會怎樣、改走哪條」；前提逐條 verified／未實查；正向攻擊找會壞的地方、反向攻擊砍掉復述不需要的東西；先呈現再落檔；落檔即結束，不挑下游 skill、不開核准關卡。已定決定可拿來拷問（取代 Lab grilling 反證版）。單檔小修改指 `_shared/tdd.md` §7；多目的地指向 common wayfinder。
- **contract**：四段改五段（目標與範圍／前提／條文／需求常數／決策與修正），釘 WHAT 不釘 HOW；必要性與違反成本分開，需求常數用精確比對驗；不確定前提隔離其依賴條文但相鄰條文照釘；不再要求儀式性確認。`references/acceptance.md` 為單一格式來源。
- **seal**：撤除固定五點 mandate、五欄 payload、複驗上限 2、fingerprint 監管鏈與每修必配 pinning test；改為「驗證強度跟著後果」——先定檢查與修復額度（`references/verification-effort.md`），派 `agents/verifier.md` 只驗不修；突變是方法不是配額，需求常數以精確比對結案；有實作授權才修、修後只複驗該處；到額度即交回。seal-log JSONL 與 Stop hook 契約不變。
- **review**：撤除七階段五視角流程、八欄簽收與 HTML 工作日誌；改為派一個乾淨 context 的 verifier，視角 agent 只為不同的實質風險才加；計數依 `_shared/fact-check.md`；乾淨的 review 是有效結果。
- `/ship` 歸檔清單加入 `seal`；`_shared/tdd.md` §8 與 `_shared/output-journal.md` 對應更新（不再預設產 HTML 日誌）。

### Removed
- `agents/seal-agent.md`（五點 mandate 隨 seal 退役）與 `review/references/orchestration-interface.md`；新增 `agents/verifier.md`。

### Tests
- `tests/skills/test-inertia-distillation-contracts.sh` 改釘新版 think／review 契約；`tests/skills/test-contract-lifecycle.sh` A2／A4／A5／A6 改釘新版 seal 條款與 `agents/verifier.md`；`tests/skills/test-plain-language-presentation.sh` 改釘新版 think 鏈與 review 報告形狀；`tests/skills/test-automation-annotation.sh` review 改為 ultracode=neutral；`tests/skills/test-orchestration-interface.sh` 迴圈移除 review；`tests/scripts/test_codex_skill_transfer.py` 對應更新；`tests/skills/test-think-rework.sh`（釘 v5.0.0 判決機字面）退役；`tests/integration/claude-md-skills-baseline.txt` 重生。

## [5.4.1] - 2026-08-30

### Fixed
- **防撞守衛前置為執行前條件**（F8d 封緘 F-1，不可逆類）。`references/proofread.md` §4 的「目標已存在→改用 `錯字修改-<YYYYMMDD-HHMMSS>.html`」原本寫在步驟 5，位置在渲染指令**之後**——而 `render` 一旦寫下去，舊報告就已經沒了，寫在後面的守衛救不回任何東西。改為步驟 3 的執行前條件：先確認 `-o` 目標不存在，已存在則把 `-o` 換成時間戳名，然後才跑指令。步驟 5 相應收斂為「目標即步驟 3 的 `-o`，防撞屬步驟 3」。Verbatim 渲染指令形一字未動。
- **完工回報範本不再硬寫路徑**（F-1 連帶）。§5 的 `✅ 校對完成：.claude/write/錯字修改.html` 改為 `✅ 校對完成：{實際寫入路徑}`——撞名改寫時間戳名之後，範本若仍硬寫預設路徑，回報的就是一個不存在的檔案。
- **位置關係斷言**（F-2）。`tests/skills/test-write-proofread-kamishibai.sh` 新增 E4：防撞語句的**行號**必須早於或等於帶 `-o .claude/write/錯字修改.html` 的首行。既有 E2／E3 只問「字面在不在」，對「在，但在指令後面」完全無感——F-1 那個缺陷正是這樣穿過去的。
- **停手句正向釘**（F-3）。新增 D2b 釘住「CLI 不可用即說明並停手、不得退回手寫 HTML」字面。既有 D3 只是 `tokens.css` 反向釘，規格書若把停手句整句刪掉、什麼都不說，D3 照樣綠——而「什麼都不說」正是模型自行即興退路的溫床。
- **SKILL.md 括號殘句收殮**（F-4）。`(analysis output + no SVG would fail book's red line and quality gate)` 改為指向單一真源：`(analysis output — the red line and the reasoning are preserved verbatim in references/proofread.md §4, the single source)`。baransu 的 `/book` 自 5.3.0 起是 stub，其紅線與品質閘實體已不在本 repo，原句是對已遷出物件的現在式斷言。`never routes through the /book pipeline` 字面照舊。
- **description 一詞隨產線改道**（F-5）。frontmatter `book-styled 錯字修改.html` → `kamishibai-rendered 錯字修改.html`。觸發詞一個未增未減。

## [5.4.0] - 2026-08-30

### Changed
- **`/write` Proofread 產線改道 `kamishibai render`**（F8d）。`錯字修改.html` 不再由模型手寫 HTML，改為「產六欄 Markdown 語料 → `kamishibai render <語料.md> -t kami/long-form -o .claude/write/錯字修改.html` → `kamishibai lint` 驗收」。`references/proofread.md` §4 全段重寫，`write/SKILL.md` 的 Done-when／Output／Constraints／Stage 4 四處同步。CLI 不可用時明令停手回報，不得退回手寫 HTML——那正是本次改道要收掉的分叉。
- **六欄表頭隨遷為無「／」形**：`段落／上下文` → `段落上下文`（proofread.md :10／:36／§4 全數改寫）。真源是 kamishibai S4 的凍結錨 `FINDINGS_HEAD`（`頁數/段落上下文/原文內容/錯誤類型/建議修正/修改原因`）；兩處各自逐字釘死，下游比對與統計以欄名為鍵，差一個字即斷契約。
- **badge 三 class 入規格書為逐字常數**：`badge badge-typo`（錯別字）／`badge badge-diction`（用語不妥）／`badge badge-flow`（語句不通順），與 `<mark>` 同為儲存格行內 HTML（table cell raw passthrough）。列常數表的理由是失效模式**靜默**——class 拼錯只是退回無樣式純文字，檔案照開、表格照讀、無人報錯。樣式由 kamishibai `templates/kami/long-form/styles.css` 的三條規則（zebra／`.table mark`／badge 三色相）承接。
- **`tokens.css` preset 段退場**：原 §4 第 1 步「讀 `{project_root}/tokens.css` 首行取 preset slug、缺檔則自訂 fallback 調色盤」整段移除——皮改由 `kami/long-form` 供給，規格書不再保留手寫 HTML 的退路（保留即等於留著舊分叉）。
- **紅線一條未破**：`a proofreading table is analysis output (which /book's "no LLM commentary" red line forbids)` 一句原樣保留，另補一句澄清「`kamishibai render` 不是 /book 管線」——單檔渲染器，無 Acquire／Synthesize 階段、無 SVG 品質閘、無 LLM 評註規則可破，防後人把紅線讀成禁止本次改道。`write/SKILL.md` 的 `never routes through the /book pipeline` 字面保持為真；`No validate-output.ts` 與寫入目標／時間戳防撞語意（`.claude/write/錯字修改.html`、撞名改 `錯字修改-<YYYYMMDD-HHMMSS>.html`、不得靜默覆蓋）逐字保留。
- **新增釘死測試** `tests/skills/test-write-proofread-kamishibai.sh`：表頭逐字、三 badge 常數逐字且與標籤同列、紅線句在檔、渲染指令形、`tokens.css` 反向釘（不得復活手寫路徑）、寫入目標與時間戳防撞語意，共 18 條。
- codex 鏡像隨 `make mirror` 重產。

## [5.3.0] - 2026-08-30

### Changed
- **`/book` 與 `/design` 改為薄提示 stub**——兩份 SKILL.md 本文全部換成轉介指引（book 39 行、design 40 行，各 ≤60 行）。frontmatter 一欄不動：`name` / `argument-hint` / `user-invocable` 原樣，`description` 逐字保留（Trigger On 詞彙不減），所以觸發面完全不變、`EXPECTED_SKILL_COUNT = 14` 不動。本文只剩三件事：退場預告、改裝指引（`/plugin install kamishibai@kamishibai` → `/kamishibai:book` / `/kamishibai:design`，或 `npm i -g @kamishibai/sdk` 走 CLI）、蟄伏機件說明。Stage 操作指示、四模式操作指示、以及 `validate-output.ts` / `check.py` / `editorial-sanity.sh` / `紙-sanity.sh` 的所有調用行全部移除。book 指向句與 design 指向句逐字入文。
- **蟄伏鐵律**：`book/scripts`、`book/references`、`design/scripts`、`design/references` 本版**零位元組變更**（`git diff --stat` 該四徑為空）。蟄伏機件（scripts/references）本版一位元未動，6.0.0 隨目錄實體退役——git 歷史即唯一備份（/analyze 前例）。
- **跨 skill bleed 面改指 kamishibai**：`agents/style-reviewer.md`（技術閘門面改指 `kamishibai lint`，GATE-F/GATE-G/check.py 標為凍結歷史；render 正確性改指 SDK `render`/`lint` lane）、`skills/_shared/output-journal.md`（渲染基準由 book golden-template 改為 kamishibai book skill，並附「kamishibai 未裝時自渲染」退路）、`skills/review/SKILL.md`（work journal 樣式改指共用渲染基準）、`skills/codex-skill-transfer/SKILL.md`（單檔慣例例證由 `design/scripts/check.py` 換成仍在役的 `hunt/scripts/hunt-search.py`）、`skills/write/references/proofread.md`（僅 markitdown 出處註腳改指，**自產 HTML 流程與 no-LLM-commentary 紅線一字未動**）、`CLAUDE.md`（Layout 註記、Design Artifacts 段、技能表 `/book` 與 `/design` 兩列、新增「book/design 為 stub、機件蟄伏非在役」不變量）。
- **`/evolve` card.html 產線改指**：`evolve/SKILL.md` Stage 7 與 `evolve/references/output-contract.md` 的 `/book` 入口改為 `/kamishibai:book`；「never hand-assemble HTML」規則不變，只換入口名，產線不斷鏈。
- **版號 5.2.0 → 5.3.0**（`plugin.json` ＋ `marketplace.json` 兩處同步；codex 鏡像隨 `make mirror` 重產）。
- **封緘修繕（三筆）**：(1) `evolve/references/output-contract.md:24` 操作序漏網的裸 `/book` 改指 `/kamishibai:book`——判官取樣由「含 card.html 的行」放寬為全檔禁裸 `/book`（歷史敘述句走逐字允許清單，非啟發式）。(2) 新增 **`make ship-check`**（`test` ＋ `mirror-check` 串跑）＝鏡射漂移閘門的唯一入口；`Makefile` 原註解「週 cron 守之」查無實體，改為事實句（本 repo 無 CI 無 cron，閘門是人工的）；`mirror-check` **仍不併入 `make test`**（開發中途未 regen 即紅），此政策由 `tests/scripts/test_ship_check_gate.py` 反向釘死。(3) 兩 stub 與 `CLAUDE.md` 的「凍結資產不再是任何現行流程的一部分」絕對句改限定句——`verify-skills.py` Gate 10 仍解析 `book/references/loop-pauses.md` 與 `design/references/loop-pauses.md`，該指標之實體收殮（重寫兩檔或 Gate 10 修憲）劃入 6.0.0 射程。

### Deprecated
- `/book`、`/design` 兩 skill 的實體目錄（含 `scripts/` 與 `references/`）預告於 **6.0.0 移除**。本版起它們是凍結資產：不得被任何 skill、agent 或共用參考援引為現行步驟。等價能力一律走 kamishibai plugin 與 `@kamishibai/sdk`。

## [5.2.0] - 2026-08-29

### Added
- **`/health` 環境醫生（Environment doctor／環境急診）**——生態系遇環境問題（skill 的 CLI/SDK 缺失、command not found、依賴壞損）的**預設調度目標**：其他 skill 撞到環境問題交給 /health，不就地即興。四步：先診斷再修（含 nvm 陷阱——node/npm 只在互動式 login shell 載入，非互動 shell 找不到不等於未安裝，先 `zsh -lic` 重試）；預設修法＝該工具官方一步「全域」安裝（如 `npm install -g <pkg>`，呼叫方指名版本即 pin）——此為「不得未確認修改」不變量的唯一豁免通道：調度本身指名工具即授權、一次一工具；硬限制（禁 sudo／替代品／source build／即興改道，一步裝失敗即大聲報錯附一行人工修法）；固定收據 `ENV_DOCTOR ｜ tool ｜ before ｜ action ｜ after ｜ shell` 成敗必發。description/when_to_use 補環境問題觸發詞（command not found、環境問題、依賴缺失、SDK 沒裝）。起因：kamishibai SDK 上 npm 前夕「新環境首用自動安裝」意圖零載體，統帥裁定 bootstrap 不散進各 skill、集中於健檢器官。Gotchas 補 nvm 列。codex 變體同步。

## [5.1.0] - 2026-08-29

### Changed
- **`/seal` 探針入場費（五點任務書第 5 點，SKILL.md 與 seal-agent 兩側逐字共用）**。每枚探針注入前必須先書面列出它重演的「真實操作鏈」——未來哪個真實行為者、在什麼正常操作下、逐步走到哪一步會穿過既有流程紀律（diff 對照／自驗／交卷一手數據）而不被攔；推演走不通的鏈是紙上談兵，該探針不得入單，任意字元竄改若無對應真實操作者一律不合格，「有可能會發生」不是入場費。選點按「被揭露的防線破口」後果嚴重度排序：一枚能揭露某族判官（如 `includes` 裸值形狀）整族空洞的探針，嚴重度以該族守護的最重表面計，不以被竄改物本身表面後果計，更不以上一輪 finding 的鄰域計（街燈禁令）。新增**零探針出口條款**（比照「無可執行測試套件」降級路徑）：本片若無任何合格探針標的，point 5 記為 `未執行`，且此事本身即 top-level finding——不得靜默判「符合」。原條文「A probe that no test catches is a finding, never a shrug」保留：入場費管誰能入單，該句管入單後的結果判讀。
- **`seal-agent` 結構化回傳新增必填 `operation_chain`**。probe_record 每筆都要載入場費（誰／什麼正常操作／哪一步穿過紀律），缺欄即 malformed，使 dispatcher 能稽核付費事實；零探針時回傳 `probe_record: []` ＋ top-level `probe_admission: none-admissible`（逐一列出考慮過的候選與落榜理由），空 probe_record 而無此行同樣視為 malformed。
- **複驗限縮為三件機械重放**（Fix loop）。複驗 dispatch 不是第二輪五點開掘，其任務書恰為：(a) 已修 findings 逐筆回歸；(b) 初驗中「已咬中」的探針全部重打——它們沒產生 finding、不在修單字面內，而修繕輪正是最可能把它們弄空的一步（實錄：修繕輪的 stub 隔離穿過交卷審查，靠複驗重打探針才咬出）；(c) 修繕輪新立判官的空洞性抽查——執行者的「紅恰一」自證只認證實際亮紅的那條鑑別分支，不認證判官自我宣稱的整個保護面，每個新生判官由複驗官親發一張紅（出生證明）。複驗中的新發現一律 report-only 入帳，**唯一例外**：不可逆／資料毀損類直接開修，且該修不計入複驗上限。複驗上限 2 與指紋比對規則不變。
- **findings 單軸分級**（Fix loop）。分級唯一軸＝後果嚴重度，不看是哪一點掃出、不看修起來多便宜、不看被竄改物多顯眼。必修類＝不可逆後果（資料毀損／滅失）與已出貨契約破裂（已發布的行為契約、授權法遵破口）。「表層資產」（樣式、文案、色票、字距）低嚴重度只是**預設先驗、不是判決**——一手證據（探針實打結果、判官形狀揭露的整族空洞）可翻轉先驗升級嚴重度；低位 findings 預設入帳不修，報告中留使用者裁量；表層資產判官一生恰領一輪探針（出生證明），後續輪次不再重打。
- **表層判官一輪計法補優先序**：輪以封緘 engagement 計、不以 dispatch 計——同一次封緘內，複驗重放 (b) 對咬過的探針不分資產類別一律重打（咬過＝證據、非先驗）；上限禁止的是之後的封緘再對該判官開新探針。
- **`/contract` G4 影響文法（`_shared/contract-gate.md` ＋ Step 2 模板）**。錯不起表面表新增「影響（資產 → 後果｜類別）」欄與入表費：影響格必須以受影響資產起句、接資產持有者會親身遭遇的一句後果、再標類別（不可逆／資料、邏輯核心、上下游契約、穩定性可靠性、UI/UX）——寫不出資產不入表（no asset, no pinned surface）、無人可感知的 epsilon 不成句、誠實歸類落在風格／命名／MOP 類者屬 lint 管區。類別欄是 `/seal` findings 分級的嚴重度真源：分級在立約時由使用者確認裁定，封緘時不再重議；seal 的分級先驗僅適用於合約未分類的表面。
- 以上各條同步鏡射至 codex 變體（`codex/plugins/baransu/skills/seal/SKILL.md`、`codex/plugins/baransu/.codex-agents/seal-agent.toml`、`codex/plugins/baransu/skills/contract/SKILL.md`、`codex/plugins/baransu/skills/_shared/contract-gate.md`）；「Probe admission」共用段落在四份檔案間逐字相同。

## [5.0.0] - 2026-08-25

### Changed
- **`/think` 從零重建為判決型 skill**。三條路徑（存廢判決 Kill/Keep/Pivot、選型判決 A-or-B 官方優先、對焦交棒 三輪對焦→交棒單路由）取代舊五段計畫＋Lightweight＋Evaluation 三模式。不再產出計畫——判決或交棒單產出後交由 `/contract`、wayfinder、或 `_shared/tdd.md` §7 接手。Verbatim Constants：verdict 行、推翻條件行、交棒單四欄位、Automation 行四組照抄模板。SKILL.md 從 478 行縮至 ≤250 行。
- **發行面全面同步**：CLAUDE.md 技能表 row、baseline.txt、plugin.json / marketplace.json 版號 4.0.0→5.0.0、AGENTS.md skill count 修正（fifteen→fourteen）、evals 五案改為新路由、loop-pauses.md 重寫為三列新互動點。
- **測試改寫**：`test-inertia-distillation-contracts.sh` think sections 改 pin 新 verdict/handoff schemas；新增 `test-think-rework.sh` pin Verbatim Constants byte-exactly。

## [4.0.0] - 2026-08-14

### Removed
- **`/analyze` 全面退役**。遙測與實際使用皆為零——大頻段全管線（goal→requirement→design→test→task 五層 spec ＋ 內建執行段）從未被真正走完過一輪，維護成本卻攤在每一次改版上。skill 目錄 `plugins/baransu/skills/analyze/` 整個移除，不歸檔——git 歷史就是唯一備份。
- **7 個管線 agent 一併移除**：`impl-agent`、`review-agent`、`merge-agent`、`e2e-fix-agent`、`final-review-agent`、`final-fixer-agent`、`smart-friend-agent`。這些 agent 只有執行段會派遣，沒有第二個消費點。`seal-agent`、5 個 review 視角 agent、3 個 health inspector、2 個 evolve agent 全數保留（18 → 11）。
- **只為 `/analyze` 存在的 CLAUDE.md 不變式一併刪除**：review-agent 不得呼叫 `/baransu:review` 的禁令、執行段 worktree 落點慣例、`goal.md 驗收標準 C{n}` 頂層驗收權威、coverage-riding 的閘時決策、`failure_count` 與 `compile_error_count` 分流。錨點沒了，條文就不留——無錨條款不入冊的反向適用。

### Changed
- **大頻段改為複合鏈，不再是單一 skill**：先把整件事畫成決策圖、切成 contract 頻段的片，每片各自走 `/contract` 釘條文 → 實作 → `/seal` 封緘。收工證據從 `final-report.md` 改為逐片的 seal 五點任務書結果。裝了 common 套件（wayfinder／delegate／strategic-advance）時，畫圖與執行可以走那條路——**先偵測，不要假設有裝**；套件名一律只出現在 body 散文，不進任何 frontmatter `description` 或觸發詞，避免在發布中繼資料裡帶出未宣告的跨 plugin 相依。
- **技能上限 15 → 14**（`scripts/verify-skills.py` 的 skill-count 檢查為機制錨點）。codex-skill-transfer 的可證偽退役條款同步下修：三個月零使用即退役、上限收回 **13**（原為 14）。「2026-07-19, 14→15」的修憲註記保留為歷史。
- **`/seal` 的大頻段邊界翻轉**：原本「大頻段 spec 驗證交給 `/analyze` 內建 final review、seal 不審多模組 spec」，改為 seal 逐片驗收——一次只對一片合約收工，多模組任務必須先切片、每片各自封緘，永遠不對整件事跑單次 seal。
- **`/contract` 的超長 off-ramp 沒有上一層可退**：合約超過 60 行不再是「該升去 `/analyze`」的訊號，而是「這片還沒切夠小」。Step 2 的非互動回報字串同步改為 `no progress: task exceeds contract band, slice it into contract-band slices`。
- **`/think` Stage G Option 2 的下游路由重寫**：medium-to-large 不再喚起 `/baransu:analyze`，改為切片後逐片 `/contract` → 依 `_shared/tdd.md` 實作 → `/seal`。KD-bound relaxation 的理由從「`/analyze` 會把它退回 `/think`」改為「單層改動切片後就只有一片」；工作日誌的追記歸屬人改為「實作方」——主 session 或受託執行者。
- **`_shared/tdd.md` 去除管線綁定**：Scope、tracer-bullet 對照表、§7 直接實作閘門不再指名 impl-agent／review-agent／執行段；`failure_count` 計數規則的外部指標（指向已刪除的 `execution-pipeline.md`）直接移除。
- **`/ship` 歸檔白名單移除 `analyze`**（Step 1 `ARCHIVE_DIRS` 與 Step 2 allowlist 維持逐字一致）；`.gitignore` 移除 `.claude/analyze/`、新增 `.strategic-advance/`。
- **`/codex-skill-transfer` 移除 analyze 專屬移植資料**：`transfer.py` 的 AskUserQuestion 能力表、Codex port adapter 與 adapter 能力表三處 analyze 條目刪除；`CODEX_PORT_PLAN.md` 與 `skill-mapping.md` 的機制落點清單與 adapter 註記改為泛化敘述。
- **路由 eval 語料刪除 analyze 案例**（cross-skill-routing 2 例、contract 1 例、design 1 例、think 1 例），不新增替代案例；各檔 id 重新連號。

## [3.4.1] - 2026-08-13

### Added
- **`/codex-skill-transfer`：`/other-skill` → `$other-skill` 呼叫提及改寫（skill-mapping §6.2）**。Codex 以 `$` 前綴提及 skill（官方文件：「run `/skills` or type `$` to mention a skill」），移植後殘留的斜線提及指向 Codex 不存在的指令。`/baransu:name` 命名空間形式無歧義、一律改寫；裸 `/name` 只在名稱屬於已知同層 skill 集合（來源 skill＋帶 SKILL.md 的 sibling 目錄）時改寫，路徑段（`.claude/read/`）、URL、更長識別字（`/design-cores`、`/reads`）一律不動。套用面：SKILL.md body、frontmatter `description` 觸發片語、references、`_shared` 共用目錄、plugin `rules/`、bundled agent TOML instructions；§6.1 豁免名單照舊，`scripts/` 內文不改寫。think Stage G adapter 模板內建的 `/review` 同步改為 `$review`。

## [3.4.0] - 2026-08-11

### Added
- **`/book --storyboard`：渲染前的逐頁確認層（Stage 2C）**。結構合成之後、Render 之前——唯一能同時拿到「真實輸出單元」又不污染設計系統的位置——把整份分鏡一次攤開：重述的場景目標，加上每個實際輸出單元（長文 section／簡報 slide）的標題、內容大綱與一個空的「感覺」欄位。使用者一輪改完並確認，確認結果即為生成依據，`$RAW_CONTENT` 只能補證據、不得遺漏或改寫。不帶旗標時渲染行為逐字不變。
- **兩個載體，各自指名消費點**。長文側寫進 `$STRUCTURE` 的 `feel`，消費點是既有的 Stage 3 §3 soft generation（本來就讀整包 `$STRUCTURE`）；簡報側寫進 `$STRUCTURE_SLIDES.slides[*].feel`，而該路徑**原本沒有任何消費點**（`render-pipelines.md` §6b Step 1 是「讀骨架填空」、逐一指名讀哪些欄位），因此該步驟同步補上消費指令。缺這句，簡報側收上來的感覺 100% 空轉——這是 `/review` 雙視角獨立撞到的同一個缺口。
- **「感覺」是有限改變，不是新的自由度**。設計意圖：每頁可以不一樣，但每頁都仍明顯屬於同一套設計系統。因此它只在既有規則早已允許的範圍內**挑值**——間距／行高／欄寬取量化級距的某一端；元件只在 `SKILL.md` §3「依資料形狀選，不依感覺」已判為合法的候選之間挑（判準不變）；`layout_type` 永不變動（Stage 2B 決策表所有，GATE-G 檢查）。唯一開放構成的是視覺重心與 §9 表現範圍內的版面。優先序鏡射既有 `$INTERVIEW_BRIEF` 的規矩：與 perception-guide 衝突時它贏、與 Stage 0b brief 衝突時感覺贏、§9 缺欄位時仍走保守回退。
- **三種溢出的統一處置與終止條件**。確認輪後若節數超出 4–8、張數超出 6–12、或字數超出 1800 詞（該上限在 Stage 2A 施加、早於確認輪），一律重整並二次回顯，且明示哪一節將轉入延伸閱讀——不靜默截斷、不代寫。第二次即最後一次，仍溢出則硬截斷並逐條列出被截單元。另：`tokens.css` 檢查升為回顯**之前**的前置條件，避免使用者做完整輪編輯才撞上 Stage 3 §1 的硬中止而全數丟失（結果不落盤）。
- **Stage 2C 已註冊進 `book/references/loop-pauses.md`**（Input class，非互動預設＝整段跳過、結構照自動合成結果）。skip 條件為 `--auto`／`--no-interview`／非互動三條，**不沿用** Stage 0b 的 slug 與短 text 兩條——2C 在 acquire 之後，slug 轉書是本功能的主要路徑。
- **旗標提示義務**：`argument-hint` 補上 `[--storyboard]`，且互動執行未帶旗標時，於結構產生後印一行不擋流程的 stderr 提示。提示點刻意不放 Stage 0b——那裡的四個跳過條件會吃掉 slug 轉書這條最常走的路徑。

### Changed
- **已知邊界，明說不粉飾**：「確認後即權威」沒有機制保證。`validate-output.ts` 的輸入是單一 HTML 檔路徑，而確認結果依設計不落盤——沒有工件，任何 gate 在原理上都比不到。SKILL.md 裡那條「不得遺漏或改寫」是可被跳過的散文規則，唯一的檢出手段是人工逐頁對照。本版不新增自動化測試，互動層維持零覆蓋。

## [3.3.2] - 2026-08-10

### Changed
- **`/hunt` 不再沉默或只丟技術結論**：調查中的 Locate、每次假說確認／排除、修復或 Handoff 前都要用繁中回報「查了什麼、證據改變了什麼、下一個具體檢查」；結案與受阻時先以白話串起「當時在做什麼 → 觸發條件 → 根因／缺失證據 → 傳導路徑 → 使用者看到的症狀 → 影響 → 下一步」，既有 Success／Handoff 欄位不變。
- **`/hunt` 的確認門檻與遠端診斷更嚴謹**：根因必須解釋全部已觀察症狀，否則只能維持假說，或以獨立證據拆成另一事件；一次只開一個 yes/no probe，2–3 個 log site 也必須共同回答同一題。本機無法重現時，改交付符合已知 runtime、且有 target／時間／工作量／輸出上限的五行唯讀診斷區塊，只保留該 probe 預先允許且已遮蔽的欄位。
- **`/think` 與 `/review` 共用同一個白話呈現契約**：補齊脈絡、證據或已知限制所支持的理由、實際影響、具體下一步；English technical term 首次出現時保留原文並就地解釋。呈現層不得補造事實、不得新增 PAUSE，也不得改動 Evaluation verdict-first、Full 五節或 review 八欄 receipt 等既有 schema。
- **`/think` 與 `/review` 加入抗慣性判斷**：Lightweight 先從行為完整的候選中選最小可靠修法；Full Approach 明列最脆弱承重前提、失敗後果與承受方式。HIGH／CRITICAL finding 必須先用不同證據來源嘗試反證；最後明說哪些值得、哪些不值得，理由須回扣 review goal。
- **`/evolve` 與 `/health` 共用蒸餾候選矩陣**：外部 repo、release log、事故、對話或 private memory 的候選先判斷是否重複、是否為長期 invariant、正確 owner layer、可讓缺失行為轉紅的 verifier，以及是否混入專案／私人資訊；只讓值得且放對層的規則進入長期資產。
- **行為契約測試**：新增白話呈現、hunt 診斷、think／review 抗慣性及蒸餾矩陣測試，釘住既有 5／6／5、4／5／8 schema，並以 mutation fixture 證明「只留說明文字、刪掉實際行為」會轉紅；Codex transfer E2E 同步確認新契約有進入生成結果。

## [3.3.1] - 2026-08-07

### Fixed
- **Windows Codex 每次 Stop 都因 seal-guard hook 報錯（hook exited with code 1）**。根因：Codex 在 Windows 把 `C:\` 形式的 `PLUGIN_ROOT` 文字代入 `bash "${PLUGIN_ROOT}/hooks/seal-guard.sh"`，而 `bash` 常解析到 WSL bash——WSL 讀不懂 Windows 路徑，腳本永遠找不到；即使找到，WSL 也不繼承 Windows 環境變數（僅 WSLENV 白名單），腳本內 `${PLUGIN_ROOT:-}` 的 runtime 偵測與 exit contract 都會錯。

### Added
- **`hooks/seal-guard.ps1` — seal-guard 的 Windows 原生移植**（Windows PowerShell 5.1+，不依賴 bash/WSL）：loop 保護、git 偵測、user-facing surface 啟發式、seal 證據、telemetry、雙 runtime exit contract（Claude exit 2＋stderr／Codex `decision:block` JSON＋exit 0）逐條對等；任何偵測失敗一律 exit 0（never-wedge 契約不變）。六情境行為測試已在真 Windows PowerShell 5.1（WSL interop）跑綠。兩個 `.ps1` 不變式：UTF-8 BOM 必須保留（PS 5.1 把無 BOM 非 ASCII 腳本當 ANSI 解析、中文字串直接 parse error——實測踩到），`SEAL_GUARD_PATTERNS` 為 .NET regex（預設值與 POSIX 版等價）。
- **`/codex-skill-transfer` 0.16.0 hook 移植的同名 `.ps1` 規則**：移植 command handler 時，凡指令執行套件內 `.sh` 且旁邊有同名 `.ps1`，`commandWindows` 即指向 `powershell -NoProfile -ExecutionPolicy Bypass -File "${PLUGIN_ROOT}/….ps1"`（Windows 全功能）；無 `.ps1` 的 handler 才降級 `cmd /c exit 0` 並列入報告；來源自帶 `commandWindows` 一律原樣保留。malformed handler（command 缺失/非 string）也保證拿到 `commandWindows`（Luna Max 獨立審核 finding 修正）。
- **測試**：pytest 新增 `.ps1` 同名規則、來源覆寫保留、malformed handler 計數三組斷言；integration suite 新增 G14（BOM＋中文指示字串與 bash 版 byte 對等）與 G15（WSL interop 存在時在真 PS 5.1 跑六情境行為套件，否則乾淨 SKIP）。

## [3.3.0] - 2026-08-06

### Changed
- **`/write` 吸收 [human-writing](https://github.com/KKKKhazix/human-writing) 對模型寫作慣性的行為級提點**。zh rule 5 從字面禁「不是X，而是Y」升級為**翻案腔修辭動作偵測**——先立讀者沒有的誤解再推翻抬價，換字仍算命中（並非…而是／不在於…而在於／與其說…不如說／看似…實則／你以為…其實／回頭才發現／A不重要，重要的是B 及省字、跨句變形；「不只…還…」正常遞進可用，落在翻案位置才處理）；en rule 5 同步改為 gesture-based（"The real question isn't X"、"You'd think X, but" 均命中）。
- **zh rule 9 修正假細節漏洞**：原條文教模型自行編出具體時地人（台北車站三樓的星巴克）替換飄浮錨點——正是「假細節越具體，AI 味越重」的反模式。改為具體錨點只能來自原文或使用者材料；Refine 無真實細節可換時在修正說明標記請使用者補、不得代編，Generate 只用 prompt 給出的具體資訊。
- **writing-principles.md 新增六條模型指紋（zh 10–15）**：句長齊一與固定鼓點（十字句要能挨著四十字句、段末不逐段補短判斷）／連接詞過密（刪一半，中文小句靠語序事理自接）／同義詞迴避（該重複就重複，不換「這門手藝」「這項技能」）／動作後補解釋（動作已載情緒就句號收住）／抒情詞與借喻包裝（安放微光褶皺＋倉庫浪潮底座＋抽象名詞配具體動詞）／商業黑話（賦能抓手閉環還原成人、動作、錢、時間、後果）。entry 9 擴充洞察路標（說白了／先說結論／更微妙的是）與提示性冒號禁令（散文冒號只引原話）。en 新增 5–6（No elegant variation／Vary sentence rhythm）。
- **Generate 加 material-bound composition**：每句要新增事實、動作或後果，換句話重講不算推進；材料薄就寫短，篇幅是目標、材料邊界是底線；不得虛構 prompt 沒給的精確細節。

## [3.2.0] - 2026-08-05

### Added
- **`/seal` 改為 dispatcher，五點驗收交給新的 verify-only `seal-agent`**。主 session 負責組裝載荷（合約路徑或 criteria 原文／diff 基準／測試指令／baseline 結果含降級旗標／scratch 路徑）、先跑 baseline、派遣、依報告修復；agent 在乾淨 context 只驗不修，寫入權限僅限突變探針注入與 byte-for-byte 還原（`git checkout` / `git restore` / `git stash` 明文禁止作為還原手段）。冷腦與修復手分開，避免「自己審自己剛改的東西」。
- **複驗迴圈與上限**：初次派遣＋最多 2 次複驗（總派遣 ≤3）。用盡仍有未清 findings → 不蓋章、seal-log 記 `unresolved`、原樣回報（「複驗上限已達（2 次）：{N} 項未清 findings 如下，未蓋章（seal-log: unresolved）。」）。seal-log result 枚舉自 `pass|fixed` 擴充為 `pass|fixed|unresolved`（seal-guard hook 只驗當日日期、不驗 result 值，故免改 hook）。
- **sealed 標記與合約狀態機**：`/contract` Step 2 模板成為 `> STATUS: sealed（{ISO 日期}）— {五點結果一行摘要}` 的唯一文法權威——位置為 H1 後第 2 行、冪等單行覆寫、只是「蓋章當下 clean」的時點聲明。`/seal` 在指紋比對（tracked diff＋untracked 清單差集）通過之後才寫入，target-pin 分支 2/3 一律不寫。
- **`tests/skills/test-contract-lifecycle.sh`**：三檔標記字面 byte-identical、seal dispatcher 條文、ship 三條件早停與兩不變式、五個使用者訊息格式、seal-agent verify-only 邊界（含「不得出現授予修復權語句」負向斷言）的具名機器錨。

### Changed
- **`/contract` 覆蓋 sealed 合約前先歸檔**：偵測到標記即 `mv` 進 `.claude/archived/{filename}-{unix_timestamp}` 後續寫，不再詢問；未 sealed 的異任務合約維持現行「停下另名」。「禁止靜默覆寫」條文加 sealed 例外。
- **`/ship` 收走做完的合約**：Step 1 偵測加第三輸入（root `CONTRACT*.md` 前 3 行含 sealed 標記），早停條件改為三者皆空（「沒有可歸檔的工作檔案，git 也乾淨，root 無 sealed 合約，結束。」）；Step 2 於 allowlist 掃描後歸檔 sealed 合約並在輸出附 sealed 計數。INV-1 明列兩個歸檔來源（allowlist 目錄＋sealed root 合約），INV-8 補註 sealed 合約刪除會入 staged diff 但不得主導 commit subject。
- **偵測一律只讀前 3 行**（`head -3 "$f" | grep -qF '> STATUS: sealed'`）：全檔 grep 會讓「把標記當常數釘在自己 Verbatim Constants 裡」的合約自我誤判為已封緘。
- **`seal/references/loop-pauses.md`**：帶內修復列改為主 session 職責（agent 回報 → 主 session 修），新增「複驗超限」與「指紋不符／探針殘留」兩個 Authorization 分類。

## [3.1.10] - 2026-08-03

### Changed
- **`/codex-skill-transfer` 0.15.0 將 Claude `AskUserQuestion` 優先映射到 Codex `request_user_input`**。Default mode 有暴露工具時，輸入與授權 PAUSE 使用結構化提問 UI；未開 `default_mode_request_user_input` 或 runtime 未提供工具時，仍保留文字停點，`/think` 則保留 phase split + `alignment.md` artifact gate，避免生成物只在單一實驗性設定下可用。
- **`/think` 四選一 Stage G 改為相容 3-option 上限的條件式兩段提問**：先選「送 /review」或「直接決定」，後者再選批准／繼續對焦／放棄；自動附加的 Other 只保留自由輸入，不承擔穩定第四選項。
- **超出 runtime payload 上限的批次會拆分**：`/book` 四題 pre-interview 轉為 3+1 兩次呼叫；所有功能性 code span 都輸出真實工具名 `request_user_input`，不再生成看似工具名的 `request_user_input authorization PAUSE` 等假 token。

## [3.1.8] - 2026-07-27

### Fixed
- **`/ship` archive 改為強制 local-only**。歸檔前先確保 repo root `.gitignore` 含 anchored archive 規則，並以 `git rm --cached` 解除既有 archive 的追蹤但保留本機檔案；ignore 與 zero-tracked 兩道檢查任一失敗即在搬移前停止。`git add -A` 不再把 hunt／review／think 工作紀錄一起送上遠端。

## [3.1.7] - 2026-07-27

### Fixed
- **seal-guard 路徑過濾器可覆寫（`SEAL_GUARD_PATHS`）**。原本來源目錄前綴寫死 `^(src|app|lib|bin|cli|ui)/`——這組假設「應用程式碼在頂層 src/」的佈局，在 plugin tree／monorepo 型 repo（含 baransu 自身）一個都不匹配，hook 因此**從未觸發過而無人知曉**：路徑不匹配時在 telemetry 寫入之前就 exit 0，月回看的「零事件」分不出是「沒漏 seal」還是「過濾器從沒匹配」。實測回報來源：ezBill 之外的三個主要 repo（baransu／common-dev-plugin／ga_agent）符合前綴的頂層目錄數皆為 0。
  - `seal-guard.sh`：前綴抽成 `SEAL_GUARD_PATHS`（預設值不變，行為零漂移），與既有 `SEAL_GUARD_PATTERNS` 同款式；註解明寫「非標準佈局必須覆寫，否則靜默不觸發」。
  - `seal-guard-hook.md`：Behavior §2 補 `SEAL_GUARD_PATHS` 與零事件歧義說明。
  - `selection-telemetry.md` 月回看段補 **Zero-event caveat**：seal-guard 零事件月在確認 `SEAL_GUARD_PATHS` 覆蓋實際佈局前不得讀為成功；只看誤擋率的降級決策看不見這種失效。
  - `test-seal-guard-hook.sh` 新增 G13：plugins/ 佈局預設不觸發（rc=0）、設 `SEAL_GUARD_PATHS=plugins` 後同一 diff 正確擋下（rc=2）。
- **Codex Stop hook 改用真正的 continuation 契約**。先前誤把通用輸出欄位 `continue:false` 當成 Stop 阻擋形式；實際上它會優先終止 continuation。Codex 分支改回傳 `decision:"block"`＋必填 `reason`，讓 seal miss 產生新的 continuation prompt；Claude 的 stderr＋exit 2 路徑保持不變。G11 改為逐欄斷言 payload，並明確拒絕 `continue`／`stopReason` 舊欄位。

## [3.1.6] - 2026-07-27

### Fixed
- **3.0.0 裁撤 `/execute` 的殘留全面清除**。裁撤時沒把名字加進殘留掃描，Gate 4 一路綠燈，發行面因此帶著一個不存在的 skill 活到 3.1.5。
  - `_shared/tdd.md`：8 處把 `/execute` 當現存 skill 的敘述改為執行管線；**§8 引用表兩列與實際 agent 檔對不上**（宣稱的參照句與路徑形式皆為舊版），改為與 `impl-agent.md` / `review-agent.md` 逐字相符。
  - `_shared/tdd.md` 另有 5 處指向 `review-agent` 的 **Phase 3 / test_quality 觀察維度**——該結構在現行 review-agent 已不存在，改綁現行四層級語義（`packaged confirm (quality)` / `advisory`）與 R6 審查順序。
  - `analyze/SKILL.md`：`/execute` 作為行為主體的兩句（`wave.md` 讀取權責、test-weight 最終裁量權）改為執行管線；移除「absorbed /execute triggers」標題註記。觸發詞「跑 execute」屬使用者輸入比對，保留。
  - `execution-pipeline.md` / `green-proof-verify.md` / `goal-alignment-filter.md` / `correction-strategy.md`：移除「formerly the standalone /execute skill」「pre-merge /execute skill」等遷移敘述，改為直述；`.claude/execute/` 目錄名保留（命名執行階段，`/ship` 歸檔規則以它為 key），但理由句不再以「合併後保留」表述。
  - `analyze/evals/`：兩份語料的 expected_behavior 仍寫「hand off to /execute」「build it with /analyze before /execute」，且提及 R8 已裁掉的 summarize-agent——修正為現行預期，避免 A/B 基準失真。
  - `codex-skill-transfer/references/`：adapter note 表改指 `/analyze`（與 `transfer.py` 的 `CODEX_SKILL_ADAPTERS` key 一致）；`agent-mapping.md` 移除 `/triage` investigator-agent 例句；`CODEX_PORT_PLAN.md` T1-1／T1-2 標題改為執行管線。
  - 三個 design preset 的 `design-cores/dashboard.html` 示範表格改用現行 skill（原列 `/grade`、`/triage`、`/bridge`、`/execute`、`/dev`）；`google-design-preset/tokens.css` 移除指向已不存在檔案的 spike 註解。

### Changed
- **殘留掃描（Gate 4）擴充為「被裁名稱＋被裁指令」**：`REMOVED_NAMES_RE` 加入 `full_review` 與 slash 形式的 `/execute`。裸 `execute` 不可用 word-boundary 掃（本倉常用動詞，且 `.claude/execute/` 是刻意保留的階段目錄名），故採 `\B/execute\b(?!/)`——命中指令形式，放行 `.claude/execute/`、`{slug}/execute/x.md`、`worktrees/execute-{date}`、`-b execute/{date}`。同時移除因來源已清而失效的 `investigator-agent` 白名單。
- **`test_design_typography_expression_axes.py` 的 optionality guard 改釘 commit range**：原以 `git diff HEAD` 判定 preset 是否被動過，實際語義是「preset 不得與 HEAD 有任何差異」，等於永久禁止後續任何 preset 編輯；改為比對該 cluster 的 `87ebbd4..2dab598`，讓「這個 cluster 沒動 preset」回到可驗證的歷史事實（沿用 dataviz E2E 套件既有的 base-commit 釘法）。
- **移除 8 處自述句「This body is English (agent-facing)」**：描述模型自己看得到的事實、不改變任何行為，只保留承重的「使用者輸出用繁體中文」指令。

## [3.1.5] - 2026-07-27

### Changed
- **週更本機自動演化（結構軸單軸，standing-auth）**：12/15 skill 體積合格（`analyze` 480、`design` 485、`book` 488 達 480 行上限跳過），全數走 diagnostician → 單變因 mutation → 3 盲評收斂護欄（keep = 3/3 strict 且每位 judge delta ≥ 2.0）。**7 採納、0 gate-退回、5 收斂擋下**；`verify-skills.py` + `make test` 全綠。
- 採納曲線（min delta）：contract +4.0、think +3.5、learn +3.0、health +2.5、ship +2.5、write +2.5、read +2.2。
  - `contract`（dim5 約束明確性）：`## Constraints` 五條各冠上具名短稱（一頁上限／閘則外置／只釘 WHAT／先讀碼再寫條文／只寫不驗），並把原本只藏在 Flow 散文裡的三條紅線升為具名條款——現實接觸強制閘、無捆綁停權、禁止靜默覆寫，各自標註所屬步驟。
  - `think`（dim6 高風險紀律）：Stage G 落檔補上防覆寫閘——`<slug>.md` / `<slug>.html` 若在開跑前已存在則一律不得覆寫或刪除，改用遞增後綴 `-2`、`-3` 直到兩個路徑都空，並在 SendUserFile caption 點名既有檔；全 skill 唯一可覆寫或刪除的檔案收斂為本回合自己產生的 `<slug>-draft.md`。
  - `learn`（dim4 可執行具體性）：Stage 4 Trigger 3「核心概念不透明」由自評式判斷（「你無法用一句話解釋」）改為可觀察測試——對每個由 `[source: {slug}]` 標記帶入的核心術語，嘗試僅用 `$FILTERED_SOURCES` 寫出一句定義並置入正文；寫不出即觸發，寫得出即不觸發，自評不再是判準。
  - `health`（dim2 階段連貫）：Step 2/3 標題改為描述實際行為（Route analysis depth／Classify findings and report）；Step 1c 移除對 Step 2 的前向引用並改用 Step 3 的三級嚴重度字彙（`[!] 嚴重`／`[~] 結構性`／`[-] 漸進`），不再使用只有 Step 3 才定義的英文別名。
  - `ship`（dim2）：Step 2 的 Archive allowlist 補上 `write`，與 Step 1 `ARCHIVE_DIRS` 對齊——原本 Step 1 偵測得到 `.claude/write/` 但 Step 2 不歸檔，偵測結果無人消費；並明寫兩份清單必須逐字一致。
  - `write`（dim3 失敗路徑）：Stage 0 voice preset 補上檔案不存在分支——不中止、不靜默丟棄，落到下一條 descriptor 規則並以 preset 字串本身當風格描述，發出固定通知；禁止改用其他 preset、禁止反問使用者，且 fallback 套用的 voice 仍受同樣的 must-not-override floor 約束。
  - `read`（dim4）：Stage 3 標題擷取的「明顯不是標題」模糊判斷改為三條可判定否決測試（章節編號 regex／去標點後長度 ≤ 2／固定 boilerplate 清單），任一命中才否決，否則該標題即為標題；fallback 順序明確化為 HTML `<title>` → URL path stem。
- 收斂擋下（不採納）：`evolve`（min 1.8 < 2.0）、`hunt`（min 1.5 < 2.0）、`codex-skill-transfer`（非全票，2/3）、`review`（非全票，2/3）、`seal`（非全票，2/3）。

## [3.1.4] - 2026-07-27

### Changed
- `/ship` 不再每次固定提交 `chore: 歸檔工作檔案並提交本次變更`。它會在 staging 後根據實際 diff 選擇 Conventional Commit type 並摘要主要交付成果；工作紀錄歸檔不會蓋過實質變更，純歸檔與無法判斷時則各有保守 fallback。

## [3.1.3] - 2026-07-27

### Fixed
- `/codex-skill-transfer` 0.14.2：生成的 `SKILL.md` 或複製的 `references/*.md` 若仍含 `CLAUDE_PLUGIN_ROOT`，transfer report 會逐檔列入需人工檢視。Token 保持原文、不盲改成僅由 Codex hook command 保證提供的 `PLUGIN_ROOT`，避免 delegate 等 skill 在移植後靜默引用不存在的 runtime 變數。

## [3.0.4] - 2026-07-20

### Changed
- **週更本機自動演化（結構軸單軸，standing-auth）**：14/15 skill 體積合格（book 480 行達上限跳過），全數走 diagnostician → 單變因 mutation → 3 盲評收斂護欄（keep = 3/3 strict 且每位 judge delta ≥ 2.0）。**10 採納、0 gate-退回、4 收斂擋下**；`verify-skills.py` + `make test` 全綠。
- 採納曲線（min delta）：seal +5、analyze +4、learn +4、contract +3、evolve +2、health +2、read +2、review +2、ship +2、think +2。
  - `analyze`（dim2 階段連貫）：改寫三處殘留的 pre-R5 多代理審查孤兒引用，Stage 4/5/6 對齊現行 Stage 6 單次 checklist 自審。
  - `contract`（dim3 失敗路徑）：Step 3 寫檔前補 CONTRACT.md 已存在分支——同任務確認後覆寫、異任務停下改名，禁止靜默覆寫。
  - `evolve`（dim4 可執行具體性）：Stage 7 held-out 釘為 Stage 5 盲評機制的逐字重跑（byte-identical panel 副本＋奇偶輪派位），回歸觸發改為可判定投票語言（≥2/3 判舊版較佳）。
  - `health`（dim4）：Step 3 跨 runtime instruction-drift 的 hedge 觸發改為可判定規則。
  - `learn`（dim4）：收窄三處未釘決策規則的 hedge（lane timeout 具約束力、無來源支撐一律排除等）。
  - `read`（dim2）：兩處跨節引用由位置索引改為具名錨點，零增行。
  - `review`（dim2）：Stage 2/3 對調，Grade-scope 表三處前向引用全部轉為後向。
  - `seal`（dim6 高風險紀律）：突變抽查第 5 點升為機制級 gate——注入前留存前像、revert 後逐 byte 確認。
  - `ship`（dim6）：`git add -A` 前插入具名 secret gate，untracked/modified 路徑逐一比對封閉字面 pattern 清單（.env、*.pem、*.key、id_rsa* 等）。
  - `think`（dim1 觸發清晰）：frontmatter description 開頭宣告補上 Evaluation Mode 的 Kill/Keep 單行判決出口。
- 收斂擋下（不採納）：`codex-skill-transfer`（min 1 < 2）、`design`（min 1 < 2）、`write`（min 1 < 2）、`hunt`（非全票，2 位判退步）。

## [3.0.3] - 2026-07-20

### Changed
- `/codex-skill-transfer` 0.13.0：依最新版 Codex hooks/plugin 官方規格，把 plugin-bundled `hooks/hooks.json` 從「只報告、不輸出」升級成 outcome-level mirror。支援的 lifecycle event + `type="command"` handler 會連同 hook scripts、manifest `"hooks": "./hooks/hooks.json"` 一起產出；`SessionEnd` 等無對應事件與非 command handler 逐名報告，絕不偷換語意。報告同步提醒 `/hooks` review/trust。
- `seal-guard` 改為 Claude/Codex 雙 runtime：Claude 維持 exit 2 + stderr；Codex 以官方 `continue:false` JSON 阻擋 Stop。Codex mirror 因此第一次實際攜帶週末新增的 seal miss 機械守衛，而不再只有說明文件。

## [3.0.2] - 2026-07-19

### Changed
- `/contract`, `/seal`: structure pass per official skill-authoring best practices (narrative provenance cut, maintainer boilerplate trimmed) + one evolve ratchet round each (blind 3/3, held-out clean): contract gains the greenfield no-code branch (affirmative G2 declaration, silence non-compliant); seal gains the Baseline suite pre-flight (no-suite degradation to static pin-audit; red-baseline relative attribution).

## [3.0.1] - 2026-07-19

### Changed
- **Telemetry centralized to user scope**: all telemetry ledgers move from per-project `.claude/harness/` to `~/.claude/baransu/telemetry/{project}/{type}-{YYYY-MM}.jsonl` — split by project (git-root basename; cwd folder name when no git) and by month (monthly files are the rotation). Collection is one directory read; `BARANSU_TELEMETRY_DIR` overrides the root. seal-guard hook, `/seal` evidence obligation, and `_shared/selection-telemetry.md` all point at the central layout.

## v3.0.0 (2026-07-19)

**版圖重組：三頻段路由落地——雙塔合一＋雙釘獨立＋修憲 15**。plugin version 2.13.0 → 3.0.0。依據：10-arm harness×model 矩陣實驗＋R1–R9 改革驗證輪（核心結論——品質槓桿是驗收條文的可斷言性，不是流程重量；改革版全套 p3-os′ 以 59% 成本追平頂級模型冠軍，一頁合約＋單次 seal 以 22% 成本達成行為面全數達標）。

- **BREAKING：`/baransu:execute` 移除**。其觸發詞（「開始執行」「跑 execute」「依照 analyze 執行」）與全流程併入 `/baransu:analyze`——spec 完成後直通內建執行管線（`analyze/references/execution-pipeline.md`）。舊 `/analyze` spec 要接續執行：改喚 `/baransu:analyze` 即可，Stage 0 會偵測既有 spec 直接進入執行段。
- **新增 `/contract`**：中頻段開工釘——一頁合約四節（目標／可斷言條文／錯不起表面清單／照抄常數塊），判準單一實作於 `_shared/contract-gate.md`（G1–G4＋R7）。
- **新增 `/seal`**：中頻段收工釘——單次窄域審查＋直接修正權，五點任務書（條文逐核／未釘 user-facing 表面掃描／cross-UI 一致性／常數 byte-diff／突變抽查），含 target-pin off-ramp。
- **執行管線 R8 裁剪**：summarize 派發與逐 task ctx 檔移除（agents 直讀 spec）、Red gate 降 advisory、審查退件重派上限 1；worktree 平行組、compile/failure 雙計數不變量、coverage-riding、merge/e2e-fix/final-fixer 收尾鏈全數保留。
- **修憲 14→15**（三處錨同步），附 falsifiable 條款：`/codex-skill-transfer` 遙測三個月零使用即退役回 14。
- **CLAUDE.md 三頻段路由表**：小＝直接實作（tdd.md §7）／中＝contract＋seal／大＝analyze 全管線；不得強迫任務升降頻段。
- **seal-guard hook 隨 plugin 出貨、安裝即生效**（`hooks/seal-guard.sh`＋`hooks/hooks.json` 註冊 Stop）：偵測「本 session 碰了 user-facing 表面卻無 seal 記錄」——**預設阻擋模式**（exit 2 擋停止並回饋繁中指示；`stop_hook_active` 防迴圈早退），`SEAL_GUARD=log|off` 可降級；無論何種模式都 append `.claude/harness/seal-guard.jsonl`（遙測不中斷）。falsifiable 條款：月回看誤擋率過高即把出貨預設降為 log。
- **選用遙測慣例**（`_shared/selection-telemetry.md`）：skill 選用決策記入 `.claude/harness/selection-log.jsonl`，月回看計算誤觸發／漏觸發率——觸發正確率可觀測是本次重組的成功判準。

## v2.13.0 (2026-07-17)

**/think Stage G 交接產物改為七段執行 prompt**。plugin version 2.12.0 → 2.13.0。原本 Option 2 批准後的交接物是「一段話 handoff summary」，下游實作方實際上還得回頭消化五段計畫與審議紀錄。改為直接產出執行者導向的七段骨架 prompt（Role / Goal / Success criteria / Constraints / Tools / Output / Stop rules，不適用的段落省略）：Building → Goal、驗收標準 → Success criteria、約束＋Key decisions＋Not building → Constraints、Unknowns → Stop rules 的 ask-or-stop 觸發。審議紀錄（Stage 記錄、PAUSE/批准軌跡）留在五段計畫作人審軌跡，不進交接物。依據：四管線 A/B 實驗（同一模糊需求 × 4 條規格化路徑 × 隱藏 fixture 盲評）——七段格式與五段計畫執行品質相同（16/17 打平），但產物縮 ~40%（120 行 → 74 行）、規格化省 44% 時間、下游執行 token 也較低。codex 變體同步鏡像。

## v2.12.0 (2026-07-15)

**codex-skill-transfer 修懸空 repo 路徑參照**。plugin version 2.11.0 → 2.12.0；skill 0.11.0 → 0.12.0。移植到 Codex 後，skill body 內以 `plugins/baransu/…` 開頭的 repo 根相對參照（reviewer/inspector agent 檔、`_shared` 共享文件、跨 skill 腳本）與 `.claude/` 輸出目錄在 Codex 佈局下懸空——被派的 subagent 被叫去讀不存在的路徑而失去目標。新增 `rewrite_repo_paths`：

- **agent 參照** `plugins/baransu/agents/<name>.md` → `~/.codex/agents/<name>.toml`（含 glob，如 `*-reviewer`）
- **`_shared`／跨 skill** `plugins/baransu/skills/<seg>/…` → 依檔案深度的相對路徑（SKILL.md `../`、references `../../`）；自我參照塌成 skill-root 相對（含剝除 `$VAR/` bash 錨點，如 health collector）
- **`.claude/<dir>` → `.codex/<dir>`**（輸出/設定目錄；`.claude-plugin` 不誤傷）與 `.claude-plugin/plugin.json` → `.codex-plugin/plugin.json`
- 作用面：SKILL.md body、`description` frontmatter、`references/*.md`、逐字複製的 `_shared/*.md`、agent stub TOML（扁平安裝，跳過無錨點的 `_shared` 相對化）
- **豁免**：`codex-skill-transfer` 自身（mapping 文件）與 design `slide-checklist.md`（版本紀律範例）——這些 `plugins/baransu/…` 是描述 repo 本身、非 live 參照
- 重生 `codex/`（Layout A 已提交產物）使修復對 Codex 使用者生效

## v2.11.0 (2026-07-12)

**全席 evolve ratchet 第一輪(v2.10.0 基準)——七席採納**。plugin version 2.10.0 → 2.11.0。nightly-evolve 盲測提案輪(14 skill × 診斷+變異+3 盲評,margin 2.0 守衛;採納走 Gate 1b standing-auth,結構閘 write-verify-restore 全過):

- **analyze D3**:Stage 7 Done-when 閘自身失敗分支明文化(缺 spec 檔→回產出層重生一次;goal/requirement placeholder 絕不自動修,呈使用者確認)
- **codex-skill-transfer D6**:marker-check 拒絕(exit 2)目錄 agent 絕不可自刪——列內容、換目錄或等人類明示路徑;移除「if you are certain」模糊授權
- **design D2**:Export-brief Step 2/3 懸空抽取錨點全解析到 Gen Mode 九節正典 + 每抽取點 if-then fallback
- **evolve D3**:Stage 3 窗口中斷恢復(live≠snapshot 且無採納記錄→先還原記 window-breach-restored 再診斷)
- **execute D4**:§4b per-task commit 釘死暫存範圍(ctx Files + impl 報告檔案;worktree 外絕不 git add -A)
- **learn D4**:四 hedge 改可判定規則(lane timeout 固定、排除=⚠️∧無補源、critical claim 可觀察定義、平行模型綁定)
- **ship D3**:Teardown 腳本遺失/不可執行→保守 GATE_FAIL(不手工替代刪除,保留 worktree 回報)
- 七席 margin-converged(0.5-1.5)= 大修後結構軸天花板健康收斂;design 首輪撞 session limit 由 resume 快取補跑

## v2.10.0 (2026-07-12)

**遞延美學功能一次落地——design/book 八候選連續完成(ultracode 單 workflow,12 agents)**。plugin version 2.9.0 → 2.10.0。上游素材淺 clone 實讀(Kami/diagram-design/guizang/Waza+官方 frontend-design),三視角對抗驗證(美學統一/機械正確性/出處汙染)後收斂:

- **book 圖表目錄 14→17**:新增 `type-org-chart`(含顧問情境矩陣變體,交叉引用 quadrant)、`type-class`(EXTENDS/HAS-A 邊語彙)、`type-architecture-board`(架構板);三檔逐節同構於既有結構契約,inline 範例全過機械閘門(雙 paper-mask、雙射 markers、寬度階、×4 幾何、單焦點、LEGEND、「圖:」)。`svg-rendering-rules` §4.9/§4.10 全表面同步、新增 §4.11。
- **維護型圖表 trio 契約**:`maintained-diagrams.md` —— 與 repo 同生圖表的生命週期契約(trio 工件、意圖塊、證據巡檢與權威鏈、成熟度編碼、匯出紀律、反模式);Kami 概念全文自行表述。
- **架構板規模級**:`type-architecture` 增補 ≤9 節點 → 分板升級 → 姊妹板+意圖檔邊界的三級指引。
- **design 尺寸反比權重梯**:`typography-discipline.md` —— 越大越細/越小越粗、字級下限(guizang AGPL 概念,n-gram 比對 0 verbatim);Waza 系 CJK 文字適配三件組(孤行防護、長詞/在地化字串預試、整段截斷紀律)。
- **表達軸雙軸**:`expression-axes.md` —— 背景質感軸(flat→grain→noise→gradient)與動效預算軸(none/functional/expressive),官方 skill 萃取,INFORM-not-dictate 錨定 aesthetics-foundation 元規則;三 preset 與 check.py 位元組不動(sha256 釘死)。
- **守衛升級**:`test_book_diagram_types_17`(5 檔×陳舊計數措辭掃描)+ `test_design_typography_expression_axes`;下游 `design-token-resolver`/`color-reasoning`/`slide-checklist` 計數殘留(含既存陳舊)全清。

## v2.9.0 (2026-07-11)

**美學基底與出廠修復——design/book 回歸「美學與統一」本心**。plugin version 2.8.0 → 2.9.0。三 PR 合併:

- **PR #5 經典美學基底(盲測全票勝出)**:`design/references/aesthetics-foundation.md`(238 行)——七部經典(Itten/Albers/Arnheim+格式塔/Rams/原研哉/Müller-Brockmann/Tschichold)經 /learn 消化蒸餾為決策規則,每條落名出處;元規則「理論服務於軟弱時刻,永不覆蓋直覺 — Itten」。實驗證據:2 brief × 2 條件盲測 clearly-better ×2 全票;機制=基底提供「brief→專屬材質隱喻→全 token 推導」,無基底側落入體裁先驗;理論致平坦化被反證。Gen Mode 接線(INFORM not dictate,Preset Mode 不讀);book 新視覺結構按需引用。上游吸收:Waza 方向防衛框架、反泛型禁名單、字型配對規則、huashu 採樣→收斂→論證+印墨彩度帶(MIT)、CJK 排印(screen/print line-height 分歧明文)、Kami AI-slop +6 列、diagram-design 7-role 節點表+註解原語(MIT)。
- **PR #4 煙霧測試出廠級修復**:真執行煙霧發現 4 high——全新 preset 過不了自家 sanity(lint 打中規格散文→check.py .md inline-code 豁免)、冪等重跑被 schema 欄打死(殘留 regex 對齊)、html2pptx 遇 inline SVG 必崩(SVGAnimatedString→getAttribute)、pptxgenjs 裝 global 驗 cwd(同境化);+6 medium(--dry-run 真列表化、GATE-F regex、playwright 驗二進位、GATE-F/G 接入實流程+slides-{slug}/ 落盤契約、Preset Mode staged 驗證錨點)。兩煙霧閘門實證翻綠。
- **PR #3 hunt 快徑收口**:C'2 驗證(Locate 期建檔錨點 PASS)回饋——資格判定去循環(路由時跑 blast grep)、relevant 定義、必記路由行、短表五節精確邊界、狀態梯快徑摺疊、建檔逐字引 status 行。

## v2.8.0 (2026-07-10)

**慣性帳本大修——用盲測 A/B 實驗量化「skill 對抗了哪些模型慣性」，據以增重與減重**。plugin version 2.7.7 → 2.8.0。方法論：同一任務三條件盲測（模型直接動手＝金標準／模型+skill／異模型+skill），不知情 examiner 依工件建行為側寫，盲測 judge 產出四欄慣性帳本（skill 解決的／沒解決的／skill 造成的枷鎖／無行為指紋的純紀錄條款），修訂後精簡驗證輪確認收斂。execute 跑了 4 輪（v1→v4）+ 平等 A/B 終局；read/learn/hunt 各 1 輪；write/design/book/health/evolve/think/analyze/review 以注入慣性知識的綜合審計覆蓋。

**核心量化結果（execute，NovelReader 書籤功能 fixture，2×3 模型×方法矩陣，9 工作區）**：
- 對齊目標達成（終審 ×2 一致判 yes）：Opus+v4 ↔ Fable+v4 相似度 82-83，達 Fable 自身噪音底線 81；R1 起點僅 ~50
- Opus 完成定義分 6→10（超越 Fable 直接跑的 8.9）；無 skill 對照組（Opus 直接）C2+C5 雙 FAIL 證實「中層字面主義／揭露不修復」為模型原生慣性，v2+ 的 goal-criteria gate 與 latent-defect 規則精準導正
- Fable 在 v4 下零回歸，且兩模型都主動修復 production FK 潛藏缺陷並寫 reopen 級測試

**execute（v1→v4）**：goal.md 準則字面權威 + Step 6 逐條 C{n} 交叉核對（test-green-but-production-inert = 未達成）；latent-defect 規則（小規模在地修復折入當前 task，揭露不換 ✅）；工作文件封閉清單（儀式 15 檔 490 行→9 檔 232 行）；coverage-riding 測試分層（純接線任務免 per-task prove-red，具名 pinning tests + E2E 網承擔；test_weight gate-time 決策入 task-map，事後追認=違規）；red_proof 證據欄（Red gate 不能事後追認）；per-task commit 明文化；persistence 措辭需 reopen 級證明；審計 bug 修復：compile error 無界重試死循環（獨立連續計數 3 次 BLOCKED）、cascade-blocked 遞移傳播、worktree checkout 撞 `.git/worktrees/`（改 `.claude/worktrees/`，實證 git metadata 同目錄樹永髒）、全降級路徑 spec_contradiction 不可達、green_proof 欄名跨檔漂移。

**無 git 專案不再死卡**：execute Step 0 git 探測 + L/XL 單向降級為就地序列執行（不重試不 block）、Step 7 清理失敗走 prune→範圍守衛 rm→續行；ship 探測前置於歸檔搬移、無 git 明確停止；analyze 覆寫重建分支無 git 時自動走 -N 後綴不刪任何東西；think Stage D REPO_ROOT cwd fallback；hunt bisect 非 git 跳過。

**read**：三 run 產出位元組級一致（相似度 90-95）證實核心機制條款對前沿模型無行為指紋——保留為跨 skill 格式契約；修 raw/ 重抓覆寫（`_vN` 版本化）、Chrome 探測改 lazy、SPA 偵測從屬品質檢查＋無 Chrome 明確出口、GET-first PDF 偵測、相對圖址＋重名唯一化、raw/material slug 配對改名、完成前強制完整性 pass（file(1) 驗圖/remote-ref grep=0）、四份 reference 繞管線直寫 material 修正、DOI 僅 --use-proxy 才進 cascade、candidate 多輪可達化、glob 空白檔名、首標題垃圾 slug 防呆。

**learn**：帳本反轉——skill 後勤全贏（工件契約/溯源），思考輸給自由跑（9.4-10 vs 6-9）；批判裝置只在 --brief 路徑。修：批判層四節強制進 digest 路徑（來源矛盾點含裁決＋「查無矛盾」須明說／盲點／信度評分表含可觀察訊號依據／後續調查角度，Refine 分割保護不被洗掉）、引註段落級保留（成文丟 tag=違規）、Refine 右尺寸（/write 長文 change-points 處理、draft 重複檔刪除、無變更合法）、§3.5 fan-out 候選落盤捕獲步（high：原規格 bare-topic 跑不完）、觸發器重置/範圍語意、語言偵測去 shell 化。

**hunt**：三 run 全 0 盲改直取根因——「不追根因」慣性在前沿模型不存在；skill 真值=案例記憶/Scope Blast/測試矩陣/儀器衛生。修：快徑（首儀器定根因+blast≤3 → 壓縮儀式）、迴歸守護端到端保真（helper/內部縫斷言不算——帳本抓到的字面化漏洞）、RED 證據逐字保存、bisect stash push→apply→drop 復原（原規格 stash 後永不 pop）、案例檔 Locate 期建立含 status 生命週期、刪矛盾的 allowed-tools frontmatter、新建 loop-pauses.md。

**輕量群綜合審計（3 high + 37 medium）**：design——google preset 過不了自家 lint（43 違規，check.py Check C/E 修復＋實證三 preset 全綠）、gen 模式自然語言入口死路、Gen 走 staging 原子流、新建 loop-pauses.md；book——PPT 管線 960px 規格必炸（統一 960pt×540pt）、html2pptx 多輸入合併、CJK 空 slug 鏈、fact-verify regex 過寬；write——change-points/「全部」契約補全（learn 消費路徑）、en/zh anti-AI floor 分語言、Generate 綁完整規則集；health——inspector 派發欄位對齊、collect-data.sh no-git/缺檔防呆、新建 loop-pauses.md；evolve——結構閘門改有界寫入→驗證→還原窗口（原規格驗的是快照非變異）、盲測改中性 panel alpha/beta 副本（路徑不再洩底，nightly workflow 同步）、held-out 回歸分支、非 baransu 目標降級閘門。

**think/analyze/review 複檢（15 項跨 skill 收口）**：think Option 1 先落盤 draft 再送 /review、loop-pauses 逐互動點枚舉（Stage G=Authorization）；analyze Stage 6 補 goal.md C{n} 驗證 lane（缺口死在 spec 期）、未檢查 verdict 補消費者、新建 loop-pauses.md、task 模板加測試重量建議欄（riding 鉤子）；review needs-judgment 統一 Authorization、review-agent green_proof 對齊 execute 機械閘門。

**匯流檔案契約**：ship 歸檔白名單補 write；execute Step 7 journal 選擇規則（slug 匹配→mtime 最新＋註明，review 亦為 producer）；loop-contract §4 註冊表補 /design /hunt /health /analyze 四列。

- 驗證：`make test` 全綠（19 結構斷言＋pytest 246+＋全 shell suite）、`make mirror-check` in sync、實驗全紀錄於 9 個 NovelReader 工作區 + 21 個 workflow/agent 回報。
- **同版本後續增補（release 前同 PR 累積）**：C' 驗證輪——learn 9.5/10 追平自由跑金標準（批判層四節實質到位、33 段落級引註過 Refine 保留，judge 判 improved、四 delta 全關）；hunt 9/10 ~7 分鐘（快徑生效、RED 逐字證據、四層端到端迴歸守護、首獵 skip，judge 判 improved 4/5 delta 關閉，殘餘 Locate 期建檔已補錨）。verify-skills.py Gates 10/11（loop-pauses 註冊完整性、green_proof 欄名一致，TDD 18 tests，零豁免執法）。覆蓋完成審計 21 項修復（codex mirror AskUserQuestion 改寫污染守衛、輸出 rmtree 防護、_shared 掃描、final-fixer C{n} 範圍擴充、loop-contract §2 釐清、tdd §7.1 canonical 收回）。evals 14 skill 體檢＋CLAUDE.md 七條新 invariant 入冊＋review target-pin 三表面統一。
- **燃燒窗口增補（2026-07-11）**：**L-class 機械首次實測**（雙獨立群組 utils fixture）——機械全過（正確路徑 worktrees、--no-ff merge、integration_status、閘門式 -D、終態零殘留），挖出 dispatch 工具缺席契約空白 → **serial-absorbed 第三執行模式入契約**（Step 0 tool-list 探測、分類/worktree/merge/清理全保留、角色吸收僅此模式獲准且機械閘門照舊）＋「Agent tool 恆在」偽不變式改寫＋§4a registry-before-add 封 crash-window；**L2 驗證輪 8.5/10 證實新契約可逐字遵循**，再收 8 條細化（證據持久性：/tmp 隔夜蒸發實錘 → output_tail/red_proof 必須落 checklist；§4a 單一表述；git+dispatch 雙缺席優先權；trace 自含性）。**health dogfood**（baransu repo 自審）：7 項 skill 自修（dogfood 邊界、\$HEALTH_SCRIPTS_DIR fallback、哨兵防碰撞、第三 mutation 列、雙向委派檢查、memory 路徑指引、tier 口徑）＋ AGENTS.md 漂移段刪除。**nightly-evolve dogfood ×4 批（14/14 skill ratchet 全覆蓋）**：盲測 panel（中性 alpha/beta、輪次奇偶）與 margin 守衛全程正常，六提案過檻採納——book 安裝閘門、read rename 防巢狀（抓到本輪自引入隱患）、analyze Stage 5 task 編號回填（解前向引用孤兒）、learn \$TEMP_FILES 追蹤式清理、design Gen 驗證錨點歸位（Check B/C 從永不觸發變可觸發）、review Stage 1 量化主張處置去循環；七個 margin 1-1.5 小改被守衛正確擋下（大修後結構軸收斂訊號）。nightly-evolve args 字串容忍（driver 實測坑）。

**review-agent rationale 對齊——收束 v2.7.6 的 leaf doc-debt**。plugin version 2.7.6 → 2.7.7。v2.7.6 因 C7「leaf worker 檔零改動」硬驗收，未一併對齊 `agents/review-agent.md` 的自我禁令理由，留下一筆跨檔不一致的 doc-debt（`review-agent.md:81` 仍寫「subagent depth = 1, cannot dispatch parallel Tasks」，而 `CLAUDE.md:81` 已改「AskUserQuestion 硬缺席」）。本版本以獨立微任務收束。

- **`agents/review-agent.md:81`**：Prohibition 理由由「depth = 1／cannot dispatch parallel Tasks」改為與 `CLAUDE.md:81` 一致的模型判斷式——「call 前自判 /review 非 subagent-safe：其路徑上有不可降級的 AskUserQuestion 點（target-pin），在 subagent 內硬缺席，故會 strand 該點，而非 depth 上限違規」。**行為結論不變**（不呼叫 /review、直接實作四層語意）。
- 版本 2.7.6→2.7.7（4 觸點）、codex mirror regen、`make test` 全綠。

## v2.7.6 (2026-07-07)

**Subagent 巢狀 fan-out——被托管 dispatcher 照常派 worker**。plugin version 2.7.5 → 2.7.6。四個會派 subagent 的 dispatcher skill（review/execute/evolve/health）原先隱含「自己被當 subagent 托管時不得再 fan-out」的 dispatcher-level depth=1 假設；探針（run a928109）實測 `Agent` 工具在 subagent 內恆在、`AskUserQuestion` 則硬缺席，故該假設事實錯誤。本版本移除之，並把「工具缺席」的互動降級收編進 loop-contract。經 /analyze→/execute 五組 TDAID 實作、/review 複審。

- **`_shared/loop-contract.md` §Scope/§2 擴充**：新增「被 subagent 托管（AskUserQuestion 工具缺席）」為一種 non-interactive driving context；§2 Input-PAUSE 觸發源涵蓋「工具缺席」，Authorization-PAUSE 明言不因工具缺席弱化（仍硬停／standing-auth，「Cannot ask」不等於「may assume」）；新增偵測原語小節＝**檢視自身工具清單**（非 attempt-and-catch），且只 gate 互動軸、不 gate fan-out。§3 三硬停未動。
- **四 dispatcher SKILL（＋execute/evolve orchestration-interface）**：明述 worker fan-out 不因自身被托管而停用（`Agent` 恆在），並清楚區分 dispatcher-level（可 fan-out）與 leaf-level（不再往下派）兩種 depth 語意；fan-out 與互動能力偵測為兩正交軸，不綁 AskUserQuestion proxy。evolve 歸類為純 fan-out（採納閘＝loop-contract Authorization PAUSE＋standing-auth）。
- **`review/SKILL.md` 四個 AskUserQuestion 點降級**：`:54` target-pin 缺席時 stop 回報 needs-input 不捏造；`:92` domain 缺席時不派 domain-reviewer、不宣稱覆蓋；`:231`/`:292` needs-judgment 缺席時取推薦預設＋標註「此處採預設」＋回報上層。human-present 路徑逐字保留（append-only）。
- **`rules/anti-patterns.md` 首條＋`CLAUDE.md` review-agent invariant** 改模型自主判斷式：事實前提由「depth 硬上限」更正為「AskUserQuestion 硬缺席」，改為呼叫方 call 前自判 subagent-safe，不設機器可檢的旗標／test gate（使用者明選模型自主，殘留風險由降級對映兜底）。
- **不變式保全**：leaf worker agent 檔（evolve-judge／health-inspector-*／review-agent／smart-friend-agent／evolve-diagnostician）git diff 零改動；/analyze 維持不可巢狀。
- **驗證**：fan-out 探針 depth-2 真實通過（並行 2 worker 皆回具名字串）；AskUserQuestion 硬缺席以 tool-list inspection live 觀察；`make test` 全綠、`make mirror-check` in sync、codex mirror 同步 regen。
- **/review 修正**：複審自身 diff 找到 2 項 in-scope 文字缺陷並直接修正——`review/SKILL.md` 降級節自引行號過時（改用 edit-stable Stage 名稱）、`CLAUDE.md` review-agent invariant 理由過度涵蓋 needs-judgment（收窄為僅 target-pin 不可降級）。

## v2.7.5 (2026-07-07)

**覆蓋錯置防護——第 8 條通用行為內核**。plugin version 2.7.4 → 2.7.5。多生態系盲測中唯一一致 partial 的缺陷（被引測試 mock 掉它宣稱要覆蓋的那一層 → 對該層覆蓋率其實為零）補上通用行為提示後升級為 full catch。

- **`_shared/fact-check.md` 新增「Coverage claims」節**：覆蓋宣稱（「已被測試／安全網充足／可安全重構」）不因測試「提到」被改單元就成立——須確認測試驅動**真實**實作並斷言其**實際**行為。符號出現在 mock／stub／spy／fake 建構裡是**反覆蓋**：證明測試刻意把該碼換成替身、一行都沒跑。計數某層覆蓋時排除所有落在 mock 建構內的引用；一支以其名為名卻 mock 掉該層的 spec，對它的覆蓋率是零。跨生態系（`vi.mock`／`jest.mock`／`Mock<>`／`patch`／`Mockito.mock` 皆示意）。
- **think Stage D test-safety-net inventory 同步 mock-awareness 應用點**：層級覆蓋 grep 排除落在 mock/stub/fake 內的 entry-point 引用（「0 unmocked invocations」）。
- **驗證**：Vue/JS 盲測重驗 FD3 3/3 partial→caught、surfaced_vimock 全 true、其餘三缺陷零退步。
- codex mirror 同步 regen。

## v2.7.4 (2026-07-07)

**De-overfit——移除 .NET 專用機器，蒸餾為 7 條跨生態系行為紀律**。plugin version 2.7.3 → 2.7.4。2.7.1–2.7.3 的 review 強化路線偏向了「造一台只會數某個 .NET 專案的機器」；本版本把它拉回通用型模型行為調教。3-agent 平行審計三 skill（think 6 general-keep／8 overfit-generalize、analyze 2／3、review 1 keep／9 generalize／2 remove）找出 41 個硬編生態系標記。

- **移除**：`skills/review/scripts/fact-count.sh` 與 `tests/skills/test-fact-count.sh`（.NET-only：`*.cs`／`*.csproj`／`[TestMethod]`／`class \w+Impl`／dot-prefixed 全寫死；於 2.7.3 引入，本版本移除）。
- **`_shared/fact-check.md` 改寫**：五條 .NET 指令模板 → 生態系無關的計數名詞／驗證原則（語法只當「例如 C 家族／Python／Node…」示意，非必要機器）。
- **think／analyze／review／quality-reviewer 共 11 處 de-.NET 編輯**：還原 `[(Test|TestMethod|Fact)]` 同步補丁、`bin/obj/node_modules` 三元組改為「本 stack 的建置／依賴目錄」、`*.csproj` 枚舉改為「本 stack 的專案／manifest／測試檔標記」、Facade-sign／簽核 domain 詞改為中性示意、修一處懸空 `category` 引用。
- **蒸餾出 7 條通用行為內核**：立場前提先重推導／repo-root 枚舉優先／覆蓋量在被改層／計數名詞紀律／claim-cite＋字面數字＋獨立重驗／分支盤點式測試設計／發出前掃描 fail-closed。
- **多生態系盲測**（不再只用 .NET）：對 Vue/JS 前端造植入四缺陷的計畫盲審——3/3 generality proven。關鍵發現：**移除過擬合腳本後，.NET 回歸反而更強**——腳本版漏掉的框架誤標與 facade 灌水，通用版全抓（模型改用推理推導正確 pattern，而非依賴會被誤用的腳本）。think／analyze 亦以同法補驗，各 3/3 proven。
- codex mirror 同步 regen（含移除的兩檔）。

## v2.7.3 (2026-07-07)

**review 計數名詞紀律機械化——fact-count.sh 執行器**（於 2.7.4 移除，見上）。plugin version 2.7.2 → 2.7.3。針對 review 重驗時「重跑目標自己的指令＝可重現但名詞可能錯」的失敗模式，把五類計數模板做成可執行檔。

- **`skills/review/scripts/fact-count.sh`**：五子指令（檔案／類別／呼叫點／測試案例／框架指紋），前導點硬編、逐專案指紋、排除建置目錄。
- **`_shared/fact-check.md` Executor 節＋SKILL template-authority 規則**：事實表列須由模板／腳本填、重跑目標指令永不算 ✔、偏離模板者標 `✘ (template-deviation)`。
- **後記（誠實）**：此路線被 2.7.4 判定為專案過擬合並移除；其一般性內核（一名詞一指令、獨立重跑、永不重跑目標指令）以純原則形式保留於改寫後的 fact-check.md。

## v2.7.2 (2026-07-07)

**review 事實查核紀律——量化宣稱 ✔/✘ 處置帳本**。plugin version 2.7.1 → 2.7.2。基準盲測顯示弱模型會「背書假前提」（把目標的計數宣稱列為逐條實查為真而未重驗），本版本強制逐條處置。

- **Stage 1 量化宣稱處置帳本**：目標的每個承重計數／存在／覆蓋宣稱進 claim checklist 帶 `✔`/`✘` 處置，嚴禁裸複述；輸出形狀改為含「實查結果」欄的表。
- **Unverified-claims hard-stop 擴充**：目標自寫的 `(verified:)` 標籤不算 in-session 證據；承重宣稱未被獨立重跑、或重跑出不同數字／名詞即命中，釘進需判斷層不可降 advisory。
- **quality-reviewer 重跑令**：計數宣稱須自 repo root 重跑其指令。
- **Stage 1.5 正向觸發**：計畫只要斷言任何狀態轉換／審批路徑即屬 business behavior（即使自稱「純結構重構」），強制建轉移表並對上游流查核。
- codex mirror 同步 regen。

## v2.7.1 (2026-07-07)

**think／analyze 行為紀律強化——讓 Opus 逼近 Fable**。plugin version 2.7.0 → 2.7.1。以 headless A/B 盲測（skill 快照當作業指令、匿名甲乙輪換盲評）診斷弱模型（Opus）跑 baransu 時相對強模型（Fable）的行為缺口，將缺口釘到 SKILL.md 指令縫並修補。

- **think（11 處）**：Stage D 頂層 ls 枚舉＋repo-root 搜尋紀律（缺席／計數宣稱不得來自子目錄搜尋）、立場前提重推導（Stage B 依賴的存在／計數前提於 Stage D 逐條以指令重推導、被推翻即改立場）、測試安全網盤點（覆蓋量在被改層而非下游 callee）、`(verified:)` 標籤須帶指令＋輸出引文且 prose 數字＝引文數字、計數名詞紀律（檔案／類別／呼叫點／測試案例各綁 pattern）、發出前掃描（五段每個數字重檢名詞是否仍符）。
- **analyze（5 處）**：goal Criteria 編號化（C1/C2…可機械追溯）、E2E 表每列一具名分支＋經 file:line 驗證的入口點、整合斷言禁同義反覆（「全綠／有回應」無具名值即拒）、邊界條件綁「製造該風險的 task」＋冗餘掃描、Stage 6 Agent 1 審查擴充為查可達性／業務語意／主流程完整（非僅錨點存在）。
- **成效**：think Opus 對 Fable 由懸殊差距收斂至同版對決近平手（探索完整性 2→8、決策密度反超）；analyze 測試質量六維全面提升。
- codex mirror 同步 regen。

## v2.7.0 (2026-07-06)

**/review 取得 domain 驗證能力**。plugin version 2.6.0 → 2.7.0（新視角屬功能新增，minor bump）。對「聲稱業務行為」的 target（測案集、業務 spec、聲稱狀態機行為的變更），/review 具備業務狀態可達性驗證：

- **review SKILL.md Stage 1.5 — Domain grounding**：target 聲稱業務行為時，dispatch 前先物化「狀態 × 事件 × 前置條件」轉移表；來源權威排序固定為 spec／上游狀態產生流程 **高於** 被測代碼；每列標注 `(verified: <source>)` 或 `(inferred: 未實查)`；來源不足時最多一輪 AskUserQuestion，仍不足則不派 domain-reviewer 且報告不得聲稱 domain 覆蓋（Hard stops 強制）。
- **第五視角 `agents/domain-reviewer.md`**：僅產出兩類 findings——F1 非自然情境點名（初始狀態無合法路徑可達，去留由人決定、不建議逕行刪除）、F2 覆蓋缺口清單（合法組合枚舉對照案例集）；雙重引用義務（轉移表列＋案例位置）、缺一自棄；與 quality-reviewer 的 dead-code reachability 明確分道。
- **Domain exception**：domain 激活不受 LOC tier 壓縮——≤100 LOC quick-pass 上限不會擠掉它，在 tier 選擇之外加派。
- **發行面同步**：CLAUDE.md agents 註解清單（Perspective 行）加入 domain-reviewer.md；版本 touchpoints 四處（plugin.json／marketplace.json／codex mirror manifest／codex-transfer 測試斷言）同步；新增 `tests/fixtures/domain-dryrun/` 迷你乾跑 fixture（一頁狀態機 spec＋7 測案含 2 個蓄意非法初始狀態＋乾跑結果）。
- codex mirror 同步 regen。

## v2.6.0 (2026-07-06)

**バランス 全面審計＋28 項修復掃除**。plugin version 2.5.21 → 2.6.0。36-agent ultracode 審計（18 審計員＋18 對抗驗證員）以「複雜度必須證明價值」為準繩檢視全部 14 skills＋agents＋_shared＋驗證基建，28 項 act 級發現由 15 個檔案所有權互斥的修復代理一次落地（net −264 行）：

- **移除 log-only 機制**：execute 的 Goal-Alignment Filter Metric 遙測（計數器穿四檔、無消費者）全數移除；book token-resolver 不再寫入不存在的 final-report.md；design Gen Mode Step 4 死 checkpoint（Stage 0 已注入、答案必被丟棄）整段刪除。
- **修復漂移矛盾**：learn brief-format.md（覆寫 vs .bak、TBD 公式）以 SKILL.md 為準單源化（132→54 行）；evolve safety-gates Gate 4 改為 Stage 3 唯一許可的 repo-mode 呼叫形式（原列損壞形式，可能假 gate 還原好變異）；book 文內驗證器聲明改為與 validate-output.ts 實際覆蓋一致（no-rgba／accent≤5% 非機械 gate）。
- **條件化 orchestration-interface 讀取**（review／execute／evolve／learn 四 skill 鏡像同一句式）：僅在 Workflow 驅動或 system-reminder 確認 ultracode 時讀取；預設互動路徑跳過、不寫 mode record。
- **強制 reference 讀取降級**：read 的 markitdown-guide／storage-protocol、learn 的 digest-frontmatter、health 的 baseline-principles 全文讀取改為 checklist-only＋失敗路徑指引;health Step 3 不再重跑 collect-data.sh 已執行的兩個腳本。
- **loop/harness 補洞**：write／book／read 新增 references/loop-pauses.md（含無頭預設）；review loop-pauses 補 Stage 1 target-pinning 列；analyze Stage 0.C resume 選項加【推薦】；loop-contract §1 評級理由裁剪＋§3 新增機器可查的 `LOOP_OUTCOME: ok | blocked | no-progress` 終行義務（取代 rc 信任——6/29 假綠的直接對策）＋§4 registry 與實存 loop-pauses 檔案同步（9 列）；全部 loop-pauses 前言統一為單行指回 §2。
- **hunt 記憶迴圈修復**：hunt-search.py 預設同時搜 `.claude/hunt-report/` 與 `.claude/archived/`（/ship 歸檔後案例仍可檢索），glob 涵蓋 /ship 撞名改名產生的 `*.md-{ts}`。
- **ship Step 1 detect 重寫**：python3/pathlib 單行取代裸 `find`＋unquoted word-splitting——在 zsh harness（不分詞、空 glob 中止整塊、find 可被劫持）下原寫法必然回空。
- **agents 瘦身**：architecture-reviewer §Language 53→9 行；impl-agent／review-agent 的 tdd.md 全文強制讀改為 `${CLAUDE_PLUGIN_ROOT}` 解析＋節選讀取（安裝版插件原路徑根本不存在）。
- **發行衛生**：刪除三個 *-workspace 評測殘骸（71 檔、~1.3M）及繞行它們的 skip 分支；transfer.py copy_aux 排除 node_modules（每週 regen 少拷 ~9.5M／1200 檔，鏡像瘦 73%）＋新增排除測試。
- **read**：Non-WSL2 CDP 死分支（依賴不存在的 port-3456 wrapper）刪除；四條搜尋 lane 候選選擇補【推薦】預設。
- 對照審計報告：`.claude/review/baransu-balance-audit-20260706.md`（28 act／65 advisory／8 dropped／91 keep）。

## v2.5.21 (2026-07-06)

**Fable-parity 真空點填補**。plugin version 2.5.20 → 2.5.21。把 Fable 5 的四個流程型思考模式編碼成步驟（非條款），讓 Sonnet/Opus 跑 baransu 時獲得接近 Fable 的行為紀律；步驟語言逐字改編官方遷移指南片段，intent-first 措辭（Fable 上無害重述、其他模型上是補強）。經 /think 五段計畫＋/review 雙視角（architecture＋quality）＋對抗輪複審後實作：

- **`_shared/tdd.md`**：§7.3 新增「gate 外的意外＝新 red」泛化段（含 §7.3 carve-out：gate 內結果依原表處理；一次 clean re-run 不算解釋）；新增 §7.5「宣告完成前：證據審計＋fresh-eyes 複核」（每個 claim 對到本 session tool-result；以陌生人視角重讀 diff＋重跑最窄驗證）；attribution 標注 §7.3 泛化段與 §7.5 為 baransu 原創、非上游衍生。
- **`_shared/output-journal.md`**：Required sections 新增第 4 項「學習記錄」——條件式（有 lesson 才寫、禁空段），格式 one lesson＋why it mattered，不記 repo/CLAUDE.md 已載明者。
- **`execute/references/output-formats.md`**：final-report Task 表新增「證據」欄，✅ 列必引 Pre-SWITCH green_proof 欄位（報告帶證據引用；守門仍在 Pre-SWITCH，Step 7 僅序列化）。
- review 修正折入：落點縮窄（execute SKILL.md 守門一字未動）、fable-patterns.md 不發行（對映表＋官方片段逐字引文留 `.claude/think/fable-parity-gaps.md` 附錄）、「對映表＝人工驗收 checklist、make test＝迴歸守護」術語校正。
- codex mirror 同步 regen。

## v2.5.20 (2026-07-03)

**health 新增「baseline working-principles coverage」檢查 + 通用理念改為 user scope**。plugin version 2.5.19 → 2.5.20；health skill 1.0.0 → 1.1.0。

- **health**：新增 `references/baseline-principles.md`（六條通用工作理念範本＋以「語意涵蓋」判定的檢查清單）。Structural lane 增設一段：比對 user scope（`~/.claude/CLAUDE.md` + rules）與專案 scope（`CLAUDE.md`/`AGENTS.md`）是否涵蓋這些理念，缺項按 tier 報 WARN／informational，經確認（INV-4）後從範本補上——通用原則寫 user scope、專案特定寫專案。定位為 advisory baseline，不會硬性 FAIL 或自動套用。
- **CLAUDE.md／AGENTS.md**：通用理念與風格（Think Before Coding／Simplicity First／Surgical Changes／Goal-Driven Execution／First Principles／Adversarial Review）自專案根 `CLAUDE.md` 上移至 user scope `~/.claude/CLAUDE.md`；專案端只留 バランス 身分理念（plugin-specific）。AGENTS.md 同步移除通用理念並修正 single-source 指向。
- codex mirror 同步 regen（含新 reference 與 SKILL.md 檢查段）。

## v2.5.19 (2026-07-03)

**全 skill 並行 evolve 一輪 sweep**。plugin version 2.5.18 → 2.5.19。承 v2.5.18 已完整棘輪的 think／review／execute，對其餘 11 支各跑一輪 `/evolve`（並行：14 mutator＋盲評，Opus）——每支經 structure gate＋**3/3 盲評全票**＋整體 make test 綠三重驗證後採納。全部為真缺陷修復而非文字打磨：

- **read**（d2）：圖片本地化誤用 initial slug 複製造成孤兒，搬到 Stage 3 用 final-slug，`./assets` 連結才解得開。
- **evolve**（d2）：Stage 6 not-kept 路徑補「遞增 no-progress 計數器」，補齊 Stage 7 N=3 收斂所依賴的計數生命週期。
- **book**（d5）：Red Lines 第 3 列理由與其正確做法欄自相矛盾（"超過 3 步" vs 上限 2 步/圖），對齊 SSOT。
- **learn**（d3）：`/write` 輸出缺 `**After:**` 標記時 fallback 為原文，不寫出空 digest。
- **write**（d3）：無關鍵詞的文件路徑路由到 Proofread（對齊 argument-hint），不再默默落回 Generate。
- **ship**（d3）：Step 5 補 `BRANCH_DELETE_FAILED` 明確狀態行＋手動復原指令。
- **health**（d3）：Step 1b MCP 探測本身跑不動時記 `live=unknown`，不誤報 server down。
- **codex-skill-transfer**（d3）：Step 1 補 no-match/marketplace-root 分支（transfer.py exit 2 不寫檔）。
- **analyze**（d3）：Stage 6 純措辭層未解發現記入 Stage 7 交接行，不靜默丟棄。
- **hunt**（d4）：Scope-Blast 閘「locking test」→「regression test」，四類 bug 都指對 artifact。
- **design**（d4）：Stage 0 插入位置由 hedge 改為確定性優先序。

think／review／execute 本輪 diagnostician 一致回報 **MARGINAL**（已收斂，殘餘為量測噪音或凍結欄位缺陷），正確 no-op。codex/ 鏡像經 `transfer.py` 重產（11 支同步）。

## v2.5.18 (2026-07-03)

**官方文件對標的全 skill 優化 rollup**。plugin version 2.5.17 → 2.5.18。以 2026 最新官方文件（code.claude.com skills／sub-agents／hooks／settings／plugins、docs.claude.com authoring best-practices、anthropics/skills spec v1.1、engineering blog）為基準，先展開 13 份官方來源的雙 brief（`.claude/learn/briefs/`），再經 `/think` 差距分析＋`/review` 三 perspective 審計（19 findings 全採納）產出 83 項優化計畫，逐批落地：

- **集合層（B1–B6 批次）**：14 條 description 全面第三人稱化（保觸發詞 byte-identical，總量 7,198→7,176 字元）；`verify-skills.py` 新增 5 項機制檢查（name==目錄名／無 XML tags／無保留字／per-skill desc+when_to_use ≤1536 硬檢查＋總量 advisory／plugin agents 禁 hooks·mcpServers·permissionMode），各附負向 fixture；`_shared/loop-contract.md` 補置頂 TOC；13 skill 補 `evals/` 觸發 routing fixture＋跨 skill routing 套件；6 skill 補 `references/loop-pauses.md` 一跳指標。
- **逐 skill 外科手術（14 commits）**：compaction-window 前移 load-bearing 段落、degrees-of-freedom 分級、引用深度攤平、referencing 檔案 TOC、術語一致化；`/ship` worktree 拆除鏈腳本化（`cleanup-worktree.sh`，argc/realpath/GUARD_REFUSED 防護＋fixture-repo shell test）；`/health` 三 inspector plugin-scoped 識別碼＋checker scripts 首獲 pytest 覆蓋；`/hunt` `hunt-search.py` 移入 `scripts/`＋pytest 釘現行行為。
- **`/evolve` 棘輪（think／review／execute）**：think 4 輪採納（89→~93.5，Evaluation 約束抽取閘＋裁決收束＋影響區塊證據紀律＋Step 0 soft-read 豁免）、review 3 輪（85→~90，pre-dispatch off-ramp＋/hunt·/read 路由＋mode-pin 重錨）、execute 5 輪（93→~94，error-miss fallback＋target_branch 釘定＋blocked-group merge 排除＋WIP-commit 閘＋TaskUpdate status 對映）；全部 3/3 盲評＋structure gate＋held-out 獨立層驗證，evolve 包落於 `.claude/evolve/`。
- codex/ 鏡像經 `transfer.py` 重產（think／review／execute／evolve 四支同步演化後內容）。
- **未竟**：11 支 skill 已過 Phase 5 優化但未進 evolve 棘輪（Fable 5 額度耗盡，execute r5 判評＋held-out 改於 Opus 完成）；13 項 behavior-semantic 變更與全面 description 格式重構延後為 `pending_findings`（見 `.claude/impl/`）。

## v2.5.17 (2026-07-02)

**Evidence-discipline transplant**。plugin version 2.5.16 → 2.5.17。從三個內建 skill（`/simplify`、`/verify`、`/code-review`）萃取反慣性紀律，就地改寫 16 處——`/review`（7 項：目標先落盤具體化、dispatcher==author 揭露、returned-set 收據、real-surface E2E 定義、direct-fix 條件式豁免）、`/analyze`（5 項：per-question verdicts、finding 錨點確認、修正後 clean-context 覆驗、`ls` 實測交付宣告、requirement↔test 覆蓋線）、`/execute`（4 項＋tdd.md §7.1 cosmetic 收斂為兩類：green_proof 落地 REQUIRE、條件式 direct-fix waiver、final-review 即跑證據、e2e_evidence 塊、off-goal 降級書面構造）。無新 stage／tier／工件，淨增趨近零。

### Notes

- codex/ 鏡像經 `transfer.py` 重產，補齊 v2.5.16 遞延的 `/design`／`/book` 內容轉譯與 v2.5.15 的 mechanism-necessity 段落（前次僅同步版本號）。

## v2.5.16 (2026-07-02)

**`/design` + `/book` 吸收 dataviz 色彩推理層，新增統計圖表類型**。plugin version 2.5.15 → 2.5.16。

### Added — 新增

- **`/book` 第 14 型「統計圖表」**：`svg-rendering-rules.md` §4.9/§4.10 由 13 型擴充為 14 型；同時修好一個既有、與本次無關的懸空引用（§4.9 原有 7 條指向 Candlestick／Waterfall／Donut／Bar／Line／Grouped Bar 等資料形狀的列從未接上任何 §4.10 參考檔），統一導向新的統計圖表類型。既有 13 型的判斷順序、視覺規格皆不受影響（既有型態優先）。
- **色彩距離驗證工具**：新增 `plugins/baransu/skills/_shared/scripts/color_distance.py`，獨立實作 Machado-Oliveira-Fernandes(2009) 色盲模擬 + CIE76 ΔE 計算，回傳建議而非阻斷判定；被 `/design`（設計期烘焙）與 `/book`（執行期驗證子集）共用。
- **`/design` 圖表分類色能力宣告**：`check.py` 新增獨立於 `schema:43` 的 `CHART_CAPABILITY` 版本層級（`--chart-cat-1`～`--chart-cat-6`）；preset/gen 流程新增宣告入口，宣告後 `tokens.css` 產出對應規範命名，未宣告時行為與現有完全一致。
- **色彩推理參考文件**：新增 `references/color-reasoning.md`，體例仿 `/write` 的 `writing-principles.md`（模型預設會犯的錯／為什麼錯／正確做法），涵蓋雙軸圖表、彩虹漸層、身份色無圖例等反面教材，僅統計圖表類型生成時讀取。
- **`perception-guide.md` 宣告感知單一 accent 例外**：Anti-Slop #8 新增容器範圍例外——已宣告能力的風格，統計圖表容器內的多色被放行，容器外仍受單一 accent 規則約束；未宣告或 `tokens.css` 缺失／格式錯誤時一律 fail-closed。

### Notes

- 紙／swiss／google-design 三個既有 preset 均未宣告此能力，回歸驗證確認行為零改變（`check.py` Check A-F、`validate-output.ts` GATE 結果皆 byte-for-byte 一致）。
- 測試從 83 條成長到 220 條（79 subtests），`make test` 全綠。
- **codex/ 樹本次僅同步版本號**（4 處：`plugin.json` ×2 + `marketplace.json` + `test_codex_skill_transfer.py` 硬編斷言），`/design`／`/book` SKILL.md 的內容尚未透過 `/codex-skill-transfer` 重新轉譯——下次動到 codex port 時需補跑。

## v2.5.15 (2026-06-25)

「機制必要性」原則 + loaded-context 自審慣性 gotchas。`/think` Stage E 與 `/review` Stage 6 新增「Mechanism necessity」段：新增機制前必須證明它在解決問題／推進目標，而非只留一個「我這裡失敗了」的 log；失敗路徑能跳過的規則不算預防。`/analyze` 新增 Gotchas 段（Option 2 同 session 交接違反 never-share-context）、`/execute` 新增 [loaded-orchestrator self-review trap] gotcha（驗證職能必須 fresh-context 隔離，orchestrator 不得自任）。雙樹同步。

## v2.5.14 (2026-06-23)

evolve 打磨 /design SKILL.md — gen 極端承諾軸補 extreme→value lookup table（dim4）+ 新增 named Design Invariants I1–I5 區塊（dim5）；雙樹同步。

## v2.5.13 (2026-06-23)

**`/design` Gen Mode 表現力升級 + `/book` 軟生成**。plugin version 2.5.12 → 2.5.13。雙樹（plugins/ + codex/）同步。

### Added — 新增

- **capability tokens（+5）併入 canonical，版本閘控**：`check.py` 拆 `BASE_TOKENS`(38) + `CAPABILITY_TOKENS`(5)（`--ease` / `--duration` / `--stagger-step` / `--font-display` / `--shadow-drama`）；Check B 改版本感知——無 `schema:` → 38 base、`schema: 43` → 38 base +5 capability。count 字串述為 `38(+5)`，version-pinned test 對 38 與 43 各斷言一次。
- **`/design` Gen Mode extreme-commitment 軸**：以單一「極端承諾」prompt（記憶點 + 承諾哪一個極端）取代中性強度滑桿；`極簡 minimal` 為平等極端而非預設安全值。所選極端同時驅動兩條衍生線——capability-token 值衍生 + DESIGN.md §9 expression-range 撰寫。
- **DESIGN.md §9 expression-range**：承諾的極端 / 空間原則 / 不對稱·重疊允許度 / 欄寬上限 / 強調色紀律，作為 `/book` 軟生成的軟範圍輸入。

### Changed — 變更

- **`/book` 軟生成 + validator 分層**：Stage 3 §3 由「固定 class 白名單」改為在 §9 表現範圍內**生成** section layout（§9 缺欄位則保守對稱 fallback）；硬地板（canonical token / no bare hex）不變，由 `validate-output.ts` 阻斷，軟範圍由 style-reviewer 評但不阻斷。Validator division of labor 明列 hard floor（阻斷）/ soft range（意見）兩層。

### Synced — 同步

- 雙樹（plugins/ + codex/）同步：8 個 canonical/asset 鏡像檔位元組一致；design / book SKILL.md 重放語意變更（保留 codex port marker：0.1.0-codex / AGENTS.md / ask-directly）。
- bump 四發行面 + version-pinned 硬編斷言（plugin.json ×2 + marketplace.json + CHANGELOG + test_codex_skill_transfer）。

## v2.5.12 (2026-06-23)

**`/design` + `/book` 美學與正確性修正**。plugin version 2.5.11 → 2.5.12。雙樹（plugins/ + codex/）同步。

### Fixed — 修正

- **`/book` Kami fallback golden-template 重寫**：從 v1.2 上游 token 名（`--parchment` / `--brand`…）改用 v1.3 canonical 名（`--paper` / `--accent`…，hex 不變），讓注入的 canonical `tokens.css` 能真正驅動配色。
- 同步修好該模板違反 skill 自身規範的三處：標題字重 700 → 500（Kami 不變量 #5）、h1 字級 28px → 38px（模組級數 hero）、正文行高 1.75 → 1.65（`/book` §3 禁用 ≥1.70）、figcaption 斜體移除（Kami 不變量 #10）。
- chrome 標籤（kicker / 編號 pill / meta / TOC / footer）從裸 `sans-serif` + `Arial` 改用 `var(--font-mono)` 印刷標籤調，去除襯線 preset 中的 generic-sans slop。A/B Playwright 截圖 + `validate-output.ts` GATE PASS 驗證。
- **canonical token 數量四處不一致修正**：全倉 `36` → `38`（以 `check.py` 的 `CANONICAL_TOKENS` 實際長度為準），同步修 `check.py` 註解的「19+ names」；Stage 0 inject 版本標記與 root `CLAUDE.md` 一併對齊。
- **`/design` SKILL.md 過時交叉引用修正**：移除「`check.py` legacy mode 被 `/book` validate-output.ts 在 GATE-F 呼叫」的不實描述（validator 自行實作 GATE-F prefix 檢查）。

### Changed — 變更

- 三支 `/book` golden-template（kami / swiss / gd）補上 `prefers-reduced-motion` 守門（既有 `scroll-behavior: smooth` + transitions 的無障礙缺口）。
- Kami `tokens.css` 間距註解不再宣稱嚴格「4pt grid」（3/5/10 為刻意手調步階）。

## v2.5.11 (2026-06-22)

**README 精簡 + 移除 LICENSE**。plugin version 2.5.10 → 2.5.11。

### Changed — 變更

- README 改寫為極簡版：核心理念錨點表 + 14 skill 用途簡表 + 安裝；安裝 URL 改為 GitHub 新家。
- `/book` 介紹移除「Kami」字樣。

### Removed — 移除

- 移除 `LICENSE` 檔與 `plugin.json` / codex 鏡像的 `"license"` 欄位（repo 移至公開 GitHub 後不再標註授權）。

## v2.5.10 (2026-06-22)

**reference ToC sweep + book 可達性修補**。plugin version 2.5.9 → 2.5.10。

依官方最佳實踐(/learn 摘要 + 並行稽核)落實 reference hygiene:官方規則要求 >100 行的 reference 檔須有目錄(ToC)。

### Changed — 變更

- **33 個 >100 行 reference 檔補上「章節層級(`##`)」ToC**(9 個 skill:book/codex-skill-transfer/design/execute/learn/read/write)。採只列 `##` 章節,避免如 slide-checklist 把 70 個小標題全列成雜訊(只列 19 章節)。
- **book diagram-types 可達性修補**:`svg-rendering-rules.md` 的 diagram 查表(§4.9/§4.10)原落在第 167 行、超過 `head -100` 範圍;新增的頂端 ToC 已把 §4.9/§4.10 列在前 12 行內,並在 book SKILL.md 補一行指標直指 `references/diagram-types/`。保留巢狀(just-in-time disclosure),不搬檔。
- **排除 3 個 preset `DESIGN.md` 範本檔**(google-design/swiss/紙):它們會被原封不動複製到使用者專案,加 ToC 會污染產出。
- codex 鏡像隨之重產同步。

## v2.5.9 (2026-06-23)

**每日 cron 自動演化 round 7:護欄下 7 達標、gate 後採納 6/14**。plugin version 2.5.8 → 2.5.9。

由 4:07 AM cron(standing authorization)非互動觸發,收斂護欄(margin≥2.0 + body<480)。14 skill 全評估,7 個過 blind margin 門檻,其中 learn 在 `make test` 結構 gate 被擋下(mutation 在 Outcome Contract 前插入 Invariants H2,違反「Outcome Contract 必為首個 H2」紅線),依「gate 為仲裁」原則退回 base,最終採納 6 個。採納曲線 14→14→14→5→6→2→6。

### Changed — 變更

- **採納 6 skill(margin≥2.0、blind 3/3、過 make test)**:analyze(Dim 6 把覆寫重建的刪除範圍釘成單一計算路徑 + path-scope guard)、book(Dim 4 把元件選用改成 data-shape→component 確定判準)、design(Dim 2 把 Gen Step 1.5 移到 Step 1 後消除前向引用)、hunt、read、write。
- **gate 退回 1 skill**:learn(blind 過關但破壞首個-H2 結構紅線,退回 base)。
- **保留 7 skill(收斂)**:codex-skill-transfer(非全票)、evolve/execute/health/review/think margin 1、ship margin 0.9。皆未改動。
- codex 鏡像隨採納重產同步。
- 本輪後每日 cron 轉為每週 /schedule 雲端例行。

## v2.5.8 (2026-06-22)

**每日 cron 自動演化 round 6:收斂明顯,僅採納 2/14**。plugin version 2.5.7 → 2.5.8。

由 4:07 AM cron(standing authorization)非互動觸發,收斂護欄(margin≥2.0 + body<480)。14 skill 全評估,僅 2 個達標採納,12 個保留(收斂)。採納曲線 14→14→14→5→6→2,趨近收斂。

### Changed — 變更

- **採納 2 skill(margin≥2.0、blind 3/3)**:analyze(Actionable-Specificity 把 Stage 6「findings 仍 substantial」hedge 釘成 wording/structural 二分判準)、hunt(單變量精修)。
- **保留 12 skill(收斂)**:book/codex-skill-transfer/design/evolve/execute/health/review/write margin 1、think 1.5;learn/read/ship 非全票。皆未改動。
- codex 鏡像隨採納重產同步。

## v2.5.7 (2026-06-21)

**每日 cron 自動演化 round 5:護欄下採納 6/14**。plugin version 2.5.6 → 2.5.7。

由 4:07 AM cron(standing authorization)非互動觸發,套用收斂護欄(margin≥2.0 + body<480)。14 skill 全評估,6 個達標採納,8 個保留(收斂)。

### Changed — 變更

- **採納 6 skill(margin≥2.0、blind 3/3)**:analyze(Failure-Mode-Encoding 補 Stage 0.C 目錄已存在 if-then,margin 5)、codex-skill-transfer(Actionable-Specificity 把報告 hedge 改為 MUST append Next-port follow-ups)、evolve(High-Risk-Action 把 real-exec 破壞性樣式改成硬性 if-then 禁止)、execute / review / write(各 1 個單變量精修)。
- **保留 8 skill(收斂)**:book/design/health/learn/ship/think margin 1;hunt、read 非全票。皆未改動。
- codex 鏡像隨採納重產同步。

## v2.5.6 (2026-06-20)

**每日 cron 自動演化 round 4:收斂護欄首次生效,只採納 5/14**。plugin version 2.5.5 → 2.5.6。

由 4:07 AM cron(standing authorization)非互動觸發。本輪起套用 v2.5.5 新增的收斂護欄(`scripts/nightly-evolve.workflow.js`:margin≥2.0 + body<480 行),14 skill 全評估,僅 5 個達標自動採納,9 個因邊際過小或非全票而保留(收斂)。

### Changed — 變更

- **採納 5 skill(margin≥2.0、blind 3/3)**:codex-skill-transfer(Trigger-Clarity 補 reverse-port not-for)、evolve(Actionable-Specificity 把 3/3 收緊條件釘到 Stage 4 real-exec 標籤)、learn / think / write(各 1 個單變量精修,多為原地改寫)。
- **保留 9 skill(收斂)**:book(margin 1.5)、execute(1.5)、design/health/hunt/review(1.0)、ship(0.7)邊際過小;analyze、read 非全票(2/3)。皆未採納、未改動。
- codex 鏡像隨採納重產同步。

## v2.5.5 (2026-06-19)

**每日 cron 自動演化 round 3:全 14 skill 結構軸再精修(standing-auth 自動採納)**。plugin version 2.5.4 → 2.5.5。

由 4:07 AM cron(standing authorization)非互動觸發;全 14 skill 經盲評 **3/3** 自動採納,結構閘 + `make test` 全綠後上 main。本輪無 API 中斷,一次跑完。

### Changed — 變更

- **全 14 skill 結構軸(dims 1–6)第三輪演化**(blind 3/3),各 1 個單變量改動:Failure-Mode-Encoding 補 if-then(analyze 補審查員未完成路徑、codex-skill-transfer 補 mode 誤判路徑)、Stage-Coherence 補 stage 分隔(book)、High-Risk-Action 把 rm -rf 目標後綴釘死(design)等。
- codex 鏡像隨之重產同步。

## v2.5.4 (2026-06-18)

**每日 cron 自動演化 round 2:全 14 skill 結構軸再精修(standing-auth 自動採納)**。plugin version 2.5.3 → 2.5.4。

由 4:07 AM cron(standing authorization)非互動觸發 evolve→codex→ship sweep;全 14 skill 經盲評 **3/3** 自動採納,結構閘 + `make test` 全綠後上 main。

### Changed — 變更

- **全 14 skill 結構軸(dims 1–6)第二輪演化**(blind 3/3):Trigger-Clarity 補 not-for 邊界(analyze/design/execute/hunt/…)、Failure-Mode-Encoding 補 if-then 復原(codex-skill-transfer/think/…)、High-Risk-Action 補 mutation-isolation 不變式(evolve)、Actionable-Specificity 釘死門檻規則(book/…)等,各 1 個單變量改動。
- codex 鏡像隨之重產同步。

### Notes

- hunt/book/think 首輪 mutate 遇暫時性 API 連線中斷掉出,經單獨 retry workflow 補齊,最終 14/14 全數採納。

## v2.5.3 (2026-06-17)

**`/evolve` 非互動 standing-authorization 自動採納 + 全 14 skill 結構軸演化精修**。plugin version 2.5.2 → 2.5.3。

### Added — 新增

1. **standing-authorization 自動採納(Loop/Ultracode 不中途停)**:`/evolve` Stage 6 採納仍是 Authorization PAUSE,但新增與 `/ship` push 一致的 carve-out —— 當 driving context(loop/cron 提示或核准計畫)明確授權採納/整條 evolve→ship 時,非互動執行可自動採納,但僅限通過**全部** Gate-1 前置條件的變更:結構閘通過、盲評門檻收緊為 **3/3**(非互動無人兜底)、保留 file-level snapshot、`log.md` 記 `decision: standing-auth auto-adopt`;任一條件未過即還原、不寫回。`make test` 為下游(/ship)的最終 go/no-go。互動式 session 維持硬停不變;無授權的裸 `/ultracode` 仍硬停 `needs input`。
2. **loop-contract §2 標準授權語意**:Authorization PAUSE 重述為「不得以預設替代滿足;授權可由互動當下給出,或由 driving context 預先記錄的 standing authorization 給出(僅限該 skill 的 `loop-pauses.md` 標記為 standing-authorizable 者)」。standing authorization 屬「預先的明確人類授權」,非 default substitution。

### Changed — 變更

- **全 14 skill 結構軸(dims 1–6)演化精修**(blind panel 3/3 採納):Trigger Clarity 補 not-for 邊界 ×7(book/evolve/learn/read/review/ship/think)、High-Risk Action Discipline 補 rm/git 破壞性守衛 ×4(design/execute/health/hunt)、Actionable Specificity 把未錨定 hedge 改為釘死規則 ×3(analyze/codex-skill-transfer/write)。
- `evolve/references/{safety-gates,loop-pauses}.md`、`evolve/SKILL.md` Stage 6 + Constraints:同步 standing-authorization 採納語意。

### Notes

- codex 鏡像待 `/codex-skill-transfer` 重產同步。

## v2.5.2 (2026-06-17)

**`/evolve` 升級 ultracode 支援:`assist` → `overlap`,並補齊 loop 支援行為**。plugin version 2.5.1 → 2.5.2。

### Added — 新增

1. **`/evolve` ultracode=overlap 雙模 orchestration interface**:新增 `evolve/references/orchestration-interface.md`,為 Stage 5 三盲評委定義雙 adapter(現行平行 Task ↔ thin Workflow),回傳同構 `{better, strict_improvement, per_dimension_deltas}` 投票;Stage 5 計票與 Stage 6 keep/restore 不感知模式。depth 不變句逐 adapter 重述(評委與 diagnostician 為 depth-1 leaf,不呼叫 skill、不再派子代)。SKILL.md 新增 ≤10 行 pointer 區塊與 Stage 0 mode pinning 指引。
2. **`/evolve` loop 支援行為**:新增 `/evolve` 的 PAUSE 分類 —— Stage 0.4 無 benchmark 為 Input PAUSE(預設走 structure-axis-only),Stage 6 採納寫回為 **Authorization PAUSE**(硬停、回報 `needs input`、絕不自動寫回)。評級由 `assist/assisted` 改為 `overlap/drivable`(與 /review 同型:採納硬停與 drivability 並存)。

### Changed — 變更

- **`loop-contract.md §4` 重構為 per-skill registry(locality)**:各 skill 的 PAUSE 分類表自 `_shared/loop-contract.md` 搬到各自的 `references/loop-pauses.md`(review/execute/learn/ship/evolve/think),§4 改為指向各檔的 registry;§1–§3(vocabulary、PAUSE semantics、hard stops)仍共用。改一個 skill 的互動點只動該 skill 的檔,不再動共用檔。
- `tests/skills/test-automation-annotation.sh`:evolve 重評級為 `overlap/drivable`。
- `tests/skills/test-orchestration-interface.sh`:測試迴圈加入 evolve(T1–T4 全綠)。

### Notes

- codex 鏡像待 `/codex-skill-transfer` 重產同步(orchestration-interface、loop-contract、SKILL.md 與版本號)。

## v2.5.1 (2026-06-17)

**`/write` 補 `argument-hint` 參數提示(輸入 `/write` 時顯示可打參數)**。plugin version 2.5.0 → 2.5.1。

### Added — 新增

1. **`/write` frontmatter 補 `argument-hint` + `user-invocable: true`**:對齊 book/design/read/learn/execute 慣例(可呼叫 skill 成對宣告兩欄位)。hint 把參數直接對應模式以利記憶:`[zh|en] [voice="…"] <text=潤稿 | prompt=生成 | file/path=校對>`。屬官方 doc 複檢列出的 MINOR 後續之一(discoverability)。

### Notes

- codex 鏡像同步重產:`argument-hint` 隨之進 codex 版 `/write`;版本同步 2.5.1。

## v2.5.0 (2026-06-17)

**`/write` 新增 Proofread（校對）模式,並對擴充後的 `/write` 跑 `/evolve` 棘輪(結構軸 84→94,3 輪皆 3/3 盲評採納)**。plugin version 2.4.5 → 2.5.0。

### Added — 新增

1. **`/write` Proofread 模式(第三模式)**:Stage 1 由 Refine/Generate 二分擴為三分(優先序 Proofread > Refine > Generate)。新增 Stage 4 校對路徑 —— 逐頁取得來源(PDF 多視窗以絕對頁碼累積、掃描頁讀不到標「無法擷取」不靜默丟棄)→ 六類作者關注收斂成三個固定 `錯誤類型`(錯別字／用語不妥／語句不通順,含台灣商業用語透鏡)→ 六欄 findings(頁數／段落上下文／原文內容／錯誤類型／建議修正／修改原因)→ 沿用 `/book` 的 Kami 設計 token 自包含渲染成 `.claude/write/錯字修改.html`。frontmatter description / 觸發詞 / Outcome Contract / Constraints 同步擴充。

### Design notes

- **不走 `/book` pipeline**:校對錯字表屬「分析輸出」,違反 `/book`「禁把 Claude 分析寫進 HTML」紅線,且無 SVG 會被 `validate-output.ts` 品質閘擋。故直接渲染、沿用 tokens.css(缺失時用乾淨現代 fallback 調色盤),不跑 SVG 閘。
- **overwrite 守衛**:`錯字修改.html` 已存在 → 改寫 `-N` 後綴並回報,杜絕覆寫前一份報告。

### `/evolve` dogfood

- 對加完功能的 `/write` 跑棘輪:R1 dim9 Robustness(PDF 多視窗契約 82→88)、R2 dim1 Trigger Clarity(frontmatter not-for 邊界 88→90)、R3 dim3/6 Failure-Mode/High-Risk(overwrite 守衛 90→94),三輪皆 3/3 盲評 strict improvement、0 回滾、結構閘全過。效能軸 dim7–9 因無 benchmark 全程標 advisory／offline,held-out 標 `no-benchmark`(誠實標,非假設)。演化包落於 `.claude/evolve/write/`(report / results.tsv / log / held-out / convergence.svg / card.png)。
- **Claude Code 官方 doc 複檢**:剔除兩條誤判(description 未超 1,536 上限;`/write` 雙語規則內容受 English-body 豁免);列出可採後續(rule sets / proofread taxonomy 外移 references/、proofread-template 統一 token、`argument-hint`、路徑 fork 約束) —— 本次未做,留待後續。

### Notes

- codex 鏡像本次僅同步版本號(2.5.0),內容未重產(Proofread 模式未反映進 codex 版);如需 codex 端對齊請另跑 `/codex-skill-transfer`。

## v2.4.5 (2026-06-16)

**`/evolve` dogfood:用 /evolve 演化 /evolve 自己,2 輪盲評棘輪(結構軸 44→48)**。plugin version 2.4.4 → 2.4.5。

### Fixed — 修正

1. **Stage 3 結構閘對「有 references/ 的 skill」假性失敗(dim 3,headroom 最大)**:原指令 `verify-skills.py <skill_dir>` 會被 verify-skills 當成 skills-root 迭代,把 skill 自己的 `references/`/`scripts/` 子目錄誤掃成 skill → 噴 `references: 缺 SKILL.md` exit 1。這讓 /evolve 對 book/design/evolve **自己** 等含 references/ 的 skill 整輪 produce nothing。改為 whole-repo 無參數模式 + 寫明陷阱。3 位盲評委各自 trace `verify-skills.py` + test fixture 實證確認。

2. **Stage 7 成果卡未持久化(dim 4)**:原「render the result card through /book」沒明說落地路徑,`成果卡`/`card.png`/「透過 /book」三方命名不一致 —— 導致上一輪 evolve 只送出暫存 PNG、沒進演化包。釘死所有工件落地 `.claude/evolve/<slug>/`、成果卡 = `card.png`、補 `convergence.svg` 語意。

### Notes

- 兩輪皆 3/3 盲評 strict improvement、0 revert、dry-run 0%;held-out 獨立層驗證 generalization pass(`硬證據`):dim-3 修正泛化到 book/design,dim-4 工件釘定 target-agnostic。
- 演化包(含本次 dogfood 正確落地的 `card.png`)落於 `.claude/evolve/evolve/`。
- 開放後續(非回歸):`held-out.md` inline 路徑、`safety-gates.md` Gate 4 殘留 `<skill_dir>` 字樣。

## v2.4.4 (2026-06-16)

**`/ship` 能力演化（由真實收尾摩擦驅動，先 `/learn` 業界做法再改）**。plugin version 2.4.3 → 2.4.4。

### Changed — 變更

1. **歸檔範圍擴大（白名單）**：Step 1/2 歸檔來源由 `{tmp,analyze,execute,think}` 擴為涵蓋全部 baransu 工作目錄 `{tmp,analyze,execute,think,design,hunt-report,evolve,review}`；`read/learn/book` 為保留產物不歸檔；Claude Code 基礎設施（worktrees/projects/jobs/settings…）以白名單機制天然不受影響。

2. **可指定 ship 到目標分支**：新增 Step 0 解析 `/ship <branch>`／`/ship 到 <branch>`／`/ship to <branch>`。land-on-target 模式（GitHub Flow 心智）將當前 worktree 分支 `merge --no-ff` 進目標分支再 push 目標；**絕不 `--force`**，遇 non-fast-forward 先 `pull --no-rebase` 再推一次。

3. **worktree 退出順化 + 安全閘**：Step 5 改為 **ancestor 安全閘** —— 拆除前以 `git merge-base --is-ancestor <branch> <safe-ref>`（Mode B 對 `origin/<target>`、Mode A 對 `origin/<branch>`）確認工作已落地才拆；精準，不像 branch-tip 啟發式會誤拒已合併分支，也不會默默丟棄未合併工作。移除採三段 fallback（`remove` → `--force` → `rm -rf` + `prune`），`branch -D` 保留。

4. **`/evolve` 棘輪打磨(dim 5 Constraint Explicitness 6→8)**：跑一輪盲評棘輪,診斷出最弱維為「紅線散在各 step、未具名」,單變數加入具名 `## Invariants` 區塊(INV-1..5),把 allowlist-only、source-emptied-not-deleted、never-force-push、ancestor-gate-before-teardown、`-D`-not-`-d` 提升為綁定 enforcing step 的具名約束。3/3 盲評一致 strict improvement、結構閘過、held-out 獨立驗證 generalization pass(且誠實標出 dim5 7/8 —— 還缺一條 INV-6「目標分支須先存在、不可 force-create」)。

5. **發行**:CLAUDE.md skills 表為通用敘述故 baseline 無需變動;codex 鏡像重產、版本同步 2.4.4。

> 設計依據:`/learn` 研究 brief 落於 `.claude/learn/briefs/ship-release-automation-git-branching-strategies.md`;`/evolve` 演化包落於 `.claude/evolve/ship/`(report / results.tsv / held-out / log)。

## v2.4.3 (2026-06-16)

**English-body 慣例落實**：把「agent-facing 內文一律英文、僅使用者輸出與 `/write` 內容留中文」這條從一句宣告，擴寫成可執行慣例並全面落實。plugin version 2.4.2 → 2.4.3。

### Changed — 變更

1. **Codify 慣例**：`CLAUDE.md` 的 English-body 條款由單句擴寫成完整定義 —— 涵蓋 `SKILL.md` body、`references/`、`skills/_shared/`、`rules/`、`agents/` system prompt；明列四類合法中文豁免（使用者輸出 / 觸發詞與 routing cue / 示範產物 / `/write` 雙語寫作內容）。

2. **全面英文化（ultracode 多 agent 盤點 + 翻譯）**：先以 17-agent 盤點量化違規（約 1,322 行 agent-facing 中文指令散文），再以 30-agent 逐檔翻譯 **51 個檔、約 2,180 行** 指令散文為英文，逐字保留 frontmatter 觸發詞、使用者輸出字串、grep anchor（design E1–E4、check.py 偵測字面、正則/CSS/code）、範例產物與 `/write` 寫作內容。熱點：`_shared/tdd.md`、`design/SKILL.md` 與五個 reference、`book/SKILL.md` 與全 reference 群（含 13 個 diagram-type）、Execute 家族 8 個 agent prompt、`codex-skill-transfer/references/CODEX_PORT_PLAN.md`、`rules/anti-patterns.md`。`evolve / read / ship` 原本 body 軸即乾淨。

3. **Gate 同步**：翻譯後對齊四處被語言耦合的測試錨點 —— `test_tdd_trigger.sh` 的被動引用語句改抓英文、`test-automation-annotation.sh` 的 loop-mode 預設句改抓 `default`（原抓 `預設`）、`tdd.md §8` 引用表改記英文句、`render-design-html.md` 的「編輯級」改譯 `editorial-tier`（避開 verify-skills 被裁名稱 `grade` 殘留掃描）、design SKILL.md 廢除目錄說明句補回 `removed/deprecated` 標記。`make test` 全綠。

4. **Codex 鏡像重產**：49 檔同步為英文鏡像，版本同步 2.4.3。

**`/book` + `/design` 達爾文式 10 輪盲評演化打磨**，plugin version 2.4.1 → 2.4.2：

### Changed — 變更

1. **/book — 10 輪棘輪（69.6→82.6；最終獨立複評 66→89。20/20 輪 keep、每輪 3/3 盲評、0 revert）**：
   - 新增 `## Red Lines（不要做什麼）` 反模式表（🛑 + 理據錨點 + 正確做法 + 權威 reference）。
   - `references/perception-guide.md`：新增 Output Anti-Slop Blacklist（8 條 grep 可驗）+ Quantified Type Scale 量化字級表 + Kami 行高禁區/單一 accent ≤5%/暖灰限定。
   - `references/slide-synthesis.md`：新增投影片字級/限高硬規則（vw/vh 雙約束 Y≥X×1.6）；SKILL.md render-time 🔴 GATE 把反 slop/字級規則由條件式升為 render 前必載；Stage 4 品質閘失敗改三段式「觸發/一線修復/兜底」。
   - `references/svg-rendering-rules.md`：修 13 型選型表 status 事實漂移，改為可 grep 二值驗證。
2. **/design — 10 輪棘輪（59.5→83.7；最終獨立複評 52→82。20/20 輪 keep、每輪 3/3 盲評、0 revert）**：
   - 新增 Decision checkpoint map + 三處行內 🔴 GATE/CHECKPOINT 顯性標記。
   - 新增 Anti-patterns 專章（5 條 ❌X→because Y→✅Z）。
   - `references/render-design-html.md`：落 Kami 編輯級排版硬規則 + E1–E4 grep 自查；`slide-checklist.md` 現象→根因→做法 fallback 正式 wire；`slide-image-prompts.md` 補 guizang P0-A-04 大字雙約束。
   - reference-honesty 修正：把假稱可跑的 script 改標 proposed 並指向真實 validator。
3. **codex 鏡像同步重產**：`/codex-skill-transfer` plugin mode 重產 book/design 鏡像（10 檔），三發行面 version 同步 2.4.2。

### 方法

達爾文式（alchaincyf/darwin-skill）：固定 9 維適應度標準 + 5 設計參考（Kami / diagram-design / guizang-ppt / huashu-design / guizang-social-card）+ 官方 Agent Skills 最佳實踐。每輪全新獨立評委盲評、不吸收前次、棘輪只進不退（嚴格進步 + `verify-skills` exit 0 + 體積 ≤150% 才 keep）。零新增檔、HTML 模板未手改、不變量全守。

### SemVer 註

patch：純改善既有 skill 的指令撰寫與產出品質，未改 skill 對外契約/功能，未新增 skill。

## v2.4.1 (2026-06-15)

**`/baransu:evolve` 自我演化三輪精修 + codex 鏡像補產**，plugin version 2.4.0 → 2.4.1：

### Changed — 變更

1. **evolve SKILL.md 三輪自演化（dogfood，皆盲評 3/3 採納）**：
   - R1 — dim3 失敗模式編碼 6→7：Stage 0.4 補上「無 benchmark / 使用者拒絕」的顯式 if-then 復原分支（只跑結構軸、硬標 dims 7–9 為 `no-benchmark`、跳過 held-out、禁靜默假裝已測效）。
   - R2 — dim4 可執行具體性 7→8：Stage 7 把未定值的 round cap 釘成 `R=6 total rounds`（與 `N=3` 對齊）。
   - R3（使用者直接回饋）— dim8 輸出保真：收尾摘要與成果卡文案強制先過 `/write` 寫成可讀白話，成果卡強制走 `/book` 渲染（禁手工拼 HTML）；`references/output-contract.md` 新增「Human-readable delivery」節。
2. **codex 鏡像全量重產**：`/codex-skill-transfer` plugin mode 重產 `codex/`，`evolve`（SKILL.md + 4 references + `evolve-diagnostician`/`evolve-judge` agent stub）正式進鏡像；三發行面 version 同步 2.4.1。

### SemVer 註

採 patch（2.4.0 → 2.4.1）：evolve skill body 精修 + 鏡像同步，無新 skill、向後相容。

## v2.4.0 (2026-06-15)

**新增第 14 個治理 skill `/baransu:evolve`（skill 演化器）**，純擴增（技能上限 13 → 14），plugin version 2.3.0 → 2.4.0：

### Added — 新增

1. **`/evolve` skill**：像訓練模型一樣優化一份 SKILL.md。固定 9 維 rubric 當選擇環境，跑只能向前轉的棘輪——獨立 diagnostician 挑最弱一維、單變數 mutation、3 個全新盲評委（中性命名、奇偶換位）≥2/3 判嚴格進步才採納、否則還原檔案級快照；連續 N=3 輪無進步收斂。含 `SKILL.md` + 4 references（`rubric-9dim` 選擇環境 / `safety-gates` 四道紅線 / `output-contract` / `provenance` 淨室）。
2. **2 個 perspective agent**：`evolve-diagnostician`（挑最弱維、只診斷不改寫）、`evolve-judge`（盲評嚴格進步，subagent depth=1）。
3. **雙軸評估與安全閘**：結構軸（9 維 rubric 靜態）+ 效果軸（real-exec 經信任+能力雙閘，否則 offline-同源重演）；held-out 加獨立層驗證防 rubric 過擬合；採納寫入釘 Authorization PAUSE（任何驅動不可跳）；回滾用檔案級 snapshot，禁 `git reset --hard` / `stash` / `clean` / `checkout`。
4. **E2E fixture**：`tests/fixtures/weak-skill/`。

### Changed — 變更

1. **技能上限 13 → 14**：同步更新 `scripts/verify-skills.py`（`EXPECTED_SKILL_COUNT` + docstring）、`tests/scripts/test_verify_skills.py`、三支 shell gate（`test-claude-md-skills-table.sh` / `test-distribution-metadata.sh` / `test-automation-annotation.sh`）、`tests/integration/claude-md-skills-baseline.txt`、`CLAUDE.md`（ceiling 句改述為「14 is the skill-count ceiling」）、`AGENTS.md`、`README.md`，以及三發行面 description（`plugin.json` / `marketplace.json` / codex `.codex-plugin/plugin.json`，皆 fourteen / 2.4.0）。

### SemVer 註

採 minor（2.3.0 → 2.4.0）：新增一個功能級 skill，向後相容。

### 建置全程

經 `/think → /review → /analyze → /execute` 全管線（兩次方向轉向：外掛式→catalog、裁撤→純擴增）；review 補抓 AGENTS.md 漏網觸點；E2E diagnostician smoke 並驅動一處 rubric 改進（dim6 vacuous-compliance 計分）。`make test` 全綠。

## v2.3.0 (2026-06-15)

**`/codex-skill-transfer` Codex Port 施工圖落地**：把 Claude→Codex 轉換從「API 對映」升級為「對抗模型慣性的配重保留」，skill metadata version 0.9.0 → 0.10.0：

### Added — 新增

1. **Capability 降級表**：`transfer.py` 新增 capability registry，每個 Claude 能力 token 對應 Codex 執行強度、替代策略、對抗的模型慣性強度、Tier 與加權風險；transfer report 新增 `Capability 降級風險 (weighted by model inertia)` 區塊。
2. **Codex Port 施工圖**：新增 `references/CODEX_PORT_PLAN.md`，明確定義「牙齒搬家，而不是降級」原則：強慣性 × 軟提示不得只靠 prompt，必須搬到 artifact gate、phase split、sandbox/approval gate 或獨立 session artifact。
3. **skill-specific adapter 注入**：Codex mirror 的 `/think`、`/review`、`/health`、`/execute` 會自動注入 adapter note，將高風險降級從報告提示變成 runtime 可見流程。

### Changed — 變更

1. **`/think` AskUserQuestion 搬牙**：不再降成一般文字詢問；Codex 版要求 Phase 1 只產對焦問題並停止，Phase 2 必須有 `alignment.md` 才能產出五段計畫。
2. **`/review` / `/health` 隔離驗證**：Codex 版要求先跑或查 `codex-isolation-probe.md`，若 subagent context 不夠乾淨，改以獨立 invocation/session 產 artifact 後再彙整，避免同 context 連續提問假裝多視角。
3. **`/execute` machine gate 與 durable state**：紅綠判定明確要求真實 test runner exit code；`TaskCreate` / `TaskUpdate` / `TaskGet` / `TaskList` / `TaskOutput` / `TaskStop` 改寫為 `task-map.md` durable source of truth，`update_plan` 僅是顯示層。
4. **AskUser 與 SendUserFile 分級**：`AskUserQuestion` 依 skill 分成 `/think` artifact gate、`/analyze`/`/review` authorization PAUSE、`/hunt` input gate、`/read`/`/book`/`/design` selection/cosmetic；`SendUserFile` 降成「寫檔並列絕對路徑」，列為低風險 delivery convenience。

### Added — 測試

- 擴充 `tests/scripts/test_codex_skill_transfer.py`，覆蓋 capability report 排序、`/think` alignment artifact gate、cosmetic AskUser 降級、`/execute` machine gate/task-map adapter、`SendUserFile` path delivery、reference scan。

### Internal

- codex/ 鏡像同步重產。

### SemVer 註

採 minor（2.2.4 → 2.3.0）：Codex port 的 runtime-facing skill body 與 transfer report 行為新增高風險 gate adapter，屬於功能級增強。

## v2.2.4 (2026-06-15)

**`/codex-skill-transfer` Codex subagent 對齊強化**（對照 2026-06-15 官方 Codex manual：Agent Skills、Build plugins、Subagents、MCP、sandbox/approval），skill metadata version 0.8.0 → 0.9.0：

### Changed — 變更

1. **多階段 subagent wording 改寫補完**：Codex mirror 不再保留 Claude `parallel Tasks` / `clean Task contexts` / `via Task` / `Dispatch **review-agent**` 等高頻語彙；轉為明確 `Spawn ... Codex subagents` wording，符合 Codex「明確要求才 spawn subagent」語意。
2. **Task 狀態面保留為 task-tracking contract**：`TaskCreate` / `TaskUpdate` / `Task Tool ID` 不再被模糊改成一般內部記憶，轉為 task-tracking record / task state wording；保留 `/execute` 的 task-map、blocked/cascade-blocked、failure_count、green-proof gate 等主 orchestrator contract。
3. **agent TOML stub 對齊官方欄位**：custom agent stubs 改為「預設繼承 parent session」語意，模型範例更新為 `gpt-5.5`（重任務）/ `gpt-5.4-mini`（輕量讀取掃描），reasoning effort 列 `minimal | low | medium | high | xhigh`，補 `.codex/agents/` project-scoped 路徑與 `skills.config` 註解。
4. **stub sandbox/approval 提醒**：依 Claude `tools:` 分辨 read-only 與 Write/Edit/Bash 類 agent，分別提示可考慮 read-only sandbox 或需人工確認 workspace-write 與 approval policy；仍不自動寫入使用者 `~/.codex/agents/`。
5. **reference scan 擴充**：references 仍不自動改寫，但現在會 flag `parallel Tasks`、`clean Task contexts`、`via Task`、`TaskCreate`、`TaskUpdate`、`Dispatch **...**`、`Workflow primitives` 等 Claude orchestration token，讓手動檢視面更完整。

### Added — 測試

- 新增 `tests/scripts/test_codex_skill_transfer.py`，直接鎖住 body rewrite、description rewrite、agent stub shape/sandbox hint、reference scan 四組行為。

### Internal

- codex/ 鏡像同步重產。

### SemVer 註

採 patch（2.2.3 → 2.2.4）：強化既有轉換器輸出與報告精度，無指令介面破壞；Codex 端行為更接近官方 subagent 模型。

## v2.2.3 (2026-06-11)

**Automation 語彙正式定義**：

### Fixed — 修正

1. **`ultracode=` / `loop=` 三值語彙落點**：`overlap`（自有多代理派遣、出貨 orchestration-interface.md 雙 adapter）/ `assist`（無 adapter、body 提示句標記可加速段）/ `neutral`（正交），與 `drivable` / `assisted` / `not-drivable` 的定義此前散落於 gate 期望表與各 body 提示句，無單一定義點——現正式寫入 `_shared/loop-contract.md` §1（Automation 行的讀取觸發已指向該檔，語彙隨之可達）。逐 skill 的分級指派仍由 `tests/skills/test-automation-annotation.sh` 釘死，文件不重複列表（避免漂移）。
2. **Scope 段過時引用清理**：「per the rule cited below」殘句（v2.2.1 內聯後已無被引規則）刪除。

### Internal

- codex/ 鏡像同步重產。

### SemVer 註

採 patch（2.2.2 → 2.2.3）：純文件語彙定義，無行為變更。

## v2.2.2 (2026-06-11)

**引用接線全面修復（reference wiring audit）**：稽核發現 aux 檔（`references/`、`../_shared/`）在 skill 調用時不會自動載入——只有 body 內在流程點下令 Read 的句子才會被執行。本版將「可達」引用全面升級為「會讀」的條件式祈使，並修復跨 skill 斷路徑：

### Fixed — 修正

1. **13 條 Automation 行升級為條件式祈使**：`（contract: ../_shared/loop-contract.md）` 後綴改為 `（when driven non-interactively — /loop, cron, Workflow — read ../_shared/loop-contract.md first and apply its PAUSE semantics）`，從可達指標變成讀取觸發；gate `tests/skills/test-automation-annotation.sh` 同步更新。
2. **orchestration-interface 引用由 locative 轉祈使**：execute（Step 0 前讀＋Step 4 入口重套）、learn（Stage 0 讀＋§3.5 fan-out 觸發時重套）、review（Stage 0 釘模式＋Stage 4 派發前讀）三處「contract lives in …」改為明確的 read-and-apply 指令。
3. **learn §3.5 跨 skill 斷路徑修復**：learn 不附帶 scripts/ 與 acquisition refs——install-deps、search-papers.py、gh-search.md、x-search.md、web-dynamic.md 全數補上 `../read/` 前綴（自安裝目錄可解析），gh/x lane 並加「先讀再跑」觸發句。
4. **design 路徑與過時引用修正**：export-brief Step 2 兩處 `{plugin_root}` 改為既定義的 `{skill_dir}`；Check D 過時的「design.md Appendix B」改指 `scripts/check.py` Check D；`紙-sanity.sh` 描述改寫對齊實際行為（自動定位 check.py、legacy per-file mode、內建 Kami 規則——原述的 `紙-sanity-rules.json` 並不存在）。
5. **hunt 接線修正**：repo-root 路徑 `plugins/baransu/skills/_shared/tdd.md`（安裝目錄不可解析）改 `../_shared/tdd.md` 並加讀取觸發；`hunt-search.py` 接到 Locate 階段（instrument 前先查 `.claude/hunt-report/` 既往案例），尾段無觸發提及改為儲存指標。
6. **read 平台疑難排解收進失敗路徑**：安裝失敗時先讀 `references/setup/{$PLATFORM}.md` 嘗試排解，仍失敗才停；刪除原無觸發的尾句提及。
7. **book perception-guide Layer-1 觸發**：Stage 2A Layer 1 加條件句——§1 未讀過 `references/perception-guide.md` 者套用前先讀。
8. **execute output-journal / error-reference 觸發**：Step 7 工作日誌追記改為明確 read-and-append；Error Reference 段改為「inline Fallback 未涵蓋的錯誤條件發生時讀表套用」。

### 決策記錄

- 否決獨立 References 段：會複製 ~50 條已正確的 in-body 觸發、徒增漂移面。採 in-place 條件式祈使為唯一慣例。

### Internal

- codex/ 鏡像同步重產。

### SemVer 註

採 patch（2.2.1 → 2.2.2）：文件接線與路徑修復，無行為變更。

## v2.2.1 (2026-06-11)

**loop-contract.md 供應鏈修復＋調用路徑接線**：

### Fixed — 修正

1. **PAUSE 分類學內聯**：`_shared/loop-contract.md` §1 原引用使用者私人全域 rule（`~/.claude/rules/common/platform-awareness.md`）定義 Input/Authorization PAUSE 二分法——散布的 plugin 不應依賴未隨附的本機檔（安裝者從未有該檔；本機亦已歸檔致引用死亡）。定義改為自含內聯，平台成本軸保留為背景說明。
2. **調用路徑接線**：loop-contract 此前無任何 SKILL.md 指向（僅 `rules/anti-patterns.md` 提及，而 plugin `rules/` 非 Claude Code 自動載入元件）——skill 被調用時 `Automation: ultracode=…, loop=…` 的值無處可查語義。13 個 SKILL.md 的 Automation 行統一加註 `（contract: ../_shared/loop-contract.md）`。

### Internal

- codex/ 鏡像同步重產（_shared 與 13 個 SKILL.md 鏡像更新）。

### SemVer 註

採 patch（2.2.0 → 2.2.1）：純文件修復與引用接線，無行為變更。

## v2.2.0 (2026-06-11)

**`/codex-skill-transfer` 對照 2026-06 官方 Codex 文件全面重驗**（developers.openai.com/codex：plugins/build、hooks、subagents、skills），skill metadata version 0.7.4 → 0.8.0：

### Fixed — 修正

1. **Plugin mode 安裝指引重寫**：移除不存在的 `codex plugin install` 子指令（`marketplace add` 即安裝）與錯誤的「必須帶 `--sparse`」宣稱（--sparse 只過濾 checkout，不會重定 marketplace root）；改印 Layout B 本地路徑安裝 + git URL 需 repo-root Layout A catalog 的正確指引，導向 marketplace-mapping.md §8。
2. **plugin.json 必填欄位對齊官方**：Codex 只必填 `name`（kebab-case）+ `version`（semver），`description` 為選填；name-暫代 fallback 保留但報告措辭改「(建議補上；Codex 選填)」；§3 補 component pointer 路徑 ≤125 字元、必以 `./` 開頭。
3. **marketplace source types 對齊官方**：官方文件列三種 source（local / url / git-subdir），非「local 唯一」；§8 加註 git-subdir 與 2026-05 `--sparse` 實測發現的未解衝突（先重驗再改 Layout A/B 建議）；provenance 改以官方 build docs 為主、plugin-creator system skill 為輔。

### Changed — 變更

1. **hooks 現實對齊**：Codex 確有 experimental lifecycle hooks（`~/.codex/hooks.json` / config.toml `[hooks]`；事件鏡像 Claude Code），預設關閉、信任授權、僅 command 型執行；frontmatter `hooks` drop 報告改「手動遷移至 .codex/hooks.json（experimental，預設關閉）」；plugin 層 hooks/MCP 設定不再無聲流失，改發需人工檢視行（不自動輸出指標）。
2. **`CLAUDE.md` → `AGENTS.md` body 改寫**：skill body 內的 CLAUDE.md 引用改寫為 AGENTS.md（Codex root-down 讀取，合併上限 32 KiB），翻譯處理報告行；references/*.md 不改寫，改掃描 Claude-only token（AskUserQuestion / Task tool / TodoWrite / EnterPlanMode / $ARGUMENTS / !`cmd` / CLAUDE.md）逐檔發需人工檢視行。
3. **裸 `$N` 改寫加防護**：僅當 frontmatter 宣告 `arguments` / `argument-hint` 時改寫，避免破壞 awk/sed/bash 字面 $1/$2；`$ARGUMENTS[n]` 改寫不受影響。
4. **輸出不變量落地**：每個 SKILL.md 寫出後檢查 ≤500 行、name 字元集/長度（agentskills.io ≤64）；`skills-ref validate` 在 PATH 上才跑並回報結果；違規照常輸出但入報告。
5. **commands 升級為可行動指引**：Codex custom prompts 已官方棄用——逐檔轉 Codex skill，勿移植 `~/.codex/prompts/`（0.117.0 regression）。
6. **安裝目的地指引**：single-skill/batch 模式輸出複製到 `<repo>/.agents/skills/`（專案）或 `~/.agents/skills/`（個人）——是 `.agents/` 不是 `.codex/`/`.claude/`；SKILL.md Step 2 + 報告各加一句。
7. **AskUserQuestion 行降信心**：「request_user_input 僅 Plan mode 可用」改為「無已驗證 Codex 等價物（官方文件未載；社群指南稱任一模式皆無）」——衝突浮出、不裁決；一律改寫為純文字提問。
8. **agent-mapping 欄位信心標注**：name/description/developer_instructions（必填）、model/sandbox_mode/mcp_servers（選填）、built-ins、max_threads=6/max_depth=1 已官方確認（codex/subagents）；model_reasoning_effort / skills.config / nickname_candidates 標社群來源待確認；gpt-5.4 為 2026-06 社群 opus 對等、會漂移。
9. **skill-root 孤兒子目錄列報**：非 scripts/references/assets/agents 的子目錄不複製、逐一入已捨棄。
10. **倉庫工程面**：AGENTS.md 改寫為委派檔（單一事實源指向 CLAUDE.md，只補非 Claude agent 所需）；新增 `make test` 統一驗證入口；測試套件 worktree-safe 修正（test-distribution-metadata / test_check_design 路徑重錨）。

### Internal

- transfer.py 雜項：刪除死碼 NAMED_ARG regex、修 batch 分支過時註解、description 縮減段補官方 skills-list context cap（~2% window / 8,000 chars）系統性理由註解並標注兩條 trigger-phrase regex 為 baransu 專屬啟發式；docstring 改正已退役 template 引用（openai.yaml / agent stub 實為 yaml.safe_dump / json.dumps 直建）。
- codex/ 鏡像以新版 transfer.py 全量重產（13 skills、v2.2.0），鏡像 skill body 已套 CLAUDE.md→AGENTS.md 改寫。
- verify-skills.py 對 gitignored 本地目錄全面免疫：殘留掃描排除 `*-workspace/` 與 `node_modules/`，skill discovery 排除 `*-workspace/`（skill-creator eval 工作區與本地 npm 安裝皆非散布內容；先前在留有這類本地檔的 checkout 上會誤報 'dev' 殘留、技能數 16≠13、workspace 缺 SKILL.md，導致 `make test` 紅而乾淨 worktree 綠——同一倉庫兩種結果）。

### SemVer 註

採 minor（2.1.2 → 2.2.0）：plugin mode 報告/輸出面新增需人工檢視管道與安裝指引變更屬使用者可見行為擴增；指令、frontmatter shape 向前相容。

## v2.1.2 (2026-06-11)

**`/design` 紙-preset 重新初始化揭露的三組修正**（`/design preset 紙` 等冪重跑 → lint 52 violations → 0）：

1. **slide-cores prefix-mix（Check C，8 檔）**：`section/quote/compare/data/closing/content-bullets/content-2col/kpi-grid` 內殘留 `swiss-*` 懸空 class（v1.3 共用 slide-cores 收編進 preset 時改名未盡），全數更名 `kami-*`；全倉本無任何 `.swiss-*` 樣式定義，純 class 字面修正，渲染零變動。
2. **long-form.html slot 註解誤判（Check E）**：slot contract 註解含字面 `data-slot="long-form-body"` 觸發唯一性檢查，改寫註解措辭；實際 slot 本來就唯一。
3. **DESIGN.md token 名對齊 canonical（Check D，43 處）**：§2 表與全文由上游 tw93/Kami 原名（parchment/brand/ivory…）改為 tokens.css 實際存在的 canonical 名（paper/accent/surface…），hex 與視覺規格零變動；表下加上游原名對應註記；`accent-light`/`charcoal`/`accent-tint(-strong)` 四個無 canonical 槽位者改文件列記法（去 `--` 前綴、字面 hex）。使用者裁決：放棄與上游文件逐位同步，換取文件與實際 token 一致＋lint 全綠。

root 與 preset source（`references/紙-preset/`）同步修改，維持 byte-identical；紙-sanity 與 verify-skills 全綠。採 patch：視覺輸出零變動。

## v2.1.1 (2026-06-11)

**README 潤稿（/write zh Refine）**：核心理念段去除上游品牌引用（strip-provenance 的自我實踐——規則靠防什麼掙位置，不靠來自哪裡）；理念段收尾的對仗句式與「存在性」名詞化改寫（rules 5/8 地板）；起源段一處破折號改冒號（rule 10 軟規則）；/health 表列去贅句。機制錨點路徑與技術 token 零變動，verify-skills 理念錨點檢查仍綠。採 patch：純文案，調用面零變動。

## v2.1.0 (2026-06-11)

**理念合併版**：baransu（結構化管線）×（tw93/Waza 的）規則即天花板哲學熔成一套，成文為 README「核心理念」五條（條款綁機制，錨點存在性由 verify-skills 機器驗證）。18 項收錄全數落地，每項標明對應理念條。規格軌跡：`.claude/think/baransu-v2.1-philosophy-merge-plan.md`（含 /review 複審紀錄）。

### Added — 新增

1. **`/health` 第 13 技能**〔結構是地板〕：移植 Waza /health — 體檢「使用者專案」的 agent 配置與 AI 可維護性，五層審計、預算姿態先行、Step 0 專案分級；9 支 stdlib-only 腳本＋3 個 inspector 子代理人（`agents/health-inspector-*.md`）。定位句明寫：baransu 自身結構驗證歸 `scripts/verify-skills.py`、審單次模型輸出歸 `/review`。
2. **「13 即上限、以裁換建」條款**〔規則是天花板〕：寫入 CLAUDE.md；機制錨點＝verify-skills 技能數檢查（12→13）。
3. **/review Finding Quality Gate**〔證據優先〕：Stage 6 四問門檻（file:line／觸發輸入／上下游已讀／嚴重度站得住）、HIGH/CRITICAL 三證據、「乾淨的 review 是有效的 review」、禁止為正當化呼叫製造發現。
4. **HTML 工作日誌**〔狀態落盤〕：/think 與 /review 交付物以 book golden-template 渲染至 `.claude/{think,review}/<slug>.html` 並 SendUserFile；實作期間持續追記規範外決策／變更／取捨。共用契約＝`_shared/output-journal.md`（新檔）；execute 與 tdd.md §7 各掛追記鉤子。
5. **claim-cite-first**〔證據優先〕：anti-patterns 新條「無源依賴」＋ `(verified: <how>)` / `(inferred: 未實查)` 標注慣例進 review/think 輸出格式。
6. **重述＋列步驟＋條件式等確認**〔人在授權點〕：anti-patterns 新條「悶頭就做」— 顯示永遠做；等確認分流（互動等、完全授權/ultracode/loop 走 Input-PAUSE 預設值）。
7. **anti-patterns 淨增 4 條**〔規則是天花板〕：Worktree Safety（授權層級＋隔離驗證）、不受信任內容、無源依賴、悶頭就做（6→10 條）；與 tdd.md 雙向 cross-ref。
8. **/write 長文 change-points 分支＋中文 AI 腔指紋**〔證據優先〕：~300 行以上輸出改變更點清單（可 diff 審）；writing-principles 折入指紋 4 條；em-dash 分級 — en 新 rule 8（U+2014 硬禁、U+2013 限數字區間）、zh 新 rule 10 軟規則＋voice-overridable 新語義類別；en 規則範例自違規兩處改寫。
9. **CLAUDE.md Skills 表「Not for（易混淆）」欄**〔規則是天花板〕：13 列歧義消解（RESOLVER 輕量版），單路由面。
10. **verify-skills 擴充**〔結構是地板〕：三發行面版本一致（plugin.json＝marketplace.json＝codex 鏡像，鏡像缺檔即違規）；README 理念段逐條錨點存在性檢查；`EXPECTED_SKILL_COUNT` 13。

### Changed — 變更（含行為變更，升級必讀）

1. **`/read` 預設改 local-first（隱私面破壞性變更）**〔人在授權點〕：舊版非 GitHub/PDF URL 一律先送 defuddle.md 代理；新版預設本地抽取、URL 不離機，代理需 `--use-proxy` 顯式開啟；本地品質不足時不再無聲降級走代理，改為停止並建議 `--use-proxy` 或 `--chrome`。認證／內部 URL 任何情況不得餵代理。
2. **/think、/review 的 Outcome Contract Output 行**：由「不另落檔」改為同步落檔 HTML 工作日誌（顯式契約變更）。
3. **/ship push 在 loop 驅動下升為 Authorization 等級**：loop-contract 補註 — 驅動上下文無常設授權紀錄即不得自動 push。
4. **execute/SKILL.md 瘦身 605→447 行**：四段自足內容逐字下放 `execute/references/`（green-proof-verify／goal-alignment-filter／correction-strategy／error-reference），failure_count 措辭經逐行比對 verbatim 保留；500 行官方上限 advisory 清除。
5. doc-debt 清零其餘三項：README Codex `--ref` 過時 pin → v2.1.0；book-stage0 測試修復（worktree 相對路徑＋重錨 Stage 0 區段）；anti-patterns↔tdd.md cross-ref 補齊。
6. 測試面 12→13 漣漪全清：baseline 重生（13 列）、D1 改 semver 斷言（不再釘死版本字串）、D2/D7、automation 標注表加 health（assist/assisted）。

### 盤點收尾（差異清零）

- **已存在、不重做**：Pattern-Fix Completeness（/hunt Scope Blast）、Autofix 四級路由（/review 四層 tier）。
- **declined（理由見計畫 Not building）**：make regenerate codegen、36 條 anti-patterns 照搬、/check maintainer 鏈、串聯改手動、第 14 技能。

### SemVer 註

採 minor（2.0.1 → 2.1.0）：主軸為新增（第 13 技能＋治理資產）。/read 的 local-first 預設變更具行為破壞性但屬隱私強化方向，已在本節 Changed 首條顯著標記；嚴格解讀者可視為 major 候選，維持 minor 是因調用面（指令、旗標、模式集）全部向前相容。

## v2.0.1 (2026-06-11)

**`hooks/wiki-sync.sh` 修 slug 抽取 bug**：`read/index.md` 以 `# Read Index` 標題行開頭時，表頭列落在 `NR>2` 之後，awk 把字面值 `slug`（表頭字）當成待同步 slug，產生 `sync | slug` 幽靈紀錄。修法：抽取條件追加 `$3=="slug"` 過濾。實測舊版對現行 index.md 首筆吐出 `slug`、新版正確過濾。採 patch：hook 內部行為修正，調用面零變動。

## v2.0.0 (2026-06-10)

**破壞性改版：治理瘦身，16 技能裁併為 12。** 依使用證據裁決（grade/triage/bridge 自癒迴路從未運轉、dev 使用最少），同版交付四項治理資產。規格與驗收軌跡見 `.claude/analyze/2026-06-10-baransu-v2-slim/` 與 `.claude/execute/2026-06-10-baransu-v2-slim/execute/final-report.md`。

### Removed — 移除（Breaking）

1. **四技能**：`/dev`、`/grade`、`/triage`、`/bridge`。
2. **自癒 harness 全套附屬資產**：`plugins/baransu/hooks/` 三支 telemetry 腳本（903 行；保留 hooks.json 與 wiki-sync.sh）、`plugins/baransu/scripts/` 9 檔（2,889 行，含零引用死碼 baseline-parity-score.py）、`agents/investigator-agent.md`、`_shared/` 三份 telemetry schema、耦合測試約 27 檔。
3. **升級註記（必讀）**：曾依 harness 安裝流程在 `~/.claude/settings.json` 註冊 hooks 者，需手動移除三個條目（`UserPromptSubmit` / `PostToolUse` / `Stop` → `plugins/baransu/hooks/*.py`），否則每個 session 都會呼叫已不存在的腳本。`.claude/harness/` 下的本地 telemetry 累積檔已無消費者，可自行刪除。

### Changed — 變更

1. **小任務 TDD 閘語義降級（明文承認）**：workflow-enforced（`/dev` 硬閘）→ discipline-suggested（`_shared/tdd.md` 新 §7「直接實作時的紅綠閘」文件紀律）；`/think` 與 `/hunt` 的小任務交接均改道至該節。中大型任務 `/analyze` → `/execute` 的 TDAID 閘門不受影響。`failure_count` 不變量唯一事實源維持在 execute/SKILL.md，tdd.md 只引用不複製。
2. **發行面全同步**：CLAUDE.md 技能表、README 工作流鏈、`plugin.json` 與 `marketplace.json` 全改 12 技能；`codex/` 鏡像以 transfer.py 全量重產（12 技能、v2.0.0）。

### Added — 新增

1. **Outcome Contract 四行頭 + Automation 第五行**：12 個 SKILL.md 統一 `Outcome / Done when / Evidence / Output` 契約 + `- **Automation**: ultracode=…, loop=…` 雙軸標注（review/execute/learn＝overlap・drivable；hunt/analyze/codex-skill-transfer＝assist・assisted；think＝neutral・not-drivable；其餘中立）。Done when 以可驗證條件為預設，審美／事件型技能允許事件型逃生門。
2. **`_shared/loop-contract.md`**：技能被 /loop、cron、Workflow 驅動時的契約單一知識源 — Input PAUSE 走預設值並在報告標注假設、Authorization PAUSE 任何情況硬停、三硬停承接（迭代上限／無進展偵測／預算上限）、per-skill PAUSE 分類表（review 2 點／execute 4 列／learn 6 點／think 不可驅動）。驅動上下文覆寫平台 supervised 預設，但 Authorization 永不可覆寫。
3. **`rules/anti-patterns.md` 容器**：含「收斂不堆積」與「strip-provenance」自治條款，首批 6 條跨技能護欄（巢狀 skill 呼叫、憑記憶改檔、改測試遷就實作、跳紅燈、語言慣例漂移、不 bump 版本）。
4. **雙模 orchestration interface（選項 A：單一介面＋薄 adapter）**：review/execute/learn 各加 `references/orchestration-interface.md` — 同形 finding schema、depth 不變量逐模重述（每檔 grep ≥2）、Stage 0 模式釘死（system-reminder 偵測，退化為使用者顯式聲明）。
5. **`scripts/verify-skills.py`**（repo root）：單一結構驗證入口，7 檢查面（frontmatter／引用檔存在／被裁名稱零殘留／雙 manifest 版本一致／Outcome Contract 四行齊備／Automation 標注／500 行 advisory），exit 0/1/2；附負向 fixture 測試（`tests/fixtures/verify-skills/bad-skill/`）堵驗證器自證循環。

### 驗收

`verify-skills.py` 綠燈（12/12 技能）、`claude plugin validate` 通過、pytest 20 綠、5/5 REQ 覆蓋（Final-Review needs_fixer: false）、15/15 TDAID 任務完成（1 重試、0 blocked）。

### SemVer 註

採 major（1.5.0 → 2.0.0）：移除四個使用者調用面技能，且升級需手動清理 settings.json hook 條目，破壞性明確。

## v1.5.0 (2026-06-10)

**`/design` 紙-preset 與 `/book` Kami 渲染對齊 tw93/Kami@5cd7c8e**：

- design 紙-preset：tag 三層規格（#E4ECF5 standard / #EEF2F7 lightest）、breaking-badge 例外色（#f0e0d8/#8b4513）、parchment hex 修正、上游 provenance pin；根目錄 DESIGN.md / tokens.css 重新同步至 byte-identical。
- book：修 stale `--paper`（#faf9f5 → #f5f4ed）、focal fill → #EEF2F7、node width 12 層 → 3 層 {128/144/160}、dots pattern 24 → 22（橫跨 13 個 diagram types）、arrow-link → `--brand-light` #2D5A8A；example-architecture 幾何修正後通過全部 validate-output.ts gates（先前違反 GATE-J/K）。
- 另含 `codex-skill-transfer` 修正：Codex port 排除 `*-workspace/` 目錄。

## v1.4.6 (2026-05-14)

**`/codex-skill-transfer`**：修 `emit_agent_stub` 兩條 bug，讓 13 個 agent stub TOML 成為 Codex `spawn_agent` 真正可載入的 schema（先前 Codex subagent runtime 實測四件套 `spawn_agent` / `send_input` / `wait_agent` / `close_agent` / `resume_agent` 全綠後，stub 內容的正確性從「UI 觀感」升格為「runtime 載入」）。

### Fixes — 修正

1. **F2：agent stub `description` 不再被截斷**。先前 200-char 硬切會在 11/13 個 stub 中產生 `Fills impl-checklist and returns s`、`Invoked once by /baransu:execute when Fin`、甚至 cut 在多 byte emoji 中間變 U+FFFD `�` 的情況。改為 first-line verbatim、`json.dumps` 處理 escape；descriptions 現完整保留（193–352 chars 範圍）。
2. **F3：source frontmatter `tools:` 不再被洗成空 `# mcp_servers = []`**。實際運作邏輯 source 已有但舊 cache 版（1.4.1 安裝快取）缺；本輪改跑 source transfer.py 後正常產出 `# mcp_servers = ["Read", "Grep", "Glob", "Bash", "Edit"]  # ported from Claude tools:; rename to Codex MCP server ids before enabling`——使用者複製 stub 到 `~/.codex/agents/` 後一眼看到工具能力線索。
3. **副產品**：跑 source（39k）vs cache（33k）transfer.py 的差異使 13 個 SKILL.md / reference 也套到 v0.7.3 既有但未套用的 Claude→Codex tool-name 重寫（`TaskCreate` → `track the task internally`、`AskUserQuestion` → `ask the user directly` 等）。文法略生硬，但符合 SKILL.md §Boundaries 規約。

### Internal

- 起因：本輪 `/review` 對 codex/ 派 architecture-reviewer，在 Codex subagent runtime 實測之後重新估權，把 F2/F3 升格為 needs-judgment。
- 修正：`plugins/baransu/skills/codex-skill-transfer/scripts/transfer.py` `emit_agent_stub` line 634-642 改為 `desc = str(fm.get("description") or "").splitlines()[0]`（拿掉 200-char cap）。F3 之 mcp_servers 改寫 logic source v0.7.3 早已含。
- skill metadata version: 0.7.3 → 0.7.4。
- codex/ 重新覆蓋：13 agent stub + 13 SKILL.md/reference 被更新。

### SemVer 註

採 patch（1.4.5 → 1.4.6）：runtime schema 修正，使用者調用面（指令名、frontmatter shape）零變動。

## v1.4.5 (2026-05-14)

**`/codex-skill-transfer`**：Step 2 補一句明示 `baransu` plugin 的 `<codex-output>` 是 repo 根目錄的 `codex/`，與 `<repo-root>/.agents/plugins/marketplace.json` (Layout A catalog) 的 `source.path` 對齊。避免下次跑時又另開一個輸出目錄、把 catalog 的 `source.path` 留成 dangling。skill metadata.version 0.7.2 → 0.7.3。

## v1.4.4 (2026-05-14)

**`/review` 強化**：源自 Waza `/check` 的「Hard stops sweep + Sign-off receipt」結構化尾段機制，作為 Stage 6 balance check 之後的彙整型閘門。

### Features — 新增功能

1. **Hard stops sweep（Stage 6 後新增）**：4 條 Required item（Unverified claims / Destructive auto-execution / Unknown identifier in target / Dependency changes）+ 1 條 Optional item（Injection / hardcoded secret，僅在 Stage 4 未派 `security-reviewer` 時列出，避免雙重把關）。任一命中時，相關 finding **強制 pin 到「需判斷」**，禁止透過 balance check 降為 advisory；report 整體 verdict 改為「需判斷」或「未完成」。
2. **Sign-off receipt（report 結構化尾段）**：fenced code block，固定 8 個對齊欄位 — `files`、`scope`、`depth`、`perspectives`、`hard_stops`、`new_tests`、`doc_debt`、`e2e_status`。SKILL.md 內 pin 死每個欄位的 semantics（避免日後漂移）；其中 `perspectives` 採 baransu Stage 4 dispatched set + Stage 5 adversarial 標記（不繼承 Waza pooled-specialists 語意），`new_tests` 為純計數（不繼承 regression-first 語意，該責任歸 /dev 或 /execute）。
3. **Hard-stops-sweep checklist**（與 prose body 並列輸出）：Required 4 條永遠列出；Optional 1 條僅當 `security-reviewer` 未派時列出。每行格式 `□ <item>: not hit` 或 `☒ <item>: hit — <one-line citation>`。

### Internal

- Source：Waza `/check` skill（read material 收於 `.claude/read/material/check-review-before-you-ship/`、digest 於 `.claude/learn/digests/waza-check-skill-code-review.md`）。
- 不繼承 release-artifact missing / generated-artifact drift / version skew 等屬於 `/ship` 的條目（責任分層保留）。
- review SKILL.md +51 行。

### SemVer 註

採 patch（1.4.3 → 1.4.4）：使用者調用面（指令名、`AskUserQuestion` option labels、Stage G handoff routing）未變；尾段結構與 hard-stop 閘門屬於輸出格式擴增與內部行為加嚴，下游消費者只需忽略額外段落即可向前相容。

## v1.4.3 (2026-05-14)

**`/hunt` 強化**：源自 Waza `/hunt` 的四項增補，inline 融入既有 SKILL.md，不引入 references/ 新檔，不更動 description / when_to_use trigger 詞。

### Features — 新增功能

1. **Instrumentation: Side-effect rule**：加 log 後若觀察到行為改變（bug 消失、症狀偏移、事件順序不同），視為 timing / lifecycle / concurrency 問題的直接證據，不准當成「log 副作用」忽略——觀察動作本身已指向根因類別。
2. **Scope Blast Mode（新章節，置於 Confirm or Discard 後、Bisect Mode 前）**：根因確認後、宣稱 fixed 前，grep 全 repo 找同形 bug 的 N-1 個兄弟；每個 match 在 case file 的 `Scope Blast` section 寫下 `<file:line> — fix | leave: <reason> | unsure: <question>`；`unsure` 在使用者回覆後就地更新為 `unsure → fix` 或 `unsure → leave: <reason> after user reply <date>`。宣稱 fixed 雙條件：(a) 每個 match 都有紀錄，AND (b) 成功格式的 `迴歸守護` line 既點到鎖定測試、又以 `HUNT-YYYY-NNN §3` 形式反向引用 case file 該 section。
3. **Repeated Regression Mode（新章節，置於 Bisect Mode 後、Hard Rules 前）**：使用者提供「好的」截圖／版本／fixture 作為 reference oracle 時的 5 步流程——列出每個症狀（保留使用者原話）→ 指認 reference oracle → 編輯前定義 pass/fail check → 比對 current vs reference 命名精確 delta → 同症狀仍在則 cross-reference Hard Rule「Same symptom recurs after fix」並從證據重建假說。末尾分流：純主觀 UI 品味 → `/baransu:design`；render / state / timing / build output / 字型 / 從已知良好版本回歸 → 留在 `/hunt`。
4. **Hard Rules +2 條**：
   - **「Fix plan or current diff touches 6 or more files (without a Scope Blast pattern justification) → Stop before adding the 6th file」**：兩個檢查時點（drafting + after each edit）；若是 class-of-bug 收網則例外（走 Scope Blast Mode）；若是 symptom-patch creep 蔓延則 narrow back 或路由到 `/baransu:analyze`。
   - **「Deflection from a specific area → Treat as a signal」**：明示為語意 trigger 非字面字串比對；附中英文具體例（「那段沒問題」「不是那邊的問題」「我已經檢查過了」/ "that part doesn't matter" / "I already checked there"），特別針對多階段 pipeline（CI segment、data pipeline stage、baransu plane handoff）中某段被排除的盲區。

### Internal

- Source：Waza `/hunt` skill（read material 收於 `.claude/read/material/waza-hunt/` 與 `.claude/read/raw/waza-hunt/`、digest 於 `.claude/learn/digests/waza-hunt-skill-diagnose-before-fix-debugging-methodology.md`）。
- 驗收路徑：`/baransu:review` 雙 perspective（architecture + quality）派發，14 findings 收斂至 5 處 surgical fix（Scope Blast 載體規格化、Repeated Regression 第 5 步改 cross-reference、Hard Rule 閾值與時點明確化、deflection trigger 雙語範例、Scope Blast 例外條款）；dry-run 用 commit `11de678` (GATE-L viewBox containment) 走完所有新段落，全部正確觸發或正確 N/A。
- hunt SKILL.md 227 → 266 行。

### SemVer 註

採 patch（1.4.2 → 1.4.3）：description / when_to_use trigger 詞依使用者明示保留原樣，沒有新增 trigger 句式；新章節是內部紀律補強，使用者調用面零變動。

## v1.4.2 (2026-05-14)

**`/think` 強化**：注入三項源自 Waza `/think`（github.com/tw93/Waza）的機制，未破壞 Stage A-G、iron rule、四選一閘門等既有骨幹。

### Features — 新增功能

1. **Step 0 改為兩層 mode selection**：第一層 Plan vs Evaluation（種類分歧），第二層 Plan 底下 Lightweight vs Full（深度）。Evaluation Mode 作為平行 H2 主體區段（與 Lightweight Mode body 平行），輸出 **Kill / Keep / Pivot** 單行裁決 + 三條基於使用者實際限制的理由。
2. **Evaluation Mode 觸發語清單與 disambiguation**：採 Waza 原文 7 句式（「判断一下」「值不值得」「有没有必要」「我不想做」「商业前景」/ "should we keep this" / "is this worth it"）；含錯誤上下文者（「判断这个报错」「判断这个错误」「这个报错值不值得修」等）一律路由至 `/hunt`，不走 Evaluation。Plan ↔ Evaluation 與 Lightweight ↔ Full 皆互斥獨立，mode 切換需手動重啟 `/think`。
3. **Stage D Premise validation 新增「記憶類型映射」子規則**：三行映射表 + 「現況覆寫記憶」原則。`decision / preference / principle` → 規劃約束（分派至 Stage F）；`pattern / learning` → 設計檢查（分派至 Stage E）；`fact` → 須以當前狀態驗證（Stage D 自身完成）。CLAUDE.md 為記憶映射的潛在全域權威來源，若衝突 global > skill-local；本版確認 CLAUDE.md 尚未編碼此語意，本 skill 暫為事實單一來源。
4. **Gotchas 改混排格式（11 條）**：保留 User-fatigue 一條 prose（多層應對需敘事完整），其餘 6 條既有 + 4 條新增 Waza 反例改 **What happened / Rule** 兩欄表格——pwd 前置、MCP 載入檢查、單一 stack 引入新語言/runtime、「判断一下报错」誤觸 Evaluation。

### Internal

- 體量檢查：SKILL.md 357 → 433 行（+21%，預算 ≤465）。Stage A-G 命名與順序、iron rule、Stage G 四選一閘門、繁中 user-facing 規約全保留。
- 不影響其他 skill：review / dev / analyze / 餘下 12 skill 皆未動。

### Fixes

- Gotchas 表格化過程中順手修正既有 Option 編號誤植：原 prose「treat it as Option 2 (還有地方要對焦)」實際應為 Option 3（Stage G 四選一閘門中 Option 2 是「批准實作（完全授權）」、Option 3 才是「還有地方要對焦」）。新表格列已對齊 Option 3。

### SemVer 註

**就 minimum-impact patch 解讀**——本版採 patch（1.4.1 → 1.4.2）：使用者調用面（指令名、`AskUserQuestion` option labels、Stage G handoff routing）皆未變，僅 SKILL.md 內部行為增補。嚴格 SemVer 解讀因 Step 0 新增使用者可見的 Plan/Evaluation 入口可落 minor；若 policy 後續要求 minor，bump 為 1.5.0。

## v1.4.0 (2026-05-13)

**Baseline-parity milestone**：對標 op7418/guizang-ppt-skill / alchaincyf/huashu-design / tw93/Kami 三 baseline 從 ~50% 推到 ≥ 90%。`baseline-parity-score.py` 自評 **100.0%**（30/33 task complete via /loop autonomous run，剩 3 為 advisory/follow-up dogfood pass）。

依據 `.claude/analyze/2026-05-12-baransu-parity-v1-4/` 規格，全 11 條 C1-C11 Criteria 達標。M3 SKILL.md fractional-heading cleanup 完成（advisory per user 定案）。

### Features — 新增功能

1. **REQ-001 / C1 — SVG 13 diagram-types 全 status=complete**：架構 / 流程 / 序列 / 狀態 / ER / 時間軸 / 泳道 / 象限 / 巢狀 / 樹 / 分層 / Venn / 金字塔，每檔含 Kami-compliant example SVG（chevron stroked markers / 節點寬 `{128,144,160}` 白名單 / focal `#1B365D` stroke + `#EEF2F7` fill / 4-multiple 座標）。
2. **REQ-001 / GATE-J/K**：`validate-output.ts` 新增兩 strict gate — GATE-J（node-width whitelist + 2-tier 例外 viewBox<360）、GATE-K（chevron-strict `<path d="M2 1 L8 5 L2 9">`）；含 negative fixtures 在 swiss-smoke-test。
3. **REQ-002 / C2 — 8 文件 schema × 3 preset × zh/en**：新增 Resume / Portfolio / One-Pager / Letter / Equity-Report / Changelog 共 6 schema md × 3 preset = 18 schema 檔 + 36 HTML 模板（每 schema zh + en variant）；en variant 採 Charter / Georgia / Palatino stack 不含 CJK 字體；人像 `<img>` 強制 `object-position: center 35%`（rule of thirds）。
4. **REQ-003 / C3 — Slide 22 layout lock list × 3 preset**：三 preset slide-cores 各擴張 9 個新 layout（timeline / process / testimonial / agenda / stat-hero / icon-grid / table-heavy / before-after / divider）+ closing 覆寫修補 v1.3 prefix-mix bug。`validate-swiss-deck.mjs` 新增 lock-list 機械驗證 + alias map for v1.3 filenames（cover→title, content-2col→two-column 等）。canonical-tokens.md 加 22-row Slide Layout Registry。
5. **REQ-003 / Modular scale 1.333**：canonical-tokens.md 新增 Modular Scale section（perfect fourth `r=1.333`）；三 preset tokens.css 重新計算 h1=2.375rem, h2=1.75rem, h3=1.3125rem；v1.2 era 2.2× / 1.24× 舊比例移除。
6. **REQ-004 / C4 — Editorial 印刷學三件套全機械化**：三 preset design-cores + golden-template 全面加 `text-wrap: pretty`；新增 `.{preset}-dropcap` class `font-size: 4.65em`（精準 3-line drop 對齊 body line-height 1.55）；prose curly quotes（`U+201C` / `U+201D`）。新增 `editorial-sanity.sh` 三 check（text-wrap pretty / dropcap font-size [4.0, 5.0]em / 0 prose straight quotes）整合進三 preset sanity wrapper。
7. **REQ-005 / C5 — Slide checklist 5 → 16 條 P0-P3**：四層分類（含 P0-S Swiss-specific / P0-A all-preset / P0-B baransu-self 三子前綴）；每條三欄（現象 / 根因 / 做法）+ source metadata（dogfood-v1.3-handoff / kami-spec-L86 / huashu-incident）。
8. **REQ-006 / C6 — Fact-Verification + Core Asset Protocol + 三 preset image-prompts**：`/book SKILL.md` Stage 2A §0 加 Fact-Verification Principle #0（regex 偵測產品/版本 / 人名+職位 → WebSearch verify → AskUserQuestion gate on 0 results）；Stage 3 §5 加 Core Asset Protocol 4-step（Ask → Generate/Search → Verify → Freeze，跳步即 fail）；三 preset image-prompts.md 含產品圖 / logo / UI 三段 + 標準負面尾巴 `no title, no footer, no page chrome, no logo, no border`。
9. **REQ-007 / C7 — `/baransu:design export-brief` 子模式**：第 4 mode（gen / preset / lint 之外）；4-step 組裝邏輯（parse preset → read sources → assemble 6-section brief → output to `.claude/design/brief-{preset}-{date}.md` 或 `--stdout`）；hex 從當前 tokens.css 動態解析（B20 邊界）；Codex CLI bridge example `codex prompt --stdin < brief-{preset}-{date}.md`。
10. **REQ-008 / C8 — DESIGN.md §9 reproducibility 三要素**：三 preset 各自含 (a) 焦點節點上限 1-2 / (b) accent hex 設計理據（HSL + oklch advisory，每 preset ≥1 條）/ (c) 我不是什麼（≥5 條 no-X anti-patterns 對齊各 preset 反例）。
11. **REQ-009 / C9 — oklch advisory**：三 preset DESIGN.md §2 accent token 旁標 `oklch(...)` 等價值 + footnote 說明 advisory；tokens.css / design-cores HTML 不含 `oklch(`（hex-only invariant preserved）。
12. **REQ-012 — `baseline-parity-score.py` 自評腳本**：11 個 check function 對應 C1-C11；加權總和 = 1.0（C1/C2/C3 各 0.15 / C4 0.10 / 其他 0.05-0.08）；`--ci` 旗標印 JSON；`--threshold N` exit 1 if < N；B26 self-exclusion assertion（C12 明文不入 score）。

### Internal Debt 收尾

- **REQ-010 M1**：`swiss-smoke-test.sh` 加 Stage 0 三 preset golden-template presence gate（kami / swiss / gd）。
- **REQ-010 M2a**：`design-token-resolver.md` 從 v1.2-era / Kami-only 升級為 v1.3+ 三 preset aware（polygon marker / 12-檔 node-width 全部標為 v1.2 retired）。
- **REQ-010 M2b**：新增 `golden-template-swiss.html`（Inter / IKB `#002FA7`）與 `golden-template-gd.html`（Roboto Flex / M3 `#6750A4`）；三檔 validate-output.ts GATE A-K 全 PASS。
- **REQ-010 M3**（advisory per user）：`/book SKILL.md` fractional headings (`### 0.0` / `### 0.5` / `### 2.5` / `### 4.5`) 整數化；`## Stage 0.5` → `## Stage 0b`（matching 2A/2B alphabetical convention）。

### Variance（已記錄非阻擋差異）

- 三 preset slide-cores 各落在 **21/22** 而非 22（`closing.html` 已存在 v1.3 軌道，本次為覆寫 prefix-mix 修補非新增）；validator soft-warns 4 missing canonical names（toc / image-full / quote-stack / breakout）— v1.4 follow-up dogfood pass 將補。
- `swiss-sanity.sh` / `google-sanity.sh` 在 TASK-editorial-04 fix attempt 內首次建立（v1.3 軌僅 `紙-sanity.sh`）。
- 完整 v1.4 fixture regen（66 layout × 3 preset + 36 schema fixture）pragmatic-scope 推遲為 follow-up；M1 以 Stage 0 presence gate 涵蓋三 preset golden-template 變體即達 REQ-010 Scenario 1 acceptance。
- spec wording `gd-*` class prefix → codebase 既有 convention `google-*`（spec drift 記錄 in pending_spec_drift；不影響功能）。

### 自評

```
$ python3 plugins/baransu/scripts/baseline-parity-score.py
✓ C1 (w=0.15): 13/13 types complete
✓ C2 (w=0.15): 18/18 new-schema md
✓ C3 (w=0.15): 3/3 presets ≥21 layouts
✓ C4 (w=0.10): 3/3 preset editorial-sanity
✓ C5 (w=0.07): P0/P1/P2/P3 = 6/4/4/2 (total 16)
✓ C6 (w=0.08): 5/5 governance checks
✓ C7 (w=0.07): 3/3 export-brief checks
✓ C8 (w=0.08): 3/3 preset §9
✓ C9 (w=0.05): 6/6 oklch checks
✓ C10 (w=0.05): 3/3 v1.3 debt (M3 advisory)
✓ C11 (w=0.05): version=1.4.0

Overall baseline-parity score: 100.0%
```

---

## v1.2.0 (2026-05-12)

### Features 新增功能

1. **Swiss preset**：`/baransu:design preset swiss` 提供 IKB 主色 + Inter/Helvetica/Noto Sans TC 字體 stack，與既有「紙」/「google-design」preset 同層
2. **`--style` 旗標**：`/baransu:book` 新增 `--style kami | swiss`（預設 kami），僅 `--format ppt` 支援；與 `--format html` 同用會報錯
3. **9 個 slide-core 版式**：cover / section / content-bullets / content-2col / data / kpi-grid / compare / quote / closing，每個含 YAML `applies_to` 供 Stage 2B 動態決策表
4. **GATE-F (class prefix 一致性)**：驗 slide HTML class 走 `kami-*` 或 `swiss-*` 單一 prefix；含 tokens.css preset 註解 tie-break
5. **GATE-G (layout registered)**：驗 `<section data-layout="X">` 對應 `{project_root}/slide-cores/X.html`；缺檔 SKIP（不 FAIL）
6. **移除 `slide-template.html`**：舊版式骨架由 `{project_root}/slide-cores/` 取代

## [1.1.17] — 2026-05-11

### 新增

- **`/baransu:book` skill** — 把任何來源轉成 Kami 主題瀏覽器 HTML 的三階段流程
  - **Acquire**：URL proxy cascade（defuddle.md → r.jina.ai → direct）、`/read` slug、`/learn` digest slug、本地檔案、`--text` 直接輸入
  - **Synthesize**：內容類型自動感知（technical / narrative / research，由 `references/perception-guide.md` 定義分類信號）、抽取 4–8 節結構 + 關鍵主張 + SVG 需求旗標、自動 slug 衝突偵測
  - **Render**：完整依照 `references/golden-template.html` 與 `design/references/paper-preset.md` 生成 Kami HTML；≥1 SVG 圖解（依感知類型決定圖解策略）；含側欄 TOC、章節編號、`.callout` / `.card-grid` / `.tradeoff-row` 等元件
  - **Validate**：`scripts/validate-output.ts` 品質閘（HTML 可解析、`<article>` 結構存在、SVG 平衡、本地資產路徑正確）；`browser-use` 自動驗跑版並儲存截圖至 `.claude/book/{slug}-preview.png`
- **`scripts/install-deps.ts`** — Stage 0 一鍵安裝 markitdown + browser-use（三段 pip fallback，不需手動）
- **`scripts/validate-output.ts`** — TypeScript 品質閘，exit 0/1/2 標準合約
- **`references/perception-guide.md`** — 內容類型分類信號表、各類視覺處理原則、SVG 策略、合成長度限制
- **`references/golden-template.html`** — Kami 黃金模板，含完整 CSS tokens、元件模式、SVG `<defs>` snippet、IntersectionObserver TOC script

### 變更

- `plugins/baransu/.claude-plugin/plugin.json` 版本提升至 1.1.17
- 關鍵字表新增 `book`

[1.1.17]: https://git.hy-tech.com.tw/ben.tsai/baransu/-/compare/1.1.16...1.1.17

## [1.1.16] — 2026-05-11

### 變更

- **plugin description / keywords 精簡** — `plugin.json` 與 `marketplace.json` 描述改為單句，keywords 改為 12 個 skill name 的扁平列表

[1.1.16]: https://git.hy-tech.com.tw/ben.tsai/baransu/-/compare/1.1.15...1.1.16

## [1.1.15] — 2026-05-07

### 新增

- **`/baransu:write` 首份 voice preset：`yu-guang-zhong-voice.md`** — 余光中 散文 voice profile 初版。基於〈聽聽那冷雨〉(1974) 萃取，捕捉**正向風格錨**（疊字節奏、聽覺擬聲、古典白話交織、句長對照、動詞密集鏈）；負規則延續 `writing-principles.md` 同源論述（拒絕英式中文、不用「被」字被動、不堆抽象名詞）。
  - 結構：風格摘要 + 6 條可執行寫法規則（含「平的 / 余光中」對照表）+ 3 段神韻 sample（疊字+擬聲+古典白話、動詞鏈+短句鎚收、跨段 motif 呼喚）+ 詞彙線索 + anti-AI floor 守則 + 來源 + 後續可擴條目
  - 來源原文已 capture 至 `.claude/read/material/ygzsw007/index.md`（via `/baransu:read --web`，Defuddle Layer 1，4361 字）
  - 啟用方式：`/baransu:write zh voice="yu-guang-zhong" [text]`，loader 走 1.1.14 加入的 `references/{name}-voice.md` 路徑

[1.1.15]: https://git.hy-tech.com.tw/ben.tsai/baransu/-/compare/1.1.14...1.1.15

## [1.1.14] — 2026-05-07

### 變更

- **`/baransu:write` 加 voice cue + long-input mode-aware suppression**（輕量版改動，SKILL.md +13/-2 行）
  - Stage 0 後加 **Voice cue 段**：optional `voice="..."` 參數；preset name（讀 `references/{name}-voice.md`）/ 具名作者 / 自由描述三種輸入；不覆蓋 rules 5/7/8（anti-AI 味底線）；Generate 模式忽略
  - Stage 2 Refine 末加 **Long input handling 段**：輸入 ≥ 5 段 OR ≥ 800 字（zh）/ ≥ 500 words（en）時，命中規則只改最影響的一處（mode-aware suppression）；rules 5/7/8 例外，仍每處套用
  - Rule tag examples 末新增 zh `voice 套用` / en `Voice applied`
- **零回歸保證** — 規則本文（zh rules 1-9 / en rules 1-7）零修改；`references/writing-principles.md` 整份零修改；既有 Refine 輸出格式（Before/After/修正說明）三 header 零修改；既有 zh/en prefix 行為零修改；/learn Stage 5 內部呼叫 `/write {LANG}`（不帶 voice）byte-for-byte backward compat。
- **新增結構測試** — `tests/skills/test-write-skill.sh`，14 個 bash 結構斷言（A1-A4 Voice cue 段、B1-B4 Long input handling、C1-C2 Rule tag、D1-D4 backward compat invariants），exit 0/1/2 標準閘門 contract，與既有 `tests/skills/test-{skill}-skill.sh` 命名慣例一致。

[1.1.14]: https://git.hy-tech.com.tw/ben.tsai/baransu/-/compare/1.1.13...1.1.14

## [1.1.13] — 2026-05-07

### 變更

- **Skill descriptions 統一三段式格式** — 全部 15 個 SKILL.md 的 `description` 改寫為 `Use When … Do … Trigger On …` 三段結構（analyze / bridge / codex-skill-transfer / design / dev / execute / grade / hunt / learn / read / review / ship / think / triage / write）。對模型 trigger 判斷與人類掃讀都更友善；繁中觸發短語全部保留。
- **codex-skill-transfer 工具映射補完 Plan Mode 差異** — `references/skill-mapping.md` §6 工具映射表新增兩列：
  - `AskUserQuestion` → 標註 Codex 的 `request_user_input` 只在 Plan mode 可用，不能當 drop-in
  - `EnterPlanMode` / `ExitPlanMode` → 明寫 Codex 沒有 skill-callable 等價物（active mode 由 developer message 切換），需改寫成 prompt-driven plan gate
- **Codex 端同步** — `codex/plugins/baransu/` 重生，反映新 description 格式 + plugin.json 版本。

[1.1.13]: https://git.hy-tech.com.tw/ben.tsai/baransu/-/compare/1.1.12...1.1.13

## [1.1.12] — 2026-05-07

### 新增 Codex CLI 支援

baransu 從本版起同時發行 Claude Code 與 Codex CLI 兩種變體。Claude 端是源頭，Codex 端是單向衍生產物。

- **Codex 變體目錄** — 整棵 Codex plugin tree 落在 `codex/`，獨立於 Claude 本體（`plugins/baransu/`），互不污染。
- **Repo-root marketplace catalog** — 新增 `.agents/plugins/marketplace.json`，讓使用者直接 `codex plugin marketplace add <git-url>` 即可安裝（不需 `--sparse` 或其他 flag）。
- **轉換工具 `/baransu:codex-skill-transfer`** — 一鍵把 Claude 端的 plugin / skills / marketplace 重生成 Codex 格式：
  - 自動轉 `disable-model-invocation` → `agents/openai.yaml`
  - 改寫 `$ARGUMENTS` 系列、bang-backtick shell injection 為 Codex 認得的自然語言
  - 描述超過 Codex 上限 1024 字元時自動剝除 Claude 觸發片語句子並收斂句尾
  - Plugin mode 自動產出 schema-合規的 marketplace catalog（`source` object 形、必選 `policy.installation` / `policy.authentication`、`category`）+ 巢狀 `plugins/<name>/` layout
- **Codex agent stubs** — `codex/plugins/baransu/.codex-agents-templates/` 內附 12 份 TOML stub，使用者自行複製到 `~/.codex/agents/` 啟用。
- **AGENTS.md** — Codex 版的 project-level instructions 檔，與 `CLAUDE.md` 對應。
- **README** — 新增 Codex CLI 安裝區（HTTPS / SSH / `--ref` pin tag）+「衍生產物別手改」警語。

### 修正

- 修掉 `codex-skill-transfer` SKILL.md 內殘留的 `` !`cmd` `` 字面 pattern，避免 slash-command 解析器把它當成 bash injection 而觸發 `command not found: cmd`。
- 修正 `grade` SKILL.md frontmatter — 描述含裸 colon（`tune_review_due: true`、`(00:00)`）導致 PyYAML 嚴格解析失敗。改用單引號包裹。

[1.1.12]: https://git.hy-tech.com.tw/ben.tsai/baransu/-/compare/1.1.4...1.1.12
