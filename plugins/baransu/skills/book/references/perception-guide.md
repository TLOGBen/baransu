## Contents

- Content Type Taxonomy
- Visual Treatment Constants (all types)
- Quantified Type Scale (do not improvise typography)
- Output Anti-Slop Blacklist (editorial typography discipline)
- SVG Strategy by Type
- Synthesis Length Limits

# Perception Guide — Content Type Classification

This file is the authoritative reference for `book`'s content-type perception layer.
Read it during Stage 2 (Synthesize) to classify the acquired content and select the
correct visual treatment for Stage 3 (Render).

---

## Content Type Taxonomy

Classify the acquired content into exactly one of three types.
Use the signals below; when signals conflict, choose the type that matches the
**dominant structural pattern** (not the topic).

### Type A — Technical

**Signals:**
- Contains code blocks, API references, CLI commands, or config snippets
- Structured around how-to steps, system architecture, or data flow
- Audience is builders/engineers; document purpose is to explain *how* something works

**Examples:** API guides, architecture docs, tool tutorials, code walkthroughs, incident reports

**Visual treatment:**
- Monospace code sections with syntax-hinted backgrounds
- Flow diagrams (nodes-and-arrows showing data movement or decision paths)
- Comparison tables (before/after, option A vs B)
- Section badges / numbered steps
- Tight body line-height — resolve to the Quantified Type Scale's dense row (1.42 at 9.2pt; regular body reading 1.50–1.55), not a looser value — engineers scan, not read linearly

---

### Type B — Narrative

**Signals:**
- Prose-heavy; argument builds across paragraphs
- Opinion piece, essay, letter, or personal reflection
- Audience is general; document purpose is to *persuade* or *share experience*

**Examples:** Blog posts, essays, X threads, newsletters, thought leadership pieces

**Visual treatment:**
- Wide body margin with reading-comfort line-height (1.55–1.65 for CJK on screen; never ≥ 1.70) — generous *margins*, not airy leading; ≥ 1.70 reads as floating web-prose, not print
- Pull-quote callouts for key claims
- Relationship diagrams (concepts mapped as a network, not a flowchart)
- Minimal chrome — let text lead; decorative elements are subtle
- Cover image or thematic SVG illustration at the top

---

### Type C — Research / Report

**Signals:**
- Contains data, citations, scoring tables, or multi-source synthesis
- Structured around findings, evidence, and conclusions
- Document purpose is to *record*, *compare*, or *evaluate*

**Examples:** Literature reviews, comparative analyses, evaluation reports, weekly digests,
learning briefs (like /learn output)

**Visual treatment:**
- Score / rating tables with visual bars or badges
- Source attribution visible on every major claim
- Side-by-side comparison layouts
- Summary callout at top (abstract / TL;DR box)
- Multi-source provenance section at the bottom

---

## Visual Treatment Constants (all types)

These apply regardless of content type — they are the standing `book` invariants, stated **preset-neutrally in canonical token names only** (concrete values come from the current preset's `tokens.css` via `design-token-resolver.md`; a swiss / google-design / gen-slug render must never receive Kami hex or fonts through this table):

| Element | Rule |
|---------|------|
| Design tokens | Read from `{project_root}/tokens.css`（canonical 38-name tokens; written by `/baransu:design preset\|gen`, this skill only reads）— use named tokens, never raw hex |
| Background | `var(--paper)` as page canvas; `var(--surface)` for cards |
| Accent | `var(--accent)` as the sole chromatic accent; no secondary accent colour |
| Typography | `var(--font-serif)` for body (the preset defines it — a serif stack in kami, a sans alias in sans-only presets like swiss/google-design); `var(--font-sans)` / `var(--font-mono)` per the preset's stacks |
| TOC sidebar | Show at ≥ 1024px viewport; sticky; highlight active section via IntersectionObserver |
| SVG diagrams | Minimum 1 per document; stroke-based, round linecap, 1.5–2px stroke; no fills heavier than 20% opacity |
| Left rule | 1px `var(--accent)` hairline at x=52px inside the paper sheet (as in the long-form SSOT / golden-template exemplars) |
| Max body width | 760px; reading column capped at 680px |
| Paper shadow | route through the preset's shadow tokens (`var(--shadow-ring)` / `var(--shadow-whisper)`), not hand-tuned rgba values |

---

## Quantified Type Scale (do not improvise typography)

Print uses pt; screen px ≈ pt × 1.33. Hard ranges — resolve any "generous" /
"tight" treatment above to a number here, never to vibes.

| Role | Size (print pt) | Weight | Line-height |
|------|-----------------|--------|-------------|
| Display / cover title | 36pt | 500 | 1.10 |
| H1 section | 22pt | 500 | 1.20 |
| H2 | 16pt | 500 | 1.25 |
| H3 item | 13pt | 500 | 1.30 |
| Body lead / pull-quote | 11pt | 400 | 1.55 |
| Body reading text | 10pt | 400 | **1.50–1.55** |
| Body dense (technical scan) | 9.2pt | 400 | 1.42 |
| Caption | 9pt | 400 | 1.45 |
| Label / eyebrow | 9pt | 600 (sans) | 1.35 |

Floors: web ≥ 12px, PDF ≥ 9pt; CJK body on screen may relax to **1.55–1.65**.
**Line-height bans:** ≥ 1.70 (airy web-prose, breaks print feel); 1.00–1.05
(lines collide). The narrative "generous reading" treatment = 1.55–1.65, **not 1.85**.
Vertical rhythm (4pt step): xs 2–3 / sm 4–5 / md 8–10 / lg 16–20 / xl 24–32 /
2xl 40–60 / **3xl 80–120pt between long-doc sections**. Section header:
eyebrow→rule 14px, **rule→H1 ≥ 36px (gap below ≥ 2× gap above)**.

### Cover / display CJK title — length-tier the size first

CJK glyphs are square and ink-dense, so a long Chinese title overflows a fixed
Display size that an English title of the same word-count survives. Before setting
the cover/display title, count the title's CJK chars and **drop to the tier size**
— do not improvise a shrink. Tier values demote the Display role from §scale's
36pt baseline (no new token; this constrains how the Display size is applied).

| CJK title length | Display size | Notes |
|------------------|-------------|-------|
| ≤ 6 chars | 36pt (full Display) | one line, breathing room |
| 7–10 chars | 30pt | one line |
| 2 lines, each ≤ 8 | 27pt | balance the two lines |
| 2 lines, 9–12 total | 24pt (= H1) | |
| 3 lines | 21pt | last resort |

**Failure branch (3 lines still overflows):** cut the title copy first —
**never push the size below the 21pt tier**. A small + heavy cover title reads
Web-1.0, not edited; "the larger, the lighter" is the rule, so undersizing to
force-fit is the opposite of the intended voice.

---

## Output Anti-Slop Blacklist (editorial typography discipline)

Things that mark a `book` output as machine-default rather than edited. Each entry
is **anti-pattern → why it is slop (carries no editorial / brand information) → only
legitimate exception**, plus a grep-able self-check. Scan before declaring Stage 3 done.

1. **Fake `::before` en-dash / hyphen bullets** → default LLM rendering, zero brand
   colour or hierarchy → no exception. Fix: native marker + `li::marker{color:var(--accent)}`.
   Check: `grep -nE "li::before|content:\s*['\"]\s*[—–-]"`
2. **Round-dot `•` bullets next to CJK** → reads childish, breaks print register → none
   for CJK lists. Fix: 8pt × 1.5pt brand bar (`li::before{width:8pt;height:1.5pt;background:var(--accent)}`).
   Check: `grep -nE "list-style.*disc|•"`
3. **ASCII arrows / straight quotes / printed italic** → keyboard defaults, not editorial
   glyphs → italic only on a screen-only landing poetic line. Fix: arrows `→`; Chinese
   quotes 「」; print carries no italic. Check: `grep -nE "\->|font-style:\s*italic"`
4. **Filler opener** ("In today's rapidly evolving…" / 「擁抱／打造／賦能／重構」) → delays
   the first claim, signals generated prose → none. Fix: lead with the first real claim.
   Check: `grep -nE "In today'?s|rapidly evolving|擁抱|打造|賦能|重構|本質是|這意味著|值得注意的是"`
5. **Caption restating the figure/title** → echo adds no information → none. Pass test
   (all captions must clear it — one failing caption = slop): **every `<figcaption>` must
   carry at least one of** — a trade-off / judgement criterion, a next-step action, or a
   dimension the figure does not directly show (comparison · trend · distribution). Pure
   restatement of the title or of node names inside the figure = fail.
   Slop: `圖 1：系統架構` / `Figure 1: System Architecture`.
   Edited: `此架構在 >9 節點時應拆為總覽+細節兩張` (gives the trade-off the diagram implies).
   Mirrors `diagram-design`'s "chart titles state the insight, not the label". Check:
   `grep -noE "<figcaption[^>]*>[^<]*</figcaption>"` then confirm each clears the pass test
   (any caption that only repeats its `<h*>`/node text = fail).
6. **Emoji / icon as section marker** → fakes hierarchy type should carry → sparing inline
   body emoji ok, none in headers/print. Fix: hierarchy via size/weight/spacing.
   Check: `grep -nE "<h[1-3][^>]*>\s*[\x{1F300}-\x{1FAFF}\x{2600}-\x{27BF}]"`
7. **`rgba()` tag/chip background** → WeasyPrint composites alpha into a double-rectangle
   ghost-border artifact in PDF → none for fills (CSS `box-shadow` rgba is exempt). Fix:
   solid hex token (`--tag-bg`), mirrors `svg-rendering-rules.md` §1.
   Check: `grep -nE "(background|fill)[^;]*rgba\("`
8. **Accent over-paint / cold-gray neutrals** → multiple chromatic accents or accent on
   > 5% of the body area reads as decoration, not restraint → the page falls back to the
   AI visual mean (carries no brand restraint); cold gray (`R≤G≤B` or pure neutral `R=G=B`)
   is the most recognisable fingerprint of the default LLM palette. Two binding rules, both
   on the *rendered* HTML body (not new tokens — these constrain how existing tokens are used):
   - **One chromatic accent only.** Every coloured element (links, `sec-num`, emphasis words,
     `1px` left rule) uses `var(--accent)`; total accent-painted area ≤ 5% of body. Emphasis
     is **colour OR weight, never both** (combining the two breaks Kami's single-weight voice).
   - **Warm-gray neutrals only.** Every neutral gray must be warm (`R≥G>B`); cold gray
     (`R≤G≤B`) and pure neutral (`R=G=B`) are banned.
   - Only legitimate exception: pre-existing warm warning tokens (e.g. changelog breaking
     badge `--breaking-bg`/`--breaking-fg`, both warm `R>G>B`). No exception for body accents.
   - **Declared-statistical-chart container exception** — additional to (does not replace or
     loosen) the warm-warning-token exception above, gated on the SAME check, not a second,
     separate declaration check: inside a section whose `statistical` chart type (§4.9/§4.10)
     resolved to the **Declared** branch — i.e. `{project_root}/tokens.css` line 1's
     `; chart-capability: <N>` header check that SKILL.md Stage 3 §4 (「Statistical-type color-capability degrade」) already performs, via `check.py`'s
     `_parse_chart_capability_header` contract — the chart's computed multi-color palette
     (SKILL.md's Declared branch: `references/color-reasoning.md` guidance +
     `color_distance.py`-validated) is exempt from the "one chromatic accent only" count, but
     **only** for colors used inside that section's own `<figure class="diagram">` / SVG
     boundary.
     - **No exception outside the container.** The section's own surrounding prose and
       `<figcaption>` outside the `<figure>` boundary, every other section in the document,
       every other diagram type (all 13 non-statistical types), and an undeclared-capability
       style's statistical chart (which stays on the existing L1/L2 degrade) all remain bound
       by the "one chromatic accent only" rule above with no exception.
     - **Fail-closed, same check.** Missing `tokens.css`, or a `chart-capability` field that
       fails to parse, resolves to `"undeclared"` / `"malformed"` per
       `_parse_chart_capability_header` — never silently treated as declared. An undeclared
       style gets zero multi-color pass-through; the single-accent rule stays fully in force.
   - Fix: demote extra accents to weight/size/spacing hierarchy; map any cold gray to the
     warm four-step text scale (`--near-black > --dark-warm > --olive > --stone`).
   Check: `grep -cE "var\(--accent\)"` (count vs total body elements — over-count = over-paint);
   `grep -nE "#[0-9a-fA-F]{6}"` then verify each gray hex by eye satisfies `R≥G>B`.

Text-adaptation IF-THEN rules (orphan-line sweep, truncation ban, CJK stack/lang/tracking) → see `../../design/references/typography-discipline.md` (advisory at render time).

---

## SVG Strategy by Type

| Type | Primary SVG | Fallback (if content resists the primary) |
|------|-------------|-------------------------------------------|
| A – Technical | Flow diagram (decision/data flow) | Comparison matrix |
| B – Narrative | Relationship / concept map | Timeline |
| C – Research | Score bar chart or comparison table with visual bars | Source provenance graph |

**Minimum requirement:** every `book` output must contain at least one SVG diagram.
If the content genuinely has nothing spatial or relational to visualise, generate a
*thematic summary SVG* — a single-sentence core claim rendered as a styled text card
with a simple geometric frame.

---

## Synthesis Length Limits

| Measure | Limit |
|---------|-------|
| Sections extracted | 4–8 |
| Key claims per section | 1–3 bullet points |
| Total body text in HTML | ≤ 1800 words |
| Content beyond limit | Reference as "延伸閱讀" link block at the bottom |

These limits keep the rendered HTML focused and readable.
Longer source material is summarised, not truncated mid-sentence.
