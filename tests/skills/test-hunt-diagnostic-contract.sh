#!/usr/bin/env bash
# CONTRACT-hunt-diagnostics.md A1–A11: structural pinning for the hunt
# diagnosis contract.  This test reads the shipped Markdown and deliberately
# mutates behavior while leaving nearby explanatory prose behind.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

python3 - "$ROOT" <<'PY'
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

root = Path(sys.argv[1])
hunt = (root / "plugins/baransu/skills/hunt/SKILL.md").read_text(encoding="utf-8")
case = (root / "plugins/baransu/skills/hunt/references/hunt-case-template.md").read_text(encoding="utf-8")
pauses = (root / "plugins/baransu/skills/hunt/references/loop-pauses.md").read_text(encoding="utf-8")


def fenced_after(text, heading):
    start = text.find(heading)
    if start < 0:
        raise AssertionError(f"missing heading {heading!r}")
    match = re.search(r"```\n(.*?)\n```", text[start:], re.S)
    if not match:
        raise AssertionError(f"missing fenced block after {heading!r}")
    return [line for line in match.group(1).splitlines() if line.strip()]


def schema_fields(lines, expected):
    found = []
    for line in lines:
        match = re.match(r"^([\u3400-\u9fff][\u3400-\u9fffA-Za-z0-9（）()—－ -]*)：", line)
        if match:
            found.append(match.group(1))
    if found != expected:
        raise AssertionError(f"field set/order/count changed: {found!r} != {expected!r}")


def reporter_program(command):
    match = re.fullmatch(
        r"唯讀命令：`bash -c '([^']*)' -- 'known-service\.service' '-15 min'`",
        command,
    )
    if not match:
        raise AssertionError("reporter command is not one constant bash -c program with positional data")
    return match.group(1)


def assert_hostile_targets_are_data(program):
    """Run the shipped inner program through fake systemd/jq binaries.

    Capturing argv as NUL-delimited bytes detects word splitting and shell
    parsing, including the actual newline hostile value.  Fake env/id mark a
    side-effect file if an interpolation regression evaluates either payload.
    """
    before = hashlib.sha256(program.encode()).hexdigest()
    projection_filter = (
        '{"timestamp": .__REALTIME_TIMESTAMP, "target": $target, '
        '"probe": .HUNT_PROBE, "event": .HUNT_EVENT, "result": .HUNT_RESULT}'
    )
    hostile_targets = ("'; env; #", "$(id)", "`id`", "\n", "--help")
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        fakebin = base / "bin"
        fakebin.mkdir()
        journal_args = base / "journalctl.argv"
        jq_args = base / "jq.argv"
        marker = base / "side-effect"
        scripts = {
            "journalctl": "#!/bin/sh\nprintf '%s\\0' \"$@\" > \"$JOURNAL_ARGS\"\nprintf '%s\\n' '{\"__REALTIME_TIMESTAMP\":\"1\",\"_SYSTEMD_UNIT\":\"safe.service\",\"HUNT_PROBE\":\"P1\",\"HUNT_EVENT\":\"E1\",\"HUNT_RESULT\":\"R1\",\"MESSAGE\":\"must-not-leak\"}'\n",
            "jq": "#!/bin/sh\nprintf '%s\\0' \"$@\" > \"$JQ_ARGS\"\ncat >/dev/null\nprintf '%s\\n' '{\"timestamp\":\"1\",\"target\":\"safe.service\",\"probe\":\"P1\",\"event\":\"E1\",\"result\":\"R1\"}'\n",
            "env": "#!/bin/sh\ntouch \"$MARKER\"\n",
            "id": "#!/bin/sh\ntouch \"$MARKER\"\n",
        }
        for name, body in scripts.items():
            path = fakebin / name
            path.write_text(body, encoding="utf-8")
            path.chmod(0o755)
        runtime_env = os.environ | {
            "PATH": str(fakebin) + os.pathsep + os.environ["PATH"],
            "JOURNAL_ARGS": str(journal_args),
            "JQ_ARGS": str(jq_args),
            "MARKER": str(marker),
        }
        for target in hostile_targets:
            result = subprocess.run(
                ["bash", "-c", program, "--", target, "-15 min"],
                env=runtime_env, text=True, capture_output=True, check=False,
            )
            if result.returncode != 0:
                raise AssertionError(f"hostile target failed shell program: {target!r}: {result.stderr}")
            argv = journal_args.read_bytes().split(b"\0")[:-1]
            unit_index = argv.index(b"-u")
            target_bytes = target.encode()
            if argv[unit_index + 1] != target_bytes or argv.count(target_bytes) != 1:
                raise AssertionError(f"hostile target was not exactly one -u argument: {target!r}, {argv!r}")
            if b"-o" not in argv or argv[argv.index(b"-o") + 1] != b"json" or b"--output-fields=__REALTIME_TIMESTAMP,_SYSTEMD_UNIT,HUNT_PROBE,HUNT_EVENT,HUNT_RESULT" not in argv or b"MESSAGE" in b"\0".join(argv):
                raise AssertionError("journalctl argv lost its structured-field allowlist")
            if marker.exists():
                raise AssertionError(f"hostile target executed a side-effect command: {target!r}")
            if hashlib.sha256(program.encode()).hexdigest() != before:
                raise AssertionError("hostile target rewrote the constant command program")
            if not jq_args.exists():
                raise AssertionError("reporter command did not invoke the field-projection jq stage")
            jq_argv = jq_args.read_bytes().split(b"\0")[:-1]
            expected_jq_argv = [
                b"-c", b"--arg", b"target", target_bytes, projection_filter.encode()
            ]
            if jq_argv != expected_jq_argv:
                raise AssertionError(
                    f"jq projection no longer selects exactly five fields: {jq_argv!r}"
                )
            returned = json.loads(result.stdout)
            if list(returned) != ["timestamp", "target", "probe", "event", "result"] or "MESSAGE" in returned:
                raise AssertionError("jq stage returned a field outside the five-field allowlist")


def validate(skill, template, pause_table):
    # A1/A2: Locate keeps every symptom, and confirmation/fixed states cannot
    # skip a mapping or explicit separate incident.
    required_skill = {
        "all symptoms": "every observed symptom is mapped to that causal chain or separated by an independent evidence citation",
        "confirmed gate": "an independent evidence citation proves the symptom does not share that chain",
        "operational confirmed gate": "an independent evidence citation proves a symptom belongs to another incident and the case file records that incident's id plus next action",
        "no label escape": "A label alone is not separation evidence; otherwise the symptom stays `pending`",
        "locate list": "**Observed symptoms**: List every reported or visible symptom",
        # A3/A4/A5: one active yes/no probe; a log-site group is one probe;
        # cross-confirmation is a later probe in another layer.
        "one active probe": "At most one probe may be active at any time",
        "single hypothesis": "all sites test the same yes/no hypothesis",
        "log group": "2–3 coordinated log sites",
        "cross-confirmation order": "close that first probe, then open one second, independent cross-confirmation probe",
        "layer exception": "sole same-layer exception is an observed failing test",
        "parallel inventory only": "never explore multiple hypothesis lines in parallel",
        # A6/A7/A10 reporter safety and exact evidence retention.
        "reporter unavailable": "### Reporter probe when local reproduction is unavailable",
        "runtime-specific example": "tested Linux systemd example, not a universal command",
        "hostile positional": "bind validated literal selectors through positional parameters",
        "hostile set": "`'; env; #`, `$(id)`, `` `id` ``, `<newline>`, and `--help`",
        "allowlist": "declare an exact minimal evidence allowlist for that hypothesis",
        "probe-specific allowlist": "other probe types choose their own minimal allowlist",
        "redacted RED": "A RED quotation must be one redacted line made only from that probe's allowlist",
        "no payload": "never a copied raw log/object/payload",
        "structured fields": "--output-fields=__REALTIME_TIMESTAMP,_SYSTEMD_UNIT,HUNT_PROBE,HUNT_EVENT,HUNT_RESULT",
        "fixed token fields": "must be predeclared fixed tokens/enums, never data-derived values",
        "structured fallback": "If it cannot, do not dump a log line: use the Handoff format instead",
        # A8: reporter wait has one Input row and the exact handoff outcome.
        "reporter outcome": "LOOP_OUTCOME: no progress: reporter probe result required",
    }
    for name, anchor in required_skill.items():
        if anchor not in skill:
            raise AssertionError(f"{name}: missing behavioral anchor")

    reporter = fenced_after(skill, "### Reporter probe when local reproduction is unavailable")
    labels = [line.split("：", 1)[0] for line in reporter]
    expected_labels = ["診斷目的", "唯讀命令", "執行界限", "請回傳", "回傳前遮蔽"]
    if labels != expected_labels:
        raise AssertionError(f"reporter block labels/order/count changed: {labels!r}")
    command = reporter[1]
    for fragment in (
        "`bash -c '", "target=$1", "since=$2", " -- 'known-service.service' '-15 min'`",
        "--no-pager", "--since \"$since\"", "-u \"$target\"", "-n 80", "-o json",
        "--output-fields=__REALTIME_TIMESTAMP,_SYSTEMD_UNIT,HUNT_PROBE,HUNT_EVENT,HUNT_RESULT",
        "jq -c --arg target \"$target\"", "head -n 80",
    ):
        if fragment not in command:
            raise AssertionError(f"reporter command lost safe/bounded fragment {fragment!r}")
    if "MESSAGE" in command:
        raise AssertionError("reporter command must not request or emit MESSAGE")
    assert_hostile_targets_are_data(reporter_program(command))
    for fragment in ("target=known-service.service", "time=15 minutes", "work=80 journal records", "output=80 lines"):
        if fragment not in reporter[2]:
            raise AssertionError(f"reporter bounds missing {fragment!r}")
    if "僅 `timestamp`、`target`、`probe`、`event`、`result` 五個欄位；最多 80 行" != reporter[3].split("：", 1)[1]:
        raise AssertionError("reporter return allowlist or output cap changed")
    if "credential/token/cookie/PII/完整 payload/私人路徑" not in reporter[4]:
        raise AssertionError("reporter redaction categories changed")

    # A9/A11: parse the actual shipped fenced output blocks, not prose about them.
    schema_fields(fenced_after(skill, "### Success format"), ["根因", "修復", "確認方式", "測試矩陣", "迴歸守護"])
    schema_fields(fenced_after(skill, "### Handoff format (use after three hypothesis failures)"), ["症狀", "已測試的假說", "已蒐集的證據", "已排除的根因", "尚不知道的事", "建議下一步"])
    fast = re.search(r"Short-form case file: EXACTLY these five named sections — ([^.]+)\.", skill)
    if not fast or fast.group(1).split(" / ") != ["root cause", "fix", "確認方式", "迴歸守護", "blast verdicts"]:
        raise AssertionError("Fast Path five-section set/order/count changed")

    expected_headings = [
        "## 症狀", "## Before You Fix", "## 調查記錄", "## 根因分析", "## 修復",
        "## Scope Blast", "## 迴歸驗證", "## 診斷工具清理", "## 🎯HUNT-id Tag 格式參考",
    ]
    actual_headings = [line for line in template.splitlines() if line.startswith("## ")]
    if actual_headings != expected_headings:
        raise AssertionError(f"case-file top-level sections changed: {actual_headings!r}")
    for anchor in (
        "`causal-chain mapping`: pending | [因果鏈位置] | separate incident: [id / independent evidence citation / next action]",
        "a label without the citation remains `pending`",
        "Allowed field names: [exact minimal fields for this probe; the tested systemd reporter example uses `timestamp`, `target`, `probe`, `event`, `result`]",
        "values are redacted before this file; no complete object, payload, credential, token, cookie, PII, or private path",
    ):
        if anchor not in template:
            raise AssertionError(f"case-file evidence/symptom contract missing {anchor!r}")

    rows = [line for line in pause_table.splitlines() if line.startswith("| ")]
    reporter_rows = [line for line in rows if line.startswith("| Reporter probe —")]
    if len(reporter_rows) != 1 or "| Input |" not in reporter_rows[0] or "LOOP_OUTCOME: no progress: reporter probe result required" not in reporter_rows[0]:
        raise AssertionError("reporter-result Input PAUSE missing or malformed")
    if sum("| Input |" in line for line in rows) != 3:
        raise AssertionError("reporter pause did not add exactly one Input row")
    if sum("| **Authorization** |" in line for line in rows) != 2:
        raise AssertionError("reporter pause must not add an Authorization row")


validate(hunt, case, pauses)

# Mutation fixtures prove that behavior, not leftover explanatory prose, is pinned.
mutations = (
    ("partial symptom coverage", hunt.replace(
        "A root cause cannot become `confirmed`, 「已解決」, or 「已解決（附帶條件說明）」 until every observed symptom maps to its causal chain, or an independent evidence citation proves the symptom does not share that chain and the case file records a separate incident id plus next action. A label alone is not separation evidence; otherwise the symptom stays `pending`.",
        "A root cause may become `confirmed` after one symptom maps; any other symptom may be labeled as a separate incident without evidence.", 1), case, pauses),
    ("downstream label-only separation", hunt.replace(
        "an independent evidence citation proves a symptom belongs to another incident and the case file records that incident's id plus next action",
        "a symptom is explicitly labeled as another incident", 1), case, pauses),
    ("fake parallel probes", hunt.replace(
        "At most one probe may be active at any time",
        "One probe is the simple explanation for disciplined investigation", 1), case, pauses),
    ("ultracode parallel hypotheses", hunt.replace(
        "They may inform the next serialized probe, but never explore multiple hypothesis lines in parallel.",
        "They may explore multiple hypothesis lines in parallel.", 1), case, pauses),
    ("unsafe command interpolation/workload", hunt.replace(
        "target=$1; since=$2; journalctl --no-pager --since \"$since\" -u \"$target\" -n 80 -o json --output-fields=__REALTIME_TIMESTAMP,_SYSTEMD_UNIT,HUNT_PROBE,HUNT_EVENT,HUNT_RESULT",
        "journalctl -f -o json", 1), case, pauses),
    ("full-payload jq projection", hunt.replace(
        'jq -c --arg target "$target" "{\\"timestamp\\": .__REALTIME_TIMESTAMP, \\"target\\": \\$target, \\"probe\\": .HUNT_PROBE, \\"event\\": .HUNT_EVENT, \\"result\\": .HUNT_RESULT}"',
        'jq -c --arg target "$target" "."', 1), case, pauses),
    ("success extra schema field", hunt.replace(
        "迴歸守護：  [test file:line] + Scope Blast: HUNT-YYYY-NNN §N ｜ 或 [無，理由 + Scope Blast citation]",
        "迴歸守護：  [test file:line] + Scope Blast: HUNT-YYYY-NNN §N ｜ 或 [無，理由 + Scope Blast citation]\n新欄位：  [must fail]", 1), case, pauses),
    ("unredacted case evidence", hunt, case.replace(
        "values are redacted before this file; no complete object, payload, credential, token, cookie, PII, or private path",
        "Evidence uses the allowlist and keeps the diagnostic explanation", 1), pauses),
)
for name, bad_skill, bad_case, bad_pauses in mutations:
    # The mutation removes the operative rule while this prose remains.  A
    # keyword-only test would stay green here; the validator must not.
    if name == "unsafe command interpolation/workload":
        assert "The systemd example is one bounded, read-only command" in bad_skill
    try:
        validate(bad_skill, bad_case, bad_pauses)
    except AssertionError:
        continue
    raise AssertionError(f"mutation fixture stayed green: {name}")

print("GREEN: hunt diagnostic contract A1–A11 is structurally pinned")
PY
