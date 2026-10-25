# hypothesis.json — schema `baransu.hypothesis/1`

The publish record of one area. Written only by `/hypothesis`, only as the last step of a publish, only by compare-and-swap on `generation`. Read only by `scripts/hypothesis-status.py`. Example: an illustrative refund service — invented for this template, unrelated to the known-answer exams under `evals/`.

```json
{
  "schema": "baransu.hypothesis/1",
  "area": "refund",
  "title": "退款流程",
  "source_kind": "code",
  "generation": 4,
  "published_at": "<ISO-8601 from the clock at publish>",

  "sync": {
    "commit": "a1b2c3d",
    "hash_algo": "sha256-lf",
    "files": {
      "src/refund/request.ts": "<sha256-lf>",
      "src/refund/review.ts":  "<sha256-lf>",
      "src/refund/cancel.ts":  "<sha256-lf>",
      "src/refund/expire.ts":  "<sha256-lf>",
      "src/refund/model.ts":   "<sha256-lf>",
      "src/refund/payout.ts":  "<sha256-lf>"
    },
    "versions": {},
    "originals": {},
    "watch": [
      { "state": "status",
        "pattern": "\\bstatus\\s*[:=]\\s*['\"](requested|accepted|cancelled|paid)['\"]",
        "paths": ["src/refund"],
        "matched": ["src/refund/cancel.ts", "src/refund/expire.ts", "src/refund/request.ts", "src/refund/review.ts"] },
      { "state": "refunded",
        "pattern": "\\brefunded\\s*[:=]",
        "matched": ["src/refund/payout.ts"] }
    ],
    "artifact": {
      "README.md": "<sha256-lf>", "check.txt": "<sha256-lf>",
      "model/Refund.tla": "<sha256-lf>", "model/Refund.cfg": "<sha256-lf>", "model/check.sh": "<sha256-lf>",
      "variants/R1-skip-balance-check.patch": "<sha256-lf>", "variants/R2-no-cancel-check.patch": "<sha256-lf>",
      "variants/R3-pay-twice.patch": "<sha256-lf>",
      "paths/P1.md": "<sha256-lf>"
    }
  },

  "check": {
    "tool": "TLC", "version": "2.19",
    "command": "bash model/check.sh <tla2tools.jar>",
    "bounds": "one order paid 1000; refund amounts ∈ {300, 800}; two refund requests, one reviewer, one payout worker",
    "assumptions": ["each request runs one handler; the order row is the only shared state; a row write replaces it whole"],
    "left_out": ["the payment provider's own retries (see unformalized U1)"],
    "states": 1310, "seconds": 1.2,
    "verdict_at_sync": "violated",
    "seen_failing": [
      { "rule": "R1", "variant": "variants/R1-skip-balance-check.patch", "caught": true },
      { "rule": "R2", "variant": "variants/R2-no-cancel-check.patch", "caught": true },
      { "rule": "R3", "variant": "variants/R3-pay-twice.patch", "caught": true }
    ],
    "seen_succeeding": [
      { "goal": "G1", "reached": true, "removed_transition": "Payout", "unreachable_after": true }
    ],
    "seen_faithful": {
      "checker": "a fresh agent given src/refund/ and the list only, reading back from each write of status and refunded",
      "model": { "model/Refund.tla": "<sha256-lf from hypothesis-status.py --model-hash refund>" },
      "sources": { "src/refund/request.ts": "<sha256-lf from the same --model-hash output>", "…": "one entry per cited source" },
      "facts": [
        { "id": "F1", "from": "Request", "kind": "guard", "text": "訂單還沒付款時，不會有人送出退款申請。", "verdict": "stands" },
        { "id": "F2", "from": "Accept", "kind": "guard", "text": "已取消的申請，不會被核准。", "verdict": "stands" },
        { "id": "F3", "from": "Cancel", "kind": "guard", "text": "已撥款的申請，不會被取消。", "verdict": "stands" },
        { "id": "F4", "from": "Payout", "kind": "guard", "text": "沒被核准的申請，不會撥款。", "verdict": "stands" },
        { "id": "F5", "from": "status", "kind": "writers", "text": "只有申請、核准、取消三個步驟會改申請的狀態。",
          "verdict": "refuted", "fixed": "src/refund/expire.ts:12 的逾期工作也會把狀態改成 cancelled；模型加上 Expire，所有檢查重跑" },
        { "id": "F6", "from": "refunded", "kind": "values", "text": "已退金額只會增加，不會減少。", "verdict": "stands" },
        { "id": "F7", "from": "Expire", "kind": "guard", "text": "還沒逾期的申請，不會被逾期工作取消。", "verdict": "stands",
          "note": "F5 改了模型之後重新推出的清單裡才有這一條，交給同一位反駁者的第二輪" }
      ]
    }
  },

  "model_map": [
    { "part": "Request",  "kind": "action",   "cites": ["src/refund/request.ts:14-29"] },
    { "part": "Accept",   "kind": "action",   "cites": ["src/refund/review.ts:40-58"] },
    { "part": "Cancel",   "kind": "action",   "cites": ["src/refund/cancel.ts:21-33"] },
    { "part": "Expire",   "kind": "action",   "cites": ["src/refund/expire.ts:8-20"] },
    { "part": "Payout",   "kind": "action",   "cites": ["src/refund/payout.ts:30-46"] },
    { "part": "status",   "kind": "variable", "cites": ["src/refund/model.ts:5"] },
    { "part": "refunded", "kind": "variable", "cites": ["src/refund/model.ts:9"] }
  ],

  "rules": [
    { "id": "R1", "kind": "safety", "name": "NeverRefundMoreThanPaid",
      "text": "退給客人的總額，絕不超過他付的錢。",
      "cites": ["src/refund/review.ts:47"], "verdict": "violated", "paths": ["P1"] },
    { "id": "R2", "kind": "safety", "name": "NoPayoutAfterCancel",
      "text": "取消的退款，不會再撥款。",
      "cites": ["src/refund/cancel.ts:30", "src/refund/payout.ts:33"], "verdict": "held", "paths": [] },
    { "id": "R3", "kind": "safety", "name": "PayoutOnce",
      "text": "同一筆退款最多撥款一次。",
      "cites": ["src/refund/payout.ts:41"], "verdict": "held", "paths": [] }
  ],

  "goals": [
    { "id": "G1", "text": "一筆 300 元的退款，可以一路走到撥款。", "guards": ["R1", "R2", "R3"] }
  ],

  "paths": [
    { "id": "P1", "rule": "R1", "finding": "bug",
      "summary": "兩筆退款同時審核，各自都看到餘額夠，兩筆都撥款，退的比付的多。",
      "script": "paths/P1.md", "steps": 6, "replay": "證實" }
  ],

  "questions": [],

  "unformalized": [
    { "id": "U1", "where": "src/refund/payout.ts:50-71", "class": "cannot-model",
      "detail": "撥款結果取決於金流服務自己的重試與回呼時機。",
      "until": "金流服務有可建模的送達合約（至少一次／至多一次）",
      "instead": "red/green test" }
  ],

  "history": [
    { "generation": 4, "from_commit": "9e8d7c6", "to_commit": "a1b2c3d", "outcome": "no-effect", "areas_changed": [] }
  ],

  "migrated_from": null
}
```

## Field rules

- `schema` — exact string; any other value makes the area `broken` until the script learns it.
- `source_kind` — `code` | `document` | `refinement` | `sketch` (a `/draft` sketch: its paths are not replayed until the code exists). For `refinement`, `roles` adds `{ "behaviour": ["<path>", …], "rules": ["<path>", …] }` — each role a list, since one side is often several files; a past commit's files are its `sources/<sha>/` copies. A design search adds a `design` block (`../references/design.md` § Record).
- `model_map[].kind` — `action` | `variable` | `constant`, on every part not marked `observer`; it decides which never-happens items `check.seen_faithful` must hold. `model_map[].role` and `facts[].role` — for code against code, the side (`before`, `after`) a part and its items belong to; the script matches items to parts by (role, part).
- `check.seen_faithful` — `checker` (who refuted the list: never the modeller), `model` and `sources` (the two maps `hypothesis-status.py --model-hash <area>` prints, taken right after the refutation: the model files, and the cited sources the refuter read), `facts[]` (`id`, `from` = a `model_map` part, `kind` = `guard` for an action, `writers` or `values` for a variable, `fairness` for a fairness assumption (its `from` is the action the assumption keeps enabled), `text` in plain words, `verdict` = `stands` | `refuted`, and `fixed` for every refuted item). The status script shows the area `draft` when it is missing, when a non-observer action has no item, when a non-observer variable has no `writers` or `values` item, when an item has no verdict or a refuted one no fix, or when any model file or any `sync.files` source differs from its recorded hash.
- `generation` — increments by one per publish; the compare-and-swap key.
- `model_map[].cites`, `rules[].cites` — `path` or `path:line[-line]` only; a document's passage goes in `model_map[].quote`.
- `sync.files` — keys are repo-relative paths (absolute only for a document outside the repo); exactly the files cited by `model_map` and `rules`.
- `sync.originals` — `{ "<repo-relative path of the copy, under the area's sources/>": "<repo-relative path of the original>" }` for each frozen copy whose original is a local file (unlike `sync.artifact`, whose keys are area-relative); when the original still exists and its content differs from the copy, the area is `stale` (`changed: <original>`).
- `sync.watch[].matched` — sorted; computed with `git grep -l --untracked -E <pattern>` at publish. `sync.watch[].paths` — optional pathspecs that limit the search (default: the whole repo); `.claude/hypothesis/` and `.codex/hypothesis/` are never searched.
- `sync.artifact` — every file in the area except `hypothesis.json` itself.
- `check.verdict_at_sync` — the model's prediction: `held` (all rules `held`) | `violated` (any `violated`) | `unformalized` (no model; `rules` may be empty). Records published before the rename say `proved` / `disproved`; the script reads them as `held` / `violated`.
- `check.seen_failing` — one entry per `safety` or `liveness` rule, `caught: true` required for the area to be `established`.
- `check.seen_succeeding` — one entry per goal, both `reached` and `unreachable_after` true; every safety and liveness rule appears in some goal's `guards`.
- `rules[].text` / `goals[].text` / `paths[].summary` / `questions[].question` — plain words, no variable or action names; these strings are what readers quote. `paths[].summary` and `questions[].question` are the plain first layer and contain none of 活性、安全性、精化、不變式、同步點、TLC、模型、狀態空間; the technical layer lives in `paths/P<n>.md`.
- `paths[].finding` — `bug` (code), `contradiction` | `gap` (document), `refinement-break` (comparison). `paths[].rule` is the first rule the path breaks; `paths[].also` lists any other rules the same path breaks. `paths[].replay` — `證實` | `無法到達`, the replay's verdict (`../SKILL.md` §5); a broken rule's path without it shows the area `draft`, why `路徑 P<n> 還沒重播`. A path the replay 推翻 is a model error and is never published.
- `questions[]` — every ambiguity, from any source: `{ "id", "quote", "location", "ask": "<whom>", "question" }`; for code, `quote` is the line and `location` its `file:line`.
- `unformalized[]` — the reason record, `templates/reason-record.md`.
- `history[]` — one row per publish after the first: the `--maintain` outcome that produced it, or `correction` for a republish that changes no rule, verdict or model meaning (a field fixed, a page aligned), with a `note`.
- `migrated_from` — `null` or the old `.claude/prove-it/formal/<area>/` path.
