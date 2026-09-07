#!/usr/bin/env bash
# Behavior-contract gate: hunt / think / review must explain their user-facing
# result in plain Traditional Chinese without changing their stable schemas
# (hunt: causal chain + fixed formats; think: chain + five plan sections; review: report shape).
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

python3 - "$ROOT" <<'PY'
import sys
from pathlib import Path

root = Path(sys.argv[1])
skills = {
    name: (root / "plugins" / "baransu" / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
    for name in ("hunt", "think", "review")
}
failures = []

common = (
    "Plain-language presentation contract",
    "immediate context",
    "practical impact",
    "concrete next step",
    "English technical term",
    "first use",
    "Do not add facts",
    "presentation-only",
    "adds no PAUSE",
)
for name, text in skills.items():
    for anchor in common:
        if anchor not in text:
            failures.append(f"{name}: missing presentation anchor {anchor!r}")

hunt = skills["hunt"]
for anchor in (
    "Do not stay silent while investigating",
    "after Locate, after each hypothesis is confirmed or discarded, and before a fix or Handoff",
    "what the user was doing → triggering event or condition → concrete root cause",
    "propagation path → visible symptom → practical impact → concrete next step",
    "Before either fixed format below",
):
    if anchor not in hunt:
        failures.append(f"hunt: missing causal/progress anchor {anchor!r}")

template = (root / "plugins" / "baransu" / "skills" / "hunt" / "references" / "hunt-case-template.md").read_text(encoding="utf-8")
for anchor in (
    "哪個 event / condition 觸發 → 具體根因",
    "如何一路傳成使用者看到的症狀 → 造成什麼影響",
    "接下來如何驗證或觀察",
    "下一個調查方向，以及需要的工具或權限",
):
    if anchor not in template:
        failures.append(f"hunt template: missing anchor {anchor!r}")

def assert_order(name, text, anchors):
    positions = [text.find(anchor) for anchor in anchors]
    missing = [a for a, p in zip(anchors, positions) if p < 0]
    if missing:
        failures.append(f"{name}: missing stable schema anchors {missing!r}")
    elif positions != sorted(positions):
        failures.append(f"{name}: stable schema order changed")

assert_order("hunt success", hunt, ("根因：", "修復：", "確認方式：", "測試矩陣：", "迴歸守護："))
assert_order("hunt handoff", hunt, ("症狀：[", "已測試的假說：", "已蒐集的證據：", "已排除的根因：", "尚不知道的事：", "建議下一步："))

think = skills["think"]
assert_order("think chain", think, (
    "## Align on a restatement, not on a solution",
    "## Take a stance",
    "## Verify the premises the stance leans on",
    "## Attack your own proposal, in both directions",
    "## Present it so a person can follow",
    "## Leave a plan on disk, then stop",
))
assert_order("think plan", think, ("- Building —", "- Not building —", "- Approach —", "- Key decisions —", "- Unknowns —"))
if "「計畫已落檔：.claude/think/{slug}.md。最關鍵的未決點：{一句話，或「無」}。」" not in think:
    failures.append("think: plan-landed closing line changed")

review = skills["review"]
for anchor in ("examined scope, findings, evidence, independence, and remaining limits", "「乾淨的 review"):
    if anchor not in review:
        failures.append(f"review: missing report-shape anchor {anchor!r}")
if "「review 完成：{N} 項有後果的發現（{M} 項值得處理）、{U} 項未驗證；獨立性：{獨立／同 context 自檢}。」" not in review:
    failures.append("review: closing line changed")

if failures:
    print("RED: plain-language presentation contract failed")
    for failure in failures:
        print(f"  - {failure}")
    raise SystemExit(1)

print("GREEN: hunt / think / review carry plain-language presentation contracts without schema drift")
PY
