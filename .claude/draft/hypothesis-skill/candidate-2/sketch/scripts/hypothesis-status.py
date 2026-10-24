#!/usr/bin/env python3
"""hypothesis-status — the one read-only view every reader skill uses.

Answers, for a selector, in one call: which hypotheses cover these files, are they in
sync, what do they say, did they pass. Freshness is computed here at read time from
content hashes; nothing it prints is cached. It never writes a file.

Usage:
  hypothesis-status.py (--diff BASE | --files PATH... | --area AREA | --all) [--json]
  hypothesis-status.py (--rules | --paths | --scope | --check) AREA [--json]

Exit: 0 every listed area proved; 10 none covers the selector; 1 any other state listed;
      2 the script failed (readers treat as `broken`).

Stdlib only, Python 3.9+, no git required except for --diff and watch patterns
(without git those make every area with watches `stale` with why `no-git`).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Sequence

SCHEMA = "baransu.hypothesis/1"
ROOT = Path(".claude/hypothesis")
LEGACY_ROOT = Path(".claude/prove-it/formal")

State = Literal["broken", "draft", "stale", "legacy", "proved", "disproved", "unformalized"]
SHOWS_VERDICT: frozenset[State] = frozenset({"proved", "disproved"})


@dataclass(frozen=True)
class Why:
    """One reason an area is not fresh. kind ∈ changed | missing | new-writer | writer-gone
    | artifact-edited | no-evidence | schema | no-git | unpublished."""
    kind: str
    subject: str  # a path, a rule id, or a schema string


@dataclass(frozen=True)
class Row:
    area: str
    state: State
    rules: int
    sync: str            # short commit, or "<doc>@<version>" for documents
    why: tuple[Why, ...]
    dir: Path


def hash_lf(path: Path) -> str | None:
    """sha256 of the file's bytes with CRLF→LF; None when the file is missing."""
    raise NotImplementedError


def load_record(area_dir: Path) -> dict | None:
    """Parse hypothesis.json; None when absent or unparseable."""
    raise NotImplementedError


def watch_matches(pattern: str) -> list[str] | None:
    """Sorted repo-relative paths from `git grep -l --untracked -E pattern`; None without git."""
    raise NotImplementedError


def compute_state(area_dir: Path) -> Row:
    """First match wins, in this order — the order is the contract (reading.md § States):
    1. no hypothesis.json → draft (why unpublished); unparseable / wrong schema → broken
    2. any sync.artifact hash differs or file missing → draft (artifact-edited)
    3. any sync.files hash differs or file missing → stale (changed / missing)
    4. any sync.watch matched set differs → stale (new-writer / writer-gone)
    5. verdict proved|disproved without complete seen_failing / seen_succeeding,
       or a reason record with an empty field or unknown class,
       or a file cited in model_map / rules[].cites that is absent from sync.files → draft (no-evidence)
    6. otherwise → check.verdict_at_sync
    """
    raise NotImplementedError


def legacy_rows() -> list[Row]:
    """One `legacy` row per .claude/prove-it/formal/<area>/ not named by any migrated_from."""
    raise NotImplementedError


def covering(rows: Sequence[Row], files: Sequence[str]) -> list[Row]:
    """Rows whose sync.files, current watch matches, or recorded watch matches meet `files`.
    Legacy rows cover by the files their README coverage map names (best effort, marked)."""
    raise NotImplementedError


def changed_since(base: str) -> list[str]:
    """`git diff --name-only base` ∪ working tree ∪ untracked, repo-relative, sorted."""
    raise NotImplementedError


def print_table(rows: Sequence[Row], as_json: bool) -> None:
    """Columns: area  state  rules  sync  why. why is '-' or 'kind: subject; …'."""
    raise NotImplementedError


def print_detail(row: Row, view: Literal["rules", "paths", "scope", "check"], as_json: bool) -> None:
    """Header '# <area>  state=<state>'. For rules/paths, every per-rule verdict is printed
    as '?' unless row.state in SHOWS_VERDICT — a reader can never quote a stale pass."""
    raise NotImplementedError


def exit_code(rows: Sequence[Row]) -> int:
    """0 if rows and all proved; 10 if no rows; else 1."""
    raise NotImplementedError


def main(argv: Sequence[str] | None = None) -> int:
    raise NotImplementedError


if __name__ == "__main__":
    raise SystemExit(main())
