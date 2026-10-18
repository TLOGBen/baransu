# exam — the blind known-answer exam

When Gate 3 allows real-exec, the effectiveness axis is an exam: the skill under test answers benchmark prompts whose answers are known, without knowing them, twice per prompt, under conditions that never change within a run. Twice, because one run cannot tell the text's effect from luck: an item found in only one run is one the text did not lead to. Fixed conditions, because a single added sentence in the examinee's prompt can change what it does, and then two versions are no longer compared on the same exam.

## Setup (Stage 0)

- **Answer keys** — per benchmark prompt: the items a correct run finds or produces, what counts as a partial hit, and what costs points (for example a finding that opposes the user's own goal, or one verified false). The user writes or confirms them; evolve never generates a key. A prompt without a key is still examined, and the judges read its outputs as offline evidence; recall is reported for keyed prompts only.
- **Case terms** — `case-terms.txt`: the terms distinctive to the prompts and keys (file and directory names, identifiers, item labels, phrases quoted from a target). evolve proposes the list from the prompts and keys; the user confirms it. Stage 3's case-term gate and the brief check grep against it.
- **Exam template** — `exam/template.md`: the examinee's entire prompt, with exactly two slots, `{prompt}` and `{skill_copy}`. It states the task and where to write the report, and says nothing about evolve, the answers, the previous run, or what to look for. Record its sha256 in `decisions.tsv`.
- **Version copies** — every version examined is copied read-only to `exam/versions/<round>/` with the agents and references it loads. The examinee dispatches each agent the skill names as a general-purpose subagent whose first instruction is to read that agent's definition from the copy — a named agent type resolves to the installed plugin, which would put an installed agent into every version's exam.
- Held-out prompts and their keys stay out of every brief, seed and Stage 1 evidence until Stage 7.

## Taking the exam (Stage 4)

1. For each train prompt, dispatch two fresh examinees, `a` and `b`, in parallel, each from the template with only the two slots filled. Nothing else reaches them: no key, no evolve context, no earlier output.
2. Before every dispatch, hash the filled template's fixed part against the recorded sha256. A mismatch means the run is contaminated: redo it from the fixed template, keep the contaminated output under `exam/contaminated/` as reference only — never scored — and add a `decisions.tsv` line.
3. Record each run's tokens and wall time from its completion notice.
4. The current version's outputs are reused from the round that produced them; only the candidate sits a new exam.

## Scoring

- One fresh **evolve-judge** in exam mode receives the answer keys and every output of the current version and the candidate (in round 1, the unmodified target's outputs alone), shuffled under neutral labels, and returns per output the items hit, partially hit and missed, and each penalty with its reason. It is not told which output came from which version or which run.
- **Recall** of a version = items hit in both runs + ½ × items hit in one run (a partial hit counts as the key says), minus penalties. Consistency is part of recall, not averaged away.
- **Items found in only one run** are listed; the next round's diagnostician treats each as a phenomenon.
- **Noise band** = the larger of the two versions' own spreads: per prompt, the difference between a version's `a` and `b` recall, and between its `a` and `b` tokens and time, summed over prompts. Two runs make a thin estimate, so a version is not penalised because the other one happened to run twice alike. A difference between versions inside the band is flat, not progress.
- **Cost** = mean tokens and wall time over the two runs.
- Write the sheet to `exam/round-<N>.md`. Stage 5 relabels it alpha/beta for the panel and applies the keep bar: recall no lower and cost no higher than the current version's beyond the noise band.

## Keeping the exam honest

An exam is a verification of the skill, and it drifts like any other: keys go stale, a prompt's wording can decide a score, a key item can sit outside what the prompt asks for. Check these before a round's misses are read as the skill's failure.

- **Each key item is able to be found.** Before the first round, show each item is reachable from the prompt as written: its location at the pinned version, the change that introduced it, and whether the prompt's scope covers it — an item that predates the change under review, or that only a run would show, is recorded as out of scope for that prompt, not as a miss.
- **The template restates only the fairness rules.** A sentence that forbids a source a correct run would read (a record, a log, an earlier commit) decides the score instead of the skill; examinees of different models read such a sentence differently. Forbid only what would leak the answer, such as anything after the pinned version.
- **Examinees take the user's path.** Each examinee uses the skill the way its user would, from a fresh session with the skill's own instructions, never through a shortcut a user would not have.
- **Record whether each item's place was reached.** The scorer notes, per key item and output, whether the place was listed, read, and how it was judged; "never reached" and "reached and judged fine" lead the next diagnosis to different clauses.
- **Classify every miss before scoring it.** A miss is the skill's, the key's (the item or its location is wrong), the exam's (wording or scope kept the examinee away), or a limit (only a run settles it). Only the first counts against the version; the other three are fixed in the key or template, with a `decisions.tsv` line, and that change is itself a reason to re-examine the current version.

## Held-out (Stage 7)

The held-out prompts sit the same exam — same template, two runs each, the same scorer protocol — for the pre-evolution and converged versions.
