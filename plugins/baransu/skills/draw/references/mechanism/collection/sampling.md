<!-- Source: https://skills.wheresryan.sh/anatomy/collection/sampling | Retrieved: 2026-10-13 | Anatomy by Ryan (@wheresryan22), MIT | extracted verbatim with curl, scripts/styles/SVG stripped -->

# Temperature

- Source: https://skills.wheresryan.sh/anatomy/collection/sampling
- Retrieved: 2026-10-13
- Section: svg
- Breadcrumb: Collection/SVG/Temperature
- Byline: No. 15 · SVG · Roulette wheel
- Collection card text: 15 | Temperature | Roulette wheel

## Description

A roulette wheel whose sixteen pockets are the likeliest next tokens, each as wide as its probability. A thermostat knob sets the temperature and moves the frets.

## Prompt

```
/anatomy explain how temperature changes how a language model picks the next token, interactive
```

## Interaction hints

- Drag to heat
- tap to spin

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
import { Sampling } from "anatomy-figures";

<Sampling theme="light" />
```

Or load this figure on its own, so the others never download:

page.tsx

```
import Sampling from "anatomy-figures/sampling";
```

## Theme it

Five themes (dark, light, paper, blueprint, sepia), or your own colours through tokens. Every token.

page.tsx

```
<Sampling
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
import { define } from "anatomy-figures/element/sampling";

define();

<anatomy-sampling theme="light"></anatomy-sampling>
```

Merge sortAfterburner

The Creation of Adam, Michelangelo, c. 1512

## Credits

- Figures and text: Ryan (@wheresryan22), Anatomy, MIT
- Page artwork credit: The Creation of Adam, Michelangelo, c. 1512
