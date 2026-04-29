#!/usr/bin/env python3
"""PostToolUse hook for the baransu telemetry harness (TASK-hooks-02).

Reads a JSON payload from stdin, computes ``commit_hash`` (via
``git rev-parse HEAD``) and ``diff_summary_redacted`` (via ``git diff
--numstat HEAD``, with sensitive paths dropped), then merges those plus a
``skill_outcome`` object into the row created by ``user-prompt-submit.py``.

Authoritative contract: ``plugins/baransu/skills/_shared/telemetry-schema.md``.
This writer owns four fields:
    skill_outcome / commit_hash / diff_summary_redacted /
    terminal_state ("in_progress" -> "completed", CAS-guarded)

Monotonic CAS rule (locked in the schema): we read the row's current
``terminal_state`` first; only ``in_progress`` is liftable to
``completed``. ``aborted`` / ``interrupted`` (set by Stop hook /
harness-reaper) are final — we merge the three non-state fields but
leave ``terminal_state`` untouched. ``completed`` is treated as an
idempotent re-fire and the row is left byte-identical (the schema calls
the three final values "immutable").

Concurrency: holds an exclusive ``flock`` on
``.claude/harness/.telemetry.lock`` for the entire read-modify-write
cycle, then atomically renames a temp file over ``telemetry.jsonl``.

Failure mode: every step is wrapped in a broad except so a hook crash
never blocks the user's main flow (Hard Constraint: hook stderr only;
exit 0 always).

Test seams (env vars, used only by ``tests/hooks/test-post-tool-use.sh``):
    POST_TOOL_USE_TEST_DIFF   — JSON array of {path, plus, minus} that
                                bypasses the real ``git diff`` call.
    POST_TOOL_USE_TEST_COMMIT — JSON-encoded string (``"<sha>"``) or
                                ``null`` that bypasses ``git rev-parse``.
"""

from __future__ import annotations

import fcntl
import fnmatch
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Path-redaction patterns (REQ-004 / TASK-hooks-02). Sensitive paths are
# MASKED — emitted as ``{"path": "<REDACTED:sensitive>", "plus": <n>,
# "minus": <n>}`` so the +N/-N audit signal survives while the path itself
# is hidden. A path matches when its basename OR full path matches any glob.
#
# Glob set covers common secret-file families:
#   .env*, *.env.*           — dotenv variants (.env, myapp.env.bak.txt)
#   *secret*, *credential*,  — generic secret/credential filenames
#   *creds*
#   *.pem, *.key,            — PEM / key files
#   *.crt, *.cer             — TLS certs
#   id_*, *_rsa*,            — SSH key variants (id_rsa, id_ed25519, id_ecdsa)
#   *_ed25519*, *_ecdsa*
#   kubeconfig*              — kubeconfig and bak variants
#   .aws/*, .ssh/*           — directory-rooted secret stores
# ---------------------------------------------------------------------------

REDACTED_PATH_PLACEHOLDER: str = "<REDACTED:sensitive>"

REDACT_PATH_GLOBS: tuple[str, ...] = (
    ".env*",
    "*.env.*",
    "*secret*",
    "*credential*",
    "*creds*",
    "*.pem",
    "*.key",
    "id_*",
    "*_rsa*",
    "*_ed25519*",
    "*_ecdsa*",
    "kubeconfig*",
    ".aws/*",
    ".ssh/*",
    "*.crt",
    "*.cer",
)


def _is_sensitive_path(path: str) -> bool:
    """Return True if ``path`` matches any redaction glob.

    Match against both basename and full path: ``.env*`` is anchored at
    the start of a name, so without basename matching ``config/.env`` and
    similar nested paths would slip through. Substring-style globs like
    ``*secret*`` are happy with either side.
    """
    base = os.path.basename(path)
    for pat in REDACT_PATH_GLOBS:
        if fnmatch.fnmatch(base, pat) or fnmatch.fnmatch(path, pat):
            return True
    return False


# ---------------------------------------------------------------------------
# Payload parsing — defensive, mirrors user-prompt-submit.py.
# ---------------------------------------------------------------------------


def _extract_session_id(payload: dict) -> str:
    candidates = [
        payload.get("session_id"),
        payload.get("sessionId"),
        (payload.get("session") or {}).get("id"),
    ]
    for c in candidates:
        if isinstance(c, str) and c:
            return c
    return ""


def _extract_skill_outcome(payload: dict) -> Optional[dict]:
    """Pull a skill_outcome object from the payload, if present.

    Claude Code's PostToolUse hook contract is sparse on what gets passed
    here. We accept either a top-level ``skill_outcome`` object or build
    one from common alternates (``tool_name`` / ``exit_code``). When
    nothing matches, return ``None`` — downstream consumers handle that
    via the schema's nullable contract.
    """
    direct = payload.get("skill_outcome")
    if isinstance(direct, dict):
        return direct
    skill_name = payload.get("skill_name") or payload.get("tool_name")
    final_state = payload.get("final_state")
    exit_code = payload.get("exit_code")
    if any(v is not None for v in (skill_name, final_state, exit_code)):
        return {
            "skill_name": skill_name,
            "final_state": final_state,
            "exit_code": exit_code,
        }
    return None


# ---------------------------------------------------------------------------
# Git helpers — both can be overridden by env vars in tests.
# ---------------------------------------------------------------------------


def _compute_commit_hash(cwd: Path) -> Optional[str]:
    """Return ``git rev-parse HEAD`` or ``None`` on any failure.

    We deliberately avoid ``check=True`` and let any failure (no .git,
    no commits yet, git not installed) collapse to ``None`` so the hook
    never aborts.
    """
    override = os.environ.get("POST_TOOL_USE_TEST_COMMIT")
    if override is not None:
        try:
            parsed = json.loads(override)
            return parsed if isinstance(parsed, str) else None
        except json.JSONDecodeError:
            return None

    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if result.returncode != 0:
            return None
        sha = result.stdout.strip()
        return sha or None
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return None


def _compute_diff_summary(cwd: Path) -> list[dict]:
    """Compute ``[{path, plus, minus}, ...]`` for the working tree vs HEAD.

    Caveat (documented for future readers): ``git diff --numstat HEAD``
    measures working-tree-vs-HEAD, not session-relative delta. If the
    skill committed during its run, this will be empty. That's acceptable
    for the harness — ``commit_hash`` already records HEAD at session end,
    and the diff is a best-effort signal for ``/grade``.
    """
    override = os.environ.get("POST_TOOL_USE_TEST_DIFF")
    if override is not None:
        try:
            parsed = json.loads(override)
            return parsed if isinstance(parsed, list) else []
        except json.JSONDecodeError:
            return []

    try:
        result = subprocess.run(
            ["git", "diff", "--numstat", "HEAD"],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if result.returncode != 0:
            return []
        return _parse_numstat(result.stdout)
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return []


def _parse_numstat(text: str) -> list[dict]:
    """Parse ``git diff --numstat`` output.

    Each line is ``<plus>\\t<minus>\\t<path>``. Binary files report ``-``
    in the count columns; we coerce those to 0 since the schema requires
    integers.
    """
    rows: list[dict] = []
    for line in text.splitlines():
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        plus_s, minus_s, path = parts[0], parts[1], "\t".join(parts[2:])
        plus = 0 if plus_s == "-" else int(plus_s) if plus_s.isdigit() else 0
        minus = 0 if minus_s == "-" else int(minus_s) if minus_s.isdigit() else 0
        rows.append({"path": path, "plus": plus, "minus": minus})
    return rows


def _redact_diff(rows: list[dict]) -> list[dict]:
    """Mask entries whose path matches a redaction glob.

    Returns a new list of ``{path, plus, minus}`` dicts. Sensitive paths
    are emitted with ``path`` replaced by ``<REDACTED:sensitive>`` while
    the +N/-N counts stay intact — that preserves the audit signal
    ("a sensitive file was touched, here's how big the change was")
    without leaking the filename itself. Non-string ``path`` values are
    still dropped (they cannot be safely emitted).
    """
    safe: list[dict] = []
    for r in rows:
        path = r.get("path") if isinstance(r, dict) else None
        if not isinstance(path, str):
            continue
        out_path = (
            REDACTED_PATH_PLACEHOLDER if _is_sensitive_path(path) else path
        )
        # Re-shape to lock down to the 3 allowed keys (no diff literal).
        safe.append(
            {
                "path": out_path,
                "plus": int(r.get("plus", 0) or 0),
                "minus": int(r.get("minus", 0) or 0),
            }
        )
    return safe


# ---------------------------------------------------------------------------
# Telemetry merge.
# ---------------------------------------------------------------------------


def _harness_dir() -> Path:
    project_root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    return Path(project_root) / ".claude" / "harness"


def _build_new_row(
    session_id: str,
    skill_outcome: Optional[dict],
    commit_hash: Optional[str],
    diff_redacted: list[dict],
) -> dict:
    """Compose a fresh 7-field row when no UserPromptSubmit row matched."""
    return {
        "session_id": session_id,
        "terminal_state": "completed",
        "prompt_text": "",
        "skill_outcome": skill_outcome,
        "commit_hash": commit_hash,
        "diff_summary_redacted": diff_redacted,
        "attempt_history": [],
    }


def _merge_into_row(
    row: dict,
    skill_outcome: Optional[dict],
    commit_hash: Optional[str],
    diff_redacted: list[dict],
) -> dict:
    """CAS-guarded merge of the three new fields + optional state lift.

    Rules (strict CAS — matches the schema's "only when current ==
    in_progress" rule literally):
      - row.terminal_state == "in_progress" -> lift to "completed",
        merge all three fields.
      - row.terminal_state in ("aborted", "interrupted") -> merge
        non-state fields only; state stays (Q-F1 ordering B).
      - row.terminal_state == "completed" -> idempotent re-fire; return
        the row unchanged so the file is byte-identical.
      - any other / missing value -> treated as undefined territory:
        merge non-state fields but DO NOT lift state. Keeps the
        monotonic-CAS invariant honest in the face of malformed rows.
    """
    state = row.get("terminal_state")
    if state == "completed":
        return row  # idempotent

    merged = dict(row)  # immutable: don't mutate caller's row
    merged["skill_outcome"] = skill_outcome
    merged["commit_hash"] = commit_hash
    merged["diff_summary_redacted"] = diff_redacted

    if state == "in_progress":
        merged["terminal_state"] = "completed"
    # else: state stays as-is (CAS guard); covers aborted, interrupted,
    # and any malformed value.
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
    """Serialise ``rows`` and atomically replace ``telemetry.jsonl``.

    Uses ``sort_keys=True`` to match user-prompt-submit.py's output style;
    that way an idempotent re-fire of a row produced by either writer is
    byte-identical.
    """
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


def _merge_telemetry(
    harness: Path,
    session_id: str,
    skill_outcome: Optional[dict],
    commit_hash: Optional[str],
    diff_redacted: list[dict],
) -> None:
    """Locate row by session_id, merge with CAS guard, write atomically."""
    harness.mkdir(parents=True, exist_ok=True)
    telemetry = harness / "telemetry.jsonl"
    lock_path = harness / ".telemetry.lock"

    lock_fd = os.open(str(lock_path), os.O_CREAT | os.O_RDWR, 0o644)
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX)

        rows = _read_jsonl(telemetry)
        idx = _locate_row_index(rows, session_id)
        if idx < 0:
            # No matching row — append a fresh completed row.
            new_row = _build_new_row(
                session_id, skill_outcome, commit_hash, diff_redacted
            )
            rows.append(new_row)
        else:
            existing = rows[idx]
            if existing.get("terminal_state") == "completed":
                # Idempotent re-fire — preserve byte-identical file.
                return
            rows[idx] = _merge_into_row(
                existing, skill_outcome, commit_hash, diff_redacted
            )

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
            # Without a session_id we cannot align with the UserPromptSubmit
            # row. Skip silently — main flow must not be blocked.
            return 0

        cwd = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
        commit_hash = _compute_commit_hash(cwd)
        raw_diff = _compute_diff_summary(cwd)
        diff_redacted = _redact_diff(raw_diff)
        skill_outcome = _extract_skill_outcome(payload)

        _merge_telemetry(
            _harness_dir(),
            session_id,
            skill_outcome,
            commit_hash,
            diff_redacted,
        )
    except Exception as exc:  # noqa: BLE001 — hook must never block.
        print(f"[post-tool-use] error: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
