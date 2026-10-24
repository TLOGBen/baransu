---
name: ship
description: "Wraps up a session: archives baransu working directories, commits under the repo's own identity and message style, pushes, merges one-way into named targets (`$baransu:ship uat main`), and removes the worktree. Trigger On '$baransu:ship', '收工', '上傳收尾', '結束這輪'."
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

# $baransu:ship — session cleanup

All user-visible output is in **Traditional Chinese (繁體中文)**.

No user confirmation required. The steps below run automatically.

---

## Outcome Contract

- **Outcome**: The session's working files are archived locally without entering Git, and all other pending changes are committed and pushed — optionally merged from this branch into each named target branch.
- **Done when**: Archivable items are moved into the main working tree's ignored `.codex/archived/`, no archive path is tracked, `git status --porcelain` is empty after the commit, and the work is on origin (the current branch pushed and, for each named target, the branch merged into it and that target pushed); when run inside a worktree whose work is confirmed on origin, the worktree is removed and its branch deleted.
- **Evidence**: The archive ignore/untracked checks, the session end output reporting the archived item count, the commit identity, the commit message (or 「跳過」), the upstream integration line (「拉入 N 個 commit」, 「無需整合」, or 「新分支，略過」), the push target and each target merge result, and the worktree cleanup status.
- **Output**: Local-only archived directories under the main working tree's `.codex/archived/`, a pushed git commit when non-archive changes exist, and the 繁中 session end report.
- **Automation**: ultracode=neutral, loop=assisted（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）
  In the same non-interactive pass, read `references/loop-pauses.md` for this skill's own PAUSE classification.

## Invariants

Named red-lines, each enforced by the step in parentheses; none is optional. The step keeps its own if-then recovery — these name the rule it enforces.

- **INV-1 — One named archive source, nothing else.** Exactly one source feeds the archive: the Step 1 `ARCHIVE_DIRS` allowlist, swept dir by dir. Everything outside it is never archived — the `read` / `learn` / `draw` products and all Claude Code infrastructure (`worktrees/`, `projects/`, `jobs/`, `plugins/`, `settings*.json`) stay in place. The allowlist is explicit; it does not open a discretionary sweep. (Step 2)
- **INV-2 — Source dirs are emptied, never deleted.** Archiving moves items out; the source directory itself stays in place. (Step 2)
- **INV-3 — Never force-push.** `--force` is forbidden on every push; `--force-with-lease` is used only when the user explicitly asks. (Step 4)
- **INV-4 — No worktree teardown until the work is on origin.** A worktree is destroyed only after `git merge-base --is-ancestor` confirms the branch is on `$SAFE_REF`. (Step 5)
- **INV-5 — Branch deletion uses `-D`, not `-d`.** After a merge the branch may read as unmerged locally, so `-d` fails. (Step 5)
- **INV-6 — `rm -rf` is only run on a validated worktree path.** The third-tier `rm -rf "$WORKTREE_PATH"` fallback runs only after a precondition guard confirms `$WORKTREE_PATH` is non-empty, is not `/`, and carries `.git`/`.git/worktrees` lineage; if the guard fails, `rm -rf` is skipped and the worktree is left intact. (Step 5)
- **INV-7 — No blind staging of secret-pattern files.** Before `git add -A`, every untracked/modified path from `git status --porcelain` is matched against the Step 3 closed pattern list; any match stops the commit before staging. (Step 3)
- **INV-8 — Commits speak for this repo, not for this machine.** The author identity, the message format and the message language come from the repo's own history and remote, never from the global git config alone; the subject names the shipped outcome, and no attribution trailer is added unless the user asked. (Step 3)
- **INV-9 — The archive is local-only and outlives the worktree.** It lives in the main working tree, never inside a linked worktree that Step 5 may delete, and is ignored through the repository's shared `info/exclude`, so the rule needs no commit and holds on every branch; the shipping branch tracks no archive path. (Step 2)
- **INV-10 — Never commit over an unverified resolution.** The remote is pulled in before the commit, and every conflict resolution — Step 2b's and each target merge's — is committed only after the Step 2b item 5 checks have each passed on their own exit status. (Step 2b, Step 4)
- **INV-11 — Merges flow one way.** Work goes from the shipping branch into each target, each target merged on its own; a target is never merged back into the shipping branch or into another target. Merge, never rebase, so commit hashes already reported stay valid. (Step 4)

## Step 0 — Parse targets

The optional argument names zero or more target branches, written `<branch>…`, `到 <branch>…`, or `to <branch>…`. Strip one leading `到` / `to` token; every remaining token (split on whitespace, `,` or `、`) is a target. `$TARGETS` keeps them in the order given, with duplicates and the current branch dropped.

- `$baransu:ship` → `$TARGETS` empty → **current-branch mode** (Step 4 Mode A).
- `$baransu:ship main` / `$baransu:ship uat main` / `$baransu:ship 到 sit uat` → **land-on-targets mode** (Step 4 Mode B), one merge per target in that order.

## Step 1 — Detect

Git probe first — run `git rev-parse --git-dir 2>/dev/null`. If it fails (the project is not a git repo), output 「此專案不是 git repo：$baransu:ship 的 commit／push／worktree 流程無法執行，已停止。如需歸檔請手動處理 .codex/ 工作目錄。」 and stop. The probe MUST run before any archive move: without git there is no commit to anchor moved files, so archiving first would strand them — and every later git step (commit, push, worktree teardown) would wedge.

Check three inputs: whether the workspace dirs hold archivable items, whether the git working tree has pending changes, AND whether HEAD carries commits that have not landed on origin yet. Stop only when **all three** are empty — otherwise there is still work to ship even when the other sides are empty. A clean tree does not mean the work is out: commits made earlier in the session (or in an earlier session) still need Step 4.

```bash
ARCHIVE_DIRS="tmp think draft hunt-report evolve review write prove-it/records"
ARCHIVE_ITEMS=$(python3 -c "import sys, pathlib; print(next((str(p) for d in sys.argv[1].split() if pathlib.Path('.codex', d).is_dir() for p in pathlib.Path('.codex', d).iterdir()), ''))" "$ARCHIVE_DIRS")
GIT_DIRTY=$(git status --porcelain 2>/dev/null | head -1)
UNLANDED=$(git rev-list HEAD --not --remotes 2>/dev/null | head -1)
```

With targets, also run this once per target `$T`, as its own command (zsh does not word-split an unquoted list, so do not loop over one):

```bash
git rev-parse --verify --quiet "origin/$T" >/dev/null || echo "no origin/$T"
git rev-list HEAD --not "origin/$T" 2>/dev/null | head -1
```

Any output there makes `UNLANDED` non-empty: HEAD is not yet in that target, so a branch that is pushed but not yet merged into every target still counts. The remote refs are the ones from the last fetch. A ref that merely lags the remote can only make `UNLANDED` non-empty, which sends the run on to Step 4 where the push is a no-op. The one case it misses is a remote branch deleted or rewound since that fetch; Step 1 does not fetch, so that case stays out of scope here.

(The detect uses python3/pathlib rather than a shell loop over `$ARCHIVE_DIRS`: zsh does not word-split unquoted parameters, so a `for d in $ARCHIVE_DIRS` + `find` pattern silently yields an always-empty `ARCHIVE_ITEMS` under zsh-driven harnesses.)

Decision:

- If `ARCHIVE_ITEMS` is empty AND `GIT_DIRTY` is empty AND `UNLANDED` is empty → output 「沒有可歸檔的工作檔案，git 也乾淨，也沒有待落地的 commit，結束。」 and stop. Do not proceed.
- Otherwise → continue (Step 2 / Step 3 each have their own empty-input fallback; Step 4 lands work unconditionally so unpushed commits from earlier sessions still go out).

---

## Step 2 — Archive

The archive root is the main working tree's `.codex/archived/`, the same place whether $baransu:ship runs there or in a linked worktree:

```bash
MAIN_REPO=$(dirname "$(git rev-parse --path-format=absolute --git-common-dir)")
ARCHIVE_ROOT="$MAIN_REPO/.codex/archived"
```

A linked worktree's own `.codex/archived/` would not survive: Step 5's `git worktree remove` deletes ignored files along with the worktree. Create `$ARCHIVE_ROOT` if it does not exist.

Before moving any item, enforce the local-only boundary:

1. Read the file at `git rev-parse --git-path info/exclude` — the repository's local exclude, one file shared by every worktree. If the exact line `/.codex/archived/` is absent, add that one line with the available file-editing tool (create the file if missing). Do not use shell redirection, and do not edit `.gitignore` for this: the archive belongs to this clone, so its rule stays out of commits and holds on whatever branch the main working tree has checked out.
2. Remove any legacy archive entries from the shipping branch's index while preserving their local files:
   ```bash
   git rm -r --cached --ignore-unmatch -- .codex/archived/
   ```
3. Verify both halves of INV-9:
   ```bash
   git -C "$MAIN_REPO" check-ignore -q .codex/archived/.ship-ignore-probe
   test -z "$(git ls-files .codex/archived/)"
   ```
   If either command fails, output 「archive ignore 驗證失敗：已停止歸檔，未移動
   任何工作檔案。」 and stop.

**Archive allowlist** — exactly the Step 1 `ARCHIVE_DIRS` value, in the same order: `tmp`, `think`, `draft`, `hunt-report`, `evolve`, `review`, `write`, `prove-it/records`. The two lists MUST stay identical; a dir detected in Step 1 but absent here would leave Step 1's detect output unconsumed.

**Never archived**: the `read`, `learn`, `draw`, `design` and `hypothesis` dirs, the prove-it recipe and feature map (`prove-it/recipe.md`, `prove-it/features/`), and any 8.15.0 formal checks not yet moved to `hypothesis/` (`prove-it/formal/`), are kept products and stay in place. Claude Code infrastructure (`worktrees/`, `projects/`, `jobs/`, `plugins/`, `settings*.json`, …) is never touched — the allowlist is explicit precisely so infra is never swept up.

For each dir in the allowlist, for each item directly inside the source directory `.codex/{dir}` of the tree $baransu:ship runs in:
- Destination: `$ARCHIVE_ROOT/{item_name}`
- If destination already exists: rename it to `$ARCHIVE_ROOT/{item_name}-{unix_timestamp}` first
- Move item to destination

Source directories are left empty (not deleted). Archiving is collision-only timestamping — the plain `{item_name}` destination is used when it is free, so archive names stay readable.

Output: 「已歸檔：{N} 個項目 → {ARCHIVE_ROOT}（read/learn/draw/design 與 prove-it 食譜保留）」

`{N}` is the total number of allowlist items moved.

If any move fails → output 「歸檔失敗：{reason}」 and stop.

---

## Step 2b — Integrate upstream locally before committing

Bring the remote in before Step 3 commits, never after. While every local change is still uncommitted, a conflict is resolved in the working tree where it can be read and checked, and the commit Step 3 creates already sits on top of the remote, so Step 4's push is a fast-forward. Merging after the commit instead yields a merge commit whose conflict resolution nobody inspected before it was pushed.

```bash
BRANCH=$(git rev-parse --abbrev-ref HEAD)
git fetch origin
```

- `git fetch origin` fails → output 「整合驗證未通過：無法 fetch origin（{error}）；已停止，未 commit。」 and stop.
- `git rev-parse --verify --quiet "origin/$BRANCH"` fails → the branch is new; Step 4 creates it with `-u`. Record 「新分支，略過」 and continue to Step 3.
- `BEHIND=$(git rev-list --count "HEAD..origin/$BRANCH")` is `0` → record 「無需整合」 and continue to Step 3.
- Otherwise run items 1–5 in order. This integrates the current branch with its own upstream only; targets are merged in Step 4.

1. **Stash** — only when `git status --porcelain` is non-empty:
   ```bash
   git stash push --include-untracked -m "ship: pre-pull"
   ```
   Ignored paths are not stashed and stay in place. The stash fails → output 「整合驗證未通過：stash 失敗（{error}）；已停止，未 commit。」 and stop.
2. **Pull without rebasing**:
   ```bash
   git pull --no-rebase --no-edit origin "$BRANCH"
   ```
   With the tree stashed clean, this pull conflicts only when local commits not yet pushed collide with the remote. On conflict → `git merge --abort`, then `git stash pop` to put the stashed work back, output 「拉取 origin/{BRANCH} 有衝突（本地已有未推送的 commit），已中止合併並還原工作樹；請手動整合後再重跑 $baransu:ship。」 and stop.
3. **Pop** — skipped when item 1 was skipped:
   ```bash
   git stash pop
   ```
   A clean pop → output 「已整合 origin/{BRANCH}：拉入 {BEHIND} 個 commit，工作樹變更已還原。」 and go to item 5. A conflicted pop keeps the stash entry and marks the conflicted paths unmerged → go to item 4.
4. **Resolve** every path listed by `git diff --name-only --diff-filter=U`, in the working tree. Read both sides and, when present, the base — conflict blocks may be in diff3 form (`<<<<<<<`, `|||||||` base, `=======`, `>>>>>>>`), so never assume a block has only two parts. Each conflicting hunk is one of three kinds:
   - **Both sides belong** — independent additions that only sit next to each other (CHANGELOG entries, table rows, list items): keep both, in the order the file's own convention gives.
   - **Derived value** — something computed from the rest of the content (a count, a total, a version): recompute it from the merged result instead of picking either side's literal; a version takes what the project's versioning rule gives for the combined change.
   - **Contradicting intent** — the two sides want different outcomes for the same thing and nothing in the repo says which wins. This is the only kind that stops: never guess. Name the file, the hunk, and what each side was trying to do, and leave the decision to the user.

   Mark each resolved path with `git add <path>`. Here a contradicting intent leaves the conflict and the stash entry as they are, outputs 「stash 還原後有意圖互相矛盾的衝突：{檔案}：{段落}——本地想 {…}，遠端想 {…}；已停止，衝突與 stash 保留在工作樹，請決定保留哪一邊後重跑 $baransu:ship。」 and stops.
5. **Verify** — read each check's exit status on its own:
   - `git diff --name-only --diff-filter=U` prints nothing;
   - `git grep -nE '^(<<<<<<<|\|\|\|\|\|\|\||>>>>>>>) '` finds no conflict marker;
   - every structured file the integration touched still parses (for JSON: `python3 -m json.tool <file> >/dev/null`);
   - when the project documents a single test entrypoint (for example `make test`), it passes.

   Drop the stash entry only after every check above passes: `git stash drop`, needed only when item 3 conflicted (a clean pop already removed it). Any check fails → output 「整合驗證未通過：{原因}；已停止，未 commit。」 and stop.

**Never run this step, Step 3 and Step 4 as one `&&` chain or under `set -e`.** Some agent harnesses execute each shell command inside an `eval` nested in an `&&` list, where errexit is silently disabled: a failed resolution then still reaches `git commit` and `git push`. Run each state-changing command on its own and read its exit status before issuing the next.

---

## Step 3 — Commit

**Secret gate (INV-7)** — run immediately before `git add -A`: run `git status --porcelain` and match each untracked/modified path's filename against this fixed, closed pattern list: `.env`, `.env.*`, `*.pem`, `*.key`, `id_rsa*`, `*.p12`, `credentials*.json`. If any path matches → output 「偵測到疑似機敏檔案：{列出檔名}，已停止 commit；請確認內容、加入 .gitignore 或手動處理後再重跑 $baransu:ship。」 and stop. If none match → proceed to `git add -A` unchanged.

**Identity (INV-8)** — decide whose commit this is from the repo, not from this machine. The git config can belong to another repo's account: a global config switched for one repo has put a personal identity on a company repo and the reverse.

```bash
git log -20 --format='%an <%ae>' | sort | uniq -c | sort -rn
git remote get-url origin
git config user.name
git config user.email
```

The repo's identity is the recent author that fits the remote's host and owner: when history shows one author and the remote does not contradict it, that author; when history is mixed, the author whose name or email matches the remote's owner or host. When the history is empty, or no recent author fits the remote, or more than one does → output 「無法判斷這個 repo 該用哪個 commit 身分：{候選身分與遠端}；已停止，未 commit，請指定身分。」 and stop. When the git config already gives the repo's identity, commit as usual; when it differs, pass the repo's identity on every commit and merge $baransu:ship creates — `git -c user.name="$NAME" -c user.email="$EMAIL" commit …` — without changing the config.

Stage first, then inspect what will actually ship:

```bash
git add -A
git diff --cached --name-status
git diff --cached --stat
git log -15 --format=%s
```

Set `COMMIT_MESSAGE` from that staged evidence, in the repo's own message style, before committing:

```bash
COMMIT_MESSAGE="chore: 收尾本次工作"
```

- Follow the format and language of the repo's recent subjects: its type prefixes or their absence, scope style, language, and conventions such as a version in parentheses. A repo with no history uses Conventional Commits in the user's language.
- Write a concise subject that names the **primary shipped outcome**, not the mechanics of committing, pushing, archiving, or "updating changes". Inspect the relevant staged hunks when filenames and stats are not enough to identify that outcome.
- Keep a generic wrap-up subject such as `chore: 收尾本次工作` (rewritten into the repo's format) only when the staged evidence genuinely cannot support a more specific summary.
- The message carries no `Co-Authored-By` or other attribution trailer unless the user asked for one.
- Archive files are ignored by INV-9 and therefore must never influence the staged outcome or commit subject.

Commit using the selected message (with the identity `-c` pair when the identity check called for it):

```bash
git commit -m "$COMMIT_MESSAGE"
```

If commit succeeds → output: 「已提交：{$COMMIT_MESSAGE}（{NAME} <{EMAIL}>）」

If nothing to commit (exit code 1, message contains "nothing to commit") → output 「無待提交的變更，跳過 commit。」 Continue to Step 4.

If commit fails for another reason → output 「Commit 失敗：{error}」 and stop.

---

## Step 4 — Push, then land on each target

```bash
BRANCH=$(git rev-parse --abbrev-ref HEAD)
MAIN_REPO=$(dirname "$(git rev-parse --path-format=absolute --git-common-dir)")
```

### Mode A — push the current branch (always runs)

```bash
git push origin "$BRANCH" || git push -u origin "$BRANCH"
```

On success → output 「已推送至 origin/{BRANCH}。」 If the push is rejected as non-fast-forward (the remote moved after Step 2b) → output 「Push 被拒：origin/{BRANCH} 在整合後又有新 commit；請重跑 $baransu:ship（會先在本地整合）。」 and stop — do not pull here: the next $baransu:ship integrates in Step 2b, before its commit, where a conflict is still resolvable in the working tree. On any other failure → output 「Push 失敗：{error}」 and stop.

With `$TARGETS` empty, Step 4 ends here. With targets, Mode A still runs first: each target is merged from this branch on its own, often days apart, so the branch has to outlive this worktree on origin — no target can stand in for it (INV-11).

### Mode B — `$TARGETS` set: merge `$BRANCH` into each target, one at a time

Run on the main repo (`$MAIN_REPO`) — the targets are checked out there, not in this worktree. **Never use `--force`.**

1. The main repo must be clean before switching branches: run `git -C "$MAIN_REPO" status --porcelain`. If its output is non-empty → output 「主 repo 有未提交變更，無法切換到目標分支；請先處理後重跑 $baransu:ship {TARGETS}。」 and stop. Record where it stands, to put it back when the run ends: `ORIG=$(git -C "$MAIN_REPO" symbolic-ref -q --short HEAD || git -C "$MAIN_REPO" rev-parse HEAD)`.
2. For each `$TARGET` in `$TARGETS`, in order, run items 3–5. A stop in any item ends the run: targets already landed stay landed, later targets are not attempted, and the stop message names both.
3. Put the main repo on `$TARGET`, caught up with origin:
   ```bash
   git -C "$MAIN_REPO" checkout "$TARGET" 2>/dev/null \
     || git -C "$MAIN_REPO" checkout -B "$TARGET" "origin/$TARGET" 2>/dev/null \
     || { echo "no such branch"; }   # → output 「找不到目標分支 {TARGET}（本地與 origin 皆無）；請先建立或改用現有分支」 and stop
   git -C "$MAIN_REPO" merge --ff-only "origin/$TARGET"   # only when origin/$TARGET exists
   ```
   The fast-forward fails only when the local `$TARGET` carries commits origin lacks → output 「本地 {TARGET} 有 origin 沒有的 commit，無法單向併入；請先處理後重跑 $baransu:ship {剩下的目標}。」 and stop.
4. Merge (no-ff), with the Step 3 identity and in the repo's own merge-subject format when its history has one:
   ```bash
   git -C "$MAIN_REPO" merge --no-ff "$BRANCH" -m "merge: $BRANCH → $TARGET (via $baransu:ship)"
   ```
   On conflict, resolve it in this merge, in `$MAIN_REPO`: classify and resolve each hunk under Step 2b item 4 — `$BRANCH` is one side, `$TARGET` the other — then run Step 2b item 5's checks with `$MAIN_REPO` as the working directory, and only when every check passes, `git -C "$MAIN_REPO" commit --no-edit`. Never rebase or cherry-pick around the conflict.
   - A contradicting intent → `git -C "$MAIN_REPO" merge --abort`, output 「合併 {BRANCH} → {TARGET} 有意圖互相矛盾的衝突：{檔案}：{段落}——{BRANCH} 想 {…}，{TARGET} 想 {…}；已中止這次合併。已落地：{已完成的目標或「無」}；未執行：{剩下的目標}。請決定保留哪一邊後重跑 $baransu:ship {剩下的目標}。」 and stop. On that rerun, the user's decision resolves the hunk.
   - A failed check → `git -C "$MAIN_REPO" merge --abort`, output 「整合驗證未通過：{原因}；已中止合併 {BRANCH} → {TARGET}。」 and stop.

   The main repo is never left mid-merge: that would fail the next $baransu:ship's item-1 cleanliness check.
5. Push without forcing:
   ```bash
   git -C "$MAIN_REPO" push origin "$TARGET"
   ```
   A non-fast-forward rejection means origin moved during this run: `git -C "$MAIN_REPO" pull --no-rebase --no-edit origin "$TARGET"`, a conflict there handled exactly as in item 4, then push once more. Any other failure → output 「Push {TARGET} 失敗：{error}」 and stop. Never `--force` (use `--force-with-lease` only if the user explicitly asks).

   On success → output 「已合併 {BRANCH} → {TARGET} 並推送至 origin/{TARGET}。」

When the run ends — after the last target or at a stop — put the main repo back: `git -C "$MAIN_REPO" checkout "$ORIG"`.

---

## Step 5 — Worktree cleanup (conditional, safety-gated)

```bash
git rev-parse --git-dir
```

If the output contains `.git/worktrees/`:

1. Capture variables before any removal. The work must be on the branch's own remote ref, which Step 4 pushed in both modes: `SAFE_REF="origin/$BRANCH"`.
   ```bash
   WORKTREE_PATH=$(pwd)
   BRANCH=$(git rev-parse --abbrev-ref HEAD)
   MAIN_REPO=$(dirname "$(git rev-parse --path-format=absolute --git-common-dir)")
   ```
2. **Teardown** — Run `bash "./scripts/cleanup-worktree.sh" "$WORKTREE_PATH" "$BRANCH" "$SAFE_REF" "$MAIN_REPO"` — execute it; do not read it as a reference. The script encapsulates the whole chain: the merge-base safety gate (INV-4; the ancestor check is exact — it never falsely refuses a merged branch and never silently discards unmerged work), the three-tier removal chain whose `rm -rf` fallback runs only behind the INV-6 guard plus a worktree-registry check, and the `branch -D` deletion (INV-5). It prints one machine-readable status line. If `"./scripts/cleanup-worktree.sh"` does not exist or cannot be executed (bash reports no such file / permission denied, so no machine-readable status line is produced) → treat it as the conservative GATE_FAIL branch: do NOT substitute a manual `git worktree remove` or `rm -rf` chain; leave the worktree and branch exactly as they are, output 「清理腳本遺失或無法執行，保留 worktree；請確認 plugin 安裝完整後重跑 $baransu:ship。」, and record this status in the Session end output's Worktree field.
3. Render the status line as the user-facing 繁中 message:
   - `GATE_FAIL …` → the work is **not** yet on `$SAFE_REF`; nothing was destroyed. Output 「分支 {BRANCH} 的工作尚未確認落地到 {SAFE_REF}，保留 worktree 以免遺失；請確認 merge/push 後再清理。」
   - `GUARD_REFUSED …` → the destructive fallback was refused and the worktree is left intact. Output 「worktree 路徑無法安全確認，停止強制刪除以免誤刪」
   - `REMOVED …` → output 「Worktree 已清理：{WORKTREE_PATH}，分支 {BRANCH} 已刪除（origin/{BRANCH} 保留，之後可再併入其他目標）。」
   - `BRANCH_DELETE_FAILED …` → the worktree was removed but its branch could not be deleted; the worktree is gone, the branch remains. Output 「Worktree 已清理：{WORKTREE_PATH}，但分支 {BRANCH} 刪除失敗，請手動執行 `git branch -D {BRANCH}` 清除。」
   - Any other non-zero exit → report the raw status line in the session end output's Worktree field.

If not in a worktree → skip silently.

---

## Session end output

```
$baransu:ship 完成。

歸檔：{N} 個項目 → {ARCHIVE_ROOT}（或「無可歸檔檔案」；read/learn/draw/design 與 prove-it 食譜保留）
整合：{「拉入 N 個 commit」、「無需整合」或「新分支，略過」}
身分：{NAME <EMAIL>}（{「與 git config 相同」或「依 repo 判斷，未採用 git config 的 X」}）
Commit：{commit message 或「跳過」}
Push：origin/{BRANCH}
併入：{每個目標一筆「BRANCH → TARGET ✓（自動解 N 處衝突）」，或「無」}
Worktree：{已清理 path 或「保留（工作未落地）」或「不適用」}
```
