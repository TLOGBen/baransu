#!/usr/bin/env python3
"""Port Claude Code material to Codex format.

Usage:
    python3 transfer.py <source-dir> <output-dir>

Direction is one-way: Claude is the source of truth (where the user's main
work lives), Codex is the secondary target. Three input shapes are auto-
detected:

  - **Plugin** (source has `.claude-plugin/plugin.json`):
        Translates the plugin manifest via assets/codex-plugin.template.json,
        batch-transfers all skills under `<source>/skills/`, and emits TOML
        stubs (assets/agent-stub.template.toml) for each `<source>/agents/*.md`.
        Output tree:
          <output>/.codex-plugin/plugin.json
          <output>/skills/<name>/...
          <output>/.codex-agents-templates/*.toml

  - **Single skill** (source has SKILL.md directly):
        Transfers one skill into <output>/<skill-name>/.

  - **Skills batch** (source's children each have SKILL.md):
        Transfers every child into <output>/<skill-name>/.

Skills containing `context: fork` are skipped with a clear warning. Codex has
a real equivalent (native Subagents at `~/.codex/agents/{name}.toml`) but the
mapping crosses the skill-package boundary into the user's Codex config; see
references/skill-mapping.md §5 for the three viable paths.

Marketplace catalog conversion is NOT automated; see
references/marketplace-mapping.md for the inline rules and
assets/codex-marketplace.template.json for a starting copy.

The script is intentionally conservative: when a rewrite is ambiguous, it
emits a `<!-- TODO(codex-transfer): ... -->` marker rather than guessing.

Output shapes (plugin.json, agents/openai.yaml, agent stub TOML) live in
assets/*.template.* — editing those changes the output without touching the
script.
"""

from __future__ import annotations

import json
import re
import shutil
import string
import sys
from dataclasses import dataclass, field
from pathlib import Path

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

INLINE_BACKTICK_CMD = re.compile(r"!`([^`]+)`")
BLOCK_BACKTICK_CMD = re.compile(r"^```!\s*\n(.*?)^```\s*$", re.MULTILINE | re.DOTALL)
ARGS_FULL = re.compile(r"\$ARGUMENTS\b")
ARGS_INDEXED = re.compile(r"\$ARGUMENTS\[(\d+)\]|\$(\d+)\b")
NAMED_ARG = re.compile(r"\$([a-z][a-z0-9_-]*)\b")
SESSION_ID = re.compile(r"\$\{CLAUDE_SESSION_ID\}")
SKILL_DIR = re.compile(r"\$\{CLAUDE_SKILL_DIR\}|\$CLAUDE_SKILL_DIR\b")
EFFORT = re.compile(r"\$\{CLAUDE_EFFORT\}")


@dataclass
class TransferReport:
    skill_name: str
    source: Path
    target: Path
    lossless: list[str] = field(default_factory=list)
    mapped: list[str] = field(default_factory=list)
    rewrites: list[str] = field(default_factory=list)
    dropped: list[str] = field(default_factory=list)
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
        if self.manual_review:
            lines += ["### ⚠️ 需人工檢視 (manual review)"]
            lines += [f"- {x}" for x in self.manual_review]
            lines += [""]
        return "\n".join(lines)


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

    # Codex enforces a 1024-char limit on `description`. Trim by stripping
    # Claude-style trigger phrase sentences first (these are useless to Codex
    # since Codex skills are command-invoked, not phrase-triggered); fall back
    # to a hard cut at the last sentence boundary if still over budget.
    desc = out["description"]
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
            report.dropped.append(f"`{k}` (no Codex equivalent)")

    return out, openai_yaml


def rewrite_body(
    body: str, report: TransferReport, named_args: list[str] | None = None
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
        nonlocal arg_count
        arg_count += 1
        idx = int(m.group(1) or m.group(2))
        ordinals = ["first", "second", "third", "fourth", "fifth"]
        word = ordinals[idx] if idx < len(ordinals) else f"#{idx + 1}"
        return f"the {word} argument the user provided"

    body = ARGS_INDEXED.sub(args_indexed_sub, body)
    body = ARGS_FULL.sub(args_full_sub, body)

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

    body = SESSION_ID.sub("the current session", body)
    body = SKILL_DIR.sub("the skill's root directory", body)
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

    # `Dispatch <X>-agent` / `Dispatches <X>-agent` → `spawn a `<X>-agent` subagent`.
    def dispatch_sub(m: re.Match[str]) -> str:
        nonlocal tool_count
        tool_count += 1
        return f"spawn a `{m.group(1)}` subagent"

    body = re.sub(r"\bDispatch[s]?\s+`?([a-zA-Z][\w-]*?-agent)`?", dispatch_sub, body)

    # Single-token Claude API references.
    TOKEN_MAP: list[tuple[str, str]] = [
        # Subagent / task plumbing
        (r"\bTask\s+tool\b", "Codex subagent"),
        (r"\bTaskCreate\b", "track the task internally"),
        (r"\bTaskUpdate\b", "update task state internally"),
        (r"\bTaskGet\b", "look up the task internally"),
        (r"\bTaskList\b", "list tracked tasks internally"),
        (r"\bTaskOutput\b", "read tracked task output internally"),
        (r"\bTaskStop\b", "stop the tracked task internally"),
        (r"\bTodoWrite\b", "track steps internally"),
        # User interaction
        (r"\bAskUserQuestion\b", "ask the user directly"),
        # Plan mode (no skill-callable equivalent in Codex)
        (r"\bEnterPlanMode\b", "produce a plan and pause for confirmation"),
        (r"\bExitPlanMode\b", "exit the plan and proceed with edits"),
        # Web access
        (r"\bWebFetch\b", "fetch the URL"),
        (r"\bWebSearch\b", "search the web"),
    ]
    for pat, repl in TOKEN_MAP:
        body, n = re.subn(pat, repl, body)
        tool_count += n

    if tool_count:
        report.rewrites.append(
            f"{tool_count} 處 Claude tool / agent 派遣關鍵字改寫為 Codex 對等敘述（AskUserQuestion / Dispatch X-agent / TaskCreate 等）"
        )

    return body


def write_skill(
    target: Path,
    frontmatter: dict,
    body: str,
    openai_meta: dict | None,
) -> None:
    """Write SKILL.md and (when policy is locked down) agents/openai.yaml.

    The openai.yaml output uses assets/openai.template.yaml so its shape
    stays in sync with the references/skill-mapping.md §2 example.
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


SKILL_DIR_ENV = re.compile(r"\$\{CLAUDE_SKILL_DIR\}|\$CLAUDE_SKILL_DIR\b")


def copy_aux(source: Path, target: Path, report: TransferReport) -> None:
    # Standard auxiliary dirs.
    for sub in ("scripts", "references", "assets"):
        src = source / sub
        if src.is_dir():
            shutil.copytree(src, target / sub, dirs_exist_ok=True)

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

    # `$CLAUDE_SKILL_DIR` rewrite — same logic for scripts/ and references/.
    # Skip transfer.py itself: its source contains the literal regex pattern
    # `\$\{CLAUDE_SKILL_DIR\}|\$CLAUDE_SKILL_DIR\b`, which the rewriter would
    # turn into `\$\{CLAUDE_SKILL_DIR\}|\.\b` (broken) on every self-port.
    rewritten = 0
    rewrite_roots = [target / "scripts", target / "references"]
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
            f"{rewritten} 處 scripts/ + references/ 內的 `${{CLAUDE_SKILL_DIR}}` 改寫為 `.`（skill root）"
        )


def transfer_one(source: Path, output_root: Path) -> TransferReport:
    skill_md = source / "SKILL.md"
    name = source.name
    target = output_root / name
    report = TransferReport(skill_name=name, source=source, target=target)

    # Always clear stale output before producing a fresh result. Without this,
    # rerunning into the same output dir would merge old files (auxiliary
    # resources, agents/openai.yaml from a prior `disable-model-invocation`,
    # etc.) with new ones, leaving artifacts that contradict the current
    # source or this run's report.
    if target.exists():
        shutil.rmtree(target)

    if not skill_md.is_file():
        report.skipped = True
        report.skip_reason = "no SKILL.md in source"
        return report

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

    new_body = rewrite_body(body, report, named_args=named_args)
    write_skill(target, new_fm, new_body, openai_yaml)
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
#   <out>/.codex-agents-templates/*.toml  ← stubs for each agents/*.md (manual)
# It does NOT emit `.codex/agents/*.toml` directly — that lives in the user's
# config dir, outside the plugin package boundary (see mapping.md §5).


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

    Returns (codex_pj, mapped_notes, dropped_notes). Codex requires
    name/version/description and (per the build docs) an explicit `skills`
    pointer when the plugin bundles skills.
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
        mapped.append("`description` 缺，以 `name` 暫代 (Codex 必填)")

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
    for k in ("commands", "lspServers", "agents"):
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
                full = str(fm.get("description") or "").splitlines()[0]
                # Word-boundary truncation: 200-char hard cap was producing
                # mid-word cuts like ".../baransu:exe" — split on whitespace
                # before the boundary and add an ellipsis so cross-skill
                # metadata stays intelligible.
                if len(full) <= 200:
                    desc = full
                else:
                    desc = full[:197].rsplit(" ", 1)[0].rstrip(",;:.") + "…"
                # Tools list — emit as a commented-out mcp_servers suggestion.
                raw_tools = fm.get("tools") or fm.get("allowed-tools")
                if isinstance(raw_tools, str):
                    tools = [t.strip() for t in raw_tools.split(",") if t.strip()]
                elif isinstance(raw_tools, list):
                    tools = [str(t).strip() for t in raw_tools if str(t).strip()]
        except yaml.YAMLError:
            pass

    instructions = body[fm_end + 4 :].lstrip("\n") if fm_end > 0 else body
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

    stub = (
        f"# Stub generated from {agent_md.name}.\n"
        f"# Review before copying to ~/.codex/agents/{name}.toml.\n"
        f"# See codex-skill-transfer references/agent-mapping.md for the mapping rules.\n"
        f"\n"
        f"name = {name_quoted}\n"
        f"description = {desc_quoted}\n"
        f"\n"
        f"developer_instructions = {instructions_block}\n"
        f"\n"
        f"# Choose what to fill in below; all are optional and inherit from parent if absent.\n"
        f"#\n"
        f"# model = \"gpt-5.4\"\n"
        f"# model_reasoning_effort = \"high\"      # low | medium | high | max\n"
        f"# sandbox_mode = \"workspace-write\"     # read-only | workspace-write | danger-full-access\n"
        f"{mcp_line}\n"
        f"# nickname_candidates = []             # cosmetic names for spawned instances\n"
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


def transfer_plugin(plugin_root: Path, output_root: Path) -> tuple[list[TransferReport], dict]:
    """Plugin-mode entry point. Returns (skill_reports, plugin_summary).

    The output_root is the *marketplace root* (the dir containing `.agents/`),
    not the plugin tree itself. Codex's marketplace schema requires the plugin
    tree at `<marketplace-root>/plugins/<plugin-name>/`, so:
      output_root/.agents/plugins/marketplace.json
      output_root/plugins/<name>/.codex-plugin/plugin.json
      output_root/plugins/<name>/skills/<skill>/...
      output_root/plugins/<name>/.codex-agents-templates/*.toml
    """
    summary: dict = {
        "manifest_mapped": [],
        "manifest_dropped": [],
        "agent_stubs": 0,
        "skill_count": 0,
        "plugin_name": "",
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
    plugin_name = codex_pj["name"]
    summary["plugin_name"] = plugin_name

    # Clear and rewrite the entire output (same rerun-correctness principle
    # as transfer_one). output_root is the marketplace root.
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
        "author", "homepage", "repository", "license", "keywords",
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
            },
            mode="json",
        )
        parsed = json.loads(rendered)
        # Drop empty-string pass-through scalars (template includes them so
        # the canonical shape stays visible; runtime omits them when absent).
        for k in ("homepage", "repository", "license"):
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

    skill_reports: list[TransferReport] = []
    aux_dirs_copied: list[str] = []
    if has_skills:
        out_skills = plugin_out / "skills"
        out_skills.mkdir()
        for child in sorted(skills_dir.iterdir()):
            if not child.is_dir():
                continue
            if (child / "SKILL.md").is_file():
                skill_reports.append(transfer_one(child, out_skills))
            else:
                # Non-skill sibling dirs under skills/ (e.g. _shared/,
                # *-workspace/) carry schema files and harness state referenced
                # by SKILL.md bodies. Copy verbatim so cross-references resolve.
                shutil.copytree(child, out_skills / child.name)
                aux_dirs_copied.append(child.name)
        summary["skill_count"] = len(skill_reports)
        summary["aux_dirs_copied"] = aux_dirs_copied

    agents_dir = plugin_root / "agents"
    if agents_dir.is_dir():
        stub_dir = plugin_out / ".codex-agents-templates"
        stub_dir.mkdir()
        for md in sorted(agents_dir.glob("*.md")):
            emit_agent_stub(md, stub_dir / f"{md.stem}.toml")
            summary["agent_stubs"] += 1

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
        skill_reports, summary = transfer_plugin(source_root, output_root)
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
        if summary["agent_stubs"]:
            print(
                f"- Agent stubs 已產出 {summary['agent_stubs']} 份至 "
                f"`.codex-agents-templates/`（請人工檢視後複製至 `~/.codex/agents/`）"
            )
        print(f"- Skills 處理：{summary['skill_count']} 個")
        if summary.get("aux_dirs_copied"):
            print(
                f"- Skills 共用目錄整批拷貝：{', '.join(summary['aux_dirs_copied'])}"
            )
        print(f"- 寫入 `.agents/plugins/marketplace.json` (marketplace 目錄結構：plugins/{summary['plugin_name']}/)")
        print(
            "- End-user install (記得寫進 README)：\n"
            f"    `codex plugin marketplace add <git-url> --sparse {output_root.name} [--ref <tag>]`\n"
            f"    `codex plugin install {summary['plugin_name']}`\n"
            "    必須帶 `--sparse <output-dir>`，否則 Codex 會在 repo 根目錄找不到 `.agents/plugins/marketplace.json`。\n"
        )
        reports = skill_reports
    else:
        output_root.mkdir(parents=True, exist_ok=True)
        reports = []
        if mode == "single-skill":
            reports.append(transfer_one(source_root, output_root))
        else:  # skills-batch or unknown (treat as batch)
            for child in sorted(source_root.iterdir()):
                if not child.is_dir():
                    continue
                if not (child / "SKILL.md").is_file():
                    continue
                reports.append(transfer_one(child, output_root))
        print(f"# Codex Transfer Batch Report\n")
        print(f"- 處理 {len(reports)} 個 skill")
        print(f"- 輸出: `{output_root}`\n")
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
