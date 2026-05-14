#!/usr/bin/env python3
"""Run skill-creator's run_loop with subscription auth (claude -p) instead of API key."""
import subprocess
import sys
from pathlib import Path

SC = Path("/home/vakarve/.claude/plugins/cache/claude-plugins-official/skill-creator/unknown/skills/skill-creator")
sys.path.insert(0, str(SC))


class _Block:
    def __init__(self, type_, text):
        self.type = type_
        self.thinking = text if type_ == "thinking" else ""
        self.text = text if type_ == "text" else ""


class _Response:
    def __init__(self, text):
        self.content = [_Block("text", text)]


class _Messages:
    def create(self, *, model, messages, **_kw):
        parts = []
        for m in messages:
            c = m["content"] if isinstance(m["content"], str) else "\n".join(
                b.get("text", "") for b in m["content"]
            )
            if m["role"] == "assistant":
                c = f"(prior assistant reply:\n{c}\n)"
            parts.append(c)
        prompt = "\n\n".join(parts)
        r = subprocess.run(
            ["claude", "-p", "--model", model, "--output-format", "text"],
            input=prompt, capture_output=True, text=True, timeout=600,
        )
        if r.returncode != 0:
            raise RuntimeError(f"claude -p failed (rc={r.returncode}): {r.stderr[:500]}")
        return _Response(r.stdout)


class _Client:
    def __init__(self, *_a, **_kw):
        self.messages = _Messages()


import anthropic
anthropic.Anthropic = _Client

from scripts.run_loop import main
main()
