#!/usr/bin/env bash
# Pinning suite: assert the Verbatim Constants from the think-rework contract
# appear byte-exactly in the new SKILL.md.
#   T1 — verdict line template
#   T2 — 推翻條件行 template
#   T3 — 交棒單 four field headings
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

python3 - "$ROOT" <<'PY'
import sys
from pathlib import Path

root = Path(sys.argv[1])
skill = (root / "plugins" / "baransu" / "skills" / "think" / "SKILL.md").read_text(encoding="utf-8")
failures = []

# T1: verdict line template — must appear exactly once
verdict = "「判決：{Kill|Keep|Pivot}——{一句話結論}」"
if skill.count(verdict) != 1:
    failures.append(f"T1: verdict line template count = {skill.count(verdict)}, expected 1")

# T2: 推翻條件行 template — must appear exactly once
falsifier = "「推翻條件：{什麼證據出現，本判決即翻}」"
if skill.count(falsifier) != 1:
    failures.append(f"T2: falsifier line template count = {skill.count(falsifier)}, expected 1")

# T3: 交棒單 four field headings — each must appear exactly once
handoff_fields = (
    "## 目的（一句話）",
    "## 約束",
    "## 成功判準",
    "## 未決（Unknowns）",
)
for field in handoff_fields:
    count = skill.count(field)
    if count != 1:
        failures.append(f"T3: handoff field {field!r} count = {count}, expected 1")

# T4: Automation line value
if "ultracode=neutral, loop=not-drivable" not in skill:
    failures.append("T4: Automation line 'ultracode=neutral, loop=not-drivable' not found")

# T5: 「查無官方解」 explicit no-official-solution line — must appear exactly once
no_official = "「查無官方解」"
if skill.count(no_official) != 1:
    failures.append(f"T5: no-official-solution line count = {skill.count(no_official)}, expected 1")

if failures:
    print("RED: think-rework verbatim constants pinning failed")
    for f in failures:
        print(f"  - {f}")
    raise SystemExit(1)

print("GREEN: T1 verdict / T2 falsifier / T3 handoff / T4 automation / T5 no-official — all byte-exact")
PY
