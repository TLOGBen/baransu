#!/usr/bin/env python3
"""hypothesis-status — the one read interface every reader skill calls.

Reads `.claude/hypothesis/*/README.md` frontmatter (and legacy
`.claude/prove-it/formal/*/README.md`), computes `stale` and `legacy`,
prints JSON. Read-only: it never writes anywhere.

Usage:
  hypothesis-status.py --all [--json]
  hypothesis-status.py --area <slug> [--json]
  hypothesis-status.py --covering <path> [<path> ...] [--json]
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Literal

Status = Literal["proved", "disproved", "draft", "unformalizable"]
Role = Literal["subject", "rules", "behaviour"]


@dataclass(frozen=True)
class SourceEntry:
    role: Role
    kind: str            # a file name under references/sources/
    fields: dict         # kind-specific sync fields (commit + covers, or path + sha256 ...)


@dataclass(frozen=True)
class Hypothesis:
    area: str
    status: Status
    revision: int
    sources: tuple[SourceEntry, ...]
    tool: dict           # name, version, cwd, command, bounds
    rules: tuple[dict, ...]
    findings: tuple[dict, ...]
    legacy: bool         # still under .claude/prove-it/formal/


# The executable half of each source adapter's § Stale. One function per kind;
# a new source adapter adds one entry here and nothing else in this file.
def stale_code(entry: SourceEntry, repo: Path) -> bool:
    """git diff --name-only <commit>..HEAD -- <covers>, or covers dirty."""
    raise NotImplementedError


def stale_document(entry: SourceEntry, repo: Path) -> bool:
    """sha256 of the original file != recorded sha256."""
    raise NotImplementedError


STALE: dict[str, Callable[[SourceEntry, Path], bool]] = {
    "code": stale_code,
    "document": stale_document,
}
# `pair` never appears here: a pair writes two entries, each of a leaf kind.


def load(readme: Path) -> Hypothesis:
    raise NotImplementedError


def is_stale(h: Hypothesis, repo: Path) -> bool:
    """Any source entry stale; an unknown kind counts as stale, never as fresh."""
    raise NotImplementedError


def covering(hs: list[Hypothesis], paths: list[str]) -> list[Hypothesis]:
    """Hypotheses whose code entries' covers, or document entries' path, include a path."""
    raise NotImplementedError


def main() -> int:
    raise NotImplementedError


if __name__ == "__main__":
    raise SystemExit(main())
