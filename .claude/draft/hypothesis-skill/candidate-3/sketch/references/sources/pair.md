# source adapter — pair (composite)

(unimplemented) Intent: one source as rules, the other as behaviour; checks that the behaviour satisfies the rules (refinement). Wraps two other source adapters and delegates every section to them; adds only the role assignment and the mapping between the two.

## Recognize

(unimplemented) Two sources, or one with `--against <rules source>`, or 「A 對照 B」「A 有沒有滿足 B」. The `--against` side is rules. Either side may be code or a document.

## Read

(unimplemented) Each side through its own adapter.

## Cite

(unimplemented) Each side's own form, tagged with its role.

## Extract

(unimplemented) Two claim sheets, one per side, then the refinement mapping: each behaviour state and step maps to a rules state and step, or to a stutter. A behaviour item with no mapping is a question, not a guess. Refinement rules `F*` join the rules side's `R*`.

## Sync point

(unimplemented) Two `sources[]` entries, `role: rules` and `role: behaviour`, each from its adapter.

## Stale

(unimplemented) Either side stale.

## Mutate

(unimplemented) A mutation on the behaviour side that drops something the rules require (a gate, a check); it must fail refinement.

## Replay

(unimplemented) Each step through the behaviour side's Replay; the rule it breaks through the rules side's Cite.

## Findings vocabulary

(unimplemented) `精化失敗 N`: the rules passage, the behaviour path, the place they part.

## Diff since sync

(unimplemented) Each side's own, merged.
