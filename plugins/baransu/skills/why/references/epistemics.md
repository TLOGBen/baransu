# Confidence and phrasing

The record behind a "why" is historical, partial and sometimes contradictory. These rules keep the answer from flattening that into false certainty.

## The five tiers

Every claim sits in exactly one tier, and the tier decides where it goes and how it is worded.

1. **Direct** — an author wrote the reason down: an ADR's decision and context, a PR body ("fixes pagination for users with more than 1000 items"), a commit message, a code comment ("clamp to 100: the upstream API rejects larger values"), a plan's Key decisions line, the user's own instruction in a transcript. Worded plainly and cited: "This exists because X (source)."
2. **Supported** — no single source says it, but several independent items point the same way: the PR title says "perf", the ticket is labelled perf, the same week's commits all touch one hot path. Worded with each item listed: "The evidence points to X: A, B, C."
3. **Inferred** — a reasonable reading that nothing states: the fix merged the same day an incident was reported, so it was likely a hotfix. Worded with the chain visible and hedged: "Given A and B, C seems likely."
4. **Speculative** — a hypothesis on thin evidence that other explanations fit as well. Worded as a guess: "One possibility is X; no source supports it." It usually belongs in 其他可能的解釋.
5. **Unknown** — searched and not found. A valid result, worded with what was searched: "Searched the tracker for A and B and the six PRs touching this file since 2024; none gives a reason."

## Who wrote it

On a machine where agents write most commits, PR bodies and plans, a written reason is often the agent's. It still counts as Direct evidence of what was recorded, but say the author was an agent (or that the author cannot be told: a commit under the user's name with no agent trailer could be either), and list the user's part separately: the user's own words are Direct, while a merge or an approval without stated reasons is Supported evidence that the user accepted it.

An upstream document or a reproduction is Direct evidence of how a tool behaves, never of why the author chose what they chose; a conclusion that joins the two ("the API rejects values above 100, which is why the code clamps to 100") is Supported at most.

When the same reason appears in several places (a commit, then the instruction file, then a code comment), cite the earliest statement and name the restatements in one line. Restatements that disagree on a fact are a contradiction, not a list of confirmations; restatements that frame the same decision differently go to 其他可能的解釋.

## Words

Words that claim intent or effect — "because", "the reason is", "was designed to", "fixes", "the team decided" (and their Chinese equivalents 因為、原因是、設計來、修好了、團隊決定) — need a Direct or Supported citation right beside them. Never use them for an inference.

Hedges mark interpretation: "appears to", "likely", "suggests", "is consistent with" (看起來、可能、顯示、符合). Use them freely in 合理推論 and nowhere in 找到什麼.

Avoid "obviously", "clearly", "of course", "just" (顯然、當然、只是): if it were obvious, the user would not be asking, and the word usually hides a gap. Do not write "I think"; the answer reports evidence, not an opinion.

## Contradictions

Show both sources with citations and let the user judge. A ticket that says "compliance requirement for customer X" and a PR that says "tech-debt cleanup" may both be true (the ticket motivated the work, the PR is the author's framing), or one may be wrong. Three sources agreeing and a fourth disagreeing makes the fourth the most interesting finding, not the one to drop.

## The user's guess

When the question embeds a hypothesis, test it like any other. Say so with citations if the record supports it; if not, say that, and show what the record does support.

## Missing evidence

An honest "we don't know" tells the user the answer is not in the obvious places and who to ask next (the author, the person who gave the instruction). Filling the gap with a plausible reason harms them, because they will act on it. Name each gap concretely: the question, each source searched, the terms used, and what came back.

## Before presenting

- Every claim in 找到什麼 has a citation; one without moves to 合理推論 or 其他可能的解釋.
- Each claim's wording matches its tier.
- No claim uses the code as evidence of its own intent.
- Every contradiction noticed is shown.
- The user's guess was tested, not confirmed by default.
- 不知道什麼 is present. If it is empty, check again: a historical search almost always leaves gaps, and an empty list usually means one was smoothed over.
