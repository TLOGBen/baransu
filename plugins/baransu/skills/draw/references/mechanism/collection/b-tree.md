<!-- Source: https://skills.wheresryan.sh/anatomy/collection/b-tree | Retrieved: 2026-10-13 | Anatomy by Ryan (@wheresryan22), MIT | extracted verbatim with curl, scripts/styles/SVG stripped -->

# B-tree index

- Source: https://skills.wheresryan.sh/anatomy/collection/b-tree
- Retrieved: 2026-10-13
- Section: svg
- Breadcrumb: Collection/SVG/B-tree index
- Byline: No. 11 · SVG · Rotary card file
- Collection card text: 11 | B-tree index | Rotary card file

## Description

A rotary card file. Ten trays on a wheel are the index's pages, and the wheel brings one to the reading stop at a time, so a lookup costs one read per level.

## Prompt

```
/anatomy explain how a B-tree index finds a row, interactive
```

## Interaction hints

- Move to pick
- tap to find

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
import { BTree } from "anatomy-figures";

<BTree theme="light" />
```

Or load this figure on its own, so the others never download:

page.tsx

```
import BTree from "anatomy-figures/b-tree";
```

## Theme it

Five themes (dark, light, paper, blueprint, sepia), or your own colours through tokens. Every token.

page.tsx

```
<BTree
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
import { define } from "anatomy-figures/element/b-tree";

define();

<anatomy-b-tree theme="light"></anatomy-b-tree>
```

Mark and sweepDebounce, throttle

The Creation of Adam, Michelangelo, c. 1512

## Credits

- Figures and text: Ryan (@wheresryan22), Anatomy, MIT
- Page artwork credit: The Creation of Adam, Michelangelo, c. 1512
