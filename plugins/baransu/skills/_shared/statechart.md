# statechart — a TLA+ model's result, turned into a chart and paths by a program

TLC's result is deterministic: the same spec, config and one worker give the same states and the same shortest paths every run. So the chart, the numbered paths and the list of rules that hold are produced by `scripts/statechart/`, never transcribed by hand from TLC's output. The one part that takes judgment is the words — what each state and each step is called for the person reading — and that goes into a view file the program applies. The model writes the view; the program writes everything else. A chart or a path edited by hand is no longer the model's result.

## Run

```sh
node <this folder>/scripts/statechart/statechart.ts SPEC.tla --config SPEC.cfg --view VIEW.mjs --out NEW_DIR
```

- Node 22.18 or later runs the `.ts` files directly; nothing is built or installed. On Unix, `scripts/statechart/statechart` picks Node, Bun or Deno.
- Set `TLA2TOOLS` to the installed `tla2tools.jar` and `JAVA` to a `java` (11 or later). Without them the program installs TLC and Java with mise, which needs the network.
- Work in a scratch copy of the spec and config. `--out` must be a new or empty folder; to redo a chart, give a new one.
- Exit code: 0 every rule held, 1 some rule broke, 2 the check did not finish (the report says why). It writes `report.md`, `chart.mmd` (when the chart fits), `tlc.out`, and `tlc-RULE.out` for a broken rule whose path the chart does not show.
- It runs TLC itself with one worker. A broken rule is removed and TLC runs again until none breaks, so every rule gets its own verdict and shortest path; after the first break each run stops at 100,000 distinct states, and a rule it could not finish is listed under "Rules not checked" — it may hold or break.

## What the spec must give it

- Every rule the reader agrees to is an `INVARIANT` (or a `PROPERTY`). When the model has no variable for a rule, add one. A rule is never weakened to make it hold.
- `Next` is a disjunction of named actions (`YouPay \/ BankApproves \/ ...`). The action names are what the view turns into arrow labels; a `Next` written as one formula gives every step the name `Next`.
- A correct end state has no step out, and TLC reports it as a deadlock. Add an action that is enabled only in the end states and changes nothing (`Done == phase \in {"paid", "failed"} /\ UNCHANGED vars`), and hide it in the view.
- TLC goes on past a broken rule, so a model with no limit on its states can run forever: keep the constants small or add a `CONSTRAINT`.

## The view

A JavaScript module (`.mjs`) that only maps values to words. Each function depends only on its arguments; the program calls each at most once per state or step and uses the answer in the chart and the report alike.

- `state(vars)` — the reader's name for a model state. A string gives a flat chart; an array gives nested states (`v.main.split(".")`); an object gives one parallel region per key (`({ Playback: v.playback, Volume: v.volume })`). In `vars`, a TLA+ sequence is an object keyed from 1 and a set is an array.
- `step(action, from, to)` — the arrow's label, as the reader sees it happen ("you press pay", "the bank times out"), never the code's or the action's name. Return `null` to hide a step. A step that happens only under a condition ends with it in brackets, in the reader's words: `you press pay [while the file loads]`. In a regions chart the program writes conditions on other regions itself; do not add brackets for those.
- `group(vars)`, `colors`, `title` — optional: a phase per state and its color class, and the chart's title.
- `rules` — optional: each rule's name mapped to the reader's words for it (`{ Qualified: "補位只找正式主管" }`), a short sentence and never a number or code. The legend and the line under each marked state use these words; a rule left out keeps its name. Give every rule the reader will see.

Labels are what the reader can see or cares about ("Paying", "Lease held, write pending"), with no variable names. Two model states that act the same for the reader share one label. A step that stays inside one label is not drawn; split the label when the reader must see it.

Keep a chart to about 20 arrows. Coarsen `state()` first; then hide steps the reader does not need. Never merge away a state on a bug path or two states that break different rules. When hiding: every chart state stays reachable from a start state, every state with a step out in the model keeps one arrow out, an arrow's steps are hidden all or none, and what was hidden is said beside the chart.

A sequence of pictures — the normal path first, then one part added at a time — is the same spec run with a sequence of views, each a little finer than the last.

## Reading the report

- Each broken rule has its shortest path, numbered from the start state, each step written as the view's arrow label and the state it reaches. That numbered list is the finding; copy it as the program wrote it.
- In `chart.mmd`, a state marked `breaks` breaks a rule in every model state behind it, `mayBreak` in some. A second line in each marked state names its rules — 「打破 補位只找正式主管」 for a rule broken in every model state behind it, 「可能打破 …」 for some — and the legend, in Chinese, names the rules of each mark. States on a shortest bug path are `bugPath`; a state a liveness counterexample repeats forever is `repeats`. The chart also shows states after a bug, because TLC goes past it.
- With `VIEW` or `SYMMETRY`, states TLC treats as the same are one state, and an arrow may lead to that one; the report says so. Past a `CONSTRAINT` TLC checks the rules but does not explore or check deadlock; a shortest path may end there.
- Above 500 states the chart draws only the paths to broken rules, and with none broken it writes no `chart.mmd`; the report still gives every verdict. Make the model smaller to see the whole graph.

## Comparing two runs

`node <this folder>/scripts/statechart-tools/compare-charts.mjs A_DIR B_DIR --mode fixed|against [--a WORDS] [--b WORDS] [--title WORDS] --out NEW_DIR` merges two runs into one chart and a rule-by-rule table. Both runs use the same view, so states match by their words; give the merged chart its own `--title` when the view's title names one side.

- `--mode fixed`: A is the model today, B the model with the change. A state is `fixed` (breaks a rule in A, not in B), `stillBreaks`, or `newBreak` (breaks only in B); a state or step only one side has is marked and named in the report. This is the picture of what a change repairs.
- `--mode against`: A models the code, B is the agreed spec. States and steps only one side has are marked, and a state takes the worse of its two marks. This is the picture of where the code departs from the spec.

The comparison reads what the two charts draw: states, starts, arrows and their conditions, and the marks. It does not replay one model's bug on the other; the table says, per rule, whether each side holds or breaks it.

## From an agreed chart to a spec

When the behaviour is not built yet — a `/draft` sketch, a flow still being designed — agree the chart with the person first, then let the program write the model:

`node <this folder>/scripts/statechart-tools/chart-to-spec.mjs CHART.mmd --module NAME [--dir DIR] --out NEW_DIR`

- The chart is a Mermaid `stateDiagram-v2` with ASCII state ids and the person's words as labels (`s1: 購物車`, or `state "購物車" as cart`). It is flat, or one top group split by `--` into named regions; each region becomes one variable. Each step label is one action, and it moves every region whose current state has a step with that label. Write a step's condition on other regions at its label's end in brackets, in the words the program draws (`同步完成 [when 線上]`), with a `%% when ID, ID` (or `%% when not ID, ID`) line right after it.
- Each rule is a line `%% never NAME: A & B -- the person's sentence`, A and B being states of different regions; NAME is an ASCII identifier. A state with no step out is an intended end and gets a `Done` step; a stop anywhere else is reported as a deadlock — a design bug.
- The first run writes `NAMERules.tla` (the rules, in a module of their own), `NAME.tla` (the model, which extends it), `NAME.cfg` and `NAME.view.mjs` — ASCII identifiers in the spec, the person's words only in the view and comments — checks them, and compares the chart the spec draws with the agreed chart: a fresh skeleton prints `same`. A broken rule there is a bug in the agreed design; take it to the people who agreed the chart.
- Later, add the real code's guards and variables to `NAME.tla`, each condition with the file and line it comes from, and run the same command with a new `--out`: an existing `NAME.tla` is kept, and every place the code departs from the chart is printed — a state the spec never reaches, a step only one side has, a condition that differs. For each, ask whether the code or the chart is wrong.
- Exit 0 is no broken rule and no difference, 1 a broken rule or a difference, 2 a run that did not finish.

## Showing it

In the conversation, when the host offers an inline drawing tool — even one only listed as deferred, which you load first — draw `chart.mmd` with it: the same states, groups, arrows, labels and marks, in the same arrangement, nothing merged, regrouped or added. Without such a tool, show `chart.mmd` as a `mermaid` block where the host renders Mermaid; otherwise give the report's numbered paths as text.

A file the person keeps, such as a README, holds `chart.mmd` itself, with the SVG that `node <this folder>/scripts/statechart-tools/render.mjs chart.mmd` writes beside it; give that SVG too when the person asks for an image. It renders with Pele, colours every mark of both programs, and follows the viewer's light or dark setting. Pele is installed once outside the repo (`npm install pele@1.9.0` in `~/.local/share/pele`, or the folder `PELE_DIR` names); when it is missing, say so with that command and keep the `.mmd`. Say what the model leaves out and which steps the view hides.

When the model describes code, replay each bug path against the real code, one step per action; a path the code cannot take is a model error until shown otherwise.
