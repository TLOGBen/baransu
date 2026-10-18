# exam — the blind known-answer exam

When Gate 3 allows real-exec, the effectiveness axis is an exam: the skill under test answers benchmark prompts whose answers are known, without knowing them, twice per prompt, under conditions that never change within a run. Twice, because one run cannot tell the text's effect from luck: an item found in only one run is one the text did not lead to. Fixed conditions, because a single added sentence in the examinee's prompt can change what it does, and then two versions are no longer compared on the same exam.

## Setup (Stage 0)

- **Answer keys** — per benchmark prompt: the items a correct run finds or produces, what counts as a partial hit, and what costs points (for example a finding that opposes the user's own goal, or one verified false). The user writes or confirms them; evolve never generates a key. A prompt without a key is still examined, and the judges read its outputs as offline evidence; recall is reported for keyed prompts only.
- **Case terms** — `case-terms.txt`: the terms distinctive to the prompts and keys (file and directory names, identifiers, item labels, phrases quoted from a target). evolve proposes the list from the prompts and keys; the user confirms it. Stage 3's case-term gate and the brief check grep against it.
- **Exam template** — `exam/template.md`: the examinee's entire prompt, with exactly two slots, `{prompt}` and `{skill_copy}`. It states the task and where to write the report, and says nothing about evolve, the answers, the previous run, or what to look for. Record its sha256 in `decisions.tsv`.
- **Version copies** — every version examined is copied read-only to `exam/versions/<round>/` with the agents and references it loads, so an examinee reads that version and nothing newer.
- Held-out prompts and their keys stay out of every brief, seed and Stage 1 evidence until Stage 7.

## Taking the exam (Stage 4)

1. For each train prompt, dispatch two fresh examinees, `a` and `b`, in parallel, each from the template with only the two slots filled. Nothing else reaches them: no key, no evolve context, no earlier output.
2. Before every dispatch, hash the filled template's fixed part against the recorded sha256. A mismatch means the run is contaminated: redo it from the fixed template, keep the contaminated output under `exam/contaminated/` as reference only — never scored — and add a `decisions.tsv` line.
3. Record each run's tokens and wall time from its completion notice.
4. The current version's outputs are reused from the round that produced them; only the candidate sits a new exam.

## Scoring

- One fresh **evolve-judge** in exam mode receives the answer keys and every output of the current version and the candidate, shuffled under neutral labels, and returns per output the items hit, partially hit and missed, and each penalty with its reason. It is not told which output came from which version or which run.
- **Recall** of a version = items hit in both runs + ½ × items hit in one run (a partial hit counts as the key says), minus penalties. Consistency is part of recall, not averaged away.
- **Items found in only one run** are listed; the next round's diagnostician treats each as a phenomenon.
- **Noise band** = the current version's own spread: per prompt, the difference between its `a` and `b` recall, and between its `a` and `b` tokens and time, summed over prompts. A difference between versions inside the band is flat, not progress.
- **Cost** = mean tokens and wall time over the two runs.
- Write the sheet to `exam/round-<N>.md`. Stage 5 relabels it alpha/beta for the panel and applies the keep bar: recall no lower and cost no higher than the current version's beyond the noise band.

## Held-out (Stage 7)

The held-out prompts sit the same exam — same template, two runs each, the same scorer protocol — for the pre-evolution and converged versions.
