# hypothesis.json — schema `baransu.hypothesis/1`

The publish record of one area. Written only by `/hypothesis`, only as the last step of a publish, only by compare-and-swap on `generation`. Read only by `scripts/hypothesis-status.py`. Example: the approval known-answer case (naive version).

```json
{
  "schema": "baransu.hypothesis/1",
  "area": "approval",
  "title": "簽核流程",
  "source_kind": "code",
  "generation": 4,
  "published_at": "<ISO-8601 from the clock at publish>",

  "sync": {
    "commit": "a1b2c3d",
    "hash_algo": "sha256-lf",
    "files": {
      "src/approval/submit.ts":   "<sha256-lf>",
      "src/approval/approve.ts":  "<sha256-lf>",
      "src/approval/withdraw.ts": "<sha256-lf>",
      "src/approval/pay.ts":      "<sha256-lf>"
    },
    "versions": {},
    "watch": [
      { "state": "status",
        "pattern": "\\bstatus\\s*[:=]\\s*['\"](approved|withdrawn|pending|rejected)['\"]",
        "matched": ["src/approval/approve.ts", "src/approval/submit.ts", "src/approval/withdraw.ts"] },
      { "state": "paid",
        "pattern": "\\bpaid\\s*[:=]\\s*true",
        "matched": ["src/approval/pay.ts"] }
    ],
    "artifact": {
      "README.md": "<sha256-lf>", "diagrams.html": "<sha256-lf>", "check.log": "<sha256-lf>",
      "model/Approval.tla": "<sha256-lf>", "model/Naive.cfg": "<sha256-lf>",
      "variants/R1-keep-old-approvals.patch": "<sha256-lf>",
      "paths/P1.md": "<sha256-lf>", "paths/P2.md": "<sha256-lf>"
    }
  },

  "check": {
    "tool": "TLC", "version": "2.19",
    "command": "java -XX:+UseParallelGC -cp <tla2tools.jar> tlc2.TLC -deadlock -config model/Naive.cfg model/Approval.tla",
    "bounds": "Amounts ∈ {500, 2000, 9000}; MaxVersion = 3; one applicant, one manager, one finance",
    "assumptions": ["each click is handled by one request; the database row is the only shared state"],
    "left_out": ["notification e-mail (see unformalized U1)"],
    "states": 425, "seconds": 0.8,
    "verdict_at_sync": "disproved",
    "seen_failing": [
      { "rule": "R2", "variant": "variants/R2-no-withdraw-check.patch", "caught": true }
    ],
    "seen_succeeding": [
      { "goal": "G1", "reached": true, "removed_transition": "Approve", "unreachable_after": true }
    ]
  },

  "model_map": [
    { "part": "Submit",   "cites": ["src/approval/submit.ts:18-31"] },
    { "part": "Approve",  "cites": ["src/approval/approve.ts:52-64"] },
    { "part": "Withdraw", "cites": ["src/approval/withdraw.ts:27-35"] },
    { "part": "Pay",      "cites": ["src/approval/pay.ts:38-47"] }
  ],

  "rules": [
    { "id": "R1", "kind": "safety", "name": "PaidMatchesApprovals",
      "text": "付款金額，一定等於主管和財務核准當下的金額。",
      "cites": ["src/approval/pay.ts:41"], "verdict": "violated", "paths": ["P1"] },
    { "id": "R2", "kind": "safety", "name": "NoPayAfterWithdraw",
      "text": "撤回之後，不會再付款。",
      "cites": ["src/approval/withdraw.ts:33", "src/approval/pay.ts:39"], "verdict": "violated", "paths": ["P2"] },
    { "id": "R3", "kind": "safety", "name": "NotStuck",
      "text": "一張申請不會卡在沒有人能動的狀態。",
      "cites": ["src/approval/approve.ts:52"], "verdict": "held", "paths": [] }
  ],

  "goals": [
    { "id": "G1", "text": "一張 2000 元的申請，可以一路走到付款。", "guards": ["R1", "R2", "R3"] }
  ],

  "paths": [
    { "id": "P1", "rule": "R1", "finding": "bug",
      "summary": "改金額後重送，舊的核准還在，用舊核准付了新金額。",
      "script": "paths/P1.md", "steps": 7 },
    { "id": "P2", "rule": "R2", "finding": "bug",
      "summary": "撤回和主管核准同時按下，撤回先寫入、核准後寫入，付款照付。",
      "script": "paths/P2.md", "steps": 5 }
  ],

  "questions": [],

  "unformalized": [
    { "id": "U1", "where": "src/approval/notify.ts:12-30", "class": "cannot-model",
      "detail": "寄通知信依賴外部郵件服務的送達結果。",
      "until": "郵件服務有可建模的送達合約（至少一次／至多一次）",
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
- `sync.files` — keys are repo-relative paths (absolute only for a document outside the repo); exactly the files cited by `model_map` and `rules`.
- `sync.watch[].matched` — sorted; computed with `git grep -l --untracked -E <pattern>` at publish.
- `sync.artifact` — every file in the area except `hypothesis.json` itself.
- `check.verdict_at_sync` — `proved` (all rules `held`) | `disproved` (any `violated`) | `unformalized` (no model; `rules` may be empty).
- `check.seen_failing` — one entry per `safety` rule, `caught: true` required for a `proved` or `disproved` area to be shown as such.
- `check.seen_succeeding` — one entry per goal, both `reached` and `unreachable_after` true; every safety rule appears in some goal's `guards`.
- `rules[].text` / `goals[].text` / `paths[].summary` / `questions[].question` — plain words, no variable or action names; these strings are what readers quote. `paths[].summary` and `questions[].question` are the plain first layer and contain none of 活性、安全性、精化、不變式、同步點、TLC、模型、狀態空間; the technical layer lives in `paths/P<n>.md`.
- `paths[].finding` — `bug` (code), `contradiction` | `gap` (document), `refinement-break` (comparison).
- `questions[]` — documents only: `{ "id", "quote", "location", "ask": "<whom>", "question" }` for every ambiguity.
- `unformalized[]` — the reason record, `templates/reason-record.md`.
- `history[]` — one row per publish after the first, the `--maintain` outcome that produced it.
- `migrated_from` — `null` or the old `.claude/prove-it/formal/<area>/` path.
