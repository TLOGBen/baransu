#!/usr/bin/env bash
# Machine anchors for /ship Step 2b — integrate upstream locally before committing
# (stash → pull → pop → resolve → verify), added after a 6.0.0 ship pushed a merge
# commit that still carried diff3 conflict markers.
#
# Assertions:
#   U1  Step 2b exists and sits between Step 2 (Archive) and Step 3 (Commit)
#   U2  the three git commands are present and ordered stash → pull → pop
#   U3  resolution rules: diff3 clause, unmerged check, conflict-marker grep,
#       stash dropped only after every check passes, no &&/set -e chaining
#   U4  the four user-facing messages of Step 2b, byte-exact
#   U5  INV-10, the Mode A rejection hint, the session-end 整合 line
#   U6  loop-pauses registers the judgment-conflict stop
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SHIP_MD="$ROOT/plugins/baransu/skills/ship/SKILL.md"
LOOP_PAUSES="$ROOT/plugins/baransu/skills/ship/references/loop-pauses.md"
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

# assert_lit <name> <file> <literal>   — literal present on one line (grep -F)
assert_lit() {
  local name="$1" file="$2" lit="$3"
  if [ ! -f "$file" ]; then fail "$name: file missing: $file"; return; fi
  if grep -qF -- "$lit" "$file"; then pass "$name"; else fail "$name" "not found in ${file#$ROOT/}: [$lit]"; fi
}

# line_of <file> <literal> — first line number holding the literal, or 0
line_of() { grep -nF -- "$2" "$1" 2>/dev/null | head -1 | cut -d: -f1 | grep -E '^[0-9]+$' || echo 0; }

# assert_order <name> <file> <literal>... — each literal first appears after the previous one
assert_order() {
  local name="$1" file="$2"; shift 2
  local prev=0 lit n
  for lit in "$@"; do
    n=$(line_of "$file" "$lit")
    if [ "$n" -eq 0 ] || [ "$n" -le "$prev" ]; then
      fail "$name" "out of order or missing at [$lit] (line $n, previous $prev)"; return
    fi
    prev=$n
  done
  pass "$name"
}

STEP2B='## Step 2b — Integrate upstream locally before committing'
STASH='git stash push --include-untracked -m "ship: pre-pull"'
PULL='git pull --no-rebase --no-edit origin "$BRANCH"'
POP='git stash pop'

echo "U1: Step 2b placement..."
assert_lit   "U1a: Step 2b heading" "$SHIP_MD" "$STEP2B"
assert_order "U1b: Step 2 < Step 2b < Step 3" "$SHIP_MD" '## Step 2 — Archive' "$STEP2B" '## Step 3 — Commit'

echo "U2: stash → pull → pop..."
assert_lit   "U2a: stash command" "$SHIP_MD" "$STASH"
assert_lit   "U2b: pull command" "$SHIP_MD" "$PULL"
assert_order "U2c: stash before pull before pop, all inside Step 2b" "$SHIP_MD" "$STEP2B" "$STASH" "$PULL" "$POP" '## Step 3 — Commit'

echo "U3: resolution and verification rules..."
assert_lit "U3a: diff3 clause" "$SHIP_MD" 'Conflict blocks may be in diff3 form'
assert_lit "U3b: unmerged-path check" "$SHIP_MD" 'git diff --name-only --diff-filter=U'
assert_lit "U3c: conflict-marker grep" "$SHIP_MD" "git grep -nE '^(<<<<<<<|\|\|\|\|\|\|\||>>>>>>>) '"
assert_lit "U3d: stash dropped only after checks" "$SHIP_MD" 'Drop the stash entry only after every check above passes'
assert_lit "U3e: no &&/set -e chaining" "$SHIP_MD" 'Never run this step, Step 3 and Step 4 as one `&&` chain or under `set -e`'

echo "U4: Step 2b user-facing messages..."
assert_lit "U4a: integrated" "$SHIP_MD" '「已整合 origin/{BRANCH}：拉入 {BEHIND} 個 commit，工作樹變更已還原。」'
assert_lit "U4b: pull conflict" "$SHIP_MD" '「拉取 origin/{BRANCH} 有衝突（本地已有未推送的 commit），已中止合併並還原工作樹；請手動整合後再重跑 /ship。」'
assert_lit "U4c: judgment conflict" "$SHIP_MD" '「stash 還原後有需要判斷的衝突：{檔案清單}；已停止，衝突與 stash 保留在工作樹，請處理後重跑 /ship。」'
assert_lit "U4d: verification failed" "$SHIP_MD" '「整合驗證未通過：{原因}；已停止，未 commit。」'

echo "U5: invariant, push hint, session end..."
assert_lit "U5a: INV-10" "$SHIP_MD" '**INV-10 — Integrate before committing; never commit over an unverified resolution.**'
assert_lit "U5b: Mode A rejection hint" "$SHIP_MD" '「Push 被拒：origin/{BRANCH} 在整合後又有新 commit；請重跑 /ship（會先在本地整合）。」'
assert_lit "U5c: session end 整合 line" "$SHIP_MD" '整合：{「拉入 N 個 commit」、「無需整合」或「新分支，略過」}'

echo "U6: loop-pauses..."
assert_lit "U6a: judgment-conflict stop row" "$LOOP_PAUSES" '| Step 2b conflict needing judgment (stash pop leaves a non-mechanical conflict) | **Input** |'

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
if [ "$FAIL" -gt 0 ]; then
  printf 'Failed: %s\n' "${FAILED_TESTS[@]}"
  exit 1
fi
exit 0
