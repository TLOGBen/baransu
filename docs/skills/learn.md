# 學習家族：read · learn

<img src="../images/family-learn.png" width="320" alt="學習家族概念圖">

> 先把原文完整讀進來，再決定要不要消化成自己的筆記。

`/read` 負責讀取與（選用的）保存；`/learn` 負責評分、篩選、整理成學習筆記。

[← 回文件索引](../README.md)

---

## `/read`

Claude Code：`/baransu:read`　Codex：`$baransu:read`

**用途**　萬用讀取：URL／路徑／glob／Chrome／剪貼簿轉成 Markdown 給 Claude 讀；加 `--save` 才存成離線檔。

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
