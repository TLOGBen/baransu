#!/usr/bin/env python3
"""Stop hook for the baransu telemetry harness (TASK-hooks-03).

Reads a JSON payload from stdin (the Claude Code Stop hook contract),
locates the row created by ``user-prompt-submit.py`` for the current
``session_id`` and, if it is still ``in_progress``, CAS-flips its
``terminal_state`` to ``aborted``. Other fields are preserved; if
``skill_outcome`` was previously ``null`` it is filled with a minimal
中斷 marker so REQ-001 Scenario 2's "skill_outcome 不留空" holds.

Authoritative contract:
``plugins/baransu/skills/_shared/telemetry-schema.md`` §5 (Writer 名單).

Monotonic CAS rule (locked in the schema): only ``in_progress`` is
liftable to ``aborted``. ``completed`` / ``aborted`` / ``interrupted``
are final; this hook leaves those rows byte-identical.

Concurrency: holds an exclusive ``flock`` on
``.claude/harness/.telemetry.lock`` for the entire read-modify-write
cycle, then atomically renames a temp file over ``telemetry.jsonl``.

Failure mode: every step is wrapped in a broad except so a hook crash
never blocks the session from ending (Hard Constraint: hook stderr
only; exit 0 always).
"""

from __future__ import annotations

import fcntl
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Payload parsing — defensive, mirrors user-prompt-submit.py / post-tool-use.py.
# ---------------------------------------------------------------------------


def _extract_session_id(payload: dict) -> str:
    """Pull session_id from the payload; empty string sentinel on miss."""
    candidates = [
        payload.get("session_id"),
        payload.get("sessionId"),
        (payload.get("session") or {}).get("id"),
    ]
    for c in candidates:
        if isinstance(c, str) and c:
            return c
    # Defensive env-var fallback — Claude Code may expose the active session id
    # via env in some configurations. If neither is present the hook is a no-op.
    env_sid = os.environ.get("CLAUDE_SESSION_ID")
    if isinstance(env_sid, str) and env_sid:
        return env_sid
    return ""


# ---------------------------------------------------------------------------
# Telemetry merge.
# ---------------------------------------------------------------------------


def _harness_dir() -> Path:
    project_root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    return Path(project_root) / ".claude" / "harness"


# Marker filled into skill_outcome when previously null. Schema mandates that
# Stop hook owns skill_outcome's "中斷標示, 不留空" (REQ-001 Scenario 2).
ABORTED_OUTCOME_MARKER = {
    "skill_name": None,
    "final_state": "aborted",
    "exit_code": None,
}


def _merge_aborted(row: dict) -> Optional[dict]:
    """CAS-guarded flip of row to aborted; returns None when no change.

    Rules (strict CAS, matching schema §2 monotonic rule):
      - state == "in_progress" -> flip to "aborted"; fill skill_outcome
        with the marker iff currently null.
      - any other value (completed / aborted / interrupted / malformed)
        -> return None to signal "no mutation; preserve byte-identical row".
    """
    if row.get("terminal_state") != "in_progress":
        return None

    merged = dict(row)  # immutable: don't mutate caller's row
    merged["terminal_state"] = "aborted"
    if merged.get("skill_outcome") is None:
        merged["skill_outcome"] = dict(ABORTED_OUTCOME_MARKER)
    return merged


def _locate_row_index(rows: list[dict], session_id: str) -> int:
    """Find the most recent row matching ``session_id``; -1 if absent."""
    for i in range(len(rows) - 1, -1, -1):
        if rows[i].get("session_id") == session_id:
            return i
    return -1


def _read_jsonl(path: Path) -> list[dict]:
    """Parse a JSONL file into a list. Bad lines are skipped (defensive)."""
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


def _write_jsonl_atomic(harness: Path, rows: list[dict]) -> None:
    """Serialise ``rows`` and atomically replace ``telemetry.jsonl``."""
    telemetry = harness / "telemetry.jsonl"
    payload = "".join(
        json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows
    ).encode("utf-8")

    fd, tmp_path = tempfile.mkstemp(prefix=".telemetry.", dir=str(harness))
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(payload)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp_path, telemetry)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def _flip_aborted(harness: Path, session_id: str) -> None:
    """Locate row by session_id, CAS-flip in_progress -> aborted, atomic write."""
    harness.mkdir(parents=True, exist_ok=True)
    telemetry = harness / "telemetry.jsonl"
    lock_path = harness / ".telemetry.lock"

    lock_fd = os.open(str(lock_path), os.O_CREAT | os.O_RDWR, 0o644)
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX)

        rows = _read_jsonl(telemetry)
        idx = _locate_row_index(rows, session_id)
        if idx < 0:
            # No matching row — nothing to flip. Stop hook does not append.
            return

        merged = _merge_aborted(rows[idx])
        if merged is None:
            # CAS guard tripped: row already in a final state. No-op so the
            # file stays byte-identical (idempotent).
            return

        rows[idx] = merged
        _write_jsonl_atomic(harness, rows)
    finally:
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
        finally:
            os.close(lock_fd)


# ---------------------------------------------------------------------------
# Entry point.
# ---------------------------------------------------------------------------


def main() -> int:
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
        if not isinstance(payload, dict):
            payload = {}

        session_id = _extract_session_id(payload)
        if not session_id:
            # Without a session_id we cannot align with the row to flip.
            # No-op silently — the staleness reaper backstops via 24h sweep.
            return 0

        _flip_aborted(_harness_dir(), session_id)
    except Exception as exc:  # noqa: BLE001 — hook must never block.
        print(f"[stop] error: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
