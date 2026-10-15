<!-- Source: https://skills.wheresryan.sh/anatomy/collection/mutex | Retrieved: 2026-10-13 | Anatomy by Ryan (@wheresryan22), MIT | extracted verbatim with curl, scripts/styles/SVG stripped -->

# Mutex

- Source: https://skills.wheresryan.sh/anatomy/collection/mutex
- Retrieved: 2026-10-13
- Section: svg
- Breadcrumb: Collection/SVG/Mutex
- Byline: No. 13 · SVG · Tank and key
- Collection card text: 13 | Mutex | Tank and key

## Description

A water tank filled by two pumps. Without the interlock key both controllers read the same level and overfill it; with it, only the one holding the key may read and run.

## Prompt

```
/anatomy explain how a mutex prevents a race condition, interactive
```

## Interaction hints

- Tap a pump
- tap the key

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
import { Mutex } from "anatomy-figures";

<Mutex theme="light" />
```

Or load this figure on its own, so the others never download:

page.tsx

```
import Mutex from "anatomy-figures/mutex";
```

## Theme it

Five themes (dark, light, paper, blueprint, sepia), or your own colours through tokens. Every token.

page.tsx

```
<Mutex
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
import { define } from "anatomy-figures/element/mutex";

define();

<anatomy-mutex theme="light"></anatomy-mutex>
```

Debounce, throttleMerge sort

The Creation of Adam, Michelangelo, c. 1512

## Credits

- Figures and text: Ryan (@wheresryan22), Anatomy, MIT
- Page artwork credit: The Creation of Adam, Michelangelo, c. 1512
