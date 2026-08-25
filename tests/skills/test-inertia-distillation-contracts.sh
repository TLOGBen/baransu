#!/usr/bin/env bash
# Contract gate: think verdict schemas, review receipt + judgment + mutation fixtures.
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

# --- think: verdict and handoff schemas ---

verdict_line = "「判決：{Kill|Keep|Pivot}——{一句話結論}」"
falsifier_line = "「推翻條件：{什麼證據出現，本判決即翻}」"
handoff_fields = ("## 目的（一句話）", "## 約束", "## 成功判準", "## 未決（Unknowns）")

if think.count(verdict_line) != 1:
    failures.append(f"think verdict: template count = {think.count(verdict_line)}, expected 1")
if think.count(falsifier_line) != 1:
    failures.append(f"think falsifier: template count = {think.count(falsifier_line)}, expected 1")
ordered(think, handoff_fields, "think handoff")
for field in handoff_fields:
    if think.count(field) != 1:
        failures.append(f"think handoff: {field!r} count = {think.count(field)}, expected 1")

route_table = ("存廢判決", "選型判決", "對焦交棒")
ordered(think, route_table, "think route table")

require(think, (
    "ultracode=neutral, loop=not-drivable",
    "references/loop-pauses.md",
    "selection-telemetry.md",
    ".claude/think/",
    "SendUserFile",
), "think outcome contract")

# --- review: receipt ---

receipt = ("files:", "scope:", "depth:", "perspectives:", "hard_stops:", "new_tests:", "doc_debt:", "e2e_status:")
ordered(review, receipt, "review receipt")
receipt_block = review.split("**Sign-off receipt**", 1)[1].split("```", 2)[1]
fields = [line.split(":", 1)[0].strip() for line in receipt_block.splitlines() if ":" in line]
if fields != [field[:-1] for field in receipt]:
    failures.append(f"review receipt: expected exactly eight fields, got {fields!r}")

# --- review: judgment + controls ---

require(review, ("prediction that would falsify its core claim", "different evidence source or mechanism", "same citation is not independent", "no executable falsifier", "which surviving findings are worth including and which are not", "when either set is empty"), "review judgment")
require(review, ("reviewers do not review each other", "INV-adversarial-once", "PAUSE classification"), "review controls")

# --- line budgets ---

source_lines, generated_lines = len(think.splitlines()), len(generated.splitlines())
transfer_overhead, distributed_max, source_max = 22, 500, 250
if source_lines > source_max:
    failures.append(f"think source budget exceeds {source_max} lines (got {source_lines})")
if generated_lines > distributed_max:
    failures.append(f"think distributed line budget exceeds {distributed_max} (got {generated_lines})")

# --- mutation fixtures ---

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

same_citation_review = review.replace(
    "then check that prediction through a different evidence source or mechanism; rereading or restating the same citation is not independent.",
    "then reread or restate the same citation and treat it as independent confirmation.",
    1,
)
if valid_review_contract(same_citation_review):
    failures.append("mutation: same-citation fake disproof was accepted in shipped review")
missing_disposition_review = review.replace(
    "In the final prose, explicitly say which surviving findings are worth including and which are not, with a one-line reason for each against the review goal; explicitly say when either set is empty. Do not hand every tier back to the user for this decision.",
    "In the final prose, list surviving findings by tier and let the user decide which to include.",
    1,
)
if valid_review_contract(missing_disposition_review):
    failures.append("mutation: omitted worth/not-worth disposition was accepted in shipped review")

# think mutation: verdict line removed
think_no_verdict = think.replace(verdict_line, "", 1)
if verdict_line in think_no_verdict:
    failures.append("mutation: think verdict line survived removal (duplicate?)")
if think_no_verdict.count(falsifier_line) != 1:
    failures.append("mutation: removing verdict line also removed falsifier")

# think mutation: falsifier replaced with vague text
think_vague_falsifier = think.replace(falsifier_line, "若情況改變則重新評估", 1)
if falsifier_line in think_vague_falsifier:
    failures.append("mutation: think falsifier survived replacement (duplicate?)")

if failures:
    print("RED: inertia/distillation judgment contract failed")
    print("\n".join(f"  - {failure}" for failure in failures))
    raise SystemExit(1)
print("GREEN: verdict/handoff/8 schemas, judgment controls, budgets, and mutation fixtures hold")
PY
