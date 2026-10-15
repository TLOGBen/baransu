<!-- Source: https://skills.wheresryan.sh/anatomy/collection/fit | Retrieved: 2026-10-13 | Anatomy by Ryan (@wheresryan22), MIT | extracted verbatim with curl, scripts/styles/SVG stripped -->

# Fit

- Source: https://skills.wheresryan.sh/anatomy/collection/fit
- Retrieved: 2026-10-13
- Section: early
- Breadcrumb: Collection/Early examples/Fit
- Byline: No. 38 · Early example
- Collection card text: 38 | Fit

## Description

A picture frame whose window is the element’s box. The print inside is scaled by cover, contain or fill, and the overhang shows what each one crops.

## Note

Drawn while the skill was being made, for a long article on rendering frosted panes in WebGL.

## Prompt

```
(no prompt on page)
```

## Interaction hints

(none on page)

## Readouts (server-rendered)

- cover · scale 0.67 · cropped 37.5%

## Legend keys

- The window: the element’s box, W × H
- Where cover cuts
- Carriages on the square: where the picture is laid

## Figure caption

No. 38. The frame’s window is the element’s box, 1000 × 1000, and the print is the picture, 2400 × 1500. `cover` scales it by `max(W/w, H/h)` = 0.67 to 1600 × 1000, so the 300 px either side fall outside the window: I cut them off and lay them beside the frame, 37.5% of the print. `contain` scales by `min(W/w, H/h)` = 0.42 to 1000 × 625 and leaves bands of 187.5 px above and below. I hatch them; the glass fills them by repeating the edge rows. `fill` scales each axis on its own, 0.42 across and 0.67 down, so the print is stretched over the window like canvas on a stretcher and its sun comes out 1.6 times taller than wide. The carriages on the steel square mark where each fit lays the picture, a tick every 50 px.

## Control labels (aria-label)

- A picture frame whose window is the 1000 × 1000 box. Cover: the 2400 × 1500 print is scaled by 0.67 to 1600 × 1000; the 300 px strips either side are cut off and lie beside the frame.
- Fit

## Figure labels (SVG text/title)

- 2400 × 1500

## Install and usage (verbatim)

## Install

```
npm install anatomy-figures
```

## In your code

page.tsx

```
import { Fit } from "anatomy-figures";

<Fit theme="light" />
```

Or load this figure on its own, so the others never download:

page.tsx

```
import Fit from "anatomy-figures/fit";
```

## Theme it

Early examples keep their own light and dark palettes: theme picks one, and --anatomy-card sets the ground.

page.tsx

```
<Fit
  theme="dark"
  tokens={{ "--anatomy-card": "#000000" }}
/>
```

## Without React

It still draws with React inside, so install react and react-dom next to it.

index.html

```
import { define } from "anatomy-figures/element/fit";

define();

<anatomy-fit theme="light"></anatomy-fit>
```

One textureOne stage

The Creation of Adam, Michelangelo, c. 1512

## Credits

- Figures and text: Ryan (@wheresryan22), Anatomy, MIT
- Page artwork credit: The Creation of Adam, Michelangelo, c. 1512
