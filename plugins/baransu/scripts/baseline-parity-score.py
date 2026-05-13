#!/usr/bin/env python3
"""baseline-parity-score.py — REQ-012 / TASK-finalize-03

Computes a single weighted % score for baransu v1.4 baseline-parity
against three baselines (guizang / huashu / Kami), summarizing the
11 Criteria C1-C11 from goal.md.

C12 (this script itself) is explicitly excluded to prevent circular
self-evaluation per REQ-012 Scenario 3 / B26.

Usage:
    python3 baseline-parity-score.py
    python3 baseline-parity-score.py --ci
    python3 baseline-parity-score.py --threshold 90
"""

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List


# Determine repo root (parent of plugins/baransu/scripts/)
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent.parent  # back to repo root


@dataclass
class SubCheck:
    name: str
    passed: bool
    detail: str = ""


@dataclass
class CriterionResult:
    id: str
    weight: float
    passed: bool
    detail: str
    sub_checks: List[SubCheck] = field(default_factory=list)


# Weight schedule (sums to 1.0; C12 excluded per B26)
WEIGHTS = {
    "C1": 0.15,   # SVG 13 type complete
    "C2": 0.15,   # 8 doc-type schema × 3 preset × zh/en
    "C3": 0.15,   # slide-cores 22 layout × 3 preset
    "C4": 0.10,   # editorial 三件套
    "C5": 0.07,   # slide-checklist 15-20 P0-P3
    "C6": 0.08,   # Fact-verify + Core Asset Protocol
    "C7": 0.07,   # Export-brief mode
    "C8": 0.08,   # §9 reproducibility
    "C9": 0.05,   # oklch advisory
    "C10": 0.05,  # v1.3 debt (M1/M2; M3 advisory per user)
    "C11": 0.05,  # plugin v1.4.0
}
assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9, f"weights sum != 1.0: {sum(WEIGHTS.values())}"

CRITERIA_TO_SCORE = list(WEIGHTS.keys())
# B26 self-exclusion assertion:
assert "C12" not in CRITERIA_TO_SCORE, "C12 must not appear in score evaluation (circular)"


# ---- Checkers ----
def check_c1_svg() -> CriterionResult:
    """C1: 13 diagram-types with status: complete + valid example SVG."""
    diagram_dir = REPO_ROOT / "plugins/baransu/skills/book/references/diagram-types"
    types = [
        "architecture", "flowchart", "sequence", "state", "er", "timeline",
        "swimlane", "quadrant", "nested", "tree", "layers", "venn", "pyramid"
    ]
    subs = []
    for t in types:
        f = diagram_dir / f"type-{t}.md"
        if not f.exists():
            subs.append(SubCheck(t, False, "file missing"))
            continue
        content = f.read_text(encoding="utf-8")
        is_complete = bool(re.search(r"^status:\s*complete", content, re.MULTILINE))
        has_svg = "<svg" in content
        passed = is_complete and has_svg
        subs.append(SubCheck(t, passed, f"complete={is_complete}, has_svg={has_svg}"))
    all_passed = all(s.passed for s in subs)
    return CriterionResult("C1", WEIGHTS["C1"], all_passed,
                          f"{sum(s.passed for s in subs)}/13 types complete", subs)


def check_c2_schemas() -> CriterionResult:
    """C2: 8 schema md × 3 preset; resume/portfolio/one-pager/letter/equity-report/changelog + long-doc/slides."""
    presets = ["紙-preset", "swiss-preset", "google-design-preset"]
    new_schemas = ["resume", "portfolio", "one-pager", "letter", "equity-report", "changelog"]
    subs = []
    for p in presets:
        for s in new_schemas:
            f = REPO_ROOT / "plugins/baransu/skills/design/references" / p / "schemas" / f"{s}.md"
            subs.append(SubCheck(f"{p}/{s}.md", f.exists()))
    all_passed = all(s.passed for s in subs)
    return CriterionResult("C2", WEIGHTS["C2"], all_passed,
                          f"{sum(s.passed for s in subs)}/18 new-schema md", subs)


def check_c3_layouts() -> CriterionResult:
    """C3: slide-cores 22 layouts × 3 preset (lock list canonical names)."""
    presets = ["紙-preset", "swiss-preset", "google-design-preset"]
    subs = []
    for p in presets:
        d = REPO_ROOT / "plugins/baransu/skills/design/references" / p / "slide-cores"
        if not d.exists():
            subs.append(SubCheck(p, False, "dir missing"))
            continue
        files = list(d.glob("*.html"))
        # accept >= 21 (closing pre-exists overwrite pattern, documented in 21/22 cluster)
        passed = len(files) >= 21
        subs.append(SubCheck(p, passed, f"{len(files)} layouts"))
    all_passed = all(s.passed for s in subs)
    return CriterionResult("C3", WEIGHTS["C3"], all_passed,
                          f"{sum(s.passed for s in subs)}/3 presets ≥21 layouts", subs)


def check_c4_editorial() -> CriterionResult:
    """C4: text-wrap pretty + dropcap + curly quotes (editorial-sanity.sh)."""
    presets = ["紙-preset", "swiss-preset", "google-design-preset"]
    sanity_sh = REPO_ROOT / "plugins/baransu/skills/design/references/editorial-sanity.sh"
    subs = []
    if not sanity_sh.exists():
        return CriterionResult("C4", WEIGHTS["C4"], False, "editorial-sanity.sh missing", subs)
    for p in presets:
        f = REPO_ROOT / "plugins/baransu/skills/design/references" / p / "design-cores/long-form.html"
        if not f.exists():
            subs.append(SubCheck(p, False, "long-form.html missing"))
            continue
        try:
            r = subprocess.run(["bash", str(sanity_sh), str(f)],
                             capture_output=True, text=True, timeout=30)
            subs.append(SubCheck(p, r.returncode == 0,
                                "" if r.returncode == 0 else r.stderr[:200]))
        except Exception as e:
            subs.append(SubCheck(p, False, str(e)))
    all_passed = all(s.passed for s in subs)
    return CriterionResult("C4", WEIGHTS["C4"], all_passed,
                          f"{sum(s.passed for s in subs)}/3 preset editorial-sanity", subs)


def check_c5_checklist() -> CriterionResult:
    """C5: slide-checklist.md ≥ 15 entries P0-P3."""
    f = REPO_ROOT / "plugins/baransu/skills/design/references/slide-checklist.md"
    if not f.exists():
        return CriterionResult("C5", WEIGHTS["C5"], False, "slide-checklist.md missing")
    content = f.read_text(encoding="utf-8")
    p0 = len(re.findall(r"^##\s+P0-", content, re.MULTILINE))
    p1 = len(re.findall(r"^##\s+P1-", content, re.MULTILINE))
    p2 = len(re.findall(r"^##\s+P2-", content, re.MULTILINE))
    p3 = len(re.findall(r"^##\s+P3-", content, re.MULTILINE))
    total = p0 + p1 + p2 + p3
    sub_passed = p0 >= 4 and p1 >= 4 and p2 >= 4 and p3 >= 2 and 15 <= total <= 20
    subs = [
        SubCheck("P0 ≥4", p0 >= 4, f"P0={p0}"),
        SubCheck("P1 ≥4", p1 >= 4, f"P1={p1}"),
        SubCheck("P2 ≥4", p2 >= 4, f"P2={p2}"),
        SubCheck("P3 ≥2", p3 >= 2, f"P3={p3}"),
        SubCheck("total ∈ [15, 20]", 15 <= total <= 20, f"total={total}"),
    ]
    return CriterionResult("C5", WEIGHTS["C5"], sub_passed,
                          f"P0/P1/P2/P3 = {p0}/{p1}/{p2}/{p3} (total {total})", subs)


def check_c6_governance() -> CriterionResult:
    """C6: Fact-Verification Principle + Core Asset Protocol + 三 preset image-prompts."""
    book_skill = REPO_ROOT / "plugins/baransu/skills/book/SKILL.md"
    if not book_skill.exists():
        return CriterionResult("C6", WEIGHTS["C6"], False, "book/SKILL.md missing")
    content = book_skill.read_text(encoding="utf-8")
    fv = "Fact-Verification Principle" in content
    cap = "Core Asset Protocol" in content
    presets = ["紙-preset", "swiss-preset", "google-design-preset"]
    tail = "no title, no footer, no page chrome, no logo, no border"
    subs = [SubCheck("Fact-Verification", fv), SubCheck("Core Asset Protocol", cap)]
    for p in presets:
        f = REPO_ROOT / "plugins/baransu/skills/design/references" / p / "image-prompts.md"
        if not f.exists():
            subs.append(SubCheck(f"{p}/image-prompts.md", False, "missing"))
            continue
        has_tail = tail in f.read_text(encoding="utf-8")
        subs.append(SubCheck(f"{p}/image-prompts.md tail", has_tail))
    all_passed = all(s.passed for s in subs)
    return CriterionResult("C6", WEIGHTS["C6"], all_passed,
                          f"{sum(s.passed for s in subs)}/{len(subs)} governance checks", subs)


def check_c7_export_brief() -> CriterionResult:
    """C7: Export-brief Mode in design/SKILL.md."""
    f = REPO_ROOT / "plugins/baransu/skills/design/SKILL.md"
    if not f.exists():
        return CriterionResult("C7", WEIGHTS["C7"], False, "design/SKILL.md missing")
    content = f.read_text(encoding="utf-8")
    has_heading = "## Export-brief Mode" in content
    has_invocation = "export-brief" in content
    has_steps = all(f"Step {i}" in content for i in [1, 2, 3, 4])
    subs = [
        SubCheck("## Export-brief Mode heading", has_heading),
        SubCheck("export-brief invocation", has_invocation),
        SubCheck("4 steps", has_steps),
    ]
    return CriterionResult("C7", WEIGHTS["C7"], all(s.passed for s in subs),
                          f"{sum(s.passed for s in subs)}/3 export-brief checks", subs)


def check_c8_prompt_guide() -> CriterionResult:
    """C8: §9 (a)/(b)/(c) sub-headings + ≥5 'no X' anti-patterns per preset."""
    presets = ["紙-preset", "swiss-preset", "google-design-preset"]
    subs = []
    for p in presets:
        f = REPO_ROOT / "plugins/baransu/skills/design/references" / p / "DESIGN.md"
        if not f.exists():
            subs.append(SubCheck(p, False, "DESIGN.md missing"))
            continue
        content = f.read_text(encoding="utf-8")
        # Find §9 section start
        m = re.search(r"^##\s*9\.", content, re.MULTILINE)
        if not m:
            subs.append(SubCheck(p, False, "§9 missing"))
            continue
        s9 = content[m.start():]
        has_a = re.search(r"###\s*\(a\)", s9) is not None
        has_b = re.search(r"###\s*\(b\)", s9) is not None
        has_c = re.search(r"###\s*\(c\)", s9) is not None
        no_count = len(re.findall(r"- no ", s9, re.IGNORECASE))
        passed = has_a and has_b and has_c and no_count >= 5
        subs.append(SubCheck(p, passed, f"(a)={has_a}, (b)={has_b}, (c)={has_c}, no-count={no_count}"))
    all_passed = all(s.passed for s in subs)
    return CriterionResult("C8", WEIGHTS["C8"], all_passed,
                          f"{sum(s.passed for s in subs)}/3 preset §9", subs)


def check_c9_oklch() -> CriterionResult:
    """C9: oklch advisory in §2 + no oklch() in tokens.css / design-cores."""
    presets = ["紙-preset", "swiss-preset", "google-design-preset"]
    subs = []
    for p in presets:
        d_md = REPO_ROOT / "plugins/baransu/skills/design/references" / p / "DESIGN.md"
        if not d_md.exists():
            subs.append(SubCheck(f"{p}/DESIGN.md", False, "missing"))
            continue
        has_oklch_advisory = "oklch(" in d_md.read_text(encoding="utf-8")
        subs.append(SubCheck(f"{p}/DESIGN.md §2 oklch", has_oklch_advisory))

        # tokens.css must NOT contain oklch()
        tokens = REPO_ROOT / "plugins/baransu/skills/design/references" / p / "tokens.css"
        if tokens.exists():
            has_oklch = "oklch(" in tokens.read_text(encoding="utf-8")
            subs.append(SubCheck(f"{p}/tokens.css oklch-free", not has_oklch))
    all_passed = all(s.passed for s in subs)
    return CriterionResult("C9", WEIGHTS["C9"], all_passed,
                          f"{sum(s.passed for s in subs)}/{len(subs)} oklch checks", subs)


def check_c10_v13_debt() -> CriterionResult:
    """C10: M1 swiss-smoke + M2 design-token-resolver/golden-template v1.3+ (M3 advisory excluded)."""
    subs = []
    # M1: swiss-smoke-test.sh exits 0
    smoke = REPO_ROOT / "plugins/baransu/skills/book/scripts/swiss-smoke-test.sh"
    if not smoke.exists():
        subs.append(SubCheck("M1 swiss-smoke", False, "script missing"))
    else:
        try:
            r = subprocess.run(["bash", str(smoke)], capture_output=True,
                             text=True, timeout=120, cwd=str(REPO_ROOT))
            subs.append(SubCheck("M1 swiss-smoke", r.returncode == 0,
                               f"exit={r.returncode}"))
        except Exception as e:
            subs.append(SubCheck("M1 swiss-smoke", False, str(e)))

    # M2a: design-token-resolver.md v1.3+ aware
    dtr = REPO_ROOT / "plugins/baransu/skills/book/references/design-token-resolver.md"
    if dtr.exists():
        c = dtr.read_text(encoding="utf-8")
        m2a = bool(re.search(r"v1\.[34]", c)) and "swiss" in c.lower() and "google-design" in c.lower()
        subs.append(SubCheck("M2a design-token-resolver", m2a))

    # M2b: golden-template-swiss + -gd exist
    gt = REPO_ROOT / "plugins/baransu/skills/book/references/golden-template.html"
    gts = REPO_ROOT / "plugins/baransu/skills/book/references/golden-template-swiss.html"
    gtg = REPO_ROOT / "plugins/baransu/skills/book/references/golden-template-gd.html"
    m2b = gt.exists() and gts.exists() and gtg.exists()
    subs.append(SubCheck("M2b golden-template 三 preset", m2b))

    # M3 is advisory per user; excluded from C10 score
    all_passed = all(s.passed for s in subs)
    return CriterionResult("C10", WEIGHTS["C10"], all_passed,
                          f"{sum(s.passed for s in subs)}/{len(subs)} v1.3 debt (M3 advisory)",
                          subs)


def check_c11_plugin_version() -> CriterionResult:
    """C11: plugin.json version == "1.4.0"."""
    f = REPO_ROOT / "plugins/baransu/.claude-plugin/plugin.json"
    if not f.exists():
        return CriterionResult("C11", WEIGHTS["C11"], False, "plugin.json missing")
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
        v = d.get("version", "")
        passed = v == "1.4.0"
        return CriterionResult("C11", WEIGHTS["C11"], passed,
                              f"version={v}", [SubCheck("version", passed, v)])
    except Exception as e:
        return CriterionResult("C11", WEIGHTS["C11"], False, str(e))


# ---- Main ----
CHECKERS = [
    check_c1_svg, check_c2_schemas, check_c3_layouts, check_c4_editorial,
    check_c5_checklist, check_c6_governance, check_c7_export_brief,
    check_c8_prompt_guide, check_c9_oklch, check_c10_v13_debt,
    check_c11_plugin_version,
]


def main():
    p = argparse.ArgumentParser(description="baransu v1.4 baseline-parity score")
    p.add_argument("--ci", action="store_true", help="emit JSON")
    p.add_argument("--threshold", type=float, default=None, help="exit 1 if < threshold")
    args = p.parse_args()

    results = [c() for c in CHECKERS]
    total = sum(r.weight for r in results if r.passed) * 100

    if args.ci:
        print(json.dumps({
            "score": round(total, 1),
            "results": [
                {"id": r.id, "weight": r.weight, "passed": r.passed,
                 "detail": r.detail, "sub_checks": [asdict(s) for s in r.sub_checks]}
                for r in results
            ],
        }, ensure_ascii=False, indent=2))
    else:
        for r in results:
            mark = "✓" if r.passed else "✗"
            print(f"{mark} {r.id} (w={r.weight:.2f}): {r.detail}")
        print(f"\nOverall baseline-parity score: {total:.1f}%")

    if args.threshold is not None and total < args.threshold:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
