#!/usr/bin/env bash
# Contract gate: minimal complete fixes, load-bearing premises, and independent review falsification.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

python3 - "$ROOT" <<'PY'
import re
import sys
from pathlib import Path

root = Path(sys.argv[1])
think = (root / "plugins/baransu/skills/think/SKILL.md").read_text(encoding="utf-8")
review = (root / "plugins/baransu/skills/review/SKILL.md").read_text(encoding="utf-8")
generated = (root / "codex/plugins/baransu/skills/think/SKILL.md").read_text(encoding="utf-8")
failures = []

def require(text, anchors, label):
    for anchor in anchors:
        if anchor not in text:
            failures.append(f"{label}: missing {anchor!r}")

def ordered(text, anchors, label):
    positions = [text.find(anchor) for anchor in anchors]
    if min(positions) < 0:
        failures.append(f"{label}: missing schema field")
    elif positions != sorted(positions):
        failures.append(f"{label}: schema order changed")

lightweight = ("推薦修法：", "涉及檔案：", "風險：", "驗證方式：")
full = ("## Building（要做什麼）", "## Not building（明確不做的事）", "## Approach（選了哪個方案及理由）", "## Key decisions（關鍵決策）", "## Unknowns（已知不知道的事）")
receipt = ("files:", "scope:", "depth:", "perspectives:", "hard_stops:", "new_tests:", "doc_debt:", "e2e_status:")
lightweight_region = think.split("Output template", 1)[1].split("Then stop.", 1)[0]
lightweight_match = re.search(r"```\n(.*?)\n```", lightweight_region, re.S)
if not lightweight_match:
    failures.append("think lightweight: missing fenced output schema")
    lightweight_block = ""
else:
    lightweight_block = lightweight_match.group(1)
    lightweight_fields = tuple(
        match.group(1)
        for line in lightweight_block.splitlines()
        if (match := re.match(r"^([\u3400-\u9fffA-Za-z]+)：", line))
    )
    if lightweight_fields != tuple(field[:-1] for field in lightweight):
        failures.append(
            f"think lightweight: expected exactly four fields, got {lightweight_fields!r}"
        )
if "請回覆「可以」或「不行，因為…」。" not in lightweight_block:
    failures.append("think lightweight: existing confirmation line changed")
full_block = think.split("Produce **exactly** this structure", 1)[1].split("Claim-cite-first", 1)[0]
actual_full = tuple(re.findall(r"^## .+$", full_block, re.M))
if actual_full != full:
    failures.append(f"think full: expected exact five-section schema, got {actual_full!r}")
ordered(review, receipt, "review receipt")
receipt_block = review.split("**Sign-off receipt**", 1)[1].split("```", 2)[1]
fields = [line.split(":", 1)[0].strip() for line in receipt_block.splitlines() if ":" in line]
if fields != [field[:-1] for field in receipt]:
    failures.append(f"review receipt: expected exactly eight fields, got {fields!r}")

if think.count("承重前提：{X}；若不成立：{實際後果 Y}；設計如何承受：{Z}。") != 1:
    failures.append("think full: load-bearing premise must appear exactly once")
if think.split("## Approach（選了哪個方案及理由）", 1)[1].split("## Key decisions（關鍵決策）", 1)[0].count("承重前提：") != 1:
    failures.append("think full: premise is not inside Approach")
require(think, ("behavior-complete candidates", "stated success, failure, and edge outcomes", "suppress/hide/bypass", "repo evidence", "next-smallest complete candidate"), "think lightweight judgment")
require(review, ("prediction that would falsify its core claim", "different evidence source or mechanism", "same citation is not independent", "no executable falsifier", "which surviving findings are worth including and which are not", "when either set is empty"), "review judgment")
require(review, ("reviewers do not review each other", "INV-adversarial-once", "PAUSE classification"), "review controls")
source_lines, generated_lines = len(think.splitlines()), len(generated.splitlines())
transfer_overhead, distributed_max = 22, 500
if source_lines > distributed_max - transfer_overhead:
    failures.append(f"think source budget exceeds {distributed_max - transfer_overhead} after transfer overhead")
if source_lines + transfer_overhead > distributed_max or generated_lines > distributed_max:
    failures.append("think distributed line budget exceeds 500")

# Mutation fixtures prove that explanatory wording without the required behavior is rejected.
def valid_lightweight_contract(text):
    return all(x in text for x in ("behavior-complete candidates", "stated success, failure, and edge outcomes", "suppress/hide/bypass", "repo evidence", "next-smallest complete candidate"))

def valid_review_contract(text):
    try:
        high = text.split("HIGH / CRITICAL findings additionally require", 1)[1].split(
            "「乾淨的 review", 1
        )[0]
        disposition = text.split("In the final prose", 1)[1].split(
            "The fourth question itself", 1
        )[0]
    except IndexError:
        return False
    return (
        "prediction that would falsify its core claim" in high
        and "different evidence source or mechanism" in high
        and "same citation is not independent" in high
        and "no executable falsifier" in high
        and "drops or downgrades" in high
        and "which surviving findings are worth including and which are not" in disposition
        and "one-line reason for each against the review goal" in disposition
        and "when either set is empty" in disposition
        and "Do not hand every tier back to the user" in disposition
    )

if not valid_review_contract(review):
    failures.append("review: operational falsification/disposition contract is incomplete")

if valid_lightweight_contract(think.replace("suppress/hide/bypass", "smaller workaround")):
    failures.append("mutation: incomplete smaller workaround was accepted")
same_citation_review = review.replace(
    "then check that prediction through a different evidence source or mechanism; rereading or restating the same citation is not independent.",
    "then reread or restate the same citation and treat it as independent confirmation.",
    1,
)
if valid_review_contract(same_citation_review):
    failures.append("mutation: same-citation fake disproof was accepted in shipped review")
behavior_removed = think.replace("behavior-complete candidates", "complete candidates", 1)
if valid_lightweight_contract(behavior_removed):
    failures.append("mutation: retained explanatory text hid removed behavior")
extra_lightweight_field = lightweight_block.replace(
    "驗證方式：", "替代方案：<must fail>\n驗證方式：", 1
)
extra_fields = tuple(
    match.group(1)
    for line in extra_lightweight_field.splitlines()
    if (match := re.match(r"^([\u3400-\u9fffA-Za-z]+)：", line))
)
if extra_fields == tuple(field[:-1] for field in lightweight):
    failures.append("mutation: extra Lightweight schema field was accepted")
missing_disposition_review = review.replace(
    "In the final prose, explicitly say which surviving findings are worth including and which are not, with a one-line reason for each against the review goal; explicitly say when either set is empty. Do not hand every tier back to the user for this decision.",
    "In the final prose, list surviving findings by tier and let the user decide which to include.",
    1,
)
if valid_review_contract(missing_disposition_review):
    failures.append("mutation: omitted worth/not-worth disposition was accepted in shipped review")

if failures:
    print("RED: inertia/distillation judgment contract failed")
    print("\n".join(f"  - {failure}" for failure in failures))
    raise SystemExit(1)
print("GREEN: 4/5/8 schemas, judgment controls, budgets, and mutation fixtures hold")
PY
