---
hunt_id: HUNT-YYYY-NNN
target: 一句話描述狩獵目標
status: scoping  # scoping | confirmed | fixed | handoff — created at Locate stage with scoping; update as the hunt progresses
created: YYYY-MM-DD
scope:
  files:
    - path: ""
      methods: []
  components: []  # for non-file targets (DB table, API endpoint, service)
diagnostic_logs:
  tag: "🎯HUNT-YYYY-NNN"
  status: active  # active | pending_removal | removed
  removed_in_commit: ""
root_cause: ""
fix: ""
---

# HUNT-YYYY-NNN — [目標描述]

## 症狀

[完整錯誤訊息或重現步驟]

## Before You Fix

### 呼叫鏈分析
- 直接呼叫者：
- 業務場景數：
- 高風險點：

### 測試矩陣
| 維度 | 值 | 必須覆蓋 |
|------|---|---------|
|  |  |  |

測試矩陣注意：unchanged 場景、multi-X 場景最容易漏。

## 調查記錄

### 假說 1
- 假說：
- 工具（帶 `🎯HUNT-YYYY-NNN` tag）：
- 結果：
- 保留或丟棄：

## 根因分析

[詳細說明根因]

## 修復

[改了什麼，在哪裡，對應哪個 commit]

## Scope Blast

Pattern signature：`[grep 的 pattern]`

每一個 grep match 一行，格式（對應 SKILL.md Scope Blast step 3）：

```
<file:line> — fix ｜ leave: <一句理由> ｜ unsure: <問題>
```

- §1 `src/example.ts:42` — fix
- §2 `src/other.ts:17` — leave: 該路徑已有上游驗證
- §3 `src/third.ts:88` — unsure: 是否共用同一把 lock？（解決後改寫為 `unsure → fix` 或 `unsure → leave: <理由> after user reply <date>`）

不得默默跳過任何 match；狩獵中發現的無關 bug 列於此、但未經使用者同意不得在本次修復。

## 迴歸驗證

- 原 bug：✅ / ❌
- 測試矩陣：N/N 通過
- 迴歸守護：[test file:line + Scope Blast: HUNT-YYYY-NNN §N ｜ 或 無（理由 + Scope Blast citation）]

## 診斷工具清理

- Tag：`🎯HUNT-YYYY-NNN`
- 狀態：active → pending_removal → removed
- 清除 commit：

---

## 🎯HUNT-id Tag 格式參考

在 log 行、assertion 或 test probe 裡帶 tag，便於一次找到並清除所有診斷工具：

```
# 格式（語言無關）：
# 🎯HUNT-YYYY-NNN [位置描述] key=value key2=value2

# 找到全部診斷工具：
grep -rn "🎯HUNT-YYYY-NNN" src/

# 清除後確認 build 通過：
<project build command>
```
