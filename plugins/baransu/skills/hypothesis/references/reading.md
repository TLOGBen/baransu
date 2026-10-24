# reading — how any skill reads a hypothesis

The single reader contract. Every reader skill (`/review`, `/hunt`, `/prove-it`, `/health`, `_shared/tdd.md` green step, `/draft`) cites this file and nothing else under `hypothesis/`, except `formal.md` for the H1–H8 trigger list and the not-trigger list. Readers never open `hypothesis.json`, never compare commits or hashes themselves, and never write under `.claude/hypothesis/`.

## One command

The invocation, resolved from the reader's own skill dir (use `python` where `python3` does not exist, as on some Windows machines):

```
python3 "$CLAUDE_SKILL_DIR/../hypothesis/scripts/hypothesis-status.py" <selector> [--json]
```

Selectors (exactly one): `--diff <base>` (hypotheses covering files changed since `<base>` — committed, working tree and untracked — plus every hypothesis whose covered content changed even where git does not track or ignores the file), `--files <path>...`, `--area <area>`, `--all`. Detail views (one area each): `--rules`, `--paths`, `--scope`, `--check`.

A missing script, a missing `python3`, or an unparseable output is state `broken` for every area the reader cares about — never a pass, never "no hypothesis".

## The table line

Columns, fixed order: `area  state  rules  sync  why`. `why` is `-` or a `;`-joined list of `changed: <file>`, `missing: <file>`, `new-writer: <file>`, `writer-gone: <file>`, `artifact-edited: <file>`, `no-evidence: <what is missing>`, `schema: <found>`, `unparseable: hypothesis.json`, `unpublished: hypothesis.json`, `no-git: <state>`, and for an `established` area `violated: <rule id>` per rule its model breaks. `--json` gives the same fields as one object per area.

## States — a closed set

Computed by the script at read time; the stored verdict is only an input. The plain name is what a reader shows the user. How an area moves between these states, and who moves it, is the shared picture `../../_shared/hypothesis-states.md`.

| state | plain name | means | the stored verdict is shown? |
|---|---|---|---|
| `broken` | 無法判定 | `hypothesis.json` unparseable or of an unknown schema, or the script could not run | no |
| `draft` | 假說未成立 | the area dir exists with no `hypothesis.json` yet, or its artifact files differ from what the last publish hashed, or the evidence gates (seen failing, seen succeeding) or a reason record are incomplete | no |
| `stale` | 過期 | a covered source differs from its sync hash or is missing, a `sources/` copy's original still exists and differs from the copy, or the set of files matching a watch pattern changed | no |
| `legacy` | 舊位置 | a `.claude/prove-it/formal/<area>/` dir not yet migrated | no |
| `established` | 成立假說 | fresh and evidence complete; each rule carries the model's prediction, 守住 or 被打破 with a path | yes |
| `unformalized` | 無法成立假說 | fresh; the attempt ended in reason records only | n/a |

The script decides in this order, first match wins: `broken`; `draft` for an unpublished or hand-edited area; `stale`; `draft` for incomplete evidence; then the stored verdict (`established` or `unformalized`). `legacy` rows come from `.claude/prove-it/formal/` and are listed after the others.

An `established` hypothesis is what `/hypothesis` exists to produce; whether its predictions hold on the running system is `/prove-it`'s to show (證實／推翻／無法到達). Only an `established` hypothesis whose every rule is 守住 may be reported as passing anything. `--rules` and `--paths` print `?` in place of every per-rule verdict unless the state is `established`.

## Exit codes

`0` every listed area is `established` with every rule 守住 (`unformalized` areas are listed, not judged); `10` no area covers the selector; `1` any other listed state, or an `established` area with a rule 被打破; `2` the script itself failed (reader treats as `broken`). A reader whose rule is "green" accepts `0` and `10` only.

## State × reader — what to do

The whole decision; no reader adds judgement to it:

| state | `/review` | green step / `/draft` done | `/prove-it` | `/hunt` | `/health` |
|---|---|---|---|---|---|
| `established`, every rule 守住 | each rule from `--rules` is a must-answer question on the walk | green | rerun `--check` command, record result | a pass never discards a clue; probe outside `--scope` | ok |
| `established`, a rule 被打破 | each path from `--paths` is a known finding; does the change fix or touch it | red: done not met | rerun; replay each path on the real app with forced order | each path → one yes/no probe | list as open finding |
| `stale` | finding 「假說 {area} 已過期：{why}；需要 /hypothesis --maintain {area}」; rules still asked as questions | **red**; invoke `/hypothesis --maintain {area}` at once, then rerun this command; green only when it exits `0` | record 「過期」, no verdict; invoke `/hypothesis --maintain {area}` at once, then rerun | paths usable as leads, labelled 過期 | list in verifier-coverage layer |
| `draft` | finding 「假說 {area} 未成立：{why}」 (`no-evidence` reads 「嚴格檢查未完成」) | red | no verdict | ignore | list |
| `legacy` | finding 「{area} 在舊位置，嚴格檢查未完成」 | red | run it the old way per § Legacy; record labelled 「嚴格檢查未完成」, never counted as established | ignore | list |
| `unformalized` | show its reason records; none are questions | green does not depend on it | nothing to rerun | route per each record's 改走 field | informational |
| `broken` | finding 「無法判定假說狀態」 | red | no verdict | ignore | WARN |
| none (`10`) | nothing to read; a claim only every order or every input settles names a hypothesis as the missing record (review `principles/evidence.md` #7) | green | invoke `/hypothesis` on an every-case claim first | may hand the symptom to `/hypothesis <HUNT-id>` | nothing |

**Telling the person.** Whenever a reader tells the person a hypothesis's state or a rule's verdict, it first introduces the hypothesis itself, once per area per report: what the area covers for whoever uses it, as the smallest visual `../../show-me/SKILL.md` lays out with one or two sentences in `/huh`'s voice (`../../huh/SKILL.md`), built from the `--rules` title and sentences; then the state and the verdicts.

The hand-off to `--maintain` is the reader's own call into the writer, made by the main session, never by a review agent (review only reports). Under a non-interactive driver, `--maintain` pauses only on a "promise changed on purpose" change (`loop-pauses.md`); the reader then reports 「卡住」 with the maintainer's questions and stays red. In the other direction, `/hypothesis` hands a freshly `established` code area with a rule 被打破 to `/prove-it` at once (`../SKILL.md` §5).

## Detail views

Exact output shape of each, so a reader quotes rather than paraphrases:
- `--rules <area>`: header `# <area>  state=<state>  title=<title>`; per rule `<id>  <kind>  <verdict|?>  <sentence>`.
- `--paths <area>`: per path `<P-id>  <rule>  <verdict|?>  <one-line summary in source words>  <script path>`.
- `--scope <area>`: bounds, assumptions, what is left out — verbatim from the artifact.
- `--check <area>`: the one pinned rerun command and the tool version; the reader runs it in a scratch dir and records the output in its own record, never in the area. A rerun on an unchanged source that disagrees with the stored verdict is reported 「與紀錄不符」 and treated as `broken`: the model, the tool or the environment moved, and no verdict from that area counts until `/hypothesis --maintain` explains why.

## Legacy

Until `/hypothesis --maintain` moves it, a `.claude/prove-it/formal/<area>/` check is read the 8.15.0 way by `/prove-it` only: run its README command, and call it stale when `git log <sync commit>..HEAD -- <covered files>` is non-empty or the working tree differs. Either way it was never seen succeeding and has no reason records, so no reader — `/prove-it` included — may use it to declare anything done: its best result is 「嚴格檢查未完成」. The same holds after the move until one `--maintain` run completes both evidence gates (the script shows it as `draft`, why `no-evidence`).
