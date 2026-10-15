<!-- Source: https://skills.wheresryan.sh/anatomy/collection/lit-by-facing | Retrieved: 2026-10-13 | Anatomy by Ryan (@wheresryan22), MIT | extracted verbatim with curl, scripts/styles/SVG stripped -->

# Lit by facing

- Source: https://skills.wheresryan.sh/anatomy/collection/lit-by-facing
- Retrieved: 2026-10-13
- Section: early
- Breadcrumb: Collection/Early examples/Lit by facing
- Byline: No. 50 · Early example
- Collection card text: 50 | Lit by facing

## Description

A clear rim lit by two fixed lights, a key and a half-strength fill, each point by how squarely its normal faces them.

## Note

Drawn while the skill was being made, for a long article on rendering frosted panes in WebGL.

## Prompt

```
(no prompt on page)
```

## Interaction hints

- Move round the rim

## Readouts (server-rendered)

- L 1.00 · rim adds 0.246

## Control labels (aria-label)

- Where the meter stands on the rim
- (aria-valuetext) top-left corner: L 1.00, the rim adds 0.246 of white at its edge
- A light-meter rig on an optical bench. A clear pane lies on a stepped plinth inside a rail ring. A key lamp on a column stands in the back corner, at the pane's top left, and a smaller fill lamp behind a half screen stands in the front corner. A carriage rides the ring with a cell facing out from the rim and a dial whose needle reads the light where its arm touches. A recorder in the left corner plots that light round the loop, and a dimmer in the right corner, wired to both lamps, is set to rim 0.16.

## Figure labels (SVG text/title)

- rim 0.16

## Install and usage (verbatim)

## Install

```
npm install anatomy-figures
```

## In your code

page.tsx

```
import { LitByFacing } from "anatomy-figures";

<LitByFacing theme="light" />
```

Or load this figure on its own, so the others never download:

page.tsx

```
import LitByFacing from "anatomy-figures/lit-by-facing";
```

## Theme it

Early examples keep their own light and dark palettes: theme picks one, and --anatomy-card sets the ground.

page.tsx

```
<LitByFacing
  theme="dark"
  tokens={{ "--anatomy-card": "#000000" }}
/>
```

## Without React

It still draws with React inside, so install react and react-dom next to it.

index.html

```
import { define } from "anatomy-figures/element/lit-by-facing";

define();

<anatomy-lit-by-facing theme="light"></anatomy-lit-by-facing>
```

Bevel offsetPress and pull

The Creation of Adam, Michelangelo, c. 1512

## Credits

- Figures and text: Ryan (@wheresryan22), Anatomy, MIT
- Page artwork credit: The Creation of Adam, Michelangelo, c. 1512
