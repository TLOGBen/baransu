<!-- Source: https://skills.wheresryan.sh/anatomy/collection/field-key | Retrieved: 2026-10-13 | Anatomy by Ryan (@wheresryan22), MIT | extracted verbatim with curl, scripts/styles/SVG stripped -->

# Field key

- Source: https://skills.wheresryan.sh/anatomy/collection/field-key
- Retrieved: 2026-10-13
- Section: early
- Breadcrumb: Collection/Early examples/Field key
- Byline: No. 41 · Early example
- Collection card text: 41 | Field key

## Description

A pin-tumbler lock cut open. The key has one cut per shape setting, and the cache only opens when every cut still matches the last frame’s.

## Note

Drawn while the skill was being made, for a long article on rendering frosted panes in WebGL.

## Prompt

```
(no prompt on page)
```

## Interaction hints

- Hover a part of the key [pointer] [touch: Tap a part of the key]

## Readouts (server-rendered)

- key matches · 0 draws

## Legend keys

- The lock: the key the stage kept
- Shear line: compared here
- Drawn this frame

## Figure caption

No. 41. `fieldKey` for a default pill in a 400 × 250 box, as a pin-tumbler lock cut open. The key is the one I build this frame: eight cuts, one for each part in the order they are joined with `|`, from width at the tip to power at the bow. The lock is pinned to the key the stage kept. When every cut matches, every pin meets the shear line and the plug turns: the pass returns and nothing is drawn. Hover a part to change it by one. Its pin stands proud, the lock jams, and the stage keeps the new key and draws all four shape targets again, 1 + 1 + 16 + 16 = 34 draws, counted off on the plate in front. One part is enough, and two cost no more.

## Control labels (aria-label)

- Change one part of the field key
- (aria-valuetext) Every cut matches the lock the stage kept: the plug turns and nothing is drawn
- A pin-tumbler lock cut open and clamped on a plinth. Its key has eight cuts, one for each part of the field key; eight pin stacks rest on them. A plate in front holds 34 holes, one for each draw a new key costs.

## Figure labels (SVG text/title)

- fieldKey

## Install and usage (verbatim)

## Install

```
npm install anatomy-figures
```

## In your code

page.tsx

```
import { FieldKey } from "anatomy-figures";

<FieldKey theme="light" />
```

Or load this figure on its own, so the others never download:

page.tsx

```
import FieldKey from "anatomy-figures/field-key";
```

## Theme it

Early examples keep their own light and dark palettes: theme picks one, and --anatomy-card sets the ground.

page.tsx

```
<FieldKey
  theme="dark"
  tokens={{ "--anatomy-card": "#000000" }}
/>
```

## Without React

It still draws with React inside, so install react and react-dom next to it.

index.html

```
import { define } from "anatomy-figures/element/field-key";

define();

<anatomy-field-key theme="light"></anatomy-field-key>
```

Separable blurFour frames

The Creation of Adam, Michelangelo, c. 1512

## Credits

- Figures and text: Ryan (@wheresryan22), Anatomy, MIT
- Page artwork credit: The Creation of Adam, Michelangelo, c. 1512
