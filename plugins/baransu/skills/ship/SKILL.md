---
name: ship
description: Session cleanup — archives .claude/tmp/, .claude/analyze/, .claude/execute/, .claude/think/, .claude/dev/ to .claude/archived/, commits all pending changes, pushes to origin, and removes the current git worktree if running inside one.
---

# /baransu:ship — session cleanup

The body below is English (agent-facing). All user-visible output is in **Traditional Chinese (繁體中文)**.

No user confirmation required. Five steps run automatically.

---

## Step 1 — Detect

Check whether `.claude/tmp/`, `.claude/analyze/`, `.claude/execute/`, `.claude/think/`, `.claude/dev/` contain any items.

```bash
find .claude/tmp .claude/analyze .claude/execute .claude/think .claude/dev -maxdepth 1 -mindepth 1 2>/dev/null | head -1
```

If no items found → output 「沒有可歸檔的工作檔案，結束。」 and stop. Do not proceed.

---

## Step 2 — Archive

Create `.claude/archived/` if it does not exist.

For each of `tmp`, `analyze`, `execute`, `think`, `dev`: for each item directly inside the source directory:
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
