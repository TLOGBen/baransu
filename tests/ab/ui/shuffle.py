#!/usr/bin/env python3
"""shuffle.py — copy each build's screenshots into blind/brief-N/{A,B}/ in random order.

Usage: python3 tests/ab/ui/shuffle.py <run-dir> [--seed N] [--shots DIRNAME]

Reads  <run-dir>/build/brief-N/<arm>/<DIRNAME, default shots>/{light-page,phone-page}.png  (exactly two arms per brief)
Writes <run-dir>/blind/brief-N/{A,B}/{light-page,phone-page}.png
       <run-dir>/mapping.json   {"brief-N": {"A": "<arm>", "B": "<arm>"}}  — outside blind/ on purpose
Exit: 0 ok; 1 a build or screenshot is missing; 2 blind/ already exists (never overwritten).
"""

from __future__ import annotations

import json
import random
import shutil
import sys
from pathlib import Path

SHOTS = ("light-page.png", "phone-page.png")


def main(argv: list[str]) -> int:
    if not argv or argv[0].startswith("-"):
        print(__doc__)
        return 1
    run = Path(argv[0])
    seed = int(argv[argv.index("--seed") + 1]) if "--seed" in argv else None
    rng = random.Random(seed)
    shots_dir = argv[argv.index("--shots") + 1] if "--shots" in argv else "shots"
    build, blind = run / "build", run / "blind"
    if blind.exists():
        print(f"{blind} 已存在，不覆寫；要重洗請先手動移走。")
        return 2
    briefs = sorted(p for p in build.glob("brief-*") if p.is_dir())
    if not briefs:
        print(f"{build} 底下沒有 brief-*。")
        return 1
    problems, plan = [], {}
    for brief in briefs:
        arms = sorted(p.name for p in brief.iterdir() if p.is_dir())
        if len(arms) != 2:
            problems.append(f"{brief.name}：需要剛好兩個 arm，實際 {arms}")
            continue
        for arm in arms:
            for shot in SHOTS:
                if not (brief / arm / shots_dir / shot).is_file():
                    problems.append(f"{brief.name}/{arm}/{shots_dir}/{shot} 不存在")
        rng.shuffle(arms)
        plan[brief.name] = {"A": arms[0], "B": arms[1]}
    if problems:
        print("\n".join(problems))
        return 1
    for name, slots in plan.items():
        for label, arm in slots.items():
            dest = blind / name / label
            dest.mkdir(parents=True)
            for shot in SHOTS:
                shutil.copyfile(build / name / arm / shots_dir / shot, dest / shot)
    (run / "mapping.json").write_text(json.dumps(plan, indent=2), encoding="utf-8")
    print(f"已洗牌 {len(plan)} 題 → {blind}；對照表 {run / 'mapping.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
