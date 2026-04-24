---
name: review
description: Independent multi-perspective re-verification of any model output — code diff, file set, directory, /think's approved plan, a bare claim. Dispatches isolated perspective agents (architecture / quality / security) in clean Task contexts to surface hallucinations, drift, over-engineering, and unnecessary complexity. Findings flow through a four-level response — direct fix for cosmetic stuff, packaged confirm for non-semantic, ask user for judgement, FYI for the rest. Balance check is mandatory on every new-work proposal. Code targets need e2e-run evidence; without it, not finished. Use when a model has just declared something done after a long-running or multi-turn session, or when the user wants a surgical second opinion on a prior actor's work. User-facing output is in Traditional Chinese (繁體中文).
---

# review — cross-perspective re-verification

Models drift. After a model claims "done" — especially after a long-running or multi-turn session — it is the wrong one to audit itself: inertia and context pollution make it confirm its own assumptions. `/review` is the counter-move. Dispatch isolated perspectives in clean Task contexts and let them re-read the target with fresh eyes — but with a surgeon's mindset: find only what matters to the user's actual concern, don't over-correct.

This skill is not a monolithic reviewer. It is a **task analyst + dispatcher**: it lifts a claim checklist out of the target, derives the review's goal, decides who to dispatch, lets them think independently, weighs returned findings on a balance scale (complexity must justify itself), and applies findings in four response tiers.

The body below is English (agent-facing). Wherever this file quotes literal user-facing copy in **Traditional Chinese (繁體中文)**, that text is output-as-shown; everything else is instruction for the agent running the skill.

---

## Three perspectives (agent files)

`plugins/baransu/agents/architecture-reviewer.md` / `quality-reviewer.md` / `security-reviewer.md`.

Each agent file defines `視角 / 目標 / 通用原則 / 禁忌` — no persona, no character voice. Role-play descriptions ("you are a senior X engineer") induce hallucination; we want an angle from which to read the target, not an actor playing a role.

---

## Stage 1 — Claim checklist AND review goal

Two things, in order, both passed to every dispatched reviewer.

### The claim checklist

Write down — in 繁中 — what the target says it did, decided, explicitly did not do, and left open. This is the reviewer's anchor against drifting into free-form critique. If no source exists for a claim (no commit message, no docstring, no plan section), write **「no explicit claim for <area>」** rather than inventing one.

Target can be any shape:
- git diff, file set, directory, uncommitted changes
- a /think 5-section plan or other design document
- a bare claim plus cited code (e.g. "this function is thread-safe" + `path/to/file.py`)

### The review goal

One sentence, in 繁中. Why does the user want this reviewed? Derived from the user's invocation plus the target's visible properties. Examples:
- 「確認這個 PR 沒有把舊的認證流程打壞」
- 「看 /think 的 plan 裡有沒有自我矛盾或偽裝成 unknown 的已決定事項」
- 「驗證 `increment()` 是否真的 thread-safe；如果不是，最小必要修法」

**The goal is the single most important input to reviewer dispatch.** It is what keeps each perspective from drifting into its own bias. Without a goal, an architecture reviewer will find architecture problems regardless of whether they matter to the user's actual concern; a security reviewer will surface every theoretical attack surface regardless of blast radius. With a goal, every perspective has a compass: findings outside the goal's orbit — even when they're correct observations — downgrade to advisory instead of packaging as action items.

This is the mechanism that lets well-meaning perspectives coexist without their individual zeal producing a collectively over-engineered review. It is the fix the skill's own experience taught us (`/review` v0.3.0 drifted because it had no goal mechanism).

---

## Stage 2 — Grade scope

| scale | configuration | adversarial |
|---|---|---|
| ≤ 100 LOC | one perspective (whichever fits target's nature) — quick pass | skip |
| 100–500 LOC | relevant perspectives (usually 2) | run if change crosses layers |
| > 500 LOC | assign applicable perspectives by file spread / layer span | one round |

On borderline cases, round up. For plan-type targets, use "independent decision points × section count" as the LOC analog.

---

## Stage 3 — Activation (target behavior, not invocation keywords)

Whether a perspective activates depends on what the target actually **does**, not which words appear in the user's invocation text:

- **Quality**: target contains executable code, a claim that needs verification, or a plan asserting it did/achieved something.
- **Architecture**: target spans files, introduces a new module boundary, changes a contract; or a plan whose sections depend on each other.
- **Security**: target's behavior touches external input, auth/authz decisions, secret handling, or cross-trust-boundary data flow — not the mere mention of those words.

Plan- or claim-type targets default to architecture + quality; security activates only when the plan materially describes one of the behaviors above.

If Stage 2's tier cap disagrees with activation count (e.g. a 100-LOC target triggers two perspectives), follow activation; the tier column is a guideline ceiling, not a hard limit.

---

## Stage 4 — Parallel dispatch

Launch one **parallel Task** per activated perspective, each in a clean context. Pass each reviewer three things: target content, the **claim checklist** (Stage 1), and the **review goal** (Stage 1). Reviewers do not know about each other and do not coordinate.

Findings return in natural language (not YAML). Each must include: citation (file:line or section), which claim it contradicts (or "none — observation"), the observation itself, the surgical fix, and a balance note (see Stage 6).

---

## Stage 5 — Adversarial round (conditional)

Run for targets > 500 LOC or those crossing layers. One Task, six angles:

1. **Violated assumption** — what unstated premise does the target rely on? Flip one — does the target still hold?
2. **Combinatorial failure** — which combination of inputs / events / states jointly breaks the target, even when each is fine alone?
3. **Chain miscommunication** — each layer locally correct, but meaning corrupted across the chain?
4. **Misuse scenarios** — what does the target do when a non-adversarial user goes off-road?
5. **Root cause vs symptom** — are reviewer findings the actual cause, or visible symptoms of a deeper one?
6. **Consensus hallucination** — if reviewers agree, is that because the claim is true, or because they share training-data priors?

For plan-type targets, translate into plan vocabulary: ambiguous premises, internally inconsistent sections, decision chains, reader-misreading, cause/effect inversion, surface-completeness as hallucination.

Adversarial augments reviewer findings; it does not override.

---

## Stage 6 — Consolidate + balance check

**Deduplicate**: collapse findings with the same citation + same observation, attributing to the narrowest-scope perspective.

**Balance check (mandatory)** — every finding that proposes new work must answer four questions:

1. 不做會得到什麼 / 失去什麼？ (What do we gain/lose by not doing this?)
2. 做了會得到什麼 / 失去什麼？ (What do we gain/lose by doing it?)
3. 有沒有更小、更平衡的中間方案？ (Is there a smaller, more balanced middle option?)
4. **這個 finding 是否服務於本次 review 的 goal？** (Does this serve the review goal, or is it the perspective's own hobby-horse?)

The fourth question is the compass — it is the difference between a review that helps the user and a review that impresses its own reviewers. A valid architecture observation off-goal is still a valid observation; it just belongs in the advisory pile, not the action pile.

**Complexity must justify itself.** Sweeping refactors, "future-proofing" additions, concerns with no concrete reproduction condition, perspective-native obsessions that don't touch the goal — anything failing the four questions drops to advisory. This is the load-bearing principle of the whole skill.

---

## Stage 7 — Four response tiers

| tier | action |
|---|---|
| **Direct fix** | formatter, import order, unused import, obvious typo, dead import. Nothing that touches behavior. Apply via Edit. |
| **Packaged confirm** | non-semantic but beyond direct fix (rename, delete dead code, semantic typo). Present the batch diff once. |
| **Needs judgment** | logic / boundary / API / behavior / security findings with concrete fixes. Batch-ask via AskUserQuestion — group by theme, not by target question count. |
| **Advisory** | balance-downgraded, off-goal, or no concrete fix. In the report, not in the user's face. |

Do not change behavior without user consent. Do not ask one question per finding.

---

## E2E hard requirement

If the target contains executable code, confirm e2e has been run. If no green-run evidence exists in-session, the report says 「未完成，等 e2e」 rather than calling the target done.

For plan / claim / pure-documentation targets, e2e does not apply — note as n/a with one-line reason.

---

## Output shape

Traditional Chinese, natural prose, this shape:

- One-sentence conclusion (完成 / 需要你的判斷 / 未完成)
- Target and scope
- Claim checklist
- Review goal
- Who was dispatched and why
- Findings by tier — 已修 / 待確認 / 需判斷 / 僅供參考
- E2E status

No verdict enum. No YAML schema. No skeleton template — write the kind of review a real engineer would read as a review.

For **needs-judgment** items, batch-ask via AskUserQuestion. Let the question count follow the natural theme grouping; don't split to hit a number, don't merge to shrink one.

---

## Gotchas — two symmetric traps

This skill has tripped on both in one session. They mirror each other and both show up during a live review run as well as during skill editing.

**Trap 1 — Over-correcting from perspective zeal.** During a review run, a perspective naturally finds real-but-off-goal issues and packages them as action items. During skill editing, the equivalent is adding "iron rules" / "what this is NOT" / numeric caps to defend against imagined failures. The fix is the same in both modes: if a finding (or a proposed rule) cannot point to the explicit review goal — or, for edits, to an observed past incident — it stays advisory, or doesn't get added. A reviewer chasing its lane's native concerns without goal anchoring hits this trap.

**Trap 2 — Over-cutting by dropping load-bearing mechanisms.** The mirror image. Mechanisms that look like prose redundancy are sometimes the only thing keeping the machinery anchored. The **goal input** (Stage 1) and the **fourth balance-check question** (Stage 6) are the concrete examples — silently assuming them instead of writing them down produced perspective drift on the first real run. When trimming, every deleted mechanism must be absorbed by something that remains; "implicit" is not a destination. A dispatcher that skips goal derivation and hopes reviewers self-anchor hits this trap.

The warning for maintainers and for invocation-time reviewers is the same: **「複雜度需要證明自己的價值」** for additions, **「精簡不能讓 load-bearing 機制變成默認」** for cuts.

---

## Core constraints

- **Perspective, not persona** — agent files must not contain "you are a senior X" voice.
- **Behavior-based activation** — don't match invocation strings; look at what the target does.
- **Goal-gated findings** — the fourth balance-check question is the compass that stops perspective-specific obsession from producing an over-engineered review.
- **Balance check is mandatory** — a new-work finding earns action-tier placement only by answering the four questions.
- **No behavior changes without consent** — auto-fix stays cosmetic.
- **No recursion** — `/review` does not invoke `/review`; adversarial is one round; reviewers do not review each other.
- **Code target without e2e green-run evidence is not finished.**
