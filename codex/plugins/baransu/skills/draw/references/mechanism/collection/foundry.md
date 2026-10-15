<!-- Source: https://skills.wheresryan.sh/anatomy/collection/foundry | Retrieved: 2026-10-13 | Anatomy by Ryan (@wheresryan22), MIT | extracted verbatim with curl, scripts/styles/SVG stripped -->

# Pouring steel

- Source: https://skills.wheresryan.sh/anatomy/collection/foundry
- Retrieved: 2026-10-13
- Section: webgl
- Breadcrumb: Collection/WebGL/Pouring steel
- Byline: No. 30 · WebGL · Ladle and mould
- Collection card text: 30 | Pouring steel | Ladle and mould

## Description

A lined ladle on trunnions, tilted by a hand wheel through a 40 to 1 worm gearbox, pours steel through a basin into a sand mould clamped on its bottom board.

## Prompt

```
/anatomy explain how molten steel is poured into a sand mould, interactive
```

## Interaction hints

- Drag or ← → to tilt
- `Space` pours

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
import { Foundry } from "anatomy-figures";

<Foundry theme="light" />
```

Or load this figure on its own, so the others never download:

page.tsx

```
import Foundry from "anatomy-figures/foundry";
```

## Theme it

Five themes (dark, light, paper, blueprint, sepia), or your own colours through tokens. Every token.

page.tsx

```
<Foundry
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
import { define } from "anatomy-figures/element/foundry";

define();

<anatomy-foundry theme="light"></anatomy-foundry>
```

Public keyBox model

The Creation of Adam, Michelangelo, c. 1512

## Credits

- Figures and text: Ryan (@wheresryan22), Anatomy, MIT
- Page artwork credit: The Creation of Adam, Michelangelo, c. 1512
