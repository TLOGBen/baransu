#!/usr/bin/env bash
# Behavior-contract gate: hunt / think / review must explain their user-facing
# result in plain Traditional Chinese without changing their stable schemas.
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
if think.count("「判決：{Kill|Keep|Pivot}——{一句話結論}」") != 1:
    failures.append("think: verdict-line verbatim template changed")
if think.count("「推翻條件：{什麼證據出現，本判決即翻}」") != 1:
    failures.append("think: falsifier-line verbatim template changed")
assert_order("think handoff", think, (
    "## 目的（一句話）",
    "## 約束",
    "## 成功判準",
    "## 未決（Unknowns）",
))

review = skills["review"]
receipt = (
    "files:", "scope:", "depth:", "perspectives:",
    "hard_stops:", "new_tests:", "doc_debt:", "e2e_status:",
)
assert_order("review receipt", review, receipt)
receipt_block = review.split("**Sign-off receipt**", 1)[1].split("```", 2)[1]
actual_fields = [line.split(":", 1)[0].strip() for line in receipt_block.splitlines() if ":" in line]
if actual_fields != [field.rstrip(":") for field in receipt]:
    failures.append(f"review: receipt must remain exactly eight fields, got {actual_fields!r}")

if failures:
    print("RED: plain-language presentation contract failed")
    for failure in failures:
        print(f"  - {failure}")
    raise SystemExit(1)

print("GREEN: hunt / think / review carry plain-language presentation contracts without schema drift")
PY
