---
name: design-token-resolver
purpose: |
  Single source of truth for how /book resolves design tokens
  (colors, surfaces, ink levels) when rendering SVG/CSS for the
  13 diagram types. Defines a three-layer fallback chain plus a
  hex shape contract that all downstream consumers (template,
  example, validate, per-type refs) MUST honour.
---

# Design Token Resolver

This document is the v1.3+ ground truth for token resolution in `/book`.
All template / example / validate code paths and the 13 per-type
reference files reference this file rather than re-deriving rules.

> **v1.4 ack note**: this file was upgraded in v1.4 cross-tool group
> TASK-ct-03 to be three-preset aware. v1.2-era specifics have been
> retired — marker geometry uses chevron `<path d='M2 1 L8 5 L2 9'>`
> (Kami v1.3+ invariant; v1.2 polygon marker is gone), and node-width
> uses the `{128, 144, 160}` 3-tier whitelist (Kami v1.3+ / TASK-svg-05
> GATE-J; the v1.2 "節點寬 12 檔" model is gone). Layer 2 now covers
> three presets — Kami (紙) / Swiss / Google-design — instead of
> Kami-only.

## Resolution flow (overview)

```
START [Need token X for SVG/CSS]
  → Layer 1 {root DESIGN.md has X?}
      yes → shape-contract {value matches ^#[0-9a-fA-F]{3,8}$ ?}
              yes → USE Layer 1 value
              no  → reject + warn → Layer 2
      no  → Layer 2
  → Layer 2 {active preset (Kami | Swiss | Google-design) has X?}
      yes → USE preset value
      no  → Layer 3 {type ∈ sequence / state / swimlane / er ?}
              yes → apply per-type derived rule → USE derived hex
              no  → FAIL: no token for X
```

Stage position inside `/book`:

```
Stage 0 (env+deps)
  → Stage 0.5 (token resolver: this file)
  → Stage 1 (Acquire)
  → Stage 2 (Synthesize)
  → Stage 3 (Render)
  → Stage 4 (validate-output.ts)
```

Relationship to `/design` skill is one-way:

```
/design  → writes →  {git-root}/DESIGN.md  → read by →  /book
```

`/book` never writes back to DESIGN.md and never tells `/design`
which tokens it consumes.

---

## Layer 1: root DESIGN.md (soft read)

Rule:

1. Resolve project root with `git rev-parse --show-toplevel`.
2. Check `{root}/DESIGN.md`. If absent → silently skip Layer 1
   (this is NOT an error; proceed to Layer 2).
3. If present, parse the `§ Color Palette & Roles` markdown table
   and extract rows of the shape
   `| --token-name | #hex | <role> |`.
4. For every extracted hex value, run the **hex shape contract**
   (see below). Values that fail are rejected — that single token
   falls back to Layer 2 (per-token fallback, not whole-table
   fallback), and a warning is appended to `final-report.md`.
5. Values that pass become the active value for that token.

Behaviour summary: Layer 1 is a *soft override*. Missing file,
malformed table, or rejected tokens never abort `/book` — they
quietly degrade to Layer 2 / Layer 3.

### Hex shape contract

A token value is accepted iff it matches:

```
^#[0-9a-fA-F]{3,8}$
```

This covers 3-, 4-, 6-, and 8-digit hex literals (with or without
alpha channel byte). Explicitly **not accepted**:

- `rgba(...)`, `rgb(...)`, `hsl(...)`, `hsla(...)`
- CSS named colors (`red`, `blue`, `currentColor`, …)
- CSS keywords (`inherit`, `transparent`, `unset`, …)
- JavaScript / template expressions
- Injection-shaped payloads such as `red;}</style><script>…`
  (treated as plain non-hex → rejected; this is **security
  critical** — never inline an unvalidated DESIGN.md value into
  an SVG attribute or `<style>` block.)

Non-hex outcome: reject this token, log a `[design-token]
warning: token --X rejected ("...")` line into `final-report.md`,
and fallback to Layer 2 for that single token. **Do not abort
`/book`.**

---

## Layer 2: Built-in presets (Kami / Swiss / Google-design)

If a token is not present (or was rejected) in Layer 1, use the
**active preset** bundled with baransu. v1.3 shipped Kami only;
v1.4 broadens Layer 2 to the three-preset set declared in root
DESIGN.md §2 (TASK-shared-02). Resolution picks the preset
referenced by `DESIGN.md` (or defaults to Kami when absent).

### Three-preset `--paper` / `--accent` hex table

The minimum surface contract — every preset must expose `--paper`
(primary background) and `--accent` (single chromatic role). These
are the canonical hex values consumed by Layer 1 fallback, Layer 3
blends, and `validate-output.ts` GATE checks (cross-ref TASK-ct-04
golden-template variants):

| Preset          | `--paper` | `--accent` | Notes                              |
|-----------------|-----------|------------|------------------------------------|
| Kami (紙)       | `#faf9f5` | `#1B365D`  | ink-blue, ≤5% surface              |
| Swiss           | `#f5f5f1` | `#002FA7`  | International Klein Blue (IKB)     |
| Google-design   | `#FEF7FF` | `#6750A4`  | Material 3 baseline primary        |

> The full per-preset 16-token tables live next to each preset's
> golden-template variant (see TASK-ct-04: `golden-template.html`
> = Kami, `golden-template-swiss.html` = Swiss,
> `golden-template-gd.html` = Google-design). Layer 3 blends
> recompute against whichever preset's `--paper` / `--ink` is
> active — the formulas are unchanged.

### Kami preset reference table (v1.3+ ground truth)

For backward compatibility and as the default fallback, the Kami
preset mirrors the Color Palette table in baransu root DESIGN.md
(16 tokens, all solid hex):

| Token                 | Value     | Role                                                  |
|-----------------------|-----------|-------------------------------------------------------|
| `--parchment`         | `#f5f4ed` | Primary background                                    |
| `--ivory`             | `#faf9f5` | Card / panel surface                                  |
| `--warm-sand`         | `#e8e6dc` | Button / interactive surface                          |
| `--dark-surface`      | `#30302e` | Dark container                                        |
| `--deep-dark`         | `#141413` | Dark page background                                  |
| `--brand`             | `#1B365D` | Accent (ink-blue, only chromatic colour, ≤5% surface) |
| `--brand-light`       | `#2D5A8A` | Link on dark surface                                  |
| `--near-black`        | `#141413` | Primary text                                          |
| `--dark-warm`         | `#3d3d3a` | Secondary text / table header                         |
| `--olive`             | `#504e49` | Subtext / description                                 |
| `--stone`             | `#6b6a64` | Tertiary text / metadata                              |
| `--charcoal`          | `#4d4c48` | Dark muted text                                       |
| `--border`            | `#e8e6dc` | Primary border / divider                              |
| `--border-soft`       | `#e5e3d8` | Secondary border / row separator                      |
| `--brand-tint`        | `#EEF2F7` | Tag background, lightest (solid hex, ≈0.08 rgba)      |
| `--brand-tint-strong` | `#E4ECF5` | Tag background, standard (solid hex, ≈0.18 rgba)      |

Aliases used in the derivation rules below:

- `paper` ≡ `--parchment` (`#f5f4ed`) — base surface for blends
- `ink`   ≡ `--near-black` (`#141413`) — foreground for blends
- `brand` ≡ `--brand` (`#1B365D`)
- `brand-tint` ≡ `--brand-tint` (`#EEF2F7`)

> Note: the blend reference values used in the v1 ground truth
> hex table below are `ink = #141413` and `paper = #faf9f5`
> (i.e. `--ivory` as the lightest neutral). If runtime DESIGN.md
> overrides `ink`/`paper`, recompute with the same formula.

---

## Layer 3: per-type derived rules

Some of the 13 diagram types need tokens that are NOT in the
basic paper / ink / accent palette. For those, Layer 3 derives
the value from an ink-on-paper opacity ramp and **pre-flattens
the result to a solid hex** so that the rendered SVG/CSS never
contains an `rgba(` call. (Kami invariant #8: tag backgrounds —
and by extension all chromatic surfaces — must be solid hex.)

These rules are hard-coded here and do NOT depend on DESIGN.md.

### Derivation formulas

| Type     | Token            | Rule                                                |
|----------|------------------|-----------------------------------------------------|
| sequence | `lifeline-color` | `solid-blend(ink @ 0.30 on paper)`                  |
| state    | `state-active`   | `brand` (direct reference)                          |
| state    | `state-inactive` | `solid-blend(ink @ 0.05 on paper)`                  |
| swimlane | `lane-A`         | `solid-blend(ink @ 0.08 on paper)`                  |
| swimlane | `lane-B`         | `solid-blend(ink @ 0.04 on paper)`                  |
| swimlane | `lane-C`         | `solid-blend(ink @ 0.02 on paper)`                  |
| er       | `entity-key`     | `brand-tint` (direct reference)                     |
| er       | `entity-attr`    | `paper` (direct reference)                          |

`solid-blend(C @ α on B)` is per-channel pre-multiplied alpha,
flattened onto an opaque base:

```
out_ch = round(C_ch × α + B_ch × (1 − α))      for ch ∈ {R, G, B}
```

The output is reassembled into a 6-digit hex literal. No
`rgba(...)` ever leaves Layer 3.

### Pre-computed hex table (v1 ground truth)

Inputs: `ink = #141413`, `paper = #faf9f5`, `brand = #1B365D`,
`brand-tint = #EEF2F7`.

| Type     | Token            | Formula                                       | Pre-computed hex |
|----------|------------------|-----------------------------------------------|------------------|
| sequence | `lifeline-color` | `solid-blend(#141413 @ 0.30 on #faf9f5)`      | `#b6b5af`        |
| state    | `state-active`   | `brand` (direct)                              | `#1B365D`        |
| state    | `state-inactive` | `solid-blend(#141413 @ 0.05 on #faf9f5)`      | `#f1f0eb`        |
| swimlane | `lane-A`         | `solid-blend(#141413 @ 0.08 on #faf9f5)`      | `#ebeae5`        |
| swimlane | `lane-B`         | `solid-blend(#141413 @ 0.04 on #faf9f5)`      | `#f3f1ec`        |
| swimlane | `lane-C`         | `solid-blend(#141413 @ 0.02 on #faf9f5)`      | `#f6f5f0`        |
| er       | `entity-key`     | `brand-tint` (direct)                         | `#EEF2F7`        |
| er       | `entity-attr`    | `paper` (direct)                              | `#faf9f5`        |

This table is the v1 ground truth. `validate-output.ts` EC-12b
verifies (a) no `rgba(` appears in the rendered SVG, and (b) at
least one occurrence of the corresponding hex appears in any SVG
of that type.

If a runtime DESIGN.md sets a different `ink` or `paper`, the
resolver re-runs the same `solid-blend` formula on the new
inputs; the table above is recomputed but the rules are
unchanged.

Purpose statement: *types in the 13-set that need surfaces
beyond paper / ink / accent derive from an ink opacity ramp;
the derived value is pre-flattened to solid hex to keep Kami
invariant #8 (no `rgba(`) intact.*

---

## Error handling (excerpt — token resolver scope)

| Scenario                                                                  | Layer          | Action                                                                                       |
|---------------------------------------------------------------------------|----------------|----------------------------------------------------------------------------------------------|
| `DESIGN.md` not present at git root                                       | token resolver | Silently skip Layer 1, proceed to Layer 2 (NOT an error)                                     |
| `DESIGN.md` token value fails `^#[0-9a-fA-F]{3,8}$`                       | token resolver | Reject that single token, log warning to `final-report.md`, fallback Layer 2                 |
| Injection-shaped value (e.g. `red;}</style><script>…`)                    | token resolver | Treated as plain non-hex → same as above. **Security critical** — never inline raw           |
| Token absent from both Layer 1 and Layer 2 but type ∈ {sequence/state/swimlane/er} | token resolver | Apply Layer 3 derived rule (no warning)                                                      |
| Token absent everywhere and no Layer 3 rule applies                       | token resolver | Hard error — `/book` reports missing token and stops Stage 0.5                               |

The warning-then-fallback path is deliberate: malformed
DESIGN.md must not be able to block `/book` — neither by
crashing it nor by injecting unsanitised content into the
rendered SVG/HTML.

---

## Quick-ref

When you need a token:

1. **Layer 1** — try `{git-root}/DESIGN.md`; accept only values
   matching `^#[0-9a-fA-F]{3,8}$`. Reject + warn + continue on
   anything else.
2. **Layer 2** — fall back to the active preset (Kami / Swiss /
   Google-design; 16 tokens each, all solid hex; covers paper /
   ink / accent / borders / tints). Kami is the default when no
   preset is selected.
3. **Layer 3** — if the type is `sequence` / `state` / `swimlane`
   / `er` and needs `lifeline-color` / `state-{active,inactive}`
   / `lane-{A,B,C}` / `entity-{key,attr}`, use the pre-computed
   hex from the ground-truth table (or recompute with
   `solid-blend` if `ink`/`paper` changed).

Output invariant: every token value that reaches the rendered
SVG/CSS is a solid hex literal — `rgba(` never appears.
