<!-- Source: https://skills.wheresryan.sh/anatomy/collection/four-frames | Retrieved: 2026-10-13 | Anatomy by Ryan (@wheresryan22), MIT | extracted verbatim with curl, scripts/styles/SVG stripped -->

# Four frames

- Source: https://skills.wheresryan.sh/anatomy/collection/four-frames
- Retrieved: 2026-10-13
- Section: early
- Breadcrumb: Collection/Early examples/Four frames
- Byline: No. 42 · Early example
- Collection card text: 42 | Four frames

## Description

One chip per draw call, stacked in the order the passes run, for four kinds of frame: from a full rebake of 38 draws down to a still frame with none.

## Note

Drawn while the skill was being made, for a long article on rendering frosted panes in WebGL.

## Prompt

```
(no prompt on page)
```

## Interaction hints

- Hover or pick a stack

## Readouts (server-rendered)

- full rebake · 38 draws

## Legend keys

- The frame picked
- Thick chip: field, ground, frost or glass
- Thin chip: one blur pass
- Empty well: nothing drawn

## Figure caption

No. 42. I stack one chip for every draw, in the order the passes run. The thin chips are the blur, a horizontal and a vertical pass for each of the 16 rounds; the thick ones are the SDF, the gradient, the ground, the two frost passes and the glass. The first frame of a frosted `<Glass>` that draws its own ground stacks all 38. A moving control rebakes its field with `SDF_UNION`, has no ground to draw and keeps its frost, so it stacks 35 on every frame it moves. A still `<Glass>` draws the glass alone. A control at rest matches its mark and returns before `draw`, so its well stays empty and its canvas keeps the last frame. The stack I pick lifts and lights from the bottom up; on the two that pay again every frame, the light keeps climbing.

## Control labels (aria-label)

- A counting tray with four round wells and a stack of chips in each, one chip for every draw, in the order the passes run: 38 chips for a full rebake, 35 for a moving control, 1 for a still pane, and an empty well for a control at rest.
- Which frame
- Full rebake, 38 draws: 1 SDF, 1 gradient, 32 blur, 1 ground, 2 frost and 1 glass
- Moving control, 35 draws: 1 SDF union, 1 gradient, 32 blur and 1 glass; no ground, and the frost is kept
- Still pane, 1 draw: the glass pass alone
- Control at rest, 0 draws: nothing; the mark matches and the frame ends before the GPU

## Figure labels (SVG text/title)

- 38
- 35
- 1
- 0

## Install and usage (verbatim)

## Install

```
npm install anatomy-figures
```

## In your code

page.tsx

```
import { FourFrames } from "anatomy-figures";

<FourFrames theme="light" />
```

Or load this figure on its own, so the others never download:

page.tsx

```
import FourFrames from "anatomy-figures/four-frames";
```

## Theme it

Early examples keep their own light and dark palettes: theme picks one, and --anatomy-card sets the ground.

page.tsx

```
<FourFrames
  theme="dark"
  tokens={{ "--anatomy-card": "#000000" }}
/>
```

## Without React

It still draws with React inside, so install react and react-dom next to it.

index.html

```
import { define } from "anatomy-figures/element/four-frames";

define();

<anatomy-four-frames theme="light"></anatomy-four-frames>
```

Field keyLookup

The Creation of Adam, Michelangelo, c. 1512

## Credits

- Figures and text: Ryan (@wheresryan22), Anatomy, MIT
- Page artwork credit: The Creation of Adam, Michelangelo, c. 1512
