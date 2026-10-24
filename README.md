<p align="center">
  <img src="docs/images/hero.jpg" width="100%" alt="baransu 概念圖">
</p>

<h1 align="center">baransu</h1>

<p align="center"><b>バランス。動手前先想，做完後驗證。</b></p>

<p align="center">23 個 skill · Claude Code 與 Codex · v8.22.0</p>

Codex skill 圖示放在各 skill 的 `assets/`，由 `agents/openai.yaml` 引用。7.3.3 修正圖示路徑，既有安裝需更新 plugin。

---

該輕的任務走輕量路徑，該重的決策不省思考。平衡不是妥協，而是知道什麼時候可以輕、什麼時候不准輕。每個 skill 都畫清楚界線：什麼能省、什麼一定要做。

## 核心理念

每條理念都綁一個倉內機制錨點——無錨點的條款不入冊，錨點存在性由結構驗證器把關。

| 理念 | 一句話 | 機制錨點 |
|---|---|---|
| 規則是天花板 | 只寫防真實翻車的規則；容器只能變深、不能變長 | `plugins/baransu/rules/anti-patterns.md` |
| 結構是地板 | 確定性檢查全走腳本閘門，不靠模型自律 | `scripts/verify-skills.py` |
| 人在授權點 | Input PAUSE 可走預設；Authorization PAUSE 不可覆寫 | `plugins/baransu/skills/_shared/loop-contract.md` |
| 證據優先 | 非顯然主張依賴前先引查證來源；乾淨的 review 也是有效的 review | `plugins/baransu/skills/review/SKILL.md` |
| 你說的不算，證明它 | 說有問題的要跑出那個錯，說完成的要照使用者的方式跑給你看 | `plugins/baransu/skills/prove-it/SKILL.md` |
| 狀態落盤 | 長流程的結論落檔交付、不賭終端顯示 | `plugins/baransu/skills/_shared/output-journal.md` |

由來與完整說明：[理念全文](docs/philosophy.md)。

## 五個家族

<table>
<tr>
<td width="300"><img src="docs/images/family-plan.png" width="280" alt="構想"></td>
<td>
<h3><a href="docs/skills/plan.md">構想</a></h3>
<p><i>動手之前，先把「要什麼」和「怎樣才算做完」說清楚。</i></p>
<b><code>/baransu:think</code></b>：復述對焦、借鏡、表態、兩向攻擊，留一份計畫，不寫程式<br>
<b><code>/baransu:draft</code></b>：方向定了、形狀還不明顯時，先寫呼叫端用法，兩個互相看不到的設計者各畫一版，選定後把骨架（型別、簽名、未實作的本體）寫進 repo，當作實作的合約<br>
<b><code>/baransu:sayagain</code></b>：用白話重述你的目標和想解決的問題，讓你確認它懂了<br>
<b><code>/baransu:domain-modeling</code></b>：邊設計邊把專案用詞磨精確、寫進 <code>CONTEXT.md</code>，難回頭的決定記成 ADR
</td>
</tr>
<tr>
<td width="300"><img src="docs/images/family-verify.png" width="280" alt="驗證"></td>
<td>
<h3><a href="docs/skills/verify.md">驗證</a></h3>
<p><i>換一雙乾淨的眼睛看，拿證據說話；乾淨的結果也是有效的結果。</i></p>
<b><code>/baransu:review</code></b>：乾淨 context 的 reviewer 只讀不跑，找出每一個跟改動對不上的地方；判「成立」也要附原文，拿不準的列「不確定」，判定照規則算，不改目標<br>
<b><code>/baransu:prove-it</code></b>：照使用者的方式實際跑一次，證明說有問題的真的有問題、說完成的真的完成，留下 review 讀得到的執行紀錄<br>
<b><code>/baransu:hypothesis</code></b>：寫下假說，把系統該怎麼運作寫成機器窮舉檢查過的形式模型，附白話規則和一張張加元件的狀態圖；程式、偶發問題、需求文件、兩份文件對照都能當輸入，改了會自己維護<br>
<b><code>/baransu:hunt</code></b>：從症狀追到根因，指到 file:line 才動手修
</td>
</tr>
<tr>
<td width="300"><img src="docs/images/family-make.png" width="280" alt="創作"></td>
<td>
<h3><a href="docs/skills/make.md">創作</a></h3>
<p><i>每個選擇都有理由：先出計畫，再動手，做完自己看過、評過再交。</i></p>
<b><code>/baransu:draw</code></b>：靜態圖、互動圖、程式渲染影片、互動元件；要整頁時交 <code>/ui</code> 組<br>
<b><code>/baransu:ui</code></b>：為你 repo 裡的介面定調色字版，直接寫改 UI 檔<br>
<b><code>/baransu:write</code></b>：雙語潤稿、生成、校對，附每處改動理由
</td>
</tr>
<tr>
<td width="300"><img src="docs/images/family-learn.png" width="280" alt="學習"></td>
<td>
<h3><a href="docs/skills/learn.md">學習</a></h3>
<p><i>先把原文完整讀進來，再決定要不要消化成自己的筆記。</i></p>
<b><code>/baransu:read</code></b>：網頁、檔案、搜尋結果轉成 Markdown；加 <code>--save</code> 才存檔<br>
<b><code>/baransu:learn</code></b>：評分篩選來源，整理成五欄摘要或完整大綱筆記<br>
<b><code>/baransu:how</code></b>：講清楚一塊程式怎麼運作：流程、關鍵概念、檔案位置、陷阱<br>
<b><code>/baransu:why</code></b>：從 git 紀錄、計畫與對話查出程式為什麼長這樣，每條主張標信心、寫明查不到什麼<br>
<b><code>/baransu:teach-me</code></b>：用對話把一塊程式或一份筆記教到你真的懂，一次一層<br>
<b><code>/baransu:show-me</code></b>：用最小的一張圖把當下的重點畫出來（流程、結構、差異），只能手動叫用<br>
<b><code>/baransu:huh</code></b>：把上一則訊息用白話重講一次，不用術語<br>
<b><code>/baransu:what-now</code></b>：你離開一陣子回來時，白話講清楚這段期間變了什麼，再把等你決定的事逐項列好（附建議、根據與風險），只能手動叫用
</td>
</tr>
<tr>
<td width="300"><img src="docs/images/family-ops.png" width="280" alt="維運"></td>
<td>
<h3><a href="docs/skills/ops.md">維運</a></h3>
<p><i>收好每一輪、照顧工具本身。</i></p>
<b><code>/baransu:ship</code></b>：歸檔工作檔、commit、push、清理 worktree<br>
<b><code>/baransu:health</code></b>：體檢專案的 agent 配置與 AI 可維護性，依證據與風險、不依 repo 大小；同一個錯一直被糾正時，找出那類錯、在 repo 裡用結構或檢查擋掉，並在過去出錯那一版證明擋得住<br>
<b><code>/baransu:evolve</code></b>：對固定標準一輪輪磨 SKILL.md，把肇事條文重寫成正面定義而非加規則，找回不輸、花費不增才保留<br>
<b><code>/baransu:codex-skill-transfer</code></b>：Claude／Codex 雙版本的移植對照與對齊檢查
</td>
</tr>
</table>

## 一件事怎麼走

```
小　單檔、範圍清楚     →  直接實作（紅綠紀律）
中　一個功能、幾個檔案 →  （形狀不明顯先 /draft）直接實作（紅綠紀律）  →  /review 獨立重驗（要跑才知道的 → /prove-it）
大　多個互相依賴的模組 →  畫成決策圖、切片  →  每片走「中」
```

方向未定先 `/think`，形狀不明顯先 `/draft`，出錯了 `/hunt`，想要第二雙眼睛 `/review`，要實際跑一次證明 `/prove-it`，核心模組不能出錯或文件要查矛盾就寫下假說 `/hypothesis`，收工 `/ship`。小任務不硬上全套，大任務不偷走輕量路。完整說明：[三頻段路由](docs/routing.md)。

## 快速開始

**Claude Code**

```
/plugin marketplace add https://github.com/TLOGBen/baransu.git
/plugin install baransu@baransu
```

**Codex CLI**（衍生變體，`codex/` 子樹手動維護；skill 以 `$baransu:<name>` 呼叫）

```
codex plugin marketplace add https://github.com/TLOGBen/baransu.git
codex plugin add baransu@baransu
```

試試看：

> 想一下：通知系統要不要從輪詢改成 WebSocket？　→ `/think`
>
> 做完「匯出 CSV 時支援自訂欄位順序」之後：`/baransu:review 看一下這個 diff`
>
> 登入後偶爾白畫面，幫我排查　→ `/hunt`
>
> review 說匯出會漏最後一列，跑跑看是不是真的　→ `/prove-it`
>
> 撤回和核准同時按，偶爾還是會付款；這個簽核模組不能出錯　→ `/hypothesis`

## 更多

[文件索引](docs/README.md) · [安裝](docs/install.md) · [開發指南](docs/development.md) · [CHANGELOG](CHANGELOG.md) · [授權與第三方來源](docs/README.md#授權與第三方來源)
