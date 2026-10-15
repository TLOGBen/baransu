<!-- Source: https://skills.wheresryan.sh/anatomy/collection/hash-map | Retrieved: 2026-10-13 | Anatomy by Ryan (@wheresryan22), MIT | extracted verbatim with curl, scripts/styles/SVG stripped -->

# Hash map collisions

- Source: https://skills.wheresryan.sh/anatomy/collection/hash-map
- Retrieved: 2026-10-13
- Section: svg
- Breadcrumb: Collection/SVG/Hash map collisions
- Byline: No. 01 · SVG · Sorting desk
- Collection card text: 01 | Hash map collisions | Sorting desk

## Description

A post-office sorting desk. A coding machine prints each letter's bucket, the hash of its name mod 8, and files it in that pigeonhole, on top of any letters already there.

## Prompt

```
/anatomy explain how a hash map handles collisions, interactive
```

## Interaction hints

- Tap to file
- hover a bucket

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
import { HashMap } from "anatomy-figures";

<HashMap theme="light" />
```

Or load this figure on its own, so the others never download:

page.tsx

```
import HashMap from "anatomy-figures/hash-map";
```

## Theme it

Five themes (dark, light, paper, blueprint, sepia), or your own colours through tokens. Every token.

page.tsx

```
<HashMap
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
import { define } from "anatomy-figures/element/hash-map";

define();

<anatomy-hash-map theme="light"></anatomy-hash-map>
```

Three readsBinary search

The Creation of Adam, Michelangelo, c. 1512

## Credits

- Figures and text: Ryan (@wheresryan22), Anatomy, MIT
- Page artwork credit: The Creation of Adam, Michelangelo, c. 1512
