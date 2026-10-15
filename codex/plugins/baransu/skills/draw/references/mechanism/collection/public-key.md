<!-- Source: https://skills.wheresryan.sh/anatomy/collection/public-key | Retrieved: 2026-10-13 | Anatomy by Ryan (@wheresryan22), MIT | extracted verbatim with curl, scripts/styles/SVG stripped -->

# Public key

- Source: https://skills.wheresryan.sh/anatomy/collection/public-key
- Retrieved: 2026-10-13
- Section: svg
- Breadcrumb: Collection/SVG/Public key
- Byline: No. 29 · SVG · Two-key strongbox
- Collection card text: 29 | Public key | Two-key strongbox

## Description

A steel strongbox with a lock in its lid. Any of the three public keys turns it to seal the box; only the one private key turns it back.

## Prompt

```
/anatomy explain public key encryption, interactive
```

## Interaction hints

- Drag to turn
- tap a key

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
import { PublicKey } from "anatomy-figures";

<PublicKey theme="light" />
```

Or load this figure on its own, so the others never download:

page.tsx

```
import PublicKey from "anatomy-figures/public-key";
```

## Theme it

Five themes (dark, light, paper, blueprint, sepia), or your own colours through tokens. Every token.

page.tsx

```
<PublicKey
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
import { define } from "anatomy-figures/element/public-key";

define();

<anatomy-public-key theme="light"></anatomy-public-key>
```

Easing curvesPouring steel

The Creation of Adam, Michelangelo, c. 1512

## Credits

- Figures and text: Ryan (@wheresryan22), Anatomy, MIT
- Page artwork credit: The Creation of Adam, Michelangelo, c. 1512
