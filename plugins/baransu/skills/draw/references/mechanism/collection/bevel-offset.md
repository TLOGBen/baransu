<!-- Source: https://skills.wheresryan.sh/anatomy/collection/bevel-offset | Retrieved: 2026-10-13 | Anatomy by Ryan (@wheresryan22), MIT | extracted verbatim with curl, scripts/styles/SVG stripped -->

# Bevel offset

- Source: https://skills.wheresryan.sh/anatomy/collection/bevel-offset
- Retrieved: 2026-10-13
- Section: early
- Breadcrumb: Collection/Early examples/Bevel offset
- Byline: No. 49 · Early example
- Collection card text: 49 | Bevel offset

## Description

A block of clear glass clamped on a bench with its profile facing you, and a comb that shows how far out each bevel pixel reads.

## Note

Drawn while the skill was being made, for a long article on rendering frosted panes in WebGL.

## Prompt

```
(no prompt on page)
```

## Interaction hints

- Slide along the bench to set the ior

## Readouts (server-rendered)

- ior 1.46 · r 14.49 · rim reads 87 px

## Control labels (aria-label)

- Index of refraction of the sample
- (aria-valuetext) ior 1.46, r 14.49: the rim reads 87 px out and the flat middle straight down
- A bench refractometer. A block of clear glass, 46 px thick with a 26 px bevel, is clamped on a stage with its cut face toward you, so its eased profile shows. A comb above it holds one pixel every 2 px; from each, a sight line drops to the glass and on to the ruled plate below, where that pixel reads. Under the flat middle the lines fall straight; across the bevel they fan out, and the rim's line lands on a cursor 6 × r past the rim. A dial at the back sets the ior from 1.00 to 1.80, and a gauge on the column reads the block's thickness.

## Figure labels (SVG text/title)

- ior

## Install and usage (verbatim)

## Install

```
npm install anatomy-figures
```

## In your code

page.tsx

```
import { BevelOffset } from "anatomy-figures";

<BevelOffset theme="light" />
```

Or load this figure on its own, so the others never download:

page.tsx

```
import BevelOffset from "anatomy-figures/bevel-offset";
```

## Theme it

Early examples keep their own light and dark palettes: theme picks one, and --anatomy-card sets the ground.

page.tsx

```
<BevelOffset
  theme="dark"
  tokens={{ "--anatomy-card": "#000000" }}
/>
```

## Without React

It still draws with React inside, so install react and react-dom next to it.

index.html

```
import { define } from "anatomy-figures/element/bevel-offset";

define();

<anatomy-bevel-offset theme="light"></anatomy-bevel-offset>
```

Spot plateLit by facing

The Creation of Adam, Michelangelo, c. 1512

## Credits

- Figures and text: Ryan (@wheresryan22), Anatomy, MIT
- Page artwork credit: The Creation of Adam, Michelangelo, c. 1512
