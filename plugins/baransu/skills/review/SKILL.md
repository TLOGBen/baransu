---
name: review
description: >-
  Dispatches isolated architecture / quality / security / style / domain perspective agents in clean Task contexts, surfacing hallucinations, drift, and over-engineering. Use when the user wants an independent second opinion on a model's output, or after a model declares something done. Trigger On 「看一下」「看看」「幫我看」「check 一下」「review 一下」, or casual "take a look at X". Not For auditing the user's own project agent-config / AI-maintainability (route to /health), nor verifying baransu's own skill structure (route to scripts/verify-skills.py). 繁體中文輸出。
---

# review — cross-perspective re-verification

Models drift. After a model claims "done" — especially after a long-running or multi-turn session — it is the wrong one to audit itself: inertia and context pollution make it confirm its own assumptions. `/review` is the counter-move. Dispatch isolated perspectives in clean Task contexts and let them re-read the target with fresh eyes — but with a surgeon's mindset: find only what matters to the user's actual concern, don't over-correct.

This skill is not a monolithic reviewer. It is a **task analyst + dispatcher**: it lifts a claim checklist out of the target, derives the review's goal, decides who to dispatch, lets them think independently, weighs returned findings on a balance scale (complexity must justify itself), and applies findings in four response tiers.

---

## Outcome Contract

- **Outcome**: One cross-perspective independent re-verification of the target; findings are graded into four response tiers after the balance check, converging into a single review report.
- **Done when**: The report contains the eight-field sign-off receipt, and the hard-stops sweep result is listed item-by-item as a checklist (each item not hit, or hit + a one-line citation).
- **Evidence**: The two structured tail elements that close the report — the hard-stops sweep checklist and the eight-field sign-off receipt fenced block.
- **Output**: A Traditional Chinese review report in the conversation (prose body + structured tail), also persisted as an HTML work journal at `.claude/review/<slug>.html` (see the HTML work journal section).
- **Automation**: ultracode=overlap, loop=drivable（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）

## Invariants

These named rules are load-bearing red lines restated here from where they appear inline in the stages below. Each stage points back to its invariant by name; do not weaken any of them.

- **INV-depth**: this dispatch is the only Task depth /review uses — /review never invokes /review, and reviewers never review each other.
- **INV-no-recursion**: if the dispatcher's impulse is to nest another /review (or let a reviewer spawn its own reviewers), then stop — there is exactly one dispatch layer.
- **INV-adversarial-once**: Stage 5 is exactly one round — if it has already run, do not run it again.
- **INV-no-manufacture**: a zero-finding report that states which surfaces were examined is valid; fabricating findings to justify the invocation is forbidden.
- **INV-consent**: never change behavior without user consent.

## Five perspectives (agent files)

`plugins/baransu/agents/architecture-reviewer.md` / `quality-reviewer.md` / `security-reviewer.md` / `style-reviewer.md` / `domain-reviewer.md`.

Each agent file defines `Perspective / Mission / Principles / Lane-keeping` — no persona, no character voice. Role-play descriptions ("you are a senior X engineer") induce hallucination; we want an angle from which to read the target, not an actor playing a role.

---

## Orchestration interface (dual-mode)

When — and only when — the run is Workflow-driven or a system-reminder confirms ultracode, read
`references/orchestration-interface.md` before Stage 1 and apply its adapter contract; on the
default interactive path, skip the read and write no mode record — the absence of a mode record
means the current (parallel-Task) adapter.

---

## Stage 1 — Claim checklist AND review goal

### Pre-dispatch off-ramp

Before materializing anything: if the invocation matches a frontmatter Not-For boundary (own-project agent-config audit → /health; baransu structure verification → scripts/verify-skills.py), name the correct route and stop — dispatch nothing. The same name-the-route-and-stop semantics apply to two adjacent confusion surfaces: a symptom/error-debugging ask (e.g. 「看一下為什麼報錯」) → /hunt; a capture-to-offline intent (e.g. 「幫我存下來」) → /read. If no target can be materialized from disk (no diff, no file, no named artifact), ask exactly ONE AskUserQuestion to pin the target; if the user cannot name one, stop without dispatching — never review from conversation memory.

Two things, in order, both passed to every dispatched reviewer.

### The claim checklist

Materialize the target from disk first (`git diff --stat` + content for code, Read for files/plans), then write down — in 繁中 — what the target claims it did, decided, explicitly did not do, and left open, against that artifact — conversation memory and commit messages are claims about it, not sources. This is the reviewer's anchor against drifting into free-form critique. If no source exists for a claim (no commit message, no docstring, no plan section), write **「no explicit claim for <area>」** rather than inventing one.

**Quantitative-claim disposition (mandatory, output-shaping).** Every load-bearing count / existence / coverage claim the target makes — N files / N classes / N call-sites / N test-cases / 「X 存在」 / 「安全網充足」 — enters the checklist with an explicit `✔`/`✘` disposition, never a bare restatement. Each disposition is set from its Stage 1.6 fact-table row — the `✔`/`✘` is that row's verdict, cited by its row number, never a free-standing judgment; a `(verified:)` tag the target already carries is a claim about the repo, not evidence, and does not discharge the row. A quantitative `✔`/`✘` carrying no fact-table row number, or a load-bearing count with no row at all, is an Unverified-claims hard-stop hit.

Target can be any shape:
- git diff, file set, directory, uncommitted changes
- a /think 5-section plan or other design document
- a bare claim plus cited code (e.g. "this function is thread-safe" + `path/to/file.py`)

### The review goal

One sentence, in 繁中. Why does the user want this reviewed? Derived from the user's invocation plus the target's visible properties. Examples:
- 「確認這個 PR 沒有把舊的認證流程打壞」
- 「看 /think 的 plan 裡有沒有自我矛盾或偽裝成 unknown 的已決定事項」
- 「驗證 `increment()` 是否真的 thread-safe；如果不是，最小必要修法」

**The goal is the single most important input to reviewer dispatch.** It is what keeps each perspective from drifting into its own bias.

This is the mechanism that lets well-meaning perspectives coexist without their individual zeal producing a collectively over-engineered review.

If the dispatcher's first impulse is to skip goal derivation and let reviewers self-anchor, treat that as the load-bearing trap in live-review form. "Implicit goal" is never a destination — every dispatched reviewer must receive a written goal sentence.

---

## Stage 1.5 — Domain grounding (business-behavior targets)

Runs only when the target **claims business behavior** — a test-case set, a business spec, or any artifact asserting states / transitions / preconditions of a business flow. A plan claims business behavior whenever it asserts *any* state transition, decision / approval path, or event fired on a transition (e.g. 推關 / 決行 / 代決 / auto-sign, or 「this refactor preserves behavior X」), even when its headline frames the work as a purely structural refactor — a business-flow claim wrapped in refactor or count vocabulary still triggers this stage. The judgment is about what the target *does*, never about which keywords appear in the invocation text — a non-business target (pure structure, no transition claim) must not trigger this stage, so no false positives are manufactured. All other targets skip straight to Stage 2 unchanged. Once the table is built, every transition the target *asserts* is checked against the upstream state-producing flow per the authority ranking below; an asserted path the upstream flow cannot produce, or an upstream-reachable path the target omits, is a domain finding.

When it triggers, the dispatcher materializes a **state × event × precondition transition table** for the claimed business flow, BEFORE Stage 4 dispatch. Authority ranking for table sources is fixed: spec / requirement documents plus upstream state-producing flows **outrank** the code under test. Rationale in one line: a test case that needs manual DB setup to reach its initial state is itself evidence that the code under test does not guard that state — the code's acceptance defines nothing about reachability. The code under test may corroborate a transition's *effect*, never which states are legal or reachable; a state combination the code accepts but no spec or upstream flow can produce is marked unreachable (or inferred), not legalized.

Every table row carries a source annotation at section granularity: `(verified: <doc §section / file:line>)` or `(inferred: 未實查)`.

If sources are insufficient (no spec found, upstream flow code unavailable): in interactive sessions, ask exactly ONE AskUserQuestion round to obtain sources. If sources remain insufficient after that round, do not dispatch domain-reviewer, and the report must not claim domain coverage — the Hard stops sweep enforces this outcome.

---

## Stage 1.6 — Fact table (load-bearing quantitative claims)

Between the claim checklist (Stage 1) and dispatch (Stage 4), the dispatcher builds a **fact table** for every load-bearing quantitative / existence claim the checklist carries — N files / N classes / N call-sites / N test-cases / a framework-identity claim / 「X 存在」. Build it per `plugins/baransu/skills/_shared/fact-check.md`: pick the category whose canonical command template backs the claim's noun and fill the row by running `plugins/baransu/skills/review/scripts/fact-count.sh` (the executable form of the templates) when a shell is available, or the verbatim template otherwise — NEVER by re-running the target's own command: the target's command proves reproducibility, not noun-correctness, and a row filled from it is a template-deviation ✘. Paste the raw output fragment into the row. The row shape and the five categories are defined there — apply them, do not restate them here.

This table is the sole evidence store for quantitative verdicts: the Stage 1 `✔`/`✘` disposition and the Output-shape claim table each cite its row numbers, and a quantitative verdict citing no row is an Unverified-claims hard-stop hit. When the environment cannot run the commands, apply fact-check.md's fail-closed rule — every such claim is unverifiable-by-harness and the Unverified-claims hard stop fires; never fail open.

---

## Stage 2 — Grade scope

| scale | configuration | adversarial |
|---|---|---|
| ≤ 100 LOC | one perspective, selected by the Stage 3 activation rule that matches the target type (executable code → quality; multi-file/contract change → architecture; rendered visual artifact → style); if two activation rules match, pick the one whose criterion the target hits most directly — quick pass | skip* |
| 100–500 LOC | dispatch exactly the perspectives whose Stage 3 activation criterion the target hits; if the count is 0, default to quality; if ≥3, keep all that activate (the tier cap is a ceiling, not a target) | run if change crosses layers |
| > 500 LOC | assign applicable perspectives by file spread / layer span | one round |

*Any semantic risk signal (auth/session/JWT, data mutation, external API integration, payments) overrides skip and adds an adversarial pass regardless of LOC tier.

**Domain exception**: when the target claims business behavior (Stage 1.5 / Stage 3 Domain criterion), domain activation is not compressed by the LOC tier — the ≤ 100 LOC single-perspective quick-pass cap does not squeeze it out; domain dispatches in addition to the tier's selection.

On borderline cases, round up. For plan-type targets, use "independent decision points × section count" as the LOC analog.

---

## Stage 3 — Activation (target behavior, not invocation keywords)

Whether a perspective activates depends on what the target actually **does**, not which words appear in the user's invocation text:

- **Quality**: target contains executable code, a claim that needs verification, or a plan asserting it did/achieved something.
- **Architecture**: target spans files, introduces a new module boundary, changes a contract; or a plan whose sections depend on each other.
- **Security**: target's behavior touches external input, auth/authz decisions, secret handling, or cross-trust-boundary data flow — not the mere mention of those words.
- **Style**: target is a rendered visual artifact (HTML / PPT / SVG) produced under a baransu design preset (`{project_root}/tokens.css` exists with `/* preset: <slug> */` header). Checks design-fidelity against `{project_root}/DESIGN.md` — typography rules, color palette discipline, Do / Don't items, AI Prompt Guide reproducibility intent. Activates only for visual outputs, not for plain code / plan / data.
- **Domain**: target claims business behavior — it asserts states / transitions / preconditions of a business flow (test-case sets, business specs, changes claiming state-machine behavior). Judged by what the target does, never by invocation keywords, per the same criterion as Stage 1.5. A plain code diff, doc, or plan with no business-state claim does not activate it — non-business targets take the existing paths above unchanged, and no false positives are manufactured.

Plan- or claim-type targets default to architecture + quality; security activates only when the plan materially describes one of the behaviors above; style activates only when target is rendered visual output with a project-root preset present.

If Stage 2's tier cap disagrees with activation count (e.g. a 100-LOC target triggers two perspectives), follow activation; the tier column is a guideline ceiling, not a hard limit.

---

## Stage 4 — Parallel dispatch

Launch one **parallel Task** per activated perspective, each in a clean context. Pass each reviewer three things: target content, the **claim checklist** (Stage 1), and the **review goal** (Stage 1). Reviewers do not know about each other and do not coordinate. The domain transition table (Stage 1.5) is added to the dispatch input of domain-reviewer only — a fourth input for that one perspective; the other four perspectives keep receiving exactly the three things above. The Stage 1.6 fact table travels WITH the claim checklist to every perspective: reviewers re-interpret its rows — and may flag a row whose category or pattern mismatches its noun — instead of producing their own counts; only when no fact table exists (standalone perspective use) does a reviewer apply `plugins/baransu/skills/_shared/fact-check.md` directly.

Findings return in natural language (not YAML). Each must include: citation (file:line or section), which claim it contradicts (or "none — observation"), the observation itself, the surgical fix, and a balance note (see Stage 6). Any non-obvious claim inside a finding carries a source annotation — `(verified: <how>)` when the reviewer actually checked, or `(inferred: 未實查)` when it rests on reasoning alone.

No recursion (**INV-no-recursion**): this dispatch is the only depth /review uses (**INV-depth**) — /review does not invoke /review, adversarial (Stage 5) is exactly one round (**INV-adversarial-once**), and reviewers do not review each other.

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

This stage runs exactly once (**INV-adversarial-once**). Adversarial augments reviewer findings; it does not override.

---

## Stage 6 — Consolidate + balance check

Before consolidating, re-read this section's four balance-check questions — context accumulates between Stage 4 dispatch and Stage 6 consolidation, and the balance check is the load-bearing mechanism most vulnerable to attention decay.

### Finding Quality Gate

Before any finding enters consolidation, it passes four quality questions. This gate is **separate from the balance check below**: the gate asks whether a finding is *real*; the balance check asks whether it is *worth acting on*. Passing one never implies the other.

1. Can it cite a concrete location (file:line, or section for plan-type targets)?
2. Can it describe a triggering input — a concrete condition under which the problem actually manifests?
3. Did the reviewer read the upstream/downstream context, not just the cited lines?
4. Does the claimed severity hold when restated against that evidence?

HIGH / CRITICAL findings additionally require **three pieces of evidence** (e.g. citation + triggering input + contradicted claim or reproduction record). A finding that fails any question downgrades one tier or drops entirely — nothing passes through "just in case".

「乾淨的 review 是有效的 review — 零發現配上明說的審查面就是完整輸出」。A zero-finding report that states exactly which surfaces were examined is a complete, valid deliverable. Manufacturing findings to justify the invocation is prohibited (**INV-no-manufacture**).

**Deduplicate**: collapse findings with the same citation + same observation, attributing to the narrowest-scope perspective.

**Balance check (mandatory)** — every finding that proposes new work must answer four questions:

1. 不做會得到什麼 / 失去什麼？ (What do we gain/lose by not doing this?)
2. 做了會得到什麼 / 失去什麼？ (What do we gain/lose by doing it?)
3. 有沒有更小、更平衡的中間方案？ (Is there a smaller, more balanced middle option?)
4. **這個 finding 是否服務於本次 review 的 goal？** (Does this serve the review goal, or is it the perspective's own hobby-horse?)

The fourth question is the compass — it is the difference between a review that helps the user and a review that impresses its own reviewers. A valid architecture observation off-goal is still a valid observation; it just belongs in the advisory pile, not the action pile.

**Complexity must justify itself.** Sweeping refactors, "future-proofing" additions, concerns with no concrete reproduction condition, perspective-native obsessions that don't touch the goal — anything failing the four questions drops to advisory. This is the load-bearing principle of the whole skill.

**Mechanism necessity — a finding that proposes new mechanism must clear one more bar.** Does the added complexity actually solve the problem or reach the goal, or does it only add weight whose sole product is a failure log — "I failed here" — that solves nothing, advances no progress, completes no milestone? Detection or narration of a failure the mechanism cannot prevent does not justify its complexity. Beware especially the recommendation that stacks another rule *inside* the same path that just failed (so the failing path can simply skip it too): prefer removing the trigger or proving the fix needs a lever outside the failing system over endorsing one more skippable layer. A reviewer who keeps proposing mechanism is at risk of the same trap the target fell into — adding complexity in place of a fix.

When a perspective surfaces a real-but-off-goal observation, the load-bearing rule applies: if it cannot be traced back to the explicit review goal, it must drop to advisory, never package as an action item.

The fourth question itself is load-bearing — silently assuming it instead of asking it produced perspective drift on past runs. Treat it as a written check at every consolidation, not as ambient atmosphere.

**Dispatcher == author.** When this session performed Edit/Write on the target files, or the target artifact was produced in this conversation, a finding that contradicts an authoring decision made in this session may not be balance-downgraded to advisory by this session alone — it routes to the needs-judgment tier instead.

**Hard-stop ordering.** After balance check completes (findings have been filtered into the action pile and the advisory pile), run the Hard stops sweep below as an aggregate gate over the surviving findings. The sweep does **not** re-do per-finding balance judgment; it checks the report as a whole. Any hit forces the report verdict to 「需判斷」 or 「未完成」 and pins the relevant findings to needs-judgment — they may no longer be balance-downgraded to advisory.

---

## Hard stops sweep

Run after Stage 6 consolidation, per the hard-stop ordering paragraph above. Each item is binary: does the report, taken as a whole, contain evidence of this failure mode? Any hit forces report verdict to 「需判斷」 or 「未完成」; pinned findings cannot be balance-downgraded to advisory. Conditions are observable from target + claim checklist + findings — no inference, no "looks risky".

**Required (5)**:

- **Unverified claims** — the target asserts something was done / verified / tested without in-session evidence (no shell output, no green-run record, no commit pointing to a real fix); OR a load-bearing count / existence / coverage claim the target tags `(verified:)` was not independently re-run this session, or re-ran to a different number or a different counted noun (file vs class vs call-site vs test-case), or was 'verified' by re-running the target's own command instead of the category's canonical template (template-deviation). A tag the target wrote is not in-session evidence — only the review's own re-run is. Pin the relevant claim-vs-implementation finding to needs-judgment.
- **Destructive auto-execution** — the target marks any operation that modifies user-visible state (history files, config, preferences, installed software, remote state) as "safe" or "auto-run" without explicit confirmation gating. Pin to needs-judgment.
- **Unknown identifier in target** — any function / variable / type / module referenced in the target that does not exist in the codebase (verify by Read / Grep, not by memory). Pin to needs-judgment.
- **Dependency changes** — additions, version bumps, or removals in package.json / Cargo.toml / go.mod / requirements.txt / lockfiles not obviously required by the target's stated goal. Pin to needs-judgment.
- **Domain grounding missing** — the target claims business behavior (per the Stage 1.5 / Stage 3 Domain criteria) but the report carries no domain transition table (never built, or sources still insufficient after the one-question round); a hit forces the verdict to 需判斷 or 未完成 and the report may not claim domain coverage, while non-business targets (no business-state claim) never hit this entry. Pin the relevant findings to needs-judgment — not balance-downgradable.

**Optional (1)** — list unless `security-reviewer` returned usable findings in Stage 4; when it did, omit, since the perspective already enforces this and listing it here would duplicate the gate:

- **Injection / hardcoded secret** — SQL / command / path injection at system entry points; credentials hardcoded, logged, committed, or copied into public docs. Pin to needs-judgment.

This list deliberately does **not** include release-artifact missing, generated-artifact drift, or version skew — those belong to `/baransu:ship`, not to /review.

---

## Stage 7 — Four response tiers

| tier | action |
|---|---|
| **Direct fix** | formatter, import order, unused import, obvious typo, dead import. Apply via Edit only when behavior-freedom is verifiable from the artifact (e.g. Grep confirms no side-effect import); any doubt demotes the item to packaged confirm with the skip noted. After applying, re-run the narrowest in-session verification covering the touched files. |
| **Packaged confirm** | non-semantic but beyond direct fix (rename, delete dead code, semantic typo). Present the batch diff once. |
| **Needs judgment** | logic / boundary / API / behavior / security findings with concrete fixes. Batch-ask via AskUserQuestion — group by theme, not by target question count. |
| **Advisory** | balance-downgraded, off-goal, or no concrete fix. In the report, not in the user's face. |

Per **INV-consent**, never change behavior without user consent. Do not ask one question per finding.

PAUSE classification for non-interactive drivers: `references/loop-pauses.md` — read it when driven by /loop, cron, or Workflow.

---

## E2E hard requirement

If the target contains executable code, confirm e2e has been run. E2e evidence means the changed flow was exercised at its real surface — a CLI invocation, an HTTP request/response, a rendered page, or a driven UI; a green unit-test or typecheck run is a proxy and does not qualify. If no such evidence exists in-session, the report says 「未完成，等 e2e」 rather than calling the target done, and `e2e_status` derives from this definition.

For plan / claim / pure-documentation targets, e2e does not apply — note as n/a with one-line reason.

---

## Output shape

Traditional Chinese, natural prose, this shape:

- One-sentence conclusion (完成 / 需要你的判斷 / 未完成)
- Target and scope
- Claim checklist — when the target carries counts / existence / coverage claims, render it as a table with a per-claim 實查結果 column: each load-bearing quantitative claim shows `✔`/`✘` plus the number the review re-ran AND the Stage 1.6 fact-table row it cites — a quantitative verdict with no cited row is an Unverified-claims hard-stop hit — never a bare echo of the target's figure
- Review goal
- Who was dispatched and why; when dispatcher == author (this session edited the target or produced it), disclose that here
- Findings by tier — 已修 / 待確認 / 需判斷 / 僅供參考. Themes hit by a Hard stops sweep item must be fully described in the prose; the hard-stops checklist below is a machine-readable companion, never a substitute — do not skip a topic in prose because it will appear in the checklist.
- E2E status

Throughout the report, non-obvious claims carry a source annotation — `(verified: <how>)` or `(inferred: 未實查)`.

After the prose above, two structured-tail elements (additive — the prose is the body, these are the receipt):

**Hard-stops sweep result** — checklist form. List every Required item from the Hard stops sweep section with its outcome; include the Optional item unless `security-reviewer` returned usable findings. Each line is one of: `□ <item>: not hit` or `☒ <item>: hit — <one-line citation>`.

**Sign-off receipt** — fenced code block, key-value aligned, exactly these eight fields:

```
files:         N (+X -Y) | N/A for plan-type
scope:         on target | drift: [what] | incomplete
depth:         quick | standard | deep
perspectives:  [arch, quality, security, style, domain] + adversarial: yes | no
hard_stops:    N hit ([item, item, ...]) | none
new_tests:     N
doc_debt:      none | <invariant>: <where to record>
e2e_status:    完成 | 未完成等 e2e | n/a
```

Field semantics (single source of truth for each):

- `files`: Stage 2's LOC / file-count classification, measured via `git diff --stat` / `wc -l` at Stage 2 — never estimated. Plan-type targets: `N/A`.
- `scope`: scope drift vs claim checklist. Vocabulary: `on target` / `drift: [one-phrase summary]` / `incomplete`.
- `depth`: Stage 2's three-tier classification (`quick` / `standard` / `deep`).
- `perspectives`: the Stage 4 returned set — a dispatched-but-failed perspective is listed as `<name>: dispatch failed` and its coverage may not be claimed — with `+ adversarial: yes|no` from Stage 5. Quick-pass targets still list ≥1 perspective.
- `hard_stops`: the source of truth for hits. The checklist above is a derived view; if `hard_stops: none` here, all checklist lines must read `□ ... not hit`.
- `new_tests`: pure count. Regression-first verification belongs to 「/baransu:execute 或依 tdd.md 的直接實作」, not /review.
- `doc_debt`: invariants the reviewer noticed are missing from project docs (AGENTS / CLAUDE / `.claude/rules`). `none` when nothing surfaced.
- `e2e_status`: three states from the E2E hard requirement section above. The hard-stop checklist's e2e-related line, if any, is **derived** from this field — do not judge e2e independently in the checklist.

No verdict enum. No YAML schema. No skeleton template — write the kind of review a real engineer would read as a review.

For **needs-judgment** items, batch-ask via AskUserQuestion. Let the question count follow the natural theme grouping; don't split to hit a number, don't merge to shrink one.

---

## HTML work journal

After the report has been presented in conversation, persist it as an HTML work journal:

1. Render the full report as a single HTML file at `.claude/review/<slug>.html`, styled after the book golden-template. The shared rendering contract lives at `plugins/baransu/skills/_shared/output-journal.md` — follow it.
2. Include an 「執行日誌」 section: off-spec decisions, forced changes, tradeoffs, and anything else from this run the user should know.
3. Send the file to the user via SendUserFile.

The in-conversation prose remains the primary deliverable; the HTML journal is its persisted, shareable form.

---

「複雜度需要證明自己的價值」 for additions.
「精簡不能讓 load-bearing 機制變成默認」 for cuts.
