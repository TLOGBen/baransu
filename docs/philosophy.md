# 理念：バランス

> バランス。動手前先想，做完後驗證。

[← 回文件索引](README.md)

## 由來

市面上的 skill 很多，用起來卻都不對勁：要嘛什麼都不管，模型照自己對需求的理解一路跑；要嘛儀式太重，改一行也得先填五張表才能動工。第一次嘗試是自製的 `everything-cli`，做完才發現走到了另一個極端——token 燒得快，每個小任務都要先過七道關卡才碰得到程式碼。有用，但太重。`baransu` 是第二次嘗試。

## 核心原則

平衡不是妥協，重點是知道**什麼時候**可以輕、什麼時候不准輕。小任務不需要三輪對焦；重要的決策不能省略思考。工具配合任務的形狀：小任務走輕量路徑，大任務走完整規格——不反過來逼任務遷就工具的流程。每個 skill 都有清楚的觸發界線：什麼可以省、什麼一定要做。

自 v2.1.0 起，這條線寫成五條可驗收的理念。每條都綁一個倉內機制錨點——無錨點的條款不入冊，錨點存在性由結構驗證器（`scripts/verify-skills.py`）把關。

## 五條理念（完整版）

| 理念 | 一句話 | 機制錨點 |
|---|---|---|
| 規則是天花板 | 只寫防真實翻車的規則；容器只能變深、不能變長 | `plugins/baransu/rules/anti-patterns.md` |
| 結構是地板 | 確定性檢查全走腳本閘門，不靠模型自律；14 個技能是上限（2026-07 修憲 14→15，2026-08 隨 `/analyze` 退役收回 14；附 codex-skill-transfer 三個月零使用即退役回 13 的可證偽條款） | `scripts/verify-skills.py` |
| 人在授權點 | Input PAUSE 可走預設；Authorization PAUSE 不可覆寫 | `plugins/baransu/skills/_shared/loop-contract.md` |
| 證據優先 | 非顯然主張依賴前先引查證來源；乾淨的 review 也是有效的 review | `plugins/baransu/skills/review/SKILL.md` |
| 狀態落盤 | 長流程的結論落檔交付、不賭終端顯示 | `plugins/baransu/skills/_shared/output-journal.md` |

首頁 [README](../README.md) 的「核心理念」表是這張表的精簡版，同樣由 `scripts/verify-skills.py` 逐列檢查錨點存在。

## 14 個 skill 的上限

14 是上限——要加第 15 個，必須先退役一個（以裁換建）。機制錨點是 `scripts/verify-skills.py` 的 skill 數量檢查。

可證偽的修憲條款（2026-07-19，14→15）：若選用遙測顯示 `/codex-skill-transfer` 連續三個月零使用，就退役它並把上限收回 13。

## 任務不遷就工具

小任務不硬上全套，大任務不偷走輕量路。實際怎麼分流，見 [三頻段路由](routing.md)。
