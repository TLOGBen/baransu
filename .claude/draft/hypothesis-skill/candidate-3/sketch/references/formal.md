# formal — when to write a hypothesis and what makes it one

(unimplemented) Intent: the single source of the trigger list and the strictness rules. Moves here from `prove-it/references/formal.md`; other skills cite it by section, never copy it. Tool-neutral and source-neutral: it names what must hold, the adapters say how.

## Triggers

(unimplemented) The H1–H8 table from the plan — category, visible signal, default tool, and at least one non-trigger example per row. The default-tool column names an adapter by its `tools/` file name.

## Not a trigger

(unimplemented) The six non-triggers from the plan; "a hypothesis already in sync covers it" means rerun it instead.

## Cost test

(unimplemented) Write one when p·(1−d)·H > C_f; the trigger rows are the cases where d is low (H1–H3) or H is high (H4–H6).

## Strictness

(unimplemented) The five gates every hypothesis passes, in the order SKILL.md step 5 runs them:
1. **True to source** — every model element has a coverage-map row whose citation resolves; indivisible in the source means one step in the model; names are the source's.
2. **Seen failing** — every safety rule caught on its mutation.
3. **Seen succeeding** — every safety rule has a goal; the goal is reachable; it is unreachable once one transition is removed.
4. **Scope stated** — bounds, assumptions, left out; `--unbounded` means a proof, not a bigger bound.
5. **Findings stay findings** — a trace every step of which the source can take is a finding; never weaken a rule or the model to pass.

## Verdicts

(unimplemented) What each value in `ports.md` § Verdict values means, and how a hypothesis-level status follows from its rules' results and its gates.

## What readers may conclude

(unimplemented) A `proved` hypothesis covers the model within its bounds at its sync point, not the system; `stale` overrides every other status for every reader.
