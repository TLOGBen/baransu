<!-- Source: https://skills.wheresryan.sh/anatomy/collection/dns | Retrieved: 2026-10-13 | Anatomy by Ryan (@wheresryan22), MIT | extracted verbatim with curl, scripts/styles/SVG stripped -->

# DNS resolution

- Source: https://skills.wheresryan.sh/anatomy/collection/dns
- Retrieved: 2026-10-13
- Section: svg
- Breadcrumb: Collection/SVG/DNS resolution
- Byline: No. 03 · SVG · Pneumatic tubes
- Collection card text: 03 | DNS resolution | Pneumatic tubes

## Description

A pneumatic tube dispatcher. The resolver sends a capsule up each server's tube, root, com, then example.com, each as long as its round trip, and every reply raises a flag in a cache rack until its time to live runs out.

## Prompt

```
/anatomy explain how DNS resolves a domain name, interactive
```

## Interaction hints

- Tap to look up
- `←→`

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
import { Dns } from "anatomy-figures";

<Dns theme="light" />
```

Or load this figure on its own, so the others never download:

page.tsx

```
import Dns from "anatomy-figures/dns";
```

## Theme it

Five themes (dark, light, paper, blueprint, sepia), or your own colours through tokens. Every token.

page.tsx

```
<Dns
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
import { define } from "anatomy-figures/element/dns";

define();

<anatomy-dns theme="light"></anatomy-dns>
```

Binary searchMessage queue

The Creation of Adam, Michelangelo, c. 1512

## Credits

- Figures and text: Ryan (@wheresryan22), Anatomy, MIT
- Page artwork credit: The Creation of Adam, Michelangelo, c. 1512
