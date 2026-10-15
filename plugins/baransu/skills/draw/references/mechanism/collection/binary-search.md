<!-- Source: https://skills.wheresryan.sh/anatomy/collection/binary-search | Retrieved: 2026-10-13 | Anatomy by Ryan (@wheresryan22), MIT | extracted verbatim with curl, scripts/styles/SVG stripped -->

# Binary search

- Source: https://skills.wheresryan.sh/anatomy/collection/binary-search
- Retrieved: 2026-10-13
- Section: svg
- Breadcrumb: Collection/SVG/Binary search
- Byline: No. 02 · SVG · Lab balance
- Collection card text: 02 | Binary search | Lab balance

## Description

A laboratory balance behind a case of sixteen brass weights in order. Each try weighs the sample against the middle weight left standing, and the half that cannot hold the answer sinks into its seats.

## Prompt

```
/anatomy explain binary search, interactive
```

## Interaction hints

- Drag along the weights

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
import { BinarySearch } from "anatomy-figures";

<BinarySearch theme="light" />
```

Or load this figure on its own, so the others never download:

page.tsx

```
import BinarySearch from "anatomy-figures/binary-search";
```

## Theme it

Five themes (dark, light, paper, blueprint, sepia), or your own colours through tokens. Every token.

page.tsx

```
<BinarySearch
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
import { define } from "anatomy-figures/element/binary-search";

define();

<anatomy-binary-search theme="light"></anatomy-binary-search>
```

Hash map collisionsDNS resolution

The Creation of Adam, Michelangelo, c. 1512

## Credits

- Figures and text: Ryan (@wheresryan22), Anatomy, MIT
- Page artwork credit: The Creation of Adam, Michelangelo, c. 1512
