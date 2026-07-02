# Stage 4 — Validate & Report (detailed spec)

## §2 Visual render verification (Playwright)

After Stage 4 §1 GATE PASS, render the HTML in headless Chromium via the bundled helper (Playwright is guaranteed installed by Stage 0). A single invocation produces both the preview screenshot and a structural JSON probe:

```bash
PROBE=$(python3 "$CLAUDE_SKILL_DIR/scripts/verify-render.py" \
  ".claude/book/{$SLUG}.html" \
  ".claude/book/{$SLUG}-preview.png")
echo "$PROBE"
```

`$PROBE` is single-line JSON:

```json
{"overflow": false, "has_paper": true, "has_h1": true, "has_h2": true, "svg_count": 3, "title": "…"}
```

Interpretation:

- `overflow` is `true` → 「⚠ 跑版偵測：有橫向溢出，請開啟 .claude/book/{$SLUG}-preview.png 手動確認。」
- any of `has_paper` / `has_h1` / `has_h2` is `false` → 「⚠ 結構元素缺失：{element} 未出現在頁面中。」
- script non-zero exit (Playwright launch / navigation failure) → 「⚠ 視覺驗證無法執行，請手動開啟 .claude/book/{$SLUG}.html。」 and continue to the completion report
- all pass → 「✅ 視覺驗證通過」

> **Why Playwright (not browser-use)**: browser-use's headless Chromium silently fails to load `file://` URLs (readyState reports complete but the DOM is empty). Playwright handles `file://` correctly and is the project-standard E2E driver.

## §3 Completion report template

Final output (繁中):

```
✅ 已儲存：
  HTML：.claude/book/{$SLUG}.html
  PDF： .claude/book/{$SLUG}.pdf        （若 $FORMAT 包含 pdf，且生成成功）
  PPT： .claude/book/{$SLUG}.pptx       （若 $FORMAT 包含 ppt，且生成成功）
        PPT：失敗（詳見上方錯誤）         （若 html2pptx.js 回傳非零 exit code）
  預覽：.claude/book/{$SLUG}-preview.png
內容類型：{$CONTENT_TYPE}
SVG 圖解：{N} 張
字數：約 {word_count} 詞
```

Rules:

- The HTML line is **always present** (every format produces HTML)
- PDF line: appears only with `--format pdf` or `--format all`
- PPT line: appears only with `--format ppt` or `--format all`; on html2pptx failure, show 「PPT：失敗（詳見上方錯誤）」 instead
- Preview screenshot (PNG): always present (the Playwright screenshot runs in §2)
- Do not re-derive `$SLUG` in Stage 4; inherit the value derived in Stage 2A §4

## Validator division of labor

Verification splits into two tiers with opposite authority: a **hard floor** (mechanical, blocking) and a **soft range** (judgment, advisory). The division is deliberate — **the hard floor blocks; the soft range advises**. Soft generation (Stage 3 §3) lives *inside* the hard floor and is *judged against* the soft range; a soft-range objection never blocks a soft-generated layout, but a hard-floor violation always does.

### Hard floor — blocking mechanical gate (`scripts/validate-output.ts`)

The hard floor is the non-negotiable safety boundary: **token-only / no-rgba (in SVG) / accent ≤5% / PDF-safe**. It is enforced mechanically by `scripts/validate-output.ts`; **any violation = GATE FAIL (blocking)** — Stage 4 §1 does not enter the completion report until exit 0 (the three-stage fallback runs first). This tier is pure mechanism, no judgment.

Mapping each hard-floor item to the existing gate that enforces it (confirmed against the current `validate-output.ts`):

| Hard-floor item | Enforcing gate in `validate-output.ts` | Coverage |
|-----------------|----------------------------------------|----------|
| token-only (class prefix routed through canonical preset) | GATE-F class-prefix (F-a prefix-in-whitelist / F-b single-prefix / F-c tokens.css tie-break) | covered for class tokens; bare-hex *color values* are **not** scanned by any gate — see follow-up note |
| no-rgba (SVG fill / stroke) | — | **not covered** by an existing gate — see follow-up note |
| accent ≤5% (single chromatic accent, painted area) | — | **not covered** by an existing gate (area share is unmeasured) — see follow-up note |
| PDF-safe (no WeasyPrint ghost-border / unsafe layout) | GATE-K chevron-strict (forbids `<polygon>` markers that ghost-border in PDF) + html2pptx pre-checks rule2_gradient / rule3_bg_on_text / rule4_div_bg_image (all `hard_fail`, PPT mode) | partially covered: chevron / gradient / bg-image ghosting is gated; the `rgba()` alpha-composite ghost-border is not (it overlaps the no-rgba gap above) |

**Follow-up note (not added this batch — do not introduce a large new validator check now):** three hard-floor items lack a dedicated mechanical gate today — (a) **bare-hex color values** anywhere in output (GATE-F only checks class-name prefixes, not `#rrggbb` literals), (b) **`rgba()` in SVG fill / stroke**, and (c) **accent-painted area ≤5%**. Until a gate is added, (a) and (b) are caught only by the render-time pre-write checklist (Stage 3 §3) and the soft-range bare-hex heuristic below; (c) lives entirely in the render-time self-check + style-reviewer. Track these as a follow-up to extend `validate-output.ts` (a no-rgba SVG scan and a bare-hex literal scan are the cheapest two to add).

### Soft range — non-blocking opinion (style-reviewer + heuristics)

The soft range judges whether a hard-floor-passing output is *stylistically within the preset's §9 expression range*. It is **NON-blocking opinion**: produced by `style-reviewer` plus a few mechanical heuristics, recorded in the review, and **never blocks output**. The heuristics are: **bare hex** (a `#rrggbb` literal that slipped past the canonical-token convention), a **second accent** (a second chromatic accent beyond the single `var(--accent)`), and **column width** exceeding the §9 欄寬上限 ceiling. A soft-range finding ("not quite within §9 style") is advice in the report, not a gate — keeping judgment-type checks out of the blocking path (per the ctx error_handling split: 軟範圍是意見非阻斷).

### Gate-internal trust boundary

- `scripts/validate-output.ts`: responsible for the output layer's (output HTML) set membership and prefix consistency, including GATE A-E (existing SVG rules) / GATE-F (class prefix `kami-*` / `swiss-*` not mixed + tokens.css preset tie-break) / GATE-G (`data-layout` must correspond to a real file under `{project_root}/slide-cores/`) / GATE-J node-width whitelist / GATE-K chevron-strict / GATE-L viewBox containment (rect/line/circle/ellipse/text all fall within the viewBox, 0.5px tolerance; skips defs/marker/pattern/clipPath/mask/symbol and transformed groups). **Trusts** that the `/design` side's `check.py` has already linted the slide-core artifact's internal structure; this validation does not redo per-file lint.
- The corresponding `/design`-side rules are in `plugins/baransu/skills/design/scripts/check.py`'s artifact-internal lint rules.

## REQ-003 Scenario 2 automated evidence

- Fixture: `scripts/validate-fixtures/swiss-positive.html` — a hand-written swiss-style slide HTML that mirrors the shape `/book` Stage 3 emits under `--format ppt --style swiss` (body 960pt×540pt, `data-layout="content-bullets"` / `quote`, all classes `swiss-*`, no hard-fail violations).
- Smoke runner: `scripts/swiss-smoke-test.sh` — Stage 1 runs `validate-output.ts` against the fixture (expected all green; GATE-C/GATE-G SKIP because of the viewBox height and the project root having no `slide-cores/`); Stage 2, when `pptxgenjs` + `playwright` are installed, runs `html2pptx.js`, and uses `python3 zipfile` to confirm the `.pptx` is a valid zip containing `ppt/presentation.xml` + `[Content_Types].xml`. When dependencies are not installed, Stage 2 SKIPs (`--strict` turns it into FAIL).
- Purpose: serves as the minimal automated-evidence starting point for REQ-003 S2 「文件可在 PowerPoint 打開」. For a full PowerPoint round-trip, run `npx tsx scripts/install-deps.ts --format ppt` first.
