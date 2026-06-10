#!/usr/bin/env bash
# TASK-contract-01 gate (REQ-003 Scenario 1): the eight verifiable skills
# (analyze/execute/ship/read/learn/hunt/design/codex-skill-transfer) each
# carry an Outcome Contract block — placed after frontmatter and before the
# first pre-existing H2 — with four ordered, non-empty lines:
#   - **Outcome**:  - **Done when**:  - **Evidence**:  - **Output**:
# Exit 0 = pass, 1 = contract missing/malformed.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

python3 - "$ROOT" <<'PY'
import re
import sys

root = sys.argv[1]
skills = [
    "analyze", "execute", "ship", "read",
    "learn", "hunt", "design", "codex-skill-transfer",
]
fields = ["Outcome", "Done when", "Evidence", "Output"]
failures = []

for skill in skills:
    path = f"{root}/plugins/baransu/skills/{skill}/SKILL.md"
    try:
        lines = open(path, encoding="utf-8").read().splitlines()
    except OSError as exc:
        failures.append(f"{skill}: cannot read SKILL.md ({exc})")
        continue

    # Frontmatter must open the file and be terminated (both styles in repo).
    if not lines or lines[0].strip() != "---":
        failures.append(f"{skill}: file does not start with frontmatter")
        continue
    fm_end = next(
        (i for i in range(1, len(lines)) if lines[i].strip() == "---"), None
    )
    if fm_end is None:
        failures.append(f"{skill}: unterminated frontmatter")
        continue

    # Contract must be the FIRST H2 after frontmatter (i.e. before any
    # pre-existing H2 of the skill body).
    h2s = [i for i in range(fm_end + 1, len(lines)) if lines[i].startswith("## ")]
    if not h2s:
        failures.append(f"{skill}: no H2 heading found after frontmatter")
        continue
    first = h2s[0]
    if lines[first].strip() != "## Outcome Contract":
        failures.append(
            f"{skill}: first H2 is {lines[first].strip()!r}, "
            "expected '## Outcome Contract'"
        )
        continue

    block_end = h2s[1] if len(h2s) > 1 else len(lines)
    block = lines[first + 1 : block_end]

    positions = []
    ok = True
    for field in fields:
        pat = re.compile(rf"^- \*\*{re.escape(field)}\*\*:\s*(\S.*)$")
        hit = next(
            ((i, m) for i, l in enumerate(block) if (m := pat.match(l))), None
        )
        if hit is None:
            failures.append(
                f"{skill}: missing or empty contract line '- **{field}**:'"
            )
            ok = False
            continue
        positions.append(hit[0])
    if ok and positions != sorted(positions):
        failures.append(
            f"{skill}: contract lines out of order "
            "(expected Outcome / Done when / Evidence / Output)"
        )

if failures:
    print("RED: Outcome Contract gate failed")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)

print("GREEN: all 8 verifiable skills carry a well-formed Outcome Contract")
PY
