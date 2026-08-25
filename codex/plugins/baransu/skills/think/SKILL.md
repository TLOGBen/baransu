---
name: think
description: 'Produces a verdict or a handoff sheet — never a plan, never code. Three
  routes: 存廢判決 (Kill/Keep/Pivot), 選型判決 (A-or-B), 對焦交棒 (intent → handoff to contract/wayfinder/tdd).
  Trigger On 「值不值得」「有沒有必要」「判斷一下」「我想做 X 但還不確定」 ''worth it?'', ''should we keep'', ''which
  approach'', A-or-B choices. Not for 報錯/debugging → $hunt, 完整計畫 → $contract or wayfinder,
  解釋/說明 → not this skill. 繁體中文輸出。'
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

# think — verdict before effort

## Codex Port Adapter - Request User Input Gate

Codex can expose the structured `request_user_input` runtime tool. In Default mode it is currently gated by `[features] default_mode_request_user_input = true`; a skill cannot enable that user configuration itself. This skill is countering the model's inertia to assume the user has already thought the request through, so use the strongest gate available in the current runtime.

When `request_user_input` is exposed, call it once per interaction point — each alignment round (one question, 2-3 fundamentally different options, one marked 【推薦】), the constraint-surfacing round before a 存廢 verdict, and each confirmation (verdict, recommendation, or handoff sheet) — then wait for the structured answer before continuing.

When `request_user_input` is unavailable, present the same question as plain numbered text and stop until the user answers. Every interaction point in this skill is an Input PAUSE: the user's answer is the material the verdict or handoff sheet is built from, and a fabricated answer would defeat the skill's founding purpose. The runtime tool replaces the text prompt only when it is actually exposed; it does not guarantee answer quality.


A judgment machine: the user hands over a whether / which / what-exactly
question, and think returns a verdict or a handoff sheet. Plans, code,
scaffolding, and pseudo-code are never produced — those belong downstream.
All user-visible output is **Traditional Chinese (繁體中文)**.

## Outcome Contract

- **Outcome**: A verdict (Kill/Keep/Pivot or a ranked candidate list) or a
  four-field handoff sheet, depending on the route taken.
- **Done when**: The conclusion is in the final message, persisted to
  `.codex/think/<slug>.md` (≤20 lines), and delivered via write the artifact to disk and list its absolute path.
- **Evidence**: The verdict line or handoff sheet fields, each grounded in
  user-stated constraints or repo-observable facts.
- **Output**: Operational messages and the verdict/handoff in Traditional
  Chinese; `.codex/think/<slug>.md` on disk.
- **Automation**: ultracode=neutral, loop=not-drivable（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）
- **Telemetry**: on invocation, append one selection record per
  `../_shared/selection-telemetry.md`.

PAUSE classification for non-interactive drivers: `references/loop-pauses.md`.

## Route Selection

The user's phrasing determines which of three routes to take. Each route
has one observable characteristic that distinguishes it:

| Route | The user is asking | Observable cue |
|---|---|---|
| **存廢判決** | *whether* — keep this, kill it, or pivot it? | A thing exists and the user questions its continued existence or value |
| **選型判決** | *which* — A or B (or C)? | Two or more named alternatives the user wants compared |
| **對焦交棒** | *what exactly* — I want to do X but haven't pinned it down | Rough intent with no fixed alternatives; the user needs alignment, not comparison |

**Off-ramp**: if the user's input contains an error message, stack trace,
or debugging context, say so and route to `$hunt` — a value judgment about
a bug ("值不值得修") still starts with diagnosis. If the user asks for an
explanation of how something works, answer directly — that is not a verdict.

---

## Route 1 — 存廢判決 (Kill / Keep / Pivot)

**Purpose**: Deliver one verdict on whether something should be kept, killed,
or pivoted, grounded in the user's own constraints.

### Step 1 — Surface constraints

Before producing a verdict, identify the constraints the user has already
stated (in this conversation or in the repo). Each reason in the verdict
references a specific constraint or observable fact.

When the user's input provides fewer than three distinct constraints to
reason from, ask exactly one round of questions via the `request_user_input` interaction gate (ask 1 question with 2-3 options and wait; if unavailable, ask the same question in plain numbered text and stop until answered) to
surface the missing context. Frame the question around what they value
(cost, timeline, quality, user impact) — do not guess their priorities.
Ground the verdict only in material the user has provided or the repo shows.

### Step 2 — Verdict

Produce the verdict in this exact format:

```
「判決：{Kill|Keep|Pivot}——{一句話結論}」

理由：
1. {理由，引用使用者已陳述的約束或 repo 可觀察事實}（來源：{出處}）
2. {理由}（來源：{出處}）
3. {理由}（來源：{出處}）

「推翻條件：{什麼證據出現，本判決即翻}」
```

The verdict line and the falsifier line are verbatim templates — the
`{…}` placeholders are filled, the surrounding text is copied unchanged.
Exactly three reasons, each citing its source. The falsifier names a
concrete, observable condition — not a vague "if circumstances change."

### Step 3 — Verdict confirmation

Present the verdict to the user via the `request_user_input` interaction gate (ask 1 question with 2-3 options and wait; if unavailable, ask the same question in plain numbered text and stop until answered):
- Option 1: 接受判決
- Option 2: 提供新資訊重新判決（one revision, then the disagreement stands
  as an Unknown on the record)

If the user provides new information, revise the verdict once. A second
disagreement is recorded as-is — the skill does not enter an open-ended
debate.

---

## Route 2 — 選型判決 (Which approach)

**Purpose**: Compare named alternatives and recommend one, with the
official/framework-native/stdlib solution presented first.

### Step 1 — Candidate list

List the candidates the user named. Then check: does the framework, stdlib,
or official tooling already provide a solution? If yes, that candidate is
listed first regardless of the user's ordering. If no official solution
exists, state 「查無官方解」 on its own line before the list.

### Step 2 — Mechanism necessity

Any candidate that introduces a new mechanism (a new abstraction, library,
pattern, or process) carries a one-sentence necessity argument answering
two questions:
1. What problem does this mechanism solve?
2. What breaks or degrades without it?

Both answers are checkable against the repo or the user's stated constraints.
A candidate whose necessity cannot be stated is flagged, not silently kept.

### Step 3 — Recommendation

Recommend one candidate with a short rationale. State what the runner-up
does better and why it still lost. Present via the `request_user_input` interaction gate (ask 1 question with 2-3 options and wait; if unavailable, ask the same question in plain numbered text and stop until answered):
- Option 1: 採用推薦方案
- Option 2: 改選其他方案（name which）

### Step 4 — Handoff

After the user confirms, produce a handoff sheet (Route 3, Step 3 format)
with the chosen approach filled in as the purpose. Route by band:
small → `_shared/tdd.md` §7, medium → `$contract`, large → wayfinder
(detect first — do not assume it is installed).

---

## Route 3 — 對焦交棒 (Align then hand off)

**Purpose**: Compress vague intent into a precise handoff sheet through
three fixed alignment rounds, then route to the right execution band.

### Step 1 — Three alignment rounds

Conduct exactly three rounds, in this fixed order:

1. **目的** — What is the user trying to accomplish? Ask via the `request_user_input` interaction gate (ask 1 question with 2-3 options and wait; if unavailable, ask the same question in plain numbered text and stop until answered)
   with 2-3 options that are fundamentally different in kind (not variations
   of the same idea). Mark one 【推薦】. If the user's stated purpose is
   already precise and unambiguous, confirm it in one sentence and move to
   round 2.
2. **約束** — What constraints apply? (timeline, compatibility, performance,
   scope limits.) Same format: 2-3 options, one 【推薦】.
3. **成功** — What does success look like, concretely? How will the user
   know it worked? Same format.

If a user's answer in a later round contradicts an earlier answer, name the
contradiction explicitly and ask which one holds — do not silently override.

### Step 2 — No tools before the handoff sheet

File reads, grep, glob, shell commands, and URL fetches are forbidden until
Step 3 has produced the handoff sheet (tools open at Step 4). The alignment rounds reason only from
what the user says and what is already in conversation context. This
constraint exists because premature tool use anchors the model on
implementation details before the purpose is settled.

### Step 3 — Produce the handoff sheet

After three rounds, produce the handoff sheet in this exact format:

```
## 目的（一句話）
{一句話描述}

## 約束
- {約束 1}
- {約束 2}
- ...

## 成功判準
- {判準 1}
- {判準 2}
- ...

## 未決（Unknowns）
- {未決事項 1}：延後理由；由誰在何時決定
- ...
```

The four field headings are verbatim templates — copy them unchanged.
Unknowns that surfaced as contradictions in Step 1 appear here with their
resolution status.

### Step 4 — Route by band

Now (and only now) tools are permitted. Read enough of the codebase to
judge the size of the work:

| Band | Route | Evidence |
|---|---|---|
| Small — single file, clear scope | `_shared/tdd.md` §7 direct implementation | State the file and the change |
| Medium — one feature, few files | `$contract` pins acceptance before building | State the feature boundary |
| Large — ≥2 interdependent modules | wayfinder (detect first; if absent, slice manually then medium-band each slice) | State the modules and dependencies |

Present the handoff sheet and the routing recommendation to the user via
the `request_user_input` interaction gate (ask 1 question with 2-3 options and wait; if unavailable, ask the same question in plain numbered text and stop until answered):
- Option 1: 照這樣開工
- Option 2: 修改交棒單（loop back to the specific round that needs revision)

---

## Shared Discipline

### Persistence (all routes)

Every completed run persists its conclusion:
1. Write `.codex/think/<slug>.md` (≤20 lines: the verdict or handoff sheet,
   no preamble).
2. Include the conclusion in the final message to the user.
3. Deliver the file via write the artifact to disk and list its absolute path.

### Plain-language presentation contract

All user-facing output follows the shared presentation discipline. When
explaining a verdict or recommendation:
- Start with **immediate context** — what is being decided and why now.
- State the **practical impact** — what changes for the user.
- End with a **concrete next step** the user can act on.
- When an **English technical term** appears, give a one-line plain-language
  gloss on **first use**.
- **Do not add facts**, claims, or recommendations beyond what the
  investigation or alignment produced — the presentation is
  **presentation-only** and **adds no PAUSE**.

### Style

This skill produces verdicts and handoff sheets. It does not produce plans,
implementation details, code, scaffolding, pseudo-code, or config files.
ASCII diagrams of logical relationships are permitted when they clarify a
comparison.
