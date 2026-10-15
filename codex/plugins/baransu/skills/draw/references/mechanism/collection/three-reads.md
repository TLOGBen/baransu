<!-- Source: https://skills.wheresryan.sh/anatomy/collection/three-reads | Retrieved: 2026-10-13 | Anatomy by Ryan (@wheresryan22), MIT | extracted verbatim with curl, scripts/styles/SVG stripped -->

# Three reads

- Source: https://skills.wheresryan.sh/anatomy/collection/three-reads
- Retrieved: 2026-10-13
- Section: early
- Breadcrumb: Collection/Early examples/Three reads
- Byline: No. 52 · Early example
- Collection card text: 52 | Three reads

## Description

Lines seen through a bevel come apart into colour: red, green and blue are read at three distances along the same normal.

## Note

Drawn while the skill was being made, for a long article on rendering frosted panes in WebGL.

## Prompt

```
(no prompt on page)
```

## Interaction hints

- Slide ← → to set the spread

## Readouts (server-rendered)

- d 0.045 clear · red–blue 6.4 px

## Control labels (aria-label)

- Dispersion, the spread between the three reads
- (aria-valuetext) d 0.045, clear: red reads 74.5 px out, green 71.3 px, blue 68.1 px; red and blue land 6.4 px apart
- A spectroscope bench. A lamp and a slit at the front send one pixel's sight line into a block of clear glass on a round screw table, cut to show the pane's edge: flat on top, then the 26 px bevel rolling off to the rim. The line meets the bevel at P, b 0.98, and leaves as three: red, green and blue, landing on a ruled screen at the back at three distances out along the same normal, red furthest and blue nearest. A drum on the stage sets the spread between them.

## Figure labels (SVG text/title)

- dispersion

## Install and usage (verbatim)

## Install

```
npm install anatomy-figures
```

## In your code

page.tsx

```
import { ThreeReads } from "anatomy-figures";

<ThreeReads theme="light" />
```

Or load this figure on its own, so the others never download:

page.tsx

```
import ThreeReads from "anatomy-figures/three-reads";
```

## Theme it

Early examples keep their own light and dark palettes: theme picks one, and --anatomy-card sets the ground.

page.tsx

```
<ThreeReads
  theme="dark"
  tokens={{ "--anatomy-card": "#000000" }}
/>
```

## Without React

It still draws with React inside, so install react and react-dom next to it.

index.html

```
import { define } from "anatomy-figures/element/three-reads";

define();

<anatomy-three-reads theme="light"></anatomy-three-reads>
```

Press and pullHash map collisions

The Creation of Adam, Michelangelo, c. 1512

## Credits

- Figures and text: Ryan (@wheresryan22), Anatomy, MIT
- Page artwork credit: The Creation of Adam, Michelangelo, c. 1512
