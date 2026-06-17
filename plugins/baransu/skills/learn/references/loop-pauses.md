# loop-pauses — /learn PAUSE classification

Per-skill PAUSE classification for non-interactive drivers. The cross-cutting
vocabulary and semantics live in `../../_shared/loop-contract.md` (§1 vocabulary,
§2 PAUSE semantics, §3 hard stops); this file enumerates only /learn's own
interaction points. Re-verify when this skill's SKILL.md changes its interaction
points.

| Interaction point | Class | Non-interactive default |
|---|---|---|
| Stage 1 §2 `--topic` — /read paper-selection prompt (surfaced as-is) | Input | Select the top-ranked paper candidate.「此處採預設：取排序最高候選」 |
| Stage 2 §1 — ask for research topic when invocation lacks `--topic` (「請輸入這批資料的研究主題」) | Input | Derive `$TOPIC` from the input slug / URL keywords; annotate the derived value |
| Stage 2 §3 — scoring table confirmation | Input | Keep all scored sources; annotate |
| Stage 3 §2 — outline confirmation before fill-in | Input | Accept the outline as generated; carry any ⚠️ 需補充調查 markers into the report |
| Stage 4 §3 — gap handling (Stage 2 fallback) asks for additional sources | Input | Skip supplementation; keep the section with its ⚠️ marker; annotate the unfilled gap |
| Stage 4 §3.4 — retreat cap choice（繼續 / 跳過此節） | Input | Option 2 跳過此節 (continuing requires human-supplied sources); annotate the skipped section |

learn's terminal stops (Stage 0 environment failures, all-lanes-fail in §3.5)
are error exits, not PAUSEs — the driver receives an explicit failure message.
