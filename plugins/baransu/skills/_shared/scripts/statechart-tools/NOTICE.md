# Third-party notice — statechart-tools

The programs in this folder are written for this repo; no upstream code is copied. They restore, in a smaller form, three features of the `statechart` skill in Cursor's pstack plugin ([cursor/plugins](https://github.com/cursor/plugins), `pstack/skills/statechart/`, by Lauren Tan, MIT License — see `../statechart/LICENSE`) that upstream removed when it moved to TypeScript (commit `34b1b7c`, 2026-10-27; the last version with them is `70cfb96`):

- `chart-to-spec.mjs` follows upstream `from-chart`: a Mermaid chart with `%% never` rules and `%% when` guards becomes a TLA+ spec, one variable per region and one action per step label that moves every region with that label, then the chart the spec draws is compared with the agreed one. Changed: identifiers are ASCII and the person's words go into a view module, so charts in Chinese work with TLC; the rules go into a module of their own; an end state gets a `Done` step; the comparison reports a differing guard as a differing condition.
- `compare-charts.mjs` follows upstream `--fixed` and `--against`: marks on one chart for what a change fixes or where code departs from a spec. Changed: it merges two finished runs of the current program by their drawn states, steps and marks, instead of replaying each bug on the other model inside the checker.
- `render.mjs` renders with Pele as upstream `references/render.md` describes, with that file's suggested colours for the upstream marks and new colours for the marks `compare-charts.mjs` adds.

Pele ([obsidianmd/pele](https://github.com/obsidianmd/pele), MIT) is not bundled; `render.mjs` loads the copy the user installs.
