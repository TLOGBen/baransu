# Benchmark — proving a number

Load this when a claim is a number someone measured or will measure: a speedup, a regression, a throughput, a latency, a library or configuration choice. A number is proved only by runs whose evidence would come out differently if the number were wrong. Answer each question below with evidence from a run, never from a reading of the code.

A quick ballpark the user asked for takes one run: still answer questions 4 and 7, say it is one run, and skip the rest unless that run looks wrong. A choice between options is never a ballpark.

## Before anything runs

- Write the claim in the words it will ship in（「匯出在 6 萬列資料集上 p50 快 30%」）. The questions test that sentence.
- Read the measurement script: what it times, what it counts, what it ignores.
- Check the machine: load average and core count. If something else is running and cannot be stopped, interleave the sides so both see the same noise, and say so in the record.

## The questions

1. **Why not double?** Name the limiter — the resource or code path that bounds the result: a core, a lock, the disk, the network, the load generator itself. Find it with a profile or system counters from a run you do not report (profilers slow the work), then map the hot spot to source. A guess from reading the code is not a limiter. If the load generator saturates first, the run measured the load generator. If a change did not move the number, the limiter says why.
2. **Was each side tuned?** Run every side the way production runs it: release builds, production flags and environment, batching and transaction settings, connection pools, caches as warm or cold as production sees them, the same versions and data. A side on defaults compares configurations, not implementations; a limiter that is a setting (a commit per row, a debug build, a missing index) means that side is untuned. Tune it and run again before naming a winner; if it cannot be tuned, name no winner from that run.
3. **Did it break a limit?** Do the arithmetic: bytes per second against disk and network bandwidth, operations per second times cost per operation against the cores, the time saved against the time the changed piece took. Removing a piece that takes 10% of the run can make the run at most about 11% faster. A result past a limit measured something else — a cache, a no-op, a bug.
4. **Did it error?** Count failures and non-success responses, and check that outputs are correct, not only present. Rejections are fast; timeouts and retries are slow. If the script does not count errors, add the count.
5. **Does it reproduce?** At least five runs per side, alternating A, B, A, B, so warmup, lazy initialisation, caches, and drift favour neither. Report the median and the range. A gap smaller than the run-to-run spread is no measurable difference; when the call is close, use a rank-sum test or the harness's own statistics.
6. **Does it matter?** Beside any micro result, measure the end-to-end path a user waits on, at realistic data sizes and concurrency, and give the micro result as a share of the whole. A helper that takes 1% of a request can make the request at most 1% faster.
7. **Did the work happen?** Confirm it ran inside the timed region: the request reached the server, the rows were written, the bytes were read, and the code used the result. Lazy code — generators nobody iterates, promises nobody awaits, results the compiler can discard — and timeouts produce numbers for work that never happened.

## Verdict and record

- The verdict is one of: faster, slower, no measurable difference, or inconclusive. It is inconclusive when a difference is claimed but the limiter is unnamed, a side ran untuned, or question 4 or 7 went unanswered; name the gap.
- The record gives the number with its unit, the run count per side, the range, and the limiter（「p50 41 ms → 33 ms，每邊 7 次取中位數，改後範圍 32～35 ms，瓶頸是單核 JSON 解析」）, plus the commands and the machine state. That is the record `/review` asks a speed claim for.
