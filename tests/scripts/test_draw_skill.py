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
- no vendored file reaches outside the skill for a file it needs.

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
        for word in ("diagram", "map", "motion", "explainer", "畫", "動畫", "/draw"):
            self.assertIn(word, desc, f"description should carry trigger word {word!r}")

    def test_four_lanes_and_spine(self):
        for h in ("## Lane: diagram", "## Lane: map", "## Lane: motion", "## Lane: page", "## The spine", "## Red lines", "## Completion report", "### Type router"):
            self.assertIn(h, self.body, f"missing section {h}")

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
        for rel in ("references/diagram/LICENSE", "references/diagram/THIRD_PARTY_LICENSES.md", "scripts/map/LICENSE", "scripts/map/THIRD_PARTY_NOTICES.md", "references/map/LICENSE", "scripts/hand-drawn/LICENSE", "references/motion/hand-drawn/LICENSE", "NOTICE.md"):
            self.assertTrue((SKILL / rel).is_file(), f"missing {rel}")

    def test_notice_lists_every_vendored_block(self):
        notice = (SKILL / "NOTICE.md").read_text(encoding="utf-8")
        for upstream in ("cathrynlavery/diagram-design", "tt-a1i/archify", "buildwithhanif/claude-animation-skill", "JohnHeibel/ClaudeAnimationBase"):
            self.assertIn(upstream, notice)
        for word in ("MIT", "CC BY 4.0"):
            self.assertIn(word, notice)


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
        self.assertIn("## The brief file", (SKILL / "references/motion/storyboard.md").read_text(encoding="utf-8"))
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


if __name__ == "__main__":
    unittest.main()
