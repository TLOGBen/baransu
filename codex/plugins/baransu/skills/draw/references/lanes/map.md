# Map lane — the vendored archify engine

The vendored engine under `scripts/map/` renders typed JSON into an explorable HTML and refuses to ship an unchecked one. Its own rules are in `references/map/`; this chapter is $baransu:draw's route through them. The steps are in `SKILL.md` § Lane: map.

## Type router

| Type | Use for | Schema | Example |
|---|---|---|---|
| `architecture` | components, services, boundaries, infrastructure; what something everyday is made of | `scripts/map/schemas/architecture.schema.json` | `scripts/map/examples/web-app.architecture.json`; deployments: `production-deployment.architecture.json` |
| `workflow` | processes, approval gates, tool calls, runbooks, CI/CD; step-by-step plans | `workflow.schema.json` | `agent-tool-call.workflow.json` |
| `sequence` | API call chains, request lifecycles, async traces; a back-and-forth between people | `sequence.schema.json` | `cache-miss-request.sequence.json` |
| `dataflow` | pipelines, ETL/ELT, lineage, consumers; where money or documents go | `dataflow.schema.json` | `product-analytics.dataflow.json` |
| `lifecycle` | state / status transitions, retries, waiting and terminal states | `lifecycle.schema.json` | `deployment-release.lifecycle.json` |

Schemas sit in `scripts/map/schemas/`, examples in `scripts/map/examples/`. An example teaches the shape of a candidate, never its facts.

### An ambiguous scenario

Run `node scripts/map/bin/archify.mjs guide "<scenario>" --json`. Its scenario prompts are upstream text: "ask before setting meta.engineering_profile" is decided by you — set it only when the request asks for a fail-closed deployment review — and noted in `docs/brief.md`. Only a missing fact may stop the run.

## Authoring

Follow `references/map/authoring-defaults.md`: composition led by the main user journey, boundaries that express real isolation, labels with meaning, placement by actual connections before coordinates, automatic routes first. Set `meta.output` to a portable relative `<slug>.map.html` and `meta.quality_profile: "showcase"` unless a dense `standard` map was asked for. For a real repository follow `references/map/repository-authoring.md`: pin the commit, attach `sources` (path and line) to every asserted node, pass `--repo-root`.

## Environment first

The browser gate finds a browser only through `ARCHIFY_CHROME`; it does not look for Playwright's Chromium on its own. Before the first `finalize`, export it (and the sandbox opt-out in a container), and switch off the package's network update check:

```bash
export ARCHIFY_CHROME="${CHROME_PATH:-$(ls -d ${PLAYWRIGHT_BROWSERS_PATH:-$HOME/.cache/ms-playwright}/chromium-*/chrome-linux*/chrome 2>/dev/null | tail -1)}"
export ARCHIFY_CHROME_NO_SANDBOX=1 ARCHIFY_UPDATE_CHECK_DISABLED=1
```

`CHROME_PATH` is the path `node scripts/motion/doctor.mjs --install` reports (on Windows and macOS use it directly; macOS system Chrome is `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`). Every vendored launcher seeds the browser profile before Chromium starts (`references/motion/pipeline.md` § Known environment failures). A receipt that says `chrome-unavailable` / `browser-check: skipped` is an environment failure: set the variable and rerun — never "repair" a candidate for it.

## Finalize

```bash
node scripts/map/bin/archify.mjs finalize <type> candidate.json <slug>.map.html --quality showcase --json [--repo-root <repo>]
```

Save the receipt as `docs/finalize.json`; a passing receipt is the evidence. Non-zero is never success: repair the connected neighbourhood per `references/map/delivery-contract.md` § Failed finalize, within its repair limit, and rerun the complete command. With `ARCHIFY_UPDATE_CHECK_DISABLED=1` the receipt's `update` block reads `disabled`; ignore it either way and never run `scripts/map/scripts/check-update.mjs`.

## Overrides on the delivery contract

These replace the vendored `references/map/delivery-contract.md` wherever the two disagree; the vendored file stays as published.

- **No correction-round cap.** The contract's "never exceed two focused correction rounds" and its `correction_rounds: 0|1|2` field do not limit $baransu:draw. The perceptual review runs on every map, and correction rounds continue until the review passes. Record the real number of rounds in `docs/review_log.md`; the receipt's `correction_rounds` field may carry `2` when more ran, with the true count in the log.
- **No repair-attempt cap.** "Within its repair limit" in § Failed finalize does not stop the work: repair and rerun `finalize` until the receipt passes.
- **Stalls end on evidence, not on a count.** When two consecutive rounds (review or repair) leave the same failure unchanged, record it under 未做到的 with the last receipt and the reason, and move on — the stall rule in `references/critique-loop.md`.

## Viewer features

`meta.animation: "trace"`, share cards and presentation are opt-in: set them, and look up `references/map/viewer-runtime.md`, only when the user asks for them.

## Without a shell

Hand-place architecture SVG into `scripts/map/assets/template.html` with the semantic CSS classes, and follow the visual-review contract in `references/map/delivery-contract.md`.
