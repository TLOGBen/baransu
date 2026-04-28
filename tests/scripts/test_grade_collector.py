#!/usr/bin/env python3
"""Tests for plugins/baransu/scripts/grade-collector.py.

Coverage:
  - INT-3:  filter completed-only (aborted/interrupted/in_progress excluded)
  - INT-10: deterministic 5-dim aggregate, equal-weight 1/5, schema formulas
  - INT-11a: tune trigger flips at 49 vs 50 cumulative completed rows
  - INV-4:  source contains 1/5 OR 0.2 OR equal[_ ]weight literal
  - Reproducibility: same input -> byte-for-byte identical grade.jsonl

Rubric formulas follow plugins/baransu/skills/_shared/grade-triage-schema.md
section 1 (READ-ONLY authority). Where ctx.md and schema disagree, schema wins
(per ctx.md to_read_only_dependency: "rubric formula must not deviate from
that table").
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

WORKTREE_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = WORKTREE_ROOT / "plugins" / "baransu" / "scripts" / "grade-collector.py"


def make_telemetry_row(
    session_id: str,
    terminal_state: str = "completed",
    exit_code: int = 0,
    final_state: str = "approved",
    skill_name: str = "think",
    diff_files: list | None = None,
    attempt_history: list | None = None,
    prompt_text: str = "test prompt",
    commit_hash: str = "0" * 40,
) -> dict:
    return {
        "session_id": session_id,
        "terminal_state": terminal_state,
        "prompt_text": prompt_text,
        "skill_outcome": {
            "skill_name": skill_name,
            "final_state": final_state,
            "exit_code": exit_code,
        },
        "commit_hash": commit_hash,
        "diff_summary_redacted": diff_files if diff_files is not None else [],
        "attempt_history": attempt_history if attempt_history is not None else [],
    }


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True))
            f.write("\n")


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


class GradeCollectorTestBase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="grade-collector-test-"))
        self.telemetry = self.tmp / "telemetry.jsonl"
        self.output = self.tmp / "grade.jsonl"
        self.state = self.tmp / "state.json"

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def read_grade_rows(self) -> list[dict]:
        if not self.output.exists():
            return []
        with self.output.open("r", encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]


class TestINT3CompletedOnly(GradeCollectorTestBase):
    """INT-3: only completed rows produce verdicts."""

    def test_only_completed_rows_emit_verdicts(self) -> None:
        rows: list[dict] = []
        # 5 completed
        for i in range(1, 6):
            rows.append(make_telemetry_row(f"s-c-{i:03d}", terminal_state="completed"))
        # 3 aborted
        for i in range(1, 4):
            rows.append(make_telemetry_row(f"s-a-{i:03d}", terminal_state="aborted"))
        # 2 interrupted
        for i in range(1, 3):
            rows.append(make_telemetry_row(f"s-i-{i:03d}", terminal_state="interrupted"))
        write_jsonl(self.telemetry, rows)

        result = run_collector(self.telemetry, self.output, self.state)
        self.assertEqual(result.returncode, 0, msg=f"stderr={result.stderr}")

        verdicts = self.read_grade_rows()
        self.assertEqual(len(verdicts), 5, "expected 5 completed verdicts")

        emitted_ids = {v["session_id"] for v in verdicts}
        completed_ids = {f"s-c-{i:03d}" for i in range(1, 6)}
        self.assertEqual(emitted_ids, completed_ids)

        for non_completed_id in (
            [f"s-a-{i:03d}" for i in range(1, 4)]
            + [f"s-i-{i:03d}" for i in range(1, 3)]
        ):
            self.assertNotIn(non_completed_id, emitted_ids)


class TestINT10DeterministicAggregate(GradeCollectorTestBase):
    """INT-10: hand-craft inputs so each dim hits a known value via schema formulas."""

    def test_all_dims_max_aggregate_excellent(self) -> None:
        # Schema formulas:
        #   outcome_quality:    completed + exit==0 + final_state has none of
        #                       {failed, aborted, error} -> 1.0
        #   iteration_velocity: 1/N where N = cluster attempt count;
        #                       no cluster -> N=1 -> 1.0
        #   scope_blast:        1 - min(1, files/10)*0.7 - risk_hit*0.3;
        #                       0 files, no risk -> 1.0
        #   human_override_rate: final_state has none of override/manual/bypass -> 1.0
        #   failure_recurrence:  K (past-7d fails for cluster) = 0 -> 1.0
        # aggregate = (1+1+1+1+1)/5 = 1.0 -> excellent
        rows = [
            make_telemetry_row(
                "s-max",
                terminal_state="completed",
                exit_code=0,
                final_state="approved",
                diff_files=[],
                attempt_history=[],
            )
        ]
        write_jsonl(self.telemetry, rows)
        result = run_collector(self.telemetry, self.output, self.state)
        self.assertEqual(result.returncode, 0, msg=f"stderr={result.stderr}")

        verdicts = self.read_grade_rows()
        self.assertEqual(len(verdicts), 1)
        v = verdicts[0]

        self.assertEqual(v["session_id"], "s-max")
        # 5 dim presence + values
        for dim in (
            "outcome_quality",
            "iteration_velocity",
            "scope_blast",
            "human_override_rate",
            "failure_recurrence",
        ):
            self.assertIn(dim, v["dims"])
            self.assertAlmostEqual(v["dims"][dim], 1.0, places=6)

        # aggregate = 1.0
        self.assertAlmostEqual(v["aggregate"], 1.0, places=6)
        self.assertEqual(v["quality"], "excellent")

        # weights = 0.2 each
        for dim in v["weights"]:
            self.assertAlmostEqual(v["weights"][dim], 0.2, places=6)

    def test_mixed_dims_acceptable(self) -> None:
        # outcome_quality:    exit_code != 0 -> 0.0
        # iteration_velocity: cluster cl-x has N=2 attempts -> 1/2 = 0.5
        # scope_blast:        5 files (no risk) -> 1 - 0.5*0.7 - 0 = 0.65
        # human_override_rate: final_state contains "override" -> 0.0
        # failure_recurrence: K=2 fails in cluster cl-x within 7d -> 1 - 0.4 = 0.6
        # aggregate = (0 + 0.5 + 0.65 + 0 + 0.6)/5 = 0.35 -> poor
        from datetime import datetime, timedelta, timezone
        now = datetime.now(timezone.utc)
        recent = (now - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        recent2 = (now - timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ")

        rows = [
            make_telemetry_row(
                "s-mid",
                terminal_state="completed",
                exit_code=1,
                final_state="manual_override",
                diff_files=[
                    {"path": f"src/file{i}.py", "plus": 1, "minus": 0}
                    for i in range(5)
                ],
                attempt_history=[
                    {"cluster_id": "cl-x", "run_at": recent, "result": "fail"},
                    {"cluster_id": "cl-x", "run_at": recent2, "result": "fail"},
                ],
            )
        ]
        write_jsonl(self.telemetry, rows)
        result = run_collector(self.telemetry, self.output, self.state)
        self.assertEqual(result.returncode, 0, msg=f"stderr={result.stderr}")

        verdicts = self.read_grade_rows()
        self.assertEqual(len(verdicts), 1)
        v = verdicts[0]

        self.assertAlmostEqual(v["dims"]["outcome_quality"], 0.0, places=6)
        self.assertAlmostEqual(v["dims"]["iteration_velocity"], 0.5, places=6)
        self.assertAlmostEqual(v["dims"]["scope_blast"], 0.65, places=6)
        self.assertAlmostEqual(v["dims"]["human_override_rate"], 0.0, places=6)
        self.assertAlmostEqual(v["dims"]["failure_recurrence"], 0.6, places=6)

        expected_aggregate = (0.0 + 0.5 + 0.65 + 0.0 + 0.6) / 5
        self.assertAlmostEqual(v["aggregate"], expected_aggregate, places=6)
        self.assertEqual(v["quality"], "poor")  # 0.35 < 0.50


class TestINT11aTuneTrigger(GradeCollectorTestBase):
    """INT-11a: 49 completed rows -> no tune trigger; 50 completed -> trigger fires."""

    def _make_n_completed(self, n: int) -> list[dict]:
        return [
            make_telemetry_row(f"s-{i:04d}", terminal_state="completed")
            for i in range(n)
        ]

    def test_49_does_not_trigger(self) -> None:
        write_jsonl(self.telemetry, self._make_n_completed(49))
        result = run_collector(self.telemetry, self.output, self.state)
        self.assertEqual(result.returncode, 0, msg=f"stderr={result.stderr}")
        self.assertNotIn("tune_review_due: true", result.stdout)
        self.assertNotIn('"tune_review_due": true', result.stdout)
        # state.json should NOT have tune_review_due_since set
        if self.state.exists():
            with self.state.open("r", encoding="utf-8") as f:
                state_obj = json.load(f)
            self.assertIsNone(state_obj.get("tune_review_due_since"))

    def test_50_triggers(self) -> None:
        write_jsonl(self.telemetry, self._make_n_completed(50))
        result = run_collector(self.telemetry, self.output, self.state)
        self.assertEqual(result.returncode, 0, msg=f"stderr={result.stderr}")
        # accept either form; orchestrator hinted JSON form, plain form is human-friendly
        triggered = (
            "tune_review_due: true" in result.stdout
            or '"tune_review_due": true' in result.stdout
            or '"tune_review_due":true' in result.stdout
        )
        self.assertTrue(triggered, f"expected tune_review_due signal in stdout: {result.stdout!r}")

        # state.json should have tune_review_due_since (ISO datetime)
        self.assertTrue(self.state.exists(), "state.json should be written")
        with self.state.open("r", encoding="utf-8") as f:
            state_obj = json.load(f)
        self.assertIsNotNone(state_obj.get("tune_review_due_since"))
        # rough ISO 8601 sniff
        self.assertRegex(
            state_obj["tune_review_due_since"],
            r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}",
        )


class TestINV4EqualWeightLiteral(unittest.TestCase):
    """INV-4: source script contains 1/5 or 0.2 or equal[_ ]weight literal."""

    def test_source_contains_equal_weight_marker(self) -> None:
        self.assertTrue(SCRIPT_PATH.exists(), f"script missing: {SCRIPT_PATH}")
        source = SCRIPT_PATH.read_text(encoding="utf-8")
        pattern = re.compile(r"1/5|0\.2|equal[_ ]weight", re.IGNORECASE)
        self.assertRegex(source, pattern, "must contain 1/5 or 0.2 or equal_weight literal")


class TestReproducibility(GradeCollectorTestBase):
    """Same input -> byte-for-byte identical grade.jsonl across runs."""

    def test_two_runs_produce_identical_output(self) -> None:
        rows = [
            make_telemetry_row(f"s-r-{i:03d}", terminal_state="completed")
            for i in range(10)
        ]
        # also throw in some non-completed to ensure stable filtering
        rows.append(make_telemetry_row("s-r-skip", terminal_state="aborted"))
        write_jsonl(self.telemetry, rows)

        result1 = run_collector(self.telemetry, self.output, self.state)
        self.assertEqual(result1.returncode, 0, msg=f"stderr={result1.stderr}")
        first_bytes = self.output.read_bytes()

        # second run: same inputs, fresh state file path simulates idempotent rebuild
        result2 = run_collector(self.telemetry, self.output, self.state)
        self.assertEqual(result2.returncode, 0, msg=f"stderr={result2.stderr}")
        second_bytes = self.output.read_bytes()

        self.assertEqual(first_bytes, second_bytes, "grade.jsonl must be byte-for-byte stable")


if __name__ == "__main__":
    unittest.main(verbosity=2)
