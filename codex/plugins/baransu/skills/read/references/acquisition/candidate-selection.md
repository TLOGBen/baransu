# AskUserQuestion 互動規格

This file is the single source of truth for keyword-search lanes that present candidates via AskUserQuestion. The four lanes — `--web`, `--gh`, `--x`, and the upgraded `--topic` — share this spec; their reference files (`web-search.md`, `gh-search.md`, `x-search.md`, `academic-search.md`) reference this file instead of redefining its rules.

## Capacity

- AskUserQuestion's hard ceiling is **4 options per round**.
- Every round reserves **1 slot for an escape option** (label: `「以上都不選」`). The remaining 3 slots are usable for results.
- Maximum result slots across the worst case = 3 rounds × 3 result slots = **9**.

## Result-count to round mapping

| Result count `N` | Rounds | Per-round result slots |
|------------------|--------|------------------------|
| `N ≤ 3` | 1 | `N` (each result slot fills, plus escape) |
| `4 ≤ N ≤ 6` | 2 | 3, then `N - 3` |
| `7 ≤ N ≤ 9` | 3 | 3, 3, then `N - 6` |
| `N ≥ 10` | 3 | 3, 3, 3 (truncated to first 9 by lane's native sort order; no local re-ranking) |

Each round always carries the escape option in addition to its result slots.

## Multi-round semantics

- The user picks a single result. Selection in any round **terminates the sequence** (single-pick semantics) — the orchestrator does not advance to subsequent rounds for that lane invocation.
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
