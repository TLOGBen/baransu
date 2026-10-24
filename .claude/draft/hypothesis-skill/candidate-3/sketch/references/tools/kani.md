# tool adapter — kani (Rust, every input)

(unimplemented) Intent: H7 for Rust — the code itself, for every input up to a bound. The representative code-level adapter; admitted only after its exam in `evals/` passes.

## Capability

(unimplemented) `shape: every-input`; `languages: rust`; `bound: bounded (unwind)`; installed when `cargo kani --version` runs.

## Pin

(unimplemented) `cargo kani --version`.

## Encode

(unimplemented) One `#[kani::proof]` harness per rule in a throwaway crate or a `cfg(kani)` module outside product files; it calls the real function, so the coverage map cites the function under test and each assumption. No hand-written model of the function.

## Safety

(unimplemented) `assert!` of the rule after the call; `kani::assume` only for preconditions the source states.

## Reachability

(unimplemented) `kani::cover!` on the goal; must be satisfiable; with the named branch removed in the mutated copy, unsatisfiable.

## Realize a mutation

(unimplemented) Run the harness against the mutated copy of the code made outside the working tree.

## Run

(unimplemented) `cargo kani --harness <name>` with `--target-dir "$HYP_TMP"`.

## Read the result

(unimplemented) `VERIFICATION:- FAILED` with the concrete playback as a `witness` trace; checks run; unwind bound.

## Bounds

(unimplemented) The unwind bound and the input sizes; `--unbounded` → Verus or a proof adapter, not admitted → reason record.
