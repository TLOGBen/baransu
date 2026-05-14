---
topic: "Waza /think skill — 動手前的設計與驗證規範"
sources:
  - slug: "think-design-and-validate-before-you-build"
    url: "https://github.com/tw93/Waza/blob/main/skills/think"
created_at: "2026-05-14T03:30:52Z"
language: "zh"
phases_completed:
  - collect
  - digest
  - outline
  - fill_in
  - refine
---

# Waza /think Skill — 動手前的設計與驗證規範

`/think` 是把粗略構想轉成「已核可方案」的設計階段技能。在使用者明確核可之前，不寫程式、不搭骨架、不貼偽碼。核心立場是：先表態，再列出能改變立場的證據；不用「這很有趣」「有很多方法」「你可以考慮」這類迴避式語句填充。

## 三種工作模式

### Lightweight Mode（修補式）
觸發條件：問題已被定義、開放議題僅為「怎麼修」。輸出是一條 2-3 句的單一推薦修法（改什麼、檔案：行號、為何），先報暴力解作預設，列出涉及檔案（>5 則明示），點出一項風險，等待核可後才動手。途中發現 3 個以上具實質取捨的不同路徑，升級為 Full Mode。

### Evaluation Mode（價值判斷）
觸發條件：「是否該存在／保留／曝光／刪除」的問題（「判断一下」「有没有必要」「值不值得」「should we keep this」等）。輸出格式為單行裁決 **Kill / Keep / Pivot**，後接三項基於使用者實際限制（時間、動機、商業模式、維護成本）的理由。Pivot 須列出具體可動方向；Kill 或重大重做須先列影響範圍（檔案、依賴者、遷移成本）再請使用者確認。不沿用 build-plan 模板、不列選項，只給一個裁決。

**關鍵分辨**：Lightweight 回答「怎麼修」（方法層），Evaluation 回答「該不該存在」（價值層）。若觸發是「判断一下这个报错」，那其實是 debug 場景，應走 `/hunt` 而非 Evaluation。

### Full Mode（隱式）
當問題不屬上述兩種、或 Lightweight 升級觸發成立時進入。Full Mode 走完整提案、驗證、交付流程（下節描述）。

## 動手前的環境檢查

讀任何程式碼之前，必須：

- 確認工作路徑（`pwd` 或 `git rev-parse --show-toplevel`）—— 不要假設 `~/project` 與 `~/www/project` 是同一份倉庫。
- 若專案存在 ADR、設計文件或 issue 討論串，先掃過與當前問題對應的紀錄。
- 若方案牽涉預設值、環境變數或設定欄位，**打開實際設定檔（`pake.json`、`tauri.conf.json`、`package.json`、`.env`）取真值**，絕不從記憶或文件複誦。

## 持久脈絡（Durable Context）預檢

僅在使用者提及記憶／預覽／先前決策／提供記憶路徑，或專案曝露明顯的本地記憶摘要時啟動。讀取順序：使用者指定路徑 → 當前專案 → 全域偏好；先列標題，至多打開 1-2 份相關摘要。跨專案條目視為可遷移模式，不直接套用。

**記憶類型映射**：
- `decision`、`preference`、`principle` → 規劃約束
- `pattern`、`learning` → 設計檢查
- `fact` → 必須以當前狀態驗證後才能影響方案

**現況優先**：當前 repo 狀態、活文件、log、test、遠端狀態皆覆寫記憶；衝突時必須點名衝突並走當前狀態，不可靜默選邊。輸出方案前掃描 `AGENTS.md`、`CLAUDE.md`、`.claude/rules/*.md`，若提案違反「hard rule / never / must / prefer」，須在輸出中以一句話揭露衝突並建議解法——不靜默繞過；若規則直接阻擋方案，停下並請示。

## 官方解優先

在提自製方案之前，先搜尋框架內建功能、官方範式與生態標準；可用 Context7 MCP 查最新文件。若有官方解，預設選它；除非能說清楚它對當前情境不足，否則不應另起爐灶。

## 提案規範

只給**一個**推薦方案及理由（成效、風險、所依託的既有程式碼）。只有當取捨真的接近（>40% 機率使用者會偏好替代）時才提一條 alternative；無論如何附上一個最小化選項。

對推薦方案必須點出最脆弱的假設（**premise collapse**）：「本案假設 X。若 X 不成立，則 Y。」若該假設關鍵且脆弱，調整設計使其能在假設失敗時仍能存活。

**Blocking ambiguities**：當需求存在使用者必須拍板的衝突（兩個矛盾來源、兩個有顯著成本差的有效解讀），須以一句話點名衝突並請示優先順序——**不可靜默選擇**。

**Attack angles**（僅在牽涉外部依賴、高併發、資料遷移時啟動）：

| 攻擊角度 | 提問 |
|---|---|
| 依賴失效 | 外部 API/服務/工具掛了，方案能優雅退化嗎？ |
| 規模爆量 | 10× 資料量或使用者負載時，哪一步先壞？ |
| 回滾代價 | 方向錯了之後，能回到什麼狀態？多難回？ |

若 attack 成立但能調整設計倖存，調整之；若擊潰整個方案，放棄並告知使用者原因。**絕不在未揭露失敗的情況下提出受過攻擊的方案**。

被否決時，問清具體哪裡不行、以收斂後的限制再進入——不要從零重來。

## 交付前驗證

- 超過 8 個檔案或新增 1 個 service？明示。
- 超過 3 個元件互換資料？畫 ASCII 圖，找出循環。
- 列出所有有意義的測試路徑：happy path / errors / edge cases。
- 能否在不動資料的前提下回滾？
- 列出所有 API key、token、第三方帳號（一句話說明）——禁止實作中途才索取。
- 每一個 MCP server、外部 API、第三方 CLI 都已驗證可達。

**已核可方案內禁止 placeholder**：TBD、TODO、「之後實作」、「同步驟 N」、「待定」皆屬禁止形態。帶 placeholder 的方案就是「之後再規劃」的空頭支票。

## Implementation Handoff

一份已完成方案必須能由另一位工程師或 agent 直接執行而無需再次決策。內容須含：

- 範圍與非範圍（scope / non-scope）
- 所選方案，以及（若取捨接近）被否決的替代方案
- 公開 API、schema、command、config、檔案介面變更
- 驗證指令與人工驗收檢查
- 發佈、發行、遷移、issue/PR 後續步驟
- 任何會改變外部狀態的步驟之回滾或失敗處理

當使用者後續說「Implement the plan」「可以干」「直接改」「整」或同義詞，視為核可。**不要再次辯論設計**；點名執行哪份方案、檢查 repo drift，然後動工。若環境變動使方案不再安全，點名具體 drift 並停手。

## Gotchas（10 條代表案例）

| 情境 | 規則 |
|------|------|
| 檔案移到 `~/project`，但 repo 在 `~/www/project` | 第一個 fs 操作前先 `pwd` |
| 三步實作後才要 API key | 交付前列盡所有依賴 |
| 「just do it」式核可 | 視為對推薦選項的核可；點名被選的選項並收尾，不在 `/think` 內實作 |
| 規劃了 MCP workflow 卻沒檢查 MCP 是否載入 | 交付前驗證工具可用性，非實作中途 |
| 被否決就從零重來 | 問清具體哪裡不行、以收斂後的限制再進入 |
| 「只是修 X」就跳過 /think | 若修動 3+ 檔或需方法選擇，暫停並走 Lightweight Mode |
| 已核可方案又被反覆辯論 | 執行已核可方案；只為 repo drift / 缺權限 / 外部狀態不安全停手 |
| 沒檢查地區／locale 變體就動 API | 寫整合碼前先列地區差異 |
| 把第二種語言／runtime 引入單一 stack 專案 | 沒有明確核可，不加新語言或 runtime |
| 「判断一下这个报错」走進 Evaluation Mode | 「判断一下」+ 錯誤上下文 = debug，走 `/hunt`；Evaluation 僅限價值/存在判斷 |

## 輸出格式

**Approved design summary** 必含：

- **Building**：這是什麼（1 段）
- **Not building**：明示 out-of-scope
- **Approach**：所選方案與理由
- **Key decisions**：3-5 條，附推理
- **Unknowns**：只放被明確延後、有理由與 owner 的項目；不放模糊缺口；若 unknown 阻擋決策，回頭重新逼近核可

核可後止步，實作另起一輪。

## After Approval

核可後輸出（2-3 句內）：

```
Plan approved. To implement: say "implement this plan". After implementation, run `/check` to review before merging or release follow-through.
```

由使用者決定何時動手。

---

## 與 baransu /think 的對照觀察

Waza `/think` 與本專案的 `/baransu:think` 走相同主幹（核可前不寫碼、強推單一方案、揭露脆弱假設），但 Waza 多了三個值得借鏡的細節：

1. **Evaluation Mode 的 Kill / Keep / Pivot 三裁決**——將「值不值得繼續」這類純價值判斷與「怎麼修」「怎麼蓋」徹底分離，避免 build-plan 模板污染價值對話。
2. **記憶類型映射為規劃約束 / 設計檢查 / 待驗事實三層**——讓 durable context 與當前狀態的衝突有明確仲裁順位。
3. **Gotchas 表將反例與規則並列**——把抽象原則錨定到具體錯誤情境，比純規則文字更易被記住與套用。

[source: think-design-and-validate-before-you-build]
