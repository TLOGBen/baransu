<!-- Source: https://skills.wheresryan.sh/anatomy/collection/separable-blur | Retrieved: 2026-10-13 | Anatomy by Ryan (@wheresryan22), MIT | extracted verbatim with curl, scripts/styles/SVG stripped -->

# Separable blur

- Source: https://skills.wheresryan.sh/anatomy/collection/separable-blur
- Retrieved: 2026-10-13
- Section: early
- Breadcrumb: Collection/Early examples/Separable blur
- Byline: No. 40 · Early example
- Collection card text: 40 | Separable blur

## Description

A bench with one blur dial and two ways to spend it: a single pass that reads a whole square of taps, or two passes that read a row and then a column.

## Note

Drawn while the skill was being made, for a long article on rendering frosted panes in WebGL.

## Prompt

```
(no prompt on page)
```

## Interaction hints

- Drag ← → to set the blur

## Readouts (server-rendered)

- blur 9 px · 98 taps, not 2,401

## Legend keys

- The comb at work: one pass, 49 taps
- The pin block: one pass over the square, for comparison

## Figure caption

No. 40. A bench with one blur dial and two ways to spend it. Every pin and every tooth is a tap; I draw every fourth, as tall as its weight. On the left, the pin block is the blur as one pass: its bed stands for 49 × 49 = 2,401 reads of the picture for each pixel. On the right is what the renderer runs. The first comb’s teeth lie along x: it reads across x and writes `scratch`, where the grid’s columns go soft. Once it has passed, the second comb’s teeth lie along y: it reads `scratch` across y and writes `frosted`. That is 49 + 49 = 98 reads. Dragging turns the dial, and only the spacing moves: there are always 8 taps per sigma, 3 sigma each way. At 0 both read one tap, the first comb stays parked, and `frosted` is a plain copy, because the renderer leaves `scratch` out.

## Control labels (aria-label)

- Blur radius
- (aria-valuetext) Blur 9 px: the pin block would read 2,401 taps in one pass; the two combs read 49 along x into scratch, then 49 along y into frosted, 98 in all
- A bench with a pin block and a tray. The pin block stands 49 by 49 taps in one bed, drawn every fourth and as tall as their weight. The tray has two combs of 49 teeth on crossing tracks: one rakes the picture along x into scratch, then the other rakes scratch along y into frosted.

## Figure labels (SVG text/title)

- 49 × 49

## Install and usage (verbatim)

## Install

```
npm install anatomy-figures
```

## In your code

page.tsx

```
import { SeparableBlur } from "anatomy-figures";

<SeparableBlur theme="light" />
```

Or load this figure on its own, so the others never download:

page.tsx

```
import SeparableBlur from "anatomy-figures/separable-blur";
```

## Theme it

Early examples keep their own light and dark palettes: theme picks one, and --anatomy-card sets the ground.

page.tsx

```
<SeparableBlur
  theme="dark"
  tokens={{ "--anatomy-card": "#000000" }}
/>
```

## Without React

It still draws with React inside, so install react and react-dom next to it.

index.html

```
import { define } from "anatomy-figures/element/separable-blur";

define();

<anatomy-separable-blur theme="light"></anatomy-separable-blur>
```

One stageField key

The Creation of Adam, Michelangelo, c. 1512

## Credits

- Figures and text: Ryan (@wheresryan22), Anatomy, MIT
- Page artwork credit: The Creation of Adam, Michelangelo, c. 1512
