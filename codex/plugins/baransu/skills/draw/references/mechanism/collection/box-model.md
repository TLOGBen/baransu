<!-- Source: https://skills.wheresryan.sh/anatomy/collection/box-model | Retrieved: 2026-10-13 | Anatomy by Ryan (@wheresryan22), MIT | extracted verbatim with curl, scripts/styles/SVG stripped -->

# Box model

- Source: https://skills.wheresryan.sh/anatomy/collection/box-model
- Retrieved: 2026-10-13
- Section: svg
- Breadcrumb: Collection/SVG/Box model
- Byline: No. 31 · SVG · Frame jig
- Collection card text: 31 | Box model | Frame jig

## Description

A picture-frame jig: content, padding, border and margin are its nested frames. Drag the width and switch box-sizing to see which of them gives way.

## Prompt

```
/anatomy explain the CSS box model, interactive
```

## Interaction hints

- Drag width
- click box-sizing

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
import { BoxModel } from "anatomy-figures";

<BoxModel theme="light" />
```

Or load this figure on its own, so the others never download:

page.tsx

```
import BoxModel from "anatomy-figures/box-model";
```

## Theme it

Five themes (dark, light, paper, blueprint, sepia), or your own colours through tokens. Every token.

page.tsx

```
<BoxModel
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
import { define } from "anatomy-figures/element/box-model";

define();

<anatomy-box-model theme="light"></anatomy-box-model>
```

Pouring steelBranch and merge

The Creation of Adam, Michelangelo, c. 1512

## Credits

- Figures and text: Ryan (@wheresryan22), Anatomy, MIT
- Page artwork credit: The Creation of Adam, Michelangelo, c. 1512
