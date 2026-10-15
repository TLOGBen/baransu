<!-- Source: https://skills.wheresryan.sh/anatomy/collection/afterburner | Retrieved: 2026-10-13 | Anatomy by Ryan (@wheresryan22), MIT | extracted verbatim with curl, scripts/styles/SVG stripped -->

# Afterburner

- Source: https://skills.wheresryan.sh/anatomy/collection/afterburner
- Retrieved: 2026-10-13
- Section: webgl
- Breadcrumb: Collection/WebGL/Afterburner
- Byline: No. 16 · WebGL · Thrust stand
- Collection card text: 16 | Afterburner | Thrust stand

## Description

A turbojet hung on a thrust stand with its afterburner cut open. Past military power, fuel sprays in behind the turbine, the flame catches on the V-gutters and the nozzle petals open, while a load cell reads the thrust climb from 52.9 to 79.3 kN.

## Prompt

```
/anatomy explain how a jet engine afterburner works, interactive
```

## Interaction hints

- Click or ← → for throttle

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
import { Afterburner } from "anatomy-figures";

<Afterburner theme="light" />
```

Or load this figure on its own, so the others never download:

page.tsx

```
import Afterburner from "anatomy-figures/afterburner";
```

## Theme it

Five themes (dark, light, paper, blueprint, sepia), or your own colours through tokens. Every token.

page.tsx

```
<Afterburner
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
import { define } from "anatomy-figures/element/afterburner";

define();

<anatomy-afterburner theme="light"></anatomy-afterburner>
```

TemperatureGlory hole

The Creation of Adam, Michelangelo, c. 1512

## Credits

- Figures and text: Ryan (@wheresryan22), Anatomy, MIT
- Page artwork credit: The Creation of Adam, Michelangelo, c. 1512
