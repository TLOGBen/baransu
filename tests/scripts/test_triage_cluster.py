#!/usr/bin/env python3
"""Tests for plugins/baransu/scripts/triage-cluster.py.

Coverage (per ctx.md TASK-scripts-02):
  1. INT-4 happy path: mock grade.jsonl with 5 poor verdicts where 3 share
     the same skill_name + same primary error signature; expect >=1 cluster
     row whose member_session_ids contains the correct 3 session_ids.
  2. Determinism: two runs on the same input -> byte-for-byte identical
     triage.jsonl.
  3. 5-dim severity present: each cluster row carries `severity_dims` with
     all 5 baransu-native names + a numeric `severity_aggregate`.
  4. Empty / non-poor input: triage.jsonl is empty (0 bytes).
  5. Schema compliance: jq -e check that each row has the 7 required keys.

Authoritative schema:
  plugins/baransu/skills/_shared/grade-triage-schema.md (read-only).

Cluster key (per ctx.md):
  cluster_id = f"{skill_name}--{sha256(primary_error_signature)[:8]}"
  primary_error_signature derives from skill_outcome.final_state (the
  structured label that changes across distinct error modes; we do not
  attempt to parse "first error line" from a non-textual object).
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

WORKTREE_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = WORKTREE_ROOT / "plugins" / "baransu" / "scripts" / "triage-cluster.py"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def sig8(final_state: str) -> str:
    return hashlib.sha256(final_state.encode("utf-8")).hexdigest()[:8]


def make_grade_row(
    session_id: str,
    quality: str = "poor",
    aggregate: float = 0.3,
    dims: dict | None = None,
) -> dict:
    if dims is None:
        dims = {
            "outcome_quality": 0.0,
            "iteration_velocity": 0.5,
            "scope_blast": 0.4,
            "human_override_rate": 0.0,
            "failure_recurrence": 0.6,
        }
    weights = {
        "outcome_quality": 0.2,
        "iteration_velocity": 0.2,
        "scope_blast": 0.2,
        "human_override_rate": 0.2,
        "failure_recurrence": 0.2,
    }
    return {
        "session_id": session_id,
        "dims": dims,
        "aggregate": aggregate,
        "quality": quality,
        "weights": weights,
    }


def make_telemetry_row(
    session_id: str,
    skill_name: str = "dev",
    final_state: str = "tests_failed",
    exit_code: int = 1,
    attempt_history: list | None = None,
) -> dict:
    return {
        "session_id": session_id,
        "terminal_state": "completed",
        "prompt_text": "test prompt",
        "skill_outcome": {
            "skill_name": skill_name,
            "final_state": final_state,
            "exit_code": exit_code,
        },
        "commit_hash": "0" * 40,
        "diff_summary_redacted": [],
        "attempt_history": attempt_history if attempt_history is not None else [],
    }


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True))
            f.write("\n")


def run_triage(
    grade: Path,
    telemetry: Path,
    output: Path,
) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--grade",
            str(grade),
            "--telemetry",
            str(telemetry),
            "--output",
            str(output),
        ],
        capture_output=True,
        text=True,
        check=False,
    )


class TriageClusterTestBase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="triage-cluster-test-"))
        self.grade = self.tmp / "grade.jsonl"
        self.telemetry = self.tmp / "telemetry.jsonl"
        self.output = self.tmp / "triage.jsonl"

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def read_triage_rows(self) -> list[dict]:
        if not self.output.exists():
            return []
        with self.output.open("r", encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]


# ---------------------------------------------------------------------------
# Test 1: INT-4 happy path — 3-of-5 cluster forms correctly
# ---------------------------------------------------------------------------

class TestINT4HappyPath(TriageClusterTestBase):
    def test_three_share_cluster_two_distinct(self) -> None:
        # 3 session ids share skill=dev + final_state=tests_failed
        shared_ids = ["s-001", "s-002", "s-003"]
        # 2 mutually distinct (different skill OR different final_state)
        distinct_a = "s-004"  # different skill_name
        distinct_b = "s-005"  # different final_state

        grade_rows = [
            make_grade_row(sid, quality="poor", aggregate=0.3) for sid in shared_ids
        ]
        grade_rows.append(make_grade_row(distinct_a, quality="poor", aggregate=0.4))
        grade_rows.append(make_grade_row(distinct_b, quality="poor", aggregate=0.45))

        telemetry_rows = [
            make_telemetry_row(sid, skill_name="dev", final_state="tests_failed")
            for sid in shared_ids
        ]
        telemetry_rows.append(
            make_telemetry_row(distinct_a, skill_name="think", final_state="tests_failed")
        )
        telemetry_rows.append(
            make_telemetry_row(distinct_b, skill_name="dev", final_state="compile_error")
        )

        write_jsonl(self.grade, grade_rows)
        write_jsonl(self.telemetry, telemetry_rows)

        result = run_triage(self.grade, self.telemetry, self.output)
        self.assertEqual(result.returncode, 0, msg=f"stderr={result.stderr}")

        triage_rows = self.read_triage_rows()
        self.assertGreaterEqual(len(triage_rows), 1, "expected at least 1 cluster row")

        # Find a cluster whose member_session_ids equals exactly the 3-shared set
        target_set = set(shared_ids)
        matched = [
            r for r in triage_rows if set(r.get("member_session_ids", [])) == target_set
        ]
        self.assertEqual(
            len(matched),
            1,
            msg=(
                "expected exactly one cluster with the 3 shared sessions; "
                f"got triage rows={triage_rows}"
            ),
        )
        cluster = matched[0]
        # verify the 2 outliers do not leak into the 3-group cluster
        self.assertNotIn(distinct_a, cluster["member_session_ids"])
        self.assertNotIn(distinct_b, cluster["member_session_ids"])


# ---------------------------------------------------------------------------
# Test 2: Determinism — two runs identical bytes
# ---------------------------------------------------------------------------

class TestDeterminism(TriageClusterTestBase):
    def test_two_runs_byte_for_byte_identical(self) -> None:
        shared_ids = ["s-a", "s-b", "s-c"]
        grade_rows = [
            make_grade_row(sid, quality="poor", aggregate=0.3) for sid in shared_ids
        ]
        grade_rows.append(make_grade_row("s-d", quality="poor", aggregate=0.4))
        telemetry_rows = [
            make_telemetry_row(sid, skill_name="dev", final_state="tests_failed")
            for sid in shared_ids
        ]
        telemetry_rows.append(
            make_telemetry_row("s-d", skill_name="think", final_state="other_error")
        )
        write_jsonl(self.grade, grade_rows)
        write_jsonl(self.telemetry, telemetry_rows)

        r1 = run_triage(self.grade, self.telemetry, self.output)
        self.assertEqual(r1.returncode, 0, msg=f"stderr={r1.stderr}")
        first_bytes = self.output.read_bytes()

        r2 = run_triage(self.grade, self.telemetry, self.output)
        self.assertEqual(r2.returncode, 0, msg=f"stderr={r2.stderr}")
        second_bytes = self.output.read_bytes()

        self.assertEqual(
            first_bytes,
            second_bytes,
            "triage.jsonl must be byte-for-byte stable across runs",
        )


# ---------------------------------------------------------------------------
# Test 3: 5-dim severity present + severity_aggregate
# ---------------------------------------------------------------------------

class TestFiveDimSeverity(TriageClusterTestBase):
    def test_severity_dims_has_all_5_keys(self) -> None:
        rows = [
            make_grade_row("s-x1", quality="poor", aggregate=0.3),
            make_grade_row("s-x2", quality="poor", aggregate=0.35),
        ]
        tele = [
            make_telemetry_row("s-x1", skill_name="dev", final_state="tests_failed"),
            make_telemetry_row("s-x2", skill_name="dev", final_state="tests_failed"),
        ]
        write_jsonl(self.grade, rows)
        write_jsonl(self.telemetry, tele)

        result = run_triage(self.grade, self.telemetry, self.output)
        self.assertEqual(result.returncode, 0, msg=f"stderr={result.stderr}")

        triage_rows = self.read_triage_rows()
        self.assertGreaterEqual(len(triage_rows), 1)

        expected_dims = {
            "outcome_quality",
            "iteration_velocity",
            "scope_blast",
            "human_override_rate",
            "failure_recurrence",
        }
        for r in triage_rows:
            self.assertIn("severity_dims", r)
            self.assertEqual(set(r["severity_dims"].keys()), expected_dims)
            self.assertIn("severity_aggregate", r)
            self.assertIsInstance(r["severity_aggregate"], (int, float))


# ---------------------------------------------------------------------------
# Test 4: Empty / non-poor input -> empty triage.jsonl (0 bytes)
# ---------------------------------------------------------------------------

class TestEmptyOrNonPoorInput(TriageClusterTestBase):
    def test_empty_grade_yields_empty_output(self) -> None:
        # Empty grade.jsonl
        self.grade.write_text("", encoding="utf-8")
        self.telemetry.write_text("", encoding="utf-8")

        result = run_triage(self.grade, self.telemetry, self.output)
        self.assertEqual(result.returncode, 0, msg=f"stderr={result.stderr}")

        self.assertTrue(self.output.exists(), "triage.jsonl should be written (empty)")
        self.assertEqual(
            self.output.read_bytes(), b"", "triage.jsonl must be 0 bytes for empty input"
        )

    def test_no_poor_verdicts_yields_empty_output(self) -> None:
        # All rows are good/excellent (no poor)
        rows = [
            make_grade_row("s-g1", quality="good", aggregate=0.8),
            make_grade_row("s-e1", quality="excellent", aggregate=0.9),
            make_grade_row("s-a1", quality="acceptable", aggregate=0.6),
        ]
        tele = [
            make_telemetry_row("s-g1"),
            make_telemetry_row("s-e1"),
            make_telemetry_row("s-a1"),
        ]
        write_jsonl(self.grade, rows)
        write_jsonl(self.telemetry, tele)

        result = run_triage(self.grade, self.telemetry, self.output)
        self.assertEqual(result.returncode, 0, msg=f"stderr={result.stderr}")
        self.assertTrue(self.output.exists())
        self.assertEqual(
            self.output.read_bytes(),
            b"",
            "triage.jsonl must be 0 bytes when no poor verdicts present",
        )


# ---------------------------------------------------------------------------
# Test 5: Schema compliance via jq -e
# ---------------------------------------------------------------------------

class TestSchemaCompliance(TriageClusterTestBase):
    def test_each_row_has_seven_required_keys(self) -> None:
        if shutil.which("jq") is None:
            raise unittest.SkipTest("jq not available on PATH")

        rows = [
            make_grade_row(f"s-k{i}", quality="poor", aggregate=0.3) for i in range(3)
        ]
        tele = [
            make_telemetry_row(f"s-k{i}", skill_name="dev", final_state="tests_failed")
            for i in range(3)
        ]
        write_jsonl(self.grade, rows)
        write_jsonl(self.telemetry, tele)

        result = run_triage(self.grade, self.telemetry, self.output)
        self.assertEqual(result.returncode, 0, msg=f"stderr={result.stderr}")

        # Each row must satisfy the schema-compliance jq filter.
        jq_filter = (
            'has("cluster_id") and has("member_session_ids") '
            'and has("severity_dims") and has("severity_aggregate") '
            'and has("escalate") and has("evidence_bundle") '
            'and has("attempt_count")'
        )
        # jq -e exits 1 if any value is null/false. Use stream mode (default).
        with self.output.open("r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                if not line.strip():
                    continue
                proc = subprocess.run(
                    ["jq", "-e", jq_filter],
                    input=line,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(
                    proc.returncode,
                    0,
                    msg=(
                        f"row {line_no} failed schema check: "
                        f"stdout={proc.stdout!r} stderr={proc.stderr!r} line={line!r}"
                    ),
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
