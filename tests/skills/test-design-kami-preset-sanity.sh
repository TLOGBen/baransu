#!/usr/bin/env bash
# Standing regression: the shipped 紙 preset must pass its own sanity gate.
#
# Promoted from the pre-v2.9.0 field-smoke gate, which caught ship-breaking
# defects in the distributed preset before release. Defect class guarded:
# SHIPPED-PRESET DRIFT — a preset edit (tokens, design-cores, slide-cores,
# schemas) that violates the Kami invariants or the swiss-deck lock list,
# so `/baransu:design preset 紙` would deploy broken artifacts to users.
#
# Runs plugins/baransu/skills/design/references/紙-preset/紙-sanity.sh
# against the preset directory itself (the exact files that ship) and
# requires exit 0.
#
# Hermetic-or-skip: 紙-sanity.sh needs python3 (check.py engine) and node
# (validate-swiss-deck.mjs — node builtins only: no npm packages, no
# network). If either interpreter is missing in a fresh checkout, SKIP
# loudly and exit 0 — never fail spuriously, never download anything.

set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PRESET_DIR="$ROOT/plugins/baransu/skills/design/references/紙-preset"
SANITY_SH="$PRESET_DIR/紙-sanity.sh"

# --- structural preconditions (these are real failures, not skips) ---
if [ ! -f "$SANITY_SH" ]; then
  echo "FAIL: shipped-preset drift — 紙-sanity.sh missing from the distributed preset ($SANITY_SH)" >&2
  exit 1
fi
if [ ! -f "$PRESET_DIR/tokens.css" ] || [ ! -f "$PRESET_DIR/DESIGN.md" ]; then
  echo "FAIL: shipped-preset drift — 紙-preset is missing tokens.css or DESIGN.md (preset no longer deployable)" >&2
  exit 1
fi

# --- hermetic-or-skip dependency guard ---
if ! command -v python3 >/dev/null 2>&1; then
  echo "SKIP test-design-kami-preset-sanity: python3 not on PATH (紙-sanity.sh check.py engine needs it) — skipping to stay hermetic"
  exit 0
fi
if ! command -v node >/dev/null 2>&1; then
  echo "SKIP test-design-kami-preset-sanity: node not on PATH (紙-sanity.sh validate-swiss-deck stage needs it) — skipping to stay hermetic"
  exit 0
fi

# --- the gate itself ---
echo "T1: shipped 紙 preset passes 紙-sanity.sh (Kami invariants + schemas + object-position + swiss-deck lock list)..."
if OUT="$(bash "$SANITY_SH" "$PRESET_DIR" 2>&1)"; then
  echo "  PASS: T1 shipped 紙 preset is sanity-clean"
else
  echo "  FAIL: T1 shipped-preset drift — the distributed 紙 preset violates its own sanity gate" >&2
  echo "        (defect class: preset edits that ship Kami-invariant / lock-list violations to users — caught pre-v2.9.0 by the field smoke)" >&2
  printf '%s\n' "$OUT" | sed 's/^/        /' >&2
  exit 1
fi

echo ""
echo "Results: 1 passed, 0 failed"
exit 0
