#!/usr/bin/env python3
"""TASK-release-01 — book/SKILL.md canonical-count mentions are version-aware.

Single source of truth: check.py's two constants BASE_TOKENS(38) +
CAPABILITY_TOKENS(5). Prose count strings are derived views, not the source.
Every canonical-count mention in book/SKILL.md must be version-aware — a bare
"canonical 38 names" (no capability / 43 / schema qualifier nearby) is a drift
risk and must be reframed to "38 base names (+5 capability for schema:43)" style.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

THIS_FILE = Path(__file__).resolve()
WORKTREE_ROOT = THIS_FILE.parents[2]
BOOK_SKILL = WORKTREE_ROOT / "plugins/baransu/skills/book/SKILL.md"

# A canonical-count mention: the literal token count 38 used to describe the
# canonical name vocabulary (e.g. "canonical 38 names", "the canonical 38 names").
CANONICAL_38_RE = re.compile(r"canonical\s+38\b|38[- ]token\b")

# Version-aware qualifier that must appear near a canonical-count mention.
QUALIFIER_RE = re.compile(r"capability|schema\s*:?\s*43|\+\s*5\b|\bbase\b", re.IGNORECASE)


class TestBookCanonicalCountVersioned(unittest.TestCase):
    def setUp(self):
        self.assertTrue(BOOK_SKILL.exists(), f"missing {BOOK_SKILL}")
        self.lines = BOOK_SKILL.read_text(encoding="utf-8").splitlines()

    def test_each_canonical_38_mention_is_version_aware(self):
        """No bare 'canonical 38' without a capability/43/schema qualifier on the line."""
        bare = []
        for i, line in enumerate(self.lines, 1):
            if CANONICAL_38_RE.search(line) and not QUALIFIER_RE.search(line):
                bare.append((i, line.strip()))
        self.assertEqual(
            bare, [],
            "book/SKILL.md has un-versioned canonical-count mention(s); "
            "reframe each to version-aware wording "
            "('38 base names (+5 capability for schema:43)'):\n"
            + "\n".join(f"  L{n}: {t}" for n, t in bare),
        )


if __name__ == "__main__":
    unittest.main()
