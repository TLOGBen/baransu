<!-- Source: https://skills.wheresryan.sh/anatomy/collection/tokamak | Retrieved: 2026-10-13 | Anatomy by Ryan (@wheresryan22), MIT | extracted verbatim with curl, scripts/styles/SVG stripped -->

# Tokamak shot

- Source: https://skills.wheresryan.sh/anatomy/collection/tokamak
- Retrieved: 2026-10-13
- Section: webgl
- Breadcrumb: Collection/WebGL/Tokamak shot
- Byline: No. 18 · WebGL · Tokamak
- Collection card text: 18 | Tokamak shot | Tokamak

## Description

A research tokamak cut open at the front, its 32 D-shaped coils, six field rings and solenoid around a ray-marched plasma. Scrub a 37 s pulse from breakdown to flat-top at 3.5 MA and back onto the limiter.

## Prompt

```
/anatomy explain how a tokamak holds a fusion plasma, interactive
```

## Interaction hints

- Drag to scrub
- `Space` plays

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
import { Tokamak } from "anatomy-figures";

<Tokamak theme="light" />
```

Or load this figure on its own, so the others never download:

page.tsx

```
import Tokamak from "anatomy-figures/tokamak";
```

## Theme it

Five themes (dark, light, paper, blueprint, sepia), or your own colours through tokens. Every token.

page.tsx

```
<Tokamak
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
import { define } from "anatomy-figures/element/tokamak";

define();

<anatomy-tokamak theme="light"></anatomy-tokamak>
```

Glory holePlasma cutter

The Creation of Adam, Michelangelo, c. 1512

## Credits

- Figures and text: Ryan (@wheresryan22), Anatomy, MIT
- Page artwork credit: The Creation of Adam, Michelangelo, c. 1512
