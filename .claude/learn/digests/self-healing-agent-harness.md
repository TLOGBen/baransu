---
topic: "self-healing agent harness"
sources:
  - slug: "the-self-healing-agent-harness"
    url: "https://x.com/intuitiveml/status/2048912026018484317"
created_at: "2026-04-28T22:09:21+08:00"
language: "zh"
phases_completed:
  - collect
  - digest
  - outline
  - fill_in
  - refine
---

# self-healing agent harness — 學習筆記

## 0. 核心命題：為什麼這套東西存在

傳統 SaaS 把「模型評估」和「QA」分屬兩個團隊：模型評估歸 ML 或 data science，他們做 dashboard；QA 歸工程，他們開 ticket、修 bug、出 release。CREAO 跑 AI agent 產品時發現，這個分工在 AI-first 環境下行不通——一個壞回應對 user 而言就是「答得不好」，但根因可能落在六種地方任一個：模型推理失誤或幻覺、整合回了 500 或過期 token、infra 抖動（Cloudflare timeout、Postgres replica 延遲、ECS OOM）、上游 schema 改變導致 tool contract 漂移、prompt 或 RAG plumbing 壞掉、deploy 默默回退了某個小元件。對 grader 而言，這六種狀況也長一樣：messageId X 拿到低分。所以「打分」就是「開 bug」、「開 bug」就是「打分」，是同一個迴圈。

更進一步：AI 把 build time 從「月」壓到「小時」後，每個下游階段（eval、QA、release）都會變成新瓶頸。把 eval 與 QA 合併成單一 funnel，是跟得上 AI-speed 實作節奏的唯一辦法。這是整個 Harness 的設計動機。

## 1. 三件式 Harness 的全景

整套系統由三個元件構成，依「分數→修補→出貨」的順序串成一個自癒迴圈：

- **Grader**：跑在 live traffic 上的三家 judge panel，對每筆 agent response 評分，取代了人工 QA review 與 offline benchmark。
- **Engineering Pipeline**：六個每日 job，把 Grader 的低分轉成 Linear ticket、draft PR、verified fix，取代手動 triage、sprint planning 與 regression test。
- **Bridge**：AI-gated grey rollout，由 Grader 分數決定新 code 能不能擴大流量，取代 staging environment 與人工 release approval。

記這張地圖前先抓住一句話：**Grader 看，Pipeline 改，Bridge 守門**。下面三節分別拆解。

## 2. Component 1 — Grader：怎麼把「答得好不好」變成可信數字

### 2.1 觸發與 Sampling

每次 agent 回應後，系統打一個 async POST 到內部 grading endpoint，帶上 messageId、threadId、以及 fallback 後實際服務這次請求的模型。整段流程完全 out-of-band，不增加任何 user-facing latency。

Sampling 不是 flat rate，而是按模型分層：主力模型 Sonnet 4.6 抽 10%，所有少數或實驗模型（Opus、GPT、Gemini 等）抽 100%。理由很實際——主力模型的流量是其他模型的 24 倍，如果用同一個 sampling rate，少數模型的訊號會被淹沒，數小時內無法達到統計顯著、無法及時 gate rollout。**「按模型 sample，不要按流量 sample」是這套 harness 的第一條設計教訓。**

### 2.2 Job 0 — Categorical Router

在三家 judge 看到 transcript 之前，先有一個 lightweight classifier（Job 0）把這次互動歸到 12 個 domain 之一：coding、research、data analysis、task automation、agent building、artifact building、traditional app building、planning、writing、creative work、conversation、error recovery。

為什麼要先分類？因為「好的 coding 答案」和「好的 research 答案」紅線完全不同。分類後，每個 judge 拿到的是 category-conditioned rubric，而不是一張通用紅線表。這個設計把「打分」拆成兩階段——先決定「應該用哪一張尺」，再評分。

### 2.3 三家 Judge、三個 Persona

三家 judge 並行跑 Anthropic、OpenAI、Google 的模型，目的是降低 self-preference bias（模型評自家輸出會偏高）。所有 judge 經 AI Gateway 同時呼叫，單家慢或失敗只會降低該筆評分的 quorum size，不會卡住整個流程。

但 panel 一致也不代表自動可信——他們仍會抽樣把 verdict 送回給人類校準。**如果 judge consensus 與 human review 出現持續落差，會視為 rubric bug，不是可容忍誤差**。這是這套 harness 願意把控制權交給 AI 的前提。

每家 judge 都必須透過 schema-locked tool call `submit_evaluation` 回傳結構化結果。這個 tool 規定五個欄位：

- `reasoning`：2-3 句逐步推論
- `category`：被評估的 domain
- `quality`：excellent、good、acceptable、poor 四選一
- `issues`：從 9 項 taxonomy 抽（incomplete、hallucination、tool_misuse、missed_context……）
- `confidence`：0-1 浮點數

Schema-lock 的好處是 downstream 的所有計算（平均、聚類、severity）都建立在固定欄位上，不會因 judge 自由發揮而崩壞。

### 2.4 數學共識：把離散分數變連續訊號

`quality` 四個 enum 映射成 1-4 分，存活的 judge 取**平均**而不是投票。這個設計把離散四分變連續指標——3.33 vs 2.66 是有意義的差異，可以在小樣本就看出 per-model 趨勢，不需要等到投票數累積才能判讀。

Self-preference bias 還是會發生：Sonnet 評 Sonnet 大約偏高 0.3。但只要 OpenAI 與 Google 的 judge 用不同 expert persona 各自抓到同一個問題，bias 會被 quorum 洗掉。為了事後可審計，每家 judge 的單獨分數都會被持久化（`sonnet_quality`、`gpt_quality`、`gemini_quality`、`judge_count`），如果某家 judge 開始 drift，工程師可以重新 weight。

Grader 的最終 output 很簡潔：一條 stream，category-tag + judge-averaged 分數 + 對應 messageId。所有下游都吃這條 stream。

## 3. Component 2 — Engineering Pipeline：六個 Job，從分數到驗證過的修補

Grader 的低分如果只進 dashboard，就只是裝飾。Engineering Pipeline 是把分數轉成「已上 production 的 fix」的轉換器，每天跑六個 sequential job：

**Job 1 — Detect & Triage**：agent 把 grader 的 poor verdicts 抓出來聚類，再用一個 9 維 severity engine 對每個 cluster 打分：user impact、velocity、duration、alarm correlation、resource pressure、latency、4xx rate、blast radius、business criticality。過閾值才往下走，不過閾值的進入 trend log 留著看趨勢。

**Job 2 — Investigate**：對 top 3 cluster，agent 自己走 stack trace、拉 CloudWatch log、檢查近期 deploy、查 DB replica，組成完整 evidence bundle，再帶著推論的根因把 ticket 派給人。**人類拿到的不是「有問題」，而是「這裡有問題、證據在這、我猜是 X」**。

**Job 3 — Auto-Fix**：對 high-confidence、緊急的問題，系統自己開 branch、寫 fix、驗證、送 draft PR。但 ambition 必須被綁住，所以有三條 guardrail：

- 每次跑最多開 3 個 PR——reviewer 有上限，bot 洗版會把 review 預算燒光
- 任何 diff 碰到 `.env`、`.github/`、IAM policy 自動關閉
- Type error 與 failing test 阻擋送出

設計哲學很明確：auto-fix 不是來解決深層架構債，而是快速消滅明顯 bug，讓人類專注深度工作。

**Job 4 — Verify**：對已進入 In Review 的 ticket，系統查近 6 小時的 CloudWatch；如果該錯誤零次再現，就帶 telemetry evidence 自動關 ticket（evidence 直接貼進 comment）；若仍失敗則更新錯誤計數重跑。**「客觀證明 fix 有效」這件事完全自動化，不需要人手動 regression test。**

**Job 5 — Re-grade**：對已關閉的 cluster，後續 24 小時 sampling 拉到 100%。如果出現 regression，自動 reopen ticket 並 revert fix。

**Job 6 — Report**：每晚 digest 進 Linear 與 team 頻道：本日偵測 cluster 數、出貨 PR、被 revert 的 PR、各 category 的分數變化、per-model leaderboard。作者強調「dashboard 不是目的，它只是已發生事件的紀錄」——pipeline 的價值在 Job 1-5 的閉環，Report 只是 audit trail。

## 4. Component 3 — Bridge：用分數決定上不上線

前兩個元件處理「已上線的 bug」，Bridge 處理「即將上線的 bug」。

當你要換基礎模型、改核心 system prompt、或把大量新 tool 權限交給 agent 時，行為風險會陡升，這時直接推 100% production 是賭博。Bridge 的解法是**讓 Grader 的分數直接當 release gate，不要 staging、不要人工 approval、不要 PR 留言「LGTM」**。

機制如下：major agent change merge 時，系統把約 10% 真實流量導到新 variant，Grader 即時跑 head-to-head 比 baseline。然後走 promotion ladder：

- **Fail 條件**：panel 平均分數比 baseline 掉 ≥ 0.15（要求 p < 0.05、最少 200 互動的視窗），或者一個確定性的 bug hunter 偵測到該 cohort 出現 novel error cluster spike——任一觸發就中止 rollout、把流量切回穩定版、開一個 Linear ticket 進入 Job 1。**rollback 不是手動操作，是自動觸發的 ticket。**
- **Hold or improve**：cohort 自動放大 5% → 20% → 50% → 100%，每一階段都要過同一個 statistical test on fresh window。

這套機制的精神是：模型用真實流量自證安全，blast radius 由 cohort size 限制；不再依賴「人在 staging 點一點」這種低訊號的 sign-off。

## 5. 三條硬規則（踩雷後的體會）

作者把實戰學到的三條規則寫成「如果你要轉到 AI-first engineering workflow，請先抄下這幾條」：

**Grade the outcome, not the trajectory**。CREAO 早期會懲罰 agent「不必要的 tool call」，後來放棄了。agent 找到的非線性路徑常常很有效，刻意懲罰路徑反而拖累整體成效。**評估產出，不要管過程**——這跟近年 agentic 研究的方向一致。

**Sample by model, not by traffic**。Flat sampling 會讓主力模型的訊號淹沒所有少數模型，少數模型在你的數據裡就永遠看不見，自然永遠投資不足、永遠不會變強。

**A score with no ticket is a dashboard nobody looks at**。Grader 沒接 Engineering Pipeline 就只是 dashboard；Pipeline 沒 Grader 餵就是瞎子。**要嘛兩個都建，要嘛都別建**。這也是為什麼這篇文章把三件事一起寫，而不是只談「我們蓋了一個很厲害的 LLM-as-judge」。

還有一條補充規則放在文章開頭：**不要陷入「scientific correctness」辯論**。許多研究背景的人會爭論「agent-based evaluation 在方法學上夠不夠嚴謹」，但對 startup 而言這是 luxury：今天就能觸發修補的「足夠好的訊號」永遠勝過下季才上線的「無懈可擊 benchmark」。Grader 的目的不是發 paper、排榜，而是快速找出產品裡的 recurring issue。

## 6. 適用邊界（這套適合誰、不適合誰）

作者把目標讀者寫得很清楚：**AI-first startup**——99% 的 production code 由 AI 寫、每天部署 3-8 次的團隊。對這類團隊，「人工 staging + 人工 review」這條傳統路徑已經跟不上實作節奏，所以三件式 harness 是必須。

反過來，作者把「還在把 Copilot 接到舊 CI/CD + 手動 QA」的多數公司稱為 **AI-assisted、不是 AI-first**——他們在小時內寫 code 卻在數天內 test code，這套 harness 並非設計給他們。

⚠️ 學習這篇時建議帶著的問題（本文未直接回答）：

- Grader 誤判（false negative / false positive）導致的 fix revert，在實務上的成本曲線是什麼？
- 9 維 severity engine 的權重怎麼來的？是經驗試錯，還是有資料驅動的調整機制？
- 三家 judge 的 inference cost 在 100% sampling 少數模型時佔總成本多少？
- 換到非 startup 場景（regulated industry、有合規要求的 release flow），這套 harness 哪些部分可以保留、哪些必須被人工 gate 取代？

如果要做選型而不是純粹學習一家公司的做法，建議拿這份筆記去對照你已經抓回來的 Anthropic `harness-design-long-running-apps`、LangChain `context-engineering-langchain`、JetBrains `jetbrains-smarter-context-management` 等資料交叉看。

---

## 一頁速記（複習用）

- **動機**：AI 把 build 時間壓到小時，eval 與 QA 必須合併成單一 funnel。
- **三件式**：Grader（眼）→ Engineering Pipeline（手）→ Bridge（守門）。
- **Grader**：async、不影響 latency；按模型 sample（主力 10%、少數 100%）；Job 0 先分 12 類；三家並行 + schema-locked tool call；分數取平均不投票。
- **Pipeline**：Detect → Investigate → Auto-Fix（最多 3 PR、`.env`/IAM 自動擋）→ Verify（CloudWatch 6 小時零再現）→ Re-grade（24 小時 100% sampling）→ Report。
- **Bridge**：10% cohort head-to-head；掉 0.15 + p < 0.05 + 200 互動視窗 → rollback；過則 5/20/50/100% 階梯。
- **硬規則**：評產出不評路徑；按模型 sample；分數沒 ticket = 廢；別陷入 scientific correctness 辯論。
- **邊界**：給 AI-first startup，不給 AI-assisted 的傳統 SaaS。
