"""Move a project's `.claude/lint/` to the 8.44 layout. Used by `/lint sync`.

  python migrate-layout.py <lint-folder>            write the new files; print what the old ones were
  python migrate-layout.py <lint-folder> --remove   delete the old files, nothing else (run alone, after checking the new)

The 8.44 layout:
  config.toml        [settings] (converter, sgconfig) · [[extends]] the sets in force · [check.<id>] patches
  sets/baransu/*     the preset's sets, as /lint sync writes them
  sets/local/*       the project's own sets

What moves where:
  lint.json                 → config.toml [settings] (converter, sgconfig; `checks` has no meaning any more)
  lint.toml                 → config.toml (its extends and patches, set paths rewritten below)
  sets/baransu-<name>.toml  → sets/baransu/<name>.toml
  sets/<other>.toml         → sets/local/<other>.toml
  checks/<id>.toml          → first through migrate-scope.py and migrate-timing.py (so the order of the sync steps
                              does not matter), then:
                              - its id defined by an extended sets/baransu/ set with the same action: a
                                [check.<id>] patch in config.toml holding only the fields that differ (none: nothing
                                is written, the preset's copy is the same) — so the next sync updates the rest;
                              - otherwise: one [check.<id>] table in sets/local/checks.toml, comments kept,
                                extended last (after the presets, so it overrides them as the checks folder did).
A field the preset has and the old file lacks now comes from the preset; each is named in the output.
Values are copied as written, line by line. A new file that already exists with other content is never
overwritten: it is named and left as it is. Writing twice gives the same files. Exit 0.
"""
import importlib.util
import json
import re
import sys
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ACTIONS = ("forbid", "run", "builtin")
META = ("from", "origin")
KEY = re.compile(r"^([A-Za-z0-9_-]+)\s*=")
HEADER = re.compile(r"^\s*\[")


def load(name: str):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


scope = load("migrate-scope")
timing = load("migrate-timing")


def split(text: str) -> tuple[list[str], dict[str, list[str]], list[str]]:
    """A one-check file → its leading comments, its top-level fields' lines by key, and any sub-table lines."""
    lines = text.split("\n")
    lead: list[str] = []
    while lines and (lines[0].startswith("#") or lines[0].strip() == ""):
        lead.append(lines.pop(0))
    fields: dict[str, list[str]] = {}
    rest: list[str] = []
    key = None
    pending: list[str] = []  # comments between fields go with the field below them

    def closed(k: str) -> bool:
        try:
            tomllib.loads("\n".join(l for l in fields[k] if not l.lstrip().startswith("#")))
            return True
        except tomllib.TOMLDecodeError:
            return False

    for ln in lines:
        if rest or (HEADER.match(ln) and (key is None or closed(key))):
            rest.append(ln)
            continue
        m = KEY.match(ln)
        if m and (key is None or closed(key)):
            key = m.group(1)
            fields[key] = [*pending, ln]
            pending = []
        elif key is not None and not closed(key):
            fields[key].append(ln)
        elif ln.strip():
            pending.append(ln)
    return [l for l in lead if l.strip()], fields, rest


def table(id_: str, text: str) -> str:
    lines = text.split("\n")
    lead = []
    while lines and (lines[0].startswith("#") or lines[0].strip() == ""):
        lead.append(lines.pop(0))
    while lines and lines[-1].strip() == "":
        lines.pop()
    # A sub-table of a flat file ([options]) belongs to the check.
    lines = [re.sub(r"^(\s*)\[(?!\[)([^\]]+)\]", lambda m: f"{m.group(1)}[check.{id_}.{m.group(2)}]", l) for l in lines]
    return "\n".join([*[l for l in lead if l.strip()], f"[check.{id_}]", *lines])


def write_new(root: Path, rel: str, data: bytes, kept: list[str]) -> None:
    """Write a new file unless one with other content is there."""
    target = root / rel
    if target.is_file():
        if target.read_bytes() != data:
            kept.append(rel)
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    root = Path(args[0])
    checks = root / "checks"
    old: list[Path] = [*sorted((root / "sets").glob("*.toml")), *(sorted(checks.glob("*.toml")) if checks.is_dir() else [])]
    old += [p for p in (root / "lint.json", root / "lint.toml") if p.is_file()]

    if "--remove" in sys.argv:
        # Deletes only: the new files were written and checked in an earlier run.
        if not (root / "config.toml").is_file():
            print("還沒有 config.toml：先跑一次不帶 --remove 的，確認新的讀得出同樣的規則，再刪舊檔")
            return 1
        for p in old:
            p.unlink()
        if checks.is_dir() and not any(checks.iterdir()):
            checks.rmdir()
        print(f"已刪除舊檔 {len(old)} 個")
        return 0

    kept: list[str] = []
    moved: dict[str, str] = {}
    set_text: dict[str, str] = {}

    # sets/ → sets/baransu/ and sets/local/
    for f in sorted((root / "sets").glob("*.toml")):
        name = f.name
        dest = f"sets/baransu/{name[len('baransu-'):]}" if name.startswith("baransu-") else f"sets/local/{name}"
        moved[f"sets/{name}"] = dest
        write_new(root, dest, f.read_bytes(), kept)
        set_text[dest] = (root / dest).read_text(encoding="utf-8")

    # lint.json → [settings]
    settings: dict = {}
    lj = root / "lint.json"
    if lj.is_file():
        try:
            given = json.loads(lj.read_text(encoding="utf-8"))
        except ValueError:
            given = {}
        for k in ("converter", "sgconfig"):
            if isinstance(given.get(k), str):
                settings[k] = given[k]

    # lint.toml → config.toml, set paths rewritten
    body = ""
    lt = root / "lint.toml"
    if lt.is_file():
        body = lt.read_text(encoding="utf-8").replace("\r\n", "\n")
        for a, b in moved.items():
            body = re.sub(r"""(set\s*=\s*["'])""" + re.escape(a) + r"""(["'])""", lambda m: m.group(1) + b + m.group(2), body)
    elif moved:
        body = "".join(f'[[extends]]\nset = "{b}"\n\n' for b in moved.values())

    # The preset checks in force: each extended sets/baransu/ set's definitions.
    try:
        doc = tomllib.loads(body)
    except tomllib.TOMLDecodeError:
        doc = {}
    patched = set((doc.get("check") or {}).keys())
    preset: dict[str, dict] = {}
    # As engine/sets.ts loads them: only / except choose, level strict and an extends severity set the severity.
    for e in doc.get("extends") or []:
        p = str(e.get("set", "")).replace("\\", "/").removeprefix("./")
        if not (p.startswith("sets/baransu/") and p in set_text):
            continue
        try:
            defs = tomllib.loads(set_text[p]).get("check") or {}
        except tomllib.TOMLDecodeError:
            continue
        only, except_ = e.get("only"), e.get("except") or []
        for id_, raw in defs.items():
            if not isinstance(raw, dict) or (only is not None and id_ not in only) or id_ in except_:
                continue
            eff = {k: v for k, v in raw.items() if k != "strict"}
            if e.get("level") == "strict" and isinstance(raw.get("strict"), str):
                eff["severity"] = raw["strict"]
            if isinstance(e.get("severity"), str) and eff.get("severity") != "off":
                eff["severity"] = e["severity"]
            preset[id_] = eff

    # checks/ → patches in config.toml, or sets/local/checks.toml
    files = sorted(checks.glob("*.toml")) if checks.is_dir() else []
    texts = {f: f.read_text(encoding="utf-8").replace("\r\n", "\n") for f in files}
    levels = any(timing.has_old(t) for t in [*texts.values(), body, *set_text.values()])
    local: list[str] = []
    patches: list[str] = []
    notes: list[str] = []
    for f in files:
        id_ = f.stem
        text = timing.rewrite(scope.migrate(texts[f])[0], levels)[0]
        try:
            mine = tomllib.loads(text)
        except tomllib.TOMLDecodeError:
            mine = None
        base = preset.get(id_)
        lead, fields, rest = split(text)
        same_action = base is not None and mine is not None and all(mine.get(a) == base.get(a) for a in ACTIONS)
        if not same_action or rest or id_ in patched:
            local.append(table(id_, text))
            continue
        # `from` says where a copy came from; it changes no behaviour.
        differ = [k for k in fields if k not in META and k != "strict" and mine.get(k) != base.get(k)]
        missing = [k for k in base if k not in mine and k not in META and k != "severity"]
        # A file without severity meant the default level; the preset's now applies.
        if missing:
            notes.append(f"{id_}：舊檔沒寫的 {'、'.join(missing)} 改照 preset")
        if differ:
            patches.append("\n".join([*lead, f"[check.{id_}]", *[l for k in differ for l in fields[k]]]))
            notes.append(f"{id_}：preset 的檢查，config.toml 只留不一樣的 {'、'.join(differ)}")
        else:
            notes.append(f"{id_}：和 preset 一樣，不另寫")

    local_rel = "sets/local/checks.toml"
    if local:
        write_new(root, local_rel, ("\n\n".join(local) + "\n").encode("utf-8"), kept)
        if local_rel not in body:
            body = body.rstrip("\n") + ("\n\n" if body.strip() else "") + f'# The project\'s own checks, moved from checks/ (8.44).\n[[extends]]\nset = "{local_rel}"\n'
    if patches:
        body = body.rstrip("\n") + "\n\n# Preset checks changed in checks/ before 8.44: only what differs.\n" + "\n\n".join(patches) + "\n"

    if body or settings:
        head = ("[settings]\n" + "".join(f"{k} = {json.dumps(v, ensure_ascii=False)}\n" for k, v in settings.items()) + "\n") if settings else ""
        write_new(root, "config.toml", (head + body).encode("utf-8"), kept)
        if "config.toml" not in kept:
            print("config.toml 寫好了")
    for a, b in moved.items():
        print(f"{a} → {b}")
    if local:
        print(f"checks/ 的 {len(local)} 條 → {local_rel}")
    for n in notes:
        print(n)
    for k in kept:
        print(f"{k} 已經有了、內容不同：沒有覆蓋，請自己比對")
    if old:
        print(f"舊檔 {len(old)} 個還在：確認新的 config.toml 與 sets/ 讀得出同樣的規則後，再單獨跑一次 --remove")
    return 0


if __name__ == "__main__":
    sys.exit(main())
