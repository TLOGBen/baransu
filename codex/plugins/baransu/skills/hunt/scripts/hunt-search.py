#!/usr/bin/env python3
"""
hunt-search.py — search hunt cases under .claude/hunt-report/ and .claude/archived/

/ship archives case files flat into .claude/archived/, so by default both
locations are searched to keep the cross-session memory loop alive.

Usage:
  python hunt-search.py                          # list all
  python hunt-search.py --status fixed           # filter by status
  python hunt-search.py --keyword "cache"        # keyword search across target / root_cause
  python hunt-search.py --id HUNT-2024-001       # exact ID lookup
  python hunt-search.py --dir /path/to/reports   # search only this directory
                                                 # (default: .claude/hunt-report/ + .claude/archived/)
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


DEFAULT_DIRS = [".claude/hunt-report", ".claude/archived"]


def load_cases(report_dirs: list[Path]) -> list[tuple[Path, dict]]:
    cases = []
    for report_dir in report_dirs:
        # "*.md-*" catches /ship's collision rename ({item_name}-{unix_timestamp}),
        # which drops the .md suffix; the hunt_id frontmatter check stays the gate.
        candidates = set(report_dir.glob("*.md")) | set(report_dir.glob("*.md-*"))
        for path in sorted(candidates):
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
    parser = argparse.ArgumentParser(description="Search the hunt-report catalog")
    parser.add_argument("--dir",     default=None, help="search only this directory (default: .claude/hunt-report/ + .claude/archived/)")
    parser.add_argument("--status",  help="filter by status (scoping|investigating|root_caused|fixed|closed)")
    parser.add_argument("--keyword", help="search keyword across target and root_cause (case-insensitive)")
    parser.add_argument("--id",      help="exact hunt_id lookup")
    args = parser.parse_args()

    report_dirs = [Path(args.dir)] if args.dir else [Path(d) for d in DEFAULT_DIRS]
    report_dirs = [d for d in report_dirs if d.exists()]
    if not report_dirs:
        print("（尚無狩獵報告）")
        sys.exit(0)

    cases = load_cases(report_dirs)

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
