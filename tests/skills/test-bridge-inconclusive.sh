#!/usr/bin/env bash
# Structural test for /bridge SKILL.md (TASK-skills-bridge-02)
# Covers: corpus < N user-facing message, Stage 3 inconclusive message,
#         cleanup contract on inconclusive / refused-to-run paths,
#         bridge-replay.sh trap coverage (verify-only),
#         documented default N = 20.
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SKILL="$ROOT/plugins/baransu/skills/bridge/SKILL.md"
REPLAY="$ROOT/plugins/baransu/scripts/bridge-replay.sh"

PASS=0
FAIL=0
FAILURES=()

assert() {
  local name="$1"
  local cond="$2"
  if eval "$cond"; then
    PASS=$((PASS + 1))
    printf "  [PASS] %s\n" "$name"
  else
    FAIL=$((FAIL + 1))
    FAILURES+=("$name")
    printf "  [FAIL] %s\n" "$name"
  fi
}

# ---- Pre-requisite: SKILL.md and bridge-replay.sh exist ----
if [[ ! -f "$SKILL" ]]; then
  echo "[FATAL] SKILL.md missing at $SKILL"
  exit 1
fi
if [[ ! -f "$REPLAY" ]]; then
  echo "[FATAL] bridge-replay.sh missing at $REPLAY"
  exit 1
fi

# ---- Assertion 1: Stage 0 has user-facing 繁中 corpus < N refuse message,
#       specific enough that the user knows to wait for more data. ----
# Required: line(s) containing "corpus" AND at least one of
# {"不足", "未達門檻", "目前累積", "暫時無法", "tip", "建議"};
# additionally, the message must guide the user to wait/accumulate
# more telemetry — keyword set: 暫時無法 OR 建議 OR 累積 OR 等待.
stage0_corpus_msg_ok=false
# Look for a line that mentions corpus and at least one of the strong
# user-guidance phrases (暫時無法 / 建議 / 累積 / 等待 / 累積至).
if grep -nE 'corpus' "$SKILL" \
     | grep -E '不足|未達門檻|目前累積|暫時無法|tip|建議' \
     | grep -E '暫時無法|建議|累積|等待' >/dev/null; then
  stage0_corpus_msg_ok=true
fi
assert "1. Stage 0 corpus<N refuse message in 繁中 with wait/accumulate guidance" \
  "$stage0_corpus_msg_ok"

# ---- Assertion 2: Stage 3 (Δ-gate) explicitly handles inconclusive case
#       with a 繁中 message that distinguishes from pass/fail. ----
stage3_inconclusive_ok=false
if grep -nE 'inconclusive' "$SKILL" \
     | grep -E '樣本|不足|尚不足以|無法判定' >/dev/null; then
  stage3_inconclusive_ok=true
fi
assert "2. Stage 3 inconclusive 繁中 message distinct from pass/fail" \
  "$stage3_inconclusive_ok"

# Additional check (under same assertion bucket): the inconclusive
# message inside Stage 3 (the Δ-gate section) itself states it is
# NOT pass / fail. Limit search to the Stage 3 section body.
stage3_body="$(awk '
  /^## Stage 3/ {capture=1; next}
  capture && /^## / {capture=0}
  capture {print}
' "$SKILL")"
stage3_distinguish_ok=false
if printf "%s" "$stage3_body" \
     | grep -E '非 pass|非 ?pass/fail|不誤判|非 ?fail|不是 pass|不是 fail' >/dev/null; then
  stage3_distinguish_ok=true
fi
assert "2b. Stage 3 inconclusive message explicitly distinguishes from pass/fail" \
  "$stage3_distinguish_ok"

# ---- Assertion 3: SKILL asserts cleanup runs on inconclusive / refuse
#       paths (cleanup keyword near inconclusive or refuse/reject/拒跑). ----
# Strategy: take grep output of "cleanup" and look for any line where
# "cleanup" co-occurs with one of {inconclusive, refuse, reject, 拒跑}
# OR adjacent lines (window ±2) have those keywords.
cleanup_invariant_ok=false
if grep -nE 'cleanup' "$SKILL" \
     | grep -E 'inconclusive|refuse|reject|拒跑' >/dev/null; then
  cleanup_invariant_ok=true
fi
# Also accept multi-line proximity (cleanup contract subsection).
if ! $cleanup_invariant_ok; then
  if grep -B2 -A2 -E 'cleanup' "$SKILL" \
       | grep -E 'inconclusive|refuse|reject|拒跑' >/dev/null; then
    cleanup_invariant_ok=true
  fi
fi
assert "3. SKILL.md asserts cleanup runs on inconclusive/refuse paths" \
  "$cleanup_invariant_ok"

# Additional check: cleanup contract subsection cites bridge-replay.sh
# (the canonical trap owner) so the contract is anchored to the script.
cleanup_cite_ok=false
if grep -B2 -A2 -E 'bridge-replay\.sh' "$SKILL" \
     | grep -E 'trap|cleanup' >/dev/null; then
  cleanup_cite_ok=true
fi
assert "3b. Cleanup contract cites bridge-replay.sh trap location" \
  "$cleanup_cite_ok"

# ---- Assertion 4: bridge-replay.sh trap covers EXIT INT TERM (verify-only). ----
trap_ok=false
if grep -E '^[[:space:]]*trap[[:space:]]+.+EXIT.*INT.*TERM|^[[:space:]]*trap[[:space:]]+.+INT.*TERM.*EXIT|^[[:space:]]*trap[[:space:]]+.+EXIT.*TERM.*INT' "$REPLAY" >/dev/null; then
  trap_ok=true
fi
assert "4. bridge-replay.sh trap covers EXIT INT TERM" "$trap_ok"

# ---- Assertion 5: SKILL.md documents default N = 20. ----
n20_ok=false
if grep -Eq 'N[[:space:]]*=[[:space:]]*20|corpus.{0,40}20|default.{0,10}20|預設.{0,5}20|預設 N|Default N is 20' "$SKILL"; then
  n20_ok=true
fi
assert "5. Default N=20 documented in SKILL.md" "$n20_ok"

# ---- Summary ----
TOTAL=$((PASS + FAIL))
echo ""
echo "Result: $PASS / $TOTAL passed"
if [[ $FAIL -gt 0 ]]; then
  echo "Failed assertions:"
  for f in "${FAILURES[@]}"; do
    echo "  - $f"
  done
  exit 1
fi
exit 0
