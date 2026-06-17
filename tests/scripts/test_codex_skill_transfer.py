#!/usr/bin/env python3
"""Focused tests for codex-skill-transfer transfer.py behavior."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


THIS_FILE = Path(__file__).resolve()
REPO_ROOT = THIS_FILE.parents[2]
TRANSFER_PATH = (
    REPO_ROOT
    / "plugins"
    / "baransu"
    / "skills"
    / "codex-skill-transfer"
    / "scripts"
    / "transfer.py"
)

spec = importlib.util.spec_from_file_location("codex_skill_transfer", TRANSFER_PATH)
assert spec is not None and spec.loader is not None
transfer = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = transfer
spec.loader.exec_module(transfer)


def report() -> object:
    return transfer.TransferReport(
        skill_name="fixture",
        source=Path("source"),
        target=Path("target"),
    )


class TestBodyRewrite(unittest.TestCase):
    def test_multistage_subagent_dispatch_is_codex_worded(self):
        rpt = report()
        body = """Dispatch 3 subagents in parallel Tasks, each in a clean context.
Dispatch **review-agent** with:
Before dispatching review-agent for the current impl attempt.
Launch one **parallel Task** per activated perspective.
Run after all Stage 4 Tasks have returned.
launch the relevant inspector subagents in parallel via Task.
All Task Tools created before execution begins.
Record: Task Tool ID → group.
TaskCreate: status=pending
TaskUpdate: status=completed
"""

        out = transfer.rewrite_body(body, rpt)

        self.assertIn("Spawn 3 Codex subagents in parallel", out)
        self.assertIn("Spawn a `review-agent` subagent with:", out)
        self.assertIn(
            "Before spawning a `review-agent` subagent for the current impl attempt.",
            out,
        )
        self.assertIn("one **parallel Codex subagent** per", out)
        self.assertIn("Stage 4 Codex subagents have returned", out)
        self.assertIn("by spawning Codex subagents", out)
        self.assertIn("All `task-map.md` records created before execution begins.", out)
        self.assertIn("Record: `task-map.md` ID → group.", out)
        self.assertIn("create a `task-map.md` record: status=pending", out)
        self.assertIn("update `task-map.md` task state: status=completed", out)
        self.assertNotIn("parallel Tasks", out)
        self.assertNotIn("via Task", out)
        self.assertIn("Task tool", rpt.capability_risks)
        self.assertIn("TaskCreate", rpt.capability_risks)
        self.assertIn("TaskUpdate", rpt.capability_risks)

    def test_think_ask_user_becomes_alignment_artifact_gate(self):
        rpt = transfer.TransferReport(
            skill_name="think",
            source=Path("source"),
            target=Path("target"),
        )

        out = transfer.rewrite_body("Call AskUserQuestion before planning.", rpt)
        out = transfer.inject_codex_port_adapter(out, rpt)

        self.assertIn("Codex Port Adapter - Alignment Gate", out)
        self.assertIn("model's inertia to skip alignment", out)
        self.assertIn("require `alignment.md` before planning", out)
        self.assertIn("AskUserQuestion:think", rpt.capability_risks)
        self.assertEqual("artifact-gate", rpt.capability_risks["AskUserQuestion:think"].codex_level)

    def test_think_ask_user_occurrences_are_context_classified(self):
        rpt = transfer.TransferReport(
            skill_name="think",
            source=Path("source"),
            target=Path("target"),
        )
        body = """## Stage A — Alignment
Then call `AskUserQuestion` with options.

## Stage G — Approval
After the plan is presented, call `AskUserQuestion` with four options.

**Option 3 — 還有地方要對焦.** Call `AskUserQuestion` to find out what needs re-alignment.
"""

        out = transfer.rewrite_body(body, rpt)

        self.assertIn("Codex alignment gate requiring alignment.md", out)
        self.assertIn("authorization PAUSE", out)
        self.assertIn("input-alignment question PAUSE", out)
        self.assertIn("AskUserQuestion:think", rpt.capability_risks)
        self.assertIn("AskUserQuestion:authorization", rpt.capability_risks)
        self.assertIn("AskUserQuestion:input-gate", rpt.capability_risks)
        self.assertNotIn("`run the Codex alignment gate: output numbered alignment questions, stop, then require `alignment.md` before planning`", out)

    def test_cosmetic_ask_user_becomes_numbered_text_pause(self):
        rpt = transfer.TransferReport(
            skill_name="read",
            source=Path("source"),
            target=Path("target"),
        )

        out = transfer.rewrite_body("Call AskUserQuestion to choose a mode.", rpt)

        self.assertIn(
            "ask the user directly with numbered options, then stop for the user's reply",
            out,
        )
        self.assertIn("AskUserQuestion:cosmetic", rpt.capability_risks)
        self.assertEqual(
            "soft-prompt",
            rpt.capability_risks["AskUserQuestion:cosmetic"].codex_level,
        )

    def test_authorization_ask_user_remains_hard_pause(self):
        rpt = transfer.TransferReport(
            skill_name="review",
            source=Path("source"),
            target=Path("target"),
        )

        out = transfer.rewrite_body("Batch-ask via AskUserQuestion.", rpt)

        self.assertIn("record the authorization decision", out)
        self.assertIn("stop until the user answers", out)
        self.assertIn("AskUserQuestion:authorization", rpt.capability_risks)
        self.assertEqual(
            "hard-pause",
            rpt.capability_risks["AskUserQuestion:authorization"].codex_level,
        )

    def test_execute_adapter_requires_machine_gate_and_task_map(self):
        rpt = transfer.TransferReport(
            skill_name="execute",
            source=Path("source"),
            target=Path("target"),
        )

        out = transfer.inject_codex_port_adapter("# Execute\n\nBody.", rpt)

        self.assertIn("Codex Port Adapter - Machine Gates and Task Map", out)
        self.assertIn("actual command exit codes", out)
        self.assertIn("Model self-report is never green proof", out)
        self.assertIn("`task-map.md` as the durable source of truth", out)
        self.assertIn("test-runner", rpt.capability_risks)
        self.assertIn("TaskCreate", rpt.capability_risks)
        self.assertIn("TaskUpdate", rpt.capability_risks)

    def test_send_user_file_is_path_delivery(self):
        rpt = report()

        out = transfer.rewrite_body("Call SendUserFile with final-report.md.", rpt)

        self.assertIn("write the artifact to disk and list its absolute path", out)
        self.assertIn("SendUserFile", rpt.capability_risks)
        self.assertEqual("T3-1", rpt.capability_risks["SendUserFile"].tier)

    def test_tool_rewrites_do_not_break_inline_code_spans(self):
        rpt = transfer.TransferReport(
            skill_name="execute",
            source=Path("source"),
            target=Path("target"),
        )
        body = "Call `TaskUpdate status=completed`, `TaskCreate status=pending`, and `SendUserFile`."

        out = transfer.rewrite_body(body, rpt)

        self.assertIn("`update task-map.md task state status=completed`", out)
        self.assertIn("`create a task-map.md record status=pending`", out)
        self.assertIn("`write the artifact to disk and list its absolute path`", out)
        self.assertNotIn("`update `task-map.md`", out)
        self.assertNotIn("`create a `task-map.md`", out)

    def test_skill_dir_rewrite_preserves_executable_code_context(self):
        rpt = report()
        body = """In prose, mention $CLAUDE_SKILL_DIR as a location.
Run `bash "$CLAUDE_SKILL_DIR/../read/scripts/install-deps.sh"`.

```bash
HEALTH_SCRIPTS_DIR="${CLAUDE_SKILL_DIR:+$CLAUDE_SKILL_DIR/scripts}"
python3 "$CLAUDE_SKILL_DIR/references/hunt-search.py"
```
"""

        out = transfer.rewrite_body(body, rpt)

        self.assertIn("mention the skill's root directory as a location", out)
        self.assertIn('`bash "./../read/scripts/install-deps.sh"`', out)
        self.assertIn('HEALTH_SCRIPTS_DIR="./scripts"', out)
        self.assertIn('python3 "./references/hunt-search.py"', out)
        self.assertNotIn("the skill's root directory/../read", out)

    def test_argument_literals_inside_code_context_are_preserved(self):
        rpt = report()
        body = "Mapping docs mention `$ARGUMENTS`, `$ARGUMENTS[0]`, and `$1` literally."

        out = transfer.rewrite_body(body, rpt, positional_args=True)

        self.assertIn("`$ARGUMENTS`", out)
        self.assertIn("`$ARGUMENTS[0]`", out)
        self.assertIn("`$1`", out)

    def test_all_task_tokens_map_to_task_map_capabilities(self):
        cases = {
            "TaskCreate": "create a `task-map.md` record",
            "TaskUpdate": "update `task-map.md` task state",
            "TaskGet": "look up `task-map.md` task state",
            "TaskList": "list `task-map.md` records",
            "TaskOutput": "read task output recorded in `task-map.md`",
            "TaskStop": "mark the task stopped in `task-map.md`",
        }

        for token, expected in cases.items():
            with self.subTest(token=token):
                rpt = report()
                out = transfer.rewrite_body(f"Call {token}.", rpt)
                self.assertIn(expected, out)
                self.assertIn(token, rpt.capability_risks)

    def test_transfer_one_pipeline_injects_review_health_execute_adapters(self):
        cases = {
            "review": ("Codex Port Adapter - Review Isolation", "Task tool"),
            "health": ("Codex Port Adapter - Inspector Isolation", "Task tool"),
            "execute": ("Codex Port Adapter - Machine Gates and Task Map", "test-runner"),
        }

        for skill_name, (heading, capability) in cases.items():
            with self.subTest(skill_name=skill_name):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    source = root / skill_name
                    source.mkdir()
                    (source / "SKILL.md").write_text(
                        f"""---
name: {skill_name}
description: Fixture.
---

# {skill_name}

Body.
""",
                        encoding="utf-8",
                    )

                    rpt = transfer.transfer_one(source, root / "out")

                    out = (root / "out" / skill_name / "SKILL.md").read_text(encoding="utf-8")
                    self.assertIn(heading, out)
                    self.assertIn(capability, rpt.capability_risks)


class TestDescriptionRewrite(unittest.TestCase):
    def test_description_normalizes_claude_task_contexts(self):
        rpt = report()
        fm = {
            "name": "review",
            "description": (
                "Use When checking output. Do Dispatch isolated perspective agents "
                "in clean Task contexts."
            ),
        }

        out, _ = transfer.translate_frontmatter(fm, rpt)

        self.assertIn("Spawn isolated perspective agents", out["description"])
        self.assertIn("clean Codex subagent contexts", out["description"])
        self.assertTrue(
            any("description" in item and "Codex" in item for item in rpt.mapped),
            rpt.mapped,
        )


class TestCapabilityReport(unittest.TestCase):
    def test_weighted_capability_report_mentions_model_inertia(self):
        rpt = report()
        transfer.note_capability(rpt, "AskUserQuestion:think")
        transfer.note_capability(rpt, "AskUserQuestion:cosmetic")

        text = rpt.render()

        self.assertIn("Capability 降級風險 (weighted by model inertia)", text)
        self.assertLess(text.index("AskUserQuestion:think"), text.index("AskUserQuestion:cosmetic"))
        self.assertIn("strength=strong", text)
        self.assertIn("counters=skipping alignment", text)
        self.assertIn("T0-1", text)
        self.assertIn("T2-2", text)


class TestAgentStub(unittest.TestCase):
    def test_agent_stub_prefers_inheritance_with_current_codex_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "review-agent.md"
            dest = root / "review-agent.toml"
            src.write_text(
                """---
description: Review code.
tools: Read, Grep
---

# review-agent

Return concise findings.
""",
                encoding="utf-8",
            )

            transfer.emit_agent_stub(src, dest)
            text = dest.read_text(encoding="utf-8")

        self.assertIn("~/.codex/agents/review-agent.toml", text)
        self.assertIn(".codex/agents/review-agent.toml", text)
        self.assertIn('# model = "gpt-5.5"', text)
        self.assertIn("# model_reasoning_effort = \"high\"", text)
        self.assertIn("minimal | low | medium | high | xhigh", text)
        self.assertIn("# [[skills.config]]", text)
        self.assertIn("# mcp_servers = [\"Read\", \"Grep\"]", text)
        self.assertIn("omit optional fields to inherit", text)
        self.assertIn("read-only sandbox", text)

    def test_agent_stub_warns_for_write_and_bash_agents(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "impl-agent.md"
            dest = root / "impl-agent.toml"
            src.write_text(
                """---
description: Implement code.
tools: Read, Write, Edit, Bash
---

Implement a task.
""",
                encoding="utf-8",
            )

            transfer.emit_agent_stub(src, dest)
            text = dest.read_text(encoding="utf-8")

        self.assertIn("writes or runs shell commands", text)
        self.assertIn("workspace-write", text)
        self.assertIn("approval policy", text)


class TestReferenceScan(unittest.TestCase):
    def test_reference_scan_flags_claude_task_orchestration_tokens(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source"
            target = root / "target"
            refs = source / "references"
            refs.mkdir(parents=True)
            (source / "SKILL.md").write_text(
                """---
name: source
description: Fixture.
---

Body.
""",
                encoding="utf-8",
            )
            (refs / "orchestration.md").write_text(
                """Dispatch **review-agent** with:
Run stages in parallel Tasks via Task.
Call TaskCreate then TaskUpdate.
Call SendUserFile with the report.
""",
                encoding="utf-8",
            )
            target.mkdir()
            rpt = report()

            transfer.copy_aux(source, target, rpt)

        manual = "\n".join(rpt.manual_review)
        self.assertIn("parallel Tasks", manual)
        self.assertIn("via Task", manual)
        self.assertIn("TaskCreate", manual)
        self.assertIn("TaskUpdate", manual)
        self.assertIn("SendUserFile", manual)
        self.assertIn("Dispatch **agent**", manual)


class TestPluginModeGeneration(unittest.TestCase):
    def test_baransu_plugin_generation_includes_inertia_adapters(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "codex"

            reports, summary = transfer.transfer_plugin(REPO_ROOT / "plugins" / "baransu", output)

            self.assertEqual("baransu", summary["plugin_name"])
            self.assertGreaterEqual(len(reports), 13)
            plugin_out = output / "plugins" / "baransu"
            manifest = json.loads(
                (plugin_out / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
            )
            self.assertEqual("2.5.3", manifest["version"])

            codex_transfer = plugin_out / "skills" / "codex-skill-transfer"
            self.assertTrue((codex_transfer / "references" / "CODEX_PORT_PLAN.md").is_file())
            self.assertIn(
                "version: 0.10.0",
                (codex_transfer / "SKILL.md").read_text(encoding="utf-8"),
            )
            codex_transfer_skill = (codex_transfer / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("`$ARGUMENTS` → natural language", codex_transfer_skill)
            self.assertIn(
                "with `$placeholder` markers",
                codex_transfer_skill,
            )
            codex_skill_mapping = (
                codex_transfer / "references" / "skill-mapping.md"
            ).read_text(encoding="utf-8")
            self.assertIn("$CLAUDE_SKILL_DIR", codex_skill_mapping)
            self.assertNotIn("`.` → `.`", codex_skill_mapping)

            think = (plugin_out / "skills" / "think" / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("Codex Port Adapter - Alignment Gate", think)
            self.assertIn("alignment.md", think)
            self.assertIn("Phase 1", think)
            self.assertIn("Phase 2", think)

            review = (plugin_out / "skills" / "review" / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("Codex Port Adapter - Review Isolation", review)
            self.assertIn("codex-isolation-probe.md", review)
            self.assertIn("independent Codex invocation or session", review)
            self.assertIn("record the authorization decision", review)

            health = (plugin_out / "skills" / "health" / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("Codex Port Adapter - Inspector Isolation", health)
            self.assertIn("codex-isolation-probe.md", health)
            self.assertIn("independent Codex invocation or session", health)

            execute = (plugin_out / "skills" / "execute" / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("Codex Port Adapter - Machine Gates and Task Map", execute)
            self.assertIn("actual command exit codes", execute)
            self.assertIn("Model self-report is never green proof", execute)
            self.assertIn("`task-map.md` as the durable source of truth", execute)
            self.assertIn("create a `task-map.md` record", execute)
            self.assertIn("update `task-map.md` task state", execute)
            self.assertNotIn("create a task-tracking record", execute)

            learn = (plugin_out / "skills" / "learn" / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn('bash "./../read/scripts/install-deps.sh"', learn)
            self.assertNotIn("the skill's root directory/../read", learn)


if __name__ == "__main__":
    unittest.main()
