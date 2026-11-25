"""Verdicts for the verification-methods hypothesis, computed from corpus.csv and tests.csv (criteria.md).

Usage: uv run check.py            (prints the tables and verdicts; exit 1 when R1 is broken on the plain reading)
"""
import csv
import sys
from collections import Counter
from pathlib import Path

HERE = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent


def rows(name):
    with open(HERE / name, encoding="utf-8-sig", newline="") as f:
        return [r for r in csv.DictReader(f) if r["id"].strip() and not r["id"].startswith("#")]


def main():
    corpus = rows("corpus.csv")
    allowed = {"e2e": {"yes", "rare", "no"}, "tla": {"yes", "transcribe", "no"}, "kit": {"yes", "no"}, "lint": {"yes", "no"}}
    for r in corpus:
        for k, ok in allowed.items():
            if r[k] not in ok:
                sys.exit(f"{r['id']}: {k}={r[k]!r} not in {sorted(ok)}")

    plain = [r for r in corpus if r["kit"] == "yes" and r["e2e"] == "no" and r["tla"] == "no"]
    strict = [r for r in corpus if r["kit"] == "yes" and r["e2e"] in {"no", "rare"} and r["tla"] in {"no", "transcribe"}]
    blind = [r for r in corpus if r["kit"] == "no" and r["e2e"] == "yes"]

    print(f"defects: {len(corpus)}")
    print("found_by:", dict(Counter(r["found_by"] for r in corpus)))
    print("e2e:", dict(Counter(r["e2e"] for r in corpus)), " tla:", dict(Counter(r["tla"] for r in corpus)), " kit:", dict(Counter(r["kit"] for r in corpus)))
    print(f"R1 plain  broken by {len(plain)}: {[r['id'] for r in plain]}")
    print(f"R1 strict broken by {len(strict)}: {[r['id'] for r in strict]}")
    print(f"kit blind, e2e sees ({len(blind)}): {[r['id'] for r in blind]}")
    kit = [r for r in corpus if r["kit"] == "yes"]
    lintable = [r for r in kit if r["lint"] == "yes"]
    print(f"C: of {len(kit)} kit-catchable, lint could refuse {len(lintable)}: {[r['id'] for r in lintable]}")
    print(f"C: R1-strict rows lint covers: {[r['id'] for r in strict if r['lint'] == 'yes']}")

    tests = rows("tests.csv")
    c = Counter(t["turned_red_because"] for t in tests for _ in range(int(t.get("count") or 1)))
    counted = c["regression"] + c["intent"] + c["wrong-test"]
    share = c["regression"] / counted if counted else 0.0
    print("tests:", dict(c), f" regression share {share:.0%} of {counted}")
    print("B holds" if counted and share < 0.5 else "B not shown")
    return 1 if plain else 0


if __name__ == "__main__":
    sys.exit(main())
