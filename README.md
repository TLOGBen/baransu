<p align="center">
  <img src="docs/images/hero.jpg" width="100%" alt="baransu 概念圖">
</p>

<h1 align="center">baransu</h1>

<p align="center"><b>バランス。動手前先想，做完後驗證。</b></p>

<p align="center">14 個 skill · Claude Code 與 Codex · v7.3.2</p>

---

該輕的任務走輕量路徑，該重的決策不省思考。平衡不是妥協，而是知道什麼時候可以輕、什麼時候不准輕。每個 skill 都畫清楚界線：什麼能省、什麼一定要做。

## 核心理念

每條理念都綁一個倉內機制錨點——無錨點的條款不入冊，錨點存在性由結構驗證器把關。

| 理念 | 一句話 | 機制錨點 |
|---|---|---|
| 規則是天花板 | 只寫防真實翻車的規則；容器只能變深、不能變長 | `plugins/baransu/rules/anti-patterns.md` |
| 結構是地板 | 確定性檢查全走腳本閘門，不靠模型自律；14 個技能是上限 | `scripts/verify-skills.py` |
| 人在授權點 | Input PAUSE 可走預設；Authorization PAUSE 不可覆寫 | `plugins/baransu/skills/_shared/loop-contract.md` |
| 證據優先 | 非顯然主張依賴前先引查證來源；乾淨的 review 也是有效的 review | `plugins/baransu/skills/review/SKILL.md` |
| 狀態落盤 | 長流程的結論落檔交付、不賭終端顯示 | `plugins/baransu/skills/_shared/output-journal.md` |

由來、上限的修憲紀錄與可證偽條款：[理念全文](docs/philosophy.md)。

## 五個家族

<table>
<tr>
<td width="300"><img src="docs/images/family-plan.png" width="280" alt="構想"></td>
<td>
<h3><a href="docs/skills/plan.md">構想</a></h3>
<p><i>動手之前，先把「要什麼」和「怎樣才算做完」說清楚。</i></p>
<b><code>/baransu:think</code></b>：復述對焦、表態、兩向攻擊，留一份計畫，不寫程式<br>
<b><code>/baransu:contract</code></b>：中型任務開工前，一頁釘死可斷言的驗收條文
</td>
</tr>
<tr>
<td width="300"><img src="docs/images/family-verify.png" width="280" alt="驗證"></td>
<td>
<h3><a href="docs/skills/verify.md">驗證</a></h3>
<p><i>換一雙乾淨的眼睛看，拿證據說話；乾淨的結果也是有效的結果。</i></p>
<b><code>/baransu:seal</code></b>：對著合約五點驗收，全清才蓋 sealed 標記<br>
<b><code>/baransu:review</code></b>：乾淨 context 的 verifier 獨立重驗任何產出，不改目標<br>
<b><code>/baransu:hunt</code></b>：從症狀追到根因，指到 file:line 才動手修
</td>
</tr>
<tr>
<td width="300"><img src="docs/images/family-make.png" width="280" alt="創作"></td>
<td>
<h3><a href="docs/skills/make.md">創作</a></h3>
<p><i>每個選擇都有理由：先出計畫，再動手，做完自己看過、評過再交。</i></p>
<b><code>/baransu:draw</code></b>：靜態圖、互動圖、程式渲染影片、可拖時間軸的說明頁<br>
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
<b><code>/baransu:learn</code></b>：評分篩選來源，整理成五欄摘要或完整大綱筆記
</td>
</tr>
<tr>
<td width="300"><img src="docs/images/family-ops.png" width="280" alt="維運"></td>
<td>
<h3><a href="docs/skills/ops.md">維運</a></h3>
<p><i>收好每一輪、照顧工具本身。</i></p>
<b><code>/baransu:ship</code></b>：歸檔工作檔、commit、push、清理 worktree<br>
<b><code>/baransu:health</code></b>：體檢專案的 agent 配置與 AI 可維護性<br>
<b><code>/baransu:evolve</code></b>：對固定標準一輪輪磨 SKILL.md，只留確有改進的改動<br>
<b><code>/baransu:codex-skill-transfer</code></b>：Claude／Codex 雙版本的移植對照與對齊檢查
</td>
</tr>
</table>

## 一件事怎麼走

```
小　單檔、範圍清楚     →  直接實作（紅綠紀律）
中　一個功能、幾個檔案 →  /contract  →  實作  →  /seal
大　多個互相依賴的模組 →  畫成決策圖、切片  →  每片走「中」
```

方向未定先 `/think`，出錯了 `/hunt`，想要第二雙眼睛 `/review`，收工 `/ship`。小任務不硬上全套，大任務不偷走輕量路。session 結束時，seal-guard hook 會擋下沒封緘的 user-facing 變更（可降級）。完整說明：[三頻段路由](docs/routing.md)。

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
> `/baransu:contract 匯出 CSV 時支援自訂欄位順序`，做完再 `/baransu:seal`
>
> 登入後偶爾白畫面，幫我排查　→ `/hunt`

## 更多

[文件索引](docs/README.md) · [安裝](docs/install.md) · [開發指南](docs/development.md) · [CHANGELOG](CHANGELOG.md) · [授權與第三方來源](docs/README.md#授權與第三方來源)
