<!-- Source: https://skills.wheresryan.sh/anatomy/collection/one-pane | Retrieved: 2026-10-13 | Anatomy by Ryan (@wheresryan22), MIT | extracted verbatim with curl, scripts/styles/SVG stripped -->

# One pane

- Source: https://skills.wheresryan.sh/anatomy/collection/one-pane
- Retrieved: 2026-10-13
- Section: early
- Breadcrumb: Collection/Early examples/One pane
- Byline: No. 34 · Early example
- Collection card text: 34 | One pane

## Description

A frosted pane as a die set, taken apart into the layers it is drawn from and stacked bottom up on four guide pillars.

## Note

Drawn while the skill was being made, for a long article on rendering frosted panes in WebGL.

## Prompt

```
(no prompt on page)
```

## Interaction hints

- Hover a layer [pointer] [touch: Tap a layer]

## Readouts (server-rendered)

- frost pane · 360 × 220

## Legend keys

- The glass, on top
- A layer it is drawn from
- Bezel, 34 px
- copyTo() into the 2D canvas

## Figure caption

No. 34. One frosted pane as a die set, taken apart into the layers it is drawn from and stacked bottom up on four guide pillars that stand on the corners of the pane’s 360 × 220 box. At the bottom, the picture behind the pane. Above it, the frosted copy I make of it: it covers the box plus 100 px on every side, the reach of the bend and the blur (6 × 11.8 + 3 × 9 + 2), and I draw it at half size, 280 × 210. Then the distance field, just the size of the box, engraved here in rings 12 px apart. On top, the glass, 40 px thick, flat in the middle and curved only in its 34 px bezel, the one band where the picture bends, by 71 px at most. The result is copied into the pane’s 2D canvas, the small frame on the front ledge.

## Control labels (aria-label)

- Lift one layer of the pane
- (aria-valuetext) All layers seated. frost pane · 360 × 220
- A frosted pane as a die set: a heavy base on four feet with four guide pillars standing on the corners of the pane's 360 by 220 box. Riding the pillars, bottom up: the picture, the frosted copy 100 px larger on every side, the distance field cut to the box, and the glass, 40 px thick with a 34 px bezel. A wire runs from the glass to a small framed 2D canvas on the front ledge.

## Figure labels (SVG text/title)

- 2D canvas

## Install and usage (verbatim)

## Install

```
npm install anatomy-figures
```

## In your code

page.tsx

```
import { OnePane } from "anatomy-figures";

<OnePane theme="light" />
```

Or load this figure on its own, so the others never download:

page.tsx

```
import OnePane from "anatomy-figures/one-pane";
```

## Theme it

Early examples keep their own light and dark palettes: theme picks one, and --anatomy-card sets the ground.

page.tsx

```
<OnePane
  theme="dark"
  tokens={{ "--anatomy-card": "#000000" }}
/>
```

## Without React

It still draws with React inside, so install react and react-dom next to it.

index.html

```
import { define } from "anatomy-figures/element/one-pane";

define();

<anatomy-one-pane theme="light"></anatomy-one-pane>
```

Pool reactorOne context

The Creation of Adam, Michelangelo, c. 1512

## Credits

- Figures and text: Ryan (@wheresryan22), Anatomy, MIT
- Page artwork credit: The Creation of Adam, Michelangelo, c. 1512
