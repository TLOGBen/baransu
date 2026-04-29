#!/usr/bin/env bash
# Structural test for /bridge SKILL.md (TASK-skills-bridge-01)
# Doc-only task: verify SKILL.md exists and contains required sections / phrases.
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SKILL="$ROOT/plugins/baransu/skills/bridge/SKILL.md"

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

# ---- Assertion 1: SKILL.md exists ----
assert "1. SKILL.md exists at plugins/baransu/skills/bridge/SKILL.md" \
  "[[ -f \"$SKILL\" ]]"

if [[ ! -f "$SKILL" ]]; then
  echo ""
  echo "Result: $PASS passed, $FAIL failed (SKILL.md missing — short-circuiting)"
  exit 1
fi

# ---- Assertion 2: frontmatter description contains 3+ trigger phrases ----
# Extract frontmatter (between first two --- lines).
FRONTMATTER="$(awk '/^---$/{c++; next} c==1' "$SKILL")"
DESC_LINE="$(printf "%s\n" "$FRONTMATTER" | grep -i '^description:' || true)"

# Count how many trigger phrases appear in the frontmatter description block.
# Description may be multi-line in YAML — capture from "description:" until next top-level key.
DESC_BLOCK="$(printf "%s\n" "$FRONTMATTER" | awk '
  /^description:/ {capture=1; print; next}
  capture && /^[a-zA-Z_]+:/ {capture=0}
  capture {print}
')"

trigger_count=0
for phrase in "比較 skill" "shadow run" "regression demo" "head-to-head" "bridge" "兩版本"; do
  if printf "%s" "$DESC_BLOCK" | grep -qF "$phrase"; then
    trigger_count=$((trigger_count + 1))
  fi
done
assert "2. Frontmatter description has 3+ trigger phrases (found: $trigger_count)" \
  "[[ $trigger_count -ge 3 ]]"

# ---- Assertion 3: Stage 0..4 sections exist ----
stage_ok=true
for n in 0 1 2 3 4; do
  if ! grep -Eq "^##[[:space:]]*Stage[[:space:]]+${n}([[:space:]:.]|$)" "$SKILL"; then
    # also accept "Stage N：" pattern (full-width colon)
    if ! grep -Eq "^##.*Stage[[:space:]]+${n}[[:space:]]*[:：]" "$SKILL"; then
      stage_ok=false
      break
    fi
  fi
done
assert "3. SKILL body has Stage 0..4 sections" "$stage_ok"

# ---- Assertion 4: manual-only marker ----
assert "4. Manual-only marker (手動 only / manual only / 不接 cron)" \
  "grep -Eq '手動 only|manual only|不接 cron' \"$SKILL\""

# ---- Assertion 5: trust check / author email ----
assert "5. Trust check / author email mention" \
  "grep -Eq 'trust check|信任檢查|author email|author_email' \"$SKILL\""

# ---- Assertion 6: --allow-untrusted opt-in flag ----
assert "6. --allow-untrusted opt-in flag mentioned" \
  "grep -qF -- '--allow-untrusted' \"$SKILL\""

# ---- Assertion 7: mktemp ----
assert "7. mktemp appears" \
  "grep -qF 'mktemp' \"$SKILL\""

# ---- Assertion 8: git worktree ----
assert "8. git worktree appears" \
  "grep -qF 'git worktree' \"$SKILL\""

# ---- Assertion 9: trap (cleanup trap mention) ----
assert "9. trap (cleanup) appears" \
  "grep -qE 'trap' \"$SKILL\""

# ---- Assertion 10: main repo working tree invariant ----
assert "10. Main repo working tree never-touch invariant phrasing" \
  "grep -Eq '不 touch|永不被 touch|never touch|不會 touch' \"$SKILL\""

# ---- Assertion 11: per-run report path ----
assert "11. .claude/harness/bridge-runs/ per-run report path appears" \
  "grep -qF '.claude/harness/bridge-runs/' \"$SKILL\""

# ---- Assertion 12: bridge-replay script reference ----
assert "12. bridge-replay script reference" \
  "grep -qF 'bridge-replay' \"$SKILL\""

# ---- Assertion 13: Δ ≥ 0.15 statistical gate threshold ----
assert "13. Δ-gate threshold (Δ … 0.15 / |Δ| … 0.15)" \
  "grep -Eq '(Δ|delta).{0,12}0\\.15|0\\.15.{0,12}(Δ|delta)' \"$SKILL\""

# ---- Assertion 14: corpus check (≥ N or ≥ 50) for inconclusive handling ----
assert "14. Corpus check (≥ N or ≥ 50) for inconclusive handling" \
  "grep -Eq 'corpus.{0,40}(≥|>=).{0,4}(N|50)|(≥|>=).{0,4}(N|50).{0,40}corpus|inconclusive' \"$SKILL\""

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
