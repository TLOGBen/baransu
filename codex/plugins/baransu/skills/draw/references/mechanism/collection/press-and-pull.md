<!-- Source: https://skills.wheresryan.sh/anatomy/collection/press-and-pull | Retrieved: 2026-10-13 | Anatomy by Ryan (@wheresryan22), MIT | extracted verbatim with curl, scripts/styles/SVG stripped -->

# Press and pull

- Source: https://skills.wheresryan.sh/anatomy/collection/press-and-pull
- Retrieved: 2026-10-13
- Section: early
- Breadcrumb: Collection/Early examples/Press and pull
- Byline: No. 51 · Early example
- Collection card text: 51 | Press and pull

## Description

A glass button that swells when pressed and leans toward the finger like a rubber band, stretching along the lean and staying a capsule.

## Note

Drawn while the skill was being made, for a long article on rendering frosted panes in WebGL.

## Prompt

```
(no prompt on page)
```

## Interaction hints

- Press, then pull ← →

## Readouts (server-rendered)

- 120.0 × 32.0 · lean 0.0 px

## Control labels (aria-label)

- Glass button on a test rig: Space presses or lets go, arrow keys move the finger and pull
- (aria-valuetext) At rest: 120.0 by 32.0 pixels, pulled 0.0 px, leaning 0.0 px
- A test rig for a glass button. A 120 × 32 capsule of glass sits on a carriage that slides on two guide rods inside a frame, held at rest by four coil springs, two at each end. A finger probe hangs from a carriage on a rail behind it: it comes down to press the glass, which swells, then slides along the rail to pull, and the glass leans after it, giving less the further it goes. A dial gauge at the end of the frame reads the lean. Let go and the springs bring it back, once past rest.

## Figure labels (SVG text/title)

- px

## Install and usage (verbatim)

## Install

```
npm install anatomy-figures
```

## In your code

page.tsx

```
import { PressAndPull } from "anatomy-figures";

<PressAndPull theme="light" />
```

Or load this figure on its own, so the others never download:

page.tsx

```
import PressAndPull from "anatomy-figures/press-and-pull";
```

## Theme it

Early examples keep their own light and dark palettes: theme picks one, and --anatomy-card sets the ground.

page.tsx

```
<PressAndPull
  theme="dark"
  tokens={{ "--anatomy-card": "#000000" }}
/>
```

## Without React

It still draws with React inside, so install react and react-dom next to it.

index.html

```
import { define } from "anatomy-figures/element/press-and-pull";

define();

<anatomy-press-and-pull theme="light"></anatomy-press-and-pull>
```

Lit by facingThree reads

The Creation of Adam, Michelangelo, c. 1512

## Credits

- Figures and text: Ryan (@wheresryan22), Anatomy, MIT
- Page artwork credit: The Creation of Adam, Michelangelo, c. 1512
