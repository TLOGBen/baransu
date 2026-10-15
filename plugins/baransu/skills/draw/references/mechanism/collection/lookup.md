<!-- Source: https://skills.wheresryan.sh/anatomy/collection/lookup | Retrieved: 2026-10-13 | Anatomy by Ryan (@wheresryan22), MIT | extracted verbatim with curl, scripts/styles/SVG stripped -->

# Lookup

- Source: https://skills.wheresryan.sh/anatomy/collection/lookup
- Retrieved: 2026-10-13
- Section: early
- Breadcrumb: Collection/Early examples/Lookup
- Byline: No. 43 · Early example
- Collection card text: 43 | Lookup

## Description

A reading stand: a clear pane on threaded posts over the frost plate it reads from. A probe sets one pixel, and the wire drops to where it samples.

## Note

Drawn while the skill was being made, for a long article on rendering frosted panes in WebGL.

## Prompt

```
(no prompt on page)
```

## Interaction hints

- Move toward the rim

## Readouts (server-rendered)

- b 0.900 · reads 29 px out

## Legend keys

- One pixel’s lookup, from the probe to the plate
- The 12 px grid, on the plate and through the pane
- Where that pixel reads

## Figure caption

No. 43. A reading stand: a clear pane on four threaded posts, held over the frost plate it reads from, both ruled with the same 12 px grid. The probe on the back rail sets one pixel on the pane, and the wire drops to the spot on the plate that pixel shows. Across the flat middle it reads straight down, and the grid passes straight through. Across the 26 px bezel it reads further out along its normal: at `b` 0.5, 0.75, 0.9 and 0.97 it reads 4, 14, 29 and 58 px out, so the grid seen through the bezel crowds toward the rim. The slope stops at 6, and so does the sled: its stop sits 87 px past the rim, and no pixel reads further.

## Control labels (aria-label)

- Where the probe sits, from the middle of the pane to its rim
- (aria-valuetext) The probe is in the bezel at b 0.900: the pixel reads the plate 29 px further out along its normal.
- A reading stand. A clear pane sits on four threaded posts over a plate ruled with a 12 px grid; seen through the pane, the grid crowds toward the rim. A probe on a rail sets one pixel on the pane, and a wire drops to where that pixel reads the plate: straight down in the middle, further out across the bezel, never more than 87 px past the rim.

## Figure labels (SVG text/title)

- clear · r 14.49

## Install and usage (verbatim)

## Install

```
npm install anatomy-figures
```

## In your code

page.tsx

```
import { Lookup } from "anatomy-figures";

<Lookup theme="light" />
```

Or load this figure on its own, so the others never download:

page.tsx

```
import Lookup from "anatomy-figures/lookup";
```

## Theme it

Early examples keep their own light and dark palettes: theme picks one, and --anatomy-card sets the ground.

page.tsx

```
<Lookup
  theme="dark"
  tokens={{ "--anatomy-card": "#000000" }}
/>
```

## Without React

It still draws with React inside, so install react and react-dom next to it.

index.html

```
import { define } from "anatomy-figures/element/lookup";

define();

<anatomy-lookup theme="light"></anatomy-lookup>
```

Four framesProfile

The Creation of Adam, Michelangelo, c. 1512

## Credits

- Figures and text: Ryan (@wheresryan22), Anatomy, MIT
- Page artwork credit: The Creation of Adam, Michelangelo, c. 1512
