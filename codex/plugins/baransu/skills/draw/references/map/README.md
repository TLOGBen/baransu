# Map lane — vendored from tt-a1i/archify (MIT, v3.0.1)

Interactive, validated diagrams from typed JSON: `architecture`, `workflow`, `sequence`, `dataflow`, `lifecycle`. The output is one standalone HTML with inline SVG, light/dark themes, focus / route / reach / lens exploration, deep links, a presentation stage, and PNG / JPEG / WebP / SVG / WebM export. The runnable package lives in `scripts/map/` (CLI `bin/archify.mjs`, renderers, schemas, examples, template); these references are copies of its authoring docs with paths rewritten (see `../../NOTICE.md`). The package needs only Node ≥ 18. Its browser gate finds a browser only through `ARCHIFY_CHROME` (plus `ARCHIFY_CHROME_NO_SANDBOX=1` in a container); point it at Playwright's Chromium or a local Chrome before `finalize`, as SKILL.md § Lane: map shows. `ARCHIFY_UPDATE_CHECK_DISABLED=1` keeps `finalize` off the network.

## Authoring path

1. Choose the type from the router in `../../SKILL.md` (§ Type router).
2. Read `authoring-defaults.md` once, then the matching example in `../../scripts/map/examples/` and, for sequence / dataflow / lifecycle, the mode schema plus `../../scripts/map/schemas/common.schema.json`. Examples teach shape, not facts: fresh IDs, wording and layout every time.
3. For a real codebase, follow `repository-authoring.md` while tracing: freeze the commit, attach `sources` (path + line) to every asserted node, pass `--repo-root`.
4. Write the complete candidate JSON (`meta.output` is a POSIX-relative `.html` path; `meta.quality_profile: "showcase"` unless dense `standard` was asked for), then:

```
node scripts/map/bin/archify.mjs finalize <type> candidate.json out.html --quality showcase --json [--repo-root <repo>]
```

A passing receipt proves validate → deliver → strict check → real-browser check all passed. A non-zero exit is never success: read the compact stdout, repair the connected neighbourhood per `delivery-contract.md` § Failed finalize (respect its repair limit), rerun the same command.

## When to read what

| Situation | Read |
|---|---|
| Several tangled architecture routes | `architecture-layout-repair.md` |
| Measured field / geometry / label failures, legend, locale, viewport | `authoring-contract.md` (table of contents at top) |
| Output paths, recovery, exports, opening, captures, handoff receipt | `delivery-contract.md` |
| A node names a real product and the user wants its mark | `brand-marks.md` |
| Share cards, trace motion, deep links, presentation, finder | `viewer-runtime.md` (only when asked; the viewer already ships them) |
| Field shapes and the legend / translations contracts | `schemas-README.md` |

`update-awareness.md` describes the upstream update notifier. This skill is self-contained: never run `scripts/map/scripts/check-update.mjs`, and ignore the `update` block in receipts.

## Mermaid in

Read Mermaid for topology and meaning, then author fresh JSON: `flowchart`/`graph` → `workflow` (or `architecture` for a component map), `sequenceDiagram` → `sequence`, `stateDiagram` → `lifecycle`. Never reproduce Mermaid styling.

## Everyday subjects

The same five modes cover a leave plan, an approval process, a rental back-and-forth, where money or documents go, where an application stands: use everyday `icon` values and `meta.legend` labels, and ask for missing personal facts rather than inventing dates, amounts or rules.
