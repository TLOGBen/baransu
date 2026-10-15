<!-- Source: https://skills.wheresryan.sh/anatomy/collection/studio | Retrieved: 2026-10-13 | Anatomy by Ryan (@wheresryan22), MIT | extracted verbatim with curl, scripts/styles/SVG stripped -->

# Rim light

- Source: https://skills.wheresryan.sh/anatomy/collection/studio
- Retrieved: 2026-10-13
- Section: early
- Breadcrumb: Collection/Early examples/Rim light
- Byline: No. 46 · Early example
- Collection card text: 46 | Rim light

## Description

A small studio with a pill-shaped control on a turntable, a key lamp and a fill on a dimmer, lighting its rim by how squarely each point faces them.

## Note

Drawn while the skill was being made, for a long article on rendering frosted panes in WebGL.

## Prompt

```
(no prompt on page)
```

## Interaction hints

- Point to turn the table [pointer] [touch: Drag to turn the table]

## Readouts (server-rendered)

- turned 20° · key (−0.6, −0.8) · fill 0.5

## Legend keys

- The rim at full: the edge faces the key
- The rim, as bright as each edge’s facing
- Where each lamp’s light lands

## Figure caption

No. 46. A small studio with a pill-shaped control on a turntable. The key lamp stands at the top left, along `(−0.6, −0.8)` on screen, and the fill stands opposite, its knob on the dimmer at half. The stroke round the rim is as bright as each edge’s facing: full where the edge faces the key, half where it faces the fill, and only a trace at the two points where it runs along the light, from the 0.03 of glow every edge keeps. The line fades over the first 1.5 px inside the edge, and where the rim is brightest the `b⁶` glow lifts the last few pixels with it. Turn the table and the bright arc stays where it is: the light is fixed on the screen, not on the pane. This pill is a control, so its rim is 0.42; a clear pane uses 0.16.

## Control labels (aria-label)

- Turn of the table under the pill
- (aria-valuetext) Turned 20 degrees. The bright arc stays on the edge that faces the key at the top left, the opposite edge takes the half-strength fill, and the two points where the edge runs along the light keep only a trace.
- A small photo studio. A pill-shaped glass control sits on a turntable in the middle of a round stage, in front of a paper backdrop. A tall key lamp with barn doors stands at the top left of the screen and a smaller fill lamp opposite, both wired to a dimmer whose key knob is at full and fill knob at half. The stroke round the pill's rim is brightest on the edge facing the key, half as bright on the edge facing the fill, and nearly dark at the two points between. As the table turns, the bright arc stays facing the key.

## Figure labels (SVG text/title)

- rim 0.42

## Install and usage (verbatim)

## Install

```
npm install anatomy-figures
```

## In your code

page.tsx

```
import { Studio } from "anatomy-figures";

<Studio theme="light" />
```

Or load this figure on its own, so the others never download:

page.tsx

```
import Studio from "anatomy-figures/studio";
```

## Theme it

Early examples keep their own light and dark palettes: theme picks one, and --anatomy-card sets the ground.

page.tsx

```
<Studio
  theme="dark"
  tokens={{ "--anatomy-card": "#000000" }}
/>
```

## Without React

It still draws with React inside, so install react and react-dom next to it.

index.html

```
import { define } from "anatomy-figures/element/studio";

define();

<anatomy-studio theme="light"></anatomy-studio>
```

DispersionFrosted copy

The Creation of Adam, Michelangelo, c. 1512

## Credits

- Figures and text: Ryan (@wheresryan22), Anatomy, MIT
- Page artwork credit: The Creation of Adam, Michelangelo, c. 1512
