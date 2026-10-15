<!-- Source: https://skills.wheresryan.sh/anatomy/collection/gradient-descent | Retrieved: 2026-10-13 | Anatomy by Ryan (@wheresryan22), MIT | extracted verbatim with curl, scripts/styles/SVG stripped -->

# Gradient descent

- Source: https://skills.wheresryan.sh/anatomy/collection/gradient-descent
- Retrieved: 2026-10-13
- Section: svg
- Breadcrumb: Collection/SVG/Gradient descent
- Byline: No. 07 · SVG · Contour model
- Collection card text: 07 | Gradient descent | Contour model

## Description

A contour model of a narrow valley, cut from stacked boards. Survey pins strung with thread mark each step down the slope, and a knob sets the learning rate.

## Prompt

```
/anatomy explain how gradient descent finds a minimum, interactive
```

## Interaction hints

- Tap a start
- turn the knob

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
import { GradientDescent } from "anatomy-figures";

<GradientDescent theme="light" />
```

Or load this figure on its own, so the others never download:

page.tsx

```
import GradientDescent from "anatomy-figures/gradient-descent";
```

## Theme it

Five themes (dark, light, paper, blueprint, sepia), or your own colours through tokens. Every token.

page.tsx

```
<GradientDescent
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
import { define } from "anatomy-figures/element/gradient-descent";

define();

<anatomy-gradient-descent theme="light"></anatomy-gradient-descent>
```

TCP handshakeBloom filter

The Creation of Adam, Michelangelo, c. 1512

## Credits

- Figures and text: Ryan (@wheresryan22), Anatomy, MIT
- Page artwork credit: The Creation of Adam, Michelangelo, c. 1512
