<!-- Source: https://skills.wheresryan.sh/anatomy/collection/mark-sweep | Retrieved: 2026-10-13 | Anatomy by Ryan (@wheresryan22), MIT | extracted verbatim with curl, scripts/styles/SVG stripped -->

# Mark and sweep

- Source: https://skills.wheresryan.sh/anatomy/collection/mark-sweep
- Retrieved: 2026-10-13
- Section: svg
- Breadcrumb: Collection/SVG/Mark and sweep
- Byline: No. 10 · SVG · Modular synth
- Collection card text: 10 | Mark and sweep | Modular synth

## Description

A modular synth case standing for the heap. Patch cables are pointers; marking lights every module reachable from the stack, and the sweep pulls the ones left dark.

## Prompt

```
/anatomy explain mark-and-sweep garbage collection, interactive
```

## Interaction hints

- Tap to collect
- cut a cable

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
import { MarkSweep } from "anatomy-figures";

<MarkSweep theme="light" />
```

Or load this figure on its own, so the others never download:

page.tsx

```
import MarkSweep from "anatomy-figures/mark-sweep";
```

## Theme it

Five themes (dark, light, paper, blueprint, sepia), or your own colours through tokens. Every token.

page.tsx

```
<MarkSweep
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
import { define } from "anatomy-figures/element/mark-sweep";

define();

<anatomy-mark-sweep theme="light"></anatomy-mark-sweep>
```

flex-growB-tree index

The Creation of Adam, Michelangelo, c. 1512

## Credits

- Figures and text: Ryan (@wheresryan22), Anatomy, MIT
- Page artwork credit: The Creation of Adam, Michelangelo, c. 1512
