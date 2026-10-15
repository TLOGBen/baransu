<!-- Source: https://skills.wheresryan.sh/anatomy/collection/turbofan | Retrieved: 2026-10-13 | Anatomy by Ryan (@wheresryan22), MIT | extracted verbatim with curl, scripts/styles/SVG stripped -->

# Turbofan ground run

- Source: https://skills.wheresryan.sh/anatomy/collection/turbofan
- Retrieved: 2026-10-13
- Section: webgl
- Breadcrumb: Collection/WebGL/Turbofan ground run
- Byline: No. 21 · WebGL · Trent 970
- Collection card text: 21 | Turbofan ground run | Trent 970

## Description

A Rolls-Royce Trent 970 hung from a ground-run thrust frame, its upper quarter cut away. Push the lever and the three spools wind up at their own speeds, and the load cell reads the thrust climb from 14 to 334 kN.

## Prompt

```
/anatomy explain how a big airliner turbofan engine like the A380's makes thrust, interactive
```

## Interaction hints

- Drag ↔ thrust
- `Space` take-off

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
import { Turbofan } from "anatomy-figures";

<Turbofan theme="light" />
```

Or load this figure on its own, so the others never download:

page.tsx

```
import Turbofan from "anatomy-figures/turbofan";
```

## Theme it

Five themes (dark, light, paper, blueprint, sepia), or your own colours through tokens. Every token.

page.tsx

```
<Turbofan
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
import { define } from "anatomy-figures/element/turbofan";

define();

<anatomy-turbofan theme="light"></anatomy-turbofan>
```

Forge and hammerPower station

The Creation of Adam, Michelangelo, c. 1512

## Credits

- Figures and text: Ryan (@wheresryan22), Anatomy, MIT
- Page artwork credit: The Creation of Adam, Michelangelo, c. 1512
