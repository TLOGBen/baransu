<!-- Source: https://skills.wheresryan.sh/anatomy/collection/git-merge | Retrieved: 2026-10-13 | Anatomy by Ryan (@wheresryan22), MIT | extracted verbatim with curl, scripts/styles/SVG stripped -->

# Branch and merge

- Source: https://skills.wheresryan.sh/anatomy/collection/git-merge
- Retrieved: 2026-10-13
- Section: svg
- Breadcrumb: Collection/SVG/Branch and merge
- Byline: No. 32 · SVG · Model railway
- Collection card text: 32 | Branch and merge | Model railway

## Description

A model railway on a baseboard. Each commit is a station with one stud per parent; committing lays track, and a merge joins feature's line back into main.

## Prompt

```
/anatomy explain how git branches and merges, interactive
```

## Interaction hints

- Drag to commit
- tap to merge

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
import { GitMerge } from "anatomy-figures";

<GitMerge theme="light" />
```

Or load this figure on its own, so the others never download:

page.tsx

```
import GitMerge from "anatomy-figures/git-merge";
```

## Theme it

Five themes (dark, light, paper, blueprint, sepia), or your own colours through tokens. Every token.

page.tsx

```
<GitMerge
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
import { define } from "anatomy-figures/element/git-merge";

define();

<anatomy-git-merge theme="light"></anatomy-git-merge>
```

Box modelPool reactor

The Creation of Adam, Michelangelo, c. 1512

## Credits

- Figures and text: Ryan (@wheresryan22), Anatomy, MIT
- Page artwork credit: The Creation of Adam, Michelangelo, c. 1512
