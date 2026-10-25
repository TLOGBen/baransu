# Evidence

Evidence is what already exists: the code, its tests' assertions, its history, and the author's record of running them on this version. Running is the author's part; reading is the review's. A question only a run could answer is a gap the author closes.

**Why:** A review that runs things answers a question the author's record left open and hides that it was open. The record is also where an environment speaks: a platform the review cannot see, it can read.

**Pattern:**
1. **Treat a record as a place.** CI output, an attached log, a red → green record is a place the target must hold with, and often the only place an environment speaks.
2. **Match the record to this version.** Its commit, and each platform the target claims. A record is of this version only when it was finished after the last edit to the code it drove: one older than that edit, or still being written when the review starts, is not evidence of this version. A claim of passing with no record of this version is a problem.
3. **Suspect the observation before the target.** Compare the environment a failing record ran in — platform, tool and dependency versions, configuration, inputs — with what the target claims or pins. Inside that, the failure is a phenomenon; outside it, it is uncertain — 「coverage lost: needs X」 naming the mismatch.
4. **Check the real thing, not a proxy.** A sentence saying it ran, a file's timestamp, an agent's self-report, or "it compiles" is not a record of the behaviour.
5. **Check a count against its noun.** Files, classes, call sites, test cases, and a metric's score — a complexity, a coverage, a size limit the repo sets — are different nouns; a count is evidenced by output that counted that noun in that scope, per `../../../_shared/fact-check.md`. A score estimated by reading is uncertain — 「coverage lost: needs X」 naming the tool that measures it.
6. **Ask a number for its limiter.** A speedup, latency, or score carries its run count, its spread, and what bounds it; one that names none has not ruled out measuring a cache, an error, or work that never ran.
7. **Leave the gap open.** Never fill it with an observation of your own; name the record that would close it. A question about every order of steps or every input — which no single run settles — names a hypothesis (`../../../hypothesis/references/model.md`, H1–H8) as that record.
8. **Prove the review's own claims the same way.** A place the review says holds, an exclusion included, is a claim: its reason is stated positively, with at least one `file:line` and its quoted text showing that what the place states or receives agrees with each text it is weighed against; "it does not say the opposite" is a proxy, not a reason. A place that cannot be shown this way fails at the confidence its evidence reaches, or is uncertain.
9. **A record proves only the path it exercised.** A run through a test-only entry, an internal setter, a mock past the production boundary, or a dry-run whose skipping nobody observed says nothing about the user's path; check what the record drove, and the resulting state and side effects it captured, not only its final line.

**The test:** For each claim the target makes about running, passing, or measuring: which record of this version shows it, and does that record cover the platform and scope claimed? For each place the review calls holding: which quoted line shows it?

**You skipped this when** the report repeats the author's "tests pass" without naming the record, or the review produced a result by running something, or a place holds because nothing there contradicts the change.
