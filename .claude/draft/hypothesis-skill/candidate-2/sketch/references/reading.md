# reading — how any skill reads a hypothesis

The single reader contract. Every reader skill (`/review`, `/hunt`, `/prove-it`, `/health`, `_shared/tdd.md` green step, `/draft`) cites this file and nothing else under `hypothesis/`. Readers never open `hypothesis.json`, never compare commits or hashes themselves, and never write under `.claude/hypothesis/`.

## One command

(unimplemented) — The invocation, resolved from the reader's own skill dir:

```
python3 "$CLAUDE_SKILL_DIR/../hypothesis/scripts/hypothesis-status.py" <selector> [--json]
```

Selectors (exactly one): `--diff <base>` (files changed since `<base>`, working tree and untracked included), `--files <path>...`, `--area <area>`, `--all`. Detail views (one area each): `--rules`, `--paths`, `--scope`, `--check`.

A missing script, a missing `python3`, or an unparseable output is state `broken` for every area the reader cares about — never a pass, never "no hypothesis".

## The table line

(unimplemented) — Columns, fixed order: `area  state  rules  sync  why`. `why` is `-` or a `;`-joined list of `changed: <file>`, `missing: <file>`, `new-writer: <file>`, `writer-gone: <file>`, `artifact-edited: <file>`, `no-evidence: <rule>`, `schema: <found>`. `--json` gives the same fields as one object per area.

## States — a closed set

(unimplemented) — Computed by the script at read time, first match wins; the stored verdict is only an input:

| state | means | the stored verdict is shown? |
|---|---|---|
| `broken` | `hypothesis.json` unparseable or of an unknown schema, or the script could not run | no |
| `draft` | the area dir exists with no `hypothesis.json` yet, or its artifact files differ from what the last publish hashed, or a `proved`/`disproved` verdict lacks its seen-failing / seen-succeeding evidence, or a reason record is incomplete | no |
| `stale` | a covered source differs from its sync hash or is missing, or the set of files matching a watch pattern changed | no |
| `legacy` | a `.claude/prove-it/formal/<area>/` dir not yet migrated | no |
| `proved` | fresh, evidence complete, every rule held within scope | yes |
| `disproved` | fresh, evidence complete, at least one rule has a counterexample path | yes |
| `unformalized` | fresh; the attempt ended in reason records only | n/a |

Only `proved` may be reported as passing anything. `--rules` and `--paths` print `?` in place of every per-rule verdict when the state is not `proved` or `disproved`.

## Exit codes

(unimplemented) — `0` every listed area is `proved`; `10` no area covers the selector; `1` at least one listed area is anything else; `2` the script itself failed (reader treats as `broken`). A reader whose rule is "green" accepts `0` and `10` only.

## State × reader — what to do

(unimplemented) — The whole decision; no reader adds judgement to it:

| state | `/review` | green step / `/draft` done | `/prove-it` | `/hunt` | `/health` |
|---|---|---|---|---|---|
| `proved` | each rule from `--rules` is a must-answer question on the walk | green | rerun `--check` command, record result | a pass never discards a clue; probe outside `--scope` | ok |
| `disproved` | each path from `--paths` is a known finding; does the change fix or touch it | red: done not met | rerun; replay each path on the real app with forced order | each path → one yes/no probe | list as open finding |
| `stale` | finding 「假說 {area} 已過期：{why}；需要 /hypothesis --maintain {area}」; rules still asked as questions | **red**; invoke `/hypothesis --maintain {area}` at once, then rerun this command; green only when it prints `proved` | record 「過期」, no verdict; invoke `/hypothesis --maintain {area}` at once, then rerun | paths usable as leads, labelled 過期 | list in verifier-coverage layer |
| `draft` | finding 「假說 {area} 未完成：{why}」 (`no-evidence` reads 「嚴格檢查未完成」) | red | no verdict | ignore | list |
| `legacy` | finding 「{area} 在舊位置，嚴格檢查未完成」 | red | run it the old way per § Legacy; record labelled 「嚴格檢查未完成」, never `proved` | ignore | list |
| `unformalized` | show its reason records; none are questions | green does not depend on it | nothing to rerun | route per each record's 改走 field | informational |
| `broken` | finding 「無法判定假說狀態」 | red | no verdict | ignore | WARN |

The hand-off to `--maintain` is the reader's own call into the writer, made by the main session, never by a review agent (review only reports). Under a non-interactive driver, `--maintain` pauses only on a "promise changed on purpose" change (`../hypothesis/references/loop-pauses.md`); the reader then reports 「卡住」 with the maintainer's questions and stays red.
| none (`10`) | when the change lands in H1–H8, write 「coverage lost: needs /hypothesis」 with one reason record | green | nothing | may hand the symptom to `/hypothesis --symptom` | nothing |

## Detail views

(unimplemented) — Exact output shape of each, so a reader quotes rather than paraphrases:
- `--rules <area>`: header `# <area>  state=<state>`; per rule `<id>  <kind>  <verdict|?>  <sentence>`.
- `--paths <area>`: per path `<P-id>  <rule>  <verdict|?>  <one-line summary in source words>  <script path>`.
- `--scope <area>`: bounds, assumptions, what is left out — verbatim from the artifact.
- `--check <area>`: the one pinned rerun command and the tool version; the reader runs it in a scratch dir and records the output in its own record, never in the area.

## Legacy

(unimplemented) — Until `/hypothesis --maintain` moves it, a `.claude/prove-it/formal/<area>/` check is read the 8.15.0 way by `/prove-it` only: run its README command, and call it stale when `git log <sync commit>..HEAD -- <covered files>` is non-empty or the working tree differs. Either way it was never seen succeeding and has no reason records, so no reader — `/prove-it` included — may use it to declare anything done: its best result is 「嚴格檢查未完成」. The same holds after the move until one `--maintain` run completes both evidence gates (the script shows it as `draft`, why `no-evidence`).
