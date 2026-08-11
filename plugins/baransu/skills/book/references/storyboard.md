# storyboard — Stage 2C confirmation rules (`--storyboard`)

Full rules for the opt-in per-page confirmation layer. SKILL.md Stage 2C carries
the hook; everything below is the detail it points to.

## Position and trigger

Stage 2C runs **after** the structures exist and **before** Stage 3 Render — the
only point where the actual output units are known. It is entered when
`$STORYBOARD` is true (Stage 0 §3b parsed `--storyboard`).

Which structures are echoed depends on what Stage 2B produced:

- `$FORMAT` ∈ {`html`, `pdf`} → long-form sections from `$STRUCTURE` only.
- `$FORMAT` ∈ {`ppt`, `all`} → **both** `$STRUCTURE` sections and
  `$STRUCTURE_SLIDES.slides` in ONE batch. `--format ppt` still produces and
  gates the long-form HTML (SKILL.md Stage 4 §1 PPT-mode addition), so its
  sections may never be skipped just because slides exist.

## Skip conditions

Skipped when any one holds — the whole stage, including the echo:

- The `--auto` or `--no-interview` flag is present (these extend to Stage 2C;
  their Stage 0b behavior is unchanged).
- The run is driven non-interactively (/loop, cron, Workflow) — see
  `loop-pauses.md`.

Stage 0b's two OTHER skip conditions (a `/read` / `/learn` slug input, and
`--text` under 200 words) **do NOT carry over**: 0b skips them because audience
and purpose are already implicit before acquisition, whereas Stage 2C runs after
the structure exists and slug-to-book is a primary path for this feature.

When skipping, print one stderr line: `Stage 2C skipped: {reason}`, then continue
to Stage 3.

## Precondition check (before the echo, not after)

`{project_root}/tokens.css` is a **hard abort** in Stage 3 §1. Verify it exists
BEFORE presenting the echo — otherwise the user completes a full round of
editing and is then aborted, losing everything (results are never persisted).
Missing → output 「請先跑 `/baransu:design preset <style>`（kami / google-design /
swiss）再用 `--storyboard`」 and stop before the echo.

## The echo (one batch, one round)

Present, in Traditional Chinese, as a single batch:

1. **場景目標** — the restated overall goal of this book, derived from
   `$STRUCTURE`'s title / subtitle plus the Stage 0b brief when one exists.
2. **One row per output unit**, in deck / document order:
   - the unit's heading
   - its content outline (long-form: the 1–3 key claims; slides: `heading` +
     `body_bullets`)
   - an empty **感覺** field for the user to fill

The user edits whatever they want and confirms once. Do not ask unit by unit —
6–12 slides one round each is a dozen round-trips, which this stage exists to
avoid.

## Where confirmed content goes

Two carriers, each with a NAMED consumer. A field with no consumer is a field
the user fills for nothing.

| Side | Carrier | Consumer |
|---|---|---|
| Long-form | `$STRUCTURE` per-section `scene_goal` / `outline` / `feel` | Stage 3 §3 soft generation (`For each section from $STRUCTURE`, SKILL.md:361/:374) — already reads the whole structure |
| Slides | `$STRUCTURE_SLIDES.slides[*].feel` | `render-pipelines.md` §6b Step 1 「Generate slide HTML」 — carries an explicit consumption instruction |

The slide side had NO consumer before this feature: §6b Step 1 reads a skeleton
and fills it, naming exactly which fields it consumes. Adding the field without
the consumption sentence in `render-pipelines.md` would make every slide-side
answer inert.

## What 感覺 may and may not do

**Design intent — bounded variation inside one frame.** The point is that each
page may feel different while every page still visibly belongs to the same
design system. So `感覺` is deliberately a *selector*, not a *composer*: it never
opens a new degree of freedom — it **picks a value inside a range the existing
rules already permit**. A page that reads as "tighter" or "airier" than its
neighbour does so by choosing a different end of an already-legal step, never by
escaping the step. Widening `感覺` into free composition would buy per-page
expressiveness at the cost of the book reading as one artifact — that trade is
explicitly refused here.

- **Spacing / line-height / column width** — pick within the quantified steps of
  SKILL.md §3's render-time hard rules (inter-section gap within the 3xl 80–120pt
  step; reading line-height within 1.50–1.55, CJK screens up to 1.65; reading
  column ≤ 740px / body ≤ 880px). Values outside those steps stay forbidden;
  `感覺` only decides which end of an already-legal range applies.
- **Component selection** — SKILL.md:366 is unchanged: `Select a component by the
  section's data shape, not by feel`. `感覺` never overrides the data-shape
  criterion; it only chooses among candidates that criterion already admits.
- **Visual focus and §9-range composition** — fully open. This is the one place
  `感覺` composes rather than selects.
- **Slide layout** — `layout_type` is decided by the Stage 2B decision table and
  checked by GATE-G. `感覺` MUST NOT change it; it adjusts how the chosen
  skeleton is filled, never which skeleton is used.

**Precedence** (mirroring what SKILL.md:155 already fixes for `$INTERVIEW_BRIEF`):

1. Conflict with `perception-guide` A/B/C layout rules → **perception-guide wins**.
2. Conflict with the Stage 0b interview brief → **`感覺` wins** (later and more
   specific).
3. When the preset's §9 lacks the expression-range fields → the SKILL.md:376
   conservative fallback still applies; `感覺` acts only inside that conservative
   baseline.

## Overflow handling (three kinds, one rule)

User edits can push the structure past a limit that was applied BEFORE this
stage. All three are handled identically:

| Overflow | Limit | Applied at |
|---|---|---|
| Section count | 4–8 | Stage 2A §4 |
| Slide count | 6–12 | Stage 2B |
| Word count | ≤ 1800 words | Stage 2A §4 (`Apply synthesis length limits`) |

On any overflow: reorganize the structure back inside the limit and echo a
SECOND time, stating explicitly which unit will move to 延伸閱讀 — never
truncate silently and never write filler on the user's behalf. Word-count
overflow matters most here: the existing remedy demotes excess into a 延伸閱讀
link block, which would silently downgrade a section the user just confirmed.

**Termination**: the second echo is the last. If the structure still overflows
after it, truncate at the hard limit, list every dropped unit by name, and
proceed to Stage 3 — no third round.

## Not persisted

Confirmed content lives in the two in-run carriers only. No storyboard file is
written, and nothing is reused across books. Consequence, stated plainly: no
gate can compare the output against what was confirmed, because there is no
artifact to compare against — `validate-output.ts` takes a single HTML path
(SKILL.md:442). The prose rule below is therefore skippable-by-construction, and
the only detection surface is a human page-by-page comparison.

**Authority of confirmed content**: the confirmed 場景目標 / 大綱 / 感覺 are the
generation basis. `$RAW_CONTENT` may supply supporting paragraphs and evidence;
it may not drop, rewrite, or override what the user confirmed.

## Hint when NOT used

When `$STORYBOARD` is false AND the run is interactive, print one stderr line
after the structures exist (never blocking, never awaiting a reply):

```
本次未逐頁確認；要逐頁確認請加 --storyboard 重跑
```

This position reaches every path — including `/read` / `/learn` slugs, which
Stage 0b skips — and the user can see the actual section / slide count the hint
refers to.
