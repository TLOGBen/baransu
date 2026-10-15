<!-- Source: https://skills.wheresryan.sh/anatomy/collection/tcp-handshake | Retrieved: 2026-10-13 | Anatomy by Ryan (@wheresryan22), MIT | extracted verbatim with curl, scripts/styles/SVG stripped -->

# TCP handshake

- Source: https://skills.wheresryan.sh/anatomy/collection/tcp-handshake
- Retrieved: 2026-10-13
- Section: svg
- Breadcrumb: Collection/SVG/TCP handshake
- Byline: No. 06 · SVG · Mail ropeway
- Collection card text: 06 | TCP handshake | Mail ropeway

## Description

A mail ropeway between two stations. Canisters flying SYN, SYN with an ACK pennant, then ACK ride the rope across, and each station's semaphore shows its connection state.

## Prompt

```
/anatomy explain the TCP three-way handshake, interactive
```

## Interaction hints

- Tap to connect
- hut to drop

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
import { TcpHandshake } from "anatomy-figures";

<TcpHandshake theme="light" />
```

Or load this figure on its own, so the others never download:

page.tsx

```
import TcpHandshake from "anatomy-figures/tcp-handshake";
```

## Theme it

Five themes (dark, light, paper, blueprint, sepia), or your own colours through tokens. Every token.

page.tsx

```
<TcpHandshake
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
import { define } from "anatomy-figures/element/tcp-handshake";

define();

<anatomy-tcp-handshake theme="light"></anatomy-tcp-handshake>
```

LRU cacheGradient descent

The Creation of Adam, Michelangelo, c. 1512

## Credits

- Figures and text: Ryan (@wheresryan22), Anatomy, MIT
- Page artwork credit: The Creation of Adam, Michelangelo, c. 1512
