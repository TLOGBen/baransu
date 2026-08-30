#!/usr/bin/env python3
"""F8b-stub — the 5.3.0 thin-stub redirect surfaces are pinned here.

book/SKILL.md and design/SKILL.md stopped being pipelines in 5.3.0: their
bodies are now thin redirects to the kamishibai plugin, and the machinery
underneath (`scripts/`, `references/`) is frozen until physical retirement at
6.0.0. Three things can silently break and leave a user in a dead end:

  1. the book stub loses its redirect (a `/book` trigger lands on nothing);
  2. the design stub loses its redirect (same, for `/design`);
  3. evolve's card.html production line still points at the retired in-repo
     `/book` entry, so the result card cannot be rendered at all.

Each is pinned below by the name the contract's surface inventory gives it.
The Verbatim Constants are byte-compared, not paraphrase-matched.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

WORKTREE_ROOT = Path(__file__).resolve().parents[2]
SKILLS = WORKTREE_ROOT / "plugins" / "baransu" / "skills"

BOOK_SKILL = SKILLS / "book" / "SKILL.md"
DESIGN_SKILL = SKILLS / "design" / "SKILL.md"
EVOLVE_SKILL = SKILLS / "evolve" / "SKILL.md"
EVOLVE_OUTPUT_CONTRACT = SKILLS / "evolve" / "references" / "output-contract.md"

# --- Verbatim Constants (CONTRACT.md §Verbatim Constants) -------------------
BOOK_POINTER = (
    "本 skill 已由 kamishibai plugin 的 book skill 承接"
    "（渲染走 `kamishibai render`，@kamishibai/sdk）；本 stub 於 6.0.0 移除。"
)
DESIGN_POINTER = (
    "本 skill 已由 kamishibai plugin 的 design skill 承接"
    "（規格歸 DESIGN.md、渲染歸 SDK）；本 stub 於 6.0.0 移除。"
)
RETIREMENT_NOTICE = (
    "蟄伏機件（scripts/references）本版一位元未動，6.0.0 隨目錄實體退役"
    "——git 歷史即唯一備份（/analyze 前例）。"
)

STUB_MAX_LINES = 60

# Trigger vocabulary that must survive the slim-down — the stub is worthless if
# the trigger no longer fires.
BOOK_TRIGGERS = ("'/book'", "'轉成 book'", "'做成 HTML book'", "'存成 book'")
DESIGN_TRIGGERS = ("'/design'", "'生成設計規格'", "'設計規格'")

# Gate scripts that must not be reachable as a current step from a stub body.
BOOK_FORBIDDEN = ("validate-output.ts", "verify-render.py", "swiss-smoke-test.sh")
DESIGN_FORBIDDEN = ("check.py", "editorial-sanity.sh", "紙-sanity.sh")

STAGE_HEADER_RE = re.compile(r"^#+\s*Stage\s", re.MULTILINE)


def read(path: Path) -> str:
    assert path.is_file(), f"missing {path}"
    return path.read_text(encoding="utf-8")


class TestStubRedirect(unittest.TestCase):
    """The three surfaces the 5.3.0 stub cut cannot afford to get wrong."""

    def test_stub_book_points_to_kamishibai(self):
        text = read(BOOK_SKILL)
        self.assertIn(
            BOOK_POINTER, text,
            "book/SKILL.md 缺 Verbatim 指向句；/book 觸發後將無改裝指引（死巷）",
        )
        self.assertIn(
            RETIREMENT_NOTICE, text,
            "book/SKILL.md 缺 Verbatim 退役預告句（6.0.0 實體退役的唯一書面告知）",
        )
        body = text.split("---", 2)[-1]
        self.assertLessEqual(
            len(text.splitlines()), STUB_MAX_LINES,
            f"book/SKILL.md 已非薄 stub：{len(text.splitlines())} 行 > {STUB_MAX_LINES}",
        )
        for trigger in BOOK_TRIGGERS:
            self.assertIn(
                trigger, text,
                f"book/SKILL.md frontmatter 掉了觸發詞 {trigger}（觸發面不得縮減）",
            )
        for script in BOOK_FORBIDDEN:
            self.assertNotIn(
                script, body,
                f"book/SKILL.md 仍殘留閘門調用 {script}；stub 不得指示執行蟄伏機件",
            )
        self.assertIsNone(
            STAGE_HEADER_RE.search(body),
            "book/SKILL.md 仍有 Stage 標題；stub 不得殘留管線操作指示",
        )

    def test_stub_design_points_to_kamishibai(self):
        text = read(DESIGN_SKILL)
        self.assertIn(
            DESIGN_POINTER, text,
            "design/SKILL.md 缺 Verbatim 指向句；/design 觸發後將無改裝指引（死巷）",
        )
        self.assertIn(
            RETIREMENT_NOTICE, text,
            "design/SKILL.md 缺 Verbatim 退役預告句（6.0.0 實體退役的唯一書面告知）",
        )
        body = text.split("---", 2)[-1]
        self.assertLessEqual(
            len(text.splitlines()), STUB_MAX_LINES,
            f"design/SKILL.md 已非薄 stub：{len(text.splitlines())} 行 > {STUB_MAX_LINES}",
        )
        for trigger in DESIGN_TRIGGERS:
            self.assertIn(
                trigger, text,
                f"design/SKILL.md frontmatter 掉了觸發詞 {trigger}（觸發面不得縮減）",
            )
        for script in DESIGN_FORBIDDEN:
            self.assertNotIn(
                script, body,
                f"design/SKILL.md 仍殘留閘門調用 {script}；stub 不得指示執行蟄伏機件",
            )
        self.assertIsNone(
            STAGE_HEADER_RE.search(body),
            "design/SKILL.md 仍有 Stage 標題；stub 不得殘留四模式操作指示",
        )

    def test_evolve_entry_not_orphaned(self):
        """evolve's card.html line must name the kamishibai successor, never a
        bare in-repo `/book` entry that no longer executes."""
        for path in (EVOLVE_SKILL, EVOLVE_OUTPUT_CONTRACT):
            text = read(path)
            card_lines = [l for l in text.splitlines() if "card.html" in l]
            self.assertTrue(
                card_lines, f"{path.name}: 找不到 card.html 產線敘述（入口已消失？）"
            )
            joined = "\n".join(card_lines)
            self.assertIn(
                "/kamishibai:book", joined,
                f"{path.name}: card.html 產線未指向 kamishibai book skill —— "
                "evolve 結果卡斷鏈（stub 不產 HTML）",
            )
            self.assertNotIn(
                "the `/book` entry", joined,
                f"{path.name}: card.html 產線仍指向已 stub 化的 in-repo `/book` 入口",
            )
        # The rule the repoint must not quietly drop.
        self.assertIn(
            "never hand-assemble", read(EVOLVE_OUTPUT_CONTRACT),
            "output-contract.md 掉了 never-hand-assemble 規則（改指不得順手鬆綁紀律）",
        )


if __name__ == "__main__":
    unittest.main()
