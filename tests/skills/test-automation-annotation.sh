#!/usr/bin/env bash
# TASK-automation-03 gate (REQ-004): all 14 surviving skills carry a fifth
# contract line inside the Outcome Contract block, after the Output bullet:
#   - **Automation**: ultracode={overlap|assist|neutral}, loop={drivable|assisted|not-drivable}（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）
# The trailing conditional imperative wires invocation-time semantics to the
# shared loop-contract reference (locative pointer since v2.2.1; upgraded to a
# read-trigger in v2.2.2 — aux files are not auto-loaded at skill invocation).
# Grading must match the plan table; the annotation lives in the body contract
# block only (no non-standard frontmatter field). hunt/analyze additionally
# carry a Workflow parallel-dispatch hint + loop-mode default sentence.
# Exit 0 = pass, 1 = annotation missing/malformed/misgraded.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

python3 - "$ROOT" <<'PY'
import re
import sys

root = sys.argv[1]
expected = {
    "review": ("overlap", "drivable"),
    "execute": ("overlap", "drivable"),
    "learn": ("overlap", "drivable"),
    "hunt": ("assist", "assisted"),
    "health": ("assist", "assisted"),
    "analyze": ("assist", "assisted"),
    "codex-skill-transfer": ("assist", "assisted"),
    "evolve": ("assist", "assisted"),
    "think": ("neutral", "not-drivable"),
    "ship": ("neutral", "assisted"),
    "write": ("neutral", "drivable"),
    "read": ("neutral", "drivable"),
    "book": ("neutral", "drivable"),
    "design": ("neutral", "drivable"),
}
auto_pat = re.compile(
    r"^- \*\*Automation\*\*: ultracode=(overlap|assist|neutral), "
    r"loop=(drivable|assisted|not-drivable)"
    r"（when driven non-interactively — /loop, cron, Workflow — read "
    r"`\.\./_shared/loop-contract\.md` first and apply its PAUSE semantics）$"
)
output_pat = re.compile(r"^- \*\*Output\*\*:\s*\S")
failures = []

for skill, (exp_ultra, exp_loop) in expected.items():
    path = f"{root}/plugins/baransu/skills/{skill}/SKILL.md"
    try:
        lines = open(path, encoding="utf-8").read().splitlines()
    except OSError as exc:
        failures.append(f"{skill}: cannot read SKILL.md ({exc})")
        continue

    # Frontmatter must open the file and be terminated; it must not carry
    # any automation annotation (no non-standard frontmatter fields).
    if not lines or lines[0].strip() != "---":
        failures.append(f"{skill}: file does not start with frontmatter")
        continue
    fm_end = next(
        (i for i in range(1, len(lines)) if lines[i].strip() == "---"), None
    )
    if fm_end is None:
        failures.append(f"{skill}: unterminated frontmatter")
        continue
    fm = "\n".join(lines[1:fm_end])
    if re.search(r"^\s*(automation|ultracode|loop)\s*:", fm, re.M | re.I):
        failures.append(
            f"{skill}: automation annotation leaked into frontmatter "
            "(non-standard field)"
        )

    # Locate the Outcome Contract block (first H2 after frontmatter).
    h2s = [i for i in range(fm_end + 1, len(lines)) if lines[i].startswith("## ")]
    if not h2s or lines[h2s[0]].strip() != "## Outcome Contract":
        failures.append(f"{skill}: Outcome Contract block not found as first H2")
        continue
    first = h2s[0]
    block_end = h2s[1] if len(h2s) > 1 else len(lines)
    block = lines[first + 1 : block_end]

    out_idx = next((i for i, l in enumerate(block) if output_pat.match(l)), None)
    if out_idx is None:
        failures.append(f"{skill}: contract block missing Output bullet")
        continue

    auto_hits = [(i, m) for i, l in enumerate(block) if (m := auto_pat.match(l))]
    if len(auto_hits) != 1:
        failures.append(
            f"{skill}: expected exactly one well-formed Automation line in the "
            f"contract block, found {len(auto_hits)}"
        )
        continue
    auto_idx, m = auto_hits[0]
    if auto_idx < out_idx:
        failures.append(
            f"{skill}: Automation line must come after the Output bullet"
        )
    if (m.group(1), m.group(2)) != (exp_ultra, exp_loop):
        failures.append(
            f"{skill}: graded ultracode={m.group(1)}, loop={m.group(2)}; "
            f"expected ultracode={exp_ultra}, loop={exp_loop}"
        )

# hunt/analyze: body must carry a Workflow parallel-dispatch hint under
# ultracode plus a loop-mode default sentence (outside the contract line).
for skill in ("hunt", "analyze"):
    path = f"{root}/plugins/baransu/skills/{skill}/SKILL.md"
    try:
        body_lines = open(path, encoding="utf-8").read().splitlines()
    except OSError:
        continue  # already reported above
    non_contract = [l for l in body_lines if not auto_pat.match(l)]
    if not any("ultracode" in l and "Workflow" in l for l in non_contract):
        failures.append(
            f"{skill}: missing ultracode Workflow parallel-dispatch hint "
            "sentence in body"
        )
    if not any(
        "loop" in l.lower() and "預設" in l for l in non_contract
    ):
        failures.append(f"{skill}: missing loop-mode default sentence in body")

if failures:
    print("RED: Automation annotation gate failed")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)

print("GREEN: all 14 skills carry a correctly graded Automation contract line")
PY
