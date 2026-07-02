#!/usr/bin/env bash
# Fixture-repo tests for plugins/baransu/skills/ship/scripts/cleanup-worktree.sh
# (ship-1: Step 5 teardown chain scriptified — merge-base gate, three-tier
# removal chain, INV-6 + registry guard, branch -D).
#
# Coverage:
#   T1: argc != 4 → exit 2
#   T2: unmerged branch → GATE_FAIL, exit != 0, worktree intact
#   T3: merged branch → REMOVED, exit 0, worktree gone, branch deleted
#   T4: empty WORKTREE_PATH → GUARD_REFUSED, exit != 0, worktree intact
#   T5: WORKTREE_PATH=/ → GUARD_REFUSED, exit != 0
#   T6: swapped args (main repo path passed as WORKTREE_PATH) → GUARD_REFUSED,
#       main repo intact
#   T7: plain directory without .git lineage → GUARD_REFUSED, directory intact
#       (rm -rf not executed)
#   T8: tier-3 fallback on a registered-but-unremovable worktree → guard passes,
#       rm -rf + prune + branch -D → REMOVED, exit 0
set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SCRIPT="$ROOT/plugins/baransu/skills/ship/scripts/cleanup-worktree.sh"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
TMP="$(realpath "$TMP")"

PASS=0
FAIL=0
FAILED_TESTS=()

pass() { PASS=$((PASS + 1)); echo "  PASS: $1"; }
fail() {
  FAIL=$((FAIL + 1))
  FAILED_TESTS+=("$1")
  echo "  FAIL: $1"
  if [ -n "${2:-}" ]; then echo "        $2"; fi
}

gitc() { # gitc <repo> <args…> — git with a fixed throwaway identity
  local repo="$1"
  shift
  git -C "$repo" -c user.name=baransu-test -c user.email=test@example.invalid \
    -c commit.gpgsign=false "$@"
}

setup_fixture() { # $1 = name → sets MAIN, WT: main repo on main + worktree on feat
  local base="$TMP/$1"
  MAIN="$base/main-repo"
  WT="$base/wt"
  mkdir -p "$base"
  git init -q -b main "$MAIN"
  gitc "$MAIN" commit -q --allow-empty -m init
  git -C "$MAIN" worktree add -q -b feat "$WT" main
}

# ---------------------------------------------------------------------------
# T1: argc != 4 → exit 2 (usage error), nothing else
# ---------------------------------------------------------------------------
echo "T1: argc != 4 exits 2..."
bash "$SCRIPT" a b c >/dev/null 2>&1
rc3=$?
bash "$SCRIPT" >/dev/null 2>&1
rc0=$?
if [ "$rc3" -eq 2 ] && [ "$rc0" -eq 2 ]; then
  pass "T1: 3 args and 0 args both exit 2"
else
  fail "T1: expected exit 2 for argc != 4" "got rc3=$rc3 rc0=$rc0"
fi

# ---------------------------------------------------------------------------
# T2: unmerged branch → GATE_FAIL, exit != 0, worktree left intact
# ---------------------------------------------------------------------------
echo "T2: unmerged branch is refused by the merge-base gate..."
setup_fixture t2
echo x >"$WT/f"
git -C "$WT" add f
gitc "$WT" commit -q -m wip
out=$(bash "$SCRIPT" "$WT" feat main "$MAIN")
rc=$?
if [ "$rc" -ne 0 ] && printf '%s\n' "$out" | grep -q '^GATE_FAIL ' \
  && [ -d "$WT" ] && git -C "$MAIN" worktree list --porcelain | grep -qxF "worktree $WT" \
  && git -C "$MAIN" show-ref -q refs/heads/feat; then
  pass "T2: GATE_FAIL, exit != 0, worktree and branch intact"
else
  fail "T2: unmerged branch not safely refused" "rc=$rc out=$out"
fi

# ---------------------------------------------------------------------------
# T3: merged branch → REMOVED, exit 0, worktree gone, branch deleted
# ---------------------------------------------------------------------------
echo "T3: merged branch removal succeeds..."
setup_fixture t3
echo x >"$WT/f"
git -C "$WT" add f
gitc "$WT" commit -q -m wip
gitc "$MAIN" merge -q feat
out=$(bash "$SCRIPT" "$WT" feat main "$MAIN")
rc=$?
if [ "$rc" -eq 0 ] && printf '%s\n' "$out" | grep -q '^REMOVED ' \
  && [ ! -e "$WT" ] && ! git -C "$MAIN" show-ref -q refs/heads/feat; then
  pass "T3: REMOVED, exit 0, worktree gone, branch deleted"
else
  fail "T3: merged removal did not complete" "rc=$rc out=$out"
fi

# ---------------------------------------------------------------------------
# T4: empty WORKTREE_PATH → GUARD_REFUSED, exit != 0, worktree intact
# ---------------------------------------------------------------------------
echo "T4: empty WORKTREE_PATH is refused..."
setup_fixture t4
out=$(bash "$SCRIPT" "" feat main "$MAIN")
rc=$?
if [ "$rc" -ne 0 ] && printf '%s\n' "$out" | grep -q '^GUARD_REFUSED' \
  && [ -d "$WT" ] && git -C "$MAIN" show-ref -q refs/heads/feat; then
  pass "T4: GUARD_REFUSED, worktree and branch intact"
else
  fail "T4: empty path not refused" "rc=$rc out=$out"
fi

# ---------------------------------------------------------------------------
# T5: WORKTREE_PATH=/ → GUARD_REFUSED, exit != 0
# ---------------------------------------------------------------------------
echo "T5: root path is refused..."
setup_fixture t5
out=$(bash "$SCRIPT" / feat main "$MAIN")
rc=$?
if [ "$rc" -ne 0 ] && printf '%s\n' "$out" | grep -q '^GUARD_REFUSED'; then
  pass "T5: GUARD_REFUSED on /"
else
  fail "T5: root path not refused" "rc=$rc out=$out"
fi

# ---------------------------------------------------------------------------
# T6: swapped args — main repo path passed as WORKTREE_PATH → GUARD_REFUSED,
#     main repo intact (INV-6 alone would pass; the registry guard refuses)
# ---------------------------------------------------------------------------
echo "T6: swapped args are refused and the main repo survives..."
setup_fixture t6
out=$(bash "$SCRIPT" "$MAIN" feat main "$WT")
rc=$?
if [ "$rc" -ne 0 ] && printf '%s\n' "$out" | grep -q '^GUARD_REFUSED' \
  && [ -d "$MAIN/.git" ] && git -C "$MAIN" rev-parse -q --verify HEAD >/dev/null \
  && [ -d "$WT" ]; then
  pass "T6: GUARD_REFUSED, main repo and worktree intact"
else
  fail "T6: swapped args destroyed something or were not refused" "rc=$rc out=$out"
fi

# ---------------------------------------------------------------------------
# T7: plain directory without .git lineage → GUARD_REFUSED, directory intact
# ---------------------------------------------------------------------------
echo "T7: plain directory without git lineage is refused..."
setup_fixture t7
PLAIN="$TMP/t7/plain"
mkdir -p "$PLAIN"
echo keep >"$PLAIN/sentinel"
out=$(bash "$SCRIPT" "$PLAIN" feat main "$MAIN")
rc=$?
if [ "$rc" -ne 0 ] && printf '%s\n' "$out" | grep -q '^GUARD_REFUSED' \
  && [ -f "$PLAIN/sentinel" ]; then
  pass "T7: GUARD_REFUSED, directory intact, rm -rf not executed"
else
  fail "T7: plain directory not safely refused" "rc=$rc out=$out"
fi

# ---------------------------------------------------------------------------
# T8: registered worktree that tiers 1-2 cannot remove (corrupted .git file)
#     → guard passes, tier-3 rm -rf + prune runs, branch deleted → REMOVED
# ---------------------------------------------------------------------------
echo "T8: tier-3 fallback fires on a registered-but-unremovable worktree..."
setup_fixture t8
echo "gitdir: /nonexistent" >"$WT/.git"
out=$(bash "$SCRIPT" "$WT" feat main "$MAIN")
rc=$?
if [ "$rc" -eq 0 ] && printf '%s\n' "$out" | grep -q '^REMOVED ' \
  && [ ! -e "$WT" ] && ! git -C "$MAIN" show-ref -q refs/heads/feat; then
  pass "T8: REMOVED via tier-3 fallback, worktree gone, branch deleted"
else
  fail "T8: tier-3 fallback did not complete" "rc=$rc out=$out"
fi

# ---------------------------------------------------------------------------
# summary
# ---------------------------------------------------------------------------
echo ""
echo "Results: $PASS passed, $FAIL failed"
if [ "${#FAILED_TESTS[@]}" -gt 0 ]; then
  echo "Failed tests:"
  for t in "${FAILED_TESTS[@]}"; do echo "  - $t"; done
  exit 1
fi
exit 0
