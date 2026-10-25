# 學習家族：read · learn · how · why · teach-me · show-me · what-now

<img src="../images/family-learn.png" width="320" alt="學習家族概念圖">

> 先把原文完整讀進來，再決定要不要消化成自己的筆記。

`/read` 負責讀取與（選用的）保存；`/learn` 負責評分、篩選、整理成學習筆記。`/how` 和 `/why` 把對象換成你 repo 裡的程式：一個講怎麼運作，一個查為什麼長這樣；`/teach-me` 把它們查到的東西，或一份 `/learn` 筆記，用對話教到你懂。

[← 回文件索引](../README.md)

---

## `/read`

Claude Code：`/baransu:read`　Codex：`$baransu:read`

**用途**　萬用讀取：URL／路徑／glob／Chrome／剪貼簿轉成 Markdown 給 Claude 讀；加 `--save`、說要存，或其他 skill（例如 `/learn`）之後要用時，才存成離線檔。只給關鍵字時會自己選來源：要論文走 `--topic`、找工具或 repo 走 `--gh`、想看大家怎麼說走 `--x`，其他走 `--web`。本地抓取失敗時，只有這次自己從公開搜尋找到的網址（`--web`、`--topic` 的候選、doi.org 連結）會自動改走 `--use-proxy`，送出前先告訴你；你自己貼的網址一定要你打 `--use-proxy` 才送，因為分享連結的鑰匙常藏在網址裡；帶登入資訊或內網的網址永遠不送代理。只有你指著瀏覽器裡開著的那頁時，才自動用 `--chrome`。

**什麼時候用**
- 想抓網頁、PDF、文件來讀或轉檔。
- 觸發語：`/read`、抓網頁、看一下這篇、轉成 markdown、存下來、存檔。
- 參數：`[URL | 路徑 | glob | --topic '關鍵字' | --web '關鍵字' | --gh '關鍵字' | --x '關鍵字' | --chrome | --clipboard] [--save] [--use-proxy]`

**兩種模式**

| 模式 | 做什麼 | 磁碟上留下什麼 |
|---|---|---|
| peek（預設） | 轉成 Markdown 讀進對話，回報標題、來源、字數 | 什麼都不留；暫存目錄刪除，`.claude/read/` 不動 |
| save（`--save` 或明確要求保存） | 另外存成離線 Markdown，圖片下載到本機 | `.claude/read/material/{slug}/index.md`（含 frontmatter）＋ `assets/`、`.claude/read/index.md` 索引列、不可變的原文 `raw/{slug}/` |

**注意**　`raw/` 一經寫入就不再改：重抓會版本化成 `raw/{slug}_vN`，連鎖抓取先寫暫存再搬入。轉檔用 markitdown；Chrome 是選用依賴，用到才檢查。

**不適用**
- 消化成筆記 → `/learn`
- 畫成圖、地圖或動畫 → `/draw`

**非互動驅動**　`loop=drivable`。

---

## `/learn`

Claude Code：`/baransu:learn`　Codex：`$baransu:learn`

**用途**　把素材整理成五欄重點摘要，可續寫成完整大綱筆記。

**什麼時候用**
- 想把來源消化成學習筆記。
- 觸發語：`/learn`、研究主題、整理筆記、學一下。
- 參數：`[URL... | --topic '關鍵字' | slug... | 混合]`（slug 指 `/read --save` 存下的素材）

**流程**　Collect（收集）→ Digest（逐源評分、使用者確認篩選）→ Outline（大綱）→ Fill In（逐段撰寫、遇缺口回頭補源）→ Refine。`--brief` 在 Digest 停下。

**產出**
- `--brief`：`.claude/learn/briefs/{slug}.md`，每個來源一份五欄摘要。
- 完整路徑：`.claude/learn/digests/{slug}.md`，結尾必有「批判層」四段——來源矛盾點／缺少資訊與盲點／各來源信度評分／建議後續調查角度。沒有矛盾也要明寫「查無矛盾」，不能留白。

**不適用**
- 只要離線原文、不要筆記 → `/read --save`
- 畫成圖、地圖或動畫 → `/draw`

**非互動驅動**　`loop=drivable`。

---

## `/how`

Claude Code：`/baransu:how`　Codex：`$baransu:how`

**用途**　用資深工程師帶人上手的程度，講清楚一塊程式怎麼運作：流程、關鍵概念、檔案位置、陷阱，以及照現有分層某個東西屬於哪一層。

**什麼時候用**
- 要改一塊陌生的程式之前，想先建立腦中的模型。
- 觸發語：`/how`、這怎麼運作、帶我看這塊、這屬於哪一層、how does X work、walk me through。
- 參數：`<子系統 | 檔案 | 符號 | 問題>`

**流程**　先自己讀入口檔；剩下的一次讀得完就直接講，分得出兩塊以上才派 2–4 個唯讀子代理分頭追，再對照程式碼調和。程式碼看不出行為時，可以跑唯讀指令或在 repo 外做拋棄式實驗。

**產出**　對話裡的說明：概觀、關鍵概念、怎麼運作（每步附 `file:line`）、東西放在哪、陷阱、還沒弄清楚。不寫檔。

**不適用**
- 想知道為什麼這樣寫 → `/why`
- 現在壞掉了 → `/hunt`
- 該放哪一層有取捨要決定 → `/think`

**非互動驅動**　`loop=drivable`。

**來源**　改編自 Cursor pstack 的 how（MIT），見 `plugins/baransu/skills/how/NOTICE.md`。

---

## `/why`

Claude Code：`/baransu:why`　Codex：`$baransu:why`

**用途**　查出一段程式、一個寫法或一個設計決定為什麼長這樣，每條主張都附出處並標信心等級，也寫明查不到什麼。

**什麼時候用**
- 想改一段看不懂用意的程式之前；想知道當初為什麼選這個做法。
- 觸發語：`/why`、為什麼這樣寫、當初為什麼、這段的由來、design rationale。
- 參數：`<file:line | 符號 | 決定> [問題]`

**流程**　先建錨點（相關檔案、最後碰過它的 commit、PR、日期、session 連結），再由近到遠查四類證據：repo 紀錄（commit、PR、CHANGELOG、指示檔的歷史）→ agent 決策紀錄（ADR、`CONTEXT.md`、`.claude/` 計畫與 git 歷史裡已移除的計畫、記憶檔、本機 log、對話紀錄）→ 有線索指向時才查的外部文件（Notion、Google Drive、Gmail 等）→ 上游資料（一頁文件或一次重現）。只有查外部文件才派唯讀子代理。

**產出**　對話裡的回答：問題、程式在哪、找到什麼（Direct／Supported）、合理推論、其他可能的解釋、不知道什麼、查了哪些來源、信心總結；問題是改動前的準備時，附「保留／可改／避開／風險」清單給 `/think` 當前提。不寫檔。

**不適用**
- 現在壞掉、回歸 → `/hunt`
- 程式怎麼運作 → `/how`
- 要不要改 → `/think`

**非互動驅動**　`loop=drivable`。

**來源**　改編自 Cursor pstack 的 why（MIT），見 `plugins/baransu/skills/why/NOTICE.md`。

---

## `/teach-me`

Claude Code：`/baransu:teach-me`　Codex：`$baransu:teach-me`

**用途**　把一塊程式、一個改動，或一份 `/learn` 筆記，用對話教到你真的懂。

**什麼時候用**
- 想真的搞懂一塊東西，而不是拿到一份參考資料。
- 觸發語：`/teach-me`、教我、讓我真的懂、解釋給我聽、teach me、help me understand。
- 參數：`<程式 | 改動 | 子系統 | .claude/learn 筆記 | 主題>`

**流程**　先從對話判斷你需要帶走哪幾件事；程式交給 `/how` 和 `/why` 去查，repo 外的主題用現有的 `/learn` 筆記，沒有就先跑 `/learn --brief`。先給白話定義，第一次只給最小完整的答案，你想深入再加一層；三個部件以上的流程用逐張累加的圖。

**產出**　對話，本身不寫檔。repo 外的主題沒有現成筆記時，會先交給 `/learn --brief` 寫一份 brief（存在 `.claude/learn/briefs/`）；其他要留下的筆記也交給 `/learn`。`/learn` 寫完筆記時也會提示可以用 `/teach-me` 讀懂它。

**不適用**
- 只是要把上一則訊息講白話 → `/huh`
- 要整理成筆記 → `/learn`

**非互動驅動**　`loop=not-drivable`（對話本身就是產品）。

**來源**　改編自 Cursor pstack 的 teach（MIT），改名為 teach-me，見 `plugins/baransu/skills/teach-me/NOTICE.md`。

## `/show-me`

Claude Code：`/baransu:show-me`　Codex：`$baransu:show-me`

**用途**　用最小的一張圖，把當下卡住的那個點畫出來：pseudocode、呼叫樹、元件樹、檔案樹、diff、Mermaid 圖，或一個聚焦的 HTML 頁面。

**什麼時候用**
- 大致懂了，只想一眼看清某個流程、結構或差異。
- 只能手動叫用（Claude Code）：`/show-me`、`/baransu:show-me`；模型不會自己觸發。Codex 版沒有這個限制。

**流程**　挑能講清楚重點的最小畫面，配一兩句說明；介面有能在對話裡直接畫圖的工具時，每張圖都用它畫；Mermaid 只在介面會畫出來的地方才算圖；都沒有時，Mermaid 畫不清楚的 UI、版面、狀態比較或太密的概念，才做一個 HTML 頁面（`.claude/show-me/` 底下）並用瀏覽器打開。畫完就停，不接著做原本的工作。

**產出**　回覆本身；需要時 `.claude/show-me/*.html`。

**不適用**
- 要從頭教到懂 → `/teach-me`
- 要一張完整的獨立圖、架構圖或影片 → `/draw`
- 只是要把上一則講白話 → `/huh`

**非互動驅動**　`loop=not-drivable`。

**來源**　改編自 HumanLayer skills 的 show-me（MIT），見 `plugins/baransu/skills/show-me/NOTICE.md`。

## `/what-now`

Claude Code：`/baransu:what-now`　Codex：`$baransu:what-now`

**用途**　你離開一陣子回來，用白話告訴你從你上一則訊息到現在變了什麼，再把只有你能決定的事一項一項列好：每項附 Claude 的建議、根據和風險，讀完回覆就能決定。

**什麼時候用**
- 交代完事情去忙別的，回來想知道進度、有沒有東西在等你。
- 只能手動叫用（Claude Code）：`/what-now`、`/baransu:what-now`；模型不會自己觸發。Codex 版沒有這個限制。

**流程**　只讀不改：整理這段期間自己和 subagent 做了什麼、別人說了什麼，重新查一次 PR、CI、agent 的現況，數字逐一對過來源。回覆先用一句話說有沒有事在等你，接著是截圖或一張小圖，再一行一件講你交代的每件事做到哪，最後列待決事項。

**產出**　回覆本身，不寫檔。

**不適用**
- 只是要把上一則講白話 → `/huh`
- 想確認 Claude 懂不懂你的目標 → `/sayagain`
- 只想把某個點畫成圖 → `/show-me`

**非互動驅動**　`loop=not-drivable`。

**來源**　改編自 Cursor pstack 的 ketchup（MIT），見 `plugins/baransu/skills/what-now/NOTICE.md`。
