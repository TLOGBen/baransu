#!/usr/bin/env python3
"""The /draw book index (references/index.json, references/INDEX.md) and its lookup tool
(scripts/lookup.py).

Pins what would silently rot when a reference is edited:
- every index entry resolves to exactly one heading (and its row / item / lines);
- every heading of every indexed reference is reachable from some topic;
- every topic a step names in its lookup_before list exists (the frozen step design below,
  and references/steps.json once it exists);
- one tool = one topic: kit cylinder, slabOf and tubePieces print three different rows,
  and the camera moves and transitions are one chapter each;
- --log appends one TSV line; an unknown id exits 1 with candidates; search words list
  candidates without dumping a section;
- --step prints every topic a step names (templates filled from --value, aliases resolved,
  {form} / {approach} from the brief) and logs one step record plus its topic lines at one
  time; an unknown step or value logs nothing; every template alias is an index alias;
- INDEX.md is exactly what --render-index produces from index.json.
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "plugins" / "baransu" / "skills" / "draw"
LOOKUP = SKILL / "scripts" / "lookup.py"
INDEX_JSON = SKILL / "references" / "index.json"
INDEX_MD = SKILL / "references" / "INDEX.md"
STEPS_JSON = SKILL / "references" / "steps.json"

_spec = importlib.util.spec_from_file_location("draw_lookup", LOOKUP)
lookup = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lookup)

# Every lookup_before id of the frozen step design (slice P3 of the 7.5.0 redesign).
# Ids with {...} are templates: the step resolves them from its own plan file
# (camera-{move} from docs/camera_plan.md, kit-{fn} from geometry.mjs, ...).
DESIGN_LOOKUP_BEFORE = """
preflight-doctor browser-launch-safety route-form-table route-approach-table route-mechanism-or-diagram
anatomy-size-classes mech-overrides brief-facts-vs-choices status-line-format design-film-brief
commission-scope-sample commission-build-for-revisions grab-url-assets design-reference-read
design-ban-identity-locks springs-tokens type-faces type-hook beat-measure-track finishing-loops springs-loopT
hand-drawn-workflow hand-drawn-traps hand-drawn-detail-override pipeline-film-folder pipeline-render-contract
pipeline-formats-safe-areas draft-direction-funnel pipeline-cmd-still composition-631-rule
composition-colour-survive composition-lighting chapters-guide-split draft-storyboard-format draft-time-reads
camera-parallax-rule camera-choosing camera-{move} transitions-rules transition-{name} draft-pacing-rules
draft-timing-sheet keys-key-card draft-animatic pipeline-cmd-animatic keys-bookends keys-layout keys-as-data
keys-review-stills shoot-interval-design springs-feel-by-mass shoot-inbetweens springs-track shoot-run-camera
review-read-sheet review-notes-frame-numbers pipeline-cmd-dailies post-execute-seams beat-ui-sounds
beat-sync-measurement beat-synthesize pipeline-motion-blur pipeline-cmd-full finishing-export
finishing-platform-limits review-export post-package component-build-order component-caption-rule keys-other-lanes
perf-one-heavy-at-a-time perf-dpr-pixel-budget perf-no-forced-layout component-mechanics component-contract
springs-primitives springs-durations-stagger perf-loop-while-moving perf-redraw-moving-parts
mech-catalog-index anatomy-examples-table anatomy-truth-first walkthrough-truth mech-invent-verb-family
mech-mapping-template mech-mapping-tests anatomy-parts-list craft-parts-vocabulary craft-anti-patterns
anatomy-plan-world kit-camera craft-camera-composition craft-round-parts craft-pipes-waypoints
craft-contacts-junctions craft-clearance-crossings kit-{fn} craft-tones craft-painters-order kit-audit
webgl-layer-stack webgl-camera-contract webgl-nothing-pops webgl-light-theme perf-shader-link 3d-model
3d-part-kinds 3d-painters-order 3d-performance anatomy-frame-card kit-card-page mech-join-diagram type-exploded
anatomy-motion-pointer anatomy-motion-keyboard anatomy-motion-vanilla-loop mech-tour-as-seek mech-join-component
mech-join-film verify-audit verify-line-ends verify-capture verify-drive verify-closeups
verify-light-theme-shaders verify-orbit verify-review-checklist verify-common-faults import-{format}
output-fidelity-ledger brand-onboarding brand-profiles diagram-type-table output-size-presets
layout-complexity-budget semantic-patterns-index type-{chosen} layout-4px-grid type-ramp-{size} diagram-tokens
connector-rules arrow-label-mask accessible-svg-contract cjk-labels-zh-hant diagram-animation-modes
seek-overlay-contract diagram-checks taste-anti-patterns taste-preoutput-checklist diagram-export
map-type-router map-authoring-composition map-authoring-layout-routing map-example-{type} map-repo-authoring
map-viewer-runtime map-browser-env map-finalize-repair map-perceptual-review verify-page-usage
perf-check-usage critique-loop-order critique-shared-scorecard critique-rows-{form} critique-rows-{approach}
completion-report-format component-ui-handoff anatomy-invent-object anatomy-build-geometry
anatomy-painters-order anatomy-make-live anatomy-verify-critic kit-audit-hook mech-join-{form}
""".split()

# Values each template is filled with by the steps.
TEMPLATE_VALUES = {
    "camera-{move}": ["pan", "tilt", "dolly", "zoom", "tracking", "orbit", "crane", "dolly-zoom", "rack-focus",
                      "handheld", "fpv", "dutch", "slow-motion", "speed-ramp", "time-lapse", "freeze-frame"],
    "transition-{name}": ["hard-cut", "match-cut", "wipe", "iris", "whip-pan", "camera-carry", "accent-carry",
                          "brush-wipe", "jump-cut", "cross-dissolve", "smash-cut", "j-cut", "l-cut"],
    "kit-{fn}": ["slabOf", "cylinder", "extrude", "lathe", "tubePieces", "translateAlong", "fitProjection",
                 "planOutline", "topTicks", "knurl", "coil", "radialTicks", "solidOf", "frameAlong", "fillet",
                 "recorder", "settle", "auditOrExit", "glLayer", "plateHtml", "kitScript"],
    "import-{format}": ["drawio", "excalidraw", "mermaid"],
    "type-ramp-{size}": ["standard", "presentation", "print"],
    "map-example-{type}": ["architecture", "workflow", "sequence", "dataflow", "lifecycle"],
    "critique-rows-{form}": ["component", "diagram", "map", "motion"],
    "critique-rows-{approach}": ["diagram-system", "mechanism", "free-creative"],
    "mech-join-{form}": ["component", "film", "diagram"],
    "type-{chosen}": ["architecture", "flowchart", "sequence", "state", "er", "timeline", "swimlane", "quadrant",
                      "nested", "tree", "layers", "venn", "pyramid", "exploded", "data-flow", "high-level"],
}


def env():
    e = dict(os.environ)
    e["PYTHONUTF8"] = "1"
    e["PYTHONIOENCODING"] = "utf-8"
    return e


def run(*args):
    return subprocess.run([sys.executable, str(LOOKUP), *args], capture_output=True, text=True,
                          encoding="utf-8", env=env(), timeout=120)


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = json.loads(INDEX_JSON.read_text(encoding="utf-8"))
        cls.names = lookup.by_name(cls.index)


class TestIndexResolves(Base):
    def test_every_entry_resolves_to_exactly_one_section(self):
        failures = []
        for e in self.index["topics"]:
            try:
                text = lookup.render(e)
            except lookup.Unresolved as exc:
                failures.append(str(exc))
                continue
            if e.get("row") is not None:
                lines = text.split("\n---\n", 1)[1].splitlines()
                rows = [ln for ln in lines if ln.lstrip().startswith("|") and not lookup.SEP_RE.match(ln)]
                # header + exactly the one row
                if len(rows) != 2 or not lookup.cells(rows[1])[0].startswith(e["row"]):
                    failures.append(f"{e['id']}: row output is not header + that row")
        self.assertEqual(failures, [], "\n".join(failures[:30]))

    def test_ids_and_aliases_are_unique(self):
        seen = {}
        for e in self.index["topics"]:
            for n in [e["id"]] + e.get("aliases", []):
                self.assertNotIn(n.lower(), seen, f"{n} used by {seen.get(n.lower())} and {e['id']}")
                seen[n.lower()] = e["id"]
                self.assertRegex(n, r"^[A-Za-z0-9][A-Za-z0-9_.-]*$", f"id {n!r} is not a plain token")

    def test_every_heading_of_every_indexed_file_is_reachable(self):
        # reached = the start of a heading topic, or inside a line range, a whole-file topic or a
        # topic flagged whole; an overview's sub-headings need topics of their own
        missing = [f"{f}:{i + 1} {text}" for f, i, text in lookup.unreached_headings(self.index["topics"])]
        self.assertEqual(missing, [], "headings with no topic:\n" + "\n".join(missing[:40]))

    def test_no_topic_prints_more_than_120_lines_unless_flagged_whole(self):
        over = []
        for e in self.index["topics"]:
            n = len(lookup.render(e, self.index["topics"]).splitlines())
            if n > 120 and not e.get("whole"):
                over.append(f"{e['id']}: {n} lines")
            if e.get("whole"):
                self.assertTrue(str(e.get("whole_reason", "")).strip(), f"{e['id']} is whole without a reason")
        self.assertEqual(over, [], "split these into sub-topics:\n" + "\n".join(over))

    def test_formerly_oversized_topics_are_overviews_of_their_sub_topics(self):
        expect = {
            "brand-onboarding": ["brand-onboarding-url", "brand-onboarding-step-2"],
            "diagram-export": [],
            "map-repo-authoring": [],
            "type-exploded": [],
            "output-size-presets": [],
            "map-delivery-validate-and-deliver": ["map-delivery-metadata-paths", "map-delivery-directory-lock",
                                                  "map-delivery-no-clobber-publish", "map-delivery-journal-provenance"],
            "map-delivery-output-path-contracts": ["map-delivery-authored-vs-cli-paths", "map-delivery-finalize-handoff",
                                                   "map-delivery-pair-commit-lock-release", "map-delivery-four-claims"],
            "kit-audit": ["kit-audit-hook", "kit-audit-depth-checks", "kit-audit-raptor-wiring", "kit-recorder"],
            "kit-round-parts": ["kit-round-parts-frames", "kit-round-parts-traps", "kit-lathe"],
            "anatomy-page-in-your-code": ["anatomy-page-in-your-code-react", "anatomy-page-in-your-code-tokens",
                                          "anatomy-page-in-your-code-element"],
        }
        for tid, subs in expect.items():
            e = self.names[tid][1]
            self.assertTrue(e.get("overview"), f"{tid} is not an overview")
            text = lookup.render(e, self.index["topics"])
            self.assertIn("overview: yes", text)
            self.assertLessEqual(len(text.splitlines()), 80, f"{tid} overview is long")
            listed = re.findall(r"^- `([^`]+)` — ", text.split("\n---\n", 1)[1], re.M)
            self.assertTrue(listed, f"{tid} lists no sub-topics")
            for s in subs:
                self.assertIn(s, listed, f"{tid} does not list {s}")
            for s in listed:
                self.assertIn(s.lower(), self.names, f"{tid} lists unknown id {s}")

    def test_a_line_range_prints_only_its_run(self):
        body = lookup.render(self.names["map-delivery-directory-lock"][1]).split("\n---\n", 1)[1]
        self.assertTrue(body.startswith("## Validate and deliver\n"))
        self.assertIn("One directory-wide `.archify-delivery-lock.json`", body)
        self.assertIn("| Observed lock state |", body)
        self.assertNotIn("Every no-clobber HTML publisher", body)
        self.assertNotIn("<output-stem>.delivery-pending.json` is the recovery journal", body)
        tail = lookup.render(self.names["map-delivery-journal-provenance"][1])
        self.assertIn("--require-provenance", tail)
        self.assertNotIn("## Output path contracts", tail)

    def test_a_collection_page_splits_into_figure_and_code(self):
        fig = lookup.render(self.names["mech-collection-b-tree"][1]).split("\n---\n", 1)[1]
        code = lookup.render(self.names["mech-collection-b-tree-code"][1]).split("\n---\n", 1)[1]
        self.assertTrue(fig.startswith("# B-tree index"))
        self.assertIn("## Description", fig)
        self.assertNotIn("## Install", fig)
        self.assertIn("## Install and usage (verbatim)", code)
        self.assertIn("## In your code", code)
        self.assertNotIn("## Description", code)
        pages = [p for p in (SKILL / "references/mechanism/collection").glob("*.md") if p.name != "INDEX.md"]
        ids = {e["file"]: e["id"] for e in self.index["topics"] if e.get("to") == "## Install and usage (verbatim)"}
        self.assertEqual(sorted(p.relative_to(SKILL).as_posix() for p in pages), sorted(ids))

    def test_camera_group_3_seams_are_aliases_of_the_transition_topics(self):
        for s in ("jump-cut", "match-cut", "whip-pan", "cross-dissolve", "wipe", "smash-cut", "j-cut", "l-cut"):
            spelled, e = self.names[f"camera-{s}"]
            self.assertEqual(e["id"], f"transition-{s}", f"camera-{s} is not an alias of transition-{s}")
            self.assertEqual(spelled, f"camera-{s}")
        cam = [e for e in self.index["topics"] if e["file"] == "references/motion/camera.md"]
        g3 = self.names["camera-group-3"][1]
        self.assertTrue(g3.get("whole"))
        inside = [e["id"] for e in cam if e is not g3 and re.match(r"(1[7-9]|2[0-4]) ", e.get("heading") or "")]
        self.assertEqual(inside, [], "Group 3 seams still have camera.md topics of their own")

    def test_routed_reference_files_are_all_indexed(self):
        indexed = {e["file"] for e in self.index["topics"]}
        expected = {p.relative_to(SKILL).as_posix() for p in (SKILL / "references").rglob("*.md")
                    if p.name != "INDEX.md" or "collection" in p.parts}
        expected |= {"scripts/anatomy/ANATOMY-SKILL.md", "SKILL.md"}
        expected |= {p.relative_to(SKILL).as_posix() for p in (SKILL / "scripts/anatomy/references").glob("*.md")}
        self.assertEqual(sorted(expected - indexed), [], "reference files with no topic")

    def test_fenced_heading_lookalikes_are_not_chapters(self):
        # prompts.md carries a director's-brief template with "## …" lines inside a code fence
        lines = lookup.read_lines(SKILL / "references/motion/prompts.md")
        flags = lookup.in_fence_flags(lines)
        fenced = {ln.lstrip("# ").strip() for ln, f in zip(lines, flags) if f and ln.startswith("#")}
        self.assertTrue(fenced, "expected fenced '#' lines in prompts.md")
        real = {h[2] for h in lookup.headings(lines)}
        for e in self.index["topics"]:
            if e["file"].endswith("motion/prompts.md") and e.get("heading") is not None:
                self.assertIn(e["heading"], real)


class TestStepTopics(Base):
    def resolve(self, tid):
        if "{" in tid:
            values = TEMPLATE_VALUES.get(tid)
            self.assertIsNotNone(values, f"template {tid} has no test values")
            return [tid.replace(re.search(r"\{[^}]+\}", tid).group(0), v) for v in values]
        return [tid]

    def check_ids(self, ids, origin):
        missing = []
        for tid in ids:
            for concrete in self.resolve(tid):
                if concrete.lower() not in self.names:
                    missing.append(f"{origin}: {concrete}")
                    continue
                try:
                    lookup.render(self.names[concrete.lower()][1])
                except lookup.Unresolved as exc:
                    missing.append(f"{origin}: {concrete}: {exc}")
        self.assertEqual(missing, [], "\n".join(missing))

    def test_design_lookup_before_ids_resolve(self):
        self.check_ids(DESIGN_LOOKUP_BEFORE, "design")

    def test_steps_json_lookup_before_ids_resolve(self):
        if not STEPS_JSON.is_file():
            self.skipTest("references/steps.json not written yet")
        data = json.loads(STEPS_JSON.read_text(encoding="utf-8"))
        steps = data["steps"] if isinstance(data, dict) else data
        ids = sorted({t for s in steps for t in s.get("lookup_before", [])})
        for tid in ids:
            if "{" in tid and tid not in TEMPLATE_VALUES:
                stem = tid.split("{")[0]
                self.assertTrue(any(n.startswith(stem.lower()) for n in self.names), f"no topic for template {tid}")
        self.check_ids([t for t in ids if "{" not in t or t in TEMPLATE_VALUES], "steps.json")


class TestOneToolOneTopic(Base):
    def body(self, tid):
        return lookup.render(self.names[tid.lower()][1]).split("\n---\n", 1)[1]

    def test_cylinder_slab_tube_are_three_topics(self):
        ids = {self.names[t][1]["id"] for t in ("kit-cylinder", "kit-slabof", "kit-tubepieces")}
        self.assertEqual(len(ids), 3)
        self.assertEqual(self.names["kit-slab"][1]["id"], "kit-slabOf")
        self.assertEqual(self.names["kit-tube"][1]["id"], "kit-tubePieces")
        cyl, slab, tube = self.body("kit-cylinder"), self.body("kit-slabOf"), self.body("kit-tubePieces")
        self.assertIn("| `cylinder(cx, cy, r, z, h, P", cyl)
        self.assertIn("| `slabOf(plan, z, h, P", slab)
        self.assertIn("| `tubePieces(points3, radius, P", tube)
        for text, others in ((cyl, ("`slabOf(", "`tubePieces(", "`extrude(")),
                             (slab, ("`cylinder(", "`tubePieces(", "`extrude(")),
                             (tube, ("`cylinder(", "`slabOf(", "`tubeSvg(", "`runsOf(total"))):
            for o in others:
                self.assertNotIn("| " + o, text)

    def test_every_kit_function_in_the_named_sections_has_its_own_topic(self):
        lines = lookup.read_lines(SKILL / "scripts/anatomy/references/kit.md")
        heads = lookup.headings(lines)
        wanted = ("3.", "4.", "5.", "10.", "11.", "12.", "13.", "15.")
        rows = []
        for k, (idx, _, text) in enumerate(heads):
            chain = lookup.ancestors(heads, k) + [text]
            if not any(c.startswith(w) for c in chain for w in wanted):
                continue
            end = heads[k + 1][0] if k + 1 < len(heads) else len(lines)
            for _, _, rs in lookup.tables(lines, idx, end):
                rows += [lookup.cells(lines[r])[0] for r in rs]
        kit_rows = {e["row"] for e in self.index["topics"] if e["file"].endswith("kit.md") and e.get("row")}
        self.assertGreater(len(rows), 80)
        self.assertEqual(sorted(set(rows) - kit_rows), [])

    def test_camera_moves_and_transitions_are_one_chapter_each(self):
        for tid in ([f"camera-{m}" for m in TEMPLATE_VALUES["camera-{move}"]]
                    + [f"transition-{n}" for n in TEMPLATE_VALUES["transition-{name}"]]):
            body = self.body(tid).splitlines()
            heads = [ln for ln in body if lookup.HEADING_RE.match(ln)]
            self.assertEqual(len(heads), 1, f"{tid} prints more than its own chapter: {heads}")

    def test_section_stops_at_the_next_heading_of_same_level(self):
        pan = self.body("camera-pan")
        self.assertIn("### 01 Pan", pan)
        self.assertNotIn("02 Tilt", pan)


class TestCli(Base):
    def test_exact_id_prints_source_heading_and_section(self):
        r = run("camera-dolly-zoom")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("source: references/motion/camera.md", r.stdout)
        self.assertIn("heading: ", r.stdout)
        self.assertIn("08 Dolly zoom (Vertigo)", r.stdout)
        self.assertNotIn("09 Rack focus", r.stdout)

    def test_log_appends_a_tsv_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "slug"
            r1 = run("kit-cylinder", "--log", str(out))
            r2 = run("springs-track", "--log", str(out))
            self.assertEqual((r1.returncode, r2.returncode), (0, 0), r1.stderr + r2.stderr)
            log = (out / "docs" / "lookups.log").read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(log), 2)
            f = log[0].split("\t")
            self.assertEqual(len(f), 5, log[0])
            self.assertRegex(f[0], r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z$")
            datetime.fromisoformat(f[0].replace("Z", "+00:00"))
            self.assertEqual(f[1:4], ["kit-cylinder", "scripts/anatomy/references/kit.md", "3. Solids"])
            self.assertTrue(f[4].startswith("`cylinder("))
            self.assertEqual(log[1].split("\t")[1], "springs-track")
            self.assertLessEqual(f[0], log[1].split("\t")[0])

    def test_log_records_the_alias_that_was_asked_for(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = run("critique-rows-diagram-system", "--log", tmp)
            self.assertEqual(r.returncode, 0, r.stderr)
            line = (Path(tmp) / "docs" / "lookups.log").read_text(encoding="utf-8").strip()
            self.assertEqual(line.split("\t")[1], "critique-rows-diagram-system")

    def test_unknown_id_exits_1_with_candidates(self):
        r = run("camera-dolly-zom")
        self.assertEqual(r.returncode, 1)
        self.assertIn("unknown topic", r.stderr)
        self.assertIn("camera-dolly-zoom", r.stdout)
        r = run("camera-{move}")
        self.assertEqual(r.returncode, 1)
        self.assertIn("camera-pan", r.stdout)

    def test_unknown_id_writes_no_log(self):
        with tempfile.TemporaryDirectory() as tmp:
            run("no-such-topic", "--log", tmp)
            self.assertFalse((Path(tmp) / "docs" / "lookups.log").exists())

    def test_search_words_rank_candidates_without_a_section(self):
        r = run("pipe", "waypoints")
        self.assertEqual(r.returncode, 0, r.stderr)
        first = [ln for ln in r.stdout.splitlines() if ln.startswith("  ")][0]
        self.assertTrue(first.strip().startswith("craft-pipes-waypoints"), r.stdout)
        self.assertNotIn("\n---\n", r.stdout)

    def test_list_area(self):
        r = run("--list", "kit")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("kit-cylinder", r.stdout)
        self.assertNotIn("camera-pan", r.stdout)
        self.assertEqual(run("--list", "no-such-area").returncode, 1)

    def test_check_mode_passes(self):
        r = run("--check")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_runs_from_any_folder_with_an_absolute_log(self):
        # the canonical call: python3 "<skill>/scripts/lookup.py" <id> --log "<project>/.claude/draw/<slug>"
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "project" / ".claude" / "draw" / "paper-plane"
            r = subprocess.run([sys.executable, str(LOOKUP), "camera-pan", "--log", str(out)], cwd=tmp,
                               capture_output=True, text=True, encoding="utf-8", env=env(), timeout=120)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("### 01 Pan", r.stdout)
            self.assertTrue((out / "docs" / "lookups.log").is_file())

    def test_a_relative_log_resolves_against_the_working_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = subprocess.run([sys.executable, str(LOOKUP), "camera-pan", "--log", ".claude/draw/x"], cwd=tmp,
                               capture_output=True, text=True, encoding="utf-8", env=env(), timeout=120)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertTrue((Path(tmp) / ".claude/draw/x/docs/lookups.log").is_file())

    def test_a_log_inside_the_skill_is_refused(self):
        for target, cwd in ((str(SKILL / ".claude" / "draw" / "oops"), None), (".claude/draw/oops", SKILL)):
            r = subprocess.run([sys.executable, str(LOOKUP), "camera-pan", "--log", target], cwd=cwd,
                               capture_output=True, text=True, encoding="utf-8", env=env(), timeout=120)
            self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
            self.assertIn("inside the draw skill", r.stderr)
            self.assertEqual(r.stdout, "")
            self.assertFalse((SKILL / ".claude").exists(), "a refused --log must not create anything")

    def test_rebuild_dry_run_changes_nothing(self):
        before = INDEX_JSON.read_bytes(), INDEX_MD.read_bytes()
        r = run("--rebuild-index", "--dry-run")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("nothing written", r.stdout)
        self.assertNotIn("added ", r.stdout)
        self.assertNotIn("dropped ", r.stdout)
        self.assertEqual((INDEX_JSON.read_bytes(), INDEX_MD.read_bytes()), before)

    def test_rebuild_flags_need_the_rebuild_mode(self):
        self.assertEqual(run("camera-pan", "--rename", "a=b").returncode, 2)


class TestStepCommand(Base):
    """lookup.py --step <id> --log <out> [--value key=value ...]: the command each step runs first."""

    def read_log(self, folder: Path) -> list[list[str]]:
        return [ln.split("\t") for ln in (folder / "docs" / "lookups.log").read_text(encoding="utf-8").splitlines()]

    def test_step_prints_every_topic_and_logs_one_record_plus_topic_lines(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "opener"
            r = run("--step", "draft-camera-plan", "--log", str(out),
                    "--value", "move=push-in", "--value", "move=whip pan,static")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("step: draft-camera-plan — Cinematography plan", r.stdout)
            self.assertIn("done when: ", r.stdout)
            # push-in → camera-dolly; whip pan → its chapter; static names no extra topic
            self.assertIn("topics: camera-parallax-rule, camera-choosing, camera-dolly, transition-whip-pan", r.stdout)
            for chapter in ("03 Dolly in / out", "Whip pan", "The parallax rule", "Choosing the film's camera language"):
                self.assertIn(chapter, r.stdout)
            log = self.read_log(out)
            self.assertEqual(log[0][1:3], ["step", "draft-camera-plan"])
            self.assertEqual(log[0][3].split(), ["camera-parallax-rule", "camera-choosing", "camera-dolly",
                                                 "transition-whip-pan"])
            self.assertEqual([f[1] for f in log[1:]], log[0][3].split())
            self.assertEqual({f[0] for f in log}, {log[0][0]}, "the record and its topic lines share one time")

    def test_template_aliases_resolve(self):
        cases = (
            # every diagram step prints the diagram overrides first; mech-build-geometry prints the kit limits
            ("diagram-layout", ["chosen=erd", "size=doc-inline"], ["diagram-overrides", "type-er", "layout-4px-grid",
                                                                    "type-ramp"]),
            ("draft-seams", ["name=push", "name=cut"], ["transitions-rules", "transition-camera-carry",
                                                         "transition-hard-cut"]),
            ("mech-build-geometry", ["fn=slab", "fn=cylinder"], ["anatomy-build-geometry", "craft-tones",
                                                                  "mechanism-kit-limits", "kit-slabOf",
                                                                  "kit-cylinder"]),
            ("map-author", ["type=sequence"], ["map-type-router", "map-authoring-composition",
                                               "map-authoring-layout-routing", "map-example-sequence"]),
            ("critique-loop", ["form=film", "approach=free-creative"],
             ["critique-loop-order", "critique-shared-scorecard", "critique-rows-motion", "critique-rows-free-creative"]),
        )
        for step, values, topics in cases:
            argv = ["--step", step]
            for v in values:
                argv += ["--value", v]
            r = run(*argv)
            self.assertEqual(r.returncode, 0, step + ": " + r.stderr)
            self.assertIn("topics: " + ", ".join(topics) + "\n", r.stdout, step)
            self.assertIn("not logged", r.stderr)

    def test_form_and_approach_default_to_the_brief(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "bs"
            (out / "docs").mkdir(parents=True)
            (out / "docs" / "brief.md").write_text("Form: component\nApproach: mechanism\n", encoding="utf-8")
            r = run("--step", "critique-loop", "--log", str(out))
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("critique-rows-component, critique-rows-mechanism", r.stdout)
            r = run("--step", "mech-join-lane", "--log", str(out))
            self.assertIn("topics: mech-join-component\n", r.stdout)

    def test_unknown_step_value_or_missing_value_exits_1_and_logs_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "x"
            for argv, msg in (
                (["--step", "no-such-step"], "unknown step"),
                (["--step", "draft-camera-plan", "--value", "move=barrel roll"], "is not a known value for camera-{move}"),
                (["--step", "draft-camera-plan"], "camera-{move} needs --value move=<value>"),
                (["--step", "draft-storyboard", "--value", "move=pan"], "has no {move} template"),
                (["--step", "mech-build-geometry", "--value", "fn=noSuchBuilder"], "is not a known value for kit-{fn}"),
            ):
                r = run(*argv, "--log", str(out))
                self.assertEqual(r.returncode, 1, argv)
                self.assertIn(msg, r.stderr, argv)
                self.assertEqual(r.stdout, "", argv)
            self.assertFalse((out / "docs" / "lookups.log").exists())
        self.assertEqual(run("camera-pan", "--value", "move=pan").returncode, 2, "--value goes with --step")
        self.assertEqual(run("--step", "draft-storyboard", "camera-pan").returncode, 2)

    def test_every_step_runs_with_its_values(self):
        data = json.loads(STEPS_JSON.read_text(encoding="utf-8"))
        sample = {"move": "pan", "name": "hard-cut", "fn": "cylinder", "chosen": "flowchart", "size": "doc-inline",
                  "format": "mermaid", "type": "architecture", "form": "component", "approach": "mechanism"}
        for s in data["steps"]:
            argv = ["--step", s["id"]]
            for tid in s["lookup_before"]:
                if "{" in tid:
                    key = re.search(r"\{([^}]+)\}", tid).group(1)
                    argv += ["--value", f"{key}={sample[key]}"]
            r = run(*argv)
            self.assertEqual(r.returncode, 0, f"{s['id']}: {r.stderr}")

    def test_single_lookups_of_template_aliases_resolve(self):
        for alias, topic in (("camera-push-in", "camera-dolly"), ("camera-static", "camera-choosing"),
                             ("transition-push", "transition-camera-carry"), ("type-ramp-doc-inline", "type-ramp"),
                             ("type-erd", "type-er"), ("type-ramp-slide-16x9", "type-ramp")):
            self.assertIn(alias, self.names, alias)
            self.assertEqual(self.names[alias][1]["id"], topic, alias)

    def test_sync_aliases_has_nothing_left_to_add(self):
        before = INDEX_JSON.read_bytes(), INDEX_MD.read_bytes()
        r = run("--sync-aliases", "--dry-run")
        self.assertIn("dry run: 0 alias(es) to add", r.stdout, r.stdout + r.stderr)
        self.assertNotIn("FAIL", r.stdout)
        self.assertEqual((INDEX_JSON.read_bytes(), INDEX_MD.read_bytes()), before)


class TestRebuild(Base):
    """--rebuild-index against edited copies of a reference held in the line cache."""

    TRANS = "references/motion/transitions.md"

    def setUp(self):
        self.path = lookup.SKILL_ROOT / self.TRANS
        self.orig = list(lookup.read_lines(self.path))
        self.extra: list[Path] = []

    def tearDown(self):
        lookup._cache[self.path] = self.orig
        for p in self.extra:
            lookup._cache.pop(p, None)

    def test_unchanged_headings_keep_the_index_as_it_is(self):
        new, report = lookup.rebuild(self.index)
        self.assertEqual(report, [])
        self.assertEqual(lookup.dump_index(new), INDEX_JSON.read_text(encoding="utf-8"))

    def test_a_renamed_heading_keeps_its_id_and_a_new_heading_gets_one(self):
        lines = [("## Iris in / out" if ln == "## Iris" else ln) for ln in self.orig]
        lookup._cache[self.path] = lines
        new, report = lookup.rebuild(self.index)
        iris = [e for e in new["topics"] if e["id"] == "transition-iris"]
        self.assertEqual(len(iris), 1)
        self.assertEqual(iris[0]["heading"], "Iris in / out")
        self.assertEqual(lookup.check(new), [])
        k = self.orig.index("## Rules")
        lookup._cache[self.path] = (self.orig[:k] + ["## Fade to white", "", "A white flash carries the cut.", ""]
                                    + self.orig[k:])
        new, report = lookup.rebuild(self.index)
        self.assertNotIn("transition-iris", " ".join(report))
        added = [e for e in new["topics"] if e.get("heading") == "Fade to white"]
        self.assertEqual(len(added), 1, report)
        self.assertEqual(added[0]["file"], self.TRANS)
        self.assertEqual(added[0]["area"], "motion")
        self.assertRegex(added[0]["id"], r"^transitions?-.*fade-white")
        order = [e["id"] for e in new["topics"]]
        self.assertEqual(order.index(added[0]["id"]), order.index("transitions-director-notes-you-can-write") + 1)

    def test_a_renamed_file_keeps_every_id(self):
        new_rel = "references/motion/seams.md"
        new_path = lookup.SKILL_ROOT / new_rel
        self.extra.append(new_path)
        lookup._cache[new_path] = self.orig
        new, report = lookup.rebuild(self.index, renames={self.TRANS: new_rel})
        old_ids = [e["id"] for e in self.index["topics"] if e["file"] == self.TRANS]
        moved = [e["id"] for e in new["topics"] if e["file"] == new_rel]
        self.assertEqual(moved, old_ids)
        self.assertFalse(any(ln.startswith(("added", "dropped")) for ln in report), report)
        self.assertEqual(lookup.check(new), [])

    def test_a_missing_file_without_a_rename_is_reported(self):
        gone = dict(self.index)
        gone["topics"] = [dict(e, file="references/motion/no-such.md") if e["file"] == self.TRANS else e
                          for e in self.index["topics"]]
        _, report = lookup.rebuild(gone)
        self.assertTrue(any(ln.startswith("dropped transition-iris") for ln in report), report)


class TestIndexMd(Base):
    def test_index_md_is_generated_from_index_json(self):
        self.assertTrue(INDEX_MD.is_file(), "run python3 scripts/lookup.py --render-index")
        self.assertEqual(INDEX_MD.read_text(encoding="utf-8"), lookup.render_index_md(self.index),
                         "references/INDEX.md is stale: run python3 scripts/lookup.py --render-index")

    def test_index_md_lists_every_topic_grouped_by_area(self):
        text = INDEX_MD.read_text(encoding="utf-8")
        for area in {e["area"] for e in self.index["topics"]}:
            self.assertIn(f"\n## {area}\n", text)
        for e in self.index["topics"]:
            self.assertIn(f"- `{e['id']}` — ", text)


if __name__ == "__main__":
    unittest.main()
