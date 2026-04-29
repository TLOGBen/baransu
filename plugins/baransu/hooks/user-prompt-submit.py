#!/usr/bin/env python3
"""UserPromptSubmit hook for the baransu telemetry harness (TASK-hooks-01).

Reads a JSON payload from stdin (the Claude Code hook contract), redacts any
secret-pattern matches in the prompt, and appends a row to
``.claude/harness/telemetry.jsonl`` under ``$CLAUDE_PROJECT_DIR`` (or the
current working directory).

Spec contract (`plugins/baransu/skills/_shared/telemetry-schema.md`):
- 7 fields per row; this writer fills `session_id`, `prompt_text`,
  `terminal_state="in_progress"`, `attempt_history=[]`, and writes ``null``
  for the three fields owned by `PostToolUse`.
- Holds an exclusive `flock` on `.claude/harness/.telemetry.lock` and writes
  via ``read full -> append in-memory -> temp file -> os.replace``.
- ALWAYS exits 0 — any error is logged to stderr but never blocks the user
  prompt (Hard Constraint: hook failure must not interrupt main flow).

Payload schema is defensively parsed: Claude Code's UserPromptSubmit hook
documentation is sparse, so we accept either the documented top-level
``prompt`` and ``session_id`` keys or a few common alternates.
"""

from __future__ import annotations

import fcntl
import json
import os
import re
import sys
import tempfile
from pathlib import Path

# ---------------------------------------------------------------------------
# Redaction patterns. Order matters: more specific patterns run first so the
# generic catch-all does not eat an already-classified match.
# ---------------------------------------------------------------------------

REDACTION_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    # GitLab personal access tokens.
    ("gitlab_token", re.compile(r"glpat-[A-Za-z0-9_\-]{20,}")),
    # GitHub tokens (classic + fine-grained + app + user-to-server + refresh).
    ("github_token", re.compile(r"gh[opusr]_[A-Za-z0-9_\-]{20,}")),
    # AWS access key id.
    ("aws_key", re.compile(r"AKIA[0-9A-Z]{16}")),
    # PEM private key block — multi-line; remove the entire block.
    (
        "private_key",
        re.compile(
            r"-----BEGIN [A-Z ]+ PRIVATE KEY-----[\s\S]*?-----END [A-Z ]+ PRIVATE KEY-----"
        ),
    ),
    # PEM fragment fallback — catches a leading BEGIN marker when the END
    # marker is missing (e.g. a truncated paste). The full multi-line
    # `private_key` pattern above runs first; this only fires on leftovers.
    ("pem_fragment", re.compile(r"-----BEGIN [A-Z ]+(?: PRIVATE KEY)?-----")),
    # JWT — three base64url segments separated by dots; the first two
    # must start with `eyJ` (the base64-encoded `{"` prefix of the
    # header/payload JSON). The third segment (signature) is plain
    # base64url. Requiring the `eyJ` anchor on the first two segments
    # rejects ordinary hex hashes and base64 blobs that lack dots.
    (
        "jwt",
        re.compile(
            r"eyJ[A-Za-z0-9_\-]+\.eyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+"
        ),
    ),
    # Slack tokens — bot/app/admin/refresh/legacy variants.
    ("slack_token", re.compile(r"xox[baprs]-[A-Za-z0-9\-]{10,}")),
    # Stripe live/test secret keys.
    ("stripe_key", re.compile(r"sk_(?:live|test)_[A-Za-z0-9]{16,}")),
    # GCP service account JSON `private_key` field. Anchored on the JSON
    # key to capture the whole `"private_key": "..."` field, including
    # the JSON-escaped `\n` PEM body. This runs after `private_key` /
    # `pem_fragment`, which may have already masked the inner BEGIN
    # marker — the surrounding JSON field still matches and is rewritten
    # to the gcp_pk_json placeholder so the type label is correct.
    (
        "gcp_pk_json",
        re.compile(r'"private_key"\s*:\s*"[^"]*"'),
    ),
    # Azure SAS token query parameter.
    ("azure_sas", re.compile(r"[?&]sig=[A-Za-z0-9%_+/=\-]{20,}")),
    # Generic secret = value / secret: value (case-insensitive). The
    # whitespace classes are intentionally line-local ([ \t]) so this catch-all
    # cannot reach across newlines and swallow already-classified tokens
    # (e.g. a PEM block on the line below a "key:" prefix).
    (
        "secret_kv",
        re.compile(
            r"(?i)\b(?:token|key|secret|password|api[_-]?key)[ \t]*[=:][ \t]*\S+"
        ),
    ),
]


def redact(text: str) -> str:
    """Apply all redaction patterns in order; return the masked text."""
    for category, pattern in REDACTION_PATTERNS:
        text = pattern.sub(f"<REDACTED:{category}>", text)
    return text


# ---------------------------------------------------------------------------
# Payload parsing — be lenient about Claude Code's hook payload shape.
# ---------------------------------------------------------------------------


def _extract_prompt(payload: dict) -> str:
    """Pull the user's prompt text from the hook payload.

    Tries the documented ``prompt`` field first; falls back to a few common
    alternates so the hook keeps working if Claude Code adjusts its schema.
    """
    candidates = [
        payload.get("prompt"),
        payload.get("user_prompt"),
        (payload.get("message") or {}).get("content"),
    ]
    for c in candidates:
        if isinstance(c, str) and c:
            return c
    return ""


def _extract_session_id(payload: dict) -> str:
    """Pull the session id; fall back to an empty-string sentinel."""
    candidates = [
        payload.get("session_id"),
        payload.get("sessionId"),
        (payload.get("session") or {}).get("id"),
    ]
    for c in candidates:
        if isinstance(c, str) and c:
            return c
    return ""


# ---------------------------------------------------------------------------
# Telemetry write path.
# ---------------------------------------------------------------------------


def _harness_dir() -> Path:
    """Return the ``.claude/harness`` directory under the project root."""
    project_root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    return Path(project_root) / ".claude" / "harness"


def _build_row(session_id: str, prompt_text: str) -> dict:
    """Compose the 7-field row for this writer.

    Fields owned by PostToolUse / Stop / harness-reaper / auto-fix are written
    as ``null`` / ``[]`` per the schema's "row created" example.
    """
    return {
        "session_id": session_id,
        "terminal_state": "in_progress",
        "prompt_text": prompt_text,
        "skill_outcome": None,
        "commit_hash": None,
        "diff_summary_redacted": None,
        "attempt_history": [],
    }


def _append_row(harness: Path, row: dict) -> None:
    """Atomically append ``row`` to telemetry.jsonl under flock.

    Follows the design.md "Telemetry mutation contract":
    read full file -> append in-memory -> temp file -> os.replace.
    Pure append could use seek+write, but the schema mandates this pattern
    for symmetry with the merge writers (PostToolUse / Stop / auto-fix).
    """
    harness.mkdir(parents=True, exist_ok=True)
    telemetry = harness / "telemetry.jsonl"
    lock_path = harness / ".telemetry.lock"

    new_line = json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n"

    # Acquire exclusive lock (created if absent). The lock fd is closed in
    # the finally block, which releases the flock automatically.
    lock_fd = os.open(str(lock_path), os.O_CREAT | os.O_RDWR, 0o644)
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
        existing = telemetry.read_bytes() if telemetry.exists() else b""
        # Defensive: ensure prior content ends with newline before appending.
        if existing and not existing.endswith(b"\n"):
            existing += b"\n"
        payload = existing + new_line.encode("utf-8")

        # Write to a temp file in the same dir, then atomic-rename.
        fd, tmp_path = tempfile.mkstemp(prefix=".telemetry.", dir=str(harness))
        try:
            with os.fdopen(fd, "wb") as fh:
                fh.write(payload)
                fh.flush()
                os.fsync(fh.fileno())
            os.replace(tmp_path, telemetry)
        except Exception:
            # Best-effort cleanup; do not mask the original error.
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise
    finally:
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
        finally:
            os.close(lock_fd)


# ---------------------------------------------------------------------------
# Entry point — wraps every step in a broad except so a hook crash never
# blocks the user's prompt from being delivered.
# ---------------------------------------------------------------------------


def main() -> int:
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
        if not isinstance(payload, dict):
            payload = {}

        session_id = _extract_session_id(payload)
        prompt_raw = _extract_prompt(payload)
        prompt_redacted = redact(prompt_raw)

        row = _build_row(session_id, prompt_redacted)
        _append_row(_harness_dir(), row)
    except Exception as exc:  # noqa: BLE001 — hook must never block.
        print(f"[user-prompt-submit] error: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
