---
name: ship
description: "Wraps up a session: archives baransu working dirs under .claude/ (except read/learn/book products) into the gitignored, local-only .claude/archived/, commits, pushes (optionally `/ship BRANCH`), and tears down the worktree once work is on origin. Trigger On '/ship', '收工', '上傳收尾', '結束這輪'. Not For writing copy (/write) or reviewing output (/review) — /ship only wraps up a session."
---

# /baransu:ship — session cleanup

All user-visible output is in **Traditional Chinese (繁體中文)**.

No user confirmation required. The steps below run automatically.

---

## Outcome Contract

- **Outcome**: The session's working files are archived locally without entering Git, and all other pending changes are committed and pushed — optionally landed on a specified target branch.
- **Done when**: Archivable items are moved into the gitignored `.claude/archived/`, no archive path is tracked, `git status --porcelain` is empty after the commit, and the work is on origin (the current branch pushed, or — when a target branch is given — the current branch merged into it and that branch pushed); when run inside a worktree whose work is confirmed on origin, the worktree is removed and its branch deleted.
- **Evidence**: The archive ignore/untracked checks, the session end output reporting the archived item count, the commit message (or 「跳過」), the push target (`origin/{branch}` or `{branch} → {target}`), and the worktree cleanup status.
- **Output**: Local-only archived directories under `.claude/archived/`, a pushed git commit when non-archive changes exist, and the 繁中 session end report.
- **Automation**: ultracode=neutral, loop=assisted（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）
  In the same non-interactive pass, read `references/loop-pauses.md` for this skill's own PAUSE classification.

## Invariants

Named red-lines, each enforced by the step in parentheses; none is optional. The step keeps its own if-then recovery — these name the rule it enforces.

- **INV-1 — Two named archive sources, nothing else.** Exactly two sources feed the archive: (1) the Step 1 `ARCHIVE_DIRS` allowlist, swept dir by dir; (2) sealed root `CONTRACT*.md` files, identified by the sealed marker in their first 3 lines. Everything outside those two is never archived — the `read` / `learn` / `book` products, unsealed contracts, and all Claude Code infrastructure (`worktrees/`, `projects/`, `jobs/`, `plugins/`, `settings*.json`) stay in place. The allowlist spirit is unchanged: naming the second source enumerates it just as explicitly, it does not open a discretionary sweep. (Step 2)
- **INV-2 — Source dirs are emptied, never deleted.** Archiving moves items out; the source directory itself stays in place. (Step 2)
- **INV-3 — Never force-push.** `--force` is forbidden on every push; `--force-with-lease` is used only when the user explicitly asks. (Step 4)
- **INV-4 — No worktree teardown until the work is on origin.** A worktree is destroyed only after `git merge-base --is-ancestor` confirms the branch is on `$SAFE_REF`. (Step 5)
- **INV-5 — Branch deletion uses `-D`, not `-d`.** After a merge the branch may read as unmerged locally, so `-d` fails. (Step 5)
- **INV-6 — `rm -rf` is only run on a validated worktree path.** The third-tier `rm -rf "$WORKTREE_PATH"` fallback runs only after a precondition guard confirms `$WORKTREE_PATH` is non-empty, is not `/`, and carries `.git`/`.git/worktrees` lineage; if the guard fails, `rm -rf` is skipped and the worktree is left intact. (Step 5)
- **INV-7 — No blind staging of secret-pattern files.** Before `git add -A`, every untracked/modified path from `git status --porcelain` is matched against the Step 3 closed pattern list; any match stops the commit before staging. (Step 3)
- **INV-8 — The commit subject names the shipped outcome.** Derive one Conventional Commit message from the staged diff; archiving and session cleanup never displace a substantive code, behavior, or documentation outcome. (Step 3)
- **INV-9 — Archive is local-only.** The archive root must be ignored and contain no tracked paths before any item is moved into it; existing tracked archives are removed from the index but retained on disk. (Step 2)

## Step 0 — Parse target branch

The optional target-branch argument may be written as `<branch>`, `到 <branch>`, or `to <branch>`. Strip a leading `到` / `to` token and take the next token as `$TARGET`; if no argument is given, `$TARGET` is empty.

- `/ship` → `$TARGET` empty → **current-branch mode** (Step 4 Mode A).
- `/ship main` / `/ship 到 main` / `/ship to release/2.5` → `$TARGET` set → **land-on-target mode** (Step 4 Mode B).

## Step 1 — Detect

Git probe first — run `git rev-parse --git-dir 2>/dev/null`. If it fails (the project is not a git repo), output 「此專案不是 git repo：/ship 的 commit／push／worktree 流程無法執行，已停止。如需歸檔請手動處理 .claude/ 工作目錄。」 and stop. The probe MUST run before any archive move: without git there is no commit to anchor moved files, so archiving first would strand them — and every later git step (commit, push, worktree teardown) would wedge.

Check three inputs: whether the workspace dirs hold archivable items, whether the git working tree has pending changes, AND whether the repo root holds a sealed contract. Stop only when **all three** are empty — otherwise there is still work to ship even when the other sides are empty.

```bash
ARCHIVE_DIRS="tmp analyze execute think design hunt-report evolve review write"
ARCHIVE_ITEMS=$(python3 -c "import sys, pathlib; print(next((str(p) for d in sys.argv[1].split() if pathlib.Path('.claude', d).is_dir() for p in pathlib.Path('.claude', d).iterdir()), ''))" "$ARCHIVE_DIRS")
GIT_DIRTY=$(git status --porcelain 2>/dev/null | head -1)
SEALED_CONTRACTS=$(find . -maxdepth 1 -type f -name 'CONTRACT*.md' | while read -r f; do
  head -3 "$f" | grep -qF '> STATUS: sealed' && printf '%s\n' "$f"
done)
```

(The detect uses python3/pathlib rather than a shell loop over `$ARCHIVE_DIRS`: zsh does not word-split unquoted parameters, so a `for d in $ARCHIVE_DIRS` + `find` pattern silently yields an always-empty `ARCHIVE_ITEMS` under zsh-driven harnesses. For the same class of reason the contract scan uses `find` with a quoted pattern instead of a `for f in CONTRACT*.md` glob: under zsh an unmatched glob is an error, not an empty list, so the glob form aborts the scan on every repo that has no contract at all. Keep the loop variable named `f` — the detection line below is a verbatim constant.)

**Sealed-contract detect.** The grammar authority for the marker is the contract template in `../contract/SKILL.md` Step 2 (sealed-marker grammar: single authority) — cite it, do not restate its rules here. `/ship` only ever reads it. The detection target is this exact line, which a sealed contract carries at line 2, immediately after the H1:

```
> STATUS: sealed（{ISO 日期}）— {五點結果一行摘要}
```

Only the first 3 lines of each candidate are scanned — never grep the whole file, or a contract that merely quotes the marker inside its own Verbatim Constants block reads as sealed:

```bash
head -3 "$f" | grep -qF '> STATUS: sealed'
```

The scan is root-only and non-recursive (`-maxdepth 1`): contracts kept at a user-chosen path outside the repo root are the user's to manage.

Decision:

- If `ARCHIVE_ITEMS` is empty AND `GIT_DIRTY` is empty AND `SEALED_CONTRACTS` is empty → output 「沒有可歸檔的工作檔案，git 也乾淨，root 無 sealed 合約，結束。」 and stop. Do not proceed.
- Otherwise → continue (Step 2 / Step 3 each have their own empty-input fallback; Step 4 lands work unconditionally so unpushed commits from earlier sessions still go out).

---

## Step 2 — Archive

Create `.claude/archived/` if it does not exist.

Before moving any item, enforce the local-only boundary:

1. Read the repo-root `.gitignore`. If the exact anchored rule `/.claude/archived/`
   is absent, add that one line with the available file-editing tool. Do not use
   shell redirection, and do not replace broader ignore rules.
2. Remove any legacy archive entries from the Git index while preserving their
   local files:
   ```bash
   git rm -r --cached --ignore-unmatch -- .claude/archived/
   ```
3. Verify both halves of INV-9:
   ```bash
   git check-ignore -q .claude/archived/.ship-ignore-probe
   test -z "$(git ls-files .claude/archived/)"
   ```
   If either command fails, output 「archive ignore 驗證失敗：已停止歸檔，未移動
   任何工作檔案。」 and stop.

**Archive allowlist** — exactly the Step 1 `ARCHIVE_DIRS` value, in the same order: `tmp`, `analyze`, `execute`, `think`, `design`, `hunt-report`, `evolve`, `review`, `write`. The two lists MUST stay identical; a dir detected in Step 1 but absent here would leave Step 1's detect output unconsumed.

**Never archived**: the `read`, `learn`, and `book` dirs are kept products and stay in place. Claude Code infrastructure (`worktrees/`, `projects/`, `jobs/`, `plugins/`, `settings*.json`, …) is never touched — the allowlist is explicit precisely so infra is never swept up.

For each dir in the allowlist, for each item directly inside the source directory:
- Destination: `.claude/archived/{item_name}`
- If destination already exists: rename it to `.claude/archived/{item_name}-{unix_timestamp}` first
- Move item to destination

Source directories are left empty (not deleted).

**Sealed root contracts** — after the allowlist sweep, take the `SEALED_CONTRACTS` list from Step 1 (the second archive source named by INV-1) and archive each one with the same collision semantics as above:
- Destination: `.claude/archived/{filename}` — `{filename}` is the basename of the detected path (Step 1's `find` output carries a `./` prefix; strip it, e.g. `basename "$f"`)
- If destination already exists: rename it to `.claude/archived/{filename}-{unix_timestamp}` first
- Move the contract to destination

A sealed contract is a completed artifact, so `/ship` collects it; an **unsealed** contract is live work and stays in place, untouched. Step 1's sealed-contract detect and this sweep MUST stay in sync — the same reason the two `ARCHIVE_DIRS` lists must: a contract detected in Step 1 but not swept here would leave Step 1's detect output unconsumed (and could early-stop nothing into a no-op run).

(Archiving here is collision-only timestamping — the plain `{filename}` destination is used when it is free. `/contract` Step 3 archives a sealed contract it is about to overwrite and always timestamps. The asymmetry is deliberate: `/contract` is mid-write and cannot afford to reason about the destination, `/ship` keeps archive names readable. Do not unify them.)

Output: 「已歸檔：{N} 個項目 → .claude/archived/（read/learn/book 產物保留；含 sealed 合約 {S} 份）」

`{N}` is the total moved — allowlist items plus sealed contracts — and `{S}` is how many of those `{N}` were sealed contracts (`{S}` is `0` when none).

If any move fails → output 「歸檔失敗：{reason}」 and stop.

---

## Step 3 — Commit

**Secret gate (INV-7)** — run immediately before `git add -A`: run `git status --porcelain` and match each untracked/modified path's filename against this fixed, closed pattern list: `.env`, `.env.*`, `*.pem`, `*.key`, `id_rsa*`, `*.p12`, `credentials*.json`. If any path matches → output 「偵測到疑似機敏檔案：{列出檔名}，已停止 commit；請確認內容、加入 .gitignore 或手動處理後再重跑 /ship。」 and stop. If none match → proceed to `git add -A` unchanged.

Stage first, then inspect what will actually ship:

```bash
git add -A
git diff --cached --name-status
git diff --cached --stat
```

Set `COMMIT_MESSAGE` from that staged evidence before committing:

```bash
COMMIT_MESSAGE="chore: 收尾本次工作"
```

- Use exactly one Conventional Commit type: `feat`, `fix`, `refactor`, `docs`, `test`, or `chore`.
- Write a concise subject that names the **primary shipped outcome**, not the mechanics of committing, pushing, archiving, or "updating changes". Inspect the relevant staged hunks when filenames and stats are not enough to identify that outcome.
- Keep `COMMIT_MESSAGE="chore: 收尾本次工作"` only when the staged evidence genuinely cannot support a more specific summary.
- Archive files are ignored by INV-9 and therefore must never influence the staged outcome or commit subject. One case does reach the staged diff: a sealed contract that was tracked at the repo root shows up as a **deletion of the old root path** (its new copy under `.claude/archived/` is ignored, so no tracked path enters the archive and INV-9's pre-move check still holds). That deletion is a legitimate staged change — do not try to unstage it — but it is session cleanup, so it must never dominate the commit subject; name the substantive outcome instead.

Commit using the selected message:

```bash
git commit -m "$COMMIT_MESSAGE"
```

If commit succeeds → output: 「已提交：{$COMMIT_MESSAGE}」

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
   If the `pull --no-rebase` itself hits a merge conflict → `git -C "$MAIN_REPO" merge --abort`, output 「整合 origin/{TARGET} 有衝突，已中止；主 repo 保持乾淨，請手動整合後再 ship。」 and stop — the main repo is never left mid-merge (which would poison the next /ship's item-1 cleanliness check). If the push still fails for any other reason → output 「Push {TARGET} 失敗：{error}」 and stop. Never `--force` (use `--force-with-lease` only if the user explicitly asks).

On success → output 「已合併 {BRANCH} → {TARGET} 並推送至 origin/{TARGET}。」 (The main repo is left on `$TARGET`.)

---

## Step 5 — Worktree cleanup (conditional, safety-gated)

```bash
git rev-parse --git-dir
```

If the output contains `.git/worktrees/`:

1. Capture variables before any removal, and pick the ref the work should now live on: `SAFE_REF="origin/$TARGET"` in Mode B, else `SAFE_REF="origin/$BRANCH"`.
   ```bash
   WORKTREE_PATH=$(pwd)
   BRANCH=$(git rev-parse --abbrev-ref HEAD)
   MAIN_REPO=$(dirname "$(git rev-parse --git-common-dir)")
   ```
2. **Teardown** — Run `bash "${CLAUDE_SKILL_DIR}/scripts/cleanup-worktree.sh" "$WORKTREE_PATH" "$BRANCH" "$SAFE_REF" "$MAIN_REPO"` — execute it; do not read it as a reference. The script encapsulates the whole chain: the merge-base safety gate (INV-4; the ancestor check is exact — it never falsely refuses a merged branch and never silently discards unmerged work), the three-tier removal chain whose `rm -rf` fallback runs only behind the INV-6 guard plus a worktree-registry check, and the `branch -D` deletion (INV-5). It prints one machine-readable status line. If `"${CLAUDE_SKILL_DIR}/scripts/cleanup-worktree.sh"` does not exist or cannot be executed (bash reports no such file / permission denied, so no machine-readable status line is produced) → treat it as the conservative GATE_FAIL branch: do NOT substitute a manual `git worktree remove` or `rm -rf` chain; leave the worktree and branch exactly as they are, output 「清理腳本遺失或無法執行，保留 worktree；請確認 plugin 安裝完整後重跑 /ship。」, and record this status in the Session end output's Worktree field.
3. Render the status line as the user-facing 繁中 message:
   - `GATE_FAIL …` → the work is **not** yet on `$SAFE_REF`; nothing was destroyed. Output 「分支 {BRANCH} 的工作尚未確認落地到 {SAFE_REF}，保留 worktree 以免遺失；請確認 merge/push 後再清理。」
   - `GUARD_REFUSED …` → the destructive fallback was refused and the worktree is left intact. Output 「worktree 路徑無法安全確認，停止強制刪除以免誤刪」
   - `REMOVED …` → output 「Worktree 已清理：{WORKTREE_PATH}，分支 {BRANCH} 已刪除。」
   - `BRANCH_DELETE_FAILED …` → the worktree was removed but its branch could not be deleted; the worktree is gone, the branch remains. Output 「Worktree 已清理：{WORKTREE_PATH}，但分支 {BRANCH} 刪除失敗，請手動執行 `git branch -D {BRANCH}` 清除。」
   - Any other non-zero exit → report the raw status line in the session end output's Worktree field.

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
