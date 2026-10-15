<!-- Source: https://skills.wheresryan.sh/anatomy/collection/message-queue | Retrieved: 2026-10-13 | Anatomy by Ryan (@wheresryan22), MIT | extracted verbatim with curl, scripts/styles/SVG stripped -->

# Message queue

- Source: https://skills.wheresryan.sh/anatomy/collection/message-queue
- Retrieved: 2026-10-13
- Section: svg
- Breadcrumb: Collection/SVG/Message queue
- Byline: No. 04 · SVG · Marble run
- Collection card text: 04 | Message queue | Marble run

## Description

A marble run. Two hoppers produce marbles into one sloping lane, the queue, where they wait in order behind an escapement, and three timer drums consume them one at a time.

## Prompt

```
/anatomy explain a message queue with producers and consumers, interactive
```

## Interaction hints

- Drag to set rate
- tap a drum

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
import { MessageQueue } from "anatomy-figures";

<MessageQueue theme="light" />
```

Or load this figure on its own, so the others never download:

page.tsx

```
import MessageQueue from "anatomy-figures/message-queue";
```

## Theme it

Five themes (dark, light, paper, blueprint, sepia), or your own colours through tokens. Every token.

page.tsx

```
<MessageQueue
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
import { define } from "anatomy-figures/element/message-queue";

define();

<anatomy-message-queue theme="light"></anatomy-message-queue>
```

DNS resolutionLRU cache

The Creation of Adam, Michelangelo, c. 1512

## Credits

- Figures and text: Ryan (@wheresryan22), Anatomy, MIT
- Page artwork credit: The Creation of Adam, Michelangelo, c. 1512
