# slide-image-prompts.md

> **Scope: PPT only.** This document governs image handling and external AI image-generation prompt templates for `/design` PPT outputs (slide-cores). It does **not** apply to long-form output (`--format longform`). The `/book` skill's image-generation capability is out of scope here — this file regulates user-supplied image placement and prompt templates only; it never calls an external image API.
>
> Audience: `/design` slide-core authors and `check.py` lint source.

---

## 1. Scope Declaration

- **Applies to**: all `--format ppt` slide-core HTML (9 layouts).
- **Does not apply to**: `--format longform` (single-column long-form is not governed by this document).
- **Out of scope**: actual invocation of external AI image-generation tools; this document only provides prompt templates for the user to copy and paste.

---

## 2. User Image Handling Rules

An `<img>` or `background-image` the user pastes into a slide-core must follow the `object-fit` / `object-position` defaults below. Defaults differ per layout because each image_slot has a different aspect ratio and content focal point.

### Reference Table

| Layout       | Default object-fit | Default object-position | fit-contain fallback | Notes |
|--------------|-----------------|----------------------|----------------------|------|
| cover        | `cover`         | `center 40%`         | switch to `contain` allowed  | Full-bleed; use `center 35%` when the portrait head sits high |
| section      | `cover`         | `center center`      | switch to `contain` allowed  | Chapter divider page, pure background or decorative use |
| content-bullets | `cover`      | `center center`      | `contain` allowed       | Bulleted page; if a right-side image_slot exists, treat as 2col |
| content-2col | `cover`         | `center 35%`         | `contain` not recommended     | Two-column portrait / scene photo; `top center` forbidden (P0-2) |
| data         | `contain`       | `center center`      | already contain by default       | Charts / screenshots; must not be cropped, keep the full border |
| kpi-grid     | `cover`         | `center center`      | `contain` allowed       | Multi-tile KPI, background image is usually texture or abstract |
| compare      | `cover`         | `center 35%`         | `contain` allowed       | Side-by-side comparison; both focal points must match (both `center 35%`) |
| quote        | `cover`         | `center center`      | `contain` allowed       | Quotation page background, avoid centering a person's face |
| closing      | `cover`         | `center 40%`         | `contain` allowed       | Closing page; consistent with cover |

### Common Rules

- **P0-2 alignment**: scenes containing a person or a primary visual focal point must use `center 35%`, **never** `top center` (which crops off the chin and body).
- **fit-contain**: chart-type layouts (data layout) always use `contain` to avoid cropping; for other layouts, if the user image has an abnormal aspect ratio, manually switching to `contain` is allowed, but the reason must be noted in an HTML comment.
- **Background-color fallback**: with `object-fit: contain`, the `<figure>` parent background uses the `--swiss-canvas-muted` token to avoid transparent color holes.
- **`<figcaption>` required**: layouts containing an image_slot (content-2col / data / kpi-grid / compare) must have `<figure>` + `<figcaption>` wrapping (even when the caption is blank, keep the DOM structure for lint).

---

## 2b. Slide Type-Size and Density Hard Thresholds (machine-verifiable value table)

Slides render one at a time, each full-screen, and runaway type size is the most common defect in PPT output. The three groups below are hard, machine-checkable values, not suggestions; on violation, reflow — do not shrink the body type size.

### (1) Large-Type Dual Constraint (vw + vh)

Large type always uses `font-size: min(Xvw, Yvh)`, with `Y ≥ X × 1.6`. Reason: on a 16:9 screen `1vw : 1vh ≈ 1.78`, so a `vw`-only constraint shrinks about 20% on a standard screen — a reproducible bug; adding the `vh` constraint is what locks the visual weight on a narrow screen.

| Role | Constraint |
|------|------|
| `h-hero` (cover main title) | `min(11.6vw, 19vh)` |
| `h-xl` (chapter heading) | `min(7vw, 12vh)` |
| Large numeral (KPI / data) | `min(8.4vw, 14vh)` |

### (2) Chinese Title Length → Type-Size Mapping (bin first, then assign level)

Bin a Chinese title by character count / line count first, then assign the type size; **when overlong, cut the copy first — do not shrink the body**.

| Bin | Characters / lines | Handling |
|------|------------|------|
| Extra short | ≤6 chars | Use the `h-hero` ceiling |
| Short | 7–10 chars | Drop one level to `h-xl` |
| Two lines | 2 lines, ≤8 chars each | `h-xl`, tighten line spacing |
| Two lines long | 2 lines, 9–12 chars | Drop one more level |
| Three lines | 3 lines | Cut copy back to two lines first; only use the body heading level when it can't be cut |

### (3) Presentation Minimum Type-Size Floor

| Text category | Floor |
|----------|------|
| Body text | ≥18px |
| Caption | ≥16px |
| meta / header & footer | ≥14px |

When it won't fit: delete copy or split the page first — **never compress the type size below the floor**.

---

## 3. Prompt Templates for External AI Image-Generation Tools

The 9 prompts below correspond to the 9 slide-core layouts (one H2 section per layout). Each is a "positive description + style anchor"; after the user copies it into any external AI image-generation tool (Midjourney / DALL·E / Stable Diffusion / nano-banana, etc.), they **must** append the shared negative tail at the end (see section 4).

## Layout: cover

```
Editorial hero image for a presentation cover slide: clean composition, single focal subject offset to the right third, generous negative space on the left for title overlay, Swiss-poster aesthetic, muted neutral palette with one bold accent color, soft natural light, photographic realism, 16:9.
```

## Layout: section

```
Abstract chapter-divider visual: minimal geometric composition, two-tone palette, large flat color field with a single linear element crossing the frame, no figurative content, suitable as a subtle backdrop behind a large numeral or section title, 16:9.
```

## Layout: content-bullets

```
Subtle textural background for a bulleted content slide: low-contrast paper-grain or fine grid texture, off-white base with one muted accent tint at 10% opacity, no central subject, no competing focal point, designed to sit behind body text without distraction, 16:9.
```

## Layout: content-2col

```
Documentary-style photograph for a two-column content slide right pane: human subject or scene, eye-line approximately 35% from the top of the frame, shallow depth of field, neutral environmental context, editorial color grade, no text, 4:5 portrait crop.
```

## Layout: data

```
Clean infographic-style chart illustration for a data slide: single chart type (bar or line), minimal axes, two-color palette aligned with Swiss preset accent, no decorative elements, no 3D effects, flat vector aesthetic, generous margins so the chart reads at slide-distance, 16:9.
```

## Layout: kpi-grid

```
Abstract textural background for a KPI-grid slide: very low-contrast geometric pattern (dot grid or thin lines), single muted tint, designed to recede behind four to six numeric tiles, no figurative content, no focal point, 16:9.
```

## Layout: compare

```
Side-by-side documentary photograph pair for a comparison slide: two subjects of the same category, identical framing and lighting, both with eye-line at approximately 35% from the top, consistent color grade across both halves, neutral backgrounds, 16:9 split into two 4:5 panes.
```

## Layout: quote

```
Atmospheric backdrop for a quotation slide: soft out-of-focus environmental texture, low-contrast neutral palette, no figurative content, no human face, designed to sit behind a large pull-quote without competing for attention, 16:9.
```

## Layout: closing

```
Editorial closing-slide hero image: open horizon or forward-looking composition, single focal element offset to lower-right third, generous upper-left negative space for closing message, warm neutral palette with one accent tint, photographic realism, 16:9.
```

---

## 4. Shared Negative Tail

Before sending any of the 9 prompts into an external AI image-generation tool, you **must** append the following string at the end (verbatim, do not reword):

```
no title, no footer, no page chrome, no logo, no border
```

Reason: the slide-core's chrome (title, footer, border, logo) is drawn by HTML + tokens.css. If the generated image embeds these elements itself, it double-stacks with the slide-core chrome and breaks the layout. The negative tail forces the AI tool to produce a "pure content" image, which the slide-core then wraps on its own.
