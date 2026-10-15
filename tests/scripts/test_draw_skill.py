#!/usr/bin/env python3
"""Structural and executable guarantees for /draw (plugins/baransu/skills/draw).

/draw is a prose skill plus a bundle of vendored tooling. The prose is covered by
scripts/verify-skills.py; this file pins the parts that would silently rot:

- the four lanes name their entry references and every named file exists;
- every vendored block ships its license and is listed in NOTICE.md;
- the vendored tools run from their new location (archify `doctor`,
  diagram-design `self_check.py`, the repo verifiers);
- the motion library's math holds (spring settles at 1, track sums springs,
  the loop wraps, swapAlpha gates);
- sfx.mjs synthesizes a WAV from a cue list with no dependencies;
- no vendored file reaches outside the skill for a file it needs;
- the step guide holds: every topic references/steps.json names resolves,
  ledger-check.py passes honest simulated builds that run `lookup.py --step`
  before each step (a mechanism component with an example built under scratch/
  and generic calls in geometry.mjs, a film with push-in / whip pan and render
  --all names, a film with a 16:9 primary, a diagram at doc-inline, a map whose
  review shots carry archify's names, a page request: diagram-system components
  handed to /ui) and fails a step with no record, WebGL used without its steps,
  a record whose topics were not printed and a record with no template value;
  a late first version is reported, not failed; the critique card carries
  approach rows, and SKILL.md has no budget cuts or plan pause.

Browser-dependent checks (render, page verification) live in
tests/skills/test-draw-toolchain.sh so they can SKIP when Playwright/ffmpeg are
absent without weakening this file.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "plugins" / "baransu" / "skills" / "draw"
SKILL_MD = SKILL / "SKILL.md"


def run(cmd, cwd=None, timeout=120):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)


class TestStructure(unittest.TestCase):
    def setUp(self):
        self.assertTrue(SKILL_MD.is_file(), f"missing {SKILL_MD}")
        self.body = SKILL_MD.read_text(encoding="utf-8")

    def test_frontmatter_name_and_pushy_description(self):
        self.assertRegex(self.body, r"^---\nname: draw\n", "frontmatter must open with name: draw")
        m = re.search(r'^description: "(.+)"$', self.body, re.M)
        self.assertIsNotNone(m)
        desc = m.group(1)
        self.assertLessEqual(len(desc), 1024)
        for word in ("diagram", "map", "motion", "component", "/ui", "畫", "動畫", "說明頁", "show me", "draw it", "/draw"):
            self.assertIn(word, desc, f"description should carry trigger word {word!r}")

    def test_four_lanes_and_spine(self):
        for h in ("## Lane: diagram", "## Lane: map", "## Lane: film", "## Lane: component", "## The flow (every request)", "## Red lines", "## Completion report"):
            self.assertIn(h, self.body, f"missing section {h}")
        for gone in ("## Lane: page", "## Lane: motion"):
            self.assertNotIn(gone, self.body, f"retired section {gone}")
        # the map type router moved with the lane detail into references/lanes/map.md
        lane_map = (SKILL / "references" / "lanes" / "map.md").read_text(encoding="utf-8")
        self.assertIn("## Type router", lane_map)

    def test_every_referenced_bundled_path_exists(self):
        tokens = set(re.findall(r"(?:references|scripts|assets)/[A-Za-z0-9_./<>-]+", self.body))
        missing = []
        for tok in tokens:
            tok = tok.rstrip(".,;:)")
            if "<" in tok or tok.endswith("/"):
                continue
            if not (SKILL / tok).exists():
                missing.append(tok)
        self.assertEqual(missing, [], f"SKILL.md names bundled paths that do not exist: {missing}")

    def test_self_contained_wording(self):
        self.assertIn("Self-contained by design", self.body)
        self.assertNotIn("tokens.css", self.body)
        self.assertNotIn("/baransu:design", self.body)
        self.assertNotIn("WebSearch", self.body)

    def test_loop_pauses_registered(self):
        lp = SKILL / "references" / "loop-pauses.md"
        self.assertTrue(lp.is_file())
        self.assertIn("Authorization", lp.read_text(encoding="utf-8"))
        contract = (ROOT / "plugins/baransu/skills/_shared/loop-contract.md").read_text(encoding="utf-8")
        self.assertIn("| /draw | `../draw/references/loop-pauses.md` |", contract)

    def test_no_nested_references_dir_under_references(self):
        nested = [p for p in (SKILL / "references").rglob("references") if p.is_dir()]
        self.assertEqual(nested, [])


class TestLicenses(unittest.TestCase):
    def test_license_files_present(self):
        for rel in ("references/diagram/LICENSE", "references/diagram/THIRD_PARTY_LICENSES.md", "scripts/map/LICENSE", "scripts/map/THIRD_PARTY_NOTICES.md", "references/map/LICENSE", "scripts/hand-drawn/LICENSE", "references/motion/hand-drawn/LICENSE", "scripts/anatomy/LICENSE", "NOTICE.md"):
            self.assertTrue((SKILL / rel).is_file(), f"missing {rel}")

    def test_notice_lists_every_vendored_block(self):
        notice = (SKILL / "NOTICE.md").read_text(encoding="utf-8")
        for upstream in ("cathrynlavery/diagram-design", "tt-a1i/archify", "buildwithhanif/claude-animation-skill", "JohnHeibel/ClaudeAnimationBase", "wheresryan22/anatomy"):
            self.assertIn(upstream, notice)
        for word in ("MIT", "CC BY 4.0"):
            self.assertIn(word, notice)
        self.assertIn("scripts/anatomy/", notice, "NOTICE.md records the vendored Anatomy copy")


class TestVendoredToolsRun(unittest.TestCase):
    def test_diagram_references_complete(self):
        refs = SKILL / "references" / "diagram"
        types = sorted(p.name for p in refs.glob("type-*.md"))
        self.assertGreaterEqual(len(types), 44, f"expected the 44 upstream type references, found {len(types)}")
        for core in ("style-guide.md", "primitives-core.md", "layout-budget.md", "output-spec.md", "semantic-patterns.md", "animation.md", "README.md"):
            self.assertTrue((refs / core).is_file(), core)
        assets = SKILL / "assets" / "diagram"
        self.assertGreaterEqual(len(list(assets.glob("example-*.html"))), 200, "all upstream examples should be bundled")
        for t in ("template.html", "template-dark.html", "template-full.html", "template-motion.html", "template-terminal.html", "template-seek.html", "icons.html"):
            self.assertTrue((assets / t).is_file(), t)

    def test_self_check_runs_on_bundled_examples(self):
        for ex in ("example-architecture.html", "example-queue-animated.html", "example-sequence.html"):
            r = run([sys.executable, str(SKILL / "scripts/diagram/self_check.py"), str(SKILL / "assets/diagram" / ex)])
            self.assertEqual(r.returncode, 0, f"{ex}: {r.stdout}\n{r.stderr}")

    def test_seek_overlay_template_splits_into_a_clean_static_twin(self):
        """The seek template is a complete static diagram plus one overlay script:
        seek_split.py must strip exactly that and the twin must pass self_check."""
        with tempfile.TemporaryDirectory() as d:
            seek = Path(d) / "flow.seek.html"
            seek.write_text((SKILL / "assets/diagram/template-seek.html").read_text(encoding="utf-8"), encoding="utf-8")
            r = run([sys.executable, str(SKILL / "scripts/diagram/seek_split.py"), str(seek)])
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            twin = Path(d) / "flow.html"
            self.assertTrue(twin.is_file())
            t = twin.read_text(encoding="utf-8")
            self.assertNotIn("data-seek-overlay", t)
            self.assertNotRegex(t, r"<div[^>]*data-seek-controls", "the controls element is stripped (its CSS selectors may stay)")
            self.assertIn("data-seek-decorative", t, "decorative group stays in the twin, hidden by CSS")
            r = run([sys.executable, str(SKILL / "scripts/diagram/repo/verify-geometry.py"), str(twin)])
            self.assertEqual(r.returncode, 0, r.stdout[-400:])
        src = (SKILL / "assets/diagram/template-seek.html").read_text(encoding="utf-8")
        self.assertIn("window.seek", src)
        self.assertIn("window.timeline", src)
        self.assertNotIn("Math.random(", src)

    def test_repo_verifiers_point_at_draw_layout(self):
        repo = SKILL / "scripts/diagram/repo"
        stale = [p.name for p in repo.glob("*.py") if "skills/diagram-design" in p.read_text(encoding="utf-8")]
        self.assertEqual(stale, [], "vendored verifiers still resolve the upstream repo layout")
        for script, example in (("verify-geometry.py", "example-sequence.html"), ("verify-motion.py", "example-queue-animated.html"), ("lint-skin.py", "example-architecture.html")):
            r = run([sys.executable, str(repo / script), str(SKILL / "assets/diagram" / example)])
            self.assertEqual(r.returncode, 0, f"{script}: {r.stdout[-400:]}\n{r.stderr[-400:]}")

    @unittest.skipUnless(shutil.which("node"), "node not installed")
    def test_archify_doctor_and_validate(self):
        pkg = SKILL / "scripts/map"
        r = run(["node", "bin/archify.mjs", "doctor"], cwd=pkg, timeout=180)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("Archify is ready", r.stdout)
        r = run(["node", "bin/archify.mjs", "validate", "architecture", "examples/web-app.architecture.json", "--json"], cwd=pkg, timeout=180)
        self.assertEqual(r.returncode, 0, r.stdout[-600:] + r.stderr[-600:])

    def test_archify_package_keeps_what_the_cli_resolves(self):
        pkg = SKILL / "scripts/map"
        for rel in ("bin/archify.mjs", "renderers/shared/validator.mjs", "schemas/architecture.schema.json", "examples/web-app.architecture.json", "assets/template.html", "references/authoring-contract.md", "recipes/scenarios.mjs"):
            self.assertTrue((pkg / rel).exists(), rel)
        self.assertFalse((pkg / "test").exists(), "upstream test/ is deliberately not bundled")
        self.assertFalse((pkg / "node_modules").exists())


class TestMotionLibrary(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "node not installed")
    def test_spring_track_loop_swap(self):
        js = (
            "const M=require(process.argv[1]);"
            "const out={s0:M.spring(0),sInf:M.spring(10),sOver:Math.max(...Array.from({length:200},(_,i)=>M.spring(i/100,200,14))),"
            "tr:M.track(10,[[0,0],[1,100],[2,50]]),trMid:M.track(0.5,[[0,0],[1,100]]),loop:M.loopT(-1,8),"
            "swapIn:M.swapAlpha(0.0,0,1),swapMid:M.swapAlpha(0.5,0,1),swapOut:M.swapAlpha(0.99,0,1),"
            "rngA:M.rng(7)(),rngB:M.rng(7)(),grid:M.beatGrid(120).at(4),feel:M.feel('snappy',5)};"
            "console.log(JSON.stringify(out));"
        )
        r = run(["node", "-e", js, str(SKILL / "assets/motion/motion.js")])
        self.assertEqual(r.returncode, 0, r.stderr)
        o = json.loads(r.stdout)
        self.assertEqual(o["s0"], 0)
        self.assertAlmostEqual(o["sInf"], 1.0, places=5)
        self.assertGreater(o["sOver"], 1.0, "playful feel should overshoot")
        self.assertAlmostEqual(o["tr"], 50.0, places=3)
        self.assertEqual(o["trMid"], 0.0, "a spring that has not started contributes nothing")
        self.assertEqual(o["loop"], 7)
        self.assertEqual(o["swapIn"], 0)
        self.assertEqual(o["swapMid"], 1)
        self.assertEqual(o["swapOut"], 0)
        self.assertEqual(o["rngA"], o["rngB"], "seeded rng must be reproducible")
        self.assertAlmostEqual(o["grid"], 2.0)
        self.assertAlmostEqual(o["feel"], 1.0, places=5)

    @unittest.skipUnless(shutil.which("node"), "node not installed")
    def test_sfx_writes_wav_without_dependencies(self):
        with tempfile.TemporaryDirectory() as d:
            cues = Path(d) / "cues.json"
            cues.write_text(json.dumps({"duration": 2, "cues": [{"t": 0.25, "type": "click"}, {"t": 1.0, "type": "impact", "gain": 0.8}, {"t": 1.9, "type": "chime"}]}))
            out = Path(d) / "mix.wav"
            r = run(["node", str(SKILL / "scripts/motion/sfx.mjs"), str(cues), str(out), "--loop"])
            self.assertEqual(r.returncode, 0, r.stderr)
            b = out.read_bytes()
            self.assertEqual(b[:4], b"RIFF")
            self.assertEqual(b[8:12], b"WAVE")
            self.assertEqual(len(b), 44 + 2 * 48000 * 4, "2 s stereo 16-bit at 48 kHz")

    def test_beats_script_compiles_and_documents_fields(self):
        src = (SKILL / "scripts/motion/beats.py").read_text(encoding="utf-8")
        compile(src, "beats.py", "exec")
        for field in ("beats", "downbeats", "hits"):
            self.assertIn(f'"{field}"', src)

    def test_seek_template_keeps_the_render_contract(self):
        t = (SKILL / "assets/motion/seek-template.html").read_text(encoding="utf-8")
        self.assertIn("window.seek", t)
        self.assertIn("window.timeline", t)
        self.assertIn("navigator.webdriver", t)
        self.assertNotIn("Math.random(", t)
        self.assertNotIn("setTimeout", t)
        self.assertNotIn("transition:", t)
        # one timeline, three formats: the page reflows on ?f= and draws against the layout object
        for s in ("FORMATS", "get('f')", "const L = {", "cursor(", "words(", "countUp(", "wipe("):
            self.assertIn(s, t, s)

    @unittest.skipUnless(shutil.which("node"), "node not installed")
    def test_on_screen_helpers_are_pure_functions_of_t(self):
        js = (
            "const M=require(process.argv[1]);"
            "const c=M.cursor(1.0,[[0,100,100],[0.5,400,300]],[0.9]);"
            "const out={cx:c.x,down:c.down,scaleDip:c.scale<1,"
            "typedDone:M.typed(5,'hello',0,14,3).done,typedEmpty:M.typed(0,'hello',0.5).text,"
            "dragRest:M.drag(0,1,2,t=>t*100,0),dragHeld:M.drag(1.5,1,2,t=>t*100,0),dragBack:M.drag(20,1,2,t=>t*100,0),"
            "cam:M.camera(5,[[0,{x:0,y:0,w:1080,h:1920}],[1,{x:0,y:0,w:540,h:960}]],1080,1920).s,"
            "wordsN:M.words(1,'a b c',0).length,wordsStagger:M.words(0.1,'a b c',0).map(w=>w.p),"
            "wipeMid:M.wipe(0.15,0,0.3,1080,1920,'right').w,irisEnd:M.iris(1,0,0.3,100,100).p,whipBlur:M.whip(0,0,0.3,1080).blur,"
            "drawOnEnd:M.drawOn(5,0),blurAtIn:M.swapBlur(0,0,1)>0,blurMid:M.swapBlur(0.5,0,1),count:M.countUp(9,0,3393,0),"
            "sameT:JSON.stringify(M.cursor(0.7,[[0,0,0],[0.3,50,50]],[0.5]))===JSON.stringify(M.cursor(0.7,[[0,0,0],[0.3,50,50]],[0.5]))};"
            "console.log(JSON.stringify(out));"
        )
        r = run(["node", "-e", js, str(SKILL / "assets/motion/motion.js")])
        self.assertEqual(r.returncode, 0, r.stderr)
        o = json.loads(r.stdout)
        self.assertGreater(o["cx"], 350, "cursor has travelled on its spring")
        self.assertTrue(o["down"] and o["scaleDip"], "a click 0.1 s ago is still pressed and scaled down")
        self.assertTrue(o["typedDone"]); self.assertEqual(o["typedEmpty"], "")
        self.assertEqual(o["dragRest"], 0); self.assertAlmostEqual(o["dragHeld"], 150); self.assertAlmostEqual(o["dragBack"], 0, places=3)
        self.assertAlmostEqual(o["cam"], 2.0, places=3, msg="a half-size rect fills the frame at 2×")
        self.assertEqual(o["wordsN"], 3); self.assertTrue(o["wordsStagger"][0] > o["wordsStagger"][1] > o["wordsStagger"][2])
        self.assertAlmostEqual(o["wipeMid"], 540); self.assertEqual(o["irisEnd"], 1); self.assertEqual(o["whipBlur"], 0)
        self.assertAlmostEqual(o["drawOnEnd"], 1.0, places=5); self.assertTrue(o["blurAtIn"]); self.assertEqual(o["blurMid"], 0)
        self.assertAlmostEqual(o["count"], 3393, places=3); self.assertTrue(o["sameT"])

    def test_motion_toolchain_grew_with_the_screen_vocabulary(self):
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        render = (SKILL / "scripts/motion/render.mjs").read_text(encoding="utf-8")
        for mode in ("stills", "animatic", "--format", "--all", "--from", "--keep", "--safe", "safeArea"):
            self.assertIn(mode, render, mode)
        # the process rules the studio articles insisted on
        self.assertIn("safe:", (SKILL / "assets/motion/seek-template.html").read_text(encoding="utf-8"))
        self.assertIn("### 1. Write the brief", (SKILL / "references/motion/1-design.md").read_text(encoding="utf-8"))
        self.assertIn("## The film folder", (SKILL / "references/motion/pipeline.md").read_text(encoding="utf-8"))
        self.assertIn("| Continuity |", (SKILL / "references/critique-loop.md").read_text(encoding="utf-8"))
        pauses = (SKILL / "references/loop-pauses.md").read_text(encoding="utf-8")
        self.assertIn("asset manifest", pauses); self.assertIn("names a real asset", pauses)
        self.assertIn("audio)", (SKILL / "scripts/motion/checks.sh").read_text(encoding="utf-8"))
        self.assertIn("?f=", render)
        self.assertIn("refs)", (SKILL / "scripts/motion/checks.sh").read_text(encoding="utf-8"))
        self.assertTrue((SKILL / "scripts/motion/grab.mjs").is_file())
        for ref in ("references/motion/type.md", "references/motion/transitions.md"):
            self.assertTrue((SKILL / ref).is_file(), ref)
            self.assertIn(ref.split("/")[-1], skill, f"SKILL.md must point at {ref}")
        for s in ("grab.mjs", "Motion.cursor", "Motion.camera", "Motion.words", "animatic", "--all"):
            self.assertIn(s, skill, s)
        beat = (SKILL / "references/motion/beat-grid.md").read_text(encoding="utf-8")
        self.assertIn("music.mjs", beat); self.assertIn("--bed", beat)
        evals = json.loads((SKILL / "evals/evals.json").read_text(encoding="utf-8"))["evals"]
        self.assertGreaterEqual(sum("Motion lane" in e["expected_output"] for e in evals), 4, "four motion evals")

    def test_motion_references_are_five_phases_plus_a_technique_library(self):
        motion = SKILL / "references/motion"
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        readme = (motion / "README.md").read_text(encoding="utf-8")
        phases = ["1-design.md", "2-draft.md", "3-keys.md", "4-shoot.md", "5-post.md"]
        for i, name in enumerate(phases, 1):
            text = (motion / name).read_text(encoding="utf-8")
            self.assertTrue(text.startswith(f"# Phase {i} — "), name)
            self.assertIn("## Gate checklist", text, name)
            self.assertIn(name, readme, f"README must route to {name}")
            self.assertIn(f"references/motion/{name}", skill, f"SKILL.md must route to {name}")
        self.assertIn("references/motion/README.md", skill)
        # every motion reference is reachable from the map; no orphans
        for p in motion.glob("*.md"):
            if p.name != "README.md":
                self.assertIn(f"`{p.name}`", readme, f"README must list {p.name}")
        # the retired files stay retired; their content lives in the phases and the library
        for gone in ("storyboard.md", "keyframes.md", "prompt-ladder.md", "directing.md", "brief.md"):
            self.assertFalse((motion / gone).exists(), gone)
        draft = (motion / "2-draft.md").read_text(encoding="utf-8")
        self.assertIn("wide → 3 → 1", draft); self.assertIn("6 : 3 : 1", draft); self.assertTrue((motion / "composition.md").is_file()); self.assertIn("docs/camera_plan.md", draft)
        self.assertIn("## The key card", (motion / "3-keys.md").read_text(encoding="utf-8"))

    def test_flow_is_preflight_form_approach_production_check(self):
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        steps = ["### 0. Preflight", "### 1. Choose the form", "### 2. Choose the approach", "### 3. Production", "### 4. Check and deliver"]
        pos = [skill.index(h) for h in steps]
        self.assertEqual(pos, sorted(pos), "the five steps appear in order")
        self.assertIn('node "<skill>/scripts/motion/doctor.mjs" --install', skill)
        for a in ("**Diagram system**", "**Mechanism**", "**Free creative**"):
            self.assertIn(a, skill)
        form_sec = skill.split("### 1. Choose the form")[1].split("### 2.")[0]
        for f in ("**diagram**", "**map**", "**film**", "**component**"):
            self.assertIn(f, form_sec)
        self.assertNotIn("**page**", form_sec, "draw has no page form; /ui assembles pages")

    def test_toolchain_finds_browsers_on_every_os_and_ships_a_loop_template(self):
        browser = (SKILL / "scripts/motion/browser.mjs").read_text(encoding="utf-8")
        for s in ("pathToFileURL", "LOCALAPPDATA", "Library", "chrome-win64/chrome.exe", "chrome-mac-arm64"):
            self.assertIn(s, browser, s)
        for f in ("render.mjs", "grab.mjs", "verify-page.mjs", "doctor.mjs"):
            self.assertIn("./browser.mjs", (SKILL / "scripts/motion" / f).read_text(encoding="utf-8"), f)
        render = (SKILL / "scripts/motion/render.mjs").read_text(encoding="utf-8")
        self.assertIn("'4:5': [1080, 1350]", render); self.assertIn("ALL_FORMATS", render)
        loop = (SKILL / "assets/motion/loop-template.html").read_text(encoding="utf-8")
        for s in ("window.seek", "loopNoise", "wrappedSpring", "seam", "TAU * p"):
            self.assertIn(s, loop, s)
        self.assertIn("## Known environment failures", (SKILL / "references/motion/pipeline.md").read_text(encoding="utf-8"))

    def test_mechanism_figures_are_a_cross_lane_section(self):
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("## Mechanism figures (any form)", skill)
        sec = skill.split("## Mechanism figures (any form)")[1].split("\n## ")[0]
        for lane in ("**component**", "**film**", "**diagram**"):
            self.assertIn(lane, sec, f"the section must say how it lands in {lane}")
        self.assertIn("怎麼運作", sec)
        # SKILL.md routes only to the router and the vendored upstream skill; the router lists the rest
        self.assertTrue((SKILL / "references/mechanism/mechanism.md").is_file())
        self.assertFalse((SKILL / "references/motion/mechanism.md").exists(), "mechanism.md moved out of motion/")
        self.assertIn("references/mechanism/mechanism.md", skill)
        self.assertIn("scripts/anatomy/ANATOMY-SKILL.md", skill)


READ_FIRST = SKILL / "references" / "read-first.json"
STEPS_JSON = SKILL / "references" / "steps.json"
INDEX_JSON = SKILL / "references" / "index.json"
LEDGER_CHECK = SKILL / "scripts" / "ledger-check.py"
STEP_KEYS = ("id", "applies_to", "title", "do", "done_when", "lookup_before", "produces")
OPTIONAL_STEP_KEYS = ("ordered", "all_products")
FORMS = ("diagram", "map", "film", "component")
APPROACH_NAMES = ("diagram-system", "mechanism", "free-creative")


def _load_module(name, path):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_lookup():
    return _load_module("draw_lookup_for_ledger_tests", SKILL / "scripts" / "lookup.py")


def run_ledger(folder, *extra):
    import os
    env = dict(os.environ)
    env.update(PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    return subprocess.run(
        [sys.executable, str(LEDGER_CHECK), str(folder), *extra],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120, env=env,
    )


class Builder:
    """An honest builder, simulated: it walks references/steps.json in order and, for every step that
    applies to the declared facts, runs the step command `lookup.py --step <id> --log <folder>
    [--value key=value ...]` and only then writes that step's products (appending to a product an
    earlier step already wrote).

    `values` maps a step id to the --value arguments the builder passes (the values it decided; the
    test states them, independently of how ledger-check reads the artifact). `files` holds the content
    of a product (rel path → text); `names` maps a produces pattern to the concrete paths written for
    it; `extra` maps a step id to further files that step writes (e.g. render --all siblings);
    `actions` maps a step id to a callable(folder) run during the step (e.g. a scratch copy).
    Deviations for the failure fixtures: `skip` (steps never done), `unrecorded` (steps done without
    their step command), `late` (steps whose files are written first, then the step command runs,
    then the files are touched again), `forge` (steps whose record is written by hand, with no
    topic lines), `topic_first` (step id → topics looked up one by one before the step command)."""

    _lookup = None
    _index = None

    def __init__(self, folder: Path, facts, *, files=None, names=None, values=None, extra=None, actions=None,
                 skip=(), unrecorded=(), late=(), forge=(), topic_first=None):
        if Builder._lookup is None:
            Builder._lookup = _load_lookup()
            Builder._index = Builder._lookup.load_index()
            Builder._lookup.load_index = lambda: Builder._index
        self.folder, self.facts = folder, set(facts) | {"all"}
        self.files, self.names, self.values = files or {}, names or {}, values or {}
        self.extra, self.actions = extra or {}, actions or {}
        self.skip, self.unrecorded, self.late, self.forge = set(skip), set(unrecorded), set(late), set(forge)
        self.topic_first = topic_first or {}
        self.slug = folder.name
        self.performed, self.failed = [], []

    def applies(self, step) -> bool:
        return any(all(a in self.facts for a in clause.split("&")) for clause in step["applies_to"])

    def _quiet(self, argv) -> tuple[int, str]:
        import contextlib
        import io
        err = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            rc = Builder._lookup.main(argv)
        return rc, err.getvalue()

    def step_command(self, step) -> None:
        argv = ["--step", step["id"], "--log", str(self.folder)]
        for v in self.values.get(step["id"], []):
            argv += ["--value", v]
        rc, err = self._quiet(argv)
        if rc != 0:
            self.failed.append(f"{step['id']}: {err.strip()[:300]}")

    def forge_record(self, step) -> None:
        from datetime import datetime, timezone
        stamp = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
        topics = [t for t in step["lookup_before"] if "{" not in t]
        log = self.folder / "docs" / "lookups.log"
        log.parent.mkdir(parents=True, exist_ok=True)
        with log.open("a", encoding="utf-8", newline="\n") as fh:
            fh.write("\t".join([stamp, "step", step["id"], " ".join(topics)]) + "\n")

    def concrete(self, pattern: str) -> list[str]:
        if pattern in self.names:
            return list(self.names[pattern])
        rel = pattern.replace("{slug}", self.slug)
        if rel in ("*.html", "<name>.html"):
            return [f"{self.slug}.html"]
        if rel == "<page-name>.html":
            return []
        rel = re.sub(r"<[^>]+>", "x", rel)
        rel = rel.replace("*", "a")
        if rel.endswith("/"):
            rel += "a.png"
        return [rel]

    def write(self, step) -> None:
        import time
        rels = [rel for pattern in step["produces"] for rel in self.concrete(pattern)]
        for rel in rels + list(self.extra.get(step["id"], [])):
            p = self.folder / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            if p.exists():
                with p.open("a", encoding="utf-8") as fh:
                    fh.write(f"\n<!-- {step['id']} -->\n")
            else:
                p.write_text(self.files.get(rel, f"{step['id']}: {rel}\n"), encoding="utf-8")
        time.sleep(0.003)

    def run(self) -> "Builder":
        import time
        steps = json.loads(STEPS_JSON.read_text(encoding="utf-8"))["steps"]
        for step in steps:
            if not self.applies(step) or step["id"] in self.skip:
                continue
            self.performed.append(step["id"])
            sid = step["id"]
            for tid in self.topic_first.get(sid, []):
                rc, err = self._quiet([tid, "--log", str(self.folder)])
                if rc != 0:
                    self.failed.append(f"{tid}: {err.strip()[:200]}")
                time.sleep(0.003)
            if sid in self.late:
                self.write(step)
                time.sleep(0.05)
                self.step_command(step)
                time.sleep(0.05)
                self.write(step)
                continue
            if sid in self.forge:
                self.forge_record(step)
            elif sid not in self.unrecorded:
                self.step_command(step)
            time.sleep(0.003)
            if sid in self.actions:
                self.actions[sid](self.folder)
            self.write(step)
        if self.failed:
            raise AssertionError("the builder's step commands failed:\n" + "\n".join(self.failed))
        return self


def slug_folder(tmp: str, slug: str) -> Path:
    p = Path(tmp) / slug
    p.mkdir()
    return p


def copy_anatomy_to_scratch(folder: Path) -> None:
    """mechanism.md's way to build an upstream example: a whole copy of the kit under <out>/scratch/."""
    shutil.copytree(SKILL / "scripts" / "anatomy", folder / "scratch" / "anatomy",
                    ignore=shutil.ignore_patterns("node_modules"))


# (a) a mechanism component: "how binary search works", an example built under scratch/
MECH_COMPONENT = dict(
    facts={"form:component", "approach:mechanism"},
    files={
        "docs/brief.md": "# Brief\nForm: component — how binary search works, one figure to play with\n"
                         "Approach: mechanism\nWhen: none\nSize: Hero\n",
        "docs/mapping.md": "CONCEPT: binary search halves a sorted range\n"
                           "OBJECT: a sorting-office ladder whose gate drops on the middle pigeonhole "
                           "(our own object; catalog rows 02, 05, 11 studied, the lab balance is not redrawn)\n",
        # generic calls (Map.set, a local draw) beside the kit builders ask for nothing more
        "geometry.mjs": 'import * as k from "../../scripts/anatomy/kit/iso-kit.mjs";\n'
                        "const parts = new Map();\n"
                        "export const base = k.slabOf(plan, 0, 4, P);\n"
                        "export const post = k.cylinder(0, 0, 3, 4, 40, P);\n"
                        "parts.set('post', post);\n"
                        "function draw(ctx) { return ctx; }\n"
                        "draw(parts);\n",
        "binary-search.html": "<!doctype html><title>Binary search</title>"
                              "<style>/* ISO_CSS */</style><script>/* kitScript() */</script>\n",
    },
    names={"<name>.html": ["binary-search.html"], "*.html": ["binary-search.html"],
           "shots/example-<name>.png": ["shots/example-dial-indicator.png"]},
    values={
        # kit-slab is an index alias of kit-slabOf
        "mech-build-geometry": ["fn=slab", "fn=cylinder"],
    },
    actions={"mech-catalog-and-example": copy_anatomy_to_scratch},
)

# (b) a 15 s film with named camera moves and seams, rendered with --all
FILM = dict(
    facts={"form:film", "approach:free-creative"},
    files={
        "docs/brief.md": "# Brief\nForm: film — a 15 s product opener\nApproach: free-creative\nWhen: none\n",
        "docs/camera_plan.md": "| shot | size | move | reason |\n|---|---|---|---|\n"
                               "| 1 | wide | Move: push-in 0–2 s, ease out | the hook lands |\n"
                               "| 2 | medium | Move: whip pan, 6 frames | carry to the dashboard |\n"
                               "| 3 | close | Move: none | hold on the number |\n\n"
                               "Notes: the camera keeps tracking the cursor in shot 2; no handheld shake; "
                               "the zoom level of the UI stays fixed.\n",
        "docs/seams.md": "- Seam: hard cut — open on frame 0\n- Seam: whip pan — shot 1 to 2\n"
                         "- Seam: cross-dissolve — shot 2 to 3 (we wipe the slate clean here)\n"
                         "- Seam: hard cut — out\n",
    },
    values={
        "draft-camera-plan": ["move=push-in", "move=whip pan", "move=none"],
        "draft-seams": ["name=hard cut", "name=whip pan,cross-dissolve"],
    },
    extra={
        # render.mjs full --all writes the primary unsuffixed master beside the format siblings
        "post-render-master": ["out/opener-9x16.mp4", "out/opener-1x1.mp4", "out/opener-16x9.mp4"],
        "shoot-dailies": ["out/opener-9x16.contact.png"],
    },
)

# (c) an architecture diagram at the default size preset
DIAGRAM = dict(
    facts={"form:diagram", "approach:diagram-system"},
    files={
        "docs/brief.md": "# Brief\nForm: diagram — a reference figure for the docs\nApproach: diagram-system\nWhen: none\n",
        "docs/diagram_plan.md": "Type: architecture\nSize: doc-inline (960 × 600)\nDetail: overview\nNodes: 7\n",
    },
    values={"diagram-layout": ["chosen=architecture", "size=doc-inline"]},
)

# (e) a request that needs a page: two diagram-system components, then /ui assembles the page
PAGE_REQUEST = dict(
    facts={"form:component", "approach:diagram-system", "when:needs-page"},
    files={
        "docs/brief.md": "# Brief\nForm: component — explain the TCP handshake (說明頁): two figures and a page\n"
                         "Approach: diagram-system\nWhen: needs-page\n",
        "docs/diagram_plan.md": "Type: sequence + state\nSize: doc-inline\n",
        "docs/ui_brief.md": "# UI brief\nPage: tcp-handshake-explained.html\n"
                            "Components: tcp-handshake-sequence.html, tcp-handshake-window.html\n",
    },
    names={"<name>.html": ["tcp-handshake-sequence.html", "tcp-handshake-window.html"],
           "*.html": ["tcp-handshake-sequence.html", "tcp-handshake-window.html"],
           "<page-name>.html": ["tcp-handshake-explained.html"]},
    values={"diagram-layout": ["chosen=sequence", "chosen=state", "size=doc-inline"]},
)


def map_scenario():
    example = SKILL / "scripts" / "map" / "examples" / "async-job-roundtrip.sequence.json"
    return dict(
        facts={"form:map", "approach:diagram-system"},
        files={
            "docs/brief.md": "# Brief\nForm: map — explore the async job roundtrip\nApproach: diagram-system\nWhen: none\n",
            "candidate.json": example.read_text(encoding="utf-8"),
        },
        values={"map-author": ["type=sequence"]},
    )


def build(tmp: str, scenario: dict, slug: str = "run", **deviations) -> Path:
    folder = slug_folder(tmp, slug)
    kwargs = {k: scenario.get(k) for k in ("files", "names", "values", "extra", "actions")}
    kwargs.update(deviations)
    Builder(folder, scenario["facts"], **kwargs).run()
    return folder


def record_topics(folder: Path, step: str) -> list[str]:
    """The topic ids of a step's step records in docs/lookups.log (fixed topics may grow; values are the test's)."""
    out = []
    for line in (folder / "docs" / "lookups.log").read_text(encoding="utf-8").splitlines():
        f = line.split("\t")
        if len(f) > 3 and f[1] == "step" and f[2] == step:
            out += f[3].split()
    return out


def row(stdout: str, step: str) -> str:
    """'<status> <detail>' of a step's row in ledger-check's table, or '' when the step has no row."""
    m = re.search(rf"^\| {re.escape(step)}\s+\| (\S+)\s+\| (.*)$", stdout, re.M)
    return f"{m.group(1)} {m.group(2)}" if m else ""


class TestReferenceFidelity(unittest.TestCase):
    """The 7.5.0 step guide: steps.json names resolvable topics; each step runs its step command
    (lookup.py --step) before its work; ledger-check proves every applicable step has a record whose
    topics were printed; approach rows, no budget, no stops."""

    def test_steps_json_replaces_read_first_and_every_topic_resolves(self):
        self.assertFalse(READ_FIRST.exists(), "read-first.json was replaced by steps.json + lookup.py")
        data = json.loads(STEPS_JSON.read_text(encoding="utf-8"))
        lookup = _load_lookup()
        index = json.loads(INDEX_JSON.read_text(encoding="utf-8"))
        names = lookup.by_name(index)
        templates = data["templates"]
        ids, problems = [], []
        atom = re.compile(r"^(all|form:(%s)|approach:(%s)|when:[a-z0-9-]+)$"
                          % ("|".join(FORMS), "|".join(APPROACH_NAMES)))
        for s in data["steps"]:
            keys = tuple(s)
            self.assertEqual(keys[:len(STEP_KEYS)], STEP_KEYS, f"{s.get('id')}: keys out of order or missing")
            self.assertTrue(set(keys[len(STEP_KEYS):]) <= set(OPTIONAL_STEP_KEYS), f"{s['id']}: unknown keys")
            ids.append(s["id"])
            for clause in s["applies_to"]:
                for part in clause.split("&"):
                    if not atom.match(part):
                        problems.append(f"{s['id']}: bad applies_to atom {part!r}")
            for pat in s["produces"]:
                if re.search(r"(^|/)(index\.html|final\.mp4)$|^out/(animatic\.mp4|contact\.png|poster\.png)$", pat):
                    problems.append(f"{s['id']}: product {pat} is not the name render.mjs writes")
            for tid in s["lookup_before"]:
                if "{" in tid:
                    if tid not in templates:
                        problems.append(f"{s['id']}: template {tid} has no templates entry")
                    continue
                if tid.lower() not in names:
                    problems.append(f"{s['id']}: {tid} is not in the index")
                    continue
                try:
                    lookup.render(names[tid.lower()][1])
                except lookup.Unresolved as exc:
                    problems.append(f"{s['id']}: {tid}: {exc}")
        for tid, spec in templates.items():
            stem = tid.split("{")[0]
            values = list(spec.get("values", []))
            if spec.get("values_from_files"):
                values += [p.stem[len(stem):] for p in SKILL.glob(spec["values_from_files"])]
            values += [v for v in spec.get("aliases", {}).values()]
            if spec.get("from") in ("@form", "@approach"):
                chosen = FORMS if spec["from"] == "@form" else APPROACH_NAMES
                values += [spec.get("map", {}).get(v, v) for v in chosen
                           if tid != "mech-join-{form}" or v in spec.get("map", {})]
            if spec.get("calls_of_index_prefix"):
                values += ["slabOf", "cylinder", "tubePieces"]
            self.assertTrue(values, tid)
            for v in set(values):
                if (stem + v).lower() not in names:
                    problems.append(f"template {tid}: {stem + v} is not in the index")
            # every alias spelling is an index alias too, so a single lookup of it resolves
            if not spec.get("from", "").startswith("@") and not spec.get("calls_of_index_prefix"):
                for alias in spec.get("aliases", {}):
                    if (stem + alias).lower() not in names:
                        problems.append(f"template {tid}: alias {stem + alias} is not in the index "
                                        "(run lookup.py --sync-aliases)")
                if spec.get("none") and (stem + spec["none"][0]).lower() not in names:
                    problems.append(f"template {tid}: {stem + spec['none'][0]} is not in the index")
        self.assertEqual(len(ids), len(set(ids)), "duplicate step ids")
        self.assertEqual(problems, [], "\n".join(problems))
        for must in ("preflight", "choose-form", "choose-approach", "mech-size", "brief-and-status-line",
                     "progress-notes", "mech-invent-object", "mech-build-geometry", "mech-painters-order",
                     "mech-make-live", "mech-audit", "webgl-layer", "component-caption-states",
                     "component-perf-plan", "component-figure-card", "component-rest-frame",
                     "component-interaction", "component-check", "first-version",
                     "critique-loop", "assemble-page", "ledger-check", "deliver-report"):
            self.assertIn(must, ids)
        self.assertFalse([i for i in ids if i.startswith("page-")], "the page form is gone: no page-* steps")
        self.assertEqual(ids[-3:], ["assemble-page", "ledger-check", "deliver-report"])
        by_id = {s["id"]: s for s in data["steps"]}
        # every form runs a browser check, so preflight applies to all of them
        self.assertEqual(by_id["preflight"]["applies_to"], ["all"])
        # the five anatomy steps that were missing their upstream chapters
        for sid, topic in (("mech-invent-object", "anatomy-invent-object"),
                           ("mech-build-geometry", "anatomy-build-geometry"),
                           ("mech-painters-order", "anatomy-painters-order"),
                           ("mech-make-live", "anatomy-make-live"), ("mech-audit", "anatomy-verify-critic")):
            self.assertIn(topic, by_id[sid]["lookup_before"], sid)
        # the /draw override is read before the upstream size chapter, and the check enforces the order
        self.assertEqual(by_id["mech-size"]["lookup_before"][:2], ["mech-overrides", "anatomy-size-classes"])
        self.assertTrue(by_id["mech-size"].get("ordered"))
        catalog = by_id["mech-catalog-and-example"]
        self.assertIn("invent your own object", catalog["do"])
        self.assertIn("never redraw a published figure", catalog["do"])
        self.assertIn("scratch/", catalog["do"])
        self.assertIn("docs/catalog_notes.md", catalog["produces"])
        # WebGL is not tied to an approach
        self.assertEqual(by_id["webgl-layer"]["applies_to"], ["when:webgl"])
        self.assertEqual(by_id["webgl-check"]["applies_to"], ["when:webgl"])
        # the page is /ui's: the last production step hands the components over in the same turn
        hand = by_id["assemble-page"]
        self.assertEqual(hand["applies_to"], ["when:needs-page"])
        self.assertIn("/ui", hand["do"]); self.assertIn("Skill", hand["do"]); self.assertIn("do not ask", hand["do"])
        self.assertTrue(hand.get("all_products"))
        self.assertEqual(hand["produces"], ["docs/ui_brief.md", "<page-name>.html"])
        # the names render.mjs writes, and a component named for its figure
        for sid, product in (("draft-animatic", "out/{slug}.animatic.mp4"), ("shoot-dailies", "out/{slug}.contact.png"),
                             ("post-render-master", "out/{slug}.mp4"), ("post-finish", "out/{slug}.poster.png"),
                             ("component-figure-card", "<name>.html"), ("design-film-folder", "{slug}.film.html")):
            self.assertIn(product, by_id[sid]["produces"], sid)
        render = (SKILL / "scripts" / "motion" / "render.mjs").read_text(encoding="utf-8")
        self.assertIn("--all also writes the 9:16 output unsuffixed", render)
        # the status line carries the delivery field
        self.assertIn("／交付 (單件|多件|元件＋/ui 組頁)／", by_id["brief-and-status-line"]["done_when"])
        # time discipline (plan § 3.8): the clock, progress lines, the stall rule, the first hour
        prog, first = by_id["progress-notes"], by_id["first-version"]
        self.assertEqual(prog["applies_to"], ["all"]); self.assertEqual(first["applies_to"], ["all"])
        self.assertIn("twice its share", prog["do"]); self.assertIn("no wait, no question", prog["do"])
        self.assertIn("two consecutive rounds", prog["do"])
        self.assertIn("one hour", first["do"]); self.assertIn("do not wait for a reply", first["do"])
        self.assertIn("60 minutes", first["done_when"])
        self.assertIn("two consecutive rounds", by_id["critique-loop"]["done_when"])
        # every type reference is a value of type-{chosen}
        self.assertTrue(templates["type-{chosen}"].get("values_from_files"))
        self.assertGreaterEqual(len(list(SKILL.glob(templates["type-{chosen}"]["values_from_files"]))), 44)

    # ---- honest runs: every applicable step's command runs before its work

    def assert_rows_pass(self, stdout, steps):
        for step in steps:
            self.assertTrue(row(stdout, step).startswith("pass "), step + ": " + row(stdout, step))

    def test_honest_mechanism_component_with_an_example_in_scratch_passes(self):
        with tempfile.TemporaryDirectory() as d:
            out = build(d, MECH_COMPONENT, slug="binary-search")
            self.assertTrue((out / "scratch" / "anatomy" / "examples" / "raptor-engine" / "build.mjs").is_file())
            r = run_ledger(out)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("ledger-check: PASS", r.stdout)
            # the scratch copy of the kit and its examples sets off no detector
            for fact in ("when:webgl", "when:3d"):
                self.assertNotIn(f"detected {fact}", r.stdout)
            self.assert_rows_pass(r.stdout, (
                "progress-notes", "mech-size", "mech-catalog-and-example", "mech-invent-object",
                "mech-build-geometry", "mech-make-live", "component-figure-card", "mech-frame-card",
                "mech-join-lane", "component-check", "first-version", "critique-loop"))
            # Map.set and a local draw() in geometry.mjs are not kit builders the ledger asks about
            self.assertTrue(row(r.stdout, "mech-build-geometry").startswith("pass 1 record(s)"),
                            row(r.stdout, "mech-build-geometry"))
            self.assertTrue({"kit-slabOf", "kit-cylinder"} <= set(record_topics(out, "mech-build-geometry")))
            self.assertNotIn("kit-set", r.stdout)
            self.assertNotIn("kit-draw", r.stdout)

    def test_honest_film_with_named_moves_and_render_all_names_passes(self):
        with tempfile.TemporaryDirectory() as d:
            out = build(d, FILM, slug="opener")
            for rel in ("opener.film.html", "out/opener.mp4", "out/opener-9x16.mp4", "out/opener.contact.png",
                        "out/opener.animatic.mp4", "out/opener.poster.png"):
                self.assertTrue((out / rel).is_file(), rel)
            r = run_ledger(out)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            # push-in is camera-dolly, whip pan its own chapter, plus the fixed camera topics
            self.assertRegex(row(r.stdout, "draft-camera-plan"), r"^pass 1 record\(s\), \d+ topic\(s\) printed")
            self.assert_rows_pass(r.stdout, ("draft-seams", "draft-animatic", "shoot-dailies",
                                             "post-render-master", "post-finish", "post-review-export"))

    def test_honest_film_with_a_16x9_primary_passes(self):
        # a 16:9 sibling rendered beside another primary (--primary 9:16 --format 16:9) carries the -16x9
        # suffix on every output; the ledger reads no file names, so the suffixed set passes as well
        sixteen = {"out/{slug}.mp4": ["out/opener-16x9.mp4"],
                   "out/{slug}.animatic.mp4": ["out/opener-16x9.animatic.mp4"],
                   "out/{slug}.contact.png": ["out/opener-16x9.contact.png"],
                   "out/{slug}.poster.png": ["out/opener-16x9.poster.png"]}
        film = dict(FILM, names=sixteen, extra={})
        with tempfile.TemporaryDirectory() as d:
            out = build(d, film, slug="opener")
            self.assertFalse((out / "out" / "opener.mp4").exists())
            self.assertTrue((out / "out" / "opener-16x9.mp4").is_file())
            r = run_ledger(out)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assert_rows_pass(r.stdout, ("draft-animatic", "shoot-dailies", "post-render-master", "post-finish"))

    def test_honest_architecture_diagram_at_doc_inline_passes(self):
        with tempfile.TemporaryDirectory() as d:
            out = build(d, DIAGRAM, slug="routing-bands")
            r = run_ledger(out)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            # doc-inline is a size preset of the standard ramp: type-ramp-doc-inline resolves to type-ramp
            self.assertTrue(row(r.stdout, "diagram-layout").startswith("pass 1 record(s)"),
                            row(r.stdout, "diagram-layout"))
            self.assertTrue(row(r.stdout, "preflight").startswith("pass"), "preflight applies to a diagram too")
            self.assertTrue({"type-architecture", "type-ramp"} <= set(record_topics(out, "diagram-layout")))

    def test_honest_map_from_a_bundled_example_passes(self):
        # archify visual-check writes <slug>.map.visual-check.json and .<WxH>.<theme>.png next to the map;
        # the step names that receipt, and nothing writes shots/map-*.png
        steps = json.loads(STEPS_JSON.read_text(encoding="utf-8"))["steps"]
        step = next(s for s in steps if s["id"] == "map-perceptual-review")
        self.assertEqual(step["produces"], ["{slug}.map.visual-check.json"])
        self.assertNotIn("shots/map-", json.dumps(step))
        scenario = map_scenario()
        scenario["names"] = {"{slug}.map.visual-check.json": ["async-job.map.visual-check.json",
                                                             "async-job.map.visual-check.1440x900.light.png",
                                                             "async-job.map.visual-check.1440x900.dark.png"]}
        with tempfile.TemporaryDirectory() as d:
            out = build(d, scenario, slug="async-job")
            self.assertFalse((out / "shots").exists())
            r = run_ledger(out)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertTrue(row(r.stdout, "map-author").startswith("pass 1 record(s)"), row(r.stdout, "map-author"))
            self.assertIn("map-example-sequence", record_topics(out, "map-author"))
            self.assert_rows_pass(r.stdout, ("map-finalize", "map-perceptual-review", "critique-loop"))

    def test_honest_page_request_with_diagram_components_hands_off_to_ui_and_passes(self):
        with tempfile.TemporaryDirectory() as d:
            out = build(d, PAGE_REQUEST, slug="tcp-handshake")
            self.assertTrue((out / "tcp-handshake-explained.html").is_file(), "the page /ui wrote")
            r = run_ledger(out)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assert_rows_pass(r.stdout, ("assemble-page", "diagram-plan", "diagram-markup", "diagram-check",
                                             "diagram-taste-gate", "component-figure-card"))
            self.assertTrue(row(r.stdout, "diagram-layout").startswith("pass 1 record(s)"),
                            row(r.stdout, "diagram-layout"))
            self.assertTrue({"type-sequence", "type-state", "type-ramp"} <= set(record_topics(out, "diagram-layout")))

    def test_a_late_first_version_is_reported_not_failed(self):
        with tempfile.TemporaryDirectory() as d:
            out = build(d, DIAGRAM, slug="routing-bands")
            log = out / "docs" / "lookups.log"
            # the run's first log line two hours before the first version
            first = log.read_text(encoding="utf-8").splitlines()[0].split("\t")
            topic_line = next(l for l in log.read_text(encoding="utf-8").splitlines() if l.split("\t")[1] != "step")
            fields = topic_line.split("\t")
            fields[0] = "2000-01-01T00:00:00.000Z"
            log.write_text("\t".join(fields) + "\n" + log.read_text(encoding="utf-8"), encoding="utf-8")
            self.assertNotEqual(first[0], fields[0])
            r = run_ledger(out)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("note: the first version came", r.stdout)
            self.assertIn("say so in the completion report", r.stdout)

    def test_upto_checks_only_the_steps_done_so_far(self):
        """The critique loop runs the ledger before its own record and before the /ui page
        assembly; --upto critique-loop must not ask for those later steps."""
        with tempfile.TemporaryDirectory() as d:
            out = build(d, DIAGRAM, slug="routing-bands", skip={"critique-loop", "deliver-report"})
            full = run_ledger(out)
            self.assertEqual(full.returncode, 1, full.stdout)
            mid = run_ledger(out, "--upto", "critique-loop")
            self.assertEqual(mid.returncode, 0, mid.stdout + mid.stderr)
            self.assertNotIn("| critique-loop", mid.stdout)
            bad = run_ledger(out, "--upto", "no-such-step")
            self.assertEqual(bad.returncode, 2, bad.stdout + bad.stderr)

    # ---- dishonest runs

    def test_a_step_without_a_record_fails(self):
        with tempfile.TemporaryDirectory() as d:
            out = build(d, DIAGRAM, slug="routing-bands", unrecorded={"diagram-layout"})
            r = run_ledger(out)
            self.assertEqual(r.returncode, 1, r.stdout)
            self.assertRegex(r.stdout, r"\| diagram-layout\s+\| FAIL\s+\| no step record")
            self.assertTrue(row(r.stdout, "diagram-plan").startswith("pass"))
            self.assertIn("ledger-check: FAIL", r.stdout)
        with tempfile.TemporaryDirectory() as d:
            # a step skipped outright (no record, no work) fails the same way
            out = build(d, FILM, slug="opener", skip={"draft-camera-plan"})
            r = run_ledger(out)
            self.assertEqual(r.returncode, 1, r.stdout)
            self.assertRegex(row(r.stdout, "draft-camera-plan"), r"^FAIL no step record")

    def test_webgl_used_without_its_steps_fails(self):
        scenario = dict(
            facts={"form:component", "approach:free-creative"},
            files={"docs/brief.md": "# Brief\nForm: component — a glowing loading widget\n"
                                    "Approach: free-creative\nWhen: none\n",
                   "glow.html": '<!doctype html><figure data-fig="1"><canvas id="gl"></canvas></figure>'
                                '<script>const g = document.getElementById("gl").getContext(%s);</script>'},
            names={"<name>.html": ["glow.html"]},
        )
        with tempfile.TemporaryDirectory() as d:
            webgl = dict(scenario, files={**scenario["files"], "glow.html": scenario["files"]["glow.html"] % '"webgl2"'})
            out = build(d, webgl, slug="glow")
            r = run_ledger(out)
            self.assertEqual(r.returncode, 1, r.stdout)
            self.assertIn("detected when:webgl (uses WebGL, glow.html) — not declared", r.stdout)
            self.assertRegex(r.stdout, r"\| webgl-layer\s+\| FAIL\s+\| no step record")
            self.assertRegex(r.stdout, r"\| webgl-check\s+\| FAIL\s+\| no step record")
        with tempfile.TemporaryDirectory() as d:
            # the same component drawing in 2D passes: the detector is what made the WebGL steps apply
            flat = dict(scenario, files={**scenario["files"], "glow.html": scenario["files"]["glow.html"] % '"2d"'})
            out = build(d, flat, slug="glow")
            r = run_ledger(out)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertNotIn("webgl-layer", r.stdout)
        with tempfile.TemporaryDirectory() as d:
            # WebGL inside the scratch copy is not the artifact's
            flat = dict(scenario, files={**scenario["files"], "glow.html": scenario["files"]["glow.html"] % '"2d"'},
                        actions={"component-figure-card": lambda f: (f / "scratch").mkdir() or
                                 (f / "scratch" / "gl.mjs").write_text('c.getContext("webgl2")', encoding="utf-8")})
            out = build(d, flat, slug="glow")
            r = run_ledger(out)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_a_record_whose_topics_were_not_printed_fails(self):
        with tempfile.TemporaryDirectory() as d:
            # a hand-written step line, no topic lines behind it
            out = build(d, DIAGRAM, slug="routing-bands", forge={"diagram-taste-gate"})
            r = run_ledger(out)
            self.assertEqual(r.returncode, 1, r.stdout)
            self.assertRegex(row(r.stdout, "diagram-taste-gate"),
                             r"^FAIL the step record at line \d+ lists topics that were not printed: .*"
                             r"taste-anti-patterns, taste-preoutput-checklist")

    def test_a_record_with_no_template_value_fails(self):
        lookup = _load_lookup()
        names = lookup.by_name(lookup.load_index())
        with tempfile.TemporaryDirectory() as d:
            out = build(d, DIAGRAM, slug="routing-bands", unrecorded={"diagram-layout"})
            # a record that printed only the fixed topic: neither {chosen} nor {size} was filled
            lookup.append_step_record(out, "diagram-layout", [("layout-4px-grid", names["layout-4px-grid"][1])])
            r = run_ledger(out)
            self.assertEqual(r.returncode, 1, r.stdout)
            self.assertIn("no topic filled from type-{chosen}, type-ramp-{size}", row(r.stdout, "diagram-layout"))

    def test_ledger_check_needs_a_form_and_a_log(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            (out / "docs").mkdir()
            (out / "docs" / "brief.md").write_text("# Brief\nno routing lines here\n", encoding="utf-8")
            (out / "docs" / "lookups.log").write_text("", encoding="utf-8")
            r = run_ledger(out)
            self.assertEqual(r.returncode, 1, r.stdout)
            self.assertIn("no Form: line", r.stdout)
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            (out / "docs").mkdir()
            (out / "docs" / "brief.md").write_text(DIAGRAM["files"]["docs/brief.md"], encoding="utf-8")
            r = run_ledger(out)
            self.assertEqual(r.returncode, 1, r.stdout)
            self.assertIn("docs/lookups.log is missing", r.stdout)
        with tempfile.TemporaryDirectory() as d:
            # the retired page form names no form any more
            out = Path(d)
            (out / "docs").mkdir()
            (out / "docs" / "brief.md").write_text("Form: page\nApproach: mechanism\n", encoding="utf-8")
            (out / "docs" / "lookups.log").write_text("", encoding="utf-8")
            r = run_ledger(out)
            self.assertIn("Form: -", r.stdout)

    def test_skill_md_has_no_budget_cuts_or_input_pause(self):
        body = SKILL_MD.read_text(encoding="utf-8")
        for banned in ("砍掉", "complexity budget", "Input PAUSE"):
            self.assertNotIn(banned, body, f"SKILL.md still says {banned!r}")

    def test_critique_loop_gates_on_the_ledger_and_approach_rows(self):
        text = (SKILL / "references/critique-loop.md").read_text(encoding="utf-8")
        self.assertIn("scripts/ledger-check.py", text)
        self.assertIn("8-point gate", text)
        for h in ("### Mechanism", "### Diagram", "### Motion and camera", "### Component"):
            self.assertIn(h, text, h)
        mech = text.split("### Mechanism")[1].split("\n### ")[0]
        for s in ("scripts/anatomy/scripts/lines.mjs", "line ends: 0", "build.mjs --audit", "0.6 px", "One lit part",
                  "40+ parts", "4× detail", "pointer and the keyboard", "one model", "scripts/motion/perf-check.mjs"):
            self.assertIn(s, mech, s)
        self.assertIn("| machine |", mech)
        self.assertIn("| judged |", mech)
        self.assertIn("self_check.py", text.split("### Diagram")[1].split("\n### ")[0])
        self.assertIn("camera.md", text.split("### Motion and camera")[1].split("\n### ")[0])
        comp = text.split("### Component rows")[1].split("\n### ")[0]
        self.assertIn("verify-page.mjs", comp); self.assertIn("perf-check.mjs", comp)
        self.assertNotIn("### Page", text)
        self.assertNotRegex(text, r"(?i)\bask (the user|for)\b")
        self.assertNotRegex(text, r"(?i)\bstop (when|and)\b")

    def test_anatomy_is_vendored_without_a_nested_skill_md(self):
        anatomy = SKILL / "scripts" / "anatomy"
        self.assertTrue((anatomy / "ANATOMY-SKILL.md").is_file())
        nested = [str(p.relative_to(SKILL)) for p in anatomy.rglob("*") if p.name.upper() == "SKILL.MD"]
        self.assertEqual(nested, [], "a nested SKILL.md would be loaded as a separate skill")

    def test_mechanism_router_points_at_anatomy_and_overrides_upstream(self):
        text = (SKILL / "references/mechanism/mechanism.md").read_text(encoding="utf-8")
        self.assertIn("ANATOMY-SKILL.md", text)
        self.assertRegex(text, r"(?i)overrid", "the router must state where /draw overrides upstream")
        for gone in ("never start it unasked", "announce it, then build", "rough effort", "workload estimate"):
            self.assertNotIn(gone, text, f"the router still downscales or estimates effort: {gone!r}")
        size = next(line for line in text.splitlines() if "Upstream workflow step 1" in line)
        for s in ("尺寸", "開工狀態行", "No time estimate", "progress clock", "does not apply"):
            self.assertIn(s, size, s)
        # the router is the anatomy step table: ten upstream steps, each with its lookups and its steps.json step
        table = text.split("## The anatomy step table")[1].split("\n## ")[0]
        rows = [ln for ln in table.splitlines() if re.match(r"^\| (\d+) \|", ln)]
        self.assertEqual([int(re.match(r"^\| (\d+)", r).group(1)) for r in rows], list(range(1, 11)))
        step_ids = {s["id"] for s in json.loads(STEPS_JSON.read_text(encoding="utf-8"))["steps"]}
        names = _load_lookup().by_name(json.loads(INDEX_JSON.read_text(encoding="utf-8")))
        for r in rows:
            cells = [c.strip() for c in r.strip("|").split("|")]
            topics = re.findall(r"`([^`]+)`", cells[2])
            self.assertTrue(topics, r)
            for t in topics:
                self.assertTrue("{" in t or t.lower() in names, f"router names unknown topic {t}")
            for sid in re.findall(r"`([^`]+)`", cells[3]):
                self.assertTrue(sid in step_ids or sid.lower() in names, f"router names unknown step {sid}")
        self.assertIn("never read whole", text)
        self.assertNotIn("Read first, in full", text)
        self.assertNotIn("read-first.json", text)
        self.assertIn("scratch", text.split("## Study an example")[1].split("\n## ")[0],
                      "examples are built in a scratch copy, never inside the skill")

    def test_every_chromium_launch_seeds_the_password_check(self):
        """Windows Chromium probes LogonUser(user, ".", "") when a fresh profile opens a tab; ten
        fresh profiles in ten minutes lock the user's account (event 4625, 2026-10-13). Every
        launcher in the skill must start Chromium on a profile whose Local State records the check.

        Checked per launch site, not per file, in both the Claude copy and the Codex copy, over every
        file of the skill (SKILL.md, NOTICE.md and the other skill-root files included; fenced code
        only in .md): a line that starts Chromium must have the Local State seed beside it. A seed
        written out by hand (not the shared seedProfile()/launchChromium() of browser.mjs) must
        also carry the '/draw:' provenance marker, which the Codex sync keeps untransformed. A
        launch() call is always bare: Playwright's launch() and launchServer() refuse a user-data-dir,
        so they always open a fresh profile — on any receiver (chromium, browserType, a destructured
        or renamed BrowserType such as `const { chromium: c } = pw; c.launch()`). Firefox and WebKit
        are never started at all. A spawn of a Chrome / Chromium / Edge executable (named in the call,
        or through a variable assigned from a chrome path) is a launch site like --user-data-dir.
        A browser tool that opens its own fresh profile (agent-browser, `npx playwright open`,
        `playwright screenshot`) is never runnable, unless the file is vendored verbatim and an
        override in the same skill copy names that exact command and says it does not apply. Every
        text file is scanned (.tsx, .json, .yaml, .ps1 and extensionless included), and so is
        ui/SKILL.md, whose browser checks run through draw's scripts."""
        # A launch that needs the Local State seed within `window` lines.
        site = re.compile(r"launch_persistent_context\(|launchPersistentContext\("
                          r"|--user-data-dir|\bp\.chromium\b|puppeteer\.launch\(")
        # A launch that is wrong wherever it appears: no seed can reach the profile it opens.
        always_bare = re.compile(r"(?<!puppeteer)\.launch\(|\.launchServer\(|\blaunch_server\("
                                 r"|\b(?:firefox|webkit)\.launch\w*\(|\bp\.(?:firefox|webkit)\b"
                                 r"|\b(?:firefox|webkit)\.launch_persistent_context\(")
        call = re.compile(r"\b(?:\w*[sS]pawn\w*|exec(?:File)?(?:Sync)?|fork|Popen"
                          r"|subprocess\.(?:run|call|check_call|check_output))\s*\(\s*\[?\s*([^,)\]]*)")
        browser_exe = re.compile(r"chrom|msedge|edge\.exe", re.I)
        assigned = re.compile(r"(?:\b(?:const|let|var)\s+)?\b(\w+)\s*=\s*[^;\n=]*(?:chrom|msedge|edge\.exe)", re.I)
        shell_exe = re.compile(r"^\s*(?:exec\s+|Start-Process\s+(?:-FilePath\s+)?|&\s*)?[\"']?(?:\$\{?\w*CHROM\w*\}?"
                               r"|\S*(?:google-chrome(?:-stable)?|chromium(?:-browser)?|chrome(?:\.exe)?|msedge(?:\.exe)?))[\"']?(?:\s|$)",
                               re.I)
        renamed = re.compile(r"\{[^}]*\b(chromium|firefox|webkit)\s*:\s*(\w+)"
                             r"|\b(\w+)\s*=\s*(?:await\s+)?(?:[\w$]+\.)*(chromium|firefox|webkit)\b\s*(?:[;,)]|$)")
        seed = re.compile(r"os_password_last_changed|seedProfile\(")
        helper = re.compile(r"seedProfile\(|launchChromium\(")
        window = 40   # lines either side of the launch site that may hold the seed
        # Lines that name a launch flag without starting a browser.
        not_a_launch = {
            ("scripts/anatomy/scripts/chrome-startup.test.mjs", "case \"$arg\" in --user-data-dir=*)"),
        }
        # Browser tools that open their own fresh profile: never runnable from the skill.
        fresh_tool = re.compile(r"\bagent-browser\b|\bnpx\s+(?:-y\s+)?playwright\s+(?:open|screenshot|codegen|pdf|cr|ff|wk)\b"
                                r"|(?<![\w-])playwright\s+(?:screenshot|open|codegen|pdf)\b", re.I)
        # A vendored file kept verbatim may keep such a command only when an override in the same skill
        # copy names that exact command and says it does not apply: (file, fragment) → (override file, text).
        overridden = {
            ("references/diagram/onboarding.md", "agent-browser navigate"):
                ("references/diagram/README.md", "its `agent-browser navigate …` command do not apply"),
        }

        # Data and text files hold instructions inline as prose: a clause that forbids a launch
        # ("never a bare chromium.launch()", "never agent-browser, ...") is not one.
        forbidding = re.compile(r"\b(?:never|not|no)\b.*?(?=\.\s|[;\"]|$)", re.I)
        prose_suffixes = {".json", ".yaml", ".yml", ".toml", ".txt"}

        def scan(rel, lines, shell, root=None, prose=False):
            """(launch sites, problems) for one file's runnable lines."""
            if prose:
                lines = [forbidding.sub("", line) for line in lines]
            text = "\n".join(lines)
            tool_problems = []
            for i, line in enumerate(lines):
                if not fresh_tool.search(line):
                    continue
                cover = next((o for (f, frag), o in overridden.items() if rel == f and frag in line), None)
                if cover and root is not None and cover[1] in (root / cover[0]).read_text(encoding="utf-8"):
                    continue
                tool_problems.append(f"{rel}:{i + 1}: a browser tool that opens a fresh profile: {line.strip()[:100]}")
            browser_vars = {m.group(1) for m in assigned.finditer(text)
                            if m.group(1) not in {"const", "let", "var"}}
            other_engine, chromium_alias = set(), set()
            for m in renamed.finditer(text):
                engine, name = (m.group(1), m.group(2)) if m.group(1) else (m.group(4), m.group(3))
                (chromium_alias if engine == "chromium" else other_engine).add(name)
            alias_launch = (re.compile(r"\b(?:" + "|".join(map(re.escape, sorted(other_engine))) + r")\.launch\w*\(")
                            if other_engine else None)
            found, problems = 0, []
            for i, line in enumerate(lines):
                if any(rel == f and frag in line for f, frag in not_a_launch):
                    continue
                spawned = call.search(line)
                spawn_site = bool(spawned and (browser_exe.search(spawned.group(1))
                                               or spawned.group(1).strip().strip("'\"") in browser_vars))
                shell_site = shell and bool(shell_exe.search(line))
                if not (site.search(line) or always_bare.search(line) or spawn_site or shell_site
                        or (alias_launch and alias_launch.search(line))):
                    continue
                found += 1
                near = "\n".join(lines[max(0, i - window): i + window + 1])
                if always_bare.search(line) or (alias_launch and alias_launch.search(line)):
                    problems.append(f"{rel}:{i + 1}: {line.strip()[:120]}")
                elif not seed.search(near):
                    problems.append(f"{rel}:{i + 1}: {line.strip()[:120]}")
                elif not helper.search(near) and "/draw:" not in near:
                    problems.append(f"{rel}:{i + 1}: hand-written seed without its '/draw:' marker: {line.strip()[:100]}")
            return found + len(tool_problems), problems + tool_problems

        # The patterns themselves: each of these unseeded launches must be caught.
        must_catch = {
            "chromium.launch": "const b = await chromium.launch({ headless: true });",
            "launchServer": "const server = await chromium.launchServer();",
            "browserType.launch": "const b = await browserType.launch();",
            "renamed BrowserType": "const { chromium: c } = await import('playwright');\nconst b = await c.launch();",
            "assigned BrowserType": "const bt = pw.chromium;\nconst b = await bt.launch();",
            "firefox": "const b = await firefox.launch();",
            "webkit persistent": "const ctx = await webkit.launchPersistentContext(dir);",
            "renamed firefox": "const { firefox: ff } = pw;\nconst ctx = await ff.launchPersistentContext(dir);",
            "python firefox": "browser = p.firefox.launch()",
            "python launch_server": "server = p.chromium.launch_server()",
            "spawn chrome": "const c = spawn('C:/Program Files/Google/Chrome/Application/chrome.exe', ['--headless=new']);",
            "spawn msedge": "spawnSync('msedge.exe', ['--headless', url]);",
            "spawn via variable": "const exe = findChrome();\nconst child = spawn(exe, args);",
            "python Popen": "proc = subprocess.Popen([chrome_path, '--headless=new', url])",
        }
        for label, sample in must_catch.items():
            n, problems = scan("sample.mjs", sample.splitlines(), shell=False)
            self.assertTrue(n and problems, f"the launch scan misses an unseeded launch: {label}")
        for label, sample in {"shell chrome": 'google-chrome --headless=new --screenshot "$url"',
                              "shell variable": '"$CHROME" --headless=new "$url"',
                              "Start-Process msedge": "Start-Process msedge.exe -ArgumentList '--headless'"}.items():
            n, problems = scan("sample.sh", sample.splitlines(), shell=True)
            self.assertTrue(n and problems, f"the launch scan misses an unseeded launch: {label}")
        # Browser tools that open a fresh profile, in any runnable line.
        for label, sample in {"agent-browser": "agent-browser navigate https://example.com --screenshot out.png",
                              "npx playwright open": "npx playwright open https://example.com",
                              "playwright screenshot": "npx -y playwright screenshot https://example.com shot.png",
                              "bare playwright screenshot": "playwright screenshot --full-page \"$url\" out.png"}.items():
            n, problems = scan("sample.sh", sample.splitlines(), shell=True)
            self.assertTrue(n and problems, f"the launch scan misses a fresh-profile browser tool: {label}")
        # An override only covers the exact vendored command it names, and only while its text is there.
        n, problems = scan("references/diagram/onboarding.md",
                           ["agent-browser navigate https://example.com --screenshot out.png"], shell=True)
        self.assertTrue(problems, "an override is honoured without reading the override file")
        # Data files: a command in a value is caught; a clause that forbids one is not a launch.
        n, problems = scan("package.json", ['  "scripts": { "shot": "npx playwright screenshot page.html out.png" }'],
                           shell=False, prose=True)
        self.assertTrue(problems, "the launch scan misses a fresh-profile browser tool in a data file")
        n, problems = scan("steps.json", ['{"do": "never a bare chromium.launch() and never agent-browser. Then run it."}'],
                           shell=False, prose=True)
        self.assertEqual(problems, [], "the launch scan flags a clause that forbids a launch")
        n, problems = scan("ok.mjs", ["const browser = await launchChromium(pw, { executablePath: exe });",
                                      "const ctx = await chromium.launchPersistentContext(dir); // seedProfile(dir) above"],
                           shell=False)
        self.assertEqual(problems, [], "the launch scan flags a seeded launch")
        # Every text file: code, data, config, PowerShell and extensionless scripts; binaries are skipped by content.
        code_suffixes = {".mjs", ".js", ".cjs", ".py", ".sh", ".ts", ".tsx", ".jsx", ".html", ".htm", ".md",
                         ".json", ".yaml", ".yml", ".toml", ".txt", ".ps1", ".psm1", ".cmd", ".bat", ".css", ""}
        shell_suffixes = {".sh", ".md", ".ps1", ".psm1", ".cmd", ".bat", ""}
        skills = SKILL.parent
        codex_skills = ROOT / "codex" / "plugins" / "baransu" / "skills"
        roots = [(skills, "")] + ([(codex_skills, "codex:")] if (codex_skills / "draw").is_dir() else [])
        files = []
        for root, tag in roots:
            n = 0
            for p in (root / "draw").rglob("*"):
                if (p.is_file() and "node_modules" not in p.parts and "__pycache__" not in p.parts
                        and p.suffix.lower() in code_suffixes and b"\0" not in p.read_bytes()[:8192]):
                    files.append((root, tag, p))
                    n += 1
            self.assertGreater(n, 100, f"the scan of {root / 'draw'} found too few files; the walk is broken")
            self.assertIn((root, tag, root / "draw" / "SKILL.md"), files, "skill-root files are not scanned")
            self.assertTrue(any(p.suffix == ".json" for r, _, p in files if r == root), "data files are not scanned")
            # /ui hands its browser checks to draw's seeded scripts: its SKILL.md is scanned with draw.
            ui = root / "ui" / "SKILL.md"
            self.assertTrue(ui.is_file(), f"{ui} is missing")
            files.append((root, tag, ui))
        bare, sites = [], 0
        for root, tag, p in files:
            rel = p.relative_to(root / "draw").as_posix() if (root / "draw") in p.parents else p.relative_to(root).as_posix()
            lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
            if p.suffix == ".md":   # prose may name a launch call; only fenced code is run
                fenced, keep = False, []
                for line in lines:
                    if line.lstrip().startswith("```"):
                        fenced = not fenced
                        keep.append("")
                    else:
                        keep.append(line if fenced else "")
                lines = keep
            n, problems = scan(rel, lines, shell=p.suffix.lower() in shell_suffixes, root=root / "draw",
                               prose=p.suffix.lower() in prose_suffixes)
            sites += n
            bare += [tag + problem for problem in problems]
        self.assertGreaterEqual(sites, 6 * len(roots), "the known seeded launch sites were not found; the pattern is broken")
        self.assertEqual(bare, [], "launch through scripts/motion/browser.mjs launchChromium() or seed Local State beside the launch")
        node = shutil.which("node")
        if node is None:
            if sys.platform == "win32":
                self.fail("node is not on PATH: the seedProfile check guards the Windows account lockout and must run here")
            self.skipTest("node unavailable (not Windows)")
        with tempfile.TemporaryDirectory() as d:
            out = subprocess.run(
                [node, "--input-type=module", "-e",
                 "import { seedProfile } from './browser.mjs'; import fs from 'node:fs'; import path from 'node:path';"
                 " const d = seedProfile(process.argv[1]); process.stdout.write(fs.readFileSync(path.join(d, 'Local State'), 'utf8'));", d],
                cwd=SKILL / "scripts" / "motion", capture_output=True, text=True, timeout=60)
            if out.returncode != 0:
                msg = f"seedProfile run failed ({out.returncode}): {(out.stderr or out.stdout)[:300]}"
                if sys.platform == "win32":
                    self.fail(msg)
                self.skipTest(msg)
            pm = json.loads(out.stdout)["password_manager"]
            self.assertIs(pm["os_password_blank"], False)
            # Chromium time: µs since 1601; must sit after any real password change (here: after now).
            now_us = int(__import__("time").time() * 1_000_000) + 11644473600 * 1_000_000
            self.assertGreater(int(pm["os_password_last_changed"]), now_us)

    def test_anatomy_landing_page_is_vendored_whole(self):
        """The Anatomy landing page is kept verbatim (plan §0 item 4), attributed and MIT-licensed."""
        page = SKILL / "references" / "mechanism" / "anatomy-page.md"
        text = page.read_text(encoding="utf-8")
        head = text.splitlines()[0]
        self.assertTrue(head.startswith("<!--") and head.endswith("-->"), "the file opens with its source comment")
        for s in ("https://skills.wheresryan.sh/anatomy", "2026-10-13", "MIT, for the skill and for the figures"):
            self.assertIn(s, head)
        sections = ["Objects, not diagrams", "Writing a prompt", "What Claude does", "Anatomy of a figure",
                    "Six machines, up close", "Two big machines", "Three layers", "How long it takes",
                    "In your code", "Install", "Limits", "Questions"]
        headings = re.findall(r"(?m)^## (\d\d) (.+)$", text)
        self.assertEqual(headings, [(f"{i:02d}", s) for i, s in enumerate(sections, 1)])
        # Verbatim sentences from different sections, the code blocks and the footnotes.
        for s in ("The object is the explanation.",
                  "**Size it.** Say up front whether this is a Figure, a Hero or an Epic",
                  "held.rate += (want - held.at) * stiff * slice - held.rate * damping * slice;",
                  "out.push(S(k.slabOf(PLATE, -PLATE_H, PLATE_H, P, 8, 1.6), { tone: \"mid\" }));",
                  "| Epic | A whole vehicle, building or plant | 6 h or more |",
                  "The first working version took 38 minutes.",
                  "npx skills add wheresryan22/anatomy",
                  "`--anatomy-lit` The one accent: the part the reader should watch.",
                  "**What is the licence?**",
                  "[^5]: The audit measured 6,320 overlapping pairs across 541 solids"):
            self.assertIn(s, text)
        refs = set(re.findall(r"\[\^(\d+)\](?!:)", text))
        notes = set(re.findall(r"(?m)^\[\^(\d+)\]:", text))
        self.assertEqual(refs, notes, "every note marker has its footnote and the reverse")
        self.assertEqual(len(notes), 8)
        self.assertEqual(text.count("```") % 2, 0, "fenced code blocks are balanced")
        self.assertNotRegex(text, r"<(script|style|svg)\b", "markup is stripped")
        notice = (SKILL / "NOTICE.md").read_text(encoding="utf-8")
        self.assertIn("references/mechanism/anatomy-page.md", notice)


if __name__ == "__main__":
    unittest.main()
