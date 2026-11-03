"""Turn a project's one-file-per-check `checks/` folder into collections: `lint.toml` + `sets/`. Used by `/lint sync`.

  python migrate-sets.py <checks-folder> <preset-folder> <out-folder>

Writes into <out-folder> only (never touches the checks folder):
  sets/baransu-<group>.toml   one per preset group the project uses: the preset's checks as [check.<id>] tables
                              (a preset `strict.toml` level is kept as each check's `strict` field)
  lint.toml                   [[extends]] for those sets — `only` lists the checks the project had copied — then,
                              per project check: nothing when it equals the preset's, a patch of the differing
                              fields when the action is the same, a whole definition when the action differs or
                              the check is the project's own
Reads `files` as `file` first (migrate-scope.py's rule), so a pre-8.43 folder migrates in one step.
Prints one line per check and what it became. Exit 0.
"""
import re
import sys
import tomllib
from pathlib import Path

ACTIONS = ("forbid", "run", "builtin")
SKIP = {"from", "origin"}  # provenance, not behaviour
GROUPS = ("general", "personal")  # preset folders that become collections; strict is folded into `strict` fields


def load(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"(?m)^(\s*)files(\s*=)", r"\1file\2", text)
    return tomllib.loads(text)


def lit(v) -> str:
    if isinstance(v, list):
        return "[" + ", ".join(lit(x) for x in v) + "]"
    s = str(v)
    if "'" not in s and "\n" not in s:
        return f"'{s}'"
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


def table(header: str, fields: dict) -> str:
    lines = [f"[{header}]"] + [f"{k} = {lit(v)}" for k, v in fields.items() if not isinstance(v, dict)]
    out = "\n".join(lines) + "\n"
    for k, v in fields.items():
        if isinstance(v, dict):
            out += table(f"{header}.{k}", v)
    return out


def behaviour(c: dict) -> dict:
    return {k: v for k, v in c.items() if k not in SKIP}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) != 4:
        print(__doc__)
        return 2
    checks_dir, preset_dir, out = (Path(a) for a in sys.argv[1:])
    preset: dict[str, tuple[str, dict]] = {}
    for g in GROUPS:
        for f in sorted((preset_dir / g / "checks").glob("*.toml")):
            preset[f.stem] = (g, behaviour(load(f)))
    # strict: a strict-only check joins general with severity off and strict on; the three raised checks get strict.
    for f in sorted((preset_dir / "strict" / "checks").glob("*.toml")):
        c = behaviour(load(f))
        c["strict"] = c.get("severity", "warn")
        c["severity"] = "off"
        preset[f.stem] = ("general", c)
    for cid in ("built-before-commit", "up-to-date", "private-key-material"):
        if cid in preset:
            preset[cid][1]["strict"] = "error"

    project = {f.stem: load(f) for f in sorted(checks_dir.glob("*.toml"))}
    used: dict[str, list[str]] = {g: [] for g in GROUPS}
    own: list[str] = []
    for cid, c in project.items():
        if cid in preset:
            g, p = preset[cid]
            used[g].append(cid)
            base = {k: v for k, v in p.items() if k != "strict"}
            mine = behaviour(c)
            same_action = all(mine.get(a) == base.get(a) for a in ACTIONS)
            if not same_action:
                own.append(table(f"check.{cid}", mine))
                print(f"{cid}: 預設規則，動作改過 → lint.toml 定義")
                continue
            diff = {k: v for k, v in mine.items() if base.get(k) != v}
            gone = [k for k in base if k not in mine]
            for k in gone:  # a field the preset has and the project dropped: reset it to what absent means
                diff[k] = [] if isinstance(base[k], list) else ("all" if k == "scope" else "")
            if diff:
                own.append(table(f"check.{cid}", diff))
                print(f"{cid}: 預設規則 → 修補 {', '.join(diff)}")
            else:
                print(f"{cid}: 預設規則，沒改 → extends")
        else:
            own.append(table(f"check.{cid}", behaviour(c)))
            print(f"{cid}: 專案自己的 → lint.toml 定義")

    (out / "sets").mkdir(parents=True, exist_ok=True)
    main_text = "# Collections this project loads, then what it changes and adds (lint-collections).\n"
    for g in GROUPS:
        if not used[g]:
            continue
        body = "".join(table(f"check.{cid}", c) for cid, (gg, c) in preset.items() if gg == g)
        (out / "sets" / f"baransu-{g}.toml").write_text(f'from = "baransu-preset"\n\n{body}', encoding="utf-8", newline="\n")
        main_text += f'\n[[extends]]\nset = "sets/baransu-{g}.toml"\nonly = {lit(sorted(used[g]))}\n'
    main_text += "\n" + "\n".join(own)
    (out / "lint.toml").write_text(main_text, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
