#!/usr/bin/env python3
"""Batch-port Claude Code skills to Codex format.

Usage:
    python3 transfer.py <source-skills-dir> <output-skills-dir>

Reads every immediate subdirectory of <source-skills-dir> that contains a
SKILL.md, applies the transformation rules documented in references/mapping.md,
and writes the Codex version under <output-skills-dir>/<skill-name>/.

Skills containing `context: fork` are skipped with a clear warning, since the
correct strategy is human judgment — see mapping.md §5.

The script is intentionally conservative: when a rewrite is ambiguous, it
emits a `# TODO(codex-transfer): ...` marker in the body rather than guessing.
"""

from __future__ import annotations

import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path

try:
    import yaml  # type: ignore
except ImportError:
    sys.stderr.write("Missing dependency: pyyaml. Install with `pip install pyyaml`.\n")
    sys.exit(2)


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
SKILL_DIR = re.compile(r"\$\{CLAUDE_SKILL_DIR\}")
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
            "interface": {
                "display_name": str(fm["name"]).replace("-", " ").title(),
                "short_description": str(fm["description"]).split(".")[0][:120],
            },
            "policy": {"allow_implicit_invocation": False},
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

    return body


def write_skill(target: Path, frontmatter: dict, body: str, openai_yaml: dict | None) -> None:
    target.mkdir(parents=True, exist_ok=True)
    fm_text = yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=True).strip()
    skill_md = f"---\n{fm_text}\n---\n\n{body.lstrip()}"
    (target / "SKILL.md").write_text(skill_md, encoding="utf-8")
    if openai_yaml is not None:
        (target / "agents").mkdir(exist_ok=True)
        (target / "agents" / "openai.yaml").write_text(
            yaml.safe_dump(openai_yaml, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )


SKILL_DIR_ENV = re.compile(r"\$\{CLAUDE_SKILL_DIR\}")


def copy_aux(source: Path, target: Path, report: TransferReport) -> None:
    for sub in ("scripts", "references", "assets"):
        src = source / sub
        if src.is_dir():
            shutil.copytree(src, target / sub, dirs_exist_ok=True)

    scripts_dir = target / "scripts"
    if not scripts_dir.is_dir():
        return

    rewritten = 0
    for path in scripts_dir.rglob("*"):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if "${CLAUDE_SKILL_DIR}" not in text:
            continue
        new_text, n = SKILL_DIR_ENV.subn(".", text)
        if n:
            path.write_text(new_text, encoding="utf-8")
            rewritten += n
    if rewritten:
        report.rewrites.append(
            f"{rewritten} 處 scripts/ 內的 `${{CLAUDE_SKILL_DIR}}` 改寫為 `.`（skill root，需從 skill 根目錄執行）"
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
            "`context: fork` / `agent` — Codex 無 forked subagent，"
            "拒絕產出檔案以免靜默丟失執行邊界。請人工重設計後再轉。"
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
    output_root.mkdir(parents=True, exist_ok=True)

    reports: list[TransferReport] = []
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
