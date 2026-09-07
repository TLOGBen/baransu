#!/usr/bin/env python3
"""Structural assertions for /design canonical-count documentation alignment.

TASK-design-skill-02 (REQ-001 / REQ-005) — the canonical-count documentation is
realigned from the bare "38" absolute to the version-gated reality:
"38 base (+5 capability = 43; schema-gated)". The single source of truth stays
check.py's two constants BASE_TOKENS(38) + CAPABILITY_TOKENS(5); the docs are a
derived, version-aware view.

This test reads the design SKILL.md and canonical-tokens.md and asserts:
  (1) canonical-tokens.md enumerates all 5 capability token names;
  (2) SKILL.md §Canonical Token Schema mentions "capability";
  (3) both files describe version-gating (a phrase like "schema: 43" or
      "+5 capability" appears) AND the lint Check B line no longer carries a
      bare un-versioned "all 38 canonical names present" absolute.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

THIS_FILE = Path(__file__).resolve()
WORKTREE_ROOT = THIS_FILE.parents[2]
DESIGN_DIR = WORKTREE_ROOT / "plugins" / "baransu" / "skills" / "design"
SKILL = DESIGN_DIR / "SKILL.md"
CANONICAL = DESIGN_DIR / "references" / "canonical-tokens.md"

CAPABILITY_TOKENS = ["--ease", "--duration", "--stagger-step", "--font-display", "--shadow-drama"]


def canonical_schema_region(text: str) -> str:
    """Isolate the SKILL.md '# Canonical Token Schema' region up to the next '# ' heading."""
    marker = "# Canonical Token Schema"
    start = text.find(marker)
    assert start != -1, "SKILL.md '# Canonical Token Schema' header not found"
    body = text[start + len(marker):]
    nxt = body.find("\n# ")
    return body if nxt == -1 else body[:nxt]


class TestCanonicalTokensCapability(unittest.TestCase):
    def setUp(self) -> None:
        self.canonical = CANONICAL.read_text(encoding="utf-8")

    def test_canonical_tokens_enumerates_all_capability_names(self):
        """canonical-tokens.md lists all 5 capability token names."""
        for name in CAPABILITY_TOKENS:
            self.assertIn(
                name,
                self.canonical,
                f"canonical-tokens.md must enumerate capability token {name}",
            )

    def test_canonical_tokens_has_capability_category(self):
        """canonical-tokens.md declares a 'Capability (5)' category."""
        self.assertRegExp = self.assertRegex
        self.assertRegex(
            self.canonical,
            r"Capability \(5\)",
            "canonical-tokens.md must declare a 'Capability (5)' category",
        )

    def test_canonical_tokens_version_aware(self):
        """canonical-tokens.md describes version-gating (schema: 43 / +5 capability)."""
        self.assertTrue(
            ("schema: 43" in self.canonical) or ("+5 capability" in self.canonical),
            "canonical-tokens.md must carry a version-aware phrase (schema: 43 / +5 capability)",
        )


class TestSkillCanonicalSchema(unittest.TestCase):
    def setUp(self) -> None:
        self.text = SKILL.read_text(encoding="utf-8")
        self.region = canonical_schema_region(self.text)

    def test_schema_region_mentions_capability(self):
        """§Canonical Token Schema mentions 'capability'."""
        self.assertIn(
            "capability",
            self.region.lower(),
            "§Canonical Token Schema must mention 'capability'",
        )

    def test_skill_version_aware(self):
        """SKILL.md describes version-gating (schema: 43 / +5 capability)."""
        self.assertTrue(
            ("schema: 43" in self.text) or ("+5 capability" in self.text),
            "SKILL.md must carry a version-aware phrase (schema: 43 / +5 capability)",
        )

    def test_check_b_no_bare_38_absolute(self):
        """Lint Check B line no longer carries a bare un-versioned '38 canonical names present'."""
        self.assertNotRegex(
            self.text,
            r"all 38 canonical names present",
            "Lint Check B must be version-gated, not a bare 'all 38 canonical names present'",
        )

    def test_check_b_is_version_gated(self):
        """The Check B description explains version-gating (mentions schema/43/capability)."""
        # Locate the Check B table row.
        m = re.search(r"\*\*B\..*?\n", self.text)
        self.assertIsNotNone(m, "Lint Check B row not found in SKILL.md")
        row = m.group(0).lower()
        self.assertTrue(
            ("schema" in row) or ("43" in row) or ("capability" in row),
            "Lint Check B row must mention version-gating (schema / 43 / capability)",
        )


if __name__ == "__main__":
    unittest.main()
