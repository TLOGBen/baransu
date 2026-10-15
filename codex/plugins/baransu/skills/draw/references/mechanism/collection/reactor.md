<!-- Source: https://skills.wheresryan.sh/anatomy/collection/reactor | Retrieved: 2026-10-13 | Anatomy by Ryan (@wheresryan22), MIT | extracted verbatim with curl, scripts/styles/SVG stripped -->

# Pool reactor

- Source: https://skills.wheresryan.sh/anatomy/collection/reactor
- Retrieved: 2026-10-13
- Section: webgl
- Breadcrumb: Collection/WebGL/Pool reactor
- Byline: No. 33 · WebGL · TRIGA reactor
- Collection card text: 33 | Pool reactor | TRIGA reactor

## Description

A TRIGA research reactor in half section, its core at the bottom of a 6.4 m water tank. Pull the rods and the power climbs; scram and they drop.

## Prompt

```
/anatomy explain how a nuclear research reactor is controlled, interactive
```

## Interaction hints

- Drag rods ↕
- `P` pulse
- `S` scram
- `A` auto

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
import { Reactor } from "anatomy-figures";

<Reactor theme="light" />
```

Or load this figure on its own, so the others never download:

page.tsx

```
import Reactor from "anatomy-figures/reactor";
```

## Theme it

Five themes (dark, light, paper, blueprint, sepia), or your own colours through tokens. Every token.

page.tsx

```
<Reactor
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
import { define } from "anatomy-figures/element/reactor";

define();

<anatomy-reactor theme="light"></anatomy-reactor>
```

Branch and mergeOne pane

The Creation of Adam, Michelangelo, c. 1512

## Credits

- Figures and text: Ryan (@wheresryan22), Anatomy, MIT
- Page artwork credit: The Creation of Adam, Michelangelo, c. 1512
