#!/usr/bin/env bash
# Red/Green gate for /learn fan-out feature
set -u
LEARN=plugins/baransu/skills/learn/SKILL.md
fail=0

check() {
  local desc="$1" want="$2" cmd="$3"
  local got
  got=$(eval "$cmd")
  if [ "$got" -ge "$want" ]; then
    printf "  PASS  %-50s (got %s, want >=%s)\n" "$desc" "$got" "$want"
  else
    printf "  FAIL  %-50s (got %s, want >=%s)\n" "$desc" "$got" "$want"
    fail=1
  fi
}

echo "== /learn fan-out spec presence =="
check "fan-out term"           1 "grep -c 'fan-out' $LEARN"
check "soft-failure invariant" 1 "grep -ci 'soft-failure\\|部分失敗' $LEARN"
check "X lane sequential MCP"  1 "grep -c 'tabs_create_mcp' $LEARN"
check "per-lane timeout 60s"   1 "grep -c '60s' $LEARN"
check "per-lane timeout 45s"   1 "grep -c '45s' $LEARN"
check "lane status 3-state"    1 "grep -c '0 hits (no results)' $LEARN"
check "fan-out fallback hint"  1 "grep -ci '純文字主題\\|bare topic\\|topic input' $LEARN"
check "lane-grouped Stage 2"   1 "grep -c '## web\\|## gh\\|## academic\\|## x' $LEARN"
check "anchor cite mechanism"  1 "grep -c 'references/acquisition/.*\\.md §\\|anchor cite' $LEARN"
check "lane tuple schema"      1 "grep -c '{path, lane}\\|lane 欄位' $LEARN"

exit $fail
