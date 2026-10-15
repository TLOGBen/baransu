<!-- Source: https://skills.wheresryan.sh/anatomy/collection/forge | Retrieved: 2026-10-13 | Anatomy by Ryan (@wheresryan22), MIT | extracted verbatim with curl, scripts/styles/SVG stripped -->

# Forge and hammer

- Source: https://skills.wheresryan.sh/anatomy/collection/forge
- Retrieved: 2026-10-13
- Section: webgl
- Breadcrumb: Collection/WebGL/Forge and hammer
- Byline: No. 20 · WebGL · Coal forge
- Collection card text: 20 | Forge and hammer | Coal forge

## Description

A coal forge with a hand-cranked blower beside a 100 lb power hammer. Cranking brings the bar to a yellow forging heat; each blow of the 45 kg ram flattens it a little more, and the quench tub takes it back to cold.

## Prompt

```
/anatomy explain how a blacksmith heats steel in a coal forge and flattens it under a power hammer, interactive
```

## Interaction hints

- Hold fire
- hold hammer
- tap tub

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
import { Forge } from "anatomy-figures";

<Forge theme="light" />
```

Or load this figure on its own, so the others never download:

page.tsx

```
import Forge from "anatomy-figures/forge";
```

## Theme it

Five themes (dark, light, paper, blueprint, sepia), or your own colours through tokens. Every token.

page.tsx

```
<Forge
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
import { define } from "anatomy-figures/element/forge";

define();

<anatomy-forge theme="light"></anatomy-forge>
```

Plasma cutterTurbofan ground run

The Creation of Adam, Michelangelo, c. 1512

## Credits

- Figures and text: Ryan (@wheresryan22), Anatomy, MIT
- Page artwork credit: The Creation of Adam, Michelangelo, c. 1512
