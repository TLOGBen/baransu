#!/usr/bin/env bash
# test-cron-runbook.sh — assert structural properties of plugins/baransu/skills/grade/CRON.md
# (TASK-integration-02 — cron schedule registration runbook)

set -u

# Locate repo root from this script's location (tests/integration/ -> repo root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CRON_MD="$REPO_ROOT/plugins/baransu/skills/grade/CRON.md"

PASS=0
FAIL=0
FAILED_ASSERTIONS=()

assert() {
  local label="$1"
  local result="$2"
  if [ "$result" = "0" ]; then
    PASS=$((PASS + 1))
    echo "  PASS: $label"
  else
    FAIL=$((FAIL + 1))
    FAILED_ASSERTIONS+=("$label")
    echo "  FAIL: $label"
  fi
}

echo "Test target: $CRON_MD"
echo

# Assertion 1: file exists
if [ -f "$CRON_MD" ]; then
  assert "1. CRON.md exists" 0
else
  assert "1. CRON.md exists" 1
  echo
  echo "Summary: $PASS passed, $FAIL failed (file missing — skipping remaining checks)"
  exit 1
fi

# Assertion 2: contains both registration approaches —
#   CronCreate AND (crontab OR systemd)
if grep -q "CronCreate" "$CRON_MD" && \
   { grep -q "crontab" "$CRON_MD" || grep -q "systemd" "$CRON_MD"; }; then
  assert "2. documents CronCreate AND (crontab OR systemd)" 0
else
  assert "2. documents CronCreate AND (crontab OR systemd)" 1
fi

# Assertion 3: documents time slot — 00:03 OR 0 3 * * * OR 3 0 * * *
if grep -qE "00:03|0 3 \* \* \*|3 0 \* \* \*" "$CRON_MD"; then
  assert "3. documents offset time slot (00:03 / cron expression)" 0
else
  assert "3. documents offset time slot (00:03 / cron expression)" 1
fi

# Assertion 4: documents the prompt to fire — /baransu:grade
if grep -q "/baransu:grade" "$CRON_MD"; then
  assert "4. documents /baransu:grade prompt" 0
else
  assert "4. documents /baransu:grade prompt" 1
fi

# Assertion 5: documents how to delete/unregister —
#   CronDelete AND (crontab -e OR systemctl disable)
if grep -q "CronDelete" "$CRON_MD" && \
   { grep -q "crontab -e" "$CRON_MD" || grep -q "systemctl disable" "$CRON_MD"; }; then
  assert "5. documents CronDelete AND (crontab -e OR systemctl disable)" 0
else
  assert "5. documents CronDelete AND (crontab -e OR systemctl disable)" 1
fi

# Assertion 6: documents 7-day auto-expire caveat for CronCreate
if grep -qE "7 day|7-day|7 天|expires" "$CRON_MD"; then
  assert "6. documents 7-day auto-expire caveat" 0
else
  assert "6. documents 7-day auto-expire caveat" 1
fi

# Assertion 7: distinguishes /grade from /bridge (manual-only)
#   Must mention /grade AND have manual-only/手動 only language near /bridge
if grep -q "/grade" "$CRON_MD" && \
   grep -q "/bridge" "$CRON_MD" && \
   grep -qE "manual-only|手動 only|手動-only|manual only" "$CRON_MD"; then
  assert "7. documents /grade vs /bridge distinction (manual-only)" 0
else
  assert "7. documents /grade vs /bridge distinction (manual-only)" 1
fi

echo
echo "Summary: $PASS passed, $FAIL failed (out of 7 assertions)"

if [ "$FAIL" -gt 0 ]; then
  echo "Failed assertions:"
  for a in "${FAILED_ASSERTIONS[@]}"; do
    echo "  - $a"
  done
  exit 1
fi

exit 0
