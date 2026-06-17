---
topic: "開發工具/CLI 的 ship/release/cleanup 自動化做法與眉角；git 分支策略對「ship 到指定 branch」的取捨"
sources:
  - slug: "assembla-tbd-vs-gitflow"
    url: "https://get.assembla.com/blog/trunk-based-development-vs-git-flow/"
  - slug: "codewithmukesh-git-workflows"
    url: "https://codewithmukesh.com/blog/git-workflows-gitflow-vs-github-flow-vs-trunk-based-development/"
  - slug: "oleksiipopov-npm-release-automation"
    url: "https://oleksiipopov.com/blog/npm-release-automation/"
  - slug: "gitworktree-org-prune"
    url: "https://www.gitworktree.org/tutorial/prune"
  - slug: "brtkwr-bulk-clean-worktrees"
    url: "https://brtkwr.com/posts/2026-03-06-bulk-cleaning-stale-git-worktrees/"
  - slug: "gitkraken-force-push"
    url: "https://www.gitkraken.com/learn/git/problems/git-push-force"
created_at: "2026-06-16"
type: "brief"
---

# Brief：ship/release/cleanup 自動化 + git 分支策略（給 /ship 演化用）

> 來源全部來自 `web` lane（gh lane rate-limited、academic/x lane 對工具題低產，soft-fail 略過）。Digest 評分後全數保留。

## (a) 核心主張列表

- **[分支策略光譜]** Git-Flow（多長壽分支 master/develop/feature/release/hotfix；適合版本化／受規範產品；重）→ **GitHub Flow**（單一 main + 短命 feature 分支，合併前過 CI；SaaS 主流中庸）→ **Trunk-Based**（單幹線 + 一兩天內短命分支；吞吐最高但需 CI + feature flag）。多數團隊混用。 [assembla-tbd-vs-gitflow, codewithmukesh-git-workflows]
- **[release 自動化三取向]** semantic-release（全自動、commit message 驅動 Angular convention，bump+changelog+tag+publish 一條龍）／Changesets（把版本意圖從 commit 解耦成 intent 檔，刻意可控）／release-please（PR 驅動，changelog + GitHub release + bump）。 [oleksiipopov-npm-release-automation]
- **[worktree 清理]** `git worktree remove` 一步清目錄 + admin data，prune 多半多餘；但移除只做半套——每個 merged 分支仍留 local branch ref，須另外刪。 [gitworktree-org-prune, brtkwr-bulk-clean-worktrees]
- **[merged 偵測法]** 判斷分支是否已併有數種：`git branch --merged <target> | grep -qw $b`（ancestor）；進階用 same-commit／ancestor／空三點 diff／tree-SHA 相等（可涵蓋 squash/rebase 合併）；或用 remote-ref 是否還在當代理（`git fetch --prune` 後顯示 `[gone]`）。 [brtkwr-bulk-clean-worktrees, codewithmukesh-git-workflows]
- **[push 安全]** 自動化**絕不** `--force` 共享歷史；要強推改用 `--force-with-lease`（檢查 remote 自上次 fetch 未被動過才覆寫）；commit 前先 `git status` 確認乾淨樹，nothing-to-commit 要可跳過（idempotent）。 [gitkraken-force-push]
- **[三段 fallback 移除]** 健壯的 worktree 移除採三層：① `git worktree remove`（髒則失敗）→ ② `--force`（無視未提交）→ ③ `rm -rf` + `git worktree prune`（修壞掉的 metadata）。 [brtkwr-bulk-clean-worktrees]

## (b) 來源矛盾點

- **merged 偵測法分歧**：brtkwr 用「remote tracking branch 還在不在」當合併代理（簡單，但依賴 `fetch --prune`，且把「remote 被刪」一律當「已併或棄置」→ 直接 force remove，風險是誤判本地未推的工作）；其他來源主張用 **ancestor / tree-SHA 直接判斷**（更準、涵蓋 squash/rebase，較複雜）。→ 對 /ship 的啟示：**本地剛 merge 完**的情境，`git merge-base --is-ancestor` 比 remote-ref 代理更直接可靠（正是我剛 ship 「到 main」時 ExitWorktree 卡住的那個洞）。
- **分支策略無「最佳解」**：Git-Flow 派重 release 控制與長壽分支；trunk-based 派視長壽分支為負債、重吞吐。價值觀相反，取捨看產品型態。
- **自動化哲學分歧**：semantic-release「commit 即真相、全自動」 vs Changesets「版本意圖該人工刻意宣告」——前者省事但綁死 conventional commits，後者可控但多一道手動。

## (c) 缺少資訊/盲點

- 來源多聚焦**多人團隊 PR-based** 流程；對「單人 + 本地 worktree + 直接 merge 到 main」這種 baransu `/ship` 情境著墨極少。
- 沒有來源直接談「CLI skill 內建 ship-to-arbitrary-branch」的語意與 UX（業界多是 CI/PR 端自動化，非 CLI 收尾指令）。
- idempotency 標記（tag/metadata 防重複處理）被 brtkwr 點名「沒人做」，但也沒給具體方案。
- **歸檔 vs 刪除**的取捨幾乎無人討論——業界傾向直接刪分支/worktree；baransu「歸檔工作檔案到 .claude/archived/」是較少見的保守保存做法，正是使用者想擴大的那一塊。

## (d) 各來源信度評分

| 來源 | 多情境適用性 | 預測力 | 通用性 | 綜合 |
|------|-------------|--------|--------|------|
| assembla-tbd-vs-gitflow | ★★★★☆ | ★★★☆☆ | ★★★★☆ | 3.7 |
| codewithmukesh-git-workflows | ★★★★☆ | ★★★☆☆ | ★★★★☆ | 3.7 |
| oleksiipopov-npm-release-automation | ★★★★☆ | ★★★★☆ | ★★★☆☆ | 3.7 |
| gitworktree-org-prune | ★★★☆☆ | ★★★☆☆ | ★★★★☆ | 3.3 |
| brtkwr-bulk-clean-worktrees | ★★★★☆ | ★★★★☆ | ★★★☆☆ | 3.7 |
| gitkraken-force-push | ★★★★★ | ★★★★☆ | ★★★★★ | 4.7 |

## (e) 建議 /think 入場角度（→ /ship 設計）

把這份 brief 餵 /ship 演化時，以下列為核心設計問題：

1. **worktree teardown 順化** ← 直接補洞：用 `git merge-base --is-ancestor <branch> <target>`（已 push 則對 `origin/<target>`）當「已併」閘 → 已併才無摩擦 `worktree remove --force` + `branch -D`；未併則保守提示，不硬刪。比 ExitWorktree 工具盲目的「有 commit 就拒」精準。
2. **ship-to-branch 採 GitHub Flow 心智**：merge 短命 worktree 分支進 `<branch>`（main 或 release 分支）→ push `<branch>`。**絕不 `--force`**；push 被拒先 `pull --no-rebase` 再推（不是 force-with-lease，因為這是自己的 fast-forward 合併情境）。
3. **push/commit 安全 + idempotency**：ship 前 `git status` 乾淨檢查、`nothing to commit` 跳過、整體可重入（再跑一次不爆）。
4. **三段 fallback 移除**納入 Step 5 健壯性（remove → --force → rm -rf + prune）。
5. **歸檔擴大（白名單）**：業界傾向刪，baransu 選保留——所以「只留 read/learn/book，其餘 baransu 工作目錄歸檔」是刻意的保守決策，無業界對標，靠白名單明列最安全（呼應使用者選的方案）。
