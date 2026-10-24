# Hypothesis

A change that reaches what a hypothesis covers either keeps every rule of that hypothesis 守住 within its scope, or the review says which rule it puts at stake and why. A hypothesis is the author's machine-checked evidence, read like a test record: the review reads its state, never runs or edits it.

**Why:** A hypothesis states, for every order of steps its model allows, what must never happen and what must stay possible. Its value lasts only while it describes the code: a change to what it covers makes it stale, and a stale pass is a false proof. The reviewer is the one reader who sees the change and the claim side by side, so it is where a broken or forgotten hypothesis is cheapest to catch.

**Pattern:**
1. **Ask the status script first.** Run `hypothesis-status.py --diff <base>` (`../../../hypothesis/references/reading.md` § One command) and quote its lines. Running it reads files; it runs no target, so it stays inside review-only.
2. **Put the coverage on the walk.** Every place a covering hypothesis cites goes on the walk, and each of its rules (`--rules <area>`) becomes that place's question: after this change, does the rule still hold here? Answer from the code, with the rule's id.
3. **Stale or unfinished is not evidence.** A `stale` hypothesis was checked against code this change no longer matches; a `draft` or `legacy` one never finished its strict check — neither is a record of this version (`evidence.md` #2). Write the finding string the `$baransu:review` column of `../../../hypothesis/references/reading.md` § State × reader gives for that state: as the impact of a problem headed per `index.md` where the author relies on it, otherwise as an uncertain item. Ask its rules as questions anyway. Maintaining it is the main session's call into `$baransu:hypothesis`, never this review's.
4. **Known paths stay known.** For an `established` hypothesis with a rule 被打破, each path (`--paths <area>`) is an existing finding: say whether the change fixes it, touches it, or leaves it, with the path id.
5. **Review a hypothesis as a target.** When the target is a hypothesis itself: its rules match what the user asked (`goal.md` #7 — a hypothesis is a plan of what must hold); every safety and liveness rule is guarded by a goal; each model part cites its source and keeps the source's indivisible steps; bounds, assumptions and what is left out are stated; seen failing and seen succeeding are recorded (the status script's `why` names what is missing); every unformalized part has a complete reason record; each finding opens in plain words.
6. **Read, never reproduce.** Do not rerun the model, open its `--check` command, or edit anything under `.codex/hypothesis/`; a claim only a rerun can settle goes to `$baransu:prove-it`.
7. **Scope is part of the proof.** A rule that holds within the stated bounds says nothing outside them (`evidence.md` #9 for a model); a place the change reaches outside the scope needs its own evidence.

**The test:** For each hypothesis the status script lists against the change: is its state quoted, does every place it covers carry its rules as questions, and is each stale or unfinished hypothesis reported rather than trusted?

**You skipped this when** the review passed a change to code a hypothesis covers without quoting the status line, or accepted 「規則都守住」 from a hypothesis the script shows as `stale`, `draft` or `legacy`.
