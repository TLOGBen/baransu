#!/usr/bin/env python3
"""Tests for §9 表現範圍規格 (Expression Range) in the three preset DESIGN.md files.

TASK-assets-02 — §9 is upgraded from a single AI-prompt blockquote into an
"Expression Range" spec. Each preset's §9 must carry the five labeled fields,
keep the reproducible prompt blockquote as a compat tail, and (for kami)
explicitly frame 極簡 as a CHOSEN extreme rather than a default safe value.
"""

from __future__ import annotations

import unittest
from pathlib import Path

THIS_FILE = Path(__file__).resolve()
WORKTREE_ROOT = THIS_FILE.parents[2]
REFS = WORKTREE_ROOT / "plugins" / "baransu" / "skills" / "design" / "references"

PRESETS = {
    "kami": REFS / "紙-preset" / "DESIGN.md",
    "swiss": REFS / "swiss-preset" / "DESIGN.md",
    "google": REFS / "google-design-preset" / "DESIGN.md",
}

FIELD_LABELS = [
    "承諾的極端",
    "空間原則",
    "不對稱/重疊允許度",
    "欄寬上限",
    "強調色紀律",
]


def section9(text: str) -> str:
    """Isolate the §9 section (from '## 9.' up to the next '## ' or EOF)."""
    marker = "\n## 9."
    start = text.find(marker)
    assert start != -1, "§9 section header '## 9.' not found"
    body = text[start + 1 :]
    nxt = body.find("\n## ", 1)
    return body if nxt == -1 else body[:nxt]


class TestExpressionRangeFields(unittest.TestCase):
    def test_all_five_field_labels_present_in_section9(self):
        for name, path in PRESETS.items():
            sec = section9(path.read_text(encoding="utf-8"))
            for label in FIELD_LABELS:
                self.assertIn(
                    label,
                    sec,
                    f"{name} §9 missing field label '{label}'",
                )

    def test_kami_marks_minimal_as_chosen_extreme(self):
        sec = section9(PRESETS["kami"].read_text(encoding="utf-8"))
        self.assertTrue(
            ("被選中的極端" in sec) or ("平等極端" in sec),
            "kami §9 must mark 極簡 as a chosen/equal extreme "
            "(「被選中的極端」or「平等極端」)",
        )

    def test_reproducible_prompt_blockquote_preserved(self):
        for name, path in PRESETS.items():
            sec = section9(path.read_text(encoding="utf-8"))
            self.assertIn(
                "> Design a UI",
                sec,
                f"{name} §9 lost the reproducible prompt blockquote",
            )


if __name__ == "__main__":
    unittest.main()
