<!-- Source: https://skills.wheresryan.sh/anatomy/collection/lru-cache | Retrieved: 2026-10-13 | Anatomy by Ryan (@wheresryan22), MIT | extracted verbatim with curl, scripts/styles/SVG stripped -->

# LRU cache

- Source: https://skills.wheresryan.sh/anatomy/collection/lru-cache
- Retrieved: 2026-10-13
- Section: svg
- Breadcrumb: Collection/SVG/LRU cache
- Byline: No. 05 · SVG · Bookcase
- Collection card text: 05 | LRU cache | Bookcase

## Description

A low bookcase. Four books stand on top between bookends, most recently used at the left; a miss sends the right-hand book back to its slot below.

## Prompt

```
/anatomy explain how an LRU cache evicts entries, interactive
```

## Interaction hints

- Click a book
- `A–J`

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
import { LruCache } from "anatomy-figures";

<LruCache theme="light" />
```

Or load this figure on its own, so the others never download:

page.tsx

```
import LruCache from "anatomy-figures/lru-cache";
```

## Theme it

Five themes (dark, light, paper, blueprint, sepia), or your own colours through tokens. Every token.

page.tsx

```
<LruCache
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
import { define } from "anatomy-figures/element/lru-cache";

define();

<anatomy-lru-cache theme="light"></anatomy-lru-cache>
```

Message queueTCP handshake

The Creation of Adam, Michelangelo, c. 1512

## Credits

- Figures and text: Ryan (@wheresryan22), Anatomy, MIT
- Page artwork credit: The Creation of Adam, Michelangelo, c. 1512
