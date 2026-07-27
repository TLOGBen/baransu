#!/usr/bin/env python3
"""Focused tests for codex-skill-transfer transfer.py behavior."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
import tempfile
import tomllib
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

    def test_noun_phrase_mentions_get_plain_noun_no_stop_imperative(self):
        # Negated/noun-phrase mentions must never receive the call-site
        # rewrite's "(stop; ...)" imperative — a mid-sentence stop instruction
        # inside a "never gated" sentence inverts the invariant.
        for skill_name, body, expected in [
            (
                "health",
                "Fan-out is released unconditionally — it is never gated "
                "behind an AskUserQuestion proxy.",
                "never gated behind a user-question proxy",
            ),
            (
                "evolve",
                "The fan-out uses 0 AskUserQuestion calls.",
                "uses 0 user-question calls",
            ),
            (
                "think",
                "Ask exactly ONE AskUserQuestion round in 繁體中文.",
                "ONE user-question round",
            ),
            (
                "book",
                "0 results triggers an AskUserQuestion block.",
                "triggers a user-question block",
            ),
        ]:
            with self.subTest(skill_name=skill_name):
                rpt = transfer.TransferReport(
                    skill_name=skill_name,
                    source=Path("source"),
                    target=Path("target"),
                )
                out = transfer.rewrite_body(body, rpt)
                self.assertIn(expected, out)
                self.assertNotIn("(stop", out)
                self.assertNotIn("AskUserQuestion", out)

    def test_descriptive_skills_fall_back_to_plain_noun_not_unclassified(self):
        # evolve/health are mapped descriptive-only: even a bare
        # occurrence outside the noun-phrase shapes must not inherit the
        # unclassified "(stop; ...)" rewrite.
        for skill_name in ("evolve", "health"):
            with self.subTest(skill_name=skill_name):
                rpt = transfer.TransferReport(
                    skill_name=skill_name,
                    source=Path("source"),
                    target=Path("target"),
                )
                out = transfer.rewrite_body("Mentions AskUserQuestion here.", rpt)
                self.assertIn("a user-question prompt", out)
                self.assertNotIn("(stop", out)

    def test_hunt_no_longer_carries_a_dead_registry_entry(self):
        # hunt contains no AskUserQuestion any more; the stale input-gate map
        # entry was removed, so hunt falls to unclassified like other skills.
        self.assertNotIn("hunt", transfer.ASK_USER_CAPABILITY_BY_SKILL)

    def test_cosmetic_ask_user_becomes_numbered_text_pause(self):
        rpt = transfer.TransferReport(
            skill_name="read",
            source=Path("source"),
            target=Path("target"),
        )

        out = transfer.rewrite_body("Call AskUserQuestion to choose a mode.", rpt)

        self.assertIn(
            "direct user question with numbered options (stop for the user's reply)",
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

    def test_analyze_adapter_requires_machine_gate_and_task_map(self):
        rpt = transfer.TransferReport(
            skill_name="analyze",
            source=Path("source"),
            target=Path("target"),
        )

        out = transfer.inject_codex_port_adapter("# Analyze\n\nBody.", rpt)

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
            skill_name="analyze",
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

    def test_transfer_one_pipeline_injects_review_health_analyze_adapters(self):
        cases = {
            "review": ("Codex Port Adapter - Review Isolation", "Task tool"),
            "health": ("Codex Port Adapter - Inspector Isolation", "Task tool"),
            "analyze": ("Codex Port Adapter - Machine Gates and Task Map", "test-runner"),
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

    def test_transfer_one_flags_plugin_root_in_skill_body_without_rewriting_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "delegate"
            source.mkdir()
            (source / "SKILL.md").write_text(
                """---
name: delegate
description: Fixture.
---

Read `${CLAUDE_PLUGIN_ROOT}/agents/reviewer.md` before delegating.
""",
                encoding="utf-8",
            )

            rpt = transfer.transfer_one(source, root / "out")

            generated = (root / "out" / "delegate" / "SKILL.md").read_text(
                encoding="utf-8"
            )
            manual = "\n".join(rpt.manual_review)
            self.assertIn("${CLAUDE_PLUGIN_ROOT}/agents/reviewer.md", generated)
            self.assertIn("`SKILL.md`", manual)
            self.assertIn("CLAUDE_PLUGIN_ROOT", manual)


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

    def test_description_output_dir_path_rewritten(self):
        rpt = report()
        fm = {
            "name": "ship",
            "description": "Archives working dirs under .claude/ into .claude/archived/.",
        }

        out, _ = transfer.translate_frontmatter(fm, rpt)

        self.assertIn(".codex/archived/", out["description"])
        self.assertNotIn(".claude/", out["description"])


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
        self.assertIn("### Next-port follow-ups", text)
        self.assertIn("- none", text)

    def test_followups_classify_dropped_and_manual_items(self):
        rpt = report()
        rpt.dropped.append("unsupported source field")
        rpt.manual_review.append("reference still needs a Codex mapping")

        text = rpt.render()

        self.assertIn("unsupported source field — `accept-as-lossy`", text)
        self.assertIn(
            "reference still needs a Codex mapping — `refresh-mapping`", text
        )


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
        self.assertIn('# model = "gpt-5.6"', text)
        self.assertIn("gpt-5.6-terra", text)
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

    def test_bundled_agent_definition_is_runtime_consumable_and_package_local(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "impl-agent.md"
            dest = root / "impl-agent.toml"
            src.write_text(
                """---
description: Implement from the exact contract.
tools: Read, Write, Edit, Bash
---

Read `${CLAUDE_PLUGIN_ROOT}/skills/_shared/tdd.md` and `CLAUDE.md`.
Dispatch through the Task tool only when required.
""",
                encoding="utf-8",
            )

            transfer.emit_bundled_agent_definition(src, dest)
            text = dest.read_text(encoding="utf-8")
            parsed = tomllib.loads(text)

        self.assertEqual("impl-agent", parsed["name"])
        self.assertEqual(
            "Implement from the exact contract.", parsed["description"]
        )
        instructions = parsed["developer_instructions"]
        self.assertIn("../skills/_shared/tdd.md", instructions)
        self.assertIn("AGENTS.md", instructions)
        self.assertNotIn("CLAUDE_PLUGIN_ROOT", instructions)
        self.assertNotIn("Task tool", instructions)


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

    def test_reference_scan_flags_plugin_root_without_rewriting_it(self):
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
            original = (
                "Read `${CLAUDE_PLUGIN_ROOT}/agents/reviewer.md` before delegating.\n"
            )
            (refs / "delegation.md").write_text(original, encoding="utf-8")
            target.mkdir()
            rpt = report()

            transfer.copy_aux(source, target, rpt)

            copied = (target / "references" / "delegation.md").read_text(
                encoding="utf-8"
            )
            manual = "\n".join(rpt.manual_review)
            self.assertEqual(original, copied)
            self.assertIn("`references/delegation.md`", manual)
            self.assertIn("CLAUDE_PLUGIN_ROOT", manual)


class TestCopyAuxExclusions(unittest.TestCase):
    def test_copy_aux_preserves_evals_as_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source"
            target = root / "target"
            evals = source / "evals"
            evals.mkdir(parents=True)
            payload = b'{"prompt":"literal CLAUDE.md example"}\n'
            (evals / "evals.json").write_bytes(payload)
            target.mkdir()
            rpt = report()

            transfer.copy_aux(source, target, rpt)

            self.assertEqual(payload, (target / "evals" / "evals.json").read_bytes())
            self.assertNotIn("evals/", "\n".join(rpt.dropped))

    def test_copy_aux_excludes_node_modules_and_pycache(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source"
            target = root / "target"
            scripts = source / "scripts"
            (scripts / "node_modules" / "pkg").mkdir(parents=True)
            (scripts / "node_modules" / "pkg" / "index.js").write_text(
                "module.exports = {};\n", encoding="utf-8"
            )
            (scripts / "__pycache__").mkdir()
            (scripts / "__pycache__" / "mod.cpython-312.pyc").write_bytes(b"\x00")
            (scripts / "run.sh").write_text("echo ok\n", encoding="utf-8")
            target.mkdir()
            rpt = report()

            transfer.copy_aux(source, target, rpt)

            self.assertTrue((target / "scripts" / "run.sh").is_file())
            self.assertFalse((target / "scripts" / "node_modules").exists())
            self.assertFalse((target / "scripts" / "__pycache__").exists())


def write_stub_skill(source: Path, name: str) -> None:
    source.mkdir(parents=True, exist_ok=True)
    (source / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: Fixture.\n---\n\n# {name}\n\nBody.\n",
        encoding="utf-8",
    )


class TestOutputGuard(unittest.TestCase):
    def test_transfer_one_refuses_nonempty_unmarked_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "alpha"
            write_stub_skill(source, "alpha")
            out = root / "out"
            unrelated = out / "alpha"
            unrelated.mkdir(parents=True)
            (unrelated / "precious.txt").write_text("keep me\n", encoding="utf-8")

            with self.assertRaises(transfer.OutputGuardError):
                transfer.transfer_one(source, out)
            # The unrelated content survived the refusal.
            self.assertTrue((unrelated / "precious.txt").is_file())

    def test_transfer_one_overwrites_previously_generated_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "alpha"
            write_stub_skill(source, "alpha")
            out = root / "out"

            first = transfer.transfer_one(source, out)
            self.assertFalse(first.skipped)
            second = transfer.transfer_one(source, out)  # marker: SKILL.md
            self.assertFalse(second.skipped)
            self.assertTrue((out / "alpha" / "SKILL.md").is_file())

    def test_transfer_plugin_refuses_nonempty_unmarked_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plugin = root / "plug"
            (plugin / ".claude-plugin").mkdir(parents=True)
            (plugin / ".claude-plugin" / "plugin.json").write_text(
                json.dumps({"name": "plug", "version": "1.0.0"}), encoding="utf-8"
            )
            write_stub_skill(plugin / "skills" / "alpha", "alpha")
            out = root / "existing"
            out.mkdir()
            (out / "precious.txt").write_text("keep me\n", encoding="utf-8")

            with self.assertRaises(transfer.OutputGuardError):
                transfer.transfer_plugin(plugin, out)
            self.assertTrue((out / "precious.txt").is_file())

    def test_transfer_plugin_rerun_into_marked_output_succeeds(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plugin = root / "plug"
            (plugin / ".claude-plugin").mkdir(parents=True)
            (plugin / ".claude-plugin" / "plugin.json").write_text(
                json.dumps({"name": "plug", "version": "1.0.0"}), encoding="utf-8"
            )
            write_stub_skill(plugin / "skills" / "alpha", "alpha")
            out = root / "codex"

            transfer.transfer_plugin(plugin, out)  # writes the marker
            reports, summary = transfer.transfer_plugin(plugin, out)  # rerun
            self.assertEqual(1, summary["skill_count"])
            self.assertEqual(1, len(reports))


class TestBatchSkipReport(unittest.TestCase):
    def test_batch_child_without_skill_md_yields_skipped_report(self):
        import contextlib
        import io

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            batch = root / "batch"
            write_stub_skill(batch / "alpha", "alpha")
            (batch / "_shared").mkdir()
            (batch / "_shared" / "notes.md").write_text("shared\n", encoding="utf-8")
            out = root / "out"

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                rc = transfer.main(["transfer.py", str(batch), str(out)])

            self.assertEqual(0, rc)
            printed = stdout.getvalue()
            self.assertIn("處理 2 個 skill", printed)
            self.assertIn("_shared", printed)
            self.assertIn("no SKILL.md in source", printed)
            # The skipped child produced no partial output.
            self.assertFalse((out / "_shared").exists())
            self.assertTrue((out / "alpha" / "SKILL.md").is_file())


class TestAuxDirScan(unittest.TestCase):
    def test_shared_aux_dirs_are_token_scanned_and_flagged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plugin = root / "plug"
            (plugin / ".claude-plugin").mkdir(parents=True)
            (plugin / ".claude-plugin" / "plugin.json").write_text(
                json.dumps({"name": "plug", "version": "1.0.0"}), encoding="utf-8"
            )
            write_stub_skill(plugin / "skills" / "alpha", "alpha")
            shared = plugin / "skills" / "_shared"
            shared.mkdir()
            (shared / "loop-contract.md").write_text(
                "Typically an AskUserQuestion. Dispatch via Task tool.\n",
                encoding="utf-8",
            )
            (shared / "plain.md").write_text("nothing Claude-only here\n", encoding="utf-8")
            out = root / "codex"

            _, summary = transfer.transfer_plugin(plugin, out)

            aux_manual = "\n".join(summary["aux_manual"])
            self.assertIn("loop-contract.md", aux_manual)
            self.assertIn("AskUserQuestion", aux_manual)
            self.assertIn("Task tool", aux_manual)
            self.assertNotIn("plain.md", aux_manual)
            # Flag only — the copied file itself is never rewritten.
            copied = (out / "plugins" / "plug" / "skills" / "_shared" / "loop-contract.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("AskUserQuestion", copied)


class TestPluginModeGeneration(unittest.TestCase):
    def _write_plugin_fixture(self, root: Path, manifest: dict | None = None) -> Path:
        plugin = root / "plug"
        (plugin / ".claude-plugin").mkdir(parents=True)
        (plugin / ".claude-plugin" / "plugin.json").write_text(
            json.dumps(manifest or {"name": "plug", "version": "1.0.0"}),
            encoding="utf-8",
        )
        write_stub_skill(plugin / "skills" / "alpha", "alpha")
        return plugin

    def test_plugin_without_hooks_does_not_emit_hook_surface(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plugin = self._write_plugin_fixture(root)
            out = root / "codex"

            transfer.transfer_plugin(plugin, out)

            plugin_out = out / "plugins" / "plug"
            manifest = json.loads(
                (plugin_out / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
            )
            self.assertNotIn("hooks", manifest)
            self.assertFalse((plugin_out / "hooks").exists())

    def test_plugin_hooks_are_ported_without_inventing_session_end(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plugin = root / "plug"
            (plugin / ".claude-plugin").mkdir(parents=True)
            (plugin / ".claude-plugin" / "plugin.json").write_text(
                json.dumps({"name": "plug", "version": "1.0.0"}), encoding="utf-8"
            )
            write_stub_skill(plugin / "skills" / "alpha", "alpha")
            hooks = plugin / "hooks"
            hooks.mkdir()
            (hooks / "guard.sh").write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            (hooks / "hooks.json").write_text(
                json.dumps(
                    {
                        "description": "fixture hooks",
                        "hooks": {
                            "SessionEnd": [
                                {"hooks": [{"type": "command", "command": "echo end"}]}
                            ],
                            "Stop": [
                                {
                                    "hooks": [
                                        {
                                            "type": "command",
                                            "command": (
                                                'ROOT="${CLAUDE_PLUGIN_ROOT}" '
                                                'DATA="${CLAUDE_PLUGIN_DATA}" '
                                                'bash "$ROOT/hooks/guard.sh"'
                                            ),
                                            "timeout": 10,
                                        }
                                    ]
                                }
                            ],
                        },
                    }
                ),
                encoding="utf-8",
            )

            out = root / "codex"
            _, summary = transfer.transfer_plugin(plugin, out)
            plugin_out = out / "plugins" / "plug"
            manifest = json.loads(
                (plugin_out / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
            )
            self.assertEqual("./hooks/hooks.json", manifest["hooks"])
            self.assertTrue((plugin_out / "hooks" / "guard.sh").is_file())
            hook_doc = json.loads(
                (plugin_out / "hooks" / "hooks.json").read_text(encoding="utf-8")
            )
            self.assertNotIn("SessionEnd", hook_doc["hooks"])
            self.assertEqual(10, hook_doc["hooks"]["Stop"][0]["hooks"][0]["timeout"])
            command = hook_doc["hooks"]["Stop"][0]["hooks"][0]["command"]
            self.assertIn("${PLUGIN_ROOT}", command)
            self.assertIn("${PLUGIN_DATA}", command)
            self.assertNotIn("CLAUDE_PLUGIN_ROOT", command)
            self.assertNotIn("CLAUDE_PLUGIN_DATA", command)
            mapped = "\n".join(summary["manifest_mapped"])
            self.assertIn("2 處 Claude plugin env", mapped)
            manual = "\n".join(summary["manifest_manual"])
            self.assertIn("不支援事件：SessionEnd", manual)
            self.assertIn("/hooks", manual)
            self.assertIn("trust", manual)
            self.assertNotIn("預設關閉", manual)

    def test_plugin_hook_drops_non_command_handler(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plugin = root / "plug"
            (plugin / ".claude-plugin").mkdir(parents=True)
            (plugin / ".claude-plugin" / "plugin.json").write_text(
                json.dumps({"name": "plug", "version": "1.0.0"}), encoding="utf-8"
            )
            write_stub_skill(plugin / "skills" / "alpha", "alpha")
            hooks = plugin / "hooks"
            hooks.mkdir()
            (hooks / "hooks.json").write_text(
                json.dumps(
                    {
                        "hooks": {
                            "Stop": [
                                {
                                    "hooks": [
                                        {"type": "prompt", "prompt": "check it"},
                                        {"type": "command", "command": "true"},
                                    ]
                                }
                            ]
                        }
                    }
                ),
                encoding="utf-8",
            )

            out = root / "codex"
            _, summary = transfer.transfer_plugin(plugin, out)
            hook_doc = json.loads(
                (out / "plugins" / "plug" / "hooks" / "hooks.json").read_text(
                    encoding="utf-8"
                )
            )
            handlers = hook_doc["hooks"]["Stop"][0]["hooks"]
            self.assertEqual(["command"], [handler["type"] for handler in handlers])
            self.assertIn(
                "不支援 handler：Stop/prompt", "\n".join(summary["manifest_manual"])
            )

    def test_malformed_hook_shapes_are_reported_without_crashing(self):
        cases = [
            ("not-json", "{", "無法解析"),
            ("hooks-not-object", json.dumps({"hooks": []}), "`hooks` 必須是 object"),
            (
                "groups-not-array",
                json.dumps({"hooks": {"Stop": {}}}),
                "event `Stop` 不是 array",
            ),
            (
                "group-not-object",
                json.dumps({"hooks": {"Stop": ["bad"]}}),
                "event `Stop` 含非 object matcher group",
            ),
            (
                "handlers-not-array",
                json.dumps({"hooks": {"Stop": [{"hooks": {}}]}}),
                "event `Stop` 的 handler 列表不是 array",
            ),
        ]
        for label, hook_text, expected in cases:
            with self.subTest(label=label), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                plugin = self._write_plugin_fixture(root)
                hooks = plugin / "hooks"
                hooks.mkdir()
                (hooks / "hooks.json").write_text(hook_text, encoding="utf-8")
                out = root / "codex"

                _, summary = transfer.transfer_plugin(plugin, out)

                self.assertIn(expected, "\n".join(summary["manifest_manual"]))
                plugin_out = out / "plugins" / "plug"
                manifest = json.loads(
                    (plugin_out / ".codex-plugin" / "plugin.json").read_text(
                        encoding="utf-8"
                    )
                )
                self.assertNotIn("hooks", manifest)
                self.assertFalse((plugin_out / "hooks").exists())

    def test_manifest_only_hook_shape_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plugin = self._write_plugin_fixture(
                root,
                {"name": "plug", "version": "1.0.0", "hooks": "./custom/hooks.json"},
            )
            out = root / "codex"

            _, summary = transfer.transfer_plugin(plugin, out)

            self.assertIn(
                "自訂來源形狀需人工映射", "\n".join(summary["manifest_manual"])
            )
            manifest = json.loads(
                (out / "plugins" / "plug" / ".codex-plugin" / "plugin.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertNotIn("hooks", manifest)

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
            self.assertEqual("3.1.3", manifest["version"])

            codex_transfer = plugin_out / "skills" / "codex-skill-transfer"
            self.assertTrue((codex_transfer / "references" / "CODEX_PORT_PLAN.md").is_file())
            self.assertIn(
                # Re-pinned 0.14.1 -> 0.14.2: unresolved CLAUDE_PLUGIN_ROOT
                # tokens are surfaced without an unsafe automatic rewrite.
                "version: 0.14.2",
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
            self.assertIn(
                "Codex Port Adapter - Bundled Agent Resolution", review
            )
            self.assertIn("AGENT_DEFINITION_MISSING", review)
            self.assertIn("codex-isolation-probe.md", review)
            self.assertIn("independent Codex invocation or session", review)
            self.assertIn("record the authorization decision", review)

            health = (plugin_out / "skills" / "health" / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("Codex Port Adapter - Inspector Isolation", health)
            self.assertIn(
                "Codex Port Adapter - Bundled Agent Resolution", health
            )
            self.assertIn("codex-isolation-probe.md", health)
            self.assertIn("independent Codex invocation or session", health)

            analyze_out = (plugin_out / "skills" / "analyze" / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("Codex Port Adapter - Machine Gates and Task Map", analyze_out)
            self.assertIn(
                "Codex Port Adapter - Bundled Agent Resolution", analyze_out
            )
            self.assertIn("actual command exit codes", analyze_out)
            self.assertIn("Model self-report is never green proof", analyze_out)
            self.assertIn("`task-map.md` as the durable source of truth", analyze_out)
            pipeline_out = (
                plugin_out / "skills" / "analyze" / "references" / "execution-pipeline.md"
            ).read_text(encoding="utf-8")
            self.assertIn("task-map.md", pipeline_out)

            read_skill = (plugin_out / "skills" / "read" / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn('bash "./scripts/install-deps.sh"', read_skill)
            self.assertNotIn("the skill's root directory/scripts", read_skill)

            # Noun-phrase guard: no generated SKILL.md may carry a "(stop; ..."
            # imperative inside a "never gated" sentence — the whole point of
            # those sentences is that fan-out must NOT stop.
            for skill_md in sorted(plugin_out.glob("skills/*/SKILL.md")):
                text = skill_md.read_text(encoding="utf-8")
                for line in text.splitlines():
                    if "never gated" in line:
                        self.assertNotIn("(stop;", line, skill_md)
            self.assertIn("never gated behind a user-question proxy", health)
            evolve = (plugin_out / "skills" / "evolve" / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn(
                "Codex Port Adapter - Bundled Agent Resolution", evolve
            )
            self.assertIn("0 user-question calls", evolve)
            self.assertIn("never gated behind a user-question proxy", evolve)

            # Every Claude agent is a package-local runtime definition. Skills
            # reference those exact files; no install-time copy to user config
            # is required, and a missing file cannot degrade into improvisation.
            agent_defs = sorted((plugin_out / ".codex-agents").glob("*.toml"))
            self.assertEqual(17, len(agent_defs))
            self.assertEqual(17, summary["agent_definitions"])
            self.assertTrue(summary["content_closure_verified"])
            self.assertFalse((plugin_out / ".codex-agents-templates").exists())
            for agent_def in agent_defs:
                parsed = tomllib.loads(agent_def.read_text(encoding="utf-8"))
                self.assertTrue(parsed["developer_instructions"].strip(), agent_def)
                self.assertNotIn("CLAUDE.md", parsed["description"], agent_def)
                self.assertNotIn(
                    "CLAUDE_PLUGIN_ROOT", parsed["developer_instructions"], agent_def
                )

            for markdown in sorted((plugin_out / "skills").rglob("*.md")):
                if "codex-skill-transfer" in markdown.parts:
                    continue
                text = markdown.read_text(encoding="utf-8")
                refs = re.findall(
                    r"`([^`]*\\.codex-agents/[A-Za-z0-9_-]+\\.toml)`", text
                )
                for ref in refs:
                    resolved = (markdown.parent / ref).resolve()
                    self.assertTrue(
                        resolved.is_file(),
                        f"{markdown.relative_to(plugin_out)} -> {ref}",
                    )

            rules = (plugin_out / "rules" / "anti-patterns.md").read_text(
                encoding="utf-8"
            )
            self.assertEqual(1, summary["rules_copied"])
            self.assertIn("AGENTS.md", rules)
            self.assertIn("../skills/_shared/tdd.md", rules)
            self.assertNotIn("CLAUDE.md", rules)
            self.assertEqual([], summary["unhandled_components"])

            # Shared aux dirs are copied verbatim AND token-scanned: the real
            # _shared/loop-contract.md carries Claude-only tokens and must be
            # flagged for manual review, never rewritten.
            aux_manual = "\n".join(summary.get("aux_manual", []))
            self.assertIn("_shared", aux_manual)
            self.assertIn("loop-contract.md", aux_manual)
            self.assertIn(
                "AskUserQuestion",
                (plugin_out / "skills" / "_shared" / "loop-contract.md").read_text(
                    encoding="utf-8"
                ),
            )

    def test_content_closure_rejects_missing_bundled_agent(self):
        with tempfile.TemporaryDirectory() as tmp:
            plugin_out = Path(tmp) / "plugin"
            agents = plugin_out / ".codex-agents"
            skills = plugin_out / "skills" / "review"
            agents.mkdir(parents=True)
            skills.mkdir(parents=True)
            (agents / "reviewer.toml").write_text(
                'name = "reviewer"\ndescription = "review"\n'
                "developer_instructions = '''review'''\n",
                encoding="utf-8",
            )
            (skills / "SKILL.md").write_text(
                "Read `../../.codex-agents/missing.toml`.\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                transfer.OutputGuardError, "missing\\.toml is missing"
            ):
                transfer.validate_plugin_content_closure(
                    Path(tmp) / "source", plugin_out, ["reviewer"], 0
                )


class TestRepoPathRewrite(unittest.TestCase):
    def test_agent_ref_becomes_codex_agents_toml(self):
        rpt = report()
        out = transfer.rewrite_body(
            "See `plugins/baransu/agents/architecture-reviewer.md` for the lane.",
            rpt,
            skill_name="review",
        )
        self.assertIn("`../../.codex-agents/architecture-reviewer.toml`", out)
        self.assertNotIn("plugins/baransu/agents", out)

    def test_agent_glob_ref_keeps_glob(self):
        rpt = report()
        out = transfer.rewrite_body(
            "Rules live in `plugins/baransu/agents/*-reviewer.md`.",
            rpt,
            skill_name="review",
        )
        self.assertIn("`../../.codex-agents/*-reviewer.toml`", out)

    def test_shared_ref_becomes_relative_from_skill_root(self):
        rpt = report()
        out = transfer.rewrite_body(
            "Apply `plugins/baransu/skills/_shared/fact-check.md` here.",
            rpt,
            skill_name="review",
        )
        self.assertIn("`../_shared/fact-check.md`", out)
        self.assertNotIn("plugins/baransu/skills", out)

    def test_cross_skill_ref_becomes_relative(self):
        rpt = report()
        out = transfer.rewrite_body(
            "The rules are in `plugins/baransu/skills/design/scripts/check.py`.",
            rpt,
            skill_name="book",
        )
        self.assertIn("`../design/scripts/check.py`", out)

    def test_self_ref_is_stripped_to_skill_root(self):
        rpt = report()
        out = transfer.rewrite_body(
            'HEALTH_SCRIPTS_DIR="$REPO_ROOT/plugins/baransu/skills/health/scripts"',
            rpt,
            skill_name="health",
        )
        self.assertIn('HEALTH_SCRIPTS_DIR="scripts"', out)
        self.assertNotIn("plugins/baransu", out)

    def test_self_ref_depth_is_relative_to_the_file_not_skill_root(self):
        # A self-reference inside a deeper file (references/*.md, updots=../../)
        # must climb back to the skill root: `../scripts/...`, NOT a bare
        # `scripts/...` that would resolve from the file's own dir.
        out, _ = transfer.rewrite_repo_paths(
            "See `plugins/baransu/skills/health/scripts/run.sh`.", "../../", "health"
        )
        self.assertIn("`../scripts/run.sh`", out)
        # At the skill root (SKILL.md, updots=../) the same ref stays bare.
        out_root, _ = transfer.rewrite_repo_paths(
            "See `plugins/baransu/skills/health/scripts/run.sh`.", "../", "health"
        )
        self.assertIn("`scripts/run.sh`", out_root)
        self.assertNotIn("`../scripts/run.sh`", out_root)

    def test_claude_dir_becomes_codex_dir(self):
        rpt = report()
        out = transfer.rewrite_body(
            "Render to `.claude/review/x.html`; catalog at `.claude-plugin/marketplace.json`.",
            rpt,
            skill_name="review",
        )
        self.assertIn("`.codex/review/x.html`", out)
        # `.claude-plugin/` must NOT be caught by the `.claude/` rule.
        self.assertIn("`.claude-plugin/marketplace.json`", out)

    def test_plugin_json_ref_becomes_codex_plugin(self):
        rpt = report()
        out = transfer.rewrite_body(
            "Bump `plugins/baransu/.claude-plugin/plugin.json`.",
            rpt,
            skill_name="analyze",
        )
        self.assertIn("`.codex-plugin/plugin.json`", out)

    def test_exempt_skill_paths_untouched(self):
        rpt = report()
        body = "Example: `plugins/baransu/agents/x.md` and `.claude/review/`."
        out = transfer.rewrite_body(body, rpt, skill_name="codex-skill-transfer")
        self.assertEqual(out, body)

    def test_copy_aux_rewrites_reference_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source"
            target = root / "target"
            refs = source / "references"
            refs.mkdir(parents=True)
            (refs / "color.md").write_text(
                "Run `plugins/baransu/skills/_shared/scripts/color_distance.py` on it.\n",
                encoding="utf-8",
            )
            target.mkdir()
            rpt = report()

            transfer.copy_aux(source, target, rpt)

            out = (target / "references" / "color.md").read_text(encoding="utf-8")
            # references/*.md is two levels below skills/ -> ../../
            self.assertIn("`../../_shared/scripts/color_distance.py`", out)
            self.assertNotIn("plugins/baransu", out)

    def test_copy_aux_exempts_slide_checklist_only_for_design(self):
        original = "Bump `plugins/baransu/.claude-plugin/plugin.json` version.\n"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source"
            # Exemption is scoped to (design, references/slide-checklist.md).
            target = root / "design"
            refs = source / "references"
            refs.mkdir(parents=True)
            (refs / "slide-checklist.md").write_text(original, encoding="utf-8")
            target.mkdir()
            transfer.copy_aux(source, target, report())
            out = (target / "references" / "slide-checklist.md").read_text(
                encoding="utf-8"
            )
            self.assertEqual(out, original)

        # A same-named file under a DIFFERENT skill is NOT exempt.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source"
            target = root / "other"
            refs = source / "references"
            refs.mkdir(parents=True)
            (refs / "slide-checklist.md").write_text(original, encoding="utf-8")
            target.mkdir()
            transfer.copy_aux(source, target, report())
            out = (target / "references" / "slide-checklist.md").read_text(
                encoding="utf-8"
            )
            self.assertIn(".codex-plugin/plugin.json", out)

    def test_plugin_rewrites_shared_aux_dir_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plugin = root / "plug"
            (plugin / ".claude-plugin").mkdir(parents=True)
            (plugin / ".claude-plugin" / "plugin.json").write_text(
                json.dumps({"name": "plug", "version": "1.0.0"}), encoding="utf-8"
            )
            write_stub_skill(plugin / "skills" / "alpha", "alpha")
            shared = plugin / "skills" / "_shared"
            shared.mkdir(parents=True)
            (shared / "tdd.md").write_text(
                "Read `plugins/baransu/agents/impl-agent.md` and "
                "`plugins/baransu/skills/execute/SKILL.md`.\n",
                encoding="utf-8",
            )
            agents = plugin / "agents"
            agents.mkdir()
            (agents / "impl-agent.md").write_text(
                "---\ndescription: Implement.\n---\n\nImplement the task.\n",
                encoding="utf-8",
            )
            out = root / "out"

            transfer.transfer_plugin(plugin, out)

            tdd = (out / "plugins" / "plug" / "skills" / "_shared" / "tdd.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("`../../.codex-agents/impl-agent.toml`", tdd)
            self.assertIn("`../execute/SKILL.md`", tdd)
            self.assertNotIn("plugins/baransu", tdd)

    def test_agent_stub_body_rewrites_flat_valid_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "quality-reviewer.md"
            dest = root / "quality-reviewer.toml"
            src.write_text(
                """---
description: Review quality.
---

Do not touch `.claude/analyze/`.
See `plugins/baransu/agents/impl-agent.md`.
Counting per `plugins/baransu/skills/_shared/fact-check.md`.
""",
                encoding="utf-8",
            )

            transfer.emit_agent_stub(src, dest)
            text = dest.read_text(encoding="utf-8")

        # Flat-valid rewrites applied.
        self.assertIn(".codex/analyze/", text)
        self.assertNotIn(".claude/analyze/", text)
        self.assertIn("~/.codex/agents/impl-agent.toml", text)
        # No `../`-anchor from a flat agent install -> `_shared` ref left as a
        # discoverable plugin path, not an unresolvable relative one.
        self.assertIn("plugins/baransu/skills/_shared/fact-check.md", text)


if __name__ == "__main__":
    unittest.main()
