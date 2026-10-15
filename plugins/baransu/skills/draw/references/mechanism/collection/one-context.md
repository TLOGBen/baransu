<!-- Source: https://skills.wheresryan.sh/anatomy/collection/one-context | Retrieved: 2026-10-13 | Anatomy by Ryan (@wheresryan22), MIT | extracted verbatim with curl, scripts/styles/SVG stripped -->

# One context

- Source: https://skills.wheresryan.sh/anatomy/collection/one-context
- Retrieved: 2026-10-13
- Section: early
- Breadcrumb: Collection/Early examples/One context
- Byline: No. 35 · Early example
- Collection card text: 35 | One context

## Description

A plotter with one print head and sixteen tiles: a single WebGL2 context renders each pane in turn, then lowers and stamps its pixels into that pane’s own canvas.

## Note

Drawn while the skill was being made, for a long article on rendering frosted panes in WebGL.

## Prompt

```
(no prompt on page)
```

## Interaction hints

- Hover a tile to send the head

## Readouts (server-rendered)

- head → pane 11 / 16 · copyTo

## Legend keys

- The print head: the one WebGL2 context
- A tile: one pane's own 2D canvas
- Just stamped by copyTo()

## Figure caption

No. 35. A plotter with one print head and 16 tiles. Each tile is a pane’s own 2D canvas, holding one of five shapes `<Glass>` knows at its default size. The head is the WebGL2 context `shared()` makes once, on a canvas that never joins the page; its 16 dots are the 16 stages it keeps, one per pane, seven render targets each. For each pane the head renders, then lowers and stamps: `copyTo()` draws the context’s pixels into that pane’s canvas, and the canvas keeps them until the next stamp. I’ve slowed it down; on a real page every pane that needs a new picture does this in its own frame callback, one after another, inside a single frame.

## Control labels (aria-label)

- Pane the print head serves
- (aria-valuetext) Pane 11 of 16, a circle: the one WebGL2 context renders it, then copyTo() stamps the pixels into the pane's own 2D canvas.
- A gantry plotter. Its bed holds a tray of 16 small tiles, each a pane's own 2D canvas with one piece of glass in it. One print head, the shared WebGL2 context, rides a carriage on a beam over the tray; it moves to one tile at a time, renders, then lowers and stamps the picture in with copyTo().

## Figure labels (SVG text/title)

- webgl2

## Install and usage (verbatim)

## Install

```
npm install anatomy-figures
```

## In your code

page.tsx

```
import { OneContext } from "anatomy-figures";

<OneContext theme="light" />
```

Or load this figure on its own, so the others never download:

page.tsx

```
import OneContext from "anatomy-figures/one-context";
```

## Theme it

Early examples keep their own light and dark palettes: theme picks one, and --anatomy-card sets the ground.

page.tsx

```
<OneContext
  theme="dark"
  tokens={{ "--anatomy-card": "#000000" }}
/>
```

## Without React

It still draws with React inside, so install react and react-dom next to it.

index.html

```
import { define } from "anatomy-figures/element/one-context";

define();

<anatomy-one-context theme="light"></anatomy-one-context>
```

One paneShared canvas

The Creation of Adam, Michelangelo, c. 1512

## Credits

- Figures and text: Ryan (@wheresryan22), Anatomy, MIT
- Page artwork credit: The Creation of Adam, Michelangelo, c. 1512
