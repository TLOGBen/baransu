# second-derivation — the brief for the agent that attacks the claim

What it is for: everything else in this skill checks the mathematics after the problem was translated into it — the bounds, the checks that say no, the calibration. None of them can see a wrong translation: a rule read wrongly, a premise never measured, a model that leaves out a path the source takes, a better answer nobody considered. The second derivation is someone who never saw that translation attacking the claim straight from the source, and trying to beat the proven bound. Its value is a finding or a better answer; agreement is the weaker result.

Its work is a fixed list, so it has an end: each rule attacked once, each open reading tried once, and — for an answer — one attempt to beat the objective. It stops when the list is done or a finding is in hand. The budget only catches a mistake.

## Before sending it

- Write the kind line of SKILL.md §3 first; the brief needs it, and it costs one line.
- Note the working tree's state (`git status`).
- Pick its scratch directory — outside the repository under test, in your own scratch or temporary space — and its ceiling — by default fifteen minutes and two gigabytes in total. Where the host lets you run a watchdog, start one on that directory that stops any process past the ceiling.
- Fill every `{…}` below and send the block, and nothing else, as the whole prompt of one fresh agent, in the background. Never add your model, your answer, your premises or your reasoning.

## The brief

```
Reply in Traditional Chinese.

You are attacking a claim, not solving the problem again. Someone else is working out an answer that you will not see. Find where the claim fails in the source, or find a better answer.

Claim: {the claim with its quantifier}
What good means: {the ideal from §1}
Rules, each with its owner and location:
{the plain rules confirmed in §2}
Readings still open: {the open questions, or "none"}
Source — read only these: {paths}
Tools here: {the interpreters, model checker and solvers §3 found, with their paths}
Kind of problem: {the kind line}. A finding is {§3's "A finding is" for this kind}.
What is too expensive here: {for an NP-hard objective: "an exact optimum only on instances of at most {n} items; anything larger is checked against a bound"; otherwise "nothing beyond the ceiling"}

Your list — do each item once, then stop:
{one line per rule}  Rule {R}: make it fail in the source — produce {§3's "A finding is" for this kind}, each step cited by file and symbol.
{one line per open reading}  Reading {Q}: what the verdict is under each meaning.
{for an answer}  Beat it: find an answer that obeys every rule and does better on {the objective} than {the target value, or "the best you can find in the list's time"}, and show why it holds.
Stop early when you have a finding.

Ceiling: {minutes} minutes and {gigabytes} GB in total. Before any run, choose its size, and give it a time limit and a memory limit inside the ceiling (a JVM `-Xmx`, a solver's memory option, a size cap on what a generator makes). A generator or a search with no chosen size is never started.
Write only inside {scratch directory}; start every command there.

Write everything — each item of the list with its result, each finding with its steps or instance, what you measured — to {scratch directory}/RESULT.md. Then reply with one line only: 「結果檔已寫好：{scratch directory}/RESULT.md」.
```

## After a fix

When §6 sends you back to §5 and you fix the model or the answer, and the judge and a real run do not already cover what the fix touched, send the same agent, or a fresh one, the fix in plain words, the source, and half the ceiling — it now sees what you changed, so this recheck tests the fix, not your independence — with a list of one item per rule the fix touches: "Check whether this fix holds in the source for each of these rules. Do not read anything else." Then stop; one recheck is enough.

## An argument a reader checks

When SKILL.md §6 sends an argument to a reader, send a fresh agent the claim, the setting from the request, and the argument, with a scratch directory outside the repository that is the only place it may write, and half the ceiling, every run with a time and a memory limit. What it gets depends on the bound:

- **Best possible** — the argument alone; it is about every answer, so yours has no place in it.
- **Proven** — the argument and the rules of your answer that the argument names, as the argument states them; never your model files, your code, or reasoning outside the argument.

Ask it: "Check whether this argument is correct; find a hole if there is one; say exactly what it holds for — deterministic or randomised answers, which inputs or metric, which limits — and whether a stronger correct version exists. Do not read anything else." Its answer goes in the report and in the README's bounds table. A hole sends the bound back to §5; the repaired argument goes to a reader once more, then stop.

## Without a way to send an agent

Say so in the report: the second derivation is missing, not done by you.
