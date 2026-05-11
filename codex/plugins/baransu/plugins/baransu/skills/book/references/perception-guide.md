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
- Tight body line-height (1.65) — engineers scan, not read linearly

---

### Type B — Narrative

**Signals:**
- Prose-heavy; argument builds across paragraphs
- Opinion piece, essay, letter, or personal reflection
- Audience is general; document purpose is to *persuade* or *share experience*

**Examples:** Blog posts, essays, X threads, newsletters, thought leadership pieces

**Visual treatment:**
- Wide body margin with generous line-height (1.85) — maximise reading comfort
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

These apply regardless of content type — they are the Kami invariants for `book`:

| Element | Rule |
|---------|------|
| Design tokens | Import from `design/references/paper-preset.md` — use named tokens, never raw hex |
| Background | `--parchment` (#f5f4ed) as page canvas; `--ivory` (#faf9f5) for cards |
| Accent | `--brand` (#1B365D) ink-blue only; no secondary accent colour |
| Typography | Charter/Georgia (en) + TsangerJinKai02/Noto Serif TC (zh) — always serif for body |
| TOC sidebar | Show at ≥ 1024px viewport; sticky; highlight active section via IntersectionObserver |
| SVG diagrams | Minimum 1 per document; stroke-based, round linecap, 1.5–2px stroke; no fills heavier than 20% opacity |
| Left rule | 1px warm accent line at x=52px inside the paper sheet (as in golden-template.html) |
| Max body width | 760px; reading column capped at 680px |
| Paper shadow | `box-shadow: 0 2px 8px rgba(0,0,0,.08), 0 12px 40px rgba(0,0,0,.06)` |

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
