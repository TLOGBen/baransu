#!/usr/bin/env python3
"""Cron silent-failure health check for the self-healing harness.

Inspects ``last_grade_run_at`` in ``state.json``; emits a 4–6 line 繁中
warning to stdout when the field is missing / null / older than
``--threshold-hours``. Always exits 0 (helper is observational; never
blocks ``/grade`` or ``/triage``).

The single source of truth for cron registration commands lives in
``plugins/baransu/skills/grade/CRON.md``; this helper only points to
that file (KD#3: "不重複 CronCreate / crontab 字面").

Trace: plan ``.claude/think/2026-04-29-harness-cron-health-check/plan.md``
(Building, KD#1–6).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


WARNING_TEMPLATE = (
    "⚠ harness 健康檢查：上次 grade {age}（threshold {thr}h），cron 可能未註冊或已停。\n"
    "請註冊 cron（兩條擇一）：\n"
    "  - Path A：session-scoped，7 天 re-expire（適合 dogfood）\n"
    "  - Path B：OS-level crontab / systemd，永久（適合 production）\n"
    "可貼指令見 plugins/baransu/skills/grade/CRON.md。\n"
    "（重新註冊後 24h 內此訊息會自動消失。）"
)


def _parse_iso(s: str) -> datetime:
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    return datetime.fromisoformat(s)


def _render(age: str, threshold_hours: int) -> str:
    return WARNING_TEMPLATE.format(age=age, thr=threshold_hours)


def _evaluate(state_path: Path, now: datetime, threshold_hours: int) -> Optional[str]:
    if not state_path.exists():
        return _render("從未跑過（state.json 不存在）", threshold_hours)

    try:
        data = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return _render("從未跑過（state.json 無法解析）", threshold_hours)

    last = data.get("last_grade_run_at") if isinstance(data, dict) else None
    if last is None:
        return _render("從未跑過", threshold_hours)

    try:
        last_dt = _parse_iso(str(last))
    except ValueError:
        return _render("時間戳無法解析", threshold_hours)

    if last_dt.tzinfo is None:
        last_dt = last_dt.replace(tzinfo=timezone.utc)

    delta_hours = (now - last_dt).total_seconds() / 3600.0
    if delta_hours > threshold_hours:
        return _render(f"跑完於 {int(delta_hours)} 小時前", threshold_hours)

    return None


def main(argv: Optional[list[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Cron silent-failure health check.")
    p.add_argument("--state", required=True, help="path to .claude/harness/state.json")
    p.add_argument(
        "--threshold-hours",
        type=int,
        default=36,
        help="staleness threshold in hours (default: 36)",
    )
    p.add_argument(
        "--now",
        default=None,
        help="ISO 8601 datetime for testing; default = UTC now",
    )
    args = p.parse_args(argv)

    try:
        now = _parse_iso(args.now) if args.now else datetime.now(timezone.utc)
    except ValueError:
        now = datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    warning = _evaluate(Path(args.state), now, args.threshold_hours)
    if warning:
        print(warning)
    return 0


if __name__ == "__main__":
    sys.exit(main())
