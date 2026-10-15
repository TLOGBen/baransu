<!-- Source: https://skills.wheresryan.sh/anatomy/collection/spot-plate | Retrieved: 2026-10-13 | Anatomy by Ryan (@wheresryan22), MIT | extracted verbatim with curl, scripts/styles/SVG stripped -->

# Spot plate

- Source: https://skills.wheresryan.sh/anatomy/collection/spot-plate
- Retrieved: 2026-10-13
- Section: early
- Breadcrumb: Collection/Early examples/Spot plate
- Byline: No. 48 · Early example
- Collection card text: 48 | Spot plate

## Description

Six channels of drops on a spot plate, each pair one group. Close enough, two drops run together into one piece of glass.

## Note

Drawn while the skill was being made, for a long article on rendering frosted panes in WebGL.

## Prompt

```
(no prompt on page)
```

## Interaction hints

- Slide across to open the fan

## Readouts (server-rendered)

- merge 20 px · 3 of 6 joined

## Control labels (aria-label)

- Merge, in pixels
- (aria-valuetext) merge 20 px: 3 of 6 pairs joined, gaps 4, 10 and 16 px; 24, 32 and 44 px stay apart
- A lab spot plate on a bench. The plate has six channels, each holding a pair of glass drops, R30 and R22, at gaps of 4, 10, 16, 24, 32, 44 px, drawn to scale against a ruler on the rim. On the right, beside a dropper bottle, a fan of six feeler blades, one for each gap, turns on a pivot over a protractor marked 0 to 48 px; the top blade is merge. As it opens, each blade stops at its own gap, and the pair with that gap runs together into one piece of glass.

## Figure labels (SVG text/title)

- merge

## Install and usage (verbatim)

## Install

```
npm install anatomy-figures
```

## In your code

page.tsx

```
import { SpotPlate } from "anatomy-figures";

<SpotPlate theme="light" />
```

Or load this figure on its own, so the others never download:

page.tsx

```
import SpotPlate from "anatomy-figures/spot-plate";
```

## Theme it

Early examples keep their own light and dark palettes: theme picks one, and --anatomy-card sets the ground.

page.tsx

```
<SpotPlate
  theme="dark"
  tokens={{ "--anatomy-card": "#000000" }}
/>
```

## Without React

It still draws with React inside, so install react and react-dom next to it.

index.html

```
import { define } from "anatomy-figures/element/spot-plate";

define();

<anatomy-spot-plate theme="light"></anatomy-spot-plate>
```

Frosted copyBevel offset

The Creation of Adam, Michelangelo, c. 1512

## Credits

- Figures and text: Ryan (@wheresryan22), Anatomy, MIT
- Page artwork credit: The Creation of Adam, Michelangelo, c. 1512
