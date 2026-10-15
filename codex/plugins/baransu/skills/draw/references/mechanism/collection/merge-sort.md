<!-- Source: https://skills.wheresryan.sh/anatomy/collection/merge-sort | Retrieved: 2026-10-13 | Anatomy by Ryan (@wheresryan22), MIT | extracted verbatim with curl, scripts/styles/SVG stripped -->

# Merge sort

- Source: https://skills.wheresryan.sh/anatomy/collection/merge-sort
- Retrieved: 2026-10-13
- Section: svg
- Breadcrumb: Collection/SVG/Merge sort
- Byline: No. 14 · SVG · Chime rack
- Collection card text: 14 | Merge sort | Chime rack

## Description

A chime rack of eight tubular bells. An overhead traveller rehangs them run by run, always taking the lower of the two front bells, until they ring in order.

## Prompt

```
/anatomy explain merge sort, interactive
```

## Interaction hints

- Hover to step
- click shuffles

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
import { MergeSort } from "anatomy-figures";

<MergeSort theme="light" />
```

Or load this figure on its own, so the others never download:

page.tsx

```
import MergeSort from "anatomy-figures/merge-sort";
```

## Theme it

Five themes (dark, light, paper, blueprint, sepia), or your own colours through tokens. Every token.

page.tsx

```
<MergeSort
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
import { define } from "anatomy-figures/element/merge-sort";

define();

<anatomy-merge-sort theme="light"></anatomy-merge-sort>
```

MutexTemperature

The Creation of Adam, Michelangelo, c. 1512

## Credits

- Figures and text: Ryan (@wheresryan22), Anatomy, MIT
- Page artwork credit: The Creation of Adam, Michelangelo, c. 1512
