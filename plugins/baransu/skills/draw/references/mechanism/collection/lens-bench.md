<!-- Source: https://skills.wheresryan.sh/anatomy/collection/lens-bench | Retrieved: 2026-10-13 | Anatomy by Ryan (@wheresryan22), MIT | extracted verbatim with curl, scripts/styles/SVG stripped -->

# Dispersion

- Source: https://skills.wheresryan.sh/anatomy/collection/lens-bench
- Retrieved: 2026-10-13
- Section: early
- Breadcrumb: Collection/Early examples/Dispersion
- Byline: No. 45 · Early example
- Collection card text: 45 | Dispersion

## Description

A lens bench at true scale: a disc of clear glass on a jointed arm over a ruled plate, splitting one probed pixel into red, green and blue reads.

## Note

Drawn while the skill was being made, for a long article on rendering frosted panes in WebGL.

## Prompt

```
(no prompt on page)
```

## Interaction hints

- Hover or ← → to move the probe [pointer] [touch: Drag to move the probe]

## Readouts (server-rendered)

- b 0.985 · red–blue 7.4 px

## Legend keys

- Blue, offset × 0.955
- Green, offset
- Red, offset × 1.045

## Figure caption

No. 45. A lens bench at true scale, one unit to a pixel. A 72 px disc of clear glass sits in a ring mount on a jointed arm, over a ruled plate it reads from. The ring of light marks one pixel in its 26 px bezel, the probe, on a track ruled in tenths of `b`; it reads the plate three times along its normal, and a vernier slider rides the rail to wherever green lands. Move the probe toward the rim and the three reads spread with the reach: red and blue land 1.6 px apart at `b` 0.8, 3.3 at 0.93 and 7.4 at 0.985. The dashed line is as far as any read can land, red at the cap, 91 px past the rim.

## Control labels (aria-label)

- Probe position in the bezel
- (aria-valuetext) b 0.985: green reads 82.7 px out, red and blue land 7.4 px apart
- A lens bench: a 72 px disc of clear glass in a ring mount on a jointed arm, held over a ruled target plate. A probe pixel in its bezel reads the plate three times along its normal; blue lands nearest, green at the offset, red furthest, and a vernier slider on a rail sits where green lands.

## Figure labels (SVG text/title)

- 0.045

## Install and usage (verbatim)

## Install

```
npm install anatomy-figures
```

## In your code

page.tsx

```
import { LensBench } from "anatomy-figures";

<LensBench theme="light" />
```

Or load this figure on its own, so the others never download:

page.tsx

```
import LensBench from "anatomy-figures/lens-bench";
```

## Theme it

Early examples keep their own light and dark palettes: theme picks one, and --anatomy-card sets the ground.

page.tsx

```
<LensBench
  theme="dark"
  tokens={{ "--anatomy-card": "#000000" }}
/>
```

## Without React

It still draws with React inside, so install react and react-dom next to it.

index.html

```
import { define } from "anatomy-figures/element/lens-bench";

define();

<anatomy-lens-bench theme="light"></anatomy-lens-bench>
```

ProfileRim light

The Creation of Adam, Michelangelo, c. 1512

## Credits

- Figures and text: Ryan (@wheresryan22), Anatomy, MIT
- Page artwork credit: The Creation of Adam, Michelangelo, c. 1512
