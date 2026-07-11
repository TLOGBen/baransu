# AskUserQuestion 互動規格

This file is the single source of truth for keyword-search lanes that present candidates via AskUserQuestion. The four lanes — `--web`, `--gh`, `--x`, and the upgraded `--topic` — share this spec; their reference files (`web-search.md`, `gh-search.md`, `x-search.md`, `academic-search.md`) reference this file instead of redefining its rules.

## Capacity

- AskUserQuestion's hard ceiling is **4 options per round**.
- Every round reserves **1 slot for an escape option** (label: `「以上都不選」`).
- A round that still has remaining candidates after it additionally reserves **1 slot for the advance option** (label: `「下一批」`), leaving **2 result slots**. The final round (no candidates remain after it) has no advance option and uses **3 result slots**.
- Maximum result slots across the worst case = 2 + 2 + 3 = **7**.

## Result-count to round mapping

| Result count `N` | Rounds | Per-round result slots |
|------------------|--------|------------------------|
| `N ≤ 3` | 1 | `N` (plus escape; no `「下一批」`) |
| `4 ≤ N ≤ 5` | 2 | 2 (+`「下一批」`), then `N - 2` |
| `6 ≤ N ≤ 7` | 3 | 2 (+`「下一批」`), 2 (+`「下一批」`), then `N - 4` |
| `N ≥ 8` | 3 | 2, 2, 3 (truncated to first 7 by lane's native sort order; no local re-ranking) |

Each round always carries the escape option in addition to its result slots (and, on non-final rounds, the advance option).

## Multi-round semantics

- The user picks a single result. Selecting a **result** in any round **terminates the sequence** (single-pick semantics) — the orchestrator does not advance to subsequent rounds for that lane invocation.
- Selecting `「下一批」` does NOT terminate: it advances to the next round (next batch of candidates). It is only present when more candidates remain; without it, rounds ≥ 2 would be unreachable.
- Selecting the escape option is a hard abort (see Escape behaviour) — it never means "show me more".
- The `acquire` phase processes only the single picked candidate.

## Recommended default

- The **top-ranked candidate** (round 1, first result slot, under the lane's native sort order — no local re-ranking) is the deterministic recommended default for every lane. Label its option `「【推薦】」`.
- Under a non-interactive driver, the selection is an **Input PAUSE** per `../../_shared/loop-contract.md` §2: take the recommended default and continue — do not run further rounds — and annotate 「此處採預設：取第 1 名」 in the completion report. See `../loop-pauses.md` for the full classification.

## Escape behaviour

- Selecting `「以上都不選」` in any round terminates the lane immediately.
- No `material/{slug}/` is produced; no `raw/{slug}/` is retained for the search-page intermediate.
- The orchestrator outputs `「使用者放棄選擇」` and stops.

## Cross-lane invariant

- Lanes do **not** apply 1-5 scoring or re-rank candidates locally.
- Lane-side schema-level health checks (e.g. `--x` substring guards) are acquire-stage failures — not candidate scoring — and apply before this file's flow runs.
