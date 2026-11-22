#!/usr/bin/env python3
"""Find the folder under Claude Code's projects root that holds a project's transcripts and memory.

Claude Code does not document how it names ~/.claude/projects/<folder>, so the folder is found
by the data first: each transcript (*.jsonl) records the "cwd" its session started in, and the
folder whose transcripts record PATH is the project's. Paths compare after normalisation:
separators, a trailing separator, and on Windows the case.

Claude Code prunes old transcripts (cleanupPeriodDays) but keeps memory/, so a project can have
memory and no transcript left to match. With --memory, a PATH no transcript matches falls back to
a folder name derived from the path the way observed on real data (every character that is not an
ASCII letter or digit becomes "-": D:\\Code\\x.y -> D--Code-x-y), taken only when that folder exists
and holds memory/. That result is less certain, and the output says so.

Run as: python3 find_project_dir.py [--memory] PROJECTS_ROOT PATH [PATH ...]
Prints "NAME<TAB>cwd" or "NAME<TAB>name" (folder name, not a path; how it was found) for the
first PATH that has a folder, or nothing. Without --memory only transcripts are matched; with
it each PATH is tried by transcript, then by derived name, before the next PATH.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

FILES_PER_FOLDER = 3  # newest transcripts read per folder
LINES_PER_FILE = 50  # a transcript's first cwd appears within its first few lines


def keys(path: str) -> set[str]:
    def norm(p: str) -> str:
        return os.path.normcase(os.path.normpath(p))

    found = {norm(path)}
    try:
        found.add(norm(os.path.realpath(path)))
    except (OSError, ValueError):
        pass
    return found


def first_cwd(transcript: Path) -> str | None:
    try:
        with transcript.open(encoding="utf-8", errors="replace") as f:
            for _, line in zip(range(LINES_PER_FILE), f):
                try:
                    cwd = json.loads(line).get("cwd")
                except (ValueError, AttributeError):
                    continue
                if isinstance(cwd, str) and cwd:
                    return cwd
    except OSError:
        pass
    return None


def folder_cwds(root: Path) -> list[tuple[float, str, set[str]]]:
    """(newest transcript mtime, folder name, keys of the cwds its newest transcripts start in)."""
    out = []
    try:
        folders = [d for d in root.iterdir() if d.is_dir()]
    except OSError:
        return out
    for folder in folders:
        try:
            transcripts = sorted(
                ((t.stat().st_mtime, t) for t in folder.glob("*.jsonl")), reverse=True
            )[:FILES_PER_FOLDER]
        except OSError:
            continue
        cwd_keys: set[str] = set()
        for _, t in transcripts:
            cwd = first_cwd(t)
            if cwd:
                cwd_keys |= keys(cwd)
        if cwd_keys:
            out.append((transcripts[0][0], folder.name, cwd_keys))
    return out


def derived_name(path: str) -> str:
    """The folder name as observed on real data: every character that is not an ASCII letter or
    digit becomes "-", one per UTF-16 unit (a character outside the BMP gives two)."""
    return "".join(
        c if c.isascii() and c.isalnum() else ("--" if ord(c) > 0xFFFF else "-") for c in path
    )


def memory_folder_by_name(root: Path, path: str) -> str | None:
    """The derived folder, only if it really exists under root and holds memory/."""
    want = os.path.normcase(derived_name(os.path.normpath(path)))
    try:
        for folder in root.iterdir():
            if os.path.normcase(folder.name) == want and (folder / "memory").is_dir():
                return folder.name
    except OSError:
        pass
    return None


def by_cwd(folders: list[tuple[float, str, set[str]]], path: str) -> str | None:
    matches = sorted((m for m in folders if m[2] & keys(path)), reverse=True)
    return matches[0][1] if matches else None


def main(argv: list[str]) -> int:
    args = argv[1:]
    memory = bool(args) and args[0] == "--memory"
    if memory:
        args = args[1:]
    if len(args) < 2:
        print("usage: find_project_dir.py [--memory] PROJECTS_ROOT PATH [PATH ...]", file=sys.stderr)
        return 2
    root = Path(args[0])
    folders = folder_cwds(root)
    for path in args[1:]:
        name = by_cwd(folders, path)
        if name:
            print(f"{name}\tcwd")
            return 0
        if memory:
            name = memory_folder_by_name(root, path)
            if name:
                print(f"{name}\tname")
                return 0
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
