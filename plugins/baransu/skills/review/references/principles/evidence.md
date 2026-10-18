# Evidence — read the record, never produce one

**Bedrock.** Evidence is what already exists: the code, its tests' assertions, its history, and the author's record of running them on this version. Running is the author's part and reading is the review's; a question only a run could answer is a gap the author closes.

1. **A record is a place.** CI output, an attached log, a red → green record is another place the target must agree with, and often the only place an environment speaks.
2. **The record must be of this version.** Match its commit, and each platform the target claims. A claim of passing with no record of this version is a problem.
3. **A failing record suspects the observation first.** Compare the environment it ran in — platform, tool and dependency versions, configuration, inputs — with what the target claims or pins. Inside that, the failure is a phenomenon. Outside it, it is 「coverage lost」 naming the mismatch.
4. **The real thing, not a proxy.** A sentence saying it ran, a file's timestamp, an agent's self-report, or "it compiles" is not a record of the behaviour.
5. **A count is checked against its noun.** Files, classes, call sites, and test cases are different nouns; a count is evidenced by output that counted that noun in that scope, per `../../../_shared/fact-check.md`.
6. **A number needs its limiter.** A measured speedup, latency, or score carries its run count, its spread, and what bounds it; one that names none has not ruled out measuring a cache, an error, or work that never ran.
7. **Never fill a gap with your own observation.** A run the review made would answer a question the author's record leaves open, and hide that it is open.
