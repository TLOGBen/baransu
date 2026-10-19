---
name: baransu-way
description: "Takes a goal, grounds it with $baransu:how and $baransu:why, picks the lightest route — one skill or a chain like think → draft → review → prove-it → ship — and on one sentence of authorization drives it to the end, stopping only where a person must decide. Trigger On '$baransu:baransu-way', '平衡之道', '全自動', '一路跑完', '幫我串起來', '該用哪個 skill', '從頭做到完', 'run it end to end'. Not for a skill you already know to call (call it directly) or a multi-session campaign (common strategic-advance)."
argument-hint: "[goal | 繼續 | ledger slug]"
---

# baransu-way — the way of balance

Balance is knowing when to go light and when lightness is not allowed. This skill applies that judgment to a whole run: how much process a goal needs, which baransu skills carry it and in what order, and, when the user authorizes it, carrying the run through every leg without being called again. It is the driver `../_shared/loop-contract.md` names: it owns the route, the ledger, and the authorization. Each leg is the real skill doing its own work under its own rules. It writes no spec, adds no gate, and never does a leg's work in place of the leg.

Two defaults this skill corrects. Handed a goal, the model either runs straight to code, skipping the leg that would have caught the wrong direction, or, handed a toolbox, runs every tool every time. And in a chain it either stops at each skill's end to ask for the obvious next step, or pushes through a stop that was the user's to make.

All user-facing output is in Traditional Chinese; keep skill names, paths, and technical terms in English, and explain a term where it first appears.

## Codex Port Adapter - Running a Leg

A Codex skill cannot call another skill mid-turn; a `$baransu:<skill>` mention only selects a skill when the user writes it. Run each leg by reading `../<skill>/SKILL.md` in full and following it in this session, the way `$baransu:think` reads `../show-me/SKILL.md` — including that skill's own Codex Port Adapter sections, so its agent dispatch (`fork_turns="none"`) and its user-input gate stay as that skill defines them. When a stop needs the user and `request_user_input` is exposed, ask through it; otherwise ask in plain text and end the turn.

## Outcome Contract

- **Outcome**: The goal carried through the lightest route that fits it: one leg handed straight to its skill, or a chain driven leg by leg to the endpoint the user authorized, every stop on the way being a user decision or a reason listed under Stops.
- **Done when**: The route was chosen after grounding, or the skip was stated; for a chain, the route card was shown, the authorization was recorded verbatim in the ledger, every leg ended in its own skill's artifact or verdict and was read before the next began, every substituted default is listed, and the run ended at its endpoint, at a stop, or blocked, reported with the ledger path.
- **Evidence**: The ledger — route, authorization, and per leg its status, artifact path, HEAD sha, and working-tree hash — and each leg's own evidence.
- **Output**: Traditional Chinese conversation; for a chain, the ledger at `.codex/baransu-way/<slug>.md` as `references/ledger.md` lays out (one leg writes none). `$baransu:ship` archives that directory.
- **Automation**: ultracode=neutral, loop=not-drivable（it is itself the driver: it holds the authorization and the stops, and a second driver wrapped around it would hold them twice）
- **Telemetry**: on invocation, append one selection record per `../_shared/selection-telemetry.md`; a route found wrong mid-run is a `"miss": true` record.

## 1. Every run

- **Ground with `$baransu:how`, and `$baransu:why` when the past matters.** Before choosing a route whose first leg touches existing code, work out how the affected area runs the way `../how/SKILL.md` does, in this session when it fits one reading. When the goal reshapes, reverts, or regresses something an earlier decision made, also work out why it has its shape the way `../why/SKILL.md` does, so that decision becomes a constraint rather than a guess. Hand both answers to the next leg as its grounding — think's restatement, draft's step 1, hunt's hypotheses — so nothing is read twice. Skip only for greenfield work, writing, or a goal that touches no code, and say so. A goal that is itself "how does X work" or "why is X this way" is the route, not its grounding.
- **Classify a fork before asking.** If a read, a run, or a throwaway sketch could settle it, it is not the user's question: settle it — the code for a fact, `$baransu:prove-it` for behaviour. Ask only for a value, budget, or authority call no experiment settles. Under an authorization, a call the authorization covers is decided and reported, not asked.
- **Name the principle.** In the reply, name each bedrock principle that shaped a decision and the choice it changed; cite only principles whose file was read this run.
- **Own every leg's result.** A leg's own "done" is a claim. Read its artifact or verdict before the next leg starts, and start the next leg from what the artifact shows.
- **Run only what the goal needs.** Copy the route's steps into the task list before any task-specific item; a step not run stays there with `skip: <reason>`.

## 2. Principles — the bedrock

The bedrock is the set of statements `$baransu:review` judges by, in `../review/references/principles/`. Building toward the same statements the closing review checks is what keeps the route honest: the work aims at what it will be judged on. Read the file in full for any principle you apply.

| File | Apply when |
|---|---|
| `goal.md` | Always: when choosing the route, and again before each leg — what was asked, nothing added, nothing narrowed. |
| `evidence.md` | Always: before relying on any claim, a leg's report included. |
| `single-source.md` | The work changes a name, value, rule, or promise stated or mirrored elsewhere. |
| `blast-radius.md` | The work changes behaviour something else relies on; it also decides whether the route needs `$baransu:prove-it`. |
| `risk.md` | The work writes, deletes, migrates, retries, runs concurrently, or is hard to undo; it also decides which Stops apply. |
| `structure.md` | The work adds or moves a module, layer, interface, state owner, or dependency; this is what sends a route through `$baransu:draft`. |
| `taste.md` | Writing code: the smallest complete change, in the repo's own way. |
| `readability.md` | The work adds indirection, state, or names a reader must hold. |
| `tests.md` | Writing, changing, keeping, or relying on a test; pairs with `../_shared/tdd.md`, which every build leg follows. |
| `domain.md` | The work encodes business states, rules, or terms; pairs with `$baransu:domain-modeling`. |
| `trust-boundary.md` | Data, a credential, or a command crosses into the system or leaves it. |
| `performance.md` | The work touches a loop over data, I/O, a query, startup, a hot path, or claims a speed. |

Beside them: `../_shared/modeling.md` when a quantity is at stake, `../_shared/fact-check.md` when a count or an absence is claimed, and `../../rules/anti-patterns.md` for every leg.

## 3. Watch for

- **Process is not progress.** A full chain on a small change is the failure this plugin exists against. Route by what the goal needs, not by what the toolbox holds; move up a band only on evidence — a second module, a second writer — and record the miss.
- **A leg that agrees with itself.** The session that wrote the work earns no independent pass on it. Review legs dispatch a fresh reviewer as `$baransu:review` does; a self-check is never reported as a review.
- **Defaults that pile up quietly.** Each substituted default goes into the ledger when it is taken, never reconstructed at the end.
- **A stale resume.** Work done outside the run since the last leg invalidates what that leg verified; Resume checks for it.
- **Review ping-pong.** The same finding twice, or two fix rounds on one review leg without a clean verdict, ends the leg as blocked.
- **Authorization creep.** 「全自動」 alone covers moving between legs. It never covers a push, an effect outside this machine, or a choice that is the user's.
- **A long context.** The ledger on disk is the run's memory; after compaction or in a fresh session, resume from it, not from recollection.

## 4. Choose the route

Classify the goal by band — small, medium, large, as `references/routes.md` defines them — and by shape, then open the matching route there.

- **One leg.** Say which skill and why in one line, then run it. No card, no ledger.
- **Two or more legs.** Show the route card: each leg's skill, what it leaves behind, and where it may stop. Ask for the endpoint unless the user's message already named one.
- **No route fits.** Say so, take the closest route, and name each step changed and why.

## 5. Drive a chain

- **Authorization.** Record the user's sentence verbatim in the ledger. It names the endpoint（「跑到 review」「全自動跑完」「跑到 ship main」）. Inside the endpoint it is a standing authorization under `../_shared/loop-contract.md` §2, and each leg runs under its own `references/loop-pauses.md`: an Input point takes its recommended default and is recorded 「此處採預設：{假設}」; an Authorization point proceeds only where that table marks it standing-authorizable and the sentence names the action — a push names its branch, an effect outside this machine names that effect.
- **think runs with the user.** When the direction is undecided the route opens with `$baransu:think`, whose restatement dialogue cannot be defaulted (`../think/references/loop-pauses.md`); run it interactively. Once the user confirms the restatement, an authorization given before or at that point carries the rest, unless the plan's Unknowns hold a decision that is the user's — then stop there.
- **Between legs.** Write the leg's status and artifact into the ledger, read the artifact, and start the next leg with it as input. Do not end the turn between legs the authorization covers. Inside a chain, a leg's own closing — think's 「end the turn」, draft's 「stop for the user's go」 — ends that leg, not the run: the only points inside a leg that stop the run are the ones its `references/loop-pauses.md` cannot default, and the Stops below.
- **Fix rounds.** A review finding is fixed in the main session under `../_shared/tdd.md`, then reviewed again by a fresh reviewer; two rounds at most per review leg.
- **Stops.** End the turn only for: (a) a choice that is the user's; (b) a blocked review leg; (c) a result that overturns the plan or the route — re-routing needs the user's yes; (d) an Authorization point the sentence does not name; (e) a leg that reports `no progress`. Record the stop in the ledger and say in one sentence what is needed. Nothing else stops the run: not a reversible decision, not a plateau, not "should I continue?".
- **Before ship.** Ship archives the ledger before it pushes, so the ledger cannot record what ship does. Before the ship leg starts, set the status to 交給 ship and finish the defaults list; ship's outcome, and any stop inside it, goes into the final report, which names the ledger at its archived path.
- **Report.** The route as run; each leg's verdict with its artifact path; every 「此處採預設」; the stops; what is left. End with:
「baransu-way：{完成|停在 {leg}|卡住}，{n}/{m} 段；帳本：{ledger path}」

## 6. Resume

`$baransu:baransu-way` with no goal, 「繼續」 after a stop, or a ledger slug: open the named ledger, or the newest open one; when none is open, the newest ledger at status 交給 ship under the archive directory ship moved it to, and only the ship leg reruns. Compare HEAD and the `git status --porcelain` hash with the last finished leg's. If either differs, say 「工作樹自 {leg} 後已變」 and rerun the last verifying leg before going on; ignored files are not tracked, and that is an accepted gap. A change in what the user wants is a re-route, not a resume.

## Not-for boundaries

- A skill you already know to call → call it; this skill adds nothing to one known leg.
- A multi-session campaign with many branches or PRs → the common suite's strategic-advance or wayfinder when installed (detect first, never assume).
- Changing how a leg works → that skill's own SKILL.md; this skill never restates a leg's rules.
