<!-- Source: https://skills.wheresryan.sh/anatomy/collection/computer | Retrieved: 2026-10-13 | Anatomy by Ryan (@wheresryan22), MIT | extracted verbatim with curl, scripts/styles/SVG stripped -->

# Desk computer

- Source: https://skills.wheresryan.sh/anatomy/collection/computer
- Retrieved: 2026-10-13
- Section: svg
- Breadcrumb: Collection/SVG/Desk computer
- Byline: No. 26 · SVG · Desk computer
- Collection card text: 26 | Desk computer | Desk computer

## Description

An old desk computer with a deep screen, a keyboard on a coiled cable and the Anthropic mark on the display. Type on it and the keys go down.

## Prompt

```
/anatomy a physical old screen like Apple’s first PC, with the Anthropic logo on the screen, and a keyboard with a cable
```

## Interaction hints

- Type on it
- click it to switch

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
import { Computer } from "anatomy-figures";

<Computer theme="light" />
```

Or load this figure on its own, so the others never download:

page.tsx

```
import Computer from "anatomy-figures/computer";
```

## Theme it

Five themes (dark, light, paper, blueprint, sepia), or your own colours through tokens. Every token.

page.tsx

```
<Computer
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
import { define } from "anatomy-figures/element/computer";

define();

<anatomy-computer theme="light"></anatomy-computer>
```

SeasonsToken bucket

The Creation of Adam, Michelangelo, c. 1512

## Credits

- Figures and text: Ryan (@wheresryan22), Anatomy, MIT
- Page artwork credit: The Creation of Adam, Michelangelo, c. 1512
