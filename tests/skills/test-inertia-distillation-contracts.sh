#!/usr/bin/env bash
# Contract gate: think restatement/stance/plan schema, review independence + judgment, mutation fixtures.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

python3 - "$ROOT" <<'PY'
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

# --- think: chain order, plan schema, exits ---
chain = (
    "## Align on a restatement, not on a solution",
    "## Take a stance",
    "## Verify the premises the stance leans on",
    "## Attack your own proposal, in both directions",
    "## Present it so a person can follow",
    "## Leave a plan on disk, then stop",
)
ordered(think, chain, "think chain")
plan_sections = ("- Building —", "- Not building —", "- Approach —", "- Key decisions —", "- Unknowns —")
ordered(think, plan_sections, "think plan schema")
for field in plan_sections:
    if think.count(field) != 1:
        failures.append(f"think plan: {field!r} count = {think.count(field)}, expected 1")
require(think, (
    "what happens if that assumption is wrong",
    'Never write a bare "this would be overturned by Z".',
    "Attack for excess:",
    "does not choose a downstream skill",
    "ultracode=neutral, loop=not-drivable",
    "references/loop-pauses.md",
    "selection-telemetry.md",
    ".claude/think/",
    "_shared/tdd.md",
), "think contract")
for forbidden in ("AskUserQuestion", "handoff prompt", "SendUserFile", ".html"):
    if forbidden in think:
        failures.append(f"think: retired mechanism still present: {forbidden!r}")

# --- review: independence + judgment ---
require(review, (
    "a clean review is a valid result",
    "「乾淨的 review",
    "agents/verifier.md",
    "Do not supply the author's defense or desired verdict.",
    "same-context self-check",
    "Test a plausible disconfirming explanation for a severe claim",
    "with a one-line reason each",
    "mocking the claimed layer does not test that layer",
    ".claude/review/",
    "loop=drivable",
    "references/loop-pauses.md",
    "fact-check.md",
    "verification-effort.md",
), "review contract")
for forbidden in ("Stage 1.6", "Sign-off receipt", "five perspectives", "HTML work journal"):
    if forbidden in review:
        failures.append(f"review: retired mechanism still present: {forbidden!r}")

# --- budgets ---
source_lines, generated_lines = len(think.splitlines()), len(generated.splitlines())
distributed_max, source_max = 500, 250
if source_lines > source_max:
    failures.append(f"think source budget exceeds {source_max} lines (got {source_lines})")
if generated_lines > distributed_max:
    failures.append(f"think distributed line budget exceeds {distributed_max} (got {generated_lines})")

# --- mutation fixtures: the gate must reject a skill with the protection removed ---
def valid_think(text):
    return "Attack for excess:" in text and "does not choose a downstream skill" in text
if valid_think(think.replace("Attack for excess:", "", 1)):
    failures.append("mutation: think without the excess attack was accepted")
if valid_think(think.replace("does not choose a downstream skill", "", 1)):
    failures.append("mutation: think that may choose a downstream skill was accepted")

def valid_review(text):
    return ("Test a plausible disconfirming explanation for a severe claim" in text
            and "with a one-line reason each" in text
            and "Do not supply the author's defense or desired verdict." in text)
if valid_review(review.replace("Test a plausible disconfirming explanation for a severe claim", "", 1)):
    failures.append("mutation: review without the disconfirming check was accepted")
if valid_review(review.replace("with a one-line reason each", "", 1)):
    failures.append("mutation: review without the worth/not-worth disposition was accepted")
if valid_review(review.replace("Do not supply the author's defense or desired verdict.", "", 1)):
    failures.append("mutation: review that feeds the author's verdict to the verifier was accepted")

if failures:
    print("FAIL: inertia distillation contracts")
    for f in failures:
        print("  -", f)
    sys.exit(1)
print("PASS: inertia distillation contracts")
PY
