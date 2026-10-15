<!-- Source: https://skills.wheresryan.sh/anatomy/collection/bloom-filter | Retrieved: 2026-10-13 | Anatomy by Ryan (@wheresryan22), MIT | extracted verbatim with curl, scripts/styles/SVG stripped -->

# Bloom filter

- Source: https://skills.wheresryan.sh/anatomy/collection/bloom-filter
- Retrieved: 2026-10-13
- Section: svg
- Breadcrumb: Collection/SVG/Bloom filter
- Byline: No. 08 · SVG · Fruit machine
- Collection card text: 08 | Bloom filter | Fruit machine

## Description

A fruit machine. Three reels are the three hash functions and a row of sixteen flags is the bit array; it pays out only when all three of a word's flags are already up.

## Prompt

```
/anatomy explain how a bloom filter works, interactive
```

## Interaction hints

- Pick a coin
- pull or press

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
import { BloomFilter } from "anatomy-figures";

<BloomFilter theme="light" />
```

Or load this figure on its own, so the others never download:

page.tsx

```
import BloomFilter from "anatomy-figures/bloom-filter";
```

## Theme it

Five themes (dark, light, paper, blueprint, sepia), or your own colours through tokens. Every token.

page.tsx

```
<BloomFilter
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
import { define } from "anatomy-figures/element/bloom-filter";

define();

<anatomy-bloom-filter theme="light"></anatomy-bloom-filter>
```

Gradient descentflex-grow

The Creation of Adam, Michelangelo, c. 1512

## Credits

- Figures and text: Ryan (@wheresryan22), Anatomy, MIT
- Page artwork credit: The Creation of Adam, Michelangelo, c. 1512
