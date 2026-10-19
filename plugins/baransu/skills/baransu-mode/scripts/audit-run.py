#!/usr/bin/env python3
"""Reconcile a baransu-mode ledger against the session transcript.

For each ledger row whose 叫用 column names a skill, report whether the
transcript holds a Skill tool call for it. Also list Bash calls that ran a
git write (commit, push, merge, branch -D, reset, rebase), which the mode
only allows inside /ship. Reads only; prints a Traditional Chinese report.

Usage: audit-run.py --ledger <path> [--transcript <session.jsonl>]
Without --transcript, the newest *.jsonl under ~/.claude/projects/ is used.
"""
import argparse
import json
import re
import sys
from pathlib import Path

GIT_WRITE = re.compile(r"\bgit\b[^|;&\n]*\b(commit|push|merge|rebase|reset|branch\s+-[dD])\b")


def newest_transcript() -> Path:
    files = sorted(Path.home().glob(".claude/projects/*/*.jsonl"), key=lambda p: p.stat().st_mtime)
    if not files:
        sys.exit("找不到對話紀錄（~/.claude/projects/*/*.jsonl）；請用 --transcript 指定。")
    return files[-1]


def tool_calls(transcript: Path):
    """Yield (name, input) for each tool call whose result was not an error."""
    calls, failed = [], set()
    for line in transcript.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        content = (entry.get("message") or {}).get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "tool_use":
                calls.append((block.get("id"), block.get("name", ""), block.get("input") or {}))
            elif block.get("type") == "tool_result" and block.get("is_error"):
                failed.add(block.get("tool_use_id"))
    for call_id, name, inp in calls:
        if call_id not in failed:
            yield name, inp


def ledger_rows(ledger: Path):
    rows = []
    for line in ledger.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 4 and cells[0].isdigit():
            rows.append({"n": cells[0], "step": cells[1], "invoked": cells[2], "status": cells[3]})
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", required=True, type=Path)
    ap.add_argument("--transcript", type=Path)
    args = ap.parse_args()
    transcript = args.transcript or newest_transcript()

    skills, git_writes = [], []
    for name, inp in tool_calls(transcript):
        if name == "Skill":
            skills.append(str(inp.get("skill", "")))
        elif name == "Bash" and GIT_WRITE.search(str(inp.get("command", ""))):
            git_writes.append(str(inp.get("command", "")).splitlines()[0][:120])

    print(f"對話紀錄：{transcript}")
    print(f"Skill 呼叫：{', '.join(skills) or '（無）'}")
    missing = 0
    for row in ledger_rows(args.ledger):
        want = row["invoked"]
        if want in ("", "—", "-"):
            print(f"- 第 {row['n']} 步 {row['step']}：帳本未記叫用（{row['status']}）")
            continue
        found = want in skills
        missing += 0 if found else 1
        mark = "有叫用" if found else "找不到叫用 → 記為 未執行"
        print(f"- 第 {row['n']} 步 {row['step']}：{want} {mark}（帳本：{row['status']}）")
    if git_writes:
        print("直接執行的 git 寫入指令（mode 只允許經由 /ship）：")
        for cmd in git_writes:
            print(f"  - {cmd}")
    print(f"結果：{missing} 步帳本有記但紀錄裡找不到叫用；{len(git_writes)} 筆直接 git 寫入。")
    return 1 if missing or git_writes else 0


if __name__ == "__main__":
    sys.exit(main())
