<!-- Source: https://skills.wheresryan.sh/anatomy/collection/rate-limiter | Retrieved: 2026-10-13 | Anatomy by Ryan (@wheresryan22), MIT | extracted verbatim with curl, scripts/styles/SVG stripped -->

# Token bucket

- Source: https://skills.wheresryan.sh/anatomy/collection/rate-limiter
- Retrieved: 2026-10-13
- Section: svg
- Breadcrumb: Collection/SVG/Token bucket
- Byline: No. 27 · SVG · Air bench
- Collection card text: 27 | Token bucket | Air bench

## Description

A pump fills a tank at two tokens a second and a relief valve vents past eight. Each press spends a token to punch a paper tape; with none left, an interlock holds the press shut.

## Prompt

```
/anatomy explain a token bucket rate limiter, interactive
```

## Interaction hints

- Hold to punch
- hover the tape

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
import { RateLimiter } from "anatomy-figures";

<RateLimiter theme="light" />
```

Or load this figure on its own, so the others never download:

page.tsx

```
import RateLimiter from "anatomy-figures/rate-limiter";
```

## Theme it

Five themes (dark, light, paper, blueprint, sepia), or your own colours through tokens. Every token.

page.tsx

```
<RateLimiter
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
import { define } from "anatomy-figures/element/rate-limiter";

define();

<anatomy-rate-limiter theme="light"></anatomy-rate-limiter>
```

Desk computerEasing curves

The Creation of Adam, Michelangelo, c. 1512

## Credits

- Figures and text: Ryan (@wheresryan22), Anatomy, MIT
- Page artwork credit: The Creation of Adam, Michelangelo, c. 1512
