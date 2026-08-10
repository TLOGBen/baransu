#!/usr/bin/env bash
# Behavioral contract verifier for CONTRACT-distillation-matrix.md A1-A11.
# It parses the shipped admission behavior, then runs absence/misrouting
# mutations. A governing phrase alone is not accepted as a verifier.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

python3 - "$ROOT" <<'PY'
import re
import sys
from pathlib import Path

root = Path(sys.argv[1])
shared = (root / "plugins/baransu/skills/_shared/distillation-candidate-matrix.md").read_text(encoding="utf-8")
evolve = (root / "plugins/baransu/skills/evolve/SKILL.md").read_text(encoding="utf-8")
health = (root / "plugins/baransu/skills/health/references/conditional-audits.md").read_text(encoding="utf-8")
contract = (root / "plugins/baransu/skills/evolve/references/output-contract.md").read_text(encoding="utf-8")
failures = []

questions = (
    "Recurrence evidence",
    "Durable invariant",
    "Target layer",
    "Verifier",
    "Project/private contamination",
)
owners = ("project", "shared-skill", "global-rule", "private-memory")
dispositions = ("PROMOTE", "REROUTE", "DEFER", "REJECT")
label = "候選處置：{PROMOTE|REROUTE|DEFER|REJECT} — {一行理由}"
artifacts = (
    "log.md", "results.tsv", "convergence.svg", "held-out.md", "report.md",
    "card.html", "snapshot/<round>.md",
)
required_fields = (
    "start/end total score and per-dimension deltas",
    "dimensions improved, rounds run, convergence reason",
    "effectiveness_mode",
    "results.tsv` score source label",
    "held-out evidence-strength",
    "any untrusted real-exec runs flagged",
)


def fail(message):
    failures.append(message)


def section(text, heading, next_heading):
    try:
        return text.split(heading, 1)[1].split(next_heading, 1)[0]
    except IndexError:
        return ""


def question_rows(text):
    return [
        line for line in text.splitlines()
        if re.match(r"^\| (?:" + "|".join(re.escape(q) for q in questions) + r") \|", line)
    ]


def parse_question_table(text):
    block = section(text, "## Five questions\n", "## Disposition").strip().split("\n\n", 1)[0]
    lines = block.splitlines()
    if len(lines) != 7:
        return None
    if lines[0] != "| Question | Required decision evidence | Failed answer |":
        return None
    if not re.match(r"^\|[-| ]+\|$", lines[1]):
        return None
    rows = []
    for line in lines[2:]:
        match = re.match(r"^\| ([^|]+?) \| (.*?) \| (.*?) \|$", line)
        if not match:
            return None
        rows.append(match.groups())
    if tuple(row[0] for row in rows) != questions:
        return None
    return rows


def parse_dispositions(text):
    block = section(text, "## Disposition\n", "`REROUTE`, `DEFER`, and `REJECT`").strip()
    lines = [line for line in block.splitlines() if line.startswith("- ")]
    names = []
    for line in lines:
        match = re.match(r"^- `([^`]+)` —", line)
        if not match:
            return None
        names.append(match.group(1))
    return tuple(names)


def validate_shared(text):
    rows = parse_question_table(text)
    if rows is None:
        return False
    evidence = dict((question, answer) for question, answer, _ in rows)
    if tuple(re.findall(r"`([^`]+)`", evidence["Target layer"])) != owners:
        return False
    if parse_dispositions(text) != dispositions:
        return False
    verifier = evidence["Verifier"]
    recurrence = evidence["Recurrence evidence"]
    durable = evidence["Durable invariant"]
    contamination = evidence["Project/private contamination"]
    return (
        "Show either (a) independent cases across fixes, releases, agents, or user reports" in recurrence
        and "or (b) one reproducible failure plus a red-on-absence behavioral verifier" in recurrence
        and "Repeated wording in one conversation is one case, not recurrence" in recurrence
        and "State a stable rule rather than a dated incident summary" in durable
        and "Demonstrate red-on-absence evidence through a mutation or pre-fix failure" in verifier
        and "text-presence grep alone is not sufficient" in verifier
        and "Necessary project-specific facts select `project` and REROUTE" in contamination
        and "private user or machine facts select `private-memory` and REROUTE" in contamination
        and "Strip only candidates destined for public/shared guidance" in contamination
        and "cannot be separated, REJECT it" in contamination
        and text.count(label) == 1
    )


def has_single_authority(authority, evolve_text, health_text):
    return (
        validate_shared(authority)
        and not question_rows(evolve_text)
        and not question_rows(health_text)
    )


def stage0_steps(text):
    stage = section(text, "## Stage 0 — Target, slug, work dir\n", "### Orchestration interface")
    steps = re.findall(r"^(\d+)\. (.+)$", stage, re.M)
    return stage, tuple((int(number), body) for number, body in steps)


def valid_evolve_stage(text):
    stage, steps = stage0_steps(text)
    if tuple(number for number, _ in steps) != (1, 2, 3, 4, 5):
        return False
    resolve, gate, create, _, _ = (body for _, body in steps)
    return (
        resolve.startswith("Resolve the target SKILL.md path.")
        and gate.startswith("Only when the proposed candidate came from a conversation, incident, external repository or release log, or private memory")
        and "apply `../_shared/distillation-candidate-matrix.md` after target resolution and before any workdir, snapshot, panel, or report write" in gate
        and "Ordinary rubric wording or structure runs skip this gate and retain the existing flow." in gate
        and "Only `PROMOTE: shared-skill` with this exact resolved target may enter Stage 1." in gate
        and label in gate
        and "stop before durable writes" in gate
        and "never mutate another owner layer or add a package artifact or report field" in gate
        and create.startswith("Create `.claude/evolve/<slug>/` with a `snapshot/` subdir.")
        and "PAUSE" not in gate
    )


def health_guidance(text):
    return section(text, "## Conversation-derived guidance\n", "## Hotspot ownership gaps")


def valid_health_guidance(text):
    guidance = health_guidance(text)
    return (
        "Only when a deep health audit reads recent agent conversations" in guidance
        and "../../_shared/distillation-candidate-matrix.md" in guidance
        and label in guidance
        and "existing finding prose" in guidance
        and "do not add report fields" in guidance
        and "do not automatically write durable docs" in guidance
        and "`DEFER` and `REJECT` must not recommend writing durable docs" in guidance
        and "every off-ramp leaves other owner layers untouched" in guidance
        and "does not block local read-only conversation inspection or inspector dispatch" in guidance
        and not question_rows(guidance)
    )


def valid_output_contract(text):
    artifact_block = section(text, "## Artifacts\n", "## Human-readable delivery")
    field_block = text.split("## report.md required fields\n", 1)[1] if "## report.md required fields\n" in text else ""
    actual_artifacts = tuple(re.findall(r"^\| `([^`]+)` \|", artifact_block, re.M))
    return actual_artifacts == artifacts and all(field in field_block for field in required_fields)


# A1-A5: exact one shared authority and a behaviorally enforceable verifier.
if not validate_shared(shared):
    fail("shared matrix does not carry the exact five-question authority")
if not has_single_authority(shared, evolve, health):
    fail("five-question matrix is duplicated outside the shared authority")
if "../_shared/distillation-candidate-matrix.md" not in evolve:
    fail("evolve does not point to the shared authority")
if "../../_shared/distillation-candidate-matrix.md" not in health:
    fail("health does not point to the shared authority")
if any(text.count(label) != 1 or "Candidate disposition:" in text for text in (shared, evolve, health)):
    fail("user-facing disposition is not the exact Traditional-Chinese contract")

# A6-A9: the numbered Stage 0 order is target resolution -> candidate gate ->
# Create workdir; health is deep-conversation-only and never writes durable docs.
if not valid_evolve_stage(evolve):
    fail("evolve Stage 0 is not the required numbered admission sequence")
if not valid_health_guidance(health):
    fail("health conversation path is not a no-write off-ramp")

# A10-A11: parse the authoritative artifact rows and required-field bullets,
# then prove that deleting any shipped required item turns this validator red.
if not valid_output_contract(contract):
    fail("output-contract artifact set or required fields drifted")
artifact_start = contract.index("## Artifacts")
artifact_end = contract.index("## Human-readable delivery")
fields_start = contract.index("## report.md required fields")
for anchor in artifacts:
    row_anchor = f"| `{anchor}` |"
    mutated = contract[:artifact_start] + contract[artifact_start:artifact_end].replace(row_anchor, "| `REMOVED` |", 1) + contract[artifact_end:]
    if valid_output_contract(mutated):
        fail(f"mutation accepted deleted output-contract artifact {anchor!r}")
for anchor in required_fields:
    mutated = contract[:fields_start] + contract[fields_start:].replace(anchor, "REMOVED", 1)
    if valid_output_contract(mutated):
        fail(f"mutation accepted deleted report required field {anchor!r}")

# Mutation fixtures prove the parser rejects an extra question, owner, or
# disposition, a copied matrix, and the absence/misrouting behaviors above.
extra_question = shared.replace("\n\nThe verifier is orthogonal", "\n| Extra question | extra | extra |\n\nThe verifier is orthogonal", 1)
if validate_shared(extra_question):
    fail("mutation accepted an extra matrix question row")
extra_owner = shared.replace("`private-memory`", "`private-memory`, `extra-owner`", 1)
if validate_shared(extra_owner):
    fail("mutation accepted an extra owner item")
extra_disposition = shared.replace("\n`REROUTE`, `DEFER`, and `REJECT`", "\n- `EXTRA` — extra disposition\n\n`REROUTE`, `DEFER`, and `REJECT`", 1)
if validate_shared(extra_disposition):
    fail("mutation accepted an extra disposition item")
duplicated_health = health + "\n" + section(shared, "## Five questions\n", "## Disposition")
if has_single_authority(shared, evolve, duplicated_health):
    fail("mutation accepted a duplicated matrix")
missing_red_evidence = shared.replace("Demonstrate red-on-absence evidence through a mutation or pre-fix failure", "Name a verifier", 1)
if validate_shared(missing_red_evidence):
    fail("mutation accepted verifier wording without red-on-absence evidence")
missing_independent_recurrence = shared.replace(
    "Repeated wording in one conversation is one case, not recurrence.",
    "Repeated wording in one conversation counts as recurrence.", 1,
)
if validate_shared(missing_independent_recurrence):
    fail("mutation accepted same-conversation repetition as independent recurrence")
missing_reproducible_alternative = shared.replace(
    "or (b) one reproducible failure plus a red-on-absence behavioral verifier.",
    "and no reproducible-failure alternative is allowed.", 1,
)
if validate_shared(missing_reproducible_alternative):
    fail("mutation removed the reproducible-failure evidence route")
missing_durable_invariant = shared.replace(
    "State a stable rule rather than a dated incident summary.",
    "Keep the dated incident summary.", 1,
)
if validate_shared(missing_durable_invariant):
    fail("mutation accepted a dated incident as a durable invariant")

stage, steps = stage0_steps(evolve)
gate = steps[1][1]
create = steps[2][1]
moved_gate = evolve.replace(f"2. {gate}\n3. {create}", f"2. {create}\n3. {gate}", 1)
if valid_evolve_stage(moved_gate):
    fail("mutation accepted candidate gate after Create workdir")
missing_promote_gate = evolve.replace("Only `PROMOTE: shared-skill` with this exact resolved target may enter Stage 1.", "", 1)
if valid_evolve_stage(missing_promote_gate):
    fail("mutation accepted missing PROMOTE-only gate")
ordinary_blocked = evolve.replace("Ordinary rubric wording or structure runs skip this gate and retain the existing flow.", "Ordinary rubric wording or structure runs must pass this gate.", 1)
if valid_evolve_stage(ordinary_blocked):
    fail("mutation accepted ordinary-run blocking")
missing_health_no_write = health.replace("do not automatically write durable docs", "may automatically write durable docs", 1)
if valid_health_guidance(missing_health_no_write):
    fail("mutation accepted health auto-write")
missing_health_off_ramp = health.replace("every off-ramp leaves other owner layers untouched", "off-ramps may write another owner layer", 1)
if valid_health_guidance(missing_health_off_ramp):
    fail("mutation accepted health off-ramp mutation")

if failures:
    print("RED: distillation candidate matrix contract failed")
    for failure in failures:
        print(f"  - {failure}")
    raise SystemExit(1)
print("GREEN: exact shared matrix, red-on-absence verifier evidence, numbered evolve gate, health no-write off-ramp, and immutable output schema hold")
PY
