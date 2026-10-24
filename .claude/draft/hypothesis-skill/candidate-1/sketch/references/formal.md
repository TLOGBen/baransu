# formal — when a hypothesis is written, with what, and what makes it trustworthy

(unimplemented) Moved from `prove-it/references/formal.md`. Single source of the trigger table: other skills cite `../hypothesis/references/formal.md` §Triggers by anchor and never copy rows.

## Triggers

(unimplemented) The H1–H8 table from the plan: # | class (HAZOP guide word) | observable signal | default tool | one not-trigger example per row. The example column is required by the success criteria and is what makes this the single source.

## Not triggers

(unimplemented) The six rows: one run settles it; a static permission check on one endpoint; appearance, copy, docs, config values, parameter choices; a read-only query with one reader; an area already in sync (rerun it instead); a prototype the user says will be thrown away.

## Tool

(unimplemented) Let the question choose: order and interleaving → TLA+ checked by TLC (default in any language); every input to the code → a code-level verifier (Kani, Verus, Dafny); a policy combination → SMT; every size → a proof. No verifier for the language → verdict `cannot`, reason class `no-tool`; never fall back to property tests.

## Strictness

(unimplemented) The six musts, one paragraph each:

### True to the source
### Seen failing
### Seen succeeding
### Scope stated
### Findings stay findings
### Stale when the source moved

## Reason record

(unimplemented) The four fields and the six classes — the only schema for "not formalized". Points at `templates/README.md` §Not formalized for the row form and gives the one-line form a reader writes when the user declines:
`未形式化：<where>｜<class>｜<detail>｜<until>｜<instead>`

| class (README value) | 中文 | the detail must name |
|---|---|---|
| `no-tool` | 沒有工具 | the missing tool |
| `cannot-model` | 無法建模 | the outside dependency |
| `too-large` | 超出範圍 | the bounds tried and the time taken |
| `not-trigger` | 符合不觸發條件 | which not-trigger row |
| `no-truth` | 沒有對錯可證 | — |
| `user-declined` | 使用者決定不做 | the user's words, quoted |

## Drift

(unimplemented) The four outcomes of `--maintain` per change since the sync point: no effect (judged against the model); the model no longer describes the source (update from the source); the promise changed on purpose (rewrite the rule citing the evidence, old and new wording); the promise may be broken (bug candidate). Per area result: in sync, updated, bug, blocked. Includes covered functions renamed, split or moved, and new code outside `covers` that writes the guarded state — found by searching for writers of each model variable, not by the diff alone.
