# Render DESIGN.html — shared spec for gen mode & preset mode

Both gen mode and preset mode, after running DESIGN.md, produce `{project_root}/DESIGN.html` — **self-demonstrating with that preset's own tokens** (no reference to Kami or external templates).

## Required 7 sections

1. **Sticky sidebar TOC** — nine-section links, colored with that preset's primary/background tokens
2. **Color palette section** — one `<div>` swatch + hex label per named color; swatch background is the actual color value
3. **Typography section** — live text samples using the spec font stacks (headings / body / captions); use `@font-face` or a safe web-font fallback, **not** a CDN link
4. **Component stylings section** — visual description or code snippet, preserving DESIGN.md terminology
5. **Do / Don't section** — two-column comparison table, using green/red accents for pass/fail
6. **AI Prompt Guide section** — copy-ready `<code>` block containing the complete reproducer prompt
7. **Remaining sections** — presented as standard `<h2>` + prose

## Technical requirements

- Fully offline (no external script, no CDN font)
- Single file, no external asset
- Valid HTML5 including `<meta charset="utf-8">` and `<meta name="viewport">`
- The page's own background / text / accent colors must correspond to the tokens in DESIGN.md §2

## Verifiable quality gates (self-check after render)

A complete seven-section structure is only a structural check; after rendering, verify the following measurable gates one by one — re-do the layout if any fails, and **do not paper over it with empty words**:

- Color count ≤3–4 (1 primary + 1 secondary + 1 accent + grayscale; accent covers ≤5% of the surface) (rationale: color-count explosion is the most common giveaway of AI aesthetics; an accent color filling the screen is no longer an accent)
- Body vs background contrast ≥4.5:1 (WCAG AA), large text (≥24px or bold ≥19px) ≥3:1 (rationale: below this value it is unreadable under projection / bright light — the hard floor of world-class output)
- Whitespace ≥40% of total area (rationale: the breathing rhythm of Kami's "less but better"; lacking whitespace looks cheap and dense)
- body line-height 1.5–1.55 for Chinese; forbid ≥1.6 (rationale: Kami's "print is tighter than web"; ≥1.6 is a floating web tone that breaks the continuous-reading rhythm of long text)
- reading-flow `max-width` ≤65ch (rationale: beyond 65 characters/line causes return-sweep fatigue — an iron rule of editorial typesetting)

### Editorial-tier micro-typography (the blind spot of gen-mode self-made presets — DESIGN.html editorial-tier self-check list)

Color count / contrast / whitespace may all pass yet still output an "AI-generic" editorial: the dividing line is the micro-typography below. These four items align with Kami editorial-tier typesetting (digests/10-kami.md §5), and are the single largest lever for pulling output from "AI-generic" up to "editorial-tier restraint".

> 🔴 **Honest disclosure**: at this layer `editorial-sanity.sh` (which only covers the kami/swiss/google prefixes of design-cores HTML) **does not yet cover** DESIGN.html — there is no script to run, so execute each item manually one by one. After rendering DESIGN.html, run E1–E4 **in order**, and **re-do the layout if any fails** — no papering over with empty words. Each item's pass criterion is written explicitly in the "Expected" field — if you cannot measure it, treat it as a fail.

- **E1 — list items use the native `<li>` marker tinted with the accent color; forbid `::before` en-dash fake bullets** (root cause: `::before` em-dash bullets are an instantly recognizable AI default output, not editorial typesetting).
  - How: `li::marker { color: var(--accent) }`, do not build bullets with `::before`.
  - Self-check: `grep -nE "li::before|content:\s*['\"][-–—]" DESIGN.html`
  - Expected pass: **empty output (0 lines)**.
- **E2 — no round-dot bullet beside CJK list items; replace with an 8px×1.5px `var(--accent)` short bar** (root cause: round dots beside Chinese read as childish; the short bar is editorial-tier restraint).
  - How: for `<li>` segments containing CJK, use `list-style: none` + `::before` to draw a `width:8px;height:1.5px;background:var(--accent)` short bar.
  - Self-check: `grep -nE "list-style(-type)?:\s*disc" DESIGN.html` (CJK segments must not have disc) + visually confirm the bar size = 8px×1.5px.
  - Expected pass: **grep disc output is empty (0 lines); bar size visually conforms**.
- **E3 — arrows are always `→`, forbid `->`; Chinese quotes use 「」, forbid straight quotes `"`; no space before %, add thousands separators to numbers (`5,000` / `90%`)** (root cause: ASCII arrows and straight quotes are the fingerprint of unedited machine output; same spirit as `editorial-sanity.sh` Check 3, but here covering DESIGN.html rather than a design-core).
  - How: change ASCII arrows in prose to `→`, straight quotes to 「」.
  - Self-check: `grep -nE -- "->" DESIGN.html` (ASCII arrows) + visually confirm no straight quotes `"` in prose (not HTML attributes).
  - Expected pass: **grep `->` output is empty (0 lines); straight-quote count in prose = 0**.
- **E4 — print- / long-form-oriented presets forbid italic** (sole exception: screen-only poetic lines; root cause: a print template using italic reveals a web tone; gen-mode self-made non-swiss presets currently have no such gate).
  - How: express emphasis with `var(--accent)` coloring or font weight, not italic.
  - Self-check: `grep -nE "font-style:\s*italic|<i>|<em>" DESIGN.html`
  - Expected pass: **empty output (0 lines); if there are hits, confirm each is genuinely a screen-only poetic-line exception, otherwise revert to expressing hierarchy via coloring / font weight**.

## Write location

`{project_root}/DESIGN.html`. Overwrite if it already exists.

## Success message

「✅ 已產出 DESIGN.html（設計系統視覺預覽，可直接用瀏覽器開啟）」
