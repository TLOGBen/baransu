#!/usr/bin/env python3
"""triage-cluster — grade.jsonl + telemetry.jsonl -> triage.jsonl.

Reads .claude/harness/grade.jsonl (filters quality == "poor"), joins
telemetry.jsonl by session_id to recover skill_outcome (skill_name +
final_state), groups verdicts into clusters by

    cluster_id = f"{skill_name}--{sha256(primary_error_signature)[:8]}"

where ``primary_error_signature`` is taken from
``skill_outcome.final_state``. The schema-level requirement ("primary
error signal hash") asks for a deterministic hash of the dominant error
signal; the structured telemetry exposes that signal as ``final_state``
(the human-readable error label, e.g. ``tests_failed`` /
``compile_error`` / ``approved``). Picking ``final_state`` keeps the
function deterministic (no log-line parsing, no time / random input) and
maps cleanly across distinct error modes.

For each cluster row we compute:
  - ``severity_dims``: arithmetic mean per dim across constituent grade rows.
    Note: ``grade.dims`` are quality scores (high = good). Per ctx.md and
    schema §6 the spec accepts mean as the deterministic aggregator and
    documents the semantic ambiguity (high quality_dim = least severe).
    We follow ctx.md literally; downstream `/triage` SKILL may invert
    later, this script is the executor only.
  - ``severity_aggregate``: ``sum(severity_dims) / 5`` (locked equal weight).
  - ``escalate``: ``false`` (boolean). The /triage SKILL.md layer maps
    this to the 3-value enum (``false`` / ``requires_human`` /
    ``daily_quota_exceeded``); this script defers that decision.
  - ``evidence_bundle``: placeholder ``{root_cause_guess: null,
    citations: [], confidence: null}``; investigator-agent fills it later.
  - ``attempt_count``: ``0`` (read-only view; spec authority is
    telemetry.attempt_history; the /triage SKILL re-derives it).

Output ordering (deterministic): rows sorted by ``severity_aggregate``
descending, ties broken by ``cluster_id`` ascending. Inside a row the
``member_session_ids`` array is sorted lexicographically. JSON output
uses ``sort_keys=True`` to lock byte-for-byte stability.

Empty/no-poor input -> 0-byte triage.jsonl (graceful exit 0). The file
is REWRITTEN on each run (not appended), matching grade-collector.py's
idempotency contract.

No external deps; stdlib only. No timestamps / uuids / random fields
flow into output rows.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Iterable

# ---------------------------------------------------------------------------
# Locked spec constants
# ---------------------------------------------------------------------------

DIM_NAMES: tuple[str, ...] = (
    "outcome_quality",
    "iteration_velocity",
    "scope_blast",
    "human_override_rate",
    "failure_recurrence",
)

DEFAULT_GRADE = ".claude/harness/grade.jsonl"
DEFAULT_TELEMETRY = ".claude/harness/telemetry.jsonl"
DEFAULT_OUTPUT = ".claude/harness/triage.jsonl"

CLUSTER_HASH_PREFIX_LEN = 8  # short hash (first 8 hex chars of sha256)


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------

def read_jsonl(path: Path) -> list[dict]:
    """Read a JSONL file. Skip blank/malformed lines with a stderr warning."""
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
                    f"warning: skipping malformed line {lineno} in {path}: {exc}",
                    file=sys.stderr,
                )
                continue
            if isinstance(obj, dict):
                rows.append(obj)
    return rows


def index_telemetry(rows: Iterable[dict]) -> dict[str, dict]:
    """Index telemetry rows by session_id. Last write wins on dup ids
    (telemetry is conceptually unique per session_id; the safeguard exists
    so the script never crashes on imperfect inputs)."""
    by_id: dict[str, dict] = {}
    for row in rows:
        sid = row.get("session_id")
        if isinstance(sid, str) and sid:
            by_id[sid] = row
    return by_id


# ---------------------------------------------------------------------------
# Cluster derivation
# ---------------------------------------------------------------------------

def primary_error_signature(telemetry_row: dict | None) -> str:
    """Derive the deterministic error signature from a telemetry row.

    Source: skill_outcome.final_state (string label). Empty / missing
    falls back to ``""`` so the hash is still defined and stable.
    """
    if not isinstance(telemetry_row, dict):
        return ""
    skill_outcome = telemetry_row.get("skill_outcome")
    if not isinstance(skill_outcome, dict):
        return ""
    final_state = skill_outcome.get("final_state")
    if not isinstance(final_state, str):
        return ""
    return final_state


def skill_name_for(telemetry_row: dict | None) -> str:
    if not isinstance(telemetry_row, dict):
        return "unknown"
    skill_outcome = telemetry_row.get("skill_outcome")
    if not isinstance(skill_outcome, dict):
        return "unknown"
    name = skill_outcome.get("skill_name")
    if not isinstance(name, str) or not name:
        return "unknown"
    return name


def derive_cluster_id(telemetry_row: dict | None) -> str:
    """cluster_id = f'{skill_name}--{sha256(final_state)[:8]}'."""
    skill = skill_name_for(telemetry_row)
    sig = primary_error_signature(telemetry_row)
    short_hash = hashlib.sha256(sig.encode("utf-8")).hexdigest()[:CLUSTER_HASH_PREFIX_LEN]
    return f"{skill}--{short_hash}"


# ---------------------------------------------------------------------------
# Severity computation
# ---------------------------------------------------------------------------

def mean_dims(grade_rows: list[dict]) -> dict[str, float]:
    """Mean of each named dim across the supplied grade rows.

    Missing/non-numeric dim values are treated as 0.0 (defensive; same
    spirit as grade-collector's "absent skill_outcome -> defensive
    default"). All cluster members are expected to be poor verdicts that
    already carry the 5 dims, so the defensive branch is rarely hit.
    """
    if not grade_rows:
        return {name: 0.0 for name in DIM_NAMES}
    n = len(grade_rows)
    out: dict[str, float] = {}
    for name in DIM_NAMES:
        total = 0.0
        for row in grade_rows:
            dims = row.get("dims") or {}
            value = dims.get(name) if isinstance(dims, dict) else None
            if isinstance(value, (int, float)):
                total += float(value)
        out[name] = total / n
    return out


def severity_aggregate(severity_dims: dict[str, float]) -> float:
    return sum(severity_dims[name] for name in DIM_NAMES) / 5


# ---------------------------------------------------------------------------
# Cluster row construction
# ---------------------------------------------------------------------------

def build_cluster_row(
    cluster_id: str,
    member_grade_rows: list[dict],
) -> dict:
    member_ids = sorted(
        str(r.get("session_id", ""))
        for r in member_grade_rows
        if isinstance(r.get("session_id"), str) and r.get("session_id")
    )
    sev_dims = mean_dims(member_grade_rows)
    # Re-key with locked DIM_NAMES order so JSON serialization is stable
    # regardless of insertion order in older interpreters.
    ordered_severity_dims = {name: sev_dims[name] for name in DIM_NAMES}

    return {
        "cluster_id": cluster_id,
        "member_session_ids": member_ids,
        "severity_dims": ordered_severity_dims,
        "severity_aggregate": severity_aggregate(ordered_severity_dims),
        # Boolean false: this script defers the 3-value enum decision to
        # /triage SKILL.md. Schema §4 enum values (`false` / `requires_human`
        # / `daily_quota_exceeded`) are mapped at the SKILL layer.
        "escalate": False,
        # Placeholder; investigator-agent populates these fields later.
        "evidence_bundle": {
            "root_cause_guess": None,
            "citations": [],
            "confidence": None,
        },
        # Read-only view; authoritative source is telemetry.attempt_history.
        # This script writes 0; /triage SKILL re-derives via jq.
        "attempt_count": 0,
    }


# ---------------------------------------------------------------------------
# Output writer
# ---------------------------------------------------------------------------

def write_triage_jsonl(path: Path, cluster_rows: list[dict]) -> None:
    """Rewrite triage.jsonl atomically (tmp + rename).

    Empty input -> 0-byte file. Sort: severity_aggregate desc, ties by
    cluster_id asc. Per-row JSON uses sort_keys=True.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    sorted_rows = sorted(
        cluster_rows,
        key=lambda r: (-r["severity_aggregate"], r["cluster_id"]),
    )
    with tmp.open("w", encoding="utf-8") as f:
        for row in sorted_rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True))
            f.write("\n")
    tmp.replace(path)


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def cluster_poor_verdicts(
    grade_rows: list[dict],
    telemetry_index: dict[str, dict],
) -> list[dict]:
    """Filter to poor verdicts, group by cluster_id, build cluster rows."""
    poor_rows = [r for r in grade_rows if r.get("quality") == "poor"]
    if not poor_rows:
        return []

    groups: dict[str, list[dict]] = {}
    for row in poor_rows:
        sid = row.get("session_id")
        if not isinstance(sid, str):
            continue
        tele_row = telemetry_index.get(sid)
        cid = derive_cluster_id(tele_row)
        groups.setdefault(cid, []).append(row)

    return [build_cluster_row(cid, members) for cid, members in groups.items()]


# ---------------------------------------------------------------------------
# CLI entrypoint
# ---------------------------------------------------------------------------

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="triage-cluster: grade.jsonl + telemetry.jsonl -> triage.jsonl",
    )
    parser.add_argument("--grade", default=DEFAULT_GRADE,
                        help="Path to grade.jsonl (default: %(default)s)")
    parser.add_argument("--telemetry", default=DEFAULT_TELEMETRY,
                        help="Path to telemetry.jsonl (default: %(default)s)")
    parser.add_argument("--output", default=DEFAULT_OUTPUT,
                        help="Path to triage.jsonl output (default: %(default)s)")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    grade_path = Path(args.grade)
    telemetry_path = Path(args.telemetry)
    output_path = Path(args.output)

    grade_rows = read_jsonl(grade_path)
    telemetry_rows = read_jsonl(telemetry_path)
    telemetry_index = index_telemetry(telemetry_rows)

    cluster_rows = cluster_poor_verdicts(grade_rows, telemetry_index)
    write_triage_jsonl(output_path, cluster_rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())
