---
name: review
description: Independent multi-perspective re-verification of any model output — code diff, file set, directory, /think's approved plan, a bare claim. Dispatches isolated perspective agents (architecture / quality / security) in clean Task contexts to surface hallucinations, drift, over-engineering, and unnecessary complexity. Findings flow through a four-level response — direct fix for cosmetic stuff, packaged confirm for non-semantic, ask user for judgement, FYI for the rest. Balance check is mandatory on every new-work proposal. Code targets need e2e-run evidence; without it, not finished. Use when a model has just declared something done after a long-running or multi-turn session, or when the user wants a surgical second opinion on a prior actor's work. User-facing output is in Traditional Chinese (繁體中文).
---

# review — 乾淨視角複審

模型剛宣稱自己做完某件事時，不適合自己驗證自己：慣性與上下文汙染會讓它確認自己的假設。`/review` 是反制 —— 派出隔離的視角，用乾淨眼睛重讀一遍。

本 skill 不是一個大而全的 reviewer，是**任務分析師 + 派遣器**。它把 target 拆成清單、依行為決定派誰、讓被派的人隔離獨立思考、回來後用天平檢視是否過度處理、分四級施工。

感覺上像一個很有經驗的專家群，協助你 review 並順手處理掉能處理的東西。

Body is English (agent-facing). All user-facing output is in **Traditional Chinese (繁體中文)**.

---

## 三個視角（agent 檔）

`plugins/baransu/agents/architecture-reviewer.md` / `quality-reviewer.md` / `security-reviewer.md`。

每個 agent 寫「視角 / 目標 / 通用原則」—— 再加一段「禁忌」界定不侵入另一視角的範圍。**不是人設**。人設式描述（"你是資深 XX 工程師"）只誘發幻覺；我們要的是看 target 的角度，不是角色。

---

## Stage 1 — 條列 checklist

第一件事：把 target 宣稱做了什麼、決定了什麼、不做什麼、延後什麼 —— 逐條列出。這是後續 review 的對照基準。**沒有 checklist 的審核會滑向自由發揮，留不下抓幻覺的錨點。**

target 可以是任意形狀：
- git diff / 檔案集 / 目錄 / 未 commit 變更
- /think 的 5-section 計畫、設計文件
- 一句宣稱 + 它所指的 code（"這個函式 thread-safe"）

從哪種形狀拉 claim：commit message / docstring / 章節標題 / 宣稱本身。拉不出來就如實寫「no explicit claim for <area>」—— 不自己編。

checklist 會隨 target 傳給每個被派的 reviewer。

---

## Stage 2 — 分級

| 規模 | 配置 | 對抗測試 |
|---|---|---|
| ≤ 100 行 | 依 target 性質挑一個視角（快速審） | 跳過 |
| 100–500 行 | 加入相關視角（通常 2 個） | 跨層級時跑一輪 |
| > 500 行 | 看跨檔範圍與層級分配全部視角 | 一輪 |

處於邊界時往上靠一階。對 plan 型 target，用「獨立決策點數 × 章節數」作為粗估 LOC 的替代。

---

## Stage 3 — 激活（看行為，不看關鍵詞）

視角是否出場，看 target 的**實際行為**，不看 invocation 文字用了哪些字：

- **品質視角**：target 含可執行程式 / 要驗證的聲明 / plan 宣稱做了什麼
- **架構視角**：跨檔變動 / 新模組邊界 / 契約變更 / plan 多章節間相互依賴
- **安全視角**：target **行為上**涉及外部輸入、認證授權、秘密處理、跨信任邊界傳遞 —— 不看 target 文字提到哪些字

Plan / claim 型 target 預設啟用架構 + 品質；安全僅在 plan 明確描述上述行為時才啟用。

如果 Stage 2 的 tier 與激活數量衝突（例：100 行碰到兩個激活），以激活為準、tier 數字是上限 guideline，不是硬卡。

---

## Stage 4 — 派遣

對每個激活的視角發一個**平行 Task**，乾淨 context 中隔離執行。帶給它：target 的內容 + Stage 1 的 checklist。reviewer 不知道彼此的存在，不協調。

finding 回來時每條自然語言即可，需含：citation（file:line 或 section）、違反了哪條 checklist（或「無，屬觀察」）、觀察、手術刀修法、**天平筆記**（見 Stage 6）。

不強制 YAML 或 JSON —— reviewer 是人類視角，不是 API。

---

## Stage 5 — 對抗測試（條件性）

規模 > 500 行或跨層級變更時加一輪。一次 Task，六個角度：

1. **違反假設** — target 有哪些沒講的前提？其中一個為假時還成立嗎？
2. **組合失敗** — 哪組輸入 / 事件 / 狀態一起發生時拆掉 target？
3. **上下級串聯錯** — 每層 local 對、但整串走下來語意跑掉？
4. **濫用場景** — 非惡意使用者走錯路時 target 做什麼？
5. **根因辨識** — reviewer 找到的問題是根因還是症狀？
6. **共識幻覺** — 如果 reviewer 都同意某事，是因為真對、還是因為共享訓練偏見？

對 plan 型 target，同六角度用 plan 語彙讀：章節前提、章節互斥、決策鏈、讀者誤讀、因果倒反、表面完整性的幻覺。

對抗的產出**補強**既有 finding，不覆蓋。

---

## Stage 6 — 彙整 + 天平檢視

**去重**：同 citation + 同觀察合併，歸給最窄覆蓋的視角。

**天平檢視（最重要）**：每條提議新工作的 finding 必須能回答：
- 不做會得到什麼 / 失去什麼？
- 做了會得到什麼 / 失去什麼？
- 有沒有更小、更平衡的中間方案？
- 這是修問題 —— 還是 reviewer 偏愛另一種風格？

**複雜度需要自己證明價值。** 推廣式重構、「為未來擴展」式建議、無具體可重現條件的 concern —— 答不出三問的一律降為參考級。

這步存在的理由：reviewer 們會過度保守或過度激進；「手術刀般精準，剛好處理掉問題」是本 skill 與一般 reviewer 的差別。

---

## Stage 7 — 四級施工

| 等級 | 處理 |
|---|---|
| **直接修** | 格式、import 順序、未用 import、明顯 typo、dead import。不動行為邏輯 —— 直接 Edit。 |
| **打包確認** | 非語意但超出直接修的（改名、刪死碼、semantic typo）。一次批次 diff 給你看。 |
| **需判斷** | 邏輯 / 邊界 / API / 行為 / 安全類，有具體修法的。用 AskUserQuestion 批次問 —— 自然主題分群，不為湊數拆或合。 |
| **僅供參考** | 天平降級過的、無具體修法的、「考慮過但不建議做」的。寫在報告裡，不打擾你。 |

**不越權改行為邏輯。** 任何動到控制流、邊界、API 形狀、狀態的變更 —— 即使 reviewer 高信心 —— 一律走打包確認或需判斷。

**不為小事一個一個來問。** 需判斷等級按主題批次，不按 finding 數量線性展開。

---

## 硬要求：e2e

target 含可執行程式時，必須確認 e2e 跑過。Session 裡沒有綠燈 PASS 證據 → 不准說完成；結論欄需明寫「未完成，等 e2e」。

Plan / claim / pure doc 型 target 此條不適用（明確寫 n/a + 理由）。

---

## 輸出

繁中報告，自然語言結構：

- **結論一句話**（是否完成 / 需介入 / 未完成）
- **target 與範圍**
- **checklist（claim）**
- **派遣了誰、為什麼**
- **四級 findings**（哪些已修 / 哪些等你確認 / 哪些需你判斷 / 哪些僅供參考）
- **e2e 狀態**

不用 verdict enum、不用 YAML、不用模板骨架 —— 一份人類工程師讀得下去的 review 長什麼樣就那樣。

---

## 核心約束

- **視角不是人設** —— agent 檔不得出現「你是資深 XX」類角色描述。
- **激活看行為不看關鍵詞** —— 不 match invocation 字串。
- **天平檢視強制** —— 提議新工作的 finding 若答不出三問，降為參考。
- **不越權改行為** —— 自動修復只碰純格式 / import / typo / dead import。
- **不遞迴** —— `/review` 不呼叫 `/review`；對抗測試每次最多一輪；reviewer 不互審。
- **Code target 沒 e2e 綠燈不准說完成。**
