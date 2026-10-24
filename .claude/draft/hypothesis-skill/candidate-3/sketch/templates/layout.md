# artifact layout

```
.claude/hypothesis/
├── .staging/<area>-<run-id>/   # this skill's in-progress run; readers ignore it; swapped in at step 8
└── <area>/                     # one hypothesis = one claim = one model; written only by /hypothesis
    ├── README.md               # the hypothesis (templates/README.md); frontmatter is the reader interface
    ├── page.html               # the diagram page (templates/page.html), regenerated each run
    ├── model/                  # tool-adapter files: *.tla + one cfg per run kind, or a harness crate
    │   ├── <Module>.tla
    │   ├── check.cfg           # the real check
    │   ├── mutate-R1.cfg …     # gate 2, one per safety rule
    │   └── reach-G1.cfg …      # gate 3, reachable and removed-transition pair
    └── sources/                # document snapshots only (code needs none: the commit is the snapshot)
        └── <slug>.md
```

Legacy, read-only until moved by `--maintain`: `.claude/prove-it/formal/<area>/`.

`/ship` keeps `hypothesis/` (and, until the move is done everywhere, `prove-it/formal/`); `.staging/` is never committed — it is listed in the kept set's ignore line, not archived.

Area slug: `<module-or-document>-<claim noun>`, lowercase ASCII, e.g. `approval-withdraw`, `sd-v3-vs-sa-v2`.
