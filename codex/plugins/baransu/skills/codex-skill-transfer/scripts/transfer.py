#!/usr/bin/env python3
"""Port Claude Code material to Codex format.

Usage:
    python3 transfer.py <source-dir> <output-dir>

Direction is one-way: Claude is the source of truth (where the user's main
work lives), Codex is the secondary target. Three input shapes are auto-
detected:

  - **Plugin** (source has `.claude-plugin/plugin.json`):
        Translates the plugin manifest via assets/codex-plugin.template.json,
        batch-transfers all skills under `<source>/skills/`, emits package-local
        runtime TOMLs for every `<source>/agents/*.md`, wires named-agent
        dispatch to those exact definitions, and copies normalized rules.
        Output tree:
          <output>/.codex-plugin/plugin.json
          <output>/skills/<name>/...
          <output>/.codex-agents/*.toml
          <output>/rules/...

  - **Single skill** (source has SKILL.md directly):
        Transfers one skill into <output>/<skill-name>/.

  - **Skills batch** (source's children each have SKILL.md):
        Transfers every child into <output>/<skill-name>/.

Skills containing `context: fork` are skipped with a clear warning. Claude
agent definitions used by plugin skills are bundled under `.codex-agents/`;
the generated skill adapters resolve and pass the exact TOML to a generic
Codex subagent, failing closed when a definition cannot be read.

Marketplace catalog conversion is NOT automated; see
references/marketplace-mapping.md for the inline rules and
assets/codex-marketplace.template.json for a starting copy.

The script is intentionally conservative: when a rewrite is ambiguous, it
emits a `<!-- TODO(codex-transfer): ... -->` marker rather than guessing.

The plugin.json output shape lives in assets/codex-plugin.template.json —
editing it changes the output without touching the script. agents/openai.yaml,
bundled runtime-agent TOMLs, and optional flat-export stubs are NOT templated:
they're built via yaml.safe_dump / json.dumps so escape correctness is
ironclad (see SKILL.md Step 4).
"""

from __future__ import annotations

import json
import os
import re
import shutil
import string
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

try:
    import yaml  # type: ignore
except ImportError:
    sys.stderr.write("Missing dependency: pyyaml. Install with `pip install pyyaml`.\n")
    sys.exit(2)


# ---------------------------------------------------------------------------
# Asset template rendering
# ---------------------------------------------------------------------------
# Output shapes live in assets/*.template.*. Each placeholder is `$name`-style
# (Python string.Template). For JSON outputs, values are passed through
# json.dumps()[1:-1] first to escape quotes/control chars; for YAML and TOML
# we accept simple values only and rely on the caller to keep them safe.

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"


def _json_escape(value: str) -> str:
    """Return a JSON-safe inline string body (without surrounding quotes)."""
    return json.dumps(str(value), ensure_ascii=False)[1:-1]


def render_template(template_name: str, context: dict, mode: str = "json") -> str:
    """Render assets/<template_name> by substituting context placeholders.

    `mode` controls escaping: 'json' for JSON outputs (escape quotes/control
    chars), 'plain' for YAML/TOML where the caller passed already-safe values.
    """
    path = ASSETS_DIR / template_name
    text = path.read_text(encoding="utf-8")
    if mode == "json":
        safe = {k: _json_escape(v) for k, v in context.items()}
    else:
        safe = {k: str(v) for k, v in context.items()}
    return string.Template(text).substitute(safe)


CLAUDE_ONLY_DROP = {
    "user-invocable",
    "argument-hint",
    "arguments",
    "model",
    "effort",
    "hooks",
    "paths",
    "shell",
}

OPEN_STANDARD = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}

CODEX_HOOK_EVENTS = {
    "SessionStart",
    "PreToolUse",
    "PermissionRequest",
    "PostToolUse",
    "PreCompact",
    "PostCompact",
    "UserPromptSubmit",
    "SubagentStart",
    "SubagentStop",
    "Stop",
}

INLINE_BACKTICK_CMD = re.compile(r"!`([^`]+)`")
BLOCK_BACKTICK_CMD = re.compile(r"^```!\s*\n(.*?)^```\s*$", re.MULTILINE | re.DOTALL)
ARGS_FULL = re.compile(r"\$ARGUMENTS\b")
ARGS_INDEXED = re.compile(r"\$ARGUMENTS\[(\d+)\]")
# Bare `$N` is rewritten ONLY when the source frontmatter declares `arguments`
# or `argument-hint` (the signal that positional substitution is in use).
# Unconditional rewriting corrupted literal $1/$2 in awk/sed/bash snippets.
ARGS_BARE_NUM = re.compile(r"\$(\d+)\b")
SESSION_ID = re.compile(r"\$\{CLAUDE_SESSION_ID\}")
SKILL_DIR = re.compile(r"\$\{CLAUDE_SKILL_DIR\}|\$CLAUDE_SKILL_DIR\b")
SKILL_DIR_PLUS = re.compile(r"\$\{CLAUDE_SKILL_DIR:\+([^}]+)\}")
EFFORT = re.compile(r"\$\{CLAUDE_EFFORT\}")


def _inside_fenced_code_block(text: str, pos: int) -> bool:
    in_fence = False
    fence_marker = ""
    for line in text[:pos].splitlines():
        m = re.match(r"^[ \t]*(```|~~~)", line)
        if not m:
            continue
        marker = m.group(1)
        if not in_fence:
            in_fence = True
            fence_marker = marker
        elif marker == fence_marker:
            in_fence = False
            fence_marker = ""
    return in_fence


def _inside_inline_code_span(text: str, pos: int) -> bool:
    """Best-effort Markdown inline-code detection for local token rewrites."""
    line_start = text.rfind("\n", 0, pos) + 1
    line_end = text.find("\n", pos)
    if line_end == -1:
        line_end = len(text)
    line = text[line_start:line_end]
    stripped = line.lstrip()
    if stripped.startswith("```") or stripped.startswith("~~~"):
        return False
    return line[: pos - line_start].count("`") % 2 == 1


def _inside_markdown_code_context(text: str, pos: int) -> bool:
    return _inside_fenced_code_block(text, pos) or _inside_inline_code_span(text, pos)


def _inline_code_safe(replacement: str) -> str:
    return replacement.replace("`", "")


def markdown_aware_subn(
    pattern: str | re.Pattern[str],
    replacement: str | Callable[[re.Match[str]], str],
    text: str,
    flags: int = 0,
    code_replacement: str | Callable[[re.Match[str]], str] | None = None,
) -> tuple[str, int]:
    """Replace tokens without introducing nested backticks inside code spans."""
    compiled = re.compile(pattern, flags) if isinstance(pattern, str) else pattern
    count = 0

    def sub(m: re.Match[str]) -> str:
        nonlocal count
        count += 1
        repl = replacement(m) if callable(replacement) else m.expand(replacement)
        if _inside_markdown_code_context(text, m.start()):
            if code_replacement is not None:
                code_repl = (
                    code_replacement(m)
                    if callable(code_replacement)
                    else m.expand(code_replacement)
                )
                return _inline_code_safe(code_repl)
            return _inline_code_safe(repl)
        return repl

    return compiled.sub(sub, text), count


def normalize_codex_subagent_terms(text: str) -> tuple[str, int]:
    """Rewrite Claude Task/subagent orchestration terms to Codex wording.

    Codex subagents are explicit natural-language spawns, not Claude Task
    invocations. Keep the operational shape intact while removing Claude-only
    Task vocabulary from Codex-facing skill bodies and descriptions.
    """
    count = 0

    def apply(
        pattern: str,
        repl: str | Callable[[re.Match[str]], str],
        flags: int = 0,
    ) -> None:
        nonlocal text, count
        text, n = markdown_aware_subn(pattern, repl, text, flags=flags)
        count += n

    def dispatch_numbered_subagents(m: re.Match[str]) -> str:
        return f"Spawn {m.group(1)} Codex subagents in parallel"

    def dispatch_one_agent_per_sub(m: re.Match[str]) -> str:
        return f"Spawn one `{m.group(1)}` subagent per"

    def dispatching_agent_sub(m: re.Match[str]) -> str:
        return f"spawning a `{m.group(1)}` subagent"

    def dispatch_agent_sub(m: re.Match[str]) -> str:
        return f"Spawn a `{m.group(1)}` subagent"

    def parallel_task_sub(m: re.Match[str]) -> str:
        return "parallel Codex subagents" if m.group(1) else "parallel Codex subagent"

    apply(
        r"\bDispatch\s+(\d+)\s+subagents\s+in\s+parallel\s+Tasks\b",
        dispatch_numbered_subagents,
    )
    apply(
        r"\bDispatch\s+one\s+(?:\*\*)?`?([a-zA-Z][\w-]*?-agent)`?(?:\*\*)?\s+per\b",
        dispatch_one_agent_per_sub,
    )
    apply(
        r"\bdispatching\s+(?:\*\*)?`?([a-zA-Z][\w-]*?-agent)`?(?:\*\*)?",
        dispatching_agent_sub,
        flags=re.IGNORECASE,
    )
    apply(
        r"\bDispatch(?:es)?\s+(?:\*\*)?`?([a-zA-Z][\w-]*?-agent)`?(?:\*\*)?",
        dispatch_agent_sub,
    )
    apply(r"\bDispatch isolated\b", "Spawn isolated")
    apply(r"\bparallel Task(s?)\b", parallel_task_sub)
    apply(r"\bparallel-Task\b", "parallel-subagent")
    apply(r"\bStage\s+(\d+)\s+Tasks\b", r"Stage \1 Codex subagents")
    apply(r"\bvia Task\b", "by spawning Codex subagents")
    apply(r"\bTask contexts\b", "Codex subagent contexts")
    apply(r"\bTask Tool Creation\b", "Task Map Setup")
    apply(r"\bTask Tool IDs\b", "`task-map.md` IDs")
    apply(r"\bTask Tool ID\b", "`task-map.md` ID")
    apply(r"\bTask Tools\b", "`task-map.md` records")

    return text, count


@dataclass(frozen=True)
class CapabilityPort:
    codex_level: str
    strategy: str
    habit_strength: str
    countered_inertia: str
    tier: str
    risk: int


CAPABILITY_REGISTRY: dict[str, CapabilityPort] = {
    "AskUserQuestion:unclassified": CapabilityPort(
        codex_level="manual-classification",
        strategy="Classify the pause as authorization, input-alignment, or cosmetic before treating it as a soft prompt.",
        habit_strength="unknown",
        countered_inertia="unknown until the pause type is classified",
        tier="T2-1",
        risk=3,
    ),
    "AskUserQuestion:cosmetic": CapabilityPort(
        codex_level="soft-prompt",
        strategy="List numbered options and stop for the user's reply.",
        habit_strength="none-or-low selection inertia",
        countered_inertia="choosing between already-bounded options",
        tier="T2-2",
        risk=1,
    ),
    "AskUserQuestion:authorization": CapabilityPort(
        codex_level="hard-pause",
        strategy="Ask directly, record the answer, and do not proceed until the user authorizes the next step.",
        habit_strength="medium-to-strong premature-continuation inertia",
        countered_inertia="continuing past an authorization boundary without user consent",
        tier="Boundary",
        risk=3,
    ),
    "AskUserQuestion:input-gate": CapabilityPort(
        codex_level="soft-prompt",
        strategy="Ask numbered input-alignment options and stop; escalate to artifact/phase gate if the skill would otherwise continue into irreversible work.",
        habit_strength="medium missing-input inertia",
        countered_inertia="continuing with missing user input",
        tier="Boundary",
        risk=2,
    ),
    "AskUserQuestion:think": CapabilityPort(
        codex_level="artifact-gate",
        strategy="Split alignment into Phase 1 questions-only output and Phase 2 gated by `alignment.md`.",
        habit_strength="strong",
        countered_inertia="skipping alignment and starting design or implementation immediately",
        tier="T0-1",
        risk=5,
    ),
    "Task tool": CapabilityPort(
        codex_level="runtime-probe",
        strategy="Spawn explicit Codex subagents; for review/health, verify isolation or fall back to independent sessions with file outputs.",
        habit_strength="medium-to-strong",
        countered_inertia="rubber-stamping the current context as independent review",
        tier="T0-2",
        risk=4,
    ),
    "test-runner": CapabilityPort(
        codex_level="machine-gate",
        strategy="Green proof must come from actual runner exit codes, never model self-report.",
        habit_strength="strong",
        countered_inertia="declaring success without machine evidence",
        tier="T1-1",
        risk=4,
    ),
    "TaskCreate": CapabilityPort(
        codex_level="durable-artifact",
        strategy="Create or update `task-map.md`; `update_plan` is display-only.",
        habit_strength="strong",
        countered_inertia="creating multi-step work without durable state",
        tier="T1-2",
        risk=4,
    ),
    "TaskUpdate": CapabilityPort(
        codex_level="durable-artifact",
        strategy="Persist every state transition in `task-map.md`.",
        habit_strength="strong",
        countered_inertia="claiming progress through conversation memory instead of state transitions",
        tier="T1-2",
        risk=4,
    ),
    "TaskGet": CapabilityPort(
        codex_level="durable-artifact",
        strategy="Read task state from `task-map.md`, including after session restart.",
        habit_strength="strong",
        countered_inertia="reconstructing state from stale or invented memory",
        tier="T1-2",
        risk=4,
    ),
    "TaskList": CapabilityPort(
        codex_level="durable-artifact",
        strategy="List task state from `task-map.md`, not conversation memory.",
        habit_strength="strong",
        countered_inertia="losing parallel task state across long orchestration",
        tier="T1-2",
        risk=4,
    ),
    "TaskOutput": CapabilityPort(
        codex_level="durable-artifact",
        strategy="Record output pointers in `task-map.md` or adjacent artifacts.",
        habit_strength="strong",
        countered_inertia="treating subtask output as remembered rather than recorded evidence",
        tier="T1-2",
        risk=4,
    ),
    "TaskStop": CapabilityPort(
        codex_level="durable-artifact",
        strategy="Persist stopped/blocked state in `task-map.md`.",
        habit_strength="strong",
        countered_inertia="forgetting blocked or stopped work and continuing anyway",
        tier="T1-2",
        risk=4,
    ),
    "SendUserFile": CapabilityPort(
        codex_level="soft-prompt",
        strategy="Write the artifact to disk and list its absolute path.",
        habit_strength="weak",
        countered_inertia="delivery convenience only; no behavior tooth",
        tier="T3-1",
        risk=1,
    ),
}


@dataclass
class TransferReport:
    skill_name: str
    source: Path
    target: Path
    lossless: list[str] = field(default_factory=list)
    mapped: list[str] = field(default_factory=list)
    rewrites: list[str] = field(default_factory=list)
    dropped: list[str] = field(default_factory=list)
    capability_risks: dict[str, CapabilityPort] = field(default_factory=dict)
    manual_review: list[str] = field(default_factory=list)
    skipped: bool = False
    skip_reason: str = ""

    def render(self) -> str:
        lines = [
            f"## Codex Transfer Report — {self.skill_name}",
            "",
            f"- 來源: `{self.source}`",
            f"- 輸出: `{self.target}`",
            "",
        ]
        if self.skipped:
            lines += ["### ⚠️ 跳過", f"- {self.skip_reason}", ""]
            return "\n".join(lines)
        if self.lossless:
            lines += ["### 完整保留 (lossless)"]
            lines += [f"- {x}" for x in self.lossless]
            lines += [""]
        if self.mapped:
            lines += ["### 翻譯處理 (mapped)"]
            lines += [f"- {x}" for x in self.mapped]
            lines += [""]
        if self.rewrites:
            lines += ["### 動態注入改寫 (rewrites)"]
            lines += [f"- {x}" for x in self.rewrites]
            lines += [""]
        if self.dropped:
            lines += ["### 已捨棄 (dropped)"]
            lines += [f"- {x}" for x in self.dropped]
            lines += [""]
        if self.capability_risks:
            lines += ["### Capability 降級風險 (weighted by model inertia)"]
            for key, cap in sorted(
                self.capability_risks.items(),
                key=lambda item: (-item[1].risk, item[0]),
            ):
                lines.append(
                    f"- `{key}` → {cap.tier} / level={cap.codex_level} / "
                    f"strength={cap.habit_strength} / counters={cap.countered_inertia}: "
                    f"{cap.strategy}"
                )
            lines += [""]
        if self.manual_review:
            lines += ["### ⚠️ 需人工檢視 (manual review)"]
            lines += [f"- {x}" for x in self.manual_review]
            lines += [""]
        lines += ["### Next-port follow-ups"]
        if self.dropped or self.manual_review:
            lines += [f"- {x} — `accept-as-lossy`" for x in self.dropped]
            lines += [f"- {x} — `refresh-mapping`" for x in self.manual_review]
        else:
            lines += ["- none"]
        lines += [""]
        return "\n".join(lines)


def note_capability(report: TransferReport, key: str) -> None:
    cap = CAPABILITY_REGISTRY.get(key)
    if cap is not None:
        report.capability_risks.setdefault(key, cap)


ASK_USER_CAPABILITY_BY_SKILL: dict[str, str] = {
    "think": "AskUserQuestion:think",
    "analyze": "AskUserQuestion:authorization",
    "review": "AskUserQuestion:authorization",
    "read": "AskUserQuestion:cosmetic",
    "book": "AskUserQuestion:cosmetic",
    "design": "AskUserQuestion:cosmetic",
    # Descriptive-only skills: their AskUserQuestion occurrences are noun
    # phrases about the tool (fan-out clauses), never a call site. Rewrite to
    # a plain noun; NEVER inject a stop instruction into these sentences.
    "evolve": "AskUserQuestion:descriptive",
    "health": "AskUserQuestion:descriptive",
}


ASK_USER_REWRITE_BY_CAPABILITY: dict[str, str] = {
    "AskUserQuestion:think": (
        "the Codex alignment gate (output numbered alignment questions; stop; "
        "then require `alignment.md` before planning)"
    ),
    "AskUserQuestion:authorization": (
        "direct user question (record the authorization decision; stop until the user answers)"
    ),
    "AskUserQuestion:input-gate": (
        "direct user question with numbered input options (stop for the user's reply)"
    ),
    "AskUserQuestion:cosmetic": (
        "direct user question with numbered options (stop for the user's reply)"
    ),
    "AskUserQuestion:unclassified": (
        "direct user question with numbered options (stop; classify whether this is an authorization PAUSE before continuing)"
    ),
    # Descriptive noun mention — no imperative, no stop. Used when the source
    # sentence talks ABOUT the tool rather than instructing a call.
    "AskUserQuestion:descriptive": "a user-question prompt",
}


ASK_USER_CODE_REWRITE_BY_CAPABILITY: dict[str, str] = {
    "AskUserQuestion:think": "Codex alignment gate requiring alignment.md",
    "AskUserQuestion:authorization": "authorization PAUSE",
    "AskUserQuestion:input-gate": "input-alignment question PAUSE",
    "AskUserQuestion:cosmetic": "numbered-options question",
    "AskUserQuestion:unclassified": "user-question PAUSE (unclassified)",
    "AskUserQuestion:descriptive": "user-question prompt",
}


def classify_ask_user_occurrence(
    report: TransferReport,
    text: str,
    match: re.Match[str],
) -> str:
    if report.skill_name != "think":
        return ASK_USER_CAPABILITY_BY_SKILL.get(
            report.skill_name,
            "AskUserQuestion:unclassified",
        )

    line_start = text.rfind("\n", 0, match.start()) + 1
    line_end = text.find("\n", match.end())
    if line_end == -1:
        line_end = len(text)
    line = text[line_start:line_end]
    before = text[: match.start()]
    h2_matches = list(re.finditer(r"^##\s+(.+)$", before, re.MULTILINE))
    section = h2_matches[-1].group(1) if h2_matches else ""
    context = text[max(0, match.start() - 250) : match.end()]
    lowered_line = line.lower()
    lowered_section = section.lower()
    lowered_context = context.lower()

    if (
        "option 3" in lowered_line
        or "re-alignment" in lowered_line
        or "realignment" in lowered_line
        or "還有地方要對焦" in line
    ):
        return "AskUserQuestion:input-gate"
    if (
        "stage g" in lowered_section
        or "approval" in lowered_section
        or "stage g" in lowered_line
        or "approval" in lowered_line
        or "approved" in lowered_line
        or "final proposal" in lowered_context
        or "four-option gate" in lowered_context
        or "批准" in line
        or "核可" in line
        or "自由文字批准" in line
    ):
        return "AskUserQuestion:authorization"
    if (
        "stage a" in lowered_section
        or "alignment" in lowered_section
        or "stage a" in lowered_line
        or "before planning" in lowered_line
        or "each round" in lowered_line
        or "對焦" in line
    ):
        return "AskUserQuestion:think"
    if "label" in lowered_line:
        return "AskUserQuestion:cosmetic"
    return "AskUserQuestion:unclassified"


CODEX_SKILL_ADAPTERS: dict[str, str] = {
    "think": """## Codex Port Adapter - Alignment Gate

Codex has no verified AskUserQuestion hard stop. This skill is countering the model's inertia to skip alignment and start designing immediately, so plain prompt wording is not enough. For ambiguous requests, run the skill in two phases:

1. Phase 1 outputs only numbered alignment questions, then stops. It must not include implementation, scaffolding, pseudo-code, or the five-section plan.
2. Phase 2 may produce the five-section plan only after an `alignment.md` artifact exists in the active think workspace and records the user's answers. If the artifact is missing, refuse to plan and ask for the answers to be written first.

This rebuilds the hard gate at the artifact layer. It does not guarantee answer quality; it only prevents planning without a recorded alignment step. Authorization PAUSE remains a hard stop; only input-selection PAUSE may degrade to direct text questions.""",
    "review": """## Codex Port Adapter - Review Isolation

This skill is countering the model's inertia to rubber-stamp its own prior work. Before relying on spawned reviewers as anti-hallucination evidence, run or consult a `codex-isolation-probe.md` conclusion for this Codex runtime. If native Codex subagents receive clean independent context, spawn the perspective agents directly. If they inherit enough parent context to rubber-stamp the current answer, run each perspective in an independent Codex invocation or session, write each result to an artifact file, then synthesize from those files.

Do not simulate independent review by asking the same conversation context several times in sequence. Authorization PAUSE remains a hard stop; only input-selection PAUSE may degrade to direct text questions.""",
    "health": """## Codex Port Adapter - Inspector Isolation

This skill is countering the model's inertia to treat same-context self-audit as independent evidence. Before using inspector subagents for deep audits, run or consult a `codex-isolation-probe.md` conclusion for this Codex runtime. If native Codex subagents are isolated, use them directly. If not, run each inspector perspective in an independent Codex invocation or session, write the raw findings to files, then merge from those artifacts.

Do not treat same-context sequential prompts as independent inspection. Authorization PAUSE remains a hard stop; only input-selection PAUSE may degrade to direct text questions.""",
    "analyze": """## Codex Port Adapter - Machine Gates and Task Map

This skill is countering the model's inertia to declare progress without machine proof or durable state. Red/green decisions must come from actual command exit codes. Model self-report is never green proof. Keep the existing invariant that compile errors do not increment `failure_count`.

Use `task-map.md` as the durable source of truth for TaskCreate/TaskUpdate semantics. `update_plan` or other runtime plan displays are presentation only; after a session restart, reconstruct task state from `task-map.md` and adjacent artifacts before continuing. Authorization PAUSE remains a hard stop.""",
}


CODEX_SKILL_ADAPTER_CAPABILITIES: dict[str, tuple[str, ...]] = {
    "think": ("AskUserQuestion:think",),
    "review": ("Task tool",),
    "health": ("Task tool",),
    "analyze": ("test-runner", "TaskCreate", "TaskUpdate"),
}


def inject_codex_port_adapter(body: str, report: TransferReport) -> str:
    adapter = CODEX_SKILL_ADAPTERS.get(report.skill_name)
    if adapter is None:
        return body

    for key in CODEX_SKILL_ADAPTER_CAPABILITIES.get(report.skill_name, ()):
        note_capability(report, key)

    lines = body.splitlines()
    block = adapter.strip()
    if lines and lines[0].startswith("# "):
        new_lines = [lines[0], "", block, "", *lines[1:]]
        result = "\n".join(new_lines)
    else:
        result = f"{block}\n\n{body.lstrip()}"
    if body.endswith("\n"):
        result += "\n"
    report.rewrites.append(f"注入 `{report.skill_name}` Codex port adapter note")
    return result


def split_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        raise ValueError("missing frontmatter delimiter")
    end = text.find("\n---", 4)
    if end == -1:
        raise ValueError("unterminated frontmatter")
    raw = text[4:end]
    body = text[end + 4 :].lstrip("\n")
    data = yaml.safe_load(raw) or {}
    if not isinstance(data, dict):
        raise ValueError("frontmatter is not a mapping")
    return data, body


def translate_frontmatter(fm: dict, report: TransferReport) -> tuple[dict, dict | None]:
    out: dict = {}
    openai_yaml: dict | None = None

    for k in ("name", "description"):
        if k not in fm:
            raise ValueError(f"required field `{k}` missing")
        out[k] = fm[k]
        report.lossless.append(f"`{k}`")

    # Codex enforces a 1024-char limit on `description`. Beyond that hard
    # limit, short descriptions matter systemically: the skills list shares a
    # context cap (~2% of the window / 8,000 chars per official docs), so
    # every description char crowds out the others. Trim by stripping
    # Claude-style trigger phrase sentences first (these are useless to Codex
    # since Codex skills are command-invoked, not phrase-triggered); fall back
    # to a hard cut at the last sentence boundary if still over budget.
    # NOTE: the two trigger-phrase regexes below are baransu-specific
    # heuristics, not general Claude conventions.
    desc = out["description"]
    codex_desc, desc_rewrite_count = normalize_codex_subagent_terms(str(desc))
    if desc_rewrite_count:
        out["description"] = codex_desc
        desc = codex_desc
        report.mapped.append(
            f"`description` {desc_rewrite_count} 處 Claude Task/subagent wording 改為 Codex wording"
        )
    # Repo-internal path refs in the description (usually the output dir, e.g.
    # `.claude/analyze/`) -> Codex layout, unless this skill documents them.
    if fm.get("name") not in REPO_PATH_REWRITE_EXEMPT_SKILLS:
        desc_paths, desc_path_n = rewrite_repo_paths(str(desc), "../", fm.get("name"))
        if desc_path_n:
            out["description"] = desc_paths
            desc = desc_paths
            report.rewrites.append(
                f"`description` {desc_path_n} 處 repo 路徑參照改寫為 Codex 佈局"
            )
    if len(desc) > 1024:
        trimmed = re.sub(
            r"\s*Trigger immediately when[^.]*\.",
            "",
            desc,
        )
        trimmed = re.sub(
            r"\s*Also fires on the daily cron schedule[^.]*\.",
            "",
            trimmed,
        )
        trimmed = trimmed.strip()
        if len(trimmed) > 1024:
            cut = trimmed.rfind(".", 0, 1024)
            if cut > 0:
                trimmed = trimmed[: cut + 1]
            else:
                trimmed = trimmed[:1024]
        if trimmed != desc:
            out["description"] = trimmed
            report.mapped.append(
                f"`description` 從 {len(desc)} 字元縮到 {len(trimmed)} 字元 "
                "(Codex 上限 1024；剝除 Claude 觸發片語)"
            )

    for k in ("license", "metadata"):
        if k in fm:
            out[k] = fm[k]
            report.lossless.append(f"`{k}`")

    out.setdefault("compatibility", "Designed for Claude Code; ported to Codex.")
    if "compatibility" in fm:
        out["compatibility"] = fm["compatibility"]
        report.lossless.append("`compatibility`")
    else:
        report.mapped.append("加入預設 `compatibility`")

    md = out.setdefault("metadata", {}) if isinstance(out.get("metadata"), dict) else {}
    if isinstance(out.get("metadata"), dict) and "version" not in md:
        md["version"] = "0.1.0-codex"
        out["metadata"] = md
        report.mapped.append("加入預設 `metadata.version: 0.1.0-codex`")
    elif "metadata" not in out:
        out["metadata"] = {"version": "0.1.0-codex"}
        report.mapped.append("加入預設 `metadata.version: 0.1.0-codex`")

    if "allowed-tools" in fm:
        out["allowed-tools"] = fm["allowed-tools"]
        report.mapped.append("`allowed-tools` 保留 (Codex 可能忽略，experimental)")

    if fm.get("disable-model-invocation") is True:
        openai_yaml = {
            "display_name": str(fm["name"]).replace("-", " ").title(),
            "short_description": str(fm["description"]).split(".")[0][:120],
        }
        report.mapped.append("`disable-model-invocation: true` → `agents/openai.yaml` policy")

    for k in CLAUDE_ONLY_DROP:
        if k in fm:
            if k == "hooks":
                # Codex skills have no frontmatter hooks, but Codex DOES have
                # lifecycle hooks in config layers and plugins. They are
                # enabled by default but trust-gated; only command handlers
                # run today. See references/skill-mapping.md hooks row.
                report.dropped.append(
                    "skill frontmatter `hooks` 無直接目標；請移至 plugin `hooks/hooks.json` "
                    "或 Codex config layer，並以 `/hooks` review and trust"
                )
            else:
                report.dropped.append(f"`{k}` (no Codex equivalent)")

    return out, openai_yaml


# ---------------------------------------------------------------------------
# Repo-internal path reference rewriting
# ---------------------------------------------------------------------------
# Claude skill bodies cite sibling material by baransu-repo-root path
# (`plugins/baransu/agents/*.md`, `plugins/baransu/skills/_shared/*`). Those
# prefixes do not exist in the Codex output tree, so left alone they dangle —
# a dispatched reviewer told to read `plugins/baransu/agents/foo.md` finds
# nothing. The Codex layout equivalents:
#   - agents/*.md          -> bundled `.codex-agents/<name>.toml`
#                             (or `~/.codex/agents/...` only for flat manual stubs)
#   - skills/<other>/...    -> `<updots><other>/...` (sibling skill under skills/)
#   - skills/<self>/...     -> skill-root-relative (strip any `$VAR/` prefix)
#   - .claude-plugin/plugin.json -> `.codex-plugin/plugin.json`
#   - `.claude/<dir>`       -> `.codex/<dir>` (output/config dirs; not .claude-plugin)
#
# Files whose baransu paths are documentation ABOUT the repo or the mapping
# itself — not live cross-references — are exempt (rewriting corrupts meaning):
# the codex-skill-transfer skill's own mapping tables, and design's
# slide-checklist version-bump example. They are still Claude-token-scanned.
REPO_PATH_REWRITE_EXEMPT_SKILLS = frozenset({"codex-skill-transfer"})
# Scoped to (skill, relpath): a bare relpath would exempt any same-named file
# in an unrelated skill. slide-checklist.md is design's version-bump example.
REPO_PATH_REWRITE_EXEMPT_RELPATHS = frozenset(
    {("design", "references/slide-checklist.md")}
)

# Agent name may carry a glob (`*-reviewer`). Accept both repo-root and
# plugin-root spellings because references commonly shorten
# `plugins/baransu/agents/foo.md` to `agents/foo.md`.
_AGENT_REF = re.compile(
    r"(?<![A-Za-z0-9_./-])(?:plugins/baransu/)?agents/([A-Za-z0-9*_-]+)\.md"
)
# Optional leading `$VAR/` lets a self-reference like
# `$REPO_ROOT/plugins/baransu/skills/health/scripts` collapse to skill-root.
_SKILLS_REF = re.compile(
    r"(?:\$[A-Za-z_][A-Za-z0-9_]*/)?plugins/baransu/skills/([A-Za-z0-9_-]+)/"
)
_PLUGIN_JSON_REF = re.compile(r"plugins/baransu/\.claude-plugin/plugin\.json")
# `.claude/` only — `.claude-plugin` (hyphen, not slash) is deliberately spared.
_CLAUDE_DIR_REF = re.compile(r"\.claude/")


def rewrite_repo_paths(
    text: str,
    updots: str,
    skill_name: str | None,
    skills_relative: bool = True,
) -> tuple[str, int]:
    """Rewrite baransu repo-internal path references to their Codex layout.

    `updots` is the `../`-prefix that reaches the skills/ dir from the file
    being rewritten (SKILL.md -> `../`, references/*.md -> `../../`).

    `skills_relative=False` is for optional flat agent-stub bodies, which install at
    `~/.codex/agents/*.toml` and therefore have NO `../`-anchor into the
    plugin's skills/ tree: the `skills/<other>/...` rule is skipped so a
    `_shared/*` ref is left as a discoverable plugin path rather than an
    unresolvable relative one. Agent→agent and `.claude/` rewrites still apply.
    Returns (rewritten_text, change_count).
    """
    n = 0

    def agent_sub(m: re.Match[str]) -> str:
        nonlocal n
        n += 1
        if skills_relative:
            # `updots` reaches `skills/`; one more `../` reaches the plugin
            # root where package-local runtime agent definitions live.
            return f"{updots}../.codex-agents/{m.group(1)}.toml"
        return f"~/.codex/agents/{m.group(1)}.toml"

    text = _AGENT_REF.sub(agent_sub, text)

    def skills_sub(m: re.Match[str]) -> str:
        nonlocal n
        n += 1
        seg = m.group(1)
        if seg == skill_name:
            # Self-reference -> skill-ROOT-relative (drop any `$VAR/` prefix).
            # `updots` reaches the skills/ dir; the skill root is one level
            # below, so strip one `../`. Depth-correct: SKILL.md `../`->`` ,
            # references/*.md `../../`->`../`. A bare `""` here would be wrong
            # for any file below the skill root (it resolves from the file's
            # own dir, not the skill root).
            return updots[3:]
        return f"{updots}{seg}/"

    if skills_relative:
        text = _SKILLS_REF.sub(skills_sub, text)

    text, k = _PLUGIN_JSON_REF.subn(".codex-plugin/plugin.json", text)
    n += k
    text, k = _CLAUDE_DIR_REF.subn(".codex/", text)
    n += k
    return text, n


def rewrite_body(
    body: str,
    report: TransferReport,
    named_args: list[str] | None = None,
    positional_args: bool = False,
    skill_name: str | None = None,
) -> str:
    inline_count = 0
    block_count = 0

    def inline_sub(m: re.Match[str]) -> str:
        nonlocal inline_count
        inline_count += 1
        return f"<!-- TODO(codex-transfer): run `{m.group(1)}` and use its output here -->"

    def block_sub(m: re.Match[str]) -> str:
        nonlocal block_count
        block_count += 1
        cmds = m.group(1).strip().splitlines()
        bullets = "\n".join(f"- `{c.strip()}`" for c in cmds if c.strip())
        return (
            "<!-- TODO(codex-transfer): run these commands and use their output here -->\n"
            f"{bullets}\n"
        )

    body = BLOCK_BACKTICK_CMD.sub(block_sub, body)
    body = INLINE_BACKTICK_CMD.sub(inline_sub, body)

    if inline_count:
        report.rewrites.append(f"{inline_count} 處 inline `!cmd` 改為 TODO 指令塊")
    if block_count:
        report.rewrites.append(f"{block_count} 處 block ```! 改為 TODO 指令塊")

    arg_count = 0

    def args_full_sub(m: re.Match[str]) -> str:
        nonlocal arg_count
        arg_count += 1
        del m
        return "the arguments the user provided"

    def args_indexed_sub(m: re.Match[str]) -> str:
        # $ARGUMENTS[n] is 0-based.
        nonlocal arg_count
        arg_count += 1
        idx = int(m.group(1))
        ordinals = ["first", "second", "third", "fourth", "fifth"]
        word = ordinals[idx] if idx < len(ordinals) else f"#{idx + 1}"
        return f"the {word} argument the user provided"

    def args_bare_num_sub(m: re.Match[str]) -> str:
        # Bare $N is 1-based (Claude Code positional args).
        nonlocal arg_count
        arg_count += 1
        n = int(m.group(1))
        ordinals = ["first", "second", "third", "fourth", "fifth"]
        word = ordinals[n - 1] if 0 < n <= len(ordinals) else f"#{n}"
        return f"the {word} argument the user provided"

    body, _ = markdown_aware_subn(
        ARGS_INDEXED,
        args_indexed_sub,
        body,
        code_replacement=lambda m: m.group(0),
    )
    # Bare `$N` only when frontmatter signals positional substitution —
    # otherwise literal $1/$2 in awk/sed/bash snippets would be corrupted.
    if positional_args:
        body, _ = markdown_aware_subn(
            ARGS_BARE_NUM,
            args_bare_num_sub,
            body,
            code_replacement=lambda m: m.group(0),
        )
    body, _ = markdown_aware_subn(
        ARGS_FULL,
        args_full_sub,
        body,
        code_replacement=lambda m: m.group(0),
    )

    named_count = 0
    if named_args:
        # Match each declared name as `$name` not followed by another word/hyphen char,
        # so `$issue` matches but `$issue-id` (a different identifier) does not.
        for arg_name in named_args:
            if not re.fullmatch(r"[a-zA-Z_][\w-]*", arg_name):
                continue
            pattern = re.compile(rf"\${re.escape(arg_name)}(?![\w-])")

            def named_sub(m: re.Match[str], _name: str = arg_name) -> str:
                nonlocal named_count
                named_count += 1
                del m
                return f"the {_name} the user provided"

            body = pattern.sub(named_sub, body)

    body, _ = markdown_aware_subn(
        SESSION_ID,
        "the current session",
        body,
        code_replacement=lambda m: m.group(0),
    )

    def skill_dir_plus_sub(m: re.Match[str]) -> str:
        return f"the skill's root directory/{m.group(1).split('/', 1)[-1]}"

    def skill_dir_plus_code_sub(m: re.Match[str]) -> str:
        return SKILL_DIR.sub(".", m.group(1))

    body, _ = markdown_aware_subn(
        SKILL_DIR_PLUS,
        skill_dir_plus_sub,
        body,
        code_replacement=skill_dir_plus_code_sub,
    )
    body, _ = markdown_aware_subn(
        SKILL_DIR,
        "the skill's root directory",
        body,
        code_replacement=".",
    )
    body = EFFORT.sub("", body)

    if arg_count:
        report.rewrites.append(f"{arg_count} 處 `$ARGUMENTS` 系列改寫為自然語言")
    if named_count:
        report.rewrites.append(
            f"{named_count} 處宣告命名參數（{', '.join(named_args or [])}）改寫為自然語言"
        )

    # Claude tool-name / agent-dispatch rewrites (skill-mapping.md §6).
    # Multi-token patterns first so they don't get partially consumed.
    tool_count = 0
    body, subagent_term_count = normalize_codex_subagent_terms(body)
    tool_count += subagent_term_count
    if subagent_term_count:
        note_capability(report, "Task tool")

    # Noun-phrase / negated-mention guard — runs BEFORE the per-skill call-site
    # rewrite. Mentions like "never gated behind an AskUserQuestion proxy",
    # "0 AskUserQuestion calls", "ONE AskUserQuestion round" are nouns inside
    # sentences that describe (often negate) the tool; injecting the call-site
    # replacement's parenthetical imperative there ("(stop; ...)") plants a
    # mid-sentence stop instruction inside a sentence whose point is that no
    # stop happens. Substitute a plain noun with no imperative instead.
    noun_count = 0

    def ask_user_article_noun_sub(m: re.Match[str]) -> str:
        nonlocal noun_count
        noun_count += 1
        art = m.group(1)
        if art.lower() in ("an", "a"):
            art = "A" if art[0].isupper() else "a"
        tail = m.group(2) or " prompt"
        return f"{art} user-question{tail}"

    def ask_user_bare_noun_sub(m: re.Match[str]) -> str:
        nonlocal noun_count
        noun_count += 1
        del m
        return "user-question"

    body, _ = markdown_aware_subn(
        r"\b(an|a|An|A|0|ONE|one)\s+AskUserQuestion\b(\s+(?:proxy|calls|round|block)\b)?",
        ask_user_article_noun_sub,
        body,
        code_replacement=lambda m: m.group(0),
    )
    body, _ = markdown_aware_subn(
        r"\bAskUserQuestion\b(?=\s+(?:proxy|calls|round|block)\b)",
        ask_user_bare_noun_sub,
        body,
        code_replacement=lambda m: m.group(0),
    )
    if noun_count:
        tool_count += noun_count
        report.rewrites.append(
            f"{noun_count} 處 AskUserQuestion 名詞性／否定語境提及改寫為 plain noun"
            "（不注入停頓指令）"
        )

    ask_keys_seen: set[str] = set()

    def ask_user_sub(m: re.Match[str]) -> str:
        key = classify_ask_user_occurrence(report, body, m)
        ask_keys_seen.add(key)
        return ASK_USER_REWRITE_BY_CAPABILITY[key]

    def ask_user_code_sub(m: re.Match[str]) -> str:
        key = classify_ask_user_occurrence(report, body, m)
        return ASK_USER_CODE_REWRITE_BY_CAPABILITY[key]

    body, ask_count = markdown_aware_subn(
        r"\bAskUserQuestion\b",
        ask_user_sub,
        body,
        code_replacement=ask_user_code_sub,
    )
    if ask_count:
        tool_count += ask_count
        for key in sorted(ask_keys_seen):
            note_capability(report, key)

    # Single-token Claude API references.
    TOKEN_MAP: list[tuple[str, str, str | None]] = [
        # Subagent / task plumbing
        (r"\bTask\s+tool\b", "Codex subagent", "Task tool"),
        (r"\bTaskCreate\b", "create a `task-map.md` record", "TaskCreate"),
        (r"\bTaskUpdate\b", "update `task-map.md` task state", "TaskUpdate"),
        (r"\bTaskGet\b", "look up `task-map.md` task state", "TaskGet"),
        (r"\bTaskList\b", "list `task-map.md` records", "TaskList"),
        (r"\bTaskOutput\b", "read task output recorded in `task-map.md`", "TaskOutput"),
        (r"\bTaskStop\b", "mark the task stopped in `task-map.md`", "TaskStop"),
        (r"\bTodoWrite\b", "track steps internally", None),
        # Plan mode (no skill-callable equivalent in Codex)
        (r"\bEnterPlanMode\b", "produce a plan and pause for confirmation", None),
        (r"\bExitPlanMode\b", "exit the plan and proceed with edits", None),
        # Artifact delivery
        (r"\bSendUserFile\b", "write the artifact to disk and list its absolute path", "SendUserFile"),
        # Web access
        (r"\bWebFetch\b", "fetch the URL", None),
        (r"\bWebSearch\b", "search the web", None),
    ]
    for pat, repl, cap_key in TOKEN_MAP:
        body, n = markdown_aware_subn(pat, repl, body)
        tool_count += n
        if n and cap_key:
            note_capability(report, cap_key)

    if tool_count:
        report.rewrites.append(
            f"{tool_count} 處 Claude tool / agent 派遣關鍵字改寫為 Codex 對等敘述（AskUserQuestion / Dispatch X-agent / TaskCreate / SendUserFile 等）"
        )

    # Instruction-file rewrite: Codex reads AGENTS.md (root-down, 32 KiB
    # combined cap), not CLAUDE.md. Body-level rewrite only — references/*.md
    # are scanned-and-flagged instead (see copy_aux), never rewritten.
    # Lines that already mention AGENTS.md are listing both files on purpose
    # (e.g. "scan AGENTS.md, CLAUDE.md") — rewriting there would produce
    # redundant "AGENTS.md / AGENTS.md" prose, so leave them untouched.
    agents_md_count = 0
    rewritten_lines = []
    for line in body.split("\n"):
        if "AGENTS.md" in line:
            rewritten_lines.append(line)
            continue
        new_line, n = re.subn(r"\bCLAUDE\.md\b", "AGENTS.md", line)
        agents_md_count += n
        rewritten_lines.append(new_line)
    body = "\n".join(rewritten_lines)
    if agents_md_count:
        report.mapped.append(
            f"{agents_md_count} 處 `CLAUDE.md` 改寫為 `AGENTS.md`"
            "（Codex 由 root 向下讀 AGENTS.md，合併上限 32 KiB）"
        )

    # Repo-internal path references -> Codex layout. SKILL.md sits at the skill
    # root, so `../` reaches the skills/ dir. Exempt skills document these paths
    # literally (see REPO_PATH_REWRITE_EXEMPT_SKILLS).
    if skill_name not in REPO_PATH_REWRITE_EXEMPT_SKILLS:
        body, path_n = rewrite_repo_paths(body, "../", skill_name)
        if path_n:
            report.rewrites.append(
                f"{path_n} 處 repo 內部路徑參照改寫為 Codex 佈局"
                "（agents→plugin `.codex-agents/*.toml`、_shared/跨 skill→相對路徑、"
                "`.claude/`→`.codex/`）"
            )

    return body


def write_skill(
    target: Path,
    frontmatter: dict,
    body: str,
    openai_meta: dict | None,
) -> None:
    """Write SKILL.md and (when policy is locked down) agents/openai.yaml.

    The openai.yaml output is built via yaml.safe_dump (not templated) and
    matches the references/skill-mapping.md §2 example shape.
    `openai_meta` carries display_name and short_description; passing None
    means no openai.yaml is emitted.
    """
    target.mkdir(parents=True, exist_ok=True)
    fm_text = yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=True).strip()
    skill_md = f"---\n{fm_text}\n---\n\n{body.lstrip()}"
    (target / "SKILL.md").write_text(skill_md, encoding="utf-8")
    if openai_meta is not None:
        # Use yaml.safe_dump rather than a template — safe_dump correctly
        # escapes quotes, newlines, and special chars in display_name /
        # short_description regardless of what the upstream description
        # contained. Templating this layer required honor-system escape
        # discipline that v0.4.0 broke (see references/skill-mapping.md §2).
        agents_dir = target / "agents"
        agents_dir.mkdir(exist_ok=True)
        openai_doc = {
            "interface": {
                "display_name": openai_meta["display_name"],
                "short_description": openai_meta["short_description"],
            },
            "policy": {"allow_implicit_invocation": False},
        }
        (agents_dir / "openai.yaml").write_text(
            yaml.safe_dump(openai_doc, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )


def check_output_invariants(target: Path, report: TransferReport) -> None:
    """Verify the documented output invariants (skill-mapping.md §7).

    Failures are flagged in the report but the output is emitted anyway —
    the user decides whether to split/rename.
    """
    skill_md = target / "SKILL.md"
    line_count = len(skill_md.read_text(encoding="utf-8").splitlines())
    if line_count > 500:
        report.manual_review.append(
            f"輸出 SKILL.md 共 {line_count} 行，超過開放規格建議的 500 行；建議拆分至 references/"
        )

    name = target.name
    if len(name) > 64 or not re.fullmatch(r"[a-z0-9-]+", name):
        report.manual_review.append(
            f"skill 名 `{name}` 不符開放規格（agentskills.io：小寫字母/數字/連字號，≤64 字元）"
        )

    # Optional external validator — run only when present on PATH.
    skills_ref = shutil.which("skills-ref")
    if skills_ref:
        proc = subprocess.run(
            [skills_ref, "validate", str(target)],
            capture_output=True,
            text=True,
        )
        if proc.returncode == 0:
            report.mapped.append("`skills-ref validate` 通過")
        else:
            detail = (proc.stderr or proc.stdout).strip().splitlines()
            first = detail[0] if detail else f"exit {proc.returncode}"
            report.manual_review.append(
                f"`skills-ref validate` 失敗（exit {proc.returncode}）：{first}"
            )


SKILL_DIR_ENV = re.compile(r"\$\{CLAUDE_SKILL_DIR\}|\$CLAUDE_SKILL_DIR\b")

# Claude-only token scan patterns. Conservative by design: scanned files are
# NEVER rewritten (they may quote these tokens as documentation — e.g. this
# skill's own mapping tables); each affected file is flagged for manual review
# instead. Used for copied references/*.md (copy_aux) AND for shared aux dirs
# copied verbatim in plugin mode (transfer_plugin).
TOKEN_SCAN_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("AskUserQuestion", re.compile(r"\bAskUserQuestion\b")),
    ("Task tool", re.compile(r"\bTask\s+tool\b")),
    ("TodoWrite", re.compile(r"\bTodoWrite\b")),
    ("EnterPlanMode", re.compile(r"\bEnterPlanMode\b")),
    ("TaskCreate", re.compile(r"\bTaskCreate\b")),
    ("TaskUpdate", re.compile(r"\bTaskUpdate\b")),
    ("TaskGet", re.compile(r"\bTaskGet\b")),
    ("TaskList", re.compile(r"\bTaskList\b")),
    ("TaskOutput", re.compile(r"\bTaskOutput\b")),
    ("TaskStop", re.compile(r"\bTaskStop\b")),
    ("SendUserFile", re.compile(r"\bSendUserFile\b")),
    ("parallel Tasks", re.compile(r"\bparallel\s+Tasks\b")),
    ("clean Task contexts", re.compile(r"\bclean\s+Task\s+contexts\b")),
    ("via Task", re.compile(r"\bvia\s+Task\b")),
    ("Dispatch **agent**", re.compile(r"\bDispatch\s+\*\*[a-zA-Z][\w-]*?-agent\*\*")),
    ("Workflow primitives", re.compile(r"\bWorkflow\s+primitives\b")),
    ("$ARGUMENTS", re.compile(r"\$ARGUMENTS\b")),
    ("!`cmd` injection", re.compile(r"!`[^`]+`")),
    ("CLAUDE_SKILL_DIR", re.compile(r"\bCLAUDE_SKILL_DIR\b")),
    ("CLAUDE.md", re.compile(r"\bCLAUDE\.md\b")),
]


class OutputGuardError(RuntimeError):
    """Existing output dir is non-empty and carries no generated marker.

    Raised instead of rmtree-ing a directory this script cannot prove it
    generated — pointing the output at an unrelated non-empty directory must
    refuse (exit 2), never silently destroy its contents.
    """


def copy_aux(source: Path, target: Path, report: TransferReport) -> None:
    # Standard auxiliary dirs. node_modules / __pycache__ are runtime-
    # regenerated install artifacts (never distributed); copying them bloats
    # the mirror by thousands of files for no consumer.
    for sub in ("scripts", "references", "assets", "evals"):
        src = source / sub
        if src.is_dir():
            shutil.copytree(
                src,
                target / sub,
                dirs_exist_ok=True,
                ignore=shutil.ignore_patterns("node_modules", "__pycache__"),
            )

    # Skill-root orphan files (e.g. grade/CRON.md). These get silently dropped
    # otherwise; surface them so SKILL.md cross-references don't dangle.
    orphan_files: list[str] = []
    for path in source.iterdir():
        if path.is_file() and path.name != "SKILL.md":
            shutil.copy2(path, target / path.name)
            orphan_files.append(path.name)
    if orphan_files:
        report.mapped.append(
            f"複製 skill-root 零散檔案：{', '.join(orphan_files)}"
        )

    # Skill-root orphan DIRECTORIES (anything beyond the standard dirs). These
    # are NOT copied — list each so the omission is visible, not silent.
    orphan_dirs = [
        p.name
        for p in sorted(source.iterdir())
        if p.is_dir()
        and p.name not in ("scripts", "references", "assets", "evals", "agents")
    ]
    for d in orphan_dirs:
        report.dropped.append(
            f"skill-root 子目錄 `{d}/` 未複製（非 scripts/references/assets/evals/agents 標準目錄）"
        )

    # A skill-root agents/ dir is also not copied (bundled runtime definitions
    # come from PLUGIN-level agents/ in plugin mode) — say so, never silent.
    if (source / "agents").is_dir():
        report.dropped.append(
            "skill-root 子目錄 `agents/` 未複製（bundled TOML 僅由 plugin 層級 agents/ 產生；skill 內附 agents/ 需手動遷移）"
        )

    # `$CLAUDE_SKILL_DIR` rewrite for copied scripts only. References are
    # copied verbatim and scanned below because they often document literal
    # mapping tokens; rewriting them corrupts the transfer guide itself.
    # Skip transfer.py itself: its source contains the literal regex pattern
    # `\$\{CLAUDE_SKILL_DIR\}|\$CLAUDE_SKILL_DIR\b`, which the rewriter would
    # turn into `\$\{CLAUDE_SKILL_DIR\}|\.\b` (broken) on every self-port.
    rewritten = 0
    rewrite_roots = [target / "scripts"]
    for root in rewrite_roots:
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            # Self-corruption guard. transfer.py is the rewriter's own source;
            # rewriting its regex literal would silently break the next dogfood.
            if path.name == "transfer.py":
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            if "CLAUDE_SKILL_DIR" not in text:
                continue
            new_text, n = SKILL_DIR_ENV.subn(".", text)
            if n:
                path.write_text(new_text, encoding="utf-8")
                rewritten += n
    if rewritten:
        report.rewrites.append(
            f"{rewritten} 處 scripts/ 內的 `${{CLAUDE_SKILL_DIR}}` 改寫為 `.`（skill root）"
        )

    # Repo-internal path references in copied references/*.md -> Codex layout.
    # (SKILL.md itself is rewritten in rewrite_body.) Exempt skills/files whose
    # baransu paths are documentation, not live refs (REPO_PATH_REWRITE_EXEMPT_*).
    refs_root = target / "references"
    skill_name = target.name
    if refs_root.is_dir() and skill_name not in REPO_PATH_REWRITE_EXEMPT_SKILLS:
        path_rewrites = 0
        for path in sorted(refs_root.rglob("*.md")):
            rel = path.relative_to(target)
            if (skill_name, str(rel)) in REPO_PATH_REWRITE_EXEMPT_RELPATHS:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            # One `../` per path component reaches the skills/ dir:
            # references/foo.md (2 parts) -> `../../`.
            new_text, n = rewrite_repo_paths(text, "../" * len(rel.parts), skill_name)
            if n:
                path.write_text(new_text, encoding="utf-8")
                path_rewrites += n
        if path_rewrites:
            report.rewrites.append(
                f"{path_rewrites} 處 references/ 內 repo 路徑參照改寫為 Codex 佈局"
            )

    # Claude-only token scan over copied references/*.md (TOKEN_SCAN_PATTERNS;
    # flag-only, never rewrite).
    if refs_root.is_dir():
        for path in sorted(refs_root.rglob("*.md")):
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            found = [label for label, pat in TOKEN_SCAN_PATTERNS if pat.search(text)]
            if found:
                rel = path.relative_to(target)
                report.manual_review.append(
                    f"`{rel}` 含 Claude-only token（{', '.join(found)}）；"
                    "引用文件不自動改寫，請人工確認語境後處理"
                )


def transfer_one(source: Path, output_root: Path) -> TransferReport:
    skill_md = source / "SKILL.md"
    name = source.name
    target = output_root / name
    report = TransferReport(skill_name=name, source=source, target=target)

    if not skill_md.is_file():
        # Skipped BEFORE any output mutation: a skipped source never wipes a
        # prior target. Batch mode feeds every dir child through here so
        # SKILL.md-less children surface as skipped report entries instead of
        # being silently dropped (SKILL.md Step 1 contract).
        report.skipped = True
        report.skip_reason = "no SKILL.md in source"
        return report

    # Always clear stale output before producing a fresh result. Without this,
    # rerunning into the same output dir would merge old files (auxiliary
    # resources, agents/openai.yaml from a prior `disable-model-invocation`,
    # etc.) with new ones, leaving artifacts that contradict the current
    # source or this run's report. Guard first: a generated skill target
    # always contains SKILL.md; a non-empty target without one was not
    # produced by this script and must not be destroyed.
    if (
        target.is_dir()
        and any(target.iterdir())
        and not (target / "SKILL.md").is_file()
    ):
        raise OutputGuardError(
            f"refused: output target ({target}) exists, is non-empty, and has "
            "no generated SKILL.md marker; not wiping a directory this script "
            "did not generate. Remove it yourself or pick another output dir."
        )
    if target.exists():
        shutil.rmtree(target)

    text = skill_md.read_text(encoding="utf-8")
    try:
        fm, body = split_frontmatter(text)
    except ValueError as e:
        report.skipped = True
        report.skip_reason = f"frontmatter parse error: {e}"
        return report

    if fm.get("name") and fm["name"] != name:
        report.manual_review.append(
            f"frontmatter name `{fm['name']}` 與目錄名 `{name}` 不一致；以目錄名為準"
        )
        fm["name"] = name

    if fm.get("context") == "fork" or "agent" in fm:
        report.skipped = True
        report.skip_reason = (
            "`context: fork` / `agent` 偵測到。Codex 有對應方案，但跨越 skill 包與 user 配置邊界，"
            "需人工選路：\n"
            "    1. 原生 Subagents（推薦，重 IO 隔離）：在 `~/.codex/agents/{name}.toml` "
            "建對應 TOML，body 改寫為「Spawn a `{name}` subagent...」。\n"
            "    2. Skill chain（輕量，無隔離）：拆兩個 skill，body 末加 `$next-skill` mention。\n"
            "    3. Codex MCP + Agents SDK（重型，程式化）：跑 `codex mcp-server`，"
            "外部 SDK 用 handoffs 編排。\n"
            "    詳見 `references/skill-mapping.md` §5。"
        )
        return report

    try:
        new_fm, openai_yaml = translate_frontmatter(fm, report)
    except ValueError as e:
        report.skipped = True
        report.skip_reason = f"frontmatter 缺必要欄位: {e}"
        return report

    named_args_raw = fm.get("arguments")
    if isinstance(named_args_raw, str):
        named_args = named_args_raw.split()
    elif isinstance(named_args_raw, list):
        named_args = [str(x) for x in named_args_raw]
    else:
        named_args = None

    positional_args = bool(fm.get("arguments") or fm.get("argument-hint"))
    new_body = rewrite_body(
        body,
        report,
        named_args=named_args,
        positional_args=positional_args,
        skill_name=name,
    )
    new_body = inject_codex_port_adapter(new_body, report)
    write_skill(target, new_fm, new_body, openai_yaml)
    check_output_invariants(target, report)
    copy_aux(source, target, report)
    return report


# ---------------------------------------------------------------------------
# Plugin / marketplace mode (added v0.3.0)
# ---------------------------------------------------------------------------
# Three input shapes are recognized:
#   - skills-batch: <dir>/<child>/SKILL.md ...    (the original mode)
#   - single-skill: <dir>/SKILL.md                (treated as batch-of-one)
#   - plugin:       <dir>/.claude-plugin/plugin.json  (NEW; full plugin port)
#
# Plugin mode produces:
#   <out>/.codex-plugin/plugin.json     ← translated manifest
#   <out>/skills/<name>/...               ← each skill via existing pipeline
#   <out>/.codex-agents/*.toml          ← bundled runtime definitions
#   <out>/rules/...                     ← normalized package rules
# Package-local TOMLs are not auto-registered by Codex. Generated skills carry
# a resolver adapter that gives a generic subagent the exact definition path
# and fails closed instead of improvising a missing role.


def detect_mode(source: Path) -> str:
    if (source / ".claude-plugin" / "plugin.json").is_file():
        return "plugin"
    if (source / "SKILL.md").is_file():
        return "single-skill"
    if any(
        (c / "SKILL.md").is_file()
        for c in source.iterdir()
        if c.is_dir()
    ):
        return "skills-batch"
    return "unknown"


def translate_plugin_manifest(claude_pj: dict, has_skills: bool) -> tuple[dict, list[str], list[str]]:
    """Translate Claude Code plugin.json → Codex .codex-plugin/plugin.json.

    Returns (codex_pj, mapped_notes, dropped_notes). Codex requires only
    `name` (kebab-case) + `version` (semver); `description` is optional per
    the official build docs but recommended, and (per the same docs) an
    explicit `skills` pointer is needed when the plugin bundles skills.
    """
    out: dict = {}
    mapped: list[str] = []
    dropped: list[str] = []

    if "name" not in claude_pj:
        raise ValueError("plugin.json missing required `name`")
    out["name"] = claude_pj["name"]

    out["version"] = str(claude_pj.get("version") or "0.1.0-codex")
    if "version" not in claude_pj:
        mapped.append("`version` 缺，補入 `0.1.0-codex` (Codex 必填 semver)")

    out["description"] = str(claude_pj.get("description") or claude_pj["name"])
    if "description" not in claude_pj:
        mapped.append("`description` 缺，以 `name` 暫代 (建議補上；Codex 選填)")

    for k in ("author", "homepage", "repository", "license", "keywords"):
        if k in claude_pj:
            out[k] = claude_pj[k]

    # Codex is manifest-driven: components must be pointed at explicitly.
    # Claude is filesystem-driven, so plugin.json typically omits these.
    if has_skills:
        out["skills"] = "./skills/"
        mapped.append("加入 `skills: \"./skills/\"` 指標 (Codex manifest-driven)")

    out["interface"] = {
        "displayName": str(out["name"]).replace("-", " ").title(),
        "shortDescription": out["description"][:120],
    }
    mapped.append("加入 `interface` 預設 (display_name + short_description)")

    # Claude-side fields that have no Codex equivalent at the plugin level.
    # (`commands` is handled separately in transfer_plugin — it needs
    # actionable manual-review guidance, not a plain drop line.)
    for k in ("lspServers", "agents"):
        if k in claude_pj:
            dropped.append(f"`{k}` (Claude-only at plugin level; agents 走 user-side `.codex/agents/*.toml`)")

    return out, mapped, dropped


def emit_agent_stub(agent_md: Path, dest: Path) -> None:
    """Emit a TOML stub from a Claude agent .md.

    The user must review and copy the result into their own ~/.codex/agents/.
    This script never writes to the user's config directory.

    TOML strategy: use literal multi-line (`'''...'''`) for instructions and
    JSON-quoted strings for name/description. Literal multi-line allows any
    character except three consecutive single-quotes — agent .md bodies almost
    never contain `'''`. If they do, we degrade to TOML basic multi-line with
    full escape (rare path; preserved for robustness).
    """
    name = agent_md.stem
    body = agent_md.read_text(encoding="utf-8")

    # Best-effort: pull `description:` and `tools:` from frontmatter if present.
    desc = ""
    tools: list[str] = []
    fm_end = body.find("\n---", 4) if body.startswith("---\n") else -1
    if fm_end > 0:
        try:
            fm = yaml.safe_load(body[4:fm_end]) or {}
            if isinstance(fm, dict):
                # Take first line only (TOML basic string is single-line),
                # no length cap: optional flat agent exports are consumed by Codex
                # spawn_agent reading ~/.codex/agents/*.toml, so truncating the
                # description corrupts the agent's load-time metadata
                # (architecture-reviewer F2, 2026-05-14). json.dumps below
                # handles all escape concerns.
                desc = str(fm.get("description") or "").splitlines()[0]
                # Tools list — emit as a commented-out mcp_servers suggestion.
                raw_tools = fm.get("tools") or fm.get("allowed-tools")
                if isinstance(raw_tools, str):
                    tools = [t.strip() for t in raw_tools.split(",") if t.strip()]
                elif isinstance(raw_tools, list):
                    tools = [str(t).strip() for t in raw_tools if str(t).strip()]
        except yaml.YAMLError:
            pass

    instructions = body[fm_end + 4 :].lstrip("\n") if fm_end > 0 else body
    # Rewrite repo-internal path refs so the stub body doesn't send the agent
    # to Claude-only paths (`.claude/analyze/`, `plugins/baransu/agents/*.md`).
    # Flat install (`~/.codex/agents/`) has no `../`-anchor into skills/, so the
    # skills-relative rule is skipped — a `_shared/*` ref stays a discoverable
    # plugin path rather than an unresolvable relative one.
    instructions, _ = rewrite_repo_paths(
        instructions, "", name, skills_relative=False
    )
    instructions_block = _toml_multiline(instructions)

    # name/description go through json.dumps for ironclad escaping. TOML
    # basic strings accept the JSON-escape syntax (\\, \", \n, \uXXXX) so the
    # round-trip is safe.
    name_quoted = json.dumps(name, ensure_ascii=False)
    desc_quoted = json.dumps(desc, ensure_ascii=False)

    # Render `tools` (Claude) as a commented mcp_servers suggestion. Codex
    # treats mcp_servers as MCP server ids, NOT as Claude tool names, so this
    # is provided as documentation only — user enables and renames after
    # mapping each Claude tool to the appropriate Codex MCP server.
    if tools:
        tools_json = json.dumps(tools, ensure_ascii=False)
        mcp_line = (
            f"# mcp_servers = {tools_json}"
            "  # ported from Claude `tools:`; rename to Codex MCP server ids before enabling"
        )
    else:
        mcp_line = "# mcp_servers = []                     # list of MCP server ids the agent may invoke"

    tool_names = {t.split("(", 1)[0].strip().lower() for t in tools}
    write_or_exec = bool(tool_names & {"write", "edit", "multiedit", "bash"})
    read_only = bool(tools) and not write_or_exec
    if write_or_exec:
        sandbox_hint = (
            "# Sandbox note: source tools include Write/Edit/Bash; this agent writes or runs shell commands.\n"
            "# Review workspace-write scope and approval policy before enabling it."
        )
    elif read_only:
        sandbox_hint = (
            "# Sandbox note: source tools look read-only; consider a read-only sandbox unless the prompt requires writes."
        )
    else:
        sandbox_hint = (
            "# Sandbox note: source did not declare tools; inherit parent sandbox unless you intentionally narrow it."
        )

    stub = (
        f"# Stub generated from {agent_md.name}.\n"
        f"# Review before copying to ~/.codex/agents/{name}.toml (personal)\n"
        f"# or .codex/agents/{name}.toml (project-scoped trusted repo).\n"
        f"# See codex-skill-transfer references/agent-mapping.md for the mapping rules.\n"
        f"\n"
        f"name = {name_quoted}\n"
        f"description = {desc_quoted}\n"
        f"\n"
        f"developer_instructions = {instructions_block}\n"
        f"\n"
        f"# Choose what to fill in below; omit optional fields to inherit from the parent session.\n"
        f"#\n"
        f"# model = \"gpt-5.6\"                   # demanding agents; use gpt-5.6-terra for light read-heavy scans\n"
        f"# model_reasoning_effort = \"high\"      # minimal | low | medium | high | xhigh\n"
        f"# sandbox_mode = \"workspace-write\"     # read-only | workspace-write | danger-full-access; parent runtime overrides win\n"
        f"{mcp_line}\n"
        f"{sandbox_hint}\n"
        f"# nickname_candidates = []             # cosmetic names for spawned instances\n"
        f"#\n"
        f"# [[skills.config]]                    # optional per-agent skill enable/disable override\n"
        f"# path = \"/path/to/skill/SKILL.md\"\n"
        f"# enabled = false\n"
    )
    dest.write_text(stub, encoding="utf-8")


def _toml_multiline(text: str) -> str:
    """Quote `text` as a TOML multi-line string.

    Prefers literal `'''...'''` (no escaping needed for `"`, `\\`, `$`). Falls
    back to basic `\"\"\"...\"\"\"` with full backslash + triple-quote escape
    when the body contains `'''`.
    """
    if "'''" not in text:
        # Literal multi-line: opening newline is stripped by TOML parser, so
        # adding one after `'''` keeps the indentation predictable.
        return f"'''\n{text}\n'''"
    # Fall back: escape every backslash, then every quote (each one
    # individually) so no run of three `"` survives.
    escaped = text.replace("\\", "\\\\").replace('"', '\\"')
    return f'"""\n{escaped}\n"""'


def rewrite_bundled_agent_instructions(text: str) -> str:
    """Translate one Claude agent body into a package-local Codex definition.

    The generated TOML lives at `<plugin>/.codex-agents/<name>.toml`.
    Relative references therefore resolve from that directory: `../skills`,
    `../rules`, and sibling agent TOMLs under `../.codex-agents`.
    """
    text = text.replace("${CLAUDE_PLUGIN_ROOT}/", "../")
    text = text.replace("$CLAUDE_PLUGIN_ROOT/", "../")
    text = text.replace("${CLAUDE_PLUGIN_DATA}", "${PLUGIN_DATA}")
    text = text.replace("$CLAUDE_PLUGIN_DATA", "$PLUGIN_DATA")
    text = re.sub(
        r"plugins/baransu/skills/([A-Za-z0-9_-]+)/",
        r"../skills/\1/",
        text,
    )
    text = re.sub(
        r"plugins/baransu/rules/",
        "../rules/",
        text,
    )
    text = re.sub(
        r"(?:plugins/baransu/)?agents/([A-Za-z0-9*_-]+)\.md",
        r"../.codex-agents/\1.toml",
        text,
    )
    text = text.replace("CLAUDE.md", "AGENTS.md")
    text = text.replace(".claude/", ".codex/")
    text, _ = normalize_codex_subagent_terms(text)
    text = re.sub(r"\bTask tool\b", "subagent dispatch", text, flags=re.IGNORECASE)
    return text


def emit_bundled_agent_definition(agent_md: Path, dest: Path) -> None:
    """Emit a runtime-consumable Codex agent TOML inside the plugin package."""
    name = agent_md.stem
    body = agent_md.read_text(encoding="utf-8")
    desc = ""
    fm_end = body.find("\n---", 4) if body.startswith("---\n") else -1
    if fm_end > 0:
        try:
            fm = yaml.safe_load(body[4:fm_end]) or {}
            if isinstance(fm, dict):
                desc = str(fm.get("description") or "").splitlines()[0]
        except yaml.YAMLError:
            pass
    desc = rewrite_bundled_agent_instructions(desc)
    instructions = body[fm_end + 4 :].lstrip("\n") if fm_end > 0 else body
    instructions = rewrite_bundled_agent_instructions(instructions)
    dest.write_text(
        "\n".join(
            [
                f"# Bundled Codex runtime definition generated from {agent_md.name}.",
                "# This file is package-local. The invoking skill passes its exact path",
                "# to a generic Codex subagent; plugins do not auto-register custom agents.",
                "",
                f"name = {json.dumps(name, ensure_ascii=False)}",
                f"description = {json.dumps(desc, ensure_ascii=False)}",
                "",
                f"developer_instructions = {_toml_multiline(instructions)}",
                "",
            ]
        ),
        encoding="utf-8",
    )


BUNDLED_AGENT_ADAPTER_HEADING = "## Codex Port Adapter - Bundled Agent Resolution"


def _inject_bundled_agent_adapter(
    skill_md: Path, agent_names: list[str], report: TransferReport
) -> None:
    """Make named-agent dispatch fail closed and package-local."""
    if not agent_names:
        return
    text = skill_md.read_text(encoding="utf-8")
    if BUNDLED_AGENT_ADAPTER_HEADING in text:
        return
    names = ", ".join(f"`{name}`" for name in agent_names)
    adapter = f"""

{BUNDLED_AGENT_ADAPTER_HEADING}

This plugin does not assume package-local TOMLs are auto-registered as custom
agents. The required definitions for this skill are bundled at
`../../.codex-agents/<agent-name>.toml`: {names}.

Before every named-agent dispatch:

1. Resolve the exact bundled TOML from this `SKILL.md` directory (strip a
   leading `baransu:` namespace from the requested name).
2. Verify the file exists, then pass its absolute path and the task input to a
   generic Codex subagent. The first instruction to that subagent is to read
   the TOML's `developer_instructions` completely before doing any task work
   and to treat relative paths as relative to the TOML file.
3. If the TOML is missing or unreadable, stop with
   `AGENT_DEFINITION_MISSING: <path>`. Never invent, summarize, or substitute a
   role from the agent name.
"""
    body_start = text.find("\n# ", text.find("\n---", 4) + 4)
    if body_start < 0:
        text = text + adapter
    else:
        heading_end = text.find("\n", body_start + 1)
        if heading_end < 0:
            heading_end = len(text)
        text = text[:heading_end] + adapter + text[heading_end:]
    skill_md.write_text(text, encoding="utf-8")
    report.rewrites.append(
        "注入 bundled agent resolver（定義缺失即 `AGENT_DEFINITION_MISSING`，禁止臨場杜撰）"
    )


def wire_bundled_agent_references(
    plugin_out: Path,
    skill_reports: list[TransferReport],
    agent_names: list[str],
) -> None:
    """Rewrite every live agent reference to a package-local TOML and add guards."""
    bundle_dir = plugin_out / ".codex-agents"
    for report in skill_reports:
        if report.skill_name == "codex-skill-transfer" or report.skipped:
            continue
        used: set[str] = set()
        for path in sorted(report.target.rglob("*.md")):
            text = path.read_text(encoding="utf-8")
            rel_bundle = Path(os.path.relpath(bundle_dir, path.parent)).as_posix()
            for name in agent_names:
                if re.search(rf"(?<![A-Za-z0-9_-])(?:baransu:)?{re.escape(name)}(?![A-Za-z0-9_-])", text):
                    used.add(name)
                patterns = (
                    rf"plugins/baransu/agents/{re.escape(name)}\.md",
                    rf"(?<![A-Za-z0-9_./-])agents/{re.escape(name)}\.md",
                    rf"(?<![A-Za-z0-9_./-]){re.escape(name)}\.md",
                )
                for pattern in patterns:
                    text = re.sub(pattern, f"{rel_bundle}/{name}.toml", text)
            if "*-reviewer.md" in text:
                text = text.replace(
                    "plugins/baransu/agents/*-reviewer.md",
                    f"{rel_bundle}/*-reviewer.toml",
                ).replace(
                    "agents/*-reviewer.md",
                    f"{rel_bundle}/*-reviewer.toml",
                )
            path.write_text(text, encoding="utf-8")
        _inject_bundled_agent_adapter(report.target / "SKILL.md", sorted(used), report)


def copy_plugin_rules(plugin_root: Path, plugin_out: Path) -> int:
    """Copy and Codex-normalize package-level rule documents."""
    source = plugin_root / "rules"
    if not source.is_dir():
        return 0
    target = plugin_out / "rules"
    shutil.copytree(source, target)
    count = 0
    for path in sorted(target.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        new = text.replace("CLAUDE.md", "AGENTS.md")
        new = re.sub(r"(?<![./])skills/", "../skills/", new)
        new = new.replace(".claude/", ".codex/")
        if new != text:
            path.write_text(new, encoding="utf-8")
        count += 1
    return count


def validate_plugin_content_closure(
    plugin_root: Path,
    plugin_out: Path,
    source_agent_names: list[str],
    source_rule_count: int,
) -> None:
    """Fail closed when generated package content has missing live artifacts."""
    errors: list[str] = []
    bundle_dir = plugin_out / ".codex-agents"
    generated_agents = (
        sorted(path.stem for path in bundle_dir.glob("*.toml"))
        if bundle_dir.is_dir()
        else []
    )
    if generated_agents != sorted(source_agent_names):
        errors.append(
            "agent definitions mismatch: "
            f"source={sorted(source_agent_names)!r}, generated={generated_agents!r}"
        )

    generated_rules = (
        sum(1 for _ in (plugin_out / "rules").rglob("*") if _.is_file())
        if (plugin_out / "rules").is_dir()
        else 0
    )
    if generated_rules != source_rule_count:
        errors.append(
            f"rules mismatch: source={source_rule_count}, generated={generated_rules}"
        )

    # Every authored skill/hook file must have an output artifact at the same
    # package-relative path. Generated dependency/cache trees are the only
    # exclusions. Evals are compared byte-for-byte because they are data, not
    # runtime instructions to reinterpret.
    for component in ("skills", "hooks"):
        source_root = plugin_root / component
        target_root = plugin_out / component
        if not source_root.is_dir():
            continue
        # A malformed/unsupported hook surface is already an explicit manual
        # boundary in the transfer report; closure only validates components
        # that were eligible for generation.
        if component == "hooks" and not target_root.is_dir():
            continue
        for source_path in sorted(source_root.rglob("*")):
            if not source_path.is_file():
                continue
            rel = source_path.relative_to(source_root)
            if any(part in {"node_modules", "__pycache__"} for part in rel.parts):
                continue
            target_path = target_root / rel
            if not target_path.is_file():
                errors.append(f"{component}/{rel} has no generated artifact")
                continue
            if "evals" in rel.parts and source_path.read_bytes() != target_path.read_bytes():
                errors.append(f"{component}/{rel} eval data changed during transfer")

    forbidden_runtime_tokens = (
        "CLAUDE_PLUGIN_ROOT",
        "CLAUDE_PLUGIN_DATA",
        "plugins/baransu/agents/",
    )
    for path in sorted(
        list(bundle_dir.glob("*.toml")) + list((plugin_out / "rules").rglob("*.md"))
    ):
        text = path.read_text(encoding="utf-8")
        found = [token for token in forbidden_runtime_tokens if token in text]
        if found:
            errors.append(
                f"{path.relative_to(plugin_out)} retains runtime token(s): "
                + ", ".join(found)
            )

    # Validate every concrete or globbed package-local agent reference from
    # the file that contains it. This catches the exact regression where a
    # variable/path rewrite succeeded textually but the corresponding file was
    # never moved into the Codex package.
    agent_ref = re.compile(
        r"(?P<path>(?:\.\./)*\.codex-agents/"
        r"(?P<name>[A-Za-z0-9_-]+|\*-[A-Za-z0-9_-]+)\.toml)"
    )
    scan_roots = [plugin_out / "skills", bundle_dir, plugin_out / "rules"]
    for root in scan_roots:
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*")):
            if path.suffix not in {".md", ".toml"} or not path.is_file():
                continue
            text = path.read_text(encoding="utf-8")
            for match in agent_ref.finditer(text):
                ref = match.group("path")
                target = path.parent / ref
                if "*" in ref:
                    if not list(target.parent.glob(target.name)):
                        errors.append(
                            f"{path.relative_to(plugin_out)} -> {ref} matches no file"
                        )
                elif not target.resolve().is_file():
                    errors.append(
                        f"{path.relative_to(plugin_out)} -> {ref} is missing"
                    )

    if errors:
        raise OutputGuardError(
            "generated plugin content closure failed:\n  - " + "\n  - ".join(errors)
        )


def transfer_plugin(plugin_root: Path, output_root: Path) -> tuple[list[TransferReport], dict]:
    """Plugin-mode entry point. Returns (skill_reports, plugin_summary).

    The output_root is the *marketplace root* (the dir containing `.agents/`),
    not the plugin tree itself. Codex's marketplace schema requires the plugin
    tree at `<marketplace-root>/plugins/<plugin-name>/`, so:
      output_root/.agents/plugins/marketplace.json
      output_root/plugins/<name>/.codex-plugin/plugin.json
      output_root/plugins/<name>/skills/<skill>/...
      output_root/plugins/<name>/.codex-agents/*.toml
      output_root/plugins/<name>/rules/...
    """
    summary: dict = {
        "manifest_mapped": [],
        "manifest_dropped": [],
        "manifest_manual": [],
        "agent_definitions": 0,
        "rules_copied": 0,
        "skill_count": 0,
        "plugin_name": "",
        "source_components": [],
        "unhandled_components": [],
        "content_closure_verified": False,
    }

    pj_path = plugin_root / ".claude-plugin" / "plugin.json"
    with pj_path.open(encoding="utf-8") as f:
        claude_pj = json.load(f)

    skills_dir = plugin_root / "skills"
    has_skills = skills_dir.is_dir() and any(
        (c / "SKILL.md").is_file() for c in skills_dir.iterdir() if c.is_dir()
    )

    codex_pj, mapped, dropped = translate_plugin_manifest(claude_pj, has_skills)
    summary["manifest_mapped"] = mapped
    summary["manifest_dropped"] = dropped

    manual: list[str] = summary["manifest_manual"]

    # Plugin-level lifecycle hooks now have a first-class Codex package
    # surface. Preserve supported command handlers and report every rejected
    # event/handler explicitly; never invent an event mapping (notably,
    # Claude SessionEnd is NOT Codex Stop).
    source_hooks_path = plugin_root / "hooks" / "hooks.json"
    codex_hooks_doc: dict | None = None
    if source_hooks_path.is_file():
        try:
            source_hooks_doc = json.loads(source_hooks_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            manual.append(f"`hooks/hooks.json` 無法解析：{exc}")
        else:
            codex_hooks_doc = {
                key: value
                for key, value in source_hooks_doc.items()
                if key != "hooks"
            }
            codex_events: dict[str, list[dict]] = {}
            raw_events = source_hooks_doc.get("hooks", {})
            if not isinstance(raw_events, dict):
                manual.append("`hooks/hooks.json` 的 `hooks` 必須是 object；本次未輸出 hooks")
                codex_hooks_doc = None
            else:
                dropped_events: list[str] = []
                hook_env_rewrites = 0
                for event, groups in raw_events.items():
                    if event not in CODEX_HOOK_EVENTS:
                        dropped_events.append(event)
                        manual.append(f"Codex hooks 不支援事件：{event}；未偷換成其他 lifecycle event")
                        continue
                    if not isinstance(groups, list):
                        manual.append(f"Codex hooks event `{event}` 不是 array；已捨棄")
                        continue
                    kept_groups: list[dict] = []
                    for group in groups:
                        if not isinstance(group, dict):
                            manual.append(f"Codex hooks event `{event}` 含非 object matcher group；已捨棄")
                            continue
                        handlers = group.get("hooks", [])
                        if not isinstance(handlers, list):
                            manual.append(f"Codex hooks event `{event}` 的 handler 列表不是 array；已捨棄")
                            continue
                        kept_handlers: list[dict] = []
                        for handler in handlers:
                            handler_type = handler.get("type") if isinstance(handler, dict) else None
                            if handler_type != "command":
                                manual.append(
                                    f"Codex hooks 不支援 handler：{event}/{handler_type or 'unknown'}；已捨棄"
                                )
                                continue
                            kept_handler = dict(handler)
                            command = kept_handler.get("command")
                            if isinstance(command, str):
                                command, root_count = re.subn(
                                    r"\bCLAUDE_PLUGIN_ROOT\b", "PLUGIN_ROOT", command
                                )
                                command, data_count = re.subn(
                                    r"\bCLAUDE_PLUGIN_DATA\b", "PLUGIN_DATA", command
                                )
                                kept_handler["command"] = command
                                hook_env_rewrites += root_count + data_count
                            kept_handlers.append(kept_handler)
                        if kept_handlers:
                            kept_group = dict(group)
                            kept_group["hooks"] = kept_handlers
                            kept_groups.append(kept_group)
                    if kept_groups:
                        codex_events[event] = kept_groups
                if dropped_events and isinstance(codex_hooks_doc.get("description"), str):
                    codex_hooks_doc["description"] += (
                        " [Codex transfer omitted unsupported events: "
                        + ", ".join(dropped_events)
                        + "]"
                    )
                if codex_events:
                    codex_hooks_doc["hooks"] = codex_events
                    codex_pj["hooks"] = "./hooks/hooks.json"
                    mapped.append("hooks/hooks.json → plugin-bundled Codex lifecycle hooks")
                    if hook_env_rewrites:
                        mapped.append(
                            f"hooks command {hook_env_rewrites} 處 Claude plugin env "
                            "改寫為 Codex canonical `PLUGIN_ROOT` / `PLUGIN_DATA`"
                        )
                    manual.append(
                        "Codex plugin hooks 已輸出；安裝或變更後仍須在 `/hooks` review and trust，"
                        "未 trust 前不會執行"
                    )
                else:
                    codex_hooks_doc = None
    elif "hooks" in claude_pj:
        manual.append(
            "來源 manifest 宣告 `hooks` 但沒有預設 `hooks/hooks.json`；"
            "自訂來源形狀需人工映射，本次未輸出 hooks pointer"
        )
    if (
        (plugin_root / "mcp.json").is_file()
        or (plugin_root / ".mcp.json").is_file()
        or "mcpServers" in claude_pj
    ):
        manual.append(
            "來源 plugin 帶 MCP 設定（mcp.json / .mcp.json）：Codex 有對應指標"
            "（`\"mcpServers\": \"./.mcp.json\"`），但伺服器啟用受信任授權把關——"
            "請人工移植並驗證，本次未自動輸出指標"
        )

    # Claude `commands/` → Codex: custom prompts are officially DEPRECATED.
    if (plugin_root / "commands").is_dir() or "commands" in claude_pj:
        manual.append(
            "來源 plugin 帶 `commands/`：Codex custom prompts 已官方棄用——"
            "請將每個 commands/*.md 轉為獨立 Codex skill（目錄 + SKILL.md）；"
            "切勿移植到 `~/.codex/prompts/`（0.117.0 已知 regression 使 prompt 載入失效）"
        )
    plugin_name = codex_pj["name"]
    summary["plugin_name"] = plugin_name

    # Inventory the source before writing output. The converter must not imply
    # a complete port while silently ignoring a new plugin component.
    known_components = {".claude-plugin", "agents", "hooks", "rules", "skills"}
    source_components = sorted(p.name for p in plugin_root.iterdir())
    unhandled_components = [
        name
        for name in source_components
        if name not in known_components
        and name not in {"commands", "mcp.json", ".mcp.json"}
    ]
    summary["source_components"] = source_components
    summary["unhandled_components"] = unhandled_components
    for name in unhandled_components:
        manual.append(
            f"來源頂層 component `{name}` 沒有 Codex 轉換規則；"
            "本次不宣稱內容閉包完整"
        )

    # Clear and rewrite the entire output (same rerun-correctness principle
    # as transfer_one). output_root is the marketplace root. Guard first:
    # every plugin-mode run writes `.agents/plugins/marketplace.json`, so a
    # non-empty output_root without that marker was not generated by this
    # script and must not be destroyed.
    marker = output_root / ".agents" / "plugins" / "marketplace.json"
    if output_root.is_dir() and any(output_root.iterdir()) and not marker.is_file():
        raise OutputGuardError(
            f"refused: output ({output_root}) exists, is non-empty, and has no "
            "generated marker (.agents/plugins/marketplace.json); not wiping a "
            "directory this script did not generate. Remove it yourself or "
            "pick another output dir."
        )
    if output_root.exists():
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True)

    plugin_out = output_root / "plugins" / plugin_name
    plugin_out.mkdir(parents=True)
    cp_dir = plugin_out / ".codex-plugin"
    cp_dir.mkdir()
    # Render plugin.json against the golden template when the manifest's
    # shape fits the standard set (skills + the common pass-through fields).
    # The template uses string scalars for the simple fields; complex fields
    # like `author` (dict) and `keywords` (list) are merged in after parsing.
    # Empty pass-through values get pruned so absent source fields don't
    # leak as empty entries.
    STANDARD_PLUGIN_KEYS = {
        "name", "version", "description", "skills", "interface",
        "author", "homepage", "repository", "license", "keywords", "hooks",
    }
    if has_skills and set(codex_pj.keys()) <= STANDARD_PLUGIN_KEYS:
        rendered = render_template(
            "codex-plugin.template.json",
            {
                "name": codex_pj["name"],
                "version": codex_pj["version"],
                "description": codex_pj["description"],
                "display_name": codex_pj["interface"]["displayName"],
                "short_description": codex_pj["interface"]["shortDescription"],
                "homepage": codex_pj.get("homepage") or "",
                "repository": codex_pj.get("repository") or "",
                "license": codex_pj.get("license") or "",
                "hooks": codex_pj.get("hooks") or "",
            },
            mode="json",
        )
        parsed = json.loads(rendered)
        # Drop empty-string pass-through scalars (template includes them so
        # the canonical shape stays visible; runtime omits them when absent).
        for k in ("homepage", "repository", "license", "hooks"):
            if parsed.get(k) == "":
                parsed.pop(k)
        # Merge complex fields directly from the translated manifest.
        if "author" in codex_pj:
            parsed["author"] = codex_pj["author"]
        if codex_pj.get("keywords"):
            parsed["keywords"] = codex_pj["keywords"]
        (cp_dir / "plugin.json").write_text(
            json.dumps(parsed, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    else:
        (cp_dir / "plugin.json").write_text(
            json.dumps(codex_pj, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    if codex_hooks_doc is not None:
        hooks_out = plugin_out / "hooks"
        shutil.copytree(
            plugin_root / "hooks",
            hooks_out,
            ignore=shutil.ignore_patterns("__pycache__"),
        )
        (hooks_out / "hooks.json").write_text(
            json.dumps(codex_hooks_doc, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    skill_reports: list[TransferReport] = []
    aux_dirs_copied: list[str] = []
    aux_manual: list[str] = []
    if has_skills:
        out_skills = plugin_out / "skills"
        out_skills.mkdir()
        for child in sorted(skills_dir.iterdir()):
            if not child.is_dir():
                continue
            if (child / "SKILL.md").is_file():
                skill_reports.append(transfer_one(child, out_skills))
            else:
                # Non-skill sibling dirs under skills/ (e.g. _shared/) carry
                # cross-skill content referenced by SKILL.md bodies (e.g.
                # _shared/tdd.md cited by think/hunt and the execute agents). Copy
                # verbatim so cross-references resolve, rewrite repo-internal
                # path refs to the Codex layout (same as SKILL.md/references —
                # `_shared/tdd.md` cites `plugins/baransu/agents/*.md` etc. that
                # would otherwise dangle), then run the same Claude-only token
                # scan copy_aux applies to references/ (flag only).
                aux_root = out_skills / child.name
                shutil.copytree(child, aux_root)
                aux_dirs_copied.append(child.name)
                for path in sorted(aux_root.rglob("*.md")):
                    try:
                        text = path.read_text(encoding="utf-8")
                    except (UnicodeDecodeError, OSError):
                        continue
                    rel_to_aux = path.relative_to(aux_root)
                    new_text, n = rewrite_repo_paths(
                        text, "../" * len(rel_to_aux.parts), child.name
                    )
                    if n:
                        path.write_text(new_text, encoding="utf-8")
                        text = new_text
                    found = [
                        label
                        for label, pat in TOKEN_SCAN_PATTERNS
                        if pat.search(text)
                    ]
                    if found:
                        rel = path.relative_to(plugin_out)
                        aux_manual.append(
                            f"`{rel}` 含 Claude-only token（{', '.join(found)}）；"
                            "共用目錄整批拷貝、不自動改寫，請人工確認語境後處理"
                        )
        summary["skill_count"] = len(skill_reports)
        summary["aux_dirs_copied"] = aux_dirs_copied
        summary["aux_manual"] = aux_manual

    agents_dir = plugin_root / "agents"
    agent_names: list[str] = []
    if agents_dir.is_dir():
        agent_dir = plugin_out / ".codex-agents"
        agent_dir.mkdir()
        for md in sorted(agents_dir.glob("*.md")):
            emit_bundled_agent_definition(md, agent_dir / f"{md.stem}.toml")
            agent_names.append(md.stem)
            summary["agent_definitions"] += 1

    # Agent refs in skills and copied shared material must resolve to the
    # package-local definitions above. Relevant SKILL.md files also receive a
    # fail-closed dispatch adapter so a missing definition can never degrade
    # into an improvised agent.
    wire_bundled_agent_references(plugin_out, skill_reports, agent_names)
    summary["rules_copied"] = copy_plugin_rules(plugin_root, plugin_out)
    source_rule_count = (
        sum(1 for path in (plugin_root / "rules").rglob("*") if path.is_file())
        if (plugin_root / "rules").is_dir()
        else 0
    )
    validate_plugin_content_closure(
        plugin_root, plugin_out, agent_names, source_rule_count
    )
    summary["content_closure_verified"] = True

    # Marketplace catalog. See references/marketplace-mapping.md §3 for the
    # required shape: source is an object, policy.installation +
    # policy.authentication are required, category is required.
    marketplace_dir = output_root / ".agents" / "plugins"
    marketplace_dir.mkdir(parents=True)
    marketplace = {
        "name": plugin_name,
        "interface": {
            "displayName": codex_pj.get("interface", {}).get("displayName") or plugin_name,
        },
        "plugins": [
            {
                "name": plugin_name,
                "source": {"source": "local", "path": f"./plugins/{plugin_name}"},
                "policy": {
                    "installation": "AVAILABLE",
                    "authentication": "ON_INSTALL",
                },
                "category": "Productivity",
            }
        ],
    }
    (marketplace_dir / "marketplace.json").write_text(
        json.dumps(marketplace, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    summary["marketplace_written"] = True

    return skill_reports, summary


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        sys.stderr.write(__doc__ or "")
        return 2
    source_root = Path(argv[1]).resolve()
    output_root = Path(argv[2]).resolve()
    if not source_root.is_dir():
        sys.stderr.write(f"source not a directory: {source_root}\n")
        return 2
    # Refuse in-place or overlapping paths. Without this guard, transfer_one's
    # rmtree(target) would delete the source skill before reading it — a
    # silent data-loss path. The contract documented in SKILL.md (§Boundaries)
    # is that source is never mutated.
    if (
        source_root == output_root
        or output_root.is_relative_to(source_root)
        or source_root.is_relative_to(output_root)
    ):
        sys.stderr.write(
            f"refused: source ({source_root}) and output ({output_root}) "
            "overlap; choose a non-overlapping output directory.\n"
        )
        return 2
    mode = detect_mode(source_root)
    if mode == "unknown":
        sys.stderr.write(
            f"refused: source ({source_root}) does not match any recognized shape.\n"
            "  Expected one of:\n"
            "    - <dir>/.claude-plugin/plugin.json  (plugin mode)\n"
            "    - <dir>/SKILL.md                    (single-skill mode)\n"
            "    - <dir>/<child>/SKILL.md            (skills-batch mode)\n"
            "  Marketplace conversion is manual; see references/marketplace-mapping.md.\n"
        )
        return 2

    if mode == "plugin":
        try:
            skill_reports, summary = transfer_plugin(source_root, output_root)
        except OutputGuardError as e:
            sys.stderr.write(f"{e}\n")
            return 2
        print(f"# Codex Transfer — Plugin Mode\n")
        print(f"- 來源 plugin: `{source_root}`")
        print(f"- 輸出 plugin: `{output_root}`")
        print(f"- 寫入 `.codex-plugin/plugin.json`")
        if summary["manifest_mapped"]:
            print(f"- Manifest 翻譯：")
            for n in summary["manifest_mapped"]:
                print(f"    - {n}")
        if summary["manifest_dropped"]:
            print(f"- Manifest 已捨棄：")
            for n in summary["manifest_dropped"]:
                print(f"    - {n}")
        if summary["manifest_manual"]:
            print(f"- Manifest ⚠️ 需人工檢視：")
            for n in summary["manifest_manual"]:
                print(f"    - {n}")
        if summary["agent_definitions"]:
            print(
                f"- Bundled agent definitions 已產出 "
                f"{summary['agent_definitions']} 份至 `.codex-agents/`；"
                "相關 skills 已注入 package-local fail-closed resolver"
            )
        if summary["rules_copied"]:
            print(f"- Rules 已轉換：{summary['rules_copied']} 份至 `rules/`")
        if summary.get("unhandled_components"):
            print(
                "- Content closure ⚠️ 未完成："
                + ", ".join(summary["unhandled_components"])
            )
        else:
            print(
                "- Content closure：來源頂層 components 均已映射或明確列為"
                "既有 manual boundary；所有 authored skill/hook 檔案、agent/rule "
                "數量與 bundled agent references 已驗證可達"
            )
        print(f"- Skills 處理：{summary['skill_count']} 個")
        if summary.get("aux_dirs_copied"):
            print(
                f"- Skills 共用目錄整批拷貝：{', '.join(summary['aux_dirs_copied'])}"
            )
        if summary.get("aux_manual"):
            print(f"- 共用目錄 ⚠️ 需人工檢視：")
            for n in summary["aux_manual"]:
                print(f"    - {n}")
        print(f"- 寫入 `.agents/plugins/marketplace.json` (marketplace 目錄結構：plugins/{summary['plugin_name']}/)")
        print(
            "- End-user install (記得寫進 README)：\n"
            f"    本輸出為 Layout B（自含 marketplace root）：\n"
            f"    `codex plugin marketplace add /local/path/to/{output_root.name}`\n"
            f"    `codex plugin add {summary['plugin_name']}@{summary['plugin_name']}`\n"
            "    （`marketplace add` 註冊來源；`plugin add` 才安裝 plugin。）\n"
            "    若要走 git URL 安裝，需在 repo 根目錄另維護 Layout A catalog —\n"
            f"    `<repo>/.agents/plugins/marketplace.json`，其 `source.path` 指向 "
            f"`./{output_root.name}/plugins/{summary['plugin_name']}`。\n"
            "    詳見 references/marketplace-mapping.md §8。\n"
        )
        reports = skill_reports
    else:
        output_root.mkdir(parents=True, exist_ok=True)
        reports = []
        try:
            if mode == "single-skill":
                reports.append(transfer_one(source_root, output_root))
            else:  # skills-batch (unknown already exited above)
                # Every dir child goes through transfer_one — children without
                # SKILL.md come back as skipped reports (skip_reason: no
                # SKILL.md in source) so the mismatch is named in the report
                # and counted by the ⚠️ stderr summary, never silently dropped.
                for child in sorted(source_root.iterdir()):
                    if not child.is_dir():
                        continue
                    reports.append(transfer_one(child, output_root))
        except OutputGuardError as e:
            sys.stderr.write(f"{e}\n")
            return 2
        print(f"# Codex Transfer Batch Report\n")
        print(f"- 處理 {len(reports)} 個 skill")
        print(f"- 輸出: `{output_root}`")
        print(
            "- 安裝位置：將輸出 skill 目錄複製到 `<repo>/.agents/skills/`（專案）"
            "或 `~/.agents/skills/`（個人）——注意是 `.agents/`，"
            "不是 `.codex/` 或 `.claude/`——重啟 Codex 後生效。\n"
        )
    for r in reports:
        print(r.render())

    skipped = sum(1 for r in reports if r.skipped)
    needs_review = sum(1 for r in reports if r.manual_review)
    if skipped or needs_review:
        sys.stderr.write(
            f"\n⚠️ {skipped} skipped, {needs_review} need manual review.\n"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
