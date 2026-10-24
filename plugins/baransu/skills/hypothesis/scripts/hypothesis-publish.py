#!/usr/bin/env python3
"""hypothesis-publish — the writer's last step; only /hypothesis runs it.

Reads `<area>/hypothesis.draft.json` (the full record without hashes), computes every
hash the readers will compare — the cited source files, the current matches of each
watch pattern, every artifact file — and swaps the record in by compare-and-swap on
`generation`. Readers never run this; `hypothesis-status.py` stays read-only.

Usage:
  hypothesis-publish.py AREA_DIR [--commit SHA]

The draft carries `base_generation`: the generation read when this run started
(0 for a first publish). If `hypothesis.json` has moved on since, nothing is written
and the exit is 3 (another writer published meanwhile: start the run again).
Exit: 0 published; 2 failed (including an artifact file git ignores); 3 lost the compare-and-swap.
"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("hypothesis_status", HERE / "hypothesis-status.py")
status = importlib.util.module_from_spec(_spec)
sys.modules["hypothesis_status"] = status  # dataclasses look their module up here
_spec.loader.exec_module(status)  # type: ignore[union-attr]

SKIP = {"hypothesis.json", "hypothesis.draft.json", "hypothesis.lock"}


def current_generation(area_dir: Path) -> int:
    rec, _ = status.load_record(area_dir)
    return int(rec.get("generation", 0)) if rec else 0


def publish(area_dir: Path, commit: str | None) -> int:
    root = status.repo_root()
    draft_path = area_dir / "hypothesis.draft.json"
    draft = json.loads(draft_path.read_text(encoding="utf-8"))
    base = int(draft.pop("base_generation", 0))
    if current_generation(area_dir) != base:
        print(f"另一個寫入者已在這段期間發布（世代 {current_generation(area_dir)} ≠ {base}），沒有寫入；請重新開始。",
              file=sys.stderr)
        return 3
    sync = draft.setdefault("sync", {})
    sync["hash_algo"] = "sha256-lf"
    if commit is None:
        head = status._git(root, "rev-parse", "--short", "HEAD")
        commit = head.strip() if head else None
    sync["commit"] = commit
    files = {}
    for name in sorted(status.cited_files(draft) | set(sync.get("extra_files", []))):
        h = status.hash_lf(root / name)
        if h is None:
            print(f"引用的檔案不存在：{name}", file=sys.stderr)
            return 2
        files[name] = h
    sync["files"] = files
    for w in sync.get("watch", []):
        now = status.watch_matches(root, w["pattern"], w.get("paths"))
        if now is None:
            print("寫入樣式需要 git；這裡沒有 git。", file=sys.stderr)
            return 2
        w["matched"] = now
    artifacts = [p for p in sorted(area_dir.rglob("*"))
                 if p.is_file() and p.name not in SKIP and not p.name.startswith("hypothesis.json.")]
    ignored = [p for p in artifacts
               if subprocess.run(["git", "check-ignore", "-q", str(p)], cwd=root).returncode == 0]
    if ignored:  # a file git ignores is missing in every other checkout, so its hash turns the area `draft` there
        print("這些產物檔被 git 忽略，別的 checkout 會看不到：" + "、".join(p.relative_to(area_dir).as_posix() for p in ignored),
              file=sys.stderr)
        return 2
    sync["artifact"] = {p.relative_to(area_dir).as_posix(): status.hash_lf(p) for p in artifacts}
    draft["schema"] = status.SCHEMA
    draft["area"] = area_dir.name
    draft["generation"] = base + 1
    draft["published_at"] = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    lock = area_dir / "hypothesis.lock"
    try:  # the compare and the swap happen under one lock, so two writers cannot both pass the compare
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        print(f"另一個寫入者正在發布（{lock.name} 存在）；請重新開始。", file=sys.stderr)
        return 3
    try:
        if current_generation(area_dir) != base:
            print("交換前發現另一個寫入者已發布，沒有寫入；請重新開始。", file=sys.stderr)
            return 3
        tmp = area_dir / f"hypothesis.json.{os.getpid()}.tmp"
        tmp.write_text(json.dumps(draft, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        os.replace(tmp, area_dir / "hypothesis.json")
        draft_path.unlink()
    finally:
        os.close(fd)
        lock.unlink()
    print(f"已發布：{area_dir.name} 世代 {base + 1}，涵蓋 {len(files)} 個檔案、{len(sync['artifact'])} 個產物檔")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="hypothesis-publish.py")
    ap.add_argument("area_dir", type=Path)
    ap.add_argument("--commit")
    a = ap.parse_args(argv)
    return publish(a.area_dir.resolve(), a.commit)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as exc:
        print(f"hypothesis-publish 失敗：{exc}", file=sys.stderr)
        raise SystemExit(2)
