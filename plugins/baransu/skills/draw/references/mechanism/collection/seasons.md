<!-- Source: https://skills.wheresryan.sh/anatomy/collection/seasons | Retrieved: 2026-10-13 | Anatomy by Ryan (@wheresryan22), MIT | extracted verbatim with curl, scripts/styles/SVG stripped -->

# Seasons

- Source: https://skills.wheresryan.sh/anatomy/collection/seasons
- Retrieved: 2026-10-13
- Section: 3d
- Breadcrumb: Collection/3D/Seasons
- Byline: No. 25 · 3D · Tellurion
- Collection card text: 25 | Seasons | Tellurion

## Description

A brass tellurion on a turntable. A lamp on the pillar is the Sun; five gears keep the globe's 23.4° axis pointing the same way all year, so the hemispheres take turns facing the lamp. Turning in true 3D made it slow to build: hours, not minutes.

## Prompt

```
/anatomy explain why the Earth has seasons, interactive
```

## Interaction hints

- Drag to turn
- `←→` date
- `Space` pause

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
import { Seasons } from "anatomy-figures";

<Seasons theme="light" />
```

Or load this figure on its own, so the others never download:

page.tsx

```
import Seasons from "anatomy-figures/seasons";
```

## Theme it

Five themes (dark, light, paper, blueprint, sepia), or your own colours through tokens. Every token.

page.tsx

```
<Seasons
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
import { define } from "anatomy-figures/element/seasons";

define();

<anatomy-seasons theme="light"></anatomy-seasons>
```

Watch movementDesk computer

The Creation of Adam, Michelangelo, c. 1512

## Credits

- Figures and text: Ryan (@wheresryan22), Anatomy, MIT
- Page artwork credit: The Creation of Adam, Michelangelo, c. 1512
