# Diagram lane — vendored from cathrynlavery/diagram-design (MIT, v2.6)

Editorial diagrams as self-contained HTML + inline SVG: 44 visual types, 9 semantic patterns, a skinnable design system, optional accessible motion, and draw.io / Mermaid / Excalidraw import. Everything the upstream skill ships is here, unchanged except for path rewrites (recorded in `../../NOTICE.md`). This file is the index; read the file a row points at only when its trigger applies.

## Read order for one diagram

1. `style-guide.md` — the tokens, typography and node treatments every diagram draws from. The skin is the shipped default unless the user supplies a brand; then follow `onboarding.md` or `profiles.md`.
2. The type reference from the table below (always, before drawing).
3. `primitives-core.md` — exact markup for background, markers, node box, arrow label, legend, and the long form of the six connector rules.
4. `layout-budget.md` — the 4 px grid, allowed values, per-type complexity limits, the summary-card pattern.
5. `output-spec.md` — format × size × detail × audience dials and the type ramp per size preset (also required for any import).
6. When behaviour carries the meaning: `semantic-patterns.md` first, then the nearest type.
7. When motion is requested: `animation.md` (reveal / step / loop; copy the controller from `../../assets/diagram/template-motion.html` verbatim), or `seek-overlay.md` when the reader should scrub a token through the diagram (start from `../../assets/diagram/template-seek.html`; `scripts/diagram/seek_split.py` gates the static twin).

Templates: `../../assets/diagram/template.html` (minimal light), `template-dark.html`, `template-full.html` (editorial card), `template-motion.html`, `template-terminal.html`. Every type has `example-<type>.html`, `-dark`, `-full` and, where motion is sanctioned, `-animated` examples beside them; `index.html` flips through all of them, `icons.html` is the icon gallery.

## Visual types

| Showing… | Type | Reference |
|---|---|---|
| Components + connections in one snapshot | Architecture | `type-architecture.md` |
| Before / Changes / After topology | Architecture delta | `type-architecture-delta.md` |
| Legacy landscape by phase or department | IT current-state | `type-it-state.md` |
| Decision logic with branches | Flowchart | `type-flowchart.md` |
| Time-ordered messages between actors | Sequence | `type-sequence.md` |
| States + transitions + guards | State machine | `type-state.md` |
| Entities + fields + relationships | ER / data model | `type-er.md` |
| Events positioned in time | Timeline | `type-timeline.md` |
| Cross-functional process with handoffs | Swimlane | `type-swimlane.md` |
| Two-axis positioning | Quadrant | `type-quadrant.md` |
| Entities scored across 3–5 criteria | Radar | `type-radar.md` |
| One series across cyclic categories | Polar | `type-polar.md` |
| Reinforcing cycle with a hub | Loop / flywheel | `type-loop.md` |
| Hierarchy by containment | Nested | `type-nested.md` |
| Parent → children | Tree | `type-tree.md` |
| Ownership, routing, escalation | Org chart | `type-org-chart.md` |
| Stacked abstraction levels | Layer stack | `type-layers.md` |
| Parts pulled apart on one axis | Exploded axonometric | `type-exploded.md` |
| A floor or site from above at an angle | Axonometric plan | `type-axonometric-plan.md` |
| Overlap between sets | Venn | `type-venn.md` |
| Ranked hierarchy or drop-off | Pyramid / funnel | `type-pyramid.md` |
| Categorical comparison (incl. dumbbell) | Bar | `type-bar.md` |
| Running total bridged by signed steps | Waterfall | `type-waterfall.md` |
| Part-of-whole by area (incl. marimekko) | Treemap | `type-treemap.md` |
| Value per row × column | Heatmap | `type-heatmap.md` |
| Trends over time (slopegraph, ridgeline, streamgraph, bump) | Line | `type-line.md` |
| Tasks and phases on a timeline | Gantt | `type-gantt.md` |
| Two variables (bubble, beeswarm) | Scatter | `type-scatter.md` |
| End-to-end stack on a cluster | High-level | `type-high-level.md` |
| Multi-actor sequential process with data handoffs | Process | `type-process.md` |
| Tiered data storage | Medallion | `type-medallion.md` |
| Role-scoped pipeline steps | Data flow | `type-data-flow.md` |
| Sources → core → consumers | DP integration | `type-dp-integration.md` |
| Per-role access permissions | DP security matrix | `type-dp-security-matrix.md` |
| Quantities that split and merge | Sankey | `type-sankey.md` |
| Grouped causes → one effect | Fishbone | `type-fishbone.md` |
| Value chain × evolution | Wardley map | `type-wardley.md` |
| Work in progress by state | Kanban | `type-kanban.md` |
| Stages, actions, sentiment | User journey | `type-journey.md` |
| Zones, hosts, artifacts | Deployment | `type-deployment.md` |
| Fan-in, ranks, cycles | Dependency graph | `type-dependency.md` |
| Classes, operations, typed relations | UML class | `type-uml-class.md` |
| Backbone × release slices | Story map | `type-story-map.md` |
| Physical tables + column FKs | Database schema | `type-db-schema.md` |

Before drawing, confirm the plan in one message; after drawing, run `taste-gate.md`. Rules of thumb from upstream: if a 3-column table says the same thing, use the table; above 9 nodes it is probably two diagrams; a semantic pattern adds behaviour-specific primitives, never a second layout grammar.

## Optional primitives and variants

`primitive-annotation.md` (editorial callouts, max 2), `primitive-sketchy.md` (hand-drawn stroke filter for essays), `primitive-icons.md` + `../../assets/diagram/icons.html` (stroked and brand icons), `primitive-terminal.md` (CLI-window chrome).

## Import

`import-drawio.md`, `import-mermaid.md`, `import-excalidraw.md`: extract with `scripts/diagram/<format>_extract.py`, set the four dials from `output-spec.md`, redraw (never convert), report the fidelity ledger.

## Export and checks

`export.md` / `export-registry.md`: PNG via a browser capture, SVG via `scripts/diagram/export_svg.py`. `taste-gate.md`: the universal anti-patterns and the pre-output checklist (remove test, signal test, technical, typography) — run it on every finished diagram. `doctor.md`: the diagnostic walk-through. `scripts/diagram/self_check.py <file>` is the shipped gate (accessible-SVG contract, single-file safety, motion basics). The upstream repository gates are vendored under `scripts/diagram/repo/` (`verify-geometry.py`, `verify-motion.py`, `lint-skin.py`, `lint-render.py`, `verify-skin-polarity.py`, `verify-block-registry.py`, and the per-type `verify-*.py` for architecture-delta, axonometric-plan, beeswarm, bubble, dumbbell, exploded, heatmap, marimekko, polar, ridgeline, sankey, sequence-oauth, slopegraph, streamgraph, treemap, waterfall); run the one the type reference names when it names one. Upstream repository-maintenance checks are not bundled.

## Commands

`commands/` holds the upstream slash-command wrappers (`doctor`, `export-diagram`, `import-*`, `profile`) as plain procedures; they are reachable through `$baransu:draw`, not as separate commands.

## Upstream skin note

The shipped example files were built under an earlier skin than the current `style-guide.md` tokens; new diagrams use the current tokens, the examples show layout grammar, not the current palette.
