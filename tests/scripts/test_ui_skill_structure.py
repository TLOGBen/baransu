"""Byte-level pins for the rebuilt /ui skill (formerly /design) and the surfaces its removal touched
(CONTRACT.md A1, A5–A8, A10, and the seal 2026-09-11 criteria patch).

Behavior is covered by skill-creator evals (evals/evals.json); this file only
pins what evals cannot: verbatim absorption of the frontend-design sections
(vendored sha256, so the pin never depends on the source being installed), the
license bytes, the NOTICE text, the Verbatim Constants and fixed sentences, the
directory manifest, and the consumer surfaces that must not regress.
"""
import hashlib
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / "plugins/baransu/skills"
SKILL_DIR = SKILLS / "ui"
SKILL = SKILL_DIR / "SKILL.md"
SHIP = SKILLS / "ship/SKILL.md"
SRC_DIR = Path.home() / ".claude/plugins/marketplaces/claude-plugins-official/plugins/frontend-design/skills/frontend-design"

SECTION_SHA256 = {
    "## Ground your designs in the subject matter": "ff3df5a1425221c3ee562af162fb08642d1dde574662a918bca1bf255e985cd2",
    "## Design principles": "3a2db7b8708b9ef81f8f87c53d6e705eeec93022833fa4fef4ef4d6e791943c7",
    "## Process: plan, review against the brief, build, critique": "48dc53911b825870f61c84801c31c96d6e91c7f11e319c6f63ac9a28c14f4a4f",
    "## Restraint and self-critique": "e830f2b880a4b7f7ef2666778983d375a72f28c497d481aeb86ec2663c467784",
    "## More on writing in design": "f1b9b215ba24e9058bd8b09afa99a4b22091d4cc079c9c811b964b283004aecf",
}
LICENSE_SHA256 = "0d542e0c8804e39aa7f37eb00da5a762149dc682d7829451287e11b938e94594"
NOTICE_LINES = [
    "SKILL.md derives from the frontend-design skill by Anthropic, licensed under the Apache License 2.0 (see LICENSE.txt).",
    "Modified: sections on learning from a reference and refining an existing UI were added; frontmatter and Outcome Contract are baransu's.",
    "Modified (2026-10-15): the subject inventory, idea sentence and competitor test, the argument before the plan, the rule for filling the space ornament leaves, and the screenshot checks are adapted in our own words from tasteskill v2 by Leonxlnx (https://github.com/Leonxlnx/taste-skill, MIT License); no script or data from it is included.",
    "Modified (2026-10-15): the main story sentence and the 6 : 3 : 1 hierarchy follow /draw's references/motion/composition.md, which credits its source in /draw's NOTICE.md.",
]
MAIN_STORY = "**Name the main story first.**"
RANK_631 = "**Rank everything 6 : 3 : 1.** Do not make everything the protagonist"
IDEA_SECTION = "## The idea, the argument, and looking at the result"
IDEA_SENTENCE = "On this page, [something only this subject has] becomes [the device that carries it]."
FIRST_QUESTION = "The idea carries the answer to the visitor's first question; it never replaces it."
PHONE_NO_SIDEWAYS = "is restacked, wrapped or redrawn for the phone, never left to scroll sideways inside its block"
CODEX_SKILL = ROOT / "codex/plugins/baransu/skills/ui/SKILL.md"
CODEX_NOTICE = ROOT / "codex/plugins/baransu/skills/ui/NOTICE.txt"
COMPETITOR_TEST = "Competitor test: put the nearest real competitor into the sentence; if it still holds, the idea belongs to the category — find another."
# Seal 2026-10-15: each rule the contract pins, as the sentence that carries it.
IDEA_RULES = [
    "instead of working through a similar prompt",                                      # A2
    "delete any section that has no claim",                                            # A3
    "Fill the space ornament leaves with one of four things only",                     # A4
    "Leave a screen empty on purpose at most once per page.",                          # A4
    "Fix at most the three most important failures",                                   # A5
    "stop after two rounds",                                                            # A5
    "When no browser tool in § Browser checks is available, skip this and say so in the closing message.",  # A5
    "name the stage, the middle and the focus",                                        # A19
    "On the `/draw` hand-off path (§ Pages built around /draw components), sample details come only from the facts in `docs/ui_brief.md`.",  # A8/A9
]
DONE_WHEN_PLAN = "The design plan (main story, idea, palette, type roles, layout concept with its 6 : 3 : 1 ranking, principles) was shown"
OLD_VERSION_CONSTANT = "old version: git show 2574bc6:plugins/baransu/skills/ui/SKILL.md"
MAX_SKILL_LINES = 175
CHECKS_LINE = "Checks: one-second focus · squint · cover the name · left edges · neighbouring sections · fullness · phone"
TRIGGERS = ["'/ui'", "'設計 UI'", "'美化'", "'調 UI'", "'介面設計'", "'照這個網站的風格'", "'styling'", "'beautifying any web UI'", "'frontend design'"]
NOT_FOR = ["Claude Design 畫布 mockup", "/draw", "design.md"]
EXTRACT_RED_LINE = "只抽性質，不抽素材、文案、logo"
NOTE_SENTENCE = "Write the result as a short prose note at `.claude/design/reference-<slug>.md`, first line naming the source"
LEARNING_SECTION = "## Learning a design language from a reference"
CLOSING_PROHIBITION = "Say only what you actually did: if you could not take a screenshot, do not write that you checked it visually; do not report scores, percentages or ratings of any kind"
REFINE_NO_NEW_FACTS = "Rewording changes how existing content is said, never what it says: add no fact the page does not already hold"
ARCHIVE_DIRS_LINE = 'ARCHIVE_DIRS="tmp think hunt-report evolve review write seal"'
SHIP_KEEP_LIST = [
    "(except read/learn/draw/design products)",
    "the `read`, `learn`, `draw`, and `design` dirs are kept products",
    "「已歸檔：{N} 個項目 → .claude/archived/（read/learn/draw/design 產物保留；含 sealed 合約 {S} 份）」",
    "歸檔：{N} 個項目（或「無可歸檔檔案」；read/learn/draw/design 產物保留）",
]
REMOVED_REFERENCES = [
    ("plugins/baransu/skills/write/references/proofread.md", r"tokens\.css"),
    ("plugins/baransu/skills/write/SKILL.md", r"tokens\.css"),
    ("plugins/baransu/skills/write/SKILL.md", r"project's book/Kami design tokens"),
    ("CLAUDE.md", r"design-cores|DESIGN\.md"),
    ("plugins/baransu/rules/anti-patterns.md", r"DESIGN\.md"),
    ("plugins/baransu/skills/codex-skill-transfer/SKILL.md", r"design/scripts/check\.py"),
]


def section(text: str, heading: str) -> str:
    start = text.index(heading)
    nxt = re.search(r"^## ", text[start + len(heading):], re.M)
    end = start + len(heading) + nxt.start() if nxt else len(text)
    return text[start:end].strip()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class TestDesignSkillStructure(unittest.TestCase):
    def setUp(self):
        self.skill = SKILL.read_text(encoding="utf-8")

    def test_a1_five_sections_match_vendored_hashes(self):
        for heading, digest in SECTION_SHA256.items():
            self.assertEqual(sha256(section(self.skill, heading).encode("utf-8")), digest, f"section drifted: {heading}")

    @unittest.skipUnless((SRC_DIR / "SKILL.md").exists(), "frontend-design source not installed on this machine")
    def test_a1_five_sections_verbatim_against_source(self):
        src = (SRC_DIR / "SKILL.md").read_text(encoding="utf-8")
        for heading in SECTION_SHA256:
            self.assertEqual(section(src, heading), section(self.skill, heading), f"section drifted from source: {heading}")

    def test_a1_license_bytes_pinned(self):
        self.assertEqual(sha256((SKILL_DIR / "LICENSE.txt").read_bytes()), LICENSE_SHA256)

    def test_a1_notice_verbatim(self):
        self.assertEqual((SKILL_DIR / "NOTICE.txt").read_text(encoding="utf-8").splitlines(), NOTICE_LINES)

    def test_a1_no_attribution_in_skill_md(self):
        self.assertIsNone(re.search(r"frontend-design|Apache", self.skill))
        self.assertNotIn("\nlicense:", self.skill)

    def test_a5_description_constants(self):
        desc = re.search(r'^description: "(.*)"$', self.skill, re.M).group(1)
        self.assertLessEqual(len(desc), 1024)
        for t in TRIGGERS + NOT_FOR:
            self.assertIn(t, desc, t)
        self.assertIn("loop=not-drivable", self.skill)
        self.assertFalse((SKILL_DIR / "references/loop-pauses.md").exists())

    def test_a2_a3_a4_fixed_sentences_verbatim(self):
        for constant in (EXTRACT_RED_LINE, CLOSING_PROHIBITION, REFINE_NO_NEW_FACTS):
            self.assertIn(constant, self.skill, constant)
        self.assertIn(NOTE_SENTENCE, section(self.skill, LEARNING_SECTION))

    def test_idea_section_constants_and_placement(self):
        idea = section(self.skill, IDEA_SECTION)
        for constant in (IDEA_SENTENCE, CHECKS_LINE, 'verify-page.mjs" <file>.html --out <dir>'):
            self.assertIn(constant, idea, constant)
        # Placed after the vendored Restraint section and before Browser checks, never inside a vendored one.
        self.assertLess(self.skill.index("## Restraint and self-critique"), self.skill.index(IDEA_SECTION))
        self.assertLess(self.skill.index(IDEA_SECTION), self.skill.index("## Browser checks"))
        # Refine mode skips the new steps; proof is never invented.
        self.assertIn("When refining an existing UI (§ Refining an existing UI), skip the inventory, the idea and the argument", idea)
        self.assertIn("Proof is never invented: no customers, testimonials, reviews, press, logos or business figures", idea)
        self.assertIsNone(re.search(r"\b(score|percent|rating)", idea, re.I))
        # A/B phase 1 loss: the idea took the first screen and pushed the prices below the fold.
        self.assertIn(FIRST_QUESTION, idea)
        self.assertIn(PHONE_NO_SIDEWAYS, idea)
        # The main story comes first and every visual choice serves it; 6 : 3 : 1 after the argument; squint checks it.
        self.assertLess(idea.index(MAIN_STORY), idea.index("**The idea comes before the palette.**"))
        self.assertIn("earns its place only by serving this story; one that does not is cut", idea)
        self.assertLess(idea.index("**The argument comes before the layout.**"), idea.index(RANK_631))
        self.assertIn("- Squint: at thumbnail size every screen reads 6 : 3 : 1", idea)
        self.assertIn("references/motion/composition.md", idea)
        self.assertTrue((SKILLS / "draw/references/motion/composition.md").is_file())

    def test_idea_section_pins_every_contract_rule(self):
        idea = section(self.skill, IDEA_SECTION)
        for rule in [COMPETITOR_TEST] + IDEA_RULES:
            self.assertIn(rule, idea, rule)
        self.assertIn(DONE_WHEN_PLAN, self.skill)
        self.assertLessEqual(len(self.skill.splitlines()), MAX_SKILL_LINES)

    def test_no_self_assessment_numbers(self):
        """A6: the 6 : 3 : 1 paragraph may name its shares; nothing else in the new section or the
        closing may carry a percentage or an n/m count (a self-score in disguise)."""
        idea = section(self.skill, IDEA_SECTION)
        rank = next(p for p in idea.split("\n\n") if p.startswith(RANK_631))
        for name, text in (("idea section", idea.replace(rank, "")), ("closing", section(self.skill, "## Closing the work"))):
            self.assertIsNone(re.search(r"\d\s*%|\b\d+\s*/\s*\d+\b", text), name)

    def test_codex_notice_matches(self):
        self.assertEqual(CODEX_NOTICE.read_text(encoding="utf-8").splitlines(), NOTICE_LINES)

    def test_ab_results_name_the_old_version(self):
        self.assertIn(OLD_VERSION_CONSTANT, (ROOT / "tests/ab/ui/results-phase1.md").read_text(encoding="utf-8"))

    def test_codex_copy_body_matches_claude_with_known_substitutions(self):
        """The Codex SKILL.md body is the Claude body with only `/draw` → `$baransu:draw` and
        `.claude/` → `.codex/`. verify-codex-parity.py checks file pairing only, so without this
        a Codex copy left on an old body passes every other gate (seal 2026-10-15, probe 1)."""
        def body(text: str) -> str:
            return text.split("\n---\n", 1)[1]
        expected = body(self.skill)
        for old, new in (("`/draw`", "`$baransu:draw`"), ("/draw components", "$baransu:draw components"), (".claude/", ".codex/")):
            expected = expected.replace(old, new)
        self.assertEqual(body(CODEX_SKILL.read_text(encoding="utf-8")), expected)

    def test_a6_directory_manifest(self):
        files = sorted(p.relative_to(SKILL_DIR).as_posix() for p in SKILL_DIR.rglob("*") if p.is_file() and "__pycache__" not in p.parts)
        self.assertEqual(files, ["LICENSE.txt", "NOTICE.txt", "SKILL.md", "evals/evals.json"])
        self.assertLessEqual(self.skill.count("\n"), 250)
        for p in SKILL_DIR.rglob("*"):
            if p.is_file() and p.name != "LICENSE.txt":
                self.assertIsNone(re.search(r"tokens\.css|DESIGN\.md|preset|design-cores|slide-cores|check\.py|export-brief", p.read_text(encoding="utf-8")), p.name)


class TestDesignRemovalConsumers(unittest.TestCase):
    def setUp(self):
        self.ship = SHIP.read_text(encoding="utf-8")

    def test_a8_ship_archive_dirs_literal_exactly_once(self):
        self.assertEqual(self.ship.count(ARCHIVE_DIRS_LINE), 1)

    def test_a8_ship_allowlist_matches_archive_dirs_in_order(self):
        allowlist = re.search(r"\*\*Archive allowlist\*\* — exactly the Step 1 `ARCHIVE_DIRS` value, in the same order: (.*?)\. ", self.ship)
        self.assertIsNotNone(allowlist)
        self.assertEqual(re.findall(r"`([^`]+)`", allowlist.group(1)), ARCHIVE_DIRS_LINE.split('"')[1].split())

    def test_a8_ship_keep_list_names_design_everywhere(self):
        for phrase in SHIP_KEEP_LIST:
            self.assertIn(phrase, self.ship, phrase)

    def test_a7_a8_removed_references_stay_gone(self):
        for rel, pattern in REMOVED_REFERENCES:
            self.assertIsNone(re.search(pattern, (ROOT / rel).read_text(encoding="utf-8")), rel)

    def test_a10_changelog_names_frontend_design_disable(self):
        entry = re.search(r"^## \[6\.0\.0\].*?(?=^## \[)", (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"), re.M | re.S)
        self.assertIsNotNone(entry)
        self.assertIn("停用 frontend-design plugin", entry.group(0))
        self.assertIn("`skills/hunt/` 三處改指 `/ui`", entry.group(0))


if __name__ == "__main__":
    unittest.main()
