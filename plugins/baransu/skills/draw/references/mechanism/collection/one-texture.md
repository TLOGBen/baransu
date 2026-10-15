<!-- Source: https://skills.wheresryan.sh/anatomy/collection/one-texture | Retrieved: 2026-10-13 | Anatomy by Ryan (@wheresryan22), MIT | extracted verbatim with curl, scripts/styles/SVG stripped -->

# One texture

- Source: https://skills.wheresryan.sh/anatomy/collection/one-texture
- Retrieved: 2026-10-13
- Section: early
- Breadcrumb: Collection/Early examples/One texture
- Byline: No. 37 · Early example
- Collection card text: 37 | One texture

## Description

A tray holding one uploaded picture and its packed chain of twelve mip levels, read through three loupes at the sizes they need.

## Note

Drawn while the skill was being made, for a long article on rendering frosted panes in WebGL.

## Prompt

```
(no prompt on page)
```

## Interaction hints

- Hover a loupe · click for a new src [touch: Tap for a new src]

## Readouts (server-rendered)

- 1 upload · 3 loupes · 12 levels

## Legend keys

- A pocket: one level, half the last
- A loupe: one pane
- Its base: the window it reads
- The pane’s own box

## Figure caption

No. 37. I’ve built the texture as a tray. The print in the slot at the back is the `<img>`, 2400 × 1500; `hang()` uploads it once with `texImage2D`, flipped in Y, and `generateMipmap` fills the other eleven pockets, each half the last, down to the 1 × 1 pit. Packed this way the twelve hold 4,799,605 texels, a third more than the picture. A dot is 75 × 75 texels of its level, and the lamps count the levels. Each loupe is a pane standing on the window it reads: its own box, dotted, plus the reach of its bend and blur, 89 px clear and 100 px frost. In a 1200 × 750 box on a 2× screen the clear panes draw at device pixels and read level 0; the frosted one draws at half scale, a quarter of the pixels each way, so its level is 1.99991 and it reads level 2. A new `src` is one upload, written from the bottom row up, and every pocket and lens follows.

## Control labels (aria-label)

- The src, the loupes and the levels. Enter loads a new src
- (aria-valuetext) hills.jpg, uploaded 1 time: one texture of 12 levels read by 3 panes.
- A tray holding one 2400 by 1500 texture. A print of the picture stands in a slot at the back. The tray has 12 pockets, one per level, each half the size of the last down to a 1 by 1 pit, packed the way a mip chain packs: the full level on the left, the next beside it, the rest in a row. Every pocket holds the same picture in halftone dots. Three linen testers stand on the pockets as three panes: two clear ones on level 0 and a small frosted one on level 2, each framing the window it reads, its lens showing the dots it draws.

## Install and usage (verbatim)

## Install

```
npm install anatomy-figures
```

## In your code

page.tsx

```
import { OneTexture } from "anatomy-figures";

<OneTexture theme="light" />
```

Or load this figure on its own, so the others never download:

page.tsx

```
import OneTexture from "anatomy-figures/one-texture";
```

## Theme it

Early examples keep their own light and dark palettes: theme picks one, and --anatomy-card sets the ground.

page.tsx

```
<OneTexture
  theme="dark"
  tokens={{ "--anatomy-card": "#000000" }}
/>
```

## Without React

It still draws with React inside, so install react and react-dom next to it.

index.html

```
import { define } from "anatomy-figures/element/one-texture";

define();

<anatomy-one-texture theme="light"></anatomy-one-texture>
```

Shared canvasFit

The Creation of Adam, Michelangelo, c. 1512

## Credits

- Figures and text: Ryan (@wheresryan22), Anatomy, MIT
- Page artwork credit: The Creation of Adam, Michelangelo, c. 1512
