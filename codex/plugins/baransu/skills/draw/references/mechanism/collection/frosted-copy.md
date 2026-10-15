<!-- Source: https://skills.wheresryan.sh/anatomy/collection/frosted-copy | Retrieved: 2026-10-13 | Anatomy by Ryan (@wheresryan22), MIT | extracted verbatim with curl, scripts/styles/SVG stripped -->

# Frosted copy

- Source: https://skills.wheresryan.sh/anatomy/collection/frosted-copy
- Retrieved: 2026-10-13
- Section: early
- Breadcrumb: Collection/Early examples/Frosted copy
- Byline: No. 47 · Early example
- Collection card text: 47 | Frosted copy

## Description

A lightbox and a print: frost is a blurred copy of what is behind the pane, made at half resolution in two passes, then bent by the glass.

## Note

Drawn while the skill was being made, for a long article on rendering frosted panes in WebGL.

## Prompt

```
(no prompt on page)
```

## Interaction hints

- Drag ← → to set the blur

## Readouts (server-rendered)

- blur 9 px · reach 100 px · 160 × 140 texels

## Control labels (aria-label)

- Blur of the frosted copy, in pixels
- (aria-valuetext) Blur 9 pixels: two passes of 49 taps write a 160 × 140 texel copy reaching 100 px past the pane.
- A lightbox with two rollers. The page, a dark print with one bright block just past the pane's right edge, lies on the lit bed. Four easel blades frame the window the copy covers: the pane plus 6r + 3σ + 2 px on every side. One roller rakes across the window and leaves the scratch copy, every row blurred; the second rakes down and leaves the frosted copy, a soft mound of dots on a half-resolution grid. On the front ledge a gauge holds the 49 taps each pass reads, 3σ each side, every fourth a pin as tall as its weight, beside the dial that sets the blur.

## Figure labels (SVG text/title)

- blur

## Install and usage (verbatim)

## Install

```
npm install anatomy-figures
```

## In your code

page.tsx

```
import { FrostedCopy } from "anatomy-figures";

<FrostedCopy theme="light" />
```

Or load this figure on its own, so the others never download:

page.tsx

```
import FrostedCopy from "anatomy-figures/frosted-copy";
```

## Theme it

Early examples keep their own light and dark palettes: theme picks one, and --anatomy-card sets the ground.

page.tsx

```
<FrostedCopy
  theme="dark"
  tokens={{ "--anatomy-card": "#000000" }}
/>
```

## Without React

It still draws with React inside, so install react and react-dom next to it.

index.html

```
import { define } from "anatomy-figures/element/frosted-copy";

define();

<anatomy-frosted-copy theme="light"></anatomy-frosted-copy>
```

Rim lightSpot plate

The Creation of Adam, Michelangelo, c. 1512

## Credits

- Figures and text: Ryan (@wheresryan22), Anatomy, MIT
- Page artwork credit: The Creation of Adam, Michelangelo, c. 1512
