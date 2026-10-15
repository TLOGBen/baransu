<!-- Source: https://skills.wheresryan.sh/anatomy/collection/process-pump | Retrieved: 2026-10-13 | Anatomy by Ryan (@wheresryan22), MIT | extracted verbatim with curl, scripts/styles/SVG stripped -->

# Process pump

- Source: https://skills.wheresryan.sh/anatomy/collection/process-pump
- Retrieved: 2026-10-13
- Section: webgl
- Breadcrumb: Collection/WebGL/Process pump
- Byline: No. 23 · WebGL · Refinery pump
- Collection card text: 23 | Process pump | Refinery pump

## Description

An API 610 process pump cut open at the shaft, drawing 255 °C gas oil from a suction drum. Starve its suction head and vapour sheets grow on the vanes at the eye while the head on the curve drops.

## Prompt

```
/anatomy explain how a refinery pump cavitates when its suction head runs short, interactive
```

## Interaction hints

- Drag ↔ valve
- ↕ drum level
- `F` strainer

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
import { ProcessPump } from "anatomy-figures";

<ProcessPump theme="light" />
```

Or load this figure on its own, so the others never download:

page.tsx

```
import ProcessPump from "anatomy-figures/process-pump";
```

## Theme it

Five themes (dark, light, paper, blueprint, sepia), or your own colours through tokens. Every token.

page.tsx

```
<ProcessPump
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
import { define } from "anatomy-figures/element/process-pump";

define();

<anatomy-process-pump theme="light"></anatomy-process-pump>
```

Power stationWatch movement

The Creation of Adam, Michelangelo, c. 1512

## Credits

- Figures and text: Ryan (@wheresryan22), Anatomy, MIT
- Page artwork credit: The Creation of Adam, Michelangelo, c. 1512
