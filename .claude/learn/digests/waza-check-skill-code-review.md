---
topic: "Waza /check skill — 出貨前 code review 流程設計"
sources:
  - slug: "check-review-before-you-ship"
    url: "https://github.com/tw93/Waza/blob/main/skills/check/SKILL.md"
created_at: "2026-05-14T03:30:29Z"
language: "zh"
phases_completed:
  - collect
  - digest
  - outline
  - fill_in
  - refine
---

# Waza /check skill — 出貨前 code review 流程設計

> 來源：tw93/Waza skills/check/SKILL.md v3.23.0（單一 spec 整理，未交叉比對其他 review skill）

## 1. Skill 定位與啟動邊界

/check 是 Waza 的 code-review skill，明確將自己框定在「程式 diff 與 release artifact 審查」之上，把「文件 / PDF / 白皮書 / 散文審稿」整批外送到 /write 的 Document Review Mode，不混在同一 skill 內。它與 Anthropic 內建 /review 命令並存：Waza 不重新觸發 /review，避免兩條 review pipeline 在同一回合疊加。命名上提供 `code-review` 別名，意圖讓使用者用語意化字串而非記憶 skill slug。

## 2. 多模式分派

/check 不只是「審 diff」單一動作，它在啟動時讀使用者第一句話判斷進入哪一個模式：

- **Plan Execution Mode**：當訊息以「按计划实施 / 整 / 可以干 / 直接改」或 /think 計畫連結開頭時，跳過 review，把計畫拆 to-do、逐項標記完成、最後跑專案 verification 命令；專案標示 review-then-ship 時自動轉 Ship。
- **Triage Mode**：訊息提到 issue / PR / batch / 批量處理時跳過 diff flow，改走 `gh issue list` + `gh log` 確認是否已修，依四種狀態（已 ship / 已合未 release / 未修 / 不合理）給出可立即執行的 disposition。
- **Release Worthiness Analysis**：使用者問「是否值得發版」時，跑 `git log <last-tag>..HEAD` 統計 feat / fix / chore 比例，輸出 verdict + 建議版號 bump + key risk 單句。
- **Ship / Release Follow-through**：在 review 之後接續處理 commit / tag / push / 回 issue / 發 release reaction，這個模式不取代 review，是 review 通過後的延伸。
- **Default Continuation**：當 AGENTS.md 或當前 thread 寫了 "ship if green" 之類字樣，review 通過直接轉 Ship 而不再次詢問。

這個分派機制把 review skill 從「單一 verb」擴展成「review + 一組可選後續動作」的小型 workflow。

## 3. Review 流程骨幹

進入正規 review 時，流程被明確分層：

1. **Project Context Extraction**：先讀 README / AGENTS.md / package manifest / CI workflow / release notes，把驗收命令、保護檔、release artifact、domain risk 與 public reply rule 萃取成 review 內部上下文；當專案文件明列 verification 命令時優先用該命令而非自動偵測。
2. **Scope 分檔**：以行數與檔案數把 diff 分成 Quick（<100 行、1–5 檔）/ Standard（100–500 行或 6–10 檔）/ Deep（500+ 行、10+ 檔，或觸及 auth / payment / data mutation），對應不同 reviewer 編制。
3. **Did We Build What Was Asked**：在讀程式碼前先比對 diff 與 goal，標記 on target / drift / incomplete；五項 drift 信號（無關檔案、純 refactor、未提及的新依賴、未要求的刪除、未必要的新抽象）任一觸發即標 drift。
4. **Hard Stops**：八類禁止項在 merge 前必須處理 — unverified claims（沒跑的不能寫 verified）、destructive auto-execution、release artifact 缺失、生成檔漂移、版本欄位 skew、diff 引用不存在的識別符、注入 / 認證問題、未預期的依賴變動。其中「unverified claims」直接綁住 sign-off 的 verification 欄位，迫使所有「I verified / tests pass」都要對應到本回合真的執行過的指令。
5. **Specialist Review**：Standard / Deep 才啟動，依 persona-catalog 平行派發專家審查；同位置高 severity 留下並標記跨審查者共識，不同位置同主題不算重複。
6. **Adversarial Pass**：僅 Deep 啟動，以「若我要透過此 diff 攻擊系統會打哪裡」為核心，從 assumption / composition / cascade / abuse 四個角度進攻，<0.60 confidence 直接抑制。

## 4. 自動修復分級

修復決策不是一個布林，而是四級：safe_auto（typo、缺 import、風格）立即套用；gated_auto（null check、加 error handling 等會改變行為的修補）批次成一個 confirmation block 而不是逐條問；manual（架構 / 行為 / 安全 trade-off）寫進 sign-off 等使用者判斷；advisory 純資訊註記。關鍵設計是「safe_auto 先全部套完、gated_auto 一次性確認」，避免使用者被多次中斷。

## 5. 知識同步與驗證閘

review 不只看程式，還看「這次 diff 是否引入新 invariant」：新 safety gate → AGENTS.md；新 UI 約束 → `.claude/rules/*.md`；新部署步驟 → AGENTS.md / docs/；新跨檔同步需求（enum ↔ HTML anchor、Swift key ↔ xcstrings）→ AGENTS.md。可以自動更新時走 safe_auto 套用，否則在 sign-off 寫 doc debt。Verification 階段必須真的執行（`bash scripts/run-tests.sh` 或專案指定命令），非零或 `(no test command detected)` 都不能算 done，且明文要求 bug fix 必須附「先在舊碼會 fail、修後 pass」的 regression test，否則該 fix 還沒結束。

## 6. Public Reply 規範

對外回覆有一套完整 shape：先用 `gh issue view --json author` 解析 `@<login>`；語言鏡像 opener（中/英對映，日韓 opener 用英文回，除非專案文件覆寫）；開頭一次致謝即止，禁止 closing thanks stack；一兩段純事實 + 阻塞點；最後必須給一個「綁定 release 或 verification」的下一步動作（下個 App Store / GitHub release、nightly 升級命令、要清的 cache 路徑、還缺什麼資訊）；更新措辭優先 PATCH 既有 comment 而非刪後重發。此 shape 在 AGENTS.md / CLAUDE.md 沒覆寫時是預設。

## 7. Sign-off 規格

固定 8 欄位輸出，使 review 結果可機器讀：files changed / scope / review depth / hard stops（找到 N、修了 N、deferred N）/ specialists（清單或 none）/ new tests / doc debt / verification（命令 → pass/fail）。Triage 模式追加一行 `triage: N reviewed, N closed, N deferred`。Ship 模式則收斂到 commit hash / tag / release URL / 版本結果 / 推送的分支 / release asset 狀態 / release reaction 狀態 / issue 狀態 / 剩餘 blocker。

## 8. 失誤備忘錄（Gotchas）

skill 把累積的失誤直接列在文件尾，作為防呆 checklist：跑 `gh issue view N` 確認標題避免認錯 issue；PR comment 寫 1–2 句自然短段落而非條列、不要結構化 AI 腔；新檔案命名前先看目錄現有 convention（`article.en.md` in `_posts_en/` 雙重後綴的教訓）；vercel 部署前 `vercel env ls` 對 key、新專案 push 前 `git remote -v` 確認 auth。這些不是規則，是有過真實傷口才寫進來的常駐 checklist。

## 對照 baransu 的可借鑑點

- /check 把 review 與 ship 的銜接寫進同一 skill（Plan / Triage / Release / Ship 多模式），baransu 則拆成 `/review` + `/ship` 兩個 skill；前者 cohesion 高、後者邊界更乾淨。
- Hard Stop「unverified claims」直接鎖死 sign-off verification 欄位，對應 baransu 「Read-before-write」與「Surgical Changes」精神，是值得在 baransu /review 的 review-agent.md 補強的硬閘。
- Sign-off 8 欄位是機器可讀產出範本，baransu /execute 的 final-report.md 可借鏡此結構化收斂格式。
