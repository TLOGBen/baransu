# Hypothesis

A change that reaches what a hypothesis covers either keeps every rule of that hypothesis 成立 within its scope, or the review says which rule it puts at stake and why. A hypothesis is the author's machine-checked evidence, read like a test record: the review reads its state, never runs or edits it.

**Why:** A hypothesis states, for every order of steps its model allows, what must never happen and what must stay possible. Its value lasts only while it describes the code: a change to what it covers makes it stale, and a stale pass is a false proof. The reviewer is the one reader who sees the change and the claim side by side, so it is where a broken or forgotten hypothesis is cheapest to catch.

**Pattern:**
1. **Ask the status script first.** Run `hypothesis-status.py --diff <base>` (`../../../hypothesis/references/reading.md` § One command) and quote its lines. Running it reads files; it runs no target, so it stays inside review-only.
2. **Put the coverage on the walk.** Every place a covering hypothesis cites goes on the walk, and each of its rules (`--rules <area>`) becomes that place's question: after this change, does the rule still hold here? Answer from the code, with the rule's id.
3. **A stale hypothesis is a finding.** Head it 「假說 {area} 已過期：{why}；需要 /hypothesis --maintain {area}」. Never treat its last verdict as evidence; ask its rules as questions anyway. Maintaining it is the main session's call into `/hypothesis`, never this review's.
4. **An unfinished one is not evidence.** A `draft` or `legacy` hypothesis — 「嚴格檢查未完成」 — proves nothing done; say so where the author relies on it.
5. **Known paths stay known.** For a `disproved` hypothesis, each path (`--paths <area>`) is an existing finding: say whether the change fixes it, touches it, or leaves it, with the path id.
6. **A risky change with no hypothesis is coverage lost.** When the change lands in an H1–H8 row of `../../../hypothesis/references/formal.md` and no hypothesis covers it, write 「coverage lost: needs /hypothesis」 with one reason record (`../../../hypothesis/templates/reason-record.md`), class and detail filled — not a severity on its own, unless the change also breaks a rule the code states elsewhere.
7. **Review a hypothesis as a target.** When the target is a hypothesis itself: its rules match what the user asked; every safety and liveness rule is guarded by a goal; each model part cites its source and keeps the source's indivisible steps; bounds, assumptions and what is left out are stated; seen failing and seen succeeding are recorded (the status script's `why` names what is missing); every unformalized part has a complete reason record; each finding opens in plain words.
8. **Read, never reproduce.** Do not rerun the model, open its `--check` command, or edit anything under `.claude/hypothesis/`; a claim only a rerun can settle goes to `/prove-it`.
9. **Scope is part of the proof.** A rule that holds within the stated bounds says nothing outside them; a place the change reaches outside the scope needs its own evidence.

**The test:** For each hypothesis the status script lists against the change: is its state quoted, does every place it covers carry its rules as questions, and is each stale, unfinished, or missing hypothesis reported rather than trusted?

**You skipped this when** the review passed a change to code a hypothesis covers without quoting the status line, or accepted 「假說成立」 from a hypothesis the script shows as `stale`, `draft` or `legacy`.
