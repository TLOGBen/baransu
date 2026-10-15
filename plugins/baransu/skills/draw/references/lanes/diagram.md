# Diagram lane — the route through the vendored diagram system

The vendored diagram system under `references/diagram/` is the authority; this chapter is /draw's route through it and the places where /draw decides what the upstream text would ask. It applies to the diagram form with the diagram-system approach, to a component that *is* a diagram, and to a seek overlay. The steps are in `SKILL.md` § Lane: diagram; each runs after its step command (`lookup.py --step <id>`), which prints the topics it needs.

## Philosophy

The highest-quality move is deletion. Every node is a distinct idea; every connection carries information; the accent goes on 1–2 focal elements; target density is 4/10; above 9 nodes it is two diagrams. The upstream question still applies — *would a well-written paragraph or a 3-column table do the same job?* If yes, build the visual anyway and put that note, with the table, under 附註 in the completion report.

## Selection

When behaviour, state, enforcement or risk carries the meaning, pick one semantic pattern from `references/diagram/semantic-patterns.md` first, then the nearest visual type; otherwise pick the type from the table in `references/diagram/README.md` § Visual types. Look up the chosen type reference (`type-<name>`) before laying out, every time: its composition, budget and verifier are the rules for this diagram.

## Design system and skin

Tokens and typography come from `references/diagram/style-guide.md`: a warm-neutral paper, one accent, a serif title, sans names and mono technical sublabels; CJK labels extend the family and keep a 12 px floor.

- **Default skin.** Keep the shipped default skin (or a saved profile). Branding is never a question.
- **A named brand.** Only when the user names a brand or points at a brand source (a URL, a token set, a folder, an installed skill's token file, or `/ui`'s `.claude/design/reference-<slug>.md`), use the extraction and mapping steps in `references/diagram/onboarding.md`, and decide every choice it would ask about yourself: the accent candidate, the dark and light defaults, the slug from the brand name. Log each choice in `docs/skin.md`.
- **Scope.** The skin applies to this run's output only; the installed `style-guide.md` is never edited. Save the profile per `references/diagram/profiles.md` without a confirmation step. Write the project marker only when the user asked for it (`references/diagram/README.md` § Overrides has the full list of upstream prompts /draw decides).

## Templates are the design-system skeleton

`assets/diagram/template.html` (and `-dark`, `-full`, `-motion`, `-terminal`, `-seek`) carry the design system: the tokens, the type and, for the diagram form, the frame around the SVG. The template is the skeleton and the token reference, not a picture to fill in:

- **Diagram form.** Start the file from the template's skeleton (tokens, type, eyebrow and h1 frame) and write the SVG body new.
- **Component.** Take the template's tokens and type into `<name>.html`, which follows the component contract (`references/motion/component.md`): no eyebrow, h1 or page frame.
- **Either way** the SVG body's composition — what the nodes are, where they sit, how connectors run — comes from the chosen type reference (`type-<name>`) and `docs/layout.md`, never from the template or an `example-*.html`; an example shows what a finished diagram of that type looks like, not what this one must look like.

## Markup

- Name the file for its subject: `<slug>.html` in the output folder, with exports `<slug>.svg` / `<slug>.png` beside it; never a generic `index` name.
- Fill `<title>` and `<desc>` with slug-prefixed ids (`references/diagram/output-spec.md` has the accessible-SVG contract).
- Exact primitives and the six connector rules: `references/diagram/primitives-core.md`. Orthogonal elbows only; masked labels with a visible gap; no overlaps; fan attach points; no transit behind a non-endpoint box; the mask is drawn before the node.
- Draw arrows before boxes. The legend is a bottom strip.
- Every coordinate is on the 4 px grid (`references/diagram/layout-budget.md`); type sizes come from the ramp in `output-spec.md` for the chosen size preset.

## Sizes, dials and imports

`references/diagram/output-spec.md` sets the four dials: format (`html` / `svg` / `png`), size preset (`doc-inline` by default, up to `slide-16x9`, `social-og` and print), detail level, audience. An import (`import-mermaid.md`, `import-drawio.md`, `import-excalidraw.md`) extracts with `scripts/diagram/<format>_extract.py`, sets the four dials, redraws (never converts), and reports the fidelity ledger in `docs/fidelity_ledger.md`.

## Motion: reveal, step, loop, or a seek overlay

Motion is added when the user asks for it or when the order genuinely needs it.

- **Reveal / step / loop** — the upstream modes in `references/diagram/animation.md`, for a short ordered explanation. The controller is copied verbatim from `assets/diagram/template-motion.html`.
- **Seek overlay** — `references/diagram/seek-overlay.md`, from `assets/diagram/template-seek.html`, when the viewer should scrub a token travelling the real connectors while nodes light up in order. It is the same `window.seek(t)` contract as a film, so `scripts/motion/render.mjs` can export it as video. It ships with its static twin: `scripts/diagram/seek_split.py` writes the twin and runs `self_check.py` on it.

Either way the static frame is complete without JavaScript and under reduced motion.

## Checks

`python3 scripts/diagram/self_check.py <file>` must pass. The type reference may name a stricter verifier under `scripts/diagram/repo/` (`verify-geometry.py`, `verify-motion.py`, `lint-skin.py`, a per-type `verify-*.py`); each one it names must pass too. Then look in a browser: `node scripts/motion/verify-page.mjs <file> --selector svg`. Then run `references/diagram/taste-gate.md` — the universal anti-patterns, the remove test, the signal test, the technical and typography rows — on the finished file; one failing row is a fix and a rerun.

## Export

PNG or SVG only when the user asks: `references/diagram/export.md` and `scripts/diagram/export_svg.py`. The file to export is the one this run built; a missing export tool is installed, not reported.
