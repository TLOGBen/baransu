#!/usr/bin/env python3
"""grade-collector — telemetry.jsonl -> grade.jsonl.

Reads .claude/harness/telemetry.jsonl, filters terminal_state == "completed",
computes the 5 baransu-native rubric dimensions deterministically (equal
weight 1/5 each, i.e. 0.2 per dim), writes grade.jsonl, and emits a
tune_review_due signal once the cumulative completed count crosses >= 50.

Authoritative rubric source:
  plugins/baransu/skills/_shared/grade-triage-schema.md, section 1.

Output formula (equal weight bootstrap):
  weights = {dim: 1/5 for dim in 5 dims}    # 0.2 each
  aggregate = sum(dims) / 5

This implementation REWRITES grade.jsonl on each run (idempotent rebuild).
ctx.md mentions "append by default" for design, but the explicit
reproducibility requirement (byte-for-byte stable output across two runs on
the same telemetry) is only achievable via a full rewrite. The schema
authority phrase "byte-for-byte reproducibility" is the tiebreaker.

No external deps; stdlib only (json, argparse, pathlib, datetime).
No timestamps or random data leak into grade.jsonl rows. The only ISO
timestamp written by this script lands in state.json's
tune_review_due_since (and only when crossing the threshold for the first
time; subsequent runs preserve the existing value).
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Locked spec constants. Do not parametrize without going through analyze.
# ---------------------------------------------------------------------------

# 5 baransu-native rubric dimensions, fixed name + order (KD-4 / INV-4).
DIM_NAMES: tuple[str, ...] = (
    "outcome_quality",
    "iteration_velocity",
    "scope_blast",
    "human_override_rate",
    "failure_recurrence",
)

# Equal-weight bootstrap: 1/5 each (= 0.2). KD-4. Grep target for INV-4.
EQUAL_WEIGHT: float = 1 / 5  # 0.2 — equal_weight bootstrap (Week-1)
WEIGHTS: dict[str, float] = {dim: EQUAL_WEIGHT for dim in DIM_NAMES}

# Tune trigger threshold: cumulative completed rows >= 50.
TUNE_TRIGGER_THRESHOLD: int = 50

# quality enum bands (locked half-open intervals).
QUALITY_BANDS: tuple[tuple[float, str], ...] = (
    (0.85, "excellent"),
    (0.70, "good"),
    (0.50, "acceptable"),
    (0.0, "poor"),
)

# Failure recurrence look-back window.
FAILURE_LOOKBACK = timedelta(days=7)

# Default I/O paths (relative to CWD when not overridden).
DEFAULT_TELEMETRY = ".claude/harness/telemetry.jsonl"
DEFAULT_OUTPUT = ".claude/harness/grade.jsonl"
DEFAULT_STATE = ".claude/harness/state.json"

# Risk path patterns for scope_blast (per schema: *.lock and migrations/*).
RISK_LOCK_SUFFIX = ".lock"
RISK_MIGRATION_PREFIX = "migrations/"


# ---------------------------------------------------------------------------
# Pure rubric helpers (deterministic; no randomness; no time-of-day reads).
# ---------------------------------------------------------------------------

def _resolve_cluster_for_row(attempt_history: list[dict]) -> str | None:
    """Pick the cluster_id representing this row.

    The telemetry row has no top-level cluster_id; only attempt_history items
    carry one. Rule (deterministic, documented):
      - If attempt_history is empty -> no cluster (None).
      - Otherwise return the most frequent cluster_id; ties broken by
        first-seen order in attempt_history.
    """
    if not attempt_history:
        return None
    seen_order: list[str] = []
    counts: Counter[str] = Counter()
    for entry in attempt_history:
        cid = entry.get("cluster_id")
        if not isinstance(cid, str):
            continue
        if cid not in counts:
            seen_order.append(cid)
        counts[cid] += 1
    if not counts:
        return None
    max_count = max(counts.values())
    for cid in seen_order:
        if counts[cid] == max_count:
            return cid
    return seen_order[0]


def compute_outcome_quality(skill_outcome: dict | None) -> float:
    """Schema rule:
        completed + exit_code == 0 + final_state has no
        {failed, aborted, error} substring -> 1.0
        Otherwise table-derived: exit_code != 0 -> 0.0; final_state contains
        failed/aborted/error -> 0.3; absent skill_outcome -> 0.5 (defensive).
    The "absent" default is documented here per ctx.md error_handling guidance
    (defensive, deterministic; no randomness).
    """
    if not isinstance(skill_outcome, dict):
        return 0.5
    exit_code = skill_outcome.get("exit_code")
    final_state = skill_outcome.get("final_state") or ""
    if not isinstance(final_state, str):
        final_state = ""
    final_state_lc = final_state.lower()
    bad_substrings = ("failed", "aborted", "error")
    has_bad_substring = any(sub in final_state_lc for sub in bad_substrings)
    if exit_code == 0 and not has_bad_substring:
        return 1.0
    if exit_code != 0:
        return 0.0
    # exit_code == 0 but bad substring in final_state
    return 0.3


def compute_iteration_velocity(attempt_history: list[dict], cluster_id: str | None) -> float:
    """Schema rule: 1 / N where N = attempt count of this row's cluster.
    No cluster -> N = 1 -> 1.0.
    """
    if cluster_id is None:
        n = 1
    else:
        n = sum(
            1
            for entry in attempt_history
            if isinstance(entry, dict) and entry.get("cluster_id") == cluster_id
        )
        if n < 1:
            n = 1
    return 1.0 / n


def _is_risk_path(path: str) -> bool:
    if path.endswith(RISK_LOCK_SUFFIX):
        return True
    if path.startswith(RISK_MIGRATION_PREFIX):
        return True
    return False


def compute_scope_blast(diff_summary_redacted: list[dict] | None) -> float:
    """Schema rule:
        score = 1 - min(1, files_touched/10) * 0.7 - risk_path_hit * 0.3
        risk_path_hit = 1 if any path matches *.lock or migrations/* else 0.
    """
    files = diff_summary_redacted if isinstance(diff_summary_redacted, list) else []
    files_touched = len(files)
    risk_hit = 0
    for entry in files:
        if isinstance(entry, dict) and _is_risk_path(entry.get("path", "")):
            risk_hit = 1
            break
    score = 1.0 - min(1.0, files_touched / 10.0) * 0.7 - risk_hit * 0.3
    if score < 0.0:
        score = 0.0
    if score > 1.0:
        score = 1.0
    return score


def compute_human_override_rate(skill_outcome: dict | None) -> float:
    """Schema rule:
        final_state contains override / manual / bypass substring -> 0.0
        else -> 1.0
    """
    if not isinstance(skill_outcome, dict):
        return 1.0
    final_state = skill_outcome.get("final_state") or ""
    if not isinstance(final_state, str):
        return 1.0
    final_state_lc = final_state.lower()
    if any(sub in final_state_lc for sub in ("override", "manual", "bypass")):
        return 0.0
    return 1.0


def _parse_iso_run_at(run_at: Any) -> datetime | None:
    if not isinstance(run_at, str):
        return None
    candidate = run_at.strip()
    if candidate.endswith("Z"):
        candidate = candidate[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(candidate)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def compute_failure_recurrence(
    attempt_history: list[dict],
    cluster_id: str | None,
    now: datetime,
) -> float:
    """Schema rule:
        K = past-7-days fail count for the same cluster_id
        score = max(0, 1 - K * 0.2)   (K=0 -> 1.0; K>=5 -> 0.0)
    """
    if cluster_id is None:
        return 1.0
    cutoff = now - FAILURE_LOOKBACK
    k = 0
    for entry in attempt_history:
        if not isinstance(entry, dict):
            continue
        if entry.get("cluster_id") != cluster_id:
            continue
        if entry.get("result") != "fail":
            continue
        run_at = _parse_iso_run_at(entry.get("run_at"))
        if run_at is None:
            continue
        if run_at >= cutoff:
            k += 1
    score = 1.0 - k * 0.2
    if score < 0.0:
        score = 0.0
    return score


def quality_band(aggregate: float) -> str:
    for threshold, label in QUALITY_BANDS:
        if aggregate >= threshold:
            return label
    return "poor"


def compute_dims(row: dict, now: datetime) -> dict[str, float]:
    skill_outcome = row.get("skill_outcome")
    attempt_history_raw = row.get("attempt_history") or []
    attempt_history = attempt_history_raw if isinstance(attempt_history_raw, list) else []
    diff_summary = row.get("diff_summary_redacted")
    cluster_id = _resolve_cluster_for_row(attempt_history)

    return {
        "outcome_quality": compute_outcome_quality(skill_outcome),
        "iteration_velocity": compute_iteration_velocity(attempt_history, cluster_id),
        "scope_blast": compute_scope_blast(diff_summary),
        "human_override_rate": compute_human_override_rate(skill_outcome),
        "failure_recurrence": compute_failure_recurrence(attempt_history, cluster_id, now),
    }


def aggregate_score(dims: dict[str, float]) -> float:
    # Equal weight: aggregate = sum(dims) / 5. Keep the explicit 5 to anchor INV-4.
    return sum(dims[name] for name in DIM_NAMES) / 5


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------

def read_telemetry(path: Path) -> list[dict]:
    """Read telemetry.jsonl line-by-line. Skip un-parseable lines with a warning
    on stderr (per ctx.md error_handling: keep going, don't abort).
    """
    rows: list[dict] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                obj = json.loads(stripped)
            except json.JSONDecodeError as exc:
                print(
                    f"warning: skipping malformed telemetry line {lineno}: {exc}",
                    file=sys.stderr,
                )
                continue
            if isinstance(obj, dict):
                rows.append(obj)
    return rows


def build_verdict(row: dict, now: datetime) -> dict:
    dims = compute_dims(row, now)
    aggregate = aggregate_score(dims)
    # Build dims with locked field order (KD-4 deterministic invariant).
    ordered_dims = {name: dims[name] for name in DIM_NAMES}
    ordered_weights = {name: WEIGHTS[name] for name in DIM_NAMES}
    return {
        "session_id": row.get("session_id", ""),
        "dims": ordered_dims,
        "aggregate": aggregate,
        "quality": quality_band(aggregate),
        "weights": ordered_weights,
    }


def write_grade_jsonl(path: Path, verdicts: list[dict]) -> None:
    """Rewrite grade.jsonl from scratch (atomic via tmp + rename).

    Note: idempotent rebuild requires rewrite, not append. See module docstring.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        for verdict in verdicts:
            # sort_keys=True for byte-stable output regardless of dict insertion
            # order in older Python versions; we also keep dim/weights ordered
            # by construction. Both layers together honour the "fields fixed
            # ordering" deterministic invariant.
            f.write(json.dumps(verdict, ensure_ascii=False, sort_keys=True))
            f.write("\n")
    tmp.replace(path)


def load_state(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            obj = json.load(f)
        if isinstance(obj, dict):
            return obj
        return {}
    except (OSError, json.JSONDecodeError) as exc:
        print(f"warning: state.json unreadable, treating as empty: {exc}", file=sys.stderr)
        return {}


def write_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, sort_keys=True)
    tmp.replace(path)


# ---------------------------------------------------------------------------
# CLI entrypoint
# ---------------------------------------------------------------------------

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="grade-collector: telemetry.jsonl -> grade.jsonl",
    )
    parser.add_argument("--telemetry", default=DEFAULT_TELEMETRY,
                        help="Path to telemetry.jsonl (default: %(default)s)")
    parser.add_argument("--output", default=DEFAULT_OUTPUT,
                        help="Path to grade.jsonl output (default: %(default)s)")
    parser.add_argument("--state", default=DEFAULT_STATE,
                        help="Path to state.json (default: %(default)s)")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    telemetry_path = Path(args.telemetry)
    output_path = Path(args.output)
    state_path = Path(args.state)

    rows = read_telemetry(telemetry_path)
    completed_rows = [r for r in rows if r.get("terminal_state") == "completed"]

    # Use UTC now() ONLY for failure_recurrence look-back and for the
    # tune_review_due_since stamp. These do not flow into grade.jsonl row
    # content (only into the optional state.json), preserving byte-for-byte
    # reproducibility of grade.jsonl on stable telemetry.
    now = datetime.now(timezone.utc)

    verdicts = [build_verdict(row, now) for row in completed_rows]
    write_grade_jsonl(output_path, verdicts)

    cumulative_completed_count = len(completed_rows)
    state = load_state(state_path)
    state["cumulative_completed_count"] = cumulative_completed_count
    state["last_grade_run_at"] = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    if cumulative_completed_count >= TUNE_TRIGGER_THRESHOLD:
        # Only set tune_review_due_since if not already set (per state schema:
        # user runs --tune-acknowledged to clear; we don't keep bumping it).
        if not state.get("tune_review_due_since"):
            state["tune_review_due_since"] = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        # Structured signal: keep both forms for grep-friendliness — JSON for
        # machines, plain for human eyeballs.
        signal = {
            "tune_review_due": True,
            "cumulative_completed_count": cumulative_completed_count,
        }
        print(json.dumps(signal, sort_keys=True))
        print(f"tune_review_due: true (cumulative_completed_count={cumulative_completed_count}, threshold>=50)")
    else:
        # Ensure key is present-and-null for downstream consumers.
        state.setdefault("tune_review_due_since", None)

    write_state(state_path, state)
    return 0


if __name__ == "__main__":
    sys.exit(main())
