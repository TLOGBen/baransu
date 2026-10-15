<!-- Source: https://skills.wheresryan.sh/anatomy/collection/easing | Retrieved: 2026-10-13 | Anatomy by Ryan (@wheresryan22), MIT | extracted verbatim with curl, scripts/styles/SVG stripped -->

# Easing curves

- Source: https://skills.wheresryan.sh/anatomy/collection/easing
- Retrieved: 2026-10-13
- Section: svg
- Breadcrumb: Collection/SVG/Easing curves
- Byline: No. 28 · SVG · Easing bench
- Collection card text: 28 | Easing curves | Easing bench

## Description

A lead screw drives a carriage across a graph board at a constant rate, which is time. A follower rides a steel band bent to the curve and lifts the element to the eased progress.

## Prompt

```
/anatomy explain how easing curves work in CSS animations, interactive
```

## Interaction hints

- Click to run
- drag a handle

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
import { Easing } from "anatomy-figures";

<Easing theme="light" />
```

Or load this figure on its own, so the others never download:

page.tsx

```
import Easing from "anatomy-figures/easing";
```

## Theme it

Five themes (dark, light, paper, blueprint, sepia), or your own colours through tokens. Every token.

page.tsx

```
<Easing
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
import { define } from "anatomy-figures/element/easing";

define();

<anatomy-easing theme="light"></anatomy-easing>
```

Token bucketPublic key

The Creation of Adam, Michelangelo, c. 1512

## Credits

- Figures and text: Ryan (@wheresryan22), Anatomy, MIT
- Page artwork credit: The Creation of Adam, Michelangelo, c. 1512
