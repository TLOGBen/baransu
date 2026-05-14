---
name: review
description: Use When the user wants an independent second opinion on a model's output,
  or after a model declares something done. Do Dispatch isolated architecture / quality
  / security perspective agents in clean Task contexts, surfacing hallucinations,
  drift, and over-engineering. Trigger On 「看一下」「看看」「幫我看」「check 一下」「review 一下」, or
  casual "take a look at X". 繁體中文輸出。
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

# review — cross-perspective re-verification

Models drift. After a model claims "done" — especially after a long-running or multi-turn session — it is the wrong one to audit itself: inertia and context pollution make it confirm its own assumptions. `/review` is the counter-move. Dispatch isolated perspectives in clean Task contexts and let them re-read the target with fresh eyes — but with a surgeon's mindset: find only what matters to the user's actual concern, don't over-correct.

This skill is not a monolithic reviewer. It is a **task analyst + dispatcher**: it lifts a claim checklist out of the target, derives the review's goal, decides who to dispatch, lets them think independently, weighs returned findings on a balance scale (complexity must justify itself), and applies findings in four response tiers.

The body below is English (agent-facing). Wherever this file quotes literal user-facing copy in **Traditional Chinese (繁體中文)**, that text is output-as-shown; everything else is instruction for the agent running the skill.

---

## Four perspectives (agent files)

`plugins/baransu/agents/architecture-reviewer.md` / `quality-reviewer.md` / `security-reviewer.md` / `style-reviewer.md`.

Each agent file defines `Perspective / Mission / Principles / Lane-keeping` — no persona, no character voice. Role-play descriptions ("you are a senior X engineer") induce hallucination; we want an angle from which to read the target, not an actor playing a role.

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

If the dispatcher's first impulse is to skip goal derivation and let reviewers self-anchor, treat that as the load-bearing trap in live-review form. "Implicit goal" is never a destination — every dispatched reviewer must receive a written goal sentence.

---

## Stage 2 — Grade scope

| scale | configuration | adversarial |
|---|---|---|
| ≤ 100 LOC | one perspective (whichever fits target's nature) — quick pass | skip* |
| 100–500 LOC | relevant perspectives (usually 2) | run if change crosses layers |
| > 500 LOC | assign applicable perspectives by file spread / layer span | one round |

*Any semantic risk signal (auth/session/JWT, data mutation, external API integration, payments) overrides skip and adds an adversarial pass regardless of LOC tier.

On borderline cases, round up. For plan-type targets, use "independent decision points × section count" as the LOC analog.

---

## Stage 3 — Activation (target behavior, not invocation keywords)

Whether a perspective activates depends on what the target actually **does**, not which words appear in the user's invocation text:

- **Quality**: target contains executable code, a claim that needs verification, or a plan asserting it did/achieved something.
- **Architecture**: target spans files, introduces a new module boundary, changes a contract; or a plan whose sections depend on each other.
- **Security**: target's behavior touches external input, auth/authz decisions, secret handling, or cross-trust-boundary data flow — not the mere mention of those words.
- **Style**: target is a rendered visual artifact (HTML / PPT / SVG) produced under a baransu design preset (`{project_root}/tokens.css` exists with `/* preset: <slug> */` header). Checks design-fidelity against `{project_root}/DESIGN.md` — typography rules, color palette discipline, Do / Don't items, AI Prompt Guide reproducibility intent. Activates only for visual outputs, not for plain code / plan / data.

Plan- or claim-type targets default to architecture + quality; security activates only when the plan materially describes one of the behaviors above; style activates only when target is rendered visual output with a project-root preset present.

If Stage 2's tier cap disagrees with activation count (e.g. a 100-LOC target triggers two perspectives), follow activation; the tier column is a guideline ceiling, not a hard limit.

---

## Stage 4 — Parallel dispatch

Launch one **parallel Task** per activated perspective, each in a clean context. Pass each reviewer three things: target content, the **claim checklist** (Stage 1), and the **review goal** (Stage 1). Reviewers do not know about each other and do not coordinate.

Findings return in natural language (not YAML). Each must include: citation (file:line or section), which claim it contradicts (or "none — observation"), the observation itself, the surgical fix, and a balance note (see Stage 6).

No recursion: this dispatch is the only depth /review uses. /review does not invoke /review, adversarial (Stage 5) is exactly one round, and reviewers do not review each other.

---

## Stage 5 — Adversarial round (conditional)

Run after all Stage 4 Tasks have returned (not in parallel with Stage 4). Receive Stage 4 findings as inline input — list them in the adversarial reasoning context so angles 5 and 6 have concrete material to work with. Six angles:

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

Before consolidating, re-read this section's four balance-check questions — context accumulates between Stage 4 dispatch and Stage 6 consolidation, and the balance check is the load-bearing mechanism most vulnerable to attention decay.

**Deduplicate**: collapse findings with the same citation + same observation, attributing to the narrowest-scope perspective.

**Balance check (mandatory)** — every finding that proposes new work must answer four questions:

1. 不做會得到什麼 / 失去什麼？ (What do we gain/lose by not doing this?)
2. 做了會得到什麼 / 失去什麼？ (What do we gain/lose by doing it?)
3. 有沒有更小、更平衡的中間方案？ (Is there a smaller, more balanced middle option?)
4. **這個 finding 是否服務於本次 review 的 goal？** (Does this serve the review goal, or is it the perspective's own hobby-horse?)

The fourth question is the compass — it is the difference between a review that helps the user and a review that impresses its own reviewers. A valid architecture observation off-goal is still a valid observation; it just belongs in the advisory pile, not the action pile.

**Complexity must justify itself.** Sweeping refactors, "future-proofing" additions, concerns with no concrete reproduction condition, perspective-native obsessions that don't touch the goal — anything failing the four questions drops to advisory. This is the load-bearing principle of the whole skill.

When a perspective surfaces a real-but-off-goal observation, the load-bearing rule applies: if it cannot be traced back to the explicit review goal, it must drop to advisory, never package as an action item.

The fourth question itself is load-bearing — silently assuming it instead of asking it produced perspective drift on past runs. Treat it as a written check at every consolidation, not as ambient atmosphere.

**Hard-stop ordering.** After balance check completes (findings have been filtered into the action pile and the advisory pile), run the Hard stops sweep below as an aggregate gate over the surviving findings. The sweep does **not** re-do per-finding balance judgment; it checks the report as a whole. Any hit forces the report verdict to 「需判斷」 or 「未完成」 and pins the relevant findings to needs-judgment — they may no longer be balance-downgraded to advisory.

---

## Hard stops sweep

Run after Stage 6 consolidation, per the hard-stop ordering paragraph above. Each item is binary: does the report, taken as a whole, contain evidence of this failure mode? Any hit forces report verdict to 「需判斷」 or 「未完成」; pinned findings cannot be balance-downgraded to advisory. Conditions are observable from target + claim checklist + findings — no inference, no "looks risky".

**Required (4)**:

- **Unverified claims** — the target asserts something was done / verified / tested without in-session evidence (no shell output, no green-run record, no commit pointing to a real fix). Pin the relevant claim-vs-implementation finding to needs-judgment.
- **Destructive auto-execution** — the target marks any operation that modifies user-visible state (history files, config, preferences, installed software, remote state) as "safe" or "auto-run" without explicit confirmation gating. Pin to needs-judgment.
- **Unknown identifier in target** — any function / variable / type / module referenced in the target that does not exist in the codebase (verify by Read / Grep, not by memory). Pin to needs-judgment.
- **Dependency changes** — additions, version bumps, or removals in package.json / Cargo.toml / go.mod / requirements.txt / lockfiles not obviously required by the target's stated goal. Pin to needs-judgment.

**Optional (1)** — list only when `security-reviewer` was not dispatched in Stage 4; otherwise omit, since the perspective already enforces this and listing it here would duplicate the gate:

- **Injection / hardcoded secret** — SQL / command / path injection at system entry points; credentials hardcoded, logged, committed, or copied into public docs. Pin to needs-judgment.

This list deliberately does **not** include release-artifact missing, generated-artifact drift, or version skew — those belong to `/baransu:ship`, not to /review.

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
- Findings by tier — 已修 / 待確認 / 需判斷 / 僅供參考. Themes hit by a Hard stops sweep item must be fully described in the prose; the hard-stops checklist below is a machine-readable companion, never a substitute — do not skip a topic in prose because it will appear in the checklist.
- E2E status

After the prose above, two structured-tail elements (additive — the prose is the body, these are the receipt):

**Hard-stops sweep result** — checklist form. List every Required item from the Hard stops sweep section with its outcome; include the Optional item only when `security-reviewer` was not dispatched. Each line is one of: `□ <item>: not hit` or `☒ <item>: hit — <one-line citation>`.

**Sign-off receipt** — fenced code block, key-value aligned, exactly these eight fields:

```
files:         N (+X -Y) | N/A for plan-type
scope:         on target | drift: [what] | incomplete
depth:         quick | standard | deep
perspectives:  [arch, quality, security, style] + adversarial: yes | no
hard_stops:    N hit ([item, item, ...]) | none
new_tests:     N
doc_debt:      none | <invariant>: <where to record>
e2e_status:    完成 | 未完成等 e2e | n/a
```

Field semantics (single source of truth for each):

- `files`: Stage 2's LOC / file-count classification. Plan-type targets: `N/A`.
- `scope`: scope drift vs claim checklist. Vocabulary: `on target` / `drift: [one-phrase summary]` / `incomplete`.
- `depth`: Stage 2's three-tier classification (`quick` / `standard` / `deep`).
- `perspectives`: the Stage 4 dispatched set, with `+ adversarial: yes|no` from Stage 5. Not Waza's pooled-specialists semantics — quick-pass targets still list ≥1 perspective.
- `hard_stops`: the source of truth for hits. The checklist above is a derived view; if `hard_stops: none` here, all checklist lines must read `□ ... not hit`.
- `new_tests`: pure count. Does **not** carry Waza's "regression-first" semantics — that fidelity is intentionally not inherited; regression-first verification belongs to `/baransu:dev` or `/baransu:execute`, not /review.
- `doc_debt`: invariants the reviewer noticed are missing from project docs (AGENTS / CLAUDE / `.claude/rules`). `none` when nothing surfaced.
- `e2e_status`: three states from the E2E hard requirement section above. The hard-stop checklist's e2e-related line, if any, is **derived** from this field — do not judge e2e independently in the checklist.

No verdict enum. No YAML schema. No skeleton template — write the kind of review a real engineer would read as a review.

For **needs-judgment** items, batch-ask via AskUserQuestion. Let the question count follow the natural theme grouping; don't split to hit a number, don't merge to shrink one.

---

「複雜度需要證明自己的價值」 for additions.
「精簡不能讓 load-bearing 機制變成默認」 for cuts.
