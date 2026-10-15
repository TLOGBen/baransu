<!-- Source: https://skills.wheresryan.sh/anatomy/collection/one-stage | Retrieved: 2026-10-13 | Anatomy by Ryan (@wheresryan22), MIT | extracted verbatim with curl, scripts/styles/SVG stripped -->

# One stage

- Source: https://skills.wheresryan.sh/anatomy/collection/one-stage
- Retrieved: 2026-10-13
- Section: early
- Breadcrumb: Collection/Early examples/One stage
- Byline: No. 39 · Early example
- Collection card text: 39 | One stage

## Description

A chest of seven drawers, one per render target, each as tall as its bytes per texel and filled in the order the passes write them.

## Note

Drawn while the skill was being made, for a long article on rendering frosted panes in WebGL.

## Prompt

```
(no prompt on page)
```

## Interaction hints

- Hover or ↑ ↓ to open a drawer [pointer] [touch: Tap a drawer to open it]

## Readouts (server-rendered)

- 4 × 8 B · 3 × 4 B per texel

## Legend keys

- Card: the glass pass binds it
- No card: only the passes in between read it

## Figure caption

No. 39. One stage as a chest of seven drawers, filled from the bottom in the order its passes write them. Each drawer is as tall as its bytes per texel: 8 for the four half-float targets that hold the shape, 4 for the three 8-bit ones that hold the backdrop, and a gap keeps the two apart. On each floor I engrave what the target holds. `sdfField` is the distance to a pill, in rings 12 px apart. `rawGradient` is its direction, ticking out from the middle segment where it flips. `blurA` and `blurB` hand it back and forth for sixteen rounds, which pulls the ticks about 7 px off that segment. `source` holds the ground, here a grid, `scratch` that grid blurred along x, and `frosted` blurred along y as well; on a pane with no blur `frosted` is a plain copy and `scratch` goes unused. A card marks the four drawers the glass pass binds, and it reads `source` only when the pane is opaque and has no picture of its own. The pill on top is what that pass draws from them, and it lights whenever one of those four is open.

## Control labels (aria-label)

- Open one of the seven drawers
- (aria-valuetext) All drawers shut
- One stage as a small chest of seven drawers on four feet: four deep drawers below for sdfField, rawGradient, blurA and blurB at 8 bytes per texel, a gap, then three shallow ones for source, scratch and frosted at 4.

## Install and usage (verbatim)

## Install

```
npm install anatomy-figures
```

## In your code

page.tsx

```
import { OneStage } from "anatomy-figures";

<OneStage theme="light" />
```

Or load this figure on its own, so the others never download:

page.tsx

```
import OneStage from "anatomy-figures/one-stage";
```

## Theme it

Early examples keep their own light and dark palettes: theme picks one, and --anatomy-card sets the ground.

page.tsx

```
<OneStage
  theme="dark"
  tokens={{ "--anatomy-card": "#000000" }}
/>
```

## Without React

It still draws with React inside, so install react and react-dom next to it.

index.html

```
import { define } from "anatomy-figures/element/one-stage";

define();

<anatomy-one-stage theme="light"></anatomy-one-stage>
```

FitSeparable blur

The Creation of Adam, Michelangelo, c. 1512

## Credits

- Figures and text: Ryan (@wheresryan22), Anatomy, MIT
- Page artwork credit: The Creation of Adam, Michelangelo, c. 1512
