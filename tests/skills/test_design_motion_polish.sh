#!/usr/bin/env bash
# Pinning suite for the mifb-absorption motion/typography polish (v3.1.11).
# Pins the surfaces CONTRACT.md (mifb 吸收 v2) names in its Surface Inventory:
# calm easing line, overshoot/transition:all bans, motion-quality trio,
# text-wrap balance on golden-template headings, AXES_LINE, dangling-ref fix.
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
D="$ROOT/plugins/baransu/skills/design/references"
B="$ROOT/plugins/baransu/skills/book/references"
K="$D/紙-preset/DESIGN.md"; S="$D/swiss-preset/DESIGN.md"; G="$D/google-design-preset/DESIGN.md"
fails=0
pass() { echo "PASS: $1"; }
fail() { echo "FAIL: $1" >&2; fails=$((fails+1)); }

# 1. Kami §7 calm easing line (verbatim CALM constant, no overshoot value outside §8)
grep -qF '阻尼（展開/收折）：`cubic-bezier(0.4, 0, 0.2, 1)`' "$K" \
  && pass "kami §7 calm easing line present" || fail "kami §7 calm easing line missing"
[ "$(grep -cF 'cubic-bezier(0.34, 1.56, 0.64, 1)' "$K")" = "1" ] \
  && pass "kami overshoot bezier appears only as the §8 prohibition example" \
  || fail "kami overshoot bezier count != 1 (must appear only in §8 Don't)"

# 2. transition: all ban in all three presets
for f in "$K" "$S" "$G"; do
  grep -q 'transition: all' "$f" \
    && pass "transition:all ban present in $(basename "$(dirname "$f")")" \
    || fail "transition:all ban missing in $(basename "$(dirname "$f")")"
done

# 3. Motion-quality trio in kami/swiss; google keeps progress exception + no px pairing
for f in "$K" "$S"; do
  [ "$(grep -c '可中斷、可反向\|退場比進場更短更輕\|動效永不是唯一回饋通道' "$f")" = "3" ] \
    && pass "motion trio (interruptible/exit-softer/not-sole-feedback) in $(basename "$(dirname "$f")")" \
    || fail "motion trio incomplete in $(basename "$(dirname "$f")")"
done
grep -qF '不用純粹裝飾性的循環動畫，progress 例外。' "$G" \
  && pass "google progress exception line intact" || fail "google progress exception line changed"
grep -q '旁 1.5px' "$G" \
  && fail "google carries px stroke pairing (must use Symbols weight axis)" \
  || pass "google has no px stroke pairing"

# 4. Nesting-radius advisory in kami/swiss only
for f in "$K" "$S"; do
  grep -q '外圓角＝內圓角＋padding' "$f" \
    && pass "nesting-radius advisory in $(basename "$(dirname "$f")")" \
    || fail "nesting-radius advisory missing in $(basename "$(dirname "$f")")"
done
grep -q '巢套圓角' "$G" && fail "google carries nesting-radius formula" || pass "google free of nesting-radius formula"

# 5. AXES_LINE verbatim in expression-axes.md
grep -qF 'Motion is never the only feedback channel — every animated state change pairs with a static cue (color, icon, or label).' \
  "$D/expression-axes.md" \
  && pass "AXES_LINE verbatim in expression-axes" || fail "AXES_LINE missing/drifted in expression-axes"

# 6. typography-discipline §4 text-wrap boundaries
grep -q '^## 4\. text-wrap boundaries' "$D/typography-discipline.md" \
  && pass "typography-discipline §4 present" || fail "typography-discipline §4 missing"

# 7. Golden templates: headings balance ×2, body p pretty retained
for f in "$B/golden-template.html" "$B/golden-template-gd.html" "$B/golden-template-swiss.html"; do
  [ "$(grep -c 'text-wrap: balance' "$f")" = "2" ] \
    && pass "$(basename "$f"): 2 balance headings" || fail "$(basename "$f"): balance count != 2"
  grep -qF 'p { margin-bottom: 14px; text-wrap: pretty; }' "$f" \
    && pass "$(basename "$f"): body pretty retained" || fail "$(basename "$f"): body pretty lost"
done

# 8. Dangling reference fixed; exception registered
grep -qF '/design § paper-craft' "$B/golden-template.html" \
  && fail "dangling '/design § paper-craft' reference still present" \
  || pass "dangling reference removed"
grep -q 'deliberate exception' "$B/golden-template.html" && grep -q 'inv #9' "$B/golden-template.html" \
  && pass "paper-shadow exception registered (deliberate exception / inv #9)" \
  || fail "paper-shadow exception annotation missing"

[ "$fails" = "0" ] && echo "All motion-polish pins green." || { echo "$fails pin(s) red." >&2; exit 1; }
