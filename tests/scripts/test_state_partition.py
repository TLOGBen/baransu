#!/usr/bin/env python3
"""Tests for state.json partition contract — TASK-scripts-fixes-02.

Coverage:
  - Test 1: REQ-005 Scenario 2 — grade-collector preserves triage partition
  - Test 2: B12 first-run — bootstrap when state.json missing
  - Test 3: B12 first-run — bootstrap on `{}` empty state without crash
  - Test 4: INT-10 (REQ-005 Scenario 4) — 100-rep partition stress
  - Test 5: B17 forward-compat — unknown future keys preserved byte-identical

Authoritative partition (per ctx.md state_json_schema_v2):
  grade partition (writer: grade-collector / --tune-acknowledged):
    - last_grade_run_at
    - cumulative_completed_count
    - tune_review_due_since
  triage partition (writer: push-gate.sh):
    - daily_push_count
    - daily_push_date
    - last_triage_run_at

Cross-partition writes are forbidden. read-merge-write atomic is required.
"""

from __future__ import annotations

import importlib.util
import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

WORKTREE_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = WORKTREE_ROOT / "plugins" / "baransu" / "scripts" / "grade-collector.py"

# Partition keys per ctx.md
GRADE_KEYS = ("last_grade_run_at", "cumulative_completed_count", "tune_review_due_since")
TRIAGE_KEYS = ("daily_push_count", "daily_push_date", "last_triage_run_at")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True))
            f.write("\n")


def make_completed_row(session_id: str) -> dict:
    return {
        "session_id": session_id,
        "terminal_state": "completed",
        "prompt_text": "test",
        "skill_outcome": {
            "skill_name": "think",
            "final_state": "approved",
            "exit_code": 0,
        },
        "commit_hash": "0" * 40,
        "diff_summary_redacted": [],
        "attempt_history": [],
    }


def run_collector(
    telemetry: Path,
    output: Path,
    state: Path,
) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--telemetry",
            str(telemetry),
            "--output",
            str(output),
            "--state",
            str(state),
        ],
        capture_output=True,
        text=True,
        check=False,
    )


def _load_grade_module():
    """Import grade-collector.py as a module so we can reuse atomic write_state.

    The hyphenated filename precludes plain `import` so we use spec_from_file_location.
    """
    spec = importlib.util.spec_from_file_location("grade_collector", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def triage_write_helper(state_path: Path, *, push_count: int, push_date: str, run_at: str) -> None:
    """Mimic push-gate.sh's read-merge-write of triage partition keys.

    push-gate.sh hasn't been written yet; this helper enforces the same
    partition contract from the triage side so the stress test confirms the
    bidirectional invariant. It loads full state, modifies ONLY triage
    partition keys, and atomic-renames the temp file.
    """
    if state_path.exists():
        try:
            with state_path.open("r", encoding="utf-8") as f:
                obj = json.load(f)
            state = obj if isinstance(obj, dict) else {}
        except (OSError, json.JSONDecodeError):
            state = {}
    else:
        state = {}

    # Merge ONLY triage partition keys.
    merged = dict(state)
    merged["daily_push_count"] = push_count
    merged["daily_push_date"] = push_date
    merged["last_triage_run_at"] = run_at

    state_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = state_path.with_suffix(state_path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, sort_keys=True)
    os.replace(tmp, state_path)


class StatePartitionTestBase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="state-partition-test-"))
        self.telemetry = self.tmp / "telemetry.jsonl"
        self.output = self.tmp / "grade.jsonl"
        self.state = self.tmp / "state.json"

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _seed_state(self, payload: dict) -> None:
        self.state.parent.mkdir(parents=True, exist_ok=True)
        with self.state.open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, sort_keys=True)

    def _read_state(self) -> dict:
        with self.state.open("r", encoding="utf-8") as f:
            return json.load(f)


class TestGradeCollectorPreservesTriagePartition(StatePartitionTestBase):
    """Test 1 — REQ-005 Scenario 2.

    state.json pre-seeded with daily_push_count=3 and daily_push_date="2026-04-29".
    After running grade-collector, those triage keys must remain byte-identical.
    """

    def test_grade_collector_preserves_triage_partition(self) -> None:
        seed = {
            "daily_push_count": 3,
            "daily_push_date": "2026-04-29",
            "last_triage_run_at": "2026-04-29T08:00:00Z",
        }
        self._seed_state(seed)

        write_jsonl(self.telemetry, [make_completed_row("s-1")])
        result = run_collector(self.telemetry, self.output, self.state)
        self.assertEqual(result.returncode, 0, msg=f"stderr={result.stderr}")

        state = self._read_state()

        # Triage partition byte-identical
        self.assertEqual(state["daily_push_count"], 3)
        self.assertEqual(state["daily_push_date"], "2026-04-29")
        self.assertEqual(state["last_triage_run_at"], "2026-04-29T08:00:00Z")

        # Grade partition reflects this run
        self.assertEqual(state["cumulative_completed_count"], 1)
        self.assertIsNotNone(state.get("last_grade_run_at"))


class TestGradeCollectorBootstrapWhenStateMissing(StatePartitionTestBase):
    """Test 2 — B12 first-run.

    state.json absent → grade-collector must bootstrap with all 6 fields at
    their documented defaults so subsequent push-gate runs don't crash.
    """

    def test_grade_collector_bootstrap_when_state_missing(self) -> None:
        # state path does not exist.
        self.assertFalse(self.state.exists())

        write_jsonl(self.telemetry, [make_completed_row("s-1")])
        result = run_collector(self.telemetry, self.output, self.state)
        self.assertEqual(result.returncode, 0, msg=f"stderr={result.stderr}")

        self.assertTrue(self.state.exists())
        state = self._read_state()

        for key in GRADE_KEYS + TRIAGE_KEYS:
            self.assertIn(key, state, f"missing bootstrap key: {key}")

        # Grade fields should reflect this run.
        self.assertEqual(state["cumulative_completed_count"], 1)
        self.assertIsNotNone(state["last_grade_run_at"])
        # tune_review_due_since must be present-and-null (count < 50).
        self.assertIsNone(state["tune_review_due_since"])

        # Triage fields should be at documented defaults.
        self.assertEqual(state["daily_push_count"], 0)
        self.assertIsNone(state["last_triage_run_at"])
        # daily_push_date default: today on first run; just assert ISO-shape string.
        self.assertIsInstance(state["daily_push_date"], str)
        self.assertRegex(state["daily_push_date"], r"^\d{4}-\d{2}-\d{2}$")


class TestGradeCollectorHandlesEmptyState(StatePartitionTestBase):
    """Test 3 — B12 first-run.

    state.json is `{}` — grade-collector must bootstrap missing fields without
    crashing.
    """

    def test_grade_collector_handles_empty_state(self) -> None:
        self._seed_state({})

        write_jsonl(self.telemetry, [make_completed_row("s-1")])
        result = run_collector(self.telemetry, self.output, self.state)
        self.assertEqual(result.returncode, 0, msg=f"stderr={result.stderr}")

        state = self._read_state()

        for key in GRADE_KEYS + TRIAGE_KEYS:
            self.assertIn(key, state, f"missing bootstrap key after empty state: {key}")

        self.assertEqual(state["cumulative_completed_count"], 1)
        self.assertIsNotNone(state["last_grade_run_at"])


class TestPartitionStress100Rep(StatePartitionTestBase):
    """Test 4 — INT-10 (REQ-005 Scenario 4).

    Pre-seed 6 fields; interleave 50 grade-collector runs with 50 triage-side
    writes (via triage_write_helper, which mimics push-gate's read-merge-write).
    After 100 invocations: all 6 fields present, grade fields reflect last
    grade write, triage fields reflect last triage write.
    """

    def test_partition_stress_100_rep(self) -> None:
        # Pre-seed
        seed = {
            "last_grade_run_at": None,
            "cumulative_completed_count": 0,
            "tune_review_due_since": None,
            "daily_push_count": 0,
            "daily_push_date": "2026-04-29",
            "last_triage_run_at": None,
        }
        self._seed_state(seed)

        # One telemetry row is enough — we just need the script to write state.
        write_jsonl(self.telemetry, [make_completed_row("s-stress-1")])

        # Build interleaved schedule: 50 grade, 50 triage, deterministic shuffle
        # so the test is stable across runs.
        events = ["grade"] * 50 + ["triage"] * 50
        rng = random.Random(0xBA7A75)  # deterministic seed
        rng.shuffle(events)

        last_grade_idx = -1
        last_triage_idx = -1
        # Track the values written by the most recent triage write so we can
        # assert byte-equality at the end.
        final_triage = {
            "daily_push_count": 0,
            "daily_push_date": "2026-04-29",
            "last_triage_run_at": None,
        }

        for idx, kind in enumerate(events):
            if kind == "grade":
                result = run_collector(self.telemetry, self.output, self.state)
                self.assertEqual(
                    result.returncode, 0,
                    msg=f"grade-collector failed at idx={idx}: stderr={result.stderr}",
                )
                last_grade_idx = idx
            else:
                push_count = idx + 1
                push_date = "2026-04-29"
                run_at = f"2026-04-29T00:{idx:02d}:00Z"
                triage_write_helper(
                    self.state,
                    push_count=push_count,
                    push_date=push_date,
                    run_at=run_at,
                )
                final_triage = {
                    "daily_push_count": push_count,
                    "daily_push_date": push_date,
                    "last_triage_run_at": run_at,
                }
                last_triage_idx = idx

        # Final assertions.
        state = self._read_state()

        # All 6 fields present.
        for key in GRADE_KEYS + TRIAGE_KEYS:
            self.assertIn(key, state, f"key dropped during stress: {key}")

        # Triage fields reflect the LAST triage write (byte-identical).
        self.assertEqual(state["daily_push_count"], final_triage["daily_push_count"])
        self.assertEqual(state["daily_push_date"], final_triage["daily_push_date"])
        self.assertEqual(state["last_triage_run_at"], final_triage["last_triage_run_at"])

        # Grade fields reflect the LAST grade write.
        # cumulative_completed_count is recomputed from telemetry on each run,
        # so its value is the count of completed rows in telemetry (= 1 here)
        # after the last grade run. last_grade_run_at must be a non-null ISO
        # timestamp set during the last grade run.
        self.assertEqual(state["cumulative_completed_count"], 1)
        self.assertIsNotNone(state["last_grade_run_at"])
        self.assertRegex(
            state["last_grade_run_at"],
            r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}",
        )

        # Sanity: both kinds actually ran.
        self.assertGreaterEqual(last_grade_idx, 0)
        self.assertGreaterEqual(last_triage_idx, 0)


class TestB17ForwardCompatUnknownKeys(StatePartitionTestBase):
    """Test 5 — B17 forward-compat.

    state.json contains an unknown future key (`last_bridge_run_at`).
    grade-collector must preserve it byte-identical.
    """

    def test_b17_forward_compat_unknown_keys(self) -> None:
        seed = {
            "last_bridge_run_at": "2026-05-15T12:34:56Z",
            "daily_push_count": 7,
            "daily_push_date": "2026-04-29",
        }
        self._seed_state(seed)

        write_jsonl(self.telemetry, [make_completed_row("s-1")])
        result = run_collector(self.telemetry, self.output, self.state)
        self.assertEqual(result.returncode, 0, msg=f"stderr={result.stderr}")

        state = self._read_state()
        # Unknown future key preserved byte-identical.
        self.assertEqual(state.get("last_bridge_run_at"), "2026-05-15T12:34:56Z")
        # Triage partition still untouched.
        self.assertEqual(state["daily_push_count"], 7)
        self.assertEqual(state["daily_push_date"], "2026-04-29")


class TestWriteStateRejectsCrossPartition(unittest.TestCase):
    """Internal contract — write_state must reject triage partition keys.

    This guards against a future regression where someone re-introduces a
    cross-partition write inside grade-collector. It is intentionally an
    in-process unit test (not subprocess) because the subprocess CLI has no
    surface to write a triage key.
    """

    def test_write_state_rejects_triage_keys(self) -> None:
        mod = _load_grade_module()
        with tempfile.TemporaryDirectory() as td:
            state_path = Path(td) / "state.json"
            with self.assertRaises(AssertionError):
                mod.write_state(state_path, {"daily_push_count": 1})


if __name__ == "__main__":
    unittest.main(verbosity=2)
