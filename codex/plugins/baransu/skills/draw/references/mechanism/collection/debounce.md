<!-- Source: https://skills.wheresryan.sh/anatomy/collection/debounce | Retrieved: 2026-10-13 | Anatomy by Ryan (@wheresryan22), MIT | extracted verbatim with curl, scripts/styles/SVG stripped -->

# Debounce, throttle

- Source: https://skills.wheresryan.sh/anatomy/collection/debounce
- Retrieved: 2026-10-13
- Section: svg
- Breadcrumb: Collection/SVG/Debounce, throttle
- Byline: No. 12 · SVG · Music-box recorder
- Collection card text: 12 | Debounce, throttle | Music-box recorder

## Description

A music-box recorder with a turning pin disc. Every click of the knob is a call; the throttle and debounce dashpots each set their own pins, so you can read when each function actually ran.

## Prompt

```
/anatomy explain debounce versus throttle, interactive
```

## Interaction hints

- Move across to turn the knob

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
import { Debounce } from "anatomy-figures";

<Debounce theme="light" />
```

Or load this figure on its own, so the others never download:

page.tsx

```
import Debounce from "anatomy-figures/debounce";
```

## Theme it

Five themes (dark, light, paper, blueprint, sepia), or your own colours through tokens. Every token.

page.tsx

```
<Debounce
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
import { define } from "anatomy-figures/element/debounce";

define();

<anatomy-debounce theme="light"></anatomy-debounce>
```

B-tree indexMutex

The Creation of Adam, Michelangelo, c. 1512

## Credits

- Figures and text: Ryan (@wheresryan22), Anatomy, MIT
- Page artwork credit: The Creation of Adam, Michelangelo, c. 1512
