<!-- Source: https://skills.wheresryan.sh/anatomy/collection/plasma-cutter | Retrieved: 2026-10-13 | Anatomy by Ryan (@wheresryan22), MIT | extracted verbatim with curl, scripts/styles/SVG stripped -->

# Plasma cutter

- Source: https://skills.wheresryan.sh/anatomy/collection/plasma-cutter
- Retrieved: 2026-10-13
- Section: webgl
- Breadcrumb: Collection/WebGL/Plasma cutter
- Byline: No. 19 · WebGL · CNC gantry
- Collection card text: 19 | Plasma cutter | CNC gantry

## Description

A gantry carries a torch over a 12 mm steel plate on water-pan slats. It pierces, then cuts a part with the arc dragging behind; sparks quench in the water, and the kerf glows for only a few millimetres.

## Prompt

```
/anatomy explain how a CNC plasma cutter cuts steel, interactive
```

## Interaction hints

- Hover or drag the plate
- `Space` runs
- `Q` speed

## Readouts (server-rendered)

(empty in server HTML; filled client-side)

## Install and usage (verbatim)

## Install

```
npm install anatomy-figures
```

## In your code

page.tsx

```
import { PlasmaCutter } from "anatomy-figures";

<PlasmaCutter theme="light" />
```

Or load this figure on its own, so the others never download:

page.tsx

```
import PlasmaCutter from "anatomy-figures/plasma-cutter";
```

## Theme it

Five themes (dark, light, paper, blueprint, sepia), or your own colours through tokens. Every token.

page.tsx

```
<PlasmaCutter
  theme="light"
  tokens={{
    "--anatomy-card": "#ffffff",
    "--anatomy-lit": "#e5484d",
  }}
/>
```

## Without React

index.html

```
import { define } from "anatomy-figures/element/plasma-cutter";

define();

<anatomy-plasma-cutter theme="light"></anatomy-plasma-cutter>
```

Tokamak shotForge and hammer

The Creation of Adam, Michelangelo, c. 1512

## Credits

- Figures and text: Ryan (@wheresryan22), Anatomy, MIT
- Page artwork credit: The Creation of Adam, Michelangelo, c. 1512
