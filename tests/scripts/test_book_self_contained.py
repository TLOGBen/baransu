#!/usr/bin/env python3
"""Tests for the /book self-contained output gate (CONTRACT-book-self-contained).

A4 — validate-output.ts must run a core `self-contained` check in every mode:
  - any `<link rel="stylesheet">` in the document  → FAIL + exit 1
  - any `@import` inside a `<style>` block         → FAIL + exit 1
  - otherwise                                      → prints `OK  self-contained`

A5 pins the three surfaces verbatim (see the contract's Verbatim Constants):
  OK  self-contained
  FAIL self-contained: external stylesheet <link href="{href}"> found — /book output must inline all CSS
  FAIL self-contained: @import inside <style> — /book output must inline all CSS

The positive run copies the blessed fixture swiss-positive.html into a temp
project root carrying a swiss-preset tokens.css, so the ambient repo-root
kami tokens.css cannot trip GATE-F (that pre-existing mismatch is unrelated
to this feature) and exit 0 is assertable.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

THIS_FILE = Path(__file__).resolve()
WORKTREE_ROOT = THIS_FILE.parents[2]
BOOK_SCRIPTS = WORKTREE_ROOT / "plugins" / "baransu" / "skills" / "book" / "scripts"
VALIDATE_OUTPUT_TS = BOOK_SCRIPTS / "validate-output.ts"
SWISS_POSITIVE = BOOK_SCRIPTS / "validate-fixtures" / "swiss-positive.html"
CHEERIO_PRESENT = (BOOK_SCRIPTS / "node_modules" / "cheerio").exists()

OK_LINE = "OK  self-contained"
FAIL_LINK_TMPL = (
    'FAIL self-contained: external stylesheet <link href="{href}"> found'
    " — /book output must inline all CSS"
)
FAIL_IMPORT = (
    "FAIL self-contained: @import inside <style>"
    " — /book output must inline all CSS"
)

# Minimal long-form-ish document that passes html-parse/structure/svg-balance
# so the self-contained verdict is what decides the run's stdout lines we pin.
BASE_BODY = """
<main>
  <article class="paper">
    <h1>t</h1>
    <svg viewBox="0 0 400 300">
      <rect width="100%" height="100%" fill="#f5f4ed"/>
    </svg>
  </article>
</main>
"""


def run_validator(html_path: Path, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["npx", "tsx", str(VALIDATE_OUTPUT_TS), str(html_path)],
        capture_output=True,
        text=True,
        cwd=str(cwd),
        timeout=120,
    )


@unittest.skipUnless(
    CHEERIO_PRESENT,
    "book scripts node_modules/cheerio absent (gitignored; fresh clone/worktree)"
    " — run `npm install` in plugins/baransu/skills/book/scripts/ first",
)
class TestSelfContained(unittest.TestCase):
    def _write_and_run(self, tmp: Path, head_extra: str) -> subprocess.CompletedProcess:
        html = tmp / "doc.html"
        html.write_text(
            "<!doctype html><html><head><title>t</title>"
            + head_extra
            + "</head><body>"
            + BASE_BODY
            + "</body></html>",
            encoding="utf-8",
        )
        return run_validator(html, tmp)

    def test_self_contained_link_fail(self):
        """負向：外部 stylesheet <link> → exit 1 + 逐字 FAIL 行。"""
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            r = self._write_and_run(
                tmp, '<link rel="stylesheet" href="../tokens.css">'
            )
            self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
            self.assertIn(FAIL_LINK_TMPL.format(href="../tokens.css"), r.stdout)
            self.assertNotIn(OK_LINE, r.stdout)

    def test_self_contained_import_fail(self):
        """負向：<style> 內 @import → exit 1 + 逐字 FAIL 行。"""
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            r = self._write_and_run(
                tmp, "<style>@import url('tokens.css');</style>"
            )
            self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
            self.assertIn(FAIL_IMPORT, r.stdout)
            self.assertNotIn(OK_LINE, r.stdout)

    def test_self_contained_positive(self):
        """正向：swiss-positive.html 於 swiss tokens.css 專案根 → exit 0 + OK 行。"""
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            (tmp / "tokens.css").write_text(
                "/* preset: swiss */\n:root { --paper: #ffffff; }\n",
                encoding="utf-8",
            )
            fixture = tmp / "swiss-positive.html"
            shutil.copyfile(SWISS_POSITIVE, fixture)
            r = run_validator(fixture, tmp)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn(OK_LINE, r.stdout)

    def test_inline_style_without_import_not_flagged(self):
        """回歸釘：一般內嵌 <style>（無 @import）不得誤殺。"""
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            r = self._write_and_run(
                tmp, "<style>:root { --paper: #f5f4ed; } body { color: var(--ink); }</style>"
            )
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn(OK_LINE, r.stdout)


class TestSelfContainedProse(unittest.TestCase):
    """Pin the A1/A2/A3 documentation surfaces (no cheerio needed)."""

    SKILL = WORKTREE_ROOT / "plugins" / "baransu" / "skills" / "book" / "SKILL.md"
    PIPELINES = (
        WORKTREE_ROOT
        / "plugins" / "baransu" / "skills" / "book"
        / "references" / "render-pipelines.md"
    )

    def test_a1_no_linked_tokens_wording(self):
        text = self.SKILL.read_text(encoding="utf-8")
        self.assertNotIn("linked tokens.css", text)
        self.assertIn("inline <style> embedding the FULL content", text)

    def test_a2_self_contained_constraint_present(self):
        text = self.SKILL.read_text(encoding="utf-8")
        self.assertIn("**Single-file self-contained output**", text)
        self.assertIn('MUST NOT contain `<link rel="stylesheet">`', text)
        self.assertIn("MUST NOT contain `@import`", text)
        self.assertIn("never a runtime dependency", text)

    def test_a3_slide_pipeline_strips_link_and_validates_four(self):
        text = self.PIPELINES.read_text(encoding="utf-8")
        self.assertIn("STRIP every `<link rel=\"stylesheet\"", text)
        self.assertIn("validate four things", text)
        self.assertIn(
            'It does not contain `<link rel="stylesheet">`', text,
            "Step 2 item 4 must pin the no-external-stylesheet check",
        )


if __name__ == "__main__":
    unittest.main()
