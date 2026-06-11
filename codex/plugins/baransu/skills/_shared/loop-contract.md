# loop-contract — skill behavior under non-interactive drivers

> **Self-declaration**: this is a baransu plugin-level convention, **not an
> official standard**（本慣例非官方標準）. Official Claude Code documentation
> does not cover headless / cron driving scenarios (checked 2026-06-10).

## Scope

Applies whenever a baransu skill is driven by a non-interactive context:
`/loop`, `/goal`-style external verifiers, cron, Workflow orchestration, or
any automation harness. Human-present sessions follow platform defaults per
the rule cited below.

---

## 1. PAUSE semantics

Two PAUSE classes (defined here, self-contained — the plugin ships with no
external rule dependency):

- **Input PAUSE** — a preference or confirmation checkpoint (typically an
  AskUserQuestion). Platform modes or `--auto`-style flags may skip it by
  taking the recommended default.
- **Authorization PAUSE** — a hard stop requiring explicit human authorization
  (acceptance gates, publishing actions). Never skippable, on any platform.

Platforms map PAUSE *cost* to their own models (free UX stop on Claude Code
vs billed request on Copilot / Claude.ai); that axis stays platform-owned.
This contract adds an orthogonal axis — the *driving context*. When a
non-interactive driver is detected, the skill behaves as follows regardless
of platform:

- **Input PAUSE** — take the recommended default and continue. The final
  report MUST annotate every substituted decision as 「此處採預設：{假設}」.
- **Authorization PAUSE** — unconditional hard stop. Report `needs input` to
  the driver; never substitute a default.

**Override precedence (explicit)**:

> 驅動上下文覆寫平台預設；Authorization PAUSE 任何情況不可覆寫。

Driving context overrides the platform default mode; an Authorization PAUSE is
never overridable — not by `--auto`, not by driver flags, not by platform mode.

---

## 2. Three hard stops — responsibility boundary

Loop control belongs to the driver; reentrancy and reporting belong to the
skill. Three driver-owned hard stops, explicitly:

| # | Hard stop | Owner | Mechanism |
|---|-----------|-------|-----------|
| 1 | Iteration cap | Driver | `/loop` / Workflow script counts rounds |
| 2 | No-progress detection | Driver | Workflow script compares consecutive outputs |
| 3 | Budget cap | Driver (harness) | harness budget mechanism |

Skill-side obligations (all mandatory):

1. **Re-entrant** — re-invocation must resume or redo safely; repetition never
   corrupts state.
2. **State on disk** — persist working artifacts under `.claude/<skill>/` so
   the driver and the next invocation can observe progress.
3. **Explicit no-progress reporting** — when the skill detects it cannot
   advance, report `no progress: {reason}` instead of silently retrying.

---

## 3. PAUSE classification table

Enumerated from the live SKILL.md of each skill (read at authoring time, not
recalled). Re-verify this table when any listed SKILL.md changes its
interaction points.

### /review

| Interaction point | Class | Non-interactive default |
|---|---|---|
| Stage 7 「Packaged confirm」 — batch diff presented once for confirmation | Input | Do NOT apply the batch; list it in the report as pending-confirm.「此處採預設：不套用，留待人工確認」 |
| Stage 7 「Needs judgment」 — batched AskUserQuestion for logic / boundary / API / behavior / security findings, including hard-stops-sweep pinned findings | **Authorization** | Hard stop. Return verdict 「需判斷」 to the driver with the findings; never auto-apply behavior changes |

### /execute

/execute has no AskUserQuestion. Its user-touch points are escalation notices;
by design it never stops early except Step 0.

| Interaction point | Class | Non-interactive default |
|---|---|---|
| Step 0 — spec dir missing or spec files incomplete → stop + escalate | **Authorization** | Hard stop. No default can substitute a missing /analyze spec |
| §4b task BLOCKED escalations (Red gate ⚠️ / persistent compile error / failure_count ≥ 3 / spec contradiction) | Input | Record BLOCKED, continue unblocked work (per skill's never-stop-early rule), annotate in final-report.md |
| §4d merge escalation (semantic conflict ❌ / Green broken ×3) | Input | Mark downstream groups BLOCKED, continue remaining steps, annotate in final-report.md |
| Step 5 E2E failure path | — (autonomous) | No interaction point in current SKILL.md: e2e-fix-agents once, one re-run, else record ❌ and proceed to Step 6 |

### /learn

| Interaction point | Class | Non-interactive default |
|---|---|---|
| Stage 1 §2 `--topic` — /read paper-selection prompt (surfaced as-is) | Input | Select the top-ranked paper candidate.「此處採預設：取排序最高候選」 |
| Stage 2 §1 — ask for research topic when invocation lacks `--topic` (「請輸入這批資料的研究主題」) | Input | Derive `$TOPIC` from the input slug / URL keywords; annotate the derived value |
| Stage 2 §3 — scoring table confirmation | Input | 全部保留 (keep all scored sources); annotate |
| Stage 3 §2 — outline confirmation before fill-in | Input | Accept the outline as generated; carry any ⚠️ 需補充調查 markers into the report |
| Stage 4 §3 — gap handling (Stage 2 fallback) asks for additional sources | Input | Skip supplementation; keep the section with its ⚠️ marker; annotate the unfilled gap |
| Stage 4 §3.4 — retreat cap choice（繼續 / 跳過此節） | Input | Option 2 跳過此節 (continuing requires human-supplied sources); annotate the skipped section |

learn's terminal stops (Stage 0 environment failures, all-lanes-fail in §3.5)
are error exits, not PAUSEs — the driver receives an explicit failure message.

### /ship

| Interaction point | Class | Non-interactive default |
|---|---|---|
| Step 4 push (`git push origin {branch}`) | **Authorization** | Hard stop. Under loop drive, never auto-push unless a standing user authorization is recorded in the driving context (e.g. the loop prompt or approved plan explicitly authorizes push); absent that record, report `needs input` to the driver |

/ship's push step is interaction-free in human-present sessions (Step 4 pushes
unconditionally), but pushing publishes state beyond the local repo — under a
non-interactive driver it carries Authorization-PAUSE weight.

### /think

| Skill | Loop-drivable? |
|---|---|
| /think | **不可 loop 驅動** — its focusing dialogue is the product; no recommended default can substitute it |
