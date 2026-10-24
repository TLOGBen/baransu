# tool adapter — tlc (TLA+ checked by TLC)

(unimplemented) Intent: the default for every transition-system claim (H1–H6), from any source kind.

## Capability

(unimplemented) `shape: transition-system`; `languages: any` (models the design, not the code); `bound: bounded`; installed when `java -version` runs and `tla2tools.jar` is found (`$TLA2TOOLS`, then known locations); otherwise reason class 沒有工具 naming Java or TLC.

## Pin

(unimplemented) The version line TLC prints on start, written to `tool.version`.

## Encode

(unimplemented) One module per hypothesis; one action per claim-sheet step, with a `\* <citation>` comment directly above it; variables named in the source's words; a `pc` per actor only where a step is not atomic. Pair: a rules module and a behaviour module with a refinement mapping (`INSTANCE … WITH`).

## Safety

(unimplemented) Each `R*` an `INVARIANT` (or a temporal property for order); each `F*` the rules module's `Spec` as a `PROPERTY`.

## Reachability

(unimplemented) Each `G*` stated as `~Goal` in a separate cfg: TLC must report it violated (the goal is reachable); then the same cfg with one named transition disabled through a constant: TLC must report it holds.

## Realize a mutation

(unimplemented) A constant that switches the mutated action in (the `Fixed` pattern of the approval exam), one cfg per mutation; TLC must report the rule violated.

## Run

(unimplemented) `java -cp "$TLA2TOOLS" tlc2.TLC -metadir "$HYP_TMP" -config <cfg> <module>` from `model/`; `-metadir` keeps `states/` out of the artifact; one command per cfg, listed in the README.

## Read the result

(unimplemented) The invariant name violated, the error trace as a `path` trace (each state's action name → coverage map → citation), distinct states found.

## Bounds

(unimplemented) The constants that bound the space, in plain words. `--unbounded` is out of this adapter: no admitted proof adapter → reason record for the unbounded part, bounded result kept.
