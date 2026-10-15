<!-- Source: https://skills.wheresryan.sh/anatomy/collection/power-station | Retrieved: 2026-10-13 | Anatomy by Ryan (@wheresryan22), MIT | extracted verbatim with curl, scripts/styles/SVG stripped -->

# Power station

- Source: https://skills.wheresryan.sh/anatomy/collection/power-station
- Retrieved: 2026-10-13
- Section: webgl
- Breadcrumb: Collection/WebGL/Power station
- Byline: No. 22 · WebGL · Generating unit
- Collection card text: 22 | Power station | Generating unit

## Description

A 660 MW generator turning at exactly 3,000 rpm and a transformer lifting 22 to 400 kV. Open the disconnector before the breaker and an arc climbs between the blades until the breaker clears it.

## Prompt

```
/anatomy explain how a power station generator puts power on the grid and why a disconnector must never break current, interactive
```

## Interaction hints

- `Space` steps
- `W` wrong order

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
import { PowerStation } from "anatomy-figures";

<PowerStation theme="light" />
```

Or load this figure on its own, so the others never download:

page.tsx

```
import PowerStation from "anatomy-figures/power-station";
```

## Theme it

Five themes (dark, light, paper, blueprint, sepia), or your own colours through tokens. Every token.

page.tsx

```
<PowerStation
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
import { define } from "anatomy-figures/element/power-station";

define();

<anatomy-power-station theme="light"></anatomy-power-station>
```

Turbofan ground runProcess pump

The Creation of Adam, Michelangelo, c. 1512

## Credits

- Figures and text: Ryan (@wheresryan22), Anatomy, MIT
- Page artwork credit: The Creation of Adam, Michelangelo, c. 1512
