## Contents

- General Rule: Relocate the Tooth, Don't Degrade It
- Tier 0 — Strong Inertia × UI Hard-Stop: Must Relocate the Tooth, Cannot Degrade to a Hint
- Tier 2 — Mechanism Convergence: collect scattered degradations into one table
- Tier 3 — Low Value: degradation is harmless, do it last
- Two Boundaries Running Through the Whole Table (preconditions written into every Codex work item)
- Priority Overview
- Mechanism Placement (grounding basis)

# Codex Port Construction Plan: Rebuilding the Teeth of Anti-Inertia Ballast

> **Positioning**: This is not a "feature mapping checklist", it is a "behavioral-ballast survival checklist".
>
> The essence of each baransu mechanism is a **ballast** that counters some model inertia — not a feature. So the correct question when porting to
> Codex is not "does Codex have an equivalent API", but **"after degrading, is there still enough force to drag the model
> back off that shortcut"**.
>
> Sort key: **whether the tooth is UI-bound × the strength of the inertia it counters**. The most dangerous place to degrade is exactly the place of highest value
> — pull out the only tooth (UI hard-stop), and what you leave the model is precisely the shortcut it most wanted to take.

---

## General Rule: Relocate the Tooth, Don't Degrade It

When the original execution surface (UI hard-stop) cannot be ported, **do not settle for turning it into a prompt hint** — relocate the tooth to
a surface that can survive in Codex. Prefer a verified runtime tool before relocating, but keep a fallback because under-development or feature-gated tools are not portable guarantees. Codex offers these usable surfaces:

- **Structured runtime pause** (`request_user_input`): when exposed, the tool suspends the turn for a structured answer. In Default mode it currently depends on `default_mode_request_user_input`; a skill cannot enable that user setting.
- **File precondition** (artifact-gate): the next step structurally requires the artifact file from the previous step.
- **phase split**: separate the stage that "would cheat the shortcut" from the stage where "there is no shortcut to cheat".
- **sandbox / approval gate**: a deterministic machine gate.

Common principle: **the model cannot talk its way through, because the next step structurally requires the previous step's artifact.**

---

## Tier 0 — Strong Inertia × UI Hard-Stop: Must Relocate the Tooth, Cannot Degrade to a Hint

### T0-1　`/think` Alignment Gate → `request_user_input` + artifact fallback

| Field | Content |
|------|------|
| **Counters** | The model's inertia of "starting to write directly without aligning with the user" |
| **Why** | Claude relies on AskUserQuestion as a hard-stop; plain numbered prose is too soft for the exact inertia `/think` counters. Codex now has `request_user_input`, but Default-mode exposure is under development and config-gated, so treating it as universally present would replace one silent downgrade with another. |
| **Codex action** | When `request_user_input` is exposed, use one sequential structured question per Stage A round. The tool allows only 2-3 authored options, so preserve Stage G's four stable choices through a conditional two-question flow rather than abusing the free-text Other field. When the tool is absent, retain the phase split: Phase 1 asks and stops; Phase 2 requires `alignment.md` and refuses to plan without it. |
| **Done when** | With the tool exposed, Stage A blocks for each structured answer and Stage G reaches all four original outcomes through the conditional flow. Without the tool, an ambiguous requirement still cannot reach the five-section plan without `alignment.md`, and Phase 1 emits no implementation / scaffolding / pseudo-code. |

### T0-2　`/review`, `/health` Isolation Tooth → first verify whether the Codex subagent context is truly isolated

| Field | Content |
|------|------|
| **Counters** | The model's inertia of "self-endorsing, rubber-stamping what it just produced" |
| **Why** | The anti-hallucination value of these two skills *comes from a clean, independent context*. If the Codex subagent shares context with the main process or is weaker, the isolation tooth is blunted — and this cell was never flagged as a risk in the original P-list. **This is a sleeper.** |
| **Codex action** | (a) First run a runtime probe — same review task, confirm whether the Codex subagent gets a fresh context or inherits the main process's memory; (b) if **truly isolated** → port directly, mark green; (c) if **not isolated** → rebuild isolation using "run each perspective in an independent invocation / independent session, write results to files, then aggregate"; do not fake multiple perspectives by asking successive questions within the same context. |
| **Done when** | There is a probe-conclusion document explaining the Codex subagent's isolation level; the Codex versions of review / health settle their port strategy (direct port or session split) according to that conclusion. |

---

## Tier 2 — Mechanism Convergence: collect scattered degradations into one table

### T2-1　capability degradation table (with **execution-strength levels**, not just strategy)

| Field | Content |
|------|------|
| **Counters** | Degradation phrasing written separately across 13 skills; new skills will miss the ballast |
| **Why** | ask_user / send_artifact / browser / tools→mcp are multiple instances of the same pattern. But every cell of the table **must record execution strength** (hard-stop / artifact-gate / soft hint), otherwise "AskUser→plain text" gets mis-marked as half-green. |
| **Codex action** | Build a registry mapping each Claude capability token to `{codex level, strategy, strength of inertia countered}`. transfer.py looks up the table and injects when it scans a token. **Any strong-habit × soft-hint cell is sent back to Tier 0 to take the tooth-relocation route**; leaving only a hint is not allowed. |
| **Done when** | The table exists; any new skill's port inherits the correct level without hand-writing degradation vocabulary; the table can produce a weighted risk list. |

### T2-2　cosmetic AskUser → `request_user_input` with text fallback

| Field | Content |
|------|------|
| **Counters** | None (these are mode selection, not countering inertia) |
| **Why** | The AskUser in `/read`, `/book`, `/design` only selects gen/lint/source, with no behavioral ballast, so degrading is harmless. **Clearly mark as low priority to avoid spending effort in the wrong place.** |
| **Codex action** | Use `request_user_input` with at most 3 questions per call and 2-3 options per question when exposed; split larger batches sequentially. Otherwise list numbered options, stop, and wait for a reply. No artifact-gate is needed for cosmetic selection. |
| **Done when** | After porting all three, the structured menus work when the tool is exposed and the plain-text fallback still stops correctly when it is not. |

---

## Tier 3 — Low Value: degradation is harmless, do it last

### T3-1　`SendUserFile` (review / think) → write the file then list the path

| Field | Content |
|------|------|
| **Counters** | None (pure delivery convenience) |
| **Why** | weak-habit × soft degradation, naturally sorts to the end. |
| **Codex action** | After writing the file, list the absolute path; use an attachment surface when the runtime has one. |
| **Done when** | The file is produced and the path is visible — that's enough. |

---

## Two Boundaries Running Through the Whole Table (preconditions written into every Codex work item)

1. **The ceiling of the goal is "rebuilding the tooth that forces a stop", not "rebuilding the quality of alignment / judgment".** An artifact-gate can guarantee
   "no answer, no going further", but it cannot stop a perfunctory answer — that is a runtime + human problem, not something an adapter can patch.
   Pin this down and you won't fall into the differential-testing abyss.
2. **Separate authorization-PAUSE from input-PAUSE**: the former (acceptance / authorization) stays a hard-stop in any runtime;
   only the latter (option alignment) is eligible for degradation. Almost all 13 skills have a PAUSE; don't cut them all the same way.

---

## Priority Overview

| # | Work Item | Inertia Strength | Tooth Source | Nature |
|----|--------|:---:|------|------|
| 1 | T0-1　think alignment gate | Strong | UI → runtime tool, artifact fallback | preserve tooth |
| 2 | T0-2　review/health isolation verification | Strong | UI → verify runtime | probe first, then decide |
| 3 | T2-1　capability degradation table | mechanism | — | convergence |
| 4 | T2-2　cosmetic AskUser | none | direct degrade | miscellaneous |
| 5 | T3-1　SendUserFile | none | direct degrade | miscellaneous |

---

## Mechanism Placement (grounding basis)

The following is the result of scanning the execution-surface primitives of the canonical skills; this construction plan uses it to place mechanisms on the correct skill:

- **AskUserQuestion**: book, design, hunt, read, review, think
  → among them think is strong inertia (alignment); review/hunt are medium; read/book/design are cosmetic (mode selection).
- **Isolated subagent**: health, review
  → the key to isolation *as a tooth* lies in review / health.
- **Red-green / test-first**: health, hunt, learn, think
- **SendUserFile**: review, think
- **PAUSE / gate**: nearly full coverage across 13 skills → must distinguish authorization vs input PAUSE.
