---
name: ship
description: Use When wrapping up a session and pushing pending changes. Do Archive
  .claude/{tmp,analyze,execute,think}/ to .claude/archived/, commit and push, optionally
  remove the current worktree. Trigger On '/ship', '收工', '上傳收尾', '結束這輪'.
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

# /baransu:ship — session cleanup

The body below is English (agent-facing). All user-visible output is in **Traditional Chinese (繁體中文)**.

No user confirmation required. Five steps run automatically.

---

## Outcome Contract

- **Outcome**: The session's working files are archived and all pending changes are committed and pushed.
- **Done when**: Archivable items are moved into `.claude/archived/`, `git status --porcelain` is empty after the commit, and the branch is pushed to origin (worktree removed and branch deleted when run inside a worktree).
- **Evidence**: The session end output reporting the archived item count, the commit message (or 「跳過」), the push target `origin/{branch}`, and the worktree cleanup status.
- **Output**: Archived directories under `.claude/archived/`, a pushed git commit, and the 繁中 session end report.
- **Automation**: ultracode=neutral, loop=assisted

## Step 1 — Detect

Check both whether the workspace dirs hold archivable items AND whether the git working tree has pending changes. Stop only when **both** are empty — otherwise there is still work to ship even when one side is empty.

```bash
ARCHIVE_ITEMS=$(find .claude/tmp .claude/analyze .claude/execute .claude/think -maxdepth 1 -mindepth 1 2>/dev/null | head -1)
GIT_DIRTY=$(git status --porcelain 2>/dev/null | head -1)
```

Decision:

- If `ARCHIVE_ITEMS` is empty AND `GIT_DIRTY` is empty → output 「沒有可歸檔的工作檔案，git 也乾淨，結束。」 and stop. Do not proceed.
- Otherwise → continue with Step 2–4 (Step 2 / Step 3 each have their own empty-input fallback; Step 4 pushes unconditionally so unpushed commits from earlier sessions still land).

---

## Step 2 — Archive

Create `.claude/archived/` if it does not exist.

For each of `tmp`, `analyze`, `execute`, `think`: for each item directly inside the source directory:
- Destination: `.claude/archived/{item_name}`
- If destination already exists: rename it to `.claude/archived/{item_name}-{unix_timestamp}` first
- Move item to destination

Source directories are left empty (not deleted).

Output: 「已歸檔：{N} 個項目 → .claude/archived/」

If any move fails → output 「歸檔失敗：{reason}」 and stop.

---

## Step 3 — Commit

```bash
git add -A
git commit -m "chore: 歸檔工作檔案並提交本次變更"
```

If commit succeeds → output: 「已提交：chore: 歸檔工作檔案並提交本次變更」

If nothing to commit (exit code 1, message contains "nothing to commit") → output 「無待提交的變更，跳過 commit。」 Continue to Step 4.

If commit fails for another reason → output 「Commit 失敗：{error}」 and stop.

---

## Step 4 — Push

```bash
BRANCH=$(git rev-parse --abbrev-ref HEAD)
git push origin "$BRANCH" || git push -u origin "$BRANCH"
```

If push succeeds → output: 「已推送至 origin/{branch}。」

If push fails → output 「Push 失敗：{error}」 and stop.

---

## Step 5 — Worktree cleanup (conditional)

```bash
git rev-parse --git-dir
```

If the output contains `.git/worktrees/`:
1. Capture variables before removal:
   ```bash
   WORKTREE_PATH=$(pwd)
   BRANCH=$(git rev-parse --abbrev-ref HEAD)
   MAIN_REPO=$(dirname "$(git rev-parse --git-common-dir)")
   ```
2. Remove worktree from main repo:
   ```bash
   git -C "$MAIN_REPO" worktree remove "$WORKTREE_PATH" --force
   ```
   If fails → output 「Worktree 移除失敗：{error}」 and stop.
3. Delete the local branch from main repo:
   ```bash
   git -C "$MAIN_REPO" branch -D "$BRANCH"
   ```
   If fails → output 「分支刪除失敗：{BRANCH}，{error}」 and stop.
4. Output: 「Worktree 已清理：{WORKTREE_PATH}，分支 {BRANCH} 已刪除。」

If not in a worktree → skip silently.

---

## Session end output

```
/baransu:ship 完成。

歸檔：{N} 個項目（或「無可歸檔檔案」）
Commit：{commit message 或「跳過」}
Push：origin/{branch}
Worktree：{已清理 path 或「不適用」}
```
