<!-- Source: https://skills.wheresryan.sh/anatomy/collection/watch | Retrieved: 2026-10-13 | Anatomy by Ryan (@wheresryan22), MIT | extracted verbatim with curl, scripts/styles/SVG stripped -->

# Watch movement

- Source: https://skills.wheresryan.sh/anatomy/collection/watch
- Retrieved: 2026-10-13
- Section: svg
- Breadcrumb: Collection/SVG/Watch movement
- Byline: No. 24 · SVG · Automatic movement
- Collection card text: 24 | Watch movement | Automatic movement

## Description

A Swiss automatic movement, 25.6 mm across, in a holder on a bench mat. The balance swings at 4 Hz and the pallet fork lets the escape wheel through half a tooth eight times a second, so the seconds step in eighths.

## Prompt

```
/anatomy explain how a mechanical watch keeps time, interactive
```

## Interaction hints

- Drag crown ↑ to wind
- `S` slow
- `E` apart

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
import { Watch } from "anatomy-figures";

<Watch theme="light" />
```

Or load this figure on its own, so the others never download:

page.tsx

```
import Watch from "anatomy-figures/watch";
```

## Theme it

Five themes (dark, light, paper, blueprint, sepia), or your own colours through tokens. Every token.

page.tsx

```
<Watch
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
import { define } from "anatomy-figures/element/watch";

define();

<anatomy-watch theme="light"></anatomy-watch>
```

Process pumpSeasons

The Creation of Adam, Michelangelo, c. 1512

## Credits

- Figures and text: Ryan (@wheresryan22), Anatomy, MIT
- Page artwork credit: The Creation of Adam, Michelangelo, c. 1512
