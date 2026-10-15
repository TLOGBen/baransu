<!-- Source: https://skills.wheresryan.sh/anatomy/collection/shared-canvas | Retrieved: 2026-10-13 | Anatomy by Ryan (@wheresryan22), MIT | extracted verbatim with curl, scripts/styles/SVG stripped -->

# Shared canvas

- Source: https://skills.wheresryan.sh/anatomy/collection/shared-canvas
- Retrieved: 2026-10-13
- Section: early
- Breadcrumb: Collection/Early examples/Shared canvas
- Byline: No. 36 · Early example
- Collection card text: 36 | Shared canvas

## Description

A drafting board in device pixels. The canvas is born at 300 × 150, and its rulers ride out whenever a draw needs more room.

## Note

Drawn while the skill was being made, for a long article on rendering frosted panes in WebGL.

## Prompt

```
(no prompt on page)
```

## Interaction hints

- Hover to hold · click to step [pointer] [touch: Tap to step]

## Readouts (server-rendered)

- draw 4 · 304 × 224 · canvas 512 × 352

## Legend keys

- Rulers on ratchets, out only
- Size a draw needs
- The draw, from (0, 0)
- copyTo(), 1:1

## Figure caption

No. 36. I’ve built the shared canvas as a drafting board, in device pixels at 2×. The corner block is (0, 0), where the viewport and the scissor start, and the two rulers that ride out from it mark the canvas’s far edges. It is born at 300 × 150, like every canvas element. When a draw needs more room, a ruler clicks out until it fits, and its ratchet never lets it back, up to `MAX_TEXTURE_SIZE`. A toggle needs 268 × 224 with its 40 px bleed, so the height ruler moves; a 96 px drop needs 352 × 352, so both do; a 256 × 144 pane needs 512 × 288, so the width ruler does; a button at its 72 px minimum needs 304 × 224, which fits, so nothing moves. Every card seats against the corner block, and `copyTo()` lifts off exactly its `w × h`, 1:1. In the code the canvas takes its new size in one step; I’ve let the rulers click out a tooth at a time so you can watch it, and spaced the teeth and the dots 32 px apart.

## Control labels (aria-label)

- Draws into the shared canvas
- (aria-valuetext) Draw 4 of 4: the button needs 304 × 224. It fits, so neither ruler moves and the canvas stays 512 × 352. Its card seats against the corner block at (0, 0), and a copy of exactly 304 × 224 lifts off, 1:1.
- Draw 4 of 4: the button needs 304 × 224. It fits, so neither ruler moves and the canvas stays 512 × 352. Its card seats against the corner block at (0, 0), and a copy of exactly 304 × 224 lifts off, 1:1.

## Figure labels (SVG text/title)

- 0,0

## Install and usage (verbatim)

## Install

```
npm install anatomy-figures
```

## In your code

page.tsx

```
import { SharedCanvas } from "anatomy-figures";

<SharedCanvas theme="light" />
```

Or load this figure on its own, so the others never download:

page.tsx

```
import SharedCanvas from "anatomy-figures/shared-canvas";
```

## Theme it

Early examples keep their own light and dark palettes: theme picks one, and --anatomy-card sets the ground.

page.tsx

```
<SharedCanvas
  theme="dark"
  tokens={{ "--anatomy-card": "#000000" }}
/>
```

## Without React

It still draws with React inside, so install react and react-dom next to it.

index.html

```
import { define } from "anatomy-figures/element/shared-canvas";

define();

<anatomy-shared-canvas theme="light"></anatomy-shared-canvas>
```

One contextOne texture

The Creation of Adam, Michelangelo, c. 1512

## Credits

- Figures and text: Ryan (@wheresryan22), Anatomy, MIT
- Page artwork credit: The Creation of Adam, Michelangelo, c. 1512
