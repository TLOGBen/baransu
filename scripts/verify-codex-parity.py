#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify-codex-parity.py — 手動維護的 Codex 版與 Claude 版逐檔配對檢查。

Codex 版（codex/plugins/baransu/）是手動維護的；本腳本只檢查「結構上沒有漏同步」：

  1. plugins/baransu/skills/** 每個檔案在 codex/plugins/baransu/skills/** 有同路徑對應，
     反之亦然；CODEX_ONLY 樣式（skill 內的 agents/openai.yaml 與 assets/icon-*.png）允許只存在於 Codex 版。
  2. Claude 版 plugin.json 與 Codex 版 plugin.json 的 version 相同。
  3. Codex 版的 hooks/lint.mjs 第一行記的原始碼雜湊，等於 lint 引擎與 Codex adapter 現在的原始碼
     （plugins/baransu/hooks/{engine,util,adapters/codex}/ 的 .ts）；不等就是改了原始碼沒重跑 make codex-lint。

內容是否正確移植不在本腳本範圍——那是 /codex-skill-transfer 稽核的工作（慣例見 docs/development.md）。

用法：
  python3 scripts/verify-codex-parity.py                       # repo 預設路徑
  python3 scripts/verify-codex-parity.py <claude-plugin> <codex-plugin>   # fixture 測試用
  python3 scripts/verify-codex-parity.py --lint-hash           # 印出原始碼雜湊（make codex-lint 寫進 lint.mjs）

Exit：0 = 配對一致；1 = 有漂移（一次列出全部）；2 = 檔案無法解析。
標準函式庫 only。
"""

from __future__ import annotations

import fnmatch
import hashlib
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CLAUDE = REPO_ROOT / "plugins" / "baransu"
DEFAULT_CODEX = REPO_ROOT / "codex" / "plugins" / "baransu"

IGNORED_PARTS = {"__pycache__", "node_modules", ".DS_Store"}
# 相對於 skills/ 的路徑樣式：只允許存在於 Codex 版。
CODEX_ONLY = ("*/agents/openai.yaml", "*/assets/icon-*.png")


def skill_files(root: Path) -> set[str]:
    if not root.is_dir():
        return set()
    return {
        p.relative_to(root).as_posix()
        for p in root.rglob("*")
        if p.is_file() and not (IGNORED_PARTS & set(p.relative_to(root).parts))
    }


# The folders whose .ts files make up the Codex lint bundle (Makefile codex-lint).
LINT_SOURCES = ("hooks/engine", "hooks/util", "hooks/adapters/codex")
LINT_HASH = re.compile(r"sources sha256:([0-9a-f]{64})")


def lint_hash(claude_plugin: Path) -> str:
    """One hash of how the bundle is made: the Makefile's esbuild line, then every bundle source (its path and
    its text with line ends as LF) in path order. A source edited, or the build changed, without a rebuild
    leaves lint.mjs's recorded hash behind."""
    h = hashlib.sha256()
    makefile = REPO_ROOT / "Makefile"
    if makefile.is_file():
        build = [l.strip() for l in makefile.read_text(encoding="utf-8").splitlines() if "esbuild@" in l]
        h.update("\n".join(build).encode() + b"\0")
    files = sorted(
        p for d in LINT_SOURCES for p in (claude_plugin / d).rglob("*.ts")
        if p.is_file() and not (IGNORED_PARTS & set(p.parts))
    )
    for p in files:
        h.update(p.relative_to(claude_plugin).as_posix().encode() + b"\0")
        h.update(p.read_bytes().replace(b"\r\n", b"\n") + b"\0")
    return h.hexdigest()


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
    bundle = codex_plugin / "hooks" / "lint.mjs"
    if (claude_plugin / LINT_SOURCES[2]).is_dir():
        try:
            head = bundle.read_text(encoding="utf-8").split("\n", 1)[0]
        except OSError:
            head = ""
        m = LINT_HASH.search(head)
        if not m:
            v.append("Codex 版 hooks/lint.mjs 不存在或沒有原始碼雜湊：跑 make codex-lint")
        elif m.group(1) != lint_hash(claude_plugin):
            v.append("Codex 版 hooks/lint.mjs 和 lint 原始碼不一致：跑 make codex-lint 並 commit 結果")
    return v


def main(argv: list[str]) -> int:
    # Its findings are Chinese: cp950 consoles would fail or garble them.
    out = getattr(sys.stdout, "reconfigure", None)
    if out:
        out(encoding="utf-8")
    err = getattr(sys.stderr, "reconfigure", None)
    if err:
        err(encoding="utf-8")
    if argv[1:] == ["--lint-hash"]:
        print(lint_hash(DEFAULT_CLAUDE))
        return 0
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
    print("== codex parity OK (skills file pairing + version + lint bundle)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
