#!/usr/bin/env python3
"""
hunt-search.py — 搜尋 .claude/hunt-report/ 裡的狩獵案例

用法：
  python hunt-search.py                          # 列出全部
  python hunt-search.py --status fixed           # 按狀態篩選
  python hunt-search.py --keyword "cache"        # 在 target / root_cause 裡關鍵字搜尋
  python hunt-search.py --id HUNT-2024-001       # 精確 ID 查詢
  python hunt-search.py --dir /path/to/reports   # 指定目錄（預設 .claude/hunt-report/）
"""

import argparse
import re
import sys
from pathlib import Path


def parse_frontmatter(text: str) -> dict:
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return {}
    fm: dict = {}
    for line in match.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            key, _, val = line.partition(":")
            val = val.strip().strip('"').strip("'")
            # strip inline YAML comments (e.g. "scoping  # scoping | ...")
            val = val.split("#")[0].strip()
            fm[key.strip()] = val
    return fm


def load_cases(report_dir: Path) -> list[tuple[Path, dict]]:
    cases = []
    for path in sorted(report_dir.glob("*.md")):
        fm = parse_frontmatter(path.read_text(encoding="utf-8"))
        if fm.get("hunt_id"):
            cases.append((path, fm))
    return cases


STATUS_COLORS = {
    "scoping":      "\033[33m",
    "investigating": "\033[34m",
    "root_caused":  "\033[35m",
    "fixed":        "\033[32m",
    "closed":       "\033[90m",
}
RESET = "\033[0m"


def fmt_status(status: str) -> str:
    color = STATUS_COLORS.get(status, "")
    return f"{color}[{status}]{RESET}"


def print_catalog(cases: list[tuple[Path, dict]]) -> None:
    if not cases:
        print("（無符合的狩獵案例）")
        return
    print(f"\n🥷  Hunt Case Catalog  ({len(cases)} cases)\n")
    for _, fm in cases:
        hunt_id  = fm.get("hunt_id", "UNKNOWN").ljust(18)
        status   = fmt_status(fm.get("status", "?"))
        created  = fm.get("created", "").ljust(12)
        target   = fm.get("target", "")
        print(f"  {hunt_id}  {status:<28}  {created}  {target}")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="狩獵報告目錄搜尋")
    parser.add_argument("--dir",     default=".claude/hunt-report", help="報告目錄")
    parser.add_argument("--status",  help="篩選 status（scoping|investigating|root_caused|fixed|closed）")
    parser.add_argument("--keyword", help="在 target 和 root_cause 裡搜尋關鍵字（大小寫不敏感）")
    parser.add_argument("--id",      help="精確 hunt_id 查詢")
    args = parser.parse_args()

    report_dir = Path(args.dir)
    if not report_dir.exists():
        print("（尚無狩獵報告）")
        sys.exit(0)

    cases = load_cases(report_dir)

    if args.id:
        cases = [(p, fm) for p, fm in cases if fm.get("hunt_id") == args.id]

    if args.status:
        cases = [(p, fm) for p, fm in cases if fm.get("status") == args.status]

    if args.keyword:
        kw = args.keyword.lower()
        cases = [
            (p, fm) for p, fm in cases
            if kw in fm.get("target", "").lower()
            or kw in fm.get("root_cause", "").lower()
        ]

    print_catalog(cases)


if __name__ == "__main__":
    main()
