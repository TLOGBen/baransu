## Contents

- Fields
- Complete Example

# Digest Frontmatter Spec

This document adds per-field prose and a complete example for the YAML frontmatter
of digest output files produced by `/baransu:learn` (`.claude/learn/digests/{slug}.md`).
The authoritative schema is the inline frontmatter block in SKILL.md Stage 5 §5 —
consult this file only when a field's meaning is in doubt. If this file and SKILL.md
ever disagree, SKILL.md wins; keep this file in sync when the skill changes.

---

## Fields

### `topic`

**Type:** string
**Required:** yes

The research topic keyword or phrase that was given to `/baransu:learn`. One sentence or
short phrase; identifies what the digest is about.

---

### `sources`

**Type:** array of objects (`{ slug, url }`)
**Required:** yes (at least one element)

The list of source materials consumed during the Collect phase. Each element has two
sub-fields, both mandatory:

| Sub-field | Type | Description |
|-----------|------|-------------|
| `slug`    | string | The `/read` material slug used internally to reference the source |
| `url`     | string | The original URL of the source, or `local:{path}` for local files |

---

### `created_at`

**Type:** string (ISO 8601 timestamp)
**Required:** yes

The moment the digest file was first written. Records when this learning artifact was
produced; enables chronological sorting and cache invalidation.

---

### `language`

**Type:** `"zh"` or `"en"`
**Required:** yes

The output language of the digest body, determined by `/baransu:learn` at Stage 5 §1:
a single CJK character anywhere in the draft sets `"zh"`; otherwise `"en"`. Exactly
one of the two allowed values must appear.

---

### `phases_completed`

**Type:** array of strings
**Required:** yes

The list of phases that have been completed for this digest. Valid values (in order):

| Value      | Phase |
|------------|-------|
| `collect`  | Collect — fetch and store source materials via `/read` |
| `digest`   | Digest — extract key points and filter noise |
| `outline`  | Outline — build the article structure |
| `fill_in`  | Fill-in — write the full draft from the outline |
| `refine`   | Refine — language polish via `/write` |

A digest written by the normal Stage 5 flow contains all five values.

---

## Complete Example

```yaml
---
topic: "WebAssembly Component Model"
sources:
  - slug: "wasm-component-model-explainer"
    url: "https://github.com/WebAssembly/component-model/blob/main/design/mvp/Explainer.md"
  - slug: "wasm-interface-types-proposal"
    url: "local:/home/user/notes/wit-proposal.md"
created_at: "2026-04-25T08:30:00+08:00"
language: "en"
phases_completed:
  - collect
  - digest
  - outline
  - fill_in
  - refine
---
```

Below the closing `---`, the file contains the Refine-phase output: a clean markdown
article with no Before/After markers or `/write` correction annotations.
