#!/usr/bin/env python3
"""hypothesis.py — the read side of /baransu:hypothesis.

The only interface reader skills use. Two subcommands:

  status [path...]          which hypotheses cover these paths, their state now, their rules and findings
  check  [path...|area...]  the same, after rerunning each in-sync hypothesis's checks

States shown: 成立 待釐清 不成立 無法寫成 過期 舊位置. A stale hypothesis never prints 成立.
Exit: 0 all 成立/無法寫成; 1 any 不成立/待釐清; 2 any 過期/舊位置; 3 could not run or 與紀錄不符.

Never writes. Never runs a shell: every external call is an argv list. Standard library only.
Contract it reads: references/area.md §The contract. (sketch: bodies unimplemented)
"""
from __future__ import annotations

import dataclasses
import pathlib
import sys

ROOT = pathlib.Path(".claude/hypothesis")
LEGACY_ROOT = pathlib.Path(".claude/prove-it/formal")


@dataclasses.dataclass
class Area:
    name: str
    readme: pathlib.Path
    verdict: str            # holds | open | broken | cannot (stored)
    sync: str
    covers: list[tuple[str, str, str]]   # (path, blob, label)
    rules: list[str]
    findings: list[str]
    checks: list[str]
    tool: str
    bounds: str
    legacy: bool = False


@dataclasses.dataclass
class Shown:
    area: Area
    state: str              # 成立 待釐清 不成立 無法寫成 過期 舊位置 與紀錄不符
    note: str               # 同步於 <sync> | <path> 在 <sync> 之後改過 | ...


def parse_front_matter(text: str) -> dict[str, str | list[str]]:
    """YAML subset: `key: scalar` and `key:` followed by `  - scalar` lines. Anything else → ValueError."""
    raise NotImplementedError


def load_areas() -> list[Area]:
    """Glob ROOT/*/README.md (dot-dirs skipped) and LEGACY_ROOT/*/README.md (legacy=True, fields left empty).
    A README that does not parse is still returned, with verdict '' so it shows as 過期."""
    raise NotImplementedError


def blob(path: str) -> str | None:
    """`git hash-object -- <path>` as argv; None when the file is missing."""
    raise NotImplementedError


def freshness(area: Area) -> Shown:
    """Legacy → 舊位置. Any covers line whose blob differs or file is missing, or no covers, or parse failure → 過期.
    Otherwise the stored verdict's 顯示."""
    raise NotImplementedError


def touching(areas: list[Area], paths: list[str]) -> list[Area]:
    """Areas whose covers contain, or sit under, any given path; an area name in paths selects it directly.
    Empty paths → all areas (status) or working-tree changes vs HEAD plus untracked (check)."""
    raise NotImplementedError


# Tool adapters: how one `checks` line is run and how its result is read. Added when a tool is first used;
# slice one ships tlc and tlc-reach only. The jar comes from $TLA2TOOLS_JAR — never a machine path in a README.
ADAPTERS: dict[str, object] = {
    # "tlc":       safety rule — exit 0 → holds; invariant violation → broken
    # "tlc-reach": goal rule — checks ~Goal as an invariant; a violation (a trace reaching the goal) → holds
}


def rerun(area: Area) -> Shown:
    """Run each checks line through its adapter, cwd = the area dir, with a timeout. Compare per-rule results with
    the stored rule statuses: any difference on an unchanged source → 與紀錄不符."""
    raise NotImplementedError


def render(shown: list[Shown], with_rule_status: bool) -> str:
    """`<area>\t<state>\t<note>\t<README>`, then rules indented (status only when in sync), then findings."""
    raise NotImplementedError


def exit_code(shown: list[Shown]) -> int:
    raise NotImplementedError


def main(argv: list[str]) -> int:
    """status | check | --help (prints the module docstring: the reader contract)."""
    raise NotImplementedError


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
