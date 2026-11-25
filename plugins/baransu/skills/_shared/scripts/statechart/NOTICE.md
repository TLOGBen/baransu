# Third-party notice — statechart

The TypeScript program in this folder is the `statechart` skill's scripts from Cursor's pstack plugin ([cursor/plugins](https://github.com/cursor/plugins), `pstack/skills/statechart/scripts/`, as of commit `0b46ec3`, 2026-11-19), by Lauren Tan, under the MIT License in `LICENSE`. `../../statechart.md` restates the upstream `SKILL.md` in this repo's words; no upstream text is copied there.

Modifications:

- Omitted: `test/`, `tsconfig.json`, the upstream `SKILL.md` and `references/render.md` (Pele rendering lives in `../statechart-tools/render.mjs`).
- `package.json` keeps only `name`, `private` and `type`; the test script and `fast-check`, which only the tests used, went with `test/`.
- `statechart.ts` passes `windowsHide: true` to the detached worker and janitor, marked `// baransu:`, so neither opens a console window on Windows. Upstream runs natively on Windows since `0b46ec3`; the rest of the Windows handling is upstream's.
- `frontends/spec.ts` reads `<![CDATA[ ... ]]>` sections as text, marked `// baransu`: newer SANY releases wrap module comments in CDATA, and the upstream parser, written against TLC 1.7.4, misread any spec that extends `Sequences`.
- Reader-facing chart, each line marked `// baransu`: the view may export `rules`, each rule's name mapped to the reader's words (`frontends/view.ts` checks it, `ir.ts` and `passes/regions.ts` carry it, `statechart.ts`'s help names it); `backends/mermaid.ts` writes the legend and the regions group in Chinese with those words, and adds under each marked state a line naming the rules it breaks (「打破 …」, or 「可能打破 …」 when only some model states behind it break the rule). The report keeps upstream's English and rule names.

No other upstream line is changed.
