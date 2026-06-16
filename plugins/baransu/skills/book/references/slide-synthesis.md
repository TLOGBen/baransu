# Stage 2B — Slide synthesis (PPT mode only)

Run only when `$FORMAT` is `ppt` or `all`. Use the same `$RAW_CONTENT` as Stage 2A; `$SLUG` is inherited from Stage 2A.

Extract the slide structure `$STRUCTURE_SLIDES` from `$RAW_CONTENT`. **layout is not hardcoded**: this stage dynamically reads `slide-cores/` from the project root, builds a decision table, then resolves each slide's `layout_type` via first-match + positional override.

## Reading project root slide-cores

Read path: `{project_root}/slide-cores/*.html` (copied to the project root by `/baransu:design preset <name>`; this stage only reads, never modifies).

Algorithm:

1. List all `.html` files under `{project_root}/slide-cores/`.
2. For each HTML, parse the leading YAML front-matter, fields:
   - `layout_id` (string, e.g. `"content-bullets"`, matching the filename)
   - `applies_to.bullet_count` (range, e.g. `"0"` / `"1-3"` / `"4-5"`)
   - `applies_to.has_image` (enum: `required` | `optional` | `forbidden`)
   - `applies_to.role` (enum: `body` | `positional_first` | `positional_last` | `section_divider`)
   - optional `image_slot.{aspect_ratio, object_position, fit}`
3. Register each `(layout_id, applies_to)` into the **dynamic decision table**; the set of available `layout_id` values in the table is exactly the enum for `$STRUCTURE_SLIDES.slides[*].layout_type`.
4. Do not hardcode the layout list — if any of the 9 layouts is removed or added, the decision table changes accordingly.

## Decision logic (first-match + positional override)

**Priority principle**: positional rules always rank higher than content-driven rules. Even if the first page has 1-3 bullets that perfectly match `content-bullets`, it still goes to `cover` (positional-driven > content-driven).

| Row | Condition | layout_type | role |
|---|---|---|---|
| 1 | position = first page (fixed) | `cover` | positional_first (take H1 + subtitle) |
| 2 | position = last page (conditional, see CTA/acknowledgement detection below) | `closing` | positional_last |
| 3 | heading-only (no body) | `section` | section_divider |
| 4 | quote within 50 characters | `quote` | body |
| 5 | A vs B comparison block | `compare` | body |
| 6 | 4-6 stat numbers | `kpi-grid` | body |
| 7 | contains inline SVG or a large table | `data` | body |
| 8 | text on the left, one visual on the right | `content-2col` | body |
| 9 | 1-3 bullets | `content-bullets` | body |
| 10 | other (fallback → same layout as row 9) | `content-bullets` | body |

**Fallback layout**: any body slot that matches none of rows 3-9 ultimately falls back to `content-bullets` (row 10 is an alias of row 9, not a new layout).

**Cover is fixed for the first page**: the first slide always goes to `cover`, taking the markdown H1 as the main title and the immediately following lead-in or subtitle as the subtitle, with no bullets.

**Closing is conditional for the last page**: in priority order, check whether the final section of the source contains any of the following:

- (a) a markdown link containing one of the verbs 「聯絡 / 訂閱 / 下單 / contact / subscribe / cta / book a call」;
- (b) a 「致謝 / Acknowledgement / Thanks」 heading;
- (c) a `mailto:` or contact-info block.

If none of the three are present → row 2 does not apply, **closing omit** (do not force-insert an empty closing), and the last page degrades to row 9 (`content-bullets`).

## Graceful degradation on missing files / parse failure

- **`{project_root}/slide-cores/` does not exist or is empty**: emit the warning「請先跑 `/baransu:design preset <name>` 取得 slide-cores」, **do not abort**; degrade to the hardcoded fallback three-layout set `{cover, closing, content-bullets}`, every body slot goes to `content-bullets`, and cover/closing still apply per the positional rule.
- **YAML parse failure on a given slide-core HTML**: warn with the filename and the failure reason, **remove that layout from the decision table**, the other layouts remain usable; content that would trigger that layout degrades to the fallback `content-bullets`.
- Both of the above degradations **do not abort** Stage 2B; the subsequent Stage 3 still renders normally (GATE-G SKIPs as needed in the later validator stage).

## $STRUCTURE_SLIDES schema

```typescript
interface SlideStructure {
  slides: Slide[];
}

interface Slide {
  // dynamic enum: taken from the set of layout_id values registered in the decision table
  // under a full preset: cover | section | content-bullets | content-2col | data | kpi-grid | compare | quote | closing
  // in fallback mode: cover | content-bullets | closing
  layout_type: string;
  heading: string;
  body_bullets?: string[];  // for content-bullets / content-2col, typically 1-3 items
  has_svg?: boolean;        // if true, generate an inline SVG on this slide
}
```

## Count and structure constraints

- Total slide count: **6-12 slides**
- The first slide is fixed as `cover`; whether the last page is `closing` depends on CTA/acknowledgement detection (omit if absent; the last page uses a body layout)
- `heading` is required; `body_bullets` and `has_svg` are optional

Store the result as `$STRUCTURE_SLIDES`.

## Hard rules for slide font sizing and height limits (PPT output quality)

Render-time standing instruction: when the Stage 3 PPTX path (render-pipelines.md step one「生成 slide HTML」) applies large type to each slide, it **must** obey the following binary-decidable hard rules. Violating any one → mark fail in the final-report self-check, and fix the copy or split the page before rendering. The slide container is 16:9 (the PPTX path is fixed at `960×540px`, so `100vw=960px`, `100vh=540px`, aspect ratio 960/540≈1.778).

### 1. Large-type dual constraint `font-size: min(Xvw, Yvh)`, and `Y ≥ X × 1.6`

Using the `vw` single constraint alone in a 16:9 container gets clipped and shrinks ~20% (reproducible bug): `min(7vw, 10vh)` at 960×540 has `7vw = 67.2px = 12.4vh`, clipped by `10vh = 54px`, leaving only ~80% in practice → large type inexplicably shrinks and the layout becomes unbalanced. Failure branch: **only `vw` is seen without `vh`, or `Y < X × 1.6` → that large type fails**.

Quick-reference table (apply directly, do not re-derive):

| Role | `font-size` |
|---|---|
| h-hero declaration / cover giant title | `min(11.6vw, 19vh)` |
| section title h-xl | `min(7vw, 12vh)` ~ `min(7.4vw, 13vh)` |
| KPI large number | `min(8.4vw, 14vh)` |
| subtitle | `min(7.6vw, 13vh)` |
| medium number | `min(4.6vw, 8.5vh)` ~ `min(5.6vw, 10vh)` |

### 2. For Chinese titles, pick the tier first, then set the font size (square characters have a large visual footprint)

First count the number of title lines and characters per line to pick the tier, then set the font size. Failure branch: **3 lines still don't fit → rewrite the copy to shorten it; do not drop the font size below the tier**.

| Tier | `font-size` |
|---|---|
| 1 line ≤8 characters | `min(6.4vw, 11.2vh)` |
| 2 lines, ≤8 characters each | `min(5.8vw, 10.2vh)` |
| 2 lines, either line 9-12 characters | `min(5.2vw, 9.2vh)` |
| 3 lines (rewrite preferred, last resort) | `min(4.6vw, 8.2vh)` |

### 3. Minimum font-size floor for presentation (a projection screen cannot use the web's 10-12px)

Slides are viewed on a projection screen / from a distance, so the floor is higher than for the web. Failure branch: **content doesn't fit → first cut copy / split the page / switch `layout_type`; never compress the font size below the floor**.

| Role | Minimum font size |
|---|---|
| body / main explanation | `≥ 18px` |
| card description / list / timeline / caption | `≥ 16px` |
| meta / kicker / chart label | `≥ 14px` |
