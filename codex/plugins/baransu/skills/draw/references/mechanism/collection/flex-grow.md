<!-- Source: https://skills.wheresryan.sh/anatomy/collection/flex-grow | Retrieved: 2026-10-13 | Anatomy by Ryan (@wheresryan22), MIT | extracted verbatim with curl, scripts/styles/SVG stripped -->

# flex-grow

- Source: https://skills.wheresryan.sh/anatomy/collection/flex-grow
- Retrieved: 2026-10-13
- Section: svg
- Breadcrumb: Collection/SVG/flex-grow
- Byline: No. 09 · SVG · Bench vise
- Collection card text: 09 | flex-grow | Bench vise

## Description

A bench vise holding three spring-loaded blocks. Each block carries one spring per point of flex-grow, so every spring takes the same share of the free space.

## Prompt

```
/anatomy explain how flex-grow shares space in CSS flexbox, interactive
```

## Interaction hints

- Drag the jaw
- tap a block

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
import { FlexGrow } from "anatomy-figures";

<FlexGrow theme="light" />
```

Or load this figure on its own, so the others never download:

page.tsx

```
import FlexGrow from "anatomy-figures/flex-grow";
```

## Theme it

Five themes (dark, light, paper, blueprint, sepia), or your own colours through tokens. Every token.

page.tsx

```
<FlexGrow
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
import { define } from "anatomy-figures/element/flex-grow";

define();

<anatomy-flex-grow theme="light"></anatomy-flex-grow>
```

Bloom filterMark and sweep

The Creation of Adam, Michelangelo, c. 1512

## Credits

- Figures and text: Ryan (@wheresryan22), Anatomy, MIT
- Page artwork credit: The Creation of Adam, Michelangelo, c. 1512
