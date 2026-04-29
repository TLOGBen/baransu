#!/usr/bin/env python3
"""Staleness reaper for the baransu telemetry harness (TASK-hooks-03).

One-shot script. Walks ``.claude/harness/telemetry.jsonl``, finds rows
whose ``terminal_state == "in_progress"`` AND whose ``created_at`` is
older than the threshold (default 24h), and CAS-flips them to
``interrupted``. CAS guard mirrors the schema's monotonic rule: only
``in_progress`` is liftable; other states are left untouched.

Designed to be called from ``/grade`` Stage 0 (per A-F3: separate from
the grade-collector itself to keep concerns disjoint), or ad-hoc from
cron / a manual sweep.

Authoritative contract:
``plugins/baransu/skills/_shared/telemetry-schema.md`` §5 (Writer 名單).

Compromise (documented for follow-up): the locked 7-field schema does
NOT currently include a ``created_at`` field. Sibling writers
(UserPromptSubmit / PostToolUse) therefore do not populate it. Until
the schema is amended via the change-management process, the reaper:
  - reads ``created_at`` opportunistically from rows that DO carry it
    (e.g. seeded by tests or future writers);
  - skips rows lacking ``created_at`` with a single stderr warning per
    row, since "stale" cannot be decided without a timestamp;
  - never mutates a row to add ``created_at`` itself (the schema's
    locked whitelist forbids us from inventing fields).

Concurrency: holds an exclusive ``flock`` on
``.claude/harness/.telemetry.lock`` for the entire read-modify-write
cycle, then atomically renames a temp file over ``telemetry.jsonl``.
"""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# CLI.
# ---------------------------------------------------------------------------


def _parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="harness-reaper",
        description="Reap stale in_progress telemetry rows -> interrupted.",
    )
    p.add_argument(
        "--telemetry",
        default=None,
        help="Path to telemetry.jsonl (default: "
        "$CLAUDE_PROJECT_DIR/.claude/harness/telemetry.jsonl).",
    )
    p.add_argument(
        "--threshold-hours",
        type=float,
        default=24.0,
        help="Reap rows whose created_at is older than N hours (default: 24).",
    )
    p.add_argument(
        "--now",
        default=None,
        help="ISO-8601 UTC timestamp to use as 'now' (test seam; default: "
        "current UTC time).",
    )
    return p.parse_args(argv)


# ---------------------------------------------------------------------------
# Time helpers.
# ---------------------------------------------------------------------------


def _parse_iso(ts: str) -> Optional[datetime]:
    """Parse an ISO-8601 string. ``Z`` suffix is normalised to ``+00:00``.

    Returns None on any parse failure so callers can skip the row.
    """
    if not isinstance(ts, str) or not ts:
        return None
    s = ts.strip()
    # datetime.fromisoformat in 3.10 doesn't grok the Z suffix; normalise.
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return None
    # Naive timestamps are treated as UTC for the staleness comparison —
    # any other interpretation would silently mis-classify rows.
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _resolve_now(now_arg: Optional[str]) -> datetime:
    if now_arg:
        parsed = _parse_iso(now_arg)
        if parsed is None:
            raise ValueError(f"--now is not a valid ISO-8601 timestamp: {now_arg!r}")
        return parsed
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Reap logic — pure-functional decision separated from I/O for testability.
# ---------------------------------------------------------------------------


def _is_stale(row: dict, now: datetime, threshold: timedelta) -> tuple[bool, str]:
    """Return (stale?, reason).

    Stale := state == in_progress AND now - created_at > threshold.
    A non-stale verdict carries a reason for stderr trace.
    """
    state = row.get("terminal_state")
    if state != "in_progress":
        return False, f"state={state} (not in_progress)"

    created_at_raw = row.get("created_at")
    if created_at_raw is None:
        return False, "created_at missing"

    created_at = _parse_iso(created_at_raw)
    if created_at is None:
        return False, f"created_at unparseable: {created_at_raw!r}"

    age = now - created_at
    if age > threshold:
        return True, f"age={age}"
    return False, f"age={age} (under threshold)"


def _flip_interrupted(row: dict) -> dict:
    """Return a new row with terminal_state='interrupted'. Caller has CAS-checked."""
    out = dict(row)
    out["terminal_state"] = "interrupted"
    return out


# ---------------------------------------------------------------------------
# Telemetry I/O — flock + atomic rename, mirroring sibling writers.
# ---------------------------------------------------------------------------


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            out.append(obj)
    return out


def _write_jsonl_atomic(path: Path, rows: list[dict]) -> None:
    payload = "".join(
        json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows
    ).encode("utf-8")

    fd, tmp_path = tempfile.mkstemp(prefix=".telemetry.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(payload)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def _resolve_telemetry_path(arg: Optional[str]) -> Path:
    if arg:
        return Path(arg)
    project_root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    return Path(project_root) / ".claude" / "harness" / "telemetry.jsonl"


def _reap(
    telemetry: Path, now: datetime, threshold: timedelta
) -> tuple[int, int]:
    """Run one sweep. Returns (changed_count, scanned_count).

    Flock-protected; atomic write only if any row changed (so an all-fresh
    sweep leaves the file's mtime untouched).
    """
    if not telemetry.exists():
        # Nothing to reap. Mirror the schema's "telemetry MAY not yet exist"
        # invariant — don't create an empty file just to please the reaper.
        return 0, 0

    lock_path = telemetry.parent / ".telemetry.lock"
    telemetry.parent.mkdir(parents=True, exist_ok=True)

    lock_fd = os.open(str(lock_path), os.O_CREAT | os.O_RDWR, 0o644)
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX)

        rows = _read_jsonl(telemetry)
        changed = 0
        for i, row in enumerate(rows):
            stale, _reason = _is_stale(row, now, threshold)
            if stale:
                rows[i] = _flip_interrupted(row)
                changed += 1
            elif (
                row.get("terminal_state") == "in_progress"
                and row.get("created_at") is None
            ):
                # Surface the gap so a caller running with stderr captured
                # can audit how often we hit the schema's missing-field path.
                sid = row.get("session_id", "<unknown>")
                print(
                    f"[harness-reaper] skip session_id={sid}: created_at missing",
                    file=sys.stderr,
                )

        if changed:
            _write_jsonl_atomic(telemetry, rows)
        return changed, len(rows)
    finally:
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
        finally:
            os.close(lock_fd)


# ---------------------------------------------------------------------------
# Entry point.
# ---------------------------------------------------------------------------


def main(argv: Optional[list[str]] = None) -> int:
    args = _parse_args(argv if argv is not None else sys.argv[1:])
    # Per ctx.md: "Exit 0 always; log errors to stderr." We do NOT exit non-zero
    # for argument-shape issues — log and degrade gracefully so /grade Stage 0
    # never gets blocked by a bad reaper invocation.
    try:
        now = _resolve_now(args.now)
    except ValueError as exc:
        print(f"[harness-reaper] {exc}", file=sys.stderr)
        return 0

    if args.threshold_hours < 0:
        print(
            "[harness-reaper] --threshold-hours must be non-negative",
            file=sys.stderr,
        )
        return 0

    threshold = timedelta(hours=args.threshold_hours)
    telemetry = _resolve_telemetry_path(args.telemetry)

    try:
        changed, scanned = _reap(telemetry, now, threshold)
    except Exception as exc:  # noqa: BLE001 — script wraps to log + exit 0.
        print(f"[harness-reaper] error: {exc}", file=sys.stderr)
        return 0

    print(
        f"[harness-reaper] scanned={scanned} reaped={changed} "
        f"telemetry={telemetry}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
