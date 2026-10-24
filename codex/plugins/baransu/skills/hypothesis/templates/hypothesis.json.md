# hypothesis.json — schema `baransu.hypothesis/1`

The publish record of one area. Written only by `$baransu:hypothesis`, only as the last step of a publish, only by compare-and-swap on `generation`. Read only by `scripts/hypothesis-status.py`. Example: an illustrative refund service — invented for this template, unrelated to the known-answer exams under `evals/`.

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
      "src/refund/payout.ts":  "<sha256-lf>"
    },
    "versions": {},
    "originals": {},
    "watch": [
      { "state": "status",
        "pattern": "\\bstatus\\s*[:=]\\s*['\"](requested|accepted|cancelled|paid)['\"]",
        "paths": ["src/refund"],
        "matched": ["src/refund/cancel.ts", "src/refund/request.ts", "src/refund/review.ts"] },
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
    ]
  },

  "model_map": [
    { "part": "Request", "cites": ["src/refund/request.ts:14-29"] },
    { "part": "Accept",  "cites": ["src/refund/review.ts:40-58"] },
    { "part": "Cancel",  "cites": ["src/refund/cancel.ts:21-33"] },
    { "part": "Payout",  "cites": ["src/refund/payout.ts:30-46"] }
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
      "script": "paths/P1.md", "steps": 6 }
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
- `source_kind` — `code` | `document` | `refinement`. For `refinement`, `roles` adds `{ "behaviour": "<path>", "rules": "<path>" }`.
- `generation` — increments by one per publish; the compare-and-swap key.
- `model_map[].cites`, `rules[].cites` — `path` or `path:line[-line]` only; a document's passage goes in `model_map[].quote`.
- `sync.files` — keys are repo-relative paths (absolute only for a document outside the repo); exactly the files cited by `model_map` and `rules`.
- `sync.originals` — `{ "<repo-relative path of the copy, under the area's sources/>": "<repo-relative path of the original>" }` for each frozen copy whose original is a local file (unlike `sync.artifact`, whose keys are area-relative); when the original still exists and its content differs from the copy, the area is `stale` (`changed: <original>`).
- `sync.watch[].matched` — sorted; computed with `git grep -l --untracked -E <pattern>` at publish. `sync.watch[].paths` — optional pathspecs that limit the search (default: the whole repo); `.codex/hypothesis/` and `.codex/hypothesis/` are never searched.
- `sync.artifact` — every file in the area except `hypothesis.json` itself.
- `check.verdict_at_sync` — the model's prediction: `held` (all rules `held`) | `violated` (any `violated`) | `unformalized` (no model; `rules` may be empty). Records published before the rename say `proved` / `disproved`; the script reads them as `held` / `violated`.
- `check.seen_failing` — one entry per `safety` or `liveness` rule, `caught: true` required for the area to be `established`.
- `check.seen_succeeding` — one entry per goal, both `reached` and `unreachable_after` true; every safety and liveness rule appears in some goal's `guards`.
- `rules[].text` / `goals[].text` / `paths[].summary` / `questions[].question` — plain words, no variable or action names; these strings are what readers quote. `paths[].summary` and `questions[].question` are the plain first layer and contain none of 活性、安全性、精化、不變式、同步點、TLC、模型、狀態空間; the technical layer lives in `paths/P<n>.md`.
- `paths[].finding` — `bug` (code), `contradiction` | `gap` (document), `refinement-break` (comparison). `paths[].rule` is the first rule the path breaks; `paths[].also` lists any other rules the same path breaks.
- `questions[]` — every ambiguity, from any source: `{ "id", "quote", "location", "ask": "<whom>", "question" }`; for code, `quote` is the line and `location` its `file:line`.
- `unformalized[]` — the reason record, `templates/reason-record.md`.
- `history[]` — one row per publish after the first: the `--maintain` outcome that produced it, or `correction` for a republish that changes no rule, verdict or model meaning (a field fixed, a page aligned), with a `note`.
- `migrated_from` — `null` or the old `.codex/prove-it/formal/<area>/` path.
