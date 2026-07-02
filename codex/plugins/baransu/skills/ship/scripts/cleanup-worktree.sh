#!/usr/bin/env bash
# cleanup-worktree.sh — /baransu:ship Step 5 worktree teardown.
#
# Usage: bash cleanup-worktree.sh WORKTREE_PATH BRANCH SAFE_REF MAIN_REPO
#
# Encapsulates Step 5 exactly: the merge-base --is-ancestor safety gate
# (INV-4), the three-tier removal chain with the INV-6 guard, and the branch
# deletion (INV-5). Prints one machine-readable status line on stdout; the
# model renders it as the skill's Traditional Chinese message:
#   GATE_FAIL branch=<b> safe_ref=<r>   work not on SAFE_REF; nothing destroyed
#   GUARD_REFUSED path=<p>              rm -rf fallback refused; worktree intact
#   BRANCH_DELETE_FAILED branch=<b>     worktree removed, branch deletion failed
#   REMOVED worktree=<p> branch=<b>     teardown complete
# Exit codes: 0 = REMOVED; 1 = any refusal/failure above; 2 = usage error.
#
# CLAUDE.md Non-obvious Invariants — quoted verbatim, enforced by the code
# below; do not "optimize" either away:
# - **`/ship` branch deletion uses `-D` not `-d`**: after push the branch is unmerged locally, so `-d` always fails. Both steps need `git -C "$MAIN_REPO" branch -D`.
# - Keep the three-tier `||` chain ordering and the `branch -D` intact:
#   `worktree remove` → `worktree remove --force` → INV-6-guarded `rm -rf` + prune.

set -u

if [ "$#" -ne 4 ]; then
  echo "usage: bash cleanup-worktree.sh WORKTREE_PATH BRANCH SAFE_REF MAIN_REPO" >&2
  exit 2
fi

WORKTREE_PATH="$1"
BRANCH="$2"
SAFE_REF="$3"
MAIN_REPO="$4"

# INV-4 — No worktree teardown until the work is on origin. The ancestor
# check is exact: it never falsely refuses a merged branch and never
# silently discards unmerged work.
if ! git -C "$MAIN_REPO" merge-base --is-ancestor "$BRANCH" "$SAFE_REF" 2>/dev/null; then
  echo "GATE_FAIL branch=$BRANCH safe_ref=$SAFE_REF"
  exit 1
fi

# Tier 3 of the removal chain. INV-6 — `rm -rf` is only run on a validated
# worktree path: `$WORKTREE_PATH` is non-empty, is not `/`, and carries
# `.git`/`.git/worktrees` lineage. On top of INV-6 (additive, not a
# replacement), a registry guard: realpath of $WORKTREE_PATH must appear as
# a worktree entry in `git -C "$MAIN_REPO" worktree list --porcelain` AND
# differ from the main working tree's toplevel; otherwise GUARD_REFUSED and
# the destructive fallback is skipped.
tier3_guarded_rm() {
  local wt_real porcelain main_toplevel main_real
  if [ -n "$WORKTREE_PATH" ] && [ "$WORKTREE_PATH" != "/" ] && [ -e "$WORKTREE_PATH/.git" ]; then
    wt_real=$(realpath "$WORKTREE_PATH" 2>/dev/null) || wt_real=""
    porcelain=$(git -C "$MAIN_REPO" worktree list --porcelain 2>/dev/null) || porcelain=""
    main_toplevel=$(printf '%s\n' "$porcelain" | sed -n 's/^worktree //p' | head -n 1)
    main_real=$(realpath "$main_toplevel" 2>/dev/null) || main_real=""
    if [ -n "$wt_real" ] && [ -n "$main_real" ] \
      && [ "$wt_real" != "$main_real" ] \
      && printf '%s\n' "$porcelain" | grep -qxF "worktree $wt_real"; then
      rm -rf "$WORKTREE_PATH" && git -C "$MAIN_REPO" worktree prune
      return $?
    fi
  fi
  echo "GUARD_REFUSED path=$WORKTREE_PATH"
  return 1
}

# Three-tier removal chain — the `||` ordering is load-bearing (see the
# invariant quoted above): plain remove, then --force, then the guarded
# rm -rf fallback. A GUARD_REFUSED tier 3 exits before any branch deletion,
# leaving the worktree intact.
git -C "$MAIN_REPO" worktree remove "$WORKTREE_PATH" 2>/dev/null \
  || git -C "$MAIN_REPO" worktree remove --force "$WORKTREE_PATH" 2>/dev/null \
  || tier3_guarded_rm \
  || exit 1

# INV-5 — Branch deletion uses `-D`, not `-d`: after a merge the branch may
# still read as unmerged locally, so `-d` fails — `-D` is required.
if ! git -C "$MAIN_REPO" branch -D "$BRANCH" 2>/dev/null; then
  echo "BRANCH_DELETE_FAILED branch=$BRANCH"
  exit 1
fi

echo "REMOVED worktree=$WORKTREE_PATH branch=$BRANCH"
exit 0
