#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify-codex-parity.py — 手動維護的 Codex 版與 Claude 版逐檔配對檢查。

Codex 版（codex/plugins/baransu/）改為手動維護後，不再以 transfer.py 重產比對；
本腳本只檢查「結構上沒有漏同步」：

  1. plugins/baransu/skills/** 每個檔案在 codex/plugins/baransu/skills/** 有同路徑對應，
     反之亦然；CODEX_ONLY 樣式（skill 內的 agents/openai.yaml 與 agents/icon-*.png）允許只存在於 Codex 版。
  2. Claude 版 plugin.json 與 Codex 版 plugin.json 的 version 相同。

內容是否正確移植不在本腳本範圍——那是 /codex-skill-transfer 檢查清單的工作。

用法：
  python3 scripts/verify-codex-parity.py                       # repo 預設路徑
  python3 scripts/verify-codex-parity.py <claude-plugin> <codex-plugin>   # fixture 測試用

Exit：0 = 配對一致；1 = 有漂移（一次列出全部）；2 = 檔案無法解析。
標準函式庫 only。
"""

from __future__ import annotations

import fnmatch
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CLAUDE = REPO_ROOT / "plugins" / "baransu"
DEFAULT_CODEX = REPO_ROOT / "codex" / "plugins" / "baransu"

IGNORED_PARTS = {"__pycache__", "node_modules", ".DS_Store"}
# 相對於 skills/ 的路徑樣式：只允許存在於 Codex 版。
CODEX_ONLY = ("*/agents/openai.yaml", "*/agents/icon-*.png")


def skill_files(root: Path) -> set[str]:
    if not root.is_dir():
        return set()
    return {
        p.relative_to(root).as_posix()
        for p in root.rglob("*")
        if p.is_file() and not (IGNORED_PARTS & set(p.relative_to(root).parts))
    }


def read_version(manifest: Path) -> str | None:
    try:
        return json.loads(manifest.read_text(encoding="utf-8")).get("version")
    except (OSError, json.JSONDecodeError) as exc:
        print(f"無法解析 {manifest}：{exc}")
        sys.exit(2)


def check(claude_plugin: Path, codex_plugin: Path) -> list[str]:
    v: list[str] = []
    claude = skill_files(claude_plugin / "skills")
    codex = skill_files(codex_plugin / "skills")
    if not claude:
        v.append(f"Claude 版沒有 skills：{claude_plugin / 'skills'}")
    for rel in sorted(claude - codex):
        v.append(f"Codex 版缺檔：skills/{rel}")
    for rel in sorted(codex - claude):
        if not any(fnmatch.fnmatch(rel, pat) for pat in CODEX_ONLY):
            v.append(f"Codex 版多出（Claude 版沒有）：skills/{rel}")
    cv = read_version(claude_plugin / ".claude-plugin" / "plugin.json")
    xv = read_version(codex_plugin / "plugin.json")
    if cv != xv:
        v.append(f"version 不一致：Claude {cv!r} vs Codex {xv!r}")
    return v


def main(argv: list[str]) -> int:
    if len(argv) == 3:
        claude_plugin, codex_plugin = Path(argv[1]), Path(argv[2])
    elif len(argv) == 1:
        claude_plugin, codex_plugin = DEFAULT_CLAUDE, DEFAULT_CODEX
    else:
        print(__doc__)
        return 2
    violations = check(claude_plugin, codex_plugin)
    if violations:
        print("== CODEX PARITY DRIFT — sync the Codex copy by hand:")
        for line in violations:
            print(f"  {line}")
        return 1
    print("== codex parity OK (skills file pairing + version)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
