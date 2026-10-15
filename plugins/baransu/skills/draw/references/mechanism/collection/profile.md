<!-- Source: https://skills.wheresryan.sh/anatomy/collection/profile | Retrieved: 2026-10-13 | Anatomy by Ryan (@wheresryan22), MIT | extracted verbatim with curl, scripts/styles/SVG stripped -->

# Profile

- Source: https://skills.wheresryan.sh/anatomy/collection/profile
- Retrieved: 2026-10-13
- Section: early
- Breadcrumb: Collection/Early examples/Profile
- Byline: No. 44 · Early example
- Collection card text: 44 | Profile

## Description

A slice through the edge of a clear pane, to scale, with a profile gauge whose forty spring pins press against the eased bevel.

## Note

Drawn while the skill was being made, for a long article on rendering frosted panes in WebGL.

## Prompt

```
(no prompt on page)
```

## Interaction hints

- Hover a pin · click to set the gauge [pointer] [touch: Tap a pin to read it]

## Readouts (server-rendered)

- 46 px thick · falls 19 px at the rim

## Legend keys

- A pin, one per pixel, resting on the glass
- The pin I'm reading
- Where the bezel starts

## Figure caption

No. 44. A slice through the edge of a clear pane, standing on a bench with its cut face up, to scale: 46 px thick, and the last 26 px are the bezel. A profile gauge rides in on two rails and presses forty spring pins against it, one per pixel, each stopping where the glass is. That is the height the slope adds up to. Across the middle the pins stand level; over the bezel they give way, slowly at first and then fast, and the caliper on the right finds the rim 26.8 px high, about 19 below the middle. The shader never builds this shape; the gauge is only how I show it.

## Control labels (aria-label)

- Read one pin of the profile gauge
- (aria-valuetext) No pin picked. The gauge is set: 46 pixels thick, falling about 19 pixels at the rim.
- A slice through the edge of a clear pane, 46 pixels thick, standing on a bench with its cut face up. A profile gauge with forty pins, one per pixel, is pressed against it: the pins stand level across the flat middle and step back over the 26 pixel bezel, slowly and then fast. A caliper finds the rim 26.8 pixels high, about 19 pixels below the middle.

## Figure labels (SVG text/title)

- clear · 46 px

## Install and usage (verbatim)

## Install

```
npm install anatomy-figures
```

## In your code

page.tsx

```
import { Profile } from "anatomy-figures";

<Profile theme="light" />
```

Or load this figure on its own, so the others never download:

page.tsx

```
import Profile from "anatomy-figures/profile";
```

## Theme it

Early examples keep their own light and dark palettes: theme picks one, and --anatomy-card sets the ground.

page.tsx

```
<Profile
  theme="dark"
  tokens={{ "--anatomy-card": "#000000" }}
/>
```

## Without React

It still draws with React inside, so install react and react-dom next to it.

index.html

```
import { define } from "anatomy-figures/element/profile";

define();

<anatomy-profile theme="light"></anatomy-profile>
```

LookupDispersion

The Creation of Adam, Michelangelo, c. 1512

## Credits

- Figures and text: Ryan (@wheresryan22), Anatomy, MIT
- Page artwork credit: The Creation of Adam, Michelangelo, c. 1512
