<!-- Source: https://skills.wheresryan.sh/anatomy/collection/glass-furnace | Retrieved: 2026-10-13 | Anatomy by Ryan (@wheresryan22), MIT | extracted verbatim with curl, scripts/styles/SVG stripped -->

# Glory hole

- Source: https://skills.wheresryan.sh/anatomy/collection/glass-furnace
- Retrieved: 2026-10-13
- Section: webgl
- Breadcrumb: Collection/WebGL/Glory hole
- Byline: No. 17 · WebGL · Drum furnace
- Collection card text: 17 | Glory hole | Drum furnace

## Description

A gas-fired drum furnace beside a steel marver. In the hole, walls at 1,150 °C and the burner flame reheat the gather toward 990 °C; on the marver, the steel takes the heat back.

## Prompt

```
/anatomy explain how a glassblower reheats glass in a glory hole, interactive
```

## Interaction hints

- Point to slide the pipe
- `←→`

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
import { GlassFurnace } from "anatomy-figures";

<GlassFurnace theme="light" />
```

Or load this figure on its own, so the others never download:

page.tsx

```
import GlassFurnace from "anatomy-figures/glass-furnace";
```

## Theme it

Five themes (dark, light, paper, blueprint, sepia), or your own colours through tokens. Every token.

page.tsx

```
<GlassFurnace
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
import { define } from "anatomy-figures/element/glass-furnace";

define();

<anatomy-glass-furnace theme="light"></anatomy-glass-furnace>
```

AfterburnerTokamak shot

The Creation of Adam, Michelangelo, c. 1512

## Credits

- Figures and text: Ryan (@wheresryan22), Anatomy, MIT
- Page artwork credit: The Creation of Adam, Michelangelo, c. 1512
