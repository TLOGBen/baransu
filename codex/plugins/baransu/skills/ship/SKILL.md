---
name: ship
description: Use When wrapping up a session and pushing pending changes. Do Archive
  every baransu working dir under .claude/ except the read/learn/book products into
  .claude/archived/, commit, push (optionally landing the work on a target branch
  via `/ship <branch>`), and tear down the worktree once its work is safely on origin.
  Trigger On '/ship', '收工', '上傳收尾', '結束這輪'. Not For writing or refining copy (use
  /write); not for reviewing code or model output (use /review) — /ship only wraps
  up a session.
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

# /baransu:ship — session cleanup

The body below is English (agent-facing). All user-visible output is in **Traditional Chinese (繁體中文)**.

No user confirmation required. The steps below run automatically.

---

## Outcome Contract

- **Outcome**: The session's working files are archived and all pending changes are committed and pushed — optionally landed on a specified target branch.
- **Done when**: Archivable items are moved into `.claude/archived/`, `git status --porcelain` is empty after the commit, and the work is on origin (the current branch pushed, or — when a target branch is given — the current branch merged into it and that branch pushed); when run inside a worktree whose work is confirmed on origin, the worktree is removed and its branch deleted.
- **Evidence**: The session end output reporting the archived item count, the commit message (or 「跳過」), the push target (`origin/{branch}` or `{branch} → {target}`), and the worktree cleanup status.
- **Output**: Archived directories under `.claude/archived/`, a pushed git commit, and the 繁中 session end report.
- **Automation**: ultracode=neutral, loop=assisted（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）

## Invariants

Named red-lines, each enforced by the step in parentheses; none is optional. The step keeps its own if-then recovery — these name the rule it enforces.

- **INV-1 — Allowlist-only archive.** Only the Step 1 `ARCHIVE_DIRS` allowlist is swept; the `read` / `learn` / `book` products and all Claude Code infrastructure (`worktrees/`, `projects/`, `jobs/`, `plugins/`, `settings*.json`) are never archived. (Step 2)
- **INV-2 — Source dirs are emptied, never deleted.** Archiving moves items out; the source directory itself stays in place. (Step 2)
- **INV-3 — Never force-push.** `--force` is forbidden on every push; `--force-with-lease` is used only when the user explicitly asks. (Step 4)
- **INV-4 — No worktree teardown until the work is on origin.** A worktree is destroyed only after `git merge-base --is-ancestor` confirms the branch is on `$SAFE_REF`. (Step 5)
- **INV-5 — Branch deletion uses `-D`, not `-d`.** After a merge the branch may read as unmerged locally, so `-d` fails. (Step 5)
- **INV-6 — `rm -rf` is only run on a validated worktree path.** The third-tier `rm -rf "$WORKTREE_PATH"` fallback runs only after a precondition guard confirms `$WORKTREE_PATH` is non-empty, is not `/`, and carries `.git`/`.git/worktrees` lineage; if the guard fails, `rm -rf` is skipped and the worktree is left intact. (Step 5)

## Step 0 — Parse target branch

The optional target-branch argument may be written as `<branch>`, `到 <branch>`, or `to <branch>`. Strip a leading `到` / `to` token and take the next token as `$TARGET`; if no argument is given, `$TARGET` is empty.

- `/ship` → `$TARGET` empty → **current-branch mode** (Step 4 Mode A).
- `/ship main` / `/ship 到 main` / `/ship to release/2.5` → `$TARGET` set → **land-on-target mode** (Step 4 Mode B).

## Step 1 — Detect

Check both whether the workspace dirs hold archivable items AND whether the git working tree has pending changes. Stop only when **both** are empty — otherwise there is still work to ship even when one side is empty.

```bash
ARCHIVE_DIRS="tmp analyze execute think design hunt-report evolve review"
ARCHIVE_ITEMS=$(for d in $ARCHIVE_DIRS; do find ".claude/$d" -maxdepth 1 -mindepth 1 2>/dev/null; done | head -1)
GIT_DIRTY=$(git status --porcelain 2>/dev/null | head -1)
```

Decision:

- If `ARCHIVE_ITEMS` is empty AND `GIT_DIRTY` is empty → output 「沒有可歸檔的工作檔案，git 也乾淨，結束。」 and stop. Do not proceed.
- Otherwise → continue (Step 2 / Step 3 each have their own empty-input fallback; Step 4 lands work unconditionally so unpushed commits from earlier sessions still go out).

---

## Step 2 — Archive

Create `.claude/archived/` if it does not exist.

**Archive allowlist** (the baransu working dirs): `tmp`, `analyze`, `execute`, `think`, `design`, `hunt-report`, `evolve`, `review`.

**Never archived**: the `read`, `learn`, and `book` dirs are kept products and stay in place. Claude Code infrastructure (`worktrees/`, `projects/`, `jobs/`, `plugins/`, `settings*.json`, …) is never touched — the allowlist is explicit precisely so infra is never swept up.

For each dir in the allowlist, for each item directly inside the source directory:
- Destination: `.claude/archived/{item_name}`
- If destination already exists: rename it to `.claude/archived/{item_name}-{unix_timestamp}` first
- Move item to destination

Source directories are left empty (not deleted).

Output: 「已歸檔：{N} 個項目 → .claude/archived/（read/learn/book 產物保留）」

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

## Step 4 — Push (current branch) or land on target

```bash
BRANCH=$(git rev-parse --abbrev-ref HEAD)
MAIN_REPO=$(dirname "$(git rev-parse --git-common-dir)")
```

### Mode A — no `$TARGET` (or `$TARGET` equals `$BRANCH`): push the current branch

```bash
git push origin "$BRANCH" || git push -u origin "$BRANCH"
```

On success → output 「已推送至 origin/{BRANCH}。」 On failure → output 「Push 失敗：{error}」 and stop.

### Mode B — `$TARGET` set and ≠ `$BRANCH`: merge `$BRANCH` into `$TARGET`, then push `$TARGET`

Run on the main repo (`$MAIN_REPO`) — the target branch lives there, not in this worktree. **Never use `--force`.**

1. The main repo must be clean before switching branches: run `git -C "$MAIN_REPO" status --porcelain`. If its output is non-empty → output 「主 repo 有未提交變更，無法切到 {TARGET}；請先處理後重跑 /ship {TARGET}。」 and stop; if its output is empty → proceed to the checkout in item 2.
2. Put the main repo on `$TARGET` (existing local branch, else track origin, else error):
   ```bash
   git -C "$MAIN_REPO" checkout "$TARGET" 2>/dev/null \
     || git -C "$MAIN_REPO" checkout -B "$TARGET" "origin/$TARGET" 2>/dev/null \
     || { echo "no such branch"; }   # → output 「找不到目標分支 {TARGET}（本地與 origin 皆無）；請先建立或改用現有分支」 and stop
   ```
3. Merge (no-ff):
   ```bash
   git -C "$MAIN_REPO" merge --no-ff "$BRANCH" -m "merge: $BRANCH → $TARGET (via /ship)"
   ```
   On conflict → `git -C "$MAIN_REPO" merge --abort`, output 「合併 {BRANCH} → {TARGET} 有衝突，已中止；請手動解決後再 ship。」 and stop.
4. Push without forcing; on a non-fast-forward rejection, integrate then retry once:
   ```bash
   git -C "$MAIN_REPO" push origin "$TARGET" \
     || { git -C "$MAIN_REPO" pull --no-rebase --no-edit origin "$TARGET" \
          && git -C "$MAIN_REPO" push origin "$TARGET"; }
   ```
   If it still fails → output 「Push {TARGET} 失敗：{error}」 and stop. Never `--force` (use `--force-with-lease` only if the user explicitly asks).

On success → output 「已合併 {BRANCH} → {TARGET} 並推送至 origin/{TARGET}。」 (The main repo is left on `$TARGET`.)

---

## Step 5 — Worktree cleanup (conditional, safety-gated)

```bash
git rev-parse --git-dir
```

If the output contains `.git/worktrees/`:

1. Capture variables before any removal:
   ```bash
   WORKTREE_PATH=$(pwd)
   BRANCH=$(git rev-parse --abbrev-ref HEAD)
   MAIN_REPO=$(dirname "$(git rev-parse --git-common-dir)")
   ```
2. **Safety gate — confirm the work is on origin before destroying the worktree.** Pick the ref the work should now live on: `SAFE_REF="origin/$TARGET"` in Mode B, else `SAFE_REF="origin/$BRANCH"`.
   ```bash
   git -C "$MAIN_REPO" merge-base --is-ancestor "$BRANCH" "$SAFE_REF"
   ```
   - Exit 0 (ancestor) → the branch's commits are safely on `$SAFE_REF` → proceed to teardown.
   - Non-zero → the work is **not** yet on `$SAFE_REF`. Do **not** destroy it. Output 「分支 {BRANCH} 的工作尚未確認落地到 {SAFE_REF}，保留 worktree 以免遺失；請確認 merge/push 後再清理。」 and skip teardown (leave the worktree intact).

   This ancestor check is exact: it never falsely refuses a merged branch (unlike branch-tip heuristics) and never silently discards unmerged work.
3. **Teardown** — three-tier removal, then delete the branch. The third tier escalates to `rm -rf`; before that destructive fallback runs, a precondition guard (INV-6) must confirm `$WORKTREE_PATH` is a validated worktree path. Keep the three-tier `||` chain ordering and the `branch -D` intact:
   ```bash
   git -C "$MAIN_REPO" worktree remove "$WORKTREE_PATH" \
     || git -C "$MAIN_REPO" worktree remove --force "$WORKTREE_PATH" \
     || { if [ -n "$WORKTREE_PATH" ] && [ "$WORKTREE_PATH" != "/" ] && [ -e "$WORKTREE_PATH/.git" ]; then \
            rm -rf "$WORKTREE_PATH" && git -C "$MAIN_REPO" worktree prune; \
          else \
            echo "worktree 路徑無法安全確認，停止強制刪除以免誤刪"; \
          fi; }
   git -C "$MAIN_REPO" branch -D "$BRANCH"
   ```
   `branch -D` (not `-d`): after a merge the branch may still read as unmerged locally, so `-d` fails — `-D` is required.

   If the guard fails (`$WORKTREE_PATH` empty, `/`, or missing `.git` lineage) → output 「worktree 路徑無法安全確認，停止強制刪除以免誤刪」 and skip teardown, leaving the worktree intact.

   Output: 「Worktree 已清理：{WORKTREE_PATH}，分支 {BRANCH} 已刪除。」

If not in a worktree → skip silently.

---

## Session end output

```
/baransu:ship 完成。

歸檔：{N} 個項目（或「無可歸檔檔案」；read/learn/book 產物保留）
Commit：{commit message 或「跳過」}
Push：{origin/BRANCH 或「BRANCH → TARGET，origin/TARGET」}
Worktree：{已清理 path 或「保留（工作未落地）」或「不適用」}
```
